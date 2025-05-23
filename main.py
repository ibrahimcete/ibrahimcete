from config import *
from maps_fetcher import fetch_from_all_sources
from website_scanner import find_relevant_pages, scan_page_for_contacts
from doc_downloader import find_and_download_documents
from ocr_extractor import extract_text_from_image, extract_contacts_from_text
from ai_enricher import (
    enrich_with_ai, make_reminder_prompt, make_segmented_prompt, generate_email_text
)
from database import (
    init_db, save_company, save_contact, save_manager,
    get_all_contacts, get_all_managers, get_valid_emails,
    company_exists, save_sent_mail, last_sent_mail_date
)
from utils import print_header
from social_scanner import find_social_links, get_instagram_bio
from linkedin_scraper import get_linkedin_contact_info
from google_snippet import google_snippet_search, gpt_snippet_analysis
from report_exporter import export_contacts_to_excel, export_contacts_to_csv
from mail_sender import send_email
from tracking_utils import check_opened

import re, os, datetime, time

def days_since(date_str):
    if not date_str:
        return 9999
    dt = datetime.datetime.fromisoformat(date_str)
    return (datetime.datetime.now() - dt).days

def extract_managers_from_text(text, company_id, source, link):
    import re
    pattern = re.compile(r"([A-ZÇĞİÖŞÜa-zçğıöşü'\s\-.]+)[–\-:|]+([A-ZÇĞİÖŞÜa-zçğıöşü'\s\-.]+)")
    for line in text.split('\n'):
        m = pattern.search(line)
        if m:
            name, position = m.group(1).strip(), m.group(2).strip()
            save_manager(company_id, {
                "full_name": name,
                "position": position,
                "source": source,
                "link": link
            })

# ---- ANA PIPELINE: FULL B2B ÇEKİM & OTOMATİK MAIL ----
def full_b2b_pipeline(mode, location, sector, num_firm):
    logs = []
    init_db()
    companies = fetch_from_all_sources(sector, location, num_firm)
    logs.append(f"{len(companies)} firma bulundu.")
    LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASS = os.getenv("LINKEDIN_PASS")
    for company in companies:
        if company_exists(company.get("website", ""), company.get("name", ""), company.get("address", "")):
            logs.append(f"Bu firma zaten sistemde: {company['name']} -> Atlanıyor...")
            continue
        if mode and mode.lower() not in company["name"].lower():
            continue
        logs.append(f"\n====== {company['name']} ======\n")
        company_id = save_company(company)
        base_url = company.get("website")
        if not base_url:
            logs.append("Web sitesi yok, atlanıyor...")
            continue

        # 1. Sosyal Medya
        social_links = find_social_links(base_url)
        if social_links:
            logs.append("[Sosyal Medya Linkleri]")
            for platform, links in social_links.items():
                logs.append(f"- {platform}: {links}")
        else:
            logs.append("[INFO] Sosyal medya linki bulunamadı.")
        if "instagram" in social_links:
            for insta_url in social_links["instagram"]:
                bio = get_instagram_bio(insta_url)
                logs.append(f"[Instagram Bio] {insta_url}: {bio}")
                emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", bio)
                for email in emails:
                    save_contact(company_id, {
                        "email": email, "phone": "", "source": "instagram", "link": insta_url
                    })
                    logs.append(f"[INSTAGRAM] {email} (bio: {insta_url})")
                extract_managers_from_text(bio, company_id, "instagram", insta_url)
        if "linkedin" in social_links and LINKEDIN_EMAIL and LINKEDIN_PASS:
            for li_url in social_links["linkedin"]:
                screenshot_path = f"screenshots/{company['name']}_linkedin_contact.png"
                os.makedirs("screenshots", exist_ok=True)
                get_linkedin_contact_info(li_url, LINKEDIN_EMAIL, LINKEDIN_PASS, screenshot_path=screenshot_path)

        # 2. Web ve Alt Sayfalar
        pages = find_relevant_pages(base_url)
        full_text = ""
        for page in pages:
            contacts = scan_page_for_contacts(page)
            for email in contacts["emails"]:
                save_contact(company_id, {
                    "email": email, "phone": "", "source": "web", "link": page
                })
                logs.append(f"[WEB] {email} (source: {page})")
            for phone in contacts["phones"]:
                save_contact(company_id, {
                    "email": "", "phone": phone, "source": "web", "link": page
                })
            extract_managers_from_text(contacts.get("text", ""), company_id, "web", page)
            full_text += " ".join(contacts["emails"] + contacts["phones"]) + " "

        # 3. Doküman ve OCR
        docs = find_and_download_documents(base_url)
        for doc in docs:
            if doc.lower().endswith((".jpg", ".jpeg", ".png", ".pdf")):
                text = extract_text_from_image(doc)
                contacts = extract_contacts_from_text(text)
                for email in contacts["emails"]:
                    save_contact(company_id, {
                        "email": email, "phone": "", "source": "ocr", "link": doc
                    })
                    logs.append(f"[OCR] {email} (from: {doc})")
                for phone in contacts["phones"]:
                    save_contact(company_id, {
                        "email": "", "phone": phone, "source": "ocr", "link": doc
                    })
                extract_managers_from_text(text, company_id, "ocr", doc)

        # 4. AI Enrichment
        if full_text.strip():
            ai_out = enrich_with_ai(full_text)
            logs.append(f"[AI] {ai_out}")
            ai_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", ai_out)
            ai_phones = re.findall(r"\+?\d[\d\-\(\) ]{8,}\d", ai_out)
            for email in ai_emails:
                save_contact(company_id, {
                    "email": email, "phone": "", "source": "ai", "link": base_url
                })
            for phone in ai_phones:
                save_contact(company_id, {
                    "email": "", "phone": phone, "source": "ai", "link": base_url
                })
            extract_managers_from_text(ai_out, company_id, "ai", base_url)

        # 5. Google Snippet + GPT Analiz
        firm_name = company.get("name")
        domain = company.get("website", "")
        if firm_name and domain:
            dork = f'"{firm_name}" site:{domain} (mail OR contact OR iletişim OR ceo OR sales OR email)'
            logs.append(f"[SNIPPET] Google araması başlatılıyor: {dork}")
            snippets = google_snippet_search(dork, max_results=3)
            for snip in snippets:
                logs.append(f"[GOOGLE] {snip['title']} | {snip['snippet']} ({snip['link']})")
            if snippets:
                gpt_out = gpt_snippet_analysis(snippets, firm_name)
                logs.append(f"[GPT Snippet Analiz]\n{gpt_out}")
                snippet_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", gpt_out)
                snippet_phones = re.findall(r"\+?\d[\d\-\(\) ]{8,}\d", gpt_out)
                for email in snippet_emails:
                    save_contact(company_id, {
                        "email": email, "phone": "", "source": "snippet_gpt", "link": "google.com"
                    })
                for phone in snippet_phones:
                    save_contact(company_id, {
                        "email": "", "phone": phone, "source": "snippet_gpt", "link": "google.com"
                    })
                extract_managers_from_text(gpt_out, company_id, "snippet_gpt", "google.com")

        # 6. E-posta gönderim & Takip
        all_contacts = get_all_contacts()
        firm_contacts = all_contacts[(all_contacts["company_id"] == company_id) & ((all_contacts["is_valid"].isnull()) | (all_contacts["is_valid"] == 1))]
        personal_email_row = None
        general_email_row = None
        for _, row in firm_contacts.iterrows():
            email = row["email"]
            if email and "@" in email:
                if not email.lower().startswith(("info@", "contact@", "sales@", "iletisim@", "admin@", "support@", "mail@")):
                    personal_email_row = row
                    break
        if not personal_email_row and not firm_contacts.empty:
            general_email_row = firm_contacts.iloc[0]
        is_personal = personal_email_row is not None
        target_row = personal_email_row if is_personal else general_email_row
        if target_row is not None:
            to_email = target_row["email"]
            last_sent = last_sent_mail_date(company_id, to_email)
            enough_days = days_since(last_sent) >= 5
            managers = get_all_managers()
            firm_managers = managers[managers["company_id"] == company_id]
            name = position = ""
            if is_personal and not firm_managers.empty:
                mgr_row = firm_managers.iloc[0]
                name = mgr_row.get("full_name", "")
                position = mgr_row.get("position", "")
            company_name = company.get("name", "")
            website = company.get("website", "")
            summary = company.get("description", "") or "Uluslararası yatak ve uyku ürünleri alanında faaliyet gösteriyoruz."
            country = company.get("country", "")
            company_size = company.get("company_size", "")
            campaign_id = f"{company_id}_{target_row['id']}_{int(time.time())}"
            sector_use = company.get("sector", sector)
            if not last_sent:
                prompt, language = make_segmented_prompt(name, company_name, country, sector_use, company_size, summary)
                mail_body = generate_email_text(prompt)
                subject = f"{company_name} ile İş Birliği Fırsatı" if language == "tr" else f"Partnership Opportunity with {company_name}"
                mail_body = mail_body + f'<img src="http://YOUR_SERVER_IP:8080/open?email={to_email}&cid={campaign_id}" width="1" height="1" style="display:none">'
                try:
                    send_email(
                        to_email=to_email,
                        subject=subject,
                        body=mail_body,
                        from_email=FROM_EMAIL,
                        smtp_server=SMTP_SERVER,
                        smtp_port=SMTP_PORT,
                        smtp_user=SMTP_USER,
                        smtp_pass=SMTP_PASS,
                        campaign_id=campaign_id
                    )
                    save_sent_mail(company_id, to_email, subject, mail_body)
                    logs.append(f"[EMAIL-İLK] {to_email} adresine ilk tanıtım maili gönderildi.")
                except Exception as e:
                    logs.append(f"[HATA] İlk mail gönderilemedi: {to_email} ({e})")
            elif enough_days:
                reminder_prompt = make_reminder_prompt(name or "Yetkili", company_name, website, language)
                mail_body = generate_email_text(reminder_prompt)
                subject = f"{company_name} - Kısa Hatırlatma"
                mail_body = mail_body + f'<img src="http://YOUR_SERVER_IP:8080/open?email={to_email}&cid={campaign_id}_reminder" width="1" height="1" style="display:none">'
                try:
                    send_email(
                        to_email=to_email,
                        subject=subject,
                        body=mail_body,
                        from_email=FROM_EMAIL,
                        smtp_server=SMTP_SERVER,
                        smtp_port=SMTP_PORT,
                        smtp_user=SMTP_USER,
                        smtp_pass=SMTP_PASS,
                        campaign_id=f"{campaign_id}_reminder"
                    )
                    save_sent_mail(company_id, to_email, subject, mail_body)
                    logs.append(f"[EMAIL-HATIRLATMA] {to_email} adresine 5 gün sonra hatırlatma maili gönderildi.")
                except Exception as e:
                    logs.append(f"[HATA] Hatırlatma maili gönderilemedi: {to_email} ({e})")
            else:
                logs.append(f"[INFO] {to_email} adresine son {days_since(last_sent)} gün önce mail atıldı, tekrar gönderilmiyor.")
            time.sleep(10)
    valid_emails = get_valid_emails()
    logs.append(f"[REPORT] {len(valid_emails)} geçerli e-posta bulundu.")
    export_contacts_to_excel(valid_emails)
    export_contacts_to_csv(valid_emails)
    logs.append("Excel ve CSV dışa aktarıldı.")
    return logs

# ---- FİRMA LİSTESİ ÇEKME ----
def get_all_firmalar():
    # db'deki firmalar
    return get_all_contacts()

# ---- MANUEL MAİL GÖNDERME ----
def send_mail(to_email, subject, body):
    send_email(
        to_email=to_email,
        subject=subject,
        body=body,
        from_email=FROM_EMAIL,
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        smtp_user=SMTP_USER,
        smtp_pass=SMTP_PASS,
        campaign_id=str(int(time.time()))
    )
    return f"{to_email} adresine mail gönderildi."

# ---- SADECE FİRMA ÇEKME (ENRICH YOK) ----
def run_firm_extraction(sector, location, num_firm):
    companies = fetch_from_all_sources(sector, location, num_firm)
    return companies

# ---- RAPOR / EXPORT ----
def run_report_export():
    valid_emails = get_valid_emails()
    export_contacts_to_excel(valid_emails)
    export_contacts_to_csv(valid_emails)
    return "Rapor dışa aktarıldı."

# ---- AI ENRICHMENT (Tek firma için, örnek) ----
def run_ai_enrichment_for_company(company_id):
    contacts = get_all_contacts()
    company_row = contacts[contacts["company_id"] == company_id]
    if company_row.empty:
        return "Firma bulunamadı"
    summary = company_row.iloc[0].get("summary", "")
    ai_out = enrich_with_ai(summary)
    return ai_out

# ---- Ana modül giriş noktası (CLI için, GUI için gerek yok) ----
if __name__ == "__main__":
    # CLI terminalden çalıştırılırsa tam pipeline çalışır, GUI bunu kullanmaz
    main_mode = input("Mod (tümü: boş bırak, tekil: 'firmaadı'): ").strip()
    main_location = input("Ülke/Şehir (örn. Berlin): ")
    main_sector = input("Sektör (örn. mattress store): ")
    main_num_firm = int(input("Kaç firma çekilsin? (örn. 10): ") or "10")
    full_b2b_pipeline(main_mode, main_location, main_sector, main_num_firm)
