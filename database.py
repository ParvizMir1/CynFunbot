import sqlite3
from config import DB_NAME


def get_conn():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_conn() as conn:
        print('Connection to db')
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'ru'
        )''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            emoji TEXT,
            title_ru TEXT,
            title_en TEXT,
            title_gr TEXT
        )''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            category_id INTEGER,
            title_ru TEXT,
            title_en TEXT,
            title_gr TEXT,
            city TEXT,
            desc_ru TEXT,
            desc_en TEXT,
            desc_gr TEXT,
            price_from REAL,
            price_to REAL,
            gmap_url TEXT,
            booking_url TEXT,
            contact TEXT,
            image_url TEXT,
            is_published BOOLEAN,
            created_at TEXT
        )''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            payload TEXT,
            timestamp TEXT,
            lang TEXT
        )''')
        conn.commit()
