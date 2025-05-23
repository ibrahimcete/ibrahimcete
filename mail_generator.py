import openai

def generate_intro_email(company_name, website, sector, summary, language="tr"):
    # Kısa prompt örneği, geliştirilebilir
    prompt = (
        f"Sen bir B2B satış uzmanısın. Firma adı: {company_name}, Web sitesi: {website}, "
        f"Sektör: {sector}. Firmanın faaliyet özeti: {summary}. "
        f"Lütfen bu firmaya özel, etkili ve profesyonel bir tanıtım maili hazırla. "
        f"Mail {language} dilinde ve sıcak ama ciddi dille yazılsın."
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", # veya gpt-4-turbo
        messages=[
            {"role": "system", "content": "Sen profesyonel bir satış ve tanıtım uzmanısın."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
        temperature=0.7,
    )
    mail_text = response['choices'][0]['message']['content']
    return mail_text
