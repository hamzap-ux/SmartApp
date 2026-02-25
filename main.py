from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-in-production'
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

    return render_template('index.html',
                           total_spending=total_spending,
                           active_subs=active_subs,
                           monthly_sub_cost=monthly_sub_cost,
                           upcoming_bills=upcoming_bills,
                           recent_expenses=recent_expenses,
                           upcoming_renewals=upcoming_renewals,
                           chart_data=chart_data)

@app.route('/subscriptions', methods=['GET', 'POST'])
@login_required
def subscriptions():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    uid = current_user.id

    if request.method == 'POST':
        name = request.form.get('name')
        provider = request.form.get('provider')
        amount = request.form.get('amount')
        billing_period = request.form.get('billing_period')
        next_renewal = request.form.get('next_renewal')

        cur.execute("""
            INSERT INTO subscriptions (user_id, name, provider, amount, billing_period, next_renewal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (uid, name, provider, amount, billing_period, next_renewal))
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
        description = request.form.get('description')
        category = request.form.get('category')
        amount = request.form.get('amount')
        date = request.form.get('date')

        cur.execute("""
            INSERT INTO expenses (user_id, description, category, amount, date)
            VALUES (?, ?, ?, ?, ?)
        """, (uid, description, category, amount, date))
        conn.commit()
        return redirect(url_for('expenses'))

    cur.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC", (uid,))
    recent_expenses = [dict(row) for row in cur.fetchall()]
    conn.close()

    return render_template('expenses.html', recent_expenses=recent_expenses)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
