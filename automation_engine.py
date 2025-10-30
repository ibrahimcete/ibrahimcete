# -*- coding: utf-8 -*-

import threading
import time
from monitoring_error_handler import MonitoringErrorHandler, logger
from workflow_orchestrator import WorkflowOrchestrator
# Try new AI-powered NLP parser first, fallback to old one
try:
    from ai_nlp_parser import NLPCommandParser
    logger.info("✨ Gelişmiş AI NLP Parser yüklendi")
except ImportError:
    from nlp_command_parser import NLPCommandParser
    logger.info("📦 Standart NLP Parser yüklendi")
from ai_learning_optimizer import AILearningOptimizer
from task_executor import TaskExecutor


class AutomationEngine:
    """
    Otomasyon görevlerini yöneten, komutları işleyen ve
    modülleri koordine eden ana sınıf.
    """
    def __init__(self, feedback_callback=None):
        """
        Başlatıcı. Gerekli tüm alt modülleri başlatır.
        Args:
            feedback_callback (callable, optional): GUI'ye veya başka bir arayüze
                                                    geri bildirim göndermek için fonksiyon.
                                                    Varsayılan: None.
        """
        self.feedback_callback = feedback_callback
        self.error_handler = MonitoringErrorHandler(notification_callback=self.send_feedback)
        
        try:
             # Önce TaskExecutor'ı başlat, diğerleri ona bağlı olabilir
             self.task_executor = TaskExecutor()
             # Diğer modülleri TaskExecutor'ı kullanarak başlat
             self.orchestrator = WorkflowOrchestrator(self.task_executor)
             self.nlp_parser = NLPCommandParser() # API key'i config'den alabilir
             self.optimizer = AILearningOptimizer(db=self.task_executor.db) # DB bağlantısını optimizer'a ver
        except RuntimeError as e:
             # TaskExecutor başlatılamazsa motoru durdur
             self.error_handler.log_critical(f"Motor başlatılamadı: {e}", exc_info=True)
             self.send_feedback(f"❌ KRİTİK HATA: Otomasyon motoru başlatılamadı! Detaylar için logları kontrol edin. Hata: {e}")
             self.is_ready = False
             return
        except Exception as e:
             self.error_handler.log_critical(f"Motor başlatılırken beklenmedik hata: {e}", exc_info=True)
             self.send_feedback(f"❌ KRİTİK HATA: Motor başlatılırken beklenmedik hata! Hata: {e}")
             self.is_ready = False
             return


        self.engine_thread = None
        self.stop_event = threading.Event()
        self.is_ready = True # Motor başarıyla başlatıldı
        self.send_feedback("✅ Otomasyon Motoru başarıyla başlatıldı.")
        
        # Yarım kalan iş var mı kontrol et ve devam ettir
        self.check_and_resume_workflow()

    def send_feedback(self, message):
        """Geri bildirim callback fonksiyonunu güvenli bir şekilde çağırır."""
        if self.feedback_callback:
            try:
                self.feedback_callback(message)
            except Exception as e:
                logger.error(f"Geri bildirim gönderilemedi: {e}")
        logger.info(f"FEEDBACK: {message}")

    def process_command(self, command_text):
        """
        Kullanıcıdan gelen doğal dil komutunu işler.
        Args:
            command_text (str): Kullanıcının girdiği komut.
        """
        if not self.is_ready:
             self.send_feedback("❌ Motor hazır değil, komut işlenemiyor.")
             return
             
        self.send_feedback(f"💬 Komut alındı: '{command_text}'")
        self.send_feedback("🧠 Komut anlaşılıyor (NLP)...")

        parsed_data = self.nlp_parser.parse_command(command_text)

        if not parsed_data or parsed_data.get('intent') == 'hata':
            error_msg = parsed_data.get('error', 'Komut anlaşılamadı.')
            self.send_feedback(f"❓ Komut anlaşılamadı veya hata oluştu: {error_msg}")
            self.error_handler.log_error(f"NLP ayrıştırma hatası: {error_msg} - Komut: {command_text}")
            return

        self.send_feedback(f"👍 Komut anlaşıldı: {parsed_data}")

        # Kampanya adı verildiyse basit şablona dönüştür
        if parsed_data.get('campaign_name') and not parsed_data.get('campaign_template'):
            campaign_name = parsed_data.get('campaign_name')
            parsed_data['campaign_template'] = {
                'subject': campaign_name,
                'instructions': f"{campaign_name} için alıcıya özel, kısa ve ikna edici bir tanıtım içeriği üret."
            }

        # Niyete göre iş akışını başlat
        intent = parsed_data.get('intent')
        
        if intent in ["firma_ara", "kampanya_gonder", "firma_ara_ve_kampanya", "analiz_et"]:
             workflow_id = f"workflow_{int(time.time())}"
             success = self.orchestrator.start_new_workflow(
                 workflow_id,
                 parsed_data,
                 self.send_feedback
             )
             if success:
                self.send_feedback(f"🚀 Yeni iş akışı '{workflow_id}' başlatıldı. İş akışı başlatıldı.")
        elif intent == "bilgi_sor":
             self.send_feedback("❓ Anladığım kadarıyla bir bilgi istiyorsunuz, ancak tam olarak ne istediğinizi belirtmelisiniz.")
        else:
             self.send_feedback(f"❓ Anlaşılan niyet '{intent}' için tanımlı bir iş akışı bulunmuyor.")
             
    def check_and_resume_workflow(self):
         """Başlangıçta yarım kalmış iş akışı olup olmadığını kontrol eder ve devam ettirir."""
         if self.orchestrator.current_workflow:
              self.send_feedback(f"⏳ Yarım kalmış bir iş akışı bulundu ({self.orchestrator.current_workflow.get('id')}). Devam ettiriliyor...")
              resume_thread = threading.Thread(target=self.orchestrator.resume_workflow, args=(self.send_feedback,), daemon=True)
              resume_thread.start()
         else:
              self.send_feedback("✅ Yarım kalmış iş akışı bulunamadı.")


    def start_engine_loop(self):
        """Motorun ana döngüsünü (gerekirse) ayrı bir thread'de başlatır."""
        if not self.is_ready:
             self.send_feedback("❌ Motor hazır olmadığı için ana döngü başlatılamıyor.")
             return
             
        if self.engine_thread and self.engine_thread.is_alive():
            logger.warning("Motor ana döngüsü zaten çalışıyor.")
            return

        self.stop_event.clear()
        self.engine_thread = threading.Thread(target=self._engine_loop, daemon=True)
        self.engine_thread.start()
        self.send_feedback("⚙️ Motor ana döngüsü başlatıldı (Arka planda çalışıyor).")

    def _engine_loop(self):
        """Motorun periyodik görevleri yürüttüğü ana döngü."""
        logger.info("Motor ana döngüsü çalışmaya başladı.")
        while not self.stop_event.is_set():
            try:
                # Periyodik görevler buraya eklenebilir
                # Örn: Zamanlanmış görevleri kontrol et, sistem durumunu izle vb.

                # İş akışı durumunu kontrol et ve geri bildirim ver
                status = self.orchestrator.get_workflow_status()
                if status['status'] != 'idle':
                     pass

                time.sleep(15)

            except Exception as e:
                self.error_handler.handle_exception(e, context="Motor ana döngüsü")
                time.sleep(60)

        logger.info("Motor ana döngüsü durduruldu.")

    def stop_engine(self):
        """Motoru ve çalışan iş akışlarını durdurur."""
        self.send_feedback("🛑 Motor durduruluyor...")
        self.stop_event.set()

        self.orchestrator.stop_workflow()

        if self.engine_thread and self.engine_thread.is_alive():
            self.engine_thread.join(timeout=10)
            if self.engine_thread.is_alive():
                 logger.warning("Motor ana döngüsü zamanında durdurulamadı.")

        self.send_feedback("👋 Motor durduruldu.")
        logger.info("Otomasyon Motoru durduruldu.")

__all__ = ["AutomationEngine"]
