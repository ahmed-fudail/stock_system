from fastapi import FastAPI
from fastapi.responses import FileResponse
import sqlite3

app = FastAPI()

# المسار الكامل لقاعدة البيانات
DB_PATH = r"D:\sharing file\stock_system\stock.db"

# صفحة الواجهة الرئيسية
@app.get("/")
def home():
    return FileResponse("index.html")

# دالة البحث الذكي
@app.get("/search")
def search(q: str):
    q = q.strip().upper()  # إزالة الفراغات وتحويل النص لأحرف كبيرة
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT
        "Material No",
        "Material description",
        "Price",
        "Crcy",
        "Unit"
    FROM items
    WHERE
        CAST("Material No" AS TEXT) LIKE ?
        OR UPPER("Material description") LIKE ?
    LIMIT 50
    """, (f"%{q}%", f"%{q}%"))

    rows = cur.fetchall()
    conn.close()
    return rows
