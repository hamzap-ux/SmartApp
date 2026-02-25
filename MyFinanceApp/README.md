# MyFinanceApp

Subscription & Expense Tracker App.
 deploying : 

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt


Initialiser la base SQLite:

mkdir -p data logs
sqlite3 data/database.sqlite < app/database/schema.sql

lancer app:

python3 main.py



Si main.py est une app Flask:

export FLASK_APP=main.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000