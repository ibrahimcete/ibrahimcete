# Mini B2B Automation Engine

Bu proje, mevcut `main.py` içindeki iş mantığını doğrudan çağırarak (GUI'ye tıklama yapmadan) uçtan uca otomatik şekilde çalışan bir B2B otomasyon motoru sağlar. Motor; NLP ile komutu anlar, Google Maps aramasını yapar, web sitelerini analiz eder ve uygun firmalara kampanya emaili gönderir. Süreç GUI’den (ANA3.py) veya başsız (run_engine.py) modda yönetilebilir.

## Mimari Genel Bakış

- `automation_engine.py` (AutomationEngine):
  - Sistemin giriş noktasıdır. Komutları alır (`process_command`), NLP ile ayrıştırır ve `workflow_orchestrator` üzerinden iş akışını başlatır.
  - Geri bildirimleri GUI’ye veya loglara iletir.

- `nlp_command_parser.py` (NLPCommandParser):
  - Doğal dil komutlarını hedef JSON şemasına dönüştürür.
  - Birincil yol: Gemini API şemasına uygun ayrıştırma (simulate edilmiştir, gerçek API anahtarı eklenebilir).
  - Yedek yol: Geliştirilmiş Türkçe anahtar kelime/regex ayrıştırması:
    - Eş anlamlı sektör eşleme (ör. yazılım/software),
    - Sayı sözcüklerinden `max_results` çıkarımı (ör. “elli”),
    - “yaklaşık/civarı/kadar” gibi belirsiz ifadelerde üst sınır ayarı,
    - Tırnaksız kampanya adı yakalama (“kampanyasını <ad>”).
  - Örnek: “Kayseri’deki mobilya firmalarını bul ve ‘Yaz Tanıtımı’ kampanyasını gönder”.

- `workflow_orchestrator.py` (WorkflowOrchestrator):
  - İş akışını adım adım yönetir: `search` -> `analyze` -> `campaign`.
  - Durumu `workflow_state.json` içine kaydeder, kesintiden sonra kaldığı yerden devam eder.
  - Arka planda thread ile çalışır; GUI donmaz.

- `task_executor.py` (TaskExecutor):
  - `main.py` içindeki sınıfları (APIManager, WebScraper, EmailManager, Database) modül olarak yükler ve gerçek işlerini çağırır.
  - Arama sonuçlarını DB’ye kaydeder, analiz çıktısını günceller, email gönderimini yürütür.

- `ai_learning_optimizer.py` (AILearningOptimizer):
  - Kampanya sonuçlarını ve NLP geri bildirimlerini basitçe toplar.
  - Gelecekte gelişmiş öğrenme/öneri mantığı için temel sağlar.

- `monitoring_error_handler.py` (MonitoringErrorHandler):
  - Standart loglama, tekrar deneme (decorator), hata yakalama ve opsiyonel Telegram bildirimleri.

## GUI (ANA3.py)

- Modern, koyu temalı bir PySide6 arayüz.
- Üst araç çubuğu: Komutu Gönder, Duraklat, Devam Et, Durdur, Logları Temizle.
- Sol panel: Komut girişi, kontrol butonları, hızlı komutlar, durum etiketi, ilerleme çubuğu, aktif iş akışları tablosu.
- Sağ panel: Log görüntüleme, Logları Temizle/Kopyala butonları.
- Chat Asistanı (yeni sekme): Komut girmek yerine etkileşimli sohbetle süreci başlatmanıza yardım eder (GUI içinden otomasyona köprü kurar).
- Menü: Dosya (Logları Kaydet), Görünüm (Koyu/Açık Tema), Ayarlar (Telegram Ayarları yazma).
- Komut geçmişi açılır listesi: Tek tıkla önceki komutlara dönme.

Çalıştırma:

```bash
python ANA3.py
```

Örnek komut:

```
Kayseri'deki mobilya firmalarını bul, analiz et ve 'Yaz Tanıtımı' kampanyasını gönder
```

## Başsız (Headless) Kullanım

- `run_engine.py` motoru 7/24 modunda başlatır. Komut parametresi verilirse tek seferlik işlenir.

```bash
python run_engine.py
python run_engine.py Kayseri'deki mobilya firmalarını bul, analiz et ve 'Yaz Tanıtımı' kampanyasını gönder
```

Windows’ta otomatik başlatmak için Görev Zamanlayıcı’ya `python run_engine.py` ekleyebilirsiniz.

## NLP Hedef Şeması

```json
{
  "type": "OBJECT",
  "properties": {
    "intent": {"type": "STRING"},
    "query": {"type": "STRING"},
    "location": {"type": "STRING"},
    "max_results": {"type": "INTEGER"},
    "campaign_name": {"type": "STRING"},
    "target_sector": {"type": "STRING"},
    "target_firm_name": {"type": "STRING"}
  },
  "required": ["intent"]
}
```

Fallback ayrıştırma kuralları (özet):
- “bul/ara/listele” -> intent=firma_ara
- “gönder/mail at/kampanya” -> intent=kampanya_gonder (veya birlikteyse firma_ara_ve_kampanya)
- “analiz et/incele” -> intent=analiz_et
- Tırnak içi ‘...’ kampanya adı; metindeki sayı max_results; bilinen şehirler location.

## Telegram Bildirimleri

`config.json` içine aşağıdaki anahtarları eklerseniz kritik bildirimler Telegram’a da gönderilir:

```json
{
  "telegram_bot_token": "123456:ABC...",
  "telegram_chat_id": "12345678"
}
```

GUI’den Ayarlar > Telegram Ayarları üzerinden de yazabilirsiniz.

## Sorun Giderme

- `main.py` sınıfları yüklenemedi: `main.py` içinde `APIManager`, `WebScraper`, `EmailManager`, `Database` sınıfları tanımlı olmalı.
- PySide6 uyarıları: Ortam kaynaklı olabilir; çalışmayı engellemiyorsa göz ardı edilebilir.
- Logları paylaşın: GUI > Dosya > Logları Kaydet.

## Yol Haritası (Öneriler)

- Çoklu iş akışı yönetimi (listeleme/çoklu kontrol).
- Kampanya şablon yöneticisi (GUI’den şablonları düzenleme/kaydetme).
- Performans metrik panosu (istek sayıları, hata oranları, ort. süreler).
 - Chat Asistanı’na bellek/özetleme, öneri üretimi ve doğrulama akışları.


