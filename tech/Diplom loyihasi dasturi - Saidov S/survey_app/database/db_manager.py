import sqlite3, json, os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'survey.db')

class DBManager:
    def init(self):
        with self._conn() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS surveys (
                id TEXT PRIMARY KEY,
                filename TEXT,
                data_json TEXT,
                created_at TEXT
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS results (
                survey_id TEXT PRIMARY KEY,
                result_json TEXT,
                created_at TEXT
            )''')

    def _conn(self):
        return sqlite3.connect(DB_PATH)

    def save_survey(self, survey_id, filename, df: pd.DataFrame):
        data = df.head(1000).replace({float('nan'): None}).to_dict(orient='records')
        with self._conn() as c:
            c.execute(
                'INSERT OR REPLACE INTO surveys VALUES (?,?,?,datetime("now"))',
                (survey_id, filename, json.dumps(data, ensure_ascii=False))
            )

    def get_survey(self, survey_id) -> pd.DataFrame:
        with self._conn() as c:
            row = c.execute('SELECT data_json FROM surveys WHERE id=?', (survey_id,)).fetchone()
        if not row: return None
        return pd.DataFrame(json.loads(row[0]))

    def save_results(self, survey_id, results: dict):
        with self._conn() as c:
            c.execute(
                'INSERT OR REPLACE INTO results VALUES (?,?,datetime("now"))',
                (survey_id, json.dumps(results, ensure_ascii=False))
            )

    def get_results(self, survey_id):
        with self._conn() as c:
            row = c.execute('SELECT result_json FROM results WHERE survey_id=?', (survey_id,)).fetchone()
        if not row: return None
        return json.loads(row[0])

    def list_surveys(self):
        with self._conn() as c:
            rows = c.execute('SELECT id, filename, created_at FROM surveys ORDER BY created_at DESC').fetchall()
        return [{'id': r[0], 'filename': r[1], 'created_at': r[2]} for r in rows]
