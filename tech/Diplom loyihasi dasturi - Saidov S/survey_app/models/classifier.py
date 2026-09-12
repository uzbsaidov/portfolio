from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import numpy as np, joblib, os

class SurveyClassifier:
    def __init__(self):
        self.model = None
        self.best_params = None

    def train_and_evaluate(self, X, y) -> dict:
        if len(np.unique(y)) < 2:
            return {'error': 'Kamida 2 ta sinf kerak'}
        if len(X) < 20:
            return {'error': 'Kamida 20 ta yozuv kerak'}

        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # GridSearch (kichik grid – tez ishlash uchun)
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth':    [10, 15, None],
            'min_samples_split': [2, 5]
        }
        rf = RandomForestClassifier(random_state=42)
        gs = GridSearchCV(rf, param_grid, cv=min(5, len(np.unique(y))),
                          scoring='f1_weighted', n_jobs=-1)
        gs.fit(X_tr, y_tr)
        self.model       = gs.best_estimator_
        self.best_params = gs.best_params_

        # CV
        cv = cross_val_score(self.model, X_tr, y_tr, cv=5)

        # Evaluate
        y_pred = self.model.predict(X_te)
        y_prob = self.model.predict_proba(X_te)
        report = classification_report(y_te, y_pred, output_dict=True)
        try:
            if y_prob.shape[1] == 2:
                auc = float(roc_auc_score(y_te, y_prob[:, 1]))
            else:
                auc = float(roc_auc_score(y_te, y_prob, multi_class='ovr'))
        except:
            auc = None

        cm = confusion_matrix(y_te, y_pred).tolist()
        fi = self.model.feature_importances_.tolist()

        return {
            'accuracy':      round(report['accuracy'], 3),
            'f1_weighted':   round(report['weighted avg']['f1-score'], 3),
            'precision':     round(report['weighted avg']['precision'], 3),
            'recall':        round(report['weighted avg']['recall'], 3),
            'auc':           round(auc, 3) if auc else None,
            'cv_mean':       round(float(cv.mean()), 3),
            'cv_std':        round(float(cv.std()), 3),
            'confusion_matrix': cm,
            'feature_importances': fi,
            'best_params':   self.best_params,
            'n_train':       len(X_tr),
            'n_test':        len(X_te)
        }

    def save(self, path='model.pkl'):
        joblib.dump(self.model, path)

    def load(self, path='model.pkl'):
        if os.path.exists(path):
            self.model = joblib.load(path)
