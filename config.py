# config.py
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASS = os.getenv("LINKEDIN_PASS")

# SMTP Ayarları (env veya direkt burada)
SMTP_SERVER = os.getenv("SMTP_SERVER") or "smtp.gmail.com"
SMTP_PORT = int(os.getenv("SMTP_PORT") or 465)
SMTP_USER = os.getenv("SMTP_USER") or "youremail@gmail.com"
SMTP_PASS = os.getenv("SMTP_PASS") or "yourpassword"
FROM_EMAIL = os.getenv("FROM_EMAIL") or SMTP_USER
