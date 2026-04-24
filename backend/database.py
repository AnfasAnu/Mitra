import sqlite3
import hashlib
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Personal profile information — saved so notifications can be personalized
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            username TEXT PRIMARY KEY,
            email TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            income INTEGER DEFAULT 0,
            category TEXT DEFAULT '',
            district TEXT DEFAULT '',
            age INTEGER DEFAULT 0,
            gender TEXT DEFAULT '',
            occupation TEXT DEFAULT '',
            education TEXT DEFAULT '',
            disability INTEGER DEFAULT 0,
            marital_status TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    # General preferences / app settings — separate from personal info
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            username TEXT PRIMARY KEY,
            preferred_language TEXT DEFAULT 'ml-IN',
            preferred_speaker TEXT DEFAULT 'anila',
            notifications_enabled INTEGER DEFAULT 1,
            auto_translate INTEGER DEFAULT 0,
            theme TEXT DEFAULT 'dark',
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True
    return False


# ── Personal Profile (User Settings) ──

def save_profile(username: str, profile: dict) -> bool:
    """Save or update user personal profile data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_profiles (username, email, phone, income, category, district, age, gender, occupation, education, disability, marital_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                email=excluded.email,
                phone=excluded.phone,
                income=excluded.income,
                category=excluded.category,
                district=excluded.district,
                age=excluded.age,
                gender=excluded.gender,
                occupation=excluded.occupation,
                education=excluded.education,
                disability=excluded.disability,
                marital_status=excluded.marital_status
        ''', (
            username,
            profile.get("email", ""),
            profile.get("phone", ""),
            profile.get("income", 0),
            profile.get("category", ""),
            profile.get("district", ""),
            profile.get("age", 0),
            profile.get("gender", ""),
            profile.get("occupation", ""),
            profile.get("education", ""),
            1 if profile.get("disability", False) else 0,
            profile.get("marital_status", ""),
        ))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def load_profile(username: str) -> dict:
    """Load user personal profile data. Returns empty dict if not found."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profiles WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "username": row[0],
            "email": row[1],
            "phone": row[2],
            "income": row[3],
            "category": row[4],
            "district": row[5],
            "age": row[6],
            "gender": row[7],
            "occupation": row[8],
            "education": row[9],
            "disability": bool(row[10]),
            "marital_status": row[11],
            "created_at": row[12],
        }
    return {}
 
def delete_profile(username: str) -> bool:
    """Delete user personal profile data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_profiles WHERE username = ?", (username,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


# ── General Preferences (General Settings) ──

def save_preferences(username: str, prefs: dict) -> bool:
    """Save or update user general preferences/settings."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_preferences (username, preferred_language, preferred_speaker, notifications_enabled, auto_translate, theme)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                preferred_language=excluded.preferred_language,
                preferred_speaker=excluded.preferred_speaker,
                notifications_enabled=excluded.notifications_enabled,
                auto_translate=excluded.auto_translate,
                theme=excluded.theme
        ''', (
            username,
            prefs.get("preferred_language", "ml-IN"),
            prefs.get("preferred_speaker", "anila"),
            1 if prefs.get("notifications_enabled", True) else 0,
            1 if prefs.get("auto_translate", False) else 0,
            prefs.get("theme", "dark"),
        ))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def load_preferences(username: str) -> dict:
    """Load user general preferences. Returns empty dict if not found."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_preferences WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "username": row[0],
            "preferred_language": row[1],
            "preferred_speaker": row[2],
            "notifications_enabled": bool(row[3]),
            "auto_translate": bool(row[4]),
            "theme": row[5],
        }
    return {}
