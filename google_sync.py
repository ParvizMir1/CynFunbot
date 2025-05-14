import gspread
from oauth2client.service_account import ServiceAccountCredentials
from database import get_conn
from datetime import datetime

CREDS_FILE = 'credentials.json'

# ID таблиц
EVENTS_SHEET_ID = '10i2sJ2YgJvjFt_8MuscBgRz3ETolujstaA7dZUMzZrw'
CATEGORIES_SHEET_ID = '1C6KZOKXowiVnShtYtdfkwcSt5bx9A7EJLlA-BRFASkU'


def sync_data():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)

    categories_ws = client.open_by_key(CATEGORIES_SHEET_ID).sheet1
    events_ws = client.open_by_key(EVENTS_SHEET_ID).sheet1

    sync_categories(categories_ws)
    sync_events(events_ws)


def sync_categories(ws):
    rows = ws.get_all_records()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM categories")
        for row in rows:
            cur.execute('''
                INSERT INTO categories (id, emoji, title_ru, title_en, title_gr)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['id'], row['emoji'], row['title_ru'], row['title_en'], row['title_gr']))
        conn.commit()
    print(f"[{datetime.now()}] ✅ Categories synced: {len(rows)}")


def sync_events(ws):
    rows = ws.get_all_records()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM events")
        for row in rows:
            cur.execute('''
                INSERT INTO events (
                    id, category_id, title_ru, title_en, title_gr,
                    city, desc_ru, desc_en, desc_gr, price_from, price_to,
                    gmap_url, booking_url, contact, image_url,
                    is_published, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['id'], row['category_id'], row['title_ru'], row['title_en'], row['title_gr'],
                row['city'], row['desc_ru'], row['desc_en'], row['desc_gr'],
                row['price_from'], row.get('price_to'),
                row['gmap_url'], row.get('booking_url'), row.get('contact'), row['image_url'],
                int(row['is_published']), row['created_at']
            ))
        conn.commit()
    print(f"[{datetime.now()}] ✅ Events synced: {len(rows)}")


if __name__ == "__main__":
    sync_data()
