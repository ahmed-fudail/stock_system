import os
import sqlite3
import zipfile

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "stock_fast.db")
ZIP_PATH = os.path.join(BASE_DIR, "stock.zip")

MAX_RESULTS = 50


def setup_database():
    """فك ضغط قاعدة البيانات عند أول تشغيل فقط."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        if os.path.exists(ZIP_PATH):
            with zipfile.ZipFile(ZIP_PATH, "r") as z:
                z.extractall(DATA_DIR)
            print("Database extracted successfully.")
        else:
            print("Warning: stock.zip not found!")


setup_database()


def get_conn():
    # قراءة فقط + mmap لتسريع القراءة
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, check_same_thread=False)
    conn.execute("PRAGMA mmap_size = 268435456")
    conn.execute("PRAGMA cache_size = -65536")
    return conn


CONN = get_conn() if os.path.exists(DB_PATH) else None


@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/image_d6ce3f.png")
def logo():
    return FileResponse(os.path.join(BASE_DIR, "image_d6ce3f.png"))


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/search")
def search(q: str = Query("", max_length=100)):
    if CONN is None:
        return {"error": "Database file not found"}

    terms = q.split()
    long_terms = [t for t in terms if len(t) >= 3]
    short_terms = [t for t in terms if len(t) < 3]

    # فهرس trigram يحتاج 3 أحرف على الأقل
    if not long_terms:
        return []

    # كل كلمة تُبحث كعبارة نصية (مع تحييد علامات الاقتباس) والنتائج يجب أن تحتوي على كل الكلمات
    match = " AND ".join('"' + t.replace('"', '""') + '"' for t in long_terms)

    sql = (
        "SELECT i.material_no, i.description, i.unit "
        "FROM items_fts f JOIN items i ON i.id = f.rowid "
        "WHERE items_fts MATCH ?"
    )
    params = [match]
    # الكلمات القصيرة (حرف/حرفان) تُطبق كفلتر إضافي على النتائج المحدودة
    for t in short_terms:
        sql += " AND (i.description LIKE ? OR i.material_no LIKE ?)"
        params += [f"%{t}%", f"%{t}%"]
    sql += f" LIMIT {MAX_RESULTS}"

    try:
        return CONN.execute(sql, params).fetchall()
    except Exception as e:
        return {"error": str(e)}
