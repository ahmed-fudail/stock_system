"""يبني قاعدة بيانات سريعة (stock_fast.db) من القاعدة الأصلية: بدون Price/Crcy + فهرس FTS5 trigram."""
import sqlite3, sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else "data/stock.db"
DST = sys.argv[2] if len(sys.argv) > 2 else "data/stock_fast.db"
if os.path.exists(DST):
    os.remove(DST)

src = sqlite3.connect(SRC)
dst = sqlite3.connect(DST)
dst.executescript("""
CREATE TABLE items(
    id INTEGER PRIMARY KEY,
    material_no TEXT NOT NULL,
    description TEXT NOT NULL,
    unit TEXT NOT NULL
);
""")
rows = (
    (str(m).strip(), (d or "").strip(), (u or "").strip())
    for m, d, u in src.execute('SELECT "Material No","Material description","Unit" FROM items')
)
dst.executemany("INSERT INTO items(material_no,description,unit) VALUES (?,?,?)", rows)
dst.executescript("""
CREATE VIRTUAL TABLE items_fts USING fts5(
    material_no, description,
    content='items', content_rowid='id',
    tokenize='trigram'
);
INSERT INTO items_fts(items_fts) VALUES('rebuild');
INSERT INTO items_fts(items_fts) VALUES('optimize');
""")
dst.commit()
dst.execute("VACUUM")
dst.close()
print("done:", DST, os.path.getsize(DST) // 1024 // 1024, "MB")
