import sqlite3
import hashlib
import os

DB_NAME = "vera_bakim.db"

# ---------------- DB CONNECTION ----------------
def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")  # Performans için WAL modunu açıyoruz
    return conn

# ---------------- PASSWORD HASH ----------------
def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(stored_password, provided_password):
    salt, hashed = stored_password.split("$")
    return hash_password(provided_password, salt) == stored_password

# ---------------- INIT DB ----------------
def init_db():
    conn = get_db()
    c = conn.cursor()

    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    # TALEPLER
    c.execute("""
    CREATE TABLE IF NOT EXISTS talepler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        mesaj TEXT,
        foto_yolu TEXT,
        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    #burda block list tutacagız
    c.execute("""
    CREATE TABLE IF NOT EXISTS blocked_ips (
        ip TEXT PRIMARY KEY,
        reason TEXT,
        risk_score INTEGER,
        created_at REAL,
        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Admin var mı kontrol et
    c.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    admin_exists = c.fetchone()

    if not admin_exists:
        admin_pass = hash_password("admin123")
        c.execute("INSERT INTO users VALUES (?, ?, ?)", ("admin", admin_pass, "admin"))

    conn.commit()
    conn.close()