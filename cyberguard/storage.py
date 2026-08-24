"""SQLite persistence for users, roles, labs, authorizations and audit logs."""
import sqlite3
from contextlib import contextmanager

class Storage:
    def __init__(self, path="cyberguard.db"):
        self.path = path

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path)
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def init(self):
        with self.connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                role TEXT NOT NULL DEFAULT 'user',
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS labs (
                lab_id TEXT PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                state TEXT NOT NULL DEFAULT 'created',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS authorizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target TEXT NOT NULL,
                scope TEXT NOT NULL,
                start_at TEXT,
                end_at TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)

    def ensure_user(self, user_id, role="user"):
        with self.connect() as con:
            con.execute("INSERT OR IGNORE INTO users(telegram_id, role) VALUES (?, ?)", (user_id, role))

    def set_role(self, user_id, role):
        with self.connect() as con:
            con.execute("UPDATE users SET role=? WHERE telegram_id=?", (role, user_id))

    def role(self, user_id):
        with self.connect() as con:
            row = con.execute("SELECT role FROM users WHERE telegram_id=?", (user_id,)).fetchone()
        return row[0] if row else "user"

    def audit(self, user_id, action, details=""):
        with self.connect() as con:
            con.execute("INSERT INTO audit_logs(user_id, action, details) VALUES (?, ?, ?)", (user_id, action, details))

    def users(self):
        with self.connect() as con:
            return con.execute("SELECT telegram_id, role, first_seen FROM users ORDER BY first_seen DESC").fetchall()

    def audits(self, limit=50):
        with self.connect() as con:
            return con.execute("SELECT user_id, action, details, created_at FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
