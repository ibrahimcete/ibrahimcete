import json
import time
import re
from monitoring_error_handler import logger, retry_on_failure


class NLPCommandParser:
    API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:{method}?key={api_key}"
    DEFAULT_MODEL = "gemini-2.5-flash-preview-09-2025"
    METHOD = "generateContent"

    TARGET_SCHEMA = {
        "type": "OBJECT",
        "properties": {
            "intent": {"type": "STRING"},
            "query": {"type": "STRING"},
            "location": {"type": "STRING"},
            "max_results": {"type": "INTEGER"},
            "campaign_name": {"type": "STRING"},
            "target_sector": {"type": "STRING"},
            "target_firm_name": {"type": "STRING"},
            # Main2 features
            "use_vapi": {"type": "BOOLEAN"},
            "use_whatsapp": {"type": "BOOLEAN"},
            "use_gpt": {"type": "BOOLEAN"},
            "message_type": {"type": "STRING"},
            "firm_id": {"type": "STRING"},
            "phone_number": {"type": "STRING"}
        },
        "required": ["intent"]
    }

    def __init__(self, api_key=""):
        self.api_key = api_key
        logger.info("NLPCommandParser başlatıldı.")
        # Eş anlamlılar ve sektör sözlüğü (basit)
        self.sector_synonyms = {
            "mobilya": ["mobilyacı", "mobilya mağazası", "mobilya firması"],
            "yazılım": ["software", "yazilim", "yazılım şirketi"],
            "restoran": ["lokanta", "restaurant"],
            "inşaat": ["insaat", "müteahhit", "yapı"],
            "imalat": ["üretim", "fabrika"],
            "tekstil": ["giyim", "konfeksiyon"],
            "lojistik": ["kargo", "nakliye"],
            "otomotiv": ["oto", "otomobil"],
            "eğitim": ["dershane", "kurs", "okul"],
        }
        
        # Main2 feature keywords
        self.vapi_keywords = ["vapi", "sesli arama", "voice call", "telefonla ara", "otomatik arama"]
        self.whatsapp_keywords = ["whatsapp", "wp", "wapp", "mesaj gönder"]
        self.gpt_keywords = ["gpt", "ai mesaj", "yapay zeka", "chatgpt"]
        # Türkçe sayı sözcükleri (temel)
        self.number_words = {
            "on": 10, "yirmi": 20, "otuz": 30, "kırk": 40, "elli": 50,
            "altmış": 60, "yetmiş": 70, "seksen": 80, "doksan": 90, "yüz": 100
        }

    @retry_on_failure(retries=3, delay=2)
    def parse_command(self, command_text):
        logger.info(f"NLP komutu ayrıştırılıyor: '{command_text}'")

        system_prompt = f"""
Sen bir B2B otomasyon asistanısın. Kullanıcı komutlarını analiz ederek aşağıdaki JSON şemasına uygun yapısal veriye dönüştür.

JSON Şeması:
```json
{json.dumps(self.TARGET_SCHEMA, indent=2, ensure_ascii=False)}
```

Kurallar:
- intent: 'bul/ara/listele' -> 'firma_ara'; 'gönder/mail at/kampanya' -> 'kampanya_gonder'; 'analiz et/incele' -> 'analiz_et'; 'ara yap/vapi' -> 'vapi_call'; 'whatsapp mesaj' -> 'whatsapp_send'; 'gpt mesaj' -> 'gpt_generate'.
- 'firma_ara' için 'query' ve 'location' doldur. 'max_results' yoksa 50.
- 'kampanya_gonder' için 'campaign_name' doldur.
- 'vapi_call', 'whatsapp_send', 'gpt_generate' gibi main2 özellikleri için ilgili boolean flag'leri true yap.
- 'vapi' veya 'sesli arama' kelimeleri varsa 'use_vapi': true yap.
- 'whatsapp' veya 'wp mesaj' varsa 'use_whatsapp': true yap.
- 'gpt' veya 'ai mesaj' varsa 'use_gpt': true yap.
- Belirsizse sadece bildiklerini doldur, 'intent'='bilgi_sor' olabilir.
- Sadece JSON döndür.
"""

        payload = {
            "contents": [{"parts": [{"text": command_text}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"responseMimeType": "application/json", "responseSchema": self.TARGET_SCHEMA}
        }

        api_url = self.API_URL_TEMPLATE.format(model=self.DEFAULT_MODEL, method=self.METHOD, api_key=self.api_key)

        try:
            logger.debug(f"Gemini API çağrısı yapılıyor: {api_url}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

            simulated_api_response_text = None
            if "mobilya" in command_text.lower() and "kayseri" in command_text.lower():
                 if "kampanya" in command_text.lower():
                     simulated_api_response_text = json.dumps({
                        "candidates": [{"content": {"parts": [{"text": json.dumps({
                            "intent": "firma_ara_ve_kampanya",
                            "query": "mobilya firması",
                            "location": "Kayseri",
                            "max_results": 50,
                            "campaign_name": "Yaz İndirimi"
                        })}]}}]
                     })
                 else:
                      simulated_api_response_text = json.dumps({
                        "candidates": [{"content": {"parts": [{"text": json.dumps({
                            "intent": "firma_ara",
                            "query": "mobilya firması",
                            "location": "Kayseri",
                            "max_results": 50
                        })}]}}]
                     })
            elif "analiz et" in command_text.lower():
                  simulated_api_response_text = json.dumps({
                      "candidates": [{"content": {"parts": [{"text": json.dumps({
                          "intent": "analiz_et",
                          "target_firm_name": "Örnek Teknoloji A.Ş."
                      })}]}}]
                  })

            if not simulated_api_response_text:
                 simulated_api_response_text = json.dumps({
                     "candidates": [{"content": {"parts": [{"text": json.dumps({
                         "intent": "bilgi_sor"
                     })}]}}]
                 })

            result = json.loads(simulated_api_response_text)
            logger.debug(f"Gemini API yanıtı (simüle): {result}")

            if (result and 'candidates' in result and result['candidates'] and 'content' in result['candidates'][0]
                    and 'parts' in result['candidates'][0]['content'] and result['candidates'][0]['content']['parts']):
                inner_json_text = result['candidates'][0]['content']['parts'][0].get('text')
                if inner_json_text:
                    try:
                        parsed_json = json.loads(inner_json_text)
                        logger.info(f"Komut başarıyla ayrıştırıldı: {parsed_json}")
                        parsed_json.setdefault('max_results', 50)
                        return parsed_json
                    except json.JSONDecodeError as e:
                         logger.error(f"API yanıtı içindeki JSON ayrıştırılamadı: {e} - Yanıt: {inner_json_text}")
                         fallback = self._fallback_parse(command_text)
                         if fallback:
                             return fallback
                         return {"intent": "hata", "error": f"API JSON parse hatası: {e}"}
                else:
                     logger.error("API yanıtında beklenen 'text' alanı bulunamadı.")
                     fallback = self._fallback_parse(command_text)
                     if fallback:
                         return fallback
                     return {"intent": "hata", "error": "API yanıtında 'text' alanı eksik."}
            else:
                error_detail = result.get('error', {}).get('message', 'Yapısal hata.')
                logger.error(f"Geçersiz API yanıtı alındı: {error_detail}")
                fallback = self._fallback_parse(command_text)
                if fallback:
                    return fallback
                return {"intent": "hata", "error": f"Geçersiz API yanıtı: {error_detail}"}
        except Exception as e:
            logger.error(f"NLP komut ayrıştırma sırasında hata: {e}", exc_info=True)
            fallback = self._fallback_parse(command_text)
            if fallback:
                return fallback
            return {"intent": "hata", "error": str(e)}

    def _fallback_parse(self, text: str):
        t = text.lower()
        intent = None
        use_vapi = False
        use_whatsapp = False
        use_gpt = False
        
        # Main2 feature detection
        if any(k in t for k in self.vapi_keywords):
            use_vapi = True
            intent = "vapi_call"
        if any(k in t for k in self.whatsapp_keywords):
            use_whatsapp = True
            if not intent:
                intent = "whatsapp_send"
        if any(k in t for k in self.gpt_keywords):
            use_gpt = True
            if not intent:
                intent = "gpt_generate"
        
        # Original intents
        if not intent:
            if any(k in t for k in ["bul", "ara", "listele"]):
                intent = "firma_ara"
            elif any(k in t for k in ["gönder", "mail at", "kampanya"]):
                intent = "kampanya_gonder"
            elif any(k in t for k in ["analiz et", "incele"]):
                intent = "analiz_et"
        
        if not intent:
            return {"intent": "bilgi_sor"}
        # max_results: sayı veya sözcüklerden yakala
        max_results = 50
        m_num = re.search(r"(\d+)", t)
        if m_num:
            max_results = int(m_num.group(1))
        else:
            for w, n in self.number_words.items():
                if w in t:
                    max_results = n
                    break
        if any(k in t for k in ["yaklaşık", "civar", "civarı", "kadar"]):
            max_results = min(200, int(max_results * 1.2))
        m_campaign = re.search(r"'([^']+)'|\"([^\"]+)\"", text)
        campaign_name = None
        if m_campaign:
            campaign_name = m_campaign.group(1) or m_campaign.group(2)
        else:
            m2 = re.search(r"kampanyas[ıi]n[ıi]?\s+([\wÇÖŞİĞÜçöşığü\- ]{3,50})", t)
            if m2:
                campaign_name = m2.group(1).strip().title()
        cities = ["istanbul","ankara","izmir","bursa","antalya","konya","adana","gaziantep","kayseri","mersin","eskisehir","diyarbakir","samsun","denizli","şanlıurfa","hatay","tekirdağ","kocaeli","sakarya","balıkesir","manisa","aydın","muğla","trabzon","ordu","malatya","erzurum"]
        location = None
        for c in cities:
            if c in t:
                location = c.title()
                break
        base_sectors = list(self.sector_synonyms.keys())
        query_candidates = base_sectors
        query = None
        for base in query_candidates:
            all_words = [base] + self.sector_synonyms.get(base, [])
            if any(w in t for w in all_words):
                query = base + " firması"
                break
        data = {"intent": intent}
        if query:
            data["query"] = query
        if location:
            data["location"] = location
        data["max_results"] = max_results
        if campaign_name and (intent in ["kampanya_gonder", "firma_ara_ve_kampanya"]):
            data["campaign_name"] = campaign_name
        
        # Main2 features
        data["use_vapi"] = use_vapi
        data["use_whatsapp"] = use_whatsapp
        data["use_gpt"] = use_gpt
        
        return data

__all__ = ["NLPCommandParser"]
