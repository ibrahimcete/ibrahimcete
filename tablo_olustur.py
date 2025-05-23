import sqlite3

conn = sqlite3.connect("veritabani.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS firmalar (
    ad TEXT,
    tur TEXT,
    mail TEXT,
    tel TEXT
)
""")
conn.commit()
conn.close()
print("Tablo oluşturuldu veya zaten vardı!")