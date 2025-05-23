import smtplib
from email.mime.text import MIMEText

# === TRACKING PIXEL FONKSİYONU ===
def append_tracking_pixel(mail_body, recipient_email, campaign_id):
    tracking_url = f"http://YOUR_SERVER_IP:8080/open?email={recipient_email}&cid={campaign_id}"
    tracking_img = f'<img src="{tracking_url}" width="1" height="1" style="display:none;" alt="">'
    if '</body>' in mail_body:
        mail_body = mail_body.replace('</body>', tracking_img + '</body>')
    else:
        mail_body += tracking_img
    return mail_body

# === MAIL GÖNDERME FONKSİYONU ===
def send_email(to_email, subject, body, from_email, smtp_server, smtp_port, smtp_user, smtp_pass, campaign_id=None):
    if campaign_id is not None:
        body = append_tracking_pixel(body, to_email, campaign_id)
    msg = MIMEText(body, "html")
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())
