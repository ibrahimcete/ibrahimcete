# social_scanner.py
import requests
from bs4 import BeautifulSoup
import re

# Sosyal medya URL'lerini tespit edecek regex'ler
SOCIAL_PLATFORMS = {
    "linkedin": re.compile(r"https?://(www\.)?linkedin\.com/[^\s'\"<>]+"),
    "facebook": re.compile(r"https?://(www\.)?facebook\.com/[^\s'\"<>]+"),
    "instagram": re.compile(r"https?://(www\.)?instagram\.com/[^\s'\"<>]+"),
    "twitter": re.compile(r"https?://(www\.)?twitter\.com/[^\s'\"<>]+"),
    "tiktok": re.compile(r"https?://(www\.)?tiktok\.com/@[^\s'\"<>]+")
}

def find_social_links(base_url):
    """
    Bir web sitesindeki sosyal medya linklerini otomatik olarak tespit eder.
    Dönüş: {'linkedin': [...], 'facebook': [...], ...}
    """
    try:
        resp = requests.get(base_url, timeout=10)
        html = resp.text
    except Exception as e:
        print(f"[ERROR] Web sitesi çekilemedi: {e}")
        return {}

    social_links = {}
    for platform, regex in SOCIAL_PLATFORMS.items():
        links = set(m.group(0) for m in regex.finditer(html))
        if links:
            social_links[platform] = list(links)
    return social_links

# ÖRNEK: Instagram bio çekme
def get_instagram_bio(insta_url):
    """
    Instagram profilinden bio (açıklama) bilgisini çeker.
    """
    try:
        resp = requests.get(insta_url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Çoğunlukla <meta property="og:description">'da bulunur
        meta = soup.find("meta", property="og:description")
        if meta and meta.get("content"):
            return meta["content"]
    except Exception as e:
        print(f"[ERROR] Instagram scraping error: {e}")
    return ""

# Geliştirerek facebook, twitter için benzer bio/contact fonksiyonları ekleyebilirsin.

if __name__ == "__main__":
    # Test amaçlı:
    url = "https://www.razzoni.com"  # Kendi denemek istediğin siteyi yazabilirsin
    socials = find_social_links(url)
    print(socials)
    if "instagram" in socials:
        for insta in socials["instagram"]:
            bio = get_instagram_bio(insta)
            print("Instagram bio:", bio)
