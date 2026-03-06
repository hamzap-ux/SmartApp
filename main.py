from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import os

app = Flask(__name__)
# Allow overriding the secret key with an environment variable in production
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key-change-in-production')
DB_PATH = Path("data") / "database.sqlite"

# AWS SES Configuration
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "noreply@yourdomain.com")

def send_welcome_email(recipient_email, username):
    """Send a welcome email using AWS SES."""
    client = boto3.client('ses', region_name=AWS_REGION)
    subject = "Welcome to SmartApp!"
    body_text = f"Hi {username},\n\nWelcome to SmartApp! We're excited to have you on board.\n\nBest,\nThe SmartApp Team"
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>Welcome to SmartApp, {username}!</h1>
      <p>We're excited to have you on board.</p>
      <p>Best,<br>The SmartApp Team</p>
    </body>
    </html>"""
    
    try:
        response = client.send_email(
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Body': {
                    'Html': {'Charset': "UTF-8", 'Data': body_html},
                    'Text': {'Charset': "UTF-8", 'Data': body_text},
                },
                'Subject': {'Charset': "UTF-8", 'Data': subject},
            },
            Source=SENDER_EMAIL,
        )
    except ClientError as e:
        print(f"Email sending failed: {e.response['Error']['Message']}")
        return False
    else:
        print(f"Email sent! Message ID: {response['MessageId']}")
        return True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User(id=row['id'], username=row['username'], email=row['email'])
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            conn.commit()
            
            # Send welcome email via AWS SES
            try:
                send_welcome_email(email, username)
            except Exception as e:
                print(f"Failed to send welcome email: {e}")
                
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = cur.fetchone()
        conn.close()

        if user_row and check_password_hash(user_row['password'], password):
            user = User(id=user_row['id'], username=user_row['username'], email=user_row['email'])
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    if not DB_PATH.exists():
        return render_template('index.html', total_spending=0, active_subs=0, monthly_sub_cost=0, upcoming_bills=0, recent_expenses=[], upcoming_renewals=[], chart_data={'categories': [], 'category_amounts': []})
        
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    uid = current_user.id

    # KPIs
    cur.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = ?", (uid,))
    total_spending = cur.fetchone()['total'] or 0.0

    cur.execute("SELECT COUNT(*) as count, SUM(amount) as total_cost FROM subscriptions WHERE active = 1 AND user_id = ?", (uid,))
    sub_data = cur.fetchone()
    active_subs = sub_data['count'] or 0
    monthly_sub_cost = sub_data['total_cost'] or 0.0

    cur.execute("SELECT COUNT(*) as count FROM reminders WHERE sent = 0 AND user_id = ?", (uid,))
    upcoming_bills = cur.fetchone()['count'] or 0

    # Lists
    cur.execute("SELECT description, amount, date FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT 5", (uid,))
    recent_expenses = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT name, amount, next_renewal FROM subscriptions WHERE active = 1 AND user_id = ? ORDER BY next_renewal ASC LIMIT 5", (uid,))
    upcoming_renewals = [dict(row) for row in cur.fetchall()]

    # Chart Data: Expenses by Category
    cur.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category", (uid,))
    cat_data = cur.fetchall()
    categories = [row['category'] for row in cat_data]
    category_amounts = [row['total'] for row in cat_data]

    conn.close()

    chart_data = {
        'categories': categories,
        'category_amounts': category_amounts,
    }

    # compute wallet balance (sum incomes - sum expenses)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) as total FROM incomes WHERE user_id = ?", (uid,))
    total_income = cur.fetchone()['total'] or 0.0
    conn.close()

    wallet_balance = (total_income or 0.0) - (total_spending or 0.0)

    return render_template('index.html',
                           total_spending=total_spending,
                           active_subs=active_subs,
                           monthly_sub_cost=monthly_sub_cost,
                           upcoming_bills=upcoming_bills,
                           recent_expenses=recent_expenses,
                           upcoming_renewals=upcoming_renewals,
                           chart_data=chart_data,
                           wallet_balance=wallet_balance)



@app.route('/api/trends')
@login_required
def api_trends():
    # returns monthly aggregated data for expenses, subscriptions and incomes
    try:
        months = int(request.args.get('months', 6))
    except ValueError:
        months = 6

    if months < 1:
        months = 6

    uid = current_user.id
    from datetime import date, datetime
    from dateutil.relativedelta import relativedelta

    today = date.today()
    # build list of months (YYYY-MM) from oldest to newest
    labels = []
    month_keys = []
    for i in range(months-1, -1, -1):
        m = today - relativedelta(months=i)
        key = m.strftime('%Y-%m')
        month_keys.append(key)
        labels.append(m.strftime('%b %Y'))

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # expenses by month
    cur.execute("""
        SELECT strftime('%Y-%m', date) as ym, SUM(amount) as total
        FROM expenses
        WHERE user_id = ? AND date IS NOT NULL
        GROUP BY ym
    """, (uid,))
    rows = {r['ym']: r['total'] for r in cur.fetchall()}
    expenses = [rows.get(k, 0.0) for k in month_keys]

    # incomes by month
    cur.execute("""
        SELECT strftime('%Y-%m', date) as ym, SUM(amount) as total
        FROM incomes
        WHERE user_id = ? AND date IS NOT NULL
        GROUP BY ym
    """, (uid,))
    rows = {r['ym']: r['total'] for r in cur.fetchall()}
    incomes = [rows.get(k, 0.0) for k in month_keys]

    # subscriptions: use monthly total of active subscriptions
    cur.execute("SELECT SUM(amount) as total FROM subscriptions WHERE active = 1 AND user_id = ?", (uid,))
    sub_total = cur.fetchone()['total'] or 0.0
    subscriptions = [sub_total for _ in month_keys]

    conn.close()

    return jsonify({
        'labels': labels,
        'expenses': expenses,
        'subscriptions': subscriptions,
        'incomes': incomes
    })

@app.route('/subscriptions', methods=['GET', 'POST'])
@login_required
def subscriptions():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    uid = current_user.id

    if request.method == 'POST':
        action = request.form.get('action', 'add')
        item_id = request.form.get('item_id')
        if action == 'add':
            name = request.form.get('name')
            provider = request.form.get('provider')
            amount = request.form.get('amount') or 0
            billing_period = request.form.get('billing_period')
            next_renewal = request.form.get('next_renewal')

            cur.execute("""
                INSERT INTO subscriptions (user_id, name, provider, amount, billing_period, next_renewal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (uid, name, provider, amount, billing_period, next_renewal))
            conn.commit()
        elif action == 'modify' and item_id:
            name = request.form.get('name')
            provider = request.form.get('provider')
            amount = request.form.get('amount') or 0
            billing_period = request.form.get('billing_period')
            next_renewal = request.form.get('next_renewal')
            cur.execute("""
                UPDATE subscriptions SET name = ?, provider = ?, amount = ?, billing_period = ?, next_renewal = ?
                WHERE id = ? AND user_id = ?
            """, (name, provider, amount, billing_period, next_renewal, item_id, uid))
            conn.commit()
        elif action == 'delete' and item_id:
            # soft delete
            cur.execute("UPDATE subscriptions SET active = 0 WHERE id = ? AND user_id = ?", (item_id, uid))
            conn.commit()
        return redirect(url_for('subscriptions'))

    cur.execute("SELECT * FROM subscriptions WHERE active = 1 AND user_id = ? ORDER BY next_renewal ASC", (uid,))
    active_subs = [dict(row) for row in cur.fetchall()]
    conn.close()

    return render_template('subscriptions.html', active_subs=active_subs)

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    uid = current_user.id

    if request.method == 'POST':
        action = request.form.get('action', 'add')
        item_id = request.form.get('item_id')
        if action == 'add':
            description = request.form.get('description')
            category = request.form.get('category')
            amount = request.form.get('amount')
            date = request.form.get('date')
            cur.execute("""
                INSERT INTO expenses (user_id, description, category, amount, date)
                VALUES (?, ?, ?, ?, ?)
            """, (uid, description, category, amount, date))
            conn.commit()
        elif action == 'modify' and item_id:
            description = request.form.get('description')
            category = request.form.get('category')
            amount = request.form.get('amount')
            date = request.form.get('date')
            cur.execute("""
                UPDATE expenses SET description = ?, category = ?, amount = ?, date = ?
                WHERE id = ? AND user_id = ?
            """, (description, category, amount, date, item_id, uid))
            conn.commit()
        elif action == 'delete' and item_id:
            cur.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (item_id, uid))
            conn.commit()
        return redirect(url_for('expenses'))

    cur.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (uid,))
    recent_expenses = [dict(row) for row in cur.fetchall()]
    conn.close()

    return render_template('expenses.html', recent_expenses=recent_expenses)


@app.route('/incomes', methods=['GET', 'POST'])
@login_required
def incomes():
    # ensure incomes table exists (safe if DB already initialized)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source TEXT,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            date DATE DEFAULT (date('now')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()

    uid = current_user.id
    if request.method == 'POST':
        action = request.form.get('action', 'add')
        item_id = request.form.get('item_id')
        if action == 'add':
            source = request.form.get('source')
            amount = request.form.get('amount') or 0
            date = request.form.get('date')
            cur.execute("""
                INSERT INTO incomes (user_id, source, amount, date)
                VALUES (?, ?, ?, ?)
            """, (uid, source, amount, date))
            conn.commit()
        elif action == 'modify' and item_id:
            source = request.form.get('source')
            amount = request.form.get('amount') or 0
            date = request.form.get('date')
            cur.execute("""
                UPDATE incomes SET source = ?, amount = ?, date = ?
                WHERE id = ? AND user_id = ?
            """, (source, amount, date, item_id, uid))
            conn.commit()
        elif action == 'delete' and item_id:
            cur.execute("DELETE FROM incomes WHERE id = ? AND user_id = ?", (item_id, uid))
            conn.commit()
        return redirect(url_for('incomes'))

    # fetch recent incomes and wallet balance
    cur.execute("SELECT * FROM incomes WHERE user_id = ? ORDER BY date DESC LIMIT 10", (uid,))
    recent_incomes = [dict(row) for row in cur.fetchall()]
    cur.execute("SELECT SUM(amount) as total FROM incomes WHERE user_id = ?", (uid,))
    total_income = cur.fetchone()['total'] or 0.0
    # optionally subtract total expenses to present wallet balance
    cur.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = ?", (uid,))
    total_expenses = cur.fetchone()['total'] or 0.0
    wallet_balance = (total_income or 0.0) - (total_expenses or 0.0)

    conn.close()
    return render_template('incomes.html', recent_incomes=recent_incomes, wallet_balance=wallet_balance)

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/reminders')
@login_required
def reminders():
    return render_template('reminders.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

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


@app.route('/settings/account')
@login_required
def settings_account():
    # Render a dedicated account settings page (same fields as inline pane)
    return render_template('account.html')

if __name__ == '__main__':
    # Enable debug/reloader when SMARTAPP_DEV is set to 1 (safe for local dev only)
    debug_mode = os.environ.get('SMARTAPP_DEV', '0').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
