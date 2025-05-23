# tracking_utils.py
import sqlite3

def check_opened(email, campaign_id):
    conn = sqlite3.connect("tracking.db")
    c = conn.cursor()
    c.execute("SELECT * FROM opens WHERE email=? AND campaign_id=?", (email, campaign_id))
    result = c.fetchone()
    conn.close()
    return result is not None
