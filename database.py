import sqlite3
import datetime
import pandas as pd

def init_db():
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    # Companies tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            website TEXT,
            address TEXT,
            description TEXT,
            sector TEXT,
            country TEXT,
            company_size TEXT,
            created_at TEXT
        )
    """)
    # Contacts tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            email TEXT,
            phone TEXT,
            source TEXT,
            link TEXT,
            is_valid INTEGER,
            score INTEGER,
            created_at TEXT
        )
    """)
    # Managers tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS managers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            full_name TEXT,
            position TEXT,
            source TEXT,
            link TEXT,
            created_at TEXT
        )
    """)
    # Sent emails tablosu
    c.execute("""
        CREATE TABLE IF NOT EXISTS sent_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            email TEXT,
            subject TEXT,
            body TEXT,
            sent_at TEXT
        )
    """)
    # Replies tablosu (YENİ: auto_replied alanı eklenmiş!)
    c.execute("""
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            email TEXT,
            subject TEXT,
            body TEXT,
            received_at TEXT,
            auto_replied INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def company_exists(website, name, address):
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    c.execute("SELECT id FROM companies WHERE website=? OR (name=? AND address=?)", (website, name, address))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_company(company):
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO companies (name, website, address, description, sector, country, company_size, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (
                  company.get("name", ""),
                  company.get("website", ""),
                  company.get("address", ""),
                  company.get("description", ""),
                  company.get("sector", ""),
                  company.get("country", ""),
                  company.get("company_size", ""),
                  now
              ))
    company_id = c.lastrowid
    conn.commit()
    conn.close()
    return company_id

def save_contact(company_id, contact):
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute("""INSERT INTO contacts (company_id, email, phone, source, link, is_valid, score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (company_id, contact.get("email", ""), contact.get("phone", ""), contact.get("source", ""), contact.get("link", ""), contact.get("is_valid", 0), contact.get("score", 0), now)
    )
    conn.commit()
    conn.close()

def save_manager(company_id, manager):
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute("""INSERT INTO managers (company_id, full_name, position, source, link, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (company_id, manager.get("full_name", ""), manager.get("position", ""), manager.get("source", ""), manager.get("link", ""), now)
    )
    conn.commit()
    conn.close()

def get_all_contacts():
    conn = sqlite3.connect("firms.db")
    df = pd.read_sql("SELECT * FROM contacts", conn)
    conn.close()
    return df

def get_all_managers():
    conn = sqlite3.connect("firms.db")
    df = pd.read_sql("SELECT * FROM managers", conn)
    conn.close()
    return df

def get_valid_emails():
    conn = sqlite3.connect("firms.db")
    df = pd.read_sql("SELECT * FROM contacts WHERE is_valid=1 OR is_valid IS NULL", conn)
    conn.close()
    return df

def save_sent_mail(company_id, email, subject, body):
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    c.execute("INSERT INTO sent_emails (company_id, email, subject, body, sent_at) VALUES (?, ?, ?, ?, ?)",
              (company_id, email, subject, body, now))
    conn.commit()
    conn.close()

def last_sent_mail_date(company_id, email):
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    c.execute("SELECT sent_at FROM sent_emails WHERE company_id=? AND email=? ORDER BY sent_at DESC LIMIT 1", (company_id, email))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def save_reply(company_id, email, subject, body, received_at=None):
    if received_at is None:
        received_at = datetime.datetime.now().isoformat()
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    c.execute("INSERT INTO replies (company_id, email, subject, body, received_at, auto_replied) VALUES (?, ?, ?, ?, ?, 0)",
              (company_id, email, subject, body, received_at))
    conn.commit()
    conn.close()

def get_all_replies():
    conn = sqlite3.connect("firms.db")
    df = pd.read_sql("SELECT * FROM replies", conn)
    conn.close()
    return df

# YENİ: Otomatik cevaplandı işaretlemesi
def mark_reply_as_auto_replied(reply_id):
    conn = sqlite3.connect("firms.db")
    c = conn.cursor()
    c.execute("UPDATE replies SET auto_replied=1 WHERE id=?", (reply_id,))
    conn.commit()
    conn.close()
