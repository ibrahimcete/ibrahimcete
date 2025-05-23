import sqlite3

try:
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    c.execute("ALTER TABLE contacts ADD COLUMN link TEXT;")
    conn.commit()
    print("Tabloya 'link' sütunu eklendi.")
except Exception as e:
    print("Hata (muhtemelen sütun zaten var):", e)
finally:
    conn.close()
