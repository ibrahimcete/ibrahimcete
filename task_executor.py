#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import importlib.util
from monitoring_error_handler import logger, retry_on_failure
import json

# Ana proje dizinini sys.path'e ekle (main.py'nin bulunduğu yer)
try:
    main_py_dir = os.path.dirname(os.path.abspath(__file__))
    if main_py_dir not in sys.path:
        sys.path.insert(0, main_py_dir)
    logger.info(f"sys.path güncellendi: {main_py_dir}")
except Exception as e:
    logger.error(f"sys.path ayarlanamadı: {e}")

# Gerekli sınıfları main.py'den yükle
try:
    spec = importlib.util.spec_from_file_location("main_module", "main.py")
    if spec and spec.loader:
        main_module = importlib.util.module_from_spec(spec)
        sys.modules["main_module"] = main_module
        spec.loader.exec_module(main_module)
        APIManager = main_module.APIManager
        WebScraper = main_module.WebScraper
        EmailManager = main_module.EmailManager
        Database = main_module.Database
        logger.info("Gerekli sınıflar main.py'den başarıyla import edildi.")
    else:
        raise ImportError("main.py modül olarak yüklenemedi.")
except ImportError as e:
    logger.critical(f"Gerekli sınıflar import edilemedi: {e}.")
    class APIManager: pass
    class WebScraper: pass
    class EmailManager: pass
    class Database: pass
except AttributeError as e:
    logger.critical(f"main.py içinde beklenen sınıflar bulunamadı: {e}.")
    class APIManager: pass
    class WebScraper: pass
    class EmailManager: pass
    class Database: pass
except Exception as e:
    logger.critical(f"Modül import sırasında beklenmeyen hata: {e}")
    class APIManager: pass
    class WebScraper: pass
    class EmailManager: pass
    class Database: pass


class TaskExecutor:
    """
    main.py ve main2.py'deki temel işlevleri çağıran sınıf.
    GUI'den bağımsız çalışacak şekilde tasarlanmıştır.
    """
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        try:
            self.db = Database()
            self.api_manager = APIManager(db=self.db)
            self.web_scraper = WebScraper()
            self.email_manager = EmailManager()

            if self.config:
                self.api_manager.update_settings(self.config)
                self.email_manager.update_settings(self.config)

            logger.info("TaskExecutor başarıyla başlatıldı ve manager'lar yüklendi.")

        except Exception as e:
            logger.critical(f"Manager sınıfları başlatılırken hata oluştu: {e}")
            self.db = None
            self.api_manager = None
            self.web_scraper = None
            self.email_manager = None
            raise RuntimeError(f"TaskExecutor başlatılamadı: {e}")

    def _load_config(self, config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Ayar dosyası bulunamadı: {config_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Ayar dosyası okunamadı (JSON format hatası): {config_path}")
            return {}
        except Exception as e:
            logger.error(f"Ayar dosyası yüklenirken hata: {e}")
            return {}

    @retry_on_failure(retries=2, delay=10)
    def execute_search(self, query, location, max_results, progress_callback=None):
        if not self.api_manager:
            raise RuntimeError("APIManager başlatılamadığı için arama yapılamıyor.")
        logger.info(f"Google Maps araması başlatılıyor: Sorgu='{query}', Konum='{location}', Max={max_results}")

        existing_ids = set()
        if self.db:
            try:
                 existing_place_ids = self.db.get_existing_place_ids()
                 existing_ids = set(existing_place_ids) if existing_place_ids else set()
                 logger.info(f"{len(existing_ids)} mevcut place_id bulundu.")
            except Exception as e:
                 logger.warning(f"Mevcut place_id'ler alınamadı: {e}")

        try:
            firms = self.api_manager.search_google_maps_batch(
                query=query,
                location=location,
                max_results=max_results,
                batch_size=min(max_results, 50),
                progress_callback=progress_callback,
                existing_firm_ids=list(existing_ids)
            )
            logger.info(f"Arama tamamlandı. {len(firms) if firms else 0} yeni firma bulundu.")

            saved_firms = []
            if firms and self.db:
                logger.info(f"{len(firms)} firma veritabanına kaydediliyor...")
                count = 0
                for firm in firms:
                     try:
                        firm_id = self.db.save_firm(firm)
                        if firm_id:
                             firm['id'] = firm_id
                             saved_firms.append(firm)
                             count += 1
                             if progress_callback:
                                 progress_callback(f"💾 Veritabanına kaydedildi: {firm.get('name', 'İsimsiz')} ({count}/{len(firms)})")
                     except Exception as db_e:
                        logger.error(f"Firma kaydedilemedi ({firm.get('name', 'İsimsiz')}): {db_e}")
                logger.info(f"{count} firma başarıyla kaydedildi.")

            return saved_firms
        except AttributeError as e:
             logger.error(f"APIManager'da beklenen fonksiyon bulunamadı: {e}. Arama yapılamıyor.")
             return None
        except Exception as e:
            logger.error(f"Google Maps arama sırasında hata: {e}", exc_info=True)
            if progress_callback:
                progress_callback(f"❌ Arama hatası: {e}")
            return None

    @retry_on_failure(retries=1, delay=5)
    def execute_analysis(self, firm_data, progress_callback=None):
        if not self.web_scraper:
            raise RuntimeError("WebScraper başlatılamadığı için analiz yapılamıyor.")
        website_url = firm_data.get('website')
        firm_name = firm_data.get('name', 'Bilinmeyen Firma')
        if not website_url:
            logger.warning(f"Analiz atlandı: {firm_name} için web sitesi URL'si yok.")
            if progress_callback:
                progress_callback(f"⚠️ Analiz atlandı (URL yok): {firm_name}")
            return firm_data

        logger.info(f"Web sitesi analizi başlatılıyor: {firm_name} - {website_url}")
        if progress_callback:
            progress_callback(f"🔎 Analiz ediliyor: {firm_name}")
        try:
            analysis_results = self.web_scraper.scrape_website(website_url, firm_name)
            if analysis_results:
                 logger.info(f"Analiz tamamlandı: {firm_name}. Bulunan emailler: {len(analysis_results.get('emails', []))}")
                 if progress_callback:
                     progress_callback(f"✅ Analiz tamamlandı: {firm_name} ({len(analysis_results.get('emails', []))} email)")
                 updated_firm_data = {**firm_data, **analysis_results, 'is_analyzed': True}
                 if self.db and 'id' in updated_firm_data:
                     try:
                        update_payload = {k: v for k, v in updated_firm_data.items() if k != 'id'}
                        success = self.db.update_firm(updated_firm_data['id'], **update_payload)
                        if success:
                            if progress_callback:
                                progress_callback(f"💾 Analiz sonuçları kaydedildi: {firm_name}")
                        else:
                             logger.warning(f"Analiz sonuçları kaydedilemedi: {firm_name}")
                     except Exception as db_e:
                        logger.error(f"Analiz sonuçları kaydedilirken DB hatası ({firm_name}): {db_e}")
                 return updated_firm_data
            else:
                 logger.warning(f"Analiz sonucu boş: {firm_name}")
                 if progress_callback:
                     progress_callback(f"⚠️ Analiz sonucu boş: {firm_name}")
                 firm_data['is_analyzed'] = False
                 return firm_data
        except AttributeError as e:
             logger.error(f"WebScraper'da beklenen fonksiyon bulunamadı: {e}. Analiz yapılamıyor.")
             return None
        except Exception as e:
            logger.error(f"Web sitesi analizi sırasında hata ({firm_name}): {e}", exc_info=True)
            if progress_callback:
                progress_callback(f"❌ Analiz hatası: {firm_name} - {e}")
            return None

    @retry_on_failure(retries=2, delay=30)
    def execute_campaign(self, firms_to_send, template, progress_callback=None):
        if not self.email_manager:
            raise RuntimeError("EmailManager başlatılamadığı için kampanya gönderilemiyor.")
        if not self.api_manager:
             logger.warning("APIManager başlatılamadı, AI ile email oluşturma kullanılamayacak.")
        logger.info(f"Email kampanyası başlatılıyor: {len(firms_to_send)} firma.")
        if progress_callback:
            progress_callback(f"🚀 Kampanya başlatılıyor ({len(firms_to_send)} firma)...")

        sent_count = 0
        failed_count = 0
        results = {'sent': [], 'failed': []}

        for i, firm in enumerate(firms_to_send):
            firm_name = firm.get('name', f"Firma {i+1}")
            valid_emails = []
            raw_emails = firm.get('emails', [])
            single_email = firm.get('email', '')
            if raw_emails is None:
                raw_emails = []
            if isinstance(raw_emails, str):
                try:
                    if raw_emails.strip():
                        raw_emails = json.loads(raw_emails)
                        if not isinstance(raw_emails, list):
                           raw_emails = []
                    else:
                       raw_emails = []
                except json.JSONDecodeError:
                     logger.warning(f"{firm_name}: 'emails' alanı JSON formatında değil, atlanıyor.")
                     raw_emails = []
            if isinstance(raw_emails, list):
                 for email_data in raw_emails:
                      if isinstance(email_data, dict) and email_data.get('email'):
                           valid_emails.append(email_data['email'])
                      elif isinstance(email_data, str) and '@' in email_data:
                           valid_emails.append(email_data)
            if single_email and '@' in single_email and single_email not in valid_emails:
                 valid_emails.append(single_email)
            if not valid_emails:
                logger.warning(f"Kampanya atlandı: {firm_name} için geçerli email bulunamadı.")
                if progress_callback:
                    progress_callback(f"⚠️ Email yok, atlandı: {firm_name}")
                failed_count += 1
                results['failed'].append({'firm': firm_name, 'reason': 'Email yok'})
                continue
            if progress_callback:
                progress_callback(f"✉️ Email hazırlanıyor: {firm_name} ({i+1}/{len(firms_to_send)})")
            subject = template.get('subject', f"{firm_name} İçin Özel Teklif")
            body = template.get('body', '')
            if not body and template.get('instructions') and self.api_manager:
                try:
                    if hasattr(self.api_manager, 'generate_email_gpt'):
                         logger.info(f"AI ile email oluşturuluyor: {firm_name}")
                         ai_content = self.api_manager.generate_email_gpt(firm, template)
                         if ai_content:
                             subject = ai_content.get('subject', subject)
                             body = ai_content.get('body', '')
                         else:
                             logger.warning(f"AI email oluşturamadı: {firm_name}")
                             body = f"Merhaba {firm_name},\n\nSize özel bir teklifimiz var."
                    else:
                         logger.warning("APIManager'da generate_email_gpt fonksiyonu yok.")
                         body = f"Merhaba {firm_name},\n\nSize özel bir teklifimiz var."
                except Exception as ai_e:
                    logger.error(f"AI email oluşturma hatası ({firm_name}): {ai_e}")
                    body = f"Merhaba {firm_name},\n\nSize özel bir teklifimiz var."
            elif not body:
                 body = f"Merhaba {firm_name},\n\nSize özel bir teklifimiz var."
            target_email = valid_emails[0]
            if progress_callback:
                progress_callback(f"➡️ Gönderiliyor: {firm_name} -> {target_email}")
            try:
                send_result = self.email_manager.send_email(
                    to_email=target_email,
                    subject=subject,
                    body=body,
                    firm_id=firm.get('id')
                )
                if self.db:
                     try:
                          self.db.save_email_log(
                               firm.get('id'),
                               target_email,
                               subject,
                               body,
                               'sent' if send_result.get('success') else 'failed'
                          )
                     except Exception as db_e:
                          logger.error(f"Email log kaydedilemedi ({firm_name}): {db_e}")
                if send_result.get('success'):
                    sent_count += 1
                    results['sent'].append({'firm': firm_name, 'email': target_email})
                    if progress_callback:
                        progress_callback(f"✅ Gönderildi: {firm_name}")
                else:
                    failed_count += 1
                    error_reason = send_result.get('error', 'Bilinmeyen hata')
                    results['failed'].append({'firm': firm_name, 'email': target_email, 'reason': error_reason})
                    logger.error(f"Email gönderilemedi ({firm_name} -> {target_email}): {error_reason}")
                    if progress_callback:
                        progress_callback(f"❌ Gönderme hatası: {firm_name} - {error_reason}")
                if i < len(firms_to_send) - 1:
                     wait_time = self.config.get('email_send_delay_seconds', 5)
                     if progress_callback:
                           progress_callback(f"⏳ {wait_time} saniye bekleniyor...")
                     time.sleep(wait_time)
            except AttributeError as e:
                logger.error(f"EmailManager'da beklenen fonksiyon bulunamadı: {e}. Kampanya durduruldu.")
                if progress_callback:
                     progress_callback(f"❌ EmailManager hatası: {e}")
                raise RuntimeError(f"EmailManager hatası: {e}")
            except Exception as e:
                failed_count += 1
                error_reason = str(e)
                results['failed'].append({'firm': firm_name, 'email': target_email, 'reason': error_reason})
                logger.error(f"Email gönderme sırasında beklenmeyen hata ({firm_name}): {e}", exc_info=True)
                if progress_callback:
                    progress_callback(f"❌ Beklenmeyen hata: {firm_name} - {error_reason}")
        logger.info(f"Kampanya tamamlandı. Başarılı: {sent_count}, Başarısız: {failed_count}")
        if progress_callback:
            progress_callback(f"🎉 Kampanya tamamlandı! Başarılı: {sent_count}, Başarısız: {failed_count}")
        return {"sent_count": sent_count, "failed_count": failed_count, "results": results}

__all__ = ["TaskExecutor"]


