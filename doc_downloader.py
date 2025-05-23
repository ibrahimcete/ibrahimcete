# doc_downloader.py
import requests
from bs4 import BeautifulSoup
import os

DOC_TYPES = ["pdf", "doc", "docx", "xls", "xlsx", "jpg", "jpeg", "png"]

def find_and_download_documents(base_url, out_dir="downloaded_docs"):
    try:
        os.makedirs(out_dir, exist_ok=True)
        resp = requests.get(base_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = [a.get('href') for a in soup.find_all('a', href=True)]
    except Exception:
        return []
    downloaded = []
    for link in links:
        if any(link.lower().endswith(ext) for ext in DOC_TYPES):
            file_url = link if link.startswith("http") else base_url.rstrip("/") + "/" + link.lstrip("/")
            try:
                file_data = requests.get(file_url).content
                filename = os.path.join(out_dir, file_url.split("/")[-1])
                with open(filename, "wb") as f:
                    f.write(file_data)
                downloaded.append(filename)
            except Exception:
                continue
    return downloaded
