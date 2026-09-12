"""
Diplom loyihasi – Saidov Suhrob Alisherovich
Ijtimoiy so'rovnomalar natijalarini tahlil qilish tizimi
Backend: Python 3.10 + Flask 2.3
"""

from flask import Flask, request, jsonify, render_template, session
import pandas as pd
import numpy as np
import os, json, uuid
from functools import wraps
from datetime import datetime

from models.classifier  import SurveyClassifier
from models.clustering  import SurveyClustering
from models.sentiment   import SentimentAnalyzer
from utils.preprocessor import DataPreprocessor
from database.db_manager import DBManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

db  = DBManager()
clf = SurveyClassifier()
clu = SurveyClustering()
sen = SentimentAnalyzer()
pre = DataPreprocessor()

# ─── Auth decorator ──────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Tizimga kiring'}), 401
        return f(*args, **kwargs)
    return decorated

# ─── Pages ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ─── Auth ────────────────────────────────────────────────────────────────────
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if username == 'admin' and password == 'admin123':
        session['user_id'] = 1
        session['username'] = username
        return jsonify({'success': True, 'username': username})
    return jsonify({'error': "Login yoki parol noto'g'ri"}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me')
def me():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'username': session.get('username')})
    return jsonify({'logged_in': False})

# ─── Upload ───────────────────────────────────────────────────────────────────
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_survey():
    if 'file' not in request.files:
        return jsonify({'error': 'Fayl topilmadi'}), 400
    file = request.files['file']
    fname = file.filename.lower()
    try:
        if fname.endswith('.csv'):
            df = pd.read_csv(file)
        elif fname.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': "Faqat CSV yoki Excel (.xlsx/.xls) yuklang"}), 400
    except Exception as e:
        return jsonify({'error': f'Fayl o\'qishda xato: {str(e)}'}), 400

    survey_id = str(uuid.uuid4())[:8]
    db.save_survey(survey_id, file.filename, df)

    preview = df.head(5).replace({np.nan: None}).to_dict(orient='records')
    return jsonify({
        'survey_id': survey_id,
        'rows': len(df),
        'columns': list(df.columns),
        'preview': preview,
        'filename': file.filename
    }), 201

# ─── Analyze ─────────────────────────────────────────────────────────────────
@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    survey_id = data.get('survey_id')
    if not survey_id:
        return jsonify({'error': 'survey_id kerak'}), 400

    df = db.get_survey(survey_id)
    if df is None:
        return jsonify({'error': "So'rovnoma topilmadi"}), 404

    results = {}

    # ── 1. Preprocessing ──────────────────────────────────────────────────
    df_clean = pre.clean(df.copy())
    num_cols  = df_clean.select_dtypes(include=np.number).columns.tolist()
    text_cols = df_clean.select_dtypes(include='object').columns.tolist()

    results['preprocessing'] = {
        'original_rows': len(df),
        'clean_rows':    len(df_clean),
        'num_columns':   num_cols,
        'text_columns':  text_cols,
    }

    # ── 2. Classification (if target column exists) ───────────────────────
    target_col = data.get('target_col')
    if target_col and target_col in df_clean.columns and len(num_cols) >= 2:
        try:
            X = df_clean[num_cols].drop(columns=[target_col], errors='ignore').values
            y = df_clean[target_col].astype(int).values
            clf_res = clf.train_and_evaluate(X, y)
            results['classification'] = clf_res
        except Exception as e:
            results['classification'] = {'error': str(e)}
    else:
        results['classification'] = {'skipped': 'Maqsad ustun tanlanmagan yoki raqamli ustunlar yetarli emas'}

    # ── 3. Clustering ─────────────────────────────────────────────────────
    if len(num_cols) >= 2:
        try:
            X_num = df_clean[num_cols].values
            k_opt, scores = clu.find_optimal_k(X_num)
            labels  = clu.fit_predict(X_num, k=k_opt)
            cluster_info = []
            for k in range(k_opt):
                mask = labels == k
                cluster_info.append({
                    'id':    k,
                    'label': f'Klaster {k}',
                    'size':  int(mask.sum()),
                    'pct':   round(float(mask.sum()) / len(labels) * 100, 1)
                })
            results['clustering'] = {
                'optimal_k': k_opt,
                'silhouette': round(scores[k_opt], 3),
                'clusters':  cluster_info,
                'labels':    labels.tolist()
            }
        except Exception as e:
            results['clustering'] = {'error': str(e)}
    else:
        results['clustering'] = {'skipped': 'Raqamli ustunlar yetarli emas'}

    # ── 4. Sentiment ──────────────────────────────────────────────────────
    if text_cols:
        try:
            col = text_cols[0]
            texts = df_clean[col].dropna().astype(str).tolist()[:200]
            sent_res = sen.analyze(texts)
            counts = {'ijobiy': 0, 'neytral': 0, 'salbiy': 0}
            for r in sent_res:
                counts[r['label']] += 1
            results['sentiment'] = {
                'column': col,
                'total':  len(sent_res),
                'counts': counts,
                'sample': sent_res[:10]
            }
        except Exception as e:
            results['sentiment'] = {'error': str(e)}
    else:
        results['sentiment'] = {'skipped': 'Matnli ustun topilmadi'}

    db.save_results(survey_id, results)
    return jsonify({'survey_id': survey_id, 'results': results})

# ─── Get results ─────────────────────────────────────────────────────────────
@app.route('/api/results/<survey_id>')
@login_required
def get_results(survey_id):
    res = db.get_results(survey_id)
    if res is None:
        return jsonify({'error': "Natijalar topilmadi"}), 404
    return jsonify(res)

@app.route('/api/surveys')
@login_required
def list_surveys():
    return jsonify(db.list_surveys())

if __name__ == '__main__':
    db.init()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
