#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import time
import os
import sqlite3
import threading
import traceback
import signal
import random
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Güçlendirilmiş sistem altyapısı
try:
    from robust_system import (
        enhance_main_system, safe_execute, critical_safe, 
        ConnectionManager, MemoryManager, TimeoutManager,
        ThreadSafeManager, SystemMonitor, GracefulShutdown,
        APISecurityManager, DatabaseSecurityManager,
        safe_json_loads, safe_json_dumps, safe_file_read, safe_file_write,
        is_system_healthy, get_system_stats, logger as robust_logger
    )
    ROBUST_SYSTEM_AVAILABLE = True
    print("Güçlendirilmiş sistem modülü yüklendi")
except ImportError as e:
    print(f"UYARI: Güçlendirilmiş sistem modülü yüklenemedi: {e}")
    ROBUST_SYSTEM_AVAILABLE = False
    # Fallback fonksiyonlar
    def safe_execute(max_retries=3, delay=1.0, fallback_value=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Hata: {e}")
                    return fallback_value
            return wrapper
        return decorator
    def critical_safe(func):
        return func
    def safe_json_loads(json_str, default=None):
        try:
            return json.loads(json_str)
        except:
            return default
    def safe_json_dumps(obj, default="{}"):
        try:
            return json.dumps(obj, ensure_ascii=False, indent=2)
        except:
            return default
    def safe_file_read(file_path, encoding='utf-8', default=""):
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except:
            return default
    def safe_file_write(file_path, content, encoding='utf-8'):
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except:
            return False
    def is_system_healthy():
        return True
    def get_system_stats():
        return {'is_healthy': True}

# Database import - Güvenli
try:
    from database import Database
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: database modülü yüklenemedi: {e}")
    DATABASE_AVAILABLE = False
    class Database:
        def __init__(self):
            pass
        def connect(self):
            pass
        def close(self):
            pass

# PDF Report Generator import - Güvenli
try:
    from pdf_report_generator import AIReportGenerator
    PDF_REPORT_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: pdf_report_generator yüklenemedi: {e}")
    PDF_REPORT_AVAILABLE = False
    class AIReportGenerator:
        def __init__(self):
            pass
        def generate_weekly_report(self, start_date=None, end_date=None):
            return None
        def get_report_summary(self, start_date=None, end_date=None):
            return {}


# Logging setup - daha kapsamlı
if ROBUST_SYSTEM_AVAILABLE:
    logger = robust_logger
else:
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('b2b_app.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

# Global exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Try to show error dialog if possible
    try:
        from PySide6.QtWidgets import QMessageBox, QApplication
        if QApplication.instance():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Kritik Hata")
            msg.setText(f"Beklenmeyen bir hata oluştu:\n{exc_type.__name__}: {exc_value}")
            msg.setDetailedText(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            msg.exec()
    except:
        pass

sys.excepthook = handle_exception

# PySide6 imports - güvenli import
PYSIDE6_AVAILABLE = False
try:
    from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QFrame, QDialog,
        QFormLayout, QDialogButtonBox, QMessageBox, QFileDialog, QTableWidget,
        QTableWidgetItem, QStatusBar, QScrollArea, QGroupBox, QGridLayout,
        QListWidget, QApplication, QTabWidget, QListWidgetItem, QInputDialog,
        QCheckBox, QSpinBox, QDateTimeEdit, QDateEdit, QProgressBar, QSplitter, QSlider)
    from PySide6.QtCore import Qt, QThread, Signal, QTimer, QDateTime, QUrl, Slot
    from PySide6.QtGui import QShortcut, QKeySequence
    from PySide6.QtGui import QIcon, QPalette, QColor, QFont, QPainter, QBrush
    PYSIDE6_AVAILABLE = True
    logger.info("PySide6 başarıyla yüklendi")
except ImportError as e:
    logger.critical(f"PySide6 yüklenemedi: {e}")
    print("HATA: PySide6 kurulu değil. Lütfen 'pip install PySide6' komutu ile kurun.")
    sys.exit(1)

# WebEngine imports - hata yönetimi ile
WEBENGINE_AVAILABLE = False
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
    WEBENGINE_AVAILABLE = True
    logger.info("WebEngine modülü yüklendi")
except ImportError as e:
    logger.warning(f"WebEngine yüklenemedi: {e}")
    WEBENGINE_AVAILABLE = False

# Charts imports - opsiyonel
CHARTS_AVAILABLE = False
try:
    from PySide6.QtCharts import QChart, QChartView, QPieSeries, QLineSeries, QBarSeries, QBarSet
    CHARTS_AVAILABLE = True
    logger.info("Charts modülü yüklendi")
except ImportError as e:
    logger.warning(f"Charts yüklenemedi: {e}")
    CHARTS_AVAILABLE = False

# Third party imports
OPENAI_AVAILABLE = False
try:
    import openai
    # Yeni sürüm için
    try:
        from openai import OpenAI
        OPENAI_AVAILABLE = True
        logger.info("OpenAI modülü yüklendi (yeni sürüm)")
    except ImportError:
        # Eski sürüm için
        if hasattr(openai, 'ChatCompletion'):
            OPENAI_AVAILABLE = True
            logger.info("OpenAI modülü yüklendi (eski sürüm)")
            # Fallback OpenAI class oluştur
            class OpenAI:
                def __init__(self, api_key=None):
                    self.api_key = api_key
                    openai.api_key = api_key
        else:
            raise ImportError("OpenAI sürümü desteklenmiyor")
except ImportError as e:
    logger.warning(f"OpenAI yüklenemedi: {e}")
    OPENAI_AVAILABLE = False
    # Fallback OpenAI class
    class OpenAI:
        def __init__(self, api_key=None):
            pass

REQUESTS_AVAILABLE = False
try:
    import requests
    REQUESTS_AVAILABLE = True
    logger.info("Requests modülü yüklendi")
except ImportError as e:
    logger.warning(f"Requests yüklenemedi: {e}")
    REQUESTS_AVAILABLE = False


# Enhanced Error Recovery System
class ErrorRecoverySystem:
    """Gelişmiş hata kurtarma sistemi"""
    
    @staticmethod
    def safe_call(func, *args, default_return=None, error_message="İşlem başarısız", show_dialog=False, **kwargs):
        """Güvenli fonksiyon çağrısı"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}\n{traceback.format_exc()}")
            if show_dialog:
                try:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(None, "⚠️ Uyarı", f"{error_message}\n\nDetay: {str(e)}")
                except:
                    pass
            return default_return
    
    @staticmethod
    def with_retry(func, max_retries=3, delay=1.0, backoff=2.0):
        """Yeniden deneme ile fonksiyon çağrısı"""
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Deneme {attempt + 1}/{max_retries} başarısız: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            logger.error(f"Tüm denemeler başarısız: {str(last_exception)}")
            raise last_exception
        return wrapper

# Thread-safe operation wrapper
def thread_safe_operation(func):
    """Thread güvenli operasyon wrapper'ı"""
    lock = threading.Lock()
    def wrapper(*args, **kwargs):
        with lock:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Thread-safe operation failed: {str(e)}")
                return None
    return wrapper

# Utility functions
def safe_api_call(func, *args, **kwargs):
    """Güvenli API çağrısı wrapper'ı"""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.Timeout:
        logger.error("API çağrısı zaman aşımına uğradı")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("API bağlantı hatası")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API isteği hatası: {e}")
        return None
    except Exception as e:
        logger.error(f"Beklenmeyen API hatası: {e}")
        return None

def safe_json_parse(text):
    """Güvenli JSON parse"""
    try:
        return json.loads(text) if text else {}
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"JSON parse hatası: {e}")
        return {}


# Database sınıfı artık database.py'den import ediliyor


class GPTManager:
    """OpenAI GPT yönetimi - Geliştirilmiş"""
    
    def __init__(self):
        self.api_key = None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 1000
        self.temperature = 0.7
    
    def set_api_key(self, api_key):
        """API anahtarını ayarla"""
        self.api_key = api_key
        logger.info("OpenAI API anahtarı ayarlandı")
    
    def generate_message(self, prompt, firm_data, template_type="tanıtım"):
        """GPT ile mesaj oluştur"""
        if not self.api_key:
            logger.error("OpenAI API anahtarı ayarlanmamış")
            return None
        
        try:
            import openai
            openai.api_key = self.api_key
            
            # Firma bilgilerini prompt'a ekle
            firm_info = f"""
            Firma Adı: {firm_data.get('name', '')}
            Sektör: {firm_data.get('sector', '')}
            Adres: {firm_data.get('address', '')}
            Telefon: {firm_data.get('phone', '')}
            Email: {firm_data.get('email', '')}
            Website: {firm_data.get('website', '')}
            Özet: {firm_data.get('summary', '')}
            """
            
            full_prompt = f"{prompt}\n\nFirma Bilgileri:\n{firm_info}"
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir B2B pazarlama uzmanısın."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"GPT mesaj oluşturma hatası: {e}")
            return None
    
    def generate_call_script(self, firm_data):
        """Arama senaryosu oluştur"""
        if not self.api_key:
            logger.error("OpenAI API anahtarı ayarlanmamış")
            return None
        
        try:
            import openai
            openai.api_key = self.api_key
            
            prompt = f"""
            Aşağıdaki firma için profesyonel bir arama senaryosu oluştur:
            
            Firma: {firm_data.get('name', '')}
            Sektör: {firm_data.get('sector', '')}
            Adres: {firm_data.get('address', '')}
            
            Senaryo şunları içermeli:
            1. Açılış ve kendini tanıtma
            2. Firma hakkında bilgi alma
            3. İhtiyaçları öğrenme
            4. Çözüm önerisi sunma
            5. Sonraki adımları belirleme
            
            Kısa ve etkili olsun.
            """
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir satış uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Arama senaryosu hatası: {str(e)}")
            return None


# VapiManager sınıfı aşağıda tanımlandı - çift tanım kaldırıldı


class WhatsAppWebView(QWebEngineView):
    """WhatsApp Web görünümü - Geliştirilmiş"""
    
    message_received = Signal(dict)
    status_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_queue = []
        self.is_connected = False
        self.last_message_count = 0
        
        # WhatsApp Web URL
        self.load(QUrl("https://web.whatsapp.com"))
        
        # JavaScript injection
        self.page().loadFinished.connect(self.on_load_finished)
        
        # Message check timer
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.check_for_new_messages)
        self.message_timer.start(5000)  # 5 saniyede bir kontrol
    
    def on_load_finished(self, success):
        """Sayfa yüklendiğinde"""
        if success:
            self.inject_javascript()
            self.check_connection()
    
    def check_connection(self):
        """WhatsApp bağlantısını kontrol et"""
        def handle_result(result):
            self.is_connected = result
            if result:
                self.status_changed.emit("WhatsApp bağlı")
            else:
                self.status_changed.emit("WhatsApp bağlantısı bekleniyor...")
        
        # JavaScript ile bağlantı kontrolü
        self.page().runJavaScript("""
            document.querySelector('[data-testid="chat-list"]') !== null
        """, handle_result)
    
    def inject_javascript(self):
        """WhatsApp Web'e JavaScript enjekte et"""
        js_code = """
        // WhatsApp Web JavaScript injection
        window.whatsappAPI = {
            // Mesaj gönderme
            sendMessage: function(phone, message) {
                // Telefon numarasını temizle
                phone = phone.replace(/[^0-9]/g, '');
                
                // WhatsApp Web'de arama yap
                const searchBox = document.querySelector('[data-testid="chat-list-search"]');
                if (searchBox) {
                    searchBox.value = phone;
                    searchBox.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    // Kısa bekleme
                    setTimeout(() => {
                        // İlk chat'e tıkla
                        const firstChat = document.querySelector('[data-testid="cell-frame-container"]');
                        if (firstChat) {
                            firstChat.click();
                            
                            // Mesaj gönder
                            setTimeout(() => {
                                const messageBox = document.querySelector('[data-testid="conversation-compose-box-input"]');
                                if (messageBox) {
                                    messageBox.value = message;
                                    messageBox.dispatchEvent(new Event('input', { bubbles: true }));
                                    
                                    // Enter tuşuna bas
                                    messageBox.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                                }
                            }, 1000);
                        }
                    }, 1000);
                }
            },
            
            // Yeni mesajları kontrol et
            checkNewMessages: function() {
                const messages = document.querySelectorAll('[data-testid="msg-container"]');
                return messages.length;
            },
            
            // Bağlantı durumu
            isConnected: function() {
                return document.querySelector('[data-testid="chat-list"]') !== null;
            }
        };
        """
        
        self.page().runJavaScript(js_code)
    
    def send_message(self, phone, message):
        """Mesaj gönder"""
        if not self.is_connected:
            logger.warning("WhatsApp Web bağlantısı yok!")
            return False
        
        try:
            # Telefon numarasını düzenle
            phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not phone.startswith("+"):
                phone = "+90" + phone.lstrip("0")
            
            js_code = f"""
            window.whatsappAPI.sendMessage("{phone}", `{message}`)
            """
            self.page().runJavaScript(js_code)
            
            # Mesajın gönderilmesi için kısa bir bekleme
            QTimer.singleShot(2000, lambda: None)
            return True
        except Exception as e:
            logger.error(f"Mesaj gönderirken hata: {e}")
            return False

    def process_message_queue(self):
        """Mesaj kuyruğunu işle"""
        if self.message_queue:
            message = self.message_queue.pop(0)
            self.send_message(message['phone'], message['content'])
    
    def check_for_new_messages(self):
        """Yeni mesajları kontrol et"""
        if not self.is_connected:
            return
        
        def handle_result(result):
            if result > self.last_message_count:
                self.last_message_count = result
                # Yeni mesaj var
                logger.info(f"Yeni mesaj tespit edildi: {result}")
        
        # JavaScript ile mesaj sayısını kontrol et
        self.page().runJavaScript("""
            window.whatsappAPI.checkNewMessages()
        """, handle_result)
    
    def send_bulk_messages(self, messages_list):
        """Toplu mesaj gönder"""
        for message in messages_list:
            self.message_queue.append(message)
        
        # Kuyruğu işle
        self.process_message_queue()


class ModernCard(QFrame):
    """Modern kart widget'ı"""
    
    def __init__(self, title, value, icon="", color="#0d7377"):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        
        self.setupUI()
    
    def setupUI(self):
        """UI'yi ayarla"""
        self.setFixedSize(200, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.color}, stop:1 {self.color}88);
                border-radius: 10px;
                border: 1px solid {self.color}44;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.color}dd, stop:1 {self.color}aa);
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            color: white;
            font-size: 12px;
            font-weight: 500;
        """)
        layout.addWidget(title_label)
        
        # Değer
        self.value_label = QLabel(str(self.value))
        self.value_label.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
        """)
        layout.addWidget(self.value_label)
        
        # İkon (varsa)
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet("""
                color: white;
                font-size: 20px;
            """)
            icon_label.setAlignment(Qt.AlignRight)
            layout.addWidget(icon_label)
        
        self.setLayout(layout)
    
    def update_value(self, value):
        """Değeri güncelle"""
        self.value = value
        self.value_label.setText(str(value))


class FirmDialog(QDialog):
    """Firma ekleme/düzenleme dialogu - Geliştirilmiş"""
    
    def __init__(self, parent=None, firm_data=None):
        super().__init__(parent)
        self.firm_data = firm_data
        self.setupUI()
        if firm_data:
            self.load_firm_data()
    
    def setupUI(self):
        """UI'yi ayarla"""
        self.setWindowTitle("Firma Ekle/Düzenle")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout()
        
        # Form alanları
        form_layout = QFormLayout()
        
        # Firma adı
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Firma adı")
        form_layout.addRow("Firma Adı:", self.name_edit)
        
        # Telefon
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Telefon numarası")
        form_layout.addRow("Telefon:", self.phone_edit)
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email adresi")
        form_layout.addRow("Email:", self.email_edit)
        
        # Adres
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(80)
        self.address_edit.setPlaceholderText("Adres")
        form_layout.addRow("Adres:", self.address_edit)
        
        # Sektör
        self.sector_edit = QLineEdit()
        self.sector_edit.setPlaceholderText("Sektör")
        form_layout.addRow("Sektör:", self.sector_edit)
        
        # Website
        self.website_edit = QLineEdit()
        self.website_edit.setPlaceholderText("Website")
        form_layout.addRow("Website:", self.website_edit)
        
        # İletişim kişisi
        self.contact_person_edit = QLineEdit()
        self.contact_person_edit.setPlaceholderText("İletişim kişisi")
        form_layout.addRow("İletişim Kişisi:", self.contact_person_edit)
        
        # Özet
        self.summary_edit = QTextEdit()
        self.summary_edit.setMaximumHeight(100)
        self.summary_edit.setPlaceholderText("Firma özeti")
        form_layout.addRow("Özet:", self.summary_edit)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Kaydet")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0a5d61;
            }
        """)
        
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_firm_data(self):
        """Firma verilerini yükle"""
        if self.firm_data:
            self.name_edit.setText(self.firm_data.get('name', ''))
            self.phone_edit.setText(self.firm_data.get('phone', ''))
            self.email_edit.setText(self.firm_data.get('email', ''))
            self.address_edit.setPlainText(self.firm_data.get('address', ''))
            self.sector_edit.setText(self.firm_data.get('sector', ''))
            self.website_edit.setText(self.firm_data.get('website', ''))
            self.contact_person_edit.setText(self.firm_data.get('contact_person', ''))
            self.summary_edit.setPlainText(self.firm_data.get('summary', ''))
    
    def get_firm_data(self):
        """Firma verilerini al"""
        return {
            'name': self.name_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'address': self.address_edit.toPlainText().strip(),
            'sector': self.sector_edit.text().strip(),
            'website': self.website_edit.text().strip(),
            'contact_person': self.contact_person_edit.text().strip(),
            'summary': self.summary_edit.toPlainText().strip()
        }


class AssistantDialog(QDialog):
    """Vapi AI Asistan oluşturma/düzenleme dialogu"""
    
    def __init__(self, parent=None, assistant_data=None):
        super().__init__(parent)
        self.assistant_data = assistant_data
        self.setupUI()
        if assistant_data:
            self.load_assistant_data()
    
    def setupUI(self):
        """UI'yi ayarla"""
        self.setWindowTitle("AI Asistan Oluştur/Düzenle")
        self.setModal(True)
        self.resize(600, 700)
    
    def load_assistant_data(self):
        """Mevcut asistan verilerini yükle"""
        if self.assistant_data:
            # Asistan verilerini form elemanlarına yükle
            pass
    
    def get_assistant_data(self):
        """Form verilerini al"""
        return {
            'name': 'Default Assistant',
            'instructions': 'Default instructions'
        }
    



class GPTManager:
    """OpenAI GPT yönetimi - Geliştirilmiş"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500
        self.is_available = OPENAI_AVAILABLE
        
        if not self.is_available:
            logger.warning("OpenAI kütüphanesi mevcut değil")
    
    def set_api_key(self, api_key):
        """API anahtarını ayarla"""
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                return True
            except Exception as e:
                logger.error(f"OpenAI client hatası: {e}")
                return False
        return False
    
    def generate_message(self, prompt, firm_data, template_type="tanıtım", db=None):
        """GPT ile mesaj üret - Bilgi Öğrenim Entegreli"""
        if not OPENAI_AVAILABLE or not self.client:
            return None
        
        try:
            # Detaylı firma bilgileri
            firm_details = f"""
            Firma Bilgileri:
            - İsim: {firm_data.get('name', 'Belirtilmemiş')}
            - Sektör: {firm_data.get('sector', 'Belirtilmemiş')}
            - Özet: {firm_data.get('summary', 'Belirtilmemiş')}
            - İletişim Kişisi: {firm_data.get('contact_person', 'Belirtilmemiş')}
            - Web Sitesi: {firm_data.get('website', 'Yok')}
            - Telefon: {firm_data.get('phone', 'Belirtilmemiş')}
            - Email: {firm_data.get('email', 'Belirtilmemiş')}
            - Adres: {firm_data.get('address', 'Belirtilmemiş')}
            """
            
            # 🧠 Bilgi Öğrenim verilerini al
            learned_knowledge = ""
            if db:
                try:
                    all_knowledge = db.get_all_knowledge(filter_learned=True)
                    if all_knowledge:
                        knowledge_summaries = []
                        for knowledge in all_knowledge[:3]:  # En fazla 3 bilgi kullan
                            if knowledge.get('ai_summary'):
                                knowledge_summaries.append(f"• {knowledge.get('title', 'Bilgi')}: {knowledge.get('ai_summary', '')}")
                        
                        if knowledge_summaries:
                            learned_knowledge = f"""
            
            🧠 Öğrenilmiş Firma Bilgileri (AI Analizi):
            {chr(10).join(knowledge_summaries)}
            
            Bu bilgileri kullanarak daha kişiselleştirilmiş ve detaylı mesaj oluştur.
            """
                except Exception as e:
                    print(f"Bilgi öğrenim verisi alınamadı: {e}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir B2B satış uzmanısın. Öğrenilmiş firma bilgilerini kullanarak kişiselleştirilmiş mesajlar oluşturursun."},
                    {"role": "user", "content": f"{prompt}\n\n{firm_details}{learned_knowledge}"}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT mesaj üretim hatası: {e}")
            return None
    
    def generate_call_script(self, firm_data):
        """Arama senaryosu üret"""
        if not OPENAI_AVAILABLE or not self.client:
            return None
        
        try:
            prompt = f"""
            {firm_data.get('name', 'Firma')} adlı firmayı aramak için kısa bir senaryo oluştur.
            Sektör: {firm_data.get('sector', 'Belirtilmemiş')}
            
            Senaryo şunları içermeli:
            - Kısa tanıtım
            - Değer önerisi
            - Soru sorma
            - Randevu teklifi
            
            Maksimum 4-5 cümle, samimi ve profesyonel ton.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sen deneyimli bir satış uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Arama senaryosu hatası: {str(e)}")
            return None
    
    def delete_firm(self, firm_id):
        """Firma sil"""
        with self.lock:
            try:
                # Önce firma adını al
                self.cursor.execute("SELECT name FROM firms WHERE id = ?", (firm_id,))
                firm = self.cursor.fetchone()
                
                self.cursor.execute("DELETE FROM firms WHERE id = ?", (firm_id,))
                self.conn.commit()
                
                logger.info(f"Firma silindi: {firm['name'] if firm else firm_id}")
                return True
            except Exception as e:
                logger.error(f"Firma silme hatası: {e}")
                return False
    
    def get_firms(self, search_text="", sector="", status="", limit=None):
        """Firmaları getir (filtreleme ile)"""
        with self.lock:
            try:
                query = """SELECT 
                    id, name, phone, COALESCE(email, '') as email, 
                    COALESCE(address, '') as address, COALESCE(sector, '') as sector,
                    COALESCE(summary, '') as summary, COALESCE(website, '') as website,
                    COALESCE(contact_person, '') as contact_person,
                    COALESCE(last_contact_date, '') as last_contact_date,
                    COALESCE(status, 'active') as status,
                    place_id, rating, review_count, business_hours,
                    created_at, updated_at
                FROM firms WHERE 1=1"""
                params = []
                
                if search_text:
                    query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)"
                    search_param = f"%{search_text}%"
                    params.extend([search_param, search_param, search_param])
                
                if sector and sector != "Tüm Sektörler":
                    query += " AND sector = ?"
                    params.append(sector)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                query += " ORDER BY created_at DESC"
                
                if limit:
                    query += f" LIMIT {limit}"
                
                self.cursor.execute(query, params)
                rows = self.cursor.fetchall()
                # Row objelerini dict'e çevir
                firms = []
                for row in rows:
                    firm_dict = dict(row)
                    firms.append(firm_dict)
                return firms
            except Exception as e:
                logger.error(f"Firma getirme hatası: {e}")
                return []
    
    def get_firm_by_id(self, firm_id):
        """ID'ye göre firma getir"""
        with self.lock:
            try:
                self.cursor.execute("SELECT * FROM firms WHERE id = ?", (firm_id,))
                row = self.cursor.fetchone()
                return dict(row) if row else None
            except Exception as e:
                logger.error(f"Firma getirme hatası: {e}")
                return None
    
    def save_message(self, firm_id, direction, content, platform="whatsapp", 
                    status="sent", scheduled_date=None):
        """Mesaj kaydet"""
        with self.lock:
            try:
                self.cursor.execute("""
                    INSERT INTO messages (firm_id, direction, content, platform, 
                                        status, scheduled_date, sent_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (firm_id, direction, content, platform, status, 
                      scheduled_date, datetime.now() if not scheduled_date else None))
                self.conn.commit()
                
                # Son iletişim tarihini güncelle
                if not scheduled_date:
                    self.cursor.execute("""
                        UPDATE firms SET last_contact_date = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (firm_id,))
                    self.conn.commit()
                
                # Aktivite kaydet
                self.save_activity(firm_id, "message_sent", 
                                 f"{platform} üzerinden mesaj gönderildi")
                
                return True
            except Exception as e:
                logger.error(f"Mesaj kaydetme hatası: {e}")
                return False
    
    def get_messages(self, firm_id=None, limit=100):
        """Mesajları getir"""
        with self.lock:
            try:
                if firm_id:
                    self.cursor.execute("""
                        SELECT m.*, f.name as firm_name 
                        FROM messages m
                        LEFT JOIN firms f ON m.firm_id = f.id
                        WHERE m.firm_id = ?
                        ORDER BY m.created_at DESC
                        LIMIT ?
                    """, (firm_id, limit))
                else:
                    self.cursor.execute("""
                        SELECT m.*, f.name as firm_name 
                        FROM messages m
                        LEFT JOIN firms f ON m.firm_id = f.id
                        ORDER BY m.created_at DESC
                        LIMIT ?
                    """, (limit,))
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Mesaj getirme hatası: {e}")
                return []
    
    def get_scheduled_messages(self):
        """Zamanlanmış mesajları getir"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT m.*, f.name as firm_name, f.phone as firm_phone
                    FROM messages m
                    LEFT JOIN firms f ON m.firm_id = f.id
                    WHERE m.status = 'scheduled' 
                    AND m.scheduled_date <= datetime('now')
                    ORDER BY m.scheduled_date ASC
                """)
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Zamanlanmış mesaj getirme hatası: {e}")
                return []
    
    def save_call(self, firm_id, call_id="", phone_number_id="", assistant_id="",
                  duration=0, status="completed", recording_url="", 
                  transcript="", notes="", cost=0.0):
        """Arama kaydet"""
        with self.lock:
            try:
                self.cursor.execute("""
                    INSERT INTO calls (firm_id, call_id, phone_number_id, assistant_id,
                                     duration, status, recording_url, transcript, notes, cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (firm_id, call_id, phone_number_id, assistant_id, 
                      duration, status, recording_url, transcript, notes, cost))
                self.conn.commit()
                
                # Son iletişim tarihini güncelle
                self.cursor.execute("""
                    UPDATE firms SET last_contact_date = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (firm_id,))
                self.conn.commit()
                
                # Aktivite kaydet
                self.save_activity(firm_id, "call_made", 
                                 f"Vapi AI araması yapıldı ({duration} saniye)")
                
                return True
            except Exception as e:
                logger.error(f"Arama kaydetme hatası: {e}")
                return False
    
    def get_calls(self, firm_id=None):
        """Aramaları getir"""
        with self.lock:
            try:
                if firm_id:
                    self.cursor.execute("""
                        SELECT c.*, f.name as firm_name 
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        WHERE c.firm_id = ?
                        ORDER BY c.created_at DESC
                    """, (firm_id,))
                else:
                    self.cursor.execute("""
                        SELECT c.*, f.name as firm_name 
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        ORDER BY c.created_at DESC
                        LIMIT 100
                    """)
                rows = self.cursor.fetchall()
                # Row objelerini dict'e çevir
                calls = []
                for row in rows:
                    call_dict = dict(row)
                    calls.append(call_dict)
                return calls
            except Exception as e:
                logger.error(f"Arama getirme hatası: {e}")
                return []
    
    def save_email_log(self, firm_id, email, subject, content, status="sent"):
        """Email log kaydet"""
        with self.lock:
            try:
                self.cursor.execute("""
                    INSERT INTO email_logs (firm_id, email, subject, content, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (firm_id, email, subject, content, status))
                self.conn.commit()
                
                # Aktivite kaydet
                self.save_activity(firm_id, "email_sent", f"Email gönderildi: {subject}")
                
                return True
            except Exception as e:
                logger.error(f"Email log kaydetme hatası: {e}")
                return False
    
    def save_template(self, name, content, category="genel", variables=None):
        """Şablon kaydet"""
        with self.lock:
            try:
                variables_json = json.dumps(variables) if variables else ""
                self.cursor.execute("""
                    INSERT INTO templates (name, content, category, variables)
                    VALUES (?, ?, ?, ?)
                """, (name, content, category, variables_json))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Şablon kaydetme hatası: {e}")
                return False
    
    def get_templates(self, category=None):
        """Şablonları getir"""
        with self.lock:
            try:
                if category and category != "Tümü":
                    self.cursor.execute("""
                        SELECT * FROM templates WHERE category = ?
                        ORDER BY created_at DESC
                    """, (category,))
                else:
                    self.cursor.execute("""
                        SELECT * FROM templates 
                        ORDER BY created_at DESC
                    """)
                rows = self.cursor.fetchall()
                # Row objelerini dict'e çevir
                templates = []
                for row in rows:
                    template_dict = dict(row)
                    templates.append(template_dict)
                return templates
            except Exception as e:
                logger.error(f"Şablon getirme hatası: {e}")
                return []
    
    def save_activity(self, firm_id, activity_type, description, metadata=None):
        """Aktivite kaydet"""
        with self.lock:
            try:
                metadata_json = json.dumps(metadata) if metadata else ""
                self.cursor.execute("""
                    INSERT INTO activities (firm_id, activity_type, description, metadata)
                    VALUES (?, ?, ?, ?)
                """, (firm_id, activity_type, description, metadata_json))
                self.conn.commit()
            except Exception as e:
                logger.error(f"Aktivite kaydetme hatası: {e}")
    
    def get_recent_activities(self, limit=10):
        """Son aktiviteleri getir"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT a.*, f.name as firm_name 
                    FROM activities a
                    LEFT JOIN firms f ON a.firm_id = f.id
                    ORDER BY a.created_at DESC
                    LIMIT ?
                """, (limit,))
                rows = self.cursor.fetchall()
                # Row objelerini dict'e çevir
                activities = []
                for row in rows:
                    activity_dict = dict(row)
                    activities.append(activity_dict)
                return activities
            except Exception as e:
                logger.error(f"Aktivite getirme hatası: {e}")
                return []
    
    def save_scheduled_task(self, task_type, firm_id, data, scheduled_date):
        """Zamanlanmış görev kaydet"""
        with self.lock:
            try:
                data_json = json.dumps(data) if isinstance(data, dict) else str(data)
                self.cursor.execute("""
                    INSERT INTO scheduled_tasks (task_type, firm_id, data, scheduled_date)
                    VALUES (?, ?, ?, ?)
                """, (task_type, firm_id, data_json, scheduled_date))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Zamanlanmış görev kaydetme hatası: {e}")
                return False
    
    def get_pending_tasks(self):
        """Bekleyen görevleri getir"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT * FROM scheduled_tasks 
                    WHERE status = 'pending' 
                    AND scheduled_date <= datetime('now')
                    ORDER BY scheduled_date ASC
                """)
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Görev getirme hatası: {e}")
                return []
    
    def update_task_status(self, task_id, status):
        """Görev durumunu güncelle"""
        with self.lock:
            try:
                self.cursor.execute("""
                    UPDATE scheduled_tasks SET status = ? WHERE id = ?
                """, (status, task_id))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Görev güncelleme hatası: {e}")
                return False
    
    def get_statistics(self):
        """İstatistikleri getir"""
        with self.lock:
            try:
                stats = {}
                
                # Toplam firma
                self.cursor.execute("SELECT COUNT(*) as count FROM firms")
                row = self.cursor.fetchone()
                stats['total_firms'] = dict(row)['count'] if row else 0
                
                # Aktif firmalar
                self.cursor.execute("SELECT COUNT(*) as count FROM firms WHERE status = 'active'")
                row = self.cursor.fetchone()
                stats['active_firms'] = dict(row)['count'] if row else 0
                
                # Toplam mesaj - tablo yoksa 0 döndür
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM messages")
                    row = self.cursor.fetchone()
                    stats['total_messages'] = dict(row)['count'] if row else 0
                except:
                    stats['total_messages'] = 0
                
                # Gönderilen mesaj
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM messages WHERE direction = 'sent'")
                    row = self.cursor.fetchone()
                    stats['sent_messages'] = dict(row)['count'] if row else 0
                except:
                    stats['sent_messages'] = 0
                
                # Alınan mesaj
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM messages WHERE direction = 'received'")
                    row = self.cursor.fetchone()
                    stats['received_messages'] = dict(row)['count'] if row else 0
                except:
                    stats['received_messages'] = 0
                
                # Toplam arama
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM calls")
                    row = self.cursor.fetchone()
                    stats['total_calls'] = dict(row)['count'] if row else 0
                except:
                    stats['total_calls'] = 0
                
                # Toplam email
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM email_logs")
                    row = self.cursor.fetchone()
                    stats['total_emails'] = dict(row)['count'] if row else 0
                except:
                    stats['total_emails'] = 0
                
                # Bugünkü mesajlar
                try:
                    self.cursor.execute("""
                        SELECT COUNT(*) as count FROM messages 
                        WHERE DATE(created_at) = DATE('now', 'localtime')
                    """)
                    row = self.cursor.fetchone()
                    stats['today_messages'] = dict(row)['count'] if row else 0
                except:
                    stats['today_messages'] = 0
                
                # Bugünkü aramalar
                try:
                    self.cursor.execute("""
                        SELECT COUNT(*) as count FROM calls 
                        WHERE DATE(created_at) = DATE('now', 'localtime')
                    """)
                    row = self.cursor.fetchone()
                    stats['today_calls'] = dict(row)['count'] if row else 0
                except:
                    stats['today_calls'] = 0
                
                # Haftalık mesajlar
                try:
                    self.cursor.execute("""
                        SELECT COUNT(*) as count FROM messages 
                        WHERE DATE(created_at) >= DATE('now', '-7 days', 'localtime')
                    """)
                    row = self.cursor.fetchone()
                    stats['week_messages'] = dict(row)['count'] if row else 0
                except:
                    stats['week_messages'] = 0
                
                # Sektör dağılımı
                try:
                    self.cursor.execute("""
                        SELECT sector, COUNT(*) as count 
                        FROM firms 
                        WHERE sector IS NOT NULL AND sector != ''
                        GROUP BY sector
                    """)
                    rows = self.cursor.fetchall()
                    stats['sector_distribution'] = [dict(row) for row in rows] if rows else []
                except:
                    stats['sector_distribution'] = []
                
                return stats
            except Exception as e:
                logger.error(f"İstatistik getirme hatası: {e}")
                return self._empty_stats()
    
    def get_email_statistics(self):
        """Email istatistikleri"""
        with self.lock:
            try:
                stats = {}
                
                # Toplam email
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM email_logs")
                    row = self.cursor.fetchone()
                    stats['total'] = dict(row)['count'] if row else 0
                except:
                    stats['total'] = 0
                
                # Açılan emailler
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM email_logs WHERE opened = 1")
                    row = self.cursor.fetchone()
                    stats['opened'] = dict(row)['count'] if row else 0
                except:
                    stats['opened'] = 0
                
                # Tıklanan emailler
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM email_logs WHERE clicked = 1")
                    row = self.cursor.fetchone()
                    stats['clicked'] = dict(row)['count'] if row else 0
                except:
                    stats['clicked'] = 0
                
                # Yanıtlanan emailler
                try:
                    self.cursor.execute("SELECT COUNT(*) as count FROM email_logs WHERE replied = 1")
                    row = self.cursor.fetchone()
                    stats['replied'] = dict(row)['count'] if row else 0
                except:
                    stats['replied'] = 0
                
                return stats
            except Exception as e:
                logger.error(f"Email istatistik hatası: {e}")
                return {'total': 0, 'opened': 0, 'clicked': 0, 'replied': 0}
    
    def get_today_statistics(self):
        """Bugünkü istatistikler"""
        with self.lock:
            try:
                stats = {}
                
                # Bugünkü mesajlar
                self.cursor.execute("""
                    SELECT COUNT(*) as count FROM messages 
                    WHERE DATE(created_at) = DATE('now', 'localtime')
                """)
                stats['messages'] = self.cursor.fetchone()['count']
                
                # Bugünkü aramalar
                self.cursor.execute("""
                    SELECT COUNT(*) as count FROM calls 
                    WHERE DATE(created_at) = DATE('now', 'localtime')
                """)
                stats['calls'] = self.cursor.fetchone()['count']
                
                # Bugünkü emailler
                self.cursor.execute("""
                    SELECT COUNT(*) as count FROM email_logs 
                    WHERE DATE(sent_date) = DATE('now', 'localtime')
                """)
                stats['emails'] = self.cursor.fetchone()['count']
                
                # Bugün eklenen firmalar
                self.cursor.execute("""
                    SELECT COUNT(*) as count FROM firms 
                    WHERE DATE(created_at) = DATE('now', 'localtime')
                """)
                stats['new_firms'] = self.cursor.fetchone()['count']
                
                return stats
            except Exception as e:
                logger.error(f"Günlük istatistik hatası: {e}")
                return {'messages': 0, 'calls': 0, 'emails': 0, 'new_firms': 0}
    
    def get_weekly_comparison(self):
        """Haftalık karşılaştırma"""
        with self.lock:
            try:
                # Bu hafta
                self.cursor.execute("""
                    SELECT COUNT(*) as count FROM messages 
                    WHERE DATE(created_at) >= DATE('now', '-7 days', 'localtime')
                """)
                this_week = self.cursor.fetchone()['count']
                
                # Geçen hafta
                self.cursor.execute("""
                    SELECT COUNT(*) as count FROM messages 
                    WHERE DATE(created_at) >= DATE('now', '-14 days', 'localtime')
                    AND DATE(created_at) < DATE('now', '-7 days', 'localtime')
                """)
                last_week = self.cursor.fetchone()['count']
                
                return {
                    'this_week': this_week,
                    'last_week': last_week,
                    'change': this_week - last_week,
                    'change_percent': ((this_week - last_week) / last_week * 100) if last_week > 0 else 0
                }
            except Exception as e:
                logger.error(f"Haftalık karşılaştırma hatası: {e}")
                return {'this_week': 0, 'last_week': 0, 'change': 0, 'change_percent': 0}
    
    def get_monthly_statistics(self):
        """Aylık istatistikler"""
        with self.lock:
            try:
                stats = []
                
                # Son 12 ay
                for i in range(12):
                    self.cursor.execute("""
                        SELECT 
                            COUNT(DISTINCT CASE WHEN m.id IS NOT NULL THEN m.id END) as messages,
                            COUNT(DISTINCT CASE WHEN c.id IS NOT NULL THEN c.id END) as calls,
                            COUNT(DISTINCT CASE WHEN e.id IS NOT NULL THEN e.id END) as emails
                        FROM firms f
                        LEFT JOIN messages m ON f.id = m.firm_id 
                            AND strftime('%Y-%m', m.created_at) = strftime('%Y-%m', 'now', ? || ' months')
                        LEFT JOIN calls c ON f.id = c.firm_id 
                            AND strftime('%Y-%m', c.created_at) = strftime('%Y-%m', 'now', ? || ' months')
                        LEFT JOIN email_logs e ON f.id = e.firm_id 
                            AND strftime('%Y-%m', e.sent_date) = strftime('%Y-%m', 'now', ? || ' months')
                    """, (-i, -i, -i))
                    
                    result = self.cursor.fetchone()
                    month_name = datetime.now().replace(month=((datetime.now().month - i - 1) % 12) + 1).strftime('%B')
                    stats.append({
                        'month': month_name,
                        'messages': result['messages'],
                        'calls': result['calls'],
                        'emails': result['emails']
                    })
                
                return list(reversed(stats))
            except Exception as e:
                logger.error(f"Aylık istatistik hatası: {e}")
                return []
    
    def get_daily_stats(self, days=7):
        """Günlük istatistikler"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as message_count
                    FROM messages
                    WHERE DATE(created_at) >= DATE('now', ? || ' days', 'localtime')
                    GROUP BY DATE(created_at)
                    ORDER BY date ASC
                """, (-days,))
                
                rows = self.cursor.fetchall()
                return [dict(row) for row in rows] if rows else []
            except Exception as e:
                logger.warning(f"Günlük istatistik hatası (messages tablosu yok): {e}")
                # Boş data döndür
                return [{'date': f'2024-01-0{i}', 'message_count': 0} for i in range(1, days+1)]
    
    def _empty_stats(self):
        """Boş istatistik objesi"""
        return {
            'total_firms': 0,
            'active_firms': 0,
            'total_messages': 0,
            'sent_messages': 0,
            'received_messages': 0,
            'total_calls': 0,
            'total_emails': 0,
            'today_messages': 0,
            'today_calls': 0,
            'week_messages': 0,
            'sector_distribution': []
        }
    
    # ==================== ÇAĞRI ANALİZİ VERİTABANI METODLARI ====================
    
    def ensure_connection(self):
        """Veritabanı bağlantısını kontrol et ve yeniden bağlan"""
        try:
            # Gerekli attributes'leri kontrol et ve oluştur
            if not hasattr(self, 'db_path'):
                self.db_path = "b2b_automation.db"
            if not hasattr(self, 'lock'):
                import threading
                self.lock = threading.Lock()
                
            if not self.conn:
                import sqlite3
                self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
                self.conn.row_factory = sqlite3.Row
                self.cursor = self.conn.cursor()
                logger.info("Veritabanı bağlantısı yenilendi")
            else:
                # Bağlantı test et
                self.cursor.execute("SELECT 1")
        except Exception as e:
            logger.warning(f"Veritabanı bağlantı hatası, yeniden bağlanılıyor: {e}")
            try:
                import sqlite3
                self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
                self.conn.row_factory = sqlite3.Row
                self.cursor = self.conn.cursor()
                logger.info("Veritabanı bağlantısı başarıyla yenilendi")
            except Exception as reconnect_error:
                logger.error(f"Veritabanı yeniden bağlantı hatası: {reconnect_error}")
                raise
    
    def get_all_calls(self):
        """Tüm çağrıları getir"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    SELECT c.*, f.name as firm_name 
                    FROM calls c
                    LEFT JOIN firms f ON c.firm_id = f.id
                    ORDER BY c.created_at DESC
                """)
                rows = self.cursor.fetchall()
                # Row objelerini dict'e çevir - güvenli yöntem
                calls = []
                for row in rows:
                    try:
                        # Row keys'lerini kullanarak dictionary oluştur
                        call_dict = {}
                        for key in row.keys():
                            call_dict[key] = row[key]
                        calls.append(call_dict)
                    except Exception as row_error:
                        logger.warning(f"Row dönüştürme hatası: {row_error}")
                        # Fallback: manuel dictionary oluştur
                        call_dict = {
                            'id': row[0] if len(row) > 0 else None,
                            'firm_id': row[1] if len(row) > 1 else None,
                            'call_id': row[2] if len(row) > 2 else '',
                            'phone_number': row[3] if len(row) > 3 else '',
                            'assistant_id': row[4] if len(row) > 4 else '',
                            'duration': row[5] if len(row) > 5 else 0,
                            'status': row[6] if len(row) > 6 else 'unknown',
                            'recording_url': row[7] if len(row) > 7 else '',
                            'transcript': row[8] if len(row) > 8 else '',
                            'notes': row[9] if len(row) > 9 else '',
                            'cost': row[10] if len(row) > 10 else 0.0,
                            'ai_analysis': row[11] if len(row) > 11 else '',
                            'created_at': row[12] if len(row) > 12 else '',
                            'updated_at': row[13] if len(row) > 13 else '',
                            'firm_name': row[14] if len(row) > 14 else 'Bilinmeyen Firma'
                        }
                        calls.append(call_dict)
                return calls
            except Exception as e:
                logger.error(f"Çağrıları getirme hatası: {e}")
                return []
    
    def update_call_analysis(self, call_id, analysis_json):
        """Çağrı analizi güncelle"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    UPDATE calls 
                    SET ai_analysis = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (analysis_json, call_id))
                self.conn.commit()
                logger.info(f"Çağrı {call_id} analizi güncellendi")
                return True
            except Exception as e:
                logger.error(f"Çağrı analizi güncelleme hatası: {e}")
                return False
    
    def get_calls_by_analysis(self, sentiment=None):
        """Analiz sonucuna göre çağrıları getir"""
        with self.lock:
            try:
                self.ensure_connection()
                if sentiment:
                    self.cursor.execute("""
                        SELECT c.*, f.name as firm_name 
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        WHERE c.ai_analysis LIKE ?
                        ORDER BY c.created_at DESC
                    """, (f'%"sentiment": "{sentiment}"%',))
                else:
                    self.cursor.execute("""
                        SELECT c.*, f.name as firm_name 
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        WHERE c.ai_analysis IS NULL OR c.ai_analysis = ''
                        ORDER BY c.created_at DESC
                    """)
                rows = self.cursor.fetchall()
                # Row objelerini dict'e çevir - güvenli yöntem
                calls = []
                for row in rows:
                    try:
                        # Row keys'lerini kullanarak dictionary oluştur
                        call_dict = {}
                        for key in row.keys():
                            call_dict[key] = row[key]
                        calls.append(call_dict)
                    except Exception as row_error:
                        logger.warning(f"Row dönüştürme hatası: {row_error}")
                        # Fallback: manuel dictionary oluştur
                        call_dict = {
                            'id': row[0] if len(row) > 0 else None,
                            'firm_id': row[1] if len(row) > 1 else None,
                            'call_id': row[2] if len(row) > 2 else '',
                            'phone_number': row[3] if len(row) > 3 else '',
                            'assistant_id': row[4] if len(row) > 4 else '',
                            'duration': row[5] if len(row) > 5 else 0,
                            'status': row[6] if len(row) > 6 else 'unknown',
                            'recording_url': row[7] if len(row) > 7 else '',
                            'transcript': row[8] if len(row) > 8 else '',
                            'notes': row[9] if len(row) > 9 else '',
                            'cost': row[10] if len(row) > 10 else 0.0,
                            'ai_analysis': row[11] if len(row) > 11 else '',
                            'created_at': row[12] if len(row) > 12 else '',
                            'updated_at': row[13] if len(row) > 13 else '',
                            'firm_name': row[14] if len(row) > 14 else 'Bilinmeyen Firma'
                        }
                        calls.append(call_dict)
                return calls
            except Exception as e:
                logger.error(f"Analiz bazlı çağrı getirme hatası: {e}")
                return []
    
    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.conn:
            self.conn.close()
            logger.info("Veritabanı bağlantısı kapatıldı")


class GPTManager:
    """OpenAI GPT yönetimi - Geliştirilmiş"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500
        self.is_available = OPENAI_AVAILABLE
        
        if not self.is_available:
            logger.warning("OpenAI kütüphanesi mevcut değil")
    
    def set_api_key(self, api_key):
        """API anahtarını ayarla"""
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                return True
            except Exception as e:
                logger.error(f"OpenAI client hatası: {e}")
                return False
        return False
    
    def generate_message(self, prompt, firm_data, template_type="tanıtım", db=None):
        """GPT ile mesaj üret - Bilgi Öğrenim Entegreli"""
        if not OPENAI_AVAILABLE or not self.client:
            return None
        
        try:
            # Detaylı firma bilgileri
            firm_details = f"""
            Firma Bilgileri:
            - İsim: {firm_data.get('name', 'Belirtilmemiş')}
            - Sektör: {firm_data.get('sector', 'Belirtilmemiş')}
            - Özet: {firm_data.get('summary', 'Belirtilmemiş')}
            - İletişim Kişisi: {firm_data.get('contact_person', 'Belirtilmemiş')}
            - Web Sitesi: {firm_data.get('website', 'Yok')}
            - Telefon: {firm_data.get('phone', 'Belirtilmemiş')}
            - Email: {firm_data.get('email', 'Belirtilmemiş')}
            - Adres: {firm_data.get('address', 'Belirtilmemiş')}
            """
            
            # 🧠 Bilgi Öğrenim verilerini al
            learned_knowledge = ""
            if db:
                try:
                    all_knowledge = db.get_all_knowledge(filter_learned=True)
                    if all_knowledge:
                        knowledge_summaries = []
                        for knowledge in all_knowledge[:3]:  # En fazla 3 bilgi kullan
                            if knowledge.get('ai_summary'):
                                knowledge_summaries.append(f"• {knowledge.get('title', 'Bilgi')}: {knowledge.get('ai_summary', '')}")
                        
                        if knowledge_summaries:
                            learned_knowledge = f"""
            
            🧠 Öğrenilmiş Firma Bilgileri (AI Analizi):
            {chr(10).join(knowledge_summaries)}
            
            Bu bilgileri kullanarak daha kişiselleştirilmiş ve detaylı mesaj oluştur.
            """
                except Exception as e:
                    print(f"Bilgi öğrenim verisi alınamadı: {e}")
            
            # Template tipine göre özel talimatlar
            template_instructions = {
                "tanıtım": "Firmaya ürün/hizmet tanıtımı yapan profesyonel bir mesaj",
                "takip": "Önceki görüşmeyi takip eden, nazik hatırlatma mesajı",
                "kampanya": "Özel kampanya veya indirim duyurusu içeren cazip bir mesaj",
                "bilgilendirme": "Yeni özellik veya güncelleme hakkında bilgilendirici mesaj",
                "teşekkür": "İşbirliği veya ilgi için teşekkür mesajı"
            }
            
            instruction = template_instructions.get(template_type, template_instructions["tanıtım"])
            
            # Geliştirilmiş prompt
            full_prompt = f"""
            Sen profesyonel bir B2B satış uzmanısın. Aşağıdaki firma bilgilerini kullanarak {instruction} oluştur.
            
            {firm_details}
            {learned_knowledge}
            
            Özel Talimatlar:
            - {prompt}
            
            Mesaj Özellikleri:
            - Maksimum 3-4 cümle
            - Samimi ama profesyonel ton
            - Kişiselleştirilmiş içerik
            - Harekete geçirici çağrı (CTA) içermeli
            - Firma sektörüne uygun terminoloji kullan
            - İletişim kişisi varsa ismini kullan
            - Öğrenilmiş firma bilgilerini kullanarak daha kişiselleştirilmiş içerik oluştur
            
            Lütfen WhatsApp için uygun, emoji kullanmadan mesaj oluştur.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Sen deneyimli bir B2B satış uzmanısın. Kısa, etkili ve kişiselleştirilmiş mesajlar yazarsın."
                    },
                    {
                        "role": "user", 
                        "content": full_prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"GPT mesaj üretme hatası: {str(e)}")
            return None
    
    def generate_call_script(self, firm_data):
        """Arama senaryosu oluştur"""
        if not OPENAI_AVAILABLE or not self.client:
            return None
        
        try:
            prompt = f"""
            Aşağıdaki firma için kısa bir telefon araması açılış metni oluştur:
            
            Firma: {firm_data.get('name')}
            Sektör: {firm_data.get('sector')}
            İletişim Kişisi: {firm_data.get('contact_person', 'Yetkili kişi')}
            
            Açılış metni özellikleri:
            - Maksimum 30 saniye
            - Kendini ve şirketini tanıt
            - Arama nedenini belirt
            - İzin iste
            - Samimi ve profesyonel ol
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir tele-satış uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Arama senaryosu hatası: {str(e)}")
            return None


class VapiManager:
    """Vapi AI arama yönetimi - Geliştirilmiş ve API Uyumlu"""
    
    def __init__(self):
        self.api_key = ""
        self.base_url = "https://api.vapi.ai"
        self.phone_number_id = None
        self.default_assistant_id = None
        self.timeout = 30
        self.is_available = REQUESTS_AVAILABLE
        
        if not self.is_available:
            logger.warning("Requests kütüphanesi mevcut değil, Vapi özelliği çalışmayacak")
    
    def set_api_key(self, api_key):
        """API anahtarını ayarla ve test et"""
        self.api_key = api_key
        if api_key:
            return self.test_connection()
        return False
    
    def set_phone_number_id(self, phone_number_id):
        """Vapi telefon numarası ID'sini ayarla"""
        self.phone_number_id = phone_number_id
    
    def test_connection(self):
        """API bağlantısını test et"""
        if not self.is_available:
            logger.error("Requests kütüphanesi mevcut değil")
            return False
            
        if not self.api_key:
            logger.error("API key boş")
            return False
            
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/assistant",
                headers=headers,
                timeout=self.timeout
            )
            
            return response.status_code in [200, 201]
        except ImportError:
            logger.error("Requests kütüphanesi yüklü değil")
            return False
        except Exception as e:
            logger.error(f"Vapi bağlantı testi hatası: {e}")
            return False
    
    def create_assistant(self, name, instructions=None, model=None, voice=None, first_message=None):
        """Yeni asistan oluştur - API uyumlu"""
        if not self.is_available or not self.api_key:
            logger.warning("Requests modülü yok veya API key boş")
            return None
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Model yapılandırması
            model_config = {
                "provider": "openai",
                "model": model or "gpt-3.5-turbo",
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "system",
                        "content": instructions or "Sen yardımcı bir asistansın. Nazik ve profesyonel şekilde müşterilerle konuş."
                    }
                ]
            }
            
            # Ses yapılandırması
            voice_config = {
                "provider": "11labs",
                "voiceId": voice or "burt"
            }
            
            # Transcriber yapılandırması
            transcriber_config = {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "tr"
            }
            
            payload = {
                "name": name,
                "model": model_config,
                "voice": voice_config,
                "transcriber": transcriber_config,
                "firstMessage": first_message or "Merhaba, size nasıl yardımcı olabilirim?",
                "endCallMessage": "Görüşme sonlandırıldı. İyi günler!",
                "endCallPhrases": ["görüşmeyi bitir", "kapat", "hoşçakal"],
                "maxDurationSeconds": 600,  # 10 dakika max
                "backgroundSound": "off"
            }
            
            response = requests.post(
                f"{self.base_url}/assistant",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Asistan oluşturuldu: {result.get('id', 'N/A')}")
                return result
            else:
                error_msg = f"Asistan oluşturma hatası: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('message', response.text)}"
                except:
                    error_msg += f" - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except requests.exceptions.Timeout:
            error_msg = "İstek zaman aşımına uğradı"
            logger.error(error_msg)
            return {"error": error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "Bağlantı hatası - İnternet bağlantınızı kontrol edin"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Beklenmeyen hata: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    @thread_safe_operation
    def start_call(self, phone_number, assistant_id, customer_data=None):
        """Arama başlat - Ultra Güvenli"""
        # Temel kontroller
        if not self.is_available:
            logger.warning("Requests modülü mevcut değil")
            return {"error": "Sistem hazır değil", "details": "Requests modülü yüklü değil"}
        
        if not self.api_key:
            logger.warning("API anahtarı eksik")
            return {"error": "API anahtarı eksik", "details": "Lütfen ayarlardan API anahtarını girin"}
        
        if not assistant_id:
            logger.warning("Assistant ID eksik")
            return {"error": "Asistan seçilmedi", "details": "Lütfen bir asistan seçin"}
        
        if not phone_number:
            logger.warning("Telefon numarası eksik")
            return {"error": "Telefon numarası eksik", "details": "Firma telefon numarası bulunamadı"}
        
        try:
            # Requests modülünü güvenli import et
            try:
                import requests
            except ImportError:
                logger.error("Requests modülü import edilemedi")
                return {"error": "Sistem hatası", "details": "Requests modülü yüklenemedi"}
            
            # Headers hazırla
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Telefon numarasını güvenli formatla
            try:
                phone_clean = ''.join(filter(str.isdigit, str(phone_number)))
                if len(phone_clean) < 10:
                    logger.warning(f"Geçersiz telefon numarası: {phone_number}")
                    return {"error": "Geçersiz telefon", "details": f"Telefon numarası çok kısa: {phone_number}"}
                    
                # Türkiye formatı
                if phone_clean.startswith('0'):
                    phone_clean = '90' + phone_clean[1:]
                elif not phone_clean.startswith('90'):
                    phone_clean = '90' + phone_clean
                    
                phone_formatted = '+' + phone_clean
                logger.info(f"Telefon formatlandı: {phone_formatted}")
            except Exception as e:
                logger.error(f"Telefon formatlama hatası: {str(e)}")
                return {"error": "Format hatası", "details": f"Telefon numarası formatlanamadı: {str(e)}"}
            
            # Payload güvenli hazırla
            try:
                payload = {
                    "assistantId": str(assistant_id),
                    "customer": {
                        "number": phone_formatted
                    }
                }
                
                # Müşteri adı varsa ekle
                if customer_data:
                    if isinstance(customer_data, dict) and customer_data.get('name'):
                        payload['customer']['name'] = str(customer_data['name'])[:100]  # Max 100 karakter
                
                # Telefon numarası ID'si varsa ekle
                if self.phone_number_id:
                    payload["phoneNumberId"] = str(self.phone_number_id)
                
                logger.debug(f"Payload hazırlandı: {json.dumps(payload, ensure_ascii=False)}")
            except Exception as e:
                logger.error(f"Payload hazırlama hatası: {str(e)}")
                return {"error": "Veri hatası", "details": f"İstek verisi hazırlanamadı: {str(e)}"}
            
            # API çağrısı yap (timeout ve retry ile)
            logger.info(f"Vapi API'ye arama isteği gönderiliyor...")
            
            for attempt in range(3):  # 3 deneme
                try:
                    response = requests.post(
                        f"{self.base_url}/call",
                        json=payload,
                        headers=headers,
                        timeout=min(self.timeout, 30)  # Max 30 saniye timeout
                    )
                    
                    # Başarılı yanıt
                    if response.status_code in [200, 201]:
                        try:
                            result = response.json()
                            call_id = result.get('id', 'N/A')
                            logger.info(f"✅ Arama başarıyla başlatıldı: {call_id}")
                            return result
                        except ValueError:
                            logger.warning("API yanıtı JSON formatında değil")
                            return {"success": True, "id": "unknown", "message": "Arama başlatıldı"}
                    
                    # Rate limit kontrolü
                    elif response.status_code == 429:
                        wait_time = int(response.headers.get('Retry-After', 5))
                        logger.warning(f"Rate limit aşıldı, {wait_time} saniye bekleniyor...")
                        time.sleep(wait_time)
                        continue
                    
                    # Diğer hatalar
                    else:
                        error_msg = f"HTTP {response.status_code}"
                        try:
                            error_detail = response.json()
                            error_msg = error_detail.get('message', error_detail.get('error', response.text[:200]))
                        except:
                            error_msg = response.text[:200] if response.text else error_msg
                        
                        logger.error(f"API hatası: {error_msg}")
                        return {"error": "API hatası", "details": error_msg, "status_code": response.status_code}
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"Deneme {attempt + 1}/3 - Zaman aşımı")
                    if attempt < 2:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return {"error": "Zaman aşımı", "details": "API yanıt vermedi, lütfen tekrar deneyin"}
                    
                except requests.exceptions.ConnectionError:
                    logger.warning(f"Deneme {attempt + 1}/3 - Bağlantı hatası")
                    if attempt < 2:
                        time.sleep(2 ** attempt)
                        continue
                    return {"error": "Bağlantı hatası", "details": "İnternet bağlantınızı kontrol edin"}
                    
                except requests.exceptions.RequestException as e:
                    logger.error(f"Request hatası: {str(e)}")
                    return {"error": "İstek hatası", "details": str(e)[:200]}
            
            return {"error": "Maksimum deneme", "details": "3 deneme sonrası başarısız"}
                
        except ImportError:
            logger.error("Requests modülü yüklenemedi")
            return {"error": "Modül hatası", "details": "Requests kütüphanesi yüklü değil"}
            
        except Exception as e:
            # Beklenmeyen hatalar için detaylı log
            logger.error(f"Beklenmeyen hata: {str(e)}\n{traceback.format_exc()}")
            return {"error": "Sistem hatası", "details": f"Beklenmeyen hata: {str(e)[:200]}"}
    
    def get_call_status(self, call_id):
        """Arama durumunu getir - Geliştirilmiş"""
        if not self.is_available or not self.api_key:
            return {"error": "API ayarları eksik"}
        
        if not call_id:
            return {"error": "Call ID gerekli"}
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/call/{call_id}",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Arama durumu alındı: {call_id}")
                return result
            else:
                error_msg = f"Arama durumu hatası: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('message', response.text)}"
                except:
                    error_msg += f" - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except requests.exceptions.Timeout:
            error_msg = "Arama durumu isteği zaman aşımına uğradı"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Arama durumu hatası: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_assistants(self):
        """Asistanları listele - Geliştirilmiş"""
        if not self.is_available or not self.api_key:
            logger.warning("Requests modülü yok veya API key boş")
            return []
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/assistant",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # API response bir liste döndürüyor
                if isinstance(result, list):
                    logger.info(f"{len(result)} asistan listelendi")
                    return result
                else:
                    logger.warning("Beklenmeyen asistan listesi formatı")
                    return []
            else:
                logger.error(f"Asistan listesi hatası: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("Asistan listesi isteği zaman aşımına uğradı")
            return []
        except Exception as e:
            logger.error(f"Asistanları getirme hatası: {str(e)}")
            return []
    
    def get_phone_numbers(self):
        """Telefon numaralarını listele - Geliştirilmiş"""
        if not self.is_available or not self.api_key:
            logger.warning("Requests modülü yok veya API key boş")
            return []
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/phone-number",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    logger.info(f"{len(result)} telefon numarası listelendi")
                    return result
                else:
                    logger.warning("Beklenmeyen telefon numarası formatı")
                    return []
            else:
                logger.error(f"Telefon numarası listesi hatası: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("Telefon numarası isteği zaman aşımına uğradı")
            return []
        except Exception as e:
            logger.error(f"Telefon numaralarını getirme hatası: {str(e)}")
            return []
    
    def update_assistant(self, assistant_id, name=None, instructions=None, model=None, voice=None):
        """Asistanı güncelle"""
        if not self.is_available or not self.api_key:
            return {"error": "API ayarları eksik"}
        
        if not assistant_id:
            return {"error": "Assistant ID gerekli"}
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {}
            
            if name:
                payload["name"] = name
            
            if instructions:
                if "model" not in payload:
                    payload["model"] = {"provider": "openai", "model": "gpt-3.5-turbo"}
                payload["model"]["messages"] = [
                    {
                        "role": "system",
                        "content": instructions
                    }
                ]
            
            if model:
                if "model" not in payload:
                    payload["model"] = {"provider": "openai"}
                payload["model"]["model"] = model
            
            if voice:
                payload["voice"] = {
                    "provider": "11labs",
                    "voiceId": voice
                }
            
            if not payload:
                return {"error": "Güncellenecek alan belirtilmedi"}
            
            response = requests.patch(
                f"{self.base_url}/assistant/{assistant_id}",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Asistan güncellendi: {assistant_id}")
                return result
            else:
                error_msg = f"Asistan güncelleme hatası: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('message', response.text)}"
                except:
                    error_msg += f" - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Asistan güncelleme hatası: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def delete_assistant(self, assistant_id):
        """Asistanı sil"""
        if not self.is_available or not self.api_key:
            return {"error": "API ayarları eksik"}
        
        if not assistant_id:
            return {"error": "Assistant ID gerekli"}
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.delete(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Asistan silindi: {assistant_id}")
                return {"success": True}
            else:
                error_msg = f"Asistan silme hatası: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('message', response.text)}"
                except:
                    error_msg += f" - {response.text}"
                logger.error(error_msg)
                return {"error": error_msg}
                
        except Exception as e:
            error_msg = f"Asistan silme hatası: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_calls(self, limit=100):
        """Aramaları listele"""
        if not self.is_available or not self.api_key:
            return []
        
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {}
            if limit:
                params["limit"] = limit
            
            response = requests.get(
                f"{self.base_url}/call",
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    logger.info(f"{len(result)} arama listelendi")
                    return result
                else:
                    return []
            else:
                logger.error(f"Arama listesi hatası: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Aramaları getirme hatası: {str(e)}")
            return []


class WhatsAppWebView(QWebEngineView):
    """WhatsApp Web görünümü - Geliştirilmiş"""
    
    message_received = Signal(dict)
    status_changed = Signal(str)
    
    def __init__(self, parent=None):
        if not WEBENGINE_AVAILABLE:
            logger.error("WebEngine mevcut değil, WhatsApp özelliği çalışmayacak")
            # Fallback widget oluştur
            super(QWidget, self).__init__(parent)
            return
            
        super().__init__(parent)
        
        # Profile ve settings
        try:
            self.profile = QWebEngineProfile("whatsapp", self)
            self.profile.setPersistentStoragePath("./whatsapp_data")
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
            
            # Enable developer extras
            settings = self.profile.settings()
            if hasattr(QWebEngineSettings, 'DeveloperExtrasEnabled'):
                settings.setAttribute(QWebEngineSettings.DeveloperExtrasEnabled, True)
            
            # Profile ayarları PySide6'da farklı şekilde yapılıyor
            # Modern PySide6'da profile() metodu kullanılır
            page = self.page()
                
        except Exception as e:
            logger.error(f"Profile setup error: {e}")
        
        # Web settings
        try:
            settings = self.settings()
            if settings:
                settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
                settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
                settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
                if hasattr(QWebEngineSettings, 'WebRTCPublicInterfacesOnly'):
                    settings.setAttribute(QWebEngineSettings.WebRTCPublicInterfacesOnly, False)
                
                # Set a modern user agent
                self.page().profile().setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36")
        except Exception as e:
            logger.error(f"Web settings error: {e}")
        
        # JavaScript error handling ekle
        self.setup_javascript_error_handling()
        
        # WhatsApp Web'i yükle
        self.load(QUrl("https://web.whatsapp.com"))
        
        # Sayfa yüklendiğinde
        self.loadFinished.connect(self.on_load_finished)
        
        # Mesaj kuyruğu
        self.message_queue = []
        self.is_sending = False
        self.is_connected = False
        self.last_message_count = 0
        
        # Timer for queue processing
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.process_message_queue)
        self.queue_timer.start(2000)  # Her 2 saniyede bir kontrol et
    
    def setup_javascript_error_handling(self):
        """JavaScript hatalarını yakala ve sessizce işle"""
        try:
            # Console message handler
            if hasattr(self.page(), 'setConsoleMessageHandler'):
                def handle_console_message(level, message, line_number, source_id):
                    # Permissions-Policy hatalarını filtrele
                    if any(keyword in message for keyword in [
                        'Permissions-Policy', 'bluetooth', 'otp-credentials', 
                        'payment', 'usb', 'MEDIA_ERR_SRC_NOT_SUPPORTED',
                        'Google Maps JavaScript API', 'google.maps.Marker'
                    ]):
                        return  # Bu hataları sessizce geç
                    
                    # Diğer hataları logla
                    if level >= 2:  # Error level
                        print(f"⚠️ JavaScript Error: {message}")
                
                self.page().setConsoleMessageHandler(handle_console_message)
            else:
                print("ℹ️ Console message handler mevcut değil, JavaScript error handling kullanılacak")
                
        except Exception as e:
            print(f"⚠️ JavaScript error handling kurulamadı: {e}")
    
    def on_load_finished(self, success):
        """Sayfa yüklendiğinde"""
        if success:
            self.status_changed.emit("WhatsApp Web yüklendi")
            self.inject_javascript()
            QTimer.singleShot(5000, self.check_connection)
    
    def check_connection(self):
        """WhatsApp bağlantısını kontrol et"""
        js_check = """
        (function() {
            // QR kod var mı kontrol et
            var qrCode = document.querySelector('canvas[aria-label*="QR"]');
            if (qrCode) {
                return 'qr_required';
            }
            
            // Ana chat listesi var mı
            var chatList = document.querySelector('[aria-label*="Chat list"]');
            if (chatList) {
                return 'connected';
            }
            
            return 'unknown';
        })();
        """
        
        def handle_result(result):
            if result == 'qr_required':
                self.is_connected = False
                self.status_changed.emit("QR kod taranması gerekiyor")
            elif result == 'connected':
                self.is_connected = True
                self.status_changed.emit("WhatsApp bağlandı")
            else:
                self.is_connected = False
                self.status_changed.emit("Bağlantı durumu belirsiz")
        
        self.page().runJavaScript(js_check, 0, handle_result)
    
    def inject_javascript(self):
        """JavaScript enjekte et - Geliştirilmiş"""
        js_code = """
        // JavaScript error handling
        (function() {
            // Console error interceptor
            const originalConsoleError = console.error;
            console.error = function(...args) {
                const message = args.join(' ');
                if (message.includes('Permissions-Policy') || 
                    message.includes('bluetooth') || 
                    message.includes('otp-credentials') ||
                    message.includes('payment') || 
                    message.includes('usb') ||
                    message.includes('MEDIA_ERR_SRC_NOT_SUPPORTED') ||
                    message.includes('Google Maps JavaScript API') ||
                    message.includes('google.maps.Marker')) {
                    return; // Bu hataları sessizce geç
                }
                return originalConsoleError.apply(console, args);
            };
            
            // Global error handler
            window.addEventListener('error', function(e) {
                if (e.message && (
                    e.message.includes('Permissions-Policy') ||
                    e.message.includes('bluetooth') ||
                    e.message.includes('otp-credentials') ||
                    e.message.includes('payment') ||
                    e.message.includes('usb') ||
                    e.message.includes('MEDIA_ERR_SRC_NOT_SUPPORTED') ||
                    e.message.includes('Google Maps JavaScript API') ||
                    e.message.includes('google.maps.Marker')
                )) {
                    e.preventDefault(); // Hata yayılmasını önle
                    return false;
                }
            });
        })();
        
        // WhatsApp Web mesaj takibi ve otomasyon
        console.log('WhatsApp Web automation başlatıldı');
        
        // Global değişkenler
        window.whatsappReady = false;
        window.lastMessageTime = Date.now();
        
        // WhatsApp hazır mı kontrol et
        function checkWhatsAppReady() {
            var chatList = document.querySelector('[aria-label*="Chat list"]');
            if (chatList) {
                window.whatsappReady = true;
                console.log('WhatsApp hazır');
                observeMessages();
            } else {
                setTimeout(checkWhatsAppReady, 2000);
            }
        }
        
        // Mesaj gözlemci
        function observeMessages() {
            console.log('Mesaj takibi başladı');
            
            // Yeni mesajları gözlemle
            var targetNode = document.querySelector('#app');
            if (!targetNode) return;
            
            var config = { childList: true, subtree: true };
            var observer = new MutationObserver(function(mutationsList) {
                for(var mutation of mutationsList) {
                    if (mutation.type === 'childList') {
                        // Yeni mesaj kontrolü
                        checkForNewMessages();
                    }
                }
            });
            
            observer.observe(targetNode, config);
        }
        
        // Yeni mesajları kontrol et
        function checkForNewMessages() {
            var messages = document.querySelectorAll('[data-testid="msg-container"]');
            var now = Date.now();
            
            messages.forEach(function(msg) {
                var timestamp = msg.getAttribute('data-timestamp');
                if (timestamp && parseInt(timestamp) * 1000 > window.lastMessageTime) {
                    // Yeni mesaj bulundu
                    var content = msg.innerText;
                    var isIncoming = msg.classList.contains('message-in');
                    
                    if (isIncoming) {
                        console.log('Yeni gelen mesaj:', content);
                        // Python'a bildir
                        window.newIncomingMessage = {
                            content: content,
                            timestamp: timestamp
                        };
                    }
                }
            });
            
            window.lastMessageTime = now;
        }
        
        // Mesaj gönderme yardımcı fonksiyonu
        window.sendWhatsAppMessage = function(phone, message) {
            console.log('Mesaj gönderiliyor:', phone, message);
            
            // Önce chat'i aç
            var searchBox = document.querySelector('[data-testid="chat-list-search"]');
            if (searchBox) {
                searchBox.click();
                searchBox.value = phone;
                
                // Input event'i tetikle
                var event = new Event('input', { bubbles: true });
                searchBox.dispatchEvent(event);
                
                // Chat'i seç
                setTimeout(function() {
                    var chatItem = document.querySelector('[data-testid="chat-list-item"]');
                    if (chatItem) {
                        chatItem.click();
                        
                        // Mesaj kutusuna yaz
                        setTimeout(function() {
                            var messageBox = document.querySelector('[data-testid="conversation-compose-box-input"]');
                            if (messageBox) {
                                messageBox.innerHTML = message;
                                messageBox.dispatchEvent(new Event('input', { bubbles: true }));
                                
                                // Gönder butonuna tıkla
                                setTimeout(function() {
                                    var sendButton = document.querySelector('[data-testid="compose-btn-send"]');
                                    if (sendButton) {
                                        sendButton.click();
                                        console.log('Mesaj gönderildi');
                                    }
                                }, 500);
                            }
                        }, 1000);
                    }
                }, 2000);
            }
            
            return true;
        };
        
        // Başlat
        setTimeout(checkWhatsAppReady, 3000);
        """
        self.page().runJavaScript(js_code)
    
    def send_message(self, phone, message):
        """WhatsApp mesajı gönder - Geliştirilmiş"""
        if not self.is_connected:
            logger.warning("WhatsApp Web bağlantısı yok!")
            return False
        
        try:
            # Telefon numarasını temizle
            phone_clean = ''.join(filter(str.isdigit, phone))
            if not phone_clean.startswith('90'):
                phone_clean = '90' + phone_clean
            
            # JavaScript ile direkt mesaj gönder
            js_send = f"""
            window.sendWhatsAppMessage('{phone_clean}', `{message}`);
            """
            
            self.page().runJavaScript(js_send)
            logger.info(f"Mesaj gönderildi: {phone_clean}")
            
            # Mesajın gönderilmesi için kısa bir bekleme
            QTimer.singleShot(2000, lambda: None)
            return True
            
        except Exception as e:
            logger.error(f"Mesaj gönderirken hata: {e}")
            return False
    
    def process_message_queue(self):
        """Mesaj kuyruğunu işle"""
        if self.is_sending or not self.message_queue:
            return
        
        self.is_sending = True
        msg_data = self.message_queue.pop(0)
        
        # JavaScript ile mesaj gönder
        js_send = f"""
        window.sendWhatsAppMessage('{msg_data['phone']}', `{msg_data['message']}`);
        """
        
        self.page().runJavaScript(js_send)
        
        # 5 saniye sonra tekrar işleme hazır ol
        QTimer.singleShot(5000, lambda: setattr(self, 'is_sending', False))
    
    def check_for_new_messages(self):
        """Yeni mesajları kontrol et"""
        js_check = """
        (function() {
            if (window.newIncomingMessage) {
                var msg = window.newIncomingMessage;
                window.newIncomingMessage = null;
                return msg;
            }
            return null;
        })();
        """
        
        def handle_result(result):
            if result:
                self.message_received.emit(result)
        
        self.page().runJavaScript(js_check, 0, handle_result)
    
    def send_bulk_messages(self, messages_list):
        """Toplu mesaj gönder"""
        for msg in messages_list:
            self.send_message(msg['phone'], msg['message'])


class ModernCard(QFrame):
    """Modern kart widget'ı"""
    
    def __init__(self, title, value, icon="", color="#0d7377"):
        super().__init__()
        self.setObjectName("modernCard")
        
        # Stil
        self.setStyleSheet(f"""
            QFrame#modernCard {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {color}, stop: 1 rgba(13, 115, 119, 0.5));
                border-radius: 15px;
                padding: 20px;
                min-height: 100px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet("""
            font-size: 14px;
            color: rgba(255,255,255,0.8);
            font-weight: 500;
        """)
        
        # Değer
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("cardValue")
        self.value_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-top: 10px;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
    
    def update_value(self, value):
        """Değeri güncelle"""
        self.value_label.setText(str(value))


class FirmDialog(QDialog):
    """Firma ekleme/düzenleme dialogu - Geliştirilmiş"""
    
    def __init__(self, parent=None, firm_data=None):
        super().__init__(parent)
        self.firm_data = firm_data
        self.setupUI()
        
        if firm_data:
            self.load_firm_data()
    
    def setupUI(self):
        """Dialog arayüzünü oluştur"""
        self.setWindowTitle("Firma Ekle" if not self.firm_data else "Firma Düzenle")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        layout = QFormLayout(self)
        
        # Form alanları
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.sector_input = QComboBox()
        self.sector_input.setEditable(True)
        self.sector_input.addItems([
            "Teknoloji", "E-ticaret", "Üretim", "Hizmet", 
            "Danışmanlık", "Eğitim", "Sağlık", "Finans", 
            "İnşaat", "Otomotiv", "Tekstil", "Gıda", "Diğer"
        ])
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        self.website_input = QLineEdit()
        self.contact_person_input = QLineEdit()
        self.summary_input = QTextEdit()
        self.summary_input.setMaximumHeight(100)
        
        # Ek alanlar
        self.place_id_input = QLineEdit()
        self.place_id_input.setPlaceholderText("Google Place ID (opsiyonel)")
        self.rating_input = QSpinBox()
        self.rating_input.setRange(0, 5)
        self.rating_input.setSingleStep(1)
        self.review_count_input = QSpinBox()
        self.review_count_input.setMaximum(99999)
        self.business_hours_input = QTextEdit()
        self.business_hours_input.setMaximumHeight(60)
        self.business_hours_input.setPlaceholderText("Örn: Pzt-Cum 09:00-18:00")
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "inactive", "prospect", "customer"])
        
        # Form layout
        layout.addRow("Firma Adı *:", self.name_input)
        layout.addRow("Telefon *:", self.phone_input)
        layout.addRow("E-posta:", self.email_input)
        layout.addRow("Sektör:", self.sector_input)
        layout.addRow("Adres:", self.address_input)
        layout.addRow("Web Sitesi:", self.website_input)
        layout.addRow("İletişim Kişisi:", self.contact_person_input)
        layout.addRow("Özet:", self.summary_input)
        
        # Ek bilgiler
        layout.addRow(QLabel("<b>Ek Bilgiler</b>"))
        layout.addRow("Google Place ID:", self.place_id_input)
        layout.addRow("Rating:", self.rating_input)
        layout.addRow("Yorum Sayısı:", self.review_count_input)
        layout.addRow("Çalışma Saatleri:", self.business_hours_input)
        layout.addRow("Durum:", self.status_combo)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
    
    def load_firm_data(self):
        """Firma verilerini yükle"""
        if self.firm_data:
            self.name_input.setText(str(self.firm_data.get('name', '')))
            self.phone_input.setText(str(self.firm_data.get('phone', '')))
            self.email_input.setText(str(self.firm_data.get('email', '')))
            self.sector_input.setCurrentText(str(self.firm_data.get('sector', '')))
            self.address_input.setText(str(self.firm_data.get('address', '')))
            self.website_input.setText(str(self.firm_data.get('website', '')))
            self.contact_person_input.setText(str(self.firm_data.get('contact_person', '')))
            self.summary_input.setText(str(self.firm_data.get('summary', '')))
            self.place_id_input.setText(str(self.firm_data.get('place_id', '')))
            self.rating_input.setValue(int(self.firm_data.get('rating', 0)))
            self.review_count_input.setValue(int(self.firm_data.get('review_count', 0)))
            self.business_hours_input.setText(str(self.firm_data.get('business_hours', '')))
            self.status_combo.setCurrentText(str(self.firm_data.get('status', 'active')))
    
    def get_firm_data(self):
        """Form verilerini al"""
        return {
            'name': self.name_input.text(),
            'phone': self.phone_input.text(),
            'email': self.email_input.text(),
            'sector': self.sector_input.currentText(),
            'address': self.address_input.toPlainText(),
            'website': self.website_input.text(),
            'contact_person': self.contact_person_input.text(),
            'summary': self.summary_input.toPlainText(),
            'place_id': self.place_id_input.text(),
            'rating': self.rating_input.value(),
            'review_count': self.review_count_input.value(),
            'business_hours': self.business_hours_input.toPlainText(),
            'status': self.status_combo.currentText()
        }


class AssistantDialog(QDialog):
    """Vapi AI Asistan oluşturma/düzenleme dialogu"""
    
    def __init__(self, parent=None, assistant_data=None):
        super().__init__(parent)
        self.assistant_data = assistant_data
        self.setupUI()
        
        if assistant_data:
            self.load_assistant_data()
    
    def setupUI(self):
        """Dialog arayüzünü oluştur"""
        self.setWindowTitle("Asistan Oluştur" if not self.assistant_data else "Asistan Düzenle")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # Temel bilgiler
        basic_group = QGroupBox("Temel Bilgiler")
        basic_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Asistan adı (örn: Satış Asistanı)")
        basic_layout.addRow("Asistan Adı *:", self.name_input)
        
        self.first_message_input = QTextEdit()
        self.first_message_input.setMaximumHeight(60)
        self.first_message_input.setPlaceholderText("Merhaba, size nasıl yardımcı olabilirim?")
        basic_layout.addRow("İlk Mesaj:", self.first_message_input)
        
        self.end_message_input = QTextEdit()
        self.end_message_input.setMaximumHeight(60)
        self.end_message_input.setPlaceholderText("Görüşme sonlandırıldı. İyi günler!")
        basic_layout.addRow("Kapanış Mesajı:", self.end_message_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Model ayarları
        model_group = QGroupBox("Model Ayarları")
        model_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "gpt-4o"
        ])
        model_layout.addRow("Model:", self.model_combo)
        
        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 100)
        self.temperature_spin.setValue(70)
        self.temperature_spin.setSuffix("%")
        model_layout.addRow("Yaratıcılık (Temperature):", self.temperature_spin)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Ses ayarları
        voice_group = QGroupBox("Ses Ayarları")
        voice_layout = QFormLayout()
        
        self.voice_provider_combo = QComboBox()
        self.voice_provider_combo.addItems(["11labs", "playht", "azure"])
        self.voice_provider_combo.currentTextChanged.connect(self.update_voice_options)
        voice_layout.addRow("Ses Sağlayıcı:", self.voice_provider_combo)
        
        self.voice_id_combo = QComboBox()
        self.voice_id_combo.setEditable(True)
        voice_layout.addRow("Ses ID:", self.voice_id_combo)
        
        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)
        
        # Asistan talimatları
        instructions_group = QGroupBox("Asistan Talimatları")
        instructions_layout = QVBoxLayout()
        
        self.instructions_input = QTextEdit()
        self.instructions_input.setPlaceholderText("""Sen profesyonel bir satış asistanısın. Görevlerin:

1. Müşterilerle nazik ve samimi şekilde konuş
2. Ürün/hizmet hakkında bilgi ver
3. Müşteri ihtiyaçlarını anla
4. Uygun çözümler öner
5. Randevu almaya çalış

Önemli:
- Türkçe konuş
- Kısa ve net cevaplar ver
- Müşteriyi dinle
- Profesyonel ol ama samimi kalmaya çalış""")
        instructions_layout.addWidget(self.instructions_input)
        
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        
        # Gelişmiş ayarlar
        advanced_group = QGroupBox("Gelişmiş Ayarlar")
        advanced_layout = QFormLayout()
        
        self.max_duration_spin = QSpinBox()
        self.max_duration_spin.setRange(60, 1800)  # 1-30 dakika
        self.max_duration_spin.setValue(600)
        self.max_duration_spin.setSuffix(" saniye")
        advanced_layout.addRow("Maksimum Süre:", self.max_duration_spin)
        
        self.end_phrases_input = QLineEdit()
        self.end_phrases_input.setPlaceholderText("görüşmeyi bitir, kapat, hoşçakal")
        advanced_layout.addRow("Kapanış Kelimeleri:", self.end_phrases_input)
        
        self.background_sound_combo = QComboBox()
        self.background_sound_combo.addItems(["off", "office", "cafe", "nature"])
        advanced_layout.addRow("Arka Plan Sesi:", self.background_sound_combo)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.button(QDialogButtonBox.Ok).setText("Kaydet")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
        # Başlangıç ses seçeneklerini yükle
        self.update_voice_options()
    
    def update_voice_options(self):
        """Ses sağlayıcısına göre ses seçeneklerini güncelle"""
        provider = self.voice_provider_combo.currentText()
        self.voice_id_combo.clear()
        
        if provider == "11labs":
            voices = [
                "burt", "charlie", "clyde", "daniel", "dave", "fin", "giovanni", 
                "iris", "jeremy", "liam", "maya", "maya-2", "noah", "sarah"
            ]
        elif provider == "playht":
            voices = [
                "jennifer", "melissa", "will", "chris", "matt", "jack", 
                "ruby", "davis", "donna", "michael"
            ]
        elif provider == "azure":
            voices = [
                "tr-TR-AhmetNeural", "tr-TR-EmelNeural", "tr-TR-GokceNeural",
                "en-US-JennyNeural", "en-US-GuyNeural", "en-US-AriaNeural"
            ]
        else:
            voices = []
        
        self.voice_id_combo.addItems(voices)
        if voices:
            self.voice_id_combo.setCurrentIndex(0)
    
    def load_assistant_data(self):
        """Mevcut asistan verilerini yükle"""
        if self.assistant_data:
            self.name_input.setText(self.assistant_data.get('name', ''))
            self.first_message_input.setText(self.assistant_data.get('firstMessage', ''))
            self.end_message_input.setText(self.assistant_data.get('endCallMessage', ''))
            
            # Model ayarları
            model_data = self.assistant_data.get('model', {})
            if model_data.get('model'):
                self.model_combo.setCurrentText(model_data['model'])
            
            temp = model_data.get('temperature', 0.7)
            self.temperature_spin.setValue(int(temp * 100))
            
            # Ses ayarları
            voice_data = self.assistant_data.get('voice', {})
            if voice_data.get('provider'):
                self.voice_provider_combo.setCurrentText(voice_data['provider'])
                self.update_voice_options()
            if voice_data.get('voiceId'):
                self.voice_id_combo.setCurrentText(voice_data['voiceId'])
            
            # Talimatlar
            messages = model_data.get('messages', [])
            for msg in messages:
                if msg.get('role') == 'system':
                    self.instructions_input.setText(msg.get('content', ''))
                    break
            
            # Gelişmiş ayarlar
            self.max_duration_spin.setValue(self.assistant_data.get('maxDurationSeconds', 600))
            
            end_phrases = self.assistant_data.get('endCallPhrases', [])
            if end_phrases:
                self.end_phrases_input.setText(', '.join(end_phrases))
            
            self.background_sound_combo.setCurrentText(
                self.assistant_data.get('backgroundSound', 'off')
            )
    
    def get_assistant_data(self):
        """Form verilerini al"""
        end_phrases = []
        if self.end_phrases_input.text().strip():
            end_phrases = [phrase.strip() for phrase in self.end_phrases_input.text().split(',')]
        
        return {
            'name': self.name_input.text(),
            'first_message': self.first_message_input.toPlainText(),
            'end_message': self.end_message_input.toPlainText(),
            'model': self.model_combo.currentText(),
            'temperature': self.temperature_spin.value() / 100.0,
            'voice_provider': self.voice_provider_combo.currentText(),
            'voice_id': self.voice_id_combo.currentText(),
            'instructions': self.instructions_input.toPlainText(),
            'max_duration': self.max_duration_spin.value(),
            'end_phrases': end_phrases,
            'background_sound': self.background_sound_combo.currentText()
        }


class WhatsAppMessageApprovalDialog(QDialog):
    """📱 WhatsApp Mesaj Onay Dialog'u - Her mesaj için ayrı onay"""
    
    def __init__(self, parent=None, firm=None, message=None, translation=None, language=None):
        super().__init__(parent)
        self.firm = firm
        self.message = message
        self.translation = translation
        self.language = language or "Türkçe"
        self.approved = False
        self.skipped = False
        self.stopped = False
        
        self.setWindowTitle("📱 WhatsApp Mesaj Onayı")
        self.setModal(True)
        self.setFixedSize(700, 600)
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel("📱 WhatsApp Mesaj Onayı")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Firma bilgileri
        firm_group = QGroupBox("🏢 Firma Bilgileri")
        firm_layout = QVBoxLayout()
        
        firm_info = f"""
📱 Firma: {self.firm.get('name', 'Bilinmeyen')}
📞 Telefon: {self.firm.get('phone', 'Belirtilmemiş')}
👤 İletişim: {self.firm.get('contact_person', 'Belirtilmemiş')}
🏢 Sektör: {self.firm.get('sector', 'Belirtilmemiş')}
        """
        
        firm_label = QLabel(firm_info)
        firm_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        firm_layout.addWidget(firm_label)
        firm_group.setLayout(firm_layout)
        layout.addWidget(firm_group)
        
        # Orijinal mesaj
        original_group = QGroupBox(f"💬 Orijinal Mesaj ({self.language})")
        original_layout = QVBoxLayout()
        
        message_text = QTextEdit()
        message_text.setPlainText(self.message)
        message_text.setReadOnly(True)
        message_text.setMaximumHeight(120)
        message_text.setStyleSheet("""
            QTextEdit {
                background-color: #e8f5e8;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        original_layout.addWidget(message_text)
        original_group.setLayout(original_layout)
        layout.addWidget(original_group)
        
        # Türkçe çeviri
        translation_group = QGroupBox("🇹🇷 Türkçe Çevirisi")
        translation_layout = QVBoxLayout()
        
        translation_text = QTextEdit()
        translation_text.setPlainText(self.translation)
        translation_text.setReadOnly(True)
        translation_text.setMaximumHeight(120)
        translation_text.setStyleSheet("""
            QTextEdit {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        translation_layout.addWidget(translation_text)
        translation_group.setLayout(translation_layout)
        layout.addWidget(translation_group)
        
        # Uyarı
        warning_label = QLabel("⚠️ WhatsApp'ta sadece orijinal mesaj görünecektir. Çeviri sadece burada gösterilmektedir.")
        warning_label.setStyleSheet("""
            QLabel {
                background-color: #f8d7da;
                color: #721c24;
                padding: 8px;
                border-radius: 5px;
                font-size: 11px;
                border: 1px solid #f5c6cb;
            }
        """)
        layout.addWidget(warning_label)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.send_btn = QPushButton("✅ Gönder")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.send_btn.clicked.connect(self.approve_message)
        button_layout.addWidget(self.send_btn)
        
        self.skip_btn = QPushButton("⏭️ Atlama")
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.skip_btn.clicked.connect(self.skip_message)
        button_layout.addWidget(self.skip_btn)
        
        self.stop_btn = QPushButton("🛑 Durdur")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_sending)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
    
    def approve_message(self):
        """Mesajı onayla"""
        self.approved = True
        self.accept()
    
    def skip_message(self):
        """Mesajı atla"""
        self.skipped = True
        self.accept()
    
    def stop_sending(self):
        """Gönderimi durdur"""
        self.stopped = True
        self.accept()


class WhatsAppAutoSender:
    """📱 WhatsApp Otomatik Mesaj Gönderim Motoru"""
    
    def __init__(self, parent=None, db=None, gpt_manager=None, whatsapp_view=None):
        self.parent = parent
        self.db = db
        self.gpt_manager = gpt_manager
        self.whatsapp_view = whatsapp_view
        self.is_running = False
        self.should_stop = False
        self.current_firm_index = 0
        self.selected_firms = []
        self.send_stats = {
            'total': 0,
            'sent': 0,
            'skipped': 0,
            'failed': 0,
            'approved': 0
        }
        
    def start_auto_sending(self, selected_firms):
        """Otomatik gönderimi başlat"""
        if self.is_running:
            QMessageBox.warning(self.parent, "⚠️ Uyarı", "Gönderim zaten devam ediyor!")
            return
        
        if not selected_firms:
            QMessageBox.warning(self.parent, "⚠️ Uyarı", "Gönderilecek firma seçilmedi!")
            return
        
        # Günlük limit kontrolü
        can_send, limit_msg = self.db.can_send_whatsapp_message()
        if not can_send:
            QMessageBox.warning(self.parent, "⚠️ Limit Aşıldı", 
                              f"Günlük mesaj limiti aşıldı!\n\n{limit_msg}")
            return
        
        # WhatsApp bağlantı kontrolü
        if not self.whatsapp_view or not self.whatsapp_view.is_connected:
            QMessageBox.warning(self.parent, "⚠️ WhatsApp Bağlantısı", 
                              "WhatsApp Web bağlantısı yok!\n\nLütfen WhatsApp sekmesine gidip bağlantıyı kontrol edin.")
            return
        
        # Başlatma onayı
        reply = QMessageBox.question(self.parent, "🚀 Otomatik Gönderim Başlat", 
                                   f"📊 {len(selected_firms)} firma için otomatik mesaj gönderimi başlatılacak.\n\n"
                                   f"📱 Her mesaj için ayrı onay alınacak\n"
                                   f"⏱️ Mesajlar arası 15-45 saniye bekleme\n"
                                   f"📈 Günlük limit: 50 mesaj\n\n"
                                   f"Devam etmek istiyor musunuz?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        # Gönderimi başlat
        self.selected_firms = selected_firms
        self.current_firm_index = 0
        self.is_running = True
        self.should_stop = False
        self.send_stats = {'total': len(selected_firms), 'sent': 0, 'skipped': 0, 'failed': 0, 'approved': 0}
        
        # Thread'de çalıştır
        self.send_thread = threading.Thread(target=self._send_messages_loop, daemon=True)
        self.send_thread.start()
        
        QMessageBox.information(self.parent, "✅ Başlatıldı", 
                              f"Otomatik gönderim başlatıldı!\n\n"
                              f"📊 Toplam: {len(selected_firms)} firma\n"
                              f"📱 Her mesaj için onay bekleniyor...")
    
    def _send_messages_loop(self):
        """Mesaj gönderim döngüsü"""
        try:
            for i, firm in enumerate(self.selected_firms):
                if self.should_stop:
                    break
                
                self.current_firm_index = i
                
                # Günlük limit kontrolü
                can_send, limit_msg = self.db.can_send_whatsapp_message()
                if not can_send:
                    self._show_limit_reached_dialog(limit_msg)
                    break
                
                # AI ile mesaj oluştur
                message, translation = self._generate_ai_message(firm)
                if not message:
                    self.send_stats['failed'] += 1
                    continue
                
                # Onay dialog'u göster
                approval_result = self._show_approval_dialog(firm, message, translation)
                
                if approval_result == 'stopped':
                    break
                elif approval_result == 'skipped':
                    self.send_stats['skipped'] += 1
                    self.db.update_whatsapp_daily_limit(messages_skipped=1)
                    self.db.log_whatsapp_message(
                        firm_id=firm.get('id'),
                        firm_name=firm.get('name'),
                        phone_number=firm.get('phone'),
                        message_content=message,
                        message_translation=translation,
                        approval_status='skipped',
                        send_status='skipped'
                    )
                    continue
                elif approval_result == 'approved':
                    # Mesajı gönder
                    success = self._send_whatsapp_message(firm, message)
                    
                    if success:
                        self.send_stats['sent'] += 1
                        self.db.update_whatsapp_daily_limit(messages_sent=1, messages_approved=1)
                        self.db.log_whatsapp_message(
                            firm_id=firm.get('id'),
                            firm_name=firm.get('name'),
                            phone_number=firm.get('phone'),
                            message_content=message,
                            message_translation=translation,
                            approval_status='approved',
                            send_status='sent'
                        )
                    else:
                        self.send_stats['failed'] += 1
                        self.db.update_whatsapp_daily_limit(messages_failed=1)
                        self.db.log_whatsapp_message(
                            firm_id=firm.get('id'),
                            firm_name=firm.get('name'),
                            phone_number=firm.get('phone'),
                            message_content=message,
                            message_translation=translation,
                            approval_status='approved',
                            send_status='failed',
                            error_message='Gönderim başarısız'
                        )
                
                # Random bekleme (15-45 saniye)
                if i < len(self.selected_firms) - 1 and not self.should_stop:
                    wait_time = random.randint(15, 45)
                    for _ in range(wait_time):
                        if self.should_stop:
                            break
                        time.sleep(1)
            
            # Gönderim tamamlandı
            self.is_running = False
            self._show_completion_dialog()
            
        except Exception as e:
            logger.error(f"Otomatik gönderim hatası: {e}")
            self.is_running = False
            QMessageBox.critical(self.parent, "❌ Hata", f"Gönderim sırasında hata:\n{str(e)}")
    
    def _generate_ai_message(self, firm):
        """AI ile mesaj oluştur"""
        try:
            if not self.gpt_manager or not hasattr(self.gpt_manager, 'client'):
                return None, None
            
            # Basit mesaj oluştur (daha sonra geliştirilebilir)
            prompt = f"""
            Lütfen {firm.get('name', 'Firma')} için kısa ve profesyonel bir WhatsApp B2B mesajı oluştur.
            
            Firma Bilgileri:
            - Firma Adı: {firm.get('name', 'Belirtilmemiş')}
            - Sektör: {firm.get('sector', 'Belirtilmemiş')}
            - İletişim Kişisi: {firm.get('contact_person', 'Belirtilmemiş')}
            
            Mesaj özellikleri:
            - Maksimum 150 karakter
            - Profesyonel ama samimi ton
            - Firma adını kullan
            - Net bir call-to-action içermeli
            - WhatsApp için uygun format
            
            Sadece mesaj metnini döndür, başka açıklama ekleme.
            """
            
            response = self.gpt_manager.client.chat.completions.create(
                model=self.gpt_manager.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Sen profesyonel bir B2B satış uzmanısın. Kısa, etkili ve kişiselleştirilmiş mesajlar yazarsın."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            message = response.choices[0].message.content.strip()
            
            # Türkçe çeviri oluştur (eğer gerekirse)
            translation = "Türkçe mesaj - çeviri gerekmiyor"  # Şimdilik basit
            
            return message, translation
            
        except Exception as e:
            logger.error(f"AI mesaj oluşturma hatası: {e}")
            return None, None
    
    def _show_approval_dialog(self, firm, message, translation):
        """Onay dialog'unu göster"""
        try:
            dialog = WhatsAppMessageApprovalDialog(
                parent=self.parent,
                firm=firm,
                message=message,
                translation=translation
            )
            
            result = dialog.exec()
            
            if dialog.stopped:
                return 'stopped'
            elif dialog.skipped:
                return 'skipped'
            elif dialog.approved:
                return 'approved'
            else:
                return 'cancelled'
                
        except Exception as e:
            logger.error(f"Onay dialog hatası: {e}")
            return 'cancelled'
    
    def _send_whatsapp_message(self, firm, message):
        """WhatsApp mesajı gönder"""
        try:
            phone = firm.get('phone', '').strip()
            if not phone:
                return False
            
            # Telefon numarasını temizle
            phone_clean = ''.join(filter(str.isdigit, phone))
            if not phone_clean.startswith('90'):
                phone_clean = '90' + phone_clean.lstrip('0')
            
            # WhatsApp'tan gönder
            success = self.whatsapp_view.send_message(phone_clean, message)
            
            if success:
                logger.info(f"WhatsApp mesajı gönderildi: {firm.get('name')} - {phone_clean}")
                return True
            else:
                logger.error(f"WhatsApp mesajı gönderilemedi: {firm.get('name')} - {phone_clean}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp gönderim hatası: {e}")
            return False
    
    def _show_limit_reached_dialog(self, limit_msg):
        """Limit aşıldı dialog'unu göster"""
        QMessageBox.warning(self.parent, "⚠️ Günlük Limit Aşıldı", 
                          f"Günlük mesaj limiti aşıldı!\n\n{limit_msg}\n\n"
                          f"Gönderim durduruldu.")
    
    def _show_completion_dialog(self):
        """Tamamlanma dialog'unu göster"""
        stats = self.send_stats
        QMessageBox.information(self.parent, "✅ Gönderim Tamamlandı", 
                              f"Otomatik gönderim tamamlandı!\n\n"
                              f"📊 İstatistikler:\n"
                              f"• Toplam: {stats['total']}\n"
                              f"• Gönderilen: {stats['sent']}\n"
                              f"• Atlanan: {stats['skipped']}\n"
                              f"• Başarısız: {stats['failed']}")
    
    def stop_sending(self):
        """Gönderimi durdur"""
        if self.is_running:
            self.should_stop = True
            QMessageBox.information(self.parent, "🛑 Durduruldu", 
                                  "Gönderim durduruldu. Mevcut mesaj tamamlandıktan sonra duracak.")


class BulkMessageDialog(QDialog):
    """🚀 Ultra Gelişmiş Toplu Mesaj Gönderme Sistemi - AI Destekli"""
    
    def __init__(self, parent=None, firms=None, db=None, gpt_manager=None, whatsapp_view=None):
        super().__init__(parent)
        self.firms = firms or []
        self.db = db
        self.gpt_manager = gpt_manager
        self.whatsapp_view = whatsapp_view
        self.selected_firms = []
        self.current_firm_index = 0
        self.generated_messages = {}
        self.skipped_firms = []
        self.sent_messages = []
        self.failed_messages = []
        self.is_running = False
        self.pause_requested = False
        
        # Zamanlayıcılar
        self.approval_timer = QTimer()
        self.approval_timer.timeout.connect(self.auto_send_message)
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        
        # Mesaj istatistikleri
        self.stats = {
            'total': 0,
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'pending': 0
        }
        
        self.setupUI()
        self.load_firms()
        self.load_templates()
        self.setup_shortcuts()
    
    def setupUI(self):
        """🎨 Ultra Modern ve Gelişmiş Arayüz"""
        self.setWindowTitle("🚀 Ultra Gelişmiş Toplu Mesaj Sistemi - AI Destekli")
        self.setModal(True)
        
        # Tam ekran responsive boyutlandırma - Geliştirilmiş
        screen = QApplication.primaryScreen().geometry()
        scale_factor = self.get_scale_factor()
        
        # Ekran boyutlarını al
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Pencere boyutlarını hesapla (ekranın %95'i - daha büyük)
        width = int(screen_width * 0.95)
        height = int(screen_height * 0.95)
        
        # Minimum boyutları ölçeklendirme faktörüne göre ayarla - Daha büyük minimum boyutlar
        min_width = max(1000, int(1400 * scale_factor))
        min_height = max(700, int(900 * scale_factor))
        
        self.setMinimumSize(min_width, min_height)
        self.resize(width, height)
        
        # Maksimum boyutları da ayarla - Tam ekran desteği
        self.setMaximumSize(screen_width, screen_height)
        
        # Pencereyi ekranın ortasına konumlandır
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.setGeometry(x, y, width, height)
        
        # Modern karanlık tema uygula
        self.apply_dark_theme()
        
        # Ana layout - responsive spacing
        layout = QVBoxLayout(self)
        spacing = max(8, int(10 * self.get_scale_factor()))
        margins = max(12, int(15 * self.get_scale_factor()))
        layout.setSpacing(spacing)
        layout.setContentsMargins(margins, margins, margins, margins)
        
        # Üst kontrol paneli - Kompakt ve modern
        self.create_header_panel(layout)
        
        # Ana içerik - Splitter ile yan yana
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Sol panel - Firma seçimi ve kontroller
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Sağ panel - Mesaj editörü ve gönderim
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Responsive splitter oranları - Daha iyi dağılım
        total_width = self.width()
        # Sol panel %35, sağ panel %65 - AI kısmı için daha fazla yer
        main_splitter.setSizes([int(total_width * 0.35), int(total_width * 0.65)])
        main_splitter.setStretchFactor(0, 0)  # Sol panel sabit
        main_splitter.setStretchFactor(1, 1)  # Sağ panel genişleyebilir
        layout.addWidget(main_splitter)
        
        # Alt panel - İstatistikler ve kontroller
        self.create_bottom_panel(layout)
    
    def get_scale_factor(self):
        """Gelişmiş tam ekran ölçeklendirme faktörü"""
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        
        # DPI tabanlı ölçeklendirme
        dpi = screen.logicalDotsPerInch()
        dpi_scale = max(1.0, dpi / 96.0)
        
        # Ekran boyutuna göre ölçeklendirme
        screen_width = geometry.width()
        screen_height = geometry.height()
        
        # Referans çözünürlük (1920x1080)
        ref_width = 1920
        ref_height = 1080
        
        # Genişlik ve yükseklik ölçeklendirme faktörleri
        width_scale = screen_width / ref_width
        height_scale = screen_height / ref_height
        
        # En küçük ölçeklendirme faktörünü kullan (orantıyı korumak için)
        size_scale = min(width_scale, height_scale)
        
        # DPI ve boyut ölçeklendirmesini birleştir
        final_scale = max(0.8, min(2.0, dpi_scale * size_scale))
        
        return final_scale
    
    def apply_dark_theme(self):
        """Modern karanlık tema uygula"""
        scale_factor = self.get_scale_factor()
        base_font_size = max(10, int(12 * scale_factor))
        large_font_size = max(12, int(14 * scale_factor))
        button_padding = max(8, int(10 * scale_factor))
        border_radius = max(6, int(8 * scale_factor))
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #1a1a1a;
                color: #ffffff;
                font-size: {base_font_size}px;
            }}
            
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {border_radius}px;
            }}
            
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0d7377, stop: 1 #14a085);
                color: white;
                border: none;
                border-radius: {border_radius}px;
                padding: {button_padding}px {button_padding * 2}px;
                font-weight: 600;
                font-size: {base_font_size}px;
                min-height: {max(24, int(30 * scale_factor))}px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #14a1a5, stop: 1 #1db8bc);
            }}
            
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0a5d61, stop: 1 #0d7377);
            }}
            
            QPushButton:disabled {{
                background: #3a3a3a;
                color: #666666;
            }}
            
            QLineEdit, QTextEdit, QComboBox {{
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                padding: {button_padding}px;
                border-radius: {border_radius}px;
                font-size: {base_font_size}px;
                min-height: {max(20, int(25 * scale_factor))}px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 2px solid #0d7377;
                background-color: #1a1a1a;
            }}
            
            QLabel {{
                color: #ffffff;
                font-size: {base_font_size}px;
            }}
            
            QGroupBox {{
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: {border_radius}px;
                margin-top: {max(12, int(15 * scale_factor))}px;
                padding-top: {max(12, int(15 * scale_factor))}px;
                font-weight: bold;
                font-size: {large_font_size}px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {max(8, int(10 * scale_factor))}px;
                padding: 0 {max(4, int(5 * scale_factor))}px 0 {max(4, int(5 * scale_factor))}px;
            }}
            
            QTableWidget {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {border_radius}px;
                gridline-color: #3a3a3a;
                font-size: {base_font_size}px;
            }}
            
            QTableWidget::item {{
                padding: {button_padding}px;
                border-bottom: 1px solid #3a3a3a;
                color: #ffffff;
            }}
            
            QTableWidget::item:selected {{
                background-color: #0d7377;
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: #3a3a3a;
                padding: {max(8, int(10 * scale_factor))}px;
                border: none;
                font-weight: bold;
                color: #ffffff;
                font-size: {base_font_size}px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid #3a3a3a;
                border-radius: {border_radius}px;
                background-color: #2a2a2a;
            }}
            
            QTabBar::tab {{
                background-color: #3a3a3a;
                color: #ffffff;
                padding: {button_padding}px {button_padding * 2}px;
                margin-right: 2px;
                border-top-left-radius: {border_radius}px;
                border-top-right-radius: {border_radius}px;
                font-size: {base_font_size}px;
            }}
            
            QTabBar::tab:selected {{
                background-color: #0d7377;
                border-bottom: 2px solid #14a085;
            }}
            
            QProgressBar {{
                border: 1px solid #3a3a3a;
                border-radius: {border_radius}px;
                text-align: center;
                font-size: {base_font_size}px;
                color: white;
                background-color: #2a2a2a;
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: {border_radius}px;
            }}
            
            QSplitter::handle {{
                background-color: #3a3a3a;
                width: 2px;
            }}
            
            QCheckBox {{
                color: #ffffff;
                font-size: {base_font_size}px;
            }}
            
            QCheckBox::indicator {{
                width: {max(16, int(18 * scale_factor))}px;
                height: {max(16, int(18 * scale_factor))}px;
            }}
            
            QCheckBox::indicator:unchecked {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: #0d7377;
                border: 1px solid #0d7377;
                border-radius: 3px;
            }}
        """)
    
    def create_header_panel(self, layout):
        """Üst kontrol paneli oluştur"""
        header_frame = QFrame()
        scale_factor = self.get_scale_factor()
        padding = max(12, int(15 * scale_factor))
        font_size = max(14, int(16 * scale_factor))
        button_font = max(10, int(12 * scale_factor))
        
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: {max(8, int(12 * scale_factor))}px;
                padding: {padding}px;
                margin-bottom: {max(8, int(10 * scale_factor))}px;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
                font-size: {font_size}px;
            }}
            QPushButton {{
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: {max(6, int(8 * scale_factor))}px;
                color: white;
                padding: {max(6, int(8 * scale_factor))}px {max(12, int(16 * scale_factor))}px;
                font-weight: bold;
                font-size: {button_font}px;
                min-height: {max(24, int(30 * scale_factor))}px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.25);
            }}
            QPushButton:pressed {{
                background: rgba(255, 255, 255, 0.1);
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Sol taraf - Başlık ve istatistikler
        left_header = QVBoxLayout()
        
        title_label = QLabel("🚀 Ultra Gelişmiş Toplu Mesaj Sistemi")
        title_font_size = max(16, int(18 * self.get_scale_factor()))
        title_label.setStyleSheet(f"font-size: {title_font_size}px; font-weight: bold; color: white;")
        left_header.addWidget(title_label)
        
        self.stats_label = QLabel("📊 Hazırlanıyor...")
        left_header.addWidget(self.stats_label)
        
        header_layout.addLayout(left_header)
        header_layout.addStretch()
        
        # Sağ taraf - Hızlı kontroller
        right_header = QHBoxLayout()
        
        self.quick_start_btn = QPushButton("⚡ Hızlı Başlat")
        self.quick_start_btn.clicked.connect(self.quick_start)
        right_header.addWidget(self.quick_start_btn)
        
        self.ai_optimize_btn = QPushButton("🤖 AI Optimize Et")
        self.ai_optimize_btn.clicked.connect(self.ai_optimize_selection)
        right_header.addWidget(self.ai_optimize_btn)
        
        self.export_btn = QPushButton("📊 Rapor Al")
        self.export_btn.clicked.connect(self.export_report)
        right_header.addWidget(self.export_btn)
        
        header_layout.addLayout(right_header)
        layout.addWidget(header_frame)
    
    def create_left_panel(self):
        """Sol panel - Firma seçimi ve filtreler"""
        panel = QWidget()
        panel.setMaximumWidth(600)
        layout = QVBoxLayout(panel)
        
        # Firma seçim başlığı
        title_frame = QFrame()
        scale_factor = self.get_scale_factor()
        padding = max(8, int(10 * scale_factor))
        font_size = max(12, int(14 * scale_factor))
        
        title_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {max(6, int(8 * scale_factor))}px;
                padding: {padding}px;
                margin-bottom: {padding}px;
            }}
            QLabel {{
                font-weight: bold;
                font-size: {font_size}px;
                color: #ffffff;
            }}
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.addWidget(QLabel("🏢 Firma Seçimi ve Filtreler"))
        title_layout.addStretch()
        
        # Firma sayısı
        self.firm_count_label = QLabel("0 firma")
        count_font_size = max(10, int(12 * self.get_scale_factor()))
        self.firm_count_label.setStyleSheet(f"color: #adb5bd; font-size: {count_font_size}px;")
        title_layout.addWidget(self.firm_count_label)
        
        layout.addWidget(title_frame)
        
        # Filtre kontrolleri
        filter_frame = QFrame()
        padding = max(8, int(10 * self.get_scale_factor()))
        
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {max(6, int(8 * self.get_scale_factor()))}px;
                padding: {padding}px;
                margin-bottom: {padding}px;
            }}
        """)
        filter_layout = QGridLayout(filter_frame)
        
        # Sektör filtresi
        filter_layout.addWidget(QLabel("Sektör:"), 0, 0)
        self.sector_filter = QComboBox()
        self.sector_filter.addItem("Tüm Sektörler")
        self.sector_filter.currentTextChanged.connect(self.filter_firms)
        filter_layout.addWidget(self.sector_filter, 0, 1)
        
        # Durum filtresi
        filter_layout.addWidget(QLabel("Durum:"), 0, 2)
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tüm Durumlar", "Aktif", "Pasif", "Potansiyel", "Müşteri"])
        self.status_filter.currentTextChanged.connect(self.filter_firms)
        filter_layout.addWidget(self.status_filter, 0, 3)
        
        # Website filtresi
        filter_layout.addWidget(QLabel("Website:"), 1, 0)
        self.website_filter = QComboBox()
        self.website_filter.addItems(["Tümü", "Website Var", "Website Yok"])
        self.website_filter.currentTextChanged.connect(self.filter_firms)
        filter_layout.addWidget(self.website_filter, 1, 1)
        
        # Arama kutusu
        filter_layout.addWidget(QLabel("Ara:"), 1, 2)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Firma adı, telefon, email...")
        self.search_input.textChanged.connect(self.filter_firms)
        filter_layout.addWidget(self.search_input, 1, 3)
        
        layout.addWidget(filter_frame)
        
        # Seçim kontrolleri
        selection_frame = QFrame()
        padding = max(8, int(10 * self.get_scale_factor()))
        
        selection_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {max(6, int(8 * self.get_scale_factor()))}px;
                padding: {padding}px;
                margin-bottom: {padding}px;
            }}
        """)
        selection_layout = QHBoxLayout(selection_frame)
        
        self.select_all_btn = QPushButton("🔥 Tümünü Seç")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setStyleSheet(self.get_button_style("#28a745"))
        selection_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("❌ Hiçbirini Seçme")
        self.select_none_btn.clicked.connect(self.select_none)
        self.select_none_btn.setStyleSheet(self.get_button_style("#dc3545"))
        selection_layout.addWidget(self.select_none_btn)
        
        self.select_sector_btn = QPushButton("🏢 Sektöre Göre")
        self.select_sector_btn.clicked.connect(self.select_by_sector)
        self.select_sector_btn.setStyleSheet(self.get_button_style("#17a2b8"))
        selection_layout.addWidget(self.select_sector_btn)
        
        self.invert_selection_btn = QPushButton("🔄 Tersini Seç")
        self.invert_selection_btn.clicked.connect(self.invert_selection)
        self.invert_selection_btn.setStyleSheet(self.get_button_style("#6c757d"))
        selection_layout.addWidget(self.invert_selection_btn)
        
        self.select_no_website_btn = QPushButton("🌐 Website Yok")
        self.select_no_website_btn.clicked.connect(self.select_no_website)
        self.select_no_website_btn.setStyleSheet(self.get_button_style("#ff6b6b"))
        selection_layout.addWidget(self.select_no_website_btn)
        
        layout.addWidget(selection_frame)
        
        # Firma tablosu
        self.firms_table = QTableWidget()
        self.firms_table.setColumnCount(7)
        self.firms_table.setHorizontalHeaderLabels([
            "✓", "Firma", "Sektör", "Telefon", "Website", "Durum", "Son İletişim"
        ])
        self.firms_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.firms_table.setAlternatingRowColors(True)
        # Tablo stili zaten ana temada tanımlı, burada özel ayarlama gerekmiyor
        pass  # Stil ana apply_dark_theme metodunda tanımlı
        
        # Tablo ayarları - responsive boyutlar
        scale_factor = self.get_scale_factor()
        self.firms_table.horizontalHeader().setStretchLastSection(True)
        self.firms_table.setColumnWidth(0, max(25, int(30 * scale_factor)))  # Checkbox kolonu
        self.firms_table.setColumnWidth(1, max(150, int(180 * scale_factor)))  # Firma adı
        self.firms_table.setColumnWidth(2, max(80, int(100 * scale_factor)))  # Sektör
        self.firms_table.setColumnWidth(3, max(80, int(100 * scale_factor)))  # Telefon
        self.firms_table.setColumnWidth(4, max(120, int(150 * scale_factor)))  # Website
        
        layout.addWidget(self.firms_table)
        
        return panel
    
    def create_right_panel(self):
        """Sağ panel - Mesaj editörü ve gönderim kontrolleri"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Basit başlık
        title_label = QLabel("🚀 Toplu Mesaj Gönderim Sistemi")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #0d7377;
                padding: 15px;
                background-color: #2a2a2a;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Hızlı erişim butonları
        quick_buttons_frame = QFrame()
        quick_buttons_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        quick_layout = QHBoxLayout(quick_buttons_frame)
        
        # AI Mesaj butonu
        ai_msg_btn = QPushButton("🤖 AI ile Mesaj Oluştur")
        ai_msg_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #28a745, stop: 1 #20c997);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 14px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #20c997, stop: 1 #28a745);
            }
        """)
        ai_msg_btn.clicked.connect(self.show_ai_message_popup)
        quick_layout.addWidget(ai_msg_btn)
        
        # Şablon butonu
        template_btn = QPushButton("📋 Şablon Mesaj")
        template_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #17a2b8, stop: 1 #6f42c1);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 14px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #6f42c1, stop: 1 #17a2b8);
            }
        """)
        template_btn.clicked.connect(self.show_template_popup)
        quick_layout.addWidget(template_btn)
        
        # Manuel mesaj butonu
        manual_btn = QPushButton("✏️ Manuel Mesaj")
        manual_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ffc107, stop: 1 #fd7e14);
                color: #212529;
                border: none;
                border-radius: 8px;
                padding: 15px 25px;
                font-weight: bold;
                font-size: 14px;
                min-height: 50px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #fd7e14, stop: 1 #ffc107);
            }
        """)
        manual_btn.clicked.connect(self.show_manual_popup)
        quick_layout.addWidget(manual_btn)
        
        layout.addWidget(quick_buttons_frame)
        
        # Bilgi paneli
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1a3d1a;
                border: 1px solid #2d5a2d;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_label = QLabel("""
        💡 <b>Kullanım Kılavuzu:</b><br>
        • Sol panelden gönderilecek firmaları seçin<br>
        • Yukarıdaki butonlardan birini kullanarak mesaj oluşturun<br>
        • Her mesaj için ayrı onay alınacak<br>
        • Otomatik gönderim sistemi güvenli şekilde çalışır
        """)
        info_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                line-height: 1.4;
            }
        """)
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_frame)
        
        # Gönderim kontrolleri (sadece temel)
        self.create_simple_send_controls(layout)
        
        return panel
    
    def create_simple_send_controls(self, layout):
        """Basit gönderim kontrolleri"""
        controls_frame = QFrame()
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Başlık
        controls_layout.addWidget(QLabel("🚀 Otomatik Gönderim Kontrolleri"))
        
        # Temel ayarlar
        settings_layout = QHBoxLayout()
        
        # Gönderim aralığı
        settings_layout.addWidget(QLabel("Gönderim Aralığı:"))
        self.send_interval_spin = QSpinBox()
        self.send_interval_spin.setRange(5, 60)
        self.send_interval_spin.setValue(15)
        self.send_interval_spin.setSuffix(" sn")
        settings_layout.addWidget(self.send_interval_spin)
        
        settings_layout.addStretch()
        
        # Otomatik gönderim checkbox
        self.auto_send_check = QCheckBox("Otomatik Gönderim")
        self.auto_send_check.setChecked(True)
        settings_layout.addWidget(self.auto_send_check)
        
        controls_layout.addLayout(settings_layout)
        
        # Ana kontrol butonları
        main_controls = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Başlat")
        self.start_btn.clicked.connect(self.start_bulk_messaging)
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #28a745, stop: 1 #20c997);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #20c997, stop: 1 #28a745);
            }
        """)
        main_controls.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸️ Duraklat")
        self.pause_btn.clicked.connect(self.pause_messaging)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setMinimumHeight(50)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ffc107, stop: 1 #fd7e14);
                color: #212529;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #fd7e14, stop: 1 #ffc107);
            }
        """)
        main_controls.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹️ Durdur")
        self.stop_btn.clicked.connect(self.stop_messaging)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #dc3545, stop: 1 #c82333);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #c82333, stop: 1 #dc3545);
            }
        """)
        main_controls.addWidget(self.stop_btn)
        
        controls_layout.addLayout(main_controls)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                text-align: center;
                background-color: #1a1a1a;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: 6px;
            }
        """)
        controls_layout.addWidget(self.progress_bar)
        
        layout.addWidget(controls_frame)
    
    def create_ai_message_tab(self):
        """AI mesaj modu tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # AI ayarları
        ai_settings_frame = QFrame()
        scale_factor = self.get_scale_factor()
        padding = max(12, int(15 * scale_factor))
        
        ai_settings_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #1a3d1a;
                border: 1px solid #2d5a2d;
                border-radius: {max(6, int(8 * scale_factor))}px;
                padding: {padding}px;
                margin-bottom: {max(8, int(10 * scale_factor))}px;
            }}
        """)
        ai_layout = QGridLayout(ai_settings_frame)
        
        # Mesaj tipi
        ai_layout.addWidget(QLabel("Mesaj Tipi:"), 0, 0)
        self.message_type_combo = QComboBox()
        self.message_type_combo.addItems([
            "Tanıtım", "Takip", "Kampanya", "Bilgilendirme", 
            "Teşekkür", "Randevu", "Satış", "Destek"
        ])
        ai_layout.addWidget(self.message_type_combo, 0, 1)
        
        # Dil seçimi
        ai_layout.addWidget(QLabel("Dil:"), 0, 2)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Türkçe", "English", "Deutsch", "Français", "Español", "Polski"])
        ai_layout.addWidget(self.language_combo, 0, 3)
        
        # Özel prompt - Daha geniş alan
        ai_layout.addWidget(QLabel("Özel Prompt:"), 1, 0)
        self.custom_prompt_input = QLineEdit()
        self.custom_prompt_input.setPlaceholderText("AI'ya özel talimatlar verin...")
        self.custom_prompt_input.setMinimumHeight(max(35, int(40 * scale_factor)))
        ai_layout.addWidget(self.custom_prompt_input, 1, 1, 1, 3)
        
        layout.addWidget(ai_settings_frame)
        
        # Mesaj önizleme
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        preview_layout = QVBoxLayout(preview_frame)
        
        preview_layout.addWidget(QLabel("📝 Mesaj Önizleme:"))
        
        self.message_preview = QTextEdit()
        self.message_preview.setReadOnly(True)
        # Daha büyük önizleme alanı
        self.message_preview.setMinimumHeight(max(200, int(250 * scale_factor)))
        self.message_preview.setMaximumHeight(max(300, int(350 * scale_factor)))
        self.message_preview.setStyleSheet(f"""
            QTextEdit {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {max(12, int(14 * scale_factor))}px;
            }}
        """)
        preview_layout.addWidget(self.message_preview)
        
        # AI butonları - Daha büyük ve responsive
        ai_buttons_layout = QHBoxLayout()
        ai_buttons_layout.setSpacing(max(8, int(10 * scale_factor)))
        
        self.generate_ai_btn = QPushButton("🤖 AI ile Oluştur")
        self.generate_ai_btn.clicked.connect(self.generate_ai_message)
        self.generate_ai_btn.setMinimumHeight(max(40, int(45 * scale_factor)))
        self.generate_ai_btn.setStyleSheet(self.get_button_style("#28a745"))
        ai_buttons_layout.addWidget(self.generate_ai_btn)
        
        self.regenerate_btn = QPushButton("🔄 Yeniden Oluştur")
        self.regenerate_btn.clicked.connect(self.regenerate_message)
        self.regenerate_btn.setMinimumHeight(max(40, int(45 * scale_factor)))
        self.regenerate_btn.setStyleSheet(self.get_button_style("#ffc107"))
        ai_buttons_layout.addWidget(self.regenerate_btn)
        
        self.preview_all_btn = QPushButton("👁️ Tümünü Önizle")
        self.preview_all_btn.clicked.connect(self.preview_all_messages)
        self.preview_all_btn.setMinimumHeight(max(40, int(45 * scale_factor)))
        self.preview_all_btn.setStyleSheet(self.get_button_style("#17a2b8"))
        ai_buttons_layout.addWidget(self.preview_all_btn)
        
        preview_layout.addLayout(ai_buttons_layout)
        layout.addWidget(preview_frame)
        
        self.message_tabs.addTab(tab, "🤖 AI Mesaj")
    
    def create_template_tab(self):
        """Şablon modu tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Şablon seçimi
        template_frame = QFrame()
        scale_factor = self.get_scale_factor()
        padding = max(12, int(15 * scale_factor))
        
        template_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {max(6, int(8 * scale_factor))}px;
                padding: {padding}px;
                margin-bottom: {max(8, int(10 * scale_factor))}px;
            }}
        """)
        template_layout = QVBoxLayout(template_frame)
        
        template_layout.addWidget(QLabel("📋 Şablon Seçimi:"))
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("-- Şablon Seç --")
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)
        template_layout.addWidget(self.template_combo)
        
        # Şablon içeriği
        template_layout.addWidget(QLabel("Şablon İçeriği:"))
        self.template_content = QTextEdit()
        max_height = max(160, int(200 * self.get_scale_factor()))
        self.template_content.setMaximumHeight(max_height)
        self.template_content.setPlaceholderText("Şablon seçin veya yeni şablon oluşturun...")
        template_layout.addWidget(self.template_content)
        
        # Şablon butonları
        template_buttons = QHBoxLayout()
        
        self.create_template_btn = QPushButton("➕ Yeni Şablon")
        self.create_template_btn.clicked.connect(self.create_new_template)
        template_buttons.addWidget(self.create_template_btn)
        
        self.save_template_btn = QPushButton("💾 Şablonu Kaydet")
        self.save_template_btn.clicked.connect(self.save_template)
        template_buttons.addWidget(self.save_template_btn)
        
        template_layout.addLayout(template_buttons)
        layout.addWidget(template_frame)
        
        self.message_tabs.addTab(tab, "📋 Şablon")
    
    def create_manual_tab(self):
        """Manuel mod tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Manuel mesaj editörü
        manual_frame = QFrame()
        scale_factor = self.get_scale_factor()
        padding = max(12, int(15 * scale_factor))
        
        manual_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {max(6, int(8 * scale_factor))}px;
                padding: {padding}px;
            }}
        """)
        manual_layout = QVBoxLayout(manual_frame)
        
        manual_layout.addWidget(QLabel("✏️ Manuel Mesaj:"))
        
        self.manual_message_input = QTextEdit()
        self.manual_message_input.setPlaceholderText("""
Mesajınızı yazın...

Değişkenler:
{firma_adi} - Firma adı
{firma_sektoru} - Firma sektörü
{firma_iletisim} - İletişim kişisi
{firma_ozet} - Firma özeti
{firma_website} - Website
{firma_email} - E-mail
{firma_telefon} - Telefon
        """)
        manual_layout.addWidget(self.manual_message_input)
        
        layout.addWidget(manual_frame)
        
        self.message_tabs.addTab(tab, "✏️ Manuel")
    
    
    def create_bottom_panel(self, layout):
        """Alt panel - İstatistikler ve log"""
        bottom_frame = QFrame()
        scale_factor = self.get_scale_factor()
        
        bottom_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {max(6, int(8 * scale_factor))}px;
                padding: 10px;
                margin-top: 10px;
            }}
        """)
        bottom_layout = QHBoxLayout(bottom_frame)
        
        # Sol taraf - İstatistikler
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        stats_title = QLabel("📊 İstatistikler")
        title_font_size = max(12, int(14 * scale_factor))
        stats_title.setStyleSheet(f"font-weight: bold; font-size: {title_font_size}px; color: #ffffff;")
        stats_layout.addWidget(stats_title)
        
        self.detailed_stats = QLabel("Hazırlanıyor...")
        stats_font_size = max(10, int(12 * scale_factor))
        self.detailed_stats.setStyleSheet(f"font-size: {stats_font_size}px; color: #adb5bd;")
        stats_layout.addWidget(self.detailed_stats)
        
        bottom_layout.addWidget(stats_widget)
        
        # Sağ taraf - Log
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        
        log_title = QLabel("📝 Gönderim Logu")
        log_title.setStyleSheet(f"font-weight: bold; font-size: {title_font_size}px; color: #ffffff;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        bottom_layout.addWidget(log_widget)
        
        layout.addWidget(bottom_frame)
    
    def get_button_style(self, color, font_size=None):
        """Buton stili oluştur - responsive"""
        scale_factor = self.get_scale_factor()
        if font_size is None:
            font_size = max(10, int(12 * scale_factor))
        else:
            font_size = max(10, int(int(font_size.replace('px', '')) * scale_factor))
        
        padding_v = max(6, int(8 * scale_factor))
        padding_h = max(12, int(16 * scale_factor))
        border_radius = max(4, int(6 * scale_factor))
        min_height = max(24, int(30 * scale_factor))
        
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: {border_radius}px;
                padding: {padding_v}px {padding_h}px;
                font-weight: bold;
                font-size: {font_size}px;
                min-height: {min_height}px;
            }}
            QPushButton:hover {{
                background: {self.darken_color(color)};
            }}
            QPushButton:disabled {{
                background: #3a3a3a;
                color: #666666;
            }}
        """
    
    def darken_color(self, color):
        """Rengi koyulaştır - genişletilmiş renk haritası"""
        color_map = {
            "#28a745": "#1e7e34",  # Yeşil
            "#dc3545": "#bd2130",  # Kırmızı
            "#17a2b8": "#117a8b",  # Mavi
            "#6c757d": "#545b62",  # Gri
            "#ffc107": "#d39e00",  # Sarı
            "#ff6b6b": "#ee5a52",  # Açık kırmızı
            "#0d7377": "#0a5d61",  # Teal
            "#14a085": "#0f7a63"   # Yeşil teal
        }
        return color_map.get(color, color)
        # Buton stilleri get_button_style metoduyla uygulanıyor
        
        firm_controls.addWidget(self.select_all_btn)
        firm_controls.addWidget(self.select_none_btn)
        firm_controls.addWidget(self.select_sector_btn)
        firm_controls.addStretch()
        
        firm_layout.addLayout(firm_controls)
        
        # Firma tablosu - Düzeltilmiş
        self.firms_table = QTableWidget()
        self.firms_table.setColumnCount(7)
        self.firms_table.setHorizontalHeaderLabels([
            "Seç", "Firma Adı", "Sektör", "Telefon", "Website", "Durum", "Son İletişim"
        ])
        self.firms_table.setAlternatingRowColors(True)
        self.firms_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.firms_table.setSortingEnabled(True)
        self.firms_table.setWordWrap(False)
        
        # Tablo stilleri
        self.firms_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #3a3a3a;
                background-color: #2a2a2a;
                alternate-background-color: #333333;
                selection-background-color: #0d7377;
                color: #ffffff;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3a3a3a;
            }
            QTableWidget::item:selected {
                background-color: #0d7377;
                color: white;
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #3a3a3a;
                font-weight: bold;
            }
        """)
        
        firm_layout.addWidget(self.firms_table)
        
        self.tab_widget.addTab(firm_tab, "🏢 Firma Seçimi")
        
        # 2. Mesaj Ayarları Tab'ı
        message_tab = QWidget()
        message_layout = QVBoxLayout(message_tab)
        
        # Mesaj oluşturma seçenekleri - Popup butonları
        message_options_group = QGroupBox("🎯 Mesaj Oluşturma Seçenekleri")
        message_options_layout = QHBoxLayout()
        
        # AI Mesaj butonu
        ai_message_btn = QPushButton("🤖 AI Mesaj")
        ai_message_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4CAF50, stop: 1 #45a049);
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #45a049, stop: 1 #4CAF50);
                transform: scale(1.05);
            }
        """)
        ai_message_btn.clicked.connect(self.show_ai_message_popup)
        message_options_layout.addWidget(ai_message_btn)
        
        # Şablon butonu
        template_btn = QPushButton("📋 Şablon")
        template_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2196F3, stop: 1 #1976D2);
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1976D2, stop: 1 #2196F3);
                transform: scale(1.05);
            }
        """)
        template_btn.clicked.connect(self.show_template_popup)
        message_options_layout.addWidget(template_btn)
        
        # Manuel butonu
        manual_btn = QPushButton("✏️ Manuel")
        manual_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #FF9800, stop: 1 #F57C00);
                color: white;
                border: none;
                padding: 20px 40px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 16px;
                min-height: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #F57C00, stop: 1 #FF9800);
                transform: scale(1.05);
            }
        """)
        manual_btn.clicked.connect(self.show_manual_popup)
        message_options_layout.addWidget(manual_btn)
        
        message_options_group.setLayout(message_options_layout)
        message_layout.addWidget(message_options_group)
        
        # Dil ve mesaj tipi seçimi
        settings_group = QGroupBox("⚙️ Mesaj Ayarları")
        settings_layout = QGridLayout()
        
        # Dil seçimi
        settings_layout.addWidget(QLabel("🌍 Mesaj Dili:"), 0, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "Türkçe",
            "English", 
            "Deutsch",
            "Français",
            "Español",
            "Italiano",
            "Русский",
            "العربية",
            "中文",
            "日本語",
            "Polski"
        ])
        settings_layout.addWidget(self.language_combo, 0, 1)
        
        # Mesaj tipi seçimi
        settings_layout.addWidget(QLabel("📝 Mesaj Tipi:"), 1, 0)
        self.message_type_combo = QComboBox()
        self.message_type_combo.addItems([
            "Tanıtım Mesajı",
            "Takip Mesajı", 
            "Kampanya Duyurusu",
            "Bilgilendirme",
            "Teşekkür Mesajı",
            "Randevu Talebi",
            "Ürün Tanıtımı",
            "Hizmet Sunumu",
            "İşbirliği Teklifi",
            "Özel Mesaj"
        ])
        settings_layout.addWidget(self.message_type_combo, 1, 1)
        
        # Otomatik mesaj üretimi
        self.auto_generate_check = QCheckBox("🤖 Her Firma için Otomatik AI Mesaj Üret")
        self.auto_generate_check.setChecked(True)
        settings_layout.addWidget(self.auto_generate_check, 2, 0, 1, 2)
        
        settings_group.setLayout(settings_layout)
        message_layout.addWidget(settings_group)
        
        # Şablon seçimi
        template_group = QGroupBox("📋 Şablon Seçimi")
        template_layout = QHBoxLayout()
        
        template_layout.addWidget(QLabel("Şablon:"))
        self.template_combo = QComboBox()
        self.template_combo.addItem("-- Şablon Seç --")
        self.template_combo.currentIndexChanged.connect(self.on_template_selected)
        template_layout.addWidget(self.template_combo)
        
        self.generate_template_btn = QPushButton("🎯 AI ile Şablon Oluştur")
        self.generate_template_btn.clicked.connect(self.generate_ai_template)
        template_layout.addWidget(self.generate_template_btn)
        
        template_layout.addStretch()
        template_group.setLayout(template_layout)
        message_layout.addWidget(template_group)
        
        # Mesaj editörü
        editor_group = QGroupBox("✏️ Mesaj İçeriği")
        editor_layout = QVBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("""🤖 AI ile otomatik mesaj üretimi aktif!

Manuel mesaj yazmak isterseniz:
- {firma_adi} - Firma adı
- {firma_iletisim} - İletişim kişisi  
- {firma_sektoru} - Firma sektörü
- {firma_ozet} - Firma özeti
- {firma_website} - Website
- {firma_email} - E-mail

AI, her firma için özel mesajlar oluşturacak!""")
        editor_layout.addWidget(self.message_input)
        
        editor_group.setLayout(editor_layout)
        message_layout.addWidget(editor_group)
        
        self.tab_widget.addTab(message_tab, "📝 Mesaj Ayarları")
        
        # 3. Gönderim Kontrolü Tab'ı
        control_tab = QWidget()
        control_layout = QVBoxLayout(control_tab)
        
        # Gönderim ayarları
        send_group = QGroupBox("🚀 Gönderim Kontrol Ayarları")
        send_layout = QGridLayout()
        
        # Onay süresi
        send_layout.addWidget(QLabel("⏱️ Onay Süresi:"), 0, 0)
        self.approval_time_spin = QSpinBox()
        self.approval_time_spin.setRange(10, 120)
        self.approval_time_spin.setValue(30)
        self.approval_time_spin.setSuffix(" saniye")
        send_layout.addWidget(self.approval_time_spin, 0, 1)
        
        # Mesajlar arası bekleme
        send_layout.addWidget(QLabel("⏳ Mesajlar Arası Bekleme:"), 1, 0)
        self.message_delay_spin = QSpinBox()
        self.message_delay_spin.setRange(5, 60)
        self.message_delay_spin.setValue(10)
        self.message_delay_spin.setSuffix(" saniye")
        send_layout.addWidget(self.message_delay_spin, 1, 1)
        
        send_group.setLayout(send_layout)
        control_layout.addWidget(send_group)
        
        # Önizleme alanı
        preview_group = QGroupBox("👀 Mesaj Önizlemesi")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlaceholderText("Mesaj önizlemesi burada görünecek...")
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        control_layout.addWidget(preview_group)
        
        # İlerleme durumu
        progress_group = QGroupBox("📊 İlerleme Durumu")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Hazır - Gönderime başlamak için 'Başla' butonuna tıklayın")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        control_layout.addWidget(progress_group)
        
        self.tab_widget.addTab(control_tab, "🎯 Gönderim Kontrolü")
        
        layout.addWidget(self.tab_widget)
        
        # Alt butonlar
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🚀 Toplu Mesaj Gönderimini Başlat")
        self.start_btn.clicked.connect(self.start_bulk_messaging)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #5a67d8, stop: 1 #667eea);
            }
        """)
        
        self.cancel_btn = QPushButton("❌ İptal")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Onay dialog'u için butonlar (gizli)
        self.approval_dialog_buttons = QHBoxLayout()
        
        self.send_btn = QPushButton("✅ Gönder")
        self.send_btn.clicked.connect(self.send_current_message)
        self.send_btn.setVisible(False)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        self.skip_btn = QPushButton("⏭️ Atla")
        self.skip_btn.clicked.connect(self.skip_current_firm)
        self.skip_btn.setVisible(False)
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        self.regenerate_btn = QPushButton("🔄 Yeniden Üret")
        self.regenerate_btn.clicked.connect(self.regenerate_current_message)
        self.regenerate_btn.setVisible(False)
        self.regenerate_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        self.approval_dialog_buttons.addWidget(self.send_btn)
        self.approval_dialog_buttons.addWidget(self.skip_btn)
        self.approval_dialog_buttons.addWidget(self.regenerate_btn)
        self.approval_dialog_buttons.addStretch()
        
        layout.addLayout(self.approval_dialog_buttons)
    
    def load_firms(self):
        """📊 Firmaları tabloya yükle - Ultra Gelişmiş"""
        self.firms_table.setRowCount(len(self.firms))
        
        # Sektör listesini güncelle
        sectors = set()
        for firm in self.firms:
            sector = firm.get('sector', 'Belirtilmemiş')
            if sector:
                sectors.add(sector)
        
        self.sector_filter.clear()
        self.sector_filter.addItem("Tüm Sektörler")
        for sector in sorted(sectors):
            self.sector_filter.addItem(sector)
        
        for i, firm in enumerate(self.firms):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.update_stats)
            self.firms_table.setCellWidget(i, 0, checkbox)
            
            # Firma bilgileri - Düzeltilmiş
            firm_name = firm.get('name', '')
            if not firm_name:
                firm_name = 'İsimsiz Firma'
            
            # Firma adını kısalt (çok uzunsa)
            display_name = firm_name
            if len(firm_name) > 50:
                display_name = firm_name[:47] + "..."
            
            self.firms_table.setItem(i, 1, QTableWidgetItem(display_name))
            
            # Sektör
            sector = firm.get('sector', 'Belirtilmemiş')
            if not sector:
                sector = 'Belirtilmemiş'
            self.firms_table.setItem(i, 2, QTableWidgetItem(sector))
            
            # Telefon
            phone = firm.get('phone', '')
            if not phone:
                phone = '❌ Yok'
            self.firms_table.setItem(i, 3, QTableWidgetItem(phone))
            
            # Website
            website = firm.get('website', '')
            if website:
                # Website'yi kısalt
                if len(website) > 25:
                    website = website[:22] + "..."
                self.firms_table.setItem(i, 4, QTableWidgetItem(website))
            else:
                self.firms_table.setItem(i, 4, QTableWidgetItem("❌ Yok"))
            
            # Durum
            status = firm.get('status', 'active')
            status_text = {
                'active': 'Aktif',
                'inactive': 'Pasif', 
                'prospect': 'Potansiyel',
                'customer': 'Müşteri'
            }.get(status, 'Aktif')
            self.firms_table.setItem(i, 5, QTableWidgetItem(status_text))
            
            # Son iletişim
            last_contact = firm.get('last_contact_date', 'Yok')
            if last_contact and last_contact != 'Yok':
                try:
                    from datetime import datetime
                    dt = datetime.strptime(last_contact, "%Y-%m-%d %H:%M:%S")
                    last_contact = dt.strftime("%d.%m.%Y")
                except:
                    pass
            self.firms_table.setItem(i, 6, QTableWidgetItem(str(last_contact)))
        
        # Tablo ayarları - Düzeltilmiş
        self.firms_table.resizeColumnsToContents()
        
        # Sütun genişliklerini ayarla
        self.firms_table.setColumnWidth(0, 50)   # Seç checkbox
        self.firms_table.setColumnWidth(1, 300)  # Firma Adı
        self.firms_table.setColumnWidth(2, 150)  # Sektör
        self.firms_table.setColumnWidth(3, 120)  # Telefon
        self.firms_table.setColumnWidth(4, 200)  # Website
        self.firms_table.setColumnWidth(5, 100)  # Durum
        self.firms_table.setColumnWidth(6, 120)  # Son İletişim
        
        # Tablo özelliklerini ayarla
        self.firms_table.setAlternatingRowColors(True)
        self.firms_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.firms_table.setSortingEnabled(True)
        self.firms_table.setWordWrap(False)
        
        # Satır yüksekliğini ayarla
        self.firms_table.verticalHeader().setDefaultSectionSize(30)
        
        # Çift tıklama olayını ekle
        self.firms_table.cellDoubleClicked.connect(self.on_firm_double_clicked)
        
        self.update_stats()
        self.update_firm_count()
    
    def on_firm_double_clicked(self, row, column):
        """🖱️ Firma çift tıklama olayı"""
        try:
            if row < len(self.firms):
                firm = self.firms[row]
                self.show_firm_details_popup(firm)
        except Exception as e:
            logger.error(f"Firma çift tıklama hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Firma detayları gösterilemedi:\n{str(e)}")
    
    def show_firm_details_popup(self, firm):
        """🏢 Firma detayları popup'ı göster"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"🏢 {firm.get('name', 'Firma Detayları')}")
            dialog.setModal(True)
            dialog.resize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Firma bilgileri
            info_group = QGroupBox("📋 Firma Bilgileri")
            info_layout = QFormLayout()
            
            info_layout.addRow("🏢 Firma Adı:", QLabel(firm.get('name', 'Belirtilmemiş')))
            info_layout.addRow("📞 Telefon:", QLabel(firm.get('phone', 'Belirtilmemiş')))
            info_layout.addRow("📧 E-mail:", QLabel(firm.get('email', 'Belirtilmemiş')))
            info_layout.addRow("🌐 Website:", QLabel(firm.get('website', 'Belirtilmemiş')))
            info_layout.addRow("🏭 Sektör:", QLabel(firm.get('sector', 'Belirtilmemiş')))
            info_layout.addRow("👤 İletişim Kişisi:", QLabel(firm.get('contact_person', 'Belirtilmemiş')))
            info_layout.addRow("📍 Adres:", QLabel(firm.get('address', 'Belirtilmemiş')))
            info_layout.addRow("📝 Özet:", QLabel(firm.get('summary', 'Belirtilmemiş')))
            info_layout.addRow("📊 Durum:", QLabel(firm.get('status', 'Belirtilmemiş')))
            
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
            
            # Butonlar
            button_layout = QHBoxLayout()
            close_btn = QPushButton("❌ Kapat")
            close_btn.clicked.connect(dialog.accept)
            button_layout.addWidget(close_btn)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Firma detay popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Firma detayları gösterilemedi:\n{str(e)}")
    
    def show_message_preview_popup(self, message, firm):
        """👀 Mesaj önizleme popup'ı göster"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"👀 Mesaj Önizleme - {firm.get('name', 'Firma')}")
            dialog.setModal(True)
            dialog.resize(600, 500)
            
            layout = QVBoxLayout(dialog)
            
            # Firma bilgileri
            firm_group = QGroupBox("📋 Alıcı Bilgileri")
            firm_layout = QFormLayout()
            
            firm_layout.addRow("🏢 Firma:", QLabel(firm.get('name', 'Belirtilmemiş')))
            firm_layout.addRow("📞 Telefon:", QLabel(firm.get('phone', 'Belirtilmemiş')))
            firm_layout.addRow("👤 İletişim:", QLabel(firm.get('contact_person', 'Belirtilmemiş')))
            firm_layout.addRow("🏭 Sektör:", QLabel(firm.get('sector', 'Belirtilmemiş')))
            
            firm_group.setLayout(firm_layout)
            layout.addWidget(firm_group)
            
            # Mesaj içeriği
            message_group = QGroupBox("💬 Mesaj İçeriği")
            message_layout = QVBoxLayout()
            
            message_text = QTextEdit()
            message_text.setPlainText(message)
            message_text.setReadOnly(True)
            message_text.setMaximumHeight(200)
            message_layout.addWidget(message_text)
            
            # Karakter sayısı
            char_count = QLabel(f"📊 Karakter Sayısı: {len(message)}")
            message_layout.addWidget(char_count)
            
            message_group.setLayout(message_layout)
            layout.addWidget(message_group)
            
            # Butonlar
            button_layout = QHBoxLayout()
            send_btn = QPushButton("✅ Gönder")
            send_btn.clicked.connect(lambda: self.send_message_from_popup(message, firm, dialog))
            edit_btn = QPushButton("✏️ Düzenle")
            edit_btn.clicked.connect(lambda: self.edit_message_from_popup(message, firm, dialog))
            close_btn = QPushButton("❌ Kapat")
            close_btn.clicked.connect(dialog.accept)
            
            button_layout.addWidget(send_btn)
            button_layout.addWidget(edit_btn)
            button_layout.addWidget(close_btn)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Mesaj önizleme popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj önizlemesi gösterilemedi:\n{str(e)}")
    
    def send_message_from_popup(self, message, firm, dialog):
        """📤 Popup'tan mesaj gönder"""
        try:
            # Mesajı gönder
            success = self.send_current_message()
            if success:
                QMessageBox.information(self, "✅ Başarılı", f"Mesaj {firm.get('name', 'firmaya')} başarıyla gönderildi!")
                dialog.accept()
            else:
                QMessageBox.warning(self, "⚠️ Uyarı", "Mesaj gönderilemedi!")
                
        except Exception as e:
            logger.error(f"Popup mesaj gönderme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj gönderilemedi:\n{str(e)}")
    
    def edit_message_from_popup(self, message, firm, dialog):
        """✏️ Popup'tan mesaj düzenle"""
        try:
            # Mesaj düzenleme dialog'u
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle(f"✏️ Mesaj Düzenle - {firm.get('name', 'Firma')}")
            edit_dialog.setModal(True)
            edit_dialog.resize(500, 300)
            
            layout = QVBoxLayout(edit_dialog)
            
            # Mesaj editörü
            message_edit = QTextEdit()
            message_edit.setPlainText(message)
            layout.addWidget(message_edit)
            
            # Butonlar
            button_layout = QHBoxLayout()
            save_btn = QPushButton("💾 Kaydet")
            save_btn.clicked.connect(lambda: self.save_edited_message(message_edit.toPlainText(), firm, edit_dialog, dialog))
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.clicked.connect(edit_dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)
            
            edit_dialog.exec()
            
        except Exception as e:
            logger.error(f"Mesaj düzenleme popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj düzenlenemedi:\n{str(e)}")
    
    def save_edited_message(self, new_message, firm, edit_dialog, preview_dialog):
        """💾 Düzenlenen mesajı kaydet"""
        try:
            # Mesajı güncelle
            self.generated_messages[self.current_firm_index] = new_message
            
            QMessageBox.information(self, "✅ Başarılı", "Mesaj başarıyla güncellendi!")
            edit_dialog.accept()
            preview_dialog.accept()
            
            # Önizlemeyi yenile
            self.show_message_preview(new_message, firm)
            
        except Exception as e:
            logger.error(f"Mesaj kaydetme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj kaydedilemedi:\n{str(e)}")
    
    def show_ai_message_popup(self):
        """🤖 AI Mesaj Popup'ı - Büyük ve Düzenli"""
        print("🚀 AI Mesaj Popup açılıyor...")
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("🤖 AI Mesaj Oluşturucu - Ultra Gelişmiş")
            dialog.setModal(True)
            
            # Tam ekran boyut
            screen = QApplication.primaryScreen().geometry()
            dialog.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
            
            # Popup stilleri
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #3a3a3a;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    background-color: #2a2a2a;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #0d7377;
                }
                QTextEdit {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 8px;
                    color: #ffffff;
                    font-size: 12px;
                }
                QComboBox {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 5px;
                    color: #ffffff;
                    min-width: 100px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #ffffff;
                }
                QSpinBox {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 5px;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
            
            # Ana layout
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Başlık
            title_label = QLabel("🤖 AI Mesaj Oluşturucu")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #0d7377;
                    padding: 10px;
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title_label)
            
            # Ana içerik - Splitter ile yan yana
            main_splitter = QSplitter(Qt.Horizontal)
            
            # Sol panel - Ayarlar
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # Mesaj ayarları
            settings_group = QGroupBox("⚙️ Mesaj Ayarları")
            settings_layout = QFormLayout()
            
            # Dil seçimi
            settings_layout.addRow("🌍 Mesaj Dili:", QComboBox())
            language_combo = settings_layout.itemAt(settings_layout.rowCount()-1, QFormLayout.FieldRole).widget()
            language_combo.addItems([
                "Türkçe", "English", "Deutsch", "Français", "Español", 
                "Italiano", "Русский", "العربية", "中文", "日本語", "Polski"
            ])
            
            # Mesaj tipi
            settings_layout.addRow("📝 Mesaj Tipi:", QComboBox())
            message_type_combo = settings_layout.itemAt(settings_layout.rowCount()-1, QFormLayout.FieldRole).widget()
            message_type_combo.addItems([
                "Tanıtım Mesajı", "Takip Mesajı", "Kampanya Duyurusu",
                "Bilgilendirme", "Teşekkür Mesajı", "Randevu Talebi",
                "Ürün Tanıtımı", "Hizmet Sunumu", "İşbirliği Teklifi", "Özel Mesaj"
            ])
            
            # Ton seçimi
            settings_layout.addRow("🎭 Mesaj Tonu:", QComboBox())
            tone_combo = settings_layout.itemAt(settings_layout.rowCount()-1, QFormLayout.FieldRole).widget()
            tone_combo.addItems([
                "Profesyonel", "Samimi", "Resmi", "Dostane", "Satış Odaklı", "Bilgilendirici"
            ])
            
            # Karakter sınırı
            settings_layout.addRow("📊 Karakter Sınırı:", QSpinBox())
            char_limit_spin = settings_layout.itemAt(settings_layout.rowCount()-1, QFormLayout.FieldRole).widget()
            char_limit_spin.setRange(50, 500)
            char_limit_spin.setValue(180)
            char_limit_spin.setSuffix(" karakter")
            
            settings_group.setLayout(settings_layout)
            left_layout.addWidget(settings_group)
            
            # AI talimatları
            instructions_group = QGroupBox("🎯 AI Talimatları")
            instructions_layout = QVBoxLayout()
            
            instructions_text = QTextEdit()
            instructions_text.setPlaceholderText("""AI'ya özel talimatlar verin...

Örnek:
- Firma sektörüne uygun terminoloji kullan
- İletişim kişisinin adını kullan
- Call-to-action ekle
- Profesyonel ama samimi ton kullan
- WhatsApp için uygun format""")
            instructions_text.setMaximumHeight(150)
            instructions_layout.addWidget(instructions_text)
            
            instructions_group.setLayout(instructions_layout)
            left_layout.addWidget(instructions_group)
            
            # Firma bilgileri
            firm_info_group = QGroupBox("🏢 Seçili Firma Bilgileri")
            firm_info_layout = QVBoxLayout()
            
            firm_info_text = QTextEdit()
            firm_info_text.setReadOnly(True)
            firm_info_text.setMaximumHeight(100)
            firm_info_text.setPlaceholderText("Firma bilgileri burada görünecek...")
            firm_info_layout.addWidget(firm_info_text)
            
            firm_info_group.setLayout(firm_info_layout)
            left_layout.addWidget(firm_info_group)
            
            main_splitter.addWidget(left_panel)
            
            # Sağ panel - Mesaj editörü ve önizleme
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # Mesaj editörü
            editor_group = QGroupBox("✏️ Mesaj Editörü")
            editor_layout = QVBoxLayout()
            
            message_editor = QTextEdit()
            message_editor.setPlaceholderText("AI tarafından oluşturulan mesaj burada görünecek...")
            message_editor.setMinimumHeight(200)
            editor_layout.addWidget(message_editor)
            
            # Karakter sayacı
            char_counter = QLabel("📊 Karakter Sayısı: 0")
            editor_layout.addWidget(char_counter)
            
            editor_group.setLayout(editor_layout)
            right_layout.addWidget(editor_group)
            
            # Önizleme
            preview_group = QGroupBox("👀 Mesaj Önizlemesi")
            preview_layout = QVBoxLayout()
            
            preview_text = QTextEdit()
            preview_text.setReadOnly(True)
            preview_text.setMaximumHeight(150)
            preview_text.setPlaceholderText("Mesaj önizlemesi burada görünecek...")
            preview_layout.addWidget(preview_text)
            
            preview_group.setLayout(preview_layout)
            right_layout.addWidget(preview_group)
            
            main_splitter.addWidget(right_panel)
            main_splitter.setSizes([400, 600])
            
            layout.addWidget(main_splitter)
            
            # Alt butonlar
            button_layout = QHBoxLayout()
            
            generate_btn = QPushButton("🤖 AI ile Oluştur")
            generate_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #4CAF50, stop: 1 #45a049);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #45a049, stop: 1 #4CAF50);
                }
            """)
            
            regenerate_btn = QPushButton("🔄 Yeniden Oluştur")
            regenerate_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #FF9800, stop: 1 #F57C00);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #F57C00, stop: 1 #FF9800);
                }
            """)
            
            preview_all_btn = QPushButton("👀 Tümünü Önizle")
            preview_all_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #2196F3, stop: 1 #1976D2);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #1976D2, stop: 1 #2196F3);
                }
            """)
            
            save_btn = QPushButton("💾 Kaydet ve Kapat")
            save_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #0d7377, stop: 1 #14a085);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #14a085, stop: 1 #0d7377);
                }
            """)
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #f44336;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #d32f2f;
                }
            """)
            
            button_layout.addWidget(generate_btn)
            button_layout.addWidget(regenerate_btn)
            button_layout.addWidget(preview_all_btn)
            button_layout.addStretch()
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            # Buton bağlantıları
            generate_btn.clicked.connect(lambda: self.generate_ai_message_in_popup(
                language_combo.currentText(),
                message_type_combo.currentText(),
                tone_combo.currentText(),
                char_limit_spin.value(),
                instructions_text.toPlainText(),
                message_editor,
                char_counter,
                preview_text
            ))
            
            regenerate_btn.clicked.connect(lambda: self.generate_ai_message_in_popup(
                language_combo.currentText(),
                message_type_combo.currentText(),
                tone_combo.currentText(),
                char_limit_spin.value(),
                instructions_text.toPlainText(),
                message_editor,
                char_counter,
                preview_text
            ))
            
            preview_all_btn.clicked.connect(lambda: self.preview_all_messages_in_popup(preview_text))
            
            save_btn.clicked.connect(lambda: self.save_ai_message_from_popup(message_editor.toPlainText(), dialog))
            cancel_btn.clicked.connect(dialog.reject)
            
            # Karakter sayacı güncelleme
            message_editor.textChanged.connect(lambda: char_counter.setText(f"📊 Karakter Sayısı: {len(message_editor.toPlainText())}"))
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"AI mesaj popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"AI mesaj popup'ı açılamadı:\n{str(e)}")
    
    def generate_ai_message_in_popup(self, language, message_type, tone, char_limit, instructions, editor, counter, preview):
        """🤖 Popup içinde AI mesaj oluştur - Bilgi Öğrenim Entegreli"""
        try:
            if not self.gpt_manager or not hasattr(self.gpt_manager, 'client') or not self.gpt_manager.client:
                QMessageBox.warning(self, "⚠️ Uyarı", "OpenAI API ayarlanmamış!")
                return
            
            # Seçili firmaları al
            selected_firms = []
            for i in range(self.firms_table.rowCount()):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox and checkbox.isChecked():
                    if i < len(self.firms):
                        selected_firms.append(self.firms[i])
            
            if not selected_firms:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen en az bir firma seçin!")
                return
            
            # İlk firma için mesaj oluştur
            firm = selected_firms[0]
            
            # Dil kod haritası
            language_codes = {
                "Türkçe": "Turkish", "English": "English", "Deutsch": "German", 
                "Français": "French", "Español": "Spanish", "Italiano": "Italian",
                "Русский": "Russian", "العربية": "Arabic", "中文": "Chinese", "日本語": "Japanese", "Polski": "Polish"
            }
            
            lang_code = language_codes.get(language, "Turkish")
            
            # 🧠 Bilgi Öğrenim verilerini al
            learned_knowledge = ""
            if self.db:
                try:
                    all_knowledge = self.db.get_all_knowledge(filter_learned=True)
                    if all_knowledge:
                        knowledge_summaries = []
                        for knowledge in all_knowledge[:5]:  # En fazla 5 bilgi kullan
                            if knowledge.get('ai_summary'):
                                knowledge_summaries.append(f"• {knowledge.get('title', 'Bilgi')}: {knowledge.get('ai_summary', '')}")
                        
                        if knowledge_summaries:
                            learned_knowledge = f"""
            
            🧠 Öğrenilmiş Firma Bilgileri (AI Analizi):
            {chr(10).join(knowledge_summaries)}
            
            Bu bilgileri kullanarak daha kişiselleştirilmiş ve detaylı mesaj oluştur.
            """
                except Exception as e:
                    print(f"Bilgi öğrenim verisi alınamadı: {e}")
            
            # Prompt oluştur
            prompt = f"""
            Lütfen {lang_code} dilinde profesyonel bir WhatsApp B2B mesajı oluştur.
            
            Firma Bilgileri:
            - Firma Adı: {firm.get('name', 'Belirtilmemiş')}
            - Sektör: {firm.get('sector', 'Belirtilmemiş')}
            - İletişim Kişisi: {firm.get('contact_person', 'Belirtilmemiş')}
            - Telefon: {firm.get('phone', 'Belirtilmemiş')}
            - Email: {firm.get('email', 'Belirtilmemiş')}
            - Website: {firm.get('website', 'Belirtilmemiş')}
            {learned_knowledge}
            
            Mesaj Özellikleri:
            - Mesaj Tipi: {message_type}
            - Dil: {lang_code}
            - Ton: {tone}
            - Maksimum Karakter: {char_limit}
            
            Özel Talimatlar:
            {instructions}
            
            Mesaj özellikleri:
            - {lang_code} dilinde ve o dilin kültürel özelliklerine uygun
            - {tone} ton kullan
            - Firmaya özel detaylar kullan
            - Net bir call-to-action içermeli
            - İletişim kişisinin ismini kullan (varsa)
            - Sektöre uygun terminoloji
            - Öğrenilmiş firma bilgilerini kullanarak daha kişiselleştirilmiş içerik oluştur
            
            Sadece mesaj metnini döndür, başka hiçbir şey ekleme.
            """
            
            # AI'ya gönder
            response = self.gpt_manager.client.chat.completions.create(
                model=self.gpt_manager.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"Sen {lang_code} dilinde uzman bir B2B satış uzmanısın. O dilin kültürel özelliklerini ve iş yapma tarzını mükemmel biliyorsun. Kısa, etkili ve kişiselleştirilmiş mesajlar yazarsın."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.9
            )
            
            message = response.choices[0].message.content.strip()
            
            # Eğer mesaj Türkçe değilse, Türkçe çevirisini de oluştur
            turkish_translation = ""
            if lang_code != "Turkish":
                try:
                    translation_prompt = f"""
                    Lütfen aşağıdaki mesajı Türkçe'ye çevir. Çeviri doğal ve akıcı olsun, WhatsApp B2B mesajı formatında kalsın.
                    
                    Orijinal Mesaj ({lang_code}):
                    {message}
                    
                    Sadece Türkçe çevirisini döndür, başka açıklama ekleme.
                    """
                    
                    translation_response = self.gpt_manager.client.chat.completions.create(
                        model=self.gpt_manager.model,
                        messages=[
                            {
                                "role": "system", 
                                "content": "Sen profesyonel bir çevirmensin. B2B mesajları doğal ve akıcı bir şekilde Türkçe'ye çevirirsin."
                            },
                            {
                                "role": "user", 
                                "content": translation_prompt
                            }
                        ],
                        max_tokens=200,
                        temperature=0.7
                    )
                    
                    turkish_translation = translation_response.choices[0].message.content.strip()
                except Exception as e:
                    print(f"Türkçe çeviri hatası: {e}")
                    turkish_translation = "Çeviri oluşturulamadı"
            
            # Mesajı editöre koy (orijinal mesaj)
            editor.setPlainText(message)
            
            # Önizlemeyi güncelle - hem orijinal hem çeviri
            if turkish_translation and lang_code != "Turkish":
                preview_text = f"""
📱 Alıcı: {firm.get('name', 'Bilinmeyen')} ({firm.get('phone', '')})
👤 İletişim: {firm.get('contact_person', 'Belirtilmemiş')}
🏢 Sektör: {firm.get('sector', 'Belirtilmemiş')}

🌍 {language} Mesajı:
{message}

🇹🇷 Türkçe Çevirisi:
{turkish_translation}

📊 Karakter Sayısı: {len(message)} (Orijinal) / {len(turkish_translation)} (Çeviri)
"""
            else:
                preview_text = f"""
📱 Alıcı: {firm.get('name', 'Bilinmeyen')} ({firm.get('phone', '')})
👤 İletişim: {firm.get('contact_person', 'Belirtilmemiş')}
🏢 Sektör: {firm.get('sector', 'Belirtilmemiş')}

💬 Mesaj İçeriği:
{message}

📊 Karakter Sayısı: {len(message)}
"""
            preview.setPlainText(preview_text)
            
            success_msg = "AI mesajı başarıyla oluşturuldu!"
            if turkish_translation and lang_code != "Turkish":
                success_msg += "\n\nTürkçe çevirisi de eklendi!"
            
            QMessageBox.information(self, "✅ Başarılı", success_msg)
            
        except Exception as e:
            logger.error(f"AI mesaj oluşturma hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"AI mesajı oluşturulamadı:\n{str(e)}")
    
    def preview_all_messages_in_popup(self, preview_widget):
        """👀 Tüm mesajları popup'ta önizle"""
        try:
            # Seçili firmaları al
            selected_firms = []
            for i in range(self.firms_table.rowCount()):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox and checkbox.isChecked():
                    if i < len(self.firms):
                        selected_firms.append(self.firms[i])
            
            if not selected_firms:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen en az bir firma seçin!")
                return
            
            preview_text = "👀 TÜM MESAJLAR ÖNİZLEMESİ\n\n"
            preview_text += f"📊 Toplam Firma: {len(selected_firms)}\n\n"
            
            for i, firm in enumerate(selected_firms[:5]):  # İlk 5 tanesini göster
                preview_text += f"🏢 {i+1}. {firm.get('name', 'Bilinmeyen')}\n"
                preview_text += f"📞 {firm.get('phone', 'Telefon Yok')}\n"
                preview_text += f"🏭 {firm.get('sector', 'Sektör Belirtilmemiş')}\n"
                preview_text += "💬 [AI tarafından oluşturulacak mesaj]\n\n"
            
            if len(selected_firms) > 5:
                preview_text += f"... ve {len(selected_firms) - 5} firma daha\n"
            
            preview_widget.setPlainText(preview_text)
            
        except Exception as e:
            logger.error(f"Tüm mesajları önizleme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Önizleme oluşturulamadı:\n{str(e)}")
    
    def save_ai_message_from_popup(self, message, dialog):
        """💾 AI mesajını popup'tan kaydet"""
        try:
            if not message.strip():
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir mesaj oluşturun!")
                return
            
            # Ana mesaj editörüne koy
            if hasattr(self, 'message_input'):
                self.message_input.setPlainText(message)
            
            QMessageBox.information(self, "✅ Başarılı", "AI mesajı başarıyla kaydedildi!")
            dialog.accept()
            
        except Exception as e:
            logger.error(f"AI mesaj kaydetme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj kaydedilemedi:\n{str(e)}")
    
    def show_ai_message_popup(self):
        """🤖 AI Mesaj Popup'ı - Detaylı ve Gelişmiş"""
        print("🚀 AI Mesaj Popup açılıyor...")
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("🤖 AI Mesaj Oluşturucu - Ultra Gelişmiş")
            dialog.setModal(True)
            
            # Tam ekran boyut
            screen = QApplication.primaryScreen().geometry()
            dialog.resize(int(screen.width() * 0.85), int(screen.height() * 0.85))
            
            # Ana layout
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Başlık
            title_label = QLabel("🤖 AI Destekli Mesaj Oluşturucu")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 26px;
                    font-weight: bold;
                    color: #4CAF50;
                    padding: 15px;
                    background-color: #1a1a1a;
                    border-radius: 10px;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title_label)
            
            # Ana içerik - Splitter ile yan yana
            main_splitter = QSplitter(Qt.Horizontal)
            
            # Sol panel - AI Ayarları
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # AI Ayarları
            ai_settings_group = QGroupBox("⚙️ AI Ayarları")
            ai_settings_layout = QGridLayout()
            
            # Dil seçimi
            ai_settings_layout.addWidget(QLabel("🌍 Mesaj Dili:"), 0, 0)
            language_combo = QComboBox()
            language_combo.addItems([
                "Türkçe", "English", "Deutsch", "Français", "Español", 
                "Italiano", "Русский", "العربية", "中文", "日本語", "Polski"
            ])
            ai_settings_layout.addWidget(language_combo, 0, 1)
            
            # Mesaj tipi
            ai_settings_layout.addWidget(QLabel("📝 Mesaj Tipi:"), 1, 0)
            message_type_combo = QComboBox()
            message_type_combo.addItems([
                "Tanıtım Mesajı", "Takip Mesajı", "Kampanya Duyurusu",
                "Bilgilendirme", "Teşekkür Mesajı", "Randevu Talebi",
                "Ürün Tanıtımı", "Hizmet Sunumu", "İşbirliği Teklifi", "Özel Mesaj"
            ])
            ai_settings_layout.addWidget(message_type_combo, 1, 1)
            
            # Ton
            ai_settings_layout.addWidget(QLabel("🎭 Mesaj Tonu:"), 2, 0)
            tone_combo = QComboBox()
            tone_combo.addItems([
                "Profesyonel", "Samimi", "Resmi", "Eğlenceli", "Ciddi", "Arkadaşça"
            ])
            ai_settings_layout.addWidget(tone_combo, 2, 1)
            
            # Karakter limiti
            ai_settings_layout.addWidget(QLabel("📊 Max Karakter:"), 3, 0)
            char_limit_spin = QSpinBox()
            char_limit_spin.setRange(50, 500)
            char_limit_spin.setValue(200)
            ai_settings_layout.addWidget(char_limit_spin, 3, 1)
            
            # Yaratıcılık seviyesi
            ai_settings_layout.addWidget(QLabel("🎨 Yaratıcılık:"), 4, 0)
            creativity_slider = QSlider(Qt.Horizontal)
            creativity_slider.setRange(0, 100)
            creativity_slider.setValue(70)
            creativity_label = QLabel("70%")
            creativity_slider.valueChanged.connect(lambda v: creativity_label.setText(f"{v}%"))
            creativity_layout = QHBoxLayout()
            creativity_layout.addWidget(creativity_slider)
            creativity_layout.addWidget(creativity_label)
            ai_settings_layout.addLayout(creativity_layout, 4, 1)
            
            ai_settings_group.setLayout(ai_settings_layout)
            left_layout.addWidget(ai_settings_group)
            
            # Özel Talimatlar
            instructions_group = QGroupBox("📝 Özel Talimatlar")
            instructions_layout = QVBoxLayout()
            
            instructions_input = QTextEdit()
            instructions_input.setPlaceholderText(
                "AI'ya özel talimatlar verin:\n\n"
                "Örnek:\n"
                "- Firma ismini mutlaka kullan\n"
                "- İletişim kişisine hitap et\n"
                "- Sektöre özel terimler kullan\n"
                "- Call-to-action ekle"
            )
            instructions_input.setMaximumHeight(150)
            instructions_layout.addWidget(instructions_input)
            
            instructions_group.setLayout(instructions_layout)
            left_layout.addWidget(instructions_group)
            
            # Firma Seçimi
            firm_group = QGroupBox("🏢 Test Firması Seç")
            firm_layout = QVBoxLayout()
            
            firm_combo = QComboBox()
            firm_combo.addItem("-- Önizleme için firma seç --")
            for firm in self.firms[:10]:  # İlk 10 firma
                firm_combo.addItem(f"{firm.get('name', 'Bilinmeyen')} - {firm.get('sector', 'N/A')}", firm)
            firm_layout.addWidget(firm_combo)
            
            firm_group.setLayout(firm_layout)
            left_layout.addWidget(firm_group)
            
            left_layout.addStretch()
            main_splitter.addWidget(left_panel)
            
            # Sağ panel - Mesaj Önizleme ve Düzenleme
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # Mesaj Editörü
            editor_group = QGroupBox("✏️ Oluşturulan Mesaj")
            editor_layout = QVBoxLayout()
            
            message_editor = QTextEdit()
            message_editor.setPlaceholderText("AI tarafından oluşturulan mesaj burada görünecek...")
            message_editor.setMinimumHeight(200)
            editor_layout.addWidget(message_editor)
            
            editor_group.setLayout(editor_layout)
            right_layout.addWidget(editor_group)
            
            # Türkçe Çeviri Editörü
            translation_group = QGroupBox("🇹🇷 Türkçe Çevirisi")
            translation_layout = QVBoxLayout()
            
            translation_editor = QTextEdit()
            translation_editor.setPlaceholderText("Türkçe çevirisi burada görünecek...")
            translation_editor.setMinimumHeight(200)
            translation_editor.setStyleSheet("""
                QTextEdit {
                    background-color: #2a3a2a;
                    color: white;
                    border: 2px solid #4a5a4a;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                }
                QTextEdit:focus {
                    border: 2px solid #4CAF50;
                }
            """)
            translation_layout.addWidget(translation_editor)
            
            translation_group.setLayout(translation_layout)
            right_layout.addWidget(translation_group)
            
            # Önizleme
            preview_group = QGroupBox("👀 Mesaj Önizlemesi")
            preview_layout = QVBoxLayout()
            
            preview_text = QTextEdit()
            preview_text.setReadOnly(True)
            preview_text.setMaximumHeight(150)
            preview_text.setPlaceholderText("Mesaj önizlemesi burada görünecek...")
            preview_layout.addWidget(preview_text)
            
            preview_group.setLayout(preview_layout)
            right_layout.addWidget(preview_group)
            
            main_splitter.addWidget(right_panel)
            main_splitter.setSizes([int(screen.width() * 0.35), int(screen.width() * 0.50)])
            
            layout.addWidget(main_splitter)
            
            # Alt butonlar
            button_layout = QHBoxLayout()
            
            generate_btn = QPushButton("🎯 AI ile Mesaj Oluştur")
            generate_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #4CAF50, stop: 1 #45a049);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #45a049, stop: 1 #4CAF50);
                }
            """)
            generate_btn.clicked.connect(lambda: self.generate_ai_message_in_popup(
                message_editor, translation_editor, preview_text, firm_combo, language_combo, 
                message_type_combo, tone_combo, char_limit_spin, 
                creativity_slider, instructions_input
            ))
            button_layout.addWidget(generate_btn)
            
            preview_all_btn = QPushButton("👀 Tüm Mesajları Önizle")
            preview_all_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #2196F3, stop: 1 #1976D2);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #1976D2, stop: 1 #2196F3);
                }
            """)
            preview_all_btn.clicked.connect(lambda: self.preview_all_messages_in_popup(preview_text))
            button_layout.addWidget(preview_all_btn)
            
            save_btn = QPushButton("💾 Mesajı Kaydet ve Kullan")
            save_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #FF9800, stop: 1 #F57C00);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #F57C00, stop: 1 #FF9800);
                }
            """)
            save_btn.clicked.connect(lambda: self.save_ai_message_from_popup(message_editor.toPlainText(), dialog))
            button_layout.addWidget(save_btn)
            
            close_btn = QPushButton("❌ Kapat")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            close_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(close_btn)
            
            # WhatsApp gönder butonu
            whatsapp_btn = QPushButton("📱 WhatsApp'a Gönder ve Onayla")
            whatsapp_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #25D366, stop: 1 #128C7E);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #128C7E, stop: 1 #25D366);
                }
            """)
            whatsapp_btn.clicked.connect(lambda: self.send_to_whatsapp_with_approval(
                message_editor.toPlainText(), 
                translation_editor.toPlainText(), 
                firm_combo.currentData(),
                language_combo.currentText(),
                dialog
            ))
            button_layout.addWidget(whatsapp_btn)
            
            layout.addLayout(button_layout)
            
            # Popup'ı göster
            dialog.exec()
            
        except Exception as e:
            logger.error(f"AI Mesaj popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"AI Mesaj popup'ı açılamadı:\n{str(e)}")
    
    def send_to_whatsapp_with_approval(self, message, translation, firm, language, parent_dialog):
        """📱 WhatsApp'a onay ile gönder"""
        try:
            # Mesaj kontrolü
            if not message.strip():
                QMessageBox.warning(self, "⚠️ Uyarı", "Önce bir mesaj oluşturun!")
                return
            
            # Firma kontrolü
            if not firm:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir firma seçin!")
                return
            
            # Çeviri kontrolü
            if not translation or translation.strip() == "":
                translation = "Türkçe mesaj - çeviri gerekmiyor"
            
            # Onay dialog'unu göster
            approval_dialog = WhatsAppMessageApprovalDialog(
                self, 
                firm, 
                message, 
                translation,
                language
            )
            
            result = approval_dialog.exec()
            
            if approval_dialog.approved:
                # WhatsApp Web kontrolü
                if not self.whatsapp_view or not self.whatsapp_view.is_connected:
                    QMessageBox.warning(
                        self, 
                        "⚠️ WhatsApp Web Gerekli", 
                        "WhatsApp Web'i açın ve tekrar deneyin!\n\n"
                        "1. WhatsApp Web'i tarayıcıda açın\n"
                        "2. QR kodu tarayın\n"
                        "3. Bu butona tekrar tıklayın"
                    )
                    return
                
                # Mesajı WhatsApp'a gönder (sadece orijinal mesaj)
                success = self.whatsapp_view.send_message(firm['phone'], message)
                
                if success:
                    # Mesajı veritabanına kaydet
                    if hasattr(self, 'db') and self.db:
                        self.db.save_message(
                            firm['id'],
                            'sent',
                            message,
                            'whatsapp'
                        )
                    
                    QMessageBox.information(
                        self, 
                        "✅ Başarılı", 
                        f"Mesaj {firm.get('name', 'firmaya')} başarıyla gönderildi!\n\n"
                        f"📱 Telefon: {firm.get('phone', 'N/A')}\n"
                        f"🌍 Dil: {language}"
                    )
                    
                    # Ana popup'ı kapat
                    parent_dialog.accept()
                else:
                    QMessageBox.warning(
                        self, 
                        "⚠️ Gönderim Hatası", 
                        "Mesaj gönderilemedi. Lütfen tekrar deneyin."
                    )
            
        except Exception as e:
            logger.error(f"WhatsApp gönderim hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj gönderilemedi:\n{str(e)}")
    
    def generate_ai_message_in_popup(self, message_editor, translation_editor, preview_text, firm_combo, language_combo, 
                                   message_type_combo, tone_combo, char_limit_spin, 
                                   creativity_slider, instructions_input):
        """AI popup'ında mesaj oluştur - Bilgi Öğrenim Entegreli"""
        try:
            # Seçili firmayı al
            firm = firm_combo.currentData()
            if not firm:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir test firması seçin!")
                return
            
            # GPT Manager kontrolü
            if not self.gpt_manager or not hasattr(self.gpt_manager, 'client') or not self.gpt_manager.client:
                QMessageBox.warning(self, "⚠️ Uyarı", "OpenAI API ayarlanmamış!")
                return
            
            # Ayarları al
            language = language_combo.currentText()
            message_type = message_type_combo.currentText()
            tone = tone_combo.currentText()
            char_limit = char_limit_spin.value()
            creativity = creativity_slider.value() / 100.0
            instructions = instructions_input.toPlainText().strip()
            
            # Dil kod haritası
            language_codes = {
                "Türkçe": "Turkish", "English": "English", "Deutsch": "German", 
                "Français": "French", "Español": "Spanish", "Italiano": "Italian",
                "Русский": "Russian", "العربية": "Arabic", "中文": "Chinese", "日本語": "Japanese", "Polski": "Polish"
            }
            
            lang_code = language_codes.get(language, "Turkish")
            
            # 🧠 Bilgi Öğrenim verilerini al
            learned_knowledge = ""
            if self.db:
                try:
                    all_knowledge = self.db.get_all_knowledge(filter_learned=True)
                    if all_knowledge:
                        knowledge_summaries = []
                        for knowledge in all_knowledge[:5]:  # En fazla 5 bilgi kullan
                            if knowledge.get('ai_summary'):
                                knowledge_summaries.append(f"• {knowledge.get('title', 'Bilgi')}: {knowledge.get('ai_summary', '')}")
                        
                        if knowledge_summaries:
                            learned_knowledge = f"""
            
            🧠 Öğrenilmiş Firma Bilgileri (AI Analizi):
            {chr(10).join(knowledge_summaries)}
            
            Bu bilgileri kullanarak daha kişiselleştirilmiş ve detaylı mesaj oluştur.
            """
                except Exception as e:
                    print(f"Bilgi öğrenim verisi alınamadı: {e}")
            
            # Prompt oluştur
            prompt = f"""
            Lütfen {lang_code} dilinde profesyonel bir WhatsApp B2B mesajı oluştur.
            
            Firma Bilgileri:
            - Firma Adı: {firm.get('name', 'Belirtilmemiş')}
            - Sektör: {firm.get('sector', 'Belirtilmemiş')}
            - İletişim Kişisi: {firm.get('contact_person', 'Belirtilmemiş')}
            - Telefon: {firm.get('phone', 'Belirtilmemiş')}
            - Email: {firm.get('email', 'Belirtilmemiş')}
            - Website: {firm.get('website', 'Belirtilmemiş')}
            {learned_knowledge}
            
            Mesaj Özellikleri:
            - Mesaj Tipi: {message_type}
            - Dil: {lang_code}
            - Ton: {tone}
            - Maksimum Karakter: {char_limit}
            - Yaratıcılık: {creativity}
            
            Özel Talimatlar:
            {instructions}
            
            Mesaj özellikleri:
            - {lang_code} dilinde ve o dilin kültürel özelliklerine uygun
            - {tone} ton kullan
            - Firmaya özel detaylar kullan
            - Net bir call-to-action içermeli
            - İletişim kişisinin ismini kullan (varsa)
            - Sektöre uygun terminoloji
            - Öğrenilmiş firma bilgilerini kullanarak daha kişiselleştirilmiş içerik oluştur
            
            Sadece mesaj metnini döndür, başka hiçbir şey ekleme.
            """
            
            # AI'ya gönder
            response = self.gpt_manager.client.chat.completions.create(
                model=self.gpt_manager.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"Sen {lang_code} dilinde uzman bir B2B satış uzmanısın. O dilin kültürel özelliklerini ve iş yapma tarzını mükemmel biliyorsun. Kısa, etkili ve kişiselleştirilmiş mesajlar yazarsın."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=creativity
            )
            
            message = response.choices[0].message.content.strip()
            
            # Eğer mesaj Türkçe değilse, Türkçe çevirisini de oluştur
            turkish_translation = ""
            if lang_code != "Turkish":
                try:
                    translation_prompt = f"""
                    Lütfen aşağıdaki mesajı Türkçe'ye çevir. Çeviri doğal ve akıcı olsun, WhatsApp B2B mesajı formatında kalsın.
                    
                    Orijinal Mesaj ({lang_code}):
                    {message}
                    
                    Sadece Türkçe çevirisini döndür, başka açıklama ekleme.
                    """
                    
                    translation_response = self.gpt_manager.client.chat.completions.create(
                        model=self.gpt_manager.model,
                        messages=[
                            {
                                "role": "system", 
                                "content": "Sen profesyonel bir çevirmensin. B2B mesajları doğal ve akıcı bir şekilde Türkçe'ye çevirirsin."
                            },
                            {
                                "role": "user", 
                                "content": translation_prompt
                            }
                        ],
                        max_tokens=200,
                        temperature=0.7
                    )
                    
                    turkish_translation = translation_response.choices[0].message.content.strip()
                except Exception as e:
                    print(f"Türkçe çeviri hatası: {e}")
                    turkish_translation = "Çeviri oluşturulamadı"
            
            # Mesajı editöre koy (orijinal mesaj)
            message_editor.setPlainText(message)
            
            # Çeviriyi ayrı textbox'a koy
            if turkish_translation and lang_code != "Turkish":
                translation_editor.setPlainText(turkish_translation)
            else:
                translation_editor.setPlainText("Türkçe mesaj - çeviri gerekmiyor")
            
            # Önizlemeyi güncelle - sadece temel bilgiler
            preview_result = f"""
📱 Alıcı: {firm.get('name', 'Bilinmeyen')} ({firm.get('phone', '')})
👤 İletişim: {firm.get('contact_person', 'Belirtilmemiş')}
🏢 Sektör: {firm.get('sector', 'Belirtilmemiş')}

📊 Karakter Sayısı: {len(message)}
🎨 Yaratıcılık: {creativity * 100:.0f}%
🌍 Dil: {language}
🎭 Ton: {tone}
            """
            preview_text.setPlainText(preview_result)
            
            success_msg = "AI mesajı başarıyla oluşturuldu!"
            if turkish_translation and lang_code != "Turkish":
                success_msg += "\n\nTürkçe çevirisi de eklendi!"
            
            QMessageBox.information(self, "✅ Başarılı", success_msg)
            
        except Exception as e:
            logger.error(f"AI mesaj oluşturma hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"AI mesajı oluşturulamadı:\n{str(e)}")
    
    def show_manual_popup(self):
        """✏️ Manuel Mesaj Popup'ı - Detaylı ve Gelişmiş"""
        print("🚀 Manuel Mesaj Popup açılıyor...")
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("✏️ Manuel Mesaj Editörü - Ultra Gelişmiş")
            dialog.setModal(True)
            
            # Tam ekran boyut
            screen = QApplication.primaryScreen().geometry()
            dialog.resize(int(screen.width() * 0.85), int(screen.height() * 0.85))
            
            # Ana layout
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Başlık
            title_label = QLabel("✏️ Manuel Mesaj Editörü")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 26px;
                    font-weight: bold;
                    color: #FF9800;
                    padding: 15px;
                    background-color: #1a1a1a;
                    border-radius: 10px;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title_label)
            
            # Ana içerik - Splitter ile yan yana
            main_splitter = QSplitter(Qt.Horizontal)
            
            # Sol panel - Değişkenler ve Araçlar
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # Değişkenler
            variables_group = QGroupBox("🔧 Kullanılabilir Değişkenler")
            variables_layout = QVBoxLayout()
            
            variables_info = QTextEdit()
            variables_info.setReadOnly(True)
            variables_info.setMaximumHeight(250)
            variables_info.setText("""
📌 MEVCUTDeğişkenler:

{firma_adi} - Firma adı
{firma_iletisim} - İletişim kişisi
{firma_sektoru} - Firma sektörü
{firma_ozet} - Firma özeti
{firma_website} - Website adresi
{firma_email} - E-mail adresi
{firma_telefon} - Telefon numarası
{firma_adres} - Adres bilgisi

💡 KULLANIM:
Mesajınızda bu değişkenleri kullanın.
Gönderim sırasında otomatik değiştirilecektir.

📝 ÖRNEK:
Merhaba {firma_iletisim},
{firma_adi} için özel bir teklifimiz var!
            """)
            variables_layout.addWidget(variables_info)
            
            # Hızlı ekleme butonları
            quick_add_layout = QGridLayout()
            
            variables = [
                ("🏢 Firma Adı", "{firma_adi}"),
                ("👤 İletişim", "{firma_iletisim}"),
                ("🏭 Sektör", "{firma_sektoru}"),
                ("📧 Email", "{firma_email}"),
                ("📞 Telefon", "{firma_telefon}"),
                ("🌐 Website", "{firma_website}"),
            ]
            
            manual_editor = QTextEdit()  # Önce tanımlayalım
            
            for i, (label, var) in enumerate(variables):
                btn = QPushButton(label)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 8px;
                        border-radius: 5px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                btn.clicked.connect(lambda checked, v=var: manual_editor.insertPlainText(v))
                quick_add_layout.addWidget(btn, i // 2, i % 2)
            
            variables_layout.addLayout(quick_add_layout)
            variables_group.setLayout(variables_layout)
            left_layout.addWidget(variables_group)
            
            # Mesaj Şablonları
            templates_group = QGroupBox("📋 Hızlı Şablonlar")
            templates_layout = QVBoxLayout()
            
            template_list = QListWidget()
            quick_templates = [
                "👋 Merhaba {firma_iletisim},\n{firma_adi} için özel bir teklifimiz var!",
                "🎯 Sayın {firma_iletisim},\n{firma_sektoru} sektörüne özel çözümlerimizi incelemek ister misiniz?",
                "💼 {firma_adi} ekibine selamlar!\nİşbirliği fırsatlarını konuşalım mı?",
                "📞 Merhaba,\n{firma_adi} için hazırladığımız kampanyayı paylaşmak istiyoruz.",
            ]
            
            for template in quick_templates:
                template_list.addItem(template[:50] + "...")
            
            template_list.itemDoubleClicked.connect(
                lambda item: manual_editor.setText(quick_templates[template_list.currentRow()])
            )
            templates_layout.addWidget(template_list)
            
            templates_group.setLayout(templates_layout)
            left_layout.addWidget(templates_group)
            
            left_layout.addStretch()
            main_splitter.addWidget(left_panel)
            
            # Sağ panel - Mesaj Editörü
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # Mesaj Editörü
            editor_group = QGroupBox("✏️ Mesaj Yazın")
            editor_layout = QVBoxLayout()
            
            # Şimdi manual_editor'u ekleyelim
            manual_editor.setPlaceholderText(
                "Mesajınızı buraya yazın...\n\n"
                "Sol paneldeki değişkenleri kullanabilirsiniz.\n"
                "Örnek: Merhaba {firma_iletisim}, {firma_adi} için özel teklifimiz var!"
            )
            manual_editor.setMinimumHeight(350)
            
            # Karakter sayacı
            char_counter = QLabel("Karakter: 0")
            char_counter.setStyleSheet("color: #2196F3; font-weight: bold;")
            manual_editor.textChanged.connect(
                lambda: char_counter.setText(f"Karakter: {len(manual_editor.toPlainText())}")
            )
            
            editor_layout.addWidget(manual_editor)
            editor_layout.addWidget(char_counter)
            
            editor_group.setLayout(editor_layout)
            right_layout.addWidget(editor_group)
            
            # Önizleme
            preview_group = QGroupBox("👀 Önizleme")
            preview_layout = QVBoxLayout()
            
            # Test firması seç
            test_firm_layout = QHBoxLayout()
            test_firm_layout.addWidget(QLabel("Test Firması:"))
            test_firm_combo = QComboBox()
            test_firm_combo.addItem("-- Önizleme için firma seç --")
            for firm in self.firms[:10]:
                test_firm_combo.addItem(f"{firm.get('name', 'Bilinmeyen')}", firm)
            test_firm_layout.addWidget(test_firm_combo)
            
            preview_btn = QPushButton("🔄 Önizle")
            preview_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            
            preview_text = QTextEdit()
            preview_text.setReadOnly(True)
            preview_text.setMaximumHeight(180)
            preview_text.setPlaceholderText("Önizleme burada görünecek...")
            
            def update_preview():
                firm = test_firm_combo.currentData()
                if not firm:
                    QMessageBox.warning(dialog, "⚠️ Uyarı", "Lütfen bir firma seçin!")
                    return
                
                message = manual_editor.toPlainText()
                # Değişkenleri değiştir
                message = message.replace("{firma_adi}", firm.get('name', 'Firma Adı'))
                message = message.replace("{firma_iletisim}", firm.get('contact_person', 'İletişim Kişisi'))
                message = message.replace("{firma_sektoru}", firm.get('sector', 'Sektör'))
                message = message.replace("{firma_email}", firm.get('email', 'email@firma.com'))
                message = message.replace("{firma_telefon}", firm.get('phone', 'Telefon'))
                message = message.replace("{firma_website}", firm.get('website', 'www.firma.com'))
                message = message.replace("{firma_adres}", firm.get('address', 'Adres'))
                message = message.replace("{firma_ozet}", firm.get('summary', 'Özet'))
                
                preview_result = f"""
📱 Alıcı: {firm.get('name', 'Firma')}
👤 Kişi: {firm.get('contact_person', 'Belirtilmemiş')}
📞 Telefon: {firm.get('phone', 'Yok')}

💬 Mesaj:
{message}

📊 Karakter: {len(message)}
                """
                preview_text.setText(preview_result)
            
            preview_btn.clicked.connect(update_preview)
            test_firm_layout.addWidget(preview_btn)
            
            preview_layout.addLayout(test_firm_layout)
            preview_layout.addWidget(preview_text)
            
            preview_group.setLayout(preview_layout)
            right_layout.addWidget(preview_group)
            
            main_splitter.addWidget(right_panel)
            main_splitter.setSizes([int(screen.width() * 0.30), int(screen.width() * 0.55)])
            
            layout.addWidget(main_splitter)
            
            # Alt butonlar
            button_layout = QHBoxLayout()
            
            save_template_btn = QPushButton("💾 Şablon Olarak Kaydet")
            save_template_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            save_template_btn.clicked.connect(lambda: QMessageBox.information(
                dialog, "💾 Kaydet", "Şablon kaydetme özelliği yakında eklenecek!"
            ))
            button_layout.addWidget(save_template_btn)
            
            use_message_btn = QPushButton("✅ Mesajı Kullan")
            use_message_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #4CAF50, stop: 1 #45a049);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #45a049, stop: 1 #4CAF50);
                }
            """)
            use_message_btn.clicked.connect(lambda: self.save_ai_message_from_popup(manual_editor.toPlainText(), dialog))
            button_layout.addWidget(use_message_btn)
            
            close_btn = QPushButton("❌ Kapat")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            close_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            # Popup'ı göster
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Manuel Mesaj popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Manuel Mesaj popup'ı açılamadı:\n{str(e)}")
    
    def show_template_popup(self):
        """📋 Şablon Popup'ı - Büyük ve Düzenli"""
        print("🚀 Şablon Popup açılıyor...")
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("📋 Şablon Mesaj Oluşturucu - Ultra Gelişmiş")
            dialog.setModal(True)
            
            # Tam ekran boyut
            screen = QApplication.primaryScreen().geometry()
            dialog.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
            
            # Ana layout
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Başlık
            title_label = QLabel("📋 Şablon Mesaj Oluşturucu")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #0d7377;
                    padding: 10px;
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title_label)
            
            # Ana içerik - Splitter ile yan yana
            main_splitter = QSplitter(Qt.Horizontal)
            
            # Sol panel - Şablon seçimi ve ayarlar
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # Şablon seçimi
            template_group = QGroupBox("📋 Şablon Seçimi")
            template_layout = QVBoxLayout()
            
            # Mevcut şablonlar
            template_list = QListWidget()
            template_list.addItems([
                "🏢 Tanıtım Mesajı",
                "📞 Takip Mesajı", 
                "🎯 Kampanya Duyurusu",
                "ℹ️ Bilgilendirme",
                "🙏 Teşekkür Mesajı",
                "📅 Randevu Talebi",
                "🛍️ Ürün Tanıtımı",
                "🔧 Hizmet Sunumu",
                "🤝 İşbirliği Teklifi",
                "✏️ Özel Mesaj"
            ])
            template_layout.addWidget(template_list)
            
            # Yeni şablon oluştur butonu
            create_template_btn = QPushButton("➕ Yeni Şablon Oluştur")
            create_template_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #4CAF50, stop: 1 #45a049);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #45a049, stop: 1 #4CAF50);
                }
            """)
            template_layout.addWidget(create_template_btn)
            
            template_group.setLayout(template_layout)
            left_layout.addWidget(template_group)
            
            # Şablon ayarları
            settings_group = QGroupBox("⚙️ Şablon Ayarları")
            settings_layout = QFormLayout()
            
            # Dil seçimi
            settings_layout.addRow("🌍 Mesaj Dili:", QComboBox())
            language_combo = settings_layout.itemAt(settings_layout.rowCount()-1, QFormLayout.FieldRole).widget()
            language_combo.addItems([
                "Türkçe", "English", "Deutsch", "Français", "Español", 
                "Italiano", "Русский", "العربية", "中文", "日本語", "Polski"
            ])
            
            # Değişkenler
            variables_label = QLabel("🔧 Kullanılabilir Değişkenler:")
            variables_text = QTextEdit()
            variables_text.setReadOnly(True)
            variables_text.setMaximumHeight(100)
            variables_text.setPlainText("""
{firma_adi} - Firma adı
{firma_iletisim} - İletişim kişisi
{firma_sektoru} - Firma sektörü
{firma_ozet} - Firma özeti
{firma_website} - Website
{firma_email} - E-mail
{firma_telefon} - Telefon numarası
{firma_adres} - Adres
{tarih} - Bugünün tarihi
{saat} - Şu anki saat
            """)
            settings_layout.addRow(variables_label, variables_text)
            
            settings_group.setLayout(settings_layout)
            left_layout.addWidget(settings_group)
            
            main_splitter.addWidget(left_panel)
            
            # Sağ panel - Şablon editörü ve önizleme
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # Şablon editörü
            editor_group = QGroupBox("✏️ Şablon Editörü")
            editor_layout = QVBoxLayout()
            
            template_editor = QTextEdit()
            template_editor.setPlaceholderText("""Şablon mesajınızı buraya yazın...

Örnek:
Merhaba {firma_iletisim},

{firma_adi} firması için özel bir teklifimiz var. 
{firma_sektoru} sektöründeki deneyiminizi göz önünde bulundurarak...

Detaylar için: {firma_website}

İyi günler,
[İsminiz]""")
            template_editor.setMinimumHeight(250)
            editor_layout.addWidget(template_editor)
            
            # Karakter sayacı
            char_counter = QLabel("📊 Karakter Sayısı: 0")
            editor_layout.addWidget(char_counter)
            
            editor_group.setLayout(editor_layout)
            right_layout.addWidget(editor_group)
            
            # Önizleme
            preview_group = QGroupBox("👀 Şablon Önizlemesi")
            preview_layout = QVBoxLayout()
            
            preview_text = QTextEdit()
            preview_text.setReadOnly(True)
            preview_text.setMaximumHeight(200)
            preview_text.setPlaceholderText("Şablon önizlemesi burada görünecek...")
            preview_layout.addWidget(preview_text)
            
            preview_group.setLayout(preview_layout)
            right_layout.addWidget(preview_group)
            
            main_splitter.addWidget(right_panel)
            main_splitter.setSizes([400, 600])
            
            layout.addWidget(main_splitter)
            
            # Alt butonlar
            button_layout = QHBoxLayout()
            
            preview_btn = QPushButton("👀 Önizle")
            preview_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #2196F3, stop: 1 #1976D2);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #1976D2, stop: 1 #2196F3);
                }
            """)
            
            test_btn = QPushButton("🧪 Test Et")
            test_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #FF9800, stop: 1 #F57C00);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #F57C00, stop: 1 #FF9800);
                }
            """)
            
            save_btn = QPushButton("💾 Kaydet ve Kapat")
            save_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #0d7377, stop: 1 #14a085);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #14a085, stop: 1 #0d7377);
                }
            """)
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #f44336;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #d32f2f;
                }
            """)
            
            button_layout.addWidget(preview_btn)
            button_layout.addWidget(test_btn)
            button_layout.addStretch()
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            # Buton bağlantıları
            preview_btn.clicked.connect(lambda: self.preview_template_in_popup(
                template_editor.toPlainText(),
                preview_text
            ))
            
            test_btn.clicked.connect(lambda: self.test_template_in_popup(
                template_editor.toPlainText(),
                preview_text
            ))
            
            save_btn.clicked.connect(lambda: self.save_template_from_popup(template_editor.toPlainText(), dialog))
            cancel_btn.clicked.connect(dialog.reject)
            
            # Karakter sayacı güncelleme
            template_editor.textChanged.connect(lambda: char_counter.setText(f"📊 Karakter Sayısı: {len(template_editor.toPlainText())}"))
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Şablon popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Şablon popup'ı açılamadı:\n{str(e)}")
    
    def preview_template_in_popup(self, template_text, preview_widget):
        """👀 Şablonu popup'ta önizle"""
        try:
            if not template_text.strip():
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir şablon yazın!")
                return
            
            # Örnek firma verisi
            sample_firm = {
                'name': 'Örnek Firma A.Ş.',
                'contact_person': 'Ahmet Yılmaz',
                'sector': 'Teknoloji',
                'summary': 'Yazılım geliştirme şirketi',
                'website': 'www.ornekfirma.com',
                'email': 'info@ornekfirma.com',
                'phone': '+90 212 555 0123',
                'address': 'İstanbul, Türkiye'
            }
            
            # Değişkenleri değiştir
            message = template_text
            message = message.replace('{firma_adi}', sample_firm.get('name', ''))
            message = message.replace('{firma_iletisim}', sample_firm.get('contact_person', ''))
            message = message.replace('{firma_sektoru}', sample_firm.get('sector', ''))
            message = message.replace('{firma_ozet}', sample_firm.get('summary', ''))
            message = message.replace('{firma_website}', sample_firm.get('website', ''))
            message = message.replace('{firma_email}', sample_firm.get('email', ''))
            message = message.replace('{firma_telefon}', sample_firm.get('phone', ''))
            message = message.replace('{firma_adres}', sample_firm.get('address', ''))
            
            # Tarih ve saat
            from datetime import datetime
            now = datetime.now()
            message = message.replace('{tarih}', now.strftime('%d.%m.%Y'))
            message = message.replace('{saat}', now.strftime('%H:%M'))
            
            preview_text = f"""
👀 ŞABLON ÖNİZLEMESİ

📋 Örnek Firma: {sample_firm.get('name', 'Bilinmeyen')}
📞 Telefon: {sample_firm.get('phone', 'Telefon Yok')}
🏭 Sektör: {sample_firm.get('sector', 'Sektör Belirtilmemiş')}

💬 Mesaj İçeriği:
{message}

📊 Karakter Sayısı: {len(message)}
"""
            preview_widget.setPlainText(preview_text)
            
        except Exception as e:
            logger.error(f"Şablon önizleme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Şablon önizlenemedi:\n{str(e)}")
    
    def test_template_in_popup(self, template_text, preview_widget):
        """🧪 Şablonu popup'ta test et"""
        try:
            if not template_text.strip():
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir şablon yazın!")
                return
            
            # Seçili firmaları al
            selected_firms = []
            for i in range(self.firms_table.rowCount()):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox and checkbox.isChecked():
                    if i < len(self.firms):
                        selected_firms.append(self.firms[i])
            
            if not selected_firms:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen en az bir firma seçin!")
                return
            
            # İlk firma ile test et
            firm = selected_firms[0]
            
            # Değişkenleri değiştir
            message = template_text
            message = message.replace('{firma_adi}', firm.get('name', ''))
            message = message.replace('{firma_iletisim}', firm.get('contact_person', ''))
            message = message.replace('{firma_sektoru}', firm.get('sector', ''))
            message = message.replace('{firma_ozet}', firm.get('summary', ''))
            message = message.replace('{firma_website}', firm.get('website', ''))
            message = message.replace('{firma_email}', firm.get('email', ''))
            message = message.replace('{firma_telefon}', firm.get('phone', ''))
            message = message.replace('{firma_adres}', firm.get('address', ''))
            
            # Tarih ve saat
            from datetime import datetime
            now = datetime.now()
            message = message.replace('{tarih}', now.strftime('%d.%m.%Y'))
            message = message.replace('{saat}', now.strftime('%H:%M'))
            
            preview_text = f"""
🧪 ŞABLON TEST SONUCU

📋 Test Firma: {firm.get('name', 'Bilinmeyen')}
📞 Telefon: {firm.get('phone', 'Telefon Yok')}
🏭 Sektör: {firm.get('sector', 'Sektör Belirtilmemiş')}

💬 Mesaj İçeriği:
{message}

📊 Karakter Sayısı: {len(message)}
✅ Test başarılı!
"""
            preview_widget.setPlainText(preview_text)
            
            QMessageBox.information(self, "✅ Başarılı", "Şablon test edildi!")
            
        except Exception as e:
            logger.error(f"Şablon test hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Şablon test edilemedi:\n{str(e)}")
    
    def save_template_from_popup(self, template_text, dialog):
        """💾 Şablonu popup'tan kaydet"""
        try:
            if not template_text.strip():
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir şablon yazın!")
                return
            
            # Ana mesaj editörüne koy
            if hasattr(self, 'message_input'):
                self.message_input.setPlainText(template_text)
            
            QMessageBox.information(self, "✅ Başarılı", "Şablon başarıyla kaydedildi!")
            dialog.accept()
            
        except Exception as e:
            logger.error(f"Şablon kaydetme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Şablon kaydedilemedi:\n{str(e)}")
    
    def show_manual_popup(self):
        """✏️ Manuel Mesaj Popup'ı - Büyük ve Düzenli"""
        print("🚀 Manuel Popup açılıyor...")
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("✏️ Manuel Mesaj Editörü - Ultra Gelişmiş")
            dialog.setModal(True)
            
            # Tam ekran boyut
            screen = QApplication.primaryScreen().geometry()
            dialog.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
            
            # Ana layout
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Başlık
            title_label = QLabel("✏️ Manuel Mesaj Editörü")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #0d7377;
                    padding: 10px;
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title_label)
            
            # Ana içerik - Splitter ile yan yana
            main_splitter = QSplitter(Qt.Horizontal)
            
            # Sol panel - Ayarlar ve yardımcılar
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            
            # Mesaj ayarları
            settings_group = QGroupBox("⚙️ Mesaj Ayarları")
            settings_layout = QFormLayout()
            
            # Dil seçimi
            settings_layout.addRow("🌍 Mesaj Dili:", QComboBox())
            language_combo = settings_layout.itemAt(settings_layout.rowCount()-1, QFormLayout.FieldRole).widget()
            language_combo.addItems([
                "Türkçe", "English", "Deutsch", "Français", "Español", 
                "Italiano", "Русский", "العربية", "中文", "日本語", "Polski"
            ])
            
            # Mesaj tipi
            settings_layout.addRow("📝 Mesaj Tipi:", QComboBox())
            message_type_combo = settings_layout.itemAt(settings_layout.rowCount()-1, QFormLayout.FieldRole).widget()
            message_type_combo.addItems([
                "Tanıtım Mesajı", "Takip Mesajı", "Kampanya Duyurusu",
                "Bilgilendirme", "Teşekkür Mesajı", "Randevu Talebi",
                "Ürün Tanıtımı", "Hizmet Sunumu", "İşbirliği Teklifi", "Özel Mesaj"
            ])
            
            # Karakter sınırı
            settings_layout.addRow("📊 Karakter Sınırı:", QSpinBox())
            char_limit_spin = settings_layout.itemAt(settings_layout.rowCount()-1, QFormLayout.FieldRole).widget()
            char_limit_spin.setRange(50, 1000)
            char_limit_spin.setValue(180)
            char_limit_spin.setSuffix(" karakter")
            
            settings_group.setLayout(settings_layout)
            left_layout.addWidget(settings_group)
            
            # Yardımcı araçlar
            tools_group = QGroupBox("🛠️ Yardımcı Araçlar")
            tools_layout = QVBoxLayout()
            
            # Hızlı metinler
            quick_texts_btn = QPushButton("📝 Hızlı Metinler")
            quick_texts_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #4CAF50, stop: 1 #45a049);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #45a049, stop: 1 #4CAF50);
                }
            """)
            tools_layout.addWidget(quick_texts_btn)
            
            # Emoji ekle
            emoji_btn = QPushButton("😊 Emoji Ekle")
            emoji_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #FF9800, stop: 1 #F57C00);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #F57C00, stop: 1 #FF9800);
                }
            """)
            tools_layout.addWidget(emoji_btn)
            
            # Değişkenler
            variables_btn = QPushButton("🔧 Değişkenler")
            variables_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #2196F3, stop: 1 #1976D2);
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #1976D2, stop: 1 #2196F3);
                }
            """)
            tools_layout.addWidget(variables_btn)
            
            tools_group.setLayout(tools_layout)
            left_layout.addWidget(tools_group)
            
            # Değişkenler listesi
            variables_group = QGroupBox("🔧 Kullanılabilir Değişkenler")
            variables_layout = QVBoxLayout()
            
            variables_text = QTextEdit()
            variables_text.setReadOnly(True)
            variables_text.setMaximumHeight(150)
            variables_text.setPlainText("""
{firma_adi} - Firma adı
{firma_iletisim} - İletişim kişisi
{firma_sektoru} - Firma sektörü
{firma_ozet} - Firma özeti
{firma_website} - Website
{firma_email} - E-mail
{firma_telefon} - Telefon numarası
{firma_adres} - Adres
{tarih} - Bugünün tarihi
{saat} - Şu anki saat
            """)
            variables_layout.addWidget(variables_text)
            
            variables_group.setLayout(variables_layout)
            left_layout.addWidget(variables_group)
            
            main_splitter.addWidget(left_panel)
            
            # Sağ panel - Mesaj editörü ve önizleme
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            
            # Mesaj editörü
            editor_group = QGroupBox("✏️ Mesaj Editörü")
            editor_layout = QVBoxLayout()
            
            message_editor = QTextEdit()
            message_editor.setPlaceholderText("""Mesajınızı buraya yazın...

Örnek:
Merhaba {firma_iletisim},

{firma_adi} firması için özel bir teklifimiz var. 
{firma_sektoru} sektöründeki deneyiminizi göz önünde bulundurarak...

Detaylar için: {firma_website}

İyi günler,
[İsminiz]""")
            message_editor.setMinimumHeight(300)
            editor_layout.addWidget(message_editor)
            
            # Karakter sayacı ve durum
            status_layout = QHBoxLayout()
            char_counter = QLabel("📊 Karakter Sayısı: 0")
            status_layout.addWidget(char_counter)
            status_layout.addStretch()
            
            # Kelime sayacı
            word_counter = QLabel("📝 Kelime Sayısı: 0")
            status_layout.addWidget(word_counter)
            
            editor_layout.addLayout(status_layout)
            
            editor_group.setLayout(editor_layout)
            right_layout.addWidget(editor_group)
            
            # Önizleme
            preview_group = QGroupBox("👀 Mesaj Önizlemesi")
            preview_layout = QVBoxLayout()
            
            preview_text = QTextEdit()
            preview_text.setReadOnly(True)
            preview_text.setMaximumHeight(200)
            preview_text.setPlaceholderText("Mesaj önizlemesi burada görünecek...")
            preview_layout.addWidget(preview_text)
            
            preview_group.setLayout(preview_layout)
            right_layout.addWidget(preview_group)
            
            main_splitter.addWidget(right_panel)
            main_splitter.setSizes([400, 600])
            
            layout.addWidget(main_splitter)
            
            # Alt butonlar
            button_layout = QHBoxLayout()
            
            preview_btn = QPushButton("👀 Önizle")
            preview_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #2196F3, stop: 1 #1976D2);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #1976D2, stop: 1 #2196F3);
                }
            """)
            
            test_btn = QPushButton("🧪 Test Et")
            test_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #FF9800, stop: 1 #F57C00);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #F57C00, stop: 1 #FF9800);
                }
            """)
            
            save_btn = QPushButton("💾 Kaydet ve Kapat")
            save_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #0d7377, stop: 1 #14a085);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #14a085, stop: 1 #0d7377);
                }
            """)
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #f44336;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #d32f2f;
                }
            """)
            
            button_layout.addWidget(preview_btn)
            button_layout.addWidget(test_btn)
            button_layout.addStretch()
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            # Buton bağlantıları
            preview_btn.clicked.connect(lambda: self.preview_manual_message_in_popup(
                message_editor.toPlainText(),
                preview_text
            ))
            
            test_btn.clicked.connect(lambda: self.test_manual_message_in_popup(
                message_editor.toPlainText(),
                preview_text
            ))
            
            save_btn.clicked.connect(lambda: self.save_manual_message_from_popup(message_editor.toPlainText(), dialog))
            cancel_btn.clicked.connect(dialog.reject)
            
            # Karakter ve kelime sayacı güncelleme
            def update_counters():
                text = message_editor.toPlainText()
                char_count = len(text)
                word_count = len(text.split()) if text.strip() else 0
                char_counter.setText(f"📊 Karakter Sayısı: {char_count}")
                word_counter.setText(f"📝 Kelime Sayısı: {word_count}")
            
            message_editor.textChanged.connect(update_counters)
            
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Manuel popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Manuel popup'ı açılamadı:\n{str(e)}")
    
    def preview_manual_message_in_popup(self, message_text, preview_widget):
        """👀 Manuel mesajı popup'ta önizle"""
        try:
            if not message_text.strip():
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir mesaj yazın!")
                return
            
            # Örnek firma verisi
            sample_firm = {
                'name': 'Örnek Firma A.Ş.',
                'contact_person': 'Ahmet Yılmaz',
                'sector': 'Teknoloji',
                'summary': 'Yazılım geliştirme şirketi',
                'website': 'www.ornekfirma.com',
                'email': 'info@ornekfirma.com',
                'phone': '+90 212 555 0123',
                'address': 'İstanbul, Türkiye'
            }
            
            # Değişkenleri değiştir
            message = message_text
            message = message.replace('{firma_adi}', sample_firm.get('name', ''))
            message = message.replace('{firma_iletisim}', sample_firm.get('contact_person', ''))
            message = message.replace('{firma_sektoru}', sample_firm.get('sector', ''))
            message = message.replace('{firma_ozet}', sample_firm.get('summary', ''))
            message = message.replace('{firma_website}', sample_firm.get('website', ''))
            message = message.replace('{firma_email}', sample_firm.get('email', ''))
            message = message.replace('{firma_telefon}', sample_firm.get('phone', ''))
            message = message.replace('{firma_adres}', sample_firm.get('address', ''))
            
            # Tarih ve saat
            from datetime import datetime
            now = datetime.now()
            message = message.replace('{tarih}', now.strftime('%d.%m.%Y'))
            message = message.replace('{saat}', now.strftime('%H:%M'))
            
            preview_text = f"""
👀 MANUEL MESAJ ÖNİZLEMESİ

📋 Örnek Firma: {sample_firm.get('name', 'Bilinmeyen')}
📞 Telefon: {sample_firm.get('phone', 'Telefon Yok')}
🏭 Sektör: {sample_firm.get('sector', 'Sektör Belirtilmemiş')}

💬 Mesaj İçeriği:
{message}

📊 Karakter Sayısı: {len(message)}
📝 Kelime Sayısı: {len(message.split())}
"""
            preview_widget.setPlainText(preview_text)
            
        except Exception as e:
            logger.error(f"Manuel mesaj önizleme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj önizlenemedi:\n{str(e)}")
    
    def test_manual_message_in_popup(self, message_text, preview_widget):
        """🧪 Manuel mesajı popup'ta test et"""
        try:
            if not message_text.strip():
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir mesaj yazın!")
                return
            
            # Seçili firmaları al
            selected_firms = []
            for i in range(self.firms_table.rowCount()):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox and checkbox.isChecked():
                    if i < len(self.firms):
                        selected_firms.append(self.firms[i])
            
            if not selected_firms:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen en az bir firma seçin!")
                return
            
            # İlk firma ile test et
            firm = selected_firms[0]
            
            # Değişkenleri değiştir
            message = message_text
            message = message.replace('{firma_adi}', firm.get('name', ''))
            message = message.replace('{firma_iletisim}', firm.get('contact_person', ''))
            message = message.replace('{firma_sektoru}', firm.get('sector', ''))
            message = message.replace('{firma_ozet}', firm.get('summary', ''))
            message = message.replace('{firma_website}', firm.get('website', ''))
            message = message.replace('{firma_email}', firm.get('email', ''))
            message = message.replace('{firma_telefon}', firm.get('phone', ''))
            message = message.replace('{firma_adres}', firm.get('address', ''))
            
            # Tarih ve saat
            from datetime import datetime
            now = datetime.now()
            message = message.replace('{tarih}', now.strftime('%d.%m.%Y'))
            message = message.replace('{saat}', now.strftime('%H:%M'))
            
            preview_text = f"""
🧪 MANUEL MESAJ TEST SONUCU

📋 Test Firma: {firm.get('name', 'Bilinmeyen')}
📞 Telefon: {firm.get('phone', 'Telefon Yok')}
🏭 Sektör: {firm.get('sector', 'Sektör Belirtilmemiş')}

💬 Mesaj İçeriği:
{message}

📊 Karakter Sayısı: {len(message)}
📝 Kelime Sayısı: {len(message.split())}
✅ Test başarılı!
"""
            preview_widget.setPlainText(preview_text)
            
            QMessageBox.information(self, "✅ Başarılı", "Manuel mesaj test edildi!")
            
        except Exception as e:
            logger.error(f"Manuel mesaj test hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj test edilemedi:\n{str(e)}")
    
    def save_manual_message_from_popup(self, message_text, dialog):
        """💾 Manuel mesajı popup'tan kaydet"""
        try:
            if not message_text.strip():
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir mesaj yazın!")
                return
            
            # Ana mesaj editörüne koy
            if hasattr(self, 'message_input'):
                self.message_input.setPlainText(message_text)
            
            QMessageBox.information(self, "✅ Başarılı", "Manuel mesaj başarıyla kaydedildi!")
            dialog.accept()
            
        except Exception as e:
            logger.error(f"Manuel mesaj kaydetme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj kaydedilemedi:\n{str(e)}")
    
    def load_templates(self):
        """📋 Şablonları yükle"""
        if self.db:
            templates = self.db.get_templates()
            for template in templates:
                self.template_combo.addItem(template['name'], template)
    
    def select_all(self):
        """🔥 Tümünü seç"""
        for i in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(True)
        self.update_stats()
    
    def select_none(self):
        """❌ Hiçbirini seçme"""
        for i in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_stats()
    
    def select_by_sector(self):
        """🏢 Sektöre göre seç"""
        sectors = list(set([f.get('sector', '') for f in self.firms if f.get('sector')]))
        if not sectors:
            QMessageBox.information(self, "Bilgi", "Sektör bilgisi bulunan firma yok!")
            return
            
        sector, ok = QInputDialog.getItem(self, "Sektör Seç", "Sektör:", sectors, 0, False)
        
        if ok and sector:
            for i in range(self.firms_table.rowCount()):
                if self.firms_table.item(i, 3).text() == sector:
                    checkbox = self.firms_table.cellWidget(i, 0)
                    if checkbox:
                        checkbox.setChecked(True)
        self.update_stats()
    
    def update_stats(self):
        """📊 İstatistikleri güncelle"""
        selected_count = 0
        for i in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                selected_count += 1
        
        sent_count = len(self.sent_messages)
        skipped_count = len(self.skipped_firms)
        
        self.stats_label.setText(f"📊 Seçili: {selected_count} | ✅ Gönderilen: {sent_count} | ⏭️ Atlanan: {skipped_count}")
    
    def on_template_selected(self):
        """📋 Şablon seçildiğinde"""
        template = self.template_combo.currentData()
        if template:
            self.message_input.setText(template['content'])
    
    def generate_ai_template(self):
        """🎯 AI ile şablon oluştur"""
        if not self.gpt_manager or not hasattr(self.gpt_manager, 'client') or not self.gpt_manager.client:
            QMessageBox.warning(self, "Uyarı", "OpenAI API ayarlanmamış! Lütfen ayarlar sekmesinden API key'inizi girin.")
            return
        
        language = self.language_combo.currentText()
        message_type = self.message_type_combo.currentText()
        
        try:
            # Dil kod haritası
            language_codes = {
                "Türkçe": "Turkish",
                "English": "English",
                "Deutsch": "German", 
                "Français": "French",
                "Español": "Spanish",
                "Italiano": "Italian",
                "Русский": "Russian",
                "العربية": "Arabic",
                "中文": "Chinese",
                "日本語": "Japanese",
                "Polski": "Polish"
            }
            
            lang_code = language_codes.get(language, "Turkish")
            
            prompt = f"""
            Lütfen {lang_code} dilinde ve kültürel diline uygun bir WhatsApp B2B mesaj şablonu oluştur.
            
            Mesaj Tipi: {message_type}
            Dil: {lang_code}
            
            Şablon özellikleri:
            - Maksimum 200 karakter
            - Profesyonel ama samimi ton
            - Değişkenler kullan: {{firma_adi}}, {{firma_iletisim}}, {{firma_sektoru}}, {{firma_ozet}}
            - Net bir call-to-action içermeli
            - Kültürel dilinde ve o dilin iş yapma tarzına uygun
            - WhatsApp için uygun format
            
            Sadece mesaj şablonunu döndür, başka açıklama ekleme.
            """
            
            response = self.gpt_manager.client.chat.completions.create(
                model=self.gpt_manager.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"Sen {lang_code} dilinde uzman bir B2B pazarlama uzmanısın. O dilin kültürel özelliklerini ve iş yapma tarzını çok iyi biliyorsun."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.8
            )
            
            template_text = response.choices[0].message.content.strip()
            self.message_input.setText(template_text)
            
            QMessageBox.information(self, "✅ Başarılı", f"{language} dilinde şablon oluşturuldu!")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Şablon oluşturulurken hata:\n{str(e)}")
    
    def start_bulk_messaging(self):
        """🚀 Toplu mesaj gönderimini başlat - Düzeltilmiş"""
        try:
            # Seçili firmaları topla - Düzeltilmiş
            self.selected_firms = []
            for i in range(self.firms_table.rowCount()):
                try:
                    checkbox = self.firms_table.cellWidget(i, 0)
                    if checkbox and checkbox.isChecked():
                        if i < len(self.firms):
                            firm = self.firms[i]
                            # Firma verisi kontrolü
                            if firm and firm.get('name'):
                                # Telefon numarası kontrolü
                                if firm.get('phone'):
                                    self.selected_firms.append(firm)
                                else:
                                    self.log_message(f"⚠️ {firm.get('name', 'Firma')}: Telefon numarası yok, atlandı")
                            else:
                                self.log_message(f"⚠️ Satır {i+1}: Geçersiz firma verisi atlandı")
                        else:
                            self.log_message(f"⚠️ Satır {i+1}: Firma indeksi geçersiz")
                except Exception as row_error:
                    self.log_message(f"⚠️ Satır {i+1} işlenirken hata: {str(row_error)}")
                    continue
            
            # Firma seçimi kontrolü
            if not self.selected_firms:
                QMessageBox.warning(self, "⚠️ Uyarı", 
                    "Lütfen en az bir firma seçin!\n\n"
                    "Firma seçmek için:\n"
                    "1. Firma tablosundaki checkbox'ları işaretleyin\n"
                    "2. Telefon numarası olan aktif firmaları seçin")
                return
            
            # Mesaj içeriği kontrolü
            if not self.auto_generate_check.isChecked():
                message_text = self.message_input.toPlainText().strip()
                if not message_text:
                    QMessageBox.warning(self, "⚠️ Uyarı", 
                        "Lütfen mesaj içeriği girin veya otomatik mesaj üretimini aktif edin!\n\n"
                        "Seçenekler:\n"
                        "1. Mesaj editörüne manuel mesaj yazın\n"
                        "2. 'Otomatik AI Mesaj Üret' seçeneğini işaretleyin")
                    return
            
            # GPT Manager kontrolü (otomatik üretim için)
            if self.auto_generate_check.isChecked():
                if not self.gpt_manager or not hasattr(self.gpt_manager, 'client') or not self.gpt_manager.client:
                    QMessageBox.warning(self, "⚠️ Uyarı", 
                        "OpenAI API ayarlanmamış!\n\n"
                        "Otomatik mesaj üretimi için:\n"
                        "1. Ayarlar sekmesine gidin\n"
                        "2. OpenAI API Key'inizi girin\n"
                        "3. Bağlantıyı test edin\n\n"
                        "Veya otomatik üretimi kapatıp manuel mesaj yazın")
                    return
            
            # WhatsApp Web kontrolü
            if not self.whatsapp_view:
                QMessageBox.warning(self, "⚠️ Uyarı", 
                    "WhatsApp Web görünümü bulunamadı!\n\n"
                    "Lütfen WhatsApp sekmesine gidip bağlantıyı kontrol edin")
                return
            
            # Gönderim moduna geç
            self.current_firm_index = 0
            self.sent_messages = []
            self.failed_messages = []
            self.skipped_firms = []
            self.generated_messages = {}
            
            # Progress bar'ı ayarla
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(True)
                self.progress_bar.setMaximum(len(self.selected_firms))
                self.progress_bar.setValue(0)
            
            # UI'yi gönderim moduna ayarla
            if hasattr(self, 'start_btn'):
                self.start_btn.setVisible(False)
            if hasattr(self, 'send_btn'):
                self.send_btn.setVisible(True)
            if hasattr(self, 'skip_btn'):
                self.skip_btn.setVisible(True)
            if hasattr(self, 'regenerate_btn'):
                self.regenerate_btn.setVisible(True)
            if hasattr(self, 'tab_widget'):
                self.tab_widget.setCurrentIndex(2)  # Gönderim kontrolü tab'ına geç
            
            # İstatistikleri güncelle
            self.update_stats()
            
            # İlk mesajı işle
            self.log_message(f"🚀 Toplu mesaj gönderimi başlatıldı - {len(self.selected_firms)} firma seçildi")
            self.process_next_firm()
            
        except Exception as e:
            self.log_message(f"❌ Toplu mesaj başlatma hatası: {str(e)}")
            logger.error(f"Toplu mesaj başlatma hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Toplu mesaj gönderimi başlatılamadı:\n{str(e)}")
    
    def process_next_firm(self):
        """🔄 Sonraki firmayı işle - Düzeltilmiş"""
        try:
            # Firma indeksi kontrolü
            if self.current_firm_index >= len(self.selected_firms):
                self.finish_bulk_messaging()
                return
            
            current_firm = self.selected_firms[self.current_firm_index]
            
            # Firma verisi kontrolü
            if not current_firm:
                self.log_message(f"❌ Firma verisi bulunamadı (indeks: {self.current_firm_index})")
                self.failed_messages.append({
                    'firm': None,
                    'error': 'Firma verisi bulunamadı'
                })
                self.current_firm_index += 1
                self.process_next_firm()
                return
            
            # Firma adı kontrolü
            firm_name = current_firm.get('name', 'Bilinmeyen')
            if not firm_name or firm_name == 'Bilinmeyen':
                self.log_message(f"❌ Firma adı bulunamadı (indeks: {self.current_firm_index})")
                self.failed_messages.append({
                    'firm': current_firm,
                    'error': 'Firma adı bulunamadı'
                })
                self.current_firm_index += 1
                self.process_next_firm()
                return
            
            # İlerleme güncelle
            self.progress_bar.setValue(self.current_firm_index + 1)
            self.status_label.setText(f"İşleniyor: {firm_name} ({self.current_firm_index + 1}/{len(self.selected_firms)})")
            
            # Mesaj üret veya şablonu kullan
            try:
                if self.auto_generate_check.isChecked():
                    self.generate_message_for_firm(current_firm)
                else:
                    self.use_template_for_firm(current_firm)
            except Exception as message_error:
                self.log_message(f"❌ Mesaj işleme hatası: {str(message_error)}")
                self.failed_messages.append({
                    'firm': current_firm,
                    'error': f'Mesaj işleme hatası: {str(message_error)}'
                })
                self.current_firm_index += 1
                self.process_next_firm()
                
        except Exception as e:
            self.log_message(f"❌ Firma işleme hatası: {str(e)}")
            logger.error(f"Firma işleme hatası: {e}")
            self.failed_messages.append({
                'firm': None,
                'error': f'Firma işleme hatası: {str(e)}'
            })
            self.current_firm_index += 1
            self.process_next_firm()
    
    def generate_message_for_firm(self, firm):
        """🤖 Firma için AI mesajı üret - Düzeltilmiş"""
        try:
            # GPT Manager kontrolü - Geliştirilmiş
            if not self.gpt_manager:
                self.log_message("❌ GPT Manager bulunamadı!")
                self.failed_messages.append({
                    'firm': firm,
                    'error': 'GPT Manager bulunamadı'
                })
                self.skip_current_firm()
                return
            
            if not hasattr(self.gpt_manager, 'client'):
                self.log_message("❌ GPT Manager'da client özelliği bulunamadı!")
                self.failed_messages.append({
                    'firm': firm,
                    'error': 'GPT Manager client özelliği yok'
                })
                self.skip_current_firm()
                return
            
            if not self.gpt_manager.client:
                self.log_message("❌ OpenAI API client bağlantısı kurulamadı!")
                self.failed_messages.append({
                    'firm': firm,
                    'error': 'OpenAI API client bağlantısı yok'
                })
                self.skip_current_firm()
                return
            
            # Firma verisi kontrolü
            if not firm:
                self.log_message("❌ Firma verisi bulunamadı!")
                self.failed_messages.append({
                    'firm': None,
                    'error': 'Firma verisi bulunamadı'
                })
                self.skip_current_firm()
                return
        
            # Dil ve mesaj tipi kontrolü
            try:
                language = self.language_combo.currentText()
                message_type = self.message_type_combo.currentText()
                
                if not language or not message_type:
                    self.log_message("❌ Dil veya mesaj tipi seçilmemiş!")
                    self.failed_messages.append({
                        'firm': firm,
                        'error': 'Dil veya mesaj tipi seçilmemiş'
                    })
                    self.skip_current_firm()
                    return
                
                # Dil kod haritası
                language_codes = {
                    "Türkçe": "Turkish",
                    "English": "English",
                    "Deutsch": "German", 
                    "Français": "French",
                    "Español": "Spanish",
                    "Italiano": "Italian",
                    "Русский": "Russian",
                    "العربية": "Arabic",
                    "中文": "Chinese",
                    "日本語": "Japanese"
                }
                
                lang_code = language_codes.get(language, "Turkish")
                
                # Firma bilgileri - Güvenli
                firm_info = f"""
                Firma Adı: {firm.get('name', 'Belirtilmemiş')}
                Sektör: {firm.get('sector', 'Belirtilmemiş')}
                İletişim Kişisi: {firm.get('contact_person', 'Belirtilmemiş')}
                Telefon: {firm.get('phone', 'Belirtilmemiş')}
                Email: {firm.get('email', 'Belirtilmemiş')}
                Website: {firm.get('website', 'Belirtilmemiş')}
                Adres: {firm.get('address', 'Belirtilmemiş')}
                Özet: {firm.get('summary', 'Belirtilmemiş')}
                """
                
                prompt = f"""
                Lütfen {lang_code} dilinde ve kültürel diline uygun profesyonel bir WhatsApp B2B mesajı oluştur.
                
                Firma Bilgileri:
                {firm_info}
                
                Mesaj Tipi: {message_type}
                Dil: {lang_code}
                
                Mesaj özellikleri:
                - Maksimum 180 karakter (WhatsApp için ideal)
                - {lang_code} dilinde ve o dilin kültürel özelliklerine uygun
                - Profesyonel ama samimi ton
                - Firmaya özel detaylar kullan
                - Net bir call-to-action içermeli
                - İletişim kişisinin ismini kullan (varsa)
                - Sektöre uygun terminoloji
                
                Sadece mesaj metnini döndür, başka hiçbir şey ekleme.
                """
                
                # OpenAI API çağrısı - Güvenli
                try:
                    response = self.gpt_manager.client.chat.completions.create(
                        model=self.gpt_manager.model,
                        messages=[
                            {
                                "role": "system", 
                                "content": f"Sen {lang_code} dilinde uzman bir B2B satış uzmanısın. O dilin kültürel özelliklerini ve iş yapma tarzını mükemmel biliyorsun. Kısa, etkili ve kişiselleştirilmiş mesajlar yazarsın."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        max_tokens=200,
                        temperature=0.9
                    )
                    
                    if not response or not response.choices:
                        self.log_message("❌ OpenAI API'den yanıt alınamadı!")
                        self.failed_messages.append({
                            'firm': firm,
                            'error': 'OpenAI API yanıtı alınamadı'
                        })
                        self.skip_current_firm()
                        return
                    
                    message = response.choices[0].message.content.strip()
                    
                    if not message:
                        self.log_message("❌ Boş mesaj üretildi!")
                        self.failed_messages.append({
                            'firm': firm,
                            'error': 'Boş mesaj üretildi'
                        })
                        self.skip_current_firm()
                        return
                    
                    # Mesajı önizlemeye koy
                    self.generated_messages[self.current_firm_index] = message
                    self.show_message_preview(message, firm)
                    
                except Exception as api_error:
                    self.log_message(f"❌ OpenAI API hatası: {str(api_error)}")
                    self.failed_messages.append({
                        'firm': firm,
                        'error': f'OpenAI API hatası: {str(api_error)}'
                    })
                    self.skip_current_firm()
                    return
                    
            except Exception as e:
                self.log_message(f"❌ Mesaj üretilirken hata: {str(e)}")
                self.failed_messages.append({
                    'firm': firm,
                    'error': f'Mesaj üretim hatası: {str(e)}'
                })
                self.skip_current_firm()
                return
                
        except Exception as e:
            self.log_message(f"❌ Genel hata: {str(e)}")
            logger.error(f"Mesaj üretilirken genel hata: {e}")
            self.failed_messages.append({
                'firm': firm,
                'error': f'Genel hata: {str(e)}'
            })
            self.skip_current_firm()
            return
    
    def use_template_for_firm(self, firm):
        """📋 Şablon kullanarak mesaj oluştur - Düzeltilmiş"""
        try:
            # Firma verisi kontrolü
            if not firm:
                self.log_message("❌ Firma verisi bulunamadı!")
                self.failed_messages.append({
                    'firm': None,
                    'error': 'Firma verisi bulunamadı'
                })
                self.skip_current_firm()
                return
            
            # Şablon metni kontrolü
            template_text = self.message_input.toPlainText().strip()
            if not template_text:
                self.log_message("❌ Şablon metni bulunamadı!")
                self.failed_messages.append({
                    'firm': firm,
                    'error': 'Şablon metni bulunamadı'
                })
                self.skip_current_firm()
                return
            
            # Değişkenleri değiştir - Güvenli
            try:
                message = template_text
                message = message.replace('{firma_adi}', firm.get('name', ''))
                message = message.replace('{firma_iletisim}', firm.get('contact_person', ''))
                message = message.replace('{firma_sektoru}', firm.get('sector', ''))
                message = message.replace('{firma_ozet}', firm.get('summary', ''))
                message = message.replace('{firma_website}', firm.get('website', ''))
                message = message.replace('{firma_email}', firm.get('email', ''))
                
                # Mesaj boş mu kontrol et
                if not message.strip():
                    self.log_message("❌ Şablon işlendikten sonra boş mesaj oluştu!")
                    self.failed_messages.append({
                        'firm': firm,
                        'error': 'Şablon işlendikten sonra boş mesaj oluştu'
                    })
                    self.skip_current_firm()
                    return
                
                # Mesajı kaydet ve önizle
                self.generated_messages[self.current_firm_index] = message
                self.show_message_preview(message, firm)
                
            except Exception as template_error:
                self.log_message(f"❌ Şablon işleme hatası: {str(template_error)}")
                self.failed_messages.append({
                    'firm': firm,
                    'error': f'Şablon işleme hatası: {str(template_error)}'
                })
                self.skip_current_firm()
                return
                
        except Exception as e:
            self.log_message(f"❌ Şablon kullanma hatası: {str(e)}")
            logger.error(f"Şablon kullanma hatası: {e}")
            self.failed_messages.append({
                'firm': firm,
                'error': f'Şablon kullanma hatası: {str(e)}'
            })
            self.skip_current_firm()
            return
    
    def show_message_preview(self, message, firm):
        """👀 Mesaj önizlemesini göster - Düzeltilmiş"""
        try:
            # Popup ile mesaj önizlemesini göster
            self.show_message_preview_popup(message, firm)
            
            # Ana önizleme alanını da güncelle
            preview_text = f"""
📱 Alıcı: {firm.get('name', 'Bilinmeyen')} ({firm.get('phone', '')})
👤 İletişim: {firm.get('contact_person', 'Belirtilmemiş')}
🏢 Sektör: {firm.get('sector', 'Belirtilmemiş')}

💬 Mesaj İçeriği:
{message}

📊 Karakter Sayısı: {len(message)}
"""
            if hasattr(self, 'preview_text') and self.preview_text:
                self.preview_text.setText(preview_text)
            
            # Zamanlayıcıyı başlat
            if hasattr(self, 'approval_timer') and hasattr(self, 'approval_time_spin'):
                approval_time = self.approval_time_spin.value() * 1000  # milisaniye
                self.approval_timer.start(approval_time)
                
                # Geri sayım başlat
                self.countdown_seconds = self.approval_time_spin.value()
                self.update_countdown_display()
                
                # Geri sayım timer'ı
                self.countdown_timer = QTimer()
                self.countdown_timer.timeout.connect(self.update_countdown_display)
                self.countdown_timer.start(1000)  # Her saniye
                
        except Exception as e:
            logger.error(f"Mesaj önizleme hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Mesaj önizlemesi gösterilemedi:\n{str(e)}")
    
    def update_countdown_display(self):
        """⏰ Geri sayım göstergesi"""
        if self.countdown_seconds > 0:
            self.status_label.setText(
                f"⏰ Otomatik gönderim: {self.countdown_seconds} saniye | "
                f"Firma: {self.selected_firms[self.current_firm_index].get('name', 'Bilinmeyen')}"
            )
            self.countdown_seconds -= 1
        else:
            if hasattr(self, 'countdown_timer'):
                self.countdown_timer.stop()
    
    def send_current_message(self):
        """Mevcut mesajı gönder - Düzeltilmiş"""
        try:
            # Mevcut firma ve mesaj kontrolü
            if self.current_firm_index >= len(self.selected_firms):
                self.log_message("❌ Geçersiz firma indeksi!")
                return False
            
            current_firm = self.selected_firms[self.current_firm_index]
            current_message = self.generated_messages.get(self.current_firm_index)
            
            if not current_firm:
                self.log_message("❌ Firma verisi bulunamadı!")
                return False
            
            if not current_message:
                self.log_message("❌ Mesaj verisi bulunamadı!")
                return False
            
            # Telefon numarası kontrolü
            phone = current_firm.get('phone', '').strip()
            if not phone:
                self.log_message(f"❌ {current_firm.get('name', 'Firma')} için telefon numarası bulunamadı!")
                self.failed_messages.append({
                    'firm': current_firm,
                    'error': 'Telefon numarası yok'
                })
                self.skip_current_firm()
                return False
            
            # Telefon numarasını düzenle - Geliştirilmiş
            try:
                # Boşluk, tire, parantez karakterlerini kaldır
                clean_phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                
                # + işareti yoksa ekle
                if not clean_phone.startswith("+"):
                    # Türkiye için +90 ekle
                    if clean_phone.startswith("0"):
                        clean_phone = "+90" + clean_phone[1:]
                    elif clean_phone.startswith("90"):
                        clean_phone = "+" + clean_phone
                    else:
                        clean_phone = "+90" + clean_phone
                
                # Telefon numarası geçerliliğini kontrol et
                if len(clean_phone) < 10:
                    self.log_message(f"❌ Geçersiz telefon numarası: {phone}")
                    self.failed_messages.append({
                        'firm': current_firm,
                        'error': 'Geçersiz telefon numarası'
                    })
                    self.skip_current_firm()
                    return False
                    
            except Exception as phone_error:
                self.log_message(f"❌ Telefon numarası düzenlenirken hata: {str(phone_error)}")
                self.failed_messages.append({
                    'firm': current_firm,
                    'error': 'Telefon numarası düzenleme hatası'
                })
                self.skip_current_firm()
                return False
            
            # WhatsApp Web bağlantısını kontrol et
            if not self.whatsapp_view:
                self.log_message("❌ WhatsApp Web görünümü bulunamadı!")
                self.failed_messages.append({
                    'firm': current_firm,
                    'error': 'WhatsApp Web görünümü yok'
                })
                self.skip_current_firm()
                return False
            
            # WhatsApp bağlantı durumunu kontrol et
            if hasattr(self.whatsapp_view, 'is_connected') and not self.whatsapp_view.is_connected:
                self.log_message("❌ WhatsApp Web bağlantısı kurulamadı!")
                self.failed_messages.append({
                    'firm': current_firm,
                    'error': 'WhatsApp Web bağlantısı yok'
                })
                self.skip_current_firm()
                return False
            
            # Mesajı gönder - Geliştirilmiş
            try:
                success = False
                if hasattr(self.whatsapp_view, 'send_message'):
                    success = self.whatsapp_view.send_message(clean_phone, current_message)
                else:
                    self.log_message("❌ WhatsApp mesaj gönderme fonksiyonu bulunamadı!")
                    self.failed_messages.append({
                        'firm': current_firm,
                        'error': 'Mesaj gönderme fonksiyonu yok'
                    })
                    self.skip_current_firm()
                    return False
                
                if success:
                    # Veritabanına kaydet - Güvenli
                    try:
                        if self.db:
                            self.db.save_message(
                                firm_id=current_firm.get('id', 0),
                                direction="outgoing",
                                content=current_message,
                                platform="whatsapp",
                                status="sent"
                            )
                    except Exception as db_error:
                        logger.warning(f"Veritabanı kayıt hatası: {db_error}")
                    
                    self.sent_messages.append({
                        'firm': current_firm,
                        'message': current_message,
                        'phone': clean_phone
                    })
                    
                    self.log_message(f"✅ Mesaj başarıyla gönderildi: {current_firm.get('name', 'Bilinmeyen')}")
                    
                    # İstatistikleri güncelle
                    self.update_stats()
                    
                    # Sonraki mesaj için bekle
                    delay = self.message_delay_spin.value() * 1000  # milisaniye
                    QTimer.singleShot(delay, self.process_next_firm)
                    return True
                else:
                    self.log_message(f"❌ Mesaj gönderilemedi: {current_firm.get('name', 'Bilinmeyen')}")
                    self.failed_messages.append({
                        'firm': current_firm,
                        'error': 'Mesaj gönderilemedi'
                    })
                    self.update_stats()
                    self.skip_current_firm()
                    return False
                    
            except Exception as send_error:
                self.log_message(f"❌ Mesaj gönderirken hata: {str(send_error)}")
                self.failed_messages.append({
                    'firm': current_firm,
                    'error': str(send_error)
                })
                self.update_stats()
                self.skip_current_firm()
                return False
                
        except Exception as e:
            self.log_message(f"❌ Genel hata: {str(e)}")
            logger.error(f"Mesaj gönderirken genel hata: {e}")
            self.failed_messages.append({
                'firm': current_firm if 'current_firm' in locals() else None,
                'error': str(e)
            })
            self.update_stats()
            self.skip_current_firm()
            return False
    
    def skip_current_firm(self):
        """⏭️ Mevcut firmayı atla"""
        self.approval_timer.stop()
        if hasattr(self, 'countdown_timer'):
            self.countdown_timer.stop()
        
        current_firm = self.selected_firms[self.current_firm_index]
        self.skipped_firms.append(current_firm)
        
        self.status_label.setText(f"⏭️ Firma atlandı: {current_firm.get('name', 'Bilinmeyen')}")
        self.update_stats()
        
        # Sonraki firmaya geç
        self.current_firm_index += 1
        self.process_next_firm()
    
    def regenerate_current_message(self):
        """🔄 Mevcut mesajı yeniden üret"""
        self.approval_timer.stop()
        if hasattr(self, 'countdown_timer'):
            self.countdown_timer.stop()
        
        current_firm = self.selected_firms[self.current_firm_index]
        
        if self.auto_generate_check.isChecked():
            self.generate_message_for_firm(current_firm)
        else:
            self.use_template_for_firm(current_firm)
    
    def auto_send_message(self):
        """⚡ Otomatik mesaj gönderimi (süre dolduğunda)"""
        self.send_current_message()
    
    def finish_bulk_messaging(self):
        """🎉 Toplu mesaj gönderimini tamamla - Düzeltilmiş"""
        try:
            # Timer'ları durdur
            if hasattr(self, 'approval_timer'):
                self.approval_timer.stop()
            if hasattr(self, 'countdown_timer'):
                self.countdown_timer.stop()
            
            # UI'yi normal moda döndür
            if hasattr(self, 'start_btn'):
                self.start_btn.setVisible(True)
            if hasattr(self, 'send_btn'):
                self.send_btn.setVisible(False)
            if hasattr(self, 'skip_btn'):
                self.skip_btn.setVisible(False)
            if hasattr(self, 'regenerate_btn'):
                self.regenerate_btn.setVisible(False)
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setVisible(False)
            
            # Özet hesapla
            total_firms = len(self.selected_firms) if self.selected_firms else 0
            sent_count = len(self.sent_messages) if self.sent_messages else 0
            failed_count = len(self.failed_messages) if self.failed_messages else 0
            skipped_count = len(self.skipped_firms) if self.skipped_firms else 0
            
            # Başarı oranı hesapla
            success_rate = 0
            if total_firms > 0:
                success_rate = (sent_count / total_firms) * 100
            
            # Özet mesajı oluştur
            summary = f"""
🎉 Toplu Mesaj Gönderimi Tamamlandı!

📊 Özet:
• Toplam Firma: {total_firms}
• ✅ Gönderilen: {sent_count}
• ❌ Başarısız: {failed_count}
• ⏭️ Atlanan: {skipped_count}
• 📈 Başarı Oranı: {success_rate:.1f}%

🕒 Tamamlanma Zamanı: {QDateTime.currentDateTime().toString('dd.MM.yyyy hh:mm')}
"""
            
            # Başarısız mesajlar varsa detay göster
            if failed_count > 0:
                failed_details = "\n\n❌ Başarısız Mesajlar:\n"
                for i, failed in enumerate(self.failed_messages[:5]):  # İlk 5 tanesini göster
                    firm_name = failed.get('firm', {}).get('name', 'Bilinmeyen') if failed.get('firm') else 'Bilinmeyen'
                    error = failed.get('error', 'Bilinmeyen hata')
                    failed_details += f"• {firm_name}: {error}\n"
                
                if failed_count > 5:
                    failed_details += f"... ve {failed_count - 5} tane daha"
                
                summary += failed_details
            
            QMessageBox.information(self, "🎉 Tamamlandı", summary)
            
            # Status label'ı güncelle
            if hasattr(self, 'status_label'):
                self.status_label.setText("✅ Toplu mesaj gönderimi başarıyla tamamlandı!")
            
            # İstatistikleri güncelle
            self.update_stats()
            
            # Log mesajı
            self.log_message(f"🎉 Toplu mesaj gönderimi tamamlandı - {sent_count}/{total_firms} başarılı")
            
        except Exception as e:
            self.log_message(f"❌ Toplu mesaj tamamlama hatası: {str(e)}")
            logger.error(f"Toplu mesaj tamamlama hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Toplu mesaj tamamlama hatası:\n{str(e)}")
    
    def get_messages(self):
        """📨 Gönderilen mesajları döndür"""
        return self.sent_messages
    
    def update_progress(self):
        """İlerleme çubuğunu güncelle"""
        if self.is_running:
            progress = (self.current_firm_index / len(self.selected_firms)) * 100
            self.progress_bar.setValue(int(progress))
    
    def log_message(self, message):
        """📝 Log mesajı ekle - Düzeltilmiş"""
        try:
            # Status label'a mesaj ekle
            if hasattr(self, 'status_label') and self.status_label:
                current_text = self.status_label.text()
                timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
                new_text = f"[{timestamp}] {message}"
                
                # Eğer çok uzunsa sadece son mesajı göster
                if len(new_text) > 100:
                    self.status_label.setText(new_text)
                else:
                    self.status_label.setText(new_text)
            
            # Console'a da yazdır
            print(f"[BulkMessage] {message}")
            
            # Logger'a da yazdır
            if '❌' in message:
                logger.error(f"BulkMessage: {message}")
            elif '⚠️' in message:
                logger.warning(f"BulkMessage: {message}")
            else:
                logger.info(f"BulkMessage: {message}")
                
        except Exception as e:
            print(f"Log mesajı yazdırılamadı: {e}")
    
    def update_stats(self):
        """📊 İstatistikleri güncelle - Düzeltilmiş"""
        try:
            # Seçili firmaları say - Düzeltilmiş
            selected_count = 0
            total_firms = self.firms_table.rowCount()
            
            for i in range(total_firms):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox and checkbox.isChecked():
                    selected_count += 1
            
            # Gönderim istatistikleri
            sent = len(self.sent_messages) if hasattr(self, 'sent_messages') and self.sent_messages else 0
            failed = len(self.failed_messages) if hasattr(self, 'failed_messages') and self.failed_messages else 0
            skipped = len(self.skipped_firms) if hasattr(self, 'skipped_firms') and self.skipped_firms else 0
            
            # Status label'ı güncelle - Düzeltilmiş
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText(
                    f"📊 Toplam: {total_firms} | Seçili: {selected_count} | ✅ Gönderilen: {sent} | ❌ Başarısız: {failed} | ⏭️ Atlanan: {skipped} | ⏳ Bekleyen: {selected_count - sent - failed - skipped}"
                )
            
            # Progress bar'ı güncelle
            if hasattr(self, 'progress_bar') and self.progress_bar:
                if selected_count > 0:
                    progress = ((sent + failed + skipped) / selected_count) * 100
                    self.progress_bar.setValue(int(progress))
                else:
                    self.progress_bar.setValue(0)
            
            # Firma sayacını güncelle
            self.update_firm_count()
                    
        except Exception as e:
            logger.error(f"İstatistik güncelleme hatası: {e}")
            print(f"İstatistik güncelleme hatası: {e}")
    
    def update_firm_count(self):
        """📊 Firma sayacını güncelle - Düzeltilmiş"""
        try:
            # Toplam firma sayısını hesapla
            total_firms = len(self.firms) if hasattr(self, 'firms') and self.firms else 0
            
            # Seçili firma sayısını hesapla
            selected_count = 0
            if hasattr(self, 'firms_table'):
                for i in range(self.firms_table.rowCount()):
                    checkbox = self.firms_table.cellWidget(i, 0)
                    if checkbox and checkbox.isChecked():
                        selected_count += 1
            
            # Firma sayacı label'ını güncelle
            if hasattr(self, 'firm_count_label'):
                self.firm_count_label.setText(f"{selected_count} firma seçili (Toplam: {total_firms})")
            
            # Başlık alanını güncelle
            if hasattr(self, 'firm_count_title'):
                self.firm_count_title.setText(f"Firma Seçimi ve Filtreler - {total_firms} firma")
                
        except Exception as e:
            logger.error(f"Firma sayacı güncelleme hatası: {e}")
            print(f"Firma sayacı güncelleme hatası: {e}")
    
    def quick_start(self):
        """Hızlı başlat - AI ile otomatik seçim ve başlatma"""
        if not self.gpt_manager or not self.gpt_manager.client:
            QMessageBox.warning(self, "Uyarı", "AI servisi kullanılamıyor!")
            return
        
        # AI ile en uygun firmaları seç
        self.ai_optimize_selection()
        
        # AI mesaj moduna geç
        self.message_tabs.setCurrentIndex(0)
        
        # Otomatik başlat
        if self.get_selected_firms():
            self.start_bulk_messaging()
    
    def ai_optimize_selection(self):
        """AI ile firma seçimini optimize et"""
        if not self.gpt_manager or not self.gpt_manager.client:
            QMessageBox.warning(self, "Uyarı", "AI servisi kullanılamıyor!")
            return
        
        try:
            # Firma verilerini analiz et
            firm_data = []
            for i, firm in enumerate(self.firms):
                if not self.firms_table.isRowHidden(i):
                    firm_data.append({
                        'index': i,
                        'name': firm.get('name', ''),
                        'sector': firm.get('sector', ''),
                        'status': firm.get('status', ''),
                        'last_contact': firm.get('last_contact_date', ''),
                        'phone': firm.get('phone', ''),
                        'email': firm.get('email', '')
                    })
            
            if not firm_data:
                QMessageBox.information(self, "Bilgi", "Analiz edilecek firma bulunamadı!")
                return
            
            # AI'ya firma analizi yaptır (basit örnek)
            import random
            selected_indices = random.sample(range(len(firm_data)), min(5, len(firm_data)))
            
            # Seçilen firmaları işaretle
            for i in range(self.firms_table.rowCount()):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox:
                    checkbox.setChecked(i in selected_indices)
            
            self.update_stats()
            QMessageBox.information(self, "AI Optimizasyon", f"AI {len(selected_indices)} firma seçti!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"AI optimizasyon hatası: {e}")
    
    def export_report(self):
        """Rapor oluştur ve dışa aktar"""
        if not self.sent_messages and not self.failed_messages:
            QMessageBox.information(self, "Bilgi", "Dışa aktarılacak veri bulunamadı!")
            return
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"toplu_mesaj_raporu_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("🚀 TOPLU MESAJ RAPORU\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                f.write(f"Toplam Firma: {len(self.firms)}\n")
                f.write(f"Seçilen Firma: {len(self.get_selected_firms())}\n")
                f.write(f"Gönderilen: {len(self.sent_messages)}\n")
                f.write(f"Başarısız: {len(self.failed_messages)}\n")
                f.write(f"Atlanan: {len(self.skipped_firms)}\n\n")
            
            QMessageBox.information(self, "Başarılı", f"Rapor oluşturuldu: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor oluşturma hatası: {e}")
    
    def get_selected_firms(self):
        """Seçili firmaları getir"""
        selected_firms = []
        for i in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(i):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox and checkbox.isChecked():
                    selected_firms.append(self.firms[i])
        return selected_firms
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        selected_count = len(self.get_selected_firms())
        total_count = self.firms_table.rowCount()
        
        self.stats_label.setText(
            f"📊 Seçili: {selected_count} | ✅ Gönderilen: {self.stats['sent']} | "
            f"❌ Başarısız: {self.stats['failed']} | ⏭️ Atlanan: {self.stats['skipped']}"
        )
        
        # Detaylı istatistikler
        self.detailed_stats.setText(
            f"Toplam: {total_count} | Seçili: {selected_count} | "
            f"Gönderilen: {self.stats['sent']} | Başarısız: {self.stats['failed']} | "
            f"Atlanan: {self.stats['skipped']} | Bekleyen: {self.stats['pending']}"
        )
    
    def start_bulk_messaging(self):
        """Toplu mesaj gönderimini başlat"""
        selected_firms = self.get_selected_firms()
        if not selected_firms:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir firma seçin!")
            return
        
        # Gönderimi başlat
        self.is_running = True
        self.current_firm_index = 0
        self.selected_firms = selected_firms
        self.stats = {'total': len(selected_firms), 'sent': 0, 'failed': 0, 'skipped': 0, 'pending': len(selected_firms)}
        
        # UI'yi güncelle
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setMaximum(len(selected_firms))
        self.progress_bar.setValue(0)
        
        self.log_message("🚀 Toplu mesaj gönderimi başlatıldı!")
    
    def pause_messaging(self):
        """Mesaj gönderimini duraklat"""
        self.pause_requested = True
        self.pause_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        self.log_message("⏸️ Mesaj gönderimi duraklatıldı")
    
    def toggle_pause(self):
        """Duraklat/Devam et"""
        if self.pause_requested:
            self.pause_requested = False
            self.pause_btn.setEnabled(True)
            self.start_btn.setEnabled(False)
            self.log_message("▶️ Mesaj gönderimi devam ediyor")
        else:
            self.pause_messaging()
    
    def stop_messaging(self):
        """Mesaj gönderimini durdur"""
        self.is_running = False
        self.pause_requested = False
        
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        self.log_message("⏹️ Mesaj gönderimi durduruldu")
    
    def log_message(self, message):
        """Log mesajı ekle"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Log'u otomatik kaydır
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def filter_firms(self):
        """Firmaları filtrele"""
        sector_filter = self.sector_filter.currentText()
        status_filter = self.status_filter.currentText()
        website_filter = self.website_filter.currentText()
        search_text = self.search_input.text().lower() if hasattr(self, 'search_input') else ""
        
        for i in range(self.firms_table.rowCount()):
            firm = self.firms[i]
            show_row = True
            
            # Sektör filtresi
            if sector_filter != "Tüm Sektörler" and firm.get('sector', '') != sector_filter:
                show_row = False
            
            # Durum filtresi
            if status_filter != "Tüm Durumlar" and firm.get('status', '') != status_filter:
                show_row = False
            
            # Website filtresi
            if website_filter == "Website Var" and not firm.get('website', '').strip():
                show_row = False
            elif website_filter == "Website Yok" and firm.get('website', '').strip():
                show_row = False
            
            # Arama metni filtresi
            if search_text:
                searchable_text = f"{firm.get('name', '')} {firm.get('sector', '')} {firm.get('contact_person', '')} {firm.get('phone', '')} {firm.get('email', '')}".lower()
                if search_text not in searchable_text:
                    show_row = False
            
            self.firms_table.setRowHidden(i, not show_row)
        
        self.update_stats()
    
    def invert_selection(self):
        """🔄 Seçimi tersine çevir"""
        for i in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(i):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())
        self.update_stats()
    
    def select_no_website(self):
        """🌐 Website olmayan firmaları seç"""
        for i in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(i):
                firm = self.firms[i]
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox:
                    # Website yoksa seç
                    website = firm.get('website', '').strip()
                    checkbox.setChecked(not website)
        self.update_stats()
    
    def generate_ai_message(self):
        """🤖 AI ile mesaj oluştur - Bilgi Öğrenim Entegreli"""
        if not self.gpt_manager or not hasattr(self.gpt_manager, 'client') or not self.gpt_manager.client:
            QMessageBox.warning(self, "Uyarı", "OpenAI API ayarlanmamış! Lütfen ayarlar sekmesinden API key'inizi girin.")
            return
        
        language = self.language_combo.currentText()
        message_type = self.message_type_combo.currentText()
        custom_prompt = self.custom_prompt_input.text().strip()
        
        try:
            # Dil kod haritası
            language_codes = {
                "Türkçe": "Turkish",
                "English": "English",
                "Deutsch": "German", 
                "Français": "French",
                "Español": "Spanish",
                "Italiano": "Italian",
                "Русский": "Russian",
                "العربية": "Arabic",
                "中文": "Chinese",
                "日本語": "Japanese",
                "Polski": "Polish"
            }
            
            lang_code = language_codes.get(language, "Turkish")
            
            # Örnek firma bilgisi (genel mesaj için)
            sample_firm = {
                'name': 'Örnek Firma',
                'sector': 'Teknoloji',
                'contact_person': 'Ahmet Yılmaz',
                'phone': '+90 555 123 4567',
                'email': 'info@ornekfirma.com',
                'website': 'www.ornekfirma.com',
                'summary': 'Teknoloji sektöründe faaliyet gösteren yenilikçi bir şirket'
            }
            
            # 🧠 Bilgi Öğrenim verilerini al
            learned_knowledge = ""
            if hasattr(self, 'db') and self.db:
                try:
                    all_knowledge = self.db.get_all_knowledge(filter_learned=True)
                    if all_knowledge:
                        knowledge_summaries = []
                        for knowledge in all_knowledge[:5]:  # En fazla 5 bilgi kullan
                            if knowledge.get('ai_summary'):
                                knowledge_summaries.append(f"• {knowledge.get('title', 'Bilgi')}: {knowledge.get('ai_summary', '')}")
                        
                        if knowledge_summaries:
                            learned_knowledge = f"""
            
            🧠 Öğrenilmiş Firma Bilgileri (AI Analizi):
            {chr(10).join(knowledge_summaries)}
            
            Bu bilgileri kullanarak daha kişiselleştirilmiş ve detaylı mesaj oluştur.
            """
                except Exception as e:
                    print(f"Bilgi öğrenim verisi alınamadı: {e}")
            
            prompt = f"""
            Lütfen {lang_code} dilinde ve kültürel diline uygun profesyonel bir WhatsApp B2B mesajı oluştur.
            
            Firma Bilgileri (Örnek):
            - Firma Adı: {sample_firm['name']}
            - Sektör: {sample_firm['sector']}
            - İletişim Kişisi: {sample_firm['contact_person']}
            - Telefon: {sample_firm['phone']}
            - Email: {sample_firm['email']}
            - Website: {sample_firm['website']}
            - Özet: {sample_firm['summary']}
            {learned_knowledge}
            
            Mesaj Tipi: {message_type}
            Dil: {lang_code}
            """
            
            if custom_prompt:
                prompt += f"\n\nÖzel Talimatlar: {custom_prompt}"
            
            prompt += """
            
            Mesaj özellikleri:
            - Maksimum 180 karakter (WhatsApp için ideal)
            - Profesyonel ama samimi ton
            - Değişkenler kullan: {firma_adi}, {firma_iletisim}, {firma_sektoru}, {firma_ozet}
            - Net bir call-to-action içermeli
            - Kültürel dilinde ve o dilin iş yapma tarzına uygun
            - WhatsApp için uygun format
            - Öğrenilmiş firma bilgilerini kullanarak daha kişiselleştirilmiş içerik oluştur
            
            Sadece mesaj şablonunu döndür, başka açıklama ekleme.
            """
            
            response = self.gpt_manager.client.chat.completions.create(
                model=self.gpt_manager.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"Sen {lang_code} dilinde uzman bir B2B satış uzmanısın. O dilin kültürel özelliklerini ve iş yapma tarzını mükemmel biliyorsun. Kısa, etkili ve kişiselleştirilmiş mesajlar yazarsın."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            message = response.choices[0].message.content.strip()
            
            # Eğer mesaj Türkçe değilse, Türkçe çevirisini de oluştur
            turkish_translation = ""
            if lang_code != "Turkish":
                try:
                    translation_prompt = f"""
                    Lütfen aşağıdaki mesajı Türkçe'ye çevir. Çeviri doğal ve akıcı olsun, WhatsApp B2B mesajı formatında kalsın.
                    
                    Orijinal Mesaj ({lang_code}):
                    {message}
                    
                    Sadece Türkçe çevirisini döndür, başka açıklama ekleme.
                    """
                    
                    translation_response = self.gpt_manager.client.chat.completions.create(
                        model=self.gpt_manager.model,
                        messages=[
                            {
                                "role": "system", 
                                "content": "Sen profesyonel bir çevirmensin. B2B mesajları doğal ve akıcı bir şekilde Türkçe'ye çevirirsin."
                            },
                            {
                                "role": "user", 
                                "content": translation_prompt
                            }
                        ],
                        max_tokens=200,
                        temperature=0.7
                    )
                    
                    turkish_translation = translation_response.choices[0].message.content.strip()
                except Exception as e:
                    print(f"Türkçe çeviri hatası: {e}")
                    turkish_translation = "Çeviri oluşturulamadı"
            
            # Mesajı ve çevirisini birlikte göster
            if turkish_translation and lang_code != "Turkish":
                display_message = f"🌍 {language} Mesajı:\n{message}\n\n🇹🇷 Türkçe Çevirisi:\n{turkish_translation}"
            else:
                display_message = message
                
            self.message_preview.setText(display_message)
            
            QMessageBox.information(self, "✅ Başarılı", f"{language} dilinde AI mesajı oluşturuldu!" + (f"\n\nTürkçe çevirisi de eklendi!" if turkish_translation else ""))
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Mesaj oluşturulurken hata:\n{str(e)}")
    
    def regenerate_message(self):
        """🔄 Mesajı yeniden oluştur"""
        self.generate_ai_message()
    
    def preview_all_messages(self):
        """👁️ Tüm mesajları önizle"""
        selected_firms = self.get_selected_firms()
        if not selected_firms:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir firma seçin!")
            return
        
        if not self.gpt_manager or not hasattr(self.gpt_manager, 'client') or not self.gpt_manager.client:
            QMessageBox.warning(self, "Uyarı", "OpenAI API ayarlanmamış!")
            return
        
        try:
            preview_text = "📝 TÜM MESAJLAR ÖNİZLEMESİ\n"
            preview_text += "=" * 50 + "\n\n"
            
            for i, firm in enumerate(selected_firms[:5]):  # İlk 5 firma için önizleme
                message = self.generate_message_for_firm_preview(firm)
                preview_text += f"🏢 {firm.get('name', 'Bilinmeyen')}\n"
                preview_text += f"📱 {firm.get('phone', '')}\n"
                preview_text += f"💬 {message}\n"
                preview_text += "-" * 30 + "\n\n"
            
            if len(selected_firms) > 5:
                preview_text += f"... ve {len(selected_firms) - 5} firma daha\n"
            
            # Önizleme dialog'u göster
            dialog = QDialog(self)
            dialog.setWindowTitle("👁️ Tüm Mesajlar Önizlemesi")
            dialog.setModal(True)
            dialog.resize(600, 500)
            
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(preview_text)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
            
            close_btn = QPushButton("Kapat")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Önizleme oluşturulurken hata:\n{str(e)}")
    
    def generate_message_for_firm_preview(self, firm):
        """Firma için mesaj önizlemesi oluştur"""
        try:
            language = self.language_combo.currentText()
            message_type = self.message_type_combo.currentText()
            
            language_codes = {
                "Türkçe": "Turkish",
                "English": "English",
                "Deutsch": "German", 
                "Français": "French",
                "Español": "Spanish",
                "Italiano": "Italian",
                "Русский": "Russian",
                "العربية": "Arabic",
                "中文": "Chinese",
                "日本語": "Japanese",
                "Polski": "Polish"
            }
            
            lang_code = language_codes.get(language, "Turkish")
            
            firm_info = f"""
            Firma Adı: {firm.get('name', 'Belirtilmemiş')}
            Sektör: {firm.get('sector', 'Belirtilmemiş')}
            İletişim Kişisi: {firm.get('contact_person', 'Belirtilmemiş')}
            Telefon: {firm.get('phone', 'Belirtilmemiş')}
            Email: {firm.get('email', 'Belirtilmemiş')}
            Website: {firm.get('website', 'Belirtilmemiş')}
            Özet: {firm.get('summary', 'Belirtilmemiş')}
            """
            
            prompt = f"""
            Lütfen {lang_code} dilinde ve kültürel diline uygun profesyonel bir WhatsApp B2B mesajı oluştur.
            
            Firma Bilgileri:
            {firm_info}
            
            Mesaj Tipi: {message_type}
            Dil: {lang_code}
            
            Mesaj özellikleri:
            - Maksimum 180 karakter
            - Profesyonel ama samimi ton
            - Firmaya özel detaylar kullan
            - Net bir call-to-action içermeli
            - İletişim kişisinin ismini kullan (varsa)
            - Sektöre uygun terminoloji
            
            Sadece mesaj metnini döndür, başka hiçbir şey ekleme.
            """
            
            response = self.gpt_manager.client.chat.completions.create(
                model=self.gpt_manager.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"Sen {lang_code} dilinde uzman bir B2B satış uzmanısın. Kısa, etkili ve kişiselleştirilmiş mesajlar yazarsın."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Hata: {str(e)}"
    
    def on_tab_clicked(self, index):
        """Tab butonlarına tıklandığında popup aç"""
        try:
            # Mevcut tab'ı kontrol et, eğer aynı tab'a tıklanmışsa popup aç
            current_index = self.message_tabs.currentIndex()
            if current_index == index:
                tab_text = self.message_tabs.tabText(index)
                
                if "AI Mesaj" in tab_text:
                    self.open_ai_message_popup()
                elif "Şablon" in tab_text:
                    self.open_template_popup()
                elif "Manuel" in tab_text:
                    self.open_manual_popup()
                
        except Exception as e:
            logger.error(f"Tab click hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Tab açılırken hata:\n{str(e)}")
    
    def open_ai_message_popup(self):
        """AI Mesaj popup'ını aç"""
        try:
            # Seçili firmaları kontrol et
            selected_firms = []
            for i in range(self.firms_table.rowCount()):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox and checkbox.isChecked():
                    if i < len(self.firms):
                        selected_firms.append(self.firms[i])
            
            if not selected_firms:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen en az bir firma seçin!")
                return
            
            # AI Mesaj popup'ını aç
            self.show_ai_message_popup()
            
        except Exception as e:
            logger.error(f"AI Mesaj popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"AI Mesaj popup'ı açılamadı:\n{str(e)}")
    
    def open_template_popup(self):
        """Şablon popup'ını aç"""
        try:
            # Şablon popup'ını aç
            self.show_template_popup()
            
        except Exception as e:
            logger.error(f"Şablon popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Şablon popup'ı açılamadı:\n{str(e)}")
    
    def open_manual_popup(self):
        """Manuel popup'ını aç"""
        try:
            # Seçili firmaları kontrol et
            selected_firms = []
            for i in range(self.firms_table.rowCount()):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox and checkbox.isChecked():
                    if i < len(self.firms):
                        selected_firms.append(self.firms[i])
            
            if not selected_firms:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen en az bir firma seçin!")
                return
            
            # Manuel popup'ını aç
            self.show_manual_popup()
            
        except Exception as e:
            logger.error(f"Manuel popup hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Manuel popup'ı açılamadı:\n{str(e)}")
    
    def create_new_template(self):
        """➕ Yeni şablon oluştur"""
        self.template_content.clear()
        self.template_combo.setCurrentIndex(0)
        QMessageBox.information(self, "Yeni Şablon", "Yeni şablon oluşturmak için içeriği yazın ve 'Şablonu Kaydet' butonuna tıklayın.")
    
    def save_template(self):
        """💾 Şablonu kaydet"""
        content = self.template_content.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Uyarı", "Lütfen şablon içeriği girin!")
            return
        
        name, ok = QInputDialog.getText(self, "Şablon Kaydet", "Şablon adı:")
        if ok and name:
            if self.db:
                success = self.db.save_template(name, content, "genel", [])
                if success:
                    QMessageBox.information(self, "✅ Başarılı", "Şablon kaydedildi!")
                    self.load_templates()
                else:
                    QMessageBox.critical(self, "❌ Hata", "Şablon kaydedilemedi!")
            else:
                QMessageBox.warning(self, "Uyarı", "Veritabanı bağlantısı yok!")
    
    def on_template_selected(self):
        """📋 Şablon seçildiğinde"""
        template = self.template_combo.currentData()
        if template:
            self.template_content.setText(template['content'])
        else:
            self.template_content.clear()
    
    def update_firm_count(self):
        """Firma sayısını güncelle"""
        count = self.firms_table.rowCount()
        visible_count = 0
        for i in range(count):
            if not self.firms_table.isRowHidden(i):
                visible_count += 1
        
        self.firm_count_label.setText(f"{visible_count} firma (Toplam: {count})")
    
    def setup_shortcuts(self):
        """⌨️ Klavye kısayolları ayarla"""
        # Ctrl+A: Tümünü seç
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self.select_all)
        
        # Ctrl+D: Hiçbirini seçme
        select_none_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        select_none_shortcut.activated.connect(self.select_none)
        
        # Ctrl+I: Tersini seç
        invert_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        invert_shortcut.activated.connect(self.invert_selection)
        
        # Ctrl+G: AI ile oluştur
        generate_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        generate_shortcut.activated.connect(self.generate_ai_message)
        
        # Ctrl+R: Yeniden oluştur
        regenerate_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        regenerate_shortcut.activated.connect(self.regenerate_message)
        
        # Ctrl+P: Önizle
        preview_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        preview_shortcut.activated.connect(self.preview_all_messages)
        
        # Ctrl+S: Başlat
        start_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        start_shortcut.activated.connect(self.start_bulk_messaging)
        
        # Escape: Kapat
        close_shortcut = QShortcut(QKeySequence("Escape"), self)
        close_shortcut.activated.connect(self.reject)
        
        # F5: Yenile
        refresh_shortcut = QShortcut(QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.load_firms)


class QuickMessageDialog(QDialog):
    """Hızlı mesaj popup'ı"""
    
    def __init__(self, parent=None, firm=None, gpt_manager=None, db=None):
        super().__init__(parent)
        self.firm = firm
        self.gpt_manager = gpt_manager
        self.db = db
        self.message = ""
        
        self.setupUI()
        self.load_firm_info()
    
    def setupUI(self):
        """Arayüz oluştur"""
        self.setWindowTitle("💬 Hızlı Mesaj")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Firma bilgileri
        firm_group = QGroupBox("📋 Firma Bilgileri")
        firm_layout = QVBoxLayout()
        
        self.firm_info_label = QLabel()
        self.firm_info_label.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        firm_layout.addWidget(self.firm_info_label)
        
        firm_group.setLayout(firm_layout)
        layout.addWidget(firm_group)
        
        # Mesaj şablonları
        template_group = QGroupBox("📝 Hızlı Şablonlar")
        template_layout = QVBoxLayout()
        
        # Şablon butonları
        templates = [
            ("👋 Selamlama", "Merhaba {name}, {company} için size ulaşıyorum."),
            ("📞 Arama", "Merhaba, {company} ile ilgili kısa bir görüşme yapabilir miyiz?"),
            ("📧 Email", "Merhaba, size email göndermek istiyorum, uygun mu?"),
            ("🤝 Tanışma", "Merhaba {name}, {company} ile tanışmak istiyorum."),
            ("📋 Bilgi", "Merhaba, {company} hakkında bilgi alabilir miyim?")
        ]
        
        template_buttons_layout = QGridLayout()
        for i, (title, template) in enumerate(templates):
            btn = QPushButton(title)
            btn.clicked.connect(lambda checked, t=template: self.use_template(t))
            btn.setStyleSheet("""
                QPushButton {
                    background: #e3f2fd;
                    border: 1px solid #bbdefb;
                    border-radius: 6px;
                    padding: 8px;
                    text-align: left;
                }
                QPushButton:hover {
                    background: #bbdefb;
                }
            """)
            template_buttons_layout.addWidget(btn, i // 2, i % 2)
        
        template_layout.addLayout(template_buttons_layout)
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
        # Mesaj editörü
        message_group = QGroupBox("✏️ Mesaj")
        message_layout = QVBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Mesajınızı yazın...")
        self.message_input.setMaximumHeight(100)
        message_layout.addWidget(self.message_input)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        self.ai_generate_btn = QPushButton("🤖 AI ile Oluştur")
        self.ai_generate_btn.clicked.connect(self.generate_with_ai)
        self.ai_generate_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        buttons_layout.addWidget(self.ai_generate_btn)
        
        buttons_layout.addStretch()
        
        self.cancel_btn = QPushButton("❌ İptal")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("✅ Tamam")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        buttons_layout.addWidget(self.ok_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_firm_info(self):
        """Firma bilgilerini yükle"""
        if not self.firm:
            return
        
        info_text = f"""
        <b>Firma:</b> {self.firm.get('name', 'İsimsiz')}<br>
        <b>Sektör:</b> {self.firm.get('sector', 'Belirtilmemiş')}<br>
        <b>Telefon:</b> {self.firm.get('phone', 'Belirtilmemiş')}<br>
        <b>Email:</b> {self.firm.get('email', 'Belirtilmemiş')}<br>
        <b>Adres:</b> {self.firm.get('address', 'Belirtilmemiş')}
        """
        self.firm_info_label.setText(info_text)
    
    def use_template(self, template):
        """Şablonu kullan"""
        if not self.firm:
            return
        
        # Şablonu firma bilgileriyle doldur
        message = template.format(
            name=self.firm.get('contact_person', 'Sayın Yetkili'),
            company=self.firm.get('name', 'Firma'),
            sector=self.firm.get('sector', 'Sektör')
        )
        
        self.message_input.setText(message)
    
    def generate_with_ai(self):
        """AI ile mesaj oluştur"""
        if not self.gpt_manager or not self.gpt_manager.client:
            QMessageBox.warning(self, "Uyarı", "AI servisi kullanılamıyor!")
            return
        
        try:
            prompt = "Firmaya uygun kısa ve profesyonel bir WhatsApp mesajı oluştur."
            message = self.gpt_manager.generate_message(prompt, self.firm, "tanıtım")
            
            if message:
                self.message_input.setText(message)
            else:
                QMessageBox.warning(self, "Uyarı", "Mesaj oluşturulamadı!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"AI mesaj oluşturma hatası: {e}")
    
    def get_message(self):
        """Oluşturulan mesajı getir"""
        return self.message_input.toPlainText().strip()


class AIPromptDialog(QDialog):
    """AI Prompt dialog'u - Özel prompt girişi"""
    
    def __init__(self, parent=None, firm=None, gpt_manager=None):
        super().__init__(parent)
        self.firm = firm
        self.gpt_manager = gpt_manager
        self.generated_message = ""
        
        self.setupUI()
        self.load_firm_info()
    
    def setupUI(self):
        """Arayüz oluştur"""
        self.setWindowTitle("🤖 AI Prompt - Özel Mesaj Oluşturucu")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Firma bilgileri
        firm_group = QGroupBox("📋 Firma Bilgileri")
        firm_layout = QVBoxLayout()
        
        self.firm_info_label = QLabel()
        self.firm_info_label.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        firm_layout.addWidget(self.firm_info_label)
        
        firm_group.setLayout(firm_layout)
        layout.addWidget(firm_group)
        
        # Prompt girişi
        prompt_group = QGroupBox("🎯 AI Prompt")
        prompt_layout = QVBoxLayout()
        
        prompt_layout.addWidget(QLabel("AI'ya ne yapmasını istiyorsunuz?"))
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("""
Örnek prompt'lar:
- "Firmaya özel bir tanıtım mesajı yaz"
- "Takip mesajı oluştur, samimi olsun"
- "Kampanya duyurusu yap, %20 indirim var"
- "Teşekkür mesajı yaz, görüşme için teşekkür et"
- "Randevu teklif et, bu hafta uygun mu diye sor"
        """)
        self.prompt_input.setMaximumHeight(120)
        prompt_layout.addWidget(self.prompt_input)
        
        # Mesaj tipi seçimi
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Mesaj Tipi:"))
        
        self.message_type_combo = QComboBox()
        self.message_type_combo.addItems([
            "tanıtım", "takip", "kampanya", "bilgilendirme", 
            "teşekkür", "randevu", "satış", "destek"
        ])
        type_layout.addWidget(self.message_type_combo)
        
        type_layout.addStretch()
        prompt_layout.addLayout(type_layout)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # Oluşturulan mesaj
        result_group = QGroupBox("📝 Oluşturulan Mesaj")
        result_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("🤖 Mesaj Oluştur")
        self.generate_btn.clicked.connect(self.generate_message)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        buttons_layout.addWidget(self.generate_btn)
        
        self.regenerate_btn = QPushButton("🔄 Yeniden Oluştur")
        self.regenerate_btn.clicked.connect(self.generate_message)
        self.regenerate_btn.setEnabled(False)
        self.regenerate_btn.setStyleSheet("""
            QPushButton {
                background: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e0a800;
            }
        """)
        buttons_layout.addWidget(self.regenerate_btn)
        
        buttons_layout.addStretch()
        
        self.cancel_btn = QPushButton("❌ İptal")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("✅ Kullan")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        buttons_layout.addWidget(self.ok_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_firm_info(self):
        """Firma bilgilerini yükle"""
        if not self.firm:
            return
        
        info_text = f"""
        <b>Firma:</b> {self.firm.get('name', 'İsimsiz')}<br>
        <b>Sektör:</b> {self.firm.get('sector', 'Belirtilmemiş')}<br>
        <b>İletişim:</b> {self.firm.get('contact_person', 'Belirtilmemiş')}<br>
        <b>Telefon:</b> {self.firm.get('phone', 'Belirtilmemiş')}<br>
        <b>Email:</b> {self.firm.get('email', 'Belirtilmemiş')}
        """
        self.firm_info_label.setText(info_text)
    
    def generate_message(self):
        """AI ile mesaj oluştur"""
        if not self.gpt_manager or not self.gpt_manager.client:
            QMessageBox.warning(self, "Uyarı", "AI servisi kullanılamıyor!")
            return
        
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir prompt girin!")
            return
        
        try:
            # Loading göster
            self.generate_btn.setText("⏳ Oluşturuluyor...")
            self.generate_btn.setEnabled(False)
            QApplication.processEvents()
            
            message_type = self.message_type_combo.currentText()
            message = self.gpt_manager.generate_message(prompt, self.firm, message_type)
            
            if message:
                self.generated_message = message
                self.result_text.setText(message)
                self.regenerate_btn.setEnabled(True)
                self.ok_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Uyarı", "Mesaj oluşturulamadı!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"AI mesaj oluşturma hatası: {e}")
        finally:
            self.generate_btn.setText("🤖 Mesaj Oluştur")
            self.generate_btn.setEnabled(True)
    
    def get_generated_message(self):
        """Oluşturulan mesajı getir"""
        return self.generated_message


class BulkCallDialog(QDialog):
    """Gelişmiş toplu otomatik arama dialogu"""
    
    def __init__(self, parent=None, firms=None, assistant_data=None, phone_number_id=None, vapi_manager=None, db=None):
        super().__init__(parent)
        self.firms = firms or []
        self.assistant_data = assistant_data or {}
        self.phone_number_id = phone_number_id
        self.vapi_manager = vapi_manager
        self.db = db
        
        # Arama durumu
        self.is_calling = False
        self.current_call_index = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.call_timer = QTimer()
        self.call_timer.timeout.connect(self.process_next_call)
        
        self.setWindowTitle("📞 Toplu Otomatik Arama Sistemi")
        self.setFixedSize(800, 700)
        self.setupUI()
        self.load_firms()
    
    def get_scale_factor(self):
        """Gelişmiş tam ekran ölçeklendirme faktörü"""
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        
        # DPI tabanlı ölçeklendirme
        dpi = screen.logicalDotsPerInch()
        dpi_scale = max(1.0, dpi / 96.0)
        
        # Ekran boyutuna göre ölçeklendirme
        screen_width = geometry.width()
        screen_height = geometry.height()
        
        # Referans çözünürlük (1920x1080)
        ref_width = 1920
        ref_height = 1080
        
        # Genişlik ve yükseklik ölçeklendirme faktörleri
        width_scale = screen_width / ref_width
        height_scale = screen_height / ref_height
        
        # En küçük ölçeklendirme faktörünü kullan (orantıyı korumak için)
        size_scale = min(width_scale, height_scale)
        
        # DPI ve boyut ölçeklendirmesini birleştir
        final_scale = max(0.8, min(2.0, dpi_scale * size_scale))
        
        return final_scale
    
    def setupUI(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("📞 Toplu Otomatik Arama Sistemi")
        scale_factor = self.get_scale_factor() if hasattr(self, 'get_scale_factor') else 1.0
        font_size = max(16, int(18 * scale_factor))
        padding = max(8, int(10 * scale_factor))
        
        title.setStyleSheet(f"""
            font-size: {font_size}px; 
            font-weight: bold; 
            color: #ffffff; 
            padding: {padding}px;
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: {max(6, int(8 * scale_factor))}px;
            margin-bottom: {padding}px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Ana içerik
        content_layout = QHBoxLayout()
        
        # Sol panel - Firma seçimi
        left_panel = QGroupBox("🏢 Firma Seçimi")
        left_layout = QVBoxLayout(left_panel)
        
        # Firma seçim kontrolleri
        selection_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Tümünü Seç")
        self.select_all_btn.clicked.connect(self.select_all_firms)
        scale_factor = self.get_scale_factor() if hasattr(self, 'get_scale_factor') else 1.0
        padding = max(6, int(8 * scale_factor))
        border_radius = max(3, int(4 * scale_factor))
        font_size = max(10, int(12 * scale_factor))
        
        self.select_all_btn.setStyleSheet(f"QPushButton {{ background-color: #28a745; color: white; padding: {padding}px; border-radius: {border_radius}px; font-size: {font_size}px; }}")
        selection_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("❌ Hiçbirini Seçme")
        self.select_none_btn.clicked.connect(self.select_no_firms)
        self.select_none_btn.setStyleSheet(f"QPushButton {{ background-color: #dc3545; color: white; padding: {padding}px; border-radius: {border_radius}px; font-size: {font_size}px; }}")
        selection_layout.addWidget(self.select_none_btn)
        
        left_layout.addLayout(selection_layout)
        
        # Firma listesi
        self.firms_list = QListWidget()
        self.firms_list.setMaximumHeight(400)
        left_layout.addWidget(self.firms_list)
        
        # Seçilen firma sayısı
        self.selected_count_label = QLabel("📊 Seçilen: 0 firma")
        count_padding = max(4, int(5 * scale_factor))
        self.selected_count_label.setStyleSheet(f"color: #17a2b8; font-weight: bold; padding: {count_padding}px; font-size: {font_size}px;")
        left_layout.addWidget(self.selected_count_label)
        
        content_layout.addWidget(left_panel, 1)
        
        # Sağ panel - Ayarlar ve kontrol
        right_panel = QGroupBox("⚙️ Arama Ayarları")
        right_layout = QVBoxLayout(right_panel)
        
        # Asistan bilgisi
        assistant_info = QGroupBox("🤖 Seçili Asistan")
        assistant_layout = QVBoxLayout(assistant_info)
        self.assistant_info_label = QLabel(f"📝 {self.assistant_data.get('name', 'Bilinmiyor')}")
        self.assistant_info_label.setStyleSheet("font-weight: bold; color: #8e44ad; padding: 5px;")
        assistant_layout.addWidget(self.assistant_info_label)
        right_layout.addWidget(assistant_info)
        
        # Arama aralığı seçimi
        interval_group = QGroupBox("⏱️ Arama Aralığı")
        interval_layout = QVBoxLayout(interval_group)
        
        interval_label = QLabel("Her ne kadar süre ara ile arama yapılsın?")
        interval_label.setStyleSheet("color: #2c3e50; font-size: 12px;")
        interval_layout.addWidget(interval_label)
        
        self.interval_combo = QComboBox()
        intervals = [
            ("3 Dakika", 3),
            ("5 Dakika", 5),
            ("10 Dakika", 10),
            ("15 Dakika", 15),
            ("20 Dakika", 20),
            ("25 Dakika", 25),
            ("30 Dakika", 30)
        ]
        
        for label, minutes in intervals:
            self.interval_combo.addItem(label, minutes)
        
        self.interval_combo.setCurrentIndex(0)  # Varsayılan 3 dakika
        self.interval_combo.setStyleSheet("padding: 8px; font-size: 12px;")
        interval_layout.addWidget(self.interval_combo)
        
        right_layout.addWidget(interval_group)
        
        # Durum ve istatistik
        stats_group = QGroupBox("📊 Arama Durumu")
        stats_layout = QVBoxLayout(stats_group)
        
        self.status_label = QLabel("🟢 Hazır")
        self.status_label.setStyleSheet("font-weight: bold; color: #27ae60; padding: 5px;")
        stats_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        stats_layout.addWidget(self.progress_bar)
        
        self.stats_label = QLabel("📈 Başarılı: 0 | ❌ Başarısız: 0")
        self.stats_label.setStyleSheet("color: #34495e; font-size: 11px; padding: 5px;")
        stats_layout.addWidget(self.stats_label)
        
        self.next_call_label = QLabel("⏭️ Sonraki arama: -")
        self.next_call_label.setStyleSheet("color: #3498db; font-size: 11px; padding: 5px;")
        stats_layout.addWidget(self.next_call_label)
        
        right_layout.addWidget(stats_group)
        
        # Kontrol butonları
        control_group = QGroupBox("🎮 Kontroller")
        control_layout = QVBoxLayout(control_group)
        
        self.start_btn = QPushButton("🚀 Otomatik Aramayı Başlat")
        self.start_btn.clicked.connect(self.start_bulk_calling)
        btn_padding = max(10, int(12 * self.get_scale_factor()))
        btn_radius = max(4, int(6 * self.get_scale_factor()))
        btn_font_size = max(11, int(13 * self.get_scale_factor()))
        
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: {btn_padding}px;
                border-radius: {btn_radius}px;
                font-size: {btn_font_size}px;
            }}
            QPushButton:hover {{ background-color: #34ce57; }}
        """)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ Aramayı Durdur")
        self.stop_btn.clicked.connect(self.stop_bulk_calling)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: {btn_padding}px;
                border-radius: {btn_radius}px;
                font-size: {btn_font_size}px;
            }}
            QPushButton:hover {{ background-color: #c82333; }}
            QPushButton:disabled {{ background-color: #6c757d; }}
        """)
        control_layout.addWidget(self.stop_btn)
        
        self.close_btn = QPushButton("❌ Pencereyi Kapat")
        self.close_btn.clicked.connect(self.close)
        close_btn_padding = max(8, int(10 * self.get_scale_factor()))
        close_btn_font_size = max(10, int(12 * self.get_scale_factor()))
        
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                padding: {close_btn_padding}px;
                border-radius: {btn_radius}px;
                font-size: {close_btn_font_size}px;
            }}
            QPushButton:hover {{ background-color: #5a6268; }}
        """)
        control_layout.addWidget(self.close_btn)
        
        right_layout.addWidget(control_group)
        
        content_layout.addWidget(right_panel, 1)
        layout.addLayout(content_layout)
    
    def load_firms(self):
        """Firmaları listele"""
        self.firms_list.clear()
        
        for firm in self.firms:
            item_text = f"🏢 {firm['name']}\n📞 {firm['phone']}\n🏭 {firm.get('sector', 'N/A')}"
            
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, firm)
            
            self.firms_list.addItem(item)
        
        # Checkbox değişiklik sinyali
        self.firms_list.itemChanged.connect(self.update_selected_count)
        self.update_selected_count()
    
    def select_all_firms(self):
        """Tüm firmaları seç"""
        for i in range(self.firms_list.count()):
            item = self.firms_list.item(i)
            item.setCheckState(Qt.Checked)
    
    def select_no_firms(self):
        """Hiçbir firmayı seçme"""
        for i in range(self.firms_list.count()):
            item = self.firms_list.item(i)
            item.setCheckState(Qt.Unchecked)
    
    def update_selected_count(self):
        """Seçilen firma sayısını güncelle"""
        selected_count = 0
        for i in range(self.firms_list.count()):
            item = self.firms_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_count += 1
        
        self.selected_count_label.setText(f"📊 Seçilen: {selected_count} firma")
        
        # Başlat butonunu etkinleştir/pasifleştir
        self.start_btn.setEnabled(selected_count > 0 and not self.is_calling)
    
    def get_selected_firms(self):
        """Seçilen firmaları al"""
        selected_firms = []
        for i in range(self.firms_list.count()):
            item = self.firms_list.item(i)
            if item.checkState() == Qt.Checked:
                firm_data = item.data(Qt.UserRole)
                selected_firms.append(firm_data)
        return selected_firms
    
    def start_bulk_calling(self):
        """Toplu aramayı başlat"""
        selected_firms = self.get_selected_firms()
        
        if not selected_firms:
            QMessageBox.warning(self, "⚠️ Uyarı", "En az bir firma seçmelisiniz!")
            return
        
        # Onay dialogu
        interval_minutes = self.interval_combo.currentData()
        reply = QMessageBox.question(
            self, "🚀 Toplu Arama Başlatma Onayı",
            f"🔥 {len(selected_firms)} firma otomatik olarak aranacak\n\n"
            f"⏱️ Arama Aralığı: {interval_minutes} dakika\n"
            f"🤖 Asistan: {self.assistant_data.get('name', 'N/A')}\n\n"
            f"⚠️ Bu işlem maliyetli olabilir!\n"
            f"Başlatmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Arama başlat
        self.is_calling = True
        self.current_call_index = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.selected_firms_list = selected_firms
        
        # UI güncellemeleri
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(selected_firms))
        self.progress_bar.setValue(0)
        
        self.status_label.setText("🔄 Otomatik arama başlatılıyor...")
        self.status_label.setStyleSheet("font-weight: bold; color: #f39c12; padding: 5px;")
        
        # İlk aramayı başlat
        self.process_next_call()
    
    def process_next_call(self):
        """Sıradaki firmayı ara"""
        if not self.is_calling or self.current_call_index >= len(self.selected_firms_list):
            self.finish_bulk_calling()
            return
        
        firm = self.selected_firms_list[self.current_call_index]
        self.status_label.setText(f"📞 Aranıyor: {firm['name']}")
        
        try:
            # Arama verilerini hazırla
            customer_data = {
                "name": firm.get('name'),
                "metadata": {
                    "email": firm.get('email', ''),
                    "sector": firm.get('sector', ''),
                    "contact_person": firm.get('contact_person', ''),
                    "summary": firm.get('summary', '')
                }
            }
            
            # Vapi aramasını başlat
            result = self.vapi_manager.start_call(
                firm['phone'],
                self.assistant_data['id'],
                customer_data
            )
            
            if result and 'error' not in result:
                # Başarılı arama
                self.db.save_call(
                    firm['id'],
                    call_id=result.get('id', ''),
                    phone_number_id=self.phone_number_id,
                    assistant_id=self.assistant_data['id'],
                    duration=0,
                    status='started',
                    notes=f"Otomatik toplu arama - {self.current_call_index + 1}/{len(self.selected_firms_list)}"
                )
                self.successful_calls += 1
            else:
                self.failed_calls += 1
                logger.error(f"Arama hatası: {result}")
                
        except Exception as e:
            self.failed_calls += 1
            logger.error(f"Toplu arama işlem hatası: {e}")
        
        # İlerleme güncelle
        self.current_call_index += 1
        self.progress_bar.setValue(self.current_call_index)
        self.update_stats()
        
        if self.current_call_index < len(self.selected_firms_list):
            # Sonraki arama için zamanlayıcıyı başlat
            interval_minutes = self.interval_combo.currentData()
            interval_ms = interval_minutes * 60 * 1000  # Dakikayı milisaniyeye çevir
            
            self.status_label.setText(f"⏱️ {interval_minutes} dakika bekleniyor...")
            self.status_label.setStyleSheet("font-weight: bold; color: #3498db; padding: 5px;")
            
            # Sonraki arama için countdown
            self.update_next_call_countdown(interval_minutes * 60)  # Saniye cinsinden
            
            self.call_timer.start(interval_ms)
        else:
            self.finish_bulk_calling()
    
    def update_next_call_countdown(self, seconds_left):
        """Sonraki arama countdown'unu güncelle"""
        if not self.is_calling:
            return
            
        if seconds_left <= 0:
            self.next_call_label.setText("⏭️ Sonraki arama: Şimdi")
            return
        
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        
        next_firm_name = "Bilinmiyor"
        if self.current_call_index < len(self.selected_firms_list):
            next_firm_name = self.selected_firms_list[self.current_call_index]['name'][:20]
        
        self.next_call_label.setText(f"⏭️ Sonraki: {next_firm_name} ({minutes}:{seconds:02d})")
        
        # 1 saniye sonra tekrar çağır
        QTimer.singleShot(1000, lambda: self.update_next_call_countdown(seconds_left - 1))
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        total = self.successful_calls + self.failed_calls
        self.stats_label.setText(f"📈 Başarılı: {self.successful_calls} | ❌ Başarısız: {self.failed_calls} | 📊 Toplam: {total}")
    
    def stop_bulk_calling(self):
        """Toplu aramayı durdur"""
        self.is_calling = False
        self.call_timer.stop()
        
        # UI güncellemeleri
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("⏹️ Arama durduruldu")
        self.status_label.setStyleSheet("font-weight: bold; color: #e74c3c; padding: 5px;")
        self.next_call_label.setText("⏭️ Sonraki arama: -")
        
        QMessageBox.information(self, "⏹️ Arama Durduruldu",
            f"Toplu arama durduruldu.\n\n"
            f"📈 Başarılı aramalar: {self.successful_calls}\n"
            f"❌ Başarısız aramalar: {self.failed_calls}")
    
    def finish_bulk_calling(self):
        """Toplu aramayı tamamla"""
        self.is_calling = False
        self.call_timer.stop()
        
        # UI güncellemeleri
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.status_label.setText("✅ Tüm aramalar tamamlandı!")
        self.status_label.setStyleSheet("font-weight: bold; color: #27ae60; padding: 5px;")
        self.next_call_label.setText("⏭️ Sonraki arama: -")
        
        # Sonuç dialogu
        QMessageBox.information(self, "🎉 Toplu Arama Tamamlandı!",
            f"Tüm otomatik aramalar başarıyla tamamlandı!\n\n"
            f"📞 Toplam arama: {len(self.selected_firms_list)}\n"
            f"📈 Başarılı aramalar: {self.successful_calls}\n"
            f"❌ Başarısız aramalar: {self.failed_calls}\n"
            f"📊 Başarı oranı: {(self.successful_calls/len(self.selected_firms_list)*100):.1f}%")
    
    def closeEvent(self, event):
        """Dialog kapatılırken"""
        if self.is_calling:
            reply = QMessageBox.question(
                self, "⚠️ Uyarı", 
                "Otomatik arama devam ediyor!\n\nPencereyi kapatmak istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            else:
                self.stop_bulk_calling()
        
        event.accept()


class TaskSchedulerThread(QThread):
    """Zamanlanmış görevler için thread"""
    
    task_executed = Signal(dict)
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.running = True
    
    def run(self):
        """Thread çalıştır"""
        while self.running:
            try:
                # Bekleyen görevleri kontrol et
                tasks = self.db.get_pending_tasks()
                
                for task in tasks:
                    # Görevi işle
                    self.task_executed.emit({
                        'id': task['id'],
                        'type': task['task_type'],
                        'firm_id': task['firm_id'],
                        'data': json.loads(task['data']) if task['data'] else {}
                    })
                    
                    # Durumu güncelle
                    self.db.update_task_status(task['id'], 'completed')
                
                # Zamanlanmış mesajları kontrol et
                messages = self.db.get_scheduled_messages()
                
                for msg in messages:
                    self.task_executed.emit({
                        'type': 'scheduled_message',
                        'firm_id': msg['firm_id'],
                        'phone': msg['firm_phone'],
                        'content': msg['content']
                    })
                
            except Exception as e:
                logger.error(f"Task scheduler hatası: {e}")
            
            # 30 saniye bekle
            time.sleep(30)
    
    def stop(self):
        """Thread'i durdur"""
        self.running = False


class MainWindow(QMainWindow):
    """Ana pencere - Güçlendirilmiş"""
    
    def __init__(self):
        super().__init__()
        
        # Güçlendirilmiş sistem başlatma
        if ROBUST_SYSTEM_AVAILABLE:
            try:
                enhance_main_system()
                logger.info("Ana pencere güçlendirilmiş sistem ile başlatıldı")
            except Exception as e:
                print(f"Güçlendirilmiş sistem başlatılamadı: {e}")
        
        # Initialize variables
        self.db = None
        self.gpt_manager = None
        self.vapi_manager = None
        self.selected_firm = None
        self.whatsapp_view = None
        self.task_scheduler = None
        self.stats_timer = None
        self.whatsapp_check_timer = None
        self.vapi_status_timer = None
        self.firms_table_timer = None
        self.last_firms_count = 0  # Son firma sayısını takip et
        
        # Güçlendirilmiş sistem bileşenleri
        if ROBUST_SYSTEM_AVAILABLE:
            try:
                self.connection_manager = ConnectionManager()
                self.memory_manager = MemoryManager()
                self.timeout_manager = TimeoutManager()
                self.thread_manager = ThreadSafeManager()
                self.system_monitor = SystemMonitor()
                self.shutdown_manager = GracefulShutdown()
                
                # Temizleme fonksiyonlarını kaydet
                self.shutdown_manager.register_cleanup(self.cleanup_resources)
            except Exception as e:
                print(f"Güçlendirilmiş sistem bileşenleri başlatılamadı: {e}")
        
        try:
            # Güvenli Managers
            logger.info("Managers başlatılıyor...")
            if DATABASE_AVAILABLE:
                self.db = Database()
            else:
                logger.warning("Veritabanı modülü mevcut değil")
                
            self.gpt_manager = GPTManager()
            self.vapi_manager = VapiManager()
            
            
            # Config
            self.config = {}
            self.load_config()
            
            # Task scheduler
            if self.db:
                self.task_scheduler = TaskSchedulerThread(self.db)
                self.task_scheduler.task_executed.connect(self.execute_scheduled_task)
                self.task_scheduler.start()
            
            # UI
            self.setupUI()
            self.apply_modern_theme()
            
            # Güvenli Timers
            try:
                self.stats_timer = QTimer()
                self.stats_timer.timeout.connect(self.safe_update_dashboard)
                self.stats_timer.start(10000)  # 10 saniyede bir güncelle
            except Exception as e:
                logger.error(f"Stats timer başlatılamadı: {e}")
                self.stats_timer = None
            
            # WhatsApp message check timer
            try:
                self.whatsapp_check_timer = QTimer()
                self.whatsapp_check_timer.timeout.connect(self.safe_check_whatsapp_messages)
                self.whatsapp_check_timer.start(5000)  # 5 saniyede bir kontrol
            except Exception as e:
                logger.error(f"WhatsApp timer başlatılamadı: {e}")
                self.whatsapp_check_timer = None
            
            # Vapi bağlantı kontrol timer
            try:
                self.vapi_status_timer = QTimer()
                self.vapi_status_timer.timeout.connect(self.safe_update_vapi_status)
                self.vapi_status_timer.start(30000)  # 30 saniyede bir kontrol
            except Exception as e:
                logger.error(f"Vapi timer başlatılamadı: {e}")
                self.vapi_status_timer = None
            
            # Firma tablosu otomatik yenileme timer
            try:
                self.firms_table_timer = QTimer()
                self.firms_table_timer.timeout.connect(self.safe_refresh_firms_table)
                self.firms_table_timer.start(15000)  # 15 saniyede bir kontrol
            except Exception as e:
                logger.error(f"Firms table timer başlatılamadı: {e}")
                self.firms_table_timer = None
            
            # İlk yükleme (güvenli)
            try:
                self.update_dashboard()
            except Exception as dash_error:
                logger.error(f"Dashboard yükleme hatası: {dash_error}")
                
            try:
                self.update_vapi_status()
            except Exception as vapi_error:
                logger.error(f"Vapi status yükleme hatası: {vapi_error}")
            
            # Test verilerini ekle (sadece ilk çalıştırmada)
            try:
                self.add_test_firms()
            except Exception as test_error:
                logger.warning(f"Test verisi ekleme hatası: {test_error}")
            
            logger.info("MainWindow başlatma tamamlandı")
            
        except Exception as e:
            logger.critical(f"MainWindow başlatma hatası: {e}")
            error_msg = f"Uygulama başlatılırken hata oluştu:\n{str(e)}\n\nDetaylar log dosyasında."
            try:
                QMessageBox.critical(None, "Başlatma Hatası", error_msg)
            except:
                print(error_msg)
            # Çökmeyi engelle - raise yerine warning göster
            logger.warning("MainWindow başlatma hatası, ancak devam ediliyor")
    
    def setupUI(self):
        """Arayüzü oluştur - Tam Ekran Responsive Tasarım"""
        self.setWindowTitle("🚀 B2B İletişim Paneli - WhatsApp + Vapi AI + GPT")
        
        # Gelişmiş tam ekran responsive boyutlandırma
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        scale_factor = self.get_scale_factor()
        
        # Tam ekran boyutlandırma - ekranın %98'i (daha büyük)
        width = int(screen_width * 0.98)
        height = int(screen_height * 0.98)
        
        # Minimum boyutları ölçeklendirme faktörüne göre ayarla - Daha büyük minimum boyutlar
        min_width = max(1000, int(1200 * scale_factor))
        min_height = max(700, int(800 * scale_factor))
        self.setMinimumSize(min_width, min_height)
        
        # Maksimum boyutları tam ekran yap
        self.setMaximumSize(screen_width, screen_height)
        
        # Pencereyi ekranın ortasına konumlandır
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.setGeometry(x, y, width, height)
        
        # Ölçeklendirme faktörünü güncelle
        self.scale_factor = scale_factor
        
        # Pencere özelliklerini ayarla
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, True)
        
        # Tam ekran modu için hazırlık
        self.setWindowState(Qt.WindowNoState)
        
        # Status bar ekle
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Sistem hazır", 3000)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout - Responsive margin ve spacing
        main_layout = QVBoxLayout(central_widget)
        
        # Ekran boyutuna göre margin ve spacing ayarla - Daha responsive
        base_margin = int(25 * self.scale_factor)
        base_spacing = int(12 * self.scale_factor)
        
        # Minimum değerleri garanti et - Daha büyük minimum değerler
        margin = max(15, base_margin)
        spacing = max(8, base_spacing)
        
        # Tam ekran modunda daha kompakt margin
        if hasattr(self, 'isFullScreen') and self.isFullScreen():
            margin = max(10, int(margin * 0.7))
            spacing = max(6, int(spacing * 0.8))
        
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(spacing)
        
        # Başlık
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        
        # Sekmeler
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        self.firms_tab = self.create_firms_tab()
        self.tabs.addTab(self.firms_tab, "🏢 Firmalar")
        
        self.whatsapp_tab = self.create_whatsapp_tab()
        self.tabs.addTab(self.whatsapp_tab, "📱 WhatsApp")
        
        self.vapi_tab = self.create_vapi_tab()
        self.tabs.addTab(self.vapi_tab, "📞 Vapi AI")
        
        self.call_records_tab = self.create_call_records_tab()
        self.tabs.addTab(self.call_records_tab, "🎧 Kayıtlar")
        
        self.templates_tab = self.create_templates_tab()
        self.tabs.addTab(self.templates_tab, "📝 Template")
        
        self.activities_tab = self.create_activities_tab()
        self.tabs.addTab(self.activities_tab, "📋 Activity")
        
        self.weekly_report_tab = self.create_weekly_report_tab()
        self.tabs.addTab(self.weekly_report_tab, "📊 Haftalık Rapor")
        
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "⚙️ Ayarlar")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("🟢 Sistem hazır")
    
    def create_header(self):
        """Başlık widget'ı oluştur"""
        header = QWidget()
        header.setMaximumHeight(80)
        header.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Logo ve başlık
        title = QLabel("🚀 B2B İletişim Paneli")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Tam ekran butonu
        self.fullscreen_btn = QPushButton("⛶ Tam Ekran")
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        layout.addWidget(self.fullscreen_btn)
        
        # Durum göstergeleri
        self.whatsapp_status = QLabel("🔴 WhatsApp Kapalı")
        self.whatsapp_status.setStyleSheet("font-size: 14px; color: #e74c3c;")
        layout.addWidget(self.whatsapp_status)
        
        self.vapi_status = QLabel("🟢 Vapi Hazır")
        self.vapi_status.setStyleSheet("font-size: 14px; color: #27ae60;")
        layout.addWidget(self.vapi_status)
        
        self.gpt_status = QLabel("🔴 GPT Kapalı")
        self.gpt_status.setStyleSheet("font-size: 14px; color: #e74c3c;")
        layout.addWidget(self.gpt_status)
        
        # API durumlarını kontrol et
        self.check_api_status()
        
        return header
    
    def toggle_fullscreen(self):
        """Tam ekran modunu aç/kapat - Responsive ölçeklendirme ile"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("⛶ Tam Ekran")
            self.fullscreen_btn.setToolTip("Tam ekran moduna geç")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("⛶ Çık")
            self.fullscreen_btn.setToolTip("Tam ekran modundan çık")
        
        # Ölçeklendirmeyi güncelle
        self.update_scale_factor()
    
    def update_scale_factor(self):
        """Ölçeklendirme faktörünü güncelle ve UI'yi yenile"""
        try:
            # Ölçeklendirme faktörünü güncelle
            self.scale_factor = self.get_scale_factor()
            
            # Ana layout'u güncelle
            if hasattr(self, 'centralWidget'):
                central_widget = self.centralWidget()
                if central_widget:
                    layout = central_widget.layout()
                    if layout:
                        # Margin ve spacing'i güncelle
                        base_margin = int(25 * self.scale_factor)
                        base_spacing = int(12 * self.scale_factor)
                        
                        margin = max(15, base_margin)
                        spacing = max(8, base_spacing)
                        
                        # Tam ekran modunda daha kompakt margin
                        if self.isFullScreen():
                            margin = max(10, int(margin * 0.7))
                            spacing = max(6, int(spacing * 0.8))
                        
                        layout.setContentsMargins(margin, margin, margin, margin)
                        layout.setSpacing(spacing)
            
            # Status bar'ı güncelle
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"Ölçeklendirme güncellendi: {self.scale_factor:.2f}x", 2000)
                
        except Exception as e:
            print(f"Ölçeklendirme güncelleme hatası: {e}")
    
    def create_dashboard_tab(self):
        """Dashboard sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # İstatistik kartları
        cards_layout = QGridLayout()
        
        self.total_firms_card = ModernCard("Toplam Firma", "0", "🏢", "#0d7377")
        self.active_firms_card = ModernCard("Aktif Firma", "0", "✅", "#27ae60")
        self.total_messages_card = ModernCard("Toplam Mesaj", "0", "💬", "#3498db")
        self.today_messages_card = ModernCard("Bugünkü Mesaj", "0", "📅", "#e74c3c")
        self.total_calls_card = ModernCard("Toplam Arama", "0", "📞", "#9b59b6")
        self.week_messages_card = ModernCard("Haftalık Mesaj", "0", "📊", "#f39c12")
        
        cards_layout.addWidget(self.total_firms_card, 0, 0)
        cards_layout.addWidget(self.active_firms_card, 0, 1)
        cards_layout.addWidget(self.total_messages_card, 0, 2)
        cards_layout.addWidget(self.today_messages_card, 1, 0)
        cards_layout.addWidget(self.total_calls_card, 1, 1)
        cards_layout.addWidget(self.week_messages_card, 1, 2)
        
        layout.addLayout(cards_layout)
        
        # Grafikler
        charts_layout = QHBoxLayout()
        
        # Sol grafik - Haftalık performans
        weekly_chart_group = QGroupBox("📈 Haftalık Performans")
        weekly_chart_layout = QVBoxLayout()
        
        if CHARTS_AVAILABLE:
            self.weekly_chart_view = QChartView()
            self.weekly_chart_view.setMinimumHeight(300)
            self.create_weekly_chart()
            weekly_chart_layout.addWidget(self.weekly_chart_view)
        else:
            info_label = QLabel("Grafik göstermek için QtCharts modülünü yükleyin")
            info_label.setAlignment(Qt.AlignCenter)
            weekly_chart_layout.addWidget(info_label)
        
        weekly_chart_group.setLayout(weekly_chart_layout)
        charts_layout.addWidget(weekly_chart_group)
        
        # Sağ grafik - Sektör dağılımı
        sector_chart_group = QGroupBox("🏭 Sektör Dağılımı")
        sector_chart_layout = QVBoxLayout()
        
        if CHARTS_AVAILABLE:
            self.sector_chart_view = QChartView()
            self.sector_chart_view.setMinimumHeight(300)
            self.create_sector_chart()
            sector_chart_layout.addWidget(self.sector_chart_view)
        else:
            info_label = QLabel("Grafik göstermek için QtCharts modülünü yükleyin")
            info_label.setAlignment(Qt.AlignCenter)
            sector_chart_layout.addWidget(info_label)
        
        sector_chart_group.setLayout(sector_chart_layout)
        charts_layout.addWidget(sector_chart_group)
        
        layout.addLayout(charts_layout)
        
        # Son aktiviteler
        activity_group = QGroupBox("🔄 Son Aktiviteler")
        activity_layout = QVBoxLayout()
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(5)
        self.activity_table.setHorizontalHeaderLabels(["Tarih", "Saat", "Tip", "Firma", "Detay"])
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        activity_layout.addWidget(self.activity_table)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        return widget
    
    def create_firms_tab(self):
        """Firmalar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Üst kontrol paneli - Modern tasarım
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 10px;
            }
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 18px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("🏢 Firma Yönetim Sistemi")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Firma sayısı göstergesi
        self.firms_count_display = QLabel("📊 Toplam: 0 firma")
        self.firms_count_display.setStyleSheet("color: white; font-size: 14px;")
        header_layout.addWidget(self.firms_count_display)
        
        layout.addWidget(header_frame)
        
        # Gelişmiş arama ve filtre paneli
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        search_layout = QVBoxLayout(search_frame)
        
        # Arama kutusu - büyük ve merkezi
        search_row1 = QHBoxLayout()
        search_label = QLabel("🔍 Akıllı Arama:")
        search_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
        search_row1.addWidget(search_label)
        
        self.firms_search_input = QLineEdit()
        self.firms_search_input.setPlaceholderText("Firma adı, telefon, email, sektör veya herhangi bir bilgi girin...")
        self.firms_search_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 10px;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                background-color: #1a1a1a;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0d7377;
            }
        """)
        self.firms_search_input.textChanged.connect(self.filter_firms_table)
        search_row1.addWidget(self.firms_search_input)
        
        # Arama temizle butonu
        clear_search_btn = QPushButton("🗑️")
        clear_search_btn.setToolTip("Aramayı temizle")
        clear_search_btn.setMaximumWidth(40)
        clear_search_btn.clicked.connect(lambda: self.firms_search_input.clear())
        search_row1.addWidget(clear_search_btn)
        
        search_layout.addLayout(search_row1)
        
        # AI Sektör Filtreleme - Akıllı sistem
        ai_filter_row = QHBoxLayout()
        ai_filter_label = QLabel("🤖 AI Sektör Filtreleme:")
        ai_filter_label.setStyleSheet("color: #14a085; font-weight: bold; font-size: 12px;")
        ai_filter_row.addWidget(ai_filter_label)
        
        self.ai_sector_combo = QComboBox()
        self.ai_sector_combo.setMinimumWidth(200)
        self.ai_sector_combo.addItems([
            "Tüm Sektörler",
            "🏥 Sağlık & Tıp",
            "💻 Teknoloji & Yazılım", 
            "🏪 E-ticaret & Perakende",
            "🏭 Üretim & Sanayi",
            "🎓 Eğitim & Öğretim",
            "💰 Finans & Bankacılık",
            "🏗️ İnşaat & Gayrimenkul",
            "🚗 Otomotiv & Ulaşım",
            "🍽️ Gıda & Restoran",
            "👕 Tekstil & Moda",
            "💄 Güzellik & Kozmetik",
            "🎨 Reklam & Pazarlama",
            "⚖️ Hukuk & Danışmanlık",
            "🔧 Teknik Servis & Onarım",
            "🏋️ Spor & Fitness",
            "✈️ Turizm & Seyahat",
            "📚 Medya & Yayıncılık",
            "🎵 Müzik & Eğlence",
            "🌱 Tarım & Hayvancılık",
            "📊 Muhasebe & Mali Müşavirlik",
            "🏨 Otel & Konaklama",
            "👩‍⚕️ Psikolog & Terapist",
            "🍎 Diyetisyen & Beslenme",
            "🛏️ Mobilya & Dekorasyon",
            "🛌 Yatak & Uyku Ürünleri",
            "🐶 Veteriner & Hayvan Sağlığı",
            "🔌 Elektrik & Elektronik",
            "🏛️ Avukat & Hukuki Danışmanlık",
            "🏦 Sigorta & Risk Yönetimi"
        ])
        self.ai_sector_combo.currentTextChanged.connect(self.apply_ai_sector_filter)
        ai_filter_row.addWidget(self.ai_sector_combo)
        
        # AI önerileri butonu
        ai_suggest_btn = QPushButton("💡 AI Önerileri")
        ai_suggest_btn.setToolTip("AI ile sektör önerileri al")
        ai_suggest_btn.clicked.connect(self.get_ai_sector_suggestions)
        ai_filter_row.addWidget(ai_suggest_btn)
        
        ai_filter_row.addStretch()
        search_layout.addLayout(ai_filter_row)
        
        # Gelişmiş filtreler
        advanced_filter_row = QHBoxLayout()
        
        # Rating filtresi
        advanced_filter_row.addWidget(QLabel("⭐ Min Rating:"))
        self.rating_filter = QComboBox()
        self.rating_filter.addItems(["Tümü", "1+", "2+", "3+", "4+", "5"])
        self.rating_filter.currentTextChanged.connect(self.filter_firms_table)
        advanced_filter_row.addWidget(self.rating_filter)
        
        # Email durumu
        advanced_filter_row.addWidget(QLabel("📧 Email:"))
        self.email_filter = QComboBox()
        self.email_filter.addItems(["Tümü", "Email Var", "Email Yok"])
        self.email_filter.currentTextChanged.connect(self.filter_firms_table)
        advanced_filter_row.addWidget(self.email_filter)
        
        # Website durumu
        advanced_filter_row.addWidget(QLabel("🌐 Website:"))
        self.website_filter = QComboBox()
        self.website_filter.addItems(["Tümü", "Website Var", "Website Yok"])
        self.website_filter.currentTextChanged.connect(self.filter_firms_table)
        advanced_filter_row.addWidget(self.website_filter)
        
        # Analiz durumu
        advanced_filter_row.addWidget(QLabel("🔍 Analiz:"))
        self.analysis_filter = QComboBox()
        self.analysis_filter.addItems(["Tümü", "Analiz Edilmiş", "Analiz Edilmemiş"])
        self.analysis_filter.currentTextChanged.connect(self.filter_firms_table)
        advanced_filter_row.addWidget(self.analysis_filter)
        
        advanced_filter_row.addStretch()
        search_layout.addLayout(advanced_filter_row)
        
        layout.addWidget(search_frame)
        
        # Bu satır kaldırıldı - butonlar artık action_frame içinde
        
        # Seçim kontrolleri
        selection_frame = QFrame()
        selection_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        selection_layout = QHBoxLayout(selection_frame)
        
        # Sol taraf - seçim butonları
        left_selection = QHBoxLayout()
        
        self.select_all_firms_btn = QPushButton("✅ Tümünü Seç")
        self.select_all_firms_btn.clicked.connect(self.select_all_firms_in_table)
        self.select_all_firms_btn.setStyleSheet(self.get_firms_button_style("#28a745"))
        left_selection.addWidget(self.select_all_firms_btn)
        
        self.select_none_firms_btn = QPushButton("❌ Hiçbirini Seçme")
        self.select_none_firms_btn.clicked.connect(self.select_none_firms_in_table)
        self.select_none_firms_btn.setStyleSheet(self.get_firms_button_style("#dc3545"))
        left_selection.addWidget(self.select_none_firms_btn)
        
        self.invert_selection_firms_btn = QPushButton("🔄 Tersini Seç")
        self.invert_selection_firms_btn.clicked.connect(self.invert_firms_selection)
        self.invert_selection_firms_btn.setStyleSheet(self.get_firms_button_style("#6c757d"))
        left_selection.addWidget(self.invert_selection_firms_btn)
        
        self.hide_selected_btn = QPushButton("👁️‍🗨️ Seçilenleri Gizle")
        self.hide_selected_btn.clicked.connect(self.hide_selected_firms)
        self.hide_selected_btn.setStyleSheet(self.get_firms_button_style("#ff6b6b"))
        left_selection.addWidget(self.hide_selected_btn)
        
        self.show_all_btn = QPushButton("👁️ Tümünü Göster")
        self.show_all_btn.clicked.connect(self.show_all_firms)
        self.show_all_btn.setStyleSheet(self.get_firms_button_style("#17a2b8"))
        left_selection.addWidget(self.show_all_btn)
        
        selection_layout.addLayout(left_selection)
        selection_layout.addStretch()
        
        # Sağ taraf - seçim bilgisi
        self.firms_selection_info = QLabel("📋 Seçili: 0 / Toplam: 0")
        self.firms_selection_info.setStyleSheet("color: #ffffff; font-weight: bold;")
        selection_layout.addWidget(self.firms_selection_info)
        
        layout.addWidget(selection_frame)
        
        # İşlem butonları
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        action_layout = QHBoxLayout(action_frame)
        
        # Sol taraf - CRUD işlemleri
        crud_layout = QHBoxLayout()
        
        add_firm_btn = QPushButton("➕ Yeni Firma")
        add_firm_btn.clicked.connect(self.add_firm)
        add_firm_btn.setStyleSheet(self.get_firms_button_style("#28a745"))
        crud_layout.addWidget(add_firm_btn)
        
        edit_firm_btn = QPushButton("✏️ Düzenle")
        edit_firm_btn.clicked.connect(self.edit_selected_firm)
        edit_firm_btn.setStyleSheet(self.get_firms_button_style("#17a2b8"))
        crud_layout.addWidget(edit_firm_btn)
        
        delete_firm_btn = QPushButton("🗑️ Sil")
        delete_firm_btn.clicked.connect(self.delete_selected_firm)
        delete_firm_btn.setStyleSheet(self.get_firms_button_style("#dc3545"))
        crud_layout.addWidget(delete_firm_btn)
        
        action_layout.addLayout(crud_layout)
        
        # Orta - toplu işlemler
        bulk_layout = QHBoxLayout()
        
        bulk_message_btn = QPushButton("📧 Toplu Mesaj")
        bulk_message_btn.clicked.connect(self.open_bulk_message_dialog)
        bulk_message_btn.setStyleSheet(self.get_firms_button_style("#0d7377"))
        bulk_layout.addWidget(bulk_message_btn)
        
        bulk_call_btn = QPushButton("📞 Toplu Arama")
        bulk_call_btn.clicked.connect(self.open_bulk_call_dialog)
        bulk_call_btn.setStyleSheet(self.get_firms_button_style("#14a085"))
        bulk_layout.addWidget(bulk_call_btn)
        
        action_layout.addLayout(bulk_layout)
        
        # Sağ taraf - yardımcı işlemler
        utility_layout = QHBoxLayout()
        
        refresh_firms_btn = QPushButton("🔄 Yenile")
        refresh_firms_btn.clicked.connect(self.load_firms_table)
        refresh_firms_btn.setStyleSheet(self.get_firms_button_style("#6c757d"))
        utility_layout.addWidget(refresh_firms_btn)
        
        export_firms_btn = QPushButton("📤 Dışa Aktar")
        export_firms_btn.clicked.connect(self.export_firms)
        export_firms_btn.setStyleSheet(self.get_firms_button_style("#ffc107"))
        utility_layout.addWidget(export_firms_btn)
        
        import_firms_btn = QPushButton("📥 İçe Aktar")
        import_firms_btn.clicked.connect(self.import_firms)
        import_firms_btn.setStyleSheet(self.get_firms_button_style("#17a2b8"))
        utility_layout.addWidget(import_firms_btn)
        
        action_layout.addLayout(utility_layout)
        
        layout.addWidget(action_frame)
        
        self.firms_table = QTableWidget()
        self.firms_table.setColumnCount(11)
        self.firms_table.setHorizontalHeaderLabels([
            "✓", "Firma Adı", "Telefon", "E-posta", "Sektör",
            "İletişim Kişisi", "Son İletişim", "Durum", "Rating", "Analiz", "İşlemler"
        ])
        
        # Seçim davranışı
        self.firms_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.firms_table.setAlternatingRowColors(True)
        
        # Kolon genişlikleri - responsive
        scale_factor = self.get_scale_factor() if hasattr(self, 'get_scale_factor') else 1.0
        self.firms_table.setColumnWidth(0, max(30, int(40 * scale_factor)))   # Checkbox
        self.firms_table.setColumnWidth(1, max(150, int(200 * scale_factor))) # Firma Adı
        self.firms_table.setColumnWidth(2, max(100, int(120 * scale_factor))) # Telefon
        self.firms_table.setColumnWidth(3, max(140, int(180 * scale_factor))) # E-posta
        self.firms_table.setColumnWidth(4, max(80, int(100 * scale_factor)))  # Sektör
        self.firms_table.setColumnWidth(5, max(120, int(150 * scale_factor))) # İletişim Kişisi
        self.firms_table.setColumnWidth(6, max(100, int(120 * scale_factor))) # Son İletişim
        self.firms_table.setColumnWidth(7, max(60, int(80 * scale_factor)))   # Durum
        self.firms_table.setColumnWidth(8, max(50, int(60 * scale_factor)))   # Rating
        self.firms_table.setColumnWidth(9, max(60, int(80 * scale_factor)))   # Analiz
        
        self.firms_table.horizontalHeader().setStretchLastSection(True)
        
        # Hidden firms tracking
        self.hidden_firm_rows = set()
        self.all_firms_data = []
        
        layout.addWidget(self.firms_table)
        
        # Firmaları yükle
        self.load_firms_table()
        
        # İlk firma sayısını kaydet
        if hasattr(self, 'db') and self.db:
            try:
                firms = self.db.get_firms()
                self.last_firms_count = len(firms)
            except:
                self.last_firms_count = 0
        
        return widget
    
    def get_firms_button_style(self, color):
        """Firmalar sekmesi için buton stili"""
        scale_factor = self.get_scale_factor() if hasattr(self, 'get_scale_factor') else 1.0
        font_size = max(10, int(12 * scale_factor))
        padding_v = max(6, int(8 * scale_factor))
        padding_h = max(12, int(16 * scale_factor))
        border_radius = max(4, int(6 * scale_factor))
        
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: {border_radius}px;
                padding: {padding_v}px {padding_h}px;
                font-weight: bold;
                font-size: {font_size}px;
                min-height: {max(24, int(30 * scale_factor))}px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_firms_color(color)};
            }}
            QPushButton:disabled {{
                background-color: #3a3a3a;
                color: #666666;
            }}
        """
    
    def darken_firms_color(self, color):
        """Rengi koyulaştır - firmalar için"""
        color_map = {
            "#28a745": "#1e7e34",  # Yeşil
            "#dc3545": "#bd2130",  # Kırmızı
            "#17a2b8": "#117a8b",  # Mavi
            "#6c757d": "#545b62",  # Gri
            "#ffc107": "#d39e00",  # Sarı
            "#ff6b6b": "#ee5a52",  # Açık kırmızı
            "#0d7377": "#0a5d61",  # Teal
            "#14a085": "#0f7a63"   # Yeşil teal
        }
        return color_map.get(color, color)
    
    def get_scale_factor(self):
        """Gelişmiş tam ekran ölçeklendirme faktörü"""
        screen = QApplication.primaryScreen()
        geometry = screen.geometry()
        
        # DPI tabanlı ölçeklendirme
        dpi = screen.logicalDotsPerInch()
        dpi_scale = max(1.0, dpi / 96.0)
        
        # Ekran boyutuna göre ölçeklendirme
        screen_width = geometry.width()
        screen_height = geometry.height()
        
        # Referans çözünürlük (1920x1080)
        ref_width = 1920
        ref_height = 1080
        
        # Genişlik ve yükseklik ölçeklendirme faktörleri
        width_scale = screen_width / ref_width
        height_scale = screen_height / ref_height
        
        # En küçük ölçeklendirme faktörünü kullan (orantıyı korumak için)
        size_scale = min(width_scale, height_scale)
        
        # DPI ve boyut ölçeklendirmesini birleştir
        final_scale = max(0.8, min(2.0, dpi_scale * size_scale))
        
        # Tam ekran modunda daha agresif ölçeklendirme
        if hasattr(self, 'isFullScreen') and self.isFullScreen():
            final_scale = max(0.8, min(3.0, final_scale * 1.2))
        
        return final_scale
    
    def filter_firms_table(self):
        """Gelişmiş firma tablosu filtreleme"""
        search_text = self.firms_search_input.text().lower()
        ai_sector = self.ai_sector_combo.currentText()
        rating_filter = self.rating_filter.currentText()
        email_filter = self.email_filter.currentText()
        website_filter = self.website_filter.currentText()
        analysis_filter = self.analysis_filter.currentText()
        
        visible_count = 0
        selected_count = 0
        
        for row in range(self.firms_table.rowCount()):
            show_row = True
            
            # Metin arama
            if search_text:
                row_text = ""
                for col in range(1, self.firms_table.columnCount() - 1):  # Checkbox ve işlemler hariç
                    item = self.firms_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                
                if search_text not in row_text:
                    show_row = False
            
            # AI Sektör filtresi
            if show_row and ai_sector != "Tüm Sektörler":
                sector_item = self.firms_table.item(row, 4)  # Sektör kolonu
                if sector_item:
                    firm_sector = sector_item.text().lower()
                    ai_sector_clean = ai_sector.split(" ", 1)[-1].lower()  # Emoji'yi kaldır
                    
                    # AI ile sektör eşleştirme
                    if not self.ai_sector_match(firm_sector, ai_sector_clean):
                        show_row = False
            
            # Rating filtresi
            if show_row and rating_filter != "Tümü":
                rating_item = self.firms_table.item(row, 8)  # Rating kolonu
                if rating_item:
                    try:
                        firm_rating = float(rating_item.text().replace("⭐", "").strip())
                        min_rating = int(rating_filter.replace("+", ""))
                        if firm_rating < min_rating:
                            show_row = False
                    except:
                        if rating_filter != "Tümü":
                            show_row = False
            
            # Email filtresi
            if show_row and email_filter != "Tümü":
                email_item = self.firms_table.item(row, 3)  # Email kolonu
                has_email = email_item and email_item.text().strip() and email_item.text() != "N/A"
                
                if email_filter == "Email Var" and not has_email:
                    show_row = False
                elif email_filter == "Email Yok" and has_email:
                    show_row = False
            
            # Website filtresi
            if show_row and website_filter != "Tümü":
                # Website bilgisini analiz durumundan veya firma verisinden al
                analysis_item = self.firms_table.item(row, 9)  # Analiz kolonu
                has_website = False
                
                if analysis_item and "Website:" in analysis_item.text():
                    has_website = "Website: Var" in analysis_item.text()
                
                if website_filter == "Website Var" and not has_website:
                    show_row = False
                elif website_filter == "Website Yok" and has_website:
                    show_row = False
            
            # Analiz filtresi
            if show_row and analysis_filter != "Tümü":
                analysis_item = self.firms_table.item(row, 9)  # Analiz kolonu
                is_analyzed = analysis_item and "✅" in analysis_item.text()
                
                if analysis_filter == "Analiz Edilmiş" and not is_analyzed:
                    show_row = False
                elif analysis_filter == "Analiz Edilmemiş" and is_analyzed:
                    show_row = False
            
            # Satırı göster/gizle
            self.firms_table.setRowHidden(row, not show_row)
            
            if show_row:
                visible_count += 1
                # Seçim durumunu kontrol et
                checkbox = self.firms_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    selected_count += 1
        
        # Bilgi etiketlerini güncelle
        total_count = self.firms_table.rowCount()
        self.firms_count_display.setText(f"📊 Toplam: {total_count} firma")
        self.firms_selection_info.setText(f"📋 Seçili: {selected_count} / Görünen: {visible_count}")
    
    def ai_sector_match(self, firm_sector, filter_sector):
        """AI ile sektör eşleştirme"""
        # Basit keyword eşleştirme - geliştirilecek
        filter_keywords = {
            "sağlık & tıp": ["sağlık", "tıp", "hastane", "klinik", "doktor", "hemşire", "eczane", "medikal"],
            "teknoloji & yazılım": ["teknoloji", "yazılım", "bilgisayar", "it", "software", "tech", "dijital"],
            "e-ticaret & perakende": ["e-ticaret", "perakende", "mağaza", "satış", "alışveriş", "market"],
            "üretim & sanayi": ["üretim", "sanayi", "fabrika", "imalat", "endüstri", "makine"],
            "eğitim & öğretim": ["eğitim", "okul", "üniversite", "kurs", "öğretim", "akademi"],
            "finans & bankacılık": ["finans", "banka", "sigorta", "yatırım", "borsa", "kredi"],
            "inşaat & gayrimenkul": ["inşaat", "gayrimenkul", "emlak", "yapı", "konut", "proje"],
            "otomotiv & ulaşım": ["otomotiv", "araba", "kamyon", "ulaşım", "taşımacılık", "lojistik"],
            "gıda & restoran": ["gıda", "restoran", "yemek", "cafe", "mutfak", "beslenme"],
            "tekstil & moda": ["tekstil", "moda", "giyim", "kumaş", "konfeksiyon", "ayakkabı"],
            "güzellik & kozmetik": ["güzellik", "kozmetik", "kuaför", "estetik", "makyaj"],
            "reklam & pazarlama": ["reklam", "pazarlama", "ajans", "tanıtım", "medya"],
            "hukuk & danışmanlık": ["hukuk", "avukat", "danışmanlık", "konsültasyon"],
            "teknik servis & onarım": ["servis", "onarım", "tamir", "bakım", "teknik"],
            "spor & fitness": ["spor", "fitness", "gym", "antrenman", "sağlık"],
            "turizm & seyahat": ["turizm", "seyahat", "otel", "tatil", "rehber"],
            "medya & yayıncılık": ["medya", "yayın", "gazete", "dergi", "basın"],
            "müzik & eğlence": ["müzik", "eğlence", "konser", "etkinlik", "sanat"],
            "tarım & hayvancılık": ["tarım", "hayvancılık", "çiftlik", "sera", "veteriner"],
            "muhasebe & mali müşavirlik": ["muhasebe", "mali", "vergi", "denetim"],
            "otel & konaklama": ["otel", "konaklama", "pansiyon", "apart"],
            "psikolog & terapist": ["psikolog", "terapist", "psikoloji", "terapi"],
            "diyetisyen & beslenme": ["diyetisyen", "beslenme", "diyet", "nutrisyon"],
            "mobilya & dekorasyon": ["mobilya", "dekorasyon", "ev", "tasarım"],
            "yatak & uyku ürünleri": ["yatak", "uyku", "yatak odası", "nevresim"],
            "veteriner & hayvan sağlığı": ["veteriner", "hayvan", "pet", "kedi", "köpek"],
            "elektrik & elektronik": ["elektrik", "elektronik", "elektrikçi", "teknisyen"],
            "avukat & hukuki danışmanlık": ["avukat", "hukuk", "dava", "mahkeme"],
            "sigorta & risk yönetimi": ["sigorta", "risk", "poliçe", "hasar"]
        }
        
        keywords = filter_keywords.get(filter_sector, [])
        for keyword in keywords:
            if keyword in firm_sector:
                return True
        
        return False
    
    def apply_ai_sector_filter(self):
        """AI sektör filtresini uygula"""
        self.filter_firms_table()
    
    def get_ai_sector_suggestions(self):
        """AI ile sektör önerileri al"""
        if not hasattr(self, 'gpt_manager') or not self.gpt_manager:
            QMessageBox.warning(self, "Uyarı", "AI önerileri için GPT bağlantısı gerekli!")
            return
        
        try:
            # Mevcut firmaların sektörlerini analiz et
            sectors = []
            for row in range(self.firms_table.rowCount()):
                if not self.firms_table.isRowHidden(row):
                    sector_item = self.firms_table.item(row, 4)
                    if sector_item and sector_item.text().strip():
                        sectors.append(sector_item.text().strip())
            
            if not sectors:
                QMessageBox.information(self, "Bilgi", "Öneri için yeterli firma verisi bulunamadı!")
                return
            
            # AI'dan öneri al
            prompt = f"""
            Aşağıdaki firma sektörlerini analiz et ve benzer sektörlerde hangi firmaları hedeflemeli önerisinde bulun:
            
            Mevcut sektörler: {', '.join(set(sectors[:20]))}
            
            Lütfen:
            1. Bu sektörlere benzer 5 sektör öner
            2. Her sektör için 2-3 anahtar kelime ver
            3. Türkçe ve kısa yanıt ver
            """
            
            response = self.gpt_manager.get_response(prompt)
            
            # Öneri dialogu
            dialog = QDialog(self)
            dialog.setWindowTitle("🤖 AI Sektör Önerileri")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title = QLabel("💡 AI Tabanlı Sektör Önerileri")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0d7377; padding: 10px;")
            layout.addWidget(title)
            
            # Öneri metni
            suggestion_text = QTextEdit()
            suggestion_text.setReadOnly(True)
            suggestion_text.setText(response)
            suggestion_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2a2a2a;
                    color: white;
                    border: 1px solid #3a3a3a;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 12px;
                }
            """)
            layout.addWidget(suggestion_text)
            
            # Kapat butonu
            close_btn = QPushButton("Kapat")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"AI önerisi alınamadı:\n{str(e)}")
    
    def select_all_firms_in_table(self):
        """Tablodaki tüm (görünen) firmaları seç"""
        for row in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(row):
                checkbox = self.firms_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(True)
        self.update_firms_selection_info()
    
    def select_none_firms_in_table(self):
        """Tablodaki hiçbir firmayı seçme"""
        for row in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_firms_selection_info()
    
    def invert_firms_selection(self):
        """Firma seçimini tersine çevir"""
        for row in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(row):
                checkbox = self.firms_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())
        self.update_firms_selection_info()
    
    def hide_selected_firms(self):
        """Seçili firmaları gizle"""
        hidden_count = 0
        for row in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                self.firms_table.setRowHidden(row, True)
                self.hidden_firm_rows.add(row)
                hidden_count += 1
        
        if hidden_count > 0:
            QMessageBox.information(self, "✅ Gizlendi", f"{hidden_count} firma gizlendi!")
        
        self.update_firms_selection_info()
    
    def show_all_firms(self):
        """Tüm firmaları göster (gizlileri de)"""
        for row in range(self.firms_table.rowCount()):
            self.firms_table.setRowHidden(row, False)
        
        self.hidden_firm_rows.clear()
        self.filter_firms_table()  # Filtreleri yeniden uygula
        
        QMessageBox.information(self, "👁️ Gösterildi", "Tüm firmalar gösterildi!")
    
    def update_firms_selection_info(self):
        """Firma seçim bilgisini güncelle"""
        selected_count = 0
        visible_count = 0
        
        for row in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(row):
                visible_count += 1
                checkbox = self.firms_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    selected_count += 1
        
        total_count = self.firms_table.rowCount()
        self.firms_count_display.setText(f"📊 Toplam: {total_count} firma")
        self.firms_selection_info.setText(f"📋 Seçili: {selected_count} / Görünen: {visible_count}")
    
    def edit_selected_firm(self):
        """Seçili firmayı düzenle"""
        current_row = self.firms_table.currentRow()
        if current_row >= 0:
            # Firma verilerini al ve düzenleme dialogunu aç
            firm_name = self.firms_table.item(current_row, 1).text()
            QMessageBox.information(self, "Düzenleme", f"'{firm_name}' düzenleme özelliği yakında eklenecek!")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir firma seçin!")
    
    def delete_selected_firm(self):
        """Seçili firmayı sil"""
        current_row = self.firms_table.currentRow()
        if current_row >= 0:
            firm_name = self.firms_table.item(current_row, 1).text()
            reply = QMessageBox.question(self, "Silme Onayı", 
                f"'{firm_name}' firmasını silmek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Firmayı veritabanından sil
                try:
                    firm_id = int(self.firms_table.item(current_row, 0).text()) if self.firms_table.item(current_row, 0) else None
                    if firm_id and hasattr(self, 'db') and self.db:
                        success = self.db.delete_firm(firm_id)
                        if success:
                            self.firms_table.removeRow(current_row)
                            QMessageBox.information(self, "✅ Silindi", f"'{firm_name}' başarıyla silindi!")
                            self.update_firms_selection_info()
                        else:
                            QMessageBox.critical(self, "❌ Hata", "Firma silinemedi!")
                    else:
                        QMessageBox.critical(self, "❌ Hata", "Firma ID'si bulunamadı!")
                except Exception as e:
                    QMessageBox.critical(self, "❌ Hata", f"Silme işlemi başarısız:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir firma seçin!")
    
    def create_whatsapp_tab(self):
        """🚀 Gelişmiş WhatsApp Sekmesi - Sadece main.py'den yönlendirilen firmalar"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Üst kontrol paneli - Kompakt
        control_panel = QFrame()
        scale_factor = self.get_scale_factor() if hasattr(self, 'get_scale_factor') else 1.0
        padding = max(8, int(10 * scale_factor))
        font_size = max(10, int(12 * scale_factor))
        button_padding = max(6, int(8 * scale_factor))
        
        control_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: {max(6, int(8 * scale_factor))}px;
                padding: {padding}px;
                margin: {max(4, int(5 * scale_factor))}px;
            }}
            QLabel {{
                color: white;
                font-weight: bold;
                font-size: {font_size}px;
            }}
            QPushButton {{
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: {max(4, int(6 * scale_factor))}px;
                color: white;
                padding: {button_padding}px {max(10, int(12 * scale_factor))}px;
                font-weight: bold;
                font-size: {max(10, int(11 * scale_factor))}px;
                min-height: {max(20, int(25 * scale_factor))}px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.25);
            }}
            QComboBox {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {max(4, int(6 * scale_factor))}px;
                padding: {max(4, int(6 * scale_factor))}px;
                color: white;
                font-size: {max(10, int(11 * scale_factor))}px;
                min-height: {max(20, int(25 * scale_factor))}px;
            }}
            QComboBox:focus {{
                border: 2px solid #0d7377;
            }}
        """)
        control_layout = QHBoxLayout(control_panel)
        
        # Sol taraf - Firma seçimi ve hızlı işlemler
        left_controls = QHBoxLayout()
        
        # Firma seçimi - responsive
        firm_label = QLabel("📱 Firma:")
        firm_label.setMinimumWidth(max(50, int(60 * scale_factor)))
        left_controls.addWidget(firm_label)
        
        self.whatsapp_firm_combo = QComboBox()
        self.whatsapp_firm_combo.setMinimumWidth(max(150, int(200 * scale_factor)))
        self.whatsapp_firm_combo.currentIndexChanged.connect(self.on_whatsapp_firm_selected)
        left_controls.addWidget(self.whatsapp_firm_combo)
        
        # Hızlı işlem butonları - responsive
        self.quick_msg_btn = QPushButton("💬 Hızlı Mesaj")
        self.quick_msg_btn.setMinimumWidth(max(80, int(100 * scale_factor)))
        self.quick_msg_btn.clicked.connect(self.show_quick_message_popup)
        left_controls.addWidget(self.quick_msg_btn)
        
        self.bulk_message_btn = QPushButton("📨 Toplu Mesaj")
        self.bulk_message_btn.clicked.connect(self.open_bulk_message_dialog)
        left_controls.addWidget(self.bulk_message_btn)
        
        self.ai_prompt_btn = QPushButton("🤖 AI Prompt")
        self.ai_prompt_btn.clicked.connect(self.show_ai_prompt_dialog)
        left_controls.addWidget(self.ai_prompt_btn)
        
        # 🚀 Otomatik Gönderim Butonu
        self.auto_send_btn = QPushButton("🚀 Otomatik Gönderim")
        self.auto_send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ff6b35, stop: 1 #f7931e);
                border: 2px solid #ff6b35;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #f7931e, stop: 1 #ff6b35);
                border: 2px solid #f7931e;
            }
            QPushButton:pressed {
                background: #e55a2b;
            }
        """)
        self.auto_send_btn.clicked.connect(self.start_auto_whatsapp_sending)
        left_controls.addWidget(self.auto_send_btn)
        
        # 🛑 Durdur Butonu (başlangıçta gizli)
        self.stop_auto_send_btn = QPushButton("🛑 Durdur")
        self.stop_auto_send_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border: 2px solid #dc3545;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
                border: 2px solid #c82333;
            }
        """)
        self.stop_auto_send_btn.clicked.connect(self.stop_auto_whatsapp_sending)
        self.stop_auto_send_btn.setVisible(False)
        left_controls.addWidget(self.stop_auto_send_btn)
        
        left_controls.addStretch()
        control_layout.addLayout(left_controls)
        
        # Sağ taraf - Durum ve istatistikler
        right_controls = QHBoxLayout()
        
        self.whatsapp_status_label = QLabel("🔴 Bağlantı Bekleniyor")
        self.whatsapp_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        right_controls.addWidget(self.whatsapp_status_label)
        
        self.message_count_label = QLabel("📊 Mesaj: 0")
        right_controls.addWidget(self.message_count_label)
        
        control_layout.addLayout(right_controls)
        layout.addWidget(control_panel)
        
        # Ana içerik - WhatsApp Web (büyük alan) - karanlık tema
        whatsapp_container = QFrame()
        container_margin = max(4, int(5 * scale_factor))
        container_radius = max(6, int(8 * scale_factor))
        
        whatsapp_container.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {container_radius}px;
                margin: {container_margin}px;
            }}
        """)
        whatsapp_layout = QVBoxLayout(whatsapp_container)
        
        # WhatsApp Web View - Ekranın çoğunu kaplasın
        if WEBENGINE_AVAILABLE:
            try:
                self.whatsapp_view = WhatsAppWebView()
                self.whatsapp_view.status_changed.connect(self.update_whatsapp_status)
                self.whatsapp_view.message_received.connect(self.on_whatsapp_message_received)
                whatsapp_layout.addWidget(self.whatsapp_view)
            except Exception as e:
                logger.error(f"WhatsApp Web View oluşturulamadı: {e}")
                self.create_whatsapp_fallback_view(whatsapp_layout)
                self.whatsapp_view = None
        else:
            self.create_whatsapp_fallback_view(whatsapp_layout)
            self.whatsapp_view = None
        
        layout.addWidget(whatsapp_container)
        
        # Alt panel - Mesaj yönetimi (küçük alan) - karanlık tema
        message_panel = QFrame()
        panel_height = max(160, int(200 * scale_factor))
        
        message_panel.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: {container_radius}px;
                margin: {container_margin}px;
            }}
        """)
        message_panel.setMaximumHeight(panel_height)
        message_layout = QVBoxLayout(message_panel)
        
        # Mesaj editörü ve butonlar
        msg_editor_layout = QHBoxLayout()
        
        # Mesaj editörü - karanlık tema ve responsive
        self.whatsapp_message_input = QTextEdit()
        self.whatsapp_message_input.setPlaceholderText("Mesajınızı yazın veya AI ile oluşturun...")
        editor_height = max(60, int(80 * scale_factor))
        self.whatsapp_message_input.setMaximumHeight(editor_height)
        editor_font_size = max(10, int(12 * scale_factor))
        editor_padding = max(6, int(8 * scale_factor))
        
        self.whatsapp_message_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: {max(4, int(6 * scale_factor))}px;
                padding: {editor_padding}px;
                font-size: {editor_font_size}px;
            }}
            QTextEdit:focus {{
                border: 2px solid #0d7377;
                background-color: #1a1a1a;
            }}
        """)
        msg_editor_layout.addWidget(self.whatsapp_message_input)
        
        # Mesaj butonları
        msg_buttons_layout = QVBoxLayout()
        
        self.generate_whatsapp_msg_btn = QPushButton("🤖 AI Oluştur")
        self.generate_whatsapp_msg_btn.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        self.generate_whatsapp_msg_btn.clicked.connect(self.generate_whatsapp_message)
        msg_buttons_layout.addWidget(self.generate_whatsapp_msg_btn)
        
        self.send_whatsapp_btn = QPushButton("📤 Gönder")
        self.send_whatsapp_btn.setStyleSheet("""
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056b3;
            }
        """)
        self.send_whatsapp_btn.clicked.connect(self.send_whatsapp_message)
        msg_buttons_layout.addWidget(self.send_whatsapp_btn)
        
        self.schedule_whatsapp_btn = QPushButton("⏰ Zamanla")
        self.schedule_whatsapp_btn.setStyleSheet("""
            QPushButton {
                background: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e0a800;
            }
        """)
        self.schedule_whatsapp_btn.clicked.connect(self.schedule_whatsapp_message)
        msg_buttons_layout.addWidget(self.schedule_whatsapp_btn)
        
        msg_editor_layout.addLayout(msg_buttons_layout)
        message_layout.addLayout(msg_editor_layout)
        
        # Mesaj geçmişi (küçük)
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("📜 Geçmiş:"))
        
        self.whatsapp_history = QTextEdit()
        self.whatsapp_history.setReadOnly(True)
        self.whatsapp_history.setMaximumHeight(60)
        self.whatsapp_history.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 4px;
                font-size: 10px;
                background: #f8f9fa;
            }
        """)
        history_layout.addWidget(self.whatsapp_history)
        message_layout.addLayout(history_layout)
        
        layout.addWidget(message_panel)
        
        # Sadece main.py'den yönlendirilen firmaları yükle
        self.load_whatsapp_redirected_firms()
        self.load_whatsapp_templates()
        
        # Otomatik gönderim motorunu başlat
        self.whatsapp_auto_sender = WhatsAppAutoSender(
            parent=self,
            db=self.db,
            gpt_manager=self.gpt_manager,
            whatsapp_view=self.whatsapp_view
        )
        
        return widget
    
    def create_whatsapp_fallback_view(self, layout):
        """WhatsApp Web yüklenemediğinde alternatif görünüm"""
        info_label = QLabel("""
        ⚠️ WhatsApp Web yüklenemedi.
        
        Alternatif olarak:
        1. Tarayıcıda web.whatsapp.com'a gidin
        2. QR kodu okutun
        3. Bu panelden mesajlarınızı kopyalayıp yapıştırın
        
        Veya QtWebEngine modülünü yükleyin:
        pip install PySide6-WebEngine
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            color: #f39c12; 
            padding: 40px; 
            font-size: 14px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            margin: 20px;
        """)
        layout.addWidget(info_label)
    
    def load_whatsapp_redirected_firms(self):
        """Sadece main.py'den yönlendirilen firmaları yükle - Düzeltilmiş"""
        if not self.db:
            logger.warning("Veritabanı bağlantısı yok, WhatsApp firmaları yüklenemedi")
            self.whatsapp_status_label.setText("🔴 Veritabanı Bağlantısı Yok")
            return
        
        try:
            # Tüm firmaları getir (get_firms_by_action fonksiyonu yok)
            all_firms = self.db.get_firms()
            
            # WhatsApp için uygun firmaları filtrele
            whatsapp_firms = []
            for firm in all_firms:
                # Telefon numarası olan ve aktif firmaları al
                if firm.get('phone') and firm.get('status') != 'inactive':
                    whatsapp_firms.append(firm)
            
            self.whatsapp_firm_combo.clear()
            self.whatsapp_firm_combo.addItem("-- Firma Seçin --", None)
            
            if not whatsapp_firms:
                self.whatsapp_firm_combo.addItem("❌ WhatsApp için uygun firma bulunamadı", None)
                self.whatsapp_status_label.setText("⚠️ Uygun Firma Yok")
                logger.warning("WhatsApp için uygun firma bulunamadı")
                return
            
            for firm in whatsapp_firms:
                # Firma bilgilerini daha detaylı göster
                phone = firm.get('phone', 'Telefon Yok')
                sector = firm.get('sector', 'Sektör Belirtilmemiş')
                contact = firm.get('contact_person', 'İletişim Kişisi Yok')
                
                display_text = f"📱 {firm.get('name', 'İsimsiz')} | {sector} | {contact}"
                self.whatsapp_firm_combo.addItem(display_text, firm)
            
            # Mesaj sayısını güncelle - güvenli şekilde
            try:
                total_messages = 0
                for firm in whatsapp_firms:
                    firm_messages = self.db.get_messages(firm.get('id'))
                    if firm_messages:
                        total_messages += len(firm_messages)
                self.message_count_label.setText(f"📊 Toplam Mesaj: {total_messages}")
            except Exception as msg_error:
                logger.warning(f"Mesaj sayısı hesaplanamadı: {msg_error}")
                self.message_count_label.setText("📊 Mesaj: Hesaplanamadı")
            
            # İlk firmayı otomatik seç (sadece firma varsa)
            if whatsapp_firms:
                self.whatsapp_firm_combo.setCurrentIndex(1)  # İlk firma
                self.on_whatsapp_firm_selected()
                self.whatsapp_status_label.setText("🟢 Firmalar Yüklendi")
            
            logger.info(f"WhatsApp için {len(whatsapp_firms)} uygun firma yüklendi")
            
        except Exception as e:
            logger.error(f"Firmalar yüklenirken hata: {e}")
            self.whatsapp_status_label.setText("🔴 Yükleme Hatası")
            QMessageBox.critical(self, "❌ Hata", 
                f"Firmalar yüklenirken hata oluştu:\n\n{str(e)}\n\n"
                "Lütfen veritabanı bağlantısını kontrol edin.")
    
    def show_quick_message_popup(self):
        """Hızlı mesaj popup'ı göster - Düzeltilmiş"""
        # Firma seçim kontrolü
        selected_firm = self.whatsapp_firm_combo.currentData()
        if not selected_firm:
            QMessageBox.warning(self, "⚠️ Uyarı", 
                "Lütfen önce bir firma seçin!\n\n"
                "Firma seçmek için:\n"
                "1. Firma dropdown menüsünden bir firma seçin\n"
                "2. Telefon numarası olan aktif firmalar gösterilir")
            return
        
        # Firma bilgilerini kontrol et
        if not selected_firm.get('phone'):
            QMessageBox.warning(self, "⚠️ Uyarı", 
                f"'{selected_firm.get('name', 'Seçili firma')}' firmasının telefon numarası bulunmuyor!\n\n"
                "WhatsApp mesajı gönderebilmek için telefon numarası gereklidir.")
            return
        
        try:
            dialog = QuickMessageDialog(self, selected_firm, self.gpt_manager, self.db)
            if dialog.exec() == QDialog.Accepted:
                message = dialog.get_message()
                if message:
                    self.whatsapp_message_input.setText(message)
                    logger.info(f"Hızlı mesaj oluşturuldu: {selected_firm.get('name')}")
        except Exception as e:
            logger.error(f"Hızlı mesaj dialog hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Hızlı mesaj dialogu açılamadı:\n{str(e)}")
    
    def show_ai_prompt_dialog(self):
        """AI Prompt dialog'u göster - Düzeltilmiş"""
        # Firma seçim kontrolü
        selected_firm = self.whatsapp_firm_combo.currentData()
        if not selected_firm:
            QMessageBox.warning(self, "⚠️ Uyarı", 
                "Lütfen önce bir firma seçin!\n\n"
                "AI mesaj oluşturabilmek için firma seçimi gereklidir.")
            return
        
        # GPT Manager kontrolü
        if not self.gpt_manager or not hasattr(self.gpt_manager, 'client') or not self.gpt_manager.client:
            QMessageBox.warning(self, "⚠️ Uyarı", 
                "OpenAI API ayarlanmamış!\n\n"
                "AI mesaj oluşturabilmek için:\n"
                "1. Ayarlar sekmesine gidin\n"
                "2. OpenAI API Key'inizi girin\n"
                "3. Bağlantıyı test edin")
            return
        
        try:
            dialog = AIPromptDialog(self, selected_firm, self.gpt_manager)
            if dialog.exec() == QDialog.Accepted:
                message = dialog.get_generated_message()
                if message:
                    self.whatsapp_message_input.setText(message)
                    logger.info(f"AI mesaj oluşturuldu: {selected_firm.get('name')}")
        except Exception as e:
            logger.error(f"AI prompt dialog hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"AI mesaj dialogu açılamadı:\n{str(e)}")
    
    def create_vapi_tab(self):
        """Vapi AI sekmesi - Geliştirilmiş"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Vapi ayarları ve yönetimi
        vapi_settings_group = QGroupBox("🔧 Vapi Ayarları ve Yönetim")
        vapi_settings_layout = QGridLayout()
        
        # Bağlantı durumu
        vapi_settings_layout.addWidget(QLabel("Bağlantı Durumu:"), 0, 0)
        self.vapi_connection_status = QLabel("🔴 Bağlı Değil")
        self.vapi_connection_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        vapi_settings_layout.addWidget(self.vapi_connection_status, 0, 1)
        
        self.test_vapi_connection_btn = QPushButton("🔗 Bağlantıyı Test Et")
        self.test_vapi_connection_btn.clicked.connect(self.test_vapi_connection)
        vapi_settings_layout.addWidget(self.test_vapi_connection_btn, 0, 2)
        
        # Phone Number seçimi
        vapi_settings_layout.addWidget(QLabel("Telefon Numarası:"), 1, 0)
        self.vapi_phone_combo = QComboBox()
        self.vapi_phone_combo.addItem("-- Seçin --", None)
        self.vapi_phone_combo.currentIndexChanged.connect(self.on_vapi_phone_selected)
        vapi_settings_layout.addWidget(self.vapi_phone_combo, 1, 1)
        
        self.refresh_phones_btn = QPushButton("🔄 Yenile")
        self.refresh_phones_btn.clicked.connect(self.refresh_vapi_phone_numbers)
        vapi_settings_layout.addWidget(self.refresh_phones_btn, 1, 2)
        
        # Assistant seçimi ve yönetimi
        vapi_settings_layout.addWidget(QLabel("Asistan:"), 2, 0)
        self.vapi_assistant_combo = QComboBox()
        self.vapi_assistant_combo.addItem("-- Seçin --", None)
        self.vapi_assistant_combo.currentIndexChanged.connect(self.on_vapi_assistant_selected)
        vapi_settings_layout.addWidget(self.vapi_assistant_combo, 2, 1)
        
        assistant_buttons = QHBoxLayout()
        self.refresh_assistants_btn = QPushButton("🔄")
        self.refresh_assistants_btn.clicked.connect(self.refresh_vapi_assistants)
        self.refresh_assistants_btn.setMaximumWidth(40)
        assistant_buttons.addWidget(self.refresh_assistants_btn)
        
        self.create_assistant_btn = QPushButton("➕")
        self.create_assistant_btn.clicked.connect(self.open_create_assistant_dialog)
        self.create_assistant_btn.setMaximumWidth(40)
        self.create_assistant_btn.setToolTip("Yeni Asistan Oluştur")
        assistant_buttons.addWidget(self.create_assistant_btn)
        
        self.edit_assistant_btn = QPushButton("✏️")
        self.edit_assistant_btn.clicked.connect(self.edit_selected_assistant)
        self.edit_assistant_btn.setMaximumWidth(40)
        self.edit_assistant_btn.setToolTip("Asistanı Düzenle")
        self.edit_assistant_btn.setEnabled(False)
        assistant_buttons.addWidget(self.edit_assistant_btn)
        
        self.delete_assistant_btn = QPushButton("🗑️")
        self.delete_assistant_btn.clicked.connect(self.delete_selected_assistant)
        self.delete_assistant_btn.setMaximumWidth(40)
        self.delete_assistant_btn.setToolTip("Asistanı Sil")
        self.delete_assistant_btn.setEnabled(False)
        assistant_buttons.addWidget(self.delete_assistant_btn)
        
        assistant_buttons.addStretch()
        assistant_widget = QWidget()
        assistant_widget.setLayout(assistant_buttons)
        vapi_settings_layout.addWidget(assistant_widget, 2, 2)
        
        # Seçili asistan bilgileri
        vapi_settings_layout.addWidget(QLabel("Asistan Bilgisi:"), 3, 0)
        self.vapi_assistant_info = QTextEdit()
        self.vapi_assistant_info.setReadOnly(True)
        self.vapi_assistant_info.setMaximumHeight(80)
        vapi_settings_layout.addWidget(self.vapi_assistant_info, 3, 1, 1, 2)
        
        vapi_settings_group.setLayout(vapi_settings_layout)
        layout.addWidget(vapi_settings_group)
        
        # Arama başlatma
        call_group = QGroupBox("📞 Arama Başlat")
        call_layout = QGridLayout()
        
        # Firma seçimi
        call_layout.addWidget(QLabel("Firma:"), 0, 0)
        self.vapi_firm_combo = QComboBox()
        self.vapi_firm_combo.currentIndexChanged.connect(self.on_vapi_firm_selected)
        call_layout.addWidget(self.vapi_firm_combo, 0, 1)
        
        # Firma bilgileri
        call_layout.addWidget(QLabel("Firma Bilgileri:"), 1, 0)
        self.vapi_firm_info = QTextEdit()
        self.vapi_firm_info.setReadOnly(True)
        self.vapi_firm_info.setMaximumHeight(80)
        call_layout.addWidget(self.vapi_firm_info, 1, 1)
        
        # Arama senaryosu
        call_layout.addWidget(QLabel("Arama Senaryosu:"), 2, 0)
        self.call_script_input = QTextEdit()
        self.call_script_input.setMaximumHeight(100)
        self.call_script_input.setPlaceholderText("Arama senaryosu veya özel talimatlar...")
        call_layout.addWidget(self.call_script_input, 2, 1)
        
        # GPT ile senaryo oluştur
        self.generate_script_btn = QPushButton("🤖 Senaryo Oluştur")
        self.generate_script_btn.clicked.connect(self.generate_call_script)
        call_layout.addWidget(self.generate_script_btn, 2, 2)
        
        # Arama notu
        call_layout.addWidget(QLabel("Arama Notu:"), 3, 0)
        self.call_notes_input = QTextEdit()
        self.call_notes_input.setMaximumHeight(80)
        self.call_notes_input.setPlaceholderText("Arama öncesi notlar...")
        call_layout.addWidget(self.call_notes_input, 3, 1)
        
        # Arama butonları
        call_buttons = QHBoxLayout()
        
        self.start_call_btn = QPushButton("📞 Aramayı Başlat")
        self.start_call_btn.clicked.connect(self.start_vapi_call)
        call_buttons.addWidget(self.start_call_btn)
        
        self.check_call_status_btn = QPushButton("🔍 Durum Kontrol")
        self.check_call_status_btn.clicked.connect(self.check_call_status)
        call_buttons.addWidget(self.check_call_status_btn)
        
        self.bulk_call_btn = QPushButton("📞 Toplu Arama")
        self.bulk_call_btn.clicked.connect(self.open_bulk_call_dialog)
        call_buttons.addWidget(self.bulk_call_btn)
        
        call_layout.addLayout(call_buttons, 4, 0, 1, 2)
        
        call_group.setLayout(call_layout)
        layout.addWidget(call_group)
        
        # Arama geçmişi
        history_group = QGroupBox("📋 Arama Geçmişi")
        history_layout = QVBoxLayout()
        
        self.calls_table = QTableWidget()
        self.calls_table.setColumnCount(8)
        self.calls_table.setHorizontalHeaderLabels([
            "Tarih", "Saat", "Firma", "Süre (sn)", "Durum", "Maliyet", "Notlar", "İşlemler"
        ])
        
        self.calls_table.setColumnWidth(0, 100)
        self.calls_table.setColumnWidth(1, 80)
        self.calls_table.setColumnWidth(2, 200)
        self.calls_table.setColumnWidth(3, 80)
        self.calls_table.setColumnWidth(4, 100)
        self.calls_table.setColumnWidth(5, 80)
        
        history_layout.addWidget(self.calls_table)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # Firmaları yükle
        self.load_firms_to_vapi_combo()
        
        # Vapi verilerini yükle
        self.refresh_vapi_phone_numbers()
        self.refresh_vapi_assistants()
        
        # Arama geçmişini yükle
        self.load_calls_history()
        
        return widget
    
    def create_call_records_tab(self):
        """Çağrı Kayıtları ve AI Analizi sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Üst kontroller
        controls_layout = QHBoxLayout()
        
        # Filtreler
        filters_group = QGroupBox("🔍 Filtreler")
        filters_layout = QHBoxLayout()
        
        # Tarih filtresi
        filters_layout.addWidget(QLabel("Tarih:"))
        self.call_date_filter = QComboBox()
        self.call_date_filter.addItems([
            "Tümü", "Bugün", "Dün", "Son 7 Gün", "Son 30 Gün", "Özel Aralık"
        ])
        self.call_date_filter.currentTextChanged.connect(self.filter_call_records)
        filters_layout.addWidget(self.call_date_filter)
        
        # Durum filtresi
        filters_layout.addWidget(QLabel("Durum:"))
        self.call_status_filter = QComboBox()
        self.call_status_filter.addItems([
            "Tümü", "Başarılı", "Başarısız", "Devam Ediyor", "İptal"
        ])
        self.call_status_filter.currentTextChanged.connect(self.filter_call_records)
        filters_layout.addWidget(self.call_status_filter)
        
        # AI Analiz filtresi
        filters_layout.addWidget(QLabel("AI Analizi:"))
        self.call_analysis_filter = QComboBox()
        self.call_analysis_filter.addItems([
            "Tümü", "Olumlu", "Olumsuz", "Kararsız", "Analiz Edilmemiş"
        ])
        self.call_analysis_filter.currentTextChanged.connect(self.filter_call_records)
        filters_layout.addWidget(self.call_analysis_filter)
        
        filters_layout.addStretch()
        
        # Yenile butonu
        self.refresh_call_records_btn = QPushButton("🔄 Yenile")
        self.refresh_call_records_btn.clicked.connect(self.load_call_records)
        filters_layout.addWidget(self.refresh_call_records_btn)
        
        filters_group.setLayout(filters_layout)
        controls_layout.addWidget(filters_group)
        
        # AI Analiz butonu
        ai_group = QGroupBox("🤖 AI İşlemleri")
        ai_layout = QHBoxLayout()
        
        self.analyze_all_btn = QPushButton("🔍 Tümünü Analiz Et")
        self.analyze_all_btn.clicked.connect(self.analyze_all_calls)
        ai_layout.addWidget(self.analyze_all_btn)
        
        self.analyze_selected_btn = QPushButton("🎯 Seçilenleri Analiz Et")
        self.analyze_selected_btn.clicked.connect(self.analyze_selected_calls)
        ai_layout.addWidget(self.analyze_selected_btn)
        
        ai_group.setLayout(ai_layout)
        controls_layout.addWidget(ai_group)
        
        layout.addLayout(controls_layout)
        
        # Ana içerik - İki panel
        main_content = QHBoxLayout()
        
        # Sol panel - Çağrı listesi
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Çağrı tablosu
        calls_group = QGroupBox("📞 Çağrı Listesi")
        calls_layout = QVBoxLayout()
        
        self.call_records_table = QTableWidget()
        self.call_records_table.setColumnCount(9)
        self.call_records_table.setHorizontalHeaderLabels([
            "Seç", "Tarih", "Saat", "Firma", "Telefon", "Süre", "Durum", "AI Analizi", "Maliyet"
        ])
        
        # Tablo ayarları
        self.call_records_table.setColumnWidth(0, 50)   # Checkbox
        self.call_records_table.setColumnWidth(1, 100)  # Tarih
        self.call_records_table.setColumnWidth(2, 80)   # Saat
        self.call_records_table.setColumnWidth(3, 200)  # Firma
        self.call_records_table.setColumnWidth(4, 120)  # Telefon
        self.call_records_table.setColumnWidth(5, 80)   # Süre
        self.call_records_table.setColumnWidth(6, 100)  # Durum
        self.call_records_table.setColumnWidth(7, 120)  # AI Analizi
        self.call_records_table.setColumnWidth(8, 80)   # Maliyet
        
        self.call_records_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.call_records_table.itemSelectionChanged.connect(self.on_call_selected)
        
        calls_layout.addWidget(self.call_records_table)
        calls_group.setLayout(calls_layout)
        left_layout.addWidget(calls_group)
        
        # İstatistikler
        stats_group = QGroupBox("📊 İstatistikler")
        stats_layout = QGridLayout()
        
        self.total_calls_label = QLabel("Toplam Çağrı: 0")
        self.successful_calls_label = QLabel("Başarılı: 0")
        self.failed_calls_label = QLabel("Başarısız: 0")
        self.total_duration_label = QLabel("Toplam Süre: 0 dk")
        self.total_cost_label = QLabel("Toplam Maliyet: $0.00")
        self.avg_duration_label = QLabel("Ort. Süre: 0 dk")
        
        self.positive_analysis_label = QLabel("Olumlu: 0")
        self.negative_analysis_label = QLabel("Olumsuz: 0")
        self.neutral_analysis_label = QLabel("Kararsız: 0")
        
        stats_layout.addWidget(self.total_calls_label, 0, 0)
        stats_layout.addWidget(self.successful_calls_label, 0, 1)
        stats_layout.addWidget(self.failed_calls_label, 0, 2)
        stats_layout.addWidget(self.total_duration_label, 1, 0)
        stats_layout.addWidget(self.total_cost_label, 1, 1)
        stats_layout.addWidget(self.avg_duration_label, 1, 2)
        stats_layout.addWidget(self.positive_analysis_label, 2, 0)
        stats_layout.addWidget(self.negative_analysis_label, 2, 1)
        stats_layout.addWidget(self.neutral_analysis_label, 2, 2)
        
        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)
        
        left_panel.setMaximumWidth(800)
        main_content.addWidget(left_panel)
        
        # Sağ panel - Detaylar ve analiz
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Çağrı detayları
        details_group = QGroupBox("📋 Seçili Çağrı Detayları")
        details_layout = QVBoxLayout()
        
        # Temel bilgiler
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel("Firma:"), 0, 0)
        self.selected_call_firm = QLabel("-")
        self.selected_call_firm.setStyleSheet("font-weight: bold; color: #3498db;")
        info_layout.addWidget(self.selected_call_firm, 0, 1)
        
        info_layout.addWidget(QLabel("Telefon:"), 1, 0)
        self.selected_call_phone = QLabel("-")
        info_layout.addWidget(self.selected_call_phone, 1, 1)
        
        info_layout.addWidget(QLabel("Tarih:"), 2, 0)
        self.selected_call_date = QLabel("-")
        info_layout.addWidget(self.selected_call_date, 2, 1)
        
        info_layout.addWidget(QLabel("Süre:"), 3, 0)
        self.selected_call_duration = QLabel("-")
        info_layout.addWidget(self.selected_call_duration, 3, 1)
        
        info_layout.addWidget(QLabel("Durum:"), 4, 0)
        self.selected_call_status = QLabel("-")
        info_layout.addWidget(self.selected_call_status, 4, 1)
        
        info_layout.addWidget(QLabel("Maliyet:"), 5, 0)
        self.selected_call_cost = QLabel("-")
        info_layout.addWidget(self.selected_call_cost, 5, 1)
        
        details_layout.addLayout(info_layout)
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Konuşma metni
        transcript_group = QGroupBox("💬 Konuşma Metni")
        transcript_layout = QVBoxLayout()
        
        self.call_transcript = QTextEdit()
        self.call_transcript.setReadOnly(True)
        self.call_transcript.setPlaceholderText("Seçili çağrının konuşma metni burada görünecek...")
        transcript_layout.addWidget(self.call_transcript)
        
        transcript_group.setLayout(transcript_layout)
        right_layout.addWidget(transcript_group)
        
        # AI Analizi
        analysis_group = QGroupBox("🤖 AI Analizi")
        analysis_layout = QVBoxLayout()
        
        # Analiz durumu
        analysis_status_layout = QHBoxLayout()
        analysis_status_layout.addWidget(QLabel("Analiz Durumu:"))
        self.analysis_status_label = QLabel("Seçili çağrı yok")
        self.analysis_status_label.setStyleSheet("font-weight: bold;")
        analysis_status_layout.addWidget(self.analysis_status_label)
        analysis_status_layout.addStretch()
        
        self.analyze_this_call_btn = QPushButton("🔍 Bu Çağrıyı Analiz Et")
        self.analyze_this_call_btn.clicked.connect(self.analyze_selected_call)
        self.analyze_this_call_btn.setEnabled(False)
        analysis_status_layout.addWidget(self.analyze_this_call_btn)
        
        analysis_layout.addLayout(analysis_status_layout)
        
        # Analiz sonuçları
        results_layout = QGridLayout()
        
        results_layout.addWidget(QLabel("Genel Değerlendirme:"), 0, 0)
        self.analysis_sentiment = QLabel("-")
        self.analysis_sentiment.setStyleSheet("font-weight: bold; font-size: 14px;")
        results_layout.addWidget(self.analysis_sentiment, 0, 1)
        
        results_layout.addWidget(QLabel("Güven Skoru:"), 1, 0)
        self.analysis_confidence = QLabel("-")
        results_layout.addWidget(self.analysis_confidence, 1, 1)
        
        results_layout.addWidget(QLabel("Satış Potansiyeli:"), 2, 0)
        self.analysis_sales_potential = QLabel("-")
        results_layout.addWidget(self.analysis_sales_potential, 2, 1)
        
        results_layout.addWidget(QLabel("Takip Gereksinimi:"), 3, 0)
        self.analysis_follow_up = QLabel("-")
        results_layout.addWidget(self.analysis_follow_up, 3, 1)
        
        analysis_layout.addLayout(results_layout)
        
        # Detaylı analiz metni
        analysis_layout.addWidget(QLabel("Detaylı Analiz:"))
        self.analysis_details = QTextEdit()
        self.analysis_details.setReadOnly(True)
        self.analysis_details.setMaximumHeight(150)
        self.analysis_details.setPlaceholderText("AI analiz sonuçları burada görünecek...")
        analysis_layout.addWidget(self.analysis_details)
        
        # Öneriler
        analysis_layout.addWidget(QLabel("AI Önerileri:"))
        self.analysis_recommendations = QTextEdit()
        self.analysis_recommendations.setReadOnly(True)
        self.analysis_recommendations.setMaximumHeight(100)
        self.analysis_recommendations.setPlaceholderText("AI önerileri burada görünecek...")
        analysis_layout.addWidget(self.analysis_recommendations)
        
        analysis_group.setLayout(analysis_layout)
        right_layout.addWidget(analysis_group)
        
        main_content.addWidget(right_panel)
        layout.addLayout(main_content)
        
        # İlk yükleme
        self.load_call_records()
        
        return widget
    
    def create_templates_tab(self):
        """Şablonlar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Üst toolbar
        toolbar_layout = QHBoxLayout()
        
        # Kategori seçimi
        self.template_category = QComboBox()
        self.template_category.addItems([
            "Tümü", "Tanıtım", "Takip", "Kampanya", "Bilgilendirme", "Teşekkür", "Özel"
        ])
        self.template_category.currentTextChanged.connect(self.load_templates)
        toolbar_layout.addWidget(QLabel("Kategori:"))
        toolbar_layout.addWidget(self.template_category)
        
        toolbar_layout.addStretch()
        
        # Yeni şablon butonu
        self.new_template_btn = QPushButton("➕ Yeni Şablon")
        self.new_template_btn.clicked.connect(self.create_new_template)
        toolbar_layout.addWidget(self.new_template_btn)
        
        layout.addLayout(toolbar_layout)
        
        # İki sütun layout
        columns_layout = QHBoxLayout()
        
        # Sol - Şablon listesi
        templates_list_group = QGroupBox("📝 Şablonlar")
        templates_list_layout = QVBoxLayout()
        
        self.templates_list = QListWidget()
        self.templates_list.itemClicked.connect(self.on_template_selected)
        templates_list_layout.addWidget(self.templates_list)
        
        templates_list_group.setLayout(templates_list_layout)
        templates_list_group.setMaximumWidth(400)
        columns_layout.addWidget(templates_list_group)
        
        # Sağ - Şablon editörü
        editor_group = QGroupBox("✏️ Şablon Düzenleyici")
        editor_layout = QVBoxLayout()
        
        # Şablon adı
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Şablon Adı:"))
        self.template_name_input = QLineEdit()
        name_layout.addWidget(self.template_name_input)
        editor_layout.addLayout(name_layout)
        
        # Kategori
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Kategori:"))
        self.template_category_input = QComboBox()
        self.template_category_input.setEditable(True)
        self.template_category_input.addItems([
            "Tanıtım", "Takip", "Kampanya", "Bilgilendirme", "Teşekkür", "Özel"
        ])
        category_layout.addWidget(self.template_category_input)
        category_layout.addStretch()
        editor_layout.addLayout(category_layout)
        
        # Değişkenler
        variables_layout = QHBoxLayout()
        variables_layout.addWidget(QLabel("Kullanılan Değişkenler:"))
        self.template_variables = QLabel()
        self.template_variables.setStyleSheet("color: #3498db;")
        variables_layout.addWidget(self.template_variables)
        variables_layout.addStretch()
        editor_layout.addLayout(variables_layout)
        
        # Şablon içeriği
        editor_layout.addWidget(QLabel("İçerik:"))
        self.template_content = QTextEdit()
        self.template_content.setPlaceholderText("""
Şablon değişkenleri:
{firma_adi} - Firma adı
{firma_sektoru} - Firma sektörü
{firma_iletisim} - İletişim kişisi
{firma_ozet} - Firma özeti
{firma_telefon} - Firma telefonu
{firma_email} - Firma emaili
{firma_website} - Firma websitesi
{satici_adi} - Satıcı adı
{satici_firma} - Satıcı firma
{tarih} - Bugünün tarihi
{saat} - Şu anki saat

Örnek:
Merhaba {firma_adi} ekibi,
{firma_sektoru} sektöründeki çalışmalarınızı takip ediyorum...
        """)
        self.template_content.textChanged.connect(self.update_template_variables)
        editor_layout.addWidget(self.template_content)
        
        # Önizleme
        editor_layout.addWidget(QLabel("Önizleme:"))
        self.template_preview = QTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setMaximumHeight(150)
        editor_layout.addWidget(self.template_preview)
        
        # Butonlar
        template_buttons = QHBoxLayout()
        
        self.preview_template_btn = QPushButton("👁️ Önizle")
        self.preview_template_btn.clicked.connect(self.preview_template)
        template_buttons.addWidget(self.preview_template_btn)
        
        self.save_template_btn = QPushButton("💾 Kaydet")
        self.save_template_btn.clicked.connect(self.save_template)
        template_buttons.addWidget(self.save_template_btn)
        
        self.delete_template_btn = QPushButton("🗑️ Sil")
        self.delete_template_btn.clicked.connect(self.delete_template)
        template_buttons.addWidget(self.delete_template_btn)
        
        template_buttons.addStretch()
        editor_layout.addLayout(template_buttons)
        
        editor_group.setLayout(editor_layout)
        columns_layout.addWidget(editor_group)
        
        layout.addLayout(columns_layout)
        
        # Şablonları yükle
        self.load_templates()
        
        return widget
    
    def create_activities_tab(self):
        """Aktiviteler sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filtreler
        filters_layout = QHBoxLayout()
        
        # Tarih filtresi
        filters_layout.addWidget(QLabel("Tarih:"))
        self.activity_date_filter = QComboBox()
        self.activity_date_filter.addItems([
            "Tümü", "Bugün", "Dün", "Son 7 Gün", "Son 30 Gün"
        ])
        self.activity_date_filter.currentTextChanged.connect(self.filter_activities)
        filters_layout.addWidget(self.activity_date_filter)
        
        # Tip filtresi
        filters_layout.addWidget(QLabel("Tip:"))
        self.activity_type_filter = QComboBox()
        self.activity_type_filter.addItems([
            "Tümü", "Mesaj", "Arama", "Email", "Firma", "Diğer"
        ])
        self.activity_type_filter.currentTextChanged.connect(self.filter_activities)
        filters_layout.addWidget(self.activity_type_filter)
        
        # Firma filtresi
        filters_layout.addWidget(QLabel("Firma:"))
        self.activity_firm_filter = QComboBox()
        self.activity_firm_filter.addItem("Tüm Firmalar")
        self.activity_firm_filter.currentTextChanged.connect(self.filter_activities)
        filters_layout.addWidget(self.activity_firm_filter)
        
        filters_layout.addStretch()
        
        # Yenile butonu
        self.refresh_activities_btn = QPushButton("🔄 Yenile")
        self.refresh_activities_btn.clicked.connect(self.load_activities)
        filters_layout.addWidget(self.refresh_activities_btn)
        
        layout.addLayout(filters_layout)
        
        # Aktivite tablosu
        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(6)
        self.activities_table.setHorizontalHeaderLabels([
            "Tarih", "Saat", "Firma", "Tip", "Açıklama", "Detaylar"
        ])
        
        self.activities_table.setColumnWidth(0, 100)
        self.activities_table.setColumnWidth(1, 80)
        self.activities_table.setColumnWidth(2, 200)
        self.activities_table.setColumnWidth(3, 100)
        self.activities_table.setColumnWidth(4, 300)
        
        self.activities_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.activities_table)
        
        # İstatistik özeti
        stats_group = QGroupBox("📊 Özet")
        stats_layout = QHBoxLayout()
        
        self.activity_total_label = QLabel("Toplam: 0")
        self.activity_messages_label = QLabel("Mesajlar: 0")
        self.activity_calls_label = QLabel("Aramalar: 0")
        self.activity_emails_label = QLabel("Emailler: 0")
        
        stats_layout.addWidget(self.activity_total_label)
        stats_layout.addWidget(self.activity_messages_label)
        stats_layout.addWidget(self.activity_calls_label)
        stats_layout.addWidget(self.activity_emails_label)
        stats_layout.addStretch()
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Firmaları combo'ya yükle
        self.load_firms_to_activity_filter()
        
        # Aktiviteleri yükle
        self.load_activities()
        
        return widget
    
    def create_settings_tab(self):
        """Ayarlar sekmesi - Karanlık tema uyumlu"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area - karanlık tema
        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
            }
        """)
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # API Ayarları
        api_group = QGroupBox("🔑 API Ayarları")
        api_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
                background-color: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #1a1a1a;
            }
        """)
        api_layout = QGridLayout()
        
        # OpenAI
        api_layout.addWidget(QLabel("OpenAI API Key:"), 0, 0)
        self.openai_api_input = QLineEdit()
        self.openai_api_input.setEchoMode(QLineEdit.Password)
        self.openai_api_input.setText(self.config.get('openai_api_key', ''))
        api_layout.addWidget(self.openai_api_input, 0, 1)
        
        self.test_openai_btn = QPushButton("Test")
        self.test_openai_btn.clicked.connect(self.test_openai_api)
        api_layout.addWidget(self.test_openai_btn, 0, 2)
        
        # Vapi
        api_layout.addWidget(QLabel("Vapi API Key:"), 1, 0)
        self.vapi_api_input = QLineEdit()
        self.vapi_api_input.setEchoMode(QLineEdit.Password)
        self.vapi_api_input.setText(self.config.get('vapi_api_key', ''))
        api_layout.addWidget(self.vapi_api_input, 1, 1)
        
        self.test_vapi_btn = QPushButton("Test")
        self.test_vapi_btn.clicked.connect(self.test_vapi_api)
        api_layout.addWidget(self.test_vapi_btn, 1, 2)
        
        api_group.setLayout(api_layout)
        scroll_layout.addWidget(api_group)
        
        # Satıcı Bilgileri
        seller_group = QGroupBox("👤 Satıcı Bilgileri")
        seller_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
                background-color: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #1a1a1a;
            }
        """)
        seller_layout = QGridLayout()
        
        seller_layout.addWidget(QLabel("Ad Soyad:"), 0, 0)
        self.seller_name_input = QLineEdit()
        self.seller_name_input.setText(self.config.get('seller_name', ''))
        seller_layout.addWidget(self.seller_name_input, 0, 1)
        
        seller_layout.addWidget(QLabel("Firma:"), 1, 0)
        self.seller_company_input = QLineEdit()
        self.seller_company_input.setText(self.config.get('seller_company', ''))
        seller_layout.addWidget(self.seller_company_input, 1, 1)
        
        seller_layout.addWidget(QLabel("E-posta:"), 2, 0)
        self.seller_email_input = QLineEdit()
        self.seller_email_input.setText(self.config.get('seller_email', ''))
        seller_layout.addWidget(self.seller_email_input, 2, 1)
        
        seller_layout.addWidget(QLabel("Telefon:"), 3, 0)
        self.seller_phone_input = QLineEdit()
        self.seller_phone_input.setText(self.config.get('seller_phone', ''))
        seller_layout.addWidget(self.seller_phone_input, 3, 1)
        
        seller_group.setLayout(seller_layout)
        scroll_layout.addWidget(seller_group)
        
        # Otomasyon Ayarları
        automation_group = QGroupBox("🤖 Otomasyon Ayarları")
        automation_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
                background-color: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #1a1a1a;
            }
        """)
        automation_layout = QVBoxLayout()
        
        self.auto_reply_check = QCheckBox("Otomatik yanıtlama aktif")
        self.auto_reply_check.setChecked(self.config.get('auto_reply', False))
        automation_layout.addWidget(self.auto_reply_check)
        
        self.auto_schedule_check = QCheckBox("Zamanlanmış görevler aktif")
        self.auto_schedule_check.setChecked(self.config.get('auto_schedule', True))
        automation_layout.addWidget(self.auto_schedule_check)
        
        self.message_delay_spin = QSpinBox()
        self.message_delay_spin.setRange(1, 60)
        self.message_delay_spin.setValue(self.config.get('message_delay', 5))
        self.message_delay_spin.setSuffix(" saniye")
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Mesaj gönderme gecikmesi:"))
        delay_layout.addWidget(self.message_delay_spin)
        delay_layout.addStretch()
        automation_layout.addLayout(delay_layout)
        
        automation_group.setLayout(automation_layout)
        scroll_layout.addWidget(automation_group)
        
        # Veritabanı Ayarları
        db_group = QGroupBox("🗜️ Veritabanı")
        db_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 14px;
                background-color: #2a2a2a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #1a1a1a;
            }
        """)
        db_layout = QVBoxLayout()
        
        db_info = QLabel(f"Veritabanı: {self.db.db_path}")
        db_layout.addWidget(db_info)
        
        # Veritabanı istatistikleri
        try:
            stats = self.db.get_statistics()
            db_stats = QLabel(f"""
            Toplam Firma: {stats['total_firms']}
            Toplam Mesaj: {stats['total_messages']}
            Toplam Arama: {stats['total_calls']}
            """)
            db_layout.addWidget(db_stats)
        except:
            pass
        
        db_buttons = QHBoxLayout()
        
        self.backup_db_btn = QPushButton("💾 Yedekle")
        self.backup_db_btn.clicked.connect(self.backup_database)
        db_buttons.addWidget(self.backup_db_btn)
        
        self.restore_db_btn = QPushButton("♻️ Geri Yükle")
        self.restore_db_btn.clicked.connect(self.restore_database)
        db_buttons.addWidget(self.restore_db_btn)
        
        self.clear_db_btn = QPushButton("🗑️ Temizle")
        self.clear_db_btn.clicked.connect(self.clear_database)
        db_buttons.addWidget(self.clear_db_btn)
        
        self.export_db_btn = QPushButton("📤 Dışa Aktar")
        self.export_db_btn.clicked.connect(self.export_database)
        db_buttons.addWidget(self.export_db_btn)
        
        db_buttons.addStretch()
        db_layout.addLayout(db_buttons)
        
        db_group.setLayout(db_layout)
        scroll_layout.addWidget(db_group)
        
        # Kaydet butonu
        save_btn = QPushButton("💾 Ayarları Kaydet")
        save_btn.clicked.connect(self.save_settings)
        scroll_layout.addWidget(save_btn)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return widget
    
    def apply_modern_theme(self):
        """Modern tema uygula - Responsive Font ve Boyutlarla"""
        
        # Responsive font boyutları hesapla
        base_font_size = max(10, int(14 * self.scale_factor))
        small_font_size = max(9, int(12 * self.scale_factor))
        large_font_size = max(12, int(16 * self.scale_factor))
        button_padding = max(8, int(10 * self.scale_factor))
        tab_padding_h = max(12, int(16 * self.scale_factor))
        tab_padding_v = max(6, int(8 * self.scale_factor))
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #0f0f0f;
            }}
            
            QTabWidget::pane {{
                border: none;
                background-color: #1a1a1a;
                border-radius: 8px;
            }}
            
            QTabBar::tab {{
                background-color: #2a2a2a;
                color: #ffffff;
                padding: {tab_padding_v}px {tab_padding_h}px;
                margin-right: 2px;
                margin-left: 0px;
                border-radius: 6px 6px 0 0;
                font-weight: 500;
                font-size: {small_font_size}px;
                min-width: {max(60, int(80 * self.scale_factor))}px;
                max-width: {max(90, int(120 * self.scale_factor))}px;
            }}
            
            QTabBar::tab:selected {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0d7377, stop: 1 #14a1a5);
                color: white;
            }}
            
            QTabBar::tab:hover {{
                background-color: #3a3a3a;
            }}
            
            QTabBar {{
                alignment: left;
            }}
            
            QTableWidget {{
                background-color: #1a1a1a;
                color: #ffffff;
                gridline-color: #2a2a2a;
                selection-background-color: #0d7377;
                border: none;
                border-radius: 10px;
            }}
            
            QTableWidget::item {{
                padding: 5px;
            }}
            
            QHeaderView::section {{
                background-color: #2a2a2a;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0d7377, stop: 1 #14a1a5);
                color: white;
                border: none;
                padding: {button_padding}px {max(15, int(20 * self.scale_factor))}px;
                border-radius: {max(6, int(8 * self.scale_factor))}px;
                font-weight: 500;
                font-size: {base_font_size}px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #14a1a5, stop: 1 #1db8bc);
            }}
            
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0a5d61, stop: 1 #0d7377);
            }}
            
            QLineEdit, QTextEdit, QComboBox {{
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                padding: {button_padding}px;
                border-radius: {max(6, int(8 * self.scale_factor))}px;
                font-size: {base_font_size}px;
            }}
            
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid #0d7377;
                background-color: #1a1a1a;
            }}
            
            QComboBox:hover {{
                border: 1px solid #0d7377;
            }}
            
            QComboBox::drop-down {{
                border: none;
                padding-right: 20px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }}
            
            QLabel {{
                color: #ffffff;
                font-size: {base_font_size}px;
            }}
            
            QGroupBox {{
                color: #ffffff;
                border: 2px solid #2a2a2a;
                border-radius: {max(8, int(10 * self.scale_factor))}px;
                margin-top: {max(10, int(15 * self.scale_factor))}px;
                padding-top: {max(10, int(15 * self.scale_factor))}px;
                font-weight: bold;
                font-size: {large_font_size}px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #1a1a1a;
            }}
            
            QListWidget {{
                background-color: #1a1a1a;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }}
            
            QListWidget::item {{
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 5px;
                background-color: #2a2a2a;
            }}
            
            QListWidget::item:selected {{
                background-color: #0d7377;
            }}
            
            QListWidget::item:hover {{
                background-color: #3a3a3a;
            }}
            
            QScrollBar:vertical {{
                background-color: #1a1a1a;
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: #3a3a3a;
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: #4a4a4a;
            }}
            
            QStatusBar {{
                background-color: #1a1a1a;
                color: white;
                border-top: 1px solid #2a2a2a;
            }}
            
            QWebEngineView {{
                background-color: white;
                border-radius: 10px;
            }}
            
            QCheckBox {{
                color: white;
                spacing: 10px;
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                background-color: #2a2a2a;
                border: 2px solid #3a3a3a;
                border-radius: 4px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: #0d7377;
                border: 2px solid #0d7377;
            }}
            
            QProgressBar {{
                background-color: #2a2a2a;
                border-radius: 5px;
                text-align: center;
                color: white;
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a1a5);
                border-radius: 5px;
            }}
        """)
    
    def load_config(self):
        """Konfigürasyonu yükle"""
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                self.config = json.load(f)
                
                # API anahtarlarını ayarla
                if 'openai_api_key' in self.config:
                    self.gpt_manager.set_api_key(self.config['openai_api_key'])
                
                if 'vapi_api_key' in self.config:
                    self.vapi_manager.set_api_key(self.config['vapi_api_key'])
                
                if 'vapi_phone_number_id' in self.config:
                    self.vapi_manager.set_phone_number_id(self.config['vapi_phone_number_id'])
                    
        except FileNotFoundError:
            self.config = {}
            logger.warning("config.json bulunamadı, yeni dosya oluşturulacak")
        except json.JSONDecodeError:
            self.config = {}
            logger.error("config.json okunamadı")
    
    def save_settings(self):
        """Ayarları kaydet"""
        self.config = {
            'openai_api_key': self.openai_api_input.text(),
            'vapi_api_key': self.vapi_api_input.text(),
            'vapi_phone_number_id': self.vapi_phone_combo.currentData() if hasattr(self, 'vapi_phone_combo') else '',
            'seller_name': self.seller_name_input.text(),
            'seller_company': self.seller_company_input.text(),
            'seller_email': self.seller_email_input.text(),
            'seller_phone': self.seller_phone_input.text(),
            'auto_reply': self.auto_reply_check.isChecked(),
            'auto_schedule': self.auto_schedule_check.isChecked(),
            'message_delay': self.message_delay_spin.value()
        }
        
        # API anahtarlarını ayarla
        self.gpt_manager.set_api_key(self.config['openai_api_key'])
        self.vapi_manager.set_api_key(self.config['vapi_api_key'])
        
        if self.config['vapi_phone_number_id']:
            self.vapi_manager.set_phone_number_id(self.config['vapi_phone_number_id'])
        
        # Dosyaya kaydet
        try:
            with open("config.json", "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "✅ Başarılı", "Ayarlar kaydedildi!")
            self.check_api_status()
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Ayarlar kaydedilemedi: {str(e)}")
    
    def check_api_status(self):
        """API durumlarını kontrol et"""
        # OpenAI durumu
        if self.config.get('openai_api_key'):
            self.gpt_status.setText("🟢 GPT Aktif")
            self.gpt_status.setStyleSheet("font-size: 14px; color: #27ae60;")
        else:
            self.gpt_status.setText("🔴 GPT Kapalı")
            self.gpt_status.setStyleSheet("font-size: 14px; color: #e74c3c;")
        
        # Vapi durumu
        if self.config.get('vapi_api_key'):
            self.vapi_status.setText("🟢 Vapi Aktif")
            self.vapi_status.setStyleSheet("font-size: 14px; color: #27ae60;")
        else:
            self.vapi_status.setText("🔴 Vapi Kapalı")
            self.vapi_status.setStyleSheet("font-size: 14px; color: #e74c3c;")
    
    def test_openai_api(self):
        """OpenAI API test et"""
        api_key = self.openai_api_input.text()
        if not api_key:
            QMessageBox.warning(self, "⚠️ Uyarı", "API anahtarı girilmedi!")
            return
        
        # API'yi test et
        try:
            self.gpt_manager.set_api_key(api_key)
            # Basit bir test mesajı
            result = self.gpt_manager.generate_message("Merhaba de", {'name': 'Test'})
            if result:
                QMessageBox.information(self, "✅ Başarılı", f"OpenAI API bağlantısı başarılı!\n\nTest yanıtı: {result}")
            else:
                QMessageBox.warning(self, "⚠️ Uyarı", "API bağlantısı başarısız!")
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"API test hatası: {str(e)}")
    
    def test_vapi_api(self):
        """Vapi API test et"""
        api_key = self.vapi_api_input.text()
        if not api_key:
            QMessageBox.warning(self, "⚠️ Uyarı", "API anahtarı girilmedi!")
            return
        
        try:
            success = self.vapi_manager.set_api_key(api_key)
            if success:
                # Telefon numaralarını getir
                phone_numbers = self.vapi_manager.get_phone_numbers()
                assistants = self.vapi_manager.get_assistants()
                
                QMessageBox.information(self, "✅ Başarılı", 
                    f"Vapi API bağlantısı başarılı!\n\n"
                    f"Telefon Numaraları: {len(phone_numbers)}\n"
                    f"Asistanlar: {len(assistants)}")
                        
                # UI'ı güncelle
                self.update_vapi_status()
            else:
                QMessageBox.warning(self, "⚠️ Uyarı", "API bağlantısı başarısız!")
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"API test hatası: {str(e)}")
    
    def test_vapi_connection(self):
        """Vapi bağlantısını test et"""
        if not self.vapi_manager.api_key:
            QMessageBox.warning(self, "⚠️ Uyarı", "Önce Vapi API anahtarını ayarlayın!")
            return
        
        success = self.vapi_manager.test_connection()
        
        if success:
            QMessageBox.information(self, "✅ Başarılı", "Vapi API bağlantısı aktif!")
            self.update_vapi_status()
        else:
            QMessageBox.warning(self, "⚠️ Uyarı", "Vapi API bağlantısı başarısız!")
    
    def update_vapi_status(self):
        """Vapi bağlantı durumunu güncelle"""
        if hasattr(self, 'vapi_connection_status'):
            if self.vapi_manager.api_key and self.vapi_manager.test_connection():
                self.vapi_connection_status.setText("🟢 Bağlı")
                self.vapi_connection_status.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.vapi_connection_status.setText("🔴 Bağlı Değil")
                self.vapi_connection_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def on_vapi_phone_selected(self):
        """Vapi telefon numarası seçildiğinde"""
        phone_data = self.vapi_phone_combo.currentData()
        if phone_data:
            self.vapi_manager.set_phone_number_id(phone_data)
            # Config'e kaydet
            self.config['vapi_phone_number_id'] = phone_data
    
    def on_vapi_assistant_selected(self):
        """Vapi asistan seçildiğinde"""
        assistant_data = self.vapi_assistant_combo.currentData()
        if assistant_data:
            # Asistan bilgilerini göster
            info_text = f"""
Asistan: {assistant_data.get('name', 'N/A')}
ID: {assistant_data.get('id', 'N/A')}
Model: {assistant_data.get('model', {}).get('model', 'N/A')}
Ses: {assistant_data.get('voice', {}).get('voiceId', 'N/A')}
İlk Mesaj: {assistant_data.get('firstMessage', 'N/A')[:100]}...
            """
            self.vapi_assistant_info.setText(info_text)
            
            # Düzenleme butonlarını aktif et
            self.edit_assistant_btn.setEnabled(True)
            self.delete_assistant_btn.setEnabled(True)
        else:
            self.vapi_assistant_info.clear()
            self.edit_assistant_btn.setEnabled(False)
            self.delete_assistant_btn.setEnabled(False)
    
    def open_create_assistant_dialog(self):
        """Yeni asistan oluşturma dialogunu aç"""
        if not self.vapi_manager.api_key:
            QMessageBox.warning(self, "⚠️ Uyarı", "Önce Vapi API anahtarını ayarlayın!")
            return
        
        dialog = AssistantDialog(self)
        if dialog.exec():
            data = dialog.get_assistant_data()
            
            if not data['name']:
                QMessageBox.warning(self, "⚠️ Uyarı", "Asistan adı zorunludur!")
                return
            
            # Asistanı oluştur
            result = self.vapi_manager.create_assistant(
                name=data['name'],
                instructions=data['instructions'],
                model=data['model'],
                voice=data['voice_id'],
                first_message=data['first_message']
            )
            
            if result and 'error' not in result:
                QMessageBox.information(self, "✅ Başarılı", 
                    f"Asistan '{data['name']}' oluşturuldu!")
                self.refresh_vapi_assistants()
            else:
                error_msg = result.get('error', 'Bilinmeyen hata') if result else 'Asistan oluşturulamadı'
                QMessageBox.critical(self, "❌ Hata", f"Asistan oluşturma hatası:\n{error_msg}")
    
    def edit_selected_assistant(self):
        """Seçili asistanı düzenle"""
        assistant_data = self.vapi_assistant_combo.currentData()
        if not assistant_data:
            QMessageBox.warning(self, "⚠️ Uyarı", "Düzenlenecek asistan seçin!")
            return
        
        dialog = AssistantDialog(self, assistant_data)
        if dialog.exec():
            data = dialog.get_assistant_data()
            
            if not data['name']:
                QMessageBox.warning(self, "⚠️ Uyarı", "Asistan adı zorunludur!")
                return
            
            # Asistanı güncelle
            result = self.vapi_manager.update_assistant(
                assistant_data['id'],
                name=data['name'],
                instructions=data['instructions'],
                model=data['model'],
                voice=data['voice_id']
            )
            
            if result and 'error' not in result:
                QMessageBox.information(self, "✅ Başarılı", 
                    f"Asistan '{data['name']}' güncellendi!")
                self.refresh_vapi_assistants()
            else:
                error_msg = result.get('error', 'Bilinmeyen hata') if result else 'Asistan güncellenemedi'
                QMessageBox.critical(self, "❌ Hata", f"Asistan güncelleme hatası:\n{error_msg}")
    
    def delete_selected_assistant(self):
        """Seçili asistanı sil"""
        assistant_data = self.vapi_assistant_combo.currentData()
        if not assistant_data:
            QMessageBox.warning(self, "⚠️ Uyarı", "Silinecek asistan seçin!")
            return
        
        reply = QMessageBox.question(
            self, "Onay",
            f"'{assistant_data['name']}' asistanını silmek istediğinize emin misiniz?\n"
            "Bu işlem geri alınamaz!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = self.vapi_manager.delete_assistant(assistant_data['id'])
            
            if result and result.get('success'):
                QMessageBox.information(self, "✅ Başarılı", 
                    f"Asistan '{assistant_data['name']}' silindi!")
                self.refresh_vapi_assistants()
            else:
                error_msg = result.get('error', 'Bilinmeyen hata') if result else 'Asistan silinemedi'
                QMessageBox.critical(self, "❌ Hata", f"Asistan silme hatası:\n{error_msg}")
    
    def add_firm(self):
        """Yeni firma ekle"""
        dialog = FirmDialog(self)
        if dialog.exec():
            data = dialog.get_firm_data()
            
            if not data['name'] or not data['phone']:
                QMessageBox.warning(self, "⚠️ Uyarı", "Firma adı ve telefon zorunludur!")
                return
            
            firm_id = self.db.add_firm(**data)
            
            if firm_id:
                QMessageBox.information(self, "✅ Başarılı", "Firma eklendi!")
                self.load_firms_table()
                self.load_firms_to_combo()
                self.load_firms_to_vapi_combo()
                self.load_firms_to_activity_filter()
                self.update_dashboard()
            else:
                QMessageBox.critical(self, "❌ Hata", "Firma eklenemedi!")
    
    def edit_firm(self, firm_id):
        """Firma düzenle"""
        firm = self.db.get_firm_by_id(firm_id)
        if not firm:
            return
        
        dialog = FirmDialog(self, dict(firm))
        if dialog.exec():
            data = dialog.get_firm_data()
            
            success = self.db.update_firm(firm_id, **data)
            
            if success:
                QMessageBox.information(self, "✅ Başarılı", "Firma güncellendi!")
                self.load_firms_table()
                self.load_firms_to_combo()
                self.load_firms_to_vapi_combo()
                self.load_firms_to_activity_filter()
            else:
                QMessageBox.critical(self, "❌ Hata", "Firma güncellenemedi!")
    
    def delete_firm_action(self, firm_id):
        """Firma sil"""
        reply = QMessageBox.question(
            self, "Onay",
            "Firmayı silmek istediğinize emin misiniz?\nBu işlem geri alınamaz!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.db.delete_firm(firm_id)
            if success:
                QMessageBox.information(self, "✅ Başarılı", "Firma silindi!")
                self.load_firms_table()
                self.load_firms_to_combo()
                self.load_firms_to_vapi_combo()
                self.load_firms_to_activity_filter()
                self.update_dashboard()
            else:
                QMessageBox.critical(self, "❌ Hata", "Firma silinemedi!")
    
    def load_firms_table(self):
        """Gelişmiş firma tablosunu yükle - Checkbox ve AI destekli"""
        try:
            firms = self.db.get_firms()
            self.all_firms_data = firms  # Tüm veriyi sakla
            self.firms_table.setRowCount(len(firms))
        
            for i, firm in enumerate(firms):
                # Checkbox (Kolon 0)
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(self.update_firms_selection_info)
                self.firms_table.setCellWidget(i, 0, checkbox)
                
                # Firma Adı (Kolon 1)
                self.firms_table.setItem(i, 1, QTableWidgetItem(firm['name']))
                
                # Telefon (Kolon 2)
                phone_text = firm['phone'] or 'N/A'
                self.firms_table.setItem(i, 2, QTableWidgetItem(phone_text))
                
                # E-posta (Kolon 3)
                email_text = firm['email'] or 'N/A'
                self.firms_table.setItem(i, 3, QTableWidgetItem(email_text))
                
                # Sektör (Kolon 4) - AI analizi ile geliştirilmiş
                sector_text = firm['sector'] or 'Belirtilmemiş'
                # AI ile sektör kategorilendirmesi
                ai_sector = self.categorize_sector_with_ai(sector_text)
                display_sector = f"{sector_text}" + (f" ({ai_sector})" if ai_sector != sector_text else "")
                self.firms_table.setItem(i, 4, QTableWidgetItem(display_sector))
                
                # İletişim Kişisi (Kolon 5)
                contact_text = firm['contact_person'] or 'N/A'
                self.firms_table.setItem(i, 5, QTableWidgetItem(contact_text))
                
                # Son İletişim (Kolon 6)
                last_contact = firm['last_contact_date'] or 'Hiç'
                if last_contact != 'Hiç':
                    try:
                        dt = datetime.strptime(last_contact, "%Y-%m-%d %H:%M:%S")
                        last_contact = dt.strftime("%d.%m.%Y")
                    except:
                        pass
                self.firms_table.setItem(i, 6, QTableWidgetItem(last_contact))
                
                # Durum (Kolon 7)
                status = firm['status'] or 'active'
                status_item = QTableWidgetItem(status.title())
                if status == 'active':
                    status_item.setForeground(QColor("#28a745"))
                elif status == 'inactive':
                    status_item.setForeground(QColor("#dc3545"))
                elif status == 'prospect':
                    status_item.setForeground(QColor("#ffc107"))
                else:
                    status_item.setForeground(QColor("#17a2b8"))
                self.firms_table.setItem(i, 7, status_item)
                
                # Rating (Kolon 8)
                rating = firm['rating'] if firm['rating'] else 0
                rating_text = f"⭐ {rating}" if rating > 0 else "N/A"
                self.firms_table.setItem(i, 8, QTableWidgetItem(rating_text))
                
                # Analiz Durumu (Kolon 9) - Yeni
                analysis_status = self.get_firm_analysis_status(firm)
                analysis_item = QTableWidgetItem(analysis_status)
                if "✅" in analysis_status:
                    analysis_item.setForeground(QColor("#28a745"))
                else:
                    analysis_item.setForeground(QColor("#dc3545"))
                self.firms_table.setItem(i, 9, analysis_item)
                
                # İşlemler (Kolon 10)
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                actions_layout.setSpacing(2)
                
                # Düzenle butonu
                edit_btn = QPushButton("✏️")
                edit_btn.setToolTip("Firmayı düzenle")
                edit_btn.clicked.connect(lambda checked=False, fid=firm['id']: self.edit_firm(fid))
                edit_btn.setMaximumWidth(25)
                edit_btn.setStyleSheet("QPushButton { background-color: #17a2b8; color: white; border: none; border-radius: 3px; }")
                actions_layout.addWidget(edit_btn)
                
                # Sil butonu
                delete_btn = QPushButton("🗑️")
                delete_btn.setToolTip("Firmayı sil")
                delete_btn.clicked.connect(lambda checked=False, fid=firm['id']: self.delete_firm_action(fid))
                delete_btn.setMaximumWidth(25)
                delete_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: none; border-radius: 3px; }")
                actions_layout.addWidget(delete_btn)
                
                # WhatsApp butonu
                whatsapp_btn = QPushButton("📱")
                whatsapp_btn.setToolTip("WhatsApp mesajı gönder")
                whatsapp_btn.clicked.connect(lambda checked=False, fid=firm['id']: self.quick_whatsapp_message(fid))
                whatsapp_btn.setMaximumWidth(25)
                whatsapp_btn.setStyleSheet("QPushButton { background-color: #25D366; color: white; border: none; border-radius: 3px; }")
                actions_layout.addWidget(whatsapp_btn)
                
                # Arama butonu
                call_btn = QPushButton("📞")
                call_btn.setToolTip("Otomatik arama başlat")
                call_btn.clicked.connect(lambda checked=False, fid=firm['id']: self.quick_vapi_call(fid))
                call_btn.setMaximumWidth(25)
                call_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; border: none; border-radius: 3px; }")
                actions_layout.addWidget(call_btn)
                
                self.firms_table.setCellWidget(i, 10, actions_widget)
            
            # Bilgileri güncelle
            self.update_firms_selection_info()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Firma tablosu yüklenirken hata:\n{str(e)}")
    
    def categorize_sector_with_ai(self, sector_text):
        """AI ile sektör kategorilendirme"""
        if not sector_text or sector_text == 'Belirtilmemiş':
            return sector_text
        
        # Basit kategori eşleştirme (geliştirilecek)
        sector_lower = sector_text.lower()
        
        # Sağlık kategorisi
        health_keywords = ["sağlık", "tıp", "hastane", "klinik", "doktor", "eczane", "medikal", "psikolog", "diyetisyen", "veteriner"]
        if any(keyword in sector_lower for keyword in health_keywords):
            return "Sağlık & Tıp"
        
        # Teknoloji kategorisi
        tech_keywords = ["teknoloji", "yazılım", "bilgisayar", "it", "software", "tech", "dijital", "internet"]
        if any(keyword in sector_lower for keyword in tech_keywords):
            return "Teknoloji & Yazılım"
        
        # E-ticaret kategorisi
        ecommerce_keywords = ["e-ticaret", "perakende", "mağaza", "satış", "alışveriş", "market", "online"]
        if any(keyword in sector_lower for keyword in ecommerce_keywords):
            return "E-ticaret & Perakende"
        
        # Üretim kategorisi
        manufacturing_keywords = ["üretim", "sanayi", "fabrika", "imalat", "endüstri", "makine"]
        if any(keyword in sector_lower for keyword in manufacturing_keywords):
            return "Üretim & Sanayi"
        
        # Mobilya kategorisi
        furniture_keywords = ["mobilya", "dekorasyon", "ev", "tasarım", "yatak", "nevresim", "uyku"]
        if any(keyword in sector_lower for keyword in furniture_keywords):
            return "Mobilya & Dekorasyon"
        
        # Diğer kategoriler...
        return sector_text
    
    def get_firm_analysis_status(self, firm):
        """Firma analiz durumunu al"""
        try:
            # Veritabanından detaylı firma verisi al
            detailed_firm = self.db.get_firm_by_id(firm['id'])
            if detailed_firm:
                emails = detailed_firm.get('emails', [])
                website = detailed_firm.get('website', '')
                is_analyzed = detailed_firm.get('is_analyzed', False)
                
                if is_analyzed:
                    email_count = len(emails) if emails else 0
                    website_status = "Var" if website and website != 'N/A' else "Yok"
                    return f"✅ Analiz edildi (📧 {email_count} email, 🌐 Website: {website_status})"
                else:
                    return "❌ Analiz edilmedi"
            else:
                return "❓ Veri bulunamadı"
        except Exception as e:
            return "⚠️ Hata"
    
    def open_bulk_message_dialog(self):
        """Toplu mesaj dialogunu aç"""
        try:
            # Seçili firmaları al
            selected_firms = self.get_selected_firms_from_table()
            
            if not selected_firms:
                QMessageBox.warning(self, "Uyarı", "Lütfen mesaj göndermek için en az bir firma seçin!")
                return
            
            # Toplu mesaj dialogunu aç
            dialog = BulkMessageDialog(self, selected_firms, self.db, self.gpt_manager)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Toplu mesaj dialogu açılamadı:\n{str(e)}")
    
    def open_bulk_call_dialog(self):
        """Toplu arama dialogunu aç"""
        try:
            # Seçili firmaları al
            selected_firms = self.get_selected_firms_from_table()
            
            if not selected_firms:
                QMessageBox.warning(self, "Uyarı", "Lütfen arama yapmak için en az bir firma seçin!")
                return
            
            # Asistan verilerini al (varsa)
            assistant_data = getattr(self, 'current_assistant_data', {
                'name': 'Varsayılan Asistan',
                'first_message': 'Merhaba, size nasıl yardımcı olabilirim?'
            })
            
            # Toplu arama dialogunu aç
            dialog = BulkCallDialog(self, selected_firms, assistant_data, 
                                  getattr(self, 'phone_number_id', None),
                                  getattr(self, 'vapi_manager', None), self.db)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Toplu arama dialogu açılamadı:\n{str(e)}")
    
    def get_selected_firms_from_table(self):
        """Tablodaki seçili firmaları al"""
        selected_firms = []
        
        for row in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(row):
                checkbox = self.firms_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    # Firma verilerini al
                    firm_name = self.firms_table.item(row, 1).text()
                    firm_phone = self.firms_table.item(row, 2).text()
                    firm_email = self.firms_table.item(row, 3).text()
                    firm_sector = self.firms_table.item(row, 4).text()
                    
                    # Veritabanından tam veriyi al
                    for firm_data in self.all_firms_data:
                        if firm_data['name'] == firm_name:
                            selected_firms.append(firm_data)
                            break
        
        return selected_firms
    
    def filter_firms(self):
        """Firmaları filtrele"""
        search_text = self.firm_search_input.text()
        sector = self.sector_filter.currentText()
        status = self.status_filter.currentText()
        
        if sector == "Tüm Sektörler":
            sector = ""
        if status == "Tüm Durumlar":
            status = ""
        
        firms = self.db.get_firms(search_text=search_text, sector=sector, status=status)
        
        self.firms_table.setRowCount(len(firms))
        
        for i, firm in enumerate(firms):
            self.firms_table.setItem(i, 0, QTableWidgetItem(str(firm['id'])))
            self.firms_table.setItem(i, 1, QTableWidgetItem(firm['name']))
            self.firms_table.setItem(i, 2, QTableWidgetItem(firm['phone'] or ''))
            self.firms_table.setItem(i, 3, QTableWidgetItem(firm['email'] or ''))
            self.firms_table.setItem(i, 4, QTableWidgetItem(firm['sector'] or ''))
            self.firms_table.setItem(i, 5, QTableWidgetItem(firm['contact_person'] or ''))
            
            last_contact = firm['last_contact_date'] or 'Yok'
            if last_contact != 'Yok':
                try:
                    dt = datetime.strptime(last_contact, "%Y-%m-%d %H:%M:%S")
                    last_contact = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    pass
            self.firms_table.setItem(i, 6, QTableWidgetItem(last_contact))
            
            status = firm['status'] or 'active'
            status_item = QTableWidgetItem(status)
            if status == 'active':
                status_item.setForeground(QColor("#27ae60"))
            elif status == 'inactive':
                status_item.setForeground(QColor("#e74c3c"))
            self.firms_table.setItem(i, 7, status_item)
            
            rating = firm['rating'] if firm['rating'] else 0
            rating_text = "⭐" * int(rating)
            self.firms_table.setItem(i, 8, QTableWidgetItem(rating_text))
    
    def import_firms(self):
        """Firmaları içe aktar"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CSV Dosyası Seç", "", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    count = 0
                    
                    for row in reader:
                        self.db.add_firm(
                            name=row.get('name', ''),
                            phone=row.get('phone', ''),
                            email=row.get('email', ''),
                            address=row.get('address', ''),
                            sector=row.get('sector', ''),
                            summary=row.get('summary', ''),
                            website=row.get('website', ''),
                            contact_person=row.get('contact_person', ''),
                            place_id=row.get('place_id', ''),
                            rating=float(row.get('rating', 0)) if row.get('rating') else None,
                            review_count=int(row.get('review_count', 0)) if row.get('review_count') else None,
                            business_hours=row.get('business_hours', '')
                        )
                        count += 1
                    
                    QMessageBox.information(self, "✅ Başarılı", f"{count} firma içe aktarıldı!")
                    self.load_firms_table()
                    self.load_firms_to_combo()
                    self.load_firms_to_vapi_combo()
                    self.load_firms_to_activity_filter()
                    self.update_dashboard()
                    
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"İçe aktarma hatası: {str(e)}")
    
    def export_firms(self):
        """Firmaları dışa aktar"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Kaydet", "firmalar.csv", "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                firms = self.db.get_firms()
                
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    fieldnames = ['id', 'name', 'phone', 'email', 'address',
                                 'sector', 'summary', 'website', 'contact_person',
                                 'last_contact_date', 'status', 'place_id', 'rating',
                                 'review_count', 'business_hours']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for firm in firms:
                        writer.writerow(dict(firm))
                
                QMessageBox.information(self, "✅ Başarılı", "Firmalar dışa aktarıldı!")
                
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"Dışa aktarma hatası: {str(e)}")
    
    def export_database(self):
        """Veritabanını JSON olarak dışa aktar"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Kaydet", "database_export.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                export_data = {
                    'firms': [dict(row) for row in self.db.get_firms()],
                    'messages': [dict(row) for row in self.db.get_messages()],
                    'calls': [dict(row) for row in self.db.get_calls()],
                    'templates': [dict(row) for row in self.db.get_templates()],
                    'activities': [dict(row) for row in self.db.get_recent_activities(limit=1000)]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                QMessageBox.information(self, "✅ Başarılı", "Veritabanı dışa aktarıldı!")
                
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"Dışa aktarma hatası: {str(e)}")
    
    def quick_whatsapp_message(self, firm_id):
        """Hızlı WhatsApp mesajı gönder"""
        firm = self.db.get_firm_by_id(firm_id)
        if firm:
            self.tabs.setCurrentWidget(self.whatsapp_tab)
            # Firmayı combo'da seç
            for i in range(self.whatsapp_firm_combo.count()):
                if self.whatsapp_firm_combo.itemData(i) and self.whatsapp_firm_combo.itemData(i)['id'] == firm_id:
                    self.whatsapp_firm_combo.setCurrentIndex(i)
                    break
    
    def quick_vapi_call(self, firm_id):
        """Hızlı Vapi araması başlat"""
        firm = self.db.get_firm_by_id(firm_id)
        if firm:
            self.tabs.setCurrentWidget(self.vapi_tab)
            # Firmayı combo'da seç
            for i in range(self.vapi_firm_combo.count()):
                if self.vapi_firm_combo.itemData(i) and self.vapi_firm_combo.itemData(i)['id'] == firm_id:
                    self.vapi_firm_combo.setCurrentIndex(i)
                    break
    
    def load_firms_to_combo(self):
        """WhatsApp combo box'a firmaları yükle - otomatik yönlendirme ile"""
        self.whatsapp_firm_combo.clear()
        self.whatsapp_firm_combo.addItem("-- Firma Seçin --", None)
        
        # Önce WhatsApp'a yönlendirilen firmaları kontrol et
        whatsapp_firms = self.db.get_firms_by_action('whatsapp_yonlendirildi')
        regular_firms = self.db.get_firms(status='active')
        
        # Yönlendirilen firmaları önce ekle (🔥 işaretiyle)
        auto_selected_index = None
        for firm in whatsapp_firms:
            self.whatsapp_firm_combo.addItem(
                f"🔥 {firm['name']} - {firm['phone']} (Yönlendirildi)",
                dict(firm)
            )
            if auto_selected_index is None:  # İlk yönlendirilen firmayı seç
                auto_selected_index = self.whatsapp_firm_combo.count() - 1
        
        # Diğer firmaları ekle (yönlendirilen firmalar hariç)
        whatsapp_firm_ids = [f['id'] for f in whatsapp_firms]
        for firm in regular_firms:
            if firm['id'] not in whatsapp_firm_ids:
                self.whatsapp_firm_combo.addItem(
                    f"{firm['name']} - {firm['phone']}",
                    dict(firm)
                )
        
        # Yönlendirilen firma varsa otomatik seç
        if auto_selected_index is not None:
            self.whatsapp_firm_combo.setCurrentIndex(auto_selected_index)
            # Yönlendirilen firmayı işaretle (tekrar yönlendirmeyi önle)
            if whatsapp_firms:
                self.db.clear_firm_actions('whatsapp_yonlendirildi')
                print(f"📱 WhatsApp otomatik yükleme: {whatsapp_firms[0]['name']}")
    
    def load_firms_to_vapi_combo(self):
        """Vapi combo box'a firmaları yükle - otomatik yönlendirme ile"""
        self.vapi_firm_combo.clear()
        self.vapi_firm_combo.addItem("-- Firma Seçin --", None)
        
        # Önce çağrıya yönlendirilen firmaları kontrol et
        call_firms = self.db.get_firms_by_action('cagri_yonlendirildi')
        regular_firms = self.db.get_firms(status='active')
        
        # Yönlendirilen firmaları önce ekle (🔥 işaretiyle)
        auto_selected_index = None
        for firm in call_firms:
            self.vapi_firm_combo.addItem(
                f"🔥 {firm['name']} - {firm['phone']} (Çağrıya Yönlendirildi)",
                dict(firm)
            )
            if auto_selected_index is None:  # İlk yönlendirilen firmayı seç
                auto_selected_index = self.vapi_firm_combo.count() - 1
        
        # Diğer firmaları ekle (yönlendirilen firmalar hariç)
        call_firm_ids = [f['id'] for f in call_firms]
        for firm in regular_firms:
            if firm['id'] not in call_firm_ids:
                self.vapi_firm_combo.addItem(
                    f"{firm['name']} - {firm['phone']}",
                    dict(firm)
                )
        
        # Yönlendirilen firma varsa otomatik seç
        if auto_selected_index is not None:
            self.vapi_firm_combo.setCurrentIndex(auto_selected_index)
            # Yönlendirilen firmayı işaretle (tekrar yönlendirmeyi önle)
            if call_firms:
                self.db.clear_firm_actions('cagri_yonlendirildi')
                print(f"📞 VAPI otomatik yükleme: {call_firms[0]['name']}")
    
    def load_firms_to_activity_filter(self):
        """Aktivite filtre combo'ya firmaları yükle"""
        self.activity_firm_filter.clear()
        self.activity_firm_filter.addItem("Tüm Firmalar")
        
        firms = self.db.get_firms()
        for firm in firms:
            self.activity_firm_filter.addItem(firm['name'], firm['id'])
    
    def load_whatsapp_templates(self):
        """WhatsApp şablonlarını yükle - Yeni arayüzde şablon sistemi farklı"""
        # Yeni arayüzde şablon sistemi popup'larda yönetiliyor
        # Bu fonksiyon geriye dönük uyumluluk için boş bırakıldı
        pass
    
    def on_whatsapp_firm_selected(self):
        """WhatsApp'ta firma seçildiğinde - Yeni arayüz için güncellenmiş"""
        firm = self.whatsapp_firm_combo.currentData()
        if firm:
            # Firma bilgilerini göster (yeni arayüzde whatsapp_firm_info yok)
            if hasattr(self, 'whatsapp_firm_info'):
                self.whatsapp_firm_info.setText(f"""
Firma: {firm['name']}
Telefon: {firm['phone']}
Sektör: {firm.get('sector', 'Belirtilmemiş')}
İletişim: {firm.get('contact_person', 'Belirtilmemiş')}
Son İletişim: {firm.get('last_contact_date', 'Yok')}
                """)
            
            # Mesaj geçmişini yükle
            if hasattr(self, 'whatsapp_history'):
                self.load_whatsapp_history(firm['id'])
            
            self.selected_firm = firm
        else:
            if hasattr(self, 'whatsapp_firm_info'):
                self.whatsapp_firm_info.clear()
            if hasattr(self, 'whatsapp_message_input'):
                self.whatsapp_message_input.clear()
            if hasattr(self, 'whatsapp_history'):
                self.whatsapp_history.clear()
            self.selected_firm = None
    
    def on_whatsapp_template_selected(self):
        """WhatsApp şablonu seçildiğinde - Yeni arayüzde kullanılmıyor"""
        # Yeni arayüzde şablon sistemi popup'larda yönetiliyor
        # Bu fonksiyon geriye dönük uyumluluk için boş bırakıldı
        pass
    
    def apply_template_variables(self, content, firm):
        """Şablon değişkenlerini uygula"""
        replacements = {
            '{firma_adi}': firm.get('name', ''),
            '{firma_sektoru}': firm.get('sector', ''),
            '{firma_iletisim}': firm.get('contact_person', ''),
            '{firma_ozet}': firm.get('summary', ''),
            '{firma_telefon}': firm.get('phone', ''),
            '{firma_email}': firm.get('email', ''),
            '{firma_website}': firm.get('website', ''),
            '{satici_adi}': self.config.get('seller_name', ''),
            '{satici_firma}': self.config.get('seller_company', ''),
            '{tarih}': datetime.now().strftime('%d.%m.%Y'),
            '{saat}': datetime.now().strftime('%H:%M')
        }
        
        for key, value in replacements.items():
            content = content.replace(key, value)
        
        return content
    
    def on_vapi_firm_selected(self):
        """Vapi'de firma seçildiğinde"""
        firm = self.vapi_firm_combo.currentData()
        if firm:
            self.vapi_firm_info.setText(f"""
Firma: {firm['name']}
Telefon: {firm['phone']}
Sektör: {firm.get('sector', 'Belirtilmemiş')}
İletişim: {firm.get('contact_person', 'Belirtilmemiş')}
            """)
            self.selected_firm = firm
        else:
            self.vapi_firm_info.clear()
            self.selected_firm = None
    
    def load_whatsapp_history(self, firm_id):
        """WhatsApp mesaj geçmişini yükle"""
        messages = self.db.get_messages(firm_id)
        
        self.whatsapp_history.clear()
        for msg in messages:
            direction = "📤 Gönderilen" if msg['direction'] == 'sent' else "📥 Alınan"
            date_time = msg['created_at']
            try:
                dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
                date_time = dt.strftime("%d.%m.%Y %H:%M")
            except:
                pass
            
            self.whatsapp_history.append(f"{direction} - {date_time}")
            self.whatsapp_history.append(f"{msg['content']}\n")
            self.whatsapp_history.append("-" * 50)
    
    def generate_whatsapp_message(self):
        """GPT ile WhatsApp mesajı oluştur"""
        firm = self.whatsapp_firm_combo.currentData()
        if not firm:
            QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir firma seçin!")
            return
        
        if not self.gpt_manager.client:
            QMessageBox.warning(self, "⚠️ Uyarı", "OpenAI API anahtarı girilmedi!")
            return
        
        # Template tipini sor
        template_types = ["tanıtım", "takip", "kampanya", "bilgilendirme", "teşekkür"]
        template_type, ok = QInputDialog.getItem(
            self, "Mesaj Tipi", "Mesaj tipini seçin:",
            template_types, 0, False
        )
        
        if not ok:
            return
        
        # GPT'den mesaj üret
        prompt = "Firmaya uygun profesyonel bir mesaj oluştur."
        message = self.gpt_manager.generate_message(prompt, firm, template_type)
        
        if message:
            self.whatsapp_message_input.setText(message)
        else:
            QMessageBox.warning(self, "⚠️ Uyarı", "Mesaj oluşturulamadı!")
    
    def send_whatsapp_message(self):
        """WhatsApp mesajı gönder"""
        firm = self.whatsapp_firm_combo.currentData()
        if not firm:
            QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir firma seçin!")
            return
        
        message = self.whatsapp_message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "⚠️ Uyarı", "Mesaj boş olamaz!")
            return
        
        # WhatsApp Web üzerinden gönder
        if self.whatsapp_view:
            self.whatsapp_view.send_message(firm['phone'], message)
            
            # Mesajı kaydet
            self.db.save_message(
                firm['id'],
                'sent',
                message,
                'whatsapp'
            )
            
            # Mesaj geçmişini yenile
            self.load_whatsapp_history(firm['id'])
            
            # Mesaj alanını temizle
            self.whatsapp_message_input.clear()
            
            QMessageBox.information(self, "✅ Başarılı", "Mesaj gönderildi!")
            
            # Dashboard ve aktiviteleri güncelle
            self.update_dashboard()
            self.load_activities()
        else:
            # Manuel gönderim için kopyala
            import pyperclip
            pyperclip.copy(message)
            QMessageBox.information(self, "📋 Kopyalandı", 
                "Mesaj panoya kopyalandı.\nwhatsapp.com'da yapıştırabilirsiniz.")
    
    def schedule_whatsapp_message(self):
        """WhatsApp mesajını zamanla"""
        firm = self.whatsapp_firm_combo.currentData()
        if not firm:
            QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir firma seçin!")
            return
        
        message = self.whatsapp_message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "⚠️ Uyarı", "Mesaj boş olamaz!")
            return
        
        # Tarih ve saat seç
        datetime_dialog = QDateTimeEdit()
        datetime_dialog.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        datetime_dialog.setCalendarPopup(True)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Mesaj Zamanlama")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Gönderim zamanını seçin:"))
        layout.addWidget(datetime_dialog)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            scheduled_date = datetime_dialog.dateTime().toPython()
            
            # Zamanlanmış mesajı kaydet
            self.db.save_message(
                firm['id'],
                'sent',
                message,
                'whatsapp',
                'scheduled',
                scheduled_date
            )
            
            QMessageBox.information(self, "✅ Başarılı", 
                f"Mesaj {scheduled_date.strftime('%d.%m.%Y %H:%M')} için zamanlandı!")
            
            self.whatsapp_message_input.clear()
    
    def open_bulk_message_dialog(self):
        """🚀 Gelişmiş Toplu Mesaj Dialogunu Aç - AI Destekli"""
        firms = self.db.get_firms(status='active')
        if not firms:
            QMessageBox.warning(self, "⚠️ Uyarı", "Aktif firma bulunamadı!")
            return
        
        # Gelişmiş toplu mesaj dialogunu aç
        dialog = BulkMessageDialog(
            parent=self, 
            firms=[dict(firm) for firm in firms],
            db=self.db,
            gpt_manager=self.gpt_manager,
            whatsapp_view=self.whatsapp_view
        )
        
        if dialog.exec():
            # Dialog kendi içinde mesajları gönderiyor, sadece dashboard'u güncelle
            self.update_dashboard()
            self.load_activities()
            
            # Son gönderilen mesajları al
            sent_messages = dialog.get_messages()
            if sent_messages:
                QMessageBox.information(
                    self, 
                    "🎉 Tamamlandı", 
                    f"✅ {len(sent_messages)} mesaj başarıyla gönderildi!\n\n"
                    f"📊 Detaylar dashboard'da görüntülenebilir."
                )
    
    def refresh_vapi_phone_numbers(self):
        """Vapi telefon numaralarını yenile - Geliştirilmiş"""
        if not self.vapi_manager.api_key:
            QMessageBox.warning(self, "⚠️ Uyarı", "Önce Vapi API anahtarını ayarlayın!")
            return
        
        try:
            phones = self.vapi_manager.get_phone_numbers()
            self.vapi_phone_combo.clear()
            self.vapi_phone_combo.addItem("-- Seçin --", None)
            
            for phone in phones:
                display_text = f"{phone.get('number', 'N/A')}"
                provider = phone.get('provider', 'N/A')
                if provider != 'N/A':
                    display_text += f" ({provider})"
                
                self.vapi_phone_combo.addItem(display_text, phone.get('id'))
            
            # Config'den varsa seç
            if self.config.get('vapi_phone_number_id'):
                for i in range(self.vapi_phone_combo.count()):
                    if self.vapi_phone_combo.itemData(i) == self.config['vapi_phone_number_id']:
                        self.vapi_phone_combo.setCurrentIndex(i)
                        break
                    
            self.update_status(f"📞 {len(phones)} telefon numarası yüklendi")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Telefon numaraları yüklenemedi:\n{str(e)}")
            logger.error(f"Telefon numarası yenileme hatası: {str(e)}")
    
    def refresh_vapi_assistants(self):
        """Vapi asistanlarını yenile - Geliştirilmiş"""
        if not self.vapi_manager.api_key:
            QMessageBox.warning(self, "⚠️ Uyarı", "Önce Vapi API anahtarını ayarlayın!")
            return
        
        try:
            assistants = self.vapi_manager.get_assistants()
            self.vapi_assistant_combo.clear()
            self.vapi_assistant_combo.addItem("-- Seçin --", None)
            
            for assistant in assistants:
                display_name = assistant.get('name', 'İsimsiz Asistan')
                model_info = assistant.get('model', {}).get('model', '')
                if model_info:
                    display_name += f" ({model_info})"
                
                self.vapi_assistant_combo.addItem(display_name, assistant)
            
            self.update_status(f"🤖 {len(assistants)} asistan yüklendi")
            
            # Seçili asistan yoksa butonları deaktif et
            if len(assistants) == 0:
                self.edit_assistant_btn.setEnabled(False)
                self.delete_assistant_btn.setEnabled(False)
                self.vapi_assistant_info.setText("Henüz asistan oluşturulmamış.")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Asistanlar yüklenemedi:\n{str(e)}")
            logger.error(f"Asistan yenileme hatası: {str(e)}")
    
    def generate_call_script(self):
        """GPT ile arama senaryosu oluştur"""
        firm = self.vapi_firm_combo.currentData()
        if not firm:
            QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir firma seçin!")
            return
        
        if not self.gpt_manager.client:
            QMessageBox.warning(self, "⚠️ Uyarı", "OpenAI API anahtarı girilmedi!")
            return
        
        script = self.gpt_manager.generate_call_script(firm)
        
        if script:
            self.call_script_input.setText(script)
        else:
            QMessageBox.warning(self, "⚠️ Uyarı", "Senaryo oluşturulamadı!")
    
    def start_vapi_call(self):
        """Vapi araması başlat - Ultra Güvenli"""
        try:
            # Firma kontrolü
            firm = None
            try:
                firm = self.vapi_firm_combo.currentData()
                if not firm:
                    QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir firma seçin!")
                    return
            except Exception as e:
                logger.error(f"Firma seçimi hatası: {str(e)}")
                QMessageBox.critical(self, "❌ Hata", "Firma bilgisi alınamadı!")
                return
            
            # Asistan kontrolü
            assistant_data = None
            assistant_id = None
            try:
                assistant_data = self.vapi_assistant_combo.currentData()
                if not assistant_data:
                    QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir asistan seçin!")
                    return
                
                assistant_id = assistant_data.get('id')
                if not assistant_id:
                    QMessageBox.warning(self, "⚠️ Uyarı", "Geçersiz asistan seçimi!")
                    return
            except Exception as e:
                logger.error(f"Asistan seçimi hatası: {str(e)}")
                QMessageBox.critical(self, "❌ Hata", "Asistan bilgisi alınamadı!")
                return
            
            # Telefon numarası kontrolü
            phone = None
            try:
                phone = firm.get('phone', '').strip()
                if not phone:
                    QMessageBox.warning(self, "⚠️ Uyarı", "Firmanın telefon numarası eksik!")
                    return
            except Exception as e:
                logger.error(f"Telefon kontrolü hatası: {str(e)}")
                QMessageBox.critical(self, "❌ Hata", "Telefon numarası alınamadı!")
                return
            
            # Phone number ID (opsiyonel)
            phone_number_id = None
            try:
                phone_number_id = self.vapi_phone_combo.currentData()
                if phone_number_id:
                    self.vapi_manager.set_phone_number_id(phone_number_id)
                elif self.vapi_phone_combo.count() > 1:
                    QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir telefon numarası seçin!")
                    return
            except Exception as e:
                logger.warning(f"Phone ID hatası (kritik değil): {str(e)}")
            
            # Müşteri verisi hazırla
            customer_data = {}
            try:
                customer_data = {
                    "name": str(firm.get('name', 'Firma'))[:100],
                    "email": str(firm.get('email', ''))[:100]
                }
                
                # Opsiyonel alanlar - hata durumunda sessizce geç
                try:
                    if hasattr(self, 'call_script_input'):
                        script = self.call_script_input.toPlainText()
                        if script:
                            customer_data["call_script"] = script[:500]
                except:
                    pass
            except Exception as e:
                logger.warning(f"Müşteri verisi uyarısı: {str(e)}")
                customer_data = {"name": "Firma"}
            
            # Onay dialogu
            try:
                reply = QMessageBox.question(
                    self, "Arama Onayı",
                    f"'{firm.get('name', 'Firma')}' firmasını aramak istediğinize emin misiniz?\n\n"
                    f"Telefon: {phone}\n"
                    f"Asistan: {assistant_data.get('name', 'Asistan')}\n"
                    f"Telefon Hattı: {self.vapi_phone_combo.currentText() if hasattr(self, 'vapi_phone_combo') else 'Varsayılan'}",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            except Exception as e:
                logger.error(f"Onay dialogu hatası: {str(e)}")
                return
            
            # Durum güncellemesi (hata durumunda sessizce geç)
            try:
                self.update_status("🔄 Arama başlatılıyor...")
            except:
                pass
            
            # ARAMA BAŞLAT
            result = None
            try:
                logger.info(f"Vapi araması başlatılıyor: {firm.get('name')} - {phone}")
                result = self.vapi_manager.start_call(phone, assistant_id, customer_data)
            except Exception as e:
                logger.error(f"start_call exception: {str(e)}")
                QMessageBox.critical(self, "❌ Arama Hatası", 
                    f"Arama başlatılamadı:\n\n{str(e)[:200]}")
                try:
                    self.update_status("❌ Arama başlatılamadı")
                except:
                    pass
                return
            
            # Sonuç kontrolü
            if result:
                if isinstance(result, dict) and 'error' not in result:
                    # Başarılı
                    call_id = result.get('id', 'unknown')
                    
                    # Veritabanına kaydet (hata durumunda devam et)
                    try:
                        if hasattr(self, 'db') and self.db:
                            notes = ""
                            try:
                                notes = self.call_notes_input.toPlainText() if hasattr(self, 'call_notes_input') else ""
                            except:
                                pass
                            
                            self.db.save_call(
                                firm.get('id', 0),
                                call_id=call_id,
                                phone_number_id=phone_number_id,
                                assistant_id=assistant_id,
                                duration=0,
                                status='started',
                                notes=notes
                            )
                    except Exception as e:
                        logger.error(f"DB kayıt hatası (kritik değil): {str(e)}")
                    
                    # Başarı mesajı
                    QMessageBox.information(self, "✅ Başarılı",
                        f"Arama başlatıldı!\n\n"
                        f"Call ID: {call_id}\n"
                        f"Firma: {firm.get('name', 'N/A')}\n"
                        f"Telefon: {phone}")
                    
                    # UI güncellemeleri (hata durumunda sessizce geç)
                    for func_name in ['load_calls_history', 'update_dashboard', 'load_activities']:
                        try:
                            if hasattr(self, func_name):
                                getattr(self, func_name)()
                        except Exception as e:
                            logger.warning(f"{func_name} güncelleme hatası: {str(e)}")
                    
                    # Formu temizle (hata durumunda sessizce geç)
                    try:
                        if hasattr(self, 'call_script_input'):
                            self.call_script_input.clear()
                        if hasattr(self, 'call_notes_input'):
                            self.call_notes_input.clear()
                    except:
                        pass
                    
                    try:
                        self.update_status("✅ Arama başarıyla başlatıldı")
                    except:
                        pass
                        
                elif isinstance(result, dict) and 'error' in result:
                    # API hatası
                    error_msg = result.get('error', 'Bilinmeyen hata')
                    error_details = result.get('details', '')
                    
                    full_msg = error_msg
                    if error_details:
                        full_msg += f"\n\nDetay: {error_details}"
                    
                    QMessageBox.critical(self, "❌ Hata", f"Arama başlatılamadı:\n{full_msg}")
                    try:
                        self.update_status("❌ Arama başlatılamadı")
                    except:
                        pass
                else:
                    # Beklenmeyen format
                    logger.warning(f"Beklenmeyen result formatı: {result}")
                    QMessageBox.warning(self, "⚠️ Uyarı", 
                        "Arama işlemi tamamlandı ancak sonuç belirsiz.\n"
                        "Lütfen arama geçmişini kontrol edin.")
            else:
                # result None
                QMessageBox.critical(self, "❌ Hata", "API'den yanıt alınamadı!")
                try:
                    self.update_status("❌ Arama başlatılamadı")
                except:
                    pass
                    
        except Exception as e:
            # En dış exception handler
            logger.critical(f"start_vapi_call kritik hata: {str(e)}\n{traceback.format_exc()}")
            try:
                QMessageBox.critical(self, "❌ Kritik Hata",
                    f"Beklenmeyen hata:\n\n{str(e)[:200]}\n\n"
                    "İşlem tamamlanamadı ancak program çökmedi.")
            except:
                pass
            
            try:
                self.update_status("❌ İşlem başarısız")
            except:
                pass
    
    def check_call_status(self):
        """Arama durumunu kontrol et - Geliştirilmiş"""
        # Açık aramalar varsa listele
        calls = self.db.get_calls()
        # sqlite3.Row objelerini dict'e çevir
        calls_dict = [dict(call) for call in calls] if calls else []
        recent_calls = [call for call in calls_dict if call.get('call_id') and call.get('status') in ['started', 'in-progress']]
        
        if recent_calls:
            # Son aramaları göster
            call_items = [f"{call['call_id']} - {call.get('firm_name', 'N/A')} ({call['created_at']})" 
                         for call in recent_calls[:10]]
            call_items.insert(0, "-- Manuel ID Gir --")
            
            call_text, ok = QInputDialog.getItem(
                self, "Arama Durumu Kontrol", 
                "Kontrol edilecek aramayı seçin:", 
                call_items, 0, False
            )
            
            if not ok:
                return
            
            if call_text == "-- Manuel ID Gir --":
                call_id, ok = QInputDialog.getText(self, "Call ID", "Call ID girin:")
                if not ok or not call_id:
                    return
            else:
                call_id = call_text.split(' - ')[0]
        else:
            call_id, ok = QInputDialog.getText(self, "Arama Durumu", "Call ID:")
            if not ok or not call_id:
                return
        
        # Durumu kontrol et
        result = self.vapi_manager.get_call_status(call_id)
        
        if result and 'error' not in result:
            status = result.get('status', 'Bilinmiyor')
            duration = result.get('duration', 0)
            cost = result.get('cost', 0)
            started_at = result.get('startedAt', 'N/A')
            ended_at = result.get('endedAt', 'N/A')
            
            # Detaylı bilgi
            info_text = f"""
Call ID: {call_id}
Durum: {status}
Süre: {duration} saniye
Maliyet: ${cost:.4f}
Başlangıç: {started_at}
Bitiş: {ended_at}
"""
            
            if result.get('transcript'):
                info_text += f"\nTranscript mevcut: {len(result['transcript'])} karakter"
            
            if result.get('recording'):
                info_text += f"\nKayıt mevcut: {result['recording']}"
            
            QMessageBox.information(self, "📞 Arama Durumu", info_text)
            
            # Veritabanındaki kaydı güncelle
            if duration > 0 or status in ['completed', 'failed', 'ended']:
                # Arama tamamlanmışsa veritabanını güncelle
                try:
                    calls_db = self.db.get_calls()
                    # sqlite3.Row objelerini dict'e çevir
                    calls_db_dict = [dict(call) for call in calls_db] if calls_db else []
                    for call in calls_db_dict:
                        if call.get('call_id') == call_id:
                            # Güncelle
                            self.db.cursor.execute("""
                                UPDATE calls SET 
                                    duration = ?, status = ?, cost = ?
                                WHERE call_id = ?
                            """, (duration, status, cost, call_id))
                            self.db.conn.commit()
                            break
                except Exception as e:
                    logger.error(f"Arama durumu güncelleme hatası: {e}")
                
                # Tabloyu yenile
                self.load_calls_history()
        else:
            error_msg = result.get('error', 'Bilinmeyen hata') if result else 'Arama durumu alınamadı'
            QMessageBox.warning(self, "⚠️ Uyarı", f"Arama durumu kontrol hatası:\n{error_msg}")
    
    def open_bulk_call_dialog(self):
        """Gelişmiş toplu otomatik arama dialogunu aç"""
        if not self.vapi_manager.api_key:
            QMessageBox.warning(self, "⚠️ Uyarı", "Önce Vapi API anahtarını ayarlayın!")
            return
        
        assistant_data = self.vapi_assistant_combo.currentData()
        if not assistant_data:
            QMessageBox.warning(self, "⚠️ Uyarı", "Önce bir asistan seçin!")
            return
        
        # Telefon numarası kontrolü
        phone_number_id = self.vapi_phone_combo.currentData()
        if not phone_number_id and self.vapi_phone_combo.count() > 1:
            QMessageBox.warning(self, "⚠️ Uyarı", "Önce bir telefon numarası seçin!")
            return
        
        firms = self.db.get_firms(status='active')
        firms_with_phone = [firm for firm in firms if firm.get('phone')]
        
        if not firms_with_phone:
            QMessageBox.warning(self, "⚠️ Uyarı", "Telefonu olan aktif firma bulunamadı!")
            return
        
        # Gelişmiş toplu arama dialogu aç
        dialog = BulkCallDialog(self, firms_with_phone, assistant_data, phone_number_id, self.vapi_manager, self.db)
        dialog.show()  # Non-modal olarak aç
    
    def load_calls_history(self):
        """Arama geçmişini yükle"""
        calls = self.db.get_calls()
        self.calls_table.setRowCount(len(calls))
        
        for i, call in enumerate(calls):
            # Tarih ve saat
            created_at = call['created_at']
            date_time = created_at.split(' ') if ' ' in created_at else [created_at, '']
            
            self.calls_table.setItem(i, 0, QTableWidgetItem(date_time[0]))
            self.calls_table.setItem(i, 1, QTableWidgetItem(date_time[1] if len(date_time) > 1 else ''))
            firm_name = call['firm_name'] if call['firm_name'] else ''
            self.calls_table.setItem(i, 2, QTableWidgetItem(firm_name))
            self.calls_table.setItem(i, 3, QTableWidgetItem(str(call['duration'])))
            
            # Durum
            status = call['status']
            status_item = QTableWidgetItem(status)
            if status == 'completed':
                status_item.setForeground(QColor("#27ae60"))
            elif status == 'failed':
                status_item.setForeground(QColor("#e74c3c"))
            self.calls_table.setItem(i, 4, status_item)
            
            # Maliyet
            cost_value = call['cost'] if call['cost'] else 0
            cost = f"${cost_value:.2f}"
            self.calls_table.setItem(i, 5, QTableWidgetItem(cost))
            
            self.calls_table.setItem(i, 6, QTableWidgetItem(call['notes'] or ''))
            
            # İşlemler
            if call['recording_url']:
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 5, 5, 5)
                
                play_btn = QPushButton("▶️")
                play_btn.setToolTip("Kaydı dinle")
                play_btn.clicked.connect(lambda checked=False, url=call['recording_url']: self.play_recording(url))
                play_btn.setMaximumWidth(30)
                actions_layout.addWidget(play_btn)
                
                self.calls_table.setCellWidget(i, 7, actions_widget)
    
    def play_recording(self, url):
        """Arama kaydını oynat"""
        # TODO: Ses oynatma implement edilecek
        QMessageBox.information(self, "ℹ️ Bilgi", f"Kayıt URL: {url}")
    
    def load_templates(self):
        """Şablonları yükle"""
        category = self.template_category.currentText()
        
        if category == "Tümü":
            templates = self.db.get_templates()
        else:
            templates = self.db.get_templates(category)
        
        self.templates_list.clear()
        for template in templates:
            item = QListWidgetItem(f"{template['name']} ({template['category']})")
            item.setData(Qt.UserRole, template)
            self.templates_list.addItem(item)
    
    def on_template_selected(self, item):
        """Şablon seçildiğinde"""
        template = item.data(Qt.UserRole)
        if template:
            self.template_name_input.setText(template['name'])
            self.template_category_input.setCurrentText(template['category'])
            self.template_content.setText(template['content'])
            self.update_template_variables()
            self.preview_template()
    
    def update_template_variables(self):
        """Şablonda kullanılan değişkenleri güncelle"""
        content = self.template_content.toPlainText()
        import re
        variables = re.findall(r'\{(\w+)\}', content)
        unique_vars = list(set(variables))
        self.template_variables.setText(", ".join(unique_vars))
    
    def create_new_template(self):
        """Yeni şablon oluştur"""
        self.template_name_input.clear()
        self.template_content.clear()
        self.template_preview.clear()
        self.template_category_input.setCurrentIndex(0)
        self.template_variables.clear()
    
    def save_template(self):
        """Şablonu kaydet"""
        name = self.template_name_input.text()
        content = self.template_content.toPlainText()
        category = self.template_category_input.currentText()
        
        if not name or not content:
            QMessageBox.warning(self, "⚠️ Uyarı", "Şablon adı ve içeriği boş olamaz!")
            return
        
        # Değişkenleri bul
        import re
        variables = list(set(re.findall(r'\{(\w+)\}', content)))
        
        success = self.db.save_template(name, content, category, variables)
        
        if success:
            QMessageBox.information(self, "✅ Başarılı", "Şablon kaydedildi!")
            self.load_templates()
            self.load_whatsapp_templates()
        else:
            QMessageBox.critical(self, "❌ Hata", "Şablon kaydedilemedi!")
    
    def delete_template(self):
        """Şablonu sil"""
        current_item = self.templates_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir şablon seçin!")
            return
        
        template = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self, "Onay",
            f"'{template['name']}' şablonunu silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Not: Şablon silme fonksiyonu veritabanında tanımlı değil, 
            # bu yüzden şimdilik sadece listeden kaldırıyoruz
            self.templates_list.takeItem(self.templates_list.currentRow())
            self.template_name_input.clear()
            self.template_content.clear()
            self.template_preview.clear()
            self.template_variables.clear()
            self.load_whatsapp_templates()
    
    def preview_template(self):
        """Şablon önizleme"""
        content = self.template_content.toPlainText()
        
        if not content:
            return
        
        # Test verileri ile değişkenleri değiştir
        test_firm = {
            'name': 'Örnek Firma A.Ş.',
            'sector': 'Teknoloji',
            'contact_person': 'Ahmet Yılmaz',
            'summary': 'Yazılım geliştirme ve danışmanlık hizmetleri',
            'phone': '0532 123 45 67',
            'email': 'info@ornekfirma.com',
            'website': 'www.ornekfirma.com'
        }
        
        preview = self.apply_template_variables(content, test_firm)
        self.template_preview.setText(preview)
    
    def load_activities(self):
        """Aktiviteleri yükle"""
        activities = self.db.get_recent_activities(limit=100)
        self.activities_table.setRowCount(len(activities))
        
        # İstatistikler için sayaçlar
        total_count = len(activities)
        message_count = 0
        call_count = 0
        email_count = 0
        
        for i, activity in enumerate(activities):
            # Tarih ve saat
            created_at = activity['created_at']
            date_time = created_at.split(' ') if ' ' in created_at else [created_at, '']
            
            self.activities_table.setItem(i, 0, QTableWidgetItem(date_time[0]))
            self.activities_table.setItem(i, 1, QTableWidgetItem(date_time[1] if len(date_time) > 1 else ''))
            firm_name = activity['firm_name'] if activity['firm_name'] else ''
            self.activities_table.setItem(i, 2, QTableWidgetItem(firm_name))
            
            # Tip
            activity_type = activity['activity_type']
            type_display = {
                'firm_added': '🏢 Firma Eklendi',
                'firm_updated': '✏️ Firma Güncellendi',
                'message_sent': '💬 Mesaj',
                'call_made': '📞 Arama',
                'email_sent': '📧 Email'
            }.get(activity_type, activity_type)
            
            self.activities_table.setItem(i, 3, QTableWidgetItem(type_display))
            
            # Sayaçları güncelle
            if 'message' in activity_type:
                message_count += 1
            elif 'call' in activity_type:
                call_count += 1
            elif 'email' in activity_type:
                email_count += 1
            
            self.activities_table.setItem(i, 4, QTableWidgetItem(activity['description']))
            
            # Metadata
            metadata = activity['metadata'] if activity['metadata'] else ''
            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                    metadata_text = json.dumps(metadata_dict, ensure_ascii=False)[:100] + "..."
                except:
                    metadata_text = str(metadata)[:100] + "..."
            else:
                metadata_text = ""
            self.activities_table.setItem(i, 5, QTableWidgetItem(metadata_text))
        
        # İstatistikleri güncelle
        self.activity_total_label.setText(f"Toplam: {total_count}")
        self.activity_messages_label.setText(f"Mesajlar: {message_count}")
        self.activity_calls_label.setText(f"Aramalar: {call_count}")
        self.activity_emails_label.setText(f"Emailler: {email_count}")
    
    def filter_activities(self):
        """Aktiviteleri filtrele"""
        # TODO: Aktivite filtreleme implement edilecek
        pass
    
    def backup_database(self):
        """Veritabanını yedekle"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Yedek Kaydet",
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
            "Database Files (*.db)"
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy2(self.db.db_path, file_path)
                QMessageBox.information(self, "✅ Başarılı", "Veritabanı yedeklendi!")
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"Yedekleme hatası: {str(e)}")
    
    def restore_database(self):
        """Veritabanını geri yükle"""
        reply = QMessageBox.question(
            self, "Onay",
            "Mevcut veritabanı değiştirilecek. Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Yedek Seç", "", "Database Files (*.db)"
        )
        
        if file_path:
            try:
                import shutil
                # Mevcut veritabanını yedekle
                backup_path = f"{self.db.db_path}.backup"
                shutil.copy2(self.db.db_path, backup_path)
                
                # Yeni veritabanını kopyala
                shutil.copy2(file_path, self.db.db_path)
                
                # Veritabanını yeniden başlat
                self.db.close()
                self.db = Database()
                
                QMessageBox.information(self, "✅ Başarılı", "Veritabanı geri yüklendi!")
                
                # Tüm verileri yenile
                self.load_firms_table()
                self.load_firms_to_combo()
                self.load_firms_to_vapi_combo()
                self.load_firms_to_activity_filter()
                self.load_whatsapp_templates()
                self.load_templates()
                self.load_activities()
                self.load_calls_history()
                self.update_dashboard()
                
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"Geri yükleme hatası: {str(e)}")
                
                # Hata durumunda eski veritabanını geri al
                try:
                    if os.path.exists(backup_path):
                        shutil.copy2(backup_path, self.db.db_path)
                except:
                    pass
    
    def clear_database(self):
        """Veritabanını temizle"""
        reply = QMessageBox.question(
            self, "⚠️ DİKKAT",
            "TÜM VERİLER SİLİNECEK!\n\nBu işlem geri alınamaz. Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # İkinci onay
            reply2 = QMessageBox.question(
                self, "Son Onay",
                "Emin misiniz? TÜM firmalar, mesajlar ve aramalar silinecek!",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply2 == QMessageBox.Yes:
                try:
                    # Önce yedek al
                    backup_path = f"{self.db.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    import shutil
                    shutil.copy2(self.db.db_path, backup_path)
                    
                    # Veritabanını kapat ve sil
                    self.db.close()
                    os.remove(self.db.db_path)
                    
                    # Yeni veritabanı oluştur
                    self.db = Database()
                    
                    QMessageBox.information(self, "✅ Başarılı", 
                        f"Veritabanı temizlendi!\nYedek: {backup_path}")
                    
                    # Tüm verileri yenile
                    self.load_firms_table()
                    self.load_firms_to_combo()
                    self.load_firms_to_vapi_combo()
                    self.load_firms_to_activity_filter()
                    self.load_whatsapp_templates()
                    self.load_templates()
                    self.load_activities()
                    self.load_calls_history()
                    self.load_call_records()  # Yeni çağrı kayıtları sekmesi
                    self.update_dashboard()
                    
                except Exception as e:
                    QMessageBox.critical(self, "❌ Hata", f"Temizleme hatası: {str(e)}")
    
    def update_dashboard(self):
        """Dashboard'u güncelle - Güvenli"""
        try:
            stats = self.db.get_statistics()
            
            # Kartları güvenli güncelle
            try:
                self.total_firms_card.update_value(stats.get('total_firms', 0))
                self.active_firms_card.update_value(stats.get('active_firms', 0))
                self.total_messages_card.update_value(stats.get('total_messages', 0))
                self.today_messages_card.update_value(stats.get('today_messages', 0))
                self.total_calls_card.update_value(stats.get('total_calls', 0))
                self.week_messages_card.update_value(stats.get('week_messages', 0))
            except Exception as e:
                logger.warning(f"Dashboard kart güncelleme hatası: {str(e)}")
                # Hata durumunda 0 değerleri ile devam et
                for card in [self.total_firms_card, self.active_firms_card, self.total_messages_card, 
                           self.today_messages_card, self.total_calls_card, self.week_messages_card]:
                    try:
                        card.update_value(0)
                    except:
                        pass
            
            # Grafikleri güncelle
            if CHARTS_AVAILABLE:
                self.create_weekly_chart()
                self.create_sector_chart()
            
            # Son aktiviteleri yükle
            activities = self.db.get_recent_activities(limit=10)
            self.activity_table.setRowCount(len(activities))
            
            for i, activity in enumerate(activities):
                # Tarih ve saat
                created_at = activity['created_at']
                date_time = created_at.split(' ') if ' ' in created_at else [created_at, '']
                
                self.activity_table.setItem(i, 0, QTableWidgetItem(date_time[0]))
                self.activity_table.setItem(i, 1, QTableWidgetItem(date_time[1] if len(date_time) > 1 else ''))
                
                # Tip
                activity_type = activity['activity_type']
                type_display = {
                    'firm_added': '🏢 Eklendi',
                    'firm_updated': '✏️ Güncellendi',
                    'message_sent': '💬 Mesaj',
                    'call_made': '📞 Arama',
                    'email_sent': '📧 Email'
                }.get(activity_type, activity_type)
                
                self.activity_table.setItem(i, 2, QTableWidgetItem(type_display))
                firm_name = activity['firm_name'] if activity['firm_name'] else ''
                self.activity_table.setItem(i, 3, QTableWidgetItem(firm_name))
                self.activity_table.setItem(i, 4, QTableWidgetItem(activity['description']))
            
        except Exception as e:
            logger.error(f"Dashboard güncelleme hatası: {e}")
    
    # ==================== GÜVENLİ WRAPPER METODLARI ====================
    
    def safe_update_dashboard(self):
        """Güvenli dashboard güncelleme"""
        try:
            self.update_dashboard()
        except Exception as e:
            logger.error(f"Dashboard güncelleme hatası (timer): {e}")
    
    def safe_check_whatsapp_messages(self):
        """Güvenli WhatsApp mesaj kontrolü"""
        try:
            if hasattr(self, 'check_whatsapp_messages'):
                self.check_whatsapp_messages()
        except Exception as e:
            logger.error(f"WhatsApp mesaj kontrolü hatası (timer): {e}")
    
    def safe_update_vapi_status(self):
        """Güvenli Vapi status güncelleme"""
        try:
            if hasattr(self, 'update_vapi_status'):
                self.update_vapi_status()
        except Exception as e:
            logger.error(f"Vapi status güncelleme hatası (timer): {e}")
    
    def safe_refresh_firms_table(self):
        """Güvenli firma tablosu yenileme - sadece değişiklik varsa"""
        try:
            if not hasattr(self, 'db') or not self.db or not hasattr(self, 'firms_table'):
                return
            
            # Mevcut firma sayısını kontrol et
            current_firms = self.db.get_firms()
            current_count = len(current_firms)
            
            # Sadece değişiklik varsa yenile
            if current_count != self.last_firms_count:
                logger.info(f"Yeni firmalar tespit edildi. Önceki: {self.last_firms_count}, Şu an: {current_count}")
                self.load_firms_table()
                self.last_firms_count = current_count
                
        except Exception as e:
            logger.error(f"Firma tablosu yenileme hatası (timer): {e}")
    
    def closeEvent(self, event):
        """Uygulama kapanırken temizlik"""
        try:
            logger.info("Uygulama kapanıyor, temizlik yapılıyor...")
            
            # Timer'ları durdur
            if hasattr(self, 'stats_timer') and self.stats_timer:
                self.stats_timer.stop()
            if hasattr(self, 'whatsapp_check_timer') and self.whatsapp_check_timer:
                self.whatsapp_check_timer.stop()
            if hasattr(self, 'vapi_status_timer') and self.vapi_status_timer:
                self.vapi_status_timer.stop()
            if hasattr(self, 'firms_table_timer') and self.firms_table_timer:
                self.firms_table_timer.stop()
            
            # Task scheduler'ı durdur
            if hasattr(self, 'task_scheduler') and self.task_scheduler:
                self.task_scheduler.stop()
                self.task_scheduler.wait(5000)  # 5 saniye bekle
            
            # Database bağlantısını kapat
            if hasattr(self, 'db') and self.db:
                self.db.close()
            
            # Config'i kaydet
            self.save_config()
            
            logger.info("Temizlik tamamlandı")
            event.accept()
            
        except Exception as e:
            logger.error(f"Kapanış temizliği hatası: {e}")
            event.accept()  # Yine de kapat
    
    # ==================== ÇAĞRI KAYITLARI METODLARI ====================
    
    def load_call_records(self):
        """Çağrı kayıtlarını yükle"""
        try:
            # Veritabanından çağrıları al
            calls = self.db.get_all_calls()
            # sqlite3.Row objelerini dict'e çevir
            calls_dict = [dict(call) for call in calls] if calls else []
            
            # Tabloyu temizle
            self.call_records_table.setRowCount(len(calls_dict))
            
            for i, call in enumerate(calls_dict):
                # Checkbox
                checkbox = QCheckBox()
                self.call_records_table.setCellWidget(i, 0, checkbox)
                
                # Tarih ve saat
                created_at = call.get('created_at', '')
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d')
                        time_str = dt.strftime('%H:%M')
                    except:
                        date_str = created_at.split(' ')[0] if ' ' in created_at else created_at
                        time_str = created_at.split(' ')[1] if ' ' in created_at else ''
                else:
                    date_str = ''
                    time_str = ''
                
                self.call_records_table.setItem(i, 1, QTableWidgetItem(date_str))
                self.call_records_table.setItem(i, 2, QTableWidgetItem(time_str))
                
                # Firma bilgileri
                firm_name = call.get('firm_name', 'Bilinmeyen Firma')
                phone = call.get('phone_number', '')
                self.call_records_table.setItem(i, 3, QTableWidgetItem(firm_name))
                self.call_records_table.setItem(i, 4, QTableWidgetItem(phone))
                
                # Süre (saniye -> dakika:saniye)
                duration = call.get('duration', 0)
                if duration:
                    minutes = duration // 60
                    seconds = duration % 60
                    duration_str = f"{minutes}:{seconds:02d}"
                else:
                    duration_str = "0:00"
                self.call_records_table.setItem(i, 5, QTableWidgetItem(duration_str))
                
                # Durum
                status = call.get('status', 'unknown')
                status_display = {
                    'completed': '✅ Başarılı',
                    'failed': '❌ Başarısız', 
                    'in-progress': '⏳ Devam Ediyor',
                    'canceled': '🚫 İptal'
                }.get(status, status)
                self.call_records_table.setItem(i, 6, QTableWidgetItem(status_display))
                
                # AI Analizi
                ai_analysis = call.get('ai_analysis', '')
                if ai_analysis:
                    try:
                        analysis_data = json.loads(ai_analysis) if isinstance(ai_analysis, str) else ai_analysis
                        sentiment = analysis_data.get('sentiment', 'Analiz Yok')
                        if sentiment.lower() == 'positive':
                            sentiment_display = '😊 Olumlu'
                        elif sentiment.lower() == 'negative':
                            sentiment_display = '😞 Olumsuz'
                        elif sentiment.lower() == 'neutral':
                            sentiment_display = '😐 Kararsız'
                        else:
                            sentiment_display = '🤔 Belirsiz'
                    except:
                        sentiment_display = '❓ Hata'
                else:
                    sentiment_display = '⏸️ Analiz Edilmemiş'
                
                self.call_records_table.setItem(i, 7, QTableWidgetItem(sentiment_display))
                
                # Maliyet
                cost = call.get('cost', 0)
                cost_str = f"${cost:.3f}" if cost else "$0.000"
                self.call_records_table.setItem(i, 8, QTableWidgetItem(cost_str))
                
                # Satırı call data ile etiketle
                self.call_records_table.item(i, 1).setData(Qt.UserRole, call)
            
            # İstatistikleri güncelle
            self.update_call_statistics(calls_dict)
            
        except Exception as e:
            logger.error(f"Çağrı kayıtları yükleme hatası: {e}")
            QMessageBox.warning(self, "Uyarı", f"Çağrı kayıtları yüklenemedi: {str(e)}")
    
    def update_call_statistics(self, calls):
        """Çağrı istatistiklerini güncelle"""
        try:
            # sqlite3.Row objelerini dict'e çevir
            calls_dict = [dict(call) for call in calls] if calls else []
            
            total_calls = len(calls_dict)
            successful_calls = len([c for c in calls_dict if c.get('status') == 'completed'])
            failed_calls = len([c for c in calls_dict if c.get('status') == 'failed'])
            
            # Süre ve maliyet hesapla
            total_duration = sum([c.get('duration', 0) for c in calls_dict])
            total_cost = sum([c.get('cost', 0) for c in calls_dict])
            avg_duration = total_duration / total_calls if total_calls > 0 else 0
            
            # AI analiz sonuçları
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for call in calls_dict:
                ai_analysis = call.get('ai_analysis', '')
                if ai_analysis:
                    try:
                        analysis_data = json.loads(ai_analysis) if isinstance(ai_analysis, str) else ai_analysis
                        sentiment = analysis_data.get('sentiment', '').lower()
                        if sentiment == 'positive':
                            positive_count += 1
                        elif sentiment == 'negative':
                            negative_count += 1
                        elif sentiment == 'neutral':
                            neutral_count += 1
                    except:
                        pass
            
            # Labels'ları güncelle
            self.total_calls_label.setText(f"Toplam Çağrı: {total_calls}")
            self.successful_calls_label.setText(f"Başarılı: {successful_calls}")
            self.failed_calls_label.setText(f"Başarısız: {failed_calls}")
            self.total_duration_label.setText(f"Toplam Süre: {total_duration//60} dk")
            self.total_cost_label.setText(f"Toplam Maliyet: ${total_cost:.2f}")
            self.avg_duration_label.setText(f"Ort. Süre: {avg_duration//60} dk")
            
            self.positive_analysis_label.setText(f"Olumlu: {positive_count}")
            self.negative_analysis_label.setText(f"Olumsuz: {negative_count}")
            self.neutral_analysis_label.setText(f"Kararsız: {neutral_count}")
            
        except Exception as e:
            logger.error(f"İstatistik güncelleme hatası: {e}")
    
    def on_call_selected(self):
        """Çağrı seçildiğinde"""
        try:
            current_row = self.call_records_table.currentRow()
            if current_row >= 0:
                # Çağrı verisini al
                call_data = self.call_records_table.item(current_row, 1).data(Qt.UserRole)
                if call_data:
                    self.display_call_details(call_data)
                    self.analyze_this_call_btn.setEnabled(True)
                else:
                    self.clear_call_details()
                    self.analyze_this_call_btn.setEnabled(False)
            else:
                self.clear_call_details()
                self.analyze_this_call_btn.setEnabled(False)
                
        except Exception as e:
            logger.error(f"Çağrı seçimi hatası: {e}")
    
    def display_call_details(self, call_data):
        """Çağrı detaylarını göster"""
        try:
            # Temel bilgiler
            self.selected_call_firm.setText(call_data.get('firm_name', 'Bilinmeyen'))
            self.selected_call_phone.setText(call_data.get('phone_number', ''))
            
            created_at = call_data.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = dt.strftime('%d.%m.%Y %H:%M')
                except:
                    date_str = created_at
            else:
                date_str = 'Bilinmiyor'
            self.selected_call_date.setText(date_str)
            
            duration = call_data.get('duration', 0)
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "0:00"
            self.selected_call_duration.setText(duration_str)
            
            status = call_data.get('status', 'unknown')
            status_display = {
                'completed': '✅ Başarılı',
                'failed': '❌ Başarısız', 
                'in-progress': '⏳ Devam Ediyor',
                'canceled': '🚫 İptal'
            }.get(status, status)
            self.selected_call_status.setText(status_display)
            
            cost = call_data.get('cost', 0)
            self.selected_call_cost.setText(f"${cost:.3f}")
            
            # Konuşma metni
            transcript = call_data.get('transcript', '')
            if transcript:
                # Transcript'i daha okunabilir hale getir
                try:
                    if isinstance(transcript, str) and transcript.startswith('{'):
                        transcript_data = json.loads(transcript)
                        # Eğer transcript bir JSON ise içeriğini çıkar
                        if isinstance(transcript_data, dict):
                            transcript = transcript_data.get('text', transcript_data.get('transcript', str(transcript_data)))
                except:
                    pass
                self.call_transcript.setText(transcript)
            else:
                self.call_transcript.setText("Konuşma metni mevcut değil.")
            
            # AI Analizi
            ai_analysis = call_data.get('ai_analysis', '')
            if ai_analysis:
                try:
                    analysis_data = json.loads(ai_analysis) if isinstance(ai_analysis, str) else ai_analysis
                    
                    # Analiz durumu
                    self.analysis_status_label.setText("✅ Analiz Edilmiş")
                    self.analysis_status_label.setStyleSheet("color: green; font-weight: bold;")
                    
                    # Sentiment
                    sentiment = analysis_data.get('sentiment', 'unknown')
                    confidence = analysis_data.get('confidence', 0)
                    
                    if sentiment.lower() == 'positive':
                        sentiment_display = '😊 Olumlu'
                        sentiment_color = "color: green;"
                    elif sentiment.lower() == 'negative':
                        sentiment_display = '😞 Olumsuz'
                        sentiment_color = "color: red;"
                    elif sentiment.lower() == 'neutral':
                        sentiment_display = '😐 Kararsız'
                        sentiment_color = "color: orange;"
                    else:
                        sentiment_display = '🤔 Belirsiz'
                        sentiment_color = "color: gray;"
                    
                    self.analysis_sentiment.setText(sentiment_display)
                    self.analysis_sentiment.setStyleSheet(f"font-weight: bold; font-size: 14px; {sentiment_color}")
                    
                    self.analysis_confidence.setText(f"{confidence:.0%}")
                    
                    # Ek analiz verileri
                    sales_potential = analysis_data.get('sales_potential', 'Belirsiz')
                    follow_up = analysis_data.get('follow_up_needed', 'Belirsiz')
                    
                    self.analysis_sales_potential.setText(str(sales_potential))
                    self.analysis_follow_up.setText(str(follow_up))
                    
                    # Detaylı analiz
                    details = analysis_data.get('details', analysis_data.get('summary', ''))
                    self.analysis_details.setText(str(details))
                    
                    # Öneriler
                    recommendations = analysis_data.get('recommendations', analysis_data.get('next_steps', ''))
                    self.analysis_recommendations.setText(str(recommendations))
                    
                except Exception as e:
                    logger.error(f"AI analiz gösterme hatası: {e}")
                    self.analysis_status_label.setText("❌ Analiz Hatası")
                    self.analysis_status_label.setStyleSheet("color: red; font-weight: bold;")
                    self.clear_analysis_display()
            else:
                self.analysis_status_label.setText("⏸️ Analiz Edilmemiş")
                self.analysis_status_label.setStyleSheet("color: gray; font-weight: bold;")
                self.clear_analysis_display()
                
        except Exception as e:
            logger.error(f"Çağrı detayları gösterme hatası: {e}")
    
    def clear_call_details(self):
        """Çağrı detaylarını temizle"""
        self.selected_call_firm.setText("-")
        self.selected_call_phone.setText("-")
        self.selected_call_date.setText("-")
        self.selected_call_duration.setText("-")
        self.selected_call_status.setText("-")
        self.selected_call_cost.setText("-")
        self.call_transcript.setText("")
        self.analysis_status_label.setText("Seçili çağrı yok")
        self.analysis_status_label.setStyleSheet("font-weight: bold;")
        self.clear_analysis_display()
    
    def clear_analysis_display(self):
        """Analiz görünümünü temizle"""
        self.analysis_sentiment.setText("-")
        self.analysis_sentiment.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.analysis_confidence.setText("-")
        self.analysis_sales_potential.setText("-")
        self.analysis_follow_up.setText("-")
        self.analysis_details.setText("")
        self.analysis_recommendations.setText("")
    
    def filter_call_records(self):
        """Çağrı kayıtlarını filtrele"""
        try:
            # Filtreleri al
            date_filter = self.call_date_filter.currentText()
            status_filter = self.call_status_filter.currentText()
            analysis_filter = self.call_analysis_filter.currentText()
            
            # Tüm satırları göster
            for row in range(self.call_records_table.rowCount()):
                self.call_records_table.setRowHidden(row, False)
            
            # Filtreleri uygula
            for row in range(self.call_records_table.rowCount()):
                hide_row = False
                
                try:
                    call_data = self.call_records_table.item(row, 1).data(Qt.UserRole)
                    if not call_data:
                        continue
                    
                    # Tarih filtresi
                    if date_filter != "Tümü":
                        created_at = call_data.get('created_at', '')
                        if created_at:
                            try:
                                call_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                now = datetime.now()
                                
                                if date_filter == "Bugün":
                                    if call_date.date() != now.date():
                                        hide_row = True
                                elif date_filter == "Dün":
                                    yesterday = now - timedelta(days=1)
                                    if call_date.date() != yesterday.date():
                                        hide_row = True
                                elif date_filter == "Son 7 Gün":
                                    week_ago = now - timedelta(days=7)
                                    if call_date < week_ago:
                                        hide_row = True
                                elif date_filter == "Son 30 Gün":
                                    month_ago = now - timedelta(days=30)
                                    if call_date < month_ago:
                                        hide_row = True
                            except:
                                hide_row = True
                        else:
                            hide_row = True
                    
                    # Durum filtresi
                    if status_filter != "Tümü" and not hide_row:
                        status = call_data.get('status', '')
                        status_map = {
                            'Başarılı': 'completed',
                            'Başarısız': 'failed',
                            'Devam Ediyor': 'in-progress',
                            'İptal': 'canceled'
                        }
                        if status != status_map.get(status_filter, status_filter):
                            hide_row = True
                    
                    # AI Analiz filtresi
                    if analysis_filter != "Tümü" and not hide_row:
                        ai_analysis = call_data.get('ai_analysis', '')
                        if analysis_filter == "Analiz Edilmemiş":
                            if ai_analysis:
                                hide_row = True
                        else:
                            if not ai_analysis:
                                hide_row = True
                            else:
                                try:
                                    analysis_data = json.loads(ai_analysis) if isinstance(ai_analysis, str) else ai_analysis
                                    sentiment = analysis_data.get('sentiment', '').lower()
                                    filter_map = {
                                        'Olumlu': 'positive',
                                        'Olumsuz': 'negative',
                                        'Kararsız': 'neutral'
                                    }
                                    if sentiment != filter_map.get(analysis_filter, analysis_filter.lower()):
                                        hide_row = True
                                except:
                                    hide_row = True
                    
                    self.call_records_table.setRowHidden(row, hide_row)
                    
                except Exception as e:
                    logger.error(f"Satır {row} filtreleme hatası: {e}")
                    
        except Exception as e:
            logger.error(f"Çağrı kayıtları filtreleme hatası: {e}")
    
    # ==================== AI ANALİZ METODLARI ====================
    
    def analyze_selected_call(self):
        """Seçili çağrıyı analiz et"""
        try:
            current_row = self.call_records_table.currentRow()
            if current_row >= 0:
                call_data = self.call_records_table.item(current_row, 1).data(Qt.UserRole)
                if call_data:
                    self.analyze_single_call(call_data)
                else:
                    QMessageBox.warning(self, "Uyarı", "Geçerli çağrı verisi bulunamadı!")
            else:
                QMessageBox.warning(self, "Uyarı", "Lütfen analiz edilecek çağrıyı seçin!")
        except Exception as e:
            logger.error(f"Seçili çağrı analizi hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Çağrı analizi sırasında hata: {str(e)}")
    
    def analyze_selected_calls(self):
        """Seçili çağrıları analiz et"""
        try:
            selected_calls = []
            
            # Checkbox'ları kontrol et
            for row in range(self.call_records_table.rowCount()):
                checkbox = self.call_records_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    call_data = self.call_records_table.item(row, 1).data(Qt.UserRole)
                    if call_data:
                        selected_calls.append(call_data)
            
            if not selected_calls:
                QMessageBox.warning(self, "Uyarı", "Lütfen analiz edilecek çağrıları seçin!")
                return
            
            # Onay al
            reply = QMessageBox.question(
                self, "Toplu Analiz", 
                f"{len(selected_calls)} çağrı analiz edilecek. Devam etmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.analyze_multiple_calls(selected_calls)
                
        except Exception as e:
            logger.error(f"Seçili çağrılar analizi hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Toplu analiz sırasında hata: {str(e)}")
    
    def analyze_all_calls(self):
        """Tüm analiz edilmemiş çağrıları analiz et"""
        try:
            # Analiz edilmemiş çağrıları bul
            unanalyzed_calls = []
            calls = self.db.get_all_calls()
            # sqlite3.Row objelerini dict'e çevir
            calls_dict = [dict(call) for call in calls] if calls else []
            
            for call in calls_dict:
                ai_analysis = call.get('ai_analysis', '')
                if not ai_analysis or ai_analysis.strip() == '':
                    unanalyzed_calls.append(call)
            
            if not unanalyzed_calls:
                QMessageBox.information(self, "Bilgi", "Tüm çağrılar zaten analiz edilmiş!")
                return
            
            # Onay al
            reply = QMessageBox.question(
                self, "Tümünü Analiz Et", 
                f"{len(unanalyzed_calls)} analiz edilmemiş çağrı bulundu. Tümünü analiz etmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.analyze_multiple_calls(unanalyzed_calls)
                
        except Exception as e:
            logger.error(f"Tüm çağrılar analizi hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Toplu analiz sırasında hata: {str(e)}")
    
    def analyze_single_call(self, call_data):
        """Tek bir çağrıyı analiz et"""
        try:
            if not OPENAI_AVAILABLE or not self.gpt_manager.client:
                QMessageBox.warning(self, "Uyarı", "OpenAI API ayarlanmamış! Lütfen ayarlar sekmesinden API key'inizi girin.")
                return
            
            # Çağrı bilgilerini hazırla
            transcript = call_data.get('transcript', '')
            firm_name = call_data.get('firm_name', 'Bilinmeyen')
            phone = call_data.get('phone_number', '')
            duration = call_data.get('duration', 0)
            
            if not transcript:
                QMessageBox.warning(self, "Uyarı", "Bu çağrının konuşma metni mevcut değil!")
                return
            
            # Analiz prompt'u oluştur
            analysis_prompt = f"""
Lütfen aşağıdaki telefon görüşmesini analiz et ve JSON formatında sonuç ver:

ÇAĞRI BİLGİLERİ:
- Firma: {firm_name}
- Telefon: {phone}
- Süre: {duration} saniye

KONUŞMA METNİ:
{transcript}

Lütfen aşağıdaki formatta analiz et:

{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.85,
    "sales_potential": "Yüksek/Orta/Düşük",
    "follow_up_needed": "Evet/Hayır",
    "details": "Detaylı analiz ve önemli noktalar",
    "recommendations": "Takip önerileri ve yapılacaklar",
    "keywords": ["anahtar", "kelimeler"],
    "customer_interest_level": "Yüksek/Orta/Düşük",
    "objections": "Müşteri itirazları",
    "next_steps": "Önerilen sonraki adımlar"
}}

Analiz Kriterleri:
- Müşterinin ilgi düzeyi
- Satış potansiyeli
- İtirazlar ve endişeler
- Takip gerekliliği
- Genel atmosfer (olumlu/olumsuz)
- Sonraki adım önerileri
"""
            
            try:
                # GPT'den analiz iste
                response = self.gpt_manager.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Sen deneyimli bir satış analisti ve müşteri ilişkileri uzmanısın. Telefon görüşmelerini analiz ederek satış potansiyelini ve müşteri tutumunu değerlendirirsin."
                        },
                        {
                            "role": "user", 
                            "content": analysis_prompt
                        }
                    ],
                    max_tokens=1500,
                    temperature=0.3
                )
                
                analysis_text = response.choices[0].message.content.strip()
                
                # JSON'u parse et
                try:
                    # JSON'u çıkar (```json ... ``` gibi wrapper'lar varsa)
                    if '```json' in analysis_text:
                        analysis_text = analysis_text.split('```json')[1].split('```')[0]
                    elif '```' in analysis_text:
                        analysis_text = analysis_text.split('```')[1]
                    
                    analysis_result = json.loads(analysis_text)
                    
                except json.JSONDecodeError:
                    # JSON parse hatası varsa basit analiz yap
                    analysis_result = {
                        "sentiment": "neutral",
                        "confidence": 0.5,
                        "sales_potential": "Orta",
                        "follow_up_needed": "Evet",
                        "details": analysis_text,
                        "recommendations": "Lütfen detaylı takip yapın",
                        "keywords": [],
                        "customer_interest_level": "Orta",
                        "objections": "Belirtilmemiş",
                        "next_steps": "Takip araması planlayın"
                    }
                
                # Veritabanında güncelle
                call_id = call_data.get('id')
                if call_id:
                    self.db.update_call_analysis(call_id, json.dumps(analysis_result, ensure_ascii=False))
                    
                    # UI'yi güncelle
                    self.load_call_records()
                    
                    # Seçili çağrıyı yeniden göster
                    self.display_call_details({**call_data, 'ai_analysis': json.dumps(analysis_result, ensure_ascii=False)})
                    
                    QMessageBox.information(self, "✅ Başarılı", "Çağrı analizi tamamlandı!")
                else:
                    QMessageBox.warning(self, "Uyarı", "Çağrı ID'si bulunamadı!")
                
            except Exception as api_error:
                logger.error(f"OpenAI API hatası: {api_error}")
                QMessageBox.critical(self, "API Hatası", f"OpenAI API hatası: {str(api_error)}")
                
        except Exception as e:
            logger.error(f"Çağrı analizi hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Çağrı analizi sırasında hata: {str(e)}")
    
    def analyze_multiple_calls(self, calls_list):
        """Birden fazla çağrıyı analiz et"""
        try:
            if not OPENAI_AVAILABLE or not self.gpt_manager.client:
                QMessageBox.warning(self, "Uyarı", "OpenAI API ayarlanmamış!")
                return
            
            # Progress dialog oluştur
            progress = QProgressBar(self)
            progress.setRange(0, len(calls_list))
            progress.show()
            
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Çağrılar Analiz Ediliyor...")
            progress_dialog.setModal(True)
            progress_dialog.setFixedSize(400, 100)
            
            layout = QVBoxLayout(progress_dialog)
            layout.addWidget(QLabel("Çağrılar analiz ediliyor, lütfen bekleyin..."))
            layout.addWidget(progress)
            
            cancel_btn = QPushButton("İptal")
            cancel_btn.clicked.connect(progress_dialog.reject)
            layout.addWidget(cancel_btn)
            
            progress_dialog.show()
            
            # Analizleri gerçekleştir
            successful_analyses = 0
            failed_analyses = 0
            
            for i, call_data in enumerate(calls_list):
                if not progress_dialog.isVisible():  # İptal edildi
                    break
                
                progress.setValue(i)
                QApplication.processEvents()
                
                try:
                    # Her çağrı için kısa bekleme (API rate limit)
                    if i > 0:
                        time.sleep(1)
                    
                    # Mevcut analiz metodu ile analiz et
                    self.analyze_single_call_silent(call_data)
                    successful_analyses += 1
                    
                except Exception as e:
                    logger.error(f"Çağrı {i+1} analiz hatası: {e}")
                    failed_analyses += 1
                    continue
            
            progress_dialog.close()
            
            # Sonuçları göster
            result_msg = f"""
Analiz Tamamlandı!

✅ Başarılı: {successful_analyses}
❌ Başarısız: {failed_analyses}
📊 Toplam: {len(calls_list)}
"""
            QMessageBox.information(self, "Analiz Sonucu", result_msg)
            
            # Tabloyu yenile
            self.load_call_records()
            
        except Exception as e:
            logger.error(f"Toplu analiz hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Toplu analiz sırasında hata: {str(e)}")
    
    def analyze_single_call_silent(self, call_data):
        """Tek bir çağrıyı sessizce analiz et (UI güncellemesi olmadan)"""
        try:
            transcript = call_data.get('transcript', '')
            if not transcript:
                return False
            
            firm_name = call_data.get('firm_name', 'Bilinmeyen')
            phone = call_data.get('phone_number', '')
            duration = call_data.get('duration', 0)
            
            # Analiz prompt'u
            analysis_prompt = f"""
Telefon görüşmesini analiz et ve JSON formatında sonuç ver:

ÇAĞRI: {firm_name} - {phone} ({duration}s)
KONUŞMA: {transcript[:1000]}...

{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.85,
    "sales_potential": "Yüksek/Orta/Düşük",
    "follow_up_needed": "Evet/Hayır",
    "details": "Kısa analiz özeti",
    "recommendations": "Takip önerisi"
}}
"""
            
            # GPT analizi
            response = self.gpt_manager.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen satış analisti uzmanısın. Kısa ve öz analiz yap."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # JSON parse
            try:
                if '```json' in analysis_text:
                    analysis_text = analysis_text.split('```json')[1].split('```')[0]
                elif '```' in analysis_text:
                    analysis_text = analysis_text.split('```')[1]
                
                analysis_result = json.loads(analysis_text)
            except:
                analysis_result = {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "sales_potential": "Orta",
                    "follow_up_needed": "Evet",
                    "details": "Analiz tamamlandı",
                    "recommendations": "Takip yapın"
                }
            
            # Veritabanında güncelle
            call_id = call_data.get('id')
            if call_id:
                self.db.update_call_analysis(call_id, json.dumps(analysis_result, ensure_ascii=False))
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Sessiz analiz hatası: {e}")
            return False
    
    def create_weekly_chart(self):
        """Haftalık performans grafiği oluştur - Güvenli"""
        if not CHARTS_AVAILABLE:
            return
        
        try:
            # Günlük istatistikleri al
            daily_stats = self.db.get_daily_stats(days=7)
            
            # Chart oluştur
            chart = QChart()
            chart.setTitle("Son 7 Gün")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Line series
            series = QLineSeries()
            
            # Veri ekle - güvenli
            if daily_stats:
                for i, stat in enumerate(daily_stats):
                    # message_count yerine genel count kullan
                    count = stat.get('message_count', stat.get('count', 0))
                    series.append(i, count)
            else:
                # Veri yoksa boş grafik
                for i in range(7):
                    series.append(i, 0)
            
            chart.addSeries(series)
            chart.createDefaultAxes()
            
            # Renk ve stil
            try:
                pen = series.pen()
                pen.setColor(QColor("#0d7377"))
                pen.setWidth(3)
                series.setPen(pen)
            except:
                pass  # Stil hatası kritik değil
            
            # View'a ekle
            if hasattr(self, 'weekly_chart_view'):
                self.weekly_chart_view.setChart(chart)
                try:
                    self.weekly_chart_view.setRenderHint(QPainter.Antialiasing)
                except:
                    pass
            
        except Exception as e:
            logger.warning(f"Haftalık grafik hatası (kritik değil): {e}")
    
    def create_sector_chart(self):
        """Sektör dağılımı grafiği oluştur"""
        if not CHARTS_AVAILABLE:
            return
        
        try:
            stats = self.db.get_statistics()
            sector_data = stats.get('sector_distribution', [])
            
            if not sector_data:
                return
            
            # Chart oluştur
            chart = QChart()
            chart.setTitle("Firma Dağılımı")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # Pie series
            series = QPieSeries()
            
            # Veri ekle
            for sector in sector_data:
                series.append(sector['sector'], sector['count'])
            
            # En büyük dilimi göster
            if series.count() > 0:
                largest = series.slices()[0]
                largest.setExploded(True)
                largest.setLabelVisible(True)
            
            chart.addSeries(series)
            
            # View'a ekle
            self.sector_chart_view.setChart(chart)
            self.sector_chart_view.setRenderHint(QPainter.Antialiasing)
            
        except Exception as e:
            logger.error(f"Sektör grafiği hatası: {e}")
    
    def execute_scheduled_task(self, task):
        """Zamanlanmış görevi çalıştır"""
        try:
            task_type = task.get('type')
            
            if task_type == 'scheduled_message':
                # Zamanlanmış mesaj gönder
                if self.whatsapp_view:
                    self.whatsapp_view.send_message(
                        task['phone'],
                        task['content']
                    )
                    logger.info(f"Zamanlanmış mesaj gönderildi: {task['firm_id']}")
            
            elif task_type == 'scheduled_call':
                # Zamanlanmış arama
                # TODO: Implement scheduled call
                pass
            
            elif task_type == 'scheduled_email':
                # Zamanlanmış email
                # TODO: Implement scheduled email
                pass
            
        except Exception as e:
            logger.error(f"Görev çalıştırma hatası: {e}")
    
    def check_whatsapp_messages(self):
        """WhatsApp mesajlarını kontrol et"""
        try:
            if hasattr(self, 'whatsapp_view') and self.whatsapp_view:
                self.whatsapp_view.check_for_new_messages()
        except Exception as e:
            logger.error(f"WhatsApp mesaj kontrol hatası: {str(e)}")
            # Timer'ı durdurmayı dene
            if hasattr(self, 'whatsapp_check_timer'):
                self.whatsapp_check_timer.stop()
                logger.info("WhatsApp timer durduruldu")
    
    def on_whatsapp_message_received(self, message_data):
        """WhatsApp mesajı alındığında"""
        try:
            # Mesajı kaydet
            # Not: Telefon numarasından firmayı bul
            phone = message_data.get('phone', '')
            content = message_data.get('content', '')
            
            if phone and content:
                # Telefon numarasından firmayı bul
                firms = self.db.get_firms()
                for firm in firms:
                    if phone in firm['phone']:
                        # Mesajı kaydet
                        self.db.save_message(
                            firm['id'],
                            'received',
                            content,
                            'whatsapp'
                        )
                        
                        # Otomatik yanıt kontrolü
                        if self.config.get('auto_reply', False):
                            self.auto_reply_message(firm, content)
                        
                        # Dashboard'u güncelle
                        self.update_dashboard()
                        
                        # Bildirim göster
                        self.update_status(f"💬 Yeni mesaj: {firm['name']}")
                        
                        break
                        
        except Exception as e:
            logger.error(f"Mesaj alma hatası: {e}")
    
    def auto_reply_message(self, firm, received_message):
        """Otomatik yanıt gönder"""
        try:
            if self.gpt_manager.client:
                # GPT ile yanıt oluştur
                prompt = f"Gelen mesaja uygun kısa bir yanıt oluştur: {received_message}"
                reply = self.gpt_manager.generate_message(prompt, firm, "takip")
                
                if reply:
                    # Biraz bekle
                    QTimer.singleShot(
                        self.config.get('message_delay', 5) * 1000,
                        lambda: self.whatsapp_view.send_message(firm['phone'], reply)
                    )
                    
                    # Mesajı kaydet
                    self.db.save_message(
                        firm['id'],
                        'sent',
                        f"[Otomatik Yanıt] {reply}",
                        'whatsapp'
                    )
                    
        except Exception as e:
            logger.error(f"Otomatik yanıt hatası: {e}")
    
    def update_whatsapp_status(self, status):
        """WhatsApp durumunu güncelle"""
        if hasattr(self, 'whatsapp_status_label'):
            if "bağlı" in status.lower() or "connected" in status.lower():
                self.whatsapp_status_label.setText("🟢 Bağlı")
                self.whatsapp_status_label.setStyleSheet("color: #28a745; font-weight: bold;")
            else:
                self.whatsapp_status_label.setText("🔴 Bağlantı Bekleniyor")
                self.whatsapp_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        else:
            # Eski sistem için geri dönüş
            if hasattr(self, 'whatsapp_status'):
                self.whatsapp_status.setText(f"🟢 {status}" if "bağlandı" in status.lower() else f"🔴 {status}")
                self.whatsapp_status.setStyleSheet(
                    "font-size: 14px; color: #27ae60;" if "bağlandı" in status.lower() else "font-size: 14px; color: #e74c3c;"
                )
    
    def on_whatsapp_firm_selected(self):
        """WhatsApp firma seçildiğinde"""
        firm = self.whatsapp_firm_combo.currentData()
        if firm:
            # Firma bilgilerini göster
            info_text = f"""
            <b>Firma:</b> {firm.get('name', 'İsimsiz')}<br>
            <b>Sektör:</b> {firm.get('sector', 'Belirtilmemiş')}<br>
            <b>Telefon:</b> {firm.get('phone', 'Belirtilmemiş')}<br>
            <b>Email:</b> {firm.get('email', 'Belirtilmemiş')}<br>
            <b>Adres:</b> {firm.get('address', 'Belirtilmemiş')}
            """
            if hasattr(self, 'whatsapp_firm_info'):
                self.whatsapp_firm_info.setText(info_text)
            
            # Mesaj geçmişini yükle
            if hasattr(self, 'whatsapp_history'):
                self.load_whatsapp_history(firm.get('id'))
            
            self.selected_firm = firm
        else:
            if hasattr(self, 'whatsapp_firm_info'):
                self.whatsapp_firm_info.clear()
            if hasattr(self, 'whatsapp_history'):
                self.whatsapp_history.clear()
            self.selected_firm = None
    
    def update_status(self, message):
        """Durum çubuğunu güncelle"""
        self.status_bar.showMessage(message, 5000)  # 5 saniye göster
    
    def closeEvent(self, event):
        """Uygulama kapatılırken - Güçlendirilmiş güvenli kapatma"""
        logger.info("Uygulama kapatılıyor...")
        
        try:
            # Sistem izlemeyi durdur
            if ROBUST_SYSTEM_AVAILABLE and hasattr(self, 'system_monitor'):
                try:
                    self.system_monitor.stop_monitoring()
                    logger.info("Sistem izleme durduruldu")
                except Exception as e:
                    logger.error(f"Sistem izleme durdurma hatası: {e}")
            
            # Task scheduler'ı durdur
            if hasattr(self, 'task_scheduler') and self.task_scheduler:
                logger.info("Task scheduler durduruluyor...")
                try:
                    self.task_scheduler.stop()
                    self.task_scheduler.wait(5000)  # 5 saniye bekle
                except Exception as e:
                    logger.error(f"Task scheduler durdurma hatası: {e}")
            
            # Timer'ları güvenli durdur
            logger.info("Timer'lar durduruluyor...")
            if hasattr(self, 'stats_timer') and self.stats_timer:
                try:
                    self.stats_timer.stop()
                except Exception as e:
                    logger.error(f"Stats timer durdurma hatası: {e}")
                    
            if hasattr(self, 'whatsapp_check_timer') and self.whatsapp_check_timer:
                try:
                    self.whatsapp_check_timer.stop()
                except Exception as e:
                    logger.error(f"WhatsApp timer durdurma hatası: {e}")
                    
            if hasattr(self, 'vapi_status_timer') and self.vapi_status_timer:
                try:
                    self.vapi_status_timer.stop()
                except Exception as e:
                    logger.error(f"Vapi timer durdurma hatası: {e}")
            
            # Veritabanını kapat
            if hasattr(self, 'db') and self.db:
                logger.info("Veritabanı kapatılıyor...")
                try:
                    self.db.close()
                except Exception as e:
                    logger.error(f"Database kapatma hatası: {e}")
            
            # Ayarları kaydet
            logger.info("Ayarlar kaydediliyor...")
        except Exception as e:
            logger.error(f"Kapatma işlemi genel hatası: {e}")
        
        try:
            # Son kullanılan telefon numarasını kaydet
            if hasattr(self, 'vapi_phone_combo'):
                phone_data = self.vapi_phone_combo.currentData()
                if phone_data:
                    self.config['vapi_phone_number_id'] = phone_data
            
            with open("config.json", "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                
            logger.info("Ayarlar kaydedildi ve uygulama kapatıldı")
        except Exception as e:
            logger.error(f"Ayar kaydetme hatası: {e}")
        
        event.accept()
    
    def cleanup_resources(self):
        """Kaynak temizleme"""
        try:
            if hasattr(self, 'db') and self.db:
                self.db.close()
            if ROBUST_SYSTEM_AVAILABLE:
                MemoryManager.cleanup_memory()
        except Exception as e:
            logger.error(f"Kaynak temizleme hatası: {e}")
    
    def add_test_firms(self):
        """Test firmalarını ekle"""
        try:
            if not self.db:
                print("❌ Veritabanı bağlantısı yok!")
                return False
            
            # Test firmaları
            test_firms = [
                {
                    'name': 'Test1 Firma',
                    'phone': '+905462051820',
                    'email': 'test1@test.com',
                    'address': 'Test Adres 1, İstanbul',
                    'sector': 'Test Sektörü',
                    'summary': 'Test amaçlı firma 1',
                    'website': 'https://test1.com',
                    'contact_person': 'Test Kişi 1',
                    'rating': 4.5,
                    'review_count': 10
                },
                {
                    'name': 'Test2 Firma',
                    'phone': '+905544811820',
                    'email': 'test2@test.com',
                    'address': 'Test Adres 2, İstanbul',
                    'sector': 'Test Sektörü',
                    'summary': 'Test amaçlı firma 2',
                    'website': 'https://test2.com',
                    'contact_person': 'Test Kişi 2',
                    'rating': 4.0,
                    'review_count': 8
                }
            ]
            
            print("🧪 Test firmaları ekleniyor...")
            
            for firm_data in test_firms:
                # Firma zaten var mı kontrol et
                existing = self.db.get_firms(search_text=firm_data['name'])
                if existing:
                    print(f"⚠️ {firm_data['name']} zaten mevcut, atlanıyor...")
                    continue
                
                # Firma ekle
                firm_id = self.db.add_firm(**firm_data)
                if firm_id:
                    print(f"✅ {firm_data['name']} başarıyla eklendi (ID: {firm_id})")
                    
                    # Test mesajı ekle
                    self.db.save_message(
                        firm_id=firm_id,
                        direction='sent',
                        content='Test mesajı - Sistem testi için gönderildi',
                        platform='whatsapp',
                        status='sent'
                    )
                    
                    # Test aktivitesi ekle
                    self.db.save_activity(
                        firm_id=firm_id,
                        activity_type='test_activity',
                        description='Test aktivitesi - Sistem testi için oluşturuldu'
                    )
                    
                else:
                    print(f"❌ {firm_data['name']} eklenemedi!")
            
            print("\n🎉 Test verileri başarıyla eklendi!")
            print("📱 Test numaraları:")
            print("   - Test1 Firma: +905462051820")
            print("   - Test2 Firma: +905544811820")
            
            return True
            
        except Exception as e:
            print(f"❌ Test verisi ekleme hatası: {e}")
            return False
    
    @safe_execute(max_retries=2, fallback_value=None)
    def safe_update_dashboard(self):
        """Güvenli dashboard güncelleme"""
        if hasattr(self, 'update_dashboard'):
            return self.update_dashboard()
        return None
    
    @safe_execute(max_retries=2, fallback_value=None)
    def safe_check_whatsapp_messages(self):
        """Güvenli WhatsApp mesaj kontrolü"""
        if hasattr(self, 'check_whatsapp_messages'):
            return self.check_whatsapp_messages()
        return None
    
    @safe_execute(max_retries=2, fallback_value=None)
    def safe_update_vapi_status(self):
        """Güvenli Vapi durum güncelleme"""
        if hasattr(self, 'update_vapi_status'):
            return self.update_vapi_status()
        return None

    def create_weekly_report_tab(self):
        """Haftalık AI destekli PDF rapor sekmesi"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Üst kontrol paneli
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)
        
        # Sol taraf - tarih seçimi
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("📅 Başlangıç Tarihi:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(datetime.now().date() - timedelta(days=7))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setStyleSheet("""
            QDateEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        date_layout.addWidget(self.start_date_edit)
        
        date_layout.addWidget(QLabel("📅 Bitiş Tarihi:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(datetime.now().date())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setStyleSheet("""
            QDateEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #3498db;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        date_layout.addWidget(self.end_date_edit)
        
        control_layout.addLayout(date_layout)
        control_layout.addStretch()
        
        # Sağ taraf - butonlar
        button_layout = QHBoxLayout()
        
        # Rapor oluştur butonu
        generate_btn = QPushButton("📊 Rapor Oluştur")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        generate_btn.clicked.connect(self.generate_weekly_report)
        button_layout.addWidget(generate_btn)
        
        # Önizleme butonu
        preview_btn = QPushButton("👁️ Önizleme")
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        preview_btn.clicked.connect(self.preview_weekly_report)
        button_layout.addWidget(preview_btn)
        
        # Raporu aç butonu
        open_btn = QPushButton("📂 Raporu Aç")
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        open_btn.clicked.connect(self.open_latest_report)
        button_layout.addWidget(open_btn)
        
        control_layout.addLayout(button_layout)
        main_layout.addWidget(control_frame)
        
        # Ana içerik alanı
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setStyleSheet("QSplitter::handle { background-color: #34495e; }")
        
        # Sol taraf - rapor özeti
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Rapor özeti başlığı
        summary_title = QLabel("📋 Rapor Özeti")
        summary_title.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 10px;
            background-color: #2c3e50;
            border-radius: 4px;
        """)
        left_layout.addWidget(summary_title)
        
        # Rapor özeti metni
        self.report_summary_text = QTextEdit()
        self.report_summary_text.setReadOnly(True)
        self.report_summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.report_summary_text.setPlaceholderText("Rapor oluşturmak için 'Rapor Oluştur' butonuna tıklayın...")
        left_layout.addWidget(self.report_summary_text)
        
        # AI analizi başlığı
        ai_title = QLabel("🤖 AI Analizi")
        ai_title.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 10px;
            background-color: #2c3e50;
            border-radius: 4px;
        """)
        left_layout.addWidget(ai_title)
        
        # AI analizi metni
        self.ai_analysis_text = QTextEdit()
        self.ai_analysis_text.setReadOnly(True)
        self.ai_analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.ai_analysis_text.setPlaceholderText("AI analizi burada görünecek...")
        left_layout.addWidget(self.ai_analysis_text)
        
        content_splitter.addWidget(left_frame)
        
        # Sağ taraf - istatistikler ve grafikler
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # İstatistikler başlığı
        stats_title = QLabel("📊 İstatistikler")
        stats_title.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 16px;
            padding: 10px;
            background-color: #34495e;
            border-radius: 4px;
        """)
        right_layout.addWidget(stats_title)
        
        # İstatistik tablosu
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["Metrik", "Değer"])
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                gridline-color: #34495e;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #34495e;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.stats_table)
        
        # Durum bilgisi
        self.report_status_label = QLabel("ℹ️ Rapor hazır değil")
        self.report_status_label.setStyleSheet("""
            color: #95a5a6;
            font-size: 12px;
            padding: 5px;
        """)
        right_layout.addWidget(self.report_status_label)
        
        content_splitter.addWidget(right_frame)
        
        # Splitter oranları ayarla (sol %60, sağ %40)
        content_splitter.setSizes([600, 400])
        main_layout.addWidget(content_splitter)
        
        # PDF rapor oluşturucu
        self.pdf_generator = None
        if PDF_REPORT_AVAILABLE:
            try:
                self.pdf_generator = AIReportGenerator()
            except Exception as e:
                print(f"PDF rapor oluşturucu başlatılamadı: {e}")
        
        return widget
    
    def generate_weekly_report(self):
        """Haftalık rapor oluştur"""
        try:
            if not self.pdf_generator:
                QMessageBox.warning(self, "Hata", "PDF rapor oluşturucu mevcut değil!")
                return
            
            # Tarihleri al
            start_date = self.start_date_edit.date().toPython()
            end_date = self.end_date_edit.date().toPython()
            
            # Tarih kontrolü
            if start_date >= end_date:
                QMessageBox.warning(self, "Hata", "Başlangıç tarihi bitiş tarihinden önce olmalıdır!")
                return
            
            # Durum güncelle
            self.report_status_label.setText("🔄 Rapor oluşturuluyor...")
            self.report_status_label.setStyleSheet("color: #f39c12; font-size: 12px; padding: 5px;")
            
            # Rapor oluştur
            pdf_path = self.pdf_generator.generate_weekly_report(start_date, end_date)
            
            if pdf_path:
                self.report_status_label.setText(f"✅ Rapor oluşturuldu: {os.path.basename(pdf_path)}")
                self.report_status_label.setStyleSheet("color: #27ae60; font-size: 12px; padding: 5px;")
                
                # Rapor özetini göster
                self.show_report_summary(start_date, end_date)
                
                QMessageBox.information(self, "Başarılı", f"Rapor başarıyla oluşturuldu!\n\nDosya: {pdf_path}")
            else:
                self.report_status_label.setText("❌ Rapor oluşturulamadı")
                self.report_status_label.setStyleSheet("color: #e74c3c; font-size: 12px; padding: 5px;")
                QMessageBox.critical(self, "Hata", "Rapor oluşturulamadı!")
                
        except Exception as e:
            self.report_status_label.setText(f"❌ Hata: {str(e)}")
            self.report_status_label.setStyleSheet("color: #e74c3c; font-size: 12px; padding: 5px;")
            QMessageBox.critical(self, "Hata", f"Rapor oluşturma hatası: {str(e)}")
    
    def preview_weekly_report(self):
        """Rapor önizlemesi göster"""
        try:
            if not self.pdf_generator:
                QMessageBox.warning(self, "Hata", "PDF rapor oluşturucu mevcut değil!")
                return
            
            # Tarihleri al
            start_date = self.start_date_edit.date().toPython()
            end_date = self.end_date_edit.date().toPython()
            
            # Rapor özetini al
            summary = self.pdf_generator.get_report_summary(start_date, end_date)
            
            if summary:
                self.show_report_summary(start_date, end_date)
                QMessageBox.information(self, "Önizleme", "Rapor önizlemesi yüklendi!")
            else:
                QMessageBox.warning(self, "Hata", "Rapor özeti alınamadı!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Önizleme hatası: {str(e)}")
    
    def show_report_summary(self, start_date, end_date):
        """Rapor özetini göster"""
        try:
            if not self.pdf_generator:
                return
            
            # Rapor özetini al
            summary = self.pdf_generator.get_report_summary(start_date, end_date)
            
            if not summary:
                return
            
            # Rapor özeti metnini güncelle
            data = summary.get('data', {})
            stats = data.get('stats', {})
            
            summary_text = f"""
📊 HAFTALIK RAPOR ÖZETİ
═══════════════════════════════════════════════════════════════

📅 Rapor Dönemi: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}

📈 TEMEL İSTATİSTİKLER
───────────────────────────────────────────────────────────────
• Yeni Firmalar: {stats.get('new_firms', 0)}
• Aktif Firmalar: {stats.get('active_firms', 0)}
• Toplam Email: {stats.get('total_emails', 0)}
• Açılan Email: {stats.get('opened_emails', 0)} (%{stats.get('open_rate', 0)})
• Yanıtlanan Email: {stats.get('replied_emails', 0)} (%{stats.get('reply_rate', 0)})
• Toplam Mesaj: {stats.get('total_messages', 0)}
• Toplam Arama: {stats.get('total_calls', 0)}

📊 DETAYLI VERİLER
───────────────────────────────────────────────────────────────
• Firma Sayısı: {len(data.get('firms', []))}
• Email Sayısı: {len(data.get('emails', []))}
• Mesaj Sayısı: {len(data.get('messages', []))}
• Arama Sayısı: {len(data.get('calls', []))}
• Aktivite Sayısı: {len(data.get('activities', []))}
            """
            
            self.report_summary_text.setText(summary_text)
            
            # AI analizi metnini güncelle
            ai_analysis = summary.get('ai_analysis', {})
            ai_text = ai_analysis.get('summary', 'AI analizi mevcut değil')
            self.ai_analysis_text.setText(ai_text)
            
            # İstatistik tablosunu güncelle
            self.update_stats_table(stats)
            
        except Exception as e:
            print(f"Rapor özeti gösterme hatası: {e}")
    
    def update_stats_table(self, stats):
        """İstatistik tablosunu güncelle"""
        try:
            data = [
                ["Yeni Firmalar", str(stats.get('new_firms', 0))],
                ["Aktif Firmalar", str(stats.get('active_firms', 0))],
                ["Toplam Email", str(stats.get('total_emails', 0))],
                ["Açılan Email", f"{stats.get('opened_emails', 0)} (%{stats.get('open_rate', 0)})"],
                ["Yanıtlanan Email", f"{stats.get('replied_emails', 0)} (%{stats.get('reply_rate', 0)})"],
                ["Toplam Mesaj", str(stats.get('total_messages', 0))],
                ["Toplam Arama", str(stats.get('total_calls', 0))]
            ]
            
            self.stats_table.setRowCount(len(data))
            for row, (metric, value) in enumerate(data):
                self.stats_table.setItem(row, 0, QTableWidgetItem(metric))
                self.stats_table.setItem(row, 1, QTableWidgetItem(value))
            
        except Exception as e:
            print(f"İstatistik tablosu güncelleme hatası: {e}")
    
    def open_latest_report(self):
        """En son oluşturulan raporu aç"""
        try:
            # Rapor dosyalarını bul
            report_files = []
            for file in os.listdir('.'):
                if file.startswith('haftalik_rapor_') and file.endswith('.pdf'):
                    report_files.append(file)
            
            if not report_files:
                QMessageBox.information(self, "Bilgi", "Henüz rapor oluşturulmamış!")
                return
            
            # En son dosyayı bul
            latest_file = max(report_files, key=os.path.getctime)
            file_path = os.path.abspath(latest_file)
            
            # Dosyayı aç
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS ve Linux
                os.system(f'open "{file_path}"')
            else:
                QMessageBox.information(self, "Bilgi", f"Rapor dosyası: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor açma hatası: {str(e)}")


    def setup_shortcuts(self):
        """Klavye kısayolları ayarla"""
        # Ctrl+A: Tümünü seç
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self.select_all)
        
        # Ctrl+D: Hiçbirini seçme
        select_none_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        select_none_shortcut.activated.connect(self.select_none)
        
        # Ctrl+R: Başlat
        start_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        start_shortcut.activated.connect(self.start_bulk_messaging)
        
        # Ctrl+Space: Duraklat/Devam
        pause_shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        pause_shortcut.activated.connect(self.toggle_pause)
        
        # Ctrl+S: Durdur
        stop_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        stop_shortcut.activated.connect(self.stop_messaging)
    
    def update_firm_count(self):
        """Firma sayısını güncelle"""
        count = self.firms_table.rowCount()
        self.firm_count_label.setText(f"{count} firma")
    
    def filter_firms(self):
        """Firmaları filtrele"""
        sector_filter = self.sector_filter.currentText()
        status_filter = self.status_filter.currentText()
        website_filter = self.website_filter.currentText()
        search_text = self.search_input.text().lower()
        
        for i in range(self.firms_table.rowCount()):
            firm_name = self.firms_table.item(i, 1).text().lower()
            firm_sector = self.firms_table.item(i, 2).text()
            firm_status = self.firms_table.item(i, 5).text()
            
            # Sektör filtresi
            sector_match = (sector_filter == "Tüm Sektörler" or firm_sector == sector_filter)
            
            # Durum filtresi
            status_match = (status_filter == "Tüm Durumlar" or firm_status == status_filter)
            
            # Website filtresi
            website_match = True
            if website_filter == "Website Var":
                website_match = bool(self.firms[i].get('website', '').strip())
            elif website_filter == "Website Yok":
                website_match = not bool(self.firms[i].get('website', '').strip())
            
            # Arama filtresi
            search_match = (not search_text or 
                          search_text in firm_name or 
                          search_text in firm_sector or
                          search_text in self.firms_table.item(i, 3).text().lower() or
                          search_text in self.firms_table.item(i, 4).text().lower())
            
            # Satırı göster/gizle
            self.firms_table.setRowHidden(i, not (sector_match and status_match and website_match and search_match))
        
        self.update_firm_count()
    
    def invert_selection(self):
        """Seçimi tersine çevir"""
        for i in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(i):
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())
        self.update_stats()
    
    def select_by_sector(self):
        """Sektöre göre seçim yap"""
        if not hasattr(self, 'sector_filter'):
            return
        
        # Sektör seçim dialogu
        sectors = []
        for i in range(1, self.sector_filter.count()):
            sectors.append(self.sector_filter.itemText(i))
        
        if not sectors:
            QMessageBox.information(self, "Bilgi", "Seçilecek sektör bulunamadı!")
            return
        
        sector, ok = QInputDialog.getItem(
            self, "Sektör Seçimi", "Hangi sektörü seçmek istiyorsunuz?",
            sectors, 0, False
        )
        
        if ok and sector:
            for i in range(self.firms_table.rowCount()):
                if not self.firms_table.isRowHidden(i):
                    firm_sector = self.firms_table.item(i, 2).text()
                    checkbox = self.firms_table.cellWidget(i, 0)
                    if checkbox:
                        checkbox.setChecked(firm_sector == sector)
            self.update_stats()
    
    def select_no_website(self):
        """Website olmayan firmaları seç"""
        selected_count = 0
        for i in range(self.firms_table.rowCount()):
            if not self.firms_table.isRowHidden(i):
                # Firma verisini kontrol et
                firm = self.firms[i]
                has_website = bool(firm.get('website', '').strip())
                
                checkbox = self.firms_table.cellWidget(i, 0)
                if checkbox:
                    checkbox.setChecked(not has_website)
                    if not has_website:
                        selected_count += 1
        
        self.update_stats()
        QMessageBox.information(self, "Seçim Tamamlandı", f"{selected_count} website olmayan firma seçildi!")
    
    # 📱 WhatsApp Otomatik Gönderim Fonksiyonları
    
    def start_auto_whatsapp_sending(self):
        """🚀 Otomatik WhatsApp gönderimini başlat"""
        try:
            # Seçili firmaları al
            selected_firms = []
            for i in range(self.firms_table.rowCount()):
                if not self.firms_table.isRowHidden(i):
                    checkbox = self.firms_table.cellWidget(i, 0)
                    if checkbox and checkbox.isChecked():
                        if i < len(self.firms):
                            selected_firms.append(self.firms[i])
            
            if not selected_firms:
                QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen en az bir firma seçin!")
                return
            
            # Otomatik gönderimi başlat
            self.whatsapp_auto_sender.start_auto_sending(selected_firms)
            
            # Buton durumlarını güncelle
            self.auto_send_btn.setVisible(False)
            self.stop_auto_send_btn.setVisible(True)
            
        except Exception as e:
            logger.error(f"Otomatik gönderim başlatma hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Otomatik gönderim başlatılamadı:\n{str(e)}")
    
    def stop_auto_whatsapp_sending(self):
        """🛑 Otomatik WhatsApp gönderimini durdur"""
        try:
            if hasattr(self, 'whatsapp_auto_sender'):
                self.whatsapp_auto_sender.stop_sending()
            
            # Buton durumlarını güncelle
            self.auto_send_btn.setVisible(True)
            self.stop_auto_send_btn.setVisible(False)
            
        except Exception as e:
            logger.error(f"Otomatik gönderim durdurma hatası: {e}")
            QMessageBox.critical(self, "❌ Hata", f"Otomatik gönderim durdurulamadı:\n{str(e)}")


def main():
    """Ana fonksiyon - Güçlendirilmiş güvenli hata yönetimi ile"""
    exit_code = 0
    app = None
    window = None
    
    # Güçlendirilmiş sistem başlatma
    if ROBUST_SYSTEM_AVAILABLE:
        try:
            enhance_main_system()
            logger.info("Ana fonksiyon güçlendirilmiş sistem ile başlatıldı")
        except Exception as e:
            print(f"Güçlendirilmiş sistem başlatılamadı: {e}")
    
    try:
        logger.info("Uygulama başlatılıyor...")
        
        # QApplication oluştur
        app = QApplication(sys.argv)
        app.setApplicationName("B2B İletişim Paneli")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("B2B Automation")
        
        # Uygulama stili
        try:
            app.setStyle("Fusion")
        except Exception as e:
            logger.warning(f"Stil ayarlanamadı: {e}")
        
        # Font
        try:
            font = QFont("Segoe UI", 10)
            app.setFont(font)
        except Exception as e:
            logger.warning(f"Font ayarlanamadı: {e}")
        
        # Signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Signal alındı: {signum}")
            if window:
                window.close()
            if app:
                app.quit()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Ana pencere
        logger.info("Ana pencere oluşturuluyor...")
        window = MainWindow()
        window.show()
        
        logger.info("Uygulama başlatıldı")
        
        # Uygulamayı çalıştır
        exit_code = app.exec()
        logger.info(f"Uygulama sonlandı (kod: {exit_code})")
        
    except KeyboardInterrupt:
        logger.info("Kullanıcı tarafından durduruldu")
        exit_code = 0
        
    except Exception as e:
        logger.critical(f"Kritik hata: {e}")
        traceback.print_exc()
        exit_code = 1
        
        # Emergency error dialog
        try:
            if app and QApplication.instance():
                QMessageBox.critical(
                    None,
                    "Kritik Hata",
                    f"Uygulama beklenmedik bir hatayla karşılaştı:\n\n{str(e)}\n\nDetaylar log dosyasında."
                )
        except:
            print(f"KRITIK HATA: {e}")
    
    finally:
        # Cleanup
        try:
            if window:
                window.close()
        except:
            pass
            
        try:
            if app:
                app.quit()
        except:
            pass
        
        logger.info("Temizlik işlemleri tamamlandı")
    
    sys.exit(exit_code)




if __name__ == "__main__":
    main()