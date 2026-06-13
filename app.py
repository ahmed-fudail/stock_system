import os
import sqlite3
import zipfile
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

# المسارات الديناميكية المتوافقة مع Render وأي بيئة تشغيل أخرى
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data") # تم التعديل هنا لإنشاء المجلد داخل المشروع
DB_PATH = os.path.join(DATA_DIR, "stock.db")
ZIP_PATH = os.path.join(BASE_DIR, "stock.zip")

# وظيفة التأكد من قاعدة البيانات عند بدء التشغيل
def setup_database():
    # 1. إنشاء مجلد data إذا لم يكن موجوداً
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # 2. إذا لم تكن قاعدة البيانات موجودة، ابحث عن الملف المضغوط وفكه
    if not os.path.exists(DB_PATH):
        if os.path.exists(ZIP_PATH):
            with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
                # نفك الضغط مباشرة داخل مجلد data
                zip_ref.extractall(DATA_DIR)
            print("Database extracted successfully.")
        else:
            print("Warning: stock.zip not found!")

# تشغيل الإعداد قبل بدء السيرفر
setup_database()

@app.get("/")
def home():
    return FileResponse("index.html")

@app.get("/search")
def search(q: str):
    q = q.strip().upper()
    if not os.path.exists(DB_PATH):
        return {"error": "Database file not found at " + DB_PATH}
        
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT "Material No", "Material description", "Price", "Crcy", "Unit"
                FROM items
                WHERE CAST("Material No" AS TEXT) LIKE ? OR UPPER("Material description") LIKE ?
                LIMIT 50
            """, (f"%{q}%", f"%{q}%"))
            return cur.fetchall()
    except Exception as e:
        return {"error": str(e)}
