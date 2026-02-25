from flask import Flask, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path("data") / "database.sqlite"

@app.route('/')
def index():
    return "MyFinanceApp — serveur local actif"

@app.route('/health')
def health():
    exists = DB_PATH.exists()
    return jsonify({'status': 'ok', 'db_exists': exists})

@app.route('/tables')
def tables():
    if not DB_PATH.exists():
        return jsonify({'error': 'database not initialized'}), 400
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return jsonify({'tables': rows})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
