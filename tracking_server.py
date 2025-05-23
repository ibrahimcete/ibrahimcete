# tracking_server.py
from flask import Flask, request, send_file
import sqlite3
import datetime
import os

app = Flask(__name__)

DB = "tracking.db"
PIXEL_PATH = "pixel.gif"

def log_open(email, campaign_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS opens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            campaign_id TEXT,
            opened_at TEXT
        )
    """)
    now = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO opens (email, campaign_id, opened_at) VALUES (?, ?, ?)",
              (email, campaign_id, now))
    conn.commit()
    conn.close()

@app.route("/open", methods=["GET"])
def open_pixel():
    email = request.args.get("email")
    campaign_id = request.args.get("cid")
    if email and campaign_id:
        log_open(email, campaign_id)
    # 1x1 transparent GIF (dosyan yoksa bir tane indir)
    if not os.path.exists(PIXEL_PATH):
        # Geçici olarak boş gif döndür
        from io import BytesIO
        return send_file(BytesIO(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF!\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'), mimetype="image/gif")
    return send_file(PIXEL_PATH, mimetype="image/gif")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
