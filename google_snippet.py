# google_snippet.py
import requests
from bs4 import BeautifulSoup
import os
import time
import openai

def google_snippet_search(query, max_results=5, sleep_sec=2):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    }
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    results = []
    for g in soup.find_all("div", class_="g")[:max_results]:
        title = g.find("h3")
        snippet = g.find("span", class_="aCOpRe")
        link = g.find("a", href=True)
        if title and link:
            results.append({
                "title": title.get_text(strip=True),
                "snippet": snippet.get_text(strip=True) if snippet else "",
                "link": link['href']
            })
        time.sleep(sleep_sec)  # bot blok riskini azaltmak için
    return results

def gpt_snippet_analysis(snippets, firm_name):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = (
        f"Aşağıda {firm_name} hakkında Google'dan elde edilen arama sonuçları var:\n"
        + "\n".join(f"Başlık: {r['title']}\nSnippet: {r['snippet']}\nLink: {r['link']}\n" for r in snippets)
        + "\nBu verilerden varsa firma çalışan adı, pozisyonu, e-posta ve telefonları maddeler halinde çıkar:"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

# Test kodu:
if __name__ == "__main__":
    firm_adi = "BeLaMa Matratzen Berlin"
    domain = "belama.de"
    dork = f'"{firm_adi}" site:{domain} (mail OR contact OR iletişim OR ceo OR sales OR email)'
    results = google_snippet_search(dork, max_results=3)
    for r in results:
        print("Başlık:", r["title"])
        print("Snippet:", r["snippet"])
        print("Link:", r["link"])
        print("-----")
    analysis = gpt_snippet_analysis(results, firm_adi)
    print(analysis)
