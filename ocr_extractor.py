# ocr_extractor.py
import pytesseract
from PIL import Image
import re

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception:
        return ""

def extract_contacts_from_text(text):
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phones = re.findall(r"\+?\d[\d\-\(\) ]{8,}\d", text)
    return {
        "emails": list(set(emails)),
        "phones": list(set(phones)),
    }
