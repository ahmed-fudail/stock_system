import os
import sqlite3
import zipfile
from functools import lru_cache

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="SAP Material Search")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "stock.db")
ZIP_PATH = os.path.join(BASE_DIR, "stock.zip")


def setup_database():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH) and os.path.exists(ZIP_PATH):
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(DATA_DIR)


setup_database()


def open_database():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA query_only = ON")
    conn.execute("PRAGMA temp_store = MEMORY")
    return conn


@lru_cache(maxsize=256)
def cached_search(term: str):
    like_term = f"%{term}%"
    with open_database() as conn:
        rows = conn.execute(
            '''
            SELECT "Material No", "Material description", "Unit"
            FROM items
            WHERE CAST("Material No" AS TEXT) LIKE ?
               OR "Material description" LIKE ? COLLATE NOCASE
            LIMIT 50
            ''',
            (like_term, like_term),
        ).fetchall()
    return rows


@app.get("/")
def home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(
        os.path.join(BASE_DIR, "manifest.webmanifest"),
        media_type="application/manifest+json",
    )


@app.get("/sw.js")
def service_worker():
    return FileResponse(
        os.path.join(BASE_DIR, "sw.js"),
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/image_d6ce3f.png")
def logo():
    return FileResponse(os.path.join(BASE_DIR, "image_d6ce3f.png"))


@app.get("/health")
def health():
    return {"status": "ok", "database": os.path.exists(DB_PATH)}


@app.get("/search")
def search(q: str = Query(min_length=2, max_length=100)):
    term = " ".join(q.strip().split()).upper()
    if len(term) < 2:
        return []
    if not os.path.exists(DB_PATH):
        return JSONResponse(
            status_code=503,
            content={"error": "Database is not available"},
        )
    try:
        return cached_search(term)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
