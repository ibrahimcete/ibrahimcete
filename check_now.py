import sqlite3
conn = sqlite3.connect('tracking.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM email_tracking")
total = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM email_tracking WHERE opened = 1")
opened = cursor.fetchone()[0]
print(f"Toplam email: {total}")
print(f"Açılan email: {opened}")
if total > 0:
    cursor.execute("SELECT tracking_id, to_email, opened, open_count FROM email_tracking ORDER BY sent_at DESC LIMIT 1")
    row = cursor.fetchone()
    print(f"\nSon email:")
    print(f"  Email: {row[1]}")
    print(f"  Durum: {'AÇILDI ✅' if row[2] else 'BEKLİYOR ⏳'}")
    print(f"  Açılma: {row[3]}x")
conn.close()

