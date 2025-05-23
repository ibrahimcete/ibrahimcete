import imaplib
import email
from email.header import decode_header
import re
from database import get_all_contacts, save_contact

# Ayarları config.py veya .env'den çekebilirsin:
IMAP_SERVER = "imap.gmail.com"           # Outlook için: "outlook.office365.com"
IMAP_USER = "youremail@example.com"
IMAP_PASS = "yourpassword"

def find_bounced_emails(imap_server, imap_user, imap_pass, since_days=7):
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(imap_user, imap_pass)
    mail.select("INBOX")
    # "MAILER-DAEMON" veya tipik bounce başlıklarını filtrele
    status, messages = mail.search(
        None, '(FROM "MAILER-DAEMON" SUBJECT "Undelivered" SUBJECT "Delivery Status" SUBJECT "not delivered")'
    )
    bounced = set()
    for num in messages[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                text = part.get_payload(decode=True).decode(errors="ignore")
                emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
                for e in emails:
                    bounced.add(e.lower())
    return bounced

def mark_bounced_emails_as_invalid(bounced_emails):
    contacts = get_all_contacts()
    for _, row in contacts.iterrows():
        if row["email"] and row["email"].lower() in bounced_emails:
            # is_valid=0 olarak blacklist et
            save_contact(row["company_id"], {
                "email": row["email"],
                "phone": row["phone"],
                "source": row["source"],
                "link": row["link"],
                "is_valid": 0,
                "score": row.get("score", 0)
            })
            print(f"[BLACKLIST] {row['email']} geçersiz olarak işaretlendi!")

if __name__ == "__main__":
    bounced = find_bounced_emails(IMAP_SERVER, IMAP_USER, IMAP_PASS)
    print("Bulunan bounce adresler:", bounced)
    mark_bounced_emails_as_invalid(bounced)
    print("Bounce adresler blacklistlendi (is_valid=0)")
