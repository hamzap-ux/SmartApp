CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    renewal_date TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    expense_date TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    remind_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
