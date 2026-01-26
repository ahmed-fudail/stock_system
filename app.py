import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
import sqlite3

app = FastAPI()

# هنا نقول لأمين المكتبة: ابحث عن قاعدة البيانات في مجلد اسمه data بجانبك
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "stock.db")

@app.get("/")
def home():
    return FileResponse("index.html")

@app.get("/search")
def search(q: str):
    q = q.strip().upper()
    # نفتح الملف ونقرأ منه ثم نغلقه بأمان
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT "Material No", "Material description", "Price", "Crcy", "Unit"
            FROM items
            WHERE CAST("Material No" AS TEXT) LIKE ? OR UPPER("Material description") LIKE ?
            LIMIT 50
        """, (f"%{q}%", f"%{q}%"))
        return cur.fetchall()
