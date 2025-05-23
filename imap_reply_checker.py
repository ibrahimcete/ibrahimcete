import imaplib
import email
from email.header import decode_header
import datetime
from database import get_all_contacts, save_reply

# Ayarları config.py veya .env'den çekebilirsin:
IMAP_SERVER = "imap.gmail.com"           # Outlook için: "outlook.office365.com"
IMAP_USER = "youremail@example.com"
IMAP_PASS = "your_password"

def connect_imap(server, user, password, folder="INBOX"):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(user, password)
    mail.select(folder)
    return mail

def search_replies(mail, since_days=7):
    # Son x günün mailini getir
    date = (datetime.datetime.now() - datetime.timedelta(days=since_days)).strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'(SINCE "{date}")')
    reply_list = []
    for num in messages[0].split():
        status, data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="replace")
        from_addr = email.utils.parseaddr(msg.get("From"))[1]
        in_reply_to = msg.get("In-Reply-To", "")
        references = msg.get("References", "")
        if in_reply_to or references:
            reply_list.append({
                "from": from_addr,
                "subject": subject,
                "date": msg.get("Date"),
                "body": get_body_from_msg(msg)
            })
    return reply_list

def get_body_from_msg(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in disp:
                charset = part.get_content_charset() or "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="replace")
                break
    else:
        charset = msg.get_content_charset() or "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")
    return body

def log_replies_to_db(reply_list):
    contacts = get_all_contacts()
    for reply in reply_list:
        # Gelen cevaptaki from adresi ile kontağı eşle
        row = contacts[contacts['email'] == reply['from']]
        company_id = int(row.iloc[0]['company_id']) if not row.empty else None
        save_reply(
            company_id=company_id,
            email=reply['from'],
            subject=reply['subject'],
            body=reply['body'],
            received_at=reply['date']
        )

if __name__ == "__main__":
    mail = connect_imap(IMAP_SERVER, IMAP_USER, IMAP_PASS)
    replies = search_replies(mail, since_days=7)
    print(f"{len(replies)} yeni yanıt bulundu.")
    log_replies_to_db(replies)
    print("Tüm yanıtlar veritabanına kaydedildi.")
