import os
from database import get_all_replies, mark_reply_as_auto_replied
from ai_enricher import generate_auto_reply
from mail_sender import send_email
from config import FROM_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS

import pandas as pd

def auto_reply_to_new_replies(your_company="KendiFirman"):
    replies = get_all_replies()
    if replies.empty:
        print("Hiç yeni reply bulunamadı.")
        return

    # Sadece daha önce otomatik cevaplanmamış olanlar!
    new_replies = replies[replies["auto_replied"].fillna(0) == 0]

    for idx, row in new_replies.iterrows():
        customer_message = row["body"]
        company_id = row["company_id"]
        email = row["email"]
        subject = row["subject"] or "İş Birliği Talebiniz"
        reply_id = row["id"]
        # (İsteğe bağlı) Şirket adını ana firmalar tablosundan çekmek istersen burada ekleyebilirsin.

        # AI ile yanıtı üret:
        company_name = "FirmaAdı"  # istersen DB'den şirket adını çekebilirsin!
        ai_reply = generate_auto_reply(customer_message, company_name, your_company)

        # E-postayı gönder:
        send_email(
            to_email=email,
            subject="RE: " + subject,
            body=ai_reply,
            from_email=FROM_EMAIL,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            smtp_user=SMTP_USER,
            smtp_pass=SMTP_PASS
        )
        # Cevaplandığını işaretle!
        mark_reply_as_auto_replied(reply_id)
        print(f"[AUTO-REPLY] {email} adresine otomatik yanıt gönderildi.")

if __name__ == "__main__":
    auto_reply_to_new_replies()
