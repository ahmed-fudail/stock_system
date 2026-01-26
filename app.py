import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
import sqlite3

app = FastAPI()

# تصحيح المسار ليعمل داخل بيئة Railway (مجلد data المحمي بالـ Volume)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# هذا المسار يضمن أن البرنامج يقرأ الملف بعد فك ضغطه داخل مجلد data
DB_PATH = "/app/data/stock.db"

# صفحة الواجهة الرئيسية
@app.get("/")
def home():
    # التأكد من وجود ملف index.html في نفس المجلد
    return FileResponse("index.html")

# دالة البحث الذكي
@app.get("/search")
def search(q: str):
    q = q.strip().upper()  # إزالة الفراغات وتحويل النص لأحرف كبيرة
    
    # استخدام with لضمان فتح وإغلاق قاعدة البيانات تلقائياً حتى لا يحدث تعليق للسيرفر
    try:
        with sqlite3.connect(DB_PATH) as conn:
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
            return rows
    except Exception as e:
        return {"error": str(e)}
