import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# --- Segmentasyon ve Şablon Yönetimi ---
TEMPLATES = {
    "luxury_mattress": {
        "tr": "Sayın {name},\nSize özel lüks yatak koleksiyonumuzu sunmak isteriz...",
        "en": "Dear {name},\nWe would like to present our luxury mattress collection...",
        "de": "Sehr geehrte/r {name},\nWir möchten Ihnen unsere Luxusmatratzen vorstellen..."
    },
    "standard_mattress": {
        "tr": "Sayın {name},\nStandart yataklarımızla ilgili bilgi almak ister misiniz?",
        "en": "Dear {name},\nWould you like to know more about our standard mattresses?"
    },
    "medical": {
        "tr": "Sayın {name},\nTıbbi ürün yelpazemiz hakkında bilgi vermek isteriz...",
        "en": "Dear {name},\nWe would like to inform you about our medical product range."
    },
    "generic_b2b": {
        "en": "Dear {name},\nWe are reaching out to introduce our company and discuss a potential partnership."
    }
}

def generate_auto_reply(customer_message, company_name, your_company, segment=None):
    system_prompt = (
        f"Bir B2B satış yöneticisi olarak, '{company_name}' firmasının iletisine "
        f"profesyonel, kibar, kısa ve eyleme çağıran bir yanıt üret. "
        f"Gelen mesaj:\n{customer_message}\n\n"
        f"Yanıtın, iş birliğini hızlandırıcı ve sektöre uygun olmalı. "
        f"Kendi firmamız: {your_company}. "
        f"Segment: {segment or 'Genel'}."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt}
        ],
        max_tokens=300,
        temperature=0.6
    )
    return response.choices[0].message['content']

def detect_language_by_country(country):
    if not country:
        return "en"
    country = country.lower()
    if country in ["germany", "deutschland", "almanya"]:
        return "de"
    elif country in ["france", "fransa"]:
        return "fr"
    elif country in ["italy", "italia", "italya"]:
        return "it"
    elif country in ["turkey", "türkiye"]:
        return "tr"
    else:
        return "en"

def select_template(sector, company_size):
    if sector and "mattress" in sector.lower():
        if company_size and ("large" in company_size.lower() or "büyük" in company_size.lower()):
            return "luxury_mattress"
        else:
            return "standard_mattress"
    elif sector and "medical" in sector.lower():
        return "medical"
    else:
        return "generic_b2b"

def make_segmented_prompt(name, company_name, country, sector, company_size, summary):
    language = detect_language_by_country(country)
    template_key = select_template(sector, company_size)
    template = TEMPLATES.get(template_key, {}).get(language, TEMPLATES["generic_b2b"]["en"])
    prompt = template.format(
        name=name or "Yetkili",
        company_name=company_name or "",
        summary=summary or ""
    )
    return prompt, language

# Eski AI enrich ve prompt fonksiyonları AYNEN KALSIN!
def enrich_with_ai(text, prompt="Bu metinden ad, soyad ve pozisyon çıkar:"):
    full_prompt = f"{prompt}\n{text}\n---"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=256,
            temperature=0.2
        )
        result = response['choices'][0]['message']['content']
        return result
    except Exception as e:
        return str(e)

def make_personalized_prompt(name, position, company_name, website, sector, summary, language="tr"):
    if language == "tr":
        prompt = (
            f"{name} adlı {position} pozisyonundaki kişiye, {company_name} şirketinde çalıştığı için doğrudan "
            f"hitap eden, birebir, profesyonel ama samimi bir tanıtım maili hazırla. Web sitesi: {website}, "
            f"sektör: {sector}. Şirket özeti: {summary}. Mailin başında {name} Bey/Hanım diye seslen. "
            f"Şirketimizin ürün/iş birliğinden kısaca bahset, iletişim ve dönüş talebini yumuşak şekilde ekle."
        )
    else:
        prompt = (
            f"Write a personalized, professional but warm introduction email directly to {name}, "
            f"who is the {position} at {company_name}. Start the mail with 'Dear {name}'. "
            f"Company website: {website}, sector: {sector}, company summary: {summary}. "
            f"Briefly mention our products or partnership opportunity and gently invite a response."
        )
    return prompt

def make_general_prompt(company_name, website, sector, summary, language="tr"):
    if language == "tr":
        prompt = (
            f"{company_name} şirketine hitap eden, profesyonel ve ilgi çekici bir tanıtım maili hazırla. "
            f"Web sitesi: {website}, sektör: {sector}. Şirket özeti: {summary}. "
            f"Mailin girişinde firmaya genel hitap kullan. Kısa bir şekilde iş birliği veya ürünümüzden bahset, "
            f"iletişim talebini yumuşakça belirt."
        )
    else:
        prompt = (
            f"Write a professional and engaging introduction email addressed to {company_name}. "
            f"Company website: {website}, sector: {sector}, summary: {summary}. "
            f"Use a general greeting for the company, briefly introduce our product or collaboration offer, "
            f"and kindly invite them to respond."
        )
    return prompt

def get_email_prompt(is_personal, name=None, position=None, company_name=None, website=None, sector=None, summary=None, language="tr"):
    if is_personal and name and position:
        return make_personalized_prompt(name, position, company_name, website, sector, summary, language)
    else:
        return make_general_prompt(company_name, website, sector, summary, language)

def generate_email_text(prompt, model="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "Sen profesyonel bir satış ve tanıtım uzmanısın."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"[GPT Error] {str(e)}"

def make_reminder_prompt(name, company_name, website, language="tr"):
    if language == "tr":
        prompt = (
            f"{company_name} için daha önce tanıtım maili gönderdik. "
            f"{name} Bey/Hanım'a 5 gün sonra samimi, kısa ve nazik bir hatırlatma maili yaz. "
            f"İlk maile yanıt gelmediyse iletişim talebini kibarca yinele."
        )
    else:
        prompt = (
            f"We sent an intro email to {company_name}. "
            f"Write a short and polite follow-up reminder to {name} after 5 days if they haven't responded."
        )
    return prompt

