# -*- coding: utf-8 -*-

import logging
import time
import traceback
from functools import wraps
import json
import os
from urllib import request, parse

# Temel loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_engine.log', encoding='utf-8'),
        logging.StreamHandler() # Konsola da yazdır
    ]
)

logger = logging.getLogger('AutomationEngine')

class MonitoringErrorHandler:
    """Hata yönetimi, loglama ve bildirim (temel) sınıfı."""

    def __init__(self, notification_callback=None):
        """
        Başlatıcı.
        Args:
            notification_callback (callable, optional): Bildirim göndermek için
                                                        kullanılacak fonksiyon.
                                                        Varsayılan: None.
        """
        self.notification_callback = notification_callback
        logger.info("MonitoringErrorHandler başlatıldı.")

    def log_info(self, message):
        """Bilgi seviyesinde log kaydı yapar."""
        logger.info(message)

    def log_warning(self, message):
        """Uyarı seviyesinde log kaydı yapar."""
        logger.warning(message)

    def log_error(self, message, exc_info=False):
        """Hata seviyesinde log kaydı yapar."""
        logger.error(message, exc_info=exc_info)

    def log_critical(self, message, exc_info=True):
        """Kritik hata seviyesinde log kaydı yapar."""
        logger.critical(message, exc_info=exc_info)

    def notify(self, title, message):
        """Bildirim gönderir (eğer callback tanımlıysa)."""
        full_message = f"{title}: {message}"
        logger.warning(f"BİLDİRİM: {full_message}") # Loglara da yazdır
        if self.notification_callback:
            try:
                self.notification_callback(full_message)
            except Exception as e:
                self.log_error(f"Bildirim gönderme hatası: {e}")
        # Opsiyonel: Telegram bildirimi
        try:
            config = {}
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
            bot_token = config.get('telegram_bot_token')
            chat_id = config.get('telegram_chat_id')
            if bot_token and chat_id:
                text = full_message
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = parse.urlencode({'chat_id': chat_id, 'text': text}).encode()
                req = request.Request(url, data=data)
                request.urlopen(req, timeout=10)
        except Exception as e:
            self.log_warning(f"Telegram bildirimi gönderilemedi: {e}")

    def handle_exception(self, error, context="Bilinmeyen işlem"):
        """Genel hata yakalama ve loglama."""
        error_details = traceback.format_exc()
        self.log_error(f"{context} sırasında hata oluştu: {error}\nDetaylar:\n{error_details}", exc_info=False)
        # Kritik hatalarda bildirim gönderilebilir
        # self.notify("Kritik Hata", f"{context} başarısız oldu: {error}")

# Decorator for retrying operations
def retry_on_failure(retries=3, delay=5, backoff=2, allowed_exceptions=(Exception,)):
    """
    Bir fonksiyonu hata durumunda belirli sayıda yeniden deneyen decorator.

    Args:
        retries (int): Maksimum yeniden deneme sayısı.
        delay (int): Denemeler arasındaki başlangıç bekleme süresi (saniye).
        backoff (int): Her denemeden sonra bekleme süresinin çarpılacağı kat sayı.
        allowed_exceptions (tuple): Yeniden denemenin tetikleneceği hata türleri.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _retries, _delay = retries, delay
            while _retries > 0:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    _retries -= 1
                    if _retries == 0:
                        logger.error(f"{func.__name__} son denemede de başarısız oldu. Hata: {e}")
                        raise  # Hata yeniden fırlatılır
                    
                    msg = (f"{func.__name__} hatası: {e}. "
                           f"{_delay} saniye sonra yeniden denenecek ({retries - _retries}/{retries}).")
                    logger.warning(msg)
                    time.sleep(_delay)
                    _delay *= backoff
        return wrapper
    return decorator

__all__ = ["logger", "MonitoringErrorHandler", "retry_on_failure"]
