# website_scanner.py
import requests
from bs4 import BeautifulSoup
import re

# (Selenium için)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

KEYWORDS = [
    "about", "team", "hakkimizda", "ekibimiz",
    "contact", "iletisim", "impressum"
]

def find_relevant_pages(base_url):
    # Eski sabit sayfaları kontrol et:
    found_pages = []
    for kw in KEYWORDS:
        try:
            resp = requests.get(f"{base_url.rstrip('/')}/{kw}")
            if resp.status_code == 200:
                found_pages.append(f"{base_url.rstrip('/')}/{kw}")
        except Exception:
            continue
    # Ana sayfadaki tüm linkleri de al:
    try:
        resp = requests.get(base_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        for link in links:
            if link.startswith("/") and not link.startswith("//"):
                link = base_url.rstrip('/') + link
            if link.startswith(base_url) and link not in found_pages:
                found_pages.append(link)
    except Exception:
        pass
    # sitemap.xml ile tarama:
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/sitemap.xml")
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "xml")
            for loc in soup.find_all("loc"):
                url = loc.text
                if url not in found_pages:
                    found_pages.append(url)
    except Exception:
        pass
    return list(set(found_pages))

def scan_page_for_contacts(url, use_selenium=False):
    try:
        if use_selenium:
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            text = driver.page_source
            driver.quit()
        else:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(" ", strip=True)
    except Exception:
        return {"emails": [], "phones": [], "url": url}
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phones = re.findall(r"\+?\d[\d\-\(\) ]{8,}\d", text)
    return {
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "url": url
    }
