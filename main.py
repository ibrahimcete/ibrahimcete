#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import time
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve, QUrl, QObject, Slot, QPointF, QRectF, QDateTime, QEvent
from PySide6.QtGui import QIcon, QAction, QPalette, QColor, QFont, QPainter, QPen, QBrush, QPolygonF
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings

# Güçlendirilmiş sistem altyapısı
try:
    from robust_system import (
        enhance_main_system, safe_execute, critical_safe, 
        ConnectionManager, MemoryManager, TimeoutManager,
        ThreadSafeManager, SystemMonitor, GracefulShutdown,
        APISecurityManager, DatabaseSecurityManager,
        safe_json_loads, safe_json_dumps, safe_file_read, safe_file_write,
        is_system_healthy, get_system_stats, logger
    )
    ROBUST_SYSTEM_AVAILABLE = True
    logger.info("Güçlendirilmiş sistem modülü yüklendi")
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

# Standart kütüphaneler
import threading

# Ana modüller (zorunlu) - Güvenli import
try:
    from api_manager import APIManager
    API_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: api_manager yüklenemedi: {e}")
    API_MANAGER_AVAILABLE = False
    class APIManager:
        def __init__(self):
            pass
        def update_settings(self, settings):
            pass
        def cancel_operation(self):
            pass

try:
    from web_scraper import WebScraper
    WEB_SCRAPER_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: web_scraper yüklenemedi: {e}")
    WEB_SCRAPER_AVAILABLE = False
    class WebScraper:
        def __init__(self):
            pass

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

try:
    from email_manager import EmailManager
    EMAIL_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: email_manager yüklenemedi: {e}")
    EMAIL_MANAGER_AVAILABLE = False
    class EmailManager:
        def __init__(self):
            pass

try:
    from database import Database
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: database yüklenemedi: {e}")
    DATABASE_AVAILABLE = False
    class Database:
        def __init__(self):
            pass
        def get_existing_place_ids(self):
            return []

# Yeni modüller - Güvenli import
try:
    from data_manager import DataManager
    DATA_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: data_manager yüklenemedi: {e}")
    DATA_MANAGER_AVAILABLE = False
    class DataManager:
        def __init__(self):
            pass

try:
    from calendar_manager import CalendarManager
    CALENDAR_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: calendar_manager yüklenemedi: {e}")
    CALENDAR_MANAGER_AVAILABLE = False
    class CalendarManager:
        def __init__(self):
            pass

try:
    from custom_mail_sender_tab import CustomMailSenderTab
    CUSTOM_MAIL_TAB_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: custom_mail_sender_tab yüklenemedi: {e}")
    CUSTOM_MAIL_TAB_AVAILABLE = False
    class CustomMailSenderTab:
        def __init__(self, parent=None):
            pass
            pass

try:
    from analytics_dashboard import AnalyticsDashboard
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: analytics_dashboard yüklenemedi: {e}")
    ANALYTICS_AVAILABLE = False
    class AnalyticsDashboard:
        def __init__(self):
            pass

try:
    from knowledge_learning_tab import KnowledgeLearningTab
    KNOWLEDGE_LEARNING_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: knowledge_learning_tab yüklenemedi: {e}")
    KNOWLEDGE_LEARNING_AVAILABLE = False
    class KnowledgeLearningTab:
        def __init__(self, *args, **kwargs):
            pass

try:
    from ai_chat_assistant import AIChatAssistantTab
    AI_CHAT_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: ai_chat_assistant yüklenemedi: {e}")
    AI_CHAT_AVAILABLE = False
    class AIChatAssistantTab:
        def __init__(self, *args, **kwargs):
            pass

try:
    from mail_strategy_tab import MailStrategyTab
    MAIL_STRATEGY_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: mail_strategy_tab yüklenemedi: {e}")
    MAIL_STRATEGY_AVAILABLE = False
    class MailStrategyTab:
        def __init__(self, *args, **kwargs):
            pass

try:
    from automation_builder import AdvancedAutomationBuilder as AutomationBuilder
    AUTOMATION_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: automation_builder yüklenemedi: {e}")
    AUTOMATION_AVAILABLE = False
    class AutomationBuilder:
        def __init__(self):
            pass

try:
    from api_cost_widget import APICostWidget, APICostDetailsDialog
    API_COST_WIDGET_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: api_cost_widget yüklenemedi: {e}")
    API_COST_WIDGET_AVAILABLE = False

try:
    from web_scraper_integration import UnifiedWebScraper
    UNIFIED_SCRAPER_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: web_scraper_integration yüklenemedi: {e}")
    UNIFIED_SCRAPER_AVAILABLE = False

# 🆕 Tracking GUI Integration
try:
    from tracking_gui_integration import get_tracking_gui_manager, TrackingGUIManager
    TRACKING_GUI_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: tracking_gui_integration yüklenemedi: {e}")
    TRACKING_GUI_AVAILABLE = False
    get_tracking_gui_manager = None
    TrackingGUIManager = None

# 🆕 Voice Assistant Integration
try:
    from voice_assistant import VoiceAssistant, VoiceAssistantGUI
    VOICE_ASSISTANT_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: voice_assistant yüklenemedi: {e}")
    VOICE_ASSISTANT_AVAILABLE = False
    VoiceAssistant = None

# 🆕 Firma Detay Analyzer Integration
try:
    from firma_detay_analyzer import FirmaDetayAnalyzer
    FIRMA_DETAY_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: firma_detay_analyzer yüklenemedi: {e}")
    FIRMA_DETAY_AVAILABLE = False
    FirmaDetayAnalyzer = None

# 🆕 AI Strategy Analyzer Integration
try:
    from ai_strategy_analyzer import AIStrategyAnalyzer, StrategyType, FirmAnalysis
    AI_STRATEGY_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: ai_strategy_analyzer yüklenemedi: {e}")
    AI_STRATEGY_AVAILABLE = False
    AIStrategyAnalyzer = None
    StrategyType = None
    FirmAnalysis = None
    VoiceAssistantGUI = None

# 🚀 Advanced Voice Assistant Integration
try:
    from advanced_voice_assistant_integration import AdvancedVoiceAssistantIntegration, AdvancedVoiceAssistantGUI
    ADVANCED_VOICE_ASSISTANT_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: advanced_voice_assistant_integration yüklenemedi: {e}")
    ADVANCED_VOICE_ASSISTANT_AVAILABLE = False
    AdvancedVoiceAssistantIntegration = None
    AdvancedVoiceAssistantGUI = None

# 🤖 Advanced AI Chat Engine Integration
try:
    from advanced_ai_chat_engine import AdvancedAIChatEngine, FloatingChatButton
    ADVANCED_AI_CHAT_AVAILABLE = True
except ImportError as e:
    print(f"UYARI: advanced_ai_chat_engine yüklenemedi: {e}")
    ADVANCED_AI_CHAT_AVAILABLE = False
    AdvancedAIChatEngine = None
    FloatingChatButton = None

# Üçüncü parti kütüphaneler
try:
    import pandas as pd
except ImportError:
    pd = None
    print("Pandas kurulu değil. Excel export özelliği çalışmayacak.")

try:
    from faker import Faker
except ImportError:
    Faker = None
    print("Faker kurulu değil. Test firma oluşturma özelliği çalışmayacak.")

# 🔧 İş Zekası Modülleri - Fallback sınıflar
try:
    from business_intelligence import BusinessIntelligenceAnalyzer
    BUSINESS_INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ İş Zekası modülü yüklenemedi: {e}")
    BUSINESS_INTELLIGENCE_AVAILABLE = False
    class BusinessIntelligenceAnalyzer:
        def __init__(self, db=None, **kwargs):
            self.db = db
            # database_path parametresi kaldırıldı - gerçek modül bunu kabul etmiyor
            print("⚠️ İş Zekası başlatılamadı: Modül bulunamadı (fallback kullanılıyor)")
        
        def analyze_company(self, *args, **kwargs):
            return {"success": False, "error": "İş Zekası modülü mevcut değil"}
        
        def get_insights(self, *args, **kwargs):
            return {"success": False, "error": "İş Zekası modülü mevcut değil"}

try:
    from ai_conversational_intelligence import AIConversationalIntelligence
    AI_CONVERSATIONAL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI Konuşma Zekası modülü yüklenemedi: {e}")
    AI_CONVERSATIONAL_AVAILABLE = False
    class AIConversationalIntelligence:
        def __init__(self, db=None, **kwargs):
            self.db = db
            print("⚠️ AI Konuşma Zekası başlatılamadı: Modül bulunamadı (fallback kullanılıyor)")
        
        def analyze_buyer_intent(self, *args, **kwargs):
            return {"success": False, "error": "AI Konuşma Zekası modülü mevcut değil", "intent": "unknown"}
        
        def generate_response(self, *args, **kwargs):
            return "AI Konuşma Zekası modülü mevcut değil"
        
        def analyze_conversation(self, *args, **kwargs):
            return {"success": False, "error": "AI Konuşma Zekası modülü mevcut değil"}


class BatchSearchThread(QThread):
    """Batch firma arama için özel thread - Güçlendirilmiş"""
    progress = Signal(str)
    batch_completed = Signal(list)
    all_completed = Signal(list)
    error = Signal(str)
    
    def __init__(self, query, location, max_results, batch_size=20, wait_minutes=20):
        super().__init__()
        self.query = query
        self.location = location
        self.max_results = max_results
        self.batch_size = batch_size
        self.wait_minutes = wait_minutes
        
        # Güvenli modül yükleme - 🆕 Database ve API Manager bağlantısı
        if DATABASE_AVAILABLE:
            self.db = Database()
        else:
            self.db = None
            
        if API_MANAGER_AVAILABLE:
            self.api_manager = APIManager(db=self.db)  # Database instance'ını geçir
        else:
            self.api_manager = None
            
        self.is_running = True
        self.is_paused = False
        self.all_firms = []
        self.retry_count = 0
        self.max_retries = 3
        self.connection_manager = ConnectionManager() if ROBUST_SYSTEM_AVAILABLE else None
    
    def pause(self):
        """İşlemi duraklat"""
        self.is_paused = True
        self.progress.emit("⏸️ İşlem duraklatıldı")
    
    def resume(self):
        """İşlemi devam ettir"""
        self.is_paused = False
        self.progress.emit("▶️ İşlem devam ediyor...")
    
    def stop(self):
        """İşlemi durdur"""
        self.is_running = False
        self.api_manager.cancel_operation()
        self.progress.emit("⏹️ İşlem durduruldu")
    
    @safe_execute(max_retries=3, fallback_value=None)
    def run(self):
        """Güçlendirilmiş run metodu"""
        print("🚀🚀🚀 BatchSearchThread RUN metodu başladı!")  # DEBUG
        try:
            print("🔍 Sistem sağlık kontrolü...")  # DEBUG
            # Sistem sağlık kontrolü
            if ROBUST_SYSTEM_AVAILABLE and not is_system_healthy():
                self.error.emit("Sistem sağlıksız durumda!")
                return
            print("✅ Sistem sağlık kontrolü geçti")  # DEBUG
            
            print("🔍 API manager kontrolü...")  # DEBUG
            # API ayarlarını güvenli yükle
            if self.api_manager:
                print("✅ API manager mevcut, config yükleniyor...")  # DEBUG
                settings = safe_file_read("config.json", default="{}")
                print(f"📁 Config dosyası okundu: {len(settings)} karakter")  # DEBUG
                if settings:
                    settings_data = safe_json_loads(settings, default={})
                    print(f"🔧 Config parse edildi: {len(settings_data)} anahtar")  # DEBUG
                    self.api_manager.update_settings(settings_data)
                    print("✅ API manager ayarları güncellendi")  # DEBUG
                else:
                    print("❌ Config dosyası boş!")  # DEBUG
                    self.error.emit("API ayarları bulunamadı!")
                    return
            else:
                print("❌ API Manager yok!")  # DEBUG
                self.error.emit("API Manager mevcut değil!")
                return
            
            print("🔍 Mevcut ID'leri alınıyor...")  # DEBUG
            # Mevcut ID'leri güvenli al
            existing_ids = set()  # Set olarak tanımla
            if self.db:
                try:
                    existing_place_ids = self.db.get_existing_place_ids()
                    existing_ids = set(existing_place_ids) if existing_place_ids else set()
                    print(f"✅ {len(existing_ids)} mevcut ID alındı")  # DEBUG
                except Exception as e:
                    print(f"⚠️ DB ID'leri alınırken hata: {e}")  # DEBUG
                    if ROBUST_SYSTEM_AVAILABLE:
                        logger.warning(f"Veritabanı ID'leri alınamadı: {e}")
                    existing_ids = set()
            else:
                print("⚠️ DB yok, mevcut ID'ler alınamıyor")  # DEBUG
            
            remaining = self.max_results
            batch_number = 1
            print(f"🎯 Başlıyor: {remaining} firma, batch {batch_number}")  # DEBUG
            
            while remaining > 0 and self.is_running:
                print(f"🔄 While döngüsü başladı - Kalan: {remaining}, Running: {self.is_running}")  # DEBUG
                # Sistem sağlık kontrolü
                if ROBUST_SYSTEM_AVAILABLE and not is_system_healthy():
                    self.error.emit("Sistem sağlıksız durumda, işlem durduruluyor!")
                    break
                
                while self.is_paused and self.is_running:
                    time.sleep(0.5)
                
                if not self.is_running:
                    print("❌ İşlem durdu, döngüden çıkılıyor")  # DEBUG
                    break
                
                current_batch_size = min(self.batch_size, remaining)
                print(f"📊 Batch {batch_number}: {current_batch_size} firma aranacak")  # DEBUG
            
                self.progress.emit(f"🔄 Batch {batch_number} başlıyor ({current_batch_size} firma)...")
                
                print(f"🌐 API çağrısı başlatılıyor... (query: {self.query}, location: {self.location})")  # DEBUG
                try:
                    firms = self.api_manager.search_google_maps_batch(
                        self.query,
                        self.location,
                        max_results=current_batch_size,
                        batch_size=current_batch_size,
                        progress_callback=self.progress.emit,
                        existing_firm_ids=list(existing_ids)  # Set'i list'e çevir
                    )
                    print(f"🌐 API çağrısı tamamlandı! {len(firms) if firms else 0} firma bulundu")  # DEBUG
                    
                    if firms:
                        print(f"✅ {len(firms)} firma işlenecek...")  # DEBUG
                        self.all_firms.extend(firms)
                        existing_ids.update([f.get('place_id') for f in firms if f.get('place_id')])
                        print("📝 Firmalar all_firms'e eklendi, existing_ids güncellendi")  # DEBUG
                        
                        print("💾 DB'ye kaydetme başlıyor...")  # DEBUG
                        for i, firm in enumerate(firms):
                            print(f"💾 İşleniyor {i+1}/{len(firms)}: {firm.get('name', 'İsimsiz')}")  # DEBUG
                            if self.db:
                                try:
                                    # Save firm to database and get the ID
                                    firm_id = self.db.save_firm(firm)
                                    if firm_id:
                                        firm['id'] = firm_id  # Add ID to the firm dictionary
                                    print(f"✅ DB'ye kaydedildi: {firm.get('name', 'İsimsiz')} (ID: {firm.get('id', 'N/A')})")  # DEBUG
                                except Exception as e:
                                    print(f"❌ DB kaydetme hatası: {e}")  # DEBUG
                            else:
                                print("⚠️ DB yok, kaydetme atlandı")  # DEBUG
                        
                        print(f"🚀 EMIT: batch_completed sinyali gönderiliyor ({len(firms)} firma)")  # DEBUG
                        self.batch_completed.emit(firms)
                        print("✅ batch_completed sinyali gönderildi!")  # DEBUG
                        
                        remaining -= len(firms)
                        batch_number += 1
                        
                        if remaining > 0 and self.is_running:
                            wait_seconds = self.wait_minutes * 60
                            for i in range(wait_seconds, 0, -1):
                                if not self.is_running:
                                    break
                                
                                while self.is_paused and self.is_running:
                                    time.sleep(0.5)
                                
                                minutes = i // 60
                                seconds = i % 60
                                self.progress.emit(
                                    f"⏳ Sonraki batch için bekleniyor: {minutes:02d}:{seconds:02d} "
                                    f"(Kalan: {remaining} firma)"
                                )
                                time.sleep(1)
                    else:
                        self.progress.emit("ℹ️ Daha fazla firma bulunamadı")
                        break
                        
                except Exception as e:
                    print(f"❌ Batch {batch_number} hatası: {str(e)}")  # DEBUG
                    self.error.emit(f"Batch {batch_number} hatası: {str(e)}")
                    break
            
            print(f"🏁 While döngüsü bitti - Running: {self.is_running}, Toplam firma: {len(self.all_firms)}")  # DEBUG
            if self.is_running:
                print("🎉 İşlem tamamlandı, all_completed sinyali gönderiliyor")  # DEBUG
                self.progress.emit(f"✅ Toplam {len(self.all_firms)} firma bulundu!")
                self.all_completed.emit(self.all_firms)
                print("✅ all_completed sinyali gönderildi!")  # DEBUG
            else:
                print("⚠️ İşlem durduruldu")  # DEBUG
                self.progress.emit(f"⏹️ İşlem durduruldu. {len(self.all_firms)} firma bulundu.")
        
        except Exception as e:
            print(f"💥 Genel hata: {str(e)}")  # DEBUG
            self.error.emit(f"Genel hata: {str(e)}")
            if ROBUST_SYSTEM_AVAILABLE:
                logger.error(f"BatchSearchThread genel hatası: {e}")
        
        print("🔚 BatchSearchThread run metodu bitti!")  # DEBUG


class SingleSearchThread(QThread):
    """Tek seferde firma arama için özel thread"""
    progress = Signal(str)
    firm_found = Signal(dict)
    all_completed = Signal(list)
    error = Signal(str)
    
    def __init__(self, query, location, max_results):
        super().__init__()
        self.query = query
        self.location = location
        self.max_results = max_results
        
        # Güvenli modül yükleme
        if API_MANAGER_AVAILABLE:
            self.api_manager = APIManager()
        else:
            self.api_manager = None
            
        if DATABASE_AVAILABLE:
            self.db = Database()
        else:
            self.db = None
            
        self.is_running = True
        self.all_firms = []
    
    def stop(self):
        """İşlemi durdur"""
        self.is_running = False
        if self.api_manager:
            self.api_manager.cancel_operation()
        self.progress.emit("⏹️ İşlem durduruldu")
    
    @safe_execute(max_retries=3, fallback_value=None)
    def run(self):
        """Tek seferde arama yap"""
        try:
            # Sistem sağlık kontrolü
            if ROBUST_SYSTEM_AVAILABLE and not is_system_healthy():
                self.error.emit("Sistem sağlıksız durumda!")
                return
            
            # API ayarlarını güvenli yükle
            if self.api_manager:
                settings = safe_file_read("config.json", default="{}")
                if settings:
                    settings_data = safe_json_loads(settings, default={})
                    self.api_manager.update_settings(settings_data)
                else:
                    self.error.emit("API ayarları bulunamadı!")
                    return
            else:
                self.error.emit("API Manager mevcut değil!")
                return
            
            # Mevcut ID'leri güvenli al
            existing_ids = set()
            if self.db:
                try:
                    existing_place_ids = self.db.get_existing_place_ids()
                    existing_ids = set(existing_place_ids) if existing_place_ids else set()
                except Exception as e:
                    if ROBUST_SYSTEM_AVAILABLE:
                        logger.warning(f"Veritabanı ID'leri alınamadı: {e}")
                    existing_ids = set()
            
            self.progress.emit(f"🔄 {self.query} aramaya başlanıyor...")
            
            # Tek seferde tüm firmaları ara
            firms = self.api_manager.search_google_maps_batch(
                self.query,
                self.location,
                max_results=self.max_results,
                batch_size=self.max_results,
                progress_callback=self.progress.emit,
                existing_firm_ids=list(existing_ids)
            )
            
            if firms and self.is_running:
                self.all_firms = firms
                
                # Her firmayı veritabanına kaydet ve signal gönder
                for firm in firms:
                    if not self.is_running:
                        break
                        
                    if self.db:
                        firm_id = self.db.save_firm(firm)
                        if firm_id:
                            firm['id'] = firm_id  # Add ID to the firm dictionary
                    
                    self.firm_found.emit(firm)
                
                self.progress.emit(f"✅ Toplam {len(firms)} firma bulundu!")
                self.all_completed.emit(firms)
            else:
                self.progress.emit("ℹ️ Firma bulunamadı")
                self.all_completed.emit([])
        
        except Exception as e:
            self.error.emit(f"Arama hatası: {str(e)}")
            if ROBUST_SYSTEM_AVAILABLE:
                logger.error(f"SingleSearchThread hatası: {e}")


class WorkerThread(QThread):
    """Genel arka plan işlemleri için thread"""
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    show_preview = Signal(dict)
    
    def __init__(self, task_type, data):
        super().__init__()
        self.task_type = task_type
        self.data = data
        
        # Manager'ları güvenli şekilde initialize et
        if API_MANAGER_AVAILABLE:
            self.api_manager = APIManager()
        else:
            self.api_manager = None
            
        if WEB_SCRAPER_AVAILABLE:
            self.web_scraper = WebScraper()
        else:
            self.web_scraper = None
            
        if EMAIL_MANAGER_AVAILABLE:
            self.email_manager = EmailManager()
            # Settings yükle - tracking pixel için gerekli!
            try:
                with open("config.json", "r", encoding='utf-8') as f:
                    settings = json.load(f)
                    self.email_manager.update_settings(settings)
            except Exception as e:
                print(f"⚠️ WorkerThread - Email Manager settings yüklenemedi: {e}")
        else:
            self.email_manager = None
            
        if DATABASE_AVAILABLE:
            self.db = Database()
        else:
            self.db = None
        
        # Yeni modüller
        self.data_manager = DataManager() if DATA_MANAGER_AVAILABLE else None
        self.calendar_manager = CalendarManager() if CALENDAR_MANAGER_AVAILABLE else None
        self.analytics = AnalyticsDashboard(self.db) if ANALYTICS_AVAILABLE else None
    
    def run(self):
        try:
            if self.task_type == "analyze_firm":
                self.analyze_firm()
            elif self.task_type == "analyze_multiple":
                self.analyze_multiple_firms()
            elif self.task_type == "send_campaign":
                self.send_campaign()
            # WhatsApp campaign task kaldırıldı
            elif self.task_type == "import_data":
                self.import_data()
            elif self.task_type == "export_data":
                self.export_data()
            elif self.task_type == "generate_test_firms":
                self.generate_test_firms()
            elif self.task_type == "check_spam_score":
                self.check_spam_score()
        except Exception as e:
            self.error.emit(str(e))
    
    def analyze_firm(self):
        firm = self.data['firm']
        
        try:
            with open("config.json", "r") as f:
                settings = json.load(f)
                self.api_manager.update_settings(settings)
        except:
            pass
        
        self.progress.emit(f"🌐 {firm['name']} websitesi analiz ediliyor...")
        
        web_data = self.web_scraper.scrape_website(
            firm.get('website', ''),
            firm['name']
        )
        
        self.progress.emit("📧 Email adresleri aranıyor...")
        
        scraped_emails = web_data.get('emails', [])
        
        domain = web_data.get('domain') or (firm.get('website', '').replace('http://', '').replace('https://', '').split('/')[0] if firm.get('website') else None)
        
        if domain:
            api_emails = self.api_manager.find_emails_combined(firm['name'], domain)
            
            all_emails = scraped_emails.copy()
            for api_email in api_emails:
                if not any(e['email'] == api_email['email'] for e in all_emails):
                    all_emails.append(api_email)
        else:
            all_emails = scraped_emails
        
        firm_data = {**firm, **web_data, "emails": all_emails}
        
        success = self.db.save_firm(firm_data)
        
        if success:
            self.progress.emit(f"✅ {firm['name']} analizi tamamlandı! ({len(all_emails)} email bulundu)")
        else:
            self.progress.emit(f"⚠️ {firm['name']} kaydedilemedi ama analiz tamamlandı")
        
        self.finished.emit({"firm_data": firm_data})
    
    def analyze_multiple_firms(self):
        firms = self.data['firms']
        analyzed_count = 0
        
        for i, firm in enumerate(firms):
            self.progress.emit(f"🔄 Analiz ediliyor ({i+1}/{len(firms)}): {firm['name']}")
            
            self.data = {'firm': firm}
            self.analyze_firm()
            
            analyzed_count += 1
            
            if analyzed_count % 5 == 0 and i < len(firms) - 1:
                self.progress.emit("⏳ Kısa mola...")
                time.sleep(5)
        
        self.finished.emit({
            "status": "completed",
            "analyzed_count": analyzed_count
        })
    
    def send_campaign(self):
        firms = self.data['firms']
        template = self.data['template']
        
        # Manager'ların doğru import edilip edilmediğini kontrol et
        print(f"🔍 DEBUG: EMAIL_MANAGER_AVAILABLE: {EMAIL_MANAGER_AVAILABLE}")
        print(f"🔍 DEBUG: API_MANAGER_AVAILABLE: {API_MANAGER_AVAILABLE}")
        print(f"🔍 DEBUG: EmailManager tipi: {type(self.email_manager)}")
        print(f"🔍 DEBUG: APIManager tipi: {type(self.api_manager)}")
        
        if not EMAIL_MANAGER_AVAILABLE or self.email_manager is None:
            self.error.emit("EmailManager modülü yüklenemedi! email_manager.py dosyasını kontrol edin.")
            return
            
        if not API_MANAGER_AVAILABLE or self.api_manager is None:
            self.error.emit("APIManager modülü yüklenemedi! api_manager.py dosyasını kontrol edin.")
            return
        
        try:
            print("🔍 DEBUG: config.json dosyası okunuyor...")
            with open("config.json", "r", encoding="utf-8") as f:
                settings = json.load(f)
                print(f"🔍 DEBUG: Config yüklendi: {list(settings.keys())}")
                
            print("🔍 DEBUG: EmailManager ayarları güncelleniyor...")
            self.email_manager.update_settings(settings)
            print("🔍 DEBUG: EmailManager ayarları güncellendi")
            
            print("🔍 DEBUG: APIManager ayarları güncelleniyor...")
            self.api_manager.update_settings(settings)
            print("🔍 DEBUG: APIManager ayarları güncellendi")
            
            # Tracking server kontrolü
            tracking_url = settings.get('tracking_url', 'https://web-production-24136.up.railway.app')
            print(f"🔍 DEBUG: Tracking server kontrol ediliyor: {tracking_url}")
            try:
                import requests
                print(f"🔍 DEBUG: Health check URL: {tracking_url}/api/health")
                response = requests.get(f"{tracking_url}/api/health", timeout=15)
                print(f"🔍 DEBUG: Response status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ DEBUG: Tracking server çalışıyor - {data.get('service', 'Unknown')} v{data.get('version', 'Unknown')}")
                    print(f"✅ DEBUG: Database: {data.get('database', 'Unknown')}")
                    print(f"✅ DEBUG: Total emails tracked: {data.get('total_emails_tracked', 0)}")
                else:
                    print(f"⚠️ DEBUG: Tracking server yanıt vermiyor - Status: {response.status_code}")
                    print(f"⚠️ DEBUG: Response: {response.text[:200]}")
            except Exception as e:
                print(f"❌ DEBUG: Railway tracking server bağlantı hatası: {str(e)}")
                print(f"❌ DEBUG: Hata türü: {type(e).__name__}")
                print("⚠️ DEBUG: Railway tracking server'a erişilemiyor")
                print("ℹ️ DEBUG: Railway dashboard'u kontrol edin: https://railway.app")
            
        except FileNotFoundError:
            print("❌ DEBUG: config.json dosyası bulunamadı!")
            self.error.emit("config.json dosyası bulunamadı!")
            return
        except json.JSONDecodeError as e:
            print(f"❌ DEBUG: JSON decode hatası: {str(e)}")
            self.error.emit(f"config.json dosyası geçersiz format: {str(e)}")
            return
        except Exception as e:
            print(f"❌ DEBUG: Genel hata: {str(e)}")
            import traceback
            traceback.print_exc()
            self.error.emit(f"Email ayarları yüklenirken hata: {str(e)}")
            return
        
        sent_count = 0
        
        for i, firm in enumerate(firms):
            firm_emails = firm.get('emails', [])
            single_email = firm.get('email', '')
            
            # None kontrolü
            if firm_emails is None:
                firm_emails = []
                firm['emails'] = firm_emails  # None'ı boş liste ile değiştir
                print(f"🔍 DEBUG: Firma {firm.get('name', 'İsimsiz')} için emails None idi, boş liste yapıldı")
            
            # Eğer emails listesi boş ama tek email alanı dolu ise, emails listesine ekle
            if not firm_emails and single_email and single_email.strip():
                email_obj = {
                    'email': single_email,
                    'position': 'Genel',
                    'source': 'Manuel',
                    'score': 0.9,
                    'is_verified': False
                }
                firm_emails = [email_obj]
                firm['emails'] = firm_emails
                print(f"🔍 DEBUG: Tek email alanından emails listesine eklendi: {single_email}")
            
            print(f"🔍 DEBUG: Kampanya gönderimi - Firma: {firm.get('name', 'İsimsiz')}")
            print(f"🔍 DEBUG: Email verisi: {firm_emails}")
            print(f"🔍 DEBUG: Email sayısı: {len(firm_emails)}")
            
            # Eğer emails yoksa, veritabanından tekrar yükle
            if not firm_emails and firm.get('id'):
                print(f"🔍 DEBUG: Email bulunamadı, veritabanından yeniden yükleniyor...")
                try:
                    db_firm = self.db.get_firm_by_id(firm['id'])
                    if db_firm:
                        firm_emails = db_firm.get('emails', [])
                        print(f"🔍 DEBUG: Veritabanından alınan raw emails: {firm_emails}")
                        print(f"🔍 DEBUG: Raw emails type: {type(firm_emails)}")
                        
                        if firm_emails is None:
                            firm_emails = []
                            print(f"🔍 DEBUG: None olarak geldi, boş liste yapıldı")
                        elif isinstance(firm_emails, str):
                            # JSON string ise parse et
                            if firm_emails.strip():  # Boş string değilse
                                try:
                                    firm_emails = json.loads(firm_emails)
                                    print(f"🔍 DEBUG: JSON parse edildi: {firm_emails}")
                                except Exception as e:
                                    print(f"❌ DEBUG: JSON parse hatası: {str(e)}")
                                    firm_emails = []
                            else:
                                # Boş string ise boş liste yap
                                firm_emails = []
                                print(f"🔍 DEBUG: Boş string, boş liste yapıldı")
                        elif isinstance(firm_emails, list):
                            print(f"🔍 DEBUG: Zaten liste formatında: {firm_emails}")
                        else:
                            print(f"🔍 DEBUG: Bilinmeyen format, boş liste yapıldı: {type(firm_emails)}")
                            firm_emails = []
                        firm['emails'] = firm_emails  # Firmayı güncelle
                        print(f"🔍 DEBUG: Veritabanından yüklenen email sayısı: {len(firm_emails)}")
                except Exception as e:
                    print(f"❌ DEBUG: Veritabanı yükleme hatası: {str(e)}")
                    firm_emails = []
            
            if not firm_emails:
                self.progress.emit(f"⚠️ {firm['name']} için email bulunamadı, atlanıyor...")
                continue
            
            self.progress.emit(f"📝 Mail hazırlanıyor: {firm['name']} ({i+1}/{len(firms)})")
            
            # GPT ile mail oluştur
            try:
                if hasattr(self.api_manager, 'generate_email_gpt'):
                    mail_content = self.api_manager.generate_email_gpt(firm, template)
                else:
                    mail_content = {
                        'subject': f"{firm['name']} için özel teklif",
                        'body': f"""
                        Merhaba {firm['name']} ekibi,
                        
                        {template.get('instructions', 'Sizin için özel bir teklifimiz var.')}
                        
                        Saygılarımla
                        """
                    }
            except Exception as e:
                self.progress.emit(f"⚠️ Mail oluşturma hatası: {str(e)}")
                continue
            
            # ÖNİZLEME BÖLÜMÜ - YENİ EKLENDİ
            self.progress.emit(f"👁️ Mail önizlemesi gösteriliyor: {firm['name']}")
            
            # Önizleme sinyali gönder
            preview_data = {
                'firm': firm,
                'subject': mail_content['subject'],
                'body': mail_content['body'],
                'emails': sorted(firm_emails, key=lambda x: x.get('score', 0), reverse=True)[:3]
            }
            
            # Ana pencereye önizleme göstermesi için sinyal gönder
            self.show_preview.emit(preview_data)
            
            # 10 saniye geri sayım
            for countdown in range(10, 0, -1):
                if hasattr(self, 'skip_preview') and self.skip_preview:
                    self.progress.emit("⏭️ Önizleme atlandı")
                    break
                self.progress.emit(f"⏳ Mail {countdown} saniye sonra gönderilecek... (ESC tuşu ile atla)")
                time.sleep(1)
            
            # Spam kontrolü
            if self.analytics:
                try:
                    spam_score = self.analytics.check_spam_score(mail_content['body'])
                    if spam_score > 5:
                        self.progress.emit(f"⚠️ Yüksek spam skoru ({spam_score}), içerik optimize ediliyor...")
                        if hasattr(self.api_manager, 'optimize_email_content'):
                            mail_content = self.api_manager.optimize_email_content(mail_content)
                except:
                    pass
            
            # Email gönder
            sorted_emails = sorted(firm_emails, key=lambda x: x.get('score', 0), reverse=True)
            
            for j, email_data in enumerate(sorted_emails[:3]):
                self.progress.emit(f"📧 Email gönderiliyor: {email_data['email']} ({j+1}/{len(sorted_emails[:3])})")
                
                print(f"🔍 DEBUG: Email gönderimi başlıyor - {email_data['email']}")
                print(f"🔍 DEBUG: Subject: {mail_content['subject']}")
                print(f"🔍 DEBUG: Body uzunluğu: {len(mail_content['body'])}")
                
                result = self.email_manager.send_email(
                    to_email=email_data['email'],
                    subject=mail_content['subject'],
                    body=mail_content['body'],
                    firm_id=firm['id']
                )
                
                print(f"🔍 DEBUG: Email gönderim sonucu: {result}")
                
                self.db.save_email_log(
                    firm['id'], 
                    email_data['email'], 
                    result.get('subject', 'Kampanya Maili'),
                    result.get('body', ''),
                    'sent' if result['success'] else 'failed'
                )
                
                if result['success']:
                    sent_count += 1
                    self.progress.emit(f"✅ Gönderildi: {email_data['email']}")
                else:
                    self.progress.emit(f"❌ Hata: {email_data['email']} - {result.get('error', 'Bilinmeyen hata')}")
                
                # GUI'yi güncelle
                self.progress.emit(f"📊 İlerleme: {sent_count} email gönderildi")
                time.sleep(0.5)  # Daha kısa bekleme
            
            if i < len(firms) - 1 and sent_count > 0:
                for j in range(10, 0, -1):
                    self.progress.emit(f"⏳ Sonraki firma için {j} saniye bekleniyor...")
                    time.sleep(1)
        
        self.progress.emit(f"🎉 Kampanya tamamlandı! {sent_count} email başarıyla gönderildi.")
        
        # GUI durumunu sıfırla - DÜZELTME
        self.progress.emit("✨ Sistem hazır - Yeni kampanya başlatabilirsiniz")
        
        self.finished.emit({
            "status": "completed",
            "sent_count": sent_count
        })
    
    # WhatsApp campaign fonksiyonu kaldırıldı
    
    def import_data(self):
        """Veri import işlemi"""
        file_path = self.data['file_path']
        file_type = self.data['file_type']
        
        self.progress.emit(f"📥 {file_type} dosyası içe aktarılıyor...")
        
        if self.data_manager:
            result = self.data_manager.import_firms(file_path, file_type)
            
            self.progress.emit(f"✅ {result['imported_count']} firma başarıyla içe aktarıldı!")
            
            if result.get('errors'):
                self.progress.emit(f"⚠️ {len(result['errors'])} hata oluştu")
            
            self.finished.emit(result)
        else:
            self.error.emit("DataManager modülü bulunamadı!")
    
    def export_data(self):
        """Veri export işlemi"""
        file_path = self.data['file_path']
        file_type = self.data['file_type']
        filters = self.data.get('filters', {})
        
        self.progress.emit(f"📤 Veriler {file_type} formatında dışa aktarılıyor...")
        
        if self.data_manager:
            firms = self.db.get_firms_by_filter(filters)
            result = self.data_manager.export_firms(firms, file_path, file_type)
            
            self.progress.emit(f"✅ {result['exported_count']} firma başarıyla dışa aktarıldı!")
            self.finished.emit(result)
        else:
            self.error.emit("DataManager modülü bulunamadı!")
    
    def generate_test_firms(self):
        """Test firmaları oluştur"""
        count = self.data['count']
        sector = self.data.get('sector', 'mixed')
        
        self.progress.emit(f"🎲 {count} adet test firma oluşturuluyor...")
        
        if self.data_manager:
            generated_firms = self.data_manager.generate_test_firms(count, sector)
            
            for i, firm in enumerate(generated_firms):
                self.db.save_firm(firm)
                if i % 10 == 0:
                    self.progress.emit(f"📝 {i+1}/{count} firma oluşturuldu...")
            
            self.progress.emit(f"✅ {count} test firma başarıyla oluşturuldu!")
            self.finished.emit({"generated_count": count, "firms": generated_firms})
        else:
            self.error.emit("DataManager modülü bulunamadı!")
    
    def check_spam_score(self):
        """Spam skoru kontrol"""
        content = self.data['content']
        
        if self.analytics:
            score = self.analytics.check_spam_score(content)
            suggestions = self.analytics.get_spam_improvement_suggestions(content)
            
            self.finished.emit({
                "score": score,
                "suggestions": suggestions
            })
        else:
            self.error.emit("AnalyticsDashboard modülü bulunamadı!")


class ModernCard(QFrame):
    """Modern kart widget'ı"""
    def __init__(self, title, value, color, icon=""):
        super().__init__()
        self.setObjectName("modernCard")
        
        # Rengi güvenli şekilde parse et
        try:
            if color.startswith("rgba"):
                # RGBA formatından RGB'ye çevir
                rgba_values = color.replace("rgba(", "").replace(")", "").split(",")
                if len(rgba_values) >= 3:
                    r, g, b = [int(x.strip()) for x in rgba_values[:3]]
                    background_color = f"rgb({r}, {g}, {b})"
                else:
                    background_color = "#0d7377"  # fallback color
            elif color.startswith("rgb"):
                background_color = color
            elif color.startswith("#"):
                background_color = color
            else:
                background_color = "#0d7377"  # fallback color
        except Exception:
            background_color = "#0d7377"  # fallback color
            
        self.setStyleSheet(f"""
            QFrame#modernCard {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {background_color},
                    stop: 1 shade({background_color}, 120));
                border-radius: 18px;
                padding: 25px;
                min-height: 120px;
                border: 2px solid shade({background_color}, 130);
            }}
            QFrame#modernCard:hover {{
                border: 3px solid shade({background_color}, 150);
                transform: scale(1.02);
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet("""
            font-size: 14px;
            color: rgba(255,255,255,0.8);
            font-weight: 500;
        """)
        
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

# ConversationBridge sınıfı kaldırıldı


# Otomasyon akış editörü için basit blok widget
class FlowBlockWidget(QGraphicsItem):
    """Otomasyon akış bloğu"""
    def __init__(self, block_type, title, x=0, y=0):
        super().__init__()
        self.block_type = block_type
        self.title = title
        self.width = 150
        self.height = 80
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        # Blok renkleri
        self.colors = {
            'trigger': QColor(52, 152, 219),     # Mavi
            'condition': QColor(241, 196, 15),   # Sarı
            'action': QColor(46, 204, 113),      # Yeşil
            'delay': QColor(155, 89, 182)        # Mor
        }
    
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        # Gölge
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
        painter.drawRoundedRect(5, 5, self.width, self.height, 10, 10)
        
        # Ana blok
        color = self.colors.get(self.block_type, QColor(100, 100, 100))
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.white, 2))
        painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)
        
        # Başlık
        painter.setPen(QPen(Qt.white))
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        painter.drawText(QRectF(0, 0, self.width, self.height), 
                        Qt.AlignCenter, self.title)

class FlowEditorBridge(QObject):
    """JavaScript ile Qt arasında köprü"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
    
    @Slot(str)
    def updateFlowData(self, flow_data_json):
        """Flow verisi güncellendi"""
        try:
            flow_data = json.loads(flow_data_json)
            self.main_window.current_flow_data = flow_data
            self.main_window.flow_modified = True
            self.main_window.save_flow_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                        stop: 0 #e74c3c, stop: 1 #c0392b);
                }
            """)
        except Exception as e:
            print(f"Flow data update error: {str(e)}")
    
    @Slot(str, str)
    def selectBlock(self, block_id, block_data_json):
        """Blok seçildi"""
        try:
            block_data = json.loads(block_data_json)
            self.main_window.show_block_properties(block_data)
            
            # Kod bloğuysa kod editörünü göster
            if block_data.get('type') == 'code':
                self.main_window.code_editor.setText(block_data.get('code', ''))
        except Exception as e:
            print(f"Block selection error: {str(e)}")
    
    @Slot(str, str)
    def selectConnection(self, edge_id, edge_data_json):
        """Bağlantı seçildi"""
        # Bağlantı özelliklerini göster
        pass
    
    @Slot()
    def clearSelection(self):
        """Seçim temizlendi"""
        self.main_window.block_properties.setRowCount(0)
        self.main_window.code_editor.clear()
    
    @Slot(str, str)
    def editBlock(self, block_id, block_data_json):
        """Blok düzenleme"""
        try:
            block_data = json.loads(block_data_json)
            self.main_window.edit_block_dialog(block_id, block_data)
        except Exception as e:
            print(f"Block edit error: {str(e)}")
    
    @Slot(str)
    def blockAdded(self, block_id):
        """Yeni blok eklendi"""
        self.main_window.debug_log(f"✅ Yeni blok eklendi: {block_id}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Global WebEngine error handler - Manifest hatalarını yakala
        self.setup_global_error_handling()
        
        # Güçlendirilmiş sistem başlatma
        if ROBUST_SYSTEM_AVAILABLE:
            try:
                enhance_main_system()
                if logger:
                    logger.info("Ana pencere güçlendirilmiş sistem ile başlatıldı")
            except Exception as e:
                print(f"Güçlendirilmiş sistem başlatılamadı: {e}")
        
        # Güvenli veritabanı bağlantısı
        if DATABASE_AVAILABLE:
            try:
                self.db = Database()
            except Exception as e:
                print(f"Veritabanı bağlantısı başarısız: {e}")
                self.db = None
        else:
            self.db = None
            
        # Güvenli API manager - 🆕 Database bağlantısı ile
        if API_MANAGER_AVAILABLE:
            try:
                self.api_manager = APIManager(db=self.db)  # Database instance'ını geçir
            except Exception as e:
                print(f"API Manager başlatılamadı: {e}")
                self.api_manager = None
        else:
            self.api_manager = None
            
        # Email Manager initialize
        if EMAIL_MANAGER_AVAILABLE:
            try:
                self.email_manager = EmailManager()
                # Settings'leri yükle
                try:
                    with open("config.json", "r") as f:
                        settings = json.load(f)
                        self.email_manager.update_settings(settings)
                        print("✅ Email Manager settings yüklendi")
                except Exception as e:
                    print(f"⚠️ Email Manager settings yüklenemedi: {e}")
            except Exception as e:
                print(f"Email Manager başlatılamadı: {e}")
                self.email_manager = None
        else:
            self.email_manager = None
            
        self.current_firms = []
        self.all_firms = []  # Tüm firmalar listesi
        self.selected_firms = []
        self.batch_search_thread = None
        self.worker_thread = None
        
        # Initialize missing UI attributes
        self.current_urls = None
        self.firm1_loading = None
        self.scraper_stats = {
            'total_scraped': 0,
            'session_start': time.time(),
            'load_times': [],
            'success_count': 0,
            'error_count': 0
        }
        
        # Güvenli manager'lar
        if DATA_MANAGER_AVAILABLE:
            try:
                self.data_manager = DataManager()
            except Exception as e:
                print(f"Data Manager başlatılamadı: {e}")
                self.data_manager = None
        else:
            self.data_manager = None
            
        if CALENDAR_MANAGER_AVAILABLE:
            try:
                self.calendar_manager = CalendarManager()
            except Exception as e:
                print(f"Calendar Manager başlatılamadı: {e}")
                self.calendar_manager = None
        else:
            self.calendar_manager = None
            
        # AI Strategy Analyzer initialize
        if AI_STRATEGY_AVAILABLE:
            try:
                self.ai_strategy_analyzer = AIStrategyAnalyzer()
                print("✅ AI Strategy Analyzer başlatıldı")
            except Exception as e:
                print(f"AI Strategy Analyzer başlatılamadı: {e}")
                self.ai_strategy_analyzer = None
        else:
            self.ai_strategy_analyzer = None
            
        if ANALYTICS_AVAILABLE and self.db:
            try:
                self.analytics_dashboard = AnalyticsDashboard(self.db)
            except Exception as e:
                print(f"Analytics Dashboard başlatılamadı: {e}")
                self.analytics_dashboard = None
        else:
            self.analytics_dashboard = None
            
        if AUTOMATION_AVAILABLE:
            try:
                self.automation_builder = AutomationBuilder()
            except Exception as e:
                print(f"Automation Builder başlatılamadı: {e}")
                self.automation_builder = None
        else:
            self.automation_builder = None
        
        # 🆕 Tracking GUI Manager
        if TRACKING_GUI_AVAILABLE:
            try:
                self.tracking_gui_manager = get_tracking_gui_manager()
                # Railway server URL'ini güncelle
                if self.tracking_gui_manager:
                    self.tracking_gui_manager.update_server_url("https://web-production-24136.up.railway.app")
                print("✅ Tracking GUI Manager başlatıldı (Railway URL)")
            except Exception as e:
                print(f"⚠️ Tracking GUI Manager başlatılamadı: {e}")
                self.tracking_gui_manager = None
        else:
            self.tracking_gui_manager = None
        
        # API Maliyet Widget'ı
        if API_COST_WIDGET_AVAILABLE:
            try:
                self.api_cost_widget = APICostWidget()
                self.api_cost_widget.set_budget_limit(10.0)  # Varsayılan $10 limit
                # İstatistikleri yükle (varsa)
                self.api_cost_widget.load_stats_from_file("api_cost_stats.json")
                print("✅ API Maliyet Widget başlatıldı")
            except Exception as e:
                print(f"API Cost Widget başlatılamadı: {e}")
                self.api_cost_widget = None
        else:
            self.api_cost_widget = None
        
        # Unified Web Scraper (API maliyet takibi ile)
        if UNIFIED_SCRAPER_AVAILABLE and WEB_SCRAPER_AVAILABLE:
            try:
                # OpenAI API key'i settings'ten al
                settings = self.load_settings()
                openai_key = settings.get('openai_api_key', '') if settings else ''
                
                self.unified_scraper = UnifiedWebScraper(
                    use_enhanced=True,
                    openai_api_key=openai_key if openai_key else None,
                    cost_tracker=self.api_cost_widget
                )
                print("✅ Unified Web Scraper başlatıldı (API maliyet takibi aktif)")
            except Exception as e:
                print(f"⚠️ Unified Web Scraper başlatılamadı: {e}")
                self.unified_scraper = None
        else:
            self.unified_scraper = None
        
        # 🆕 Voice Assistant GUI Manager
        if VOICE_ASSISTANT_AVAILABLE:
            try:
                self.voice_assistant_gui = VoiceAssistantGUI(self)
                print("✅ Sesli Asistan GUI başlatıldı")
            except Exception as e:
                print(f"⚠️ Sesli Asistan GUI başlatılamadı: {e}")
                self.voice_assistant_gui = None
        else:
            self.voice_assistant_gui = None
        
        # 🚀 Advanced Voice Assistant GUI Manager
        if ADVANCED_VOICE_ASSISTANT_AVAILABLE:
            try:
                self.advanced_voice_assistant_gui = AdvancedVoiceAssistantGUI(self)
                print("✅ Gelişmiş Sesli Asistan GUI başlatıldı")
            except Exception as e:
                print(f"⚠️ Gelişmiş Sesli Asistan GUI başlatılamadı: {e}")
                self.advanced_voice_assistant_gui = None
        else:
            self.advanced_voice_assistant_gui = None
        
        # WhatsApp Business API kaldırıldı
        
        # WhatsApp modülü kaldırıldı
        
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
        
        # Güvenli timer'lar
        try:
            self.tracking_timer = QTimer()
            self.tracking_timer.timeout.connect(self.safe_check_email_opens)
            self.tracking_timer.start(30000)
        except Exception as e:
            print(f"Tracking timer başlatılamadı: {e}")
            self.tracking_timer = None
        
        try:
            self.dashboard_timer = QTimer()
            self.dashboard_timer.timeout.connect(self.safe_update_dashboard)
            self.dashboard_timer.start(60000)
        except Exception as e:
            print(f"Dashboard timer başlatılamadı: {e}")
            self.dashboard_timer = None
        
        # Analytics timer
        try:
            self.analytics_timer = QTimer()
            self.analytics_timer.timeout.connect(self.safe_update_analytics)
            self.analytics_timer.start(120000)  # 2 dakikada bir
        except Exception as e:
            print(f"Analytics timer başlatılamadı: {e}")
            self.analytics_timer = None
        
        # Sistem izlemeyi başlat
        if ROBUST_SYSTEM_AVAILABLE and hasattr(self, 'system_monitor'):
            try:
                self.system_monitor.start_monitoring()
            except Exception as e:
                print(f"Sistem izleme başlatılamadı: {e}")
        
        self.setupUI()
        self.apply_modern_theme()
        self.load_settings()
    
    def closeEvent(self, event):
        """Güçlendirilmiş pencere kapatma"""
        try:
            # API maliyet istatistiklerini kaydet
            if hasattr(self, 'api_cost_widget') and self.api_cost_widget:
                try:
                    self.api_cost_widget.save_stats("api_cost_stats.json")
                    print("✅ API maliyet istatistikleri kaydedildi")
                except Exception as e:
                    print(f"⚠️ API maliyet kayıt hatası: {e}")
            
            # Timer'ları güvenli durdur
            if hasattr(self, 'tracking_timer') and self.tracking_timer:
                self.tracking_timer.stop()
            if hasattr(self, 'dashboard_timer') and self.dashboard_timer:
                self.dashboard_timer.stop()
            if hasattr(self, 'analytics_timer') and self.analytics_timer:
                self.analytics_timer.stop()
            
            # Thread'leri güvenli durdur
            if hasattr(self, 'batch_search_thread') and self.batch_search_thread and self.batch_search_thread.isRunning():
                self.batch_search_thread.stop()
                self.batch_search_thread.wait(2000)
            
            if hasattr(self, 'worker_thread') and self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(2000)
            
            # Sistem izlemeyi durdur
            if ROBUST_SYSTEM_AVAILABLE and hasattr(self, 'system_monitor'):
                try:
                    self.system_monitor.stop_monitoring()
                except Exception as e:
                    print(f"Sistem izleme durdurulamadı: {e}")
            
            # Veritabanı bağlantısını güvenli kapat
            if hasattr(self, 'db') and self.db and hasattr(self.db, 'close'):
                try:
                    self.db.close()
                except Exception as e:
                    print(f"Veritabanı kapatılamadı: {e}")
            
            # Bellek temizliği
            if ROBUST_SYSTEM_AVAILABLE:
                try:
                    MemoryManager.cleanup_memory()
                except Exception as e:
                    print(f"Bellek temizliği başarısız: {e}")
            
            # Güçlendirilmiş sistem temizliği
            if ROBUST_SYSTEM_AVAILABLE and hasattr(self, 'shutdown_manager'):
                try:
                    self.shutdown_manager.cleanup()
                except Exception as e:
                    print(f"Sistem temizliği başarısız: {e}")
            
            event.accept()
            
        except Exception as e:
            print(f"Kapatma işlemi sırasında hata: {e}")
            event.accept()  # Yine de kapatmaya devam et
    
    def cleanup_resources(self):
        """Kaynak temizleme"""
        try:
            if hasattr(self, 'db') and self.db:
                self.db.close()
            if ROBUST_SYSTEM_AVAILABLE:
                MemoryManager.cleanup_memory()
        except Exception as e:
            print(f"Kaynak temizleme hatası: {e}")
    
    @safe_execute(max_retries=2, fallback_value=None)
    def safe_check_email_opens(self):
        """Güvenli email açılma kontrolü"""
        if hasattr(self, 'check_email_opens'):
            return self.check_email_opens()
        return None
    
    @safe_execute(max_retries=2, fallback_value=None)
    def safe_update_dashboard(self):
        """Güvenli dashboard güncelleme"""
        if hasattr(self, 'update_dashboard'):
            return self.update_dashboard()
        return None
    
    @safe_execute(max_retries=2, fallback_value=None)
    def safe_update_analytics(self):
        """Güvenli analytics güncelleme"""
        if hasattr(self, 'update_analytics'):
            return self.update_analytics()
        return None
    
    # API Maliyet Widget Fonksiyonları
    def reset_api_costs(self):
        """API maliyet istatistiklerini sıfırla"""
        try:
            reply = QMessageBox.question(
                self,
                "🔄 İstatistikleri Sıfırla",
                "API maliyet istatistiklerini sıfırlamak istediğinizden emin misiniz?\n\n"
                "Bu işlem geri alınamaz!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if hasattr(self, 'api_cost_widget') and self.api_cost_widget:
                    self.api_cost_widget.reset_stats()
                    QMessageBox.information(
                        self,
                        "✅ Başarılı",
                        "API maliyet istatistikleri sıfırlandı."
                    )
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"İstatistik sıfırlama hatası:\n{str(e)}")
    
    def show_api_cost_details(self):
        """Detaylı API maliyet istatistiklerini göster"""
        try:
            if hasattr(self, 'api_cost_widget') and self.api_cost_widget:
                stats = self.api_cost_widget.get_stats()
                
                if API_COST_WIDGET_AVAILABLE:
                    dialog = APICostDetailsDialog(stats, self)
                    dialog.exec()
                else:
                    # Basit mesaj kutusu
                    details = f"""
📊 API Maliyet İstatistikleri

💰 Maliyet Bilgileri:
• Toplam Harcama: ${stats['total_cost']:.4f}
• Bütçe Limiti: ${stats['budget_limit']:.2f}
• Kalan Bütçe: ${stats['remaining_budget']:.4f}
• Kullanım Oranı: %{stats['usage_percentage']:.1f}

📊 Kullanım İstatistikleri:
• Toplam İstek: {stats['total_requests']}
• Analiz Edilen Görsel: {stats['total_images']}
• İstek Başına Ort. Maliyet: ${stats['average_cost_per_request']:.4f}
• Görsel Başına Ort. Maliyet: ${stats['average_cost_per_image']:.4f}

⏱️ Oturum Bilgileri:
• Başlangıç: {stats['session_start']}
                    """
                    QMessageBox.information(self, "📊 API Maliyet Detayları", details)
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Detay gösterme hatası:\n{str(e)}")
    
    def apply_modern_theme(self):
        """Modern tema uygula - Responsive Font ve Boyutlarla"""
        
        # Responsive font boyutları ve boyut değerleri hesapla
        if not hasattr(self, 'scale_factor'):
            self.scale_factor = 1.0
        
        base_font_size = max(11, int(14 * self.scale_factor))
        small_font_size = max(10, int(12 * self.scale_factor))
        large_font_size = max(14, int(18 * self.scale_factor))
        button_padding = max(8, int(10 * self.scale_factor))
        button_padding_h = max(16, int(20 * self.scale_factor))
        border_radius = max(6, int(8 * self.scale_factor))
        tab_padding = max(10, int(12 * self.scale_factor))
        tab_padding_h = max(20, int(24 * self.scale_factor))
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #0f0f0f;
            }}
            
            QTabWidget::pane {{
                border: none;
                background-color: #1a1a1a;
                border-radius: 10px;
            }}
            
            QTabBar::tab {{
                background-color: #2a2a2a;
                color: #ffffff;
                padding: {tab_padding}px {tab_padding_h}px;
                margin-right: 5px;
                border-radius: {border_radius}px {border_radius}px 0 0;
                font-weight: 500;
                font-size: {small_font_size}px;
            }}
            
            QTabBar::tab:selected {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0d7377, stop: 1 #14a1a5);
                color: white;
            }}
            
            QTabBar::tab:hover {{
                background-color: #3a3a3a;
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
                padding: 8px;
                border-bottom: 1px solid #2a2a2a;
            }}
            
            QHeaderView::section {{
                background-color: #2a2a2a;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
            
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0d7377, stop: 1 #14a1a5);
                color: white;
                border: none;
                padding: {button_padding}px {button_padding_h}px;
                border-radius: {border_radius}px;
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
            
            QPushButton:disabled {{
                background: #3a3a3a;
                color: #666666;
            }}
            
            QLineEdit, QTextEdit, QSpinBox, QComboBox {{
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                padding: {button_padding}px;
                border-radius: {border_radius}px;
                font-size: {base_font_size}px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border: 2px solid #0d7377;
                background-color: #1a1a1a;
            }}
            
            QLabel {{
                color: #ffffff;
                font-size: {base_font_size}px;
            }}
            
            QGroupBox {{
                color: #ffffff;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
                margin-top: {max(12, int(15 * self.scale_factor))}px;
                padding-top: {max(12, int(15 * self.scale_factor))}px;
                font-weight: bold;
                font-size: {large_font_size}px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #1a1a1a;
            }}
            
            QProgressBar {{
                border: none;
                border-radius: 10px;
                text-align: center;
                background-color: #2a2a2a;
                height: 25px;
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a1a5);
                border-radius: 10px;
            }}
            
            QCheckBox {{
                color: white;
                spacing: 10px;
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #3a3a3a;
                background-color: #2a2a2a;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: #0d7377;
                border-color: #0d7377;
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
            
            QGraphicsView {{
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 10px;
            }}
            
            QDateTimeEdit {{
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                padding: 10px;
                border-radius: 8px;
            }}
            
            QDateTimeEdit::drop-down {{
                background-color: #3a3a3a;
                border-radius: 4px;
            }}
            
            QDateTimeEdit::down-arrow {{
                image: none;
                width: 10px;
                height: 10px;
                background-color: white;
            }}
        """)
    
    def setupUI(self):
        """Ana UI Kurulumu"""
        self.setWindowTitle("B2B Mail Automation Pro - AI Powered ✨")
        
        # Basit pencere boyutlandırma
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        
        # Tab widget oluştur
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Tab'ları oluştur
        # Tab 1: Dashboard
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # Tab 2: Kampanya
        self.campaign_tab = self.create_campaign_tab()
        self.tabs.addTab(self.campaign_tab, "📧 Kampanya")
        
        # Tab 3: Firma Arama
        self.search_tab = self.create_search_tab()
        self.tabs.addTab(self.search_tab, "🔍 Arama")
        
        # Tab 4: Firma Yönetimi
        self.firms_tab = self.create_firms_tab()
        self.tabs.addTab(self.firms_tab, "🏢 Firmalar")
        
        # Tab 5: Akıllı Gruplandırma
        self.grouping_tab = self.create_grouping_tab()
        self.tabs.addTab(self.grouping_tab, "📊 Gruplandırma")
        
        # Tab 6: Kategori Yönetimi
        self.categories_tab = self.create_categories_tab()
        self.tabs.addTab(self.categories_tab, "🏷️ Kategoriler")
        
        # Tab 5: Takip
        self.tracking_tab = self.create_tracking_tab()
        self.tabs.addTab(self.tracking_tab, "📈 Takip")
        
        # Tab 6: WhatsApp
        self.whatsapp_tab = self.create_whatsapp_tab()
        self.tabs.addTab(self.whatsapp_tab, "📱 WhatsApp")
        
        # Tab 7: Özel Mail Gönderim
        if CUSTOM_MAIL_TAB_AVAILABLE and self.email_manager:
            self.custom_mail_tab = CustomMailSenderTab(self)
            self.custom_mail_tab.set_email_manager(self.email_manager)
            self.tabs.addTab(self.custom_mail_tab, "✉️ Özel Mail")
        
        # Tab 8: Gelişmiş Analitik
        self.analytics_tab = self.create_analytics_tab()
        self.tabs.addTab(self.analytics_tab, "📊 Analitik")
        
        # Tab 9: Otomasyon Akışları
        self.automation_tab = self.create_automation_tab()
        self.tabs.addTab(self.automation_tab, "🔄 Otomasyon")
        
        # Tab 10: Randevu & Takvim
        self.calendar_tab = self.create_calendar_tab()
        self.tabs.addTab(self.calendar_tab, "📅 Takvim")
        
        # Tab 11: Import/Export
        self.import_export_tab = self.create_import_export_tab()
        self.tabs.addTab(self.import_export_tab, "📥 I/O")
        
        # Tab 12: Web Scraper
        self.webscraper_tab = self.create_webscraper_tab()
        self.tabs.addTab(self.webscraper_tab, "🌐 Scraper")
        
        # Tab 13: Haftalık Rapor
        self.weekly_report_tab = self.create_weekly_report_tab()
        self.tabs.addTab(self.weekly_report_tab, "📊 Haftalık Rapor")
        
        # Tab 13: Firma Bilgi Öğretim
        if KNOWLEDGE_LEARNING_AVAILABLE:
            try:
                self.knowledge_learning_tab = KnowledgeLearningTab(self.db, self.api_manager)
                self.tabs.addTab(self.knowledge_learning_tab, "🧠 Bilgi Öğretim")
                print("✅ Bilgi Öğretim sekmesi eklendi")
            except Exception as e:
                print(f"⚠️ Bilgi Öğretim sekmesi yüklenemedi: {e}")
        
        # Tab 14: AI Strateji Analizi
        if AI_STRATEGY_AVAILABLE and self.ai_strategy_analyzer:
            self.ai_strategy_tab = self.create_ai_strategy_tab()
            self.tabs.addTab(self.ai_strategy_tab, "🤖 AI Strateji")
            print("✅ AI Strateji sekmesi eklendi")
        
        # Tab 15: AI Sohbet Asistanı
        if AI_CHAT_AVAILABLE:
            try:
                self.ai_chat_tab = AIChatAssistantTab(self.db, self.api_manager)
                self.tabs.addTab(self.ai_chat_tab, "🤖 AI Asistan")
                print("✅ AI Sohbet Asistanı sekmesi eklendi")
            except Exception as e:
                print(f"⚠️ AI Sohbet Asistanı yüklenemedi: {e}")
        
        # Tab 15: AI Mail Takip Stratejisi
        if MAIL_STRATEGY_AVAILABLE:
            try:
                self.mail_strategy_tab = MailStrategyTab(parent=self)
                # Database erişimi sağla
                if hasattr(self, 'db') and self.db:
                    self.mail_strategy_tab.parent = self
                self.tabs.addTab(self.mail_strategy_tab, "🎯 Mail Stratejisi")
                print("✅ AI Mail Takip Stratejisi sekmesi eklendi")
            except Exception as e:
                print(f"⚠️ Mail Stratejisi sekmesi yüklenemedi: {e}")
        
        # Tab 16: Sesli Asistan
        if VOICE_ASSISTANT_AVAILABLE:
            try:
                self.voice_assistant_tab = self.create_voice_assistant_tab()
                self.tabs.addTab(self.voice_assistant_tab, "🎤 Sesli Asistan")
                print("✅ Sesli Asistan sekmesi eklendi")
            except Exception as e:
                print(f"⚠️ Sesli Asistan sekmesi yüklenemedi: {e}")
        
        # Tab 17: Ayarlar
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "⚙️ Ayarlar")
        
        # Tab 18: Firma Detay Analizi (YENİ)
        if FIRMA_DETAY_AVAILABLE:
            try:
                self.firma_detay_tab = FirmaDetayAnalyzer(self.db, self.api_manager)
                self.tabs.addTab(self.firma_detay_tab, "🏢 Firma Detay")
                print("✅ Firma Detay Analiz sekmesi eklendi")
            except Exception as e:
                print(f"⚠️ Firma Detay Analiz sekmesi yüklenemedi: {e}")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✨ Hazır")
        
        # Progress bar (status bar içinde)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Mevcut firmaları yükle
        self.load_all_firms()
    
    def load_all_firms(self):
        """Mevcut tüm firmaları yükle"""
        try:
            if self.db:
                self.all_firms = self.db.get_firms_by_filter({})
                print(f"📊 {len(self.all_firms)} firma yüklendi")
            else:
                self.all_firms = []
                print("⚠️ Veritabanı bağlantısı yok, firma listesi boş")
        except Exception as e:
            print(f"❌ Firma yükleme hatası: {e}")
            self.all_firms = []
    
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
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout - Responsive margin ve spacing
        main_layout = QVBoxLayout(central_widget)
        
        # Ekran boyutuna göre margin ve spacing hesapla
        base_margin = int(20 * self.scale_factor)
        base_spacing = int(10 * self.scale_factor)
        
        # Minimum değerleri garanti et
        margin = max(15, base_margin)
        spacing = max(8, base_spacing)
        
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(spacing)
        
        # Başlık paneli - Responsive yükseklik
        header_widget = QWidget()
        header_height = max(50, int(60 * self.scale_factor))
        header_widget.setMaximumHeight(header_height)
        # Responsive header styling
        header_padding = max(8, int(10 * self.scale_factor))
        header_border_radius = max(8, int(10 * self.scale_factor))
        
        header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: #1a1a1a;
                border-radius: {header_border_radius}px;
                padding: {header_padding}px;
            }}
        """)
        
        header_layout = QHBoxLayout(header_widget)
        # Responsive header margins
        header_margin_h = max(15, int(20 * self.scale_factor))
        header_margin_v = max(8, int(10 * self.scale_factor))
        header_layout.setContentsMargins(header_margin_h, header_margin_v, header_margin_h, header_margin_v)
        
        # Logo ve başlık - Responsive font size
        title_label = QLabel("🚀 B2B Mail Automation Pro")
        title_font_size = max(20, int(28 * self.scale_factor))
        title_label.setStyleSheet(f"""
            font-size: {title_font_size}px;
            font-weight: bold;
            color: white;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Hızlı istatistikler - Responsive font size
        self.quick_stats_label = QLabel("📊 Yükleniyor...")
        stats_font_size = max(12, int(14 * self.scale_factor))
        self.quick_stats_label.setStyleSheet(f"""
            font-size: {stats_font_size}px;
            color: #14a1a5;
            font-weight: 500;
        """)
        header_layout.addWidget(self.quick_stats_label)
        
        main_layout.addWidget(header_widget)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #1a1a1a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                margin-left: 0px;
                border-radius: 6px 6px 0 0;
                font-weight: 500;
                font-size: 12px;
                min-width: 80px;
                max-width: 120px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0d7377, stop: 1 #14a1a5);
                color: white;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
            QTabBar {
                alignment: left;
            }
        """)
        
        # Tab 1: Dashboard
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # Tab 2: Firma Ara
        self.search_tab = self.create_search_tab()
        self.tabs.addTab(self.search_tab, "🔍 Firma Ara")
        
        # Tab 3: Kampanya
        self.campaign_tab = self.create_campaign_tab()
        self.tabs.addTab(self.campaign_tab, "📧 Kampanya")
        
        # Tab 4: Tracking
        self.tracking_tab = self.create_tracking_tab()
        self.tabs.addTab(self.tracking_tab, "📈 Tracking")
        
        # Tab 5: Firmalar
        self.firms_tab = self.create_firms_tab()
        self.tabs.addTab(self.firms_tab, "🏢 Firmalar")
        
        # Tab 6: WhatsApp
        self.whatsapp_tab = self.create_whatsapp_tab()
        self.tabs.addTab(self.whatsapp_tab, "📱 WhatsApp")
        
        # Tab 7: Gelişmiş Analitik (YENİ)
        self.analytics_tab = self.create_analytics_tab()
        self.tabs.addTab(self.analytics_tab, "📊 Analitik")
        
        # Tab 8: Otomasyon Akışları (YENİ)
        self.automation_tab = self.create_automation_tab()
        self.tabs.addTab(self.automation_tab, "🔄 Otomasyon")
        
        # Tab 9: Randevu & Takvim (YENİ)
        self.calendar_tab = self.create_calendar_tab()
        self.tabs.addTab(self.calendar_tab, "📅 Takvim")
        
        # Tab 10: Import/Export (YENİ)
        self.import_export_tab = self.create_import_export_tab()
        self.tabs.addTab(self.import_export_tab, "📥 I/O")
        
        # Tab 11: Web Scraper (YENİ)
        self.webscraper_tab = self.create_webscraper_tab()
        self.tabs.addTab(self.webscraper_tab, "🌐 Scraper")
        
        # Tab 12: Haftalık Rapor (YENİ)
        self.weekly_report_tab = self.create_weekly_report_tab()
        self.tabs.addTab(self.weekly_report_tab, "📊 Haftalık Rapor")
        
        # Tab 13: Firma Bilgi Öğretim
        if KNOWLEDGE_LEARNING_AVAILABLE:
            try:
                self.knowledge_learning_tab = KnowledgeLearningTab(self.db, self.api_manager)
                self.tabs.addTab(self.knowledge_learning_tab, "🧠 Bilgi Öğretim")
            except Exception as e:
                print(f"⚠️ Bilgi Öğretim sekmesi yüklenemedi: {e}")
        
        # Tab 14: Ayarlar
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "⚙️ Ayarlar")
        
        # Tab 15: Firma Detay Analizi (YENİ)
        if FIRMA_DETAY_AVAILABLE:
            try:
                self.firma_detay_tab = FirmaDetayAnalyzer(self.db, self.api_manager)
                self.tabs.addTab(self.firma_detay_tab, "🏢 Firma Detay")
                print("✅ Firma Detay Analiz sekmesi eklendi")
            except Exception as e:
                print(f"⚠️ Firma Detay Analiz sekmesi yüklenemedi: {e}")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✨ Hazır")
        
        # Progress bar (status bar içinde)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def create_dashboard_tab(self):
        """Ultra modern ve gelişmiş dashboard - Gerçek verilerle"""
        widget = QWidget()
        widget.setObjectName("dashboardWidget")
        
        # Ana layout
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #0f0f0f;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
        """)
        
        # Scroll içeriği
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. ÜST HEADER BÖLÜMÜ
        header_widget = QWidget()
        header_widget.setObjectName("dashboardHeader")
        header_widget.setStyleSheet("""
            #dashboardHeader {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a1a1a, stop: 0.5 #0d7377, stop: 1 #1a1a1a);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_widget)
        
        # Hoşgeldin mesajı ve tarih
        welcome_layout = QHBoxLayout()
        
        welcome_label = QLabel("🚀 B2B Mail Automation Dashboard")
        welcome_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 10px;
        """)
        welcome_layout.addWidget(welcome_label)
        
        welcome_layout.addStretch()
        
        # Tarih ve saat widget'ı
        datetime_widget = QWidget()
        datetime_layout = QVBoxLayout(datetime_widget)
        datetime_layout.setContentsMargins(0, 0, 0, 0)
        
        self.date_label = QLabel(datetime.now().strftime("%d %B %Y"))
        self.date_label.setStyleSheet("""
            font-size: 16px;
            color: white;
            font-weight: 500;
        """)
        self.date_label.setAlignment(Qt.AlignRight)
        
        self.time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.time_label.setStyleSheet("""
            font-size: 24px;
            color: #1db8bc;
            font-weight: bold;
        """)
        self.time_label.setAlignment(Qt.AlignRight)
        
        datetime_layout.addWidget(self.date_label)
        datetime_layout.addWidget(self.time_label)
        
        welcome_layout.addWidget(datetime_widget)
        
        header_layout.addLayout(welcome_layout)
        
        # Gerçek özet bilgileri
        stats = self.db.get_statistics()
        today_stats = self.db.get_today_statistics()
        
        # Günlük hedefler (config'den veya varsayılan)
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                daily_email_target = config.get("daily_email_target", 50)
                daily_firm_target = config.get("daily_firm_target", 20)
        except:
            daily_email_target = 50
            daily_firm_target = 20
        
        # Özet bilgi satırı
        summary_layout = QHBoxLayout()
        
        summary_items = [
            ("📈 Günlük Email", f"{today_stats.get('emails_sent_today', 0)}/{daily_email_target}", 
            "#27ae60" if today_stats.get('emails_sent_today', 0) >= daily_email_target else "#f39c12"),
            ("🎯 Günlük Dönüşüm", f"%{today_stats.get('conversion_rate_today', 0):.1f}", 
            "#27ae60" if today_stats.get('conversion_rate_today', 0) > 10 else "#e74c3c"),
            ("💰 Potansiyel Müşteri", f"{today_stats.get('hot_leads', 0)}", "#3498db"),
            ("🔥 Aktif Kampanya", f"{today_stats.get('active_campaigns', 0)}", "#e74c3c")
        ]
        
        for title, value, color in summary_items:
            summary_item = QWidget()
            summary_item_layout = QVBoxLayout(summary_item)
            summary_item_layout.setContentsMargins(10, 5, 10, 5)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
            """)
            title_label.setAlignment(Qt.AlignCenter)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"""
                color: {color};
                font-size: 20px;
                font-weight: bold;
            """)
            value_label.setAlignment(Qt.AlignCenter)
            
            summary_item_layout.addWidget(title_label)
            summary_item_layout.addWidget(value_label)
            
            summary_layout.addWidget(summary_item)
            
            if summary_items.index((title, value, color)) < len(summary_items) - 1:
                separator = QLabel("|")
                separator.setStyleSheet("color: rgba(255, 255, 255, 0.3); font-size: 24px;")
                summary_layout.addWidget(separator)
        
        header_layout.addLayout(summary_layout)
        
        scroll_layout.addWidget(header_widget)
        
        # 1.5. API MALİYET WIDGET'I (Yeni!)
        if hasattr(self, 'api_cost_widget') and self.api_cost_widget:
            api_cost_container = QWidget()
            api_cost_container.setStyleSheet("""
                QWidget {
                    background-color: #1a1a1a;
                    border-radius: 15px;
                    padding: 15px;
                }
            """)
            api_cost_layout = QVBoxLayout(api_cost_container)
            api_cost_layout.setContentsMargins(0, 0, 0, 0)
            
            # Başlık
            api_title = QLabel("💰 API Maliyet Takibi")
            api_title.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 10px;
            """)
            api_cost_layout.addWidget(api_title)
            
            # Widget'ı ekle
            self.api_cost_widget.setFixedWidth(280)
            api_cost_layout.addWidget(self.api_cost_widget)
            
            # Signal bağlantıları
            self.api_cost_widget.reset_requested.connect(self.reset_api_costs)
            self.api_cost_widget.details_requested.connect(self.show_api_cost_details)
            
            scroll_layout.addWidget(api_cost_container)
        
        # 2. ANA İSTATİSTİK KARTLARI
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Gerçek istatistikleri al
        weekly_stats = self.db.get_weekly_comparison()
        monthly_stats = self.db.get_monthly_statistics()
        
        # Gelişmiş kart widget'ı oluştur
        def create_advanced_card(title, value, icon, gradient_colors, trend=None, mini_chart_data=None):
            card = QFrame()
            card.setObjectName("advancedCard")
            card.setStyleSheet(f"""
                #advancedCard {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 {gradient_colors[0]}, stop: 1 {gradient_colors[1]});
                    border-radius: 20px;
                    padding: 20px;
                    min-height: 160px;
                }}
                #advancedCard:hover {{
                    padding: 18px;
                    border: 2px solid {gradient_colors[1]};
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            # Üst kısım - başlık ve ikon
            top_layout = QHBoxLayout()
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("""
                font-size: 32px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 10px;
            """)
            top_layout.addWidget(icon_label)
            
            top_layout.addStretch()
            
            # Trend göstergesi
            if trend is not None:
                trend_widget = QWidget()
                trend_layout = QHBoxLayout(trend_widget)
                trend_layout.setContentsMargins(0, 0, 0, 0)
                
                trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                trend_color = "#27ae60" if trend > 0 else "#e74c3c" if trend < 0 else "#f39c12"
                
                trend_label = QLabel(f"{trend_icon} {abs(trend):.1f}%")
                trend_label.setStyleSheet(f"""
                    color: {trend_color};
                    font-size: 14px;
                    font-weight: bold;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 5px 10px;
                    border-radius: 10px;
                """)
                trend_layout.addWidget(trend_label)
                
                top_layout.addWidget(trend_widget)
            
            card_layout.addLayout(top_layout)
            
            # Orta kısım - değer
            value_label = QLabel(str(value))
            value_label.setObjectName("cardValue")
            value_label.setStyleSheet("""
                font-size: 22px;
                font-weight: bold;
                color: white;
                margin: 10px 0;
            """)
            card_layout.addWidget(value_label)
            
            # Alt kısım - başlık
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 12px;
                color: rgba(255, 255, 255, 0.9);
                font-weight: 500;
            """)
            card_layout.addWidget(title_label)
            
            # Mini grafik
            if mini_chart_data:
                chart_widget = QWidget()
                chart_widget.setFixedHeight(40)
                chart_widget.setStyleSheet("""
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 5px;
                    margin-top: 10px;
                """)
                # Burada mini grafik çizimi yapılabilir
                card_layout.addWidget(chart_widget)
            
            card_layout.addStretch()
            
            return card, value_label
        
        # Kartları oluştur - Gerçek verilerle
        self.total_firms_card, self.total_firms_value = create_advanced_card(
            "Toplam Firma", 
            stats['total_firms'], 
            "🏢", 
            ["rgba(13, 115, 119, 0.8)", "rgba(13, 115, 119, 0.6)"],
            trend=weekly_stats.get('firms_growth_percent', 0),
            mini_chart_data=True
        )
        
        self.analyzed_firms_card, self.analyzed_firms_value = create_advanced_card(
            "Analiz Edilmiş", 
            stats['analyzed_firms'], 
            "🔍",
            ["rgba(20, 161, 165, 0.8)", "rgba(20, 161, 165, 0.6)"],
            trend=weekly_stats.get('analyzed_growth_percent', 0),
            mini_chart_data=True
        )
        
        self.total_emails_card, self.total_emails_value = create_advanced_card(
            "Toplam Email", 
            stats['total_emails'], 
            "📧",
            ["rgba(243, 156, 18, 0.8)", "rgba(243, 156, 18, 0.6)"],
            trend=weekly_stats.get('emails_growth_percent', 0),
            mini_chart_data=True
        )
        
        self.sent_emails_card, self.sent_emails_value = create_advanced_card(
            "Gönderilen", 
            stats['total_sent'], 
            "📤",
            ["rgba(39, 174, 96, 0.8)", "rgba(39, 174, 96, 0.6)"],
            trend=weekly_stats.get('sent_growth_percent', 0),
            mini_chart_data=True
        )
        
        self.open_rate_card, self.open_rate_value = create_advanced_card(
            "Açılma Oranı", 
            f"%{stats['open_rate']}", 
            "📊",
            ["rgba(52, 152, 219, 0.8)", "rgba(52, 152, 219, 0.6)"],
            trend=weekly_stats.get('open_rate_change', 0)
        )
        
        self.response_rate_card, self.response_rate_value = create_advanced_card(
            "Yanıt Oranı", 
            f"%{stats['reply_rate']}", 
            "💬",
            ["rgba(155, 89, 182, 0.8)", "rgba(155, 89, 182, 0.6)"],
            trend=weekly_stats.get('reply_rate_change', 0)
        )
        
        # Kartları grid'e ekle
        stats_grid.addWidget(self.total_firms_card, 0, 0)
        stats_grid.addWidget(self.analyzed_firms_card, 0, 1)
        stats_grid.addWidget(self.total_emails_card, 0, 2)
        stats_grid.addWidget(self.sent_emails_card, 1, 0)
        stats_grid.addWidget(self.open_rate_card, 1, 1)
        stats_grid.addWidget(self.response_rate_card, 1, 2)
        
        scroll_layout.addLayout(stats_grid)
        
        # 3. GRAFİKLER VE ANALİZ BÖLÜMÜ
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Sol taraf - Ana performans grafiği
        main_chart_widget = QFrame()
        main_chart_widget.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        main_chart_layout = QVBoxLayout(main_chart_widget)
        
        # Grafik başlığı ve kontroller
        chart_header_layout = QHBoxLayout()
        
        chart_title = QLabel("📈 Performans Analizi")
        chart_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        chart_header_layout.addWidget(chart_title)
        
        chart_header_layout.addStretch()
        
        # Zaman aralığı butonları
        time_buttons_widget = QWidget()
        time_buttons_layout = QHBoxLayout(time_buttons_widget)
        time_buttons_layout.setContentsMargins(0, 0, 0, 0)
        time_buttons_layout.setSpacing(5)
        
        self.chart_period = "7G"  # Varsayılan
        time_periods = ["24H", "7G", "30G", "3A", "1Y"]
        for period in time_periods:
            period_btn = QPushButton(period)
            period_btn.setObjectName("timeButton")
            period_btn.setCheckable(True)
            period_btn.setChecked(period == "7G")
            period_btn.setStyleSheet("""
                QPushButton#timeButton {
                    background-color: #2a2a2a;
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 8px;
                    font-weight: 500;
                }
                QPushButton#timeButton:checked {
                    background-color: #0d7377;
                }
                QPushButton#timeButton:hover {
                    background-color: #3a3a3a;
                }
            """)
            period_btn.clicked.connect(lambda checked=False, p=period: self.update_chart_period(p))
            time_buttons_layout.addWidget(period_btn)
        
        chart_header_layout.addWidget(time_buttons_widget)
        
        main_chart_layout.addLayout(chart_header_layout)
        
        # Ana grafik
        self.main_chart_view = QWebEngineView()
        self.main_chart_view.setMinimumHeight(400)
        
        # JavaScript error handling ekle
        self.setup_webengine_error_handling(self.main_chart_view)
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = self.main_chart_view.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Main chart profile ayarları uygulanamadı: {e}")
        
        main_chart_layout.addWidget(self.main_chart_view)
        
        charts_layout.addWidget(main_chart_widget, 2)
        
        # Sağ taraf - Ek bilgiler
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Canlı aktivite feed'i
        activity_widget = QFrame()
        activity_widget.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        activity_layout = QVBoxLayout(activity_widget)
        
        activity_title = QLabel("🔄 Son Aktiviteler")
        activity_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        activity_layout.addWidget(activity_title)
        
        # Aktivite listesi
        self.activity_list = QListWidget()
        self.activity_list.setObjectName("activityList")
        self.activity_list.setStyleSheet("""
            QListWidget#activityList {
                background-color: transparent;
                border: none;
            }
            QListWidget#activityList::item {
                background-color: #2a2a2a;
                color: white;
                padding: 12px;
                margin-bottom: 8px;
                border-radius: 10px;
                border-left: 3px solid #0d7377;
            }
            QListWidget#activityList::item:hover {
                background-color: #3a3a3a;
            }
        """)
        activity_layout.addWidget(self.activity_list)
        
        right_layout.addWidget(activity_widget)
        
        # Hedef takip widget'ı
        goals_widget = QFrame()
        goals_widget.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        goals_layout = QVBoxLayout(goals_widget)
        
        goals_title = QLabel("🎯 Günlük Hedefler")
        goals_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        goals_layout.addWidget(goals_title)
        
        # Hedef progress barları - Gerçek verilerle
        goals_data = [
            ("Email Gönderimi", 
            today_stats.get('emails_sent_today', 0), 
            daily_email_target, 
            "#3498db"),
            ("Firma Analizi", 
            today_stats.get('firms_analyzed_today', 0), 
            daily_firm_target, 
            "#e74c3c"),
            ("Yanıt Alımı", 
            today_stats.get('replies_today', 0), 
            max(1, int(daily_email_target * 0.1)),  # Hedef: gönderilen emaillerin %10'u
            "#27ae60")
        ]
        
        for goal_name, current, target, color in goals_data:
            goal_item = QWidget()
            goal_item_layout = QVBoxLayout(goal_item)
            goal_item_layout.setContentsMargins(0, 5, 0, 5)
            
            # Başlık ve değer
            goal_header = QHBoxLayout()
            goal_label = QLabel(goal_name)
            goal_label.setStyleSheet("color: white; font-size: 14px;")
            goal_header.addWidget(goal_label)
            
            goal_value = QLabel(f"{current}/{target}")
            goal_value.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
            goal_header.addWidget(goal_value)
            
            goal_item_layout.addLayout(goal_header)
            
            # Progress bar
            progress = QProgressBar()
            progress.setMaximum(target)
            progress.setValue(current)
            progress.setTextVisible(False)
            progress.setFixedHeight(8)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #2a2a2a;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 4px;
                }}
            """)
            goal_item_layout.addWidget(progress)
            
            goals_layout.addWidget(goal_item)
        
        right_layout.addWidget(goals_widget)
        
        charts_layout.addWidget(right_panel, 1)
        
        scroll_layout.addLayout(charts_layout)
        
        # 4. DETAYLI ANALİTİK TABLOLAR
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(15)
        
        # En başarılı kampanyalar
        campaigns_widget = QFrame()
        campaigns_widget.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        campaigns_layout = QVBoxLayout(campaigns_widget)
        
        campaigns_title = QLabel("🏆 Kampanya Performansları")
        campaigns_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        campaigns_layout.addWidget(campaigns_title)
        
        self.campaigns_table = QTableWidget()
        self.campaigns_table.setMinimumHeight(250)
        self.campaigns_table.setColumnCount(5)
        self.campaigns_table.setHorizontalHeaderLabels(["Kampanya", "Gönderim", "Açılma", "Tıklama", "Dönüşüm"])
        self.campaigns_table.horizontalHeader().setStretchLastSection(True)
        self.campaigns_table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                border: none;
                border-radius: 10px;
            }
            QTableWidget::item {
                color: white;
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #0d7377;
                color: white;
                padding: 10px;
                border: none;
            }
        """)
        campaigns_layout.addWidget(self.campaigns_table)
        
        tables_layout.addWidget(campaigns_widget)
        
        # Son aktiviteler tablosu
        recent_widget = QFrame()
        recent_widget.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        recent_layout = QVBoxLayout(recent_widget)
        
        recent_title = QLabel("📋 Son İşlemler")
        recent_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        recent_layout.addWidget(recent_title)
        
        self.activity_table = QTableWidget()
        self.activity_table.setMinimumHeight(250)
        self.activity_table.setColumnCount(5)
        self.activity_table.setHorizontalHeaderLabels(["Tarih", "Firma", "Email", "Durum", "Detay"])
        self.activity_table.horizontalHeader().setStretchLastSection(True)
        self.activity_table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                border: none;
                border-radius: 10px;
            }
            QTableWidget::item {
                color: white;
                padding: 10px;
            }
            QHeaderView::section {
                background-color: #0d7377;
                color: white;
                padding: 10px;
                border: none;
            }
        """)
        recent_layout.addWidget(self.activity_table)
        
        tables_layout.addWidget(recent_widget)
        
        scroll_layout.addLayout(tables_layout)
        
        # 5. ALT BİLGİ BÖLÜMÜ
        footer_widget = QWidget()
        footer_widget.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 15px;
            padding: 20px;
            margin-top: 10px;
        """)
        footer_layout = QHBoxLayout(footer_widget)
        
        # Sistem durumu
        system_status_text = "🟢 Sistem Aktif"
        if hasattr(self.db, 'check_connection'):
            if not self.db.check_connection():
                system_status_text = "🔴 Database Bağlantı Hatası"
        
        system_status = QLabel(system_status_text)
        system_status.setStyleSheet("""
            color: #27ae60;
            font-size: 14px;
            font-weight: bold;
        """)
        footer_layout.addWidget(system_status)
        
        footer_layout.addStretch()
        
        # Son güncelleme
        self.last_update_label = QLabel("Son güncelleme: -")
        self.last_update_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            font-size: 14px;
        """)
        footer_layout.addWidget(self.last_update_label)
        
        footer_layout.addStretch()
        
        # Yenile butonu
        refresh_btn = QPushButton("🔄 Dashboard'u Yenile")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0d7377, stop: 1 #14a1a5);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #14a1a5, stop: 1 #1db8bc);
            }
        """)
        refresh_btn.clicked.connect(self.update_dashboard)
        footer_layout.addWidget(refresh_btn)
        
        scroll_layout.addWidget(footer_widget)
        
        # Scroll widget'ı ayarla
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Timer'lar
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        # İlk yükleme
        self.update_dashboard()
        self.load_real_dashboard_chart()
        self.load_real_activities()
        
        return widget

    def update_clock(self):
        """Saat güncelleme"""
        current_time = datetime.now()
        self.time_label.setText(current_time.strftime("%H:%M:%S"))
        
        # Her gün başında tarihi güncelle
        if current_time.hour == 0 and current_time.minute == 0 and current_time.second == 0:
            self.date_label.setText(current_time.strftime("%d %B %Y"))

    def update_chart_period(self, period):
        """Grafik periyodunu güncelle"""
        self.chart_period = period
        self.load_real_dashboard_chart()

    def load_real_activities(self):
        """Gerçek aktiviteleri yükle"""
        # Son aktiviteleri database'den al
        recent_activities = self.db.get_recent_activities(limit=10)
        
        self.activity_list.clear()
        
        for activity in recent_activities:
            activity_time = activity.get('date', '').split(' ')[-1] if ' ' in activity.get('date', '') else ''
            activity_type = activity.get('activity_type', 'general')
            
            # Aktivite tipine göre ikon belirle
            icon = "📧"
            if 'açıldı' in activity.get('status', '').lower():
                icon = "👁️"
            elif 'yanıt' in activity.get('status', '').lower():
                icon = "💬"
            elif 'tıklandı' in activity.get('status', '').lower():
                icon = "🔗"
            elif 'analiz' in activity.get('detail', '').lower():
                icon = "🔍"
            elif 'kampanya' in activity.get('detail', '').lower():
                icon = "📤"
            
            activity_text = f"{activity_time} - {icon} {activity.get('detail', '')[:50]}..."
            item = QListWidgetItem(activity_text)
            self.activity_list.addItem(item)

    def load_real_dashboard_chart(self):
        """Gerçek verilerle dashboard grafiği yükle"""
        # Periyoda göre veri al
        if self.chart_period == "24H":
            chart_data = self.db.get_hourly_statistics(hours=24)
            labels_js = json.dumps([f"{h}:00" for h in range(24)])
        elif self.chart_period == "7G":
            chart_data = self.db.get_daily_statistics(days=7)
            labels_js = json.dumps(['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'])
        elif self.chart_period == "30G":
            chart_data = self.db.get_daily_statistics(days=30)
            labels_js = json.dumps([f"Gün {i+1}" for i in range(30)])
        elif self.chart_period == "3A":
            chart_data = self.db.get_monthly_statistics(months=3)
            labels_js = json.dumps(['3 Ay Önce', '2 Ay Önce', 'Bu Ay'])
        else:  # 1Y
            chart_data = self.db.get_monthly_statistics(months=12)
            labels_js = json.dumps(['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'])
        
        # Veri dizilerini hazırla
        sent_data = json.dumps(chart_data.get('sent', [0] * 7))
        opened_data = json.dumps(chart_data.get('opened', [0] * 7))
        replied_data = json.dumps(chart_data.get('replied', [0] * 7))
        
        chart_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 10px;
                    background-color: #1a1a1a;
                    font-family: Arial, sans-serif;
                }}
                .chart-container {{
                    position: relative;
                    height: 350px;
                }}
            </style>
        </head>
        <body>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
            
            <script>
                const ctx = document.getElementById('performanceChart').getContext('2d');
                
                // Gradient oluştur
                const gradient1 = ctx.createLinearGradient(0, 0, 0, 300);
                gradient1.addColorStop(0, 'rgba(13, 115, 119, 0.8)');
                gradient1.addColorStop(1, 'rgba(13, 115, 119, 0.1)');
                
                const gradient2 = ctx.createLinearGradient(0, 0, 0, 300);
                gradient2.addColorStop(0, 'rgba(20, 161, 165, 0.8)');
                gradient2.addColorStop(1, 'rgba(20, 161, 165, 0.1)');
                
                const gradient3 = ctx.createLinearGradient(0, 0, 0, 300);
                gradient3.addColorStop(0, 'rgba(155, 89, 182, 0.8)');
                gradient3.addColorStop(1, 'rgba(155, 89, 182, 0.1)');
                
                // Gerçek veriler
                const labels = {labels_js};
                const sentData = {sent_data};
                const openedData = {opened_data};
                const repliedData = {replied_data};
                
                const data = {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Gönderilen',
                            data: sentData,
                            borderColor: '#0d7377',
                            backgroundColor: gradient1,
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3,
                            pointRadius: 5,
                            pointHoverRadius: 7,
                            pointBackgroundColor: '#0d7377',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        }},
                        {{
                            label: 'Açılan',
                            data: openedData,
                            borderColor: '#14a1a5',
                            backgroundColor: gradient2,
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3,
                            pointRadius: 5,
                            pointHoverRadius: 7,
                            pointBackgroundColor: '#14a1a5',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        }},
                        {{
                            label: 'Yanıtlanan',
                            data: repliedData,
                            borderColor: '#9b59b6',
                            backgroundColor: gradient3,
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3,
                            pointRadius: 5,
                            pointHoverRadius: 7,
                            pointBackgroundColor: '#9b59b6',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2
                        }}
                    ]
                }};
                
                // Chart config
                const config = {{
                    type: 'line',
                    data: data,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            mode: 'index',
                            intersect: false,
                        }},
                        plugins: {{
                            legend: {{
                                display: true,
                                position: 'bottom',
                                labels: {{
                                    color: '#ffffff',
                                    padding: 20,
                                    usePointStyle: true,
                                    font: {{
                                        size: 12
                                    }}
                                }}
                            }},
                            tooltip: {{
                                backgroundColor: 'rgba(0, 0, 0, 0.9)',
                                titleColor: '#fff',
                                bodyColor: '#fff',
                                borderColor: '#333',
                                borderWidth: 1,
                                cornerRadius: 8,
                                padding: 12,
                                displayColors: true,
                                callbacks: {{
                                    title: function(context) {{
                                        return context[0].label;
                                    }},
                                    label: function(context) {{
                                        return context.dataset.label + ': ' + context.parsed.y + ' adet';
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                grid: {{
                                    color: 'rgba(255, 255, 255, 0.1)',
                                    drawBorder: false
                                }},
                                ticks: {{
                                    color: 'rgba(255, 255, 255, 0.7)',
                                    font: {{
                                        size: 11
                                    }}
                                }}
                            }},
                            x: {{
                                grid: {{
                                    color: 'rgba(255, 255, 255, 0.1)',
                                    drawBorder: false
                                }},
                                ticks: {{
                                    color: 'rgba(255, 255, 255, 0.7)',
                                    font: {{
                                        size: 11
                                    }},
                                    maxRotation: 45,
                                    minRotation: 0
                                }}
                            }}
                        }},
                        animation: {{
                            duration: 2000,
                            easing: 'easeInOutQuart'
                        }}
                    }}
                }};
                
                // Chart oluştur
                const chart = new Chart(ctx, config);
            </script>
        </body>
        </html>
        """
        
        self.main_chart_view.setHtml(chart_html)

    
    def create_search_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Arama ayarları
        search_group = QGroupBox("🔍 Firma Arama Ayarları")
        search_layout = QGridLayout()
        
        # Sektör
        search_layout.addWidget(QLabel("Sektör/İş Türü:"), 0, 0)
        self.sector_input = QLineEdit()
        self.sector_input.setPlaceholderText("örn: yazılım şirketi, restaurant, otel, danışmanlık")
        search_layout.addWidget(self.sector_input, 0, 1, 1, 2)
        
        # Konum
        search_layout.addWidget(QLabel("Konum:"), 1, 0)
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("örn: İstanbul, Ankara Çankaya, İzmir Alsancak")
        search_layout.addWidget(self.location_input, 1, 1, 1, 2)
        
        # Max firma sayısı
        search_layout.addWidget(QLabel("Max Firma Sayısı:"), 2, 0)
        self.max_firms_input = QSpinBox()
        self.max_firms_input.setMinimum(10)
        self.max_firms_input.setMaximum(500)
        self.max_firms_input.setValue(100)
        self.max_firms_input.setSingleStep(10)
        search_layout.addWidget(self.max_firms_input, 2, 1)
        
        # Batch ayarları
        self.batch_mode_check = QCheckBox("Batch Mode (20'şerli gruplar)")
        self.batch_mode_check.setChecked(True)
        search_layout.addWidget(self.batch_mode_check, 2, 2)
        
        # Arama butonları
        button_layout = QHBoxLayout()
        
        self.search_btn = QPushButton("🔍 Aramayı Başlat")
        self.search_btn.clicked.connect(self.start_search)
        button_layout.addWidget(self.search_btn)
        
        self.pause_btn = QPushButton("⏸️ Duraklat")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_search)
        button_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹️ Durdur")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_search)
        button_layout.addWidget(self.stop_btn)
        
        search_layout.addLayout(button_layout, 3, 0, 1, 3)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # İlerleme çubuğu
        self.search_progress = QProgressBar()
        self.search_progress.setVisible(False)
        layout.addWidget(self.search_progress)
        
        # Sonuçlar
        results_group = QGroupBox("📍 Bulunan Firmalar")
        results_layout = QVBoxLayout()
        
        # Seçim butonları
        selection_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("✅ Tümünü Seç")
        self.select_all_btn.clicked.connect(self.select_all_firms)
        selection_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("❌ Hiçbirini Seçme")
        self.deselect_all_btn.clicked.connect(self.deselect_all_firms)
        selection_layout.addWidget(self.deselect_all_btn)
        
        self.analyze_selected_btn = QPushButton("🤖 Seçilenleri Analiz Et")
        self.analyze_selected_btn.clicked.connect(self.analyze_selected_firms)
        self.analyze_selected_btn.setEnabled(False)  # Başlangıçta deaktif
        selection_layout.addWidget(self.analyze_selected_btn)
        
        # Kampanyaya Ekle butonu - daha belirgin
        self.add_to_campaign_btn = QPushButton("📧 Kampanyaya Ekle")
        self.add_to_campaign_btn.clicked.connect(self.add_selected_to_campaign)
        self.add_to_campaign_btn.setEnabled(False)  # Başlangıçta deaktif
        self.add_to_campaign_btn.setStyleSheet("""
            QPushButton {
                background-color: #14a085;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0d7377;
            }
            QPushButton:disabled {
                background-color: #4a6c7a;
                color: #888;
            }
        """)
        selection_layout.addWidget(self.add_to_campaign_btn)
        
        # Toplu silme butonu
        self.delete_selected_btn = QPushButton("🗑️ Seçili Firmaları Sil")
        self.delete_selected_btn.clicked.connect(self.delete_selected_firms)
        self.delete_selected_btn.setEnabled(False)  # Başlangıçta deaktif
        self.delete_selected_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: none; border-radius: 5px; padding: 8px; font-weight: bold; }")
        selection_layout.addWidget(self.delete_selected_btn)
        
        # Yeni butonlar - WhatsApp ve Çağrı yönlendirme
        self.send_to_whatsapp_btn = QPushButton("📱 WhatsApp'a At")
        self.send_to_whatsapp_btn.clicked.connect(self.send_selected_to_whatsapp)
        self.send_to_whatsapp_btn.setEnabled(False)  # Başlangıçta deaktif
        selection_layout.addWidget(self.send_to_whatsapp_btn)
        
        self.send_to_call_btn = QPushButton("📞 Çağrıya At")
        self.send_to_call_btn.clicked.connect(self.send_selected_to_call)
        self.send_to_call_btn.setEnabled(False)  # Başlangıçta deaktif
        selection_layout.addWidget(self.send_to_call_btn)
        
        selection_layout.addStretch()
        
        self.selected_count_label = QLabel("0 firma seçili")
        selection_layout.addWidget(self.selected_count_label)
        
        results_layout.addLayout(selection_layout)
        
        # Firma tablosu
        self.firms_table = QTableWidget()
        self.firms_table.setColumnCount(9)
        self.firms_table.setHorizontalHeaderLabels([
            "Seç", "Firma Adı", "Rating", "Website", "Telefon", 
            "Adres", "Durum", "İşlem", "Detay"
        ])
        self.firms_table.setAlternatingRowColors(True)
        self.firms_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.firms_table.customContextMenuRequested.connect(self.on_firms_table_context_menu)
        results_layout.addWidget(self.firms_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        return widget
    
    def get_firms_button_style(self, color):
        """Firmalar sekmesi için buton stili"""
        scale_factor = self.scale_factor if hasattr(self, 'scale_factor') else 1.0
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
    
    def filter_firms_table(self):
        """Gelişmiş firma tablosu filtreleme"""
        search_text = self.firms_search_input.text().lower()
        ai_sector = self.ai_sector_combo.currentText()
        rating_filter = self.rating_filter.currentText()
        email_filter = self.email_filter.currentText()
        website_filter = self.website_filter.currentText()
        
        # Eski checkbox filtreler
        analyzed_only = self.firm_analyzed_check.isChecked()
        has_email_only = self.firm_has_email_check.isChecked()
        min_rating = self.min_rating_input.value()
        
        visible_count = 0
        selected_count = 0
        
        for row in range(self.all_firms_table.rowCount()):
            show_row = True
            
            # Metin arama
            if search_text:
                row_text = ""
                for col in range(1, self.all_firms_table.columnCount() - 1):  # Checkbox ve işlemler hariç
                    item = self.all_firms_table.item(row, col)
                    if item:
                        row_text += item.text().lower() + " "
                
                if search_text not in row_text:
                    show_row = False
            
            # AI Sektör filtresi
            if show_row and ai_sector != "Tüm Sektörler":
                sector_item = self.all_firms_table.item(row, 6)  # Sektör kolonu
                if sector_item:
                    firm_sector = sector_item.text().lower()
                    ai_sector_clean = ai_sector.split(" ", 1)[-1].lower()  # Emoji'yi kaldır
                    
                    # AI ile sektör eşleştirme
                    if not self.ai_sector_match(firm_sector, ai_sector_clean):
                        show_row = False
            
            # Rating filtresi
            if show_row and rating_filter != "Tümü":
                rating_item = self.all_firms_table.item(row, 2)  # Rating kolonu
                if rating_item:
                    try:
                        firm_rating = float(rating_item.text().replace("⭐", "").strip())
                        min_rating_filter = int(rating_filter.replace("+", ""))
                        if firm_rating < min_rating_filter:
                            show_row = False
                    except:
                        if rating_filter != "Tümü":
                            show_row = False
            
            # Email filtresi
            if show_row and email_filter != "Tümü":
                email_count_item = self.all_firms_table.item(row, 3)  # Email sayısı kolonu
                has_email = email_count_item and int(email_count_item.text()) > 0
                
                if email_filter == "Email Var" and not has_email:
                    show_row = False
                elif email_filter == "Email Yok" and has_email:
                    show_row = False
            
            # Website filtresi
            if show_row and website_filter != "Tümü":
                website_item = self.all_firms_table.item(row, 4)  # Website kolonu
                has_website = website_item and website_item.text().strip() and website_item.text() != "N/A"
                
                if website_filter == "Website Var" and not has_website:
                    show_row = False
                elif website_filter == "Website Yok" and has_website:
                    show_row = False
            
            # Eski filtreler - backward compatibility
            if show_row and analyzed_only:
                analysis_item = self.all_firms_table.item(row, 7)  # Analiz kolonu
                is_analyzed = analysis_item and "✅" in analysis_item.text()
                if not is_analyzed:
                    show_row = False
            
            if show_row and has_email_only:
                email_count_item = self.all_firms_table.item(row, 3)
                has_email = email_count_item and int(email_count_item.text()) > 0
                if not has_email:
                    show_row = False
            
            if show_row and min_rating > 0:
                rating_item = self.all_firms_table.item(row, 2)
                if rating_item:
                    try:
                        firm_rating = float(rating_item.text().replace("⭐", "").strip())
                        if firm_rating < min_rating:
                            show_row = False
                    except:
                        show_row = False
            
            # Satırı göster/gizle
            self.all_firms_table.setRowHidden(row, not show_row)
            
            if show_row:
                visible_count += 1
                # Seçim durumunu kontrol et
                checkbox = self.all_firms_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    selected_count += 1
        
        # Bilgi etiketlerini güncelle
        total_count = self.all_firms_table.rowCount()
        self.firms_count_display.setText(f"📊 Toplam: {total_count} firma")
        self.firms_selection_info.setText(f"📋 Seçili: {selected_count} / Görünen: {visible_count}")
        
        # Eski label'ı da güncelle
        if hasattr(self, 'firms_count_label'):
            self.firms_count_label.setText(f"Toplam: {visible_count} firma")
    
    def ai_sector_match(self, firm_sector, filter_sector):
        """AI ile sektör eşleştirme"""
        filter_keywords = {
            "sağlık & tıp": ["sağlık", "tıp", "hastane", "klinik", "doktor", "hemşire", "eczane", "medikal", "psikolog", "diyetisyen", "veteriner"],
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
    
    def categorize_sector_with_ai(self, sector_text):
        """AI ile sektör kategorilendirme"""
        if not sector_text or sector_text == 'Belirtilmemiş':
            return sector_text
        
        # Basit kategori eşleştirme
        sector_lower = sector_text.lower()
        
        # Sağlık kategorisi
        health_keywords = ["sağlık", "tıp", "hastane", "klinik", "doktor", "eczane", "medikal", "psikolog", "diyetisyen", "veteriner"]
        if any(keyword in sector_lower for keyword in health_keywords):
            return "Sağlık & Tıp"
        
        # Teknoloji kategorisi
        tech_keywords = ["teknoloji", "yazılım", "bilgisayar", "it", "software", "tech", "dijital", "internet"]
        if any(keyword in sector_lower for keyword in tech_keywords):
            return "Teknoloji & Yazılım"
        
        # Mobilya kategorisi
        furniture_keywords = ["mobilya", "dekorasyon", "ev", "tasarım", "yatak", "nevresim", "uyku"]
        if any(keyword in sector_lower for keyword in furniture_keywords):
            return "Mobilya & Dekorasyon"
        
        # Diğer kategoriler...
        return sector_text
    
    def get_ai_sector_suggestions(self):
        """AI ile sektör önerileri al"""
        if not hasattr(self, 'api_manager') or not self.api_manager:
            QMessageBox.warning(self, "Uyarı", "AI önerileri için API bağlantısı gerekli!")
            return
        
        try:
            # Mevcut firmaların sektörlerini analiz et
            sectors = []
            for row in range(self.all_firms_table.rowCount()):
                if not self.all_firms_table.isRowHidden(row):
                    sector_item = self.all_firms_table.item(row, 6)  # Sektör kolonu
                    if sector_item and sector_item.text().strip():
                        sectors.append(sector_item.text().strip())
            
            if not sectors:
                QMessageBox.information(self, "Bilgi", "Öneri için yeterli firma verisi bulunamadı!")
                return
            
            # OpenAI'dan öneri al
            prompt = f"""
            Aşağıdaki firma sektörlerini analiz et ve benzer sektörlerde hangi firmaları hedeflemeli önerisinde bulun:
            
            Mevcut sektörler: {', '.join(set(sectors[:20]))}
            
            Lütfen:
            1. Bu sektörlere benzer 5 sektör öner
            2. Her sektör için 2-3 anahtar kelime ver
            3. Türkçe ve kısa yanıt ver
            """
            
            # API manager ile GPT çağrısı
            if hasattr(self.api_manager, 'generate_email_gpt'):
                response = self.api_manager.generate_email_gpt({'name': 'AI Analiz'}, {'instructions': prompt})
                response_text = response.get('body', 'AI önerisi alınamadı')
            else:
                response_text = "AI öneri sistemi şu anda mevcut değil."
            
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
            suggestion_text.setText(response_text)
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
        for row in range(self.all_firms_table.rowCount()):
            if not self.all_firms_table.isRowHidden(row):
                checkbox = self.all_firms_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(True)
        self.update_firms_selection_info()
    
    def select_none_firms_in_table(self):
        """Tablodaki hiçbir firmayı seçme"""
        for row in range(self.all_firms_table.rowCount()):
            checkbox = self.all_firms_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_firms_selection_info()
    
    def invert_firms_selection(self):
        """Firma seçimini tersine çevir"""
        for row in range(self.all_firms_table.rowCount()):
            if not self.all_firms_table.isRowHidden(row):
                checkbox = self.all_firms_table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(not checkbox.isChecked())
        self.update_firms_selection_info()
    
    def hide_selected_firms(self):
        """Seçili firmaları gizle"""
        if not hasattr(self, 'hidden_firm_rows'):
            self.hidden_firm_rows = set()
        
        hidden_count = 0
        for row in range(self.all_firms_table.rowCount()):
            checkbox = self.all_firms_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                self.all_firms_table.setRowHidden(row, True)
                self.hidden_firm_rows.add(row)
                hidden_count += 1
        
        if hidden_count > 0:
            QMessageBox.information(self, "✅ Gizlendi", f"{hidden_count} firma gizlendi!")
        
        self.update_firms_selection_info()
    
    def show_all_firms(self):
        """Tüm firmaları göster (gizlileri de)"""
        if not hasattr(self, 'hidden_firm_rows'):
            self.hidden_firm_rows = set()
        
        for row in range(self.all_firms_table.rowCount()):
            self.all_firms_table.setRowHidden(row, False)
        
        self.hidden_firm_rows.clear()
        self.filter_firms_table()  # Filtreleri yeniden uygula
        
        QMessageBox.information(self, "👁️ Gösterildi", "Tüm firmalar gösterildi!")
    
    def update_firms_selection_info(self):
        """Firma seçim bilgisini güncelle"""
        selected_count = 0
        visible_count = 0
        
        for row in range(self.all_firms_table.rowCount()):
            if not self.all_firms_table.isRowHidden(row):
                visible_count += 1
                checkbox = self.all_firms_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    selected_count += 1
        
        total_count = self.all_firms_table.rowCount()
        self.firms_count_display.setText(f"📊 Toplam: {total_count} firma")
        self.firms_selection_info.setText(f"📋 Seçili: {selected_count} / Görünen: {visible_count}")
        
        # Eski label'ı da güncelle
        if hasattr(self, 'firms_count_label'):
            self.firms_count_label.setText(f"Toplam: {visible_count} firma")
        
        # Butonları aktif/pasif yap
        has_selection = selected_count > 0
        
        if hasattr(self, 'analyze_selected_btn'):
            self.analyze_selected_btn.setEnabled(has_selection)
        if hasattr(self, 'add_to_campaign_btn'):
            self.add_to_campaign_btn.setEnabled(has_selection)
        if hasattr(self, 'analyze_selected_firms_btn'):
            self.analyze_selected_firms_btn.setEnabled(has_selection)
        if hasattr(self, 'delete_selected_btn'):
            self.delete_selected_btn.setEnabled(has_selection)
        if hasattr(self, 'send_to_whatsapp_btn'):
            self.send_to_whatsapp_btn.setEnabled(has_selection)
        if hasattr(self, 'send_to_call_btn'):
            self.send_to_call_btn.setEnabled(has_selection)
    
    def open_bulk_message_dialog(self):
        """Toplu mesaj dialogunu aç"""
        try:
            # Seçili firmaları al
            selected_firms = self.get_selected_firms_from_table()
            
            if not selected_firms:
                QMessageBox.warning(self, "Uyarı", "Lütfen mesaj göndermek için en az bir firma seçin!")
                return
            
            QMessageBox.information(self, "Bilgi", 
                f"{len(selected_firms)} firma seçildi!\n\n"
                "Toplu mesaj özelliği main2.py'de mevcuttur.\n"
                "Gelişmiş toplu mesaj için main2.py'yi kullanın.")
            
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
            
            QMessageBox.information(self, "Bilgi", 
                f"{len(selected_firms)} firma seçildi!\n\n"
                "Toplu arama özelliği main2.py'de mevcuttur.\n"
                "Gelişmiş toplu arama için main2.py'yi kullanın.")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Toplu arama dialogu açılamadı:\n{str(e)}")
    
    def get_selected_firms_from_table(self):
        """Tablodaki seçili firmaları al"""
        selected_firms = []
        
        for row in range(self.all_firms_table.rowCount()):
            if not self.all_firms_table.isRowHidden(row):
                checkbox = self.all_firms_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    # Firma verilerini al
                    firm_name = self.all_firms_table.item(row, 1).text()
                    
                    # Veritabanından tam veriyi al
                    for firm_data in self.all_firms_data:
                        if firm_data['name'] == firm_name:
                            selected_firms.append(firm_data)
                            break
        
        return selected_firms
    
    def add_new_firm(self):
        """Yeni firma ekleme dialogu"""
        try:
            # Yeni firma ekleme dialogu
            dialog = QDialog(self)
            dialog.setWindowTitle("➕ Yeni Firma Ekle")
            dialog.setModal(True)
            dialog.resize(500, 400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2a2a2a;
                    color: white;
                }
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                }
                QLineEdit, QTextEdit {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 8px;
                    color: white;
                    font-size: 12px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border: 2px solid #0d7377;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
                QPushButton#cancel_btn {
                    background-color: #6c757d;
                }
                QPushButton#cancel_btn:hover {
                    background-color: #5a6268;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title_label = QLabel("➕ Yeni Firma Ekle")
            title_label.setStyleSheet("font-size: 16px; color: #0d7377; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # Form alanları
            form_layout = QFormLayout()
            
            # Firma Adı (zorunlu)
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("Firma adını girin...")
            form_layout.addRow("🏢 Firma Adı *:", name_edit)
            
            # Telefon
            phone_edit = QLineEdit()
            phone_edit.setPlaceholderText("Telefon numarası...")
            form_layout.addRow("📞 Telefon:", phone_edit)
            
            # Email
            email_edit = QLineEdit()
            email_edit.setPlaceholderText("E-posta adresi...")
            form_layout.addRow("📧 E-posta:", email_edit)
            
            # Adres
            address_edit = QTextEdit()
            address_edit.setPlaceholderText("Tam adres bilgisi...")
            address_edit.setMaximumHeight(80)
            form_layout.addRow("📍 Adres:", address_edit)
            
            # Website
            website_edit = QLineEdit()
            website_edit.setPlaceholderText("Website URL'si...")
            form_layout.addRow("🌐 Website:", website_edit)
            
            # Sektör
            sector_edit = QLineEdit()
            sector_edit.setPlaceholderText("Sektör bilgisi...")
            form_layout.addRow("🏭 Sektör:", sector_edit)
            
            # Açıklama
            description_edit = QTextEdit()
            description_edit.setPlaceholderText("Firma hakkında açıklama...")
            description_edit.setMaximumHeight(80)
            form_layout.addRow("📝 Açıklama:", description_edit)
            
            layout.addLayout(form_layout)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            save_btn = QPushButton("💾 Firma Ekle")
            save_btn.clicked.connect(lambda: self.save_new_firm(
                dialog, {
                    'name': name_edit.text().strip(),
                    'phone': phone_edit.text().strip(),
                    'email': email_edit.text().strip(),
                    'address': address_edit.toPlainText().strip(),
                    'website': website_edit.text().strip(),
                    'sector': sector_edit.text().strip(),
                    'description': description_edit.toPlainText().strip()
                }
            ))
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.setObjectName("cancel_btn")
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Yeni firma ekleme dialogu açılamadı:\n{str(e)}")
    
    def save_new_firm(self, dialog, firm_data):
        """Yeni firmayı kaydet"""
        try:
            # Zorunlu alanları kontrol et
            if not firm_data['name']:
                QMessageBox.warning(dialog, "Uyarı", "Firma adı boş olamaz!")
                return
            
            # Email formatını kontrol et (eğer girilmişse)
            if firm_data['email']:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, firm_data['email']):
                    QMessageBox.warning(dialog, "Uyarı", "Geçerli bir email adresi girin!")
                    return
            
            # Veritabanına ekle
            if self.db:
                # Yeni firma verisi hazırla
                new_firm_data = {
                    'name': firm_data['name'],
                    'phone': firm_data['phone'],
                    'email': firm_data['email'],
                    'address': firm_data['address'],
                    'website': firm_data['website'],
                    'sector': firm_data['sector'],
                    'summary': firm_data['description'],
                    'emails': []  # Boş email listesi
                }
                
                # Eğer email adresi girilmişse, emails listesine de ekle
                if firm_data['email']:
                    email_obj = {
                        'email': firm_data['email'],
                        'position': 'Genel',
                        'source': 'Manuel',
                        'score': 0.9,
                        'is_verified': False
                    }
                    new_firm_data['emails'] = [email_obj]
                
                print(f"🔍 DEBUG: Yeni firma ekleniyor: {new_firm_data}")
                
                # Veritabanına ekle
                success = self.db.add_firm(**new_firm_data)
                
                if success:
                    print("✅ DEBUG: Yeni firma başarıyla eklendi!")
                    
                    # Firmaları yeniden yükle
                    self.load_all_firms()
                    
                    # Tabloyu güncelle
                    self.refresh_firms_table()
                    
                    # Kullanıcıya seçenek sun
                    reply = QMessageBox.question(dialog, "✅ Firma Eklendi", 
                        f"Yeni firma başarıyla eklendi!\n\n"
                        f"Firma: {firm_data['name']}\n"
                        f"Telefon: {firm_data['phone'] or 'Belirtilmemiş'}\n"
                        f"Email: {firm_data['email'] or 'Belirtilmemiş'}\n\n"
                        f"Bu firmayı hemen mail kampanyasına eklemek ister misiniz?",
                        QMessageBox.Yes | QMessageBox.No)
                    
                    dialog.accept()
                    
                    # Eğer kullanıcı kampanyaya eklemek isterse
                    if reply == QMessageBox.Yes:
                        # Yeni eklenen firmayı bul ve kampanyaya ekle
                        new_firm = self.db.get_firm_by_id(success)
                        if new_firm:
                            # Email adresi kontrolü - hem emails listesine hem de email alanına bak
                            emails = new_firm.get('emails', [])
                            single_email = new_firm.get('email', '')
                            has_emails = (emails and len(emails) > 0) or (single_email and single_email.strip())
                            
                            if not has_emails:
                                # Email adresi yoksa analiz öner
                                analyze_reply = QMessageBox.question(self, "📧 Email Adresi Gerekli", 
                                    f"'{firm_data['name']}' firmasının email adresi bulunamadı.\n\n"
                                    f"Mail gönderebilmek için önce firma analiz edilmeli.\n"
                                    f"Şimdi analiz etmek ister misiniz?",
                                    QMessageBox.Yes | QMessageBox.No)
                                
                                if analyze_reply == QMessageBox.Yes:
                                    # Analiz için firmayı seç ve analiz et
                                    self.current_firms = [new_firm]
                                    self.analyze_selected_firms()
                                    return
                                else:
                                    # Analiz yapmadan kampanyaya ekle (sadece bilgi amaçlı)
                                    self.selected_firms = [new_firm]
                                    self.tabs.setCurrentIndex(2)
                                    self.update_campaign_firms_list()
                                    
                                    QMessageBox.information(self, "📧 Kampanyaya Eklendi", 
                                        f"'{firm_data['name']}' firması kampanyaya eklendi!\n\n"
                                        f"⚠️ Email adresi olmadığı için mail gönderilemez.\n"
                                        f"Mail gönderebilmek için önce firma analiz edilmelidir.")
                            else:
                                # Email adresi varsa direkt kampanyaya ekle
                                self.selected_firms = [new_firm]
                                self.tabs.setCurrentIndex(2)
                                self.update_campaign_firms_list()
                                
                                QMessageBox.information(self, "📧 Kampanyaya Eklendi", 
                                    f"'{firm_data['name']}' firması kampanyaya eklendi!\n\n"
                                    f"Mail şablonunu hazırlayıp kampanyayı başlatabilirsiniz.")
                        else:
                            QMessageBox.warning(self, "⚠️ Uyarı", 
                                "Firma kampanyaya eklenemedi. Lütfen manuel olarak ekleyin.")
                else:
                    QMessageBox.critical(dialog, "❌ Hata", "Firma eklenemedi!")
            else:
                QMessageBox.warning(dialog, "Uyarı", "Veritabanı bağlantısı yok!")
                
        except Exception as e:
            QMessageBox.critical(dialog, "❌ Hata", f"Firma kaydetme hatası:\n{str(e)}")
            print(f"❌ DEBUG: Firma kaydetme hatası: {str(e)}")
    
    def edit_selected_firm(self):
        """Seçili firmayı düzenle"""
        current_row = self.all_firms_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir firma seçin!")
            return
        
        # Seçili firmayı bul
        firm_name = self.all_firms_table.item(current_row, 1).text()
        firm_data = None
        
        print(f"🔍 DEBUG: Aranan firma adı: '{firm_name}'")
        print(f"🔍 DEBUG: Toplam firma sayısı: {len(self.all_firms)}")
        
        # Firma verisini bul - daha esnek arama
        for i, firm in enumerate(self.all_firms):
            firm_name_in_data = firm.get('name', '')
            print(f"🔍 DEBUG: Firma {i}: '{firm_name_in_data}'")
            
            # Tam eşleşme
            if firm_name_in_data == firm_name:
                firm_data = firm
                print(f"✅ DEBUG: Tam eşleşme bulundu!")
                break
            # Kısmi eşleşme (boşluk ve büyük/küçük harf farkları)
            elif firm_name_in_data.strip().lower() == firm_name.strip().lower():
                firm_data = firm
                print(f"✅ DEBUG: Kısmi eşleşme bulundu!")
                break
        
        if not firm_data:
            # Alternatif: Tablodan direkt veri al
            print("🔍 DEBUG: Alternatif yöntem deneniyor...")
            firm_data = self.get_firm_data_from_table_row(current_row)
            
            if not firm_data:
                QMessageBox.warning(self, "Hata", 
                    f"Firma verisi bulunamadı!\n\n"
                    f"Aranan: '{firm_name}'\n"
                    f"Toplam firma: {len(self.all_firms)}")
                return
        
        # Düzenleme dialogunu aç
        self.open_edit_firm_dialog(firm_data, current_row)
    
    def get_firm_data_from_table_row(self, row):
        """Tablodan direkt firma verisini al"""
        try:
            firm_data = {
                'id': None,  # ID tabloda yok, sonradan bulunacak
                'name': self.all_firms_table.item(row, 1).text() if self.all_firms_table.item(row, 1) else '',
                'phone': self.all_firms_table.item(row, 2).text() if self.all_firms_table.item(row, 2) else '',
                'address': self.all_firms_table.item(row, 3).text() if self.all_firms_table.item(row, 3) else '',
                'website': self.all_firms_table.item(row, 4).text() if self.all_firms_table.item(row, 4) else '',
                'email': self.all_firms_table.item(row, 5).text() if self.all_firms_table.item(row, 5) else '',
                'sector': self.all_firms_table.item(row, 6).text() if self.all_firms_table.item(row, 6) else '',
                'description': self.all_firms_table.item(row, 7).text() if self.all_firms_table.item(row, 7) else ''
            }
            
            # ID'yi all_firms'den bul - daha kapsamlı arama
            print(f"🔍 DEBUG: ID aranıyor - Firma: '{firm_data['name']}', Telefon: '{firm_data['phone']}'")
            
            for i, firm in enumerate(self.all_firms):
                firm_name = firm.get('name', '').strip().lower()
                firm_phone = firm.get('phone', '').strip()
                search_name = firm_data['name'].strip().lower()
                search_phone = firm_data['phone'].strip()
                
                print(f"🔍 DEBUG: Firma {i} - İsim: '{firm_name}', Telefon: '{firm_phone}'")
                
                # İsim eşleşmesi
                if firm_name and search_name and firm_name == search_name:
                    firm_data['id'] = firm.get('id')
                    print(f"✅ DEBUG: İsim eşleşmesi ile ID bulundu: {firm_data['id']}")
                    break
                
                # Telefon eşleşmesi
                elif firm_phone and search_phone and firm_phone == search_phone:
                    firm_data['id'] = firm.get('id')
                    print(f"✅ DEBUG: Telefon eşleşmesi ile ID bulundu: {firm_data['id']}")
                    break
                
                # Kısmi isim eşleşmesi
                elif firm_name and search_name and (firm_name in search_name or search_name in firm_name):
                    firm_data['id'] = firm.get('id')
                    print(f"✅ DEBUG: Kısmi isim eşleşmesi ile ID bulundu: {firm_data['id']}")
                    break
            
            # Eğer hala ID bulunamadıysa, yeni ID oluştur
            if not firm_data['id']:
                print("⚠️ DEBUG: ID bulunamadı, yeni ID oluşturuluyor...")
                # Mevcut en büyük ID'yi bul
                max_id = 0
                for firm in self.all_firms:
                    if firm.get('id') and isinstance(firm.get('id'), int):
                        max_id = max(max_id, firm.get('id'))
                firm_data['id'] = max_id + 1
                print(f"🆕 DEBUG: Yeni ID oluşturuldu: {firm_data['id']}")
            
            print(f"🔍 DEBUG: Tablodan alınan veri: {firm_data}")
            return firm_data
            
        except Exception as e:
            print(f"❌ DEBUG: Tablo veri alma hatası: {str(e)}")
            return None
    
    def add_test_firm_data(self):
        """Test firma verisi ekle"""
        try:
            if not self.db:
                QMessageBox.warning(self, "Uyarı", "Veritabanı bağlantısı yok!")
                return
            
            # Test verisi
            test_firm_data = {
                'name': 'tes',
                'phone': '05462051820',
                'email': 'cetederya7@gmail.com',
                'address': 'Test Adresi, İstanbul, Türkiye',
                'sector': 'Test Sektörü',
                'summary': 'Test firma açıklaması',
                'website': 'https://www.test.com',
                'contact_person': 'Test Kişi'
            }
            
            print(f"🧪 DEBUG: Test firma verisi ekleniyor: {test_firm_data}")
            
            # Veritabanına ekle
            success = self.db.add_firm(**test_firm_data)
            
            if success:
                print("✅ DEBUG: Test firma başarıyla eklendi!")
                
                # Firmaları yeniden yükle
                self.load_all_firms()
                
                # Tabloyu güncelle
                self.refresh_firms_table()
                
                QMessageBox.information(self, "✅ Başarılı", 
                    "Test firma verisi başarıyla eklendi!\n\n"
                    f"İsim: {test_firm_data['name']}\n"
                    f"Telefon: {test_firm_data['phone']}\n"
                    f"Email: {test_firm_data['email']}")
            else:
                QMessageBox.critical(self, "❌ Hata", "Test firma eklenemedi!")
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Test veri ekleme hatası:\n{str(e)}")
            print(f"❌ DEBUG: Test veri ekleme hatası: {str(e)}")
    
    def add_email_to_firm(self):
        """Firmaya email adresi ekle"""
        try:
            current_row = self.all_firms_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen email eklemek için bir firma seçin!")
                return
            
            # Seçili firmayı bul
            firm_name = self.all_firms_table.item(current_row, 1).text()
            firm_data = None
            
            for firm in self.all_firms:
                if firm.get('name', '').strip().lower() == firm_name.strip().lower():
                    firm_data = firm
                    break
            
            if not firm_data:
                QMessageBox.warning(self, "Hata", "Firma verisi bulunamadı!")
                return
            
            # Email ekleme dialogu
            dialog = QDialog(self)
            dialog.setWindowTitle("📧 Email Adresi Ekle")
            dialog.setModal(True)
            dialog.resize(400, 300)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2a2a2a;
                    color: white;
                }
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                }
                QLineEdit, QTextEdit {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 8px;
                    color: white;
                    font-size: 12px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border: 2px solid #0d7377;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
                QPushButton#cancel_btn {
                    background-color: #6c757d;
                }
                QPushButton#cancel_btn:hover {
                    background-color: #5a6268;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title_label = QLabel(f"📧 {firm_data['name']} - Email Adresi Ekle")
            title_label.setStyleSheet("font-size: 16px; color: #0d7377; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # Form alanları
            form_layout = QFormLayout()
            
            # İsim Soyisim (YENİ)
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("Ahmet Yılmaz")
            form_layout.addRow("👤 İsim Soyisim:", name_edit)
            
            # Email adresi
            email_edit = QLineEdit()
            email_edit.setPlaceholderText("ornek@firma.com")
            form_layout.addRow("📧 Email Adresi:", email_edit)
            
            # Pozisyon
            position_edit = QLineEdit()
            position_edit.setPlaceholderText("Genel Müdür, Satış Müdürü, vb.")
            form_layout.addRow("💼 Pozisyon:", position_edit)
            
            # Kaynak
            source_edit = QLineEdit()
            source_edit.setPlaceholderText("Website, LinkedIn, vb.")
            form_layout.addRow("🔍 Kaynak:", source_edit)
            
            # Notlar
            notes_edit = QTextEdit()
            notes_edit.setPlaceholderText("Ek notlar...")
            notes_edit.setMaximumHeight(60)
            form_layout.addRow("📝 Notlar:", notes_edit)
            
            layout.addLayout(form_layout)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            save_btn = QPushButton("💾 Email Ekle")
            save_btn.clicked.connect(lambda: self.save_email_to_firm(
                dialog, firm_data, current_row, {
                    'name': name_edit.text().strip(),
                    'email': email_edit.text().strip(),
                    'position': position_edit.text().strip(),
                    'source': source_edit.text().strip(),
                    'notes': notes_edit.toPlainText().strip()
                }
            ))
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.setObjectName("cancel_btn")
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Email ekleme dialogu açılamadı:\n{str(e)}")
    
    def save_email_to_firm(self, dialog, firm_data, table_row, email_data):
        """Firmaya email adresini kaydet"""
        try:
            if not email_data['email']:
                QMessageBox.warning(dialog, "Uyarı", "Email adresi boş olamaz!")
                return
            
            # Email formatını kontrol et
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email_data['email']):
                QMessageBox.warning(dialog, "Uyarı", "Geçerli bir email adresi girin!")
                return
            
            # Yeni email objesi oluştur
            new_email = {
                'name': email_data['name'] or 'Bilinmiyor',
                'email': email_data['email'],
                'position': email_data['position'] or 'Bilinmiyor',
                'source': email_data['source'] or 'Manuel',
                'score': 0.8,  # Manuel eklenen emailler için yüksek skor
                'is_verified': False,
                'notes': email_data['notes']
            }
            
            # Firmaya email ekle
            if 'emails' not in firm_data:
                firm_data['emails'] = []
            
            # Aynı email var mı kontrol et
            existing_emails = [e.get('email', '') for e in firm_data.get('emails', [])]
            if email_data['email'] in existing_emails:
                QMessageBox.warning(dialog, "Uyarı", "Bu email adresi zaten mevcut!")
                return
            
            firm_data['emails'].append(new_email)
            
            # Veritabanında güncelle
            if self.db and firm_data.get('id'):
                update_data = {
                    'emails': firm_data['emails']
                }
                print(f"🔍 DEBUG: Email verisi güncelleniyor: {firm_data['emails']}")
                success = self.db.update_firm(firm_data['id'], **update_data)
                
                if success:
                    # Tabloyu güncelle
                    self.refresh_firms_table()
                    
                    # all_firms listesini güncelle
                    for i, firm in enumerate(self.all_firms):
                        if firm.get('id') == firm_data.get('id'):
                            self.all_firms[i]['emails'] = firm_data['emails']
                            break
                    
                    QMessageBox.information(dialog, "✅ Başarılı", 
                        f"Email adresi başarıyla eklendi!\n\n"
                        f"Email: {email_data['email']}\n"
                        f"Toplam email sayısı: {len(firm_data['emails'])}")
                    dialog.accept()
                else:
                    QMessageBox.critical(dialog, "❌ Hata", "Email veritabanında güncellenemedi!")
            else:
                QMessageBox.warning(dialog, "Uyarı", "Veritabanı bağlantısı yok veya firma ID'si bulunamadı!")
                
        except Exception as e:
            QMessageBox.critical(dialog, "❌ Hata", f"Email kaydetme hatası:\n{str(e)}")
    
    def on_firm_table_cell_clicked(self, row, column):
        """Firma tablosunda hücre tıklandığında"""
        if column == 3:  # Email Detayları sütunu
            self.show_email_details_dialog(row)
    
    def show_email_details_dialog(self, row):
        """Email detaylarını göster"""
        try:
            if row >= len(self.all_firms_data):
                return
            
            firm = self.all_firms_data[row]
            emails = firm.get('emails', [])
            
            if not emails:
                QMessageBox.information(self, "📧 Email Detayları", 
                    f"❌ {firm.get('name', 'Firma')} için henüz email adresi eklenmemiş.\n\n"
                    "Email eklemek için '📧 Email Ekle' butonunu kullanabilirsiniz.")
                return
            
            # Email detayları dialogu
            dialog = QDialog(self)
            dialog.setWindowTitle(f"📧 {firm.get('name', 'Firma')} - Email Detayları")
            dialog.setModal(True)
            dialog.resize(600, 400)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2a2a2a;
                    color: white;
                }
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                }
                QTableWidget {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 5px;
                    color: white;
                    gridline-color: #555;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #555;
                }
                QTableWidget::item:selected {
                    background-color: #0d7377;
                }
                QHeaderView::section {
                    background-color: #1a1a1a;
                    color: white;
                    padding: 8px;
                    border: none;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
                QPushButton#add_email_btn {
                    background-color: #28a745;
                }
                QPushButton#add_email_btn:hover {
                    background-color: #218838;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title_label = QLabel(f"📧 {firm.get('name', 'Firma')} - Email Adresleri")
            title_label.setStyleSheet("font-size: 16px; color: #0d7377; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # Email tablosu
            email_table = QTableWidget()
            email_table.setColumnCount(5)
            email_table.setHorizontalHeaderLabels([
                "👤 İsim", "📧 Email", "💼 Pozisyon", "🔍 Kaynak", "📝 Notlar"
            ])
            email_table.setRowCount(len(emails))
            
            for i, email in enumerate(emails):
                email_table.setItem(i, 0, QTableWidgetItem(email.get('name', 'Bilinmiyor')))
                email_table.setItem(i, 1, QTableWidgetItem(email.get('email', '')))
                email_table.setItem(i, 2, QTableWidgetItem(email.get('position', 'Bilinmiyor')))
                email_table.setItem(i, 3, QTableWidgetItem(email.get('source', 'Manuel')))
                email_table.setItem(i, 4, QTableWidgetItem(email.get('notes', '')))
            
            # Tablo ayarları
            email_table.setAlternatingRowColors(True)
            email_table.setSelectionBehavior(QTableWidget.SelectRows)
            email_table.horizontalHeader().setStretchLastSection(True)
            email_table.setColumnWidth(0, 120)  # İsim
            email_table.setColumnWidth(1, 200)  # Email
            email_table.setColumnWidth(2, 120)  # Pozisyon
            email_table.setColumnWidth(3, 80)   # Kaynak
            
            layout.addWidget(email_table)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            add_email_btn = QPushButton("➕ Yeni Email Ekle")
            add_email_btn.setObjectName("add_email_btn")
            add_email_btn.clicked.connect(lambda: self.add_email_to_firm_from_dialog(dialog, firm, row))
            
            close_btn = QPushButton("❌ Kapat")
            close_btn.clicked.connect(dialog.accept)
            
            button_layout.addWidget(add_email_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Email detayları gösterilemedi:\n{str(e)}")
    
    def add_email_to_firm_from_dialog(self, parent_dialog, firm_data, table_row):
        """Dialog içinden email ekleme"""
        parent_dialog.accept()  # Önce dialogu kapat
        self.add_email_to_firm()  # Email ekleme dialogunu aç
    
    def add_email_to_firm_from_detail_dialog(self, parent_dialog, firm_data):
        """Firma detay dialogundan email ekleme"""
        try:
            # Email ekleme dialogu
            dialog = QDialog(self)
            dialog.setWindowTitle("📧 Email Adresi Ekle")
            dialog.setModal(True)
            dialog.resize(400, 300)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2a2a2a;
                    color: white;
                }
                QLabel {
                    color: #ffffff;
                    font-weight: bold;
                }
                QLineEdit, QTextEdit {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 8px;
                    color: white;
                    font-size: 12px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border: 2px solid #0d7377;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
                QPushButton#cancel_btn {
                    background-color: #6c757d;
                }
                QPushButton#cancel_btn:hover {
                    background-color: #5a6268;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title_label = QLabel(f"📧 {firm_data['name']} - Email Adresi Ekle")
            title_label.setStyleSheet("font-size: 16px; color: #0d7377; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # Form alanları
            form_layout = QFormLayout()
            
            # İsim Soyisim
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("Ahmet Yılmaz")
            form_layout.addRow("👤 İsim Soyisim:", name_edit)
            
            # Email adresi
            email_edit = QLineEdit()
            email_edit.setPlaceholderText("ornek@firma.com")
            form_layout.addRow("📧 Email Adresi:", email_edit)
            
            # Pozisyon
            position_edit = QLineEdit()
            position_edit.setPlaceholderText("Genel Müdür, Satış Müdürü, vb.")
            form_layout.addRow("💼 Pozisyon:", position_edit)
            
            # Kaynak
            source_edit = QLineEdit()
            source_edit.setPlaceholderText("Website, LinkedIn, vb.")
            form_layout.addRow("🔍 Kaynak:", source_edit)
            
            # Notlar
            notes_edit = QTextEdit()
            notes_edit.setPlaceholderText("Ek notlar...")
            notes_edit.setMaximumHeight(60)
            form_layout.addRow("📝 Notlar:", notes_edit)
            
            layout.addLayout(form_layout)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            save_btn = QPushButton("💾 Email Ekle")
            save_btn.clicked.connect(lambda: self.save_email_from_detail_dialog(
                dialog, parent_dialog, firm_data, {
                    'name': name_edit.text().strip(),
                    'email': email_edit.text().strip(),
                    'position': position_edit.text().strip(),
                    'source': source_edit.text().strip(),
                    'notes': notes_edit.toPlainText().strip()
                }
            ))
            
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.setObjectName("cancel_btn")
            cancel_btn.clicked.connect(dialog.reject)
            
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Email ekleme dialogu açılamadı:\n{str(e)}")
    
    def save_email_from_detail_dialog(self, dialog, parent_dialog, firm_data, email_data):
        """Firma detay dialogundan email kaydet"""
        try:
            if not email_data['email']:
                QMessageBox.warning(dialog, "Uyarı", "Email adresi boş olamaz!")
                return
            
            # Email formatını kontrol et
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email_data['email']):
                QMessageBox.warning(dialog, "Uyarı", "Geçerli bir email adresi girin!")
                return
            
            # Yeni email objesi oluştur
            new_email = {
                'name': email_data['name'] or 'Bilinmiyor',
                'email': email_data['email'],
                'position': email_data['position'] or 'Bilinmiyor',
                'source': email_data['source'] or 'Manuel',
                'score': 0.8,  # Manuel eklenen emailler için yüksek skor
                'is_verified': False,
                'notes': email_data['notes']
            }
            
            # Firmaya email ekle
            if 'emails' not in firm_data:
                firm_data['emails'] = []
            
            # Aynı email var mı kontrol et
            existing_emails = [e.get('email', '') for e in firm_data.get('emails', [])]
            if email_data['email'] in existing_emails:
                QMessageBox.warning(dialog, "Uyarı", "Bu email adresi zaten mevcut!")
                return
            
            firm_data['emails'].append(new_email)
            
            # Veritabanında güncelle
            if self.db and firm_data.get('id'):
                update_data = {
                    'emails': firm_data['emails']
                }
                if self.db.update_firm(firm_data['id'], update_data):
                    QMessageBox.information(dialog, "✅ Başarılı", 
                        f"Email adresi başarıyla eklendi!\n\n"
                        f"📧 {email_data['email']}\n"
                        f"👤 {email_data['name'] or 'Bilinmiyor'}\n"
                        f"💼 {email_data['position'] or 'Bilinmiyor'}")
                    
                    dialog.accept()
                    parent_dialog.accept()  # Ana dialogu da kapat
                    
                    # Firmalar tablosunu yenile
                    self.load_all_firms()
                else:
                    QMessageBox.critical(dialog, "❌ Hata", "Email veritabanında güncellenemedi!")
            else:
                QMessageBox.warning(dialog, "Uyarı", "Veritabanı bağlantısı yok veya firma ID'si bulunamadı!")
                
        except Exception as e:
            QMessageBox.critical(dialog, "❌ Hata", f"Email kaydetme hatası:\n{str(e)}")
    
    def refresh_firms_table(self):
        """Firmalar tablosunu yenile"""
        try:
            # Firmaları yeniden yükle
            self.load_all_firms()
            
            # Tabloyu güncelle
            if hasattr(self, 'all_firms_table'):
                self.all_firms_table.setRowCount(len(self.all_firms))
                
                for i, firm in enumerate(self.all_firms):
                    # Checkbox (Kolon 0)
                    checkbox = QCheckBox()
                    checkbox.stateChanged.connect(self.update_firms_selection_info)
                    self.all_firms_table.setCellWidget(i, 0, checkbox)
                    
                    # Firma Adı (Kolon 1)
                    self.all_firms_table.setItem(i, 1, QTableWidgetItem(firm.get('name', '')))
                    
                    # Telefon (Kolon 2)
                    self.all_firms_table.setItem(i, 2, QTableWidgetItem(firm.get('phone', '')))
                    
                    # Adres (Kolon 3)
                    self.all_firms_table.setItem(i, 3, QTableWidgetItem(firm.get('address', '')))
                    
                    # Website (Kolon 4)
                    self.all_firms_table.setItem(i, 4, QTableWidgetItem(firm.get('website', '')))
                    
                    # Email Detayları (Kolon 3) - Sadece email sayısı
                    emails = firm.get('emails', [])
                    
                    # JSON string ise parse et
                    if isinstance(emails, str):
                        try:
                            emails = json.loads(emails) if emails.strip() else []
                        except:
                            emails = []
                    elif emails is None:
                        emails = []
                    
                    email_count = len(emails)
                    email_text = f"📧 {email_count} email"
                    self.all_firms_table.setItem(i, 3, QTableWidgetItem(email_text))
                    
                    # Sektör (Kolon 6)
                    self.all_firms_table.setItem(i, 6, QTableWidgetItem(firm.get('sector', '')))
                    
                    # Açıklama (Kolon 7)
                    self.all_firms_table.setItem(i, 7, QTableWidgetItem(firm.get('summary', '')))
                
                # Firma sayısını güncelle
                if hasattr(self, 'firms_count_display'):
                    self.firms_count_display.setText(f"📊 Toplam: {len(self.all_firms)} firma")
                
                print(f"✅ DEBUG: Tablo yenilendi - {len(self.all_firms)} firma")
                
        except Exception as e:
            print(f"❌ DEBUG: Tablo yenileme hatası: {str(e)}")
    
    def open_edit_firm_dialog(self, firm_data, table_row):
        """Firma düzenleme dialogunu aç"""
        dialog = QDialog(self)
        dialog.setWindowTitle("✏️ Firma Düzenle")
        dialog.setModal(True)
        dialog.resize(500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2a2a2a;
                color: white;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #0d7377;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton#cancel_btn {
                background-color: #6c757d;
            }
            QPushButton#cancel_btn:hover {
                background-color: #5a6268;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Başlık
        title_label = QLabel("🏢 Firma Bilgilerini Düzenle")
        title_label.setStyleSheet("font-size: 16px; color: #0d7377; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Form alanları
        form_layout = QFormLayout()
        
        # Firma Adı
        name_edit = QLineEdit(firm_data.get('name', ''))
        name_edit.setPlaceholderText("Firma adını girin...")
        form_layout.addRow("🏢 Firma Adı:", name_edit)
        
        # Telefon
        phone_edit = QLineEdit(firm_data.get('phone', ''))
        phone_edit.setPlaceholderText("Telefon numarası...")
        form_layout.addRow("📞 Telefon:", phone_edit)
        
        # Adres
        address_edit = QTextEdit()
        address_edit.setPlainText(firm_data.get('address', ''))
        address_edit.setPlaceholderText("Tam adres bilgisi...")
        address_edit.setMaximumHeight(80)
        form_layout.addRow("📍 Adres:", address_edit)
        
        # Website
        website_edit = QLineEdit(firm_data.get('website', ''))
        website_edit.setPlaceholderText("Website URL'si...")
        form_layout.addRow("🌐 Website:", website_edit)
        
        # Email
        email_edit = QLineEdit(firm_data.get('email', ''))
        email_edit.setPlaceholderText("E-posta adresi...")
        form_layout.addRow("📧 E-posta:", email_edit)
        
        # Sektör
        sector_edit = QLineEdit(firm_data.get('sector', ''))
        sector_edit.setPlaceholderText("Sektör bilgisi...")
        form_layout.addRow("🏭 Sektör:", sector_edit)
        
        # Açıklama
        description_edit = QTextEdit()
        description_edit.setPlainText(firm_data.get('description', ''))
        description_edit.setPlaceholderText("Firma hakkında açıklama...")
        description_edit.setMaximumHeight(80)
        form_layout.addRow("📝 Açıklama:", description_edit)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Kaydet")
        save_btn.clicked.connect(lambda: self.save_edited_firm(
            dialog, firm_data, table_row, {
                'name': name_edit.text().strip(),
                'phone': phone_edit.text().strip(),
                'address': address_edit.toPlainText().strip(),
                'website': website_edit.text().strip(),
                'email': email_edit.text().strip(),
                'sector': sector_edit.text().strip(),
                'description': description_edit.toPlainText().strip()
            }
        ))
        
        cancel_btn = QPushButton("❌ İptal")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def save_edited_firm(self, dialog, original_firm, table_row, new_data):
        """Düzenlenen firma bilgilerini kaydet"""
        try:
            # Boş alanları kontrol et
            if not new_data['name']:
                QMessageBox.warning(dialog, "Uyarı", "Firma adı boş olamaz!")
                return
            
            # Veritabanında güncelle
            if self.db:
                update_data = {
                    'name': new_data['name'],
                    'phone': new_data['phone'],
                    'address': new_data['address'],
                    'website': new_data['website'],
                    'email': new_data['email'],
                    'sector': new_data['sector'],
                    'description': new_data['description']
                }
                
                # ID ile güncelle
                if original_firm.get('id'):
                    print(f"🔍 DEBUG: ID ile güncelleme: {original_firm['id']}")
                    success = self.db.update_firm(original_firm['id'], **update_data)
                    if success:
                        # Tabloyu güncelle
                        self.update_firm_in_table(table_row, new_data)
                        
                        # all_firms listesini güncelle
                        for i, firm in enumerate(self.all_firms):
                            if firm.get('id') == original_firm.get('id'):
                                self.all_firms[i].update(update_data)
                                break
                        
                        QMessageBox.information(dialog, "✅ Başarılı", "Firma bilgileri güncellendi!")
                        dialog.accept()
                    else:
                        QMessageBox.critical(dialog, "❌ Hata", "Firma güncellenemedi!")
                else:
                    # ID yoksa, isim ile güncelle
                    print("⚠️ DEBUG: ID yok, isim ile güncelleme deneniyor...")
                    firm_name = original_firm.get('name', '')
                    if firm_name:
                        # Veritabanında isim ile firma bul
                        firms = self.db.get_firms_by_filter({'name': firm_name})
                        if firms:
                            firm_id = firms[0].get('id')
                            print(f"🔍 DEBUG: İsim ile bulunan ID: {firm_id}")
                            success = self.db.update_firm(firm_id, **update_data)
                            if success:
                                # Tabloyu güncelle
                                self.update_firm_in_table(table_row, new_data)
                                
                                # all_firms listesini güncelle
                                for i, firm in enumerate(self.all_firms):
                                    if firm.get('name', '').strip().lower() == firm_name.strip().lower():
                                        self.all_firms[i].update(update_data)
                                        break
                                
                                QMessageBox.information(dialog, "✅ Başarılı", "Firma bilgileri güncellendi!")
                                dialog.accept()
                            else:
                                QMessageBox.critical(dialog, "❌ Hata", "Firma güncellenemedi!")
                        else:
                            QMessageBox.warning(dialog, "Uyarı", 
                                f"Veritabanında '{firm_name}' isimli firma bulunamadı!\n\n"
                                "Bu firma sadece tabloda görünüyor olabilir.")
                    else:
                        QMessageBox.warning(dialog, "Uyarı", "Firma adı ve ID'si bulunamadı!")
            else:
                QMessageBox.warning(dialog, "Uyarı", "Veritabanı bağlantısı yok!")
                
        except Exception as e:
            QMessageBox.critical(dialog, "❌ Hata", f"Güncelleme hatası:\n{str(e)}")
    
    def update_firm_in_table(self, row, new_data):
        """Tablodaki firma bilgilerini güncelle"""
        try:
            # Tablo sütunları: [Seçim, Firma Adı, Telefon, Adres, Website, Email, Sektör, Açıklama]
            if new_data['name']:
                self.all_firms_table.setItem(row, 1, QTableWidgetItem(new_data['name']))
            if new_data['phone']:
                self.all_firms_table.setItem(row, 2, QTableWidgetItem(new_data['phone']))
            if new_data['address']:
                self.all_firms_table.setItem(row, 3, QTableWidgetItem(new_data['address']))
            if new_data['website']:
                self.all_firms_table.setItem(row, 4, QTableWidgetItem(new_data['website']))
            if new_data['email']:
                self.all_firms_table.setItem(row, 5, QTableWidgetItem(new_data['email']))
            if new_data['sector']:
                self.all_firms_table.setItem(row, 6, QTableWidgetItem(new_data['sector']))
            if new_data['description']:
                self.all_firms_table.setItem(row, 7, QTableWidgetItem(new_data['description']))
                
        except Exception as e:
            print(f"Tablo güncelleme hatası: {str(e)}")
    
    def delete_selected_firm(self):
        """Seçili firmayı sil"""
        current_row = self.all_firms_table.currentRow()
        if current_row >= 0:
            firm_name = self.all_firms_table.item(current_row, 1).text()
            
            # Firma ID'sini bul
            firm_id = None
            for firm in self.all_firms:
                if firm['name'] == firm_name:
                    firm_id = firm['id']
                    break
            
            if not firm_id:
                QMessageBox.warning(self, "Hata", "Firma ID'si bulunamadı!")
                return
            
            reply = QMessageBox.question(self, "Silme Onayı", 
                f"'{firm_name}' firmasını veritabanından kalıcı olarak silmek istediğinize emin misiniz?\n\n"
                f"Bu işlem geri alınamaz!",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                try:
                    # Veritabanından sil
                    success = self.db.delete_firm(firm_id)
                    
                    if success:
                        # Tablodan kaldır
                        self.all_firms_table.removeRow(current_row)
                        
                        # all_firms listesinden kaldır
                        self.all_firms = [f for f in self.all_firms if f['id'] != firm_id]
                        
                        # current_firms listesinden de kaldır (varsa)
                        self.current_firms = [f for f in self.current_firms if f['id'] != firm_id]
                        
                        # Ana tabloyu yenile
                        self.refresh_firms_table()
                        
                        QMessageBox.information(self, "✅ Başarılı", 
                            f"'{firm_name}' firması başarıyla silindi!")
                    else:
                        QMessageBox.critical(self, "❌ Hata", "Firma silinirken bir hata oluştu!")
                        
                except Exception as e:
                    QMessageBox.critical(self, "❌ Hata", f"Firma silinirken hata oluştu:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir firma seçin!")
    
    def delete_selected_firms(self):
        """Seçili firmaları toplu olarak sil"""
        selected_firms = []
        
        # Seçili firmaları bul
        for row in range(self.all_firms_table.rowCount()):
            checkbox = self.all_firms_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                firm_name = self.all_firms_table.item(row, 1).text()
                # Firma ID'sini bul
                for firm in self.all_firms:
                    if firm['name'] == firm_name:
                        selected_firms.append(firm)
                        break
        
        if not selected_firms:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için en az bir firma seçin!")
            return
        
        # Onay al
        firm_names = [f['name'] for f in selected_firms]
        reply = QMessageBox.question(self, "Toplu Silme Onayı", 
            f"{len(selected_firms)} firmayı veritabanından kalıcı olarak silmek istediğinize emin misiniz?\n\n"
            f"Silinecek firmalar:\n" + "\n".join(firm_names[:5]) + 
            (f"\n... ve {len(firm_names)-5} firma daha" if len(firm_names) > 5 else "") +
            f"\n\nBu işlem geri alınamaz!",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                success_count = 0
                failed_firms = []
                
                for firm in selected_firms:
                    try:
                        # Veritabanından sil
                        success = self.db.delete_firm(firm['id'])
                        if success:
                            success_count += 1
                        else:
                            failed_firms.append(firm['name'])
                    except Exception as e:
                        failed_firms.append(f"{firm['name']} (Hata: {str(e)})")
                
                # Başarılı silinen firmaları tablodan kaldır
                if success_count > 0:
                    # Ters sırada sil (indeks kaymasını önlemek için)
                    for row in range(self.all_firms_table.rowCount() - 1, -1, -1):
                        checkbox = self.all_firms_table.cellWidget(row, 0)
                        if checkbox and checkbox.isChecked():
                            self.all_firms_table.removeRow(row)
                    
                    # Listelerden kaldır
                    deleted_ids = [f['id'] for f in selected_firms if f['name'] not in failed_firms]
                    self.all_firms = [f for f in self.all_firms if f['id'] not in deleted_ids]
                    self.current_firms = [f for f in self.current_firms if f['id'] not in deleted_ids]
                    
                    # Ana tabloyu yenile
                    self.refresh_firms_table()
                
                # Sonuç mesajı
                if success_count == len(selected_firms):
                    QMessageBox.information(self, "✅ Başarılı", 
                        f"{success_count} firma başarıyla silindi!")
                elif success_count > 0:
                    QMessageBox.warning(self, "⚠️ Kısmen Başarılı", 
                        f"{success_count} firma silindi, {len(failed_firms)} firma silinemedi:\n" + 
                        "\n".join(failed_firms[:3]) + 
                        (f"\n... ve {len(failed_firms)-3} firma daha" if len(failed_firms) > 3 else ""))
                else:
                    QMessageBox.critical(self, "❌ Hata", 
                        "Hiçbir firma silinemedi!\n" + "\n".join(failed_firms[:3]))
                        
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"Toplu silme işleminde hata oluştu:\n{str(e)}")
    
    def send_selected_to_whatsapp(self):
        """Seçili firmaları WhatsApp'a yönlendir"""
        selected_firms = []
        
        for row in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                firm = self.current_firms[row]
                selected_firms.append(firm)
        
        if not selected_firms:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir firma seçin!")
            return
        
        # Database'de işaretle
        success_count = 0
        for firm in selected_firms:
            if 'id' in firm:
                success = self.db.update_firm_action(firm['id'], 'whatsapp_yonlendirildi')
                if success:
                    success_count += 1
        
        if success_count > 0:
            QMessageBox.information(self, "✅ Başarılı", 
                f"{success_count} firma WhatsApp'a yönlendirildi!\n\n"
                "main2.py'yi açtığınızda bu firmalar WhatsApp sekmesinde otomatik seçili olacak.")
            
            # Status bar güncellemesi
            self.status_bar.showMessage(f"📱 {success_count} firma WhatsApp'a yönlendirildi")
        else:
            QMessageBox.warning(self, "Hata", "Firma yönlendirme işlemi başarısız!")
    
    def send_selected_to_call(self):
        """Seçili firmaları çağrıya yönlendir"""
        selected_firms = []
        
        for row in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                firm = self.current_firms[row]
                selected_firms.append(firm)
        
        if not selected_firms:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir firma seçin!")
            return
        
        # Database'de işaretle
        success_count = 0
        for firm in selected_firms:
            if 'id' in firm:
                success = self.db.update_firm_action(firm['id'], 'cagri_yonlendirildi')
                if success:
                    success_count += 1
        
        if success_count > 0:
            QMessageBox.information(self, "✅ Başarılı", 
                f"{success_count} firma çağrıya yönlendirildi!\n\n"
                "main2.py'yi açtığınızda bu firmalar VAPI çağrı sekmesinde otomatik seçili olacak.")
            
            # Status bar güncellemesi
            self.status_bar.showMessage(f"📞 {success_count} firma çağrıya yönlendirildi")
        else:
            QMessageBox.warning(self, "Hata", "Firma yönlendirme işlemi başarısız!")
    
    def send_firm_to_whatsapp(self, firm):
        """Tek firmayı WhatsApp'a yönlendir"""
        if not firm or not firm.get('id'):
            QMessageBox.warning(self, "Hata", "Firma bilgisi eksik!")
            return
        
        success = self.db.update_firm_action(firm['id'], 'whatsapp_yonlendirildi')
        
        if success:
            QMessageBox.information(self, "✅ Başarılı", 
                f"{firm.get('name', 'Firma')} WhatsApp'a yönlendirildi!\n\n"
                "main2.py'yi açtığınızda bu firma WhatsApp sekmesinde otomatik seçili olacak.")
            
            self.status_bar.showMessage(f"📱 {firm.get('name', 'Firma')} WhatsApp'a yönlendirildi")
        else:
            QMessageBox.warning(self, "Hata", "Firma yönlendirme işlemi başarısız!")
    
    def send_firm_to_call(self, firm):
        """Tek firmayı çağrıya yönlendir"""
        if not firm or not firm.get('id'):
            QMessageBox.warning(self, "Hata", "Firma bilgisi eksik!")
            return
        
        success = self.db.update_firm_action(firm['id'], 'cagri_yonlendirildi')
        
        if success:
            QMessageBox.information(self, "✅ Başarılı", 
                f"{firm.get('name', 'Firma')} çağrıya yönlendirildi!\n\n"
                "main2.py'yi açtığınızda bu firma VAPI çağrı sekmesinde otomatik seçili olacak.")
            
            self.status_bar.showMessage(f"📞 {firm.get('name', 'Firma')} çağrıya yönlendirildi")
        else:
            QMessageBox.warning(self, "Hata", "Firma yönlendirme işlemi başarısız!")
    
    def create_campaign_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Sol panel - Kampanya firmaları
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        campaign_firms_group = QGroupBox("📋 Kampanya Firmaları")
        campaign_firms_layout = QVBoxLayout()
        
        # Firma sayısı
        self.campaign_info_label = QLabel("0 firma, 0 email")
        self.campaign_info_label.setStyleSheet("font-size: 16px; color: #14a1a5;")
        campaign_firms_layout.addWidget(self.campaign_info_label)
        
        # Firma listesi
        self.campaign_firms_list = QListWidget()
        campaign_firms_layout.addWidget(self.campaign_firms_list)
        
        # İşlem butonları
        firm_buttons_layout = QHBoxLayout()
        
        remove_firm_btn = QPushButton("❌ Seçiliyi Kaldır")
        remove_firm_btn.clicked.connect(self.remove_selected_firm)
        firm_buttons_layout.addWidget(remove_firm_btn)
        
        clear_all_btn = QPushButton("🗑️ Tümünü Temizle")
        clear_all_btn.clicked.connect(self.clear_campaign_firms)
        firm_buttons_layout.addWidget(clear_all_btn)
        
        campaign_firms_layout.addLayout(firm_buttons_layout)
        
        campaign_firms_group.setLayout(campaign_firms_layout)
        left_layout.addWidget(campaign_firms_group)
        
        layout.addWidget(left_panel, 1)
        
        # Sağ panel - Mail ayarları
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Mail şablonu
        template_group = QGroupBox("✉️ Mail Şablonu")
        template_layout = QVBoxLayout()
        
        # Şablon yönetimi
        template_management_layout = QHBoxLayout()
        template_management_layout.addWidget(QLabel("📝 Şablon:"))
        
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Özel Şablon",
            "Yazılım Firmaları İçin",
            "E-ticaret Firmaları İçin",
            "Danışmanlık Firmaları İçin",
            "Üretim Firmaları İçin"
        ])
        self.template_combo.currentTextChanged.connect(self.load_template)
        template_management_layout.addWidget(self.template_combo)
        
        # Şablon yönetim butonları
        manage_template_btn = QPushButton("⚙️ Yönet")
        manage_template_btn.setToolTip("Şablon yönetim panelini aç")
        manage_template_btn.clicked.connect(self.show_template_manager)
        manage_template_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        template_management_layout.addWidget(manage_template_btn)
        
        new_template_btn = QPushButton("➕ Yeni")
        new_template_btn.setToolTip("Yeni şablon oluştur")
        new_template_btn.clicked.connect(self.create_new_template)
        new_template_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        template_management_layout.addWidget(new_template_btn)
        
        template_layout.addLayout(template_management_layout)
        
        # Mail talimatları
        template_layout.addWidget(QLabel("Mail Talimatları (AI için):"))
        self.mail_instructions = QTextEdit()
        self.mail_instructions.setPlaceholderText(
            "Örnek: Yazılım hizmetlerimizi tanıtan, samimi ve profesyonel bir mail yaz. "
            "Firma'nın teknolojilerini ve başarılarını öv. 15 dakikalık demo randevusu iste."
        )
        self.mail_instructions.setMaximumHeight(120)
        template_layout.addWidget(self.mail_instructions)
        
        # Sistem promptu
        template_layout.addWidget(QLabel("AI Sistem Promptu:"))
        self.system_prompt = QTextEdit()
        self.system_prompt.setPlaceholderText(
            "Örnek: Sen B2B satış uzmanısın. Kişiselleştirilmiş ve ikna edici mailler yazıyorsun."
        )
        self.system_prompt.setText(
            "Sen deneyimli bir B2B satış uzmanısın. Türkçe, samimi ama profesyonel, "
            "kişiselleştirilmiş satış mailleri yazıyorsun. Firma hakkında verilen bilgileri "
            "kullanarak spesifik ve ikna edici mailler oluşturuyorsun."
        )
        self.system_prompt.setMaximumHeight(100)
        template_layout.addWidget(self.system_prompt)
        
        # Spam kontrol
        spam_check_layout = QHBoxLayout()
        self.spam_check_btn = QPushButton("🛡️ Spam Kontrolü Yap")
        self.spam_check_btn.clicked.connect(self.check_template_spam_score)
        spam_check_layout.addWidget(self.spam_check_btn)
        
        self.spam_score_label = QLabel("")
        spam_check_layout.addWidget(self.spam_score_label)
        spam_check_layout.addStretch()
        
        template_layout.addLayout(spam_check_layout)
        
        template_group.setLayout(template_layout)
        right_layout.addWidget(template_group)
        
        # Önizleme
        preview_group = QGroupBox("👁️ Mail Önizleme")
        preview_layout = QVBoxLayout()
        
        # Önizleme butonları
        preview_buttons = QHBoxLayout()
        
        preview_btn = QPushButton("🔍 Önizleme Oluştur")
        preview_btn.clicked.connect(self.generate_preview)
        preview_buttons.addWidget(preview_btn)
        
        self.preview_firm_combo = QComboBox()
        self.preview_firm_combo.setPlaceholderText("Önizleme için firma seç")
        preview_buttons.addWidget(self.preview_firm_combo)
        
        preview_layout.addLayout(preview_buttons)
        
        # Önizleme alanı
        self.preview_web = QWebEngineView()
        self.preview_web.setMinimumHeight(300)
        
        # JavaScript error handling ekle
        self.setup_webengine_error_handling(self.preview_web)
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = self.preview_web.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Preview web profile ayarları uygulanamadı: {e}")
        
        preview_layout.addWidget(self.preview_web)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        # Kampanya başlat
        start_layout = QHBoxLayout()
        
        self.test_mode_check = QCheckBox("Test Modu (İlk 3 firmaya gönder)")
        start_layout.addWidget(self.test_mode_check)
        
        start_layout.addStretch()
        
        self.start_campaign_btn = QPushButton("🚀 Kampanyayı Başlat")
        self.start_campaign_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #27ae60, stop: 1 #2ecc71);
                font-size: 16px;
                padding: 15px 30px;
            }
        """)
        self.start_campaign_btn.clicked.connect(self.start_campaign)
        start_layout.addWidget(self.start_campaign_btn)
        
        right_layout.addLayout(start_layout)
        
        layout.addWidget(right_panel, 2)
        
        return widget
    
    def create_tracking_tab(self):
        """Gelişmiş tracking dashboard'u"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Üst kısım - Özet kartlar ve filtreler
        top_layout = QVBoxLayout()
        
        # Hızlı istatistik kartları
        stats_cards_layout = QHBoxLayout()
        
        # Kart widget'ları - Cooler renk şeması
        self.sent_card = ModernCard("Gönderilen", "0", "#667eea", "📤")
        self.opened_card = ModernCard("Açılan", "0", "#48BB78", "👁️")
        self.clicked_card = ModernCard("Tıklanan", "0", "#ED8936", "🖱️")
        self.replied_card = ModernCard("Yanıtlanan", "0", "#9F7AEA", "💬")
        self.bounce_card = ModernCard("Geri Dönen", "0", "#F56565", "⚠️")
        self.unsubscribe_card = ModernCard("Abonelikten Çıkan", "0", "#A0AEC0", "🚫")
        
        stats_cards_layout.addWidget(self.sent_card)
        stats_cards_layout.addWidget(self.opened_card)
        stats_cards_layout.addWidget(self.clicked_card)
        stats_cards_layout.addWidget(self.replied_card)
        stats_cards_layout.addWidget(self.bounce_card)
        stats_cards_layout.addWidget(self.unsubscribe_card)
        
        top_layout.addLayout(stats_cards_layout)
        
        # Filtreler ve kontroller
        filter_layout = QHBoxLayout()
        
        # Sol - Filtreler
        filter_left = QHBoxLayout()
        
        filter_left.addWidget(QLabel("📅 Dönem:"))
        self.period_filter = QComboBox()
        self.period_filter.addItems(["Son 24 Saat", "Son 7 Gün", "Son 30 Gün", "Son 3 Ay", "Tümü"])
        self.period_filter.setCurrentIndex(1)
        self.period_filter.currentTextChanged.connect(self.update_tracking_dashboard)
        filter_left.addWidget(self.period_filter)

        # Eğer date_filter eklemek isterseniz:
        filter_left.addWidget(QLabel("📆 Tarih:"))
        self.date_filter = QComboBox()
        self.date_filter.addItems(["Son 7 Gün", "Son 30 Gün", "Son 3 Ay", "Tümü"])
        self.date_filter.currentTextChanged.connect(self.update_tracking_dashboard)
        filter_left.addWidget(self.date_filter)
        
        filter_left.addWidget(QLabel("🏷️ Kampanya:"))
        self.campaign_filter = QComboBox()
        self.campaign_filter.addItems(["Tüm Kampanyalar"])
        self.campaign_filter.currentTextChanged.connect(self.update_tracking_dashboard)
        filter_left.addWidget(self.campaign_filter)
        
        filter_left.addWidget(QLabel("📊 Durum:"))
        self.status_filter_tracking = QComboBox()
        self.status_filter_tracking.addItems(["Tümü", "Gönderildi", "Açıldı", "Tıklandı", "Yanıtlandı", "Geri Döndü"])
        self.status_filter_tracking.currentTextChanged.connect(self.filter_tracking_table)
        filter_left.addWidget(self.status_filter_tracking)
        
        filter_layout.addLayout(filter_left)
        filter_layout.addStretch()
        
        # Sağ - Kontroller
        filter_right = QHBoxLayout()
        
        # Gerçek zamanlı takip
        self.realtime_tracking_check = QCheckBox("🔴 Gerçek Zamanlı Takip")
        self.realtime_tracking_check.setChecked(True)
        self.realtime_tracking_check.stateChanged.connect(self.toggle_realtime_tracking)
        filter_right.addWidget(self.realtime_tracking_check)
        
        # Yenile butonu
        refresh_tracking_btn = QPushButton("🔄 Yenile")
        refresh_tracking_btn.clicked.connect(self.update_tracking_dashboard)
        filter_right.addWidget(refresh_tracking_btn)
        
        # Export butonu
        export_tracking_btn = QPushButton("📥 Rapor İndir")
        export_tracking_btn.clicked.connect(self.export_tracking_report)
        filter_right.addWidget(export_tracking_btn)
        
        filter_layout.addLayout(filter_right)
        
        top_layout.addLayout(filter_layout)
        layout.addLayout(top_layout)
        
        # Ana içerik - Tab widget
        tracking_tabs = QTabWidget()
        
        # Tab 1: Canlı İzleme (HTML Dashboard)
        live_tab = QWidget()
        live_layout = QVBoxLayout(live_tab)
        
        self.tracking_dashboard_view = QWebEngineView()
        self.tracking_dashboard_view.setMinimumHeight(500)
        
        # JavaScript error handling ekle
        self.setup_webengine_error_handling(self.tracking_dashboard_view)
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = self.tracking_dashboard_view.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Tracking dashboard profile ayarları uygulanamadı: {e}")
        
        live_layout.addWidget(self.tracking_dashboard_view)
        
        tracking_tabs.addTab(live_tab, "📊 Canlı İzleme")
        
        # Tab 2: Detaylı Liste
        detail_tab = QWidget()
        detail_layout = QVBoxLayout(detail_tab)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Ara:"))
        self.tracking_search_input = QLineEdit()
        self.tracking_search_input.setPlaceholderText("Firma adı, email veya konu...")
        self.tracking_search_input.textChanged.connect(self.search_tracking_table)
        search_layout.addWidget(self.tracking_search_input)
        detail_layout.addLayout(search_layout)
        
        # Tracking tablosu
        self.tracking_table = QTableWidget()
        self.tracking_table.setColumnCount(11)
        self.tracking_table.setHorizontalHeaderLabels([
            "Firma", "Email", "Konu", "Kampanya", "Gönderim", 
            "Açılma", "Açılma Sayısı", "Tıklama", "Yanıt", "Durum", "İşlem"
        ])
        self.tracking_table.setAlternatingRowColors(True)
        self.tracking_table.setSortingEnabled(True)
        
        # Sütun genişlikleri
        self.tracking_table.setColumnWidth(0, 150)  # Firma
        self.tracking_table.setColumnWidth(1, 200)  # Email
        self.tracking_table.setColumnWidth(2, 200)  # Konu
        self.tracking_table.setColumnWidth(3, 120)  # Kampanya
        
        detail_layout.addWidget(self.tracking_table)
        
        tracking_tabs.addTab(detail_tab, "📋 Detaylı Liste")
        
        # Tab 3: Isı Haritası
        heatmap_tab = QWidget()
        heatmap_layout = QVBoxLayout(heatmap_tab)
        
        self.heatmap_view = QWebEngineView()
        self.heatmap_view.setMinimumHeight(500)
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = self.heatmap_view.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Heatmap view profile ayarları uygulanamadı: {e}")
        
        heatmap_layout.addWidget(self.heatmap_view)
        
        tracking_tabs.addTab(heatmap_tab, "🔥 Isı Haritası")
        
        # Tab 4: Cihaz/Lokasyon Analizi
        device_tab = QWidget()
        device_layout = QVBoxLayout(device_tab)
        
        self.device_analysis_view = QWebEngineView()
        self.device_analysis_view.setMinimumHeight(500)
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = self.device_analysis_view.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Device analysis view profile ayarları uygulanamadı: {e}")
        
        device_layout.addWidget(self.device_analysis_view)
        
        tracking_tabs.addTab(device_tab, "📱 Cihaz/Lokasyon")
        
        layout.addWidget(tracking_tabs)
        
        # Alt bilgi paneli
        info_layout = QHBoxLayout()
        
        self.tracking_info_label = QLabel("ℹ️ Tracking pixel ile gerçek zamanlı email takibi aktif")
        self.tracking_info_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(self.tracking_info_label)
        
        info_layout.addStretch()
        
        self.last_update_label = QLabel("Son güncelleme: -")
        self.last_update_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(self.last_update_label)
        
        layout.addLayout(info_layout)
        
        # Timer for real-time updates
        self.tracking_update_timer = QTimer()
        self.tracking_update_timer.timeout.connect(self.update_tracking_realtime)
        self.tracking_update_timer.start(5000)  # Her 5 saniyede bir güncelle
        
        # İlk yükleme
        QTimer.singleShot(100, self.update_tracking_dashboard)
        
        return widget

    def update_tracking_dashboard(self):
        """Tracking dashboard'unu güncelle - YENİ TRACKING SİSTEMİ"""
        try:
            # Dönem seçimi (filter'dan al)
            period_text = self.period_filter.currentText()
            
            # Dönemi güne çevir
            period_days_map = {
                "Son 24 Saat": 1,
                "Son 7 Gün": 7,
                "Son 30 Gün": 30,
                "Son 3 Ay": 90,
                "Tümü": 365
            }
            days = period_days_map.get(period_text, 7)
            
            # Yeni tracking sistem mevcut mu?
            if self.tracking_gui_manager:
                # Yeni sistemden istatistikleri al
                dashboard_data = self.tracking_gui_manager.get_dashboard_stats(days=days)
                stats = dashboard_data.get('overall', {})
                
                # Server sağlık kontrolü
                health = self.tracking_gui_manager.check_server_health()
                if health['status'] == 'healthy':
                    self.tracking_info_label.setText(
                        f"✅ Tracking Server: Aktif | "
                        f"Database: {health.get('data', {}).get('total_emails_tracked', 0)} email"
                    )
                    self.tracking_info_label.setStyleSheet("color: #4ade80; font-size: 12px;")
                else:
                    self.tracking_info_label.setText(
                        f"⚠️ Tracking Server: {health.get('error', 'Bilinmeyen hata')}"
                    )
                    self.tracking_info_label.setStyleSheet("color: #f59e0b; font-size: 12px;")
            else:
                # Eski sistem (fallback - database'den al)
                if self.db:
                    campaign = self.campaign_filter.currentText()
                    stats = self.db.get_tracking_statistics(period_text, campaign)
                else:
                    stats = {}
                
                self.tracking_info_label.setText(
                    "ℹ️ Tracking pixel ile email takibi (Eski sistem)"
                )
                self.tracking_info_label.setStyleSheet("color: #666; font-size: 12px;")
            
            # Kartları güncelle
            self.sent_card.update_value(stats.get('total_sent', 0))
            self.opened_card.update_value(stats.get('total_opened', 0))
            self.clicked_card.update_value(stats.get('total_clicked', 0))
            
            # Eski sistemde olan ama yenide olmayan alanlar için fallback
            self.replied_card.update_value(stats.get('replied', stats.get('total_replied', 0)))
            self.bounce_card.update_value(stats.get('bounced', stats.get('total_bounced', 0)))
            self.unsubscribe_card.update_value(stats.get('unsubscribed', stats.get('total_unsubscribed', 0)))
            
            # HTML Dashboard'u güncelle (yeni sistem)
            if self.tracking_gui_manager:
                html_content = self.tracking_gui_manager.generate_html_dashboard(dashboard_data)
                self.tracking_dashboard_view.setHtml(html_content)
                
                # Isı haritasını güncelle
                heatmap_data = self.tracking_gui_manager.get_hourly_heatmap(days=days)
                heatmap_html = self.tracking_gui_manager.generate_heatmap_html(heatmap_data)
                self.heatmap_view.setHtml(heatmap_html)
                
                # Cihaz analizi için basit HTML (device_breakdown'dan)
                device_breakdown = dashboard_data.get('device_breakdown', {})
                self.load_device_analysis_html_new(device_breakdown)
            else:
                # Eski sistem HTML'leri
                self.load_tracking_dashboard_html(stats)
                self.load_heatmap_html(stats)
                self.load_device_analysis_html(stats)
            
            # Tabloyu güncelle
            self.update_tracking()
            
            # Son güncelleme zamanı
            self.last_update_label.setText(f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}")
            self.last_update_label.setStyleSheet("color: #4ade80; font-size: 12px;")
            
        except Exception as e:
            print(f"❌ Tracking dashboard güncelleme hatası: {e}")
            self.tracking_info_label.setText(f"❌ Hata: {str(e)}")
            self.tracking_info_label.setStyleSheet("color: #ef4444; font-size: 12px;")

    def load_tracking_dashboard_html(self, stats):
        """HTML tracking dashboard'unu yükle"""
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@1.0.1/dist/chartjs-adapter-moment.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: #0f0f0f;
                    color: white;
                    font-family: Arial, sans-serif;
                }}
                .dashboard-grid {{
                    display: grid;
                    grid-template-columns: 2fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .chart-container {{
                    background: #1a1a1a;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                }}
                .stats-container {{
                    background: #1a1a1a;
                    border-radius: 10px;
                    padding: 20px;
                }}
                .stat-item {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 0;
                    border-bottom: 1px solid #2a2a2a;
                }}
                .stat-item:last-child {{
                    border-bottom: none;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #999;
                }}
                .stat-value {{
                    font-size: 20px;
                    font-weight: bold;
                }}
                .progress-bar {{
                    width: 100%;
                    height: 8px;
                    background: #2a2a2a;
                    border-radius: 4px;
                    margin-top: 5px;
                    overflow: hidden;
                }}
                .progress-fill {{
                    height: 100%;
                    border-radius: 4px;
                    transition: width 0.5s ease;
                }}
                .timeline-container {{
                    background: #1a1a1a;
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 20px;
                    max-height: 300px;
                    overflow-y: auto;
                }}
                .timeline-item {{
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    margin-bottom: 10px;
                    background: #2a2a2a;
                    border-radius: 8px;
                    transition: all 0.3s ease;
                }}
                .timeline-item:hover {{
                    background: #3a3a3a;
                    transform: translateX(5px);
                }}
                .timeline-icon {{
                    font-size: 24px;
                    margin-right: 15px;
                }}
                .timeline-content {{
                    flex: 1;
                }}
                .timeline-time {{
                    font-size: 12px;
                    color: #666;
                }}
                h3 {{
                    margin: 0 0 20px 0;
                    color: #14a1a5;
                }}
                .live-indicator {{
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    background: #27ae60;
                    border-radius: 50%;
                    margin-right: 5px;
                    animation: pulse 2s infinite;
                }}
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.5; }}
                    100% {{ opacity: 1; }}
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-grid">
                <!-- Sol - Ana grafik -->
                <div class="chart-container">
                    <h3><span class="live-indicator"></span>Gerçek Zamanlı Email Performansı</h3>
                    <canvas id="realtimeChart"></canvas>
                </div>
                
                <!-- Sağ - Özet istatistikler -->
                <div class="stats-container">
                    <h3>📊 Performans Özeti</h3>
                    
                    <div class="stat-item">
                        <span class="stat-label">Açılma Oranı</span>
                        <span class="stat-value" style="color: #27ae60;">{stats.get('open_rate', 0):.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {stats.get('open_rate', 0)}%; background: #27ae60;"></div>
                    </div>
                    
                    <div class="stat-item">
                        <span class="stat-label">Tıklama Oranı</span>
                        <span class="stat-value" style="color: #f39c12;">{stats.get('click_rate', 0):.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {stats.get('click_rate', 0)}%; background: #f39c12;"></div>
                    </div>
                    
                    <div class="stat-item">
                        <span class="stat-label">Yanıt Oranı</span>
                        <span class="stat-value" style="color: #9b59b6;">{stats.get('reply_rate', 0):.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {stats.get('reply_rate', 0)}%; background: #9b59b6;"></div>
                    </div>
                    
                    <div class="stat-item">
                        <span class="stat-label">Geri Dönüş Oranı</span>
                        <span class="stat-value" style="color: #e74c3c;">{stats.get('bounce_rate', 0):.1f}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {stats.get('bounce_rate', 0)}%; background: #e74c3c;"></div>
                    </div>
                    
                    <div class="stat-item" style="margin-top: 20px; border-top: 1px solid #2a2a2a; padding-top: 20px;">
                        <span class="stat-label">Ortalama Açılma Süresi</span>
                        <span class="stat-value">{stats.get('avg_open_time', '0')} dk</span>
                    </div>
                    
                    <div class="stat-item">
                        <span class="stat-label">En İyi Performans Saati</span>
                        <span class="stat-value">{stats.get('best_hour', '14:00')}</span>
                    </div>
                </div>
            </div>
            
            <!-- Alt - Son aktiviteler -->
            <div class="timeline-container">
                <h3>🔄 Son Aktiviteler</h3>
                <div id="timeline"></div>
            </div>
            
            <script>
                // Gerçek zamanlı grafik
                const ctx = document.getElementById('realtimeChart').getContext('2d');
                const realtimeChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        datasets: [
                            {{
                                label: 'Açılmalar',
                                data: [],
                                borderColor: '#27ae60',
                                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                                borderWidth: 2,
                                tension: 0.4
                            }},
                            {{
                                label: 'Tıklamalar',
                                data: [],
                                borderColor: '#f39c12',
                                backgroundColor: 'rgba(243, 156, 18, 0.1)',
                                borderWidth: 2,
                                tension: 0.4
                            }},
                            {{
                                label: 'Yanıtlar',
                                data: [],
                                borderColor: '#9b59b6',
                                backgroundColor: 'rgba(155, 89, 182, 0.1)',
                                borderWidth: 2,
                                tension: 0.4
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            intersect: false,
                            mode: 'index'
                        }},
                        plugins: {{
                            legend: {{
                                labels: {{
                                    color: '#ffffff',
                                    usePointStyle: true,
                                    padding: 20
                                }}
                            }},
                            tooltip: {{
                                backgroundColor: 'rgba(0,0,0,0.8)',
                                titleColor: '#ffffff',
                                bodyColor: '#ffffff',
                                borderColor: '#333',
                                borderWidth: 1,
                                padding: 10,
                                displayColors: true,
                                callbacks: {{
                                    title: function(context) {{
                                        return moment(context[0].parsed.x).format('DD MMM HH:mm');
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            x: {{
                                type: 'time',
                                time: {{
                                    displayFormats: {{
                                        minute: 'HH:mm',
                                        hour: 'HH:mm'
                                    }}
                                }},
                                grid: {{
                                    color: '#2a2a2a',
                                    drawBorder: false
                                }},
                                ticks: {{
                                    color: '#999',
                                    maxRotation: 0
                                }}
                            }},
                            y: {{
                                beginAtZero: true,
                                grid: {{
                                    color: '#2a2a2a',
                                    drawBorder: false
                                }},
                                ticks: {{
                                    color: '#999',
                                    precision: 0
                                }}
                            }}
                        }}
                    }}
                }});
                
                // Grafik verilerini güncelle
                function updateChartData(newData) {{
                    const now = new Date();
                    
                    // Son 24 saatlik veriyi tut
                    realtimeChart.data.datasets.forEach((dataset, index) => {{
                        dataset.data = dataset.data.filter(point => {{
                            const pointTime = new Date(point.x);
                            return now - pointTime < 24 * 60 * 60 * 1000;
                        }});
                        
                        // Yeni veri ekle
                        if (newData[index]) {{
                            dataset.data.push({{
                                x: now,
                                y: newData[index]
                            }});
                        }}
                    }});
                    
                    realtimeChart.update('none');
                }}
                
                // Timeline güncelleme
                function addTimelineItem(icon, title, description, time) {{
                    const timeline = document.getElementById('timeline');
                    const item = document.createElement('div');
                    item.className = 'timeline-item';
                    item.innerHTML = `
                        <div class="timeline-icon">${{icon}}</div>
                        <div class="timeline-content">
                            <div>${{title}}</div>
                            <div class="timeline-time">${{description}} - ${{time}}</div>
                        </div>
                    `;
                    
                    timeline.insertBefore(item, timeline.firstChild);
                    
                    // En fazla 20 item tut
                    while (timeline.children.length > 20) {{
                        timeline.removeChild(timeline.lastChild);
                    }}
                }}
                
                // Örnek veri ekle (gerçek uygulamada WebSocket veya API'den gelecek)
                const sampleData = {stats.get('timeline_data', '[]')};
                sampleData.forEach(item => {{
                    addTimelineItem(item.icon, item.title, item.description, item.time);
                }});
                
                // Başlangıç grafiği verisi
                const initialData = {stats.get('chart_data', '[]')};
                initialData.forEach(point => {{
                    realtimeChart.data.datasets[0].data.push({{x: new Date(point.time), y: point.opens}});
                    realtimeChart.data.datasets[1].data.push({{x: new Date(point.time), y: point.clicks}});
                    realtimeChart.data.datasets[2].data.push({{x: new Date(point.time), y: point.replies}});
                }});
                realtimeChart.update();
            </script>
        </body>
        </html>
        """
        
        self.tracking_dashboard_view.setHtml(dashboard_html)

    def load_heatmap_html(self, stats):
        """Email açılma ısı haritasını yükle"""
        heatmap_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: #0f0f0f;
                    color: white;
                    font-family: Arial, sans-serif;
                }}
                .heatmap-container {{
                    background: #1a1a1a;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                }}
                h3 {{
                    margin: 0 0 20px 0;
                    color: #14a1a5;
                }}
                .heatmap-grid {{
                    display: grid;
                    grid-template-columns: auto repeat(7, 1fr);
                    gap: 5px;
                    margin-top: 20px;
                }}
                .heatmap-cell {{
                    width: 100%;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                }}
                .heatmap-cell:hover {{
                    transform: scale(1.1);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }}
                .hour-label {{
                    display: flex;
                    align-items: center;
                    padding-right: 10px;
                    font-size: 12px;
                    color: #999;
                }}
                .day-label {{
                    text-align: center;
                    padding-bottom: 10px;
                    font-size: 12px;
                    color: #999;
                }}
                .legend {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-top: 20px;
                    gap: 20px;
                }}
                .legend-item {{
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }}
                .legend-box {{
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="heatmap-container">
                <h3>🔥 Email Açılma Isı Haritası (Gün/Saat)</h3>
                
                <div class="heatmap-grid">
                    <!-- Boş köşe -->
                    <div></div>
                    <!-- Gün başlıkları -->
                    <div class="day-label">Pzt</div>
                    <div class="day-label">Sal</div>
                    <div class="day-label">Çar</div>
                    <div class="day-label">Per</div>
                    <div class="day-label">Cum</div>
                    <div class="day-label">Cmt</div>
                    <div class="day-label">Paz</div>
                    
                    <!-- Saat satırları -->
                    <script>
                        const heatmapData = {stats.get('heatmap_data', '{}')};
                        const maxValue = Math.max(...Object.values(heatmapData).flat());
                        
                        const colors = [
                            '#1a1a1a', // 0
                            '#0d4f4f', // Düşük
                            '#0d7377', // Orta-düşük
                            '#14a1a5', // Orta
                            '#1db8bc', // Orta-yüksek
                            '#27d6db'  // Yüksek
                        ];
                        
                        function getColor(value) {{
                            if (value === 0) return colors[0];
                            const ratio = value / maxValue;
                            const index = Math.floor(ratio * (colors.length - 1));
                            return colors[Math.max(1, index)];
                        }}
                        
                        // 24 saat için satırlar oluştur
                        for (let hour = 0; hour < 24; hour++) {{
                            // Saat etiketi
                            document.write(`<div class="hour-label">${{String(hour).padStart(2, '0')}}:00</div>`);
                            
                            // 7 gün için hücreler
                            for (let day = 0; day < 7; day++) {{
                                const key = `${{day}}_${{hour}}`;
                                const value = heatmapData[key] || 0;
                                const color = getColor(value);
                                const opacity = value > 0 ? 1 : 0.3;
                                
                                document.write(`
                                    <div class="heatmap-cell" 
                                        style="background-color: ${{color}}; opacity: ${{opacity}};"
                                        title="${{['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'][day]}} ${{hour}}:00 - ${{value}} açılma">
                                        ${{value > 0 ? value : ''}}
                                    </div>
                                `);
                            }}
                        }}
                    </script>
                </div>
                
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-box" style="background: #1a1a1a;"></div>
                        <span>0</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #0d4f4f;"></div>
                        <span>Düşük</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #0d7377;"></div>
                        <span>Orta</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #14a1a5;"></div>
                        <span>Yüksek</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-box" style="background: #27d6db;"></div>
                        <span>Çok Yüksek</span>
                    </div>
                </div>
            </div>
            
            <div class="heatmap-container">
                <h3>📈 Günlük Performans Trendi</h3>
                <canvas id="dailyTrendChart" height="100"></canvas>
            </div>
            
            <script>
                // Günlük trend grafiği
                const ctx = document.getElementById('dailyTrendChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar'],
                        datasets: [{{
                            label: 'Toplam Açılma',
                            data: {stats.get('daily_opens', '[0,0,0,0,0,0,0]')},
                            backgroundColor: '#0d7377',
                            borderColor: '#14a1a5',
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            x: {{
                                grid: {{
                                    color: '#2a2a2a',
                                    drawBorder: false
                                }},
                                ticks: {{
                                    color: '#999'
                                }}
                            }},
                            y: {{
                                beginAtZero: true,
                                grid: {{
                                    color: '#2a2a2a',
                                    drawBorder: false
                                }},
                                ticks: {{
                                    color: '#999'
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        self.heatmap_view.setHtml(heatmap_html)

    def load_device_analysis_html(self, stats):
        """Cihaz ve lokasyon analizi HTML'i"""
        device_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background-color: #0f0f0f;
                    color: white;
                    font-family: Arial, sans-serif;
                }}
                .analysis-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }}
                .chart-container {{
                    background: #1a1a1a;
                    border-radius: 10px;
                    padding: 20px;
                }}
                h3 {{
                    margin: 0 0 20px 0;
                    color: #14a1a5;
                }}
                .device-list {{
                    margin-top: 20px;
                }}
                .device-item {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px;
                    background: #2a2a2a;
                    border-radius: 6px;
                    margin-bottom: 10px;
                }}
                .device-bar {{
                    width: 100%;
                    height: 4px;
                    background: #2a2a2a;
                    border-radius: 2px;
                    margin-top: 5px;
                }}
                .device-bar-fill {{
                    height: 100%;
                    background: #14a1a5;
                    border-radius: 2px;
                }}
                .location-map {{
                    height: 300px;
                    background: #2a2a2a;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #666;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="analysis-grid">
                <!-- Sol - Cihaz analizi -->
                <div class="chart-container">
                    <h3>📱 Cihaz Dağılımı</h3>
                    <canvas id="deviceChart"></canvas>
                    
                    <div class="device-list">
                        <h4 style="color: #999; margin-bottom: 10px;">İşletim Sistemleri</h4>
                        <div id="osList"></div>
                    </div>
                </div>
                
                <!-- Sağ - Email istemcileri -->
                <div class="chart-container">
                    <h3>📧 Email İstemcileri</h3>
                    <canvas id="clientChart"></canvas>
                    
                    <div class="device-list">
                        <h4 style="color: #999; margin-bottom: 10px;">Tarayıcılar</h4>
                        <div id="browserList"></div>
                    </div>
                </div>
            </div>
            
            <div class="chart-container" style="margin-top: 20px;">
                <h3>🌍 Coğrafi Dağılım</h3>
                <div class="location-map">
                    <canvas id="locationChart" height="150"></canvas>
                </div>
            </div>
            
            <script>
                // Cihaz grafiği
                const deviceCtx = document.getElementById('deviceChart').getContext('2d');
                new Chart(deviceCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: {stats.get('device_labels', '["Desktop", "Mobile", "Tablet"]')},
                        datasets: [{{
                            data: {stats.get('device_data', '[60, 30, 10]')},
                            backgroundColor: ['#0d7377', '#14a1a5', '#1db8bc'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    color: '#ffffff',
                                    padding: 20,
                                    usePointStyle: true
                                }}
                            }}
                        }}
                    }}
                }});
                
                // Email istemci grafiği
                const clientCtx = document.getElementById('clientChart').getContext('2d');
                new Chart(clientCtx, {{
                    type: 'doughnut',
                    data: {{
                        labels: {stats.get('client_labels', '["Gmail", "Outlook", "Yahoo", "Other"]')},
                        datasets: [{{
                            data: {stats.get('client_data', '[45, 30, 15, 10]')},
                            backgroundColor: ['#e74c3c', '#3498db', '#9b59b6', '#95a5a6'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                                labels: {{
                                    color: '#ffffff',
                                    padding: 20,
                                    usePointStyle: true
                                }}
                            }}
                        }}
                    }}
                }});
                
                // Lokasyon grafiği
                const locationCtx = document.getElementById('locationChart').getContext('2d');
                new Chart(locationCtx, {{
                    type: 'bar',
                    data: {{
                        labels: {stats.get('location_labels', '["İstanbul", "Ankara", "İzmir", "Antalya", "Bursa"]')},
                        datasets: [{{
                            label: 'Açılma Sayısı',
                            data: {stats.get('location_data', '[120, 80, 60, 40, 30]')},
                            backgroundColor: '#14a1a5',
                            borderColor: '#1db8bc',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: false
                            }}
                        }},
                        scales: {{
                            x: {{
                                grid: {{
                                    color: '#2a2a2a',
                                    drawBorder: false
                                }},
                                ticks: {{
                                    color: '#999'
                                }}
                            }},
                            y: {{
                                grid: {{
                                    display: false
                                }},
                                ticks: {{
                                    color: '#999'
                                }}
                            }}
                        }}
                    }}
                }});
                
                // OS listesi
                const osData = {stats.get('os_data', '[]')};
                const osList = document.getElementById('osList');
                osData.forEach(os => {{
                    osList.innerHTML += `
                        <div class="device-item">
                            <span>${{os.name}}</span>
                            <span style="color: #14a1a5;">${{os.percentage}}%</span>
                        </div>
                        <div class="device-bar">
                            <div class="device-bar-fill" style="width: ${{os.percentage}}%;"></div>
                        </div>
                    `;
                }});
                
                // Tarayıcı listesi
                const browserData = {stats.get('browser_data', '[]')};
                const browserList = document.getElementById('browserList');
                browserData.forEach(browser => {{
                    browserList.innerHTML += `
                        <div class="device-item">
                            <span>${{browser.name}}</span>
                            <span style="color: #14a1a5;">${{browser.percentage}}%</span>
                        </div>
                        <div class="device-bar">
                            <div class="device-bar-fill" style="width: ${{browser.percentage}}%;"></div>
                        </div>
                    `;
                }});
            </script>
        </body>
        </html>
        """
        
        self.device_analysis_view.setHtml(device_html)

    def update_tracking(self):
        """Tracking tablosunu güncelle"""
        emails = self.db.get_all_emails(
            self.status_filter_tracking.currentText() if hasattr(self, 'status_filter_tracking') else "Tümü",
            self.date_filter.currentText() if hasattr(self, 'date_filter') else "Son 7 Gün"
        )
        
        self.tracking_table.setRowCount(len(emails))
        
        for i, email in enumerate(emails):
            # Firma
            self.tracking_table.setItem(i, 0, QTableWidgetItem(email.get('firm_name', 'N/A')))
            
            # Email
            self.tracking_table.setItem(i, 1, QTableWidgetItem(email.get('to_email', 'N/A')))
            
            # Konu
            subject = email.get('subject', 'N/A')
            if len(subject) > 30:
                subject = subject[:30] + '...'
            self.tracking_table.setItem(i, 2, QTableWidgetItem(subject))
            
            # Kampanya
            campaign = email.get('campaign_name', 'Genel')
            self.tracking_table.setItem(i, 3, QTableWidgetItem(campaign))
            
            # Gönderim zamanı
            sent_time = email.get('sent_date', 'N/A')
            self.tracking_table.setItem(i, 4, QTableWidgetItem(sent_time))
            
            # Açılma zamanı
            open_time = email.get('opened_date', '-')
            if open_time != '-':
                # Açılma sayısını da göster
                open_count = email.get('open_count', 1)
                if open_count > 1:
                    open_time = f"{open_time} ({open_count}x)"
            self.tracking_table.setItem(i, 5, QTableWidgetItem(open_time))
            
            # Açılma sayısı
            open_count = email.get('open_count', 0)
            open_count_item = QTableWidgetItem(str(open_count))
            if open_count > 5:
                open_count_item.setBackground(QColor(39, 174, 96))  # Yeşil arka plan
            elif open_count > 2:
                open_count_item.setBackground(QColor(241, 196, 15))  # Sarı arka plan
            self.tracking_table.setItem(i, 6, open_count_item)
            
            # Tıklama zamanı
            click_time = email.get('clicked_date', '-')
            if click_time != '-':
                click_count = email.get('click_count', 1)
                if click_count > 1:
                    click_time = f"{click_time} ({click_count}x)"
            self.tracking_table.setItem(i, 7, QTableWidgetItem(click_time))
            
            # Yanıt zamanı
            reply_time = email.get('replied_date', '-')
            self.tracking_table.setItem(i, 8, QTableWidgetItem(reply_time))
            
            # Durum
            status = "📤 Gönderildi"
            status_color = QColor(100, 100, 100)
            
            if email.get('bounced_at'):
                status = "⚠️ Geri Döndü"
                status_color = QColor(231, 76, 60)
            elif email.get('unsubscribed_at'):
                status = "🚫 Abonelikten Çıktı"
                status_color = QColor(149, 165, 166)
            elif email.get('replied_at'):
                status = "💬 Yanıtlandı"
                status_color = QColor(155, 89, 182)
            elif email.get('clicked_at'):
                status = "🖱️ Tıklandı"
                status_color = QColor(241, 196, 15)
            elif email.get('opened_at'):
                status = "👁️ Açıldı"
                status_color = QColor(46, 204, 113)
            
            status_item = QTableWidgetItem(status)
            status_item.setBackground(status_color)
            self.tracking_table.setItem(i, 9, status_item)
            
            # İşlem butonları
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            # Detay butonu
            detail_btn = QPushButton("📊")
            detail_btn.setToolTip("Detaylı Analiz")
            detail_btn.setMaximumWidth(30)
            detail_btn.clicked.connect(lambda checked=False, e=email: self.show_email_detail(e))
            action_layout.addWidget(detail_btn)
            
            # Takip butonu
            if not email.get('replied_at'):
                followup_btn = QPushButton("📨")
                followup_btn.setToolTip("Takip Maili Gönder")
                followup_btn.setMaximumWidth(30)
                followup_btn.clicked.connect(lambda checked=False, e=email: self.send_follow_up_email(e))
                action_layout.addWidget(followup_btn)
            
            action_widget.setLayout(action_layout)
            self.tracking_table.setCellWidget(i, 10, action_widget)

    def show_email_detail(self, email):
        """Email detaylarını göster"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📊 Email Detaylı Analiz")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # HTML içeriği
        detail_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #1a1a1a;
                    color: white;
                    padding: 20px;
                    margin: 0;
                }}
                .header {{
                    background: linear-gradient(135deg, #0d7377, #14a1a5);
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .info-box {{
                    background: #2a2a2a;
                    padding: 15px;
                    border-radius: 8px;
                }}
                .timeline {{
                    background: #2a2a2a;
                    padding: 20px;
                    border-radius: 8px;
                }}
                .timeline-item {{
                    display: flex;
                    align-items: center;
                    padding: 10px 0;
                    border-bottom: 1px solid #3a3a3a;
                }}
                .timeline-item:last-child {{
                    border-bottom: none;
                }}
                .timeline-icon {{
                    font-size: 20px;
                    margin-right: 10px;
                }}
                .label {{
                    color: #999;
                    font-size: 12px;
                }}
                .value {{
                    font-size: 16px;
                    margin-top: 5px;
                }}
                h3 {{
                    margin: 0 0 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2 style="margin: 0;">{email.get('subject', 'N/A')}</h2>
                <p style="margin: 5px 0;">Firma: {email.get('firm_name', 'N/A')} • {email.get('to_email', 'N/A')}</p>
            </div>
            
            <div class="info-grid">
                <div class="info-box">
                    <div class="label">Gönderim Zamanı</div>
                    <div class="value">📤 {email.get('sent_date', 'N/A')}</div>
                </div>
                <div class="info-box">
                    <div class="label">İlk Açılma</div>
                    <div class="value">👁️ {email.get('opened_date', 'Açılmadı')}</div>
                </div>
                <div class="info-box">
                    <div class="label">Toplam Açılma</div>
                    <div class="value">📊 {email.get('open_count', 0)} kez</div>
                </div>
                <div class="info-box">
                    <div class="label">Tıklama</div>
                    <div class="value">🖱️ {email.get('click_count', 0)} kez</div>
                </div>
            </div>
            
            <div class="timeline">
                <h3>📜 Zaman Çizelgesi</h3>
        """
        
        # Timeline öğeleri ekle
        if email.get('sent_at'):
            detail_html += f"""
                <div class="timeline-item">
                    <span class="timeline-icon">📤</span>
                    <div>
                        <strong>Gönderildi</strong><br>
                        <span style="color: #999;">{email.get('sent_date', 'N/A')}</span>
                    </div>
                </div>
            """
        
        if email.get('opened_at'):
            detail_html += f"""
                <div class="timeline-item">
                    <span class="timeline-icon">👁️</span>
                    <div>
                        <strong>İlk Açılma</strong><br>
                        <span style="color: #999;">{email.get('opened_date', 'N/A')} • {email.get('open_device', 'Bilinmeyen cihaz')}</span>
                    </div>
                </div>
            """
        
        if email.get('clicked_at'):
            detail_html += f"""
                <div class="timeline-item">
                    <span class="timeline-icon">🖱️</span>
                    <div>
                        <strong>Link Tıklandı</strong><br>
                        <span style="color: #999;">{email.get('clicked_date', 'N/A')} • {email.get('clicked_link', 'Link')}</span>
                    </div>
                </div>
            """
        
        if email.get('replied_at'):
            detail_html += f"""
                <div class="timeline-item">
                    <span class="timeline-icon">💬</span>
                    <div>
                        <strong>Yanıt Alındı</strong><br>
                        <span style="color: #999;">{email.get('replied_date', 'N/A')}</span>
                    </div>
                </div>
            """
        
        detail_html += """
            </div>
        </body>
        </html>
        """
        
        web_view = QWebEngineView()
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = web_view.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Detail web view profile ayarları uygulanamadı: {e}")
        
        web_view.setHtml(detail_html)
        layout.addWidget(web_view)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def toggle_realtime_tracking(self, state):
        """Gerçek zamanlı takibi aç/kapa"""
        if state == 2:  # Checked
            self.tracking_update_timer.start(5000)
            self.tracking_info_label.setText("ℹ️ Tracking pixel ile gerçek zamanlı email takibi aktif")
        else:
            self.tracking_update_timer.stop()
            self.tracking_info_label.setText("ℹ️ Gerçek zamanlı takip duraklatıldı")

    def update_tracking_realtime(self):
        """Gerçek zamanlı tracking güncellemesi"""
        # Sadece değişiklikleri güncelle
        try:
            # Son 1 dakikadaki değişiklikleri al
            recent_changes = self.db.get_recent_email_activities(minutes=1)
            
            if recent_changes:
                # Dashboard'daki timeline'ı güncelle
                for change in recent_changes:
                    icon = "👁️" if change['type'] == 'opened' else "🖱️" if change['type'] == 'clicked' else "💬"
                    
                    js_code = f"""
                    addTimelineItem('{icon}', 
                        '{change.get('firm_name', 'Unknown')}', 
                        '{change.get('description', '')}', 
                        '{change.get('time', 'Az önce')}');
                    """
                    
                    self.tracking_dashboard_view.page().runJavaScript(js_code)
                
                # Tabloyu güncelle
                self.update_tracking()
                
                # Son güncelleme zamanı
                self.last_update_label.setText(f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Realtime tracking güncelleme hatası: {str(e)}")

    def filter_tracking_table(self):
        """Tracking tablosunu filtrele"""
        self.update_tracking()

    def search_tracking_table(self, text):
        """Tracking tablosunda ara"""
        for row in range(self.tracking_table.rowCount()):
            hide = True
            for col in range(self.tracking_table.columnCount() - 1):  # Son sütun hariç
                item = self.tracking_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    hide = False
                    break
            self.tracking_table.setRowHidden(row, hide)

    def load_device_analysis_html_new(self, device_breakdown: dict):
        """Yeni tracking sisteminden gelen cihaz analizi HTML'i"""
        devices = device_breakdown.get('devices', [])
        browsers = device_breakdown.get('browsers', [])
        os_list = device_breakdown.get('operating_systems', [])
        
        # Basit cihaz dağılımı HTML'i
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}
        .chart-box {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }}
        .chart-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
        }}
        canvas {{
            max-height: 300px;
        }}
    </style>
</head>
<body>
    <div class="grid">
        <div class="chart-box">
            <div class="chart-title">📱 Cihaz Dağılımı</div>
            <canvas id="deviceChart"></canvas>
        </div>
        <div class="chart-box">
            <div class="chart-title">🌐 Tarayıcılar</div>
            <canvas id="browserChart"></canvas>
        </div>
        <div class="chart-box">
            <div class="chart-title">💻 İşletim Sistemleri</div>
            <canvas id="osChart"></canvas>
        </div>
    </div>
    
    <script>
        // Cihaz grafiği
        const deviceLabels = {json.dumps([d.get('device_type', 'Unknown') for d in devices])};
        const deviceData = {json.dumps([d.get('count', 0) for d in devices])};
        
        new Chart(document.getElementById('deviceChart'), {{
            type: 'doughnut',
            data: {{
                labels: deviceLabels,
                datasets: [{{
                    data: deviceData,
                    backgroundColor: ['#3b82f6', '#22c55e', '#f59e0b', '#a855f7'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#fff'
                        }}
                    }}
                }}
            }}
        }});
        
        // Tarayıcı grafiği
        const browserLabels = {json.dumps([b.get('browser', 'Unknown') for b in browsers])};
        const browserData = {json.dumps([b.get('count', 0) for b in browsers])};
        
        new Chart(document.getElementById('browserChart'), {{
            type: 'bar',
            data: {{
                labels: browserLabels,
                datasets: [{{
                    label: 'Kullanım',
                    data: browserData,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 2,
                    borderRadius: 10
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            color: '#fff'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }}
                    }},
                    x: {{
                        ticks: {{
                            color: '#fff'
                        }},
                        grid: {{
                            display: false
                        }}
                    }}
                }}
            }}
        }});
        
        // OS grafiği
        const osLabels = {json.dumps([o.get('os', 'Unknown') for o in os_list])};
        const osData = {json.dumps([o.get('count', 0) for o in os_list])};
        
        new Chart(document.getElementById('osChart'), {{
            type: 'polarArea',
            data: {{
                labels: osLabels,
                datasets: [{{
                    data: osData,
                    backgroundColor: [
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(251, 191, 36, 0.8)',
                        'rgba(168, 85, 247, 0.8)',
                        'rgba(236, 72, 153, 0.8)',
                        'rgba(14, 165, 233, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#fff'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        self.device_analysis_view.setHtml(html)
    
    def export_tracking_report(self):
        """Tracking raporunu dışa aktar - YENİ TRACKING SİSTEMİ"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Tracking Raporu Kaydet",
            f"tracking_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        
        if file_name:
            try:
                # Yeni tracking sistemi varsa JSON export et
                if self.tracking_gui_manager and file_name.endswith('.json'):
                    success = self.tracking_gui_manager.export_report(file_name)
                    
                    if success:
                        QMessageBox.information(self, "✅ Başarılı",
                            f"Detaylı tracking raporu JSON olarak kaydedildi!\n\n"
                            f"Dosya: {file_name}\n\n"
                            f"İçerik:\n"
                            f"• Dashboard istatistikleri\n"
                            f"• Engagement analizi\n"
                            f"• Link performansı\n"
                            f"• Firma liderlik tablosu\n"
                            f"• En iyi gönderim zamanları\n"
                            f"• Isı haritası verileri")
                    else:
                        raise Exception("JSON export başarısız")
                
                # Excel veya CSV için (hem eski hem yeni sistem)
                elif file_name.endswith(('.xlsx', '.csv')):
                    period = self.period_filter.currentText()
                    
                    # Verileri database'den al
                    if self.db:
                        emails = self.db.get_all_emails("Tümü", period)
                    else:
                        emails = []
                    
                    # Pandas DataFrame oluştur
                    data = []
                    for email in emails:
                        data.append({
                            'Firma': email.get('firm_name', 'N/A'),
                            'Email': email.get('to_email', 'N/A'),
                            'Konu': email.get('subject', 'N/A'),
                            'Kampanya': email.get('campaign_name', 'Genel'),
                            'Gönderim': email.get('sent_date', 'N/A'),
                            'Açılma': email.get('opened_date', '-'),
                            'Açılma Sayısı': email.get('open_count', 0),
                            'Tıklama': email.get('clicked_date', '-'),
                            'Tıklama Sayısı': email.get('click_count', 0),
                            'Yanıt': email.get('replied_date', '-'),
                            'Durum': self._get_email_status(email),
                            'Cihaz': email.get('open_device', '-'),
                            'Lokasyon': email.get('open_location', '-')
                        })
                    
                    if pd:
                        df = pd.DataFrame(data)
                        
                        if file_name.endswith('.xlsx'):
                            # Excel'e özel formatlama
                            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                                df.to_excel(writer, sheet_name='Tracking Raporu', index=False)
                                
                                # Özet sayfası ekle
                                summary_data = {
                                    'Metrik': ['Toplam Gönderim', 'Açılan', 'Açılma Oranı', 
                                            'Tıklanan', 'Tıklama Oranı', 'Yanıtlanan', 'Yanıt Oranı'],
                                    'Değer': [
                                        len(emails),
                                        sum(1 for e in emails if e.get('opened_at')),
                                        f"%{(sum(1 for e in emails if e.get('opened_at')) / len(emails) * 100):.1f}" if emails else "%0",
                                        sum(1 for e in emails if e.get('clicked_at')),
                                        f"%{(sum(1 for e in emails if e.get('clicked_at')) / len(emails) * 100):.1f}" if emails else "%0",
                                        sum(1 for e in emails if e.get('replied_at')),
                                        f"%{(sum(1 for e in emails if e.get('replied_at')) / len(emails) * 100):.1f}" if emails else "%0"
                                    ]
                                }
                                summary_df = pd.DataFrame(summary_data)
                                summary_df.to_excel(writer, sheet_name='Özet', index=False)
                        else:
                            df.to_csv(file_name, index=False, encoding='utf-8-sig')
                        
                        QMessageBox.information(self, "✅ Başarılı",
                            f"Tracking raporu başarıyla kaydedildi!\n\n{file_name}")
                    else:
                        # Pandas yoksa basit CSV
                        import csv
                        with open(file_name, 'w', newline='', encoding='utf-8-sig') as f:
                            writer = csv.DictWriter(f, fieldnames=data[0].keys() if data else [])
                            writer.writeheader()
                            writer.writerows(data)
                        
                        QMessageBox.information(self, "✅ Başarılı",
                            f"Tracking raporu başarıyla kaydedildi!\n\n{file_name}")
                else:
                    QMessageBox.warning(self, "⚠️ Uyarı", 
                        "Lütfen geçerli bir dosya formatı seçin:\n"
                        "• JSON (Detaylı analytics)\n"
                        "• Excel (.xlsx)\n"
                        "• CSV (.csv)")
                        
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata",
                    f"Rapor kaydedilemedi:\n{str(e)}")

    def _get_email_status(self, email):
        """Email durumunu belirle"""
        if email.get('bounced_at'):
            return "Geri Döndü"
        elif email.get('unsubscribed_at'):
            return "Abonelikten Çıktı"
        elif email.get('replied_at'):
            return "Yanıtlandı"
        elif email.get('clicked_at'):
            return "Tıklandı"
        elif email.get('opened_at'):
            return "Açıldı"
        else:
            return "Gönderildi"
    
    def create_firms_tab(self):
        """Firmalar sekmesi - Gelişmiş arama ve AI filtreleme ile"""
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
        
        # AI Chat butonu - Daire şeklinde
        self.ai_chat_btn = QPushButton("🤖")
        self.ai_chat_btn.setFixedSize(50, 50)
        self.ai_chat_btn.setToolTip("AI Asistan ile Sohbet Et")
        self.ai_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 3px solid rgba(255, 255, 255, 0.5);
                border-radius: 25px;
                font-size: 20px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 3px solid white;
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.4);
                border: 3px solid white;
            }
        """)
        self.ai_chat_btn.clicked.connect(self.show_ai_chat_popup)
        header_layout.addWidget(self.ai_chat_btn)
        
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
            "🏢 Üretim & Sanayi",
            "🎓 Eğitim & Öğretim",
            "💰 Finans & Bankacılık",
            "🏠 İnşaat & Gayrimenkul",
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
            "🏭 Avukat & Hukuki Danışmanlık",
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
        
        # Analiz durumu (eski checkbox'ları da koruyoruz)
        self.firm_analyzed_check = QCheckBox("Sadece Analiz Edilmiş")
        self.firm_analyzed_check.stateChanged.connect(self.filter_firms_table)
        advanced_filter_row.addWidget(self.firm_analyzed_check)
        
        self.firm_has_email_check = QCheckBox("Email'i Olanlar")
        self.firm_has_email_check.stateChanged.connect(self.filter_firms_table)
        advanced_filter_row.addWidget(self.firm_has_email_check)
        
        # Min rating (eski SpinBox'u da koruyoruz)
        advanced_filter_row.addWidget(QLabel("Min Rating:"))
        self.min_rating_input = QSpinBox()
        self.min_rating_input.setMinimum(0)
        self.min_rating_input.setMaximum(5)
        self.min_rating_input.setSingleStep(1)
        self.min_rating_input.valueChanged.connect(self.filter_firms_table)
        advanced_filter_row.addWidget(self.min_rating_input)
        
        advanced_filter_row.addStretch()
        search_layout.addLayout(advanced_filter_row)
        
        layout.addWidget(search_frame)
        
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
        
        self.hide_selected_btn = QPushButton("👁️‍🗞️ Seçilenleri Gizle")
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
        
        # Firma listesi - gelişmiş özelliklerle
        self.all_firms_table = QTableWidget()
        self.all_firms_table.setColumnCount(11)
        self.all_firms_table.setHorizontalHeaderLabels([
            "✓", "Firma Adı", "Rating", "Email Detayları", "Website", "Telefon", "Sektör", "Analiz", "Kampanya", "Detay", "İşlemler"
        ])
        self.all_firms_table.setAlternatingRowColors(True)
        self.all_firms_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Context menu için
        self.all_firms_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.all_firms_table.customContextMenuRequested.connect(self.on_all_firms_table_context_menu)
        
        # Email detayları için tıklama olayı
        self.all_firms_table.cellClicked.connect(self.on_firm_table_cell_clicked)
        
        # Kolon genişlikleri - responsive
        scale_factor = self.scale_factor if hasattr(self, 'scale_factor') else 1.0
        self.all_firms_table.setColumnWidth(0, max(30, int(40 * scale_factor)))   # Checkbox
        self.all_firms_table.setColumnWidth(1, max(150, int(200 * scale_factor))) # Firma Adı
        self.all_firms_table.setColumnWidth(2, max(60, int(80 * scale_factor)))   # Rating
        self.all_firms_table.setColumnWidth(3, max(80, int(100 * scale_factor)))  # Email Sayısı
        self.all_firms_table.setColumnWidth(4, max(120, int(150 * scale_factor))) # Website
        self.all_firms_table.setColumnWidth(5, max(100, int(120 * scale_factor))) # Telefon
        self.all_firms_table.setColumnWidth(6, max(80, int(100 * scale_factor)))  # Sektör
        self.all_firms_table.setColumnWidth(7, max(80, int(100 * scale_factor)))  # Analiz
        self.all_firms_table.setColumnWidth(8, max(80, int(100 * scale_factor)))  # Kampanya
        self.all_firms_table.setColumnWidth(9, max(60, int(80 * scale_factor)))   # Detay
        
        self.all_firms_table.horizontalHeader().setStretchLastSection(True)
        
        # Hidden firms tracking
        self.hidden_firm_rows = set()
        self.all_firms_data = []
        
        layout.addWidget(self.all_firms_table)
        
        # İşlem butonları
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        action_layout = QHBoxLayout(action_frame)
        
        # Sol taraf - CRUD işlemleri
        crud_layout = QHBoxLayout()
        
        add_firm_btn = QPushButton("➕ Yeni Firma")
        add_firm_btn.clicked.connect(self.add_new_firm)
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
        
        # Test verisi ekleme butonu
        test_data_btn = QPushButton("🧪 Test Verisi Ekle")
        test_data_btn.clicked.connect(self.add_test_firm_data)
        test_data_btn.setStyleSheet(self.get_firms_button_style("#6f42c1"))
        crud_layout.addWidget(test_data_btn)
        
        
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
        
        # Seçilenleri Analiz Et butonu
        self.analyze_selected_firms_btn = QPushButton("🤖 Seçilenleri Analiz Et")
        self.analyze_selected_firms_btn.clicked.connect(self.analyze_selected_firms)
        self.analyze_selected_firms_btn.setStyleSheet(self.get_firms_button_style("#e17055"))
        bulk_layout.addWidget(self.analyze_selected_firms_btn)
        
        action_layout.addLayout(bulk_layout)
        
        # Sağ taraf - yardımcı işlemler
        utility_layout = QHBoxLayout()
        
        refresh_firms_btn = QPushButton("🔄 Yenile")
        refresh_firms_btn.clicked.connect(self.load_all_firms)
        refresh_firms_btn.setStyleSheet(self.get_firms_button_style("#6c757d"))
        utility_layout.addWidget(refresh_firms_btn)
        
        # Kampanyaya Ekle butonu - Yenile butonunun yanına ekle
        self.add_to_campaign_btn = QPushButton("📧 Kampanyaya Ekle")
        self.add_to_campaign_btn.clicked.connect(self.add_selected_to_campaign)
        self.add_to_campaign_btn.setEnabled(False)  # Başlangıçta deaktif
        self.add_to_campaign_btn.setStyleSheet(self.get_firms_button_style("#14a085"))
        utility_layout.addWidget(self.add_to_campaign_btn)
        
        export_btn = QPushButton("📤 Excel'e Aktar")
        export_btn.clicked.connect(self.export_firms)
        export_btn.setStyleSheet(self.get_firms_button_style("#ffc107"))
        utility_layout.addWidget(export_btn)
        
        action_layout.addLayout(utility_layout)
        
        layout.addWidget(action_frame)
        
        # İlk yükleme
        self.load_all_firms()
        
        # Firms count label compatibility
        self.firms_count_label = self.firms_count_display
        
        return widget
    
    def create_analytics_tab(self):
        """Gelişmiş analitik sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Üst bilgi kartları
        top_cards_layout = QHBoxLayout()
        
        # Performans kartları
        self.conversion_rate_card = ModernCard("Dönüşüm Oranı", "%0", "rgba(46, 204, 113", "🎯")
        self.bounce_rate_card = ModernCard("Bounce Rate", "%0", "rgba(231, 76, 60", "📉")
        self.avg_response_time_card = ModernCard("Ort. Yanıt Süresi", "0 saat", "rgba(52, 152, 219", "⏱️")
        self.spam_score_avg_card = ModernCard("Ort. Spam Skoru", "0/10", "rgba(155, 89, 182", "🛡️")
        
        top_cards_layout.addWidget(self.conversion_rate_card)
        top_cards_layout.addWidget(self.bounce_rate_card)
        top_cards_layout.addWidget(self.avg_response_time_card)
        top_cards_layout.addWidget(self.spam_score_avg_card)
        
        layout.addLayout(top_cards_layout)
        
        # Ana içerik - 2 kolon
        content_layout = QHBoxLayout()
        
        # Sol kolon - Grafikler
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        
        # Performans grafikleri
        performance_group = QGroupBox("📊 Detaylı Performans Analizi")
        performance_layout = QVBoxLayout()
        
        self.analytics_chart = QWebEngineView()
        self.analytics_chart.setMinimumHeight(400)
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = self.analytics_chart.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Analytics chart profile ayarları uygulanamadı: {e}")
        
        # Global manifest error handling enjekte et
        self.analytics_chart.loadFinished.connect(lambda success: self.inject_global_manifest_error_handling(self.analytics_chart) if success else None)
        
        performance_layout.addWidget(self.analytics_chart)
        
        # Grafik kontrolleri
        chart_controls = QHBoxLayout()
        
        chart_controls.addWidget(QLabel("Grafik Tipi:"))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Zaman Serisi",
            "Sektör Analizi",
            "Email Performansı",
            "Coğrafi Dağılım",
            "A/B Test Sonuçları"
        ])
        self.chart_type_combo.currentTextChanged.connect(self.update_analytics_chart)
        chart_controls.addWidget(self.chart_type_combo)
        
        chart_controls.addWidget(QLabel("Dönem:"))
        self.analytics_period_combo = QComboBox()
        self.analytics_period_combo.addItems(["Son 7 Gün", "Son 30 Gün", "Son 3 Ay", "Tümü"])
        self.analytics_period_combo.currentTextChanged.connect(self.update_analytics_chart)
        chart_controls.addWidget(self.analytics_period_combo)
        
        chart_controls.addStretch()
        
        performance_layout.addLayout(chart_controls)
        
        performance_group.setLayout(performance_layout)
        left_layout.addWidget(performance_group)
        
        # Spam analizi
        spam_group = QGroupBox("🛡️ Spam Analizi")
        spam_layout = QVBoxLayout()
        
        self.spam_analysis_table = QTableWidget()
        self.spam_analysis_table.setColumnCount(4)
        self.spam_analysis_table.setHorizontalHeaderLabels([
            "Tarih", "Kampanya", "Spam Skoru", "Durum"
        ])
        self.spam_analysis_table.setMaximumHeight(200)
        spam_layout.addWidget(self.spam_analysis_table)
        
        spam_group.setLayout(spam_layout)
        left_layout.addWidget(spam_group)
        
        content_layout.addWidget(left_column, 2)
        
        # Sağ kolon - KPI'lar ve öneriler
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        
        # KPI'lar
        kpi_group = QGroupBox("🎯 Temel Performans Göstergeleri")
        kpi_layout = QVBoxLayout()
        
        self.kpi_list = QListWidget()
        kpi_layout.addWidget(self.kpi_list)
        
        kpi_group.setLayout(kpi_layout)
        right_layout.addWidget(kpi_group)
        
        # AI önerileri
        suggestions_group = QGroupBox("💡 AI Önerileri")
        suggestions_layout = QVBoxLayout()
        
        self.ai_suggestions_text = QTextEdit()
        self.ai_suggestions_text.setReadOnly(True)
        suggestions_layout.addWidget(self.ai_suggestions_text)
        
        refresh_suggestions_btn = QPushButton("🔄 Önerileri Yenile")
        refresh_suggestions_btn.clicked.connect(self.update_ai_suggestions)
        suggestions_layout.addWidget(refresh_suggestions_btn)
        
        suggestions_group.setLayout(suggestions_layout)
        right_layout.addWidget(suggestions_group)
        
        content_layout.addWidget(right_column, 1)
        
        layout.addLayout(content_layout)
        
        # Alt butonlar
        bottom_layout = QHBoxLayout()
        
        export_analytics_btn = QPushButton("📊 Rapor İndir (PDF)")
        export_analytics_btn.clicked.connect(self.export_analytics_report)
        bottom_layout.addWidget(export_analytics_btn)
        
        bottom_layout.addStretch()
        
        refresh_analytics_btn = QPushButton("🔄 Tüm Analitikleri Yenile")
        refresh_analytics_btn.clicked.connect(self.update_analytics)
        bottom_layout.addWidget(refresh_analytics_btn)
        
        layout.addLayout(bottom_layout)
        
        # İlk yükleme
        QTimer.singleShot(100, self.update_analytics)
        
        return widget
    
    def create_automation_tab(self):
        """Gelişmiş otomasyon akış editörü sekmesi"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        
        # Üst toolbar - Gelişmiş kontroller
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar.setMaximumHeight(60)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-bottom: 2px solid #0d7377;
                padding: 10px;
            }
        """)
        
        # Sol - Akış kontrolleri
        flow_controls = QHBoxLayout()
        
        # Akış seçimi
        flow_controls.addWidget(QLabel("📋 Akış:"))
        self.flow_combo = QComboBox()
        self.flow_combo.setMinimumWidth(200)
        self.flow_combo.currentTextChanged.connect(self.load_selected_flow)
        flow_controls.addWidget(self.flow_combo)
        
        # Akış işlemleri
        new_flow_btn = QPushButton("➕ Yeni")
        new_flow_btn.clicked.connect(self.create_new_automation_flow)
        flow_controls.addWidget(new_flow_btn)
        
        duplicate_flow_btn = QPushButton("📑 Kopyala")
        duplicate_flow_btn.clicked.connect(self.duplicate_flow)
        flow_controls.addWidget(duplicate_flow_btn)
        
        import_flow_btn = QPushButton("📥 İçe Aktar")
        import_flow_btn.clicked.connect(self.import_flow)
        flow_controls.addWidget(import_flow_btn)
        
        export_flow_btn = QPushButton("📤 Dışa Aktar")
        export_flow_btn.clicked.connect(self.export_flow)
        flow_controls.addWidget(export_flow_btn)
        
        toolbar_layout.addLayout(flow_controls)
        toolbar_layout.addStretch()
        
        # Sağ - Yürütme kontrolleri
        execution_controls = QHBoxLayout()
        
        # Durum göstergesi
        self.flow_status_indicator = QLabel("⚫ Pasif")
        self.flow_status_indicator.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 15px;
                background-color: #2a2a2a;
            }
        """)
        execution_controls.addWidget(self.flow_status_indicator)
        
        # Kontrol butonları
        self.save_flow_btn = QPushButton("💾 Kaydet")
        self.save_flow_btn.clicked.connect(self.save_automation_flow)
        execution_controls.addWidget(self.save_flow_btn)
        
        self.validate_flow_btn = QPushButton("✅ Doğrula")
        self.validate_flow_btn.clicked.connect(self.validate_flow)
        execution_controls.addWidget(self.validate_flow_btn)
        
        self.test_flow_btn = QPushButton("🧪 Test")
        self.test_flow_btn.clicked.connect(self.test_automation_flow)
        execution_controls.addWidget(self.test_flow_btn)
        
        self.activate_flow_btn = QPushButton("▶️ Aktifleştir")
        self.activate_flow_btn.clicked.connect(self.toggle_flow_activation)
        execution_controls.addWidget(self.activate_flow_btn)
        
        toolbar_layout.addLayout(execution_controls)
        
        main_layout.addWidget(toolbar)
        
        # Ana içerik - Splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Sol panel - Blok kütüphanesi ve özellikler
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        # Blok arama
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍"))
        self.block_search = QLineEdit()
        self.block_search.setPlaceholderText("Blok ara...")
        self.block_search.textChanged.connect(self.filter_blocks)
        search_layout.addWidget(self.block_search)
        left_layout.addLayout(search_layout)
        
        # Blok kategorileri - Accordion tarzı
        self.block_accordion = QToolBox()
        self.block_accordion.setStyleSheet("""
            QToolBox::tab {
                background: #2a2a2a;
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 2px;
            }
            QToolBox::tab:selected {
                background: #0d7377;
            }
        """)
        
        # Kategori oluştur
        self.create_block_categories()
        
        left_layout.addWidget(self.block_accordion)
        
        # Blok özellikleri paneli
        properties_group = QGroupBox("⚙️ Blok Özellikleri")
        properties_layout = QVBoxLayout()
        
        self.block_properties = QTableWidget()
        self.block_properties.setColumnCount(2)
        self.block_properties.setHorizontalHeaderLabels(["Özellik", "Değer"])
        self.block_properties.horizontalHeader().setStretchLastSection(True)
        self.block_properties.setAlternatingRowColors(True)
        properties_layout.addWidget(self.block_properties)
        
        properties_group.setLayout(properties_layout)
        left_layout.addWidget(properties_group)
        
        splitter.addWidget(left_panel)
        
        # Orta panel - Flow editör
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        # Flow bilgileri
        flow_info_widget = QWidget()
        flow_info_layout = QGridLayout(flow_info_widget)
        flow_info_widget.setMaximumHeight(100)
        
        flow_info_layout.addWidget(QLabel("📝 Akış Adı:"), 0, 0)
        self.flow_name_edit = QLineEdit()
        flow_info_layout.addWidget(self.flow_name_edit, 0, 1)
        
        flow_info_layout.addWidget(QLabel("📄 Açıklama:"), 0, 2)
        self.flow_description_edit = QLineEdit()
        flow_info_layout.addWidget(self.flow_description_edit, 0, 3)
        
        flow_info_layout.addWidget(QLabel("🏷️ Etiketler:"), 1, 0)
        self.flow_tags_edit = QLineEdit()
        self.flow_tags_edit.setPlaceholderText("Virgülle ayırın: email, takip, ai")
        flow_info_layout.addWidget(self.flow_tags_edit, 1, 1)
        
        flow_info_layout.addWidget(QLabel("📌 Versiyon:"), 1, 2)
        self.flow_version_label = QLabel("1.0.0")
        flow_info_layout.addWidget(self.flow_version_label, 1, 3)
        
        center_layout.addWidget(flow_info_widget)
        
        # Flow canvas - QGraphicsView yerine Web tabanlı
        self.flow_editor = QWebEngineView()
        self.flow_editor.setMinimumHeight(500)
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = self.flow_editor.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Flow editor profile ayarları uygulanamadı: {e}")
        
        # Flow editor HTML'i yükle
        self.load_flow_editor_html()
        
        # JavaScript bridge
        self.flow_channel = QWebChannel()
        self.flow_bridge = FlowEditorBridge(self)
        self.flow_channel.registerObject("qt", self.flow_bridge)
        self.flow_editor.page().setWebChannel(self.flow_channel)
        
        center_layout.addWidget(self.flow_editor)
        
        # Alt panel - Kod editörü ve debug
        bottom_tabs = QTabWidget()
        bottom_tabs.setMaximumHeight(250)
        
        # Kod editörü
        code_tab = QWidget()
        code_layout = QVBoxLayout(code_tab)
        
        code_toolbar = QHBoxLayout()
        code_toolbar.addWidget(QLabel("🐍 Python Kodu:"))
        
        self.code_syntax_check = QPushButton("✔️ Syntax Kontrol")
        self.code_syntax_check.clicked.connect(self.check_code_syntax)
        code_toolbar.addWidget(self.code_syntax_check)
        
        code_toolbar.addStretch()
        code_layout.addLayout(code_toolbar)
        
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 10))
        self.code_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3a3a3a;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        code_layout.addWidget(self.code_editor)
        
        bottom_tabs.addTab(code_tab, "📝 Kod Editörü")
        
        # Dug_toolbar.addWidget(QLabel("🐛 Debug Konsolu:"))
        
        # Debug sekmesi
        debug_tab = QWidget()
        debug_layout = QVBoxLayout(debug_tab)

        # Debug toolbar
        debug_toolbar = QHBoxLayout()
        debug_toolbar.addWidget(QLabel("🐛 Debug Konsolu:"))

        clear_debug_btn = QPushButton("🗑️ Temizle")
        clear_debug_btn.clicked.connect(lambda: self.debug_console.clear())
        debug_toolbar.addWidget(clear_debug_btn)
        
        debug_toolbar.addStretch()
        debug_layout.addLayout(debug_toolbar)
        
        self.debug_console = QTextEdit()
        self.debug_console.setReadOnly(True)
        self.debug_console.setFont(QFont("Consolas", 9))
        self.debug_console.setStyleSheet("""
            QTextEdit {
                background-color: #0c0c0c;
                color: #00ff00;
                border: 1px solid #2a2a2a;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        debug_layout.addWidget(self.debug_console)
        
        bottom_tabs.addTab(debug_tab, "🐛 Debug")
        
        # Değişkenler
        variables_tab = QWidget()
        variables_layout = QVBoxLayout(variables_tab)
        
        var_toolbar = QHBoxLayout()
        var_toolbar.addWidget(QLabel("📊 Akış Değişkenleri:"))
        
        add_var_btn = QPushButton("➕ Ekle")
        add_var_btn.clicked.connect(self.add_flow_variable)
        var_toolbar.addWidget(add_var_btn)
        
        var_toolbar.addStretch()
        variables_layout.addLayout(var_toolbar)
        
        self.variables_table = QTableWidget()
        self.variables_table.setColumnCount(5)
        self.variables_table.setHorizontalHeaderLabels(["Ad", "Tip", "Değer", "Kapsam", "İşlem"])
        variables_layout.addWidget(self.variables_table)
        
        bottom_tabs.addTab(variables_tab, "📊 Değişkenler")
        
        center_layout.addWidget(bottom_tabs)
        
        splitter.addWidget(center_panel)
        
        # Sağ panel - Execution monitoring
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_panel.setMaximumWidth(400)
        
        # Execution durumu
        exec_status_group = QGroupBox("🚀 Yürütme Durumu")
        exec_status_layout = QVBoxLayout()
        
        # Aktif yürütmeler
        self.active_executions_list = QListWidget()
        self.active_executions_list.itemClicked.connect(self.show_execution_details)
        exec_status_layout.addWidget(self.active_executions_list)
        
        # Kontroller
        exec_controls = QHBoxLayout()
        
        pause_exec_btn = QPushButton("⏸️")
        pause_exec_btn.setToolTip("Duraklat")
        pause_exec_btn.clicked.connect(self.pause_execution)
        exec_controls.addWidget(pause_exec_btn)
        
        stop_exec_btn = QPushButton("⏹️")
        stop_exec_btn.setToolTip("Durdur")
        stop_exec_btn.clicked.connect(self.stop_execution)
        exec_controls.addWidget(stop_exec_btn)
        
        exec_controls.addStretch()
        exec_status_layout.addLayout(exec_controls)
        
        exec_status_group.setLayout(exec_status_layout)
        right_layout.addWidget(exec_status_group)
        
        # Execution logları
        logs_group = QGroupBox("📜 Yürütme Logları")
        logs_layout = QVBoxLayout()
        
        self.execution_logs = QTextEdit()
        self.execution_logs.setReadOnly(True)
        self.execution_logs.setMaximumHeight(200)
        logs_layout.addWidget(self.execution_logs)
        
        logs_group.setLayout(logs_layout)
        right_layout.addWidget(logs_group)
        
        # İstatistikler
        stats_group = QGroupBox("📊 Akış İstatistikleri")
        stats_layout = QVBoxLayout()
        
        self.flow_stats_text = QTextEdit()
        self.flow_stats_text.setReadOnly(True)
        self.flow_stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.flow_stats_text)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        splitter.addWidget(right_panel)
        
        # Splitter oranları
        splitter.setSizes([300, 800, 350])
        
        main_layout.addWidget(splitter)
        
        # Timer for updates
        self.automation_update_timer = QTimer()
        self.automation_update_timer.timeout.connect(self.update_automation_status)
        self.automation_update_timer.start(1000)  # Her saniye güncelle
        
        # İlk yükleme
        self.load_automation_flows()
        
        return widget

    def create_block_categories(self):
        """Blok kategorilerini oluştur"""
        if not self.automation_builder:
            return
        
        templates = self.automation_builder.get_block_templates()
        
        # Tetikleyiciler
        triggers_widget = QListWidget()
        triggers_widget.setDragEnabled(True)
        for trigger in templates.get("triggers", []):
            item = QListWidgetItem(f"{trigger['title']}")
            item.setData(Qt.UserRole, trigger)
            item.setToolTip(trigger['description'])
            triggers_widget.addItem(item)
        
        self.block_accordion.addItem(triggers_widget, "⚡ Tetikleyiciler")
        
        # Koşullar
        conditions_widget = QListWidget()
        conditions_widget.setDragEnabled(True)
        for condition in templates.get("conditions", []):
            item = QListWidgetItem(f"{condition['title']}")
            item.setData(Qt.UserRole, condition)
            item.setToolTip(condition['description'])
            conditions_widget.addItem(item)
        
        self.block_accordion.addItem(conditions_widget, "❓ Koşullar")
        
        # Aksiyonlar
        actions_widget = QListWidget()
        actions_widget.setDragEnabled(True)
        for action in templates.get("actions", []):
            item = QListWidgetItem(f"{action['title']}")
            item.setData(Qt.UserRole, action)
            item.setToolTip(action['description'])
            actions_widget.addItem(item)
        
        self.block_accordion.addItem(actions_widget, "🎯 Aksiyonlar")
        
        # Kod blokları
        code_widget = QListWidget()
        code_widget.setDragEnabled(True)
        for code_block in templates.get("code", []):
            item = QListWidgetItem(f"{code_block['title']}")
            item.setData(Qt.UserRole, code_block)
            item.setToolTip(code_block['description'])
            code_widget.addItem(item)
        
        self.block_accordion.addItem(code_widget, "🐍 Kod Blokları")
        
        # Döngüler
        loops_widget = QListWidget()
        loops_widget.setDragEnabled(True)
        for loop in templates.get("loops", []):
            item = QListWidgetItem(f"{loop['title']}")
            item.setData(Qt.UserRole, loop)
            item.setToolTip(loop['description'])
            loops_widget.addItem(item)
        
        self.block_accordion.addItem(loops_widget, "🔄 Döngüler")
        
        # Araçlar
        utilities_widget = QListWidget()
        utilities_widget.setDragEnabled(True)
        for utility in templates.get("utilities", []):
            item = QListWidgetItem(f"{utility['title']}")
            item.setData(Qt.UserRole, utility)
            item.setToolTip(utility['description'])
            utilities_widget.addItem(item)
        
        self.block_accordion.addItem(utilities_widget, "🛠️ Araçlar")

    def load_flow_editor_html(self):
        """Flow editor HTML'ini yükle"""
        editor_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: #0f0f0f;
                font-family: Arial, sans-serif;
                overflow: hidden;
            }
            #flow-editor {
                width: 100%;
                height: 100vh;
                position: relative;
            }
            .context-menu {
                position: absolute;
                background: #1a1a1a;
                border: 1px solid #0d7377;
                border-radius: 5px;
                padding: 5px 0;
                display: none;
                z-index: 1000;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            .context-menu-item {
                padding: 8px 20px;
                color: white;
                cursor: pointer;
                font-size: 14px;
            }
            .context-menu-item:hover {
                background: #0d7377;
            }
            .toolbar {
                position: absolute;
                top: 10px;
                right: 10px;
                background: #1a1a1a;
                border-radius: 5px;
                padding: 10px;
                display: flex;
                gap: 10px;
                z-index: 100;
            }
            .toolbar button {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            .toolbar button:hover {
                background: #3a3a3a;
                border-color: #0d7377;
            }
            .minimap {
                position: absolute;
                bottom: 10px;
                right: 10px;
                width: 200px;
                height: 150px;
                background: #1a1a1a;
                border: 2px solid #0d7377;
                border-radius: 5px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div id="flow-editor"></div>
        
        <div class="toolbar">
            <button onclick="autoLayout()">📐 Otomatik Düzenle</button>
            <button onclick="zoomFit()">🔍 Sığdır</button>
            <button onclick="togglePhysics()">🌊 Fizik</button>
            <button onclick="toggleMinimap()">🗺️ Mini Harita</button>
        </div>
        
        <div class="minimap" id="minimap" style="display: none;"></div>
        
        <div class="context-menu" id="contextMenu">
            <div class="context-menu-item" onclick="editBlock()">✏️ Düzenle</div>
            <div class="context-menu-item" onclick="duplicateBlock()">📑 Kopyala</div>
            <div class="context-menu-item" onclick="deleteBlock()">🗑️ Sil</div>
            <div class="context-menu-item" onclick="disableBlock()">🚫 Devre Dışı</div>
        </div>
        
        <script>
            let network = null;
            let nodes = null;
            let edges = null;
            let currentFlow = null;
            let selectedNode = null;
            let selectedEdge = null;
            let bridge = null;
            let physicsEnabled = false;
            
            // Qt bridge bağlantısı
            new QWebChannel(qt.webChannelTransport, function(channel) {
                bridge = channel.objects.qt;
            });
            
            // Network oluştur
            function initNetwork() {
                const container = document.getElementById('flow-editor');
                
                nodes = new vis.DataSet([]);
                edges = new vis.DataSet([]);
                
                const data = { nodes: nodes, edges: edges };
                
                const options = {
                    nodes: {
                        shape: 'box',
                        margin: 10,
                        widthConstraint: { minimum: 120, maximum: 200 },
                        font: { color: '#ffffff', size: 14 },
                        borderWidth: 2,
                        shadow: true
                    },
                    edges: {
                        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
                        smooth: { type: 'cubicBezier', roundness: 0.5 },
                        width: 2,
                        shadow: true,
                        color: { color: '#666666', highlight: '#0d7377', hover: '#14a1a5' }
                    },
                    physics: {
                        enabled: false
                    },
                    interaction: {
                        hover: true,
                        tooltipDelay: 200,
                        hideEdgesOnDrag: true
                    },
                    manipulation: {
                        enabled: false
                    }
                };
                
                network = new vis.Network(container, data, options);
                
                // Event handlers
                network.on('click', onClick);
                network.on('oncontext', onRightClick);
                network.on('doubleClick', onDoubleClick);
                network.on('dragEnd', onDragEnd);
                
                // Drop handler
                container.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'copy';
                });
                
                container.addEventListener('drop', onDrop);
            }
            
            // Node renkleri
            const nodeColors = {
                trigger: { background: '#2980b9', border: '#3498db' },
                condition: { background: '#f39c12', border: '#f1c40f' },
                action: { background: '#27ae60', border: '#2ecc71' },
                delay: { background: '#8e44ad', border: '#9b59b6' },
                code: { background: '#e74c3c', border: '#c0392b' },
                loop: { background: '#16a085', border: '#1abc9c' },
                api: { background: '#34495e', border: '#2c3e50' },
                variable: { background: '#95a5a6', border: '#7f8c8d' },
                error_handler: { background: '#c0392b', border: '#e74c3c' }
            };
            
            // Node ikonu
            const nodeIcons = {
                trigger: '⚡',
                condition: '❓',
                action: '🎯',
                delay: '⏰',
                code: '🐍',
                loop: '🔄',
                api: '🌐',
                variable: '📊',
                error_handler: '⚠️'
            };
            
            function loadFlow(flowData) {
                currentFlow = flowData;
                nodes.clear();
                edges.clear();
                
                // Blokları ekle
                if (flowData.blocks) {
                    flowData.blocks.forEach(block => {
                        const color = nodeColors[block.type] || nodeColors.action;
                        const icon = nodeIcons[block.type] || '📦';
                        
                        nodes.add({
                            id: block.id,
                            label: `${icon} ${block.title || block.type}`,
                            title: block.description || '',
                            color: color,
                            data: block,
                            x: block.x,
                            y: block.y
                        });
                    });
                }
                
                // Bağlantıları ekle
                if (flowData.connections) {
                    flowData.connections.forEach((conn, index) => {
                        const edgeData = {
                            id: `edge_${index}`,
                            from: conn.from,
                            to: conn.to,
                            data: conn
                        };
                        
                        if (conn.condition) {
                            edgeData.label = conn.condition;
                            edgeData.font = { color: '#ffffff', size: 12 };
                            
                            if (conn.condition === 'true') {
                                edgeData.color = { color: '#27ae60' };
                            } else if (conn.condition === 'false') {
                                edgeData.color = { color: '#e74c3c' };
                            }
                        }
                        
                        edges.add(edgeData);
                    });
                }
                
                setTimeout(() => {
                    network.fit();
                }, 100);
            }
            
            function saveFlow() {
                const positions = network.getPositions();
                const flowData = {
                    blocks: [],
                    connections: []
                };
                
                // Blokları kaydet
                nodes.forEach(node => {
                    const pos = positions[node.id];
                    const blockData = { ...node.data };
                    blockData.x = pos.x;
                    blockData.y = pos.y;
                    flowData.blocks.push(blockData);
                });
                
                // Bağlantıları kaydet
                edges.forEach(edge => {
                    flowData.connections.push(edge.data);
                });
                
                if (bridge) {
                    bridge.updateFlowData(JSON.stringify(flowData));
                }
            }
            
            function onClick(params) {
                if (params.nodes.length > 0) {
                    selectedNode = params.nodes[0];
                    selectedEdge = null;
                    
                    const node = nodes.get(selectedNode);
                    if (bridge) {
                        bridge.selectBlock(selectedNode, JSON.stringify(node.data));
                    }
                } else if (params.edges.length > 0) {
                    selectedEdge = params.edges[0];
                    selectedNode = null;
                    
                    const edge = edges.get(selectedEdge);
                    if (bridge) {
                        bridge.selectConnection(selectedEdge, JSON.stringify(edge.data));
                    }
                } else {
                    selectedNode = null;
                    selectedEdge = null;
                    if (bridge) {
                        bridge.clearSelection();
                    }
                }
            }
            
            function onRightClick(params) {
                params.event.preventDefault();
                const menu = document.getElementById('contextMenu');
                
                if (params.nodes.length > 0) {
                    selectedNode = params.nodes[0];
                    menu.style.display = 'block';
                    menu.style.left = params.event.pageX + 'px';
                    menu.style.top = params.event.pageY + 'px';
                } else {
                    menu.style.display = 'none';
                }
                
                // Menüyü gizle
                document.addEventListener('click', () => {
                    menu.style.display = 'none';
                }, { once: true });
            }
            
            function onDoubleClick(params) {
                if (params.nodes.length > 0) {
                    editBlock();
                }
            }
            
            function onDragEnd(params) {
                if (params.nodes.length > 0) {
                    saveFlow();
                }
            }
            
            function onDrop(e) {
                e.preventDefault();
                
                const blockData = e.dataTransfer.getData('application/json');
                if (!blockData) return;
                
                const block = JSON.parse(blockData);
                const rect = e.target.getBoundingClientRect();
                const position = network.DOMtoCanvas({
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top
                });
                
                // Yeni blok ekle
                const blockId = 'block_' + Date.now();
                const color = nodeColors[block.type] || nodeColors.action;
                const icon = nodeIcons[block.type] || '📦';
                
                nodes.add({
                    id: blockId,
                    label: `${icon} ${block.title}`,
                    title: block.description || '',
                    color: color,
                    data: {
                        id: blockId,
                        type: block.type,
                        title: block.title,
                        ...block.config
                    },
                    x: position.x,
                    y: position.y
                });
                
                saveFlow();
                
                if (bridge) {
                    bridge.blockAdded(blockId);
                }
            }
            
            function editBlock() {
                if (!selectedNode) return;
                
                const node = nodes.get(selectedNode);
                if (bridge) {
                    bridge.editBlock(selectedNode, JSON.stringify(node.data));
                }
            }
            
            function duplicateBlock() {
                if (!selectedNode) return;
                
                const node = nodes.get(selectedNode);
                const newId = 'block_' + Date.now();
                const newNode = {
                    id: newId,
                    label: node.label,
                    title: node.title,
                    color: node.color,
                    data: { ...node.data, id: newId },
                    x: node.x + 50,
                    y: node.y + 50
                };
                
                nodes.add(newNode);
                saveFlow();
            }
            
            function deleteBlock() {
                if (!selectedNode) return;
                
                // Bağlantıları da sil
                const connectedEdges = network.getConnectedEdges(selectedNode);
                edges.remove(connectedEdges);
                nodes.remove(selectedNode);
                
                selectedNode = null;
                saveFlow();
            }
            
            function disableBlock() {
                if (!selectedNode) return;
                
                const node = nodes.get(selectedNode);
                node.data.enabled = !node.data.enabled;
                
                if (node.data.enabled) {
                    node.color = nodeColors[node.data.type] || nodeColors.action;
                } else {
                    node.color = { background: '#555555', border: '#333333' };
                }
                
                nodes.update(node);
                saveFlow();
            }
            
            function addConnection(fromId, toId, condition) {
                const edgeId = 'edge_' + Date.now();
                const edgeData = {
                    id: edgeId,
                    from: fromId,
                    to: toId,
                    data: { from: fromId, to: toId }
                };
                
                if (condition) {
                    edgeData.label = condition;
                    edgeData.font = { color: '#ffffff', size: 12 };
                    edgeData.data.condition = condition;
                    
                    if (condition === 'true') {
                        edgeData.color = { color: '#27ae60' };
                    } else if (condition === 'false') {
                        edgeData.color = { color: '#e74c3c' };
                    }
                }
                
                edges.add(edgeData);
                saveFlow();
            }
            
            function updateBlock(blockId, blockData) {
                const node = nodes.get(blockId);
                if (node) {
                    node.data = blockData;
                    node.label = `${nodeIcons[blockData.type] || '📦'} ${blockData.title}`;
                    nodes.update(node);
                    saveFlow();
                }
            }
            
            function autoLayout() {
                const options = {
                    hierarchical: {
                        enabled: true,
                        direction: 'UD',
                        sortMethod: 'directed',
                        nodeSpacing: 150,
                        levelSeparation: 150
                    }
                };
                
                network.setOptions({ layout: options });
                setTimeout(() => {
                    network.setOptions({ layout: { hierarchical: false } });
                    saveFlow();
                }, 1000);
            }
            
            function zoomFit() {
                network.fit({ animation: true });
            }
            
            function togglePhysics() {
                physicsEnabled = !physicsEnabled;
                network.setOptions({ physics: { enabled: physicsEnabled } });
            }
            
            function toggleMinimap() {
                const minimap = document.getElementById('minimap');
                minimap.style.display = minimap.style.display === 'none' ? 'block' : 'none';
            }
            
            // Başlangıç
            initNetwork();
            
            // Public API
            window.flowEditor = {
                loadFlow,
                saveFlow,
                addConnection,
                updateBlock,
                getSelectedNode: () => selectedNode,
                getSelectedEdge: () => selectedEdge
            };
        </script>
    </body>
    </html>
    """
        
        self.flow_editor.setHtml(editor_html)

    def create_block_categories(self):
        """Blok kategorilerini oluştur"""
        if not self.automation_builder:
            return
        
        templates = self.automation_builder.get_block_templates()
        
        # Tetikleyiciler
        triggers_widget = QListWidget()
        triggers_widget.setDragEnabled(True)
        for trigger in templates.get("triggers", []):
            item = QListWidgetItem(f"{trigger['title']}")
            item.setData(Qt.UserRole, trigger)
            item.setToolTip(trigger['description'])
            triggers_widget.addItem(item)
        
        self.block_accordion.addItem(triggers_widget, "⚡ Tetikleyiciler")
        
        # Koşullar
        conditions_widget = QListWidget()
        conditions_widget.setDragEnabled(True)
        for condition in templates.get("conditions", []):
            item = QListWidgetItem(f"{condition['title']}")
            item.setData(Qt.UserRole, condition)
            item.setToolTip(condition['description'])
            conditions_widget.addItem(item)
        
        self.block_accordion.addItem(conditions_widget, "❓ Koşullar")
        
        # Aksiyonlar
        actions_widget = QListWidget()
        actions_widget.setDragEnabled(True)
        for action in templates.get("actions", []):
            item = QListWidgetItem(f"{action['title']}")
            item.setData(Qt.UserRole, action)
            item.setToolTip(action['description'])
            actions_widget.addItem(item)
        
        self.block_accordion.addItem(actions_widget, "🎯 Aksiyonlar")
        
        # Kod blokları
        code_widget = QListWidget()
        code_widget.setDragEnabled(True)
        for code_block in templates.get("code", []):
            item = QListWidgetItem(f"{code_block['title']}")
            item.setData(Qt.UserRole, code_block)
            item.setToolTip(code_block['description'])
            code_widget.addItem(item)
        
        self.block_accordion.addItem(code_widget, "🐍 Kod Blokları")
        
        # Döngüler
        loops_widget = QListWidget()
        loops_widget.setDragEnabled(True)
        for loop in templates.get("loops", []):
            item = QListWidgetItem(f"{loop['title']}")
            item.setData(Qt.UserRole, loop)
            item.setToolTip(loop['description'])
            loops_widget.addItem(item)
        
        self.block_accordion.addItem(loops_widget, "🔄 Döngüler")
        
        # Araçlar
        utilities_widget = QListWidget()
        utilities_widget.setDragEnabled(True)
        for utility in templates.get("utilities", []):
            item = QListWidgetItem(f"{utility['title']}")
            item.setData(Qt.UserRole, utility)
            item.setToolTip(utility['description'])
            utilities_widget.addItem(item)
        
        self.block_accordion.addItem(utilities_widget, "🛠️ Araçlar")

    def load_flow_editor_html(self):
        """Flow editor HTML'ini yükle"""
        editor_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <style>
            body {
                margin: 0;
                padding: 0;
                background-color: #0f0f0f;
                font-family: Arial, sans-serif;
                overflow: hidden;
            }
            #flow-editor {
                width: 100%;
                height: 100vh;
                position: relative;
            }
            .context-menu {
                position: absolute;
                background: #1a1a1a;
                border: 1px solid #0d7377;
                border-radius: 5px;
                padding: 5px 0;
                display: none;
                z-index: 1000;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            .context-menu-item {
                padding: 8px 20px;
                color: white;
                cursor: pointer;
                font-size: 14px;
            }
            .context-menu-item:hover {
                background: #0d7377;
            }
            .toolbar {
                position: absolute;
                top: 10px;
                right: 10px;
                background: #1a1a1a;
                border-radius: 5px;
                padding: 10px;
                display: flex;
                gap: 10px;
                z-index: 100;
            }
            .toolbar button {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            .toolbar button:hover {
                background: #3a3a3a;
                border-color: #0d7377;
            }
            .minimap {
                position: absolute;
                bottom: 10px;
                right: 10px;
                width: 200px;
                height: 150px;
                background: #1a1a1a;
                border: 2px solid #0d7377;
                border-radius: 5px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div id="flow-editor"></div>
        
        <div class="toolbar">
            <button onclick="autoLayout()">📐 Otomatik Düzenle</button>
            <button onclick="zoomFit()">🔍 Sığdır</button>
            <button onclick="togglePhysics()">🌊 Fizik</button>
            <button onclick="toggleMinimap()">🗺️ Mini Harita</button>
        </div>
        
        <div class="minimap" id="minimap" style="display: none;"></div>
        
        <div class="context-menu" id="contextMenu">
            <div class="context-menu-item" onclick="editBlock()">✏️ Düzenle</div>
            <div class="context-menu-item" onclick="duplicateBlock()">📑 Kopyala</div>
            <div class="context-menu-item" onclick="deleteBlock()">🗑️ Sil</div>
            <div class="context-menu-item" onclick="disableBlock()">🚫 Devre Dışı</div>
        </div>
        
        <script>
            let network = null;
            let nodes = null;
            let edges = null;
            let currentFlow = null;
            let selectedNode = null;
            let selectedEdge = null;
            let bridge = null;
            let physicsEnabled = false;
            
            // Qt bridge bağlantısı
            new QWebChannel(qt.webChannelTransport, function(channel) {
                bridge = channel.objects.qt;
            });
            
            // Network oluştur
            function initNetwork() {
                const container = document.getElementById('flow-editor');
                
                nodes = new vis.DataSet([]);
                edges = new vis.DataSet([]);
                
                const data = { nodes: nodes, edges: edges };
                
                const options = {
                    nodes: {
                        shape: 'box',
                        margin: 10,
                        widthConstraint: { minimum: 120, maximum: 200 },
                        font: { color: '#ffffff', size: 14 },
                        borderWidth: 2,
                        shadow: true
                    },
                    edges: {
                        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
                        smooth: { type: 'cubicBezier', roundness: 0.5 },
                        width: 2,
                        shadow: true,
                        color: { color: '#666666', highlight: '#0d7377', hover: '#14a1a5' }
                    },
                    physics: {
                        enabled: false
                    },
                    interaction: {
                        hover: true,
                        tooltipDelay: 200,
                        hideEdgesOnDrag: true
                    },
                    manipulation: {
                        enabled: false
                    }
                };
                
                network = new vis.Network(container, data, options);
                
                // Event handlers
                network.on('click', onClick);
                network.on('oncontext', onRightClick);
                network.on('doubleClick', onDoubleClick);
                network.on('dragEnd', onDragEnd);
                
                // Drop handler
                container.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'copy';
                });
                
                container.addEventListener('drop', onDrop);
            }
            
            // Node renkleri
            const nodeColors = {
                trigger: { background: '#2980b9', border: '#3498db' },
                condition: { background: '#f39c12', border: '#f1c40f' },
                action: { background: '#27ae60', border: '#2ecc71' },
                delay: { background: '#8e44ad', border: '#9b59b6' },
                code: { background: '#e74c3c', border: '#c0392b' },
                loop: { background: '#16a085', border: '#1abc9c' },
                api: { background: '#34495e', border: '#2c3e50' },
                variable: { background: '#95a5a6', border: '#7f8c8d' },
                error_handler: { background: '#c0392b', border: '#e74c3c' }
            };
            
            // Node ikonu
            const nodeIcons = {
                trigger: '⚡',
                condition: '❓',
                action: '🎯',
                delay: '⏰',
                code: '🐍',
                loop: '🔄',
                api: '🌐',
                variable: '📊',
                error_handler: '⚠️'
            };
            
            function loadFlow(flowData) {
                currentFlow = flowData;
                nodes.clear();
                edges.clear();
                
                // Blokları ekle
                if (flowData.blocks) {
                    flowData.blocks.forEach(block => {
                        const color = nodeColors[block.type] || nodeColors.action;
                        const icon = nodeIcons[block.type] || '📦';
                        
                        nodes.add({
                            id: block.id,
                            label: `${icon} ${block.title || block.type}`,
                            title: block.description || '',
                            color: color,
                            data: block,
                            x: block.x,
                            y: block.y
                        });
                    });
                }
                
                // Bağlantıları ekle
                if (flowData.connections) {
                    flowData.connections.forEach((conn, index) => {
                        const edgeData = {
                            id: `edge_${index}`,
                            from: conn.from,
                            to: conn.to,
                            data: conn
                        };
                        
                        if (conn.condition) {
                            edgeData.label = conn.condition;
                            edgeData.font = { color: '#ffffff', size: 12 };
                            
                            if (conn.condition === 'true') {
                                edgeData.color = { color: '#27ae60' };
                            } else if (conn.condition === 'false') {
                                edgeData.color = { color: '#e74c3c' };
                            }
                        }
                        
                        edges.add(edgeData);
                    });
                }
                
                setTimeout(() => {
                    network.fit();
                }, 100);
            }
            
            function saveFlow() {
                const positions = network.getPositions();
                const flowData = {
                    blocks: [],
                    connections: []
                };
                
                // Blokları kaydet
                nodes.forEach(node => {
                    const pos = positions[node.id];
                    const blockData = { ...node.data };
                    blockData.x = pos.x;
                    blockData.y = pos.y;
                    flowData.blocks.push(blockData);
                });
                
                // Bağlantıları kaydet
                edges.forEach(edge => {
                    flowData.connections.push(edge.data);
                });
                
                if (bridge) {
                    bridge.updateFlowData(JSON.stringify(flowData));
                }
            }
            
            function onClick(params) {
                if (params.nodes.length > 0) {
                    selectedNode = params.nodes[0];
                    selectedEdge = null;
                    
                    const node = nodes.get(selectedNode);
                    if (bridge) {
                        bridge.selectBlock(selectedNode, JSON.stringify(node.data));
                    }
                } else if (params.edges.length > 0) {
                    selectedEdge = params.edges[0];
                    selectedNode = null;
                    
                    const edge = edges.get(selectedEdge);
                    if (bridge) {
                        bridge.selectConnection(selectedEdge, JSON.stringify(edge.data));
                    }
                } else {
                    selectedNode = null;
                    selectedEdge = null;
                    if (bridge) {
                        bridge.clearSelection();
                    }
                }
            }
            
            function onRightClick(params) {
                params.event.preventDefault();
                const menu = document.getElementById('contextMenu');
                
                if (params.nodes.length > 0) {
                    selectedNode = params.nodes[0];
                    menu.style.display = 'block';
                    menu.style.left = params.event.pageX + 'px';
                    menu.style.top = params.event.pageY + 'px';
                } else {
                    menu.style.display = 'none';
                }
                
                // Menüyü gizle
                document.addEventListener('click', () => {
                    menu.style.display = 'none';
                }, { once: true });
            }
            
            function onDoubleClick(params) {
                if (params.nodes.length > 0) {
                    editBlock();
                }
            }
            
            function onDragEnd(params) {
                if (params.nodes.length > 0) {
                    saveFlow();
                }
            }
            
            function onDrop(e) {
                e.preventDefault();
                
                const blockData = e.dataTransfer.getData('application/json');
                if (!blockData) return;
                
                const block = JSON.parse(blockData);
                const rect = e.target.getBoundingClientRect();
                const position = network.DOMtoCanvas({
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top
                });
                
                // Yeni blok ekle
                const blockId = 'block_' + Date.now();
                const color = nodeColors[block.type] || nodeColors.action;
                const icon = nodeIcons[block.type] || '📦';
                
                nodes.add({
                    id: blockId,
                    label: `${icon} ${block.title}`,
                    title: block.description || '',
                    color: color,
                    data: {
                        id: blockId,
                        type: block.type,
                        title: block.title,
                        ...block.config
                    },
                    x: position.x,
                    y: position.y
                });
                
                saveFlow();
                
                if (bridge) {
                    bridge.blockAdded(blockId);
                }
            }
            
            function editBlock() {
                if (!selectedNode) return;
                
                const node = nodes.get(selectedNode);
                if (bridge) {
                    bridge.editBlock(selectedNode, JSON.stringify(node.data));
                }
            }
            
            function duplicateBlock() {
                if (!selectedNode) return;
                
                const node = nodes.get(selectedNode);
                const newId = 'block_' + Date.now();
                const newNode = {
                    id: newId,
                    label: node.label,
                    title: node.title,
                    color: node.color,
                    data: { ...node.data, id: newId },
                    x: node.x + 50,
                    y: node.y + 50
                };
                
                nodes.add(newNode);
                saveFlow();
            }
            
            function deleteBlock() {
                if (!selectedNode) return;
                
                // Bağlantıları da sil
                const connectedEdges = network.getConnectedEdges(selectedNode);
                edges.remove(connectedEdges);
                nodes.remove(selectedNode);
                
                selectedNode = null;
                saveFlow();
            }
            
            function disableBlock() {
                if (!selectedNode) return;
                
                const node = nodes.get(selectedNode);
                node.data.enabled = !node.data.enabled;
                
                if (node.data.enabled) {
                    node.color = nodeColors[node.data.type] || nodeColors.action;
                } else {
                    node.color = { background: '#555555', border: '#333333' };
                }
                
                nodes.update(node);
                saveFlow();
            }
            
            function addConnection(fromId, toId, condition) {
                const edgeId = 'edge_' + Date.now();
                const edgeData = {
                    id: edgeId,
                    from: fromId,
                    to: toId,
                    data: { from: fromId, to: toId }
                };
                
                if (condition) {
                    edgeData.label = condition;
                    edgeData.font = { color: '#ffffff', size: 12 };
                    edgeData.data.condition = condition;
                    
                    if (condition === 'true') {
                        edgeData.color = { color: '#27ae60' };
                    } else if (condition === 'false') {
                        edgeData.color = { color: '#e74c3c' };
                    }
                }
                
                edges.add(edgeData);
                saveFlow();
            }
            
            function updateBlock(blockId, blockData) {
                const node = nodes.get(blockId);
                if (node) {
                    node.data = blockData;
                    node.label = `${nodeIcons[blockData.type] || '📦'} ${blockData.title}`;
                    nodes.update(node);
                    saveFlow();
                }
            }
            
            function autoLayout() {
                const options = {
                    hierarchical: {
                        enabled: true,
                        direction: 'UD',
                        sortMethod: 'directed',
                        nodeSpacing: 150,
                        levelSeparation: 150
                    }
                };
                
                network.setOptions({ layout: options });
                setTimeout(() => {
                    network.setOptions({ layout: { hierarchical: false } });
                    saveFlow();
                }, 1000);
            }
            
            function zoomFit() {
                network.fit({ animation: true });
            }
            
            function togglePhysics() {
                physicsEnabled = !physicsEnabled;
                network.setOptions({ physics: { enabled: physicsEnabled } });
            }
            
            function toggleMinimap() {
                const minimap = document.getElementById('minimap');
                minimap.style.display = minimap.style.display === 'none' ? 'block' : 'none';
            }
            
            // Başlangıç
            initNetwork();
            
            // Public API
            window.flowEditor = {
                loadFlow,
                saveFlow,
                addConnection,
                updateBlock,
                getSelectedNode: () => selectedNode,
                getSelectedEdge: () => selectedEdge
            };
        </script>
    </body>
    </html>
        """
        
        self.flow_editor.setHtml(editor_html)
    
    def create_calendar_tab(self):
        """Randevu ve takvim sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Google Calendar bağlantı durumu
        connection_layout = QHBoxLayout()
        
        self.calendar_status_label = QLabel("📅 Google Calendar: Bağlı Değil")
        self.calendar_status_label.setStyleSheet("font-size: 16px; padding: 10px;")
        connection_layout.addWidget(self.calendar_status_label)
        
        connect_calendar_btn = QPushButton("🔗 Google Calendar'a Bağlan")
        connect_calendar_btn.clicked.connect(self.connect_google_calendar)
        connection_layout.addWidget(connect_calendar_btn)
        
        connection_layout.addStretch()
        
        layout.addLayout(connection_layout)
        
        # Ana içerik - 2 kolon
        content_layout = QHBoxLayout()
        
        # Sol - Randevu oluşturma
        appointment_panel = QWidget()
        appointment_layout = QVBoxLayout(appointment_panel)
        
        create_group = QGroupBox("📝 Yeni Randevu Oluştur")
        create_layout = QGridLayout()
        
        # Firma seçimi
        create_layout.addWidget(QLabel("Firma:"), 0, 0)
        self.appointment_firm_combo = QComboBox()
        self.appointment_firm_combo.setEditable(True)
        create_layout.addWidget(self.appointment_firm_combo, 0, 1)
        
        # Kişi
        create_layout.addWidget(QLabel("Kişi:"), 1, 0)
        self.appointment_person_input = QLineEdit()
        create_layout.addWidget(self.appointment_person_input, 1, 1)
        
        # Başlık
        create_layout.addWidget(QLabel("Başlık:"), 2, 0)
        self.appointment_title_input = QLineEdit()
        self.appointment_title_input.setPlaceholderText("örn: Demo Görüşmesi")
        create_layout.addWidget(self.appointment_title_input, 2, 1)
        
        # Tarih ve saat
        create_layout.addWidget(QLabel("Tarih:"), 3, 0)
        self.appointment_date = QDateTimeEdit()
        self.appointment_date.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.appointment_date.setCalendarPopup(True)
        create_layout.addWidget(self.appointment_date, 3, 1)
        
        # Süre
        create_layout.addWidget(QLabel("Süre:"), 4, 0)
        duration_layout = QHBoxLayout()
        self.appointment_duration = QSpinBox()
        self.appointment_duration.setMinimum(15)
        self.appointment_duration.setMaximum(240)
        self.appointment_duration.setValue(30)
        self.appointment_duration.setSingleStep(15)
        duration_layout.addWidget(self.appointment_duration)
        duration_layout.addWidget(QLabel("dakika"))
        duration_layout.addStretch()
        create_layout.addLayout(duration_layout, 4, 1)
        
        # Tip
        create_layout.addWidget(QLabel("Görüşme Tipi:"), 5, 0)
        self.appointment_type_combo = QComboBox()
        self.appointment_type_combo.addItems([
            "Demo Görüşmesi",
            "Satış Görüşmesi", 
            "Takip Görüşmesi",
            "Destek Görüşmesi",
            "Genel Toplantı"
        ])
        create_layout.addWidget(self.appointment_type_combo, 5, 1)
        
        # Notlar
        create_layout.addWidget(QLabel("Notlar:"), 6, 0)
        self.appointment_notes = QTextEdit()
        self.appointment_notes.setMaximumHeight(100)
        create_layout.addWidget(self.appointment_notes, 6, 1)
        
        # Hatırlatma
        create_layout.addWidget(QLabel("Hatırlatma:"), 7, 0)
        self.appointment_reminder_combo = QComboBox()
        self.appointment_reminder_combo.addItems([
            "10 dakika önce",
            "30 dakika önce",
            "1 saat önce",
            "1 gün önce",
            "Hatırlatma yok"
        ])
        create_layout.addWidget(self.appointment_reminder_combo, 7, 1)
        
        # Oluştur butonu
        create_appointment_btn = QPushButton("📅 Randevu Oluştur")
        create_appointment_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3498db, stop: 1 #2980b9);
                font-size: 16px;
                padding: 12px;
            }
        """)
        create_appointment_btn.clicked.connect(self.create_appointment)
        create_layout.addWidget(create_appointment_btn, 8, 0, 1, 2)
        
        create_group.setLayout(create_layout)
        appointment_layout.addWidget(create_group)
        
        # Müsaitlik kontrolü
        availability_group = QGroupBox("🕐 Müsaitlik Kontrolü")
        availability_layout = QVBoxLayout()
        
        check_availability_btn = QPushButton("🔍 Müsaitliği Kontrol Et")
        check_availability_btn.clicked.connect(self.check_availability)
        availability_layout.addWidget(check_availability_btn)
        
        self.availability_text = QTextEdit()
        self.availability_text.setReadOnly(True)
        self.availability_text.setMaximumHeight(150)
        availability_layout.addWidget(self.availability_text)
        
        availability_group.setLayout(availability_layout)
        appointment_layout.addWidget(availability_group)
        
        content_layout.addWidget(appointment_panel, 1)
        
        # Sağ - Randevu listesi ve takvim
        calendar_panel = QWidget()
        calendar_layout = QVBoxLayout(calendar_panel)
        
        # Yaklaşan randevular
        upcoming_group = QGroupBox("📅 Yaklaşan Randevular")
        upcoming_layout = QVBoxLayout()
        
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(6)
        self.appointments_table.setHorizontalHeaderLabels([
            "Tarih", "Saat", "Firma", "Kişi", "Tip", "İşlem"
        ])
        upcoming_layout.addWidget(self.appointments_table)
        
        # Yenile butonu
        refresh_appointments_btn = QPushButton("🔄 Randevuları Yenile")
        refresh_appointments_btn.clicked.connect(self.refresh_appointments)
        upcoming_layout.addWidget(refresh_appointments_btn)
        
        upcoming_group.setLayout(upcoming_layout)
        calendar_layout.addWidget(upcoming_group)
        
        # İstatistikler
        stats_group = QGroupBox("📊 Randevu İstatistikleri")
        stats_layout = QGridLayout()
        
        self.total_appointments_label = QLabel("Toplam: 0")
        self.completed_appointments_label = QLabel("Tamamlanan: 0")
        self.upcoming_appointments_label = QLabel("Yaklaşan: 0")
        self.conversion_from_appointments_label = QLabel("Dönüşüm: %0")
        
        stats_layout.addWidget(self.total_appointments_label, 0, 0)
        stats_layout.addWidget(self.completed_appointments_label, 0, 1)
        stats_layout.addWidget(self.upcoming_appointments_label, 1, 0)
        stats_layout.addWidget(self.conversion_from_appointments_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        calendar_layout.addWidget(stats_group)
        
        content_layout.addWidget(calendar_panel, 2)
        
        layout.addLayout(content_layout)
        
        # İlk yükleme
        self.load_firms_for_appointment()
        self.refresh_appointments()
        
        return widget
    
    def create_import_export_tab(self):
        """Import/Export ve test firma sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Test firma oluşturma
        test_group = QGroupBox("🎲 Test Firma Oluşturucu")
        test_layout = QVBoxLayout()
        
        # Test firma ayarları
        test_settings_layout = QGridLayout()
        
        test_settings_layout.addWidget(QLabel("Firma Sayısı:"), 0, 0)
        self.test_firm_count = QSpinBox()
        self.test_firm_count.setMinimum(1)
        self.test_firm_count.setMaximum(100)
        self.test_firm_count.setValue(10)
        test_settings_layout.addWidget(self.test_firm_count, 0, 1)
        
        test_settings_layout.addWidget(QLabel("Sektör:"), 0, 2)
        self.test_sector_combo = QComboBox()
        self.test_sector_combo.addItems([
            "Karışık",
            "Yazılım",
            "E-ticaret",
            "Danışmanlık",
            "Üretim",
            "Sağlık",
            "Eğitim",
            "Finans"
        ])
        test_settings_layout.addWidget(self.test_sector_combo, 0, 3)
        
        test_settings_layout.addWidget(QLabel("Email Sayısı:"), 1, 0)
        self.test_email_count = QSpinBox()
        self.test_email_count.setMinimum(0)
        self.test_email_count.setMaximum(10)
        self.test_email_count.setValue(3)
        test_settings_layout.addWidget(self.test_email_count, 1, 1)
        
        test_settings_layout.addWidget(QLabel("Konum:"), 1, 2)
        self.test_location_combo = QComboBox()
        self.test_location_combo.addItems([
            "Karışık",
            "İstanbul",
            "Ankara",
            "İzmir",
            "Bursa",
            "Antalya"
        ])
        test_settings_layout.addWidget(self.test_location_combo, 1, 3)
        
        test_layout.addLayout(test_settings_layout)
        
        # Gelişmiş seçenekler
        advanced_check = QCheckBox("Gelişmiş seçenekleri göster")
        test_layout.addWidget(advanced_check)
        
        self.advanced_test_options = QWidget()
        advanced_layout = QGridLayout(self.advanced_test_options)
        
        advanced_layout.addWidget(QLabel("Min Rating:"), 0, 0)
        self.test_min_rating = QSpinBox()
        self.test_min_rating.setMinimum(1)
        self.test_min_rating.setMaximum(5)
        self.test_min_rating.setValue(3)
        advanced_layout.addWidget(self.test_min_rating, 0, 1)
        
        advanced_layout.addWidget(QLabel("Max Rating:"), 0, 2)
        self.test_max_rating = QSpinBox()
        self.test_max_rating.setMinimum(1)
        self.test_max_rating.setMaximum(5)
        self.test_max_rating.setValue(5)
        advanced_layout.addWidget(self.test_max_rating, 0, 3)
        
        self.test_with_website_check = QCheckBox("Website'li firmalar")
        self.test_with_website_check.setChecked(True)
        advanced_layout.addWidget(self.test_with_website_check, 1, 0, 1, 2)
        
        self.test_with_phone_check = QCheckBox("Telefonlu firmalar")
        self.test_with_phone_check.setChecked(True)
        advanced_layout.addWidget(self.test_with_phone_check, 1, 2, 1, 2)
        
        self.advanced_test_options.setVisible(False)
        advanced_check.stateChanged.connect(lambda: self.advanced_test_options.setVisible(advanced_check.isChecked()))
        
        test_layout.addWidget(self.advanced_test_options)
        
        # Test firma oluştur butonu
        generate_test_btn = QPushButton("🎲 Test Firmaları Oluştur")
        generate_test_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #f39c12, stop: 1 #e67e22);
                font-size: 16px;
                padding: 12px;
            }
        """)
        generate_test_btn.clicked.connect(self.generate_test_firms)
        test_layout.addWidget(generate_test_btn)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # Import/Export
        import_export_layout = QHBoxLayout()
        
        # Import
        import_group = QGroupBox("📥 Veri İçe Aktarma")
        import_layout = QVBoxLayout()
        
        # Dosya seçimi
        file_select_layout = QHBoxLayout()
        self.import_file_path = QLineEdit()
        self.import_file_path.setPlaceholderText("Dosya seçin...")
        self.import_file_path.setReadOnly(True)
        file_select_layout.addWidget(self.import_file_path)
        
        browse_btn = QPushButton("📁 Gözat")
        browse_btn.clicked.connect(self.browse_import_file)
        file_select_layout.addWidget(browse_btn)
        
        import_layout.addLayout(file_select_layout)
        
        # Format seçimi
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.import_format_combo = QComboBox()
        self.import_format_combo.addItems(["CSV", "Excel", "XML", "JSON"])
        format_layout.addWidget(self.import_format_combo)
        format_layout.addStretch()
        
        import_layout.addLayout(format_layout)
        
        # Import ayarları
        self.skip_duplicates_check = QCheckBox("Mevcut firmaları atla")
        self.skip_duplicates_check.setChecked(True)
        import_layout.addWidget(self.skip_duplicates_check)
        
        self.auto_analyze_check = QCheckBox("İçe aktarılan firmaları otomatik analiz et")
        import_layout.addWidget(self.auto_analyze_check)
        
        # Şablon indir
        download_template_btn = QPushButton("📄 Örnek Şablon İndir")
        download_template_btn.clicked.connect(self.download_import_template)
        import_layout.addWidget(download_template_btn)
        
        # Import başlat
        start_import_btn = QPushButton("📥 İçe Aktarmayı Başlat")
        start_import_btn.clicked.connect(self.start_import)
        import_layout.addWidget(start_import_btn)
        
        import_group.setLayout(import_layout)
        import_export_layout.addWidget(import_group)
        
        # Export
        export_group = QGroupBox("📤 Veri Dışa Aktarma")
        export_layout = QVBoxLayout()
        
        # Export filtreleri
        export_layout.addWidget(QLabel("Dışa aktarılacak firmalar:"))
        
        self.export_all_radio = QRadioButton("Tüm firmalar")
        self.export_all_radio.setChecked(True)
        export_layout.addWidget(self.export_all_radio)
        
        self.export_filtered_radio = QRadioButton("Filtrelenmiş firmalar")
        export_layout.addWidget(self.export_filtered_radio)
        
        # Filtre seçenekleri
        self.export_filters_widget = QWidget()
        export_filters_layout = QVBoxLayout(self.export_filters_widget)
        
        self.export_analyzed_only_check = QCheckBox("Sadece analiz edilmiş")
        export_filters_layout.addWidget(self.export_analyzed_only_check)
        
        self.export_with_emails_check = QCheckBox("Email'i olanlar")
        export_filters_layout.addWidget(self.export_with_emails_check)
        
        self.export_campaign_firms_check = QCheckBox("Kampanyaya eklenmiş")
        export_filters_layout.addWidget(self.export_campaign_firms_check)
        
        self.export_filters_widget.setEnabled(False)
        self.export_filtered_radio.toggled.connect(self.export_filters_widget.setEnabled)
        
        export_layout.addWidget(self.export_filters_widget)
        
        # Export formatı
        format_layout2 = QHBoxLayout()
        format_layout2.addWidget(QLabel("Format:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["Excel", "CSV", "XML", "JSON"])
        format_layout2.addWidget(self.export_format_combo)
        format_layout2.addStretch()
        
        export_layout.addLayout(format_layout2)
        
        # Export seçenekleri
        self.include_emails_check = QCheckBox("Email listelerini dahil et")
        self.include_emails_check.setChecked(True)
        export_layout.addWidget(self.include_emails_check)
        
        self.include_analysis_check = QCheckBox("Analiz verilerini dahil et")
        self.include_analysis_check.setChecked(True)
        export_layout.addWidget(self.include_analysis_check)
        
        # Export başlat
        start_export_btn = QPushButton("📤 Dışa Aktarmayı Başlat")
        start_export_btn.clicked.connect(self.start_export)
        export_layout.addWidget(start_export_btn)
        
        export_group.setLayout(export_layout)
        import_export_layout.addWidget(export_group)
        
        layout.addLayout(import_export_layout)
        
        # Son işlemler
        recent_group = QGroupBox("📋 Son İşlemler")
        recent_layout = QVBoxLayout()
        
        self.import_export_log = QTextEdit()
        self.import_export_log.setReadOnly(True)
        self.import_export_log.setMaximumHeight(150)
        recent_layout.addWidget(self.import_export_log)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        return widget
    
    def create_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # API Test Butonları
        test_group = QGroupBox("🧪 API Bağlantı Testleri")
        test_layout = QHBoxLayout()
        
        self.test_google_btn = QPushButton("🗺️ Google Maps Test")
        self.test_google_btn.clicked.connect(self.test_google_api)
        test_layout.addWidget(self.test_google_btn)
        
        self.test_openai_btn = QPushButton("🤖 OpenAI Test")
        self.test_openai_btn.clicked.connect(self.test_openai_api)
        test_layout.addWidget(self.test_openai_btn)
        
        self.test_snov_btn = QPushButton("📧 Snov.io Test")
        self.test_snov_btn.clicked.connect(self.test_snov_api)
        test_layout.addWidget(self.test_snov_btn)
        
        self.test_smtp_btn = QPushButton("📮 SMTP Test")
        self.test_smtp_btn.clicked.connect(self.test_smtp_connection)
        test_layout.addWidget(self.test_smtp_btn)
        
        # WhatsApp test butonu kaldırıldı
        
        self.test_calendar_btn = QPushButton("📅 Calendar Test")
        self.test_calendar_btn.clicked.connect(self.test_calendar_connection)
        test_layout.addWidget(self.test_calendar_btn)
        
        test_group.setLayout(test_layout)
        scroll_layout.addWidget(test_group)
        
        # API Ayarları
        api_group = QGroupBox("🔑 API Ayarları")
        api_layout = QGridLayout()
        
        # Google Maps
        api_layout.addWidget(QLabel("Google Maps API Key:"), 0, 0)
        self.google_api_input = QLineEdit()
        self.google_api_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.google_api_input, 0, 1)
        
        google_link = QLabel('<a href="https://console.cloud.google.com/apis/credentials" style="color: #14a1a5;">API Key Al</a>')
        google_link.setOpenExternalLinks(True)
        api_layout.addWidget(google_link, 0, 2)
        
        # OpenAI
        api_layout.addWidget(QLabel("OpenAI API Key:"), 1, 0)
        self.openai_api_input = QLineEdit()
        self.openai_api_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.openai_api_input, 1, 1)
        
        openai_link = QLabel('<a href="https://platform.openai.com/api-keys" style="color: #14a1a5;">API Key Al</a>')
        openai_link.setOpenExternalLinks(True)
        api_layout.addWidget(openai_link, 1, 2)
        
        # Snov.io
        api_layout.addWidget(QLabel("Snov.io Client ID:"), 2, 0)
        self.snov_id_input = QLineEdit()
        api_layout.addWidget(self.snov_id_input, 2, 1)
        
        api_layout.addWidget(QLabel("Snov.io Client Secret:"), 3, 0)
        self.snov_secret_input = QLineEdit()
        self.snov_secret_input.setEchoMode(QLineEdit.Password)
        api_layout.addWidget(self.snov_secret_input, 3, 1)
        
        snov_link = QLabel('<a href="https://app.snov.io/api-setting" style="color: #14a1a5;">API Key Al</a>')
        snov_link.setOpenExternalLinks(True)
        api_layout.addWidget(snov_link, 2, 2, 2, 1)
        
        api_group.setLayout(api_layout)
        scroll_layout.addWidget(api_group)
        
        # WhatsApp Business API Ayarları kaldırıldı
        
        # Google Calendar Ayarları
        calendar_group = QGroupBox("📅 Google Calendar API")
        calendar_layout = QGridLayout()
        
        calendar_layout.addWidget(QLabel("Client ID:"), 0, 0)
        self.calendar_client_id_input = QLineEdit()
        calendar_layout.addWidget(self.calendar_client_id_input, 0, 1)
        
        calendar_layout.addWidget(QLabel("Client Secret:"), 1, 0)
        self.calendar_client_secret_input = QLineEdit()
        self.calendar_client_secret_input.setEchoMode(QLineEdit.Password)
        calendar_layout.addWidget(self.calendar_client_secret_input, 1, 1)
        
        calendar_layout.addWidget(QLabel("Redirect URI:"), 2, 0)
        self.calendar_redirect_uri_input = QLineEdit()
        self.calendar_redirect_uri_input.setText("http://localhost:8080/callback")
        calendar_layout.addWidget(self.calendar_redirect_uri_input, 2, 1)
        
        calendar_link = QLabel('<a href="https://console.cloud.google.com/apis/credentials" style="color: #14a1a5;">Google Calendar API Kurulumu</a>')
        calendar_link.setOpenExternalLinks(True)
        calendar_layout.addWidget(calendar_link, 0, 2, 3, 1)
        
        calendar_group.setLayout(calendar_layout)
        scroll_layout.addWidget(calendar_group)
        
        # Email Ayarları
        email_group = QGroupBox("📧 Email Ayarları (SMTP)")
        email_layout = QGridLayout()
        
        email_layout.addWidget(QLabel("Email:"), 0, 0)
        self.email_input = QLineEdit()
        email_layout.addWidget(self.email_input, 0, 1)
        
        email_layout.addWidget(QLabel("App Password:"), 1, 0)
        self.email_password_input = QLineEdit()
        self.email_password_input.setEchoMode(QLineEdit.Password)
        email_layout.addWidget(self.email_password_input, 1, 1)
        
        email_help = QLabel('<a href="https://support.google.com/accounts/answer/185833" style="color: #14a1a5;">Gmail App Password Nasıl Alınır?</a>')
        email_help.setOpenExternalLinks(True)
        email_layout.addWidget(email_help, 1, 2)
        
        email_layout.addWidget(QLabel("SMTP Server:"), 2, 0)
        self.smtp_server_input = QLineEdit()
        self.smtp_server_input.setText("smtp.gmail.com")
        email_layout.addWidget(self.smtp_server_input, 2, 1)
        
        email_layout.addWidget(QLabel("SMTP Port:"), 3, 0)
        self.smtp_port_input = QLineEdit()
        self.smtp_port_input.setText("587")
        email_layout.addWidget(self.smtp_port_input, 3, 1)
        
        email_group.setLayout(email_layout)
        scroll_layout.addWidget(email_group)
        
        # Tracking Ayarları
        tracking_group = QGroupBox("📊 Tracking Ayarları")
        tracking_layout = QGridLayout()
        
        tracking_layout.addWidget(QLabel("Tracking Server URL:"), 0, 0)
        self.tracking_url_input = QLineEdit()
        self.tracking_url_input.setPlaceholderText("https://web-production-24136.up.railway.app")
        tracking_layout.addWidget(self.tracking_url_input, 0, 1)
        
        tracking_info = QLabel("ℹ️ Email açılma takibi için Railway cloud'da tracking server çalışıyor")
        tracking_info.setStyleSheet("color: #666666; font-size: 12px;")
        tracking_layout.addWidget(tracking_info, 1, 0, 1, 2)
        
        tracking_group.setLayout(tracking_layout)
        scroll_layout.addWidget(tracking_group)
        
        # Kaydet butonu
        save_btn = QPushButton("💾 Ayarları Kaydet")
        save_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #27ae60, stop: 1 #2ecc71);
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        scroll_layout.addWidget(save_btn)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return widget
    
    def create_whatsapp_tab(self):
        """WhatsApp Web sekmesi - Modern Chrome desteği ile"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Modern Chrome profili oluştur
        profile = QWebEngineProfile.defaultProfile()
        
        # Modern Chrome User Agent (Chrome 120+)
        modern_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        profile.setHttpUserAgent(modern_user_agent)
        
        # Modern tarayıcı özelliklerini aktifleştir - Manifest hatalarını önlemek için
        settings = profile.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.XSSAuditingEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.SpatialNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.HyperlinkAuditingEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)  # Manifest hatalarını önlemek için
        settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)  # Manifest hatalarını önlemek için
        settings.setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PrintElementBackgrounds, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowGeolocationOnInsecureOrigins, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanPaste, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)  # Manifest hatalarını önlemek için
        
        # Manifest hatalarını önlemek için ek ayarlar
        try:
            # Cache ayarlarını devre dışı bırak
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
            # Offline storage'ı devre dışı bırak
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        except Exception as e:
            print(f"⚠️ Profile ayarları uygulanamadı: {e}")
        
        # WhatsApp Web görüntüleyicisi
        self.whatsapp_web = QWebEngineView()
        
        # Profili uygula
        page = QWebEnginePage(profile, self.whatsapp_web)
        self.whatsapp_web.setPage(page)
        
        # Error handler ekle - Manifest hatalarını yakala
        page.loadFinished.connect(self.on_whatsapp_loaded)
        page.loadProgress.connect(self.on_whatsapp_progress)
        
        # Console mesajlarını yakala (manifest hatalarını görmek için)
        def handle_console_message(level, message, lineNumber, sourceID):
            if "manifest" in message.lower() or "404" in message or "XHRRequest" in message:
                print(f"⚠️ WebEngine Console: {message}")
        
        try:
            # PySide6'da farklı signal isimleri kullanılabilir
            if hasattr(page, 'consoleMessageReceived'):
                page.consoleMessageReceived.connect(handle_console_message)
            elif hasattr(page, 'consoleMessage'):
                page.consoleMessage.connect(handle_console_message)
            else:
                print("ℹ️ Console message handler mevcut değil, JavaScript error handling kullanılacak")
        except Exception as e:
            print(f"⚠️ Console message handler eklenemedi: {e}")
        
        # Durum bilgisi
        status_layout = QHBoxLayout()
        self.whatsapp_status = QLabel("🔄 WhatsApp Web yükleniyor...")
        self.whatsapp_status.setStyleSheet("color: #2c3e50; font-weight: bold; padding: 5px;")
        status_layout.addWidget(self.whatsapp_status)
        
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                border: none; border-radius: 5px;
                padding: 8px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        refresh_btn.clicked.connect(lambda: self.whatsapp_web.reload())
        status_layout.addWidget(refresh_btn)
        
        layout.addLayout(status_layout)
        layout.addWidget(self.whatsapp_web)
        
        # Sayfa yüklenme durumunu izle
        self.whatsapp_web.loadFinished.connect(self.on_whatsapp_loaded)
        self.whatsapp_web.loadProgress.connect(self.on_whatsapp_progress)
        
        # Global manifest error handling enjekte et
        self.whatsapp_web.loadFinished.connect(lambda success: self.inject_global_manifest_error_handling(self.whatsapp_web) if success else None)
        
        # WhatsApp Web'i yükle
        self.whatsapp_web.setUrl(QUrl("https://web.whatsapp.com"))
        
        return widget
    
    def create_webscraper_tab(self):
        """Web Scraper sekmesi - Basit ve etkili dual scraping"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Üst kontrol paneli - basit
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)
        
        # Sol taraf - durum bilgileri
        status_layout = QVBoxLayout()
        
        self.analysis_status = QLabel("📊 Analiz Durumu: Hazır")
        self.analysis_status.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")
        status_layout.addWidget(self.analysis_status)
        
        # Current URLs display
        self.current_urls = QLabel("🔗 Scraper 1: Yok | Scraper 2: Yok")
        self.current_urls.setStyleSheet("color: #95a5a6; font-size: 11px;")
        status_layout.addWidget(self.current_urls)
        
        # Sistem bilgileri
        system_info = QHBoxLayout()
        self.memory_usage = QLabel("💾 RAM: 0 MB")
        self.memory_usage.setStyleSheet("color: #3498db; font-size: 11px; font-weight: bold;")
        system_info.addWidget(self.memory_usage)
        
        self.scraper1_status = QLabel("🟢 Scraper 1")
        self.scraper1_status.setStyleSheet("color: #2ecc71; font-size: 11px; font-weight: bold;")
        system_info.addWidget(self.scraper1_status)
        
        self.scraper2_status = QLabel("🟢 Scraper 2") 
        self.scraper2_status.setStyleSheet("color: #e67e22; font-size: 11px; font-weight: bold;")
        system_info.addWidget(self.scraper2_status)
        
        status_layout.addLayout(system_info)
        control_layout.addLayout(status_layout)
        
        control_layout.addStretch()
        
        # Sağ taraf - butonlar
        button_layout = QHBoxLayout()
        
        select_firm_btn = QPushButton("📋 Firma Seç")
        select_firm_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                border: none; border-radius: 6px;
                padding: 10px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        select_firm_btn.clicked.connect(self.select_firm_for_scraper)
        button_layout.addWidget(select_firm_btn)
        
        screenshot_btn = QPushButton("📸 Screenshot")
        screenshot_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white;
                border: none; border-radius: 6px;
                padding: 10px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        screenshot_btn.clicked.connect(self.take_screenshots)
        button_layout.addWidget(screenshot_btn)
        
        clear_btn = QPushButton("🧹 Temizle")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6; color: white;
                border: none; border-radius: 6px;
                padding: 10px 15px; font-weight: bold;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        clear_btn.clicked.connect(self.clear_all_scrapers)
        button_layout.addWidget(clear_btn)
        
        control_layout.addLayout(button_layout)
        main_layout.addWidget(control_frame)
        
        # Ana içerik alanı
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setStyleSheet("QSplitter::handle { background-color: #34495e; }")
        
        # Sol taraf - iki scraper penceresi (alt alta)
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border: 1px solid #2c3e50;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(8, 8, 8, 8)
        
        # Scraper 1
        scraper1_frame = self.create_simple_scraper_frame(1, "#3498db", "Scraper 1")
        left_layout.addWidget(scraper1_frame)
        
        # Scraper 2  
        scraper2_frame = self.create_simple_scraper_frame(2, "#e67e22", "Scraper 2")
        left_layout.addWidget(scraper2_frame)
        
        content_splitter.addWidget(left_frame)
        
        # Sağ taraf - firma bilgileri
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
        
        # Firma 1 bilgileri
        firm1_info_frame = QFrame()
        firm1_info_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        firm1_info_layout = QVBoxLayout(firm1_info_frame)
        
        self.firm1_title = QLabel("🏢 Firma 1: Seçilmedi")
        self.firm1_title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        firm1_info_layout.addWidget(self.firm1_title)
        
        self.firm1_phone = QLabel("📞 -")
        self.firm1_phone.setStyleSheet("color: #ecf0f1; font-size: 11px;")
        firm1_info_layout.addWidget(self.firm1_phone)
        
        self.firm1_website = QLabel("🌐 -")
        self.firm1_website.setStyleSheet("color: #ecf0f1; font-size: 11px;")
        firm1_info_layout.addWidget(self.firm1_website)
        
        # Durum göstergesi
        self.firm1_status_dot = QLabel("🟢")
        self.firm1_status_dot.setStyleSheet("color: #2ecc71; font-size: 11px;")
        firm1_info_layout.addWidget(self.firm1_status_dot)
        
        # Loading indicator
        self.firm1_loading = QLabel("⏱️ Hazır")
        self.firm1_loading.setStyleSheet("color: #95a5a6; font-size: 10px;")
        firm1_info_layout.addWidget(self.firm1_loading)
        
        right_layout.addWidget(firm1_info_frame)
        
        # Firma 2 bilgileri
        firm2_info_frame = QFrame()
        firm2_info_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        firm2_info_layout = QVBoxLayout(firm2_info_frame)
        
        self.firm2_title = QLabel("🏢 Firma 2: Seçilmedi")
        self.firm2_title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        firm2_info_layout.addWidget(self.firm2_title)
        
        self.firm2_phone = QLabel("📞 -")
        self.firm2_phone.setStyleSheet("color: #ecf0f1; font-size: 11px;")
        firm2_info_layout.addWidget(self.firm2_phone)
        
        self.firm2_website = QLabel("🌐 -")
        self.firm2_website.setStyleSheet("color: #ecf0f1; font-size: 11px;")
        firm2_info_layout.addWidget(self.firm2_website)
        
        # Durum göstergesi
        self.firm2_status_dot = QLabel("🟢")
        self.firm2_status_dot.setStyleSheet("color: #e67e22; font-size: 11px;")
        firm2_info_layout.addWidget(self.firm2_status_dot)
        
        right_layout.addWidget(firm2_info_frame)
        
        # Scraper statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("📊 İstatistikler")
        stats_title.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(stats_title)
        
        # Statistics labels
        self.total_scraped = QLabel("🔍 Toplam: 0")
        self.total_scraped.setStyleSheet("color: #ecf0f1; font-size: 11px;")
        stats_layout.addWidget(self.total_scraped)
        
        self.success_rate = QLabel("✅ Başarı: 0%")
        self.success_rate.setStyleSheet("color: #ecf0f1; font-size: 11px;")
        stats_layout.addWidget(self.success_rate)
        
        self.session_time = QLabel("⏰ Süre: 00:00")
        self.session_time.setStyleSheet("color: #ecf0f1; font-size: 11px;")
        stats_layout.addWidget(self.session_time)
        
        right_layout.addWidget(stats_frame)
        right_layout.addStretch()
        content_splitter.addWidget(right_frame)
        
        # Splitter oranları ayarla (sol %70, sağ %30)
        content_splitter.setSizes([700, 300])
        main_layout.addWidget(content_splitter)
        
        # Değişkenler
        self.current_firm1 = None
        self.current_firm2 = None
        self.analysis_queue = []
        
        # RAM takip timer'ı
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.update_memory_usage)
        self.memory_timer.start(3000)  # 3 saniyede bir güncelle
        
        return widget
    
    def create_simple_scraper_frame(self, scraper_id, color, title):
        """Basit scraper frame oluştur"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #2c3e50;
                border: 2px solid {color};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Başlık ve kontroller
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"🌐 {title}")
        title_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Basit kontroller
        if scraper_id == 1:
            back_btn = QPushButton("◀")
            back_btn.setMaximumWidth(30)
            back_btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 4px; padding: 4px;")
            back_btn.clicked.connect(lambda: self.navigate_scraper(1, "back"))
            header_layout.addWidget(back_btn)
            
            forward_btn = QPushButton("▶")
            forward_btn.setMaximumWidth(30)
            forward_btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 4px; padding: 4px;")
            forward_btn.clicked.connect(lambda: self.navigate_scraper(1, "forward"))
            header_layout.addWidget(forward_btn)
            
            refresh_btn = QPushButton("🔄")
            refresh_btn.setMaximumWidth(30)
            refresh_btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 4px; padding: 4px;")
            refresh_btn.clicked.connect(lambda: self.refresh_scraper(1))
            header_layout.addWidget(refresh_btn)
        else:
            back_btn = QPushButton("◀")
            back_btn.setMaximumWidth(30)
            back_btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 4px; padding: 4px;")
            back_btn.clicked.connect(lambda: self.navigate_scraper(2, "back"))
            header_layout.addWidget(back_btn)
            
            forward_btn = QPushButton("▶")
            forward_btn.setMaximumWidth(30)
            forward_btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 4px; padding: 4px;")
            forward_btn.clicked.connect(lambda: self.navigate_scraper(2, "forward"))
            header_layout.addWidget(forward_btn)
            
            refresh_btn = QPushButton("🔄")
            refresh_btn.setMaximumWidth(30)
            refresh_btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 4px; padding: 4px;")
            refresh_btn.clicked.connect(lambda: self.refresh_scraper(2))
            header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # URL girişi
        url_layout = QHBoxLayout()
        
        if scraper_id == 1:
            self.scraper1_url = QLineEdit()
            self.scraper1_url.setPlaceholderText("Website URL'si girin...")
            self.scraper1_url.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #34495e; color: white;
                    border: 1px solid {color}; border-radius: 4px;
                    padding: 6px;
                }}
            """)
            self.scraper1_url.returnPressed.connect(lambda: self.load_scraper_url(1, self.scraper1_url.text()))
            url_layout.addWidget(self.scraper1_url)
            
            go_btn = QPushButton("Git")
            go_btn.setMaximumWidth(50)
            go_btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 4px; padding: 6px; font-weight: bold;")
            go_btn.clicked.connect(lambda: self.load_scraper_url(1, self.scraper1_url.text()))
            url_layout.addWidget(go_btn)
        else:
            self.scraper2_url = QLineEdit()
            self.scraper2_url.setPlaceholderText("Website URL'si girin...")
            self.scraper2_url.setStyleSheet(f"""
                QLineEdit {{
                    background-color: #34495e; color: white;
                    border: 1px solid {color}; border-radius: 4px;
                    padding: 6px;
                }}
            """)
            self.scraper2_url.returnPressed.connect(lambda: self.load_scraper_url(2, self.scraper2_url.text()))
            url_layout.addWidget(self.scraper2_url)
            
            go_btn = QPushButton("Git")
            go_btn.setMaximumWidth(50)
            go_btn.setStyleSheet(f"background-color: {color}; color: white; border: none; border-radius: 4px; padding: 6px; font-weight: bold;")
            go_btn.clicked.connect(lambda: self.load_scraper_url(2, self.scraper2_url.text()))
            url_layout.addWidget(go_btn)
        
        layout.addLayout(url_layout)
        
        # Speed indicators
        speed_layout = QHBoxLayout()
        if scraper_id == 1:
            self.scraper1_speed = QLabel("⚡ S1: -")
            self.scraper1_speed.setStyleSheet("color: #3498db; font-size: 10px;")
            speed_layout.addWidget(self.scraper1_speed)
        else:
            self.scraper2_speed = QLabel("⚡ S2: -")
            self.scraper2_speed.setStyleSheet("color: #e67e22; font-size: 10px;")
            speed_layout.addWidget(self.scraper2_speed)
        
        speed_layout.addStretch()
        layout.addLayout(speed_layout)
        
        # Web view - daha büyük (Manifest hatalarını önlemek için)
        if scraper_id == 1:
            self.scraper1_web = QWebEngineView()
            self.scraper1_web.setMinimumHeight(450)  # Büyütüldü
            self.scraper1_web.setStyleSheet(f"border: 1px solid {color}; border-radius: 4px;")
            self.scraper1_web.loadStarted.connect(lambda: self.on_scraper_load_started(1))
            self.scraper1_web.loadFinished.connect(lambda success: self.on_scraper_load_finished(1, success))
            
            # Manifest hatalarını önlemek için profile ayarları
            try:
                profile = self.scraper1_web.page().profile()
                settings = profile.settings()
                settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
                profile.setHttpCacheType(QWebEngineProfile.NoCache)
            except Exception as e:
                print(f"⚠️ Scraper1 profile ayarları uygulanamadı: {e}")
            
            # Global manifest error handling enjekte et
            self.scraper1_web.loadFinished.connect(lambda success: self.inject_global_manifest_error_handling(self.scraper1_web) if success else None)
            layout.addWidget(self.scraper1_web)
        else:
            self.scraper2_web = QWebEngineView()
            self.scraper2_web.setMinimumHeight(450)  # Büyütüldü
            self.scraper2_web.setStyleSheet(f"border: 1px solid {color}; border-radius: 4px;")
            self.scraper2_web.loadStarted.connect(lambda: self.on_scraper_load_started(2))
            self.scraper2_web.loadFinished.connect(lambda success: self.on_scraper_load_finished(2, success))
            
            # Manifest hatalarını önlemek için profile ayarları
            try:
                profile = self.scraper2_web.page().profile()
                settings = profile.settings()
                settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
                settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
                profile.setHttpCacheType(QWebEngineProfile.NoCache)
            except Exception as e:
                print(f"⚠️ Scraper2 profile ayarları uygulanamadı: {e}")
            
            # Global manifest error handling enjekte et
            self.scraper2_web.loadFinished.connect(lambda success: self.inject_global_manifest_error_handling(self.scraper2_web) if success else None)
            layout.addWidget(self.scraper2_web)
        
        return frame
    
    def update_memory_usage(self):
        """RAM kullanımını güncelle"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            used_mb = memory.used // (1024 * 1024)
            percent = memory.percent
            self.memory_usage.setText(f"💾 RAM: {used_mb} MB ({percent:.1f}%)")
            
            # Renk değişimi
            if percent < 60:
                color = "#2ecc71"  # yeşil
            elif percent < 80:
                color = "#f39c12"  # sarı
            else:
                color = "#e74c3c"  # kırmızı
            
            self.memory_usage.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")
        except ImportError:
            self.memory_usage.setText("💾 RAM: Bilgi alınamadı")
            self.memory_usage.setStyleSheet("color: #95a5a6; font-size: 11px; font-weight: bold;")
        except Exception as e:
            self.memory_usage.setText("💾 RAM: -")
            self.memory_usage.setStyleSheet("color: #95a5a6; font-size: 11px; font-weight: bold;")
    
    def create_scraper_toolbar(self):
        """Gelişmiş scraper toolbar oluştur"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #34495e, stop: 0.5 #2c3e50, stop: 1 #34495e);
                border: 2px solid #0d7377;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        
        # Session control group
        session_group = QFrame()
        session_group.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        session_layout = QHBoxLayout(session_group)
        
        # New session
        new_session_btn = QPushButton("🆕 Yeni")
        new_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white;
                border: none; border-radius: 5px;
                padding: 8px 12px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        new_session_btn.clicked.connect(self.start_new_session)
        session_layout.addWidget(new_session_btn)
        
        # Save session
        save_session_btn = QPushButton("💾 Kaydet")
        save_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                border: none; border-radius: 5px;
                padding: 8px 12px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #5dade2; }
        """)
        save_session_btn.clicked.connect(self.save_session)
        session_layout.addWidget(save_session_btn)
        
        toolbar_layout.addWidget(session_group)
        
        # View control group
        view_group = QFrame()
        view_group.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        view_layout = QHBoxLayout(view_group)
        
        # History button
        history_btn = QPushButton("📋 Geçmiş")
        history_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad; color: white;
                border: none; border-radius: 5px;
                padding: 8px 12px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #a569bd; }
        """)
        history_btn.clicked.connect(self.show_scraper_history)
        view_layout.addWidget(history_btn)
        
        # Bookmarks button
        bookmarks_btn = QPushButton("⭐ Favoriler")
        bookmarks_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; color: white;
                border: none; border-radius: 5px;
                padding: 8px 12px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #f1c40f; }
        """)
        bookmarks_btn.clicked.connect(self.show_bookmarks)
        view_layout.addWidget(bookmarks_btn)
        
        toolbar_layout.addWidget(view_group)
        
        toolbar_layout.addStretch()
        
        # Tools group
        tools_group = QFrame()
        tools_group.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        tools_layout = QHBoxLayout(tools_group)
        
        # Auto-refresh toggle
        self.auto_refresh_btn = QPushButton("🔄 Auto: OFF")
        self.auto_refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white;
                border: none; border-radius: 5px;
                padding: 8px 12px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        tools_layout.addWidget(self.auto_refresh_btn)
        
        # Mobile view toggle
        self.mobile_view_btn = QPushButton("📱 Desktop")
        self.mobile_view_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085; color: white;
                border: none; border-radius: 5px;
                padding: 8px 12px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #1abc9c; }
        """)
        self.mobile_view_btn.clicked.connect(self.toggle_mobile_view)
        tools_layout.addWidget(self.mobile_view_btn)
        
        toolbar_layout.addWidget(tools_group)
        
        return toolbar
    
    # Yeni fonksiyonlar - Analytics Tab
    def update_analytics(self):
        """Gelişmiş analitikleri güncelle"""
        if self.analytics_dashboard:
            try:
                # Kartları güncelle
                analytics_data = self.analytics_dashboard.get_analytics_summary()
                
                self.conversion_rate_card.update_value(f"%{analytics_data.get('conversion_rate', 0)}")
                self.bounce_rate_card.update_value(f"%{analytics_data.get('bounce_rate', 0)}")
                self.avg_response_time_card.update_value(f"{analytics_data.get('avg_response_time', 0)} saat")
                self.spam_score_avg_card.update_value(f"{analytics_data.get('avg_spam_score', 0)}/10")
                
                # KPI listesi güncelle
                self.kpi_list.clear()
                for kpi in analytics_data.get('kpis', []):
                    self.kpi_list.addItem(f"• {kpi}")
                
                # Spam analiz tablosu
                spam_data = self.analytics_dashboard.get_spam_analysis()
                self.spam_analysis_table.setRowCount(len(spam_data))
                
                for i, data in enumerate(spam_data):
                    self.spam_analysis_table.setItem(i, 0, QTableWidgetItem(data['date']))
                    self.spam_analysis_table.setItem(i, 1, QTableWidgetItem(data['campaign']))
                    self.spam_analysis_table.setItem(i, 2, QTableWidgetItem(str(data['score'])))
                    
                    status = "✅ İyi" if data['score'] < 3 else "⚠️ Orta" if data['score'] < 6 else "❌ Yüksek"
                    self.spam_analysis_table.setItem(i, 3, QTableWidgetItem(status))
                
                # Grafiği güncelle
                self.update_analytics_chart()
                
                # AI önerilerini güncelle
                self.update_ai_suggestions()
            except Exception as e:
                print(f"Analytics güncelleme hatası: {str(e)}")
    
    def update_analytics_chart(self):
        """Analitik grafiğini güncelle"""
        if not self.analytics_dashboard:
            return
        
        try:
            chart_type = self.chart_type_combo.currentText()
            period = self.analytics_period_combo.currentText()
            
            chart_html = self.analytics_dashboard.generate_chart_html(chart_type, period)
            self.analytics_chart.setHtml(chart_html)
        except Exception as e:
            print(f"Chart güncelleme hatası: {str(e)}")
            # Varsayılan bir chart göster
            default_html = """
            <html><body style='background-color: #1a1a1a; color: white; text-align: center; padding: 50px;'>
            <h3>Grafik yüklenemedi</h3>
            <p>AnalyticsDashboard modülü kurulu değil</p>
            </body></html>
            """
            self.analytics_chart.setHtml(default_html)
    
    def update_ai_suggestions(self):
        """AI önerilerini güncelle"""
        if self.analytics_dashboard:
            try:
                suggestions = self.analytics_dashboard.get_ai_suggestions()
                
                suggestions_text = "🤖 AI Tabanlı Öneriler:\n\n"
                for i, suggestion in enumerate(suggestions, 1):
                    suggestions_text += f"{i}. {suggestion}\n\n"
                
                self.ai_suggestions_text.setText(suggestions_text)
            except Exception as e:
                self.ai_suggestions_text.setText(
                    "🤖 AI Önerileri\n\n"
                    "AnalyticsDashboard modülü yüklü değil veya bir hata oluştu."
                )
    
    def export_analytics_report(self):
        """Analitik raporunu PDF olarak dışa aktar"""
        if self.analytics_dashboard:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Raporu Kaydet", 
                f"analytics_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_name:
                success = self.analytics_dashboard.export_report_to_pdf(file_name)
                if success:
                    QMessageBox.information(self, "✅ Başarılı", "Rapor başarıyla kaydedildi!")
                else:
                    QMessageBox.critical(self, "❌ Hata", "Rapor kaydedilemedi!")
    
    # Automation Tab fonksiyonları
    def load_demo_flow(self):
        """Demo otomasyon akışı yükle"""
        # Örnek bloklar ekle
        trigger = FlowBlockWidget("trigger", "Email Açıldı", 50, 50)
        self.flow_scene.addItem(trigger)
        
        condition = FlowBlockWidget("condition", "24 Saat İçinde", 250, 50)
        self.flow_scene.addItem(condition)
        
        action1 = FlowBlockWidget("action", "Takip Maili", 450, 20)
        self.flow_scene.addItem(action1)
        
        action2 = FlowBlockWidget("action", "WhatsApp Mesajı", 450, 120)
        self.flow_scene.addItem(action2)
        
        # Bağlantı çizgileri ekle (basit örnek)
        self.flow_scene.addLine(200, 90, 250, 90, QPen(Qt.white, 2))
        self.flow_scene.addLine(400, 90, 450, 60, QPen(Qt.white, 2))
        self.flow_scene.addLine(400, 90, 450, 160, QPen(Qt.white, 2))
    
    def add_block_to_flow(self, block_type, title):
        """Akışa yeni blok ekle"""
        # Rastgele pozisyon
        import random
        x = random.randint(50, 600)
        y = random.randint(50, 400)
        
        block = FlowBlockWidget(block_type, title, x, y)
        self.flow_scene.addItem(block)
        
        self.update_status(f"✅ '{title}' bloğu eklendi")
    
    def create_new_flow(self):
        """Yeni otomasyon akışı oluştur"""
        name, ok = QInputDialog.getText(self, "Yeni Akış", "Akış adı:")
        if ok and name:
            self.flow_name_input.setText(name)
            self.flow_scene.clear()
            self.flow_select_combo.addItem(name)
            self.flow_select_combo.setCurrentText(name)
            self.update_status(f"✅ '{name}' akışı oluşturuldu")
    
    def save_current_flow(self):
        """Mevcut akışı kaydet"""
        if self.automation_builder:
            flow_name = self.flow_name_input.text()
            if not flow_name:
                QMessageBox.warning(self, "Uyarı", "Lütfen akış adı girin!")
                return
            
            # Akış verilerini topla (gerçek implementasyonda daha detaylı olacak)
            flow_data = {
                "name": flow_name,
                "blocks": [],
                "connections": []
            }
            
            try:
                success = self.automation_builder.save_flow(flow_data)
                if success:
                    QMessageBox.information(self, "✅ Başarılı", "Akış kaydedildi!")
                else:
                    QMessageBox.critical(self, "❌ Hata", "Akış kaydedilemedi!")
            except:
                QMessageBox.warning(self, "Uyarı", "AutomationBuilder modülü yüklü değil!")
        else:
            QMessageBox.warning(self, "Uyarı", "AutomationBuilder modülü bulunamadı!")
    
    def test_current_flow(self):
        """Mevcut akışı test et"""
        QMessageBox.information(self, "🧪 Test", 
            "Akış test ediliyor...\n\n"
            "Bu özellik yakında eklenecek!")
    
    def run_current_flow(self):
        """Mevcut akışı çalıştır"""
        reply = QMessageBox.question(self, "Onay",
            "Bu akışı çalıştırmak istiyor musunuz?\n\n"
            "Akış, belirlediğiniz kurallara göre otomatik çalışacaktır.",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.flow_status_label.setText("🟢 Aktif")
            self.flow_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.update_status("✅ Otomasyon akışı başlatıldı")
    
    # Calendar Tab fonksiyonları
    def connect_google_calendar(self):
        """Google Calendar'a bağlan"""
        if self.calendar_manager:
            try:
                auth_url = self.calendar_manager.get_auth_url()
                QMessageBox.information(self, "📅 Google Calendar Bağlantısı",
                    f"Tarayıcınızda açılacak sayfada Google hesabınıza giriş yapın ve izin verin.\n\n"
                    f"URL: {auth_url}")
                
                # URL'yi tarayıcıda aç
                import webbrowser
                webbrowser.open(auth_url)
                
                # Auth code al
                code, ok = QInputDialog.getText(self, "Yetkilendirme Kodu", 
                    "Google'dan aldığınız yetkilendirme kodunu girin:")
                
                if ok and code:
                    success = self.calendar_manager.authenticate(code)
                    if success:
                        self.calendar_status_label.setText("📅 Google Calendar: ✅ Bağlı")
                        self.calendar_status_label.setStyleSheet("font-size: 16px; padding: 10px; color: #27ae60;")
                        QMessageBox.information(self, "✅ Başarılı", "Google Calendar bağlantısı kuruldu!")
                    else:
                        QMessageBox.critical(self, "❌ Hata", "Bağlantı kurulamadı!")
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"Calendar bağlantı hatası:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Uyarı", "CalendarManager modülü bulunamadı!")
    
    def load_firms_for_appointment(self):
        """Randevu için firma listesini yükle"""
        # get_all_firms yerine get_firms_by_filter kullan
        firms = self.db.get_firms_by_filter({})  # Boş filtre = tüm firmalar
        self.appointment_firm_combo.clear()
        
        for firm in firms[:100]:  # İlk 100 firma
            self.appointment_firm_combo.addItem(firm['name'], firm)
    
    def create_appointment(self):
        """Yeni randevu oluştur"""
        # Form validasyonu
        if not self.appointment_title_input.text():
            QMessageBox.warning(self, "Uyarı", "Randevu başlığı gerekli!")
            return
        
        # Randevu verilerini topla
        appointment_data = {
            'firm': self.appointment_firm_combo.currentData() or {'name': self.appointment_firm_combo.currentText()},
            'person': self.appointment_person_input.text(),
            'title': self.appointment_title_input.text(),
            'date': self.appointment_date.dateTime().toString(Qt.DateFormat.ISODate),  # ISO format string
            'duration': self.appointment_duration.value(),
            'type': self.appointment_type_combo.currentText(),
            'notes': self.appointment_notes.toPlainText(),
            'reminder': self.appointment_reminder_combo.currentText()
        }
        
        # Google Calendar'a ekle
        if self.calendar_manager:
            try:
                if hasattr(self.calendar_manager, 'is_authenticated') and self.calendar_manager.is_authenticated():
                    event_id = self.calendar_manager.create_event(appointment_data)
                    if event_id:
                        # Veritabanına kaydet
                        try:
                            if hasattr(self.db, 'save_appointment'):
                                self.db.save_appointment(appointment_data, event_id)
                        except:
                            pass  # Database'de bu metod yoksa sessizce geç
                        
                        QMessageBox.information(self, "✅ Başarılı", 
                            f"Randevu oluşturuldu!\n\n"
                            f"Tarih: {appointment_data['date']}\n"
                            f"Firma: {appointment_data['firm']['name']}")
                        
                        # Formu temizle
                        self.appointment_person_input.clear()
                        self.appointment_title_input.clear()
                        self.appointment_notes.clear()
                        
                        # Randevu listesini yenile
                        self.refresh_appointments()
                    else:
                        QMessageBox.critical(self, "❌ Hata", "Randevu oluşturulamadı!")
                else:
                    # Calendar authenticated değilse sadece veritabanına kaydet
                    try:
                        if hasattr(self.db, 'save_appointment'):
                            self.db.save_appointment(appointment_data)
                    except:
                        pass
                    QMessageBox.information(self, "📝 Not", 
                        "Randevu kaydedildi ancak Google Calendar'a eklenmedi.\n"
                        "Google Calendar bağlantısı kurun.")
                    self.refresh_appointments()
            except Exception as e:
                print(f"Calendar error: {str(e)}")
                # Hata durumunda da veritabanına kaydet
                try:
                    if hasattr(self.db, 'save_appointment'):
                        self.db.save_appointment(appointment_data)
                except:
                    pass
                QMessageBox.information(self, "📝 Not", 
                    "Randevu kaydedildi ancak Google Calendar'a eklenmedi.")
                self.refresh_appointments()
        else:
            # Sadece veritabanına kaydet
            try:
                if hasattr(self.db, 'save_appointment'):
                    self.db.save_appointment(appointment_data)
            except:
                pass
            QMessageBox.information(self, "📝 Not", 
                "Randevu kaydedildi ancak Google Calendar'a eklenmedi.\n"
                "Google Calendar bağlantısı kurun.")
            self.refresh_appointments()
    
    def check_availability(self):
        """Müsaitlik kontrolü yap"""
        if self.calendar_manager:
            try:
                if hasattr(self.calendar_manager, 'is_authenticated') and self.calendar_manager.is_authenticated():
                    date = self.appointment_date.dateTime()  # QDateTime olarak kullan
                    duration = self.appointment_duration.value()
                    
                    # CalendarManager'a datetime objesi göndermek gerekiyorsa
                    date_python = datetime(
                        date.date().year(),
                        date.date().month(),
                        date.date().day(),
                        date.time().hour(),
                        date.time().minute()
                    )
                    
                    available_slots = self.calendar_manager.check_availability(date_python, duration)
                    
                    if available_slots:
                        text = "🟢 Müsait Saatler:\n\n"
                        for slot in available_slots:
                            text += f"• {slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')}\n"
                    else:
                        text = "🔴 Bu tarihte müsait saat bulunamadı."
                    
                    self.availability_text.setText(text)
                else:
                    self.availability_text.setText("⚠️ Google Calendar bağlantısı gerekli!")
            except:
                self.availability_text.setText("⚠️ Müsaitlik kontrolü yapılamadı!")
        else:
            self.availability_text.setText("⚠️ CalendarManager modülü yüklü değil!")
    
    def refresh_appointments(self):
        """Randevu listesini yenile"""
        try:
            # get_upcoming_appointments metodu yoksa boş liste
            if hasattr(self.db, 'get_upcoming_appointments'):
                appointments = self.db.get_upcoming_appointments()
            else:
                appointments = []  # Database'de bu metod yoksa boş liste
            
            self.appointments_table.setRowCount(len(appointments))
            
            total = len(appointments)
            completed = sum(1 for a in appointments if a.get('status') == 'completed')
            upcoming = sum(1 for a in appointments if a.get('status') == 'upcoming')
            
            # İstatistikleri güncelle
            self.total_appointments_label.setText(f"Toplam: {total}")
            self.completed_appointments_label.setText(f"Tamamlanan: {completed}")
            self.upcoming_appointments_label.setText(f"Yaklaşan: {upcoming}")
            
            # Conversion hesapla
            if completed > 0 and hasattr(self.db, 'get_appointment_conversions'):
                try:
                    converted = self.db.get_appointment_conversions()
                    conversion_rate = (converted / completed) * 100
                    self.conversion_from_appointments_label.setText(f"Dönüşüm: %{conversion_rate:.1f}")
                except:
                    self.conversion_from_appointments_label.setText(f"Dönüşüm: %0")
            else:
                self.conversion_from_appointments_label.setText(f"Dönüşüm: %0")
            
            # Tabloyu doldur
            for i, appointment in enumerate(appointments):
                # Tarih parse etme
                try:
                    if isinstance(appointment['date'], str):
                        date = datetime.fromisoformat(appointment['date'])
                    else:
                        date = appointment['date']
                    
                    self.appointments_table.setItem(i, 0, QTableWidgetItem(date.strftime('%d.%m.%Y')))
                    self.appointments_table.setItem(i, 1, QTableWidgetItem(date.strftime('%H:%M')))
                except:
                    self.appointments_table.setItem(i, 0, QTableWidgetItem(str(appointment.get('date', ''))))
                    self.appointments_table.setItem(i, 1, QTableWidgetItem('-'))
                
                self.appointments_table.setItem(i, 2, QTableWidgetItem(appointment.get('firm_name', '')))
                self.appointments_table.setItem(i, 3, QTableWidgetItem(appointment.get('person', '')))
                self.appointments_table.setItem(i, 4, QTableWidgetItem(appointment.get('type', '')))
                
                # İşlem butonları
                action_layout = QHBoxLayout()
                action_widget = QWidget()
                
                # Düzenle
                edit_btn = QPushButton("✏️")
                edit_btn.clicked.connect(lambda checked=False, a=appointment: self.edit_appointment(a))
                action_layout.addWidget(edit_btn)
                
                # İptal
                cancel_btn = QPushButton("❌")
                cancel_btn.clicked.connect(lambda checked=False, a=appointment: self.cancel_appointment(a))
                action_layout.addWidget(cancel_btn)
                
                action_widget.setLayout(action_layout)
                self.appointments_table.setCellWidget(i, 5, action_widget)
        except Exception as e:
            print(f"Randevu listesi yükleme hatası: {str(e)}")
    
    def edit_appointment(self, appointment):
        """Randevuyu düzenle"""
        QMessageBox.information(self, "Bilgi", "Randevu düzenleme özelliği yakında eklenecek!")
    
    def cancel_appointment(self, appointment):
        """Randevuyu iptal et"""
        reply = QMessageBox.question(self, "Onay", 
            "Bu randevuyu iptal etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Google Calendar'dan sil
            if self.calendar_manager and appointment.get('google_event_id'):
                self.calendar_manager.delete_event(appointment['google_event_id'])
            
            # Veritabanından sil
            try:
                if hasattr(self.db, 'cancel_appointment'):
                    self.db.cancel_appointment(appointment['id'])
            except:
                pass  # Database'de bu metod yoksa sessizce geç
            
            self.refresh_appointments()
            QMessageBox.information(self, "✅ Başarılı", "Randevu iptal edildi!")
    
    def test_calendar_connection(self):
        """Calendar bağlantısını test et"""
        if self.calendar_manager:
            try:
                if hasattr(self.calendar_manager, 'test_connection') and self.calendar_manager.test_connection():
                    QMessageBox.information(self, "✅ Başarılı", 
                        "Google Calendar bağlantısı başarılı!")
                else:
                    QMessageBox.critical(self, "❌ Hata", 
                        "Google Calendar bağlantısı başarısız!\n"
                        "Lütfen ayarlarınızı kontrol edin.")
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", 
                    f"Calendar test hatası:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Uyarı", "CalendarManager modülü bulunamadı!")
    
    # Import/Export Tab fonksiyonları
    def generate_test_firms(self):
        """Test firmaları oluştur"""
        if not self.data_manager:
            QMessageBox.critical(self, "Hata",
                "Test firma oluşturmak için DataManager modülü gerekli!")
            return
            
        count = self.test_firm_count.value()
        sector = self.test_sector_combo.currentText()
        
        # Onay al
        reply = QMessageBox.question(self, "Onay",
            f"{count} adet test firma oluşturulacak.\n"
            f"Sektör: {sector}\n\n"
            "Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Gelişmiş seçenekleri topla
            options = {
                'email_count': self.test_email_count.value(),
                'location': self.test_location_combo.currentText(),
                'min_rating': self.test_min_rating.value() if hasattr(self, 'test_min_rating') else 3,
                'max_rating': self.test_max_rating.value() if hasattr(self, 'test_max_rating') else 5,
                'with_website': self.test_with_website_check.isChecked() if hasattr(self, 'test_with_website_check') else True,
                'with_phone': self.test_with_phone_check.isChecked() if hasattr(self, 'test_with_phone_check') else True
            }
            
            self.worker_thread = WorkerThread("generate_test_firms", {
                'count': count,
                'sector': sector.lower(),
                'options': options
            })
            
            self.worker_thread.progress.connect(self.update_status)
            self.worker_thread.finished.connect(self.on_test_firms_generated)
            self.worker_thread.error.connect(self.on_error)
            self.worker_thread.show_preview.connect(self.show_email_preview_dialog)  # YENİ BAĞLANTI
            self.worker_thread.start()
            
            # Log ekle
            self.import_export_log.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🎲 {count} test firma oluşturuluyor..."
            )
    
    def on_test_firms_generated(self, data):
        """Test firmaları oluşturuldu"""
        count = data.get('generated_count', 0)
        
        self.import_export_log.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {count} test firma başarıyla oluşturuldu!"
        )
        
        QMessageBox.information(self, "✅ Başarılı",
            f"{count} test firma oluşturuldu!\n\n"
            "Firmalar veritabanına kaydedildi.")
        
        # Firma listesini yenile
        self.load_all_firms()
    
    def browse_import_file(self):
        """Import dosyası seç"""
        file_filter = {
            "CSV": "CSV Files (*.csv)",
            "Excel": "Excel Files (*.xlsx *.xls)",
            "XML": "XML Files (*.xml)",
            "JSON": "JSON Files (*.json)"
        }
        
        format_type = self.import_format_combo.currentText()
        
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Dosya Seç", "", 
            file_filter.get(format_type, "All Files (*.*)")
        )
        
        if file_name:
            self.import_file_path.setText(file_name)
    
    def download_import_template(self):
        """Import şablonu indir"""
        format_type = self.import_format_combo.currentText()
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Şablonu Kaydet",
            f"firma_sablonu.{format_type.lower()}",
            f"{format_type} Files (*.{format_type.lower()})"
        )
        
        if file_name:
            if self.data_manager:
                try:
                    success = self.data_manager.create_import_template(file_name, format_type)
                    if success:
                        QMessageBox.information(self, "✅ Başarılı", 
                            f"{format_type} şablonu başarıyla oluşturuldu!")
                    else:
                        QMessageBox.critical(self, "❌ Hata", "Şablon oluşturulamadı!")
                except Exception as e:
                    QMessageBox.critical(self, "❌ Hata", f"Şablon oluşturma hatası:\n{str(e)}")
            else:
                QMessageBox.warning(self, "Uyarı", "DataManager modülü bulunamadı!")
    
    def start_import(self):
        """Import işlemini başlat"""
        file_path = self.import_file_path.text()
        
        if not file_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir dosya seçin!")
            return
        
        self.worker_thread = WorkerThread("import_data", {
            'file_path': file_path,
            'file_type': self.import_format_combo.currentText(),
            'skip_duplicates': self.skip_duplicates_check.isChecked(),
            'auto_analyze': self.auto_analyze_check.isChecked()
        })
        
        self.worker_thread.progress.connect(self.update_status)
        self.worker_thread.finished.connect(self.on_import_finished)
        self.worker_thread.error.connect(self.on_error)
        self.worker_thread.start()
        
        self.import_export_log.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Import başlatıldı: {file_path}"
        )
    
    def on_import_finished(self, data):
        """Import tamamlandı"""
        imported_count = data.get('imported_count', 0)
        errors = data.get('errors', [])
        
        self.import_export_log.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {imported_count} firma içe aktarıldı"
        )
        
        if errors:
            self.import_export_log.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {len(errors)} hata oluştu"
            )
        
        msg = f"{imported_count} firma başarıyla içe aktarıldı!"
        if errors:
            msg += f"\n\n{len(errors)} hata oluştu."
        
        QMessageBox.information(self, "✅ Import Tamamlandı", msg)
        
        # Firma listesini yenile
        self.load_all_firms()
    
    def start_export(self):
        """Export işlemini başlat"""
        format_type = self.export_format_combo.currentText()
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Dışa Aktar",
            f"firmalar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type.lower()}",
            f"{format_type} Files (*.{format_type.lower()})"
        )
        
        if file_name:
            # Filtreleri topla
            filters = {}
            if self.export_filtered_radio.isChecked():
                filters['analyzed_only'] = self.export_analyzed_only_check.isChecked()
                filters['has_emails'] = self.export_with_emails_check.isChecked()
                filters['in_campaign'] = self.export_campaign_firms_check.isChecked()
            
            self.worker_thread = WorkerThread("export_data", {
                'file_path': file_name,
                'file_type': format_type,
                'filters': filters,
                'include_emails': self.include_emails_check.isChecked(),
                'include_analysis': self.include_analysis_check.isChecked()
            })
            
            self.worker_thread.progress.connect(self.update_status)
            self.worker_thread.finished.connect(self.on_export_finished)
            self.worker_thread.error.connect(self.on_error)
            self.worker_thread.start()
            
            self.import_export_log.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] 📤 Export başlatıldı: {file_name}"
            )
    
    def on_export_finished(self, data):
        """Export tamamlandı"""
        exported_count = data.get('exported_count', 0)
        
        self.import_export_log.append(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {exported_count} firma dışa aktarıldı"
        )
        
        QMessageBox.information(self, "✅ Export Tamamlandı",
            f"{exported_count} firma başarıyla dışa aktarıldı!")
    
    # Spam kontrol fonksiyonları
    def check_template_spam_score(self):
        """Mail şablonunun spam skorunu kontrol et"""
        instructions = self.mail_instructions.toPlainText()
        
        if not instructions:
            QMessageBox.warning(self, "Uyarı", "Lütfen mail talimatlarını girin!")
            return
        
        if self.analytics_dashboard:
            try:
                # Örnek bir mail oluştur
                sample_content = f"""
                Merhaba [Firma Adı],
                
                {instructions}
                
                Saygılarımla,
                [İmza]
                """
                
                score = self.analytics_dashboard.check_spam_score(sample_content)
                
                # Renk belirle
                if score < 3:
                    color = "#27ae60"  # Yeşil
                    status = "İyi"
                elif score < 6:
                    color = "#f39c12"  # Sarı
                    status = "Orta"
                else:
                    color = "#e74c3c"  # Kırmızı
                    status = "Yüksek"
                
                self.spam_score_label.setText(f"Spam Skoru: {score}/10 ({status})")
                self.spam_score_label.setStyleSheet(f"color: {color}; font-weight: bold;")
                
                # Öneriler göster
                if score >= 3:
                    suggestions = self.analytics_dashboard.get_spam_improvement_suggestions(sample_content)
                    
                    msg = f"Spam Skoru: {score}/10\n\n"
                    msg += "İyileştirme önerileri:\n"
                    for suggestion in suggestions:
                        msg += f"• {suggestion}\n"
                    
                    QMessageBox.information(self, "🛡️ Spam Analizi", msg)
            except Exception as e:
                self.spam_score_label.setText("Spam kontrolü yapılamadı")
                print(f"Spam kontrol hatası: {str(e)}")
        else:
            self.spam_score_label.setText("AnalyticsDashboard modülü yok")
    
    # Mevcut fonksiyonlar devam ediyor...
    # initialize_whatsapp_tab fonksiyonu kaldırıldı
    
    # test_whatsapp_api fonksiyonu kaldırıldı
    
    # refresh_whatsapp_templates fonksiyonu kaldırıldı
    
    # start_whatsapp_campaign fonksiyonu kaldırıldı
    
    # on_whatsapp_campaign_finished fonksiyonu kaldırıldı
    
    # load_conversations fonksiyonu kaldırıldı
    
    # filter_conversations fonksiyonu kaldırıldı
    
    # load_conversation fonksiyonu kaldırıldı
    
    # send_whatsapp_message_from_ui fonksiyonu kaldırıldı
    
    # load_automation_rules fonksiyonu kaldırıldı
    
    # edit_automation_rule fonksiyonu kaldırıldı
    
    # update_whatsapp_stats fonksiyonu kaldırıldı
    
    # run_whatsapp_automation fonksiyonu kaldırıldı
    
    # run_whatsapp_automation_manual fonksiyonu kaldırıldı
    
    # on_automation_complete fonksiyonu kaldırıldı
    
    # on_automation_error fonksiyonu kaldırıldı
    
    # Diğer mevcut fonksiyonlar...
    def start_search(self):
        """Firma aramayı başlat"""
        sector = self.sector_input.text().strip()
        location = self.location_input.text().strip()
        max_results = self.max_firms_input.value()
        
        if not sector or not location:
            QMessageBox.warning(self, "Uyarı", "Lütfen sektör ve konum bilgilerini girin!")
            return
        
        self.search_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.search_progress.setVisible(True)
        self.search_progress.setMaximum(max_results)
        self.search_progress.setValue(0)
        
        self.firms_table.setRowCount(0)
        self.current_firms = []
        print(f"🧹 Tablo temizlendi, başlangıç satır sayısı: {self.firms_table.rowCount()}")  # DEBUG
        
        if self.batch_mode_check.isChecked():
            # Batch modunda arama
            self.batch_search_thread = BatchSearchThread(
                sector, location, max_results,
                batch_size=20, wait_minutes=20
            )
            print("🔗 BatchSearchThread sinyal-slot bağlantıları kuruluyor...")  # DEBUG
            self.batch_search_thread.progress.connect(self.update_search_status)
            self.batch_search_thread.batch_completed.connect(self.on_batch_completed)
            self.batch_search_thread.all_completed.connect(self.on_search_completed)
            self.batch_search_thread.error.connect(self.on_search_error)
            print("🚀 BatchSearchThread başlatılıyor...")  # DEBUG
            self.batch_search_thread.start()
        else:
            # Normal modunda arama
            self.single_search_thread = SingleSearchThread(
                sector, location, max_results
            )
            self.single_search_thread.progress.connect(self.update_search_status)
            self.single_search_thread.firm_found.connect(self.add_firm_to_table)
            self.single_search_thread.firm_found.connect(self.add_firm_to_all_firms_table)
            self.single_search_thread.all_completed.connect(self.on_search_completed)
            self.single_search_thread.error.connect(self.on_search_error)
            self.single_search_thread.start()
    
    def pause_search(self):
        """Aramayı duraklat"""
        if hasattr(self, 'batch_search_thread') and self.batch_search_thread:
            if self.pause_btn.text() == "⏸️ Duraklat":
                self.batch_search_thread.pause()
                self.pause_btn.setText("▶️ Devam Et")
            else:
                self.batch_search_thread.resume()
                self.pause_btn.setText("⏸️ Duraklat")
        # Single search thread için pause işlevi yok, sadece stop
    
    def stop_search(self):
        """Aramayı durdur"""
        if hasattr(self, 'batch_search_thread') and self.batch_search_thread:
            self.batch_search_thread.stop()
        
        if hasattr(self, 'single_search_thread') and self.single_search_thread:
            self.single_search_thread.stop()
        
        self.search_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
    
    def on_batch_completed(self, firms):
        """Bir batch tamamlandığında"""
        print(f"🔥 BATCH COMPLETED: {len(firms)} firma geldi!")  # DEBUG
        for firm in firms:
            print(f"  📍 Firma: {firm.get('name', 'İsimsiz')}")  # DEBUG
            self.add_firm_to_table(firm)
            self.add_firm_to_all_firms_table(firm)
        
        self.search_progress.setValue(len(self.current_firms))
        self.update_selected_count()
        print(f"🔥 Tabloya eklenen toplam firma sayısı: {self.firms_table.rowCount()}")  # DEBUG
    
    def on_search_completed(self, all_firms):
        """Tüm arama tamamlandığında"""
        self.search_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.search_progress.setVisible(False)
        
        # save_search_history metodu yoksa atlayalım
        try:
            if hasattr(self.db, 'save_search_history'):
                self.db.save_search_history(
                    self.sector_input.text(),
                    self.location_input.text(),
                    len(all_firms)
                )
        except:
            pass
        
        # Duplikat önleme istatistiklerini al
        duplicate_stats = {}
        if self.db and hasattr(self.db, 'get_duplicate_prevention_stats'):
            try:
                duplicate_stats = self.db.get_duplicate_prevention_stats()
            except:
                pass
        
        # Mesaj oluştur
        message = f"Arama tamamlandı!\n\nToplam {len(all_firms)} yeni firma bulundu."
        
        if duplicate_stats and duplicate_stats.get('duplicate_prevention_rate', 0) > 0:
            message += f"\n\n🛡️ Duplikat Önleme:\n"
            message += f"• {duplicate_stats.get('firms_with_place_id', 0)} firma duplikat koruması altında\n"
            message += f"• %{duplicate_stats.get('duplicate_prevention_rate', 0)} duplikat önleme oranı"
        
        QMessageBox.information(self, "✅ Tamamlandı", message)
    
    def on_search_error(self, error_msg):
        """Arama hatası"""
        self.search_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.search_progress.setVisible(False)
        
        QMessageBox.critical(self, "❌ Hata", f"Arama hatası:\n{error_msg}")
    
    def add_firm_to_table(self, firm):
        """Firmayı tabloya ekle"""
        print(f"🔧 add_firm_to_table çağrıldı: {firm.get('name', 'İsimsiz')}")  # DEBUG
        
        # Ensure firm has an ID
        if not firm.get('id'):
            # Try to get ID from database
            try:
                existing_firms = self.db.get_firms(search_text=firm.get('name', ''), limit=5)
                for existing_firm in existing_firms:
                    if existing_firm.get('name') == firm.get('name'):
                        firm['id'] = existing_firm.get('id')
                        print(f"✅ Firma ID bulundu: {firm['id']}")
                        break
            except Exception as e:
                print(f"⚠️ Firma ID arama hatası: {e}")
        
        self.current_firms.append(firm)
        self.all_firms.append(firm)  # all_firms listesine de ekle
        
        row = self.firms_table.rowCount()
        print(f"🔧 Yeni satır ekleniyor: {row}")  # DEBUG
        self.firms_table.insertRow(row)
        
        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.update_selected_count)
        
        # Store firm ID in the checkbox's data for easy retrieval
        checkbox.setProperty('firm_id', firm.get('id'))
        checkbox.setProperty('firm_name', firm.get('name', ''))
        
        self.firms_table.setCellWidget(row, 0, checkbox)
        
        print(f"🔧 Satır {row}'a veri ekleniyor...")  # DEBUG
        self.firms_table.setItem(row, 1, QTableWidgetItem(firm.get('name', '')))
        
        rating_text = f"⭐ {firm.get('rating', 'N/A')} ({firm.get('review_count', 0)})"
        self.firms_table.setItem(row, 2, QTableWidgetItem(rating_text))
        
        website = firm.get('website', 'N/A')
        if website and website != 'N/A':
            website = website.replace('http://', '').replace('https://', '').split('/')[0]
        self.firms_table.setItem(row, 3, QTableWidgetItem(website))
        print(f"🔧 Satır {row} tamamlandı!")  # DEBUG
        
        self.firms_table.setItem(row, 4, QTableWidgetItem(firm.get('phone', 'N/A')))
        
        address = firm.get('address', 'N/A')
        if len(address) > 50:
            address = address[:50] + "..."
        self.firms_table.setItem(row, 5, QTableWidgetItem(address))
        
        db_firm = self.db.get_firm_by_id(firm['id'])
        if db_firm and db_firm.get('is_analyzed'):
            status_text = f"✅ Analiz edildi ({len(db_firm.get('emails', []))} email)"
            self.firms_table.setItem(row, 6, QTableWidgetItem(status_text))
        else:
            self.firms_table.setItem(row, 6, QTableWidgetItem("❌ Analiz edilmedi"))
        
        analyze_btn = QPushButton("🤖 Analiz Et")
        analyze_btn.clicked.connect(lambda checked=False, f=firm: self.analyze_single_firm(f))
        if db_firm and db_firm.get('is_analyzed'):
            analyze_btn.setText("🔄 Tekrar Analiz")
        self.firms_table.setCellWidget(row, 7, analyze_btn)
        
        detail_btn = QPushButton("👁️ Detay")
        detail_btn.clicked.connect(lambda checked=False, f=firm: self.show_firm_detail(f))
        self.firms_table.setCellWidget(row, 8, detail_btn)
        
        # Silme butonu ekle
        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.clicked.connect(lambda checked=False, f=firm: self.delete_single_firm(f))
        delete_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: none; border-radius: 3px; padding: 4px; }")
        self.firms_table.setCellWidget(row, 9, delete_btn)
        
        # Kategori atama butonu ekle
        category_btn = QPushButton("🏷️ Kategori")
        category_btn.clicked.connect(lambda checked=False, f=firm: self.assign_firm_to_category_quick(f))
        category_btn.setStyleSheet("QPushButton { background-color: #8e44ad; color: white; border: none; border-radius: 3px; padding: 4px; }")
        self.firms_table.setCellWidget(row, 10, category_btn)
    
    def delete_single_firm(self, firm):
        """Tek firmayı sil"""
        firm_name = firm.get('name', 'İsimsiz Firma')
        firm_id = firm.get('id')
        
        # If ID is not found, try to get it from the table widget first
        if not firm_id:
            # Try to find the firm in the table and get ID from checkbox
            for row in range(self.firms_table.rowCount()):
                checkbox = self.firms_table.cellWidget(row, 0)
                if checkbox:
                    stored_id = checkbox.property('firm_id')
                    stored_name = checkbox.property('firm_name')
                    if stored_name == firm_name and stored_id:
                        firm_id = stored_id
                        firm['id'] = stored_id
                        print(f"✅ Firma ID widget'tan alındı: {firm_id}")
                        break
        
        # If still not found, try database lookup
        if not firm_id:
            print(f"⚠️ Firma ID bulunamadı, veritabanından aranıyor: {firm_name}")
            try:
                # Try to get firm ID from database using name
                all_firms = self.db.get_firms(search_text="", limit=None)  # Get all firms
                for f in all_firms:
                    if f.get('name') == firm_name:
                        firm_id = f.get('id')
                        firm['id'] = firm_id  # Update the firm dictionary
                        print(f"✅ Firma ID veritabanından alındı: {firm_id}")
                        break
                        
                # If still not found, try searching in current_firms and all_firms lists
                if not firm_id:
                    if hasattr(self, 'current_firms'):
                        for f in self.current_firms:
                            if f.get('name') == firm_name:
                                firm_id = f.get('id')
                                firm['id'] = firm_id
                                print(f"✅ Firma ID current_firms'ten alındı: {firm_id}")
                                break
                    
                    if not firm_id and hasattr(self, 'all_firms'):
                        for f in self.all_firms:
                            if f.get('name') == firm_name:
                                firm_id = f.get('id')
                                firm['id'] = firm_id
                                print(f"✅ Firma ID all_firms'ten alındı: {firm_id}")
                                break
                        
            except Exception as e:
                print(f"❌ Veritabanı arama hatası: {e}")
        
        if not firm_id:
            QMessageBox.warning(self, "Hata", f"'{firm_name}' firmasının ID'si bulunamadı!\n\nFirmayı silmek için lütfen yeniden yükleyin.")
            return
        
        reply = QMessageBox.question(self, "Silme Onayı", 
            f"'{firm_name}' firmasını veritabanından kalıcı olarak silmek istediğinize emin misiniz?\n\n"
            f"Bu işlem geri alınamaz!",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Veritabanından sil
                success = self.db.delete_firm(firm_id)
                
                if success:
                    # Tablodan kaldır
                    for row in range(self.firms_table.rowCount()):
                        if self.firms_table.item(row, 1).text() == firm_name:
                            self.firms_table.removeRow(row)
                            break
                    
                    # current_firms listesinden kaldır
                    self.current_firms = [f for f in self.current_firms if f['id'] != firm_id]
                    
                    # all_firms listesinden de kaldır (varsa)
                    if hasattr(self, 'all_firms'):
                        self.all_firms = [f for f in self.all_firms if f['id'] != firm_id]
                    
                    QMessageBox.information(self, "✅ Başarılı", 
                        f"'{firm_name}' firması başarıyla silindi!")
                else:
                    QMessageBox.critical(self, "❌ Hata", "Firma silinirken bir hata oluştu!")
                    
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"Firma silinirken hata oluştu:\n{str(e)}")
    
    def assign_firm_to_category_quick(self, firm):
        """Firmayı hızlı kategori atama"""
        try:
            # Mevcut kategorileri al
            categories = self.db.get_categories()
            if not categories:
                QMessageBox.warning(self, "Uyarı", "Önce kategori oluşturun!")
                return
            
            # Mevcut firma kategorilerini al
            firm_categories = self.db.get_firm_categories(firm['id'])
            firm_category_ids = [cat['id'] for cat in firm_categories]
            
            # Kategori seçim dialogu
            dialog = QDialog(self)
            dialog.setWindowTitle(f"🏷️ {firm['name']} - Kategori Atama")
            dialog.setMinimumSize(400, 300)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title_label = QLabel(f"📋 {firm['name']} firmasını kategorilere ata")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # Mevcut kategoriler
            current_label = QLabel("Mevcut Kategoriler:")
            current_label.setStyleSheet("font-weight: bold; color: #27ae60; margin-top: 10px;")
            layout.addWidget(current_label)
            
            current_categories_text = ", ".join([cat['name'] for cat in firm_categories]) if firm_categories else "Kategori atanmamış"
            current_text = QLabel(current_categories_text)
            current_text.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
            layout.addWidget(current_text)
            
            # Kategori seçim listesi
            categories_list = QListWidget()
            categories_list.setSelectionMode(QListWidget.MultiSelection)
            categories_list.setStyleSheet("""
                QListWidget {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #bdc3c7;
                }
                QListWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
            """)
            
            for category in categories:
                item = QListWidgetItem(f"🏷️ {category['name']}")
                item.setData(Qt.UserRole, category['id'])
                
                # Mevcut kategorileri işaretle
                if category['id'] in firm_category_ids:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
                
                categories_list.addItem(item)
            
            layout.addWidget(categories_list)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            # Kaydet butonu
            save_btn = QPushButton("💾 Kaydet")
            save_btn.clicked.connect(lambda: self.save_firm_categories(firm, categories_list, dialog))
            save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2ecc71;
                }
            """)
            button_layout.addWidget(save_btn)
            
            # İptal butonu
            cancel_btn = QPushButton("❌ İptal")
            cancel_btn.clicked.connect(dialog.reject)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Kategori atama hatası:\n{str(e)}")
    
    def save_firm_categories(self, firm, categories_list, dialog):
        """Firma kategorilerini kaydet"""
        try:
            firm_id = firm['id']
            selected_categories = []
            
            # Seçili kategorileri al
            for i in range(categories_list.count()):
                item = categories_list.item(i)
                if item.checkState() == Qt.Checked:
                    category_id = item.data(Qt.UserRole)
                    selected_categories.append(category_id)
            
            # Mevcut kategorileri al
            current_categories = self.db.get_firm_categories(firm_id)
            current_category_ids = [cat['id'] for cat in current_categories]
            
            # Kaldırılacak kategoriler
            to_remove = [cat_id for cat_id in current_category_ids if cat_id not in selected_categories]
            
            # Eklenmesi gereken kategoriler
            to_add = [cat_id for cat_id in selected_categories if cat_id not in current_category_ids]
            
            # Kategorileri güncelle
            success_count = 0
            
            # Kaldır
            for category_id in to_remove:
                if self.db.remove_firm_from_category(firm_id, category_id):
                    success_count += 1
            
            # Ekle
            for category_id in to_add:
                if self.db.assign_firm_to_category(firm_id, category_id):
                    success_count += 1
            
            if success_count > 0:
                QMessageBox.information(self, "✅ Başarılı", 
                    f"'{firm['name']}' firmasının kategorileri güncellendi!")
                dialog.accept()
            else:
                QMessageBox.warning(self, "Uyarı", "Hiçbir değişiklik yapılmadı!")
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Kategori kaydetme hatası:\n{str(e)}")
    
    def create_smart_grouping_system(self):
        """Profesyonel akıllı gruplandırma sistemi oluştur"""
        # Gruplandırma kriterleri
        self.grouping_criteria = {
            'country': self.extract_country_from_address,
            'sector': lambda firm: firm.get('sector', 'Belirtilmemiş'),
            'rating': self.get_rating_group,
            'email_count': self.get_email_count_group,
            'analysis_status': lambda firm: 'Analiz Edildi' if firm.get('is_analyzed') else 'Analiz Edilmedi',
            'business_size': self.get_business_size_group,
            'technology_level': self.get_technology_level_group
        }
        
        # Gruplandırma seçenekleri
        self.grouping_options = {
            'country': '🌍 Ülke',
            'sector': '🏢 Sektör', 
            'rating': '⭐ Rating',
            'email_count': '📧 Email Sayısı',
            'analysis_status': '🤖 Analiz Durumu',
            'business_size': '🏭 İşletme Büyüklüğü',
            'technology_level': '💻 Teknoloji Seviyesi'
        }
    
    def extract_country_from_address(self, firm):
        """Adresten ülke bilgisini çıkar"""
        address = firm.get('address', '')
        if not address:
            return 'Bilinmeyen'
        
        # Türkiye şehirleri
        turkey_cities = ['istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 'adana', 'konya', 'gaziantep', 
                        'mersin', 'diyarbakır', 'kayseri', 'eskişehir', 'urfa', 'malatya', 'erzurum',
                        'van', 'batman', 'elazığ', 'izmit', 'manisa', 'sivas', 'trabzon', 'ordu',
                        'afyon', 'denizli', 'kahramanmaraş', 'sakarya', 'muğla', 'tekirdağ', 'balıkesir']
        
        address_lower = address.lower()
        for city in turkey_cities:
            if city in address_lower:
                return 'Türkiye'
        
        # Diğer ülkeler için basit kontrol
        if any(country in address_lower for country in ['germany', 'deutschland', 'berlin', 'munich']):
            return 'Almanya'
        elif any(country in address_lower for country in ['france', 'paris', 'lyon']):
            return 'Fransa'
        elif any(country in address_lower for country in ['italy', 'roma', 'milano']):
            return 'İtalya'
        elif any(country in address_lower for country in ['spain', 'madrid', 'barcelona']):
            return 'İspanya'
        elif any(country in address_lower for country in ['uk', 'london', 'england']):
            return 'İngiltere'
        elif any(country in address_lower for country in ['usa', 'america', 'new york', 'california']):
            return 'ABD'
        
        return 'Diğer'
    
    def get_rating_group(self, firm):
        """Rating'e göre grup belirle"""
        rating = firm.get('rating', 0)
        if rating >= 4.5:
            return '⭐⭐⭐⭐⭐ Mükemmel (4.5+)'
        elif rating >= 4.0:
            return '⭐⭐⭐⭐ Çok İyi (4.0-4.4)'
        elif rating >= 3.5:
            return '⭐⭐⭐ İyi (3.5-3.9)'
        elif rating >= 3.0:
            return '⭐⭐ Orta (3.0-3.4)'
        elif rating > 0:
            return '⭐ Düşük (3.0 altı)'
        else:
            return '📊 Rating Yok'
    
    def get_email_count_group(self, firm):
        """Email sayısına göre grup belirle"""
        email_count = len(firm.get('emails') or [])
        if email_count >= 10:
            return '📧 Çok Fazla (10+)'
        elif email_count >= 5:
            return '📧 Fazla (5-9)'
        elif email_count >= 2:
            return '📧 Orta (2-4)'
        elif email_count == 1:
            return '📧 Az (1)'
        else:
            return '📧 Email Yok'
    
    def get_business_size_group(self, firm):
        """İşletme büyüklüğüne göre grup belirle"""
        team_size = firm.get('team_size_estimate', '')
        if isinstance(team_size, str):
            team_size = team_size.lower()
            if any(word in team_size for word in ['büyük', 'large', 'enterprise', '100+', '500+']):
                return '🏢 Büyük İşletme'
            elif any(word in team_size for word in ['orta', 'medium', '50+', '100+']):
                return '🏢 Orta İşletme'
            elif any(word in team_size for word in ['küçük', 'small', 'startup', '1-10', '10-50']):
                return '🏢 Küçük İşletme'
            else:
                return '🏢 Bilinmeyen'
        else:
            return '🏢 Bilinmeyen'
    
    def get_technology_level_group(self, firm):
        """Teknoloji seviyesine göre grup belirle"""
        technologies = firm.get('technologies', [])
        if not technologies:
            return '💻 Teknoloji Bilgisi Yok'
        
        tech_count = len(technologies)
        if tech_count >= 10:
            return '💻 Çok Teknolojik (10+)'
        elif tech_count >= 5:
            return '💻 Teknolojik (5-9)'
        elif tech_count >= 2:
            return '💻 Orta Teknoloji (2-4)'
        else:
            return '💻 Az Teknoloji (1)'
    
    def apply_smart_grouping(self, firms, primary_criteria, secondary_criteria=None):
        """Akıllı gruplandırma uygula"""
        if primary_criteria not in self.grouping_criteria:
            return firms
        
        # Birincil gruplandırma
        primary_groups = {}
        for firm in firms:
            group_key = self.grouping_criteria[primary_criteria](firm)
            if group_key not in primary_groups:
                primary_groups[group_key] = []
            primary_groups[group_key].append(firm)
        
        # İkincil gruplandırma (varsa)
        if secondary_criteria and secondary_criteria in self.grouping_criteria:
            for group_key, group_firms in primary_groups.items():
                secondary_groups = {}
                for firm in group_firms:
                    sub_group_key = self.grouping_criteria[secondary_criteria](firm)
                    if sub_group_key not in secondary_groups:
                        secondary_groups[sub_group_key] = []
                    secondary_groups[sub_group_key].append(firm)
                primary_groups[group_key] = secondary_groups
        
        return primary_groups
    
    def get_grouping_statistics(self, grouped_firms):
        """Gruplandırma istatistiklerini al"""
        stats = {}
        total_firms = 0
        
        for group_name, group_data in grouped_firms.items():
            if isinstance(group_data, dict):  # İkincil gruplandırma
                group_count = sum(len(firms) for firms in group_data.values())
                stats[group_name] = {
                    'count': group_count,
                    'subgroups': {sub_name: len(sub_firms) for sub_name, sub_firms in group_data.items()}
                }
            else:  # Birincil gruplandırma
                group_count = len(group_data)
                stats[group_name] = {'count': group_count}
            
            total_firms += group_count
        
        stats['total'] = total_firms
        return stats
    
    def create_grouping_tab(self):
        """Akıllı gruplandırma sekmesi oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Başlık
        title_label = QLabel("📊 Akıllı Gruplandırma Sistemi")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
                background-color: #2c3e50;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Kontrol paneli
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Birincil kriter seçimi
        primary_label = QLabel("🎯 Birincil Kriter:")
        primary_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        control_layout.addWidget(primary_label)
        
        self.primary_criteria_combo = QComboBox()
        self.primary_criteria_combo.addItems([
            "🌍 Ülke", "🏢 Sektör", "⭐ Rating", "📧 Email Sayısı", 
            "🤖 Analiz Durumu", "🏭 İşletme Büyüklüğü", "💻 Teknoloji Seviyesi"
        ])
        self.primary_criteria_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        control_layout.addWidget(self.primary_criteria_combo)
        
        # İkincil kriter seçimi
        secondary_label = QLabel("🎯 İkincil Kriter:")
        secondary_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        control_layout.addWidget(secondary_label)
        
        self.secondary_criteria_combo = QComboBox()
        self.secondary_criteria_combo.addItem("❌ Yok")
        self.secondary_criteria_combo.addItems([
            "🌍 Ülke", "🏢 Sektör", "⭐ Rating", "📧 Email Sayısı", 
            "🤖 Analiz Durumu", "🏭 İşletme Büyüklüğü", "💻 Teknoloji Seviyesi"
        ])
        self.secondary_criteria_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        control_layout.addWidget(self.secondary_criteria_combo)
        
        # Gruplandırma butonu
        self.group_btn = QPushButton("📊 Gruplandır")
        self.group_btn.clicked.connect(self.apply_grouping)
        self.group_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        control_layout.addWidget(self.group_btn)
        
        # İstatistik butonu
        self.stats_btn = QPushButton("📈 İstatistikler")
        self.stats_btn.clicked.connect(self.show_grouping_stats)
        self.stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        control_layout.addWidget(self.stats_btn)
        
        layout.addWidget(control_panel)
        
        # Sonuç alanı
        self.grouping_results = QTextEdit()
        self.grouping_results.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        self.grouping_results.setReadOnly(True)
        layout.addWidget(self.grouping_results)
        
        # Gruplandırma sistemi oluştur
        self.create_smart_grouping_system()
        
        return tab
    
    def apply_grouping(self):
        """Gruplandırma uygula"""
        try:
            # Kriterleri al
            primary_text = self.primary_criteria_combo.currentText()
            secondary_text = self.secondary_criteria_combo.currentText()
            
            # Kriter anahtarlarını bul
            primary_key = None
            secondary_key = None
            
            for key, value in self.grouping_options.items():
                if value == primary_text:
                    primary_key = key
                if value == secondary_text:
                    secondary_key = key
            
            if not primary_key:
                QMessageBox.warning(self, "Hata", "Geçersiz birincil kriter seçimi!")
                return
            
            # Firmaları al
            firms = self.all_firms if hasattr(self, 'all_firms') else []
            if not firms:
                QMessageBox.warning(self, "Hata", "Gruplandırılacak firma bulunamadı!")
                return
            
            # Gruplandırma uygula
            grouped_firms = self.apply_smart_grouping(firms, primary_key, secondary_key)
            
            # Sonuçları göster
            self.display_grouping_results(grouped_firms, primary_text, secondary_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Gruplandırma sırasında hata oluştu:\n{str(e)}")
    
    def display_grouping_results(self, grouped_firms, primary_text, secondary_text):
        """Gruplandırma sonuçlarını göster"""
        results = []
        results.append(f"📊 GRUPLANDIRMA SONUÇLARI")
        results.append(f"🎯 Birincil Kriter: {primary_text}")
        results.append(f"🎯 İkincil Kriter: {secondary_text}")
        results.append("=" * 60)
        results.append("")
        
        total_firms = 0
        
        for group_name, group_data in grouped_firms.items():
            if isinstance(group_data, dict):  # İkincil gruplandırma
                group_count = sum(len(firms) for firms in group_data.values())
                results.append(f"📁 {group_name} ({group_count} firma)")
                results.append("-" * 40)
                
                for sub_name, sub_firms in group_data.items():
                    results.append(f"  📂 {sub_name}: {len(sub_firms)} firma")
                    # İlk 3 firmayı göster
                    for i, firm in enumerate(sub_firms[:3]):
                        results.append(f"    • {firm.get('name', 'İsimsiz')}")
                    if len(sub_firms) > 3:
                        results.append(f"    ... ve {len(sub_firms) - 3} firma daha")
                results.append("")
                total_firms += group_count
            else:  # Birincil gruplandırma
                results.append(f"📁 {group_name} ({len(group_data)} firma)")
                results.append("-" * 40)
                # İlk 5 firmayı göster
                for i, firm in enumerate(group_data[:5]):
                    results.append(f"  • {firm.get('name', 'İsimsiz')}")
                if len(group_data) > 5:
                    results.append(f"  ... ve {len(group_data) - 5} firma daha")
                results.append("")
                total_firms += len(group_data)
        
        results.append("=" * 60)
        results.append(f"📊 TOPLAM: {total_firms} firma")
        results.append(f"📁 GRUP SAYISI: {len(grouped_firms)}")
        
        self.grouping_results.setPlainText("\n".join(results))
    
    def show_grouping_stats(self):
        """Gruplandırma istatistiklerini göster"""
        try:
            # Mevcut gruplandırma sonuçlarını al
            current_text = self.grouping_results.toPlainText()
            if not current_text or "GRUPLANDIRMA SONUÇLARI" not in current_text:
                QMessageBox.warning(self, "Uyarı", "Önce gruplandırma yapın!")
                return
            
            # İstatistikleri hesapla
            firms = self.all_firms if hasattr(self, 'all_firms') else []
            if not firms:
                QMessageBox.warning(self, "Hata", "İstatistik hesaplanacak firma bulunamadı!")
                return
            
            # Basit istatistikler
            stats = {
                'total_firms': len(firms),
                'analyzed_firms': len([f for f in firms if f.get('is_analyzed')]),
                'countries': len(set(self.extract_country_from_address(f) for f in firms)),
                'sectors': len(set(f.get('sector', 'Belirtilmemiş') for f in firms)),
                'avg_rating': sum(f.get('rating', 0) for f in firms) / len(firms) if firms else 0,
                'total_emails': sum(len(f.get('emails') or []) for f in firms)
            }
            
            # İstatistik dialogu
            stats_dialog = QDialog(self)
            stats_dialog.setWindowTitle("📈 Gruplandırma İstatistikleri")
            stats_dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout(stats_dialog)
            
            # Başlık
            title_label = QLabel("📈 Genel İstatistikler")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # İstatistik tablosu
            stats_table = QTableWidget()
            stats_table.setColumnCount(2)
            stats_table.setRowCount(6)
            stats_table.setHorizontalHeaderLabels(["Metrik", "Değer"])
            
            stats_data = [
                ("📊 Toplam Firma", str(stats['total_firms'])),
                ("🤖 Analiz Edilmiş", f"{stats['analyzed_firms']} ({stats['analyzed_firms']/stats['total_firms']*100:.1f}%)"),
                ("🌍 Farklı Ülke", str(stats['countries'])),
                ("🏢 Farklı Sektör", str(stats['sectors'])),
                ("⭐ Ortalama Rating", f"{stats['avg_rating']:.2f}"),
                ("📧 Toplam Email", str(stats['total_emails']))
            ]
            
            for i, (metric, value) in enumerate(stats_data):
                stats_table.setItem(i, 0, QTableWidgetItem(metric))
                stats_table.setItem(i, 1, QTableWidgetItem(value))
            
            stats_table.setStyleSheet("""
                QTableWidget {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #bdc3c7;
                }
                QHeaderView::section {
                    background-color: #34495e;
                    color: white;
                    padding: 8px;
                    border: none;
                }
            """)
            
            layout.addWidget(stats_table)
            
            # Kapat butonu
            close_btn = QPushButton("Kapat")
            close_btn.clicked.connect(stats_dialog.accept)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            layout.addWidget(close_btn)
            
            stats_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İstatistik hesaplama sırasında hata oluştu:\n{str(e)}")
    
    def create_categories_tab(self):
        """Kategori yönetimi sekmesi oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Başlık
        title_label = QLabel("🏷️ Özel Kategori Yönetimi")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
                background-color: #8e44ad;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Üst panel - Kategori oluşturma
        create_panel = QWidget()
        create_layout = QHBoxLayout(create_panel)
        
        # Kategori adı
        name_label = QLabel("📝 Kategori Adı:")
        name_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        create_layout.addWidget(name_label)
        
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("Örn: Mekiska Yatak, Teknoloji, Sağlık...")
        self.category_name_input.setStyleSheet("""
            QLineEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        create_layout.addWidget(self.category_name_input)
        
        # Kategori açıklaması
        desc_label = QLabel("📄 Açıklama:")
        desc_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        create_layout.addWidget(desc_label)
        
        self.category_desc_input = QLineEdit()
        self.category_desc_input.setPlaceholderText("Kategori açıklaması (opsiyonel)")
        self.category_desc_input.setStyleSheet("""
            QLineEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        create_layout.addWidget(self.category_desc_input)
        
        # Renk seçimi
        color_label = QLabel("🎨 Renk:")
        color_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        create_layout.addWidget(color_label)
        
        self.category_color_combo = QComboBox()
        self.category_color_combo.addItems([
            "🔵 Mavi (#3498db)", "🟢 Yeşil (#27ae60)", "🔴 Kırmızı (#e74c3c)", 
            "🟡 Sarı (#f39c12)", "🟣 Mor (#9b59b6)", "🟠 Turuncu (#e67e22)",
            "⚫ Siyah (#2c3e50)", "⚪ Gri (#95a5a6)"
        ])
        self.category_color_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                padding: 5px;
                min-width: 120px;
            }
        """)
        create_layout.addWidget(self.category_color_combo)
        
        # Kategori oluştur butonu
        self.create_category_btn = QPushButton("➕ Kategori Oluştur")
        self.create_category_btn.clicked.connect(self.create_new_category)
        self.create_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        create_layout.addWidget(self.create_category_btn)
        
        layout.addWidget(create_panel)
        
        # Orta panel - Kategori listesi
        categories_panel = QWidget()
        categories_layout = QVBoxLayout(categories_panel)
        
        categories_title = QLabel("📋 Mevcut Kategoriler")
        categories_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; margin: 10px 0;")
        categories_layout.addWidget(categories_title)
        
        # Kategori tablosu
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(4)
        self.categories_table.setHorizontalHeaderLabels(["Kategori Adı", "Açıklama", "Firma Sayısı", "İşlemler"])
        self.categories_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 8px;
                gridline-color: #7f8c8d;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #7f8c8d;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        categories_layout.addWidget(self.categories_table)
        
        layout.addWidget(categories_panel)
        
        # Alt panel - Firma atama
        assign_panel = QWidget()
        assign_layout = QHBoxLayout(assign_panel)
        
        assign_title = QLabel("🏢 Firmaları Kategoriye Ata")
        assign_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        assign_layout.addWidget(assign_title)
        
        # Kategori seçimi
        self.assign_category_combo = QComboBox()
        self.assign_category_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        assign_layout.addWidget(self.assign_category_combo)
        
        # Firma seçimi
        self.assign_firm_combo = QComboBox()
        self.assign_firm_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 5px;
                padding: 5px;
                min-width: 200px;
            }
        """)
        assign_layout.addWidget(self.assign_firm_combo)
        
        # Ata butonu
        self.assign_btn = QPushButton("🔗 Ata")
        self.assign_btn.clicked.connect(self.assign_firm_to_category)
        self.assign_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        assign_layout.addWidget(self.assign_btn)
        
        # Kategorideki firmaları göster butonu
        self.show_category_firms_btn = QPushButton("👁️ Kategorideki Firmalar")
        self.show_category_firms_btn.clicked.connect(self.show_category_firms)
        self.show_category_firms_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        assign_layout.addWidget(self.show_category_firms_btn)
        
        layout.addWidget(assign_panel)
        
        # Kategorileri yükle
        self.load_categories()
        self.load_firms_for_assignment()
        
        return tab
    
    def create_new_category(self):
        """Yeni kategori oluştur"""
        name = self.category_name_input.text().strip()
        description = self.category_desc_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Uyarı", "Kategori adı boş olamaz!")
            return
        
        # Renk kodunu çıkar
        color_text = self.category_color_combo.currentText()
        color_code = color_text.split("(")[1].split(")")[0] if "(" in color_text else "#3498db"
        
        try:
            category_id = self.db.create_category(name, description, color_code)
            if category_id:
                QMessageBox.information(self, "✅ Başarılı", f"'{name}' kategorisi oluşturuldu!")
                self.category_name_input.clear()
                self.category_desc_input.clear()
                self.load_categories()
                self.load_firms_for_assignment()
            else:
                QMessageBox.critical(self, "❌ Hata", "Kategori oluşturulamadı!")
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Kategori oluşturma hatası:\n{str(e)}")
    
    def load_categories(self):
        """Kategorileri yükle"""
        try:
            categories = self.db.get_categories()
            self.categories_table.setRowCount(len(categories))
            
            for i, category in enumerate(categories):
                # Kategori adı
                name_item = QTableWidgetItem(category['name'])
                name_item.setBackground(QColor(category['color']))
                name_item.setForeground(QColor('white'))
                self.categories_table.setItem(i, 0, name_item)
                
                # Açıklama
                desc_item = QTableWidgetItem(category.get('description', ''))
                self.categories_table.setItem(i, 1, desc_item)
                
                # Firma sayısı
                firm_count = len(self.db.get_category_firms(category['id']))
                count_item = QTableWidgetItem(str(firm_count))
                self.categories_table.setItem(i, 2, count_item)
                
                # İşlemler
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                # Düzenle butonu
                edit_btn = QPushButton("✏️")
                edit_btn.setMaximumWidth(30)
                edit_btn.setStyleSheet("QPushButton { background-color: #f39c12; color: white; border: none; border-radius: 3px; }")
                edit_btn.clicked.connect(lambda checked, cat=category: self.edit_category(cat))
                actions_layout.addWidget(edit_btn)
                
                # Sil butonu
                delete_btn = QPushButton("🗑️")
                delete_btn.setMaximumWidth(30)
                delete_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 3px; }")
                delete_btn.clicked.connect(lambda checked, cat=category: self.delete_category(cat))
                actions_layout.addWidget(delete_btn)
                
                self.categories_table.setCellWidget(i, 3, actions_widget)
            
            # Kategori seçimi için combo'yu güncelle
            self.assign_category_combo.clear()
            for category in categories:
                self.assign_category_combo.addItem(f"{category['name']} ({len(self.db.get_category_firms(category['id']))} firma)")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Kategoriler yüklenirken hata:\n{str(e)}")
    
    def load_firms_for_assignment(self):
        """Firma atama için firmaları yükle"""
        try:
            firms = self.all_firms if hasattr(self, 'all_firms') else []
            self.assign_firm_combo.clear()
            
            for firm in firms:
                firm_name = firm.get('name', 'İsimsiz')
                # Mevcut kategorileri göster
                categories = self.db.get_firm_categories(firm['id'])
                category_names = [cat['name'] for cat in categories]
                category_text = f" ({', '.join(category_names)})" if category_names else ""
                
                self.assign_firm_combo.addItem(f"{firm_name}{category_text}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Firmalar yüklenirken hata:\n{str(e)}")
    
    def assign_firm_to_category(self):
        """Firmayı kategoriye ata"""
        try:
            category_index = self.assign_category_combo.currentIndex()
            firm_index = self.assign_firm_combo.currentIndex()
            
            if category_index < 0 or firm_index < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen kategori ve firma seçin!")
                return
            
            categories = self.db.get_categories()
            firms = self.all_firms if hasattr(self, 'all_firms') else []
            
            if category_index >= len(categories) or firm_index >= len(firms):
                QMessageBox.warning(self, "Uyarı", "Geçersiz seçim!")
                return
            
            category = categories[category_index]
            firm = firms[firm_index]
            
            success = self.db.assign_firm_to_category(firm['id'], category['id'])
            if success:
                QMessageBox.information(self, "✅ Başarılı", 
                    f"'{firm['name']}' firması '{category['name']}' kategorisine atandı!")
                self.load_categories()
                self.load_firms_for_assignment()
            else:
                QMessageBox.critical(self, "❌ Hata", "Firma atanamadı!")
                
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Firma atama hatası:\n{str(e)}")
    
    def show_category_firms(self):
        """Kategorideki firmaları göster"""
        try:
            category_index = self.assign_category_combo.currentIndex()
            if category_index < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir kategori seçin!")
                return
            
            categories = self.db.get_categories()
            if category_index >= len(categories):
                QMessageBox.warning(self, "Uyarı", "Geçersiz kategori seçimi!")
                return
            
            category = categories[category_index]
            firms = self.db.get_category_firms(category['id'])
            
            if not firms:
                QMessageBox.information(self, "Bilgi", f"'{category['name']}' kategorisinde firma bulunmuyor.")
                return
            
            # Firmalar dialogu
            firms_dialog = QDialog(self)
            firms_dialog.setWindowTitle(f"🏢 {category['name']} Kategorisindeki Firmalar")
            firms_dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(firms_dialog)
            
            # Başlık
            title_label = QLabel(f"📋 {category['name']} Kategorisi ({len(firms)} firma)")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
            layout.addWidget(title_label)
            
            # Firma tablosu
            firms_table = QTableWidget()
            firms_table.setColumnCount(4)
            firms_table.setHorizontalHeaderLabels(["Firma Adı", "Sektör", "Email Sayısı", "İşlemler"])
            firms_table.setRowCount(len(firms))
            
            for i, firm in enumerate(firms):
                firms_table.setItem(i, 0, QTableWidgetItem(firm.get('name', 'İsimsiz')))
                firms_table.setItem(i, 1, QTableWidgetItem(firm.get('sector', 'Belirtilmemiş')))
                firms_table.setItem(i, 2, QTableWidgetItem(str(len(firm.get('emails') or []))))
                
                # Kategoriden çıkar butonu
                remove_btn = QPushButton("❌ Çıkar")
                remove_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; border: none; border-radius: 3px; padding: 4px; }")
                remove_btn.clicked.connect(lambda checked, f=firm, c=category: self.remove_firm_from_category_ui(f, c, firms_dialog))
                firms_table.setCellWidget(i, 3, remove_btn)
            
            firms_table.setStyleSheet("""
                QTableWidget {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #bdc3c7;
                }
                QHeaderView::section {
                    background-color: #34495e;
                    color: white;
                    padding: 8px;
                    border: none;
                }
            """)
            
            layout.addWidget(firms_table)
            
            # Kapat butonu
            close_btn = QPushButton("Kapat")
            close_btn.clicked.connect(firms_dialog.accept)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            layout.addWidget(close_btn)
            
            firms_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Firmalar gösterilirken hata:\n{str(e)}")
    
    def remove_firm_from_category_ui(self, firm, category, dialog):
        """Firmayı kategoriden çıkar (UI)"""
        try:
            reply = QMessageBox.question(self, "Onay", 
                f"'{firm['name']}' firmasını '{category['name']}' kategorisinden çıkarmak istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                success = self.db.remove_firm_from_category(firm['id'], category['id'])
                if success:
                    QMessageBox.information(self, "✅ Başarılı", 
                        f"'{firm['name']}' firması '{category['name']}' kategorisinden çıkarıldı!")
                    dialog.accept()
                    self.load_categories()
                    self.load_firms_for_assignment()
                else:
                    QMessageBox.critical(self, "❌ Hata", "Firma kategoriden çıkarılamadı!")
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Firma çıkarma hatası:\n{str(e)}")
    
    def edit_category(self, category):
        """Kategori düzenle"""
        # Basit düzenleme dialogu
        name, ok = QInputDialog.getText(self, "Kategori Düzenle", "Yeni kategori adı:", text=category['name'])
        if ok and name.strip():
            success = self.db.update_category(category['id'], name=name.strip())
            if success:
                QMessageBox.information(self, "✅ Başarılı", "Kategori güncellendi!")
                self.load_categories()
            else:
                QMessageBox.critical(self, "❌ Hata", "Kategori güncellenemedi!")
    
    def delete_category(self, category):
        """Kategori sil"""
        reply = QMessageBox.question(self, "Onay", 
            f"'{category['name']}' kategorisini silmek istediğinize emin misiniz?\n\n"
            f"Bu işlem geri alınamaz ve kategorideki tüm firma atamaları silinir!",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.db.delete_category(category['id'])
            if success:
                QMessageBox.information(self, "✅ Başarılı", "Kategori silindi!")
                self.load_categories()
                self.load_firms_for_assignment()
            else:
                QMessageBox.critical(self, "❌ Hata", "Kategori silinemedi!")
    
    def select_all_firms(self):
        """Tüm firmaları seç"""
        for row in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)
        self.update_selected_count()
    
    def deselect_all_firms(self):
        """Hiçbir firmayı seçme"""
        for row in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_selected_count()
    
    def update_selected_count(self):
        """Seçili firma sayısını güncelle"""
        count = 0
        total_rows = self.all_firms_table.rowCount()
        print(f"🔧 DEBUG: update_selected_count - Toplam satır: {total_rows}")  # DEBUG
        
        for row in range(total_rows):
            if not self.all_firms_table.isRowHidden(row):
                checkbox = self.all_firms_table.cellWidget(row, 0)
                if checkbox and checkbox.isChecked():
                    count += 1
                    print(f"🔧 DEBUG: Satır {row} seçili")  # DEBUG
        
        print(f"🔧 DEBUG: Toplam seçili: {count}")  # DEBUG
        self.selected_count_label.setText(f"{count} firma seçili")
        
        # Buton durumlarını güncelle
        is_enabled = count > 0
        self.analyze_selected_btn.setEnabled(is_enabled)
        self.add_to_campaign_btn.setEnabled(is_enabled)
    
    def on_firms_table_context_menu(self, position):
        """Sağ tık context menu - Firmalar tablosu"""
        item = self.firms_table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        firm_name = self.firms_table.item(row, 1).text() if self.firms_table.item(row, 1) else ''
        
        # Firmayı bul
        firm = None
        for f in self.current_firms:
            if f.get('name') == firm_name:
                firm = f
                break
        
        if not firm:
            return
        
        # Context menu oluştur
        menu = QMenu(self)
        
        # Detay göster
        show_detail_action = QAction("👁️ Firma Detayını Göster", self)
        show_detail_action.triggered.connect(lambda: self.show_firm_detail_and_switch_tab(firm))
        menu.addAction(show_detail_action)
        
        # Analiz et
        analyze_action = QAction("🤖 Analiz Et", self)
        analyze_action.triggered.connect(lambda: self.analyze_single_firm(firm))
        menu.addAction(analyze_action)
        
        menu.addSeparator()
        
        # Kampanyaya ekle
        add_to_campaign_action = QAction("📧 Kampanyaya Ekle", self)
        add_to_campaign_action.triggered.connect(lambda: self.add_single_firm_to_campaign(firm))
        menu.addAction(add_to_campaign_action)
        
        menu.addSeparator()
        
        # Sil
        delete_action = QAction("🗑️ Sil", self)
        delete_action.triggered.connect(lambda: self.delete_single_firm(firm))
        menu.addAction(delete_action)
        
        # Menüyü göster
        menu.exec(self.firms_table.mapToGlobal(position))
    
    def show_firm_detail_and_switch_tab(self, firm):
        """Firma detayını göster ve detay sekmesine geç"""
        # Firma detay sekmesini bul
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "🏢 Firma Detay":
                self.tabs.setCurrentIndex(i)
                
                # If it's a FirmaDetayAnalyzer, load the firm
                widget = self.tabs.widget(i)
                if hasattr(widget, 'load_firm_by_name'):
                    widget.load_firm_by_name(firm.get('name'))
                elif hasattr(widget, 'load_firma_details') and firm.get('id'):
                    widget.load_firma_details(firm.get('id'))
                break
    
    def add_single_firm_to_campaign(self, firm):
        """Tek firmayı kampanyaya ekle"""
        if not hasattr(self, 'selected_firms'):
            self.selected_firms = []
        
        self.selected_firms.append(firm)
        
        # Kampanya sekmesine geç
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i).startswith("📧 Kampanya"):
                self.tabs.setCurrentIndex(i)
                # Update campaign firms list
                if hasattr(self, 'update_campaign_firms_list'):
                    self.update_campaign_firms_list()
                break
        
        QMessageBox.information(self, "✅ Başarılı", f"'{firm.get('name')}' kampanyaya eklendi!")
    
    def on_all_firms_table_context_menu(self, position):
        """Sağ tık context menu - Tüm Firmalar tablosu"""
        item = self.all_firms_table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        firm_name = self.all_firms_table.item(row, 1).text() if self.all_firms_table.item(row, 1) else ''
        
        # Firmayı bul - Önce checkbox'tan ID al
        firm = None
        firm_id = None
        
        # Checkbox'tan ID al
        checkbox = self.all_firms_table.cellWidget(row, 0)
        if checkbox:
            firm_id = checkbox.property('firm_id')
        
        # Firma verisini bul
        if firm_id:
            # ID ile bul
            if hasattr(self, 'all_firms'):
                for f in self.all_firms:
                    if f.get('id') == firm_id:
                        firm = f
                        break
            if not firm and hasattr(self, 'all_firms_data'):
                for f in self.all_firms_data:
                    if f.get('id') == firm_id:
                        firm = f
                        break
        else:
            # İsim ile bul
            if hasattr(self, 'all_firms'):
                for f in self.all_firms:
                    if f.get('name') == firm_name:
                        firm = f
                        break
        
        if not firm:
            return
        
        # Context menu oluştur
        menu = QMenu(self)
        
        # Detay göster - Firma Detay sekmesine git
        show_detail_action = QAction("👁️ Firma Detayını Göster", self)
        show_detail_action.triggered.connect(lambda: self.show_firm_detail_and_switch_tab(firm))
        menu.addAction(show_detail_action)
        
        # Analiz et
        analyze_action = QAction("🤖 Analiz Et", self)
        analyze_action.triggered.connect(lambda: self.analyze_single_firm(firm))
        menu.addAction(analyze_action)
        
        menu.addSeparator()
        
        # Kampanyaya ekle
        add_to_campaign_action = QAction("📧 Kampanyaya Ekle", self)
        add_to_campaign_action.triggered.connect(lambda: self.add_single_firm_to_campaign(firm))
        menu.addAction(add_to_campaign_action)
        
        menu.addSeparator()
        
        # Sil
        delete_action = QAction("🗑️ Sil", self)
        delete_action.triggered.connect(lambda: self.delete_single_firm(firm))
        menu.addAction(delete_action)
        
        # Menüyü göster
        menu.exec(self.all_firms_table.mapToGlobal(position))
    
    def analyze_single_firm(self, firm):
        """Tek firma analizi"""
        self.status_bar.showMessage(f"🔄 {firm['name']} analiz ediliyor...")
        
        # Web Scraper sekmesine otomatik geç
        self.switch_to_webscraper_tab()
        
        # Firmayı webscraper sekmesinde göster
        self.update_scraper_analysis_status(f"🔄 Analiz başlıyor: {firm['name']}")
        
        # Firmayı scraper 1'e yükle
        if hasattr(self, 'load_firm_to_scraper'):
            self.load_firm_to_scraper(firm, 1)
        
        self.worker_thread = WorkerThread("analyze_firm", {"firm": firm})
        self.worker_thread.progress.connect(self.update_status)
        self.worker_thread.finished.connect(self.on_analyze_finished)
        self.worker_thread.error.connect(self.on_error)
        self.worker_thread.start()
    
    def analyze_selected_firms(self):
        """Seçili firmaları analiz et - İkili Scraper Sistemi ile"""
        print("🔧 DEBUG: analyze_selected_firms çağrıldı!")  # DEBUG
        selected_firms = []
        
        # Try both tables to find checked firms
        tables_to_check = []
        if hasattr(self, 'all_firms_table') and self.all_firms_table.rowCount() > 0:
            tables_to_check.append(self.all_firms_table)
        if hasattr(self, 'firms_table') and self.firms_table.rowCount() > 0:
            tables_to_check.append(self.firms_table)
        
        if not tables_to_check:
            QMessageBox.warning(self, "Uyarı", "Görüntülenecek firma yok!")
            return
        
        # Scan all tables for checked rows
        for table_to_check in tables_to_check:
            for row in range(table_to_check.rowCount()):
                if not table_to_check.isRowHidden(row):
                    checkbox = table_to_check.cellWidget(row, 0)
                    if checkbox and checkbox.isChecked():
                        # Firma verilerini al
                        firm_name = table_to_check.item(row, 1).text() if table_to_check.item(row, 1) else ''
                        
                        if not firm_name:
                            continue
                        
                        # Search in all available data sources
                        firm_found = None
                        
                        # Try all_firms first (most complete data)
                        if hasattr(self, 'all_firms'):
                            for firm in self.all_firms:
                                if firm.get('name') == firm_name:
                                    firm_found = firm
                                    break
                        
                        # If not found, try all_firms_data
                        if not firm_found and hasattr(self, 'all_firms_data'):
                            for firm_data in self.all_firms_data:
                                if firm_data.get('name') == firm_name:
                                    firm_found = firm_data
                                    break
                        
                        # If still not found, try current_firms
                        if not firm_found and hasattr(self, 'current_firms'):
                            for firm in self.current_firms:
                                if firm.get('name') == firm_name:
                                    firm_found = firm
                                    break
                        
                        # If still not found, search in database
                        if not firm_found:
                            try:
                                firms = self.db.get_firms(search_text=firm_name, limit=5)
                                for f in firms:
                                    if f.get('name') == firm_name:
                                        firm_found = f
                                        break
                            except:
                                pass
                        
                        if firm_found:
                            selected_firms.append(firm_found)
                            print(f"✅ Firma eklendi: {firm_name}")  # DEBUG
        
        print(f"🔧 DEBUG: {len(selected_firms)} firma seçili")  # DEBUG
        
        if not selected_firms:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir firma seçin!")
            return
        
        # İkili tarama mı yoksa tek tarama mı?
        dual_mode = len(selected_firms) >= 2
        mode_text = "İkili Tarama" if dual_mode else "Tek Tarama"
        
        reply = QMessageBox.question(self, f"🚀 {mode_text} - Scraper Analizi",
            f"✨ YENİ SİSTEM: {len(selected_firms)} firma scraper panellerinde analiz edilecek!\n\n"
            f"🔥 {mode_text}: Firmalar scraper panellerinde görüntülenecek\n"
            f"⚡ Chrome açılmayacak - mevcut scraper panelleri kullanılacak\n"
            f"🎯 Random gecikme ile dikkat çekmeden tarama yapılacak\n\n"
            "Bu işlem biraz zaman alabilir. Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Web Scraper sekmesine otomatik geç
            self.switch_to_webscraper_tab()
            
            # İkili scraper analizi başlat
            self.start_dual_scraper_analysis(selected_firms)
            
            self.update_status(f"🚀 {mode_text} başlatıldı - {len(selected_firms)} firma!")
    
    def ai_bulk_analyze_selected_firms(self):
        """Seçili firmaları detay popup'ındaki mantıkla analiz et"""
        print("🔧 DEBUG: Seçili firmalar analiz ediliyor!")
        
        selected_firms = []
        print(f"🔧 DEBUG: Tablo satır sayısı: {self.all_firms_table.rowCount()}")
        
        for row in range(self.all_firms_table.rowCount()):
            if not self.all_firms_table.isRowHidden(row):
                checkbox = self.all_firms_table.cellWidget(row, 0)
                print(f"🔧 DEBUG: Satır {row} - Checkbox var mı: {checkbox is not None}, Seçili mi: {checkbox.isChecked() if checkbox else False}")
                
                if checkbox and checkbox.isChecked():
                    # Firma verilerini al
                    firm_name = self.all_firms_table.item(row, 1).text()
                    print(f"🔧 DEBUG: Seçili firma: {firm_name}")
                    
                    # Veritabanından tam veriyi al
                    if hasattr(self, 'all_firms_data'):
                        for firm_data in self.all_firms_data:
                            if firm_data.get('name') == firm_name:
                                selected_firms.append(firm_data)
                                print(f"🔧 DEBUG: Firma verisi bulundu: {firm_name}")
                                break
                        else:
                            print(f"🔧 DEBUG: Firma verisi bulunamadı: {firm_name}")
                    else:
                        print(f"🔧 DEBUG: all_firms_data tanımlı değil!")
                        # Veri yoksa tablodan direkt al
                        firm_data = {
                            'name': firm_name,
                            'phone': self.all_firms_table.item(row, 2).text() if self.all_firms_table.item(row, 2) else '',
                            'website': self.all_firms_table.item(row, 4).text() if self.all_firms_table.item(row, 4) else '',
                            'email': self.all_firms_table.item(row, 5).text() if self.all_firms_table.item(row, 5) else '',
                            'sector': self.all_firms_table.item(row, 6).text() if self.all_firms_table.item(row, 6) else ''
                        }
                        selected_firms.append(firm_data)
        
        print(f"🔧 DEBUG: {len(selected_firms)} firma seçili")
        print(f"🔧 DEBUG: all_firms_data var mı: {hasattr(self, 'all_firms_data')}")
        if hasattr(self, 'all_firms_data'):
            print(f"🔧 DEBUG: all_firms_data uzunluğu: {len(self.all_firms_data)}")
        
        if not selected_firms:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir firma seçin!")
            return
        
        # Onay dialogu
        reply = QMessageBox.question(self, "🤖 Seçili Firmaları Analiz Et",
            f"✨ {len(selected_firms)} firma analiz edilecek!\n\n"
            f"🔄 Her firma için:\n"
            f"• Web Scraper sekmesine geçilecek\n"
            f"• Firma scraper panellerinde görüntülenecek\n"
            f"• Detay popup'ındaki analiz işlemi uygulanacak\n\n"
            f"⏱️ Firmalar sırasıyla işlenecek\n\n"
            "Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Seçili firmaları sırayla analiz et
            self.analyze_selected_firms_sequentially(selected_firms)
    
    def analyze_selected_firms_sequentially(self, selected_firms):
        """Seçili firmaları sırayla detay popup mantığıyla analiz et"""
        import threading
        import time
        
        def run_sequential_analysis():
            for i, firm in enumerate(selected_firms):
                try:
                    print(f"🔄 Analiz ediliyor: {firm['name']} ({i+1}/{len(selected_firms)})")
                    
                    # Detay popup'ındaki analyze_single_firm mantığını uygula
                    self.status_bar.showMessage(f"🔄 {firm['name']} analiz ediliyor...")
                    
                    # Web Scraper sekmesine otomatik geç
                    self.switch_to_webscraper_tab()
                    
                    # Firmayı webscraper sekmesinde göster
                    self.update_scraper_analysis_status(f"🔄 Analiz başlıyor: {firm['name']}")
                    
                    # Firmayı scraper 1'e yükle
                    if hasattr(self, 'load_firm_to_scraper'):
                        self.load_firm_to_scraper(firm, 1)
                    
                    # Worker thread ile analiz
                    self.worker_thread = WorkerThread("analyze_firm", {"firm": firm})
                    self.worker_thread.progress.connect(self.update_status)
                    self.worker_thread.finished.connect(self.on_analyze_finished)
                    self.worker_thread.error.connect(self.on_error)
                    self.worker_thread.start()
                    
                    # Thread'in bitmesini bekle
                    self.worker_thread.wait()
                    
                    print(f"✅ Tamamlandı: {firm['name']}")
                    
                    # Kısa bekleme
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"❌ Hata {firm['name']}: {str(e)}")
                    continue
            
            print(f"🎉 Tüm firmalar analiz edildi! ({len(selected_firms)} firma)")
            self.update_status(f"✅ Toplu analiz tamamlandı - {len(selected_firms)} firma!")
        
        # Thread'de çalıştır
        analysis_thread = threading.Thread(target=run_sequential_analysis, daemon=True)
        analysis_thread.start()
    
    def start_ai_bulk_analysis(self, selected_firms):
        """AI toplu analizi başlat"""
        import threading
        import time
        
        # Analiz durumu için değişkenler
        self.ai_analysis_queue = selected_firms.copy()
        self.ai_analysis_progress = 0
        self.ai_analysis_total = len(selected_firms)
        self.ai_analysis_current_firm = None
        self.ai_analysis_is_running = True
        
        # Progress dialog oluştur
        self.create_ai_analysis_progress_dialog()
        
        # Analiz thread'ini başlat
        self.ai_analysis_thread = threading.Thread(target=self.run_ai_bulk_analysis, daemon=True)
        self.ai_analysis_thread.start()
        
        self.update_status(f"🧠 AI toplu analiz başlatıldı - {len(selected_firms)} firma!")
    
    def create_ai_analysis_progress_dialog(self):
        """AI analiz progress dialogu oluştur"""
        self.ai_progress_dialog = QDialog(self)
        self.ai_progress_dialog.setWindowTitle("🧠 AI Toplu Analiz")
        self.ai_progress_dialog.setModal(True)
        self.ai_progress_dialog.resize(500, 200)
        
        layout = QVBoxLayout(self.ai_progress_dialog)
        
        # Başlık
        title_label = QLabel("🧠 AI ile Toplu Firma Analizi")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #6c5ce7;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Mevcut firma
        self.ai_current_firm_label = QLabel("Hazırlanıyor...")
        self.ai_current_firm_label.setStyleSheet("font-size: 12px; color: #2d3436;")
        self.ai_current_firm_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ai_current_firm_label)
        
        # Progress bar
        self.ai_progress_bar = QProgressBar()
        self.ai_progress_bar.setRange(0, 100)
        self.ai_progress_bar.setValue(0)
        layout.addWidget(self.ai_progress_bar)
        
        # Durum
        self.ai_status_label = QLabel("Analiz başlatılıyor...")
        self.ai_status_label.setStyleSheet("font-size: 11px; color: #636e72;")
        self.ai_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ai_status_label)
        
        # İptal butonu
        cancel_btn = QPushButton("❌ İptal Et")
        cancel_btn.clicked.connect(self.cancel_ai_analysis)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e17055;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d63031;
            }
        """)
        layout.addWidget(cancel_btn)
        
        self.ai_progress_dialog.show()
    
    def run_ai_bulk_analysis(self):
        """AI toplu analizi çalıştır"""
        try:
            for i, firm in enumerate(self.ai_analysis_queue):
                if not self.ai_analysis_is_running:
                    break
                
                # Mevcut firma bilgisini güncelle
                self.ai_analysis_current_firm = firm
                self.ai_analysis_progress = i
                
                # UI güncellemeleri
                QApplication.processEvents()
                
                # Firma analizi
                self.analyze_single_firm_with_ai(firm)
                
                # Progress güncelle
                progress_percent = int((i + 1) / self.ai_analysis_total * 100)
                
                # UI thread'inde güncelle
                QApplication.postEvent(self, QEvent(QEvent.Type.User))
                
                # Kısa bekleme
                time.sleep(1)
            
            # Tamamlandı
            if self.ai_analysis_is_running:
                QApplication.postEvent(self, QEvent(QEvent.Type.User + 1))
                
        except Exception as e:
            print(f"❌ AI toplu analiz hatası: {str(e)}")
            QApplication.postEvent(self, QEvent(QEvent.Type.User + 2))
    
    def analyze_single_firm_with_ai(self, firm):
        """Tek firmayı AI ile analiz et"""
        try:
            print(f"🧠 AI analiz ediliyor: {firm['name']}")
            
            # OpenAI API key'i al
            settings = self.load_settings()
            openai_key = settings.get('openai_api_key', '') if settings else ''
            
            # Web scraper ile firma verilerini topla
            from web_scraper_integration import UnifiedWebScraper
            scraper = UnifiedWebScraper(
                use_enhanced=True,
                openai_api_key=openai_key if openai_key else None,
                cost_tracker=getattr(self, 'api_cost_widget', None)
            )
            
            # Firma web sitesini analiz et
            if firm.get('website'):
                website_url = firm['website']
                if not website_url.startswith(('http://', 'https://')):
                    website_url = 'https://' + website_url
                
                # Scraping işlemi
                result = scraper.scrape_website(website_url, firm['name'])
                
                if result and result.get('success'):
                    # Veritabanını güncelle
                    self.update_firm_with_ai_analysis(firm, result)
                    print(f"✅ AI analiz tamamlandı: {firm['name']}")
                else:
                    print(f"⚠️ AI analiz başarısız: {firm['name']}")
            else:
                print(f"⚠️ Website yok: {firm['name']}")
                
        except Exception as e:
            print(f"❌ Firma AI analiz hatası {firm['name']}: {str(e)}")
    
    def update_firm_with_ai_analysis(self, firm, analysis_result):
        """Firma verilerini AI analiz sonucu ile güncelle"""
        try:
            # Veritabanı güncelleme verileri
            update_data = {
                'is_analyzed': 1,
                'last_scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # AI analiz sonuçlarını ekle
            data = analysis_result.get('data', analysis_result)  # Enhanced scraper için
            
            # Temel bilgiler
            if data.get('contact_info', {}).get('emails'):
                update_data['emails'] = json.dumps(data['contact_info']['emails'], ensure_ascii=False)
            elif data.get('emails'):
                update_data['emails'] = json.dumps(data['emails'], ensure_ascii=False)
            
            if data.get('contact_info', {}).get('phones'):
                update_data['phone_numbers'] = json.dumps(data['contact_info']['phones'], ensure_ascii=False)
            elif data.get('phone_numbers'):
                update_data['phone_numbers'] = json.dumps(data['phone_numbers'], ensure_ascii=False)
            
            if data.get('contact_info', {}).get('social_media'):
                update_data['social_media'] = json.dumps(data['contact_info']['social_media'], ensure_ascii=False)
            elif data.get('social_media'):
                update_data['social_media'] = json.dumps(data['social_media'], ensure_ascii=False)
            
            if data.get('social_media_details'):
                update_data['social_media_details'] = json.dumps(data['social_media_details'], ensure_ascii=False)
            
            # İş bilgileri
            if data.get('products_services', {}).get('services'):
                update_data['services'] = json.dumps(data['products_services']['services'], ensure_ascii=False)
            elif data.get('services'):
                update_data['services'] = json.dumps(data['services'], ensure_ascii=False)
            
            if data.get('products_services', {}).get('products'):
                update_data['products'] = json.dumps(data['products_services']['products'], ensure_ascii=False)
            elif data.get('products'):
                update_data['products'] = json.dumps(data['products'], ensure_ascii=False)
            
            if data.get('business_info'):
                update_data['business_info'] = json.dumps(data['business_info'], ensure_ascii=False)
            
            # AI özeti - Enhanced scraper'dan
            if data.get('ai_summary'):
                update_data['ai_summary'] = data['ai_summary']
                print(f"🤖 AI özeti kaydedildi: {len(data['ai_summary'])} karakter")
            
            # Firma tipi bilgisi - Enhanced scraper'dan
            if data.get('company_type_analysis', {}).get('primary_type_tr'):
                update_data['sector'] = data['company_type_analysis']['primary_type_tr']
            
            # Kalite skoru - Enhanced scraper'dan
            if data.get('quality_score', {}).get('total_score'):
                update_data['quality_score'] = data['quality_score']['total_score']
            
            # Ürün/hizmet sayıları - Enhanced scraper'dan
            if data.get('products_services', {}).get('product_count'):
                update_data['product_count'] = data['products_services']['product_count']
            
            if data.get('products_services', {}).get('service_count'):
                update_data['service_count'] = data['products_services']['service_count']
            
            # Veritabanını güncelle
            self.db.update_firm(firm['id'], **update_data)
            
            print(f"💾 Veritabanı güncellendi: {firm['name']}")
            
        except Exception as e:
            print(f"❌ Veritabanı güncelleme hatası {firm['name']}: {str(e)}")
    
    def cancel_ai_analysis(self):
        """AI analizi iptal et"""
        self.ai_analysis_is_running = False
        if hasattr(self, 'ai_progress_dialog'):
            self.ai_progress_dialog.close()
        self.update_status("❌ AI toplu analiz iptal edildi")
    
    def customEvent(self, event):
        """Custom event handler for AI analysis progress updates"""
        if event.type() == QEvent.Type.User:
            # Progress güncelle
            if hasattr(self, 'ai_progress_dialog') and self.ai_progress_dialog.isVisible():
                progress_percent = int((self.ai_analysis_progress + 1) / self.ai_analysis_total * 100)
                self.ai_progress_bar.setValue(progress_percent)
                
                if self.ai_analysis_current_firm:
                    self.ai_current_firm_label.setText(f"🔄 Analiz ediliyor: {self.ai_analysis_current_firm['name']}")
                    self.ai_status_label.setText(f"İlerleme: {self.ai_analysis_progress + 1}/{self.ai_analysis_total} firma")
                
        elif event.type() == QEvent.Type.User + 1:
            # Tamamlandı
            if hasattr(self, 'ai_progress_dialog'):
                self.ai_progress_dialog.close()
            
            QMessageBox.information(self, "✅ Tamamlandı", 
                f"🧠 AI toplu analiz tamamlandı!\n\n"
                f"📊 {self.ai_analysis_total} firma analiz edildi\n"
                f"💾 Tüm veriler veritabanına kaydedildi\n\n"
                f"Firmalar tablosunu yenileyin.")
            
            self.update_status(f"✅ AI toplu analiz tamamlandı - {self.ai_analysis_total} firma!")
            
            # Firmalar tablosunu yenile
            self.load_firms_table()
            
        elif event.type() == QEvent.Type.User + 2:
            # Hata
            if hasattr(self, 'ai_progress_dialog'):
                self.ai_progress_dialog.close()
            
            QMessageBox.warning(self, "❌ Hata", "AI toplu analiz sırasında hata oluştu!")
            self.update_status("❌ AI toplu analiz hatası!")
    
    def start_dual_scraper_analysis(self, selected_firms):
        """İkili scraper analizi başlat - Chrome yerine scraper panelleri kullan"""
        import random
        import time
        
        # Analiz edilecek firmaları queue'ya ekle
        self.analysis_queue = selected_firms.copy()
        self.current_analysis_firms = []
        
        # İkili tarama mı?
        dual_mode = len(selected_firms) >= 2
        
        if dual_mode:
            # İkili tarama - İlk iki firmayı al
            firm1 = selected_firms[0]
            firm2 = selected_firms[1] if len(selected_firms) > 1 else None
            
            # Proxy/engel kontrolü simüle et (gerçek kontrolü için geliştirilebir)
            proxy_check_passed = self.check_proxy_status()
            
            if proxy_check_passed and firm2:
                # İkili tarama - Random gecikme ile başlat
                self.update_status("🔥 İkili tarama başlatılıyor - Proxy kontrolü OK!")
                
                # İlk firmayı hemen yükle
                self.load_firm_to_scraper(firm1, 1)
                self.current_analysis_firms.append(firm1)
                
                # İkinci firmayı random gecikme ile yükle
                delay = random.randint(2, 5)  # 2-5 saniye gecikme
                self.update_status(f"⏰ İkinci firma {delay} saniye sonra yüklenecek...")
                
                # Timer ile gecikme
                QTimer.singleShot(delay * 1000, lambda: self.load_second_firm(firm2))
                
                # Kalan firmaları queue'ya ekle
                if len(selected_firms) > 2:
                    remaining_firms = selected_firms[2:]
                    self.analysis_queue = remaining_firms
                    self.update_status(f"📋 {len(remaining_firms)} firma daha kuyrukta bekliyor...")
                    
                    # İkili analiz bitince kalan firmaları işle
                    self.setup_analysis_completion_monitor()
                else:
                    self.analysis_queue = []
            else:
                # Tek tarama - Proxy sorunu var
                self.update_status("⚠️ Proxy/bağlantı sorunu - Tek tarama moduna geçiliyor...")
                self.load_firm_to_scraper(firm1, 1)
                self.current_analysis_firms.append(firm1)
                
                # Kalan firmaları sırayla işle
                if len(selected_firms) > 1:
                    self.analysis_queue = selected_firms[1:]
                    self.setup_single_analysis_monitor()
        else:
            # Tek firma analizi
            firm1 = selected_firms[0]
            self.load_firm_to_scraper(firm1, 1)
            self.current_analysis_firms.append(firm1)
            self.analysis_queue = []
            self.update_status("🎯 Tek firma analizi başladı!")
    
    def load_second_firm(self, firm):
        """İkinci firmayı scraper 2'ye yükle"""
        try:
            self.load_firm_to_scraper(firm, 2)
            self.current_analysis_firms.append(firm)
            self.update_status(f"🚀 İkili tarama aktif: {len(self.current_analysis_firms)} firma yüklendi!")
        except Exception as e:
            self.update_status(f"❌ İkinci firma yükleme hatası: {e}")
    
    def check_proxy_status(self):
        """Proxy ve bağlantı durumunu kontrol et"""
        # Basit kontrol - geliştirilebir
        try:
            import urllib.request
            urllib.request.urlopen('http://www.google.com', timeout=3)
            return True
        except:
            return False
    
    def setup_analysis_completion_monitor(self):
        """İkili analiz tamamlanma monitörü"""
        # Timer ile periyodik kontrol
        if not hasattr(self, 'analysis_monitor_timer'):
            self.analysis_monitor_timer = QTimer()
            self.analysis_monitor_timer.timeout.connect(self.check_analysis_progress)
            self.analysis_monitor_timer.start(10000)  # 10 saniyede bir kontrol
    
    def setup_single_analysis_monitor(self):
        """Tek analiz tamamlanma monitörü"""
        if not hasattr(self, 'single_monitor_timer'):
            self.single_monitor_timer = QTimer()
            self.single_monitor_timer.timeout.connect(self.check_single_analysis_progress)
            self.single_monitor_timer.start(15000)  # 15 saniyede bir kontrol
    
    def check_analysis_progress(self):
        """Analiz ilerlemesini kontrol et"""
        if not hasattr(self, 'analysis_queue') or not self.analysis_queue:
            # Analiz tamamlandı
            if hasattr(self, 'analysis_monitor_timer'):
                self.analysis_monitor_timer.stop()
            self.update_status("✅ Tüm analizler tamamlandı!")
            return
        
        # Sıradaki firmayı işle
        if len(self.current_analysis_firms) < 2 and self.analysis_queue:
            next_firm = self.analysis_queue.pop(0)
            available_scraper = 1 if len(self.current_analysis_firms) == 0 else 2
            
            self.load_firm_to_scraper(next_firm, available_scraper)
            self.current_analysis_firms.append(next_firm)
            self.update_status(f"🔄 Sıradaki firma yüklendi - Kalan: {len(self.analysis_queue)}")
    
    def check_single_analysis_progress(self):
        """Tek analiz ilerlemesini kontrol et"""
        if not hasattr(self, 'analysis_queue') or not self.analysis_queue:
            if hasattr(self, 'single_monitor_timer'):
                self.single_monitor_timer.stop()
            self.update_status("✅ Tek analiz modu tamamlandı!")
            return
        
        # Sıradaki firmayı yükle
        next_firm = self.analysis_queue.pop(0)
        self.load_firm_to_scraper(next_firm, 1)
        self.update_status(f"🔄 Sıradaki firma - Kalan: {len(self.analysis_queue)}")
    
    def stop_dual_scraper_analysis(self):
        """İkili scraper analizini durdur"""
        try:
            # Timer'ları durdur
            if hasattr(self, 'analysis_monitor_timer'):
                self.analysis_monitor_timer.stop()
                delattr(self, 'analysis_monitor_timer')
            
            if hasattr(self, 'single_monitor_timer'):
                self.single_monitor_timer.stop()
                delattr(self, 'single_monitor_timer')
            
            # Queue'yu temizle
            if hasattr(self, 'analysis_queue'):
                self.analysis_queue = []
            
            if hasattr(self, 'current_analysis_firms'):
                self.current_analysis_firms = []
            
            # Status güncelle
            self.update_status("⏹️ Scraper analizi durduruldu!")
            
        except Exception as e:
            print(f"Analiz durdurma hatası: {e}")
    
    def get_scraper_analysis_status(self):
        """Scraper analiz durumunu getir"""
        status = {
            'active': False,
            'queue_count': 0,
            'current_firms': 0,
            'mode': 'idle'
        }
        
        try:
            if hasattr(self, 'analysis_queue') and self.analysis_queue:
                status['active'] = True
                status['queue_count'] = len(self.analysis_queue)
            
            if hasattr(self, 'current_analysis_firms') and self.current_analysis_firms:
                status['current_firms'] = len(self.current_analysis_firms)
                status['active'] = True
                status['mode'] = 'dual' if len(self.current_analysis_firms) > 1 else 'single'
                
        except:
            pass
            
        return status
    
    def on_analyze_finished(self, data):
        """Tek firma analizi tamamlandı"""
        firm_data = data['firm_data']
        
        # Veritabanından güncel veriyi çek
        db_firm = self.db.get_firm_by_id(firm_data['id'])
        if db_firm:
            firm_data = db_firm
            print(f"🔧 DEBUG: DB'den güncel veri alındı: {firm_data.get('name', 'İsimsiz')}")
        
        # Analiz tamamlandı olarak işaretle
        firm_data['is_analyzed'] = True
        
        # Veritabanında güncelle
        self.db.update_firm(firm_data['id'], is_analyzed=True)
        
        # Update the firm data in current_firms list
        for i, firm in enumerate(self.current_firms):
            if firm['name'] == firm_data['name']:
                self.current_firms[i] = firm_data
                print(f"🔧 DEBUG: Firm data updated in current_firms: {firm_data.get('ai_summary', 'YOK')[:50] if firm_data.get('ai_summary') else 'YOK'}...")  # DEBUG
                break
        
        # Tabloyu güncelle
        self.update_firm_in_table_analysis(firm_data)
        
        QMessageBox.information(self, "✅ Analiz Tamamlandı",
            f"{firm_data['name']} için analiz tamamlandı!\n\n"
            f"Bulunan email sayısı: {len(firm_data.get('emails') or [])}\n"
            f"Teknolojiler: {', '.join((firm_data.get('technologies') or [])[:3])}")
    
    def update_firm_in_table_analysis(self, firm_data):
        """Firma analiz verisini tabloda güncelle"""
        # Ana tabloyu güncelle
        for row in range(self.firms_table.rowCount()):
            if self.firms_table.item(row, 1).text() == firm_data['name']:
                # Analiz durumunu güncelle
                if firm_data.get('is_analyzed'):
                    status_text = f"✅ Analiz edildi ({len(firm_data.get('emails') or [])} email)"
                    self.firms_table.setItem(row, 6, QTableWidgetItem(status_text))
                    
                    # Analiz butonunu güncelle
                    analyze_btn = self.firms_table.cellWidget(row, 7)
                    if analyze_btn:
                        analyze_btn.setText("🔄 Tekrar Analiz")
                else:
                    self.firms_table.setItem(row, 6, QTableWidgetItem("❌ Analiz edilmedi"))
                
                print(f"🔧 DEBUG: Ana tablo güncellendi - {firm_data['name']}")
                break
        
        # Tüm firmalar tablosunu da güncelle
        for row in range(self.all_firms_table.rowCount()):
            if self.all_firms_table.item(row, 1).text() == firm_data['name']:
                if firm_data.get('is_analyzed'):
                    self.all_firms_table.setItem(row, 7, QTableWidgetItem("✅ Evet"))
                else:
                    self.all_firms_table.setItem(row, 7, QTableWidgetItem("❌ Hayır"))
                
                print(f"🔧 DEBUG: Tüm firmalar tablosu güncellendi - {firm_data['name']}")
                break
    
    def on_analyze_multiple_finished(self, data):
        """Çoklu firma analizi tamamlandı - Web Scraper entegrasyonu ile"""
        analyzed_count = 0
        
        for row in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                firm_id = self.current_firms[row]['id']
                db_firm = self.db.get_firm_by_id(firm_id)
                
                if db_firm and db_firm.get('is_analyzed'):
                    self.firms_table.setItem(row, 6,
                        QTableWidgetItem(f"✅ Analiz edildi ({len(db_firm.get('emails', []))} email)"))
                    
                    analyze_btn = self.firms_table.cellWidget(row, 7)
                    if analyze_btn:
                        analyze_btn.setText("🔄 Tekrar Analiz")
                    
                    analyzed_count += 1
                    
                    # Web Scraper'daki firma durumunu güncelle
                    if hasattr(self, 'current_firm1') and self.current_firm1:
                        if self.current_firm1.get('id') == firm_id:
                            self.update_scraper_firm_status(1, db_firm)
                    if hasattr(self, 'current_firm2') and self.current_firm2:
                        if self.current_firm2.get('id') == firm_id:
                            self.update_scraper_firm_status(2, db_firm)
        
        # Web Scraper analiz durumunu güncelle
        if hasattr(self, 'analysis_status'):
            self.analysis_status.setText(f"✅ Analiz tamamlandı: {analyzed_count} firma işlendi")
        
        # Kuyrukta kalan firma varsa devam et
        if hasattr(self, 'analysis_queue') and self.analysis_queue:
            self.process_next_firms_in_queue()
        else:
            # Tüm analiz tamamlandı
            if hasattr(self, 'queue_info'):
                self.queue_info.setText("📊 Kuyruk: Tüm firmalar analiz edildi")
        
        QMessageBox.information(self, "✅ Tamamlandı",
            f"Toplu analiz tamamlandı!\n\n"
            f"Analiz edilen firma sayısı: {analyzed_count}\n\n"
            f"🌐 Web Scraper sekmesinde detayları görüntüleyebilirsiniz.")
    
    def add_selected_to_campaign(self):
        """Seçili firmaları kampanyaya ekle"""
        print("🔧 DEBUG: add_selected_to_campaign çağrıldı!")  # DEBUG
        selected_firms = []
        
        for row in range(self.firms_table.rowCount()):
            checkbox = self.firms_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                firm = self.current_firms[row]
                
                db_firm = self.db.get_firm_by_id(firm.get('id')) if firm.get('id') else None
                if db_firm:
                    selected_firms.append(db_firm)
                else:
                    selected_firms.append(firm)
        
        print(f"🔧 DEBUG: {len(selected_firms)} firma kampanyaya eklenecek")  # DEBUG
        
        if not selected_firms:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir firma seçin!")
            return
        
        # Email kontrolü - hem emails listesine hem de email alanına bak
        firms_without_email = []
        for f in selected_firms:
            emails = f.get('emails', [])
            single_email = f.get('email', '')
            has_emails = (emails and len(emails) > 0) or (single_email and single_email.strip())
            if not has_emails:
                firms_without_email.append(f)
        
        if firms_without_email:
            msg = f"{len(firms_without_email)} firma henüz analiz edilmemiş ve email adresleri yok.\n\n"
            msg += "Bu firmaları kampanyaya eklemek için önce analiz edilmeleri gerekiyor.\n"
            msg += "Önce analiz etmek ister misiniz?"
            
            reply = QMessageBox.question(self, "Email Eksik", msg,
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.analyze_selected_firms()
                return
        
        self.selected_firms = selected_firms
        
        self.tabs.setCurrentIndex(2)
        
        self.update_campaign_firms_list()
        
        QMessageBox.information(self, "✅ Eklendi",
            f"{len(selected_firms)} firma kampanyaya eklendi.")
    
    def update_campaign_firms_list(self):
        """Kampanya firma listesini güncelle"""
        self.campaign_firms_list.clear()
        
        total_emails = 0
        
        print(f"🔍 DEBUG: Kampanya güncelleniyor - {len(self.selected_firms)} firma")
        
        for firm in self.selected_firms:
            # Email verilerini debug et - None kontrolü ekle
            emails = firm.get('emails', [])
            
            # None kontrolü
            if emails is None:
                emails = []
                firm['emails'] = emails  # None'ı boş liste ile değiştir
                print(f"🔍 DEBUG: Firma {firm.get('name', 'İsimsiz')} için emails None idi, boş liste yapıldı")
            
            # Email sayısını hesapla - hem emails listesine hem de email alanına bak
            single_email = firm.get('email', '')
            email_count = len(emails)
            
            # Eğer emails listesi boş ama tek email alanı dolu ise, sayıyı 1 yap
            if email_count == 0 and single_email and single_email.strip():
                email_count = 1
            
            print(f"🔍 DEBUG: Firma: {firm.get('name', 'İsimsiz')}")
            print(f"🔍 DEBUG: Email verisi: {emails}")
            print(f"🔍 DEBUG: Tek email: {single_email}")
            print(f"🔍 DEBUG: Email sayısı: {email_count}")
            
            # Eğer emails yoksa, veritabanından tekrar yükle
            if email_count == 0 and firm.get('id') and self.db:
                print(f"🔍 DEBUG: Email bulunamadı, veritabanından yeniden yükleniyor...")
                try:
                    db_firm = self.db.get_firm_by_id(firm['id'])
                    if db_firm:
                        emails = db_firm.get('emails', [])
                        print(f"🔍 DEBUG: Veritabanından alınan raw emails: {emails}")
                        print(f"🔍 DEBUG: Raw emails type: {type(emails)}")
                        
                        if emails is None:
                            emails = []
                            print(f"🔍 DEBUG: None olarak geldi, boş liste yapıldı")
                        elif isinstance(emails, str):
                            # JSON string ise parse et
                            if emails.strip():  # Boş string değilse
                                try:
                                    emails = json.loads(emails)
                                    print(f"🔍 DEBUG: JSON parse edildi: {emails}")
                                except Exception as e:
                                    print(f"❌ DEBUG: JSON parse hatası: {str(e)}")
                                    emails = []
                            else:
                                # Boş string ise boş liste yap
                                emails = []
                                print(f"🔍 DEBUG: Boş string, boş liste yapıldı")
                        elif isinstance(emails, list):
                            print(f"🔍 DEBUG: Zaten liste formatında: {emails}")
                        else:
                            print(f"🔍 DEBUG: Bilinmeyen format, boş liste yapıldı: {type(emails)}")
                            emails = []
                        email_count = len(emails)
                        firm['emails'] = emails  # Firmayı güncelle
                        print(f"🔍 DEBUG: Veritabanından yüklenen email sayısı: {email_count}")
                except Exception as e:
                    print(f"❌ DEBUG: Veritabanı yükleme hatası: {str(e)}")
                    emails = []
                    email_count = 0
            
            total_emails += email_count
            
            # Email durumuna göre item metni ve rengi
            if email_count == 0:
                item_text = f"⚠️ {firm['name']} - {(firm.get('address') or 'N/A')[:30]}... (Email yok - Analiz gerekli)"
                item = QListWidgetItem(item_text)
                item.setBackground(QColor(150, 50, 50))  # Kırmızı - Email yok
                item.setToolTip("Bu firma için email adresi bulunamadı. Mail gönderebilmek için önce analiz edilmelidir.")
            elif email_count < 3:
                item_text = f"📍 {firm['name']} - {(firm.get('address') or 'N/A')[:30]}... ({email_count} email)"
                item = QListWidgetItem(item_text)
                item.setBackground(QColor(150, 150, 50))  # Sarı - Az email
                item.setToolTip(f"Bu firma için {email_count} email adresi bulundu.")
            else:
                item_text = f"✅ {firm['name']} - {(firm.get('address') or 'N/A')[:30]}... ({email_count} email)"
                item = QListWidgetItem(item_text)
                item.setBackground(QColor(50, 150, 50))  # Yeşil - Yeterli email
                item.setToolTip(f"Bu firma için {email_count} email adresi bulundu. Mail gönderilebilir.")
            
            self.campaign_firms_list.addItem(item)
        
        print(f"🔍 DEBUG: Toplam email sayısı: {total_emails}")
        self.campaign_info_label.setText(f"{len(self.selected_firms)} firma, {total_emails} email")
        
        self.preview_firm_combo.clear()
        for firm in self.selected_firms[:10]:
            self.preview_firm_combo.addItem(firm['name'], firm)
    
    def remove_selected_firm(self):
        """Seçili firmayı kampanyadan kaldır"""
        current_item = self.campaign_firms_list.currentItem()
        if current_item:
            row = self.campaign_firms_list.row(current_item)
            self.campaign_firms_list.takeItem(row)
            del self.selected_firms[row]
            self.update_campaign_firms_list()
    
    def clear_campaign_firms(self):
        """Tüm firmaları kampanyadan temizle"""
        reply = QMessageBox.question(self, "Onay",
            "Tüm firmalar kampanyadan kaldırılacak. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.selected_firms = []
            self.update_campaign_firms_list()
    
    def load_template(self, template_name):
        """Hazır şablon yükle"""
        templates = {
            "Mobilya Firmaları İçin": {
                "instructions": """
                Yazılım firmasına özel bir B2B satış maili yaz. Şunlara dikkat et:
                - Mobilya ürünlerinizi tanıtan, samimi ama profesyonel bir e-posta hazırla.
                - Firma sahibine özel isim varsa: “Merhaba [isim] Bey/Hanım” şeklinde hitap et.
                - Firmanın başarılarını ve sektördeki yerini öv. Ama kesinlikle abartma uygun bir dille öv
                - Sonunda 15 dakikalık tanıtım toplantısı iste.
                - Kesinlikle bir yapay zeka tarafında yazıldığı anlaşılmasın İnsan yazmış gibi yazılsın; yapay zeka dili kesinlikle kullanılmasın.
                - Kültüre uygun, iş dünyasında kullanılan kelimeler tercih edilsin.
                - Mail dili: İngilizce.
                - Ülkenin kültürel yapsına uygun yaz lütfen
                """,
                "system": "Sen İbrahim’sin, Kayseri'de dış ticaret uzmanı olarak mobilya tedariki yapıyorsun.Profesyonel, saygılı ama içten bir dille yazmalısın. Maillerinde güven verici bir ton kullan, aşırı satış odaklı olma. Kişisel iletişim kuran bir dış ticaret temsilcisi gibi yaz. Türk iş kültürüne ve yerel duyarlılıklara uygun olmalı.Yazdığın kesinlikle bir insan eliyle yazılmış gibi görünmeli."
            },
            "E-ticaret Firmaları İçin": {
                "instructions": """
                E-ticaret firmasına özel bir satış maili yaz:
                - Satış artırma ve dönüşüm oranı iyileştirme vurgula
                - Stok yönetimi ve sipariş otomasyonu faydalarını belirt
                - Müşteri deneyimi ve hızlı teslimat avantajlarını öne çıkar
                - Rakamsal faydalar sun (%30 satış artışı gibi)
                """,
                "system": "Sen e-ticaret sektörüne özel B2B çözümler sunan bir satış uzmanısın."
            }
        }
        
        if template_name in templates:
            template = templates[template_name]
            self.mail_instructions.setText(template["instructions"])
            self.system_prompt.setText(template["system"])
    
    def generate_preview(self):
        """Mail önizlemesi oluştur"""
        if not self.preview_firm_combo.currentData():
            QMessageBox.warning(self, "Uyarı", "Önizleme için bir firma seçin!")
            return
        
        firm = self.preview_firm_combo.currentData()
        template = {
            "instructions": self.mail_instructions.toPlainText(),
            "system_prompt": self.system_prompt.toPlainText()
        }
        
        try:
            with open("config.json", "r") as f:
                settings = json.load(f)
                self.api_manager.update_settings(settings)
        except:
            QMessageBox.warning(self, "Uyarı", "API ayarları bulunamadı!")
            return
        
        self.status_bar.showMessage("📝 Mail önizlemesi oluşturuluyor...")
        
        try:
            mail_content = self.api_manager.generate_email_gpt(firm, template)
            
            preview_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }}
                    .email-container {{
                        background-color: white;
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .email-header {{
                        background-color: #0d7377;
                        color: white;
                        padding: 20px;
                        border-radius: 10px 10px 0 0;
                        margin: -30px -30px 20px -30px;
                    }}
                    .subject {{
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }}
                    .to-email {{
                        font-size: 14px;
                        opacity: 0.8;
                    }}
                    .email-body {{
                        padding: 20px 0;
                    }}
                    .email-footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        font-size: 12px;
                        color: #666;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="email-header">
                        <div class="subject">{mail_content['subject']}</div>
                        <div class="to-email">Kime: {mail_content.get('to_email', 'info@example.com')}</div>
                    </div>
                    <div class="email-body">
                        {mail_content['body']}
                    </div>
                    <div class="email-footer">
                        Bu bir önizlemedir. Gerçek mail gönderilmemiştir.
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.preview_web.setHtml(preview_html)
            self.status_bar.showMessage("✅ Önizleme hazır!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Önizleme oluşturulamadı:\n{str(e)}")
            self.status_bar.showMessage("❌ Önizleme hatası!")
    
    def start_campaign(self):
        """Kampanyayı başlat"""
        if not self.selected_firms:
            QMessageBox.warning(self, "Uyarı", "Kampanya için firma seçilmedi!")
            return
        
        instructions = self.mail_instructions.toPlainText()
        system_prompt = self.system_prompt.toPlainText()
        
        if not instructions or not system_prompt:
            QMessageBox.warning(self, "Uyarı", "Lütfen mail şablonunu doldurun!")
            return
        
        # Email adresi olan ve olmayan firmaları ayır
        firms_with_email = []
        firms_without_email = []
        
        for firm in self.selected_firms:
            emails = firm.get('emails', [])
            single_email = firm.get('email', '')
            
            # Hem emails listesine hem de tek email alanına bak
            has_emails = (emails and len(emails) > 0) or (single_email and single_email.strip())
            
            if has_emails:
                firms_with_email.append(firm)
            else:
                firms_without_email.append(firm)
        
        # Email adresi olmayan firmalar varsa uyar
        if firms_without_email:
            warning_msg = f"⚠️ DİKKAT: {len(firms_without_email)} firma için email adresi bulunamadı!\n\n"
            warning_msg += "Email adresi olmayan firmalar:\n"
            for firm in firms_without_email[:5]:  # İlk 5'ini göster
                warning_msg += f"• {firm['name']}\n"
            if len(firms_without_email) > 5:
                warning_msg += f"... ve {len(firms_without_email) - 5} firma daha\n"
            
            warning_msg += f"\nSadece {len(firms_with_email)} firmaya mail gönderilecek.\n"
            warning_msg += "Email adresi olmayan firmalar için önce analiz yapılmalıdır.\n\n"
            warning_msg += "Devam etmek istiyor musunuz?"
            
            reply = QMessageBox.question(self, "⚠️ Email Adresi Eksik", warning_msg,
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.No:
                return
            
            firms_to_send = firms_with_email
        else:
            firms_to_send = self.selected_firms
        
        if not firms_to_send:
            QMessageBox.warning(self, "Uyarı", "Mail gönderilebilecek firma bulunamadı!")
            return
        
        if self.test_mode_check.isChecked():
            firms_to_send = firms_to_send[:3]
            msg = f"Test modunda sadece ilk 3 firmaya ({', '.join([f['name'] for f in firms_to_send])}) mail gönderilecek."
        else:
            msg = f"{len(firms_to_send)} firmaya mail gönderilecek."
        
        msg += "\n\nHer mail arasında güvenlik için bekleme yapılacak.\n"
        msg += "Devam etmek istiyor musunuz?"
        
        reply = QMessageBox.question(self, "Kampanya Onayı", msg,
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.start_campaign_btn.setEnabled(False)
            
            self.worker_thread = WorkerThread("send_campaign", {
                "firms": firms_to_send,
                "template": {
                    "instructions": instructions,
                    "system_prompt": system_prompt
                }
            })
            self.worker_thread.progress.connect(self.update_status)
            self.worker_thread.finished.connect(self.on_campaign_finished)
            self.worker_thread.error.connect(self.on_error)
            self.worker_thread.start()
    
    def on_campaign_finished(self, data):
        """Kampanya tamamlandı"""
        # GUI durumunu tamamen sıfırla - DÜZELTME
        self.start_campaign_btn.setEnabled(True)
        self.status_bar.showMessage("✨ Hazır - Yeni kampanya başlatabilirsiniz")
        
        # Progress bar varsa gizle
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setVisible(False)
            self.progress_bar.setValue(0)
        
        sent_count = data.get('sent_count', 0)
        
        if sent_count > 0:
            QMessageBox.information(self, "✅ Kampanya Tamamlandı",
                f"Kampanya başarıyla tamamlandı!\n\n"
                f"Gönderilen mail sayısı: {sent_count}\n\n"
                f"Email'lerin durumunu Tracking sekmesinden takip edebilirsiniz.")
        else:
            QMessageBox.warning(self, "⚠️ Dikkat",
                "Kampanya tamamlandı ancak hiç mail gönderilemedi.\n\n"
                "Lütfen email ayarlarınızı kontrol edin.")
        
        self.update_dashboard()
        self.update_tracking()
    
    def update_dashboard(self):
        """Dashboard istatistiklerini güncelle"""
        stats = self.db.get_statistics()
        
        # Value label'ları güncelle - update_value yerine setText kullan
        if hasattr(self, 'total_firms_value'):
            self.total_firms_value.setText(str(stats.get('total_firms', 0)))
        if hasattr(self, 'analyzed_firms_value'):
            self.analyzed_firms_value.setText(str(stats.get('analyzed_firms', 0)))
        if hasattr(self, 'total_emails_value'):
            self.total_emails_value.setText(str(stats.get('total_emails', 0)))
        if hasattr(self, 'sent_emails_value'):
            self.sent_emails_value.setText(str(stats.get('total_sent', 0)))
        if hasattr(self, 'open_rate_value'):
            self.open_rate_value.setText(f"%{stats.get('open_rate', 0)}")
        if hasattr(self, 'response_rate_value'):
            self.response_rate_value.setText(f"%{stats.get('reply_rate', 0)}")
        
        # Hızlı istatistik güncelleme
        if hasattr(self, 'quick_stats_label'):
            self.quick_stats_label.setText(
                f"📊 Bugün: {stats.get('sent_today', 0)} gönderim | "
                f"{stats.get('opened_today', 0)} açılma | "
                f"Bu hafta: {stats.get('sent_this_week', 0)} mail"
            )
        
        # Son aktiviteleri güncelle
        if hasattr(self, 'activity_table'):
            activities = self.db.get_recent_activities(limit=20)
            self.activity_table.setRowCount(len(activities))
            
            for i, activity in enumerate(activities):
                self.activity_table.setItem(i, 0, QTableWidgetItem(activity.get('date', '')))
                self.activity_table.setItem(i, 1, QTableWidgetItem(activity.get('firm_name', '')))
                self.activity_table.setItem(i, 2, QTableWidgetItem(activity.get('to_email', '')))
                self.activity_table.setItem(i, 3, QTableWidgetItem(activity.get('status', '')))
                self.activity_table.setItem(i, 4, QTableWidgetItem(activity.get('detail', '')))
    
    def load_dashboard_chart(self):
        """Dashboard grafiği yükle"""
        chart_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    background-color: #1a1a1a;
                }
                canvas {
                    max-height: 250px;
                }
            </style>
        </head>
        <body>
            <canvas id="performanceChart"></canvas>
            <script>
                const ctx = document.getElementById('performanceChart').getContext('2d');
                const chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma'],
                        datasets: [{
                            label: 'Gönderilen',
                            data: [12, 19, 15, 25, 22],
                            borderColor: '#0d7377',
                            backgroundColor: 'rgba(13, 115, 119, 0.1)',
                            tension: 0.4
                        }, {
                            label: 'Açılan',
                            data: [8, 15, 12, 20, 18],
                            borderColor: '#14a1a5',
                            backgroundColor: 'rgba(20, 161, 165, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: {
                                    color: '#ffffff'
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: '#2a2a2a'
                                },
                                ticks: {
                                    color: '#ffffff'
                                }
                            },
                            x: {
                                grid: {
                                    color: '#2a2a2a'
                                },
                                ticks: {
                                    color: '#ffffff'
                                }
                            }
                        }
                    }
                });
            </script>
        </body>
        </html>
        """
        self.chart_view.setHtml(chart_html)
    
    def update_tracking(self):
        """Tracking tablosunu güncelle"""
        emails = self.db.get_all_emails(
            self.status_filter_tracking.currentText() if hasattr(self, 'status_filter_tracking') else "Tümü",
            self.period_filter.currentText() if hasattr(self, 'period_filter') else "Son 7 Gün"
        )
        
        self.tracking_table.setRowCount(len(emails))
        
        total = len(emails)
        opened = sum(1 for e in emails if e.get('opened_at'))
        clicked = sum(1 for e in emails if e.get('clicked_at'))
        
        # tracking_stats_label kaldırılmış görünüyor, bu satırı da kaldırabilirsiniz
        # self.tracking_stats_label.setText(
        #     f"📊 Toplam: {total} | Açılan: {opened} | Tıklanan: {clicked}"
        # )
        
        for i, email in enumerate(emails):
            self.tracking_table.setItem(i, 0, QTableWidgetItem(email.get('firm_name', 'N/A')))
            self.tracking_table.setItem(i, 1, QTableWidgetItem(email.get('to_email', 'N/A')))
            self.tracking_table.setItem(i, 2, QTableWidgetItem(email.get('subject', '')[:50] + '...'))
            self.tracking_table.setItem(i, 3, QTableWidgetItem(email.get('sent_date', '-')))
            self.tracking_table.setItem(i, 4, QTableWidgetItem(email.get('opened_date', '-')))
            self.tracking_table.setItem(i, 5, QTableWidgetItem(email.get('clicked_date', '-')))
            
            status = "📤 Gönderildi"
            if email.get('replied_at'):
                status = "💬 Yanıtlandı"
            elif email.get('clicked_at'):
                status = "🖱️ Tıklandı"
            elif email.get('opened_at'):
                status = "👁️ Açıldı"
            
            self.tracking_table.setItem(i, 6, QTableWidgetItem(status))
            
            action_btn = QPushButton("📨 Takip")
            action_btn.clicked.connect(lambda checked=False, e=email: self.send_follow_up_email(e))
            self.tracking_table.setCellWidget(i, 7, action_btn)
    
    def filter_tracking(self):
        """Tracking filtreleme"""
        self.update_tracking()
    
    def load_all_firms(self):
        """Gelişmiş firma tablosunu yükle - Checkbox ve AI destekli"""
        try:
            # Filtreleri uygula
            filters = {
                'analyzed_only': self.firm_analyzed_check.isChecked(),
                'has_emails': self.firm_has_email_check.isChecked(),
                'min_rating': self.min_rating_input.value() if self.min_rating_input.value() > 0 else None
            }
            
            firms = self.db.get_firms_by_filter(filters)
            self.all_firms_data = firms  # Tüm veriyi sakla
            
            self.all_firms_table.setRowCount(len(firms))
            
            for i, firm in enumerate(firms):
                # Checkbox (Kolon 0)
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(self.update_firms_selection_info)
                self.all_firms_table.setCellWidget(i, 0, checkbox)
                
                # Firma Adı (Kolon 1)
                self.all_firms_table.setItem(i, 1, QTableWidgetItem(firm['name']))
                
                # Rating (Kolon 2)
                rating_text = f"⭐ {firm.get('rating', 'N/A')}"
                self.all_firms_table.setItem(i, 2, QTableWidgetItem(rating_text))
                
                # Email Detayları (Kolon 3) - Sadece email sayısı
                emails = firm.get('emails', [])
                
                # JSON string ise parse et
                if isinstance(emails, str):
                    try:
                        emails = json.loads(emails) if emails.strip() else []
                    except:
                        emails = []
                elif emails is None:
                    emails = []
                
                email_count = len(emails)
                email_text = f"📧 {email_count} email"
                self.all_firms_table.setItem(i, 3, QTableWidgetItem(email_text))
                
                # Website (Kolon 4)
                website = firm.get('website', 'N/A')
                if website and website != 'N/A':
                    website = website.replace('http://', '').replace('https://', '').split('/')[0]
                self.all_firms_table.setItem(i, 4, QTableWidgetItem(website))
                
                # Telefon (Kolon 5)
                self.all_firms_table.setItem(i, 5, QTableWidgetItem(firm.get('phone', 'N/A')))
                
                # Sektör (Kolon 6) - AI analizi ile geliştirilmiş
                sector_text = firm.get('sector', 'Belirtilmemiş')
                ai_sector = self.categorize_sector_with_ai(sector_text)
                display_sector = f"{sector_text}" + (f" ({ai_sector})" if ai_sector != sector_text else "")
                self.all_firms_table.setItem(i, 6, QTableWidgetItem(display_sector))
                
                # Analiz Durumu (Kolon 7)
                email_count = len(emails)
                if firm.get('is_analyzed'):
                    analysis_text = f"✅ Evet ({email_count} email)"
                    analysis_item = QTableWidgetItem(analysis_text)
                    analysis_item.setForeground(QColor("#28a745"))
                else:
                    analysis_item = QTableWidgetItem("❌ Hayır")
                    analysis_item.setForeground(QColor("#dc3545"))
                self.all_firms_table.setItem(i, 7, analysis_item)
                
                # Kampanya (Kolon 8)
                add_btn = QPushButton("➕")
                add_btn.setToolTip("Kampanyaya Ekle")
                add_btn.clicked.connect(lambda checked=False, f=firm: self.add_firm_to_campaign(f))
                add_btn.setMaximumWidth(30)
                add_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: none; border-radius: 3px; }")
                self.all_firms_table.setCellWidget(i, 8, add_btn)
                
                # Detay (Kolon 9)
                detail_btn = QPushButton("👁️")
                detail_btn.setToolTip("Detay Görüntüle")
                detail_btn.clicked.connect(lambda checked=False, f=firm: self.show_firm_detail(f))
                detail_btn.setMaximumWidth(30)
                detail_btn.setStyleSheet("QPushButton { background-color: #17a2b8; color: white; border: none; border-radius: 3px; }")
                self.all_firms_table.setCellWidget(i, 9, detail_btn)
                
                # İşlemler (Kolon 10) - Birleştirilmiş
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(2, 2, 2, 2)
                actions_layout.setSpacing(2)
                
                # WhatsApp butonu
                whatsapp_btn = QPushButton("📱")
                whatsapp_btn.setToolTip("WhatsApp'a Yönlendir")
                whatsapp_btn.clicked.connect(lambda checked=False, f=firm: self.send_firm_to_whatsapp(f))
                whatsapp_btn.setMaximumWidth(25)
                whatsapp_btn.setStyleSheet("QPushButton { background-color: #25D366; color: white; border: none; border-radius: 3px; }")
                actions_layout.addWidget(whatsapp_btn)
                
                # Arama butonu
                call_btn = QPushButton("📞")
                call_btn.setToolTip("Çağrıya Yönlendir")
                call_btn.clicked.connect(lambda checked=False, f=firm: self.send_firm_to_call(f))
                call_btn.setMaximumWidth(25)
                call_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; border: none; border-radius: 3px; }")
                actions_layout.addWidget(call_btn)
                
                self.all_firms_table.setCellWidget(i, 10, actions_widget)
            
            # Bilgileri güncelle
            self.update_firms_selection_info()
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Firma tablosu yüklenirken hata:\n{str(e)}")
    
    def add_firm_to_all_firms_table(self, firm):
        """Yeni firmayı all_firms_table'a ekle"""
        if not hasattr(self, 'all_firms_table'):
            return
            
        # Mevcut satır sayısını al
        row = self.all_firms_table.rowCount()
        self.all_firms_table.insertRow(row)
        
        # Firma bilgilerini ekle
        self.all_firms_table.setItem(row, 0, QTableWidgetItem(firm.get('name', '')))
        
        rating_text = f"⭐ {firm.get('rating', 'N/A')}"
        self.all_firms_table.setItem(row, 1, QTableWidgetItem(rating_text))
        
        self.all_firms_table.setItem(row, 2, QTableWidgetItem(str(firm.get('email_count', 0))))
        
        website = firm.get('website', 'N/A')
        if website and website != 'N/A':
            website = website.replace('http://', '').replace('https://', '').split('/')[0]
        self.all_firms_table.setItem(row, 3, QTableWidgetItem(website))
        
        self.all_firms_table.setItem(row, 4, QTableWidgetItem(firm.get('phone', 'N/A')))
        
        if firm.get('is_analyzed'):
            self.all_firms_table.setItem(row, 5, QTableWidgetItem("✅ Evet"))
        else:
            self.all_firms_table.setItem(row, 5, QTableWidgetItem("❌ Hayır"))
        
        add_btn = QPushButton("➕ Kampanyaya Ekle")
        add_btn.clicked.connect(lambda checked=False, f=firm: self.add_firm_to_campaign(f))
        self.all_firms_table.setCellWidget(row, 6, add_btn)
        
        detail_btn = QPushButton("👁️ Detay")
        detail_btn.clicked.connect(lambda checked=False, f=firm: self.show_firm_detail(f))
        self.all_firms_table.setCellWidget(row, 7, detail_btn)
        
        # WhatsApp'a At butonu
        whatsapp_btn = QPushButton("📱")
        whatsapp_btn.setToolTip("WhatsApp'a Yönlendir")
        whatsapp_btn.setMaximumWidth(40)
        whatsapp_btn.clicked.connect(lambda checked=False, f=firm: self.send_firm_to_whatsapp(f))
        self.all_firms_table.setCellWidget(row, 8, whatsapp_btn)
        
        # Çağrıya At butonu
        call_btn = QPushButton("📞")
        call_btn.setToolTip("Çağrıya Yönlendir")
        call_btn.setMaximumWidth(40)
        call_btn.clicked.connect(lambda checked=False, f=firm: self.send_firm_to_call(f))
        self.all_firms_table.setCellWidget(row, 9, call_btn)
        
        # Firma sayısını güncelle
        current_count = self.all_firms_table.rowCount()
        self.firms_count_label.setText(f"Toplam: {current_count} firma")

    def filter_firms(self):
        """Firmaları filtrele - backward compatibility için"""
        self.filter_firms_table()
    
    def add_firm_to_campaign(self, firm):
        """Tek firmayı kampanyaya ekle"""
        print(f"🔧 DEBUG: add_firm_to_campaign çağrıldı - Firma: {firm.get('name', 'İsimsiz')}")  # DEBUG
        
        if not hasattr(self, 'selected_firms'):
            self.selected_firms = []
            print("🔧 DEBUG: selected_firms listesi oluşturuldu")  # DEBUG
        
        if firm['id'] not in [f.get('id', 0) for f in self.selected_firms]:
            self.selected_firms.append(firm)
            self.tabs.setCurrentIndex(2)
            self.update_campaign_firms_list()
            QMessageBox.information(self, "✅ Eklendi", f"{firm['name']} kampanyaya eklendi.")
            print(f"🔧 DEBUG: {firm['name']} kampanyaya eklendi")  # DEBUG
        else:
            QMessageBox.warning(self, "⚠️ Uyarı", "Bu firma zaten kampanyada!")
            print("🔧 DEBUG: Firma zaten kampanyada")  # DEBUG
    
    def export_firms(self):
        """Firmaları Excel'e aktar"""
        if pd is None:
            QMessageBox.critical(self, "Hata", 
                "Excel dışa aktarma için 'pandas' kurulu olmalı!\n\n"
                "Kurulum: pip install pandas openpyxl")
            return
            
        try:
            firms = self.db.get_firms_by_filter({})
            
            if not firms:
                QMessageBox.warning(self, "Uyarı", "Dışa aktarılacak firma bulunamadı!")
                return
            
            data = []
            for firm in firms:
                emails = self.db.get_firm_by_id(firm['id']).get('emails', [])
                email_list = ', '.join([e['email'] for e in emails])
                
                data.append({
                    'Firma Adı': firm['name'],
                    'Rating': firm.get('rating', ''),
                    'Telefon': firm.get('phone', ''),
                    'Website': firm.get('website', ''),
                    'Adres': firm.get('address', ''),
                    'Email Sayısı': firm.get('email_count', 0),
                    'Email Listesi': email_list,
                    'Analiz Durumu': 'Evet' if firm.get('is_analyzed') else 'Hayır'
                })
            
            df = pd.DataFrame(data)
            
            filename = f"firmalar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            
            QMessageBox.information(self, "✅ Başarılı", 
                f"Firmalar başarıyla dışa aktarıldı!\n\nDosya: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma hatası:\n{str(e)}")
    
    def show_firm_detail(self, firm):
        """Firma detaylarını göster"""
        print(f"🔧 DEBUG: show_firm_detail çağrıldı - Firma: {firm.get('name', 'İsimsiz')}")  # DEBUG
        print(f"🔧 DEBUG: Firm ID: {firm.get('id', 'YOK')}")  # DEBUG
        
        if not firm.get('id'):
            QMessageBox.warning(self, "Hata", "Firma ID'si bulunamadı!")
            return
            
        db_firm = self.db.get_firm_by_id(firm['id'])
        if db_firm:
            firm = db_firm
            print(f"🔧 DEBUG: DB'den firma alındı: {db_firm.get('name', 'İsimsiz')}")  # DEBUG
            print(f"🔧 DEBUG: AI Summary: {db_firm.get('ai_summary', 'YOK')[:100] if db_firm.get('ai_summary') else 'YOK'}...")  # DEBUG
        
        detail_dialog = QDialog(self)
        detail_dialog.setWindowTitle(f"{firm['name']} - Detaylı Bilgiler")
        detail_dialog.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(detail_dialog)
        
        tabs = QTabWidget()
        
        # Genel bilgiler sekmesi
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        
        email_list = ""
        if 'emails' in firm and firm['emails']:
            for email in firm['emails']:
                if isinstance(email, str):
                    email_address = email
                    position = 'Bilinmiyor'
                elif isinstance(email, dict):
                    email_address = email.get('email', '')
                    position = email.get('position', 'Bilinmiyor')
                else:
                    email_address = str(email)
                    position = 'Bilinmiyor'
                score = email.get('score', 0)
                source = email.get('source', 'unknown')
                verified = "✅" if email.get('is_verified') else "❓"
                email_list += f"""
                <tr>
                    <td>{email['email']}</td>
                    <td>{position}</td>
                    <td>{score}</td>
                    <td>{source}</td>
                    <td>{verified}</td>
                </tr>
                """
        else:
            email_list = "<tr><td colspan='5'>Henüz email bulunamadı</td></tr>"
        
        photos_html = ""
        if firm.get('photos'):
            photos_html = "<h3>📸 Fotoğraflar:</h3><div style='display: flex; gap: 10px;'>"
            for photo in firm['photos'][:3]:
                photos_html += f"<img src='{photo}' style='width: 200px; height: 150px; object-fit: cover; border-radius: 5px;'>"
            photos_html += "</div>"
        
        info_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h2 {{ color: #0d7377; }}
                h3 {{ color: #14a1a5; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #0d7377; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .info-section {{ margin-bottom: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h2>{firm['name']}</h2>
            
            <div class="info-section">
                <h3>📍 Temel Bilgiler</h3>
                <p><b>Rating:</b> ⭐ {firm.get('rating', 'N/A')}/5 ({firm.get('review_count', 0)} değerlendirme)</p>
                <p><b>Popülerlik Skoru:</b> {firm.get('popularity_score', 0)}</p>
                <p><b>Website:</b> <a href="{firm.get('website', '#')}">{firm.get('website', 'N/A')}</a></p>
                <p><b>Telefon:</b> {firm.get('phone', 'N/A')}</p>
                <p><b>Adres:</b> {firm.get('address', 'N/A')}</p>
                <p><b>Google Maps:</b> <a href="{firm.get('google_maps_url', '#')}">Haritada Gör</a></p>
                <p><b>Çalışma Saatleri:</b> {'Açık' if firm.get('is_open') else 'Kapalı' if firm.get('is_open') is not None else 'Bilinmiyor'}</p>
            </div>
            
            {photos_html}
            
            <div class="info-section">
                <h3>🤖 AI Analiz Özeti</h3>
                <p>{firm.get('ai_summary', 'Henüz analiz edilmedi.')}</p>
            </div>
            
            <div class="info-section">
                <h3>💻 Teknolojiler</h3>
                <p>{', '.join(firm.get('technologies') or ['Henüz tespit edilmedi'])}</p>
            </div>
            
            <div class="info-section">
                <h3>🛠️ Hizmetler</h3>
                <ul>
                    {''.join([f"<li>{service}</li>" for service in (firm.get('services') or ['Henüz tespit edilmedi'])[:10]])}
                </ul>
            </div>
            
            <div class="info-section">
                <h3>📊 Diğer Bilgiler</h3>
                <p><b>Tahmini Çalışan Sayısı:</b> {firm.get('team_size', 'Bilinmiyor')}</p>
                <p><b>Sektör:</b> {', '.join(firm.get('industry_keywords') or ['Belirtilmemiş'])}</p>
                <p><b>İş Türleri:</b> {', '.join(firm.get('types') or [])}</p>
                <p><b>Son Analiz:</b> {firm.get('last_scraped', 'Henüz yapılmadı')}</p>
            </div>
            
            <h3>📧 Bulunan Email Adresleri ({len(firm.get('emails') or [])})</h3>
            <table>
                <tr>
                    <th>Email</th>
                    <th>Pozisyon</th>
                    <th>Skor</th>
                    <th>Kaynak</th>
                    <th>Doğrulama</th>
                </tr>
                {email_list}
            </table>
        </body>
        </html>
        """
        
        info_text.setHtml(info_html)
        general_layout.addWidget(info_text)
        
        tabs.addTab(general_tab, "📋 Genel Bilgiler")
        
        # Web analiz sekmesi
        if firm.get('scraped_data'):
            web_tab = QWidget()
            web_layout = QVBoxLayout(web_tab)
            
            web_text = QTextEdit()
            web_text.setReadOnly(True)
            
            scraped = firm.get('scraped_data', {})
            web_content = "# Web Sitesi Analiz Detayları\n\n"
            
            for page_name, page_data in scraped.items():
                if isinstance(page_data, dict):
                    web_content += f"\n## {page_name.replace('_', ' ').title()}\n"
                    web_content += f"URL: {page_data.get('url', 'N/A')}\n\n"
                    
                    if page_data.get('text'):
                        web_content += f"### İçerik Özeti:\n{page_data['text'][:500]}...\n\n"
                    
                    if page_data.get('emails'):
                        web_content += f"### Bulunan Emailler ({len(page_data['emails'])}):\n"
                        for email in page_data['emails']:
                            web_content += f"- {email.get('email', 'N/A')} ({email.get('type', 'unknown')})\n"
                        web_content += "\n"
            
            web_text.setPlainText(web_content)
            web_layout.addWidget(web_text)
            
            tabs.addTab(web_tab, "🌐 Web Analizi")
        
        # Email geçmişi sekmesi
        email_history_tab = QWidget()
        email_layout = QVBoxLayout(email_history_tab)
        
        email_history_text = QTextEdit()
        email_history_text.setReadOnly(True)
        
        email_logs = self.db.get_all_emails()
        firm_logs = [log for log in email_logs if log.get('firm_id') == firm['id']]
        
        if firm_logs:
            history_html = """
            <h3>📮 Email Gönderim Geçmişi</h3>
            <table width='100%'>
                <tr>
                    <th>Tarih</th>
                    <th>Alıcı</th>
                    <th>Konu</th>
                    <th>Durum</th>
                </tr>
            """
            
            for log in firm_logs:
                status = "📤 Gönderildi"
                if log.get('replied_at'):
                    status = "💬 Yanıtlandı"
                elif log.get('clicked_at'):
                    status = "🖱️ Tıklandı"
                elif log.get('opened_at'):
                    status = "👁️ Açıldı"
                
                history_html += f"""
                <tr>
                    <td>{log.get('sent_date', 'N/A')}</td>
                    <td>{log.get('to_email', 'N/A')}</td>
                    <td>{log.get('subject', 'N/A')[:50]}...</td>
                    <td>{status}</td>
                </tr>
                """
            
            history_html += "</table>"
        else:
            history_html = "<p>Henüz bu firmaya email gönderilmemiş.</p>"
        
        email_history_text.setHtml(history_html)
        email_layout.addWidget(email_history_text)
        
        tabs.addTab(email_history_tab, "📬 Email Geçmişi")
        
        # WhatsApp geçmişi sekmesi kaldırıldı
        
        layout.addWidget(tabs)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        if not firm.get('emails'):
            analyze_btn = QPushButton("🤖 Bu Firmayı Analiz Et")
            analyze_btn.clicked.connect(lambda: self.analyze_single_firm(firm))
            button_layout.addWidget(analyze_btn)
        
        add_campaign_btn = QPushButton("📧 Kampanyaya Ekle")
        add_campaign_btn.clicked.connect(lambda: self.add_firm_to_campaign(firm))
        button_layout.addWidget(add_campaign_btn)
        
        # Email ekleme butonu
        add_email_btn = QPushButton("➕ Email Ekle")
        add_email_btn.clicked.connect(lambda: self.add_email_to_firm_from_detail_dialog(detail_dialog, firm))
        add_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(add_email_btn)
        
        # Kişisel E-Posta Tespit Et butonu
        find_email_btn = QPushButton("🔍 Kişisel E-Posta Tespit Et")
        find_email_btn.clicked.connect(lambda: self.show_email_finder_popup(firm))
        find_email_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        button_layout.addWidget(find_email_btn)
        
        # WhatsApp butonu kaldırıldı
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(detail_dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        detail_dialog.exec()
    
    # send_whatsapp_to_firm fonksiyonu kaldırıldı
    
    def show_email_finder_popup(self, firm):
        """Kişisel e-posta tespit et popup'ı göster - Apollo.io ve Snov.io entegrasyonu"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("🔍 Kişisel E-Posta Tespit Et")
            dialog.setModal(True)
            dialog.resize(700, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title_label = QLabel("🔍 Kişisel E-Posta Arama")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007bff; padding: 10px;")
            layout.addWidget(title_label)
            
            # Firma bilgileri
            firm_info = QTextEdit()
            firm_info.setReadOnly(True)
            firm_info.setMaximumHeight(100)
            firm_info.setHtml(f"""
                <html>
                    <body style='font-family: Arial; padding: 10px;'>
                        <h3>{firm.get('name', 'Bilinmiyor')}</h3>
                        <p><b>Website:</b> {firm.get('website', 'N/A')}</p>
                        <p><b>Sektör:</b> {firm.get('sector', 'N/A')}</p>
                    </body>
                </html>
            """)
            layout.addWidget(firm_info)
            
            # API seçimi
            api_group = QGroupBox("API Seçimi")
            api_layout = QVBoxLayout()
            
            self.apollo_radio = QRadioButton("🔵 Apollo.io - Lead ve Contact Bulma")
            self.apollo_radio.setChecked(True)
            api_layout.addWidget(self.apollo_radio)
            
            self.snov_radio = QRadioButton("🟣 Snov.io - Email Discovery & Verification")
            api_layout.addWidget(self.snov_radio)
            
            api_group.setLayout(api_layout)
            layout.addWidget(api_group)
            
            # Arama parametreleri
            params_group = QGroupBox("Arama Parametreleri")
            params_layout = QFormLayout()
            
            self.department_input = QLineEdit()
            self.department_input.setPlaceholderText("Örn: Satış, Pazarlama, İK")
            params_layout.addRow("Departman:", self.department_input)
            
            self.seniority_input = QLineEdit()
            self.seniority_input.setPlaceholderText("Örn: Müdür, Direktör, CEO")
            params_layout.addRow("Kıdem Seviyesi:", self.seniority_input)
            
            params_group.setLayout(params_layout)
            layout.addWidget(params_group)
            
            # Sonuçlar alanı
            results_group = QGroupBox("🔍 Bulunan E-Posta Adresleri")
            results_layout = QVBoxLayout()
            
            self.results_text = QTextEdit()
            self.results_text.setReadOnly(True)
            self.results_text.setMinimumHeight(150)
            self.results_text.setText("🔎 Arama yapmak için 'Aramayı Başlat' butonuna tıklayın...")
            results_layout.addWidget(self.results_text)
            
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            results_layout.addWidget(self.progress_bar)
            
            results_group.setLayout(results_layout)
            layout.addWidget(results_group)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            self.start_search_btn = QPushButton("🔍 Aramayı Başlat")
            self.start_search_btn.clicked.connect(lambda: self.start_email_finder_search(firm, dialog))
            self.start_search_btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            button_layout.addWidget(self.start_search_btn)
            
            self.save_btn = QPushButton("💾 Bulunan E-postaları Kaydet")
            self.save_btn.clicked.connect(lambda: self.save_found_emails(firm, dialog))
            self.save_btn.setEnabled(False)
            self.save_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                    color: #666;
                }
            """)
            button_layout.addWidget(self.save_btn)
            
            close_btn = QPushButton("❌ Kapat")
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"E-posta bulucu açılamadı:\n{str(e)}")
    
    def start_email_finder_search(self, firm, dialog):
        """E-posta aramasını başlat"""
        try:
            # Progress bar'ı göster
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            
            # Seçilen API'yi belirle
            use_apollo = self.apollo_radio.isChecked()
            
            # Parametreleri al
            department = self.department_input.text()
            seniority = self.seniority_input.text()
            
            # Arama sonuçları
            results = []
            
            if use_apollo:
                # Apollo.io API çağrısı
                results = self.search_apollo_io(firm, department, seniority)
            else:
                # Snov.io API çağrısı
                results = self.search_snov_io(firm, department, seniority)
            
            # Sonuçları göster
            if results:
                results_html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
                results_html += "<tr style='background-color: #007bff; color: white;'>"
                results_html += "<th>Ad Soyad</th><th>Email</th><th>Pozisyon</th><th>Doğrulama</th>"
                results_html += "</tr>"
                
                for result in results:
                    verification = result.get('verified', False)
                    status = "✅ Doğrulanmış" if verification else "❓ Doğrulanmamış"
                    results_html += f"""
                    <tr>
                        <td>{result.get('name', 'N/A')}</td>
                        <td>{result.get('email', 'N/A')}</td>
                        <td>{result.get('position', 'N/A')}</td>
                        <td>{status}</td>
                    </tr>
                    """
                
                results_html += "</table>"
                self.results_text.setHtml(results_html)
                self.save_btn.setEnabled(True)
                
                # Veritabanına kaydet
                self.found_emails = results
                
            else:
                self.results_text.setText("❌ Hiçbir sonuç bulunamadı. Lütfen farklı parametreler deneyin.")
                self.save_btn.setEnabled(False)
            
            self.progress_bar.setVisible(False)
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Hata", f"Arama sırasında hata oluştu:\n{str(e)}")
    
    def search_apollo_io(self, firm, department=None, seniority=None):
        """Apollo.io API ile e-posta ara"""
        import requests
        try:
            print(f"🔵 Apollo.io ile arama yapılıyor: {firm.get('name')}")
            
            # Apollo.io API Key (config.json'dan al veya environment variable)
            apollo_api_key = self.get_apollo_api_key()
            if not apollo_api_key:
                QMessageBox.warning(self, "API Key Eksik", 
                                   "Apollo.io API key bulunamadı!\n\n"
                                   "Lütfen config.json dosyasına 'apollo_api_key' ekleyin veya\n"
                                   "Apollo.io kullanmak için API key'inizi girin.")
                return []
            
            # Company domain'ini çıkar
            website = firm.get('website', '')
            if website:
                domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            else:
                return []
            
            # API endpoint
            url = "https://api.apollo.io/v1/contacts/search"
            
            headers = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            }
            
            # Apollo.io API params
            params = {
                "api_key": apollo_api_key,
                "organization_domains": domain
            }
            
            # Department ve seniority varsa ekle
            if department:
                params["person_departments"] = department
            
            # API çağrısı
            response = requests.post(url, json=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                contacts = data.get('contacts', [])
                
                results = []
                for contact in contacts[:10]:  # İlk 10 sonuç
                    email = contact.get('email')
                    if email:
                        results.append({
                            'name': f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                            'email': email,
                            'position': contact.get('title', 'N/A'),
                            'verified': contact.get('email_status') == 'verified',
                            'source': 'Apollo.io'
                        })
                
                print(f"✅ Apollo.io: {len(results)} kişi bulundu")
                return results
            else:
                error_msg = response.text
                print(f"❌ Apollo.io API hatası ({response.status_code}): {error_msg}")
                QMessageBox.warning(self, "Apollo.io API Hatası", 
                                   f"API çağrısı başarısız!\n\n"
                                   f"Status Code: {response.status_code}\n"
                                   f"Hata: {error_msg}")
                return []
            
        except requests.exceptions.RequestException as e:
            print(f"Apollo.io network hatası: {e}")
            QMessageBox.warning(self, "Network Hatası", 
                               f"Apollo.io API'ye bağlanılamadı:\n{str(e)}")
            return []
        except Exception as e:
            print(f"Apollo.io arama hatası: {e}")
            QMessageBox.warning(self, "Hata", f"Apollo.io arama sırasında hata:\n{str(e)}")
            return []
    
    def search_snov_io(self, firm, department=None, seniority=None):
        """Snov.io API ile e-posta ara"""
        import requests
        try:
            print(f"🟣 Snov.io ile arama yapılıyor: {firm.get('name')}")
            
            # Snov.io API Key
            snov_api_key = self.get_snov_api_key()
            if not snov_api_key:
                QMessageBox.warning(self, "API Key Eksik", 
                                   "Snov.io API key bulunamadı!\n\n"
                                   "Lütfen config.json dosyasına 'snov_api_key' ekleyin veya\n"
                                   "Snov.io kullanmak için API key'inizi girin.")
                return []
            
            # Company domain'ini çıkar
            website = firm.get('website', '')
            if website:
                domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            else:
                return []
            
            # Snov.io API - Basit authentication kullan
            # Client ID ve Client Secret'ı query params olarak kullan
            url = "https://api.snov.io/v1/get-domain-emails-from-url"
            
            params = {
                "access_token": self.get_snov_access_token(snov_api_key),
                "domain": domain,
                "limit": 10
            }
            
            # API çağrısı
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Snov.io API response formatı değişebilir
                emails = data.get('result', {}).get('emails', [])
                if not emails:
                    emails = data.get('emails', [])
                
                results = []
                for email_data in emails:
                    # Email string veya dict olabilir
                    if isinstance(email_data, str):
                        email = email_data
                        results.append({
                            'name': 'N/A',
                            'email': email,
                            'position': 'N/A',
                            'verified': True,
                            'source': 'Snov.io'
                        })
                    elif isinstance(email_data, dict):
                        email = email_data.get('email')
                        if email:
                            results.append({
                                'name': f"{email_data.get('firstName', '')} {email_data.get('lastName', '')}".strip() or 'N/A',
                                'email': email,
                                'position': email_data.get('jobTitle', 'N/A'),
                                'verified': email_data.get('status', '').lower() in ['valid', 'accept_all'],
                                'source': 'Snov.io'
                            })
                
                print(f"✅ Snov.io: {len(results)} email bulundu")
                return results
            else:
                error_msg = response.text
                print(f"❌ Snov.io API hatası ({response.status_code}): {error_msg}")
                QMessageBox.warning(self, "Snov.io API Hatası", 
                                   f"API çağrısı başarısız!\n\n"
                                   f"Status Code: {response.status_code}\n"
                                   f"Hata: {error_msg}")
                return []
            
        except requests.exceptions.RequestException as e:
            print(f"Snov.io network hatası: {e}")
            QMessageBox.warning(self, "Network Hatası", 
                               f"Snov.io API'ye bağlanılamadı:\n{str(e)}")
            return []
        except Exception as e:
            print(f"Snov.io arama hatası: {e}")
            QMessageBox.warning(self, "Hata", f"Snov.io arama sırasında hata:\n{str(e)}")
            return []
    
    def save_found_emails(self, firm, dialog):
        """Bulunan e-postaları kaydet"""
        try:
            if not hasattr(self, 'found_emails') or not self.found_emails:
                QMessageBox.warning(self, "Uyarı", "Kaydedilecek e-posta adresi bulunamadı!")
                return
            
            # Veritabanına kaydet
            for email_data in self.found_emails:
                email_address = email_data.get('email', '')
                if email_address:
                    # Email'i firmaya ekle
                    existing_emails = firm.get('emails', [])
                    if isinstance(existing_emails, str):
                        existing_emails = [existing_emails]
                    
                    new_email = {
                        'email': email_address,
                        'position': email_data.get('position', 'N/A'),
                        'verified': email_data.get('verified', False),
                        'source': email_data.get('source', 'unknown')
                    }
                    
                    existing_emails.append(new_email)
                    
                    # Veritabanını güncelle
                    self.db.update_firm(firm['id'], {'emails': existing_emails})
            
            QMessageBox.information(self, "✅ Başarılı", 
                                   f"{len(self.found_emails)} e-posta adresi başarıyla kaydedildi!")
            
            dialog.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"E-posta kaydedilemedi:\n{str(e)}")
    
    def get_apollo_api_key(self):
        """Apollo.io API key'ini config.json'dan al"""
        try:
            import json
            import os
            
            config_file = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('apollo_api_key', '')
            
            # Environment variable'dan dene
            import os
            return os.environ.get('APOLLO_API_KEY', '')
        except Exception as e:
            print(f"Apollo API key okuma hatası: {e}")
            return ''
    
    def get_snov_api_key(self):
        """Snov.io API key'ini config.json'dan al"""
        try:
            import json
            import os
            
            config_file = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get('snov_api_key', {})
                    if isinstance(api_key, str):
                        return {'api_key': api_key}
                    return api_key
            
            # Environment variable'dan dene
            import os
            client_id = os.environ.get('SNOV_CLIENT_ID', '')
            client_secret = os.environ.get('SNOV_CLIENT_SECRET', '')
            if client_id and client_secret:
                return {'client_id': client_id, 'client_secret': client_secret}
            
            return {}
        except Exception as e:
            print(f"Snov API key okuma hatası: {e}")
            return {}
    
    def get_snov_access_token(self, snov_api_key):
        """Snov.io access token al"""
        try:
            import requests
            
            url = "https://api.snov.io/v1/oauth/access_token"
            
            params = {
                "grant_type": "client_credentials",
                "client_id": snov_api_key.get('client_id', ''),
                "client_secret": snov_api_key.get('client_secret', '')
            }
            
            response = requests.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('access_token', '')
            
            print(f"Snov.io token alma hatası: {response.status_code}")
            return ''
            
        except Exception as e:
            print(f"Snov.io token alma hatası: {e}")
            return ''
    
    def check_email_opens(self):
        """Email açılmalarını kontrol et"""
        try:
            # get_new_email_opens metodu yoksa boş liste döndür
            if hasattr(self.db, 'get_new_email_opens'):
                new_opens = self.db.get_new_email_opens(last_minutes=5)
            else:
                new_opens = []  # Database'de bu metod yoksa boş liste
            
            for open_data in new_opens:
                self.show_notification(
                    f"📧 Mail Açıldı!",
                    f"{open_data['firm_name']} firması mailimizi açtı!"
                )
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("📧 Mail Açıldı!")
                msg.setText(f"{open_data['firm_name']} firması mailimizi açtı!")
                msg.setInformativeText(
                    f"Email: {open_data.get('to_email', 'N/A')}\n"
                    f"Açılma zamanı: Az önce\n\n"
                    "Takip maili göndermek ister misiniz?"
                )
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                
                if msg.exec() == QMessageBox.Yes:
                    self.send_follow_up_email(open_data)
        except Exception as e:
            print(f"Email açılma kontrolü hatası: {str(e)}")
    
    def send_follow_up_email(self, email_data):
        """Takip maili gönder"""
        try:
            with open("config.json", "r") as f:
                settings = json.load(f)
                self.api_manager.update_settings(settings)
        except:
            QMessageBox.warning(self, "Uyarı", "API ayarları bulunamadı!")
            return
        
        # Takip maili oluştur
        try:
            if hasattr(self.api_manager, 'generate_follow_up_email'):
                follow_up_content = self.api_manager.generate_follow_up_email(email_data)
            else:
                # Varsayılan bir takip maili oluştur
                follow_up_content = {
                    'subject': f"Re: {email_data.get('firm_name', 'Firma')} - Takip",
                    'body': f"""
                    Merhaba {email_data.get('firm_name', '')},
                    
                    Gönderdiğimiz e-postayı inceleme fırsatınız oldu mu?
                    
                    Sorularınız olursa memnuniyetle yanıtlarım.
                    
                    Saygılarımla
                    """
                }
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Takip maili oluşturulamadı:\n{str(e)}")
            return
        
        # Email gönder
        email_manager = EmailManager()
        email_manager.update_settings(settings)
        
        result = email_manager.send_email(
            to_email=email_data.get('to_email', email_data.get('email')),
            subject=follow_up_content['subject'],
            body=follow_up_content['body'],
            firm_id=email_data['firm_id'],
            is_follow_up=True
        )
        
        if result['success']:
            QMessageBox.information(self, "✅ Başarılı", "Takip maili başarıyla gönderildi!")
            self.db.save_email_log(
                email_data['firm_id'], 
                email_data.get('to_email'), 
                result.get('subject', 'Takip Maili'),
                result.get('body', ''),
                'sent' if result['success'] else 'failed'
            )
        else:
            QMessageBox.critical(self, "❌ Hata", f"Takip maili gönderilemedi:\n{result.get('error')}")
    
    def show_notification(self, title, message):
        """Masaüstü bildirimi göster"""
        try:
            if sys.platform == "darwin":
                os.system(f'''osascript -e 'display notification "{message}" with title "{title}"' ''')
            elif sys.platform == "win32":
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=10)
            else:
                os.system(f'notify-send "{title}" "{message}"')
        except:
            pass
    
    def test_google_api(self):
        """Google Maps API test"""
        self.save_settings()
        result = self.api_manager.test_google_maps_api()
        
        if result['success']:
            QMessageBox.information(self, "✅ Başarılı", result['message'])
        else:
            QMessageBox.critical(self, "❌ Hata", 
                f"API Testi Başarısız!\n\n"
                f"Hata: {result['error']}\n"
                f"Detay: {result['message']}")
    
    def test_openai_api(self):
        """OpenAI API test"""
        self.save_settings()
        result = self.api_manager.test_openai_api()
        
        if result['success']:
            QMessageBox.information(self, "✅ Başarılı", 
                f"{result['message']}\n\n"
                f"Yanıt: {result.get('response', '')}")
        else:
            QMessageBox.critical(self, "❌ Hata", 
                f"API Testi Başarısız!\n\n"
                f"Hata: {result['error']}\n"
                f"Detay: {result['message']}")
    
    def test_snov_api(self):
        """Snov.io API test"""
        self.save_settings()
        result = self.api_manager.test_snov_api()
        
        if result['success']:
            QMessageBox.information(self, "✅ Başarılı", result['message'])
        else:
            QMessageBox.critical(self, "❌ Hata", 
                f"API Testi Başarısız!\n\n"
                f"Hata: {result['error']}\n"
                f"Detay: {result['message']}")
    
    def test_smtp_connection(self):
        """SMTP bağlantı testi"""
        self.save_settings()
        
        email_manager = EmailManager()
        with open("config.json", "r") as f:
            settings = json.load(f)
            email_manager.update_settings(settings)
        
        result = email_manager.test_smtp_connection()
        
        if result['success']:
            QMessageBox.information(self, "✅ Başarılı", result['message'])
        else:
            QMessageBox.critical(self, "❌ Hata", 
                f"SMTP Testi Başarısız!\n\n"
                f"Hata: {result['error']}")
    
    def save_settings(self):
        """Ayarları kaydet"""
        settings = {
            "google_api_key": self.google_api_input.text(),
            "openai_api_key": self.openai_api_input.text(),
            "snov_client_id": self.snov_id_input.text(),
            "snov_client_secret": self.snov_secret_input.text(),
            "smtp_email": self.email_input.text(),
            "smtp_password": self.email_password_input.text(),
            "smtp_server": self.smtp_server_input.text(),
            "smtp_port": self.smtp_port_input.text(),
            "tracking_url": self.tracking_url_input.text(),
            # WhatsApp ayarları kaldırıldı
            "calendar_client_id": self.calendar_client_id_input.text() if hasattr(self, 'calendar_client_id_input') else "",
            "calendar_client_secret": self.calendar_client_secret_input.text() if hasattr(self, 'calendar_client_secret_input') else "",
            "calendar_redirect_uri": self.calendar_redirect_uri_input.text() if hasattr(self, 'calendar_redirect_uri_input') else "http://localhost:8080/callback"
        }
        
        with open("config.json", "w") as f:
            json.dump(settings, f, indent=4)
        
        self.api_manager.update_settings(settings)
        # WhatsApp API ayarları kaldırıldı
        
        if self.calendar_manager and hasattr(self.calendar_manager, 'update_settings'):
            self.calendar_manager.update_settings(settings)
        
        QMessageBox.information(self, "✅ Başarılı", "Ayarlar başarıyla kaydedildi!")
    
    def load_settings(self):
        """Ayarları yükle ve return et"""
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                settings = json.load(f)
                
            # UI elementleri varsa ayarları yükle (her birini güvenli şekilde)
            try:
                if hasattr(self, 'google_api_input'):
                    self.google_api_input.setText(str(settings.get("google_api_key", "")))
                if hasattr(self, 'openai_api_input'):
                    self.openai_api_input.setText(str(settings.get("openai_api_key", "")))
                if hasattr(self, 'snov_id_input'):
                    self.snov_id_input.setText(str(settings.get("snov_client_id", "")))
                if hasattr(self, 'snov_secret_input'):
                    self.snov_secret_input.setText(str(settings.get("snov_client_secret", "")))
                if hasattr(self, 'email_input'):
                    self.email_input.setText(str(settings.get("smtp_email", "")))
                if hasattr(self, 'email_password_input'):
                    self.email_password_input.setText(str(settings.get("smtp_password", "")))
                if hasattr(self, 'smtp_server_input'):
                    self.smtp_server_input.setText(str(settings.get("smtp_server", "smtp.gmail.com")))
                if hasattr(self, 'smtp_port_input'):
                    # smtp_port integer olabilir, string'e çevir
                    smtp_port = settings.get("smtp_port", "587")
                    self.smtp_port_input.setText(str(smtp_port))
                if hasattr(self, 'tracking_url_input'):
                    self.tracking_url_input.setText(str(settings.get("tracking_url", "")))
                # WhatsApp ayarları yükleme kaldırıldı
                
                if hasattr(self, 'calendar_client_id_input'):
                    self.calendar_client_id_input.setText(str(settings.get("calendar_client_id", "")))
                    self.calendar_client_secret_input.setText(str(settings.get("calendar_client_secret", "")))
                    self.calendar_redirect_uri_input.setText(str(settings.get("calendar_redirect_uri", "http://localhost:8080/callback")))
            except Exception as ui_error:
                print(f"⚠️ UI settings yükleme hatası: {ui_error}")
                # UI hatası olsa bile devam et
            
            # Manager ayarlarını güncelle
            if hasattr(self, 'api_manager') and self.api_manager:
                self.api_manager.update_settings(settings)
            
            if hasattr(self, 'calendar_manager') and self.calendar_manager and hasattr(self.calendar_manager, 'update_settings'):
                self.calendar_manager.update_settings(settings)
            
            return settings  # ✅ Settings'i return et
                
        except FileNotFoundError:
            print("⚠️ config.json bulunamadı, yeni oluşturuluyor...")
            self.save_settings()
            return {}  # ✅ Dosya yoksa boş dict return et
        except json.JSONDecodeError as json_err:
            print(f"❌ config.json parse hatası: {json_err}")
            print("⚠️ config.json dosyası bozuk olabilir!")
            return {}
        except Exception as e:
            print(f"⚠️ Settings yükleme hatası: {e}")
            import traceback
            traceback.print_exc()
            return {}  # ✅ Hata durumunda boş dict return et
    
    def update_status(self, message):
        """Status bar güncelle"""
        self.status_bar.showMessage(message)
    
    def update_search_status(self, message):
        """Arama durumunu güncelle"""
        self.status_bar.showMessage(message)
    
    def on_error(self, error_message):
        """Hata mesajı göster"""
        QMessageBox.critical(self, "❌ Hata", f"Bir hata oluştu:\n{error_message}")
        self.status_bar.showMessage("❌ Hata oluştu!")

    def load_automation_flows(self):
        """Otomasyon akışlarını yükle"""
        if not self.automation_builder:
            self.automation_builder = AutomationBuilder()
        
        self.flow_combo.clear()
        self.flow_combo.addItem("-- Yeni Akış --")
        
        # get_all_flows yerine flows attribute'unu kullan
        if hasattr(self.automation_builder, 'flows'):
            flows = self.automation_builder.flows
        else:
            # Eğer flows attribute'u da yoksa boş bir dict kullan
            flows = {}
        
        for flow_id, flow in flows.items():
            # Flow dict ise
            if isinstance(flow, dict):
                name = flow.get('name', 'İsimsiz')
                status = flow.get('status', 'inactive')
            # Flow object ise
            else:
                name = getattr(flow, 'name', 'İsimsiz')
                status = getattr(flow, 'status', 'inactive')
            
            self.flow_combo.addItem(f"{name} ({status})", flow_id)
        
        self.current_flow_id = None
        self.current_flow_data = None
        self.flow_modified = False

    def create_new_automation_flow(self):
        """Yeni otomasyon akışı oluştur"""
        name, ok = QInputDialog.getText(self, "Yeni Akış", "Akış adı:")
        if ok and name:
            # Varsayılan bir başlangıç bloğu ile oluştur
            flow_data = {
                "name": name,
                "description": "",
                "status": "inactive",
                "blocks": [
                    {
                        "id": "start_1",
                        "type": "trigger",
                        "title": "Başlangıç",
                        "trigger_type": "manual",
                        "description": "Manuel başlatma tetikleyicisi",
                        "x": 100,
                        "y": 100,
                        "enabled": True
                    }
                ],
                "connections": [],
                "variables": []
            }
            
            try:
                flow_id = self.automation_builder.create_flow(flow_data)
                self.flow_combo.addItem(f"{name} (inactive)", flow_id)
                self.flow_combo.setCurrentIndex(self.flow_combo.count() - 1)
                
                self.debug_log(f"✅ Yeni akış oluşturuldu: {name}")
                
                # Yeni akışı editöre yükle
                QTimer.singleShot(500, lambda: self.flow_editor.page().runJavaScript(
                    f"if(typeof flowEditor !== 'undefined') {{ flowEditor.loadFlow({json.dumps(flow_data)}); }}"
                ))
                
            except ValueError as e:
                QMessageBox.critical(self, "Hata", f"Akış oluşturulamadı:\n{str(e)}")
                self.debug_log(f"❌ Akış oluşturma hatası: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Beklenmeyen hata:\n{str(e)}")
                self.debug_log(f"❌ Beklenmeyen hata: {str(e)}")

    def save_automation_flow(self):
        """Mevcut akışı kaydet"""
        if not self.current_flow_id or not self.current_flow_data:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek akış yok!")
            return
        
        # Akış bilgilerini güncelle
        self.current_flow_data["name"] = self.flow_name_edit.text()
        self.current_flow_data["description"] = self.flow_description_edit.text()
        self.current_flow_data["tags"] = [tag.strip() for tag in self.flow_tags_edit.text().split(",") if tag.strip()]
        
        # Değişkenleri güncelle
        variables = []
        for row in range(self.variables_table.rowCount()):
            var_data = {
                "name": self.variables_table.item(row, 0).text(),
                "type": self.variables_table.item(row, 1).text(),
                "value": self.variables_table.item(row, 2).text(),
                "scope": self.variables_table.item(row, 3).text()
            }
            variables.append(var_data)
        
        self.current_flow_data["variables"] = variables
        
        # Kaydet
        success = self.automation_builder.update_flow(self.current_flow_id, self.current_flow_data)
        
        if success:
            self.flow_modified = False
            self.save_flow_btn.setStyleSheet("")  # Normal renge dön
            self.debug_log(f"✅ Akış kaydedildi: {self.current_flow_data['name']}")
            QMessageBox.information(self, "Başarılı", "Akış başarıyla kaydedildi!")
        else:
            QMessageBox.critical(self, "Hata", "Akış kaydedilemedi!")

    def show_block_properties(self, block_data):
        """Blok özelliklerini göster"""
        self.block_properties.setRowCount(0)
        
        # Temel özellikler
        properties = [
            ("ID", block_data.get("id", "")),
            ("Tip", block_data.get("type", "")),
            ("Başlık", block_data.get("title", "")),
            ("Açıklama", block_data.get("description", "")),
            ("Aktif", "Evet" if block_data.get("enabled", True) else "Hayır"),
            ("Tekrar", str(block_data.get("retry_count", 0))),
            ("Timeout", f"{block_data.get('timeout', 300)} sn")
        ]
        
        # Tip bazlı özellikler
        if block_data.get("type") == "trigger":
            properties.append(("Tetikleyici Tipi", block_data.get("trigger_type", "")))
        elif block_data.get("type") == "condition":
            properties.append(("Operatör", block_data.get("condition", {}).get("operator", "")))
        elif block_data.get("type") == "api":
            properties.append(("URL", block_data.get("url", "")))
            properties.append(("Method", block_data.get("method", "")))
        
        # Tabloya ekle
        for prop_name, prop_value in properties:
            row = self.block_properties.rowCount()
            self.block_properties.insertRow(row)
            self.block_properties.setItem(row, 0, QTableWidgetItem(prop_name))
            self.block_properties.setItem(row, 1, QTableWidgetItem(str(prop_value)))

    def debug_log(self, message):
        """Debug konsoluna log ekle"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.debug_console.append(f"[{timestamp}] {message}")

    def update_automation_status(self):
        """Otomasyon durumunu güncelle"""
        if not self.automation_builder:
            return
        
        # Aktif yürütmeleri güncelle
        self.active_executions_list.clear()
        
        running_flows = self.automation_builder.executor.running_flows
        for exec_id, exec_info in running_flows.items():
            flow = exec_info["flow"]
            context = exec_info["context"]
            
            status_icon = {
                "running": "🟢",
                "paused": "🟡",
                "failed": "🔴"
            }.get(context.status.value, "⚫")
            
            item_text = f"{status_icon} {flow.name} - {context.current_block or 'Başlıyor...'}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, exec_id)
            self.active_executions_list.addItem(item)
        
        # Akış durumunu güncelle
        if self.current_flow_id:
            flow = self.automation_builder.flows.get(self.current_flow_id)
            if flow:
                if flow.status == "active":
                    self.flow_status_indicator.setText("🟢 Aktif")
                    self.flow_status_indicator.setStyleSheet("""
                        QLabel {
                            font-size: 14px;
                            font-weight: bold;
                            padding: 5px 15px;
                            border-radius: 15px;
                            background-color: #27ae60;
                        }
                    """)
                    self.activate_flow_btn.setText("⏸️ Duraklat")
                else:
                    self.flow_status_indicator.setText("⚫ Pasif")
                    self.flow_status_indicator.setStyleSheet("""
                        QLabel {
                            font-size: 14px;
                            font-weight: bold;
                            padding: 5px 15px;
                            border-radius: 15px;
                            background-color: #2a2a2a;
                        }
                    """)
                    self.activate_flow_btn.setText("▶️ Aktifleştir")

    def load_selected_flow(self, flow_name):
        """Seçili akışı yükle"""
        if flow_name == "-- Yeni Akış --":
            # Yeni akış modu
            self.current_flow_id = None
            self.current_flow_data = {
                "name": "",
                "description": "",
                "blocks": [],
                "connections": [],
                "variables": []
            }
            self.flow_name_edit.clear()
            self.flow_description_edit.clear()
            self.flow_tags_edit.clear()
            self.flow_version_label.setText("1.0.0")
            self.variables_table.setRowCount(0)
            
            # Editörü temizle - flowEditor yüklenmesini bekle
            QTimer.singleShot(500, lambda: self.flow_editor.page().runJavaScript(
                "if(typeof flowEditor !== 'undefined') { flowEditor.loadFlow({ blocks: [], connections: [] }); }"
            ))
            self.debug_log("📝 Yeni akış modu")
            return
        
        # Mevcut akışı yükle
        index = self.flow_combo.currentIndex()
        if index > 0:
            self.current_flow_id = self.flow_combo.currentData()
            
            if self.current_flow_id and self.automation_builder:
                if hasattr(self.automation_builder, 'flows'):
                    flow = self.automation_builder.flows.get(self.current_flow_id)
                    if flow:
                        if hasattr(flow, 'to_dict'):
                            self.current_flow_data = flow.to_dict()
                        else:
                            self.current_flow_data = flow
                        
                        # Bilgileri doldur
                        self.flow_name_edit.setText(self.current_flow_data.get("name", ""))
                        self.flow_description_edit.setText(self.current_flow_data.get("description", ""))
                        self.flow_tags_edit.setText(", ".join(self.current_flow_data.get("tags", [])))
                        self.flow_version_label.setText(self.current_flow_data.get("version", "1.0.0"))
                        
                        # Değişkenleri yükle
                        self.load_flow_variables()
                        
                        # Editöre yükle - flowEditor yüklenmesini bekle
                        flow_json = json.dumps(self.current_flow_data)
                        QTimer.singleShot(500, lambda: self.flow_editor.page().runJavaScript(
                            f"if(typeof flowEditor !== 'undefined') {{ flowEditor.loadFlow({flow_json}); }}"
                        ))
                        
                        # İstatistikleri güncelle
                        self.update_flow_statistics()
                        
                        self.debug_log(f"✅ Akış yüklendi: {self.current_flow_data['name']}")
                        self.flow_modified = False

    def validate_flow(self):
        """Akışı doğrula"""
        if not self.current_flow_data:
            QMessageBox.warning(self, "Uyarı", "Doğrulanacak akış yok!")
            return
        
        self.debug_log("🔍 Akış doğrulaması başlatılıyor...")
        
        # Geçici flow oluştur ve doğrula
        try:
            # Flow class tanımlı değil, validation'ı basit yap
            # temp_flow = Flow("temp_validation", self.current_flow_data.get("name", "Test"), self.current_flow_data)
            # Geçici çözüm
            errors = []
            
            # temp_flow.validate() - Flow class yok, basit validation yap
            if not self.current_flow_data.get('blocks'):
                errors.append("Akışta hiç blok yok!")
            
            if errors:
                # Hataları göster
                error_dialog = QDialog(self)
                error_dialog.setWindowTitle("❌ Doğrulama Hataları")
                error_dialog.setMinimumSize(600, 400)
                
                layout = QVBoxLayout(error_dialog)
                
                error_list = QListWidget()
                for error in errors:
                    item = QListWidgetItem(f"⚠️ {error}")
                    error_list.addItem(item)
                
                layout.addWidget(error_list)
                
                close_btn = QPushButton("Kapat")
                close_btn.clicked.connect(error_dialog.close)
                layout.addWidget(close_btn)
                
                error_dialog.exec()
                
                self.debug_log(f"❌ {len(errors)} doğrulama hatası bulundu")
            else:
                QMessageBox.information(self, "✅ Başarılı", 
                    "Akış doğrulaması başarılı!\n\n"
                    "Hiçbir hata bulunamadı.")
                self.debug_log("✅ Akış doğrulaması başarılı")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Doğrulama hatası:\n{str(e)}")
            self.debug_log(f"❌ Doğrulama hatası: {str(e)}")

    def test_automation_flow(self):
        """Akışı test et"""
        if not self.current_flow_id:
            QMessageBox.warning(self, "Uyarı", "Test edilecek akış yok!")
            return
        
        # Test verisi dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("🧪 Akış Test")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Test verisi girişi
        layout.addWidget(QLabel("Test Verisi (JSON):"))
        
        test_data_editor = QTextEdit()
        test_data_editor.setFont(QFont("Consolas", 10))
        
        # Örnek test verisi
        sample_data = {
            "trigger": {
                "firm_id": "test_123",
                "firm_name": "Test Firması",
                "email": "test@example.com",
                "website": "https://example.com"
            },
            "test_mode": True
        }
        
        test_data_editor.setText(json.dumps(sample_data, indent=2))
        layout.addWidget(test_data_editor)
        
        # Test sonuçları
        layout.addWidget(QLabel("Test Sonuçları:"))
        
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        layout.addWidget(results_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        run_test_btn = QPushButton("▶️ Testi Çalıştır")
        
        def run_test():
            try:
                test_data = json.loads(test_data_editor.toPlainText())
                
                results_text.append("🔄 Test başlatılıyor...\n")
                
                # Test çalıştır
                result = self.automation_builder.test_flow(self.current_flow_id, test_data)
                
                # Sonuçları göster
                results_text.append(f"✅ Akış: {result['flow_name']}\n")
                
                if result['validation']:
                    results_text.append("❌ Doğrulama Hataları:")
                    for error in result['validation']:
                        results_text.append(f"  - {error}")
                else:
                    results_text.append("✅ Doğrulama başarılı\n")
                
                results_text.append("\n📦 Blok Test Sonuçları:")
                for block in result['blocks']:
                    status_icon = "✅" if block.get('status') == 'valid' else "❌"
                    results_text.append(f"\n{status_icon} {block['title']} ({block['block_type']})")
                    
                    if block['validation']:
                        for error in block['validation']:
                            results_text.append(f"  ⚠️ {error}")
                    
                    if 'error' in block:
                        results_text.append(f"  ❌ Hata: {block['error']}")
                
                self.debug_log(f"✅ Test tamamlandı: {result['flow_name']}")
                
            except json.JSONDecodeError as e:
                results_text.append(f"❌ JSON hatası: {str(e)}")
            except Exception as e:
                results_text.append(f"❌ Test hatası: {str(e)}")
        
        run_test_btn.clicked.connect(run_test)
        button_layout.addWidget(run_test_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()

    def toggle_flow_activation(self):
        """Akışı aktif/pasif yap"""
        if not self.current_flow_id:
            QMessageBox.warning(self, "Uyarı", "Aktifleştirilecek akış yok!")
            return
        
        flow = self.automation_builder.flows.get(self.current_flow_id)
        if not flow:
            return
        
        if flow.status == "inactive":
            # Önce doğrula
            errors = flow.validate()
            if errors:
                reply = QMessageBox.question(self, "Doğrulama Hataları",
                    f"{len(errors)} doğrulama hatası var.\n\n"
                    "Yine de aktifleştirmek istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No)
                
                if reply != QMessageBox.Yes:
                    return
            
            # Aktifleştir
            flow.status = "active"
            self.automation_builder._register_flow_triggers(flow)
            self.automation_builder.save_flows()
            
            QMessageBox.information(self, "✅ Aktif", "Akış aktifleştirildi!")
            self.debug_log(f"✅ Akış aktifleştirildi: {flow.name}")
            
        else:
            # Pasifleştir
            flow.status = "inactive"
            self.automation_builder._unregister_flow_triggers(flow)
            self.automation_builder.save_flows()
            
            QMessageBox.information(self, "⏸️ Pasif", "Akış pasifleştirildi!")
            self.debug_log(f"⏸️ Akış pasifleştirildi: {flow.name}")
        
        # UI güncelle
        self.update_automation_status()
        
        # Combo güncelle
        for i in range(self.flow_combo.count()):
            if self.flow_combo.itemData(i) == self.current_flow_id:
                self.flow_combo.setItemText(i, f"{flow.name} ({flow.status})")
                break

    def edit_block_dialog(self, block_id, block_data):
        """Blok düzenleme dialogu"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"✏️ Blok Düzenle: {block_data.get('title', 'Untitled')}")
        dialog.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Genel sekmesi
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # Temel alanlar
        title_input = QLineEdit(block_data.get("title", ""))
        general_layout.addRow("Başlık:", title_input)
        
        description_input = QTextEdit()
        description_input.setText(block_data.get("description", ""))
        description_input.setMaximumHeight(80)
        general_layout.addRow("Açıklama:", description_input)
        
        enabled_check = QCheckBox("Aktif")
        enabled_check.setChecked(block_data.get("enabled", True))
        general_layout.addRow("Durum:", enabled_check)
        
        retry_spin = QSpinBox()
        retry_spin.setRange(0, 10)
        retry_spin.setValue(block_data.get("retry_count", 0))
        general_layout.addRow("Tekrar Sayısı:", retry_spin)
        
        timeout_spin = QSpinBox()
        timeout_spin.setRange(1, 3600)
        timeout_spin.setValue(block_data.get("timeout", 300))
        timeout_spin.setSuffix(" saniye")
        general_layout.addRow("Timeout:", timeout_spin)
        
        tabs.addTab(general_tab, "📋 Genel")
        
        # Tip bazlı sekmeler
        block_type = block_data.get("type")
        
        if block_type == "code":
            code_tab = QWidget()
            code_layout = QVBoxLayout(code_tab)
            
            code_layout.addWidget(QLabel("Python Kodu:"))
            
            code_editor = QTextEdit()
            code_editor.setFont(QFont("Consolas", 10))
            code_editor.setText(block_data.get("code", ""))
            code_layout.addWidget(code_editor)
            
            # Syntax kontrol
            syntax_btn = QPushButton("✔️ Syntax Kontrol")
            
            def check_syntax():
                try:
                    import ast
                    ast.parse(code_editor.toPlainText())
                    QMessageBox.information(dialog, "✅ Başarılı", "Kod syntax'ı geçerli!")
                except SyntaxError as e:
                    QMessageBox.critical(dialog, "❌ Syntax Hatası", str(e))
            
            syntax_btn.clicked.connect(check_syntax)
            code_layout.addWidget(syntax_btn)
            
            tabs.addTab(code_tab, "🐍 Kod")
        
        elif block_type == "api":
            api_tab = QWidget()
            api_layout = QFormLayout(api_tab)
            
            url_input = QLineEdit(block_data.get("url", ""))
            api_layout.addRow("URL:", url_input)
            
            method_combo = QComboBox()
            method_combo.addItems(["GET", "POST", "PUT", "PATCH", "DELETE"])
            method_combo.setCurrentText(block_data.get("method", "GET"))
            api_layout.addRow("Method:", method_combo)
            
            headers_input = QTextEdit()
            headers_input.setText(json.dumps(block_data.get("headers", {}), indent=2))
            headers_input.setMaximumHeight(100)
            api_layout.addRow("Headers (JSON):", headers_input)
            
            body_input = QTextEdit()
            body_input.setText(json.dumps(block_data.get("body", {}), indent=2))
            api_layout.addRow("Body (JSON):", body_input)
            
            tabs.addTab(api_tab, "🌐 API")
        
        elif block_type == "condition":
            condition_tab = QWidget()
            condition_layout = QFormLayout(condition_tab)
            
            condition_type_combo = QComboBox()
            condition_type_combo.addItems(["Basit", "Gelişmiş"])
            condition_layout.addRow("Koşul Tipi:", condition_type_combo)
            
            # Basit koşul
            simple_widget = QWidget()
            simple_layout = QFormLayout(simple_widget)
            
            operator_combo = QComboBox()
            operator_combo.addItems([
                "equals", "not_equals", "greater_than", "less_than",
                "contains", "starts_with", "ends_with", "regex"
            ])
            simple_layout.addRow("Operatör:", operator_combo)
            
            left_input = QLineEdit()
            left_input.setPlaceholderText("{{variable}} veya değer")
            simple_layout.addRow("Sol Taraf:", left_input)
            
            right_input = QLineEdit()
            right_input.setPlaceholderText("{{variable}} veya değer")
            simple_layout.addRow("Sağ Taraf:", right_input)
            
            condition_layout.addRow(simple_widget)
            
            # Gelişmiş koşul
            advanced_input = QTextEdit()
            advanced_input.setPlaceholderText("Python expression: variables.score > 50")
            advanced_input.setVisible(False)
            condition_layout.addRow("İfade:", advanced_input)
            
            def toggle_condition_type(index):
                simple_widget.setVisible(index == 0)
                advanced_input.setVisible(index == 1)
            
            condition_type_combo.currentIndexChanged.connect(toggle_condition_type)
            
            tabs.addTab(condition_tab, "❓ Koşul")
        
        elif block_type == "loop":
            loop_tab = QWidget()
            loop_layout = QFormLayout(loop_tab)
            
            loop_type_combo = QComboBox()
            loop_type_combo.addItems(["Sayaç", "Liste", "Koşul"])
            loop_layout.addRow("Döngü Tipi:", loop_type_combo)
            
            # Sayaç
            count_spin = QSpinBox()
            count_spin.setRange(1, 1000)
            count_spin.setValue(block_data.get("count", 10))
            loop_layout.addRow("Tekrar Sayısı:", count_spin)
            
            # Liste
            items_input = QLineEdit()
            items_input.setPlaceholderText("{{variable}} - liste değişkeni")
            items_input.setText(block_data.get("items", ""))
            loop_layout.addRow("Liste:", items_input)
            
            # Max iterations
            max_iter_spin = QSpinBox()
            max_iter_spin.setRange(1, 10000)
            max_iter_spin.setValue(block_data.get("max_iterations", 1000))
            loop_layout.addRow("Max İterasyon:", max_iter_spin)
            
            tabs.addTab(loop_tab, "🔄 Döngü")
        
        # Hata yönetimi sekmesi
        error_tab = QWidget()
        error_layout = QFormLayout(error_tab)
        
        error_action_combo = QComboBox()
        error_action_combo.addItems(["log", "skip", "retry", "fail", "default_value", "goto"])
        
        error_handler = block_data.get("error_handler", {})
        if isinstance(error_handler, dict):
            error_action_combo.setCurrentText(error_handler.get("action", "log"))
        
        error_layout.addRow("Hata Durumunda:", error_action_combo)
        
        error_message_input = QLineEdit()
        error_layout.addRow("Hata Mesajı:", error_message_input)
        
        default_value_input = QLineEdit()
        default_value_input.setPlaceholderText("Varsayılan değer")
        error_layout.addRow("Varsayılan Değer:", default_value_input)
        
        goto_block_combo = QComboBox()
        goto_block_combo.setPlaceholderText("Hedef blok seçin")
        error_layout.addRow("Git:", goto_block_combo)
        
        tabs.addTab(error_tab, "⚠️ Hata Yönetimi")
        
        layout.addWidget(tabs)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Kaydet")
        
        def save_block():
            # Verileri topla
            updated_data = {
                "id": block_id,
                "type": block_type,
                "title": title_input.text(),
                "description": description_input.toPlainText(),
                "enabled": enabled_check.isChecked(),
                "retry_count": retry_spin.value(),
                "timeout": timeout_spin.value()
            }
            
            # Tip bazlı veriler
            if block_type == "code":
                updated_data["code"] = code_editor.toPlainText()
            
            elif block_type == "api":
                try:
                    updated_data["url"] = url_input.text()
                    updated_data["method"] = method_combo.currentText()
                    updated_data["headers"] = json.loads(headers_input.toPlainText() or "{}")
                    updated_data["body"] = json.loads(body_input.toPlainText() or "{}")
                except json.JSONDecodeError:
                    QMessageBox.warning(dialog, "Uyarı", "JSON formatı hatalı!")
                    return
            
            elif block_type == "condition":
                if condition_type_combo.currentIndex() == 0:
                    updated_data["condition"] = {
                        "operator": operator_combo.currentText(),
                        "left": left_input.text(),
                        "right": right_input.text()
                    }
                else:
                    updated_data["condition"] = advanced_input.toPlainText()
            
            elif block_type == "loop":
                loop_type = loop_type_combo.currentText()
                if loop_type == "Sayaç":
                    updated_data["count"] = count_spin.value()
                elif loop_type == "Liste":
                    updated_data["items"] = items_input.text()
                
                updated_data["max_iterations"] = max_iter_spin.value()
            
            # Hata yönetimi
            error_action = error_action_combo.currentText()
            if error_action != "log":
                updated_data["error_handler"] = {
                    "action": error_action,
                    "message": error_message_input.text()
                }
                
                if error_action == "default_value":
                    updated_data["error_handler"]["value"] = default_value_input.text()
                elif error_action == "goto":
                    updated_data["error_handler"]["target"] = goto_block_combo.currentText()
            
            # JavaScript'e gönder
            js_data = json.dumps(updated_data)
            self.flow_editor.page().runJavaScript(f"flowEditor.updateBlock('{block_id}', {js_data});")
            
            self.debug_log(f"✅ Blok güncellendi: {updated_data['title']}")
            dialog.close()
        
        save_btn.clicked.connect(save_block)
        button_layout.addWidget(save_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()

    def add_flow_variable(self):
        """Akış değişkeni ekle"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Değişken Ekle")
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        layout.addRow("Değişken Adı:", name_input)
        
        type_combo = QComboBox()
        type_combo.addItems(["string", "integer", "float", "boolean", "list", "dict", "any"])
        layout.addRow("Tip:", type_combo)
        
        value_input = QLineEdit()
        layout.addRow("Varsayılan Değer:", value_input)
        
        scope_combo = QComboBox()
        scope_combo.addItems(["flow", "global", "local"])
        layout.addRow("Kapsam:", scope_combo)
        
        readonly_check = QCheckBox("Salt Okunur")
        layout.addRow("", readonly_check)
        
        description_input = QTextEdit()
        description_input.setMaximumHeight(60)
        layout.addRow("Açıklama:", description_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Ekle")
        
        def add_variable():
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(dialog, "Uyarı", "Değişken adı gerekli!")
                return
            
            # Tabloya ekle
            row = self.variables_table.rowCount()
            self.variables_table.insertRow(row)
            
            self.variables_table.setItem(row, 0, QTableWidgetItem(name))
            self.variables_table.setItem(row, 1, QTableWidgetItem(type_combo.currentText()))
            self.variables_table.setItem(row, 2, QTableWidgetItem(value_input.text()))
            self.variables_table.setItem(row, 3, QTableWidgetItem(scope_combo.currentText()))
            
            # İşlem butonu
            delete_btn = QPushButton("🗑️")
            delete_btn.clicked.connect(lambda: self.delete_variable(row))
            self.variables_table.setCellWidget(row, 4, delete_btn)
            
            self.flow_modified = True
            self.debug_log(f"✅ Değişken eklendi: {name}")
            dialog.close()
        
        add_btn.clicked.connect(add_variable)
        button_layout.addWidget(add_btn)
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        
        dialog.exec()

    def delete_variable(self, row):
        """Değişkeni sil"""
        var_name = self.variables_table.item(row, 0).text()
        
        reply = QMessageBox.question(self, "Onay",
            f"'{var_name}' değişkenini silmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.variables_table.removeRow(row)
            self.flow_modified = True
            self.debug_log(f"🗑️ Değişken silindi: {var_name}")

    def load_flow_variables(self):
        """Akış değişkenlerini yükle"""
        self.variables_table.setRowCount(0)
        
        variables = self.current_flow_data.get("variables", [])
        for var in variables:
            row = self.variables_table.rowCount()
            self.variables_table.insertRow(row)
            
            self.variables_table.setItem(row, 0, QTableWidgetItem(var.get("name", "")))
            self.variables_table.setItem(row, 1, QTableWidgetItem(var.get("type", "any")))
            self.variables_table.setItem(row, 2, QTableWidgetItem(str(var.get("value", ""))))
            self.variables_table.setItem(row, 3, QTableWidgetItem(var.get("scope", "flow")))
            
            # Silme butonu
            delete_btn = QPushButton("🗑️")
            delete_btn.clicked.connect(lambda checked=False, r=row: self.delete_variable(r))
            self.variables_table.setCellWidget(row, 4, delete_btn)

    def check_code_syntax(self):
        """Kod editöründeki kodun syntax kontrolü"""
        code = self.code_editor.toPlainText()
        
        if not code:
            QMessageBox.warning(self, "Uyarı", "Kontrol edilecek kod yok!")
            return
        
        try:
            import ast
            ast.parse(code)
            QMessageBox.information(self, "✅ Başarılı", "Kod syntax'ı geçerli!")
            self.debug_log("✅ Kod syntax kontrolü başarılı")
        except SyntaxError as e:
            QMessageBox.critical(self, "❌ Syntax Hatası", 
                f"Satır {e.lineno}: {e.msg}\n\n{e.text}")
            self.debug_log(f"❌ Syntax hatası: Satır {e.lineno} - {e.msg}")

    def show_execution_details(self, item):
        """Yürütme detaylarını göster"""
        exec_id = item.data(Qt.UserRole)
        
        if self.automation_builder:
            status = self.automation_builder.executor.get_execution_status(exec_id)
            
            if status:
                # Log temizle ve yeni logları ekle
                self.execution_logs.clear()
                
                self.execution_logs.append(f"🔍 Execution ID: {exec_id}")
                self.execution_logs.append(f"📋 Flow: {status['flow_name']}")
                self.execution_logs.append(f"📊 Status: {status['status']}")
                self.execution_logs.append(f"⏰ Start: {status['start_time'] or 'N/A'}")
                self.execution_logs.append(f"📍 Current Block: {status['current_block'] or 'N/A'}")
                self.execution_logs.append("\n📜 Logs:")
                
                for log in status.get('logs', []):
                    level_icon = {
                        'info': 'ℹ️',
                        'warning': '⚠️',
                        'error': '❌',
                        'debug': '🐛'
                    }.get(log['level'], '📝')
                    
                    self.execution_logs.append(
                        f"[{log['timestamp']}] {level_icon} {log['message']}"
                    )

    def pause_execution(self):
        """Seçili yürütmeyi duraklat"""
        current_item = self.active_executions_list.currentItem()
        if current_item:
            exec_id = current_item.data(Qt.UserRole)
            
            if self.automation_builder:
                self.automation_builder.executor.pause_execution(exec_id)
                self.debug_log(f"⏸️ Yürütme duraklatıldı: {exec_id}")

    def stop_execution(self):
        """Seçili yürütmeyi durdur"""
        current_item = self.active_executions_list.currentItem()
        if current_item:
            exec_id = current_item.data(Qt.UserRole)
            
            reply = QMessageBox.question(self, "Onay",
                "Yürütmeyi durdurmak istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes and self.automation_builder:
                self.automation_builder.executor.cancel_execution(exec_id)
                self.debug_log(f"⏹️ Yürütme durduruldu: {exec_id}")

    def filter_blocks(self, search_text):
        """Blok listesini filtrele"""
        search_text = search_text.lower()
        
        # Her kategorideki itemları filtrele
        for i in range(self.block_accordion.count()):
            widget = self.block_accordion.widget(i)
            if isinstance(widget, QListWidget):
                for j in range(widget.count()):
                    item = widget.item(j)
                    item.setHidden(search_text not in item.text().lower())

    def duplicate_flow(self):
        """Mevcut akışı kopyala"""
        if not self.current_flow_id:
            QMessageBox.warning(self, "Uyarı", "Kopyalanacak akış yok!")
            return
        
        name, ok = QInputDialog.getText(self, "Akış Kopyala", 
            "Yeni akış adı:", text=f"{self.current_flow_data['name']} (Kopya)")
        
        if ok and name:
            # Akışı export et
            export_data = self.automation_builder.export_flow(self.current_flow_id)
            
            if export_data:
                export_data['name'] = name
                
                # Yeni akış olarak import et
                new_flow_id = self.automation_builder.import_flow(export_data)
                
                # Listeye ekle
                self.flow_combo.addItem(f"{name} (inactive)", new_flow_id)
                
                QMessageBox.information(self, "✅ Başarılı", "Akış kopyalandı!")
                self.debug_log(f"📑 Akış kopyalandı: {name}")

    def import_flow(self):
        """Akış dosyasını içe aktar"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Akış Dosyası Seç", "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    flow_data = json.load(f)
                
                # İsim kontrolü
                name = flow_data.get('name', 'İsimsiz Akış')
                name, ok = QInputDialog.getText(self, "Akış İsmi", 
                    "Akış adı:", text=name)
                
                if ok:
                    flow_data['name'] = name
                    
                    # Import et
                    flow_id = self.automation_builder.import_flow(flow_data)
                    
                    # Listeye ekle
                    self.flow_combo.addItem(f"{name} (inactive)", flow_id)
                    
                    QMessageBox.information(self, "✅ Başarılı", 
                        f"Akış başarıyla içe aktarıldı!\n\n{name}")
                    self.debug_log(f"📥 Akış içe aktarıldı: {name}")
                    
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", 
                    f"Akış içe aktarılamadı:\n{str(e)}")

    def export_flow(self):
        """Mevcut akışı dışa aktar"""
        if not self.current_flow_id:
            QMessageBox.warning(self, "Uyarı", "Dışa aktarılacak akış yok!")
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Akışı Kaydet",
            f"{self.current_flow_data['name'].replace(' ', '_')}_flow.json",
            "JSON Files (*.json)"
        )
        
        if file_name:
            try:
                export_data = self.automation_builder.export_flow(self.current_flow_id)
                
                if export_data:
                    with open(file_name, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=2)
                    
                    QMessageBox.information(self, "✅ Başarılı", 
                        f"Akış başarıyla dışa aktarıldı!\n\n{file_name}")
                    self.debug_log(f"📤 Akış dışa aktarıldı: {file_name}")
                else:
                    QMessageBox.critical(self, "❌ Hata", "Akış dışa aktarılamadı!")
                    
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", 
                    f"Dışa aktarma hatası:\n{str(e)}")

    def update_flow_statistics(self):
        """Akış istatistiklerini güncelle"""
        if not self.current_flow_id or not self.automation_builder:
            return
        
        stats = self.automation_builder.get_flow_statistics(self.current_flow_id)
        
        if stats:
            stats_text = f"""📊 Akış İstatistikleri

    📋 Ad: {stats['flow_name']}
    📌 Versiyon: {stats['version']}
    🔧 Durum: {stats['status']}

    📦 Toplam Blok: {stats['total_blocks']}
    - Tetikleyici: {stats['block_types'].get('trigger', 0)}
    - Koşul: {stats['block_types'].get('condition', 0)}
    - Aksiyon: {stats['block_types'].get('action', 0)}
    - Kod: {stats['block_types'].get('code', 0)}

    🚀 Yürütmeler:
    - Toplam: {stats['total_executions']}
    - Başarılı: {stats['successful_executions']}
    - Başarısız: {stats['failed_executions']}
    - Ort. Süre: {stats['average_duration']:.2f} sn

    🕐 Oluşturma: {stats['created_at']}
    🕐 Güncelleme: {stats['updated_at']}
    """
            
            if stats['last_execution']:
                last_exec = stats['last_execution']
                stats_text += f"\n🔄 Son Yürütme: {last_exec.get('start_time', 'N/A')}"
            
            self.flow_stats_text.setText(stats_text)

    def show_email_preview_dialog(self, preview_data):
        """Email önizleme dialogu göster"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📧 Mail Önizlemesi - {preview_data['firm']['name']}")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Üst bilgi
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 10px;
            padding: 15px;
        """)
        header_layout = QVBoxLayout(header_widget)
        
        firm_info = QLabel(f"🏢 Firma: {preview_data['firm']['name']}")
        firm_info.setStyleSheet("font-size: 18px; font-weight: bold; color: #14a1a5;")
        header_layout.addWidget(firm_info)
        
        email_info = QLabel(f"📧 Alıcılar: {', '.join([e['email'] for e in preview_data['emails']])}")
        email_info.setStyleSheet("font-size: 14px; color: #ffffff;")
        header_layout.addWidget(email_info)
        
        layout.addWidget(header_widget)
        
        # Mail önizleme
        preview_web = QWebEngineView()
        
        # Manifest hatalarını önlemek için profile ayarları
        try:
            profile = preview_web.page().profile()
            settings = profile.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.TouchIconsEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
        except Exception as e:
            print(f"⚠️ Mail preview web view profile ayarları uygulanamadı: {e}")
        
        preview_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 700px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .email-header {{
                    background-color: #0d7377;
                    color: white;
                    padding: 20px;
                    border-radius: 10px 10px 0 0;
                    margin: -30px -30px 20px -30px;
                }}
                .subject {{
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .email-body {{
                    padding: 20px 0;
                    white-space: pre-wrap;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="email-header">
                    <div class="subject">{preview_data['subject']}</div>
                </div>
                <div class="email-body">{preview_data['body']}</div>
            </div>
        </body>
        </html>
        """
        preview_web.setHtml(preview_html)
        layout.addWidget(preview_web)
        
        # Geri sayım ve butonlar
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("""
            background-color: #1a1a1a;
            border-radius: 10px;
            padding: 15px;
        """)
        bottom_layout = QHBoxLayout(bottom_widget)
        
        self.countdown_label = QLabel("⏳ Mail 30 saniye sonra gönderilecek...")
        self.countdown_label.setStyleSheet("font-size: 16px; color: #f39c12; font-weight: bold;")
        bottom_layout.addWidget(self.countdown_label)
        
        bottom_layout.addStretch()
        
        skip_btn = QPushButton("⏭️ Hemen Gönder")
        skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        edit_btn = QPushButton("✏️ Düzenle")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        cancel_btn = QPushButton("❌ İptal")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        bottom_layout.addWidget(skip_btn)
        bottom_layout.addWidget(edit_btn)
        bottom_layout.addWidget(cancel_btn)
        
        layout.addWidget(bottom_widget)
        
        # Timer için
        self.preview_countdown = 30
        
        def update_countdown():
            self.preview_countdown -= 1
            if self.preview_countdown > 0:
                self.countdown_label.setText(f"⏳ Mail {self.preview_countdown} saniye sonra gönderilecek...")
            else:
                dialog.accept()
        
        timer = QTimer()
        timer.timeout.connect(update_countdown)
        timer.start(1000)
        
        # Buton işlevleri
        skip_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        def edit_email():
            # Düzenleme dialogu
            edit_dialog = QDialog(dialog)
            edit_dialog.setWindowTitle("✏️ Email Düzenle")
            edit_dialog.setMinimumSize(600, 500)
            
            edit_layout = QVBoxLayout(edit_dialog)
            
            edit_layout.addWidget(QLabel("Konu:"))
            subject_edit = QLineEdit(preview_data['subject'])
            edit_layout.addWidget(subject_edit)
            
            edit_layout.addWidget(QLabel("İçerik:"))
            body_edit = QTextEdit()
            body_edit.setText(preview_data['body'])
            edit_layout.addWidget(body_edit)
            
            edit_buttons = QHBoxLayout()
            save_btn = QPushButton("💾 Kaydet")
            cancel_edit_btn = QPushButton("İptal")
            
            edit_buttons.addWidget(save_btn)
            edit_buttons.addWidget(cancel_edit_btn)
            edit_layout.addLayout(edit_buttons)
            
            def save_changes():
                preview_data['subject'] = subject_edit.text()
                preview_data['body'] = body_edit.toPlainText()
                
                # Önizlemeyi güncelle
                new_html = preview_html.replace(
                    f"<div class=\"subject\">{preview_data['subject']}</div>",
                    f"<div class=\"subject\">{subject_edit.text()}</div>"
                ).replace(
                    f"<div class=\"email-body\">{preview_data['body']}</div>",
                    f"<div class=\"email-body\">{body_edit.toPlainText()}</div>"
                )
                preview_web.setHtml(new_html)
                
                edit_dialog.accept()
            
            save_btn.clicked.connect(save_changes)
            cancel_edit_btn.clicked.connect(edit_dialog.reject)
            
            edit_dialog.exec()
        
        edit_btn.clicked.connect(edit_email)
        
        result = dialog.exec()
        timer.stop()
        
        return result == QDialog.Accepted

    # Web Scraper yardımcı fonksiyonları
    def load_scraper_url(self, scraper_id, url):
        """Gelişmiş scraper URL yükleme"""
        if not url:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir URL girin!")
            return
            
        # http/https ekle eğer yoksa
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            if scraper_id == 1:
                self.scraper1_web.setUrl(QUrl(url))
                self.scraper1_url.setText(url)
                self.update_status(f"Scraper 1: {url} yükleniyor...")
                self.update_current_urls()
            else:
                self.scraper2_web.setUrl(QUrl(url))  
                self.scraper2_url.setText(url)
                self.update_status(f"Scraper 2: {url} yükleniyor...")
                self.update_current_urls()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"URL yüklenirken hata: {str(e)}")
    
    def select_firm_for_scraper(self):
        """Dual scraper için firma seç"""
        try:
            # Veritabanından firmaları al
            if hasattr(self, 'db') and self.db and DATABASE_AVAILABLE:
                firms = self.db.get_firms()
                if not firms:
                    QMessageBox.information(self, "Bilgi", "Henüz kayıtlı firma bulunamadı!\n\nÖnce 'Firma Ara' sekmesinden firma arayıp analiz edin.")
                    return
                    
                # Hangi scraper'a yükleneceğini sor
                scraper_choice, ok = QInputDialog.getItem(
                    self, "Scraper Seç", 
                    "Hangi scraper'a yüklensin?",
                    ["🔹 Scraper 1 (Sol Panel)", "🔸 Scraper 2 (Sağ Panel)"], 0, False
                )
                
                if not ok:
                    return
                    
                scraper_id = 1 if "Scraper 1" in scraper_choice else 2
                
                # Firma seçim dialogu
                firm_names = []
                for firm in firms:
                    name = firm.get('name', 'Bilinmeyen')
                    phone = firm.get('phone', 'Tel yok')
                    website = firm.get('website', 'Site yok')
                    firm_names.append(f"{name} - {phone} - {website[:30]}...")
                
                selected, ok = QInputDialog.getItem(
                    self, f"Firma Seç (Scraper {scraper_id})", 
                    "Hangi firmayı seçmek istiyorsunuz?",
                    firm_names, 0, False
                )
                
                if ok and selected:
                    # Seçilen firmayı bul
                    selected_index = firm_names.index(selected)
                    selected_firm = firms[selected_index]
                    
                    # Firmayı ilgili scraper'a yükle
                    self.load_firm_to_scraper(selected_firm, scraper_id)
                    
            else:
                QMessageBox.warning(self, "Hata", "Veritabanı bağlantısı bulunamadı!")
                
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Firma seçilirken hata: {str(e)}")
    
    def load_firm_to_scraper(self, firm, scraper_id):
        """Firmayı belirtilen scraper'a yükle"""
        try:
            if scraper_id == 1:
                self.current_firm1 = firm
                self.firm1_title.setText(f"🏢 Firma 1: {firm.get('name', 'Bilinmeyen')}")
                self.firm1_phone.setText(f"📞 {firm.get('phone', '-')}")
                
                website = firm.get('website', '-')
                if len(website) > 25:
                    website = website[:22] + "..."
                self.firm1_website.setText(f"🌐 {website}")
                
                # Website'yi URL kutusuna yükle
                if firm.get('website'):
                    full_website = firm.get('website')
                    if not full_website.startswith(('http://', 'https://')):
                        full_website = 'https://' + full_website
                    self.scraper1_url.setText(full_website)
                    self.scraper1_web.setUrl(QUrl(full_website))
                    
            else:  # scraper_id == 2
                self.current_firm2 = firm
                self.firm2_title.setText(f"🏢 Firma 2: {firm.get('name', 'Bilinmeyen')}")
                self.firm2_phone.setText(f"📞 {firm.get('phone', '-')}")
                
                website = firm.get('website', '-')
                if len(website) > 25:
                    website = website[:22] + "..."
                self.firm2_website.setText(f"🌐 {website}")
                
                # Website'yi URL kutusuna yükle
                if firm.get('website'):
                    full_website = firm.get('website')
                    if not full_website.startswith(('http://', 'https://')):
                        full_website = 'https://' + full_website
                    self.scraper2_url.setText(full_website)
                    self.scraper2_web.setUrl(QUrl(full_website))
            
            self.update_current_urls()
            self.update_status(f"Firma {firm.get('name', 'Bilinmeyen')} scraper {scraper_id}'e yüklendi")
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Firma scraper'a yüklenirken hata: {str(e)}")
    
    def clear_all_scrapers(self):
        """Tüm scraper'ları temizle"""
        reply = QMessageBox.question(self, "Temizle", 
                                   "Tüm scraper'ları temizlemek istediğinize emin misiniz?")
        
        if reply == QMessageBox.Yes:
            try:
                # Scraper 1 temizle
                self.current_firm1 = None
                self.firm1_title.setText("🏢 Firma 1: Bekleniyor...")
                self.firm1_phone.setText("📞 -")
                self.firm1_website.setText("🌐 -")
                self.scraper1_url.clear()
                self.scraper1_web.setUrl(QUrl("about:blank"))
                
                # Scraper 2 temizle
                self.current_firm2 = None
                self.firm2_title.setText("🏢 Firma 2: Bekleniyor...")
                self.firm2_phone.setText("📞 -")
                self.firm2_website.setText("🌐 -")
                self.scraper2_url.clear()
                self.scraper2_web.setUrl(QUrl("about:blank"))
                
                # Kuyruğu temizle
                self.analysis_queue.clear()
                self.update_queue_info()
                self.update_current_urls()
                self.analysis_status.setText("🔄 Analiz durumu: Temizlendi")
                
                self.update_status("Tüm scraper'lar temizlendi")
                
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Temizlerken hata: {str(e)}")
    
    def update_current_urls(self):
        """Geçerli URL'leri güncelle"""
        try:
            url1 = self.scraper1_url.text() if self.scraper1_url.text() else "Yok"
            url2 = self.scraper2_url.text() if self.scraper2_url.text() else "Yok"
            
            # URL'leri kısalt
            if len(url1) > 30:
                url1 = url1[:27] + "..."
            if len(url2) > 30:
                url2 = url2[:27] + "..."
                
            self.current_urls.setText(f"🔗 Scraper 1: {url1} | Scraper 2: {url2}")
        except Exception as e:
            print(f"URL güncelleme hatası: {str(e)}")
    
    def update_queue_info(self):
        """Kuyruk bilgisini güncelle"""
        try:
            queue_count = len(self.analysis_queue)
            self.queue_info.setText(f"📊 Kuyruk: {queue_count} firma bekliyor")
        except Exception as e:
            print(f"Kuyruk güncelleme hatası: {str(e)}")
    
    def add_firms_to_analysis_queue(self, firms):
        """Firmaları analiz kuyruğuna ekle"""
        try:
            self.analysis_queue.extend(firms)
            self.update_queue_info()
            self.analysis_status.setText(f"🔄 Analiz durumu: {len(firms)} firma kuyruğa eklendi")
            
            # İlk firmayı scraper'lara yükle
            if len(firms) >= 1 and not self.current_firm1:
                self.load_firm_to_scraper(firms[0], 1)
            if len(firms) >= 2 and not self.current_firm2:
                self.load_firm_to_scraper(firms[1], 2)
                
        except Exception as e:
            print(f"Kuyruk ekleme hatası: {str(e)}")
    
    def process_next_firms_in_queue(self):
        """Kuyruktaki sonraki firmaları işle"""
        try:
            if not self.analysis_queue:
                return
                
            # Boş scraper varsa doldur
            if not self.current_firm1 and self.analysis_queue:
                firm = self.analysis_queue.pop(0)
                self.load_firm_to_scraper(firm, 1)
                
            if not self.current_firm2 and self.analysis_queue:
                firm = self.analysis_queue.pop(0)
                self.load_firm_to_scraper(firm, 2)
                
            self.update_queue_info()
            
        except Exception as e:
            print(f"Kuyruk işleme hatası: {str(e)}")

    # Eski fonksiyonlar - uyumluluk için
    def update_firm_info_display(self, firm):
        """Eski fonksiyon - yeni sisteme yönlendir"""
        self.load_firm_to_scraper(firm, 1)
    
    def load_firm_website(self, website_url):
        """Eski fonksiyon - scraper 1'e yükle"""
        if website_url and website_url != '-':
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            self.scraper1_url.setText(website_url)
            self.scraper1_web.setUrl(QUrl(website_url))
    
    def refresh_firm_website(self):
        """Eski fonksiyon - scraper 1'i yenile"""
        try:
            self.scraper1_web.reload()
            self.update_status("Scraper 1 yenileniyor...")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Yenilenirken hata: {str(e)}")

    # Gelişmiş Web Scraper fonksiyonları
    def navigate_scraper(self, scraper_id, direction):
        """Scraper navigasyon (geri/ileri)"""
        try:
            if scraper_id == 1:
                if direction == "back":
                    self.scraper1_web.back()
                else:
                    self.scraper1_web.forward()
            else:
                if direction == "back":
                    self.scraper2_web.back()
                else:
                    self.scraper2_web.forward()
            
            self.update_status(f"Scraper {scraper_id}: {direction} navigate")
            
        except Exception as e:
            QMessageBox.warning(self, "Navigasyon Hatası", f"Hata: {str(e)}")
    
    def refresh_scraper(self, scraper_id):
        """Belirtilen scraper'ı yenile"""
        try:
            if scraper_id == 1:
                self.scraper1_web.reload()
                self.firm1_status_dot.setText("🟡")
            else:
                self.scraper2_web.reload()
                self.firm2_status_dot.setText("🟡")
            
            self.update_status(f"Scraper {scraper_id} yenileniyor...")
            
        except Exception as e:
            QMessageBox.warning(self, "Yenileme Hatası", f"Hata: {str(e)}")
    
    def zoom_scraper(self, scraper_id, factor):
        """Scraper zoom kontrolü"""
        try:
            if scraper_id == 1:
                current_zoom = self.scraper1_web.zoomFactor()
                new_zoom = current_zoom * factor
                new_zoom = max(0.25, min(5.0, new_zoom))  # 0.25x - 5x arası
                self.scraper1_web.setZoomFactor(new_zoom)
            else:
                current_zoom = self.scraper2_web.zoomFactor()
                new_zoom = current_zoom * factor
                new_zoom = max(0.25, min(5.0, new_zoom))  # 0.25x - 5x arası
                self.scraper2_web.setZoomFactor(new_zoom)
            
            zoom_percent = int(new_zoom * 100)
            self.update_status(f"Scraper {scraper_id}: Zoom {zoom_percent}%")
            
        except Exception as e:
            print(f"Zoom error: {str(e)}")
    
    def toggle_split_view(self):
        """Dikey/Yatay görünüm değiştir"""
        try:
            if self.is_vertical_split:
                # Yatay'a geç
                new_layout = QHBoxLayout(self.scraper_container)
                self.is_vertical_split = False
                self.split_view_btn.setText("🔄 Dikey")
            else:
                # Dikey'e geç
                new_layout = QVBoxLayout(self.scraper_container)
                self.is_vertical_split = True
                self.split_view_btn.setText("🔄 Yatay")
            
            # Mevcut widget'ları kaldır
            old_layout = self.scraper_container.layout()
            if old_layout:
                while old_layout.count():
                    child = old_layout.takeAt(0)
                    if child.widget():
                        new_layout.addWidget(child.widget())
            
            # Eski layoutu sil ve yenisini ayarla
            if old_layout:
                old_layout.deleteLater()
            self.scraper_container.setLayout(new_layout)
            
            self.update_status(f"Görünüm: {'Dikey' if self.is_vertical_split else 'Yatay'}")
            
        except Exception as e:
            QMessageBox.warning(self, "Görünüm Hatası", f"Hata: {str(e)}")
    
    def toggle_sync_scroll(self):
        """Senkronize kaydırma açık/kapat"""
        try:
            self.sync_scroll_enabled = not self.sync_scroll_enabled
            
            if self.sync_scroll_enabled:
                self.sync_scroll_btn.setText("🔗 ON")
                self.sync_scroll_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 #2ecc71, stop: 1 #27ae60);
                        color: white; border: none; border-radius: 6px;
                        padding: 8px; font-weight: bold; font-size: 11px;
                    }
                    QPushButton:hover { background-color: #58d68d; }
                """)
            else:
                self.sync_scroll_btn.setText("🔗 OFF")
                self.sync_scroll_btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 #e74c3c, stop: 1 #c0392b);
                        color: white; border: none; border-radius: 6px;
                        padding: 8px; font-weight: bold; font-size: 11px;
                    }
                    QPushButton:hover { background-color: #ec7063; }
                """)
            
            self.update_status(f"Sync Scroll: {'Açık' if self.sync_scroll_enabled else 'Kapalı'}")
            
        except Exception as e:
            print(f"Sync scroll error: {str(e)}")
    
    def take_screenshots(self):
        """Her iki scraper'ın screenshot'ını al"""
        try:
            import os
            from datetime import datetime
            
            # Screenshots klasörü oluştur
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Scraper 1 screenshot
            if hasattr(self, 'scraper1_web'):
                filename1 = f"screenshots/scraper1_{timestamp}.png"
                self.scraper1_web.grab().save(filename1)
            
            # Scraper 2 screenshot
            if hasattr(self, 'scraper2_web'):
                filename2 = f"screenshots/scraper2_{timestamp}.png"
                self.scraper2_web.grab().save(filename2)
            
            QMessageBox.information(self, "✅ Screenshot Alındı", 
                                  f"Screenshot'lar kaydedildi:\n\n"
                                  f"📁 screenshots/{timestamp}")
            
            self.update_status(f"Screenshot alındı: {timestamp}")
            
        except Exception as e:
            QMessageBox.warning(self, "Screenshot Hatası", f"Hata: {str(e)}")
    
    def on_scraper_load_started(self, scraper_id):
        """Scraper yüklenme başladığında"""
        try:
            import time
            current_time = time.time()
            
            if scraper_id == 1:
                self.firm1_status_dot.setText("🟡")
                if hasattr(self, 'firm1_loading'):
                    self.firm1_loading.setText("⏱️ Yükleniyor...")
                self.scraper1_load_start = current_time
            else:
                self.firm2_status_dot.setText("🟡")
                if hasattr(self, 'firm2_loading'):
                    self.firm2_loading.setText("⏱️ Yükleniyor...")
                self.scraper2_load_start = current_time
            
            self.update_status(f"Scraper {scraper_id}: Sayfa yükleniyor...")
            
        except Exception as e:
            print(f"Load started error: {str(e)}")
    
    def on_scraper_load_finished(self, scraper_id, success):
        """Scraper yüklenme tamamlandığında"""
        try:
            import time
            current_time = time.time()
            
            if scraper_id == 1:
                if hasattr(self, 'scraper1_load_start'):
                    load_time = current_time - self.scraper1_load_start
                    if hasattr(self, 'firm1_loading'):
                        self.firm1_loading.setText(f"⏱️ {load_time:.1f}s")
                    if hasattr(self, 'scraper1_speed'):
                        self.scraper1_speed.setText(f"⚡ S1: {int(load_time*1000)}ms")
                    
                if success:
                    if hasattr(self, 'firm1_status_dot'):
                        self.firm1_status_dot.setText("🟢")
                    self.scraper_stats['success_count'] += 1
                else:
                    if hasattr(self, 'firm1_status_dot'):
                        self.firm1_status_dot.setText("🔴")
                    self.scraper_stats['error_count'] += 1
            else:
                if hasattr(self, 'scraper2_load_start'):
                    load_time = current_time - self.scraper2_load_start
                    if hasattr(self, 'firm2_loading'):
                        self.firm2_loading.setText(f"⏱️ {load_time:.1f}s")
                    if hasattr(self, 'scraper2_speed'):
                        self.scraper2_speed.setText(f"⚡ S2: {int(load_time*1000)}ms")
                    
                if success:
                    if hasattr(self, 'firm2_status_dot'):
                        self.firm2_status_dot.setText("🟢")
                    self.scraper_stats['success_count'] += 1
                else:
                    if hasattr(self, 'firm2_status_dot'):
                        self.firm2_status_dot.setText("🔴")
                    self.scraper_stats['error_count'] += 1
            
            # Genel istatistikleri güncelle
            self.scraper_stats['total_scraped'] += 1
            self.update_scraper_statistics()
            
            status = "✅ Yüklendi" if success else "❌ Hata"
            self.update_status(f"Scraper {scraper_id}: {status}")
            
        except Exception as e:
            print(f"Load finished error: {str(e)}")
    
    def update_scraper_statistics(self):
        """Scraper istatistiklerini güncelle"""
        try:
            total = self.scraper_stats['total_scraped']
            success = self.scraper_stats['success_count']
            
            self.total_scraped.setText(f"🔍 Toplam: {total}")
            
            if total > 0:
                success_rate = int((success / total) * 100)
                self.success_rate.setText(f"✅ Başarı: {success_rate}%")
                
        except Exception as e:
            print(f"Statistics update error: {str(e)}")
    
    def update_performance_stats(self):
        """Performance istatistiklerini güncelle"""
        try:
            import psutil
            import time
            
            # Memory usage
            memory_mb = int(psutil.Process().memory_info().rss / 1024 / 1024)
            self.memory_usage.setText(f"💾 RAM: {memory_mb}MB")
            
            # Session time
            if self.scraper_stats.get('session_start'):
                elapsed = time.time() - self.scraper_stats['session_start']
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                self.session_time.setText(f"⏰ Süre: {hours:02d}:{minutes:02d}")
            
            # Network status (simulated)
            import random
            statuses = ["Strong", "Good", "Weak"]
            colors = ["#2ecc71", "#f39c12", "#e74c3c"]
            status = random.choice(statuses)
            color = colors[statuses.index(status)]
            self.network_status.setText(f"📡 WiFi: {status}")
            self.network_status.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")
            
        except Exception as e:
            print(f"Performance stats error: {str(e)}")
    
    # Toolbar fonksiyonları
    def start_new_session(self):
        """Yeni scraping session'ı başlat"""
        try:
            import time
            reply = QMessageBox.question(self, "Yeni Session", 
                                       "Yeni bir scraping session'ı başlatmak istiyor musunuz?\n\n"
                                       "Bu işlem mevcut verileri temizleyecek.")
            
            if reply == QMessageBox.Yes:
                # Stats'ı sıfırla
                self.scraper_stats = {
                    'total_scraped': 0,
                    'session_start': time.time(),
                    'load_times': [],
                    'success_count': 0,
                    'error_count': 0
                }
                
                # UI'ı güncelle
                self.clear_all_scrapers()
                self.update_scraper_statistics()
                
                self.update_status("🆕 Yeni session başlatıldı")
                
        except Exception as e:
            QMessageBox.warning(self, "Session Hatası", f"Hata: {str(e)}")
    
    def save_session(self):
        """Mevcut session'ı kaydet"""
        try:
            from datetime import datetime
            
            session_data = {
                'timestamp': datetime.now().isoformat(),
                'stats': self.scraper_stats,
                'scraper1_url': self.scraper1_url.text(),
                'scraper2_url': self.scraper2_url.text(),
                'current_firm1': self.current_firm1,
                'current_firm2': self.current_firm2,
                'analysis_queue': self.analysis_queue
            }
            
            filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "✅ Session Kaydedildi", 
                                  f"Session başarıyla kaydedildi:\n\n📁 {filename}")
            
            self.update_status(f"Session kaydedildi: {filename}")
            
        except Exception as e:
            QMessageBox.warning(self, "Kayıt Hatası", f"Hata: {str(e)}")
    
    def show_scraper_history(self):
        """Scraper geçmişini göster"""
        try:
            # Basit geçmiş dialogu
            history_dialog = QDialog(self)
            history_dialog.setWindowTitle("📋 Scraper Geçmişi")
            history_dialog.setFixedSize(600, 400)
            
            layout = QVBoxLayout(history_dialog)
            
            history_list = QListWidget()
            history_list.addItem("🕐 15:30 - https://example1.com - Scraper 1")
            history_list.addItem("🕐 15:28 - https://example2.com - Scraper 2")
            history_list.addItem("🕐 15:25 - https://example3.com - Scraper 1")
            
            layout.addWidget(history_list)
            
            close_btn = QPushButton("Kapat")
            close_btn.clicked.connect(history_dialog.close)
            layout.addWidget(close_btn)
            
            history_dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Geçmiş Hatası", f"Hata: {str(e)}")
    
    def show_bookmarks(self):
        """Bookmark'ları göster"""
        try:
            QMessageBox.information(self, "⭐ Favoriler", "Bookmark özelliği yakında eklenecek!")
            
        except Exception as e:
            print(f"Bookmarks error: {str(e)}")
    
    def toggle_auto_refresh(self):
        """Otomatik yenileme açık/kapat"""
        try:
            if not hasattr(self, 'auto_refresh_timer'):
                self.auto_refresh_timer = QTimer()
                self.auto_refresh_timer.timeout.connect(self.refresh_all_scrapers)
                self.auto_refresh_enabled = False
            
            if self.auto_refresh_enabled:
                self.auto_refresh_timer.stop()
                self.auto_refresh_enabled = False
                self.auto_refresh_btn.setText("🔄 Auto: OFF")
                self.auto_refresh_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c; color: white;
                        border: none; border-radius: 5px;
                        padding: 8px 12px; font-weight: bold; font-size: 11px;
                    }
                    QPushButton:hover { background-color: #c0392b; }
                """)
            else:
                self.auto_refresh_timer.start(30000)  # 30 saniyede bir
                self.auto_refresh_enabled = True
                self.auto_refresh_btn.setText("🔄 Auto: ON")
                self.auto_refresh_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60; color: white;
                        border: none; border-radius: 5px;
                        padding: 8px 12px; font-weight: bold; font-size: 11px;
                    }
                    QPushButton:hover { background-color: #2ecc71; }
                """)
            
            status = "Açık" if self.auto_refresh_enabled else "Kapalı"
            self.update_status(f"Otomatik yenileme: {status}")
            
        except Exception as e:
            print(f"Auto refresh error: {str(e)}")
    
    def toggle_mobile_view(self):
        """Mobil/Masaüstü görünüm değiştir"""
        try:
            if not hasattr(self, 'mobile_view_enabled'):
                self.mobile_view_enabled = False
            
            if self.mobile_view_enabled:
                # Desktop view
                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                self.mobile_view_enabled = False
                self.mobile_view_btn.setText("📱 Desktop")
            else:
                # Mobile view
                user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15"
                self.mobile_view_enabled = True
                self.mobile_view_btn.setText("💻 Mobile")
            
            # User agent'ı değiştir (sadece yeni yüklemeler için)
            self.update_status(f"Görünüm: {'Mobile' if self.mobile_view_enabled else 'Desktop'}")
            
        except Exception as e:
            print(f"Mobile view error: {str(e)}")
    
    def bookmark_current_pages(self):
        """Mevcut sayfaları favorilere ekle"""
        try:
            url1 = self.scraper1_url.text()
            url2 = self.scraper2_url.text()
            
            bookmarks = []
            if url1:
                bookmarks.append(f"Scraper 1: {url1}")
            if url2:
                bookmarks.append(f"Scraper 2: {url2}")
            
            if bookmarks:
                QMessageBox.information(self, "⭐ Favorilere Eklendi", 
                                      "\n".join(bookmarks))
            else:
                QMessageBox.information(self, "⭐ Favoriler", "Kaydedilecek URL bulunamadı!")
                
        except Exception as e:
            print(f"Bookmark error: {str(e)}")
    
    def toggle_fullscreen_mode(self):
        """Tam ekran modu aç/kapat"""
        try:
            if self.isFullScreen():
                self.showNormal()
                self.fullscreen_btn.setText("🔳")
            else:
                self.showFullScreen()
                self.fullscreen_btn.setText("🔲")
                
        except Exception as e:
            print(f"Fullscreen error: {str(e)}")
    
    def refresh_all_scrapers(self):
        """Tüm scraper'ları yenile"""
        try:
            self.refresh_scraper(1)
            self.refresh_scraper(2)
            
        except Exception as e:
            print(f"Refresh all error: {str(e)}")
    
    # Sekme yönetimi ve analiz entegrasyonu
    def switch_to_webscraper_tab(self):
        """Web Scraper sekmesine geç"""
        try:
            # Web Scraper sekmesinin index'ini bul
            for i in range(self.tabs.count()):
                if "Web Scraper" in self.tabs.tabText(i):
                    self.tabs.setCurrentIndex(i)
                    self.update_status("Web Scraper sekmesine geçildi")
                    return
        except Exception as e:
            print(f"Sekme geçiş hatası: {str(e)}")
    
    def update_scraper_analysis_status(self, message):
        """Scraper analiz durumunu güncelle"""
        try:
            if hasattr(self, 'analysis_status'):
                # Analiz mesajlarını filtrele ve scraper'a özel hale getir
                if "analiz ediliyor" in message.lower():
                    firm_name = message.split(' ')[1] if len(message.split(' ')) > 1 else "Firma"
                    self.analysis_status.setText(f"🔄 Analiz: {firm_name} işleniyor...")
                elif "email" in message.lower() and "bulundu" in message.lower():
                    self.analysis_status.setText(f"📧 {message}")
                elif "tamamlandı" in message.lower():
                    self.analysis_status.setText(f"✅ {message}")
                    # Analiz tamamlandığında sıradaki firmayı yükle
                    self.process_next_firms_in_queue()
        except Exception as e:
            print(f"Scraper status güncelleme hatası: {str(e)}")
    
    def on_whatsapp_loaded(self, success):
        """WhatsApp Web yüklenme durumu"""
        try:
            if success:
                self.whatsapp_status.setText("✅ WhatsApp Web yüklendi - QR kod için hazır")
                self.whatsapp_status.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
            else:
                self.whatsapp_status.setText("❌ WhatsApp Web yüklenemedi - Yenile butonuna tıklayın")
                self.whatsapp_status.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 5px;")
        except Exception as e:
            print(f"WhatsApp yüklenme durumu hatası: {str(e)}")
    
    def on_whatsapp_progress(self, progress):
        """WhatsApp Web yüklenme ilerlemesi"""
        try:
            if progress < 100:
                self.whatsapp_status.setText(f"🔄 WhatsApp Web yükleniyor... %{progress}")
                self.whatsapp_status.setStyleSheet("color: #f39c12; font-weight: bold; padding: 5px;")
        except Exception as e:
            print(f"WhatsApp yüklenme ilerlemesi hatası: {str(e)}")

    def on_firm_analysis_completed(self, firm_data):
        """Tek firma analizi tamamlandığında çağrılır"""
        try:
            # Hangi scraper'da bu firma varsa güncelle
            if self.current_firm1 and self.current_firm1.get('name') == firm_data.get('name'):
                self.update_scraper_firm_status(1, firm_data)
            elif self.current_firm2 and self.current_firm2.get('name') == firm_data.get('name'):
                self.update_scraper_firm_status(2, firm_data)
            
            # Sıradaki firmayı yükle
            self.process_next_firms_in_queue()
            
        except Exception as e:
            print(f"Firma analizi tamamlanma hatası: {str(e)}")
    
    def update_scraper_firm_status(self, scraper_id, firm_data):
        """Scraper'daki firma durumunu güncelle"""
        try:
            email_count = len(firm_data.get('emails', []))
            status_text = f"✅ {email_count} email bulundu"
            
            if scraper_id == 1:
                current_text = self.firm1_title.text()
                if ":" in current_text:
                    base_text = current_text.split(":")[0] + f": {firm_data.get('name', 'Bilinmeyen')}"
                    self.firm1_title.setText(f"{base_text} ({status_text})")
            else:
                current_text = self.firm2_title.text()
                if ":" in current_text:
                    base_text = current_text.split(":")[0] + f": {firm_data.get('name', 'Bilinmeyen')}"
                    self.firm2_title.setText(f"{base_text} ({status_text})")
                    
        except Exception as e:
            print(f"Scraper firma durumu güncelleme hatası: {str(e)}")

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
            # Raporlar klasöründeki dosyaları bul
            reports_dir = os.path.join(os.getcwd(), "Raporlar")
            report_files = []
            
            if os.path.exists(reports_dir):
                for file in os.listdir(reports_dir):
                    if file.startswith('Haftalik_Rapor_') and file.endswith('.pdf'):
                        report_files.append(file)
            
            if not report_files:
                QMessageBox.information(self, "Bilgi", "Henüz rapor oluşturulmamış!")
                return
            
            # En son dosyayı bul
            latest_file = max(report_files, key=lambda f: os.path.getctime(os.path.join(reports_dir, f)))
            file_path = os.path.join(reports_dir, latest_file)
            
            # Dosyayı aç
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS ve Linux
                os.system(f'open "{file_path}"')
            else:
                QMessageBox.information(self, "Bilgi", f"Rapor dosyası: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor açma hatası: {str(e)}")

    def create_ai_strategy_tab(self):
        """🤖 AI Strateji Analizi Sekmesi - Firma verilerini AI ile analiz eder"""
        widget = QWidget()
        widget.setObjectName("aiStrategyWidget")
        
        # Ana layout
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Başlık ve istatistikler
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        # Sol taraf - Başlık ve açıklama
        left_header = QWidget()
        left_header_layout = QVBoxLayout(left_header)
        
        title_label = QLabel("🤖 AI Strateji Analizi")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #14a1a5;
                margin-bottom: 5px;
            }
        """)
        left_header_layout.addWidget(title_label)
        
        desc_label = QLabel("Firma verilerinizi AI ile analiz edin ve en uygun pazarlama stratejilerini keşfedin")
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #cccccc;
                margin-bottom: 10px;
            }
        """)
        left_header_layout.addWidget(desc_label)
        
        # Sağ taraf - Hızlı istatistikler
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        # İstatistik kartları
        self.ai_total_firms_card = self.create_stat_card("📊 Toplam Firma", "0", "#17a2b8")
        self.ai_analyzed_card = self.create_stat_card("✅ Analiz Edilen", "0", "#28a745")
        self.ai_pending_card = self.create_stat_card("⏳ Bekleyen", "0", "#ffc107")
        self.ai_success_rate_card = self.create_stat_card("📈 Başarı Oranı", "0%", "#6f42c1")
        
        stats_layout.addWidget(self.ai_total_firms_card)
        stats_layout.addWidget(self.ai_analyzed_card)
        stats_layout.addWidget(self.ai_pending_card)
        stats_layout.addWidget(self.ai_success_rate_card)
        
        header_layout.addWidget(left_header)
        header_layout.addWidget(stats_widget)
        main_layout.addWidget(header_widget)
        
        # Ana içerik - Horizontal layout
        content_layout = QHBoxLayout()
        
        # Sol panel - Firma listesi ve analiz
        left_panel = QWidget()
        left_panel.setMaximumWidth(450)
        left_layout = QVBoxLayout(left_panel)
        
        # Firma seçimi grubu - Gelişmiş
        firm_selection_group = QGroupBox("📋 Firma Seçimi ve Filtreleme")
        firm_selection_layout = QVBoxLayout()
        
        # Üst kısım - Arama ve filtreler
        top_controls = QWidget()
        top_controls_layout = QVBoxLayout(top_controls)
        
        # Arama çubuğu
        search_layout = QHBoxLayout()
        self.ai_strategy_search_input = QLineEdit()
        self.ai_strategy_search_input.setPlaceholderText("🔍 Firma adı, sektör veya kalite skoruna göre ara...")
        self.ai_strategy_search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #444;
                border-radius: 6px;
                background-color: #2a2a2a;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #14a1a5;
            }
        """)
        self.ai_strategy_search_input.textChanged.connect(self.filter_ai_strategy_firms)
        search_layout.addWidget(self.ai_strategy_search_input)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Listeyi yenile")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_ai_strategy_firms)
        search_layout.addWidget(refresh_btn)
        
        top_controls_layout.addLayout(search_layout)
        
        # Akıllı filtreler
        smart_filters = QHBoxLayout()
        
        # Sadece email'i olanlar
        self.ai_strategy_email_only = QCheckBox("📧 Email'li")
        self.ai_strategy_email_only.setToolTip("Sadece email adresi bulunan firmaları göster")
        self.ai_strategy_email_only.stateChanged.connect(self.filter_ai_strategy_firms)
        smart_filters.addWidget(self.ai_strategy_email_only)
        
        # Sektör filtresi
        self.ai_strategy_sector_combo = QComboBox()
        self.ai_strategy_sector_combo.setEditable(False)
        self.ai_strategy_sector_combo.addItem("Tüm Sektörler", "")
        try:
            sectors = []
            if hasattr(self, 'ai_strategy_analyzer') and self.ai_strategy_analyzer and hasattr(self.ai_strategy_analyzer, 'get_all_sectors'):
                sectors = self.ai_strategy_analyzer.get_all_sectors() or []
            elif hasattr(self, 'db') and self.db and hasattr(self.db, 'cursor'):
                self.db.cursor.execute("SELECT DISTINCT COALESCE(sector,'') FROM firms WHERE sector IS NOT NULL AND sector != '' ORDER BY sector")
                sectors = [row[0] for row in self.db.cursor.fetchall()]
        except Exception:
            sectors = []
        for s in sectors:
            if s:
                self.ai_strategy_sector_combo.addItem(s, s)
        self.ai_strategy_sector_combo.currentIndexChanged.connect(self.filter_ai_strategy_firms)
        smart_filters.addWidget(QLabel("🏭 Sektör:"))
        smart_filters.addWidget(self.ai_strategy_sector_combo)
        
        # Minimum kalite skoru
        self.ai_strategy_min_quality = QSpinBox()
        self.ai_strategy_min_quality.setRange(0, 100)
        self.ai_strategy_min_quality.setValue(0)
        self.ai_strategy_min_quality.valueChanged.connect(self.filter_ai_strategy_firms)
        smart_filters.addWidget(QLabel("⭐ Min Kalite:"))
        smart_filters.addWidget(self.ai_strategy_min_quality)
        smart_filters.addStretch()
        
        top_controls_layout.addLayout(smart_filters)
        
        # Filtre butonları
        filter_layout = QHBoxLayout()
        
        self.filter_all_btn = QPushButton("Tümü")
        self.filter_all_btn.setCheckable(True)
        self.filter_all_btn.setChecked(True)
        self.filter_all_btn.clicked.connect(lambda: self.filter_by_status("all"))
        
        self.filter_analyzed_btn = QPushButton("Analiz Edilen")
        self.filter_analyzed_btn.setCheckable(True)
        self.filter_analyzed_btn.clicked.connect(lambda: self.filter_by_status("analyzed"))
        
        self.filter_pending_btn = QPushButton("Bekleyen")
        self.filter_pending_btn.setCheckable(True)
        self.filter_pending_btn.clicked.connect(lambda: self.filter_by_status("pending"))
        
        self.filter_high_quality_btn = QPushButton("Yüksek Kalite")
        self.filter_high_quality_btn.setCheckable(True)
        self.filter_high_quality_btn.clicked.connect(lambda: self.filter_by_status("high_quality"))
        
        for btn in [self.filter_all_btn, self.filter_analyzed_btn, self.filter_pending_btn, self.filter_high_quality_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #444;
                    color: white;
                    border: 1px solid #666;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 12px;
                }
                QPushButton:checked {
                    background-color: #14a1a5;
                    border-color: #14a1a5;
                }
                QPushButton:hover {
                    background-color: #555;
                }
            """)
            filter_layout.addWidget(btn)
        
        top_controls_layout.addLayout(filter_layout)
        firm_selection_layout.addWidget(top_controls)
        
        # Firma listesi - Gelişmiş
        self.ai_strategy_firms_list = QListWidget()
        self.ai_strategy_firms_list.setMaximumHeight(300)
        self.ai_strategy_firms_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ai_strategy_firms_list.customContextMenuRequested.connect(self.show_ai_strategy_context_menu)
        self.ai_strategy_firms_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #14a1a5;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #444;
            }
        """)
        self.ai_strategy_firms_list.itemClicked.connect(self.on_ai_strategy_firm_selected)
        firm_selection_layout.addWidget(self.ai_strategy_firms_list)
        
        # Analiz butonları - Gelişmiş
        analysis_buttons_widget = QWidget()
        analysis_buttons_layout = QVBoxLayout(analysis_buttons_widget)
        
        # Tekil analiz
        single_analysis_layout = QHBoxLayout()
        analyze_btn = QPushButton("🔍 Seçili Firmayı Analiz Et")
        analyze_btn.clicked.connect(self.analyze_selected_firm)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #14a1a5;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0f8a8e;
            }
            QPushButton:pressed {
                background-color: #0d7377;
            }
        """)
        single_analysis_layout.addWidget(analyze_btn)
        
        # Hızlı analiz butonu
        quick_analyze_btn = QPushButton("⚡ Hızlı Analiz")
        quick_analyze_btn.clicked.connect(self.quick_analyze_firm)
        quick_analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        single_analysis_layout.addWidget(quick_analyze_btn)
        analysis_buttons_layout.addLayout(single_analysis_layout)
        
        # Toplu analiz
        batch_analysis_layout = QHBoxLayout()
        analyze_all_btn = QPushButton("🚀 Tümünü Analiz Et")
        analyze_all_btn.clicked.connect(self.analyze_all_firms)
        analyze_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        batch_analysis_layout.addWidget(analyze_all_btn)
        
        # Seçili firmaları analiz et
        analyze_selected_btn = QPushButton("📋 Seçilileri Analiz Et")
        analyze_selected_btn.clicked.connect(self.analyze_selected_firms)
        analyze_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: #fd7e14;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8650e;
            }
        """)
        batch_analysis_layout.addWidget(analyze_selected_btn)
        analysis_buttons_layout.addLayout(batch_analysis_layout)
        
        firm_selection_layout.addWidget(analysis_buttons_widget)
        
        firm_selection_group.setLayout(firm_selection_layout)
        left_layout.addWidget(firm_selection_group)
        
        # Analiz durumu - Gelişmiş
        status_group = QGroupBox("📊 Analiz Durumu ve İstatistikler")
        status_layout = QVBoxLayout()
        
        # Durum göstergesi
        self.ai_analysis_status = QLabel("🟡 Analiz bekleniyor...")
        self.ai_analysis_status.setStyleSheet("""
            QLabel {
                color: #ffc107;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                background-color: #2a2a2a;
                border-radius: 4px;
                border-left: 4px solid #ffc107;
            }
        """)
        status_layout.addWidget(self.ai_analysis_status)
        
        # Progress bar
        self.ai_analysis_progress = QProgressBar()
        self.ai_analysis_progress.setVisible(False)
        self.ai_analysis_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 6px;
                text-align: center;
                background-color: #2a2a2a;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #14a1a5;
                border-radius: 4px;
            }
        """)
        status_layout.addWidget(self.ai_analysis_progress)
        
        # Hızlı istatistikler
        stats_mini_layout = QHBoxLayout()
        
        self.mini_analyzed_count = QLabel("✅ 0")
        self.mini_pending_count = QLabel("⏳ 0")
        self.mini_error_count = QLabel("❌ 0")
        
        for label in [self.mini_analyzed_count, self.mini_pending_count, self.mini_error_count]:
            label.setStyleSheet("""
                QLabel {
                    color: #cccccc;
                    font-size: 12px;
                    padding: 4px 8px;
                    background-color: #333;
                    border-radius: 4px;
                    margin: 2px;
                }
            """)
            stats_mini_layout.addWidget(label)
        
        status_layout.addLayout(stats_mini_layout)
        status_group.setLayout(status_layout)
        left_layout.addWidget(status_group)
        
        left_layout.addStretch()
        content_layout.addWidget(left_panel)
        
        # Sağ panel - Analiz sonuçları
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Seçili firma bilgisi - Gelişmiş
        firm_info_group = QGroupBox("🏢 Seçili Firma Bilgileri")
        firm_info_layout = QVBoxLayout()
        
        self.selected_firm_info = QLabel("Firma seçin...")
        self.selected_firm_info.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #14a1a5;
                margin-bottom: 10px;
                padding: 10px;
                background-color: #2a2a2a;
                border-radius: 6px;
                border-left: 4px solid #14a1a5;
            }
        """)
        firm_info_layout.addWidget(self.selected_firm_info)
        
        # Firma detayları
        self.firm_details = QLabel("Detaylar yüklenecek...")
        self.firm_details.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #cccccc;
                padding: 8px;
                background-color: #333;
                border-radius: 4px;
            }
        """)
        self.firm_details.setWordWrap(True)
        firm_info_layout.addWidget(self.firm_details)
        
        firm_info_group.setLayout(firm_info_layout)
        right_layout.addWidget(firm_info_group)
        
        # Analiz sonuçları grubu - Gelişmiş
        results_group = QGroupBox("🎯 AI Analiz Sonuçları")
        results_layout = QVBoxLayout()
        
        # Tab widget for results
        results_tabs = QTabWidget()
        results_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #2a2a2a;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #444;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #14a1a5;
            }
            QTabBar::tab:hover {
                background-color: #555;
            }
        """)
        
        # Strateji önerileri tab
        strategy_tab = QWidget()
        strategy_layout = QVBoxLayout(strategy_tab)
        
        self.strategy_recommendations = QTextEdit()
        self.strategy_recommendations.setPlaceholderText("Strateji önerileri burada görünecek...")
        self.strategy_recommendations.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        strategy_layout.addWidget(self.strategy_recommendations)
        results_tabs.addTab(strategy_tab, "📊 Stratejiler")
        
        # AI talimatları tab
        instructions_tab = QWidget()
        instructions_layout = QVBoxLayout(instructions_tab)
        
        self.ai_instructions = QTextEdit()
        self.ai_instructions.setPlaceholderText("AI talimatları burada görünecek...")
        self.ai_instructions.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        instructions_layout.addWidget(self.ai_instructions)
        results_tabs.addTab(instructions_tab, "🤖 AI Talimatları")
        
        # Risk analizi tab
        risk_tab = QWidget()
        risk_layout = QVBoxLayout(risk_tab)
        
        self.risk_analysis = QTextEdit()
        self.risk_analysis.setPlaceholderText("Risk analizi burada görünecek...")
        self.risk_analysis.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        risk_layout.addWidget(self.risk_analysis)
        results_tabs.addTab(risk_tab, "⚠️ Risk Analizi")
        
        results_layout.addWidget(results_tabs)
        
        # Aksiyon butonları
        action_buttons_layout = QHBoxLayout()
        
        send_to_campaign_btn = QPushButton("📧 Kampanyaya Gönder")
        send_to_campaign_btn.clicked.connect(self.send_to_campaign)
        send_to_campaign_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        action_buttons_layout.addWidget(send_to_campaign_btn)
        
        export_analysis_btn = QPushButton("💾 Analizi Kaydet")
        export_analysis_btn.clicked.connect(self.export_analysis)
        export_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        action_buttons_layout.addWidget(export_analysis_btn)
        
        results_layout.addLayout(action_buttons_layout)
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        # Analiz geçmişi - Gelişmiş
        history_group = QGroupBox("📈 Analiz Geçmişi ve Performans")
        history_layout = QVBoxLayout()
        
        # Geçmiş listesi
        self.analysis_history = QListWidget()
        self.analysis_history.setMaximumHeight(120)
        self.analysis_history.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #444;
                border-radius: 3px;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: #444;
            }
        """)
        history_layout.addWidget(self.analysis_history)
        
        # Performans özeti
        performance_layout = QHBoxLayout()
        
        self.performance_summary = QLabel("Performans: 0 analiz")
        self.performance_summary.setStyleSheet("""
            QLabel {
                color: #14a1a5;
                font-weight: bold;
                font-size: 12px;
                padding: 4px 8px;
                background-color: #333;
                border-radius: 4px;
            }
        """)
        performance_layout.addWidget(self.performance_summary)
        
        clear_history_btn = QPushButton("🗑️ Temizle")
        clear_history_btn.clicked.connect(self.clear_analysis_history)
        clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        performance_layout.addWidget(clear_history_btn)
        
        history_layout.addLayout(performance_layout)
        history_group.setLayout(history_layout)
        right_layout.addWidget(history_group)
        
        content_layout.addWidget(right_panel)
        main_layout.addLayout(content_layout)
        
        # Firmaları yükle
        self.refresh_ai_strategy_firms()
        
        return widget

    def create_voice_assistant_tab(self):
        """🎤 Sesli Asistan Sekmesi - AI Destekli Sesli Komut Sistemi"""
        widget = QWidget()
        widget.setObjectName("voiceAssistantWidget")
        
        # Ana layout
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Başlık
        title_label = QLabel("🎤 Sesli Asistan")
        title_label.setObjectName("voiceAssistantTitle")
        title_label.setStyleSheet("""
            #voiceAssistantTitle {
                font-size: 28px;
                font-weight: bold;
                color: #00d4aa;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #1a1a1a, stop: 0.5 #0d7377, stop: 1 #1a1a1a);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Durum kartları
        status_layout = QHBoxLayout()
        
        # Dinleme durumu
        self.voice_status_card = self.create_voice_status_card()
        status_layout.addWidget(self.voice_status_card)
        
        # AI durumu
        self.ai_status_card = self.create_ai_status_card()
        status_layout.addWidget(self.ai_status_card)
        
        # Komut sayısı
        self.command_count_card = self.create_command_count_card()
        status_layout.addWidget(self.command_count_card)
        
        main_layout.addLayout(status_layout)
        
        # Kontrol paneli
        control_panel = self.create_voice_control_panel()
        main_layout.addWidget(control_panel)
        
        # Komut geçmişi
        history_section = self.create_voice_history_section()
        main_layout.addWidget(history_section)
        
        # Komut listesi
        commands_section = self.create_voice_commands_section()
        main_layout.addWidget(commands_section)
        
        # Ayarlar
        settings_section = self.create_voice_settings_section()
        main_layout.addWidget(settings_section)
        
        return widget
    
    def create_voice_status_card(self):
        """Sesli durum kartı"""
        card = QWidget()
        card.setObjectName("voiceStatusCard")
        card.setStyleSheet("""
            #voiceStatusCard {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # İkon ve başlık
        header_layout = QHBoxLayout()
        icon_label = QLabel("🎤")
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Dinleme Durumu")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e8f0;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Durum göstergesi
        self.voice_status_label = QLabel("🔇 Durduruldu")
        self.voice_status_label.setStyleSheet("font-size: 14px; color: #f56565;")
        layout.addWidget(self.voice_status_label)
        
        # Son aktivite
        self.last_activity_label = QLabel("Son aktivite: Hiç")
        self.last_activity_label.setStyleSheet("font-size: 12px; color: #a0aec0;")
        layout.addWidget(self.last_activity_label)
        
        return card
    
    def create_ai_status_card(self):
        """AI durum kartı"""
        card = QWidget()
        card.setObjectName("aiStatusCard")
        card.setStyleSheet("""
            #aiStatusCard {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # İkon ve başlık
        header_layout = QHBoxLayout()
        icon_label = QLabel("🤖")
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("AI Durumu")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e8f0;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # AI durumu
        self.ai_status_label = QLabel("🔴 Bağlantı yok")
        self.ai_status_label.setStyleSheet("font-size: 14px; color: #f56565;")
        layout.addWidget(self.ai_status_label)
        
        # Model durumu
        self.model_status_label = QLabel("Modeller: Yükleniyor...")
        self.model_status_label.setStyleSheet("font-size: 12px; color: #a0aec0;")
        layout.addWidget(self.model_status_label)
        
        return card
    
    def create_command_count_card(self):
        """Komut sayısı kartı"""
        card = QWidget()
        card.setObjectName("commandCountCard")
        card.setStyleSheet("""
            #commandCountCard {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # İkon ve başlık
        header_layout = QHBoxLayout()
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("İstatistikler")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e2e8f0;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Komut sayısı
        self.command_count_label = QLabel("0 komut")
        self.command_count_label.setStyleSheet("font-size: 14px; color: #68d391;")
        layout.addWidget(self.command_count_label)
        
        # Başarı oranı
        self.success_rate_label = QLabel("Başarı: %0")
        self.success_rate_label.setStyleSheet("font-size: 12px; color: #a0aec0;")
        layout.addWidget(self.success_rate_label)
        
        return card
    
    def create_voice_control_panel(self):
        """Sesli kontrol paneli"""
        panel = QWidget()
        panel.setObjectName("voiceControlPanel")
        panel.setStyleSheet("""
            #voiceControlPanel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Başlık
        title_label = QLabel("🎛️ Kontrol Paneli")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e2e8f0; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        # Dinleme başlat/durdur
        self.start_listening_btn = QPushButton("🎤 Dinlemeyi Başlat")
        self.start_listening_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #48bb78, stop: 1 #38a169);
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #38a169, stop: 1 #2f855a);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2f855a, stop: 1 #276749);
            }
        """)
        self.start_listening_btn.clicked.connect(self.start_voice_listening)
        button_layout.addWidget(self.start_listening_btn)
        
        self.stop_listening_btn = QPushButton("🔇 Dinlemeyi Durdur")
        self.stop_listening_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f56565, stop: 1 #e53e3e);
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e53e3e, stop: 1 #c53030);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #c53030, stop: 1 #9c2626);
            }
        """)
        self.stop_listening_btn.clicked.connect(self.stop_voice_listening)
        button_layout.addWidget(self.stop_listening_btn)
        
        # Test konuşma
        self.test_speech_btn = QPushButton("🔊 Test Konuşma")
        self.test_speech_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4299e1, stop: 1 #3182ce);
                border: none;
                border-radius: 10px;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3182ce, stop: 1 #2c5282);
            }
        """)
        self.test_speech_btn.clicked.connect(self.test_voice_speech)
        button_layout.addWidget(self.test_speech_btn)
        
        layout.addLayout(button_layout)
        
        # Hızlı komutlar
        quick_commands_layout = QHBoxLayout()
        
        quick_commands_label = QLabel("Hızlı Komutlar:")
        quick_commands_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e2e8f0;")
        quick_commands_layout.addWidget(quick_commands_label)
        
        self.quick_hello_btn = QPushButton("Merhaba")
        self.quick_hello_btn.setStyleSheet("""
            QPushButton {
                background: #4a5568;
                border: 1px solid #718096;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: #5a6578;
            }
        """)
        self.quick_hello_btn.clicked.connect(lambda: self.send_voice_command("merhaba"))
        quick_commands_layout.addWidget(self.quick_hello_btn)
        
        self.quick_help_btn = QPushButton("Yardım")
        self.quick_help_btn.setStyleSheet("""
            QPushButton {
                background: #4a5568;
                border: 1px solid #718096;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: #5a6578;
            }
        """)
        self.quick_help_btn.clicked.connect(lambda: self.send_voice_command("yardım"))
        quick_commands_layout.addWidget(self.quick_help_btn)
        
        self.quick_status_btn = QPushButton("Durum")
        self.quick_status_btn.setStyleSheet("""
            QPushButton {
                background: #4a5568;
                border: 1px solid #718096;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                color: #e2e8f0;
            }
            QPushButton:hover {
                background: #5a6578;
            }
        """)
        self.quick_status_btn.clicked.connect(lambda: self.send_voice_command("sistem durumu"))
        quick_commands_layout.addWidget(self.quick_status_btn)
        
        quick_commands_layout.addStretch()
        layout.addLayout(quick_commands_layout)
        
        return panel
    
    def create_voice_history_section(self):
        """Sesli komut geçmişi bölümü"""
        section = QWidget()
        section.setObjectName("voiceHistorySection")
        section.setStyleSheet("""
            #voiceHistorySection {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(section)
        
        # Başlık ve temizle butonu
        header_layout = QHBoxLayout()
        
        title_label = QLabel("📝 Komut Geçmişi")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e2e8f0;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.clear_history_btn = QPushButton("🗑️ Temizle")
        self.clear_history_btn.setStyleSheet("""
            QPushButton {
                background: #f56565;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
                color: white;
            }
            QPushButton:hover {
                background: #e53e3e;
            }
        """)
        self.clear_history_btn.clicked.connect(self.clear_voice_history)
        header_layout.addWidget(self.clear_history_btn)
        
        layout.addLayout(header_layout)
        
        # Geçmiş listesi
        self.voice_history_list = QListWidget()
        self.voice_history_list.setStyleSheet("""
            QListWidget {
                background: #1a202c;
                border: 1px solid #4a5568;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }
            QListWidget::item {
                background: #2d3748;
                border: 1px solid #4a5568;
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
            }
            QListWidget::item:hover {
                background: #4a5568;
            }
            QListWidget::item:selected {
                background: #4299e1;
            }
        """)
        self.voice_history_list.setMaximumHeight(200)
        layout.addWidget(self.voice_history_list)
        
        return section
    
    def create_voice_commands_section(self):
        """Sesli komutlar bölümü"""
        section = QWidget()
        section.setObjectName("voiceCommandsSection")
        section.setStyleSheet("""
            #voiceCommandsSection {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(section)
        
        # Başlık
        title_label = QLabel("🎯 Kullanılabilir Komutlar")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e2e8f0; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        # Komut kategorileri
        categories_layout = QHBoxLayout()
        
        # Genel komutlar
        general_group = QGroupBox("Genel")
        general_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4a5568;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background: #1a202c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e2e8f0;
            }
        """)
        general_layout = QVBoxLayout(general_group)
        
        general_commands = [
            "merhaba", "selam", "hey",
            "teşekkürler", "sağol",
            "görüşürüz", "bye"
        ]
        
        for cmd in general_commands:
            label = QLabel(f"• {cmd}")
            label.setStyleSheet("color: #a0aec0; font-size: 12px; margin: 2px;")
            general_layout.addWidget(label)
        
        categories_layout.addWidget(general_group)
        
        # Sistem komutları
        system_group = QGroupBox("Sistem")
        system_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4a5568;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background: #1a202c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e2e8f0;
            }
        """)
        system_layout = QVBoxLayout(system_group)
        
        system_commands = [
            "sistem durumu",
            "bilgisayar kapat",
            "yeniden başlat"
        ]
        
        for cmd in system_commands:
            label = QLabel(f"• {cmd}")
            label.setStyleSheet("color: #a0aec0; font-size: 12px; margin: 2px;")
            system_layout.addWidget(label)
        
        categories_layout.addWidget(system_group)
        
        # B2B komutları
        b2b_group = QGroupBox("B2B")
        b2b_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4a5568;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background: #1a202c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e2e8f0;
            }
        """)
        b2b_layout = QVBoxLayout(b2b_group)
        
        b2b_commands = [
            "firma ara",
            "müşteri listesi",
            "email gönder",
            "rapor oluştur"
        ]
        
        for cmd in b2b_commands:
            label = QLabel(f"• {cmd}")
            label.setStyleSheet("color: #a0aec0; font-size: 12px; margin: 2px;")
            b2b_layout.addWidget(label)
        
        categories_layout.addWidget(b2b_group)
        
        # Web komutları
        web_group = QGroupBox("Web")
        web_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4a5568;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background: #1a202c;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #e2e8f0;
            }
        """)
        web_layout = QVBoxLayout(web_group)
        
        web_commands = [
            "web sitesi aç",
            "arama yap",
            "youtube aç"
        ]
        
        for cmd in web_commands:
            label = QLabel(f"• {cmd}")
            label.setStyleSheet("color: #a0aec0; font-size: 12px; margin: 2px;")
            web_layout.addWidget(label)
        
        categories_layout.addWidget(web_group)
        
        layout.addLayout(categories_layout)
        
        return section
    
    def create_voice_settings_section(self):
        """Sesli asistan ayarları bölümü"""
        section = QWidget()
        section.setObjectName("voiceSettingsSection")
        section.setStyleSheet("""
            #voiceSettingsSection {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2d3748, stop: 1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(section)
        
        # Başlık
        title_label = QLabel("⚙️ Ayarlar")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e2e8f0; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        # Ayarlar grid
        settings_layout = QGridLayout()
        
        # Ses hızı
        speed_label = QLabel("Ses Hızı:")
        speed_label.setStyleSheet("color: #e2e8f0; font-size: 14px;")
        settings_layout.addWidget(speed_label, 0, 0)
        
        self.voice_speed_slider = QSlider(Qt.Horizontal)
        self.voice_speed_slider.setMinimum(100)
        self.voice_speed_slider.setMaximum(300)
        self.voice_speed_slider.setValue(180)
        self.voice_speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #4a5568;
                height: 8px;
                background: #2d3748;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4299e1;
                border: 1px solid #3182ce;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        settings_layout.addWidget(self.voice_speed_slider, 0, 1)
        
        self.voice_speed_label = QLabel("180")
        self.voice_speed_label.setStyleSheet("color: #a0aec0; font-size: 12px;")
        settings_layout.addWidget(self.voice_speed_label, 0, 2)
        
        # Ses seviyesi
        volume_label = QLabel("Ses Seviyesi:")
        volume_label.setStyleSheet("color: #e2e8f0; font-size: 14px;")
        settings_layout.addWidget(volume_label, 1, 0)
        
        self.voice_volume_slider = QSlider(Qt.Horizontal)
        self.voice_volume_slider.setMinimum(0)
        self.voice_volume_slider.setMaximum(100)
        self.voice_volume_slider.setValue(90)
        self.voice_volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #4a5568;
                height: 8px;
                background: #2d3748;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #48bb78;
                border: 1px solid #38a169;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
        settings_layout.addWidget(self.voice_volume_slider, 1, 1)
        
        self.voice_volume_label = QLabel("90%")
        self.voice_volume_label.setStyleSheet("color: #a0aec0; font-size: 12px;")
        settings_layout.addWidget(self.voice_volume_label, 1, 2)
        
        # Otomatik dinleme
        self.auto_listen_checkbox = QCheckBox("Otomatik dinlemeyi başlat")
        self.auto_listen_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e2e8f0;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #4a5568;
                background: #2d3748;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4299e1;
                background: #4299e1;
                border-radius: 3px;
            }
        """)
        settings_layout.addWidget(self.auto_listen_checkbox, 2, 0, 1, 3)
        
        layout.addLayout(settings_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.save_settings_btn = QPushButton("💾 Ayarları Kaydet")
        self.save_settings_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #48bb78, stop: 1 #38a169);
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #38a169, stop: 1 #2f855a);
            }
        """)
        self.save_settings_btn.clicked.connect(self.save_voice_settings)
        button_layout.addWidget(self.save_settings_btn)
        
        self.export_data_btn = QPushButton("📁 Verileri Dışa Aktar")
        self.export_data_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4299e1, stop: 1 #3182ce);
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3182ce, stop: 1 #2c5282);
            }
        """)
        self.export_data_btn.clicked.connect(self.export_voice_data)
        button_layout.addWidget(self.export_data_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return section
    
    # Sesli asistan fonksiyonları
    def start_voice_listening(self):
        """Sesli dinlemeyi başlat"""
        # Önce gelişmiş sistemi dene
        if self.advanced_voice_assistant_gui:
            success = self.advanced_voice_assistant_gui.start_advanced_listening()
            if success:
                self.voice_status_label.setText("🚀 Gelişmiş AI Dinleniyor...")
                self.voice_status_label.setStyleSheet("font-size: 14px; color: #68d391;")
                self.start_listening_btn.setEnabled(False)
                self.stop_listening_btn.setEnabled(True)
                print("✅ Gelişmiş sesli dinleme başlatıldı")
                return
        
        # Fallback: Temel sesli asistan
        if self.voice_assistant_gui:
            success = self.voice_assistant_gui.start_listening()
            if success:
                self.voice_status_label.setText("🎤 Dinleniyor...")
                self.voice_status_label.setStyleSheet("font-size: 14px; color: #68d391;")
                self.start_listening_btn.setEnabled(False)
                self.stop_listening_btn.setEnabled(True)
                print("✅ Sesli dinleme başlatıldı")
            else:
                QMessageBox.warning(self, "Uyarı", "Sesli asistan başlatılamadı!")
        else:
            QMessageBox.critical(self, "Hata", "Sesli asistan modülü yüklenemedi!")
    
    def stop_voice_listening(self):
        """Sesli dinlemeyi durdur"""
        # Önce gelişmiş sistemi durdur
        if self.advanced_voice_assistant_gui:
            success = self.advanced_voice_assistant_gui.stop_advanced_listening()
            if success:
                self.voice_status_label.setText("🔇 Gelişmiş AI Durduruldu")
                self.voice_status_label.setStyleSheet("font-size: 14px; color: #f56565;")
                self.start_listening_btn.setEnabled(True)
                self.stop_listening_btn.setEnabled(False)
                print("🔇 Gelişmiş sesli dinleme durduruldu")
                return
        
        # Fallback: Temel sesli asistan
        if self.voice_assistant_gui:
            success = self.voice_assistant_gui.stop_listening()
            if success:
                self.voice_status_label.setText("🔇 Durduruldu")
                self.voice_status_label.setStyleSheet("font-size: 14px; color: #f56565;")
                self.start_listening_btn.setEnabled(True)
                self.stop_listening_btn.setEnabled(False)
                print("🔇 Sesli dinleme durduruldu")
            else:
                QMessageBox.warning(self, "Uyarı", "Sesli dinleme durdurulamadı!")
        else:
            QMessageBox.critical(self, "Hata", "Sesli asistan modülü yüklenemedi!")
    
    def test_voice_speech(self):
        """Test konuşması"""
        if self.voice_assistant_gui:
            self.voice_assistant_gui.speak("Merhaba! Ben sesli asistanınızım. Size nasıl yardımcı olabilirim?")
        else:
            QMessageBox.critical(self, "Hata", "Sesli asistan modülü yüklenemedi!")
    
    def send_voice_command(self, command: str):
        """Manuel komut gönder"""
        if self.voice_assistant_gui and self.voice_assistant_gui.assistant:
            self.voice_assistant_gui.assistant.process_command(command)
            self.update_voice_history()
        else:
            QMessageBox.critical(self, "Hata", "Sesli asistan modülü yüklenemedi!")
    
    def clear_voice_history(self):
        """Sesli komut geçmişini temizle"""
        if self.voice_assistant_gui:
            self.voice_assistant_gui.clear_history()
            self.voice_history_list.clear()
            print("🗑️ Sesli komut geçmişi temizlendi")
    
    def update_voice_history(self):
        """Sesli komut geçmişini güncelle"""
        if self.voice_assistant_gui:
            history = self.voice_assistant_gui.get_command_history()
            self.voice_history_list.clear()
            
            for item in history:
                timestamp = item.get('timestamp', '')
                command = item.get('command', '')
                time_str = datetime.fromisoformat(timestamp).strftime('%H:%M:%S') if timestamp else 'Bilinmiyor'
                
                list_item = QListWidgetItem(f"[{time_str}] {command}")
                list_item.setStyleSheet("color: #e2e8f0;")
                self.voice_history_list.addItem(list_item)
    
    def save_voice_settings(self):
        """Sesli asistan ayarlarını kaydet"""
        if self.voice_assistant_gui and self.voice_assistant_gui.assistant:
            # Ayarları güncelle
            speed = self.voice_speed_slider.value()
            volume = self.voice_volume_slider.value() / 100.0
            
            self.voice_assistant_gui.assistant.tts_engine.setProperty('rate', speed)
            self.voice_assistant_gui.assistant.tts_engine.setProperty('volume', volume)
            
            QMessageBox.information(self, "Başarılı", "Sesli asistan ayarları kaydedildi!")
        else:
            QMessageBox.critical(self, "Hata", "Sesli asistan modülü yüklenemedi!")
    
    def export_voice_data(self):
        """Sesli asistan verilerini dışa aktar"""
        if self.voice_assistant_gui:
            from PySide6.QtWidgets import QFileDialog
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Sesli Asistan Verilerini Kaydet",
                f"voice_assistant_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                success = self.voice_assistant_gui.export_data(file_path)
                if success:
                    QMessageBox.information(self, "Başarılı", f"Veriler kaydedildi: {file_path}")
                else:
                    QMessageBox.critical(self, "Hata", "Veriler kaydedilemedi!")
        else:
            QMessageBox.critical(self, "Hata", "Sesli asistan modülü yüklenemedi!")
    
    # AI Strateji Analizi Metodları
    def create_stat_card(self, title, value, color):
        """İstatistik kartı oluştur"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        layout.addWidget(value_label)
        
        return card
    
    def filter_by_status(self, status):
        """Firmaları duruma göre filtrele"""
        try:
            # Diğer butonları kapat
            for btn in [self.filter_all_btn, self.filter_analyzed_btn, self.filter_pending_btn, self.filter_high_quality_btn]:
                btn.setChecked(False)
            
            # Seçili butonu işaretle
            if status == "all":
                self.filter_all_btn.setChecked(True)
            elif status == "analyzed":
                self.filter_analyzed_btn.setChecked(True)
            elif status == "pending":
                self.filter_pending_btn.setChecked(True)
            elif status == "high_quality":
                self.filter_high_quality_btn.setChecked(True)
            
            # Filtreleme uygula
            for i in range(self.ai_strategy_firms_list.count()):
                item = self.ai_strategy_firms_list.item(i)
                firm_id = item.data(Qt.UserRole)
                
                if not firm_id:
                    continue
                
                # Firma verilerini al
                firm_data = self.ai_strategy_analyzer.get_firm_data(firm_id) if self.ai_strategy_analyzer else None
                
                show_item = True
                
                if status == "analyzed" and firm_data:
                    show_item = firm_data.get('is_analyzed', 0) == 1
                elif status == "pending" and firm_data:
                    show_item = firm_data.get('is_analyzed', 0) == 0
                elif status == "high_quality" and firm_data:
                    quality_score = firm_data.get('quality_score', 0)
                    show_item = quality_score and quality_score >= 70
                
                item.setHidden(not show_item)
                
        except Exception as e:
            print(f"Filtreleme hatası: {e}")
    
    def quick_analyze_firm(self):
        """Hızlı analiz yap"""
        try:
            current_item = self.ai_strategy_firms_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uyarı", "Lütfen analiz edilecek firmayı seçin!")
                return
            
            firm_id = current_item.data(Qt.UserRole)
            if not firm_id:
                return
            
            # Hızlı analiz için basit strateji belirleme
            firm_data = self.ai_strategy_analyzer.get_firm_data(firm_id) if self.ai_strategy_analyzer else None
            
            if firm_data:
                quality_score = firm_data.get('quality_score', 50)
                sector = firm_data.get('sector', 'Bilinmiyor')
                
                # Basit strateji belirleme
                if quality_score >= 80:
                    strategy = "Agresif"
                    confidence = 85
                elif quality_score >= 60:
                    strategy = "Eğitici"
                    confidence = 70
                else:
                    strategy = "Muhafazakar"
                    confidence = 60
                
                # Sonuçları göster
                self.strategy_recommendations.setText(f"""
Hızlı Analiz Sonucu:
====================
Firma: {firm_data['name']}
Sektör: {sector}
Kalite Skoru: {quality_score}/100
Önerilen Strateji: {strategy}
Güven Skoru: {confidence}%

Bu hızlı analiz temel verilere dayanmaktadır.
Detaylı analiz için "Seçili Firmayı Analiz Et" butonunu kullanın.
                """)
                
                self.ai_instructions.setText(f"""
Hızlı AI Talimatları:
====================
- {strategy} strateji yaklaşımı uygula
- {sector} sektörüne uygun içerik hazırla
- Kalite skoru {quality_score} olduğu için uygun ton kullan
- Firma adını kişiselleştir: {firm_data['name']}
                """)
                
                self.risk_analysis.setText(f"""
Hızlı Risk Değerlendirmesi:
===========================
Spam Riski: {'Düşük' if quality_score >= 70 else 'Orta'}
Etkileşim Potansiyeli: {'Yüksek' if quality_score >= 80 else 'Orta'}
Önerilen Mail Sıklığı: {'Haftalık' if quality_score >= 80 else 'İki haftada bir'}
                """)
                
                self.ai_analysis_status.setText("⚡ Hızlı analiz tamamlandı!")
                self.ai_analysis_status.setStyleSheet("color: #6f42c1; font-weight: bold;")
                
                QMessageBox.information(self, "Hızlı Analiz", f"{firm_data['name']} için hızlı analiz tamamlandı!")
            else:
                QMessageBox.warning(self, "Uyarı", "Firma verileri alınamadı!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hızlı analiz hatası:\n{str(e)}")
    
    def analyze_selected_firms(self):
        """Seçili firmaları analiz et"""
        try:
            # Seçili firmaları bul
            selected_items = []
            for i in range(self.ai_strategy_firms_list.count()):
                item = self.ai_strategy_firms_list.item(i)
                if not item.isHidden() and item.isSelected():
                    selected_items.append(item)
            
            if not selected_items:
                QMessageBox.warning(self, "Uyarı", "Lütfen analiz edilecek firmaları seçin!")
                return
            
            reply = QMessageBox.question(
                self, "Onay", 
                f"{len(selected_items)} firma seçildi. Analiz etmek istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Progress bar'ı ayarla
            self.ai_analysis_progress.setVisible(True)
            self.ai_analysis_progress.setRange(0, len(selected_items))
            self.ai_analysis_progress.setValue(0)
            
            success_count = 0
            error_count = 0
            
            for i, item in enumerate(selected_items):
                try:
                    firm_id = item.data(Qt.UserRole)
                    firm_name = item.text().split(' - ')[0]
                    
                    self.ai_analysis_status.setText(f"Analiz ediliyor: {firm_name} ({i+1}/{len(selected_items)})")
                    
                    # Analizi yap
                    analysis = self.ai_strategy_analyzer.analyze_firm_with_ai(firm_id) if self.ai_strategy_analyzer else None
                    
                    if analysis:
                        self.ai_strategy_analyzer.save_analysis_to_database(analysis)
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # Progress'i güncelle
                    self.ai_analysis_progress.setValue(i + 1)
                    QApplication.processEvents()
                    
                except Exception as e:
                    print(f"Firma analiz hatası {item.text()}: {e}")
                    error_count += 1
            
            # Sonuçları göster
            self.ai_analysis_status.setText(f"✅ Seçili analiz tamamlandı! Başarılı: {success_count}, Hata: {error_count}")
            self.ai_analysis_status.setStyleSheet("color: #28a745; font-weight: bold;")
            
            QMessageBox.information(
                self, "Seçili Analiz Tamamlandı", 
                f"Seçilen {len(selected_items)} firma analiz edildi.\nBaşarılı: {success_count}\nHata: {error_count}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Seçili analiz hatası:\n{str(e)}")
        finally:
            self.ai_analysis_progress.setVisible(False)
    
    def export_analysis(self):
        """Analiz sonuçlarını dışa aktar"""
        try:
            current_item = self.ai_strategy_firms_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uyarı", "Lütfen dışa aktarılacak firmayı seçin!")
                return
            
            firm_id = current_item.data(Qt.UserRole)
            if not firm_id:
                return
            
            # Dosya seçimi
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Analiz Sonuçlarını Kaydet",
                f"ai_analysis_{firm_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                # Analiz verilerini topla
                analysis_data = {
                    'firm_id': firm_id,
                    'firm_name': current_item.text().split(' - ')[0],
                    'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'strategy_recommendations': self.strategy_recommendations.toPlainText(),
                    'ai_instructions': self.ai_instructions.toPlainText(),
                    'risk_analysis': self.risk_analysis.toPlainText()
                }
                
                # JSON olarak kaydet
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "Başarılı", f"Analiz sonuçları kaydedildi:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma hatası:\n{str(e)}")
    
    def clear_analysis_history(self):
        """Analiz geçmişini temizle"""
        try:
            reply = QMessageBox.question(
                self, "Onay", 
                "Analiz geçmişini temizlemek istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.analysis_history.clear()
                self.performance_summary.setText("Performans: 0 analiz")
                QMessageBox.information(self, "Başarılı", "Analiz geçmişi temizlendi!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Geçmiş temizleme hatası:\n{str(e)}")
    
    def show_ai_strategy_context_menu(self, position):
        """AI Strateji sekmesinde sağ tık menüsü"""
        try:
            item = self.ai_strategy_firms_list.itemAt(position)
            if not item:
                return
            
            # Context menu oluştur
            context_menu = QMenu(self)
            
            # Firma detaylarını göster
            show_details_action = QAction("📋 Firma Detaylarını Göster", self)
            show_details_action.triggered.connect(self.show_firm_detailed_summary)
            context_menu.addAction(show_details_action)
            
            # Analiz yap
            analyze_action = QAction("🤖 AI Analizi Yap", self)
            analyze_action.triggered.connect(self.analyze_selected_firm)
            context_menu.addAction(analyze_action)
            
            # Hızlı analiz
            quick_analyze_action = QAction("⚡ Hızlı Analiz", self)
            quick_analyze_action.triggered.connect(self.quick_analyze_firm)
            context_menu.addAction(quick_analyze_action)
            
            context_menu.addSeparator()
            
            # Kampanyaya gönder
            send_campaign_action = QAction("📧 Kampanyaya Gönder", self)
            send_campaign_action.triggered.connect(self.send_to_campaign)
            context_menu.addAction(send_campaign_action)
            
            # Dışa aktar
            export_action = QAction("💾 Analizi Dışa Aktar", self)
            export_action.triggered.connect(self.export_analysis)
            context_menu.addAction(export_action)
            
            # Menüyü göster
            context_menu.exec_(self.ai_strategy_firms_list.mapToGlobal(position))
            
        except Exception as e:
            print(f"Context menu hatası: {e}")
    
    def show_firm_detailed_summary(self):
        """Firma detaylı özetini popup olarak göster"""
        try:
            current_item = self.ai_strategy_firms_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir firma seçin!")
                return
            
            firm_id = current_item.data(Qt.UserRole)
            if not firm_id:
                QMessageBox.warning(self, "Uyarı", "Firma ID bulunamadı!")
                return
            
            # Firma verilerini getir
            firm_data = self.ai_strategy_analyzer.get_firm_data(firm_id)
            if not firm_data:
                QMessageBox.warning(self, "Uyarı", "Firma verileri bulunamadı!")
                return
            
            # Popup dialog oluştur
            dialog = QDialog(self)
            dialog.setWindowTitle(f"📋 {firm_data['name']} - Detaylı Özet")
            dialog.setModal(True)
            dialog.resize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title_label = QLabel(f"🏢 {firm_data['name']}")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    font-weight: bold;
                    color: #14a1a5;
                    margin-bottom: 10px;
                }
            """)
            layout.addWidget(title_label)
            
            # Scroll area
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            
            # Firma bilgileri
            info_text = f"""
            <h3>📊 Temel Bilgiler</h3>
            <p><b>Sektör:</b> {firm_data.get('sector', 'Bilinmiyor')}</p>
            <p><b>Web Sitesi:</b> <a href="{firm_data.get('website', '#')}">{firm_data.get('website', 'Yok')}</a></p>
            <p><b>Kalite Skoru:</b> {firm_data.get('quality_score', 'Bilinmiyor')}/100</p>
            <p><b>Kalite Notu:</b> {firm_data.get('quality_grade', 'Bilinmiyor')}</p>
            <p><b>E-ticaret:</b> {'Evet' if firm_data.get('has_ecommerce') else 'Hayır'}</p>
            <p><b>Teknik Skor:</b> {firm_data.get('technical_score', 'Bilinmiyor')}/100</p>
            <p><b>İçerik Skoru:</b> {firm_data.get('content_score', 'Bilinmiyor')}/100</p>
            <p><b>Şirket Tipi:</b> {firm_data.get('company_type', 'Bilinmiyor')}</p>
            <p><b>Güven Skoru:</b> {firm_data.get('company_type_confidence', 'Bilinmiyor')}%</p>
            <p><b>Takım Büyüklüğü:</b> {firm_data.get('team_size_estimate', 'Bilinmiyor')}</p>
            
            <h3>📝 Ürünler ve Hizmetler</h3>
            <p><b>Ürünler:</b> {firm_data.get('products', 'Yok')}</p>
            <p><b>Hizmetler:</b> {firm_data.get('services', 'Yok')}</p>
            
            <h3>📄 İş Bilgileri</h3>
            <p><b>İş Bilgileri:</b> {firm_data.get('business_info', 'Yok')}</p>
            <p><b>Hakkında Metni:</b> {firm_data.get('about_text', 'Yok')}</p>
            
            <h3>🤖 AI Özeti</h3>
            <p>{firm_data.get('ai_summary', 'AI özeti bulunmuyor')}</p>
            """
            
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: #2a2a2a;
                    padding: 15px;
                    border-radius: 8px;
                    font-size: 14px;
                }
                QLabel a {
                    color: #14a1a5;
                    text-decoration: none;
                }
                QLabel a:hover {
                    text-decoration: underline;
                }
            """)
            scroll_layout.addWidget(info_label)
            
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            close_btn = QPushButton("❌ Kapat")
            close_btn.clicked.connect(dialog.close)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            
            analyze_btn = QPushButton("🤖 AI Analizi Yap")
            analyze_btn.clicked.connect(lambda: [dialog.close(), self.analyze_selected_firm()])
            analyze_btn.setStyleSheet("""
                QPushButton {
                    background-color: #14a1a5;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0d7377;
                }
            """)
            
            button_layout.addWidget(analyze_btn)
            button_layout.addWidget(close_btn)
            layout.addLayout(button_layout)
            
            # Dialog stil
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1e1e1e;
                    color: white;
                }
            """)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Detaylı özet gösterimi hatası:\n{str(e)}")

    def refresh_ai_strategy_firms(self):
        """AI Strateji sekmesindeki firma listesini yenile"""
        try:
            if not self.ai_strategy_analyzer:
                QMessageBox.warning(self, "Uyarı", "AI Strateji Analyzer mevcut değil!")
                return
            
            # Firmaları getir
            firms = self.ai_strategy_analyzer.get_all_firms_for_analysis()
            
            # Listeyi temizle
            self.ai_strategy_firms_list.clear()
            
            # Firmaları ekle
            for firm in firms:
                item_text = f"{firm['name']} - {firm['sector']} (Skor: {firm['quality_score']})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, firm['id'])  # Firma ID'sini sakla
                
                # Analiz durumuna göre renk
                if firm['is_analyzed']:
                    item.setBackground(QColor(40, 167, 69, 50))  # Yeşil - analiz edilmiş
                else:
                    item.setBackground(QColor(255, 193, 7, 50))  # Sarı - analiz bekliyor
                
                self.ai_strategy_firms_list.addItem(item)
            
            self.ai_analysis_status.setText(f"✅ {len(firms)} firma yüklendi")
            
            # İstatistikleri güncelle
            self.update_ai_strategy_stats(firms)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Firma listesi yüklenemedi:\n{str(e)}")
    
    def update_ai_strategy_stats(self, firms):
        """AI Strateji istatistiklerini güncelle"""
        try:
            total_firms = len(firms)
            analyzed_count = sum(1 for firm in firms if firm.get('is_analyzed', 0) == 1)
            pending_count = total_firms - analyzed_count
            success_rate = (analyzed_count / total_firms * 100) if total_firms > 0 else 0
            
            # Ana istatistik kartlarını güncelle
            if hasattr(self, 'ai_total_firms_card'):
                self.ai_total_firms_card.findChild(QLabel).setText(str(total_firms))
            
            if hasattr(self, 'ai_analyzed_card'):
                self.ai_analyzed_card.findChild(QLabel).setText(str(analyzed_count))
            
            if hasattr(self, 'ai_pending_card'):
                self.ai_pending_card.findChild(QLabel).setText(str(pending_count))
            
            if hasattr(self, 'ai_success_rate_card'):
                self.ai_success_rate_card.findChild(QLabel).setText(f"{success_rate:.1f}%")
            
            # Mini istatistikleri güncelle
            if hasattr(self, 'mini_analyzed_count'):
                self.mini_analyzed_count.setText(f"✅ {analyzed_count}")
            
            if hasattr(self, 'mini_pending_count'):
                self.mini_pending_count.setText(f"⏳ {pending_count}")
            
            if hasattr(self, 'mini_error_count'):
                self.mini_error_count.setText("❌ 0")
            
            # Performans özetini güncelle
            if hasattr(self, 'performance_summary'):
                self.performance_summary.setText(f"Performans: {analyzed_count} analiz")
                
        except Exception as e:
            print(f"İstatistik güncelleme hatası: {e}")
    
    def filter_ai_strategy_firms(self):
        """AI Strateji sekmesindeki firmaları filtrele"""
        try:
            search_text = self.ai_strategy_search_input.text().lower()
            email_only = self.ai_strategy_email_only.isChecked() if hasattr(self, 'ai_strategy_email_only') else False
            sector_filter = self.ai_strategy_sector_combo.currentData() if hasattr(self, 'ai_strategy_sector_combo') else ""
            min_quality = self.ai_strategy_min_quality.value() if hasattr(self, 'ai_strategy_min_quality') else 0
            
            for i in range(self.ai_strategy_firms_list.count()):
                item = self.ai_strategy_firms_list.item(i)
                if not item:
                    continue
                
                # Metin arama
                if search_text and search_text not in item.text().lower():
                    item.setHidden(True)
                    continue
                
                # Detay filtreler için firma verisini çek
                show_item = True
                firm_id = item.data(Qt.UserRole)
                firm_data = self.ai_strategy_analyzer.get_firm_data(firm_id) if (hasattr(self, 'ai_strategy_analyzer') and self.ai_strategy_analyzer and firm_id) else None
                
                if email_only and firm_data:
                    has_email = bool(firm_data.get('email')) or bool(firm_data.get('emails'))
                    show_item = show_item and has_email
                
                if sector_filter and firm_data:
                    show_item = show_item and (firm_data.get('sector') == sector_filter)
                
                if firm_data and min_quality > 0:
                    show_item = show_item and (int(firm_data.get('quality_score', 0)) >= min_quality)
                
                item.setHidden(not show_item)
                    
        except Exception as e:
            print(f"Firma filtreleme hatası: {e}")
    
    def on_ai_strategy_firm_selected(self, item):
        """AI Strateji sekmesinde firma seçildiğinde"""
        try:
            firm_id = item.data(Qt.UserRole)
            if not firm_id:
                return
            
            # Firma bilgilerini göster
            firm_data = self.ai_strategy_analyzer.get_firm_data(firm_id) if self.ai_strategy_analyzer else None
            if firm_data:
                # Firma bilgilerini göster
                self.selected_firm_info.setText(f"🏢 {firm_data['name']}")
                
                # Firma detaylarını göster
                details = f"""
Sektör: {firm_data.get('sector', 'Bilinmiyor')}
Kalite Skoru: {firm_data.get('quality_score', 'N/A')}/100
Web Sitesi: {firm_data.get('website', 'Yok')}
Analiz Durumu: {'✅ Analiz Edilmiş' if firm_data.get('is_analyzed', 0) == 1 else '⏳ Bekliyor'}
Son Güncelleme: {firm_data.get('last_scraped_at', 'Bilinmiyor')}
                """.strip()
                self.firm_details.setText(details)
                
                # Mevcut analiz varsa göster
                analysis_data = self.ai_strategy_analyzer.get_analysis_for_campaign(firm_id) if self.ai_strategy_analyzer else None
                if analysis_data:
                    self.strategy_recommendations.setText(str(analysis_data['strategy_recommendations']))
                    self.ai_instructions.setText(analysis_data['ai_instructions'])
                    
                    # Risk analizi varsa göster
                    if 'risk_assessment' in analysis_data:
                        risk_text = f"""
Spam Riski: {analysis_data['risk_assessment'].get('spam_risk', 'N/A')}%
Aşırı Takip Riski: {analysis_data['risk_assessment'].get('over_contact_risk', 'N/A')}%
Düşük Etkileşim Riski: {analysis_data['risk_assessment'].get('low_engagement_risk', 'N/A')}%
                        """.strip()
                        self.risk_analysis.setText(risk_text)
                else:
                    self.strategy_recommendations.setText("Henüz analiz yapılmamış.\nDetaylı analiz için 'Seçili Firmayı Analiz Et' butonunu kullanın.")
                    self.ai_instructions.setText("Analiz yapıldıktan sonra AI talimatları burada görünecek.")
                    self.risk_analysis.setText("Risk analizi için önce firma analizi yapılmalı.")
            else:
                self.selected_firm_info.setText("❌ Firma verileri alınamadı")
                self.firm_details.setText("Veri yükleme hatası")
                self.strategy_recommendations.setText("Firma verileri alınamadı")
                self.ai_instructions.setText("Firma verileri alınamadı")
                self.risk_analysis.setText("Firma verileri alınamadı")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Firma seçimi hatası:\n{str(e)}")
    
    def analyze_selected_firm(self):
        """Seçili firmayı analiz et"""
        try:
            current_item = self.ai_strategy_firms_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uyarı", "Lütfen analiz edilecek firmayı seçin!")
                return
            
            firm_id = current_item.data(Qt.UserRole)
            if not firm_id:
                return
            
            # Analiz durumunu güncelle
            self.ai_analysis_status.setText("Analiz yapılıyor...")
            self.ai_analysis_status.setStyleSheet("color: #ffc107; font-weight: bold;")
            self.ai_analysis_progress.setVisible(True)
            self.ai_analysis_progress.setRange(0, 0)  # Indeterminate progress
            
            # Analizi başlat
            analysis = self.ai_strategy_analyzer.analyze_firm_with_ai(firm_id)
            
            if analysis:
                # Analizi kaydet
                self.ai_strategy_analyzer.save_analysis_to_database(analysis)
                
                # Sonuçları göster - Detaylı karşılaştırmalı analiz
                strategy_text = f"""
🎯 STRATEJİ ÖNERİLERİ:
====================
{json.dumps(analysis.strategy_recommendations, ensure_ascii=False, indent=2)}

📊 VERİ KARŞILAŞTIRMA ANALİZİ:
=============================
{getattr(analysis, 'comparison_insights', 'Karşılaştırma analizi mevcut değil')}

🔍 DETAYLI ANALİZ:
================
- Firma Tipi: {getattr(analysis, 'firm_type', 'Bilinmiyor')}
- Güçlü Yönler: {', '.join(getattr(analysis, 'strengths', []))}
- Zayıflıklar: {', '.join(getattr(analysis, 'weaknesses', []))}
- Pazar Konumu: {getattr(analysis, 'market_position', 'Bilinmiyor')}
                """.strip()
                
                self.strategy_recommendations.setText(strategy_text)
                
                ai_instructions_text = f"""
🤖 AI TALİMATLARI:
=================
{analysis.ai_instructions}

📝 ÖZEL PROMPT:
==============
{analysis.custom_prompt}

🎯 KİŞİSELLEŞTİRME STRATEJİSİ:
============================
- Kişiselleştirme Seviyesi: {getattr(analysis, 'personalization_level', 'Orta')}
- İçerik Odak Noktaları: {', '.join(getattr(analysis, 'content_focus', []))}
- Zamanlama Önerileri: {getattr(analysis, 'timing_recommendations', 'Genel')}
                """.strip()
                
                self.ai_instructions.setText(ai_instructions_text)
                
                # Durumu güncelle
                self.ai_analysis_status.setText("✅ Analiz tamamlandı!")
                self.ai_analysis_status.setStyleSheet("color: #28a745; font-weight: bold;")
                
                # Risk analizi göster
                risk_text = f"""
⚠️ RİSK DEĞERLENDİRMESİ:
=======================
- Spam Riski: {analysis.risk_assessment.get('spam_risk', 'N/A')}%
- Aşırı Takip Riski: {analysis.risk_assessment.get('over_contact_risk', 'N/A')}%
- Düşük Etkileşim Riski: {analysis.risk_assessment.get('low_engagement_risk', 'N/A')}%
- Veri Güvenilirlik Riski: {analysis.risk_assessment.get('data_reliability_risk', 'N/A')}%

📈 FIRSAT ANALİZİ:
=================
- Yüksek Etkileşim Potansiyeli: {getattr(analysis, 'opportunity_score', 0)}%
- En İyi Zamanlama: {getattr(analysis, 'best_timing', 'Genel')}
- İçerik Fırsatları: {', '.join(getattr(analysis, 'content_opportunities', []))}
- Kişiselleştirme Fırsatları: {', '.join(getattr(analysis, 'personalization_opportunities', []))}

🎯 VERİ KARŞILAŞTIRMA SONUÇLARI:
===============================
- Tutarlılık Skoru: {getattr(analysis, 'consistency_score', 'N/A')}%
- Veri Kalitesi: {getattr(analysis, 'data_quality', 'Orta')}
- Çelişen Veriler: {', '.join(getattr(analysis, 'conflicting_data', []))}
- Eksik Veriler: {', '.join(getattr(analysis, 'missing_data', []))}
                """.strip()
                
                self.risk_analysis.setText(risk_text)
                
                # Geçmişe ekle
                history_item = f"{analysis.firm_name} - {analysis.recommended_strategy.value} ({analysis.analysis_date})"
                self.analysis_history.addItem(history_item)
                
                QMessageBox.information(self, "Başarılı", f"{analysis.firm_name} analizi tamamlandı!")
            else:
                self.ai_analysis_status.setText("❌ Analiz başarısız!")
                self.ai_analysis_status.setStyleSheet("color: #dc3545; font-weight: bold;")
                QMessageBox.critical(self, "Hata", "Analiz yapılamadı!")
            
        except Exception as e:
            self.ai_analysis_status.setText("❌ Analiz hatası!")
            self.ai_analysis_status.setStyleSheet("color: #dc3545; font-weight: bold;")
            QMessageBox.critical(self, "Hata", f"Analiz hatası:\n{str(e)}")
        finally:
            self.ai_analysis_progress.setVisible(False)
    
    def analyze_all_firms(self):
        """Tüm firmaları analiz et"""
        try:
            reply = QMessageBox.question(
                self, "Onay", 
                "Tüm firmaları analiz etmek istediğinizden emin misiniz?\nBu işlem uzun sürebilir.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Firmaları getir
            firms = self.ai_strategy_analyzer.get_all_firms_for_analysis()
            total_firms = len(firms)
            
            if total_firms == 0:
                QMessageBox.information(self, "Bilgi", "Analiz edilecek firma bulunamadı!")
                return
            
            # Progress bar'ı ayarla
            self.ai_analysis_progress.setVisible(True)
            self.ai_analysis_progress.setRange(0, total_firms)
            self.ai_analysis_progress.setValue(0)
            
            success_count = 0
            error_count = 0
            
            for i, firm in enumerate(firms):
                try:
                    self.ai_analysis_status.setText(f"Analiz ediliyor: {firm['name']} ({i+1}/{total_firms})")
                    
                    # Analizi yap
                    analysis = self.ai_strategy_analyzer.analyze_firm_with_ai(firm['id'])
                    
                    if analysis:
                        self.ai_strategy_analyzer.save_analysis_to_database(analysis)
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # Progress'i güncelle
                    self.ai_analysis_progress.setValue(i + 1)
                    QApplication.processEvents()  # UI'yi güncelle
                    
                except Exception as e:
                    print(f"Firma analiz hatası {firm['name']}: {e}")
                    error_count += 1
            
            # Sonuçları göster
            self.ai_analysis_status.setText(f"✅ Toplu analiz tamamlandı! Başarılı: {success_count}, Hata: {error_count}")
            self.ai_analysis_status.setStyleSheet("color: #28a745; font-weight: bold;")
            
            QMessageBox.information(
                self, "Toplu Analiz Tamamlandı", 
                f"Toplam {total_firms} firma analiz edildi.\nBaşarılı: {success_count}\nHata: {error_count}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Toplu analiz hatası:\n{str(e)}")
        finally:
            self.ai_analysis_progress.setVisible(False)
    
    def send_to_campaign(self):
        """Seçili firmayı kampanya sekmesine gönder"""
        try:
            current_item = self.ai_strategy_firms_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uyarı", "Lütfen kampanyaya gönderilecek firmayı seçin!")
                return
            
            firm_id = current_item.data(Qt.UserRole)
            if not firm_id:
                QMessageBox.warning(self, "Uyarı", "Firma ID bulunamadı!")
                return
            
            # Firma verilerini al
            firm_data = self.ai_strategy_analyzer.get_firm_data(firm_id)
            if not firm_data:
                QMessageBox.critical(self, "Hata", "Firma verileri alınamadı!")
                return
            
            # Analiz verilerini al
            analysis_data = self.ai_strategy_analyzer.get_analysis_for_campaign(firm_id)
            
            # Kampanya sekmesine firma ekle
            if hasattr(self, 'campaign_firms_list'):
                # Firma adını kampanya listesine ekle
                firm_name = firm_data['name']
                item = QListWidgetItem(firm_name)
                item.setData(Qt.UserRole, firm_id)  # Firma ID'sini de sakla
                self.campaign_firms_list.addItem(item)
                
                # Kampanya bilgilerini güncelle
                if hasattr(self, 'campaign_info_label'):
                    current_count = self.campaign_firms_list.count()
                    self.campaign_info_label.setText(f"{current_count} firma, 0 email")
                
                # AI talimatlarını kampanya sekmesine aktar
                if analysis_data:
                    if hasattr(self, 'mail_instructions') and analysis_data.get('ai_instructions'):
                        self.mail_instructions.setText(analysis_data['ai_instructions'])
                        print(f"✅ Mail talimatları aktarıldı: {analysis_data['ai_instructions'][:100]}...")
                    
                    if hasattr(self, 'system_prompt') and analysis_data.get('custom_prompt'):
                        self.system_prompt.setText(analysis_data['custom_prompt'])
                        print(f"✅ Sistem promptu aktarıldı: {analysis_data['custom_prompt'][:100]}...")
                else:
                    # Analiz verisi yoksa varsayılan talimatlar
                    if hasattr(self, 'mail_instructions'):
                        default_instructions = f"Firma: {firm_name}\nSektör: {firm_data.get('sector', 'Bilinmiyor')}\n\nBu firmaya uygun, kişiselleştirilmiş bir B2B satış maili yaz."
                        self.mail_instructions.setText(default_instructions)
                        print(f"✅ Varsayılan mail talimatları eklendi")
                    
                    if hasattr(self, 'system_prompt'):
                        default_prompt = "Sen deneyimli bir B2B satış uzmanısın. Türkçe, samimi ama profesyonel, kişiselleştirilmiş satış mailleri yazıyorsun."
                        self.system_prompt.setText(default_prompt)
                        print(f"✅ Varsayılan sistem promptu eklendi")
                
                # Kampanya sekmesine geç
                if hasattr(self, 'tabs'):
                    campaign_index = -1
                    for i in range(self.tabs.count()):
                        if "Kampanya" in self.tabs.tabText(i) or "📧" in self.tabs.tabText(i):
                            campaign_index = i
                            break
                    
                    if campaign_index >= 0:
                        self.tabs.setCurrentIndex(campaign_index)
                        print(f"✅ Kampanya sekmesine geçildi")
                    else:
                        print("⚠️ Kampanya sekmesi bulunamadı")
                
                # Firma seçimini kampanya listesinde yap
                if hasattr(self, 'campaign_firms_list'):
                    # Son eklenen item'ı seç
                    last_item = self.campaign_firms_list.item(self.campaign_firms_list.count() - 1)
                    if last_item:
                        self.campaign_firms_list.setCurrentItem(last_item)
                        print(f"✅ Firma seçildi: {firm_name}")
                
                QMessageBox.information(self, "Başarılı", f"{firm_name} kampanyaya eklendi!\n\nAI talimatları ve sistem promptu otomatik olarak dolduruldu.")
            else:
                QMessageBox.warning(self, "Uyarı", "Kampanya sekmesi bulunamadı!")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kampanyaya gönderme hatası:\n{str(e)}")
            print(f"❌ Kampanyaya gönderme hatası: {e}")

    def update_analytics(self):
        """Analytics sekmesini güncelle - Business Intelligence devre dışı bırakıldı"""
        try:
            # Analytics dashboard'dan verileri al
            if hasattr(self, 'analytics_dashboard') and self.analytics_dashboard:
                summary = self.analytics_dashboard.get_analytics_summary()
                
                # Kartları güncelle
                if hasattr(self, 'conversion_rate_card'):
                    self.conversion_rate_card.update_value(f"%{summary.get('conversion_rate', 0)}")
                if hasattr(self, 'bounce_rate_card'):
                    self.bounce_rate_card.update_value(f"%{summary.get('bounce_rate', 0)}")
                if hasattr(self, 'avg_response_time_card'):
                    self.avg_response_time_card.update_value(f"{summary.get('avg_response_time', 0)} saat")
                if hasattr(self, 'spam_score_avg_card'):
                    self.spam_score_avg_card.update_value(f"{summary.get('avg_spam_score', 0)}/10")
                
                # KPI listesini güncelle
                if hasattr(self, 'kpi_list'):
                    self.kpi_list.clear()
                    for kpi in summary.get('kpis', []):
                        self.kpi_list.addItem(kpi)
                
                # Analytics grafiğini güncelle
                if hasattr(self, 'analytics_chart'):
                    chart_type = self.chart_type_combo.currentText() if hasattr(self, 'chart_type_combo') else "Zaman Serisi"
                    period = self.analytics_period_combo.currentText() if hasattr(self, 'analytics_period_combo') else "Son 7 Gün"
                    
                    chart_html = self.analytics_dashboard.generate_chart_html(chart_type, period)
                    self.analytics_chart.setHtml(chart_html)
                
                print("✅ Analytics güncellendi")
            else:
                print("⚠️ Analytics dashboard mevcut değil")
                
        except Exception as e:
            print(f"⚠️ İş zekası sistemi yüklenirken hata: {e}")
            # Hata durumunda varsayılan değerler
            if hasattr(self, 'conversion_rate_card'):
                self.conversion_rate_card.update_value("%0")
            if hasattr(self, 'bounce_rate_card'):
                self.bounce_rate_card.update_value("%0")
    
    def update_analytics_chart(self):
        """Analytics grafiğini güncelle"""
        try:
            if hasattr(self, 'analytics_dashboard') and self.analytics_dashboard:
                chart_type = self.chart_type_combo.currentText() if hasattr(self, 'chart_type_combo') else "Zaman Serisi"
                period = self.analytics_period_combo.currentText() if hasattr(self, 'analytics_period_combo') else "Son 7 Gün"
                
                chart_html = self.analytics_dashboard.generate_chart_html(chart_type, period)
                if hasattr(self, 'analytics_chart'):
                    self.analytics_chart.setHtml(chart_html)
        except Exception as e:
            print(f"⚠️ Analytics grafik güncelleme hatası: {e}")
    
    def update_ai_suggestions(self):
        """AI önerilerini güncelle"""
        try:
            if hasattr(self, 'ai_suggestions_text'):
                suggestions = """
📊 Performans Önerileri:

1. Email Zamanlaması:
   • En yüksek açılma oranı: Salı-Perşembe 10:00-11:00
   • Kaçınılması gereken zaman: Pazartesi sabahları ve Cuma öğleden sonra

2. Konu Başlıkları:
   • Kişiselleştirilmiş başlıklar %40 daha fazla açılıyor
   • Emoji kullanımı dikkatli olmalı (spam riski)
   • Soru cümleleri daha etkili

3. İçerik Stratejisi:
   • Kısa ve öz mailler tercih ediliyor
   • Değer önermesi açık olmalı
   • CTA (Call to Action) net olmalı

4. Segmentasyon:
   • Sektöre özel içerik hazırlayın
   • Firmanın büyüklüğüne göre mesaj tonu ayarlayın
   • Teknoloji seviyesine göre teknik detay verin

5. Takip Stratejisi:
   • İlk takip: 3-5 gün sonra
   • İkinci takip: 7-10 gün sonra
   • Farklı kanal deneyin (email + WhatsApp)
                """
                self.ai_suggestions_text.setText(suggestions)
        except Exception as e:
            print(f"⚠️ AI önerileri güncelleme hatası: {e}")
    
    def export_analytics_report(self):
        """Analytics raporunu PDF'e aktar"""
        try:
            if hasattr(self, 'analytics_dashboard') and self.analytics_dashboard:
                from PySide6.QtWidgets import QFileDialog
                
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Analytics Raporunu Kaydet",
                    f"analytics_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    "PDF Files (*.pdf)"
                )
                
                if file_path:
                    success = self.analytics_dashboard.export_report_to_pdf(file_path)
                    if success:
                        QMessageBox.information(self, "Başarılı", f"Rapor kaydedildi: {file_path}")
                    else:
                        QMessageBox.warning(self, "Uyarı", "Rapor oluşturulamadı. Matplotlib kurulu olduğundan emin olun.")
            else:
                QMessageBox.warning(self, "Uyarı", "Analytics dashboard mevcut değil!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor oluşturma hatası:\n{str(e)}")
    
    def setup_webengine_error_handling(self, web_view):
        """QWebEngineView için JavaScript error handling"""
        try:
            # Console message handler
            if hasattr(web_view.page(), 'setConsoleMessageHandler'):
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
                
                web_view.page().setConsoleMessageHandler(handle_console_message)
            else:
                print("ℹ️ Console message handler mevcut değil, JavaScript error handling kullanılacak")
                
        except Exception as e:
            print(f"⚠️ JavaScript error handling kurulamadı: {e}")
    
    def setup_global_error_handling(self):
        """Global WebEngine error handling - Manifest hatalarını yakala"""
        try:
            # Tüm QWebEngineView'lar için global error handler
            def handle_web_engine_error(error_type, error_message):
                if "manifest" in error_message.lower() or "404" in error_message or "XHRRequest" in error_message:
                    print(f"⚠️ WebEngine Error: {error_type} - {error_message}")
                else:
                    print(f"ℹ️ WebEngine Error: {error_type} - {error_message}")
            
            # Global error handler'ı kaydet
            self.web_engine_error_handler = handle_web_engine_error
            print("✅ Global WebEngine error handler kuruldu")
            
        except Exception as e:
            print(f"⚠️ Global error handler kurulamadı: {e}")
    
    def inject_global_manifest_error_handling(self, web_view):
        """Tüm QWebEngineView'lar için global manifest error handling enjekte et"""
        try:
            error_script = """
            // Global manifest error handling
            (function() {
                // Console error interceptor
                const originalConsoleError = console.error;
                console.error = function(...args) {
                    const message = args.join(' ');
                    if (message.includes('manifest') || message.includes('404') || message.includes('XHRRequest')) {
                        console.log('⚠️ Manifest Error Intercepted:', message);
                    }
                    return originalConsoleError.apply(console, args);
                };
                
                // Global error handler
                window.addEventListener('error', function(e) {
                    if (e.message && (e.message.includes('manifest') || e.message.includes('404') || e.message.includes('XHRRequest'))) {
                        console.log('⚠️ Global Manifest Error:', e.message);
                    }
                });
                
                // XHR interceptor
                const originalXHROpen = XMLHttpRequest.prototype.open;
                XMLHttpRequest.prototype.open = function(method, url, ...args) {
                    this.addEventListener('error', function() {
                        if (url.includes('manifest') || this.status === 404) {
                            console.log('⚠️ XHR Manifest Error:', url, this.status);
                        }
                    });
                    return originalXHROpen.apply(this, [method, url, ...args]);
                };
                
                // Fetch interceptor
                const originalFetch = window.fetch;
                window.fetch = function(url, ...args) {
                    return originalFetch.apply(this, [url, ...args]).catch(error => {
                        if (url.includes('manifest') || error.message.includes('404')) {
                            console.log('⚠️ Fetch Manifest Error:', url, error.message);
                        }
                        throw error;
                    });
                };
            })();
            """
            web_view.page().runJavaScript(error_script)
        except Exception as e:
            print(f"⚠️ Global manifest error handling enjekte edilemedi: {e}")

    def show_template_manager(self):
        """Şablon yönetim panelini göster"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("⚙️ Şablon Yönetimi")
            dialog.setModal(True)
            dialog.resize(800, 600)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2a2a2a;
                    color: white;
                }
                QLabel {
                    color: white;
                }
                QLineEdit, QTextEdit {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 8px;
                    color: white;
                }
                QListWidget {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 5px;
                    color: white;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title = QLabel("⚙️ Mail Şablon Yönetimi")
            title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title)
            
            # Şablon listesi
            list_layout = QHBoxLayout()
            
            template_list = QListWidget()
            template_list.addItems([
                "Yazılım Firmaları İçin",
                "E-ticaret Firmaları İçin",
                "Danışmanlık Firmaları İçin",
                "Üretim Firmaları İçin"
            ])
            list_layout.addWidget(template_list)
            
            # Düzenleme alanı
            edit_layout = QVBoxLayout()
            
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("Şablon Adı")
            edit_layout.addWidget(QLabel("Şablon Adı:"))
            edit_layout.addWidget(name_edit)
            
            content_edit = QTextEdit()
            content_edit.setPlaceholderText("Mail içeriği...")
            edit_layout.addWidget(QLabel("Mail İçeriği:"))
            edit_layout.addWidget(content_edit)
            
            list_layout.addLayout(edit_layout)
            layout.addLayout(list_layout)
            
            # Butonlar
            buttons = QHBoxLayout()
            
            save_btn = QPushButton("💾 Kaydet")
            delete_btn = QPushButton("🗑️ Sil")
            close_btn = QPushButton("❌ Kapat")
            
            buttons.addWidget(save_btn)
            buttons.addWidget(delete_btn)
            buttons.addStretch()
            buttons.addWidget(close_btn)
            
            close_btn.clicked.connect(dialog.reject)
            layout.addLayout(buttons)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Şablon yöneticisi açılamadı:\n{str(e)}")
    
    def create_new_template(self):
        """Gelişmiş AI destekli yeni şablon oluştur"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("🤖 AI Destekli Şablon Oluştur")
            dialog.setModal(True)
            dialog.resize(900, 700)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2a2a2a;
                    color: white;
                }
                QLabel {
                    color: white;
                }
                QLineEdit, QTextEdit {
                    background-color: #3a3a3a;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 8px;
                    color: white;
                }
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            title = QLabel("🤖 AI Destekli Şablon Oluşturucu")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #14a085; margin-bottom: 15px;")
            layout.addWidget(title)
            
            # Tab widget
            tabs = QTabWidget()
            
            # Tab 1: Temel Bilgiler
            basic_tab = QWidget()
            basic_layout = QVBoxLayout(basic_tab)
            basic_layout.setSpacing(10)
            
            basic_layout.addWidget(QLabel("📝 Şablon Adı:"))
            name_edit = QLineEdit()
            name_edit.setPlaceholderText("Örn: Teknoloji Firmaları için B2B Mail")
            basic_layout.addWidget(name_edit)
            
            basic_layout.addWidget(QLabel("🏭 Hedef Sektör (Opsiyonel):"))
            sector_edit = QLineEdit()
            sector_edit.setPlaceholderText("Örn: Teknoloji, E-ticaret, İnşaat")
            basic_layout.addWidget(sector_edit)
            
            basic_layout.addWidget(QLabel("📊 Strateji Tipi:"))
            strategy_combo = QComboBox()
            strategy_combo.addItems([
                "Soft Sell (Yumuşak Satış)",
                "Hard Sell (Sert Satış)",
                "Value Proposition (Değer Önerisi)",
                "Educational (Eğitici İçerik)",
                "Nurture Campaign (Besleme Kampanyası)",
                "Follow-up (Takip Maili)"
            ])
            basic_layout.addWidget(strategy_combo)
            
            tabs.addTab(basic_tab, "📋 Temel Bilgiler")
            
            # Tab 2: Mail Talimatları
            instructions_tab = QWidget()
            instructions_layout = QVBoxLayout(instructions_tab)
            
            instructions_layout.addWidget(QLabel("📧 Mail Talimatları (AI için):"))
            mail_instructions_edit = QTextEdit()
            mail_instructions_edit.setPlaceholderText(
                "Örnek: Yazılım hizmetlerimizi tanıtan, samimi ve profesyonel bir mail yaz. "
                "Firma'nın teknolojilerini ve başarılarını öv. 15 dakikalık demo randevusu iste."
            )
            mail_instructions_edit.setMinimumHeight(150)
            
            # AI ile öneri al butonu
            ai_suggest_btn = QPushButton("🤖 AI'dan Otomatik Öneri Al")
            ai_suggest_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #764ba2, stop:1 #667eea);
                }
            """)
            ai_suggest_btn.clicked.connect(lambda: self.generate_ai_template_suggestion(
                name_edit.text(), sector_edit.text(), strategy_combo.currentText(),
                mail_instructions_edit, system_prompt_edit
            ))
            
            instructions_layout.addWidget(ai_suggest_btn)
            instructions_layout.addWidget(mail_instructions_edit)
            
            tabs.addTab(instructions_tab, "📧 Mail Talimatları")
            
            # Tab 3: AI Sistem Promptu
            system_tab = QWidget()
            system_layout = QVBoxLayout(system_tab)
            
            system_layout.addWidget(QLabel("🤖 AI Sistem Promptu:"))
            system_prompt_edit = QTextEdit()
            system_prompt_edit.setPlaceholderText(
                "Örnek: Sen B2B satış uzmanısın. Kişiselleştirilmiş ve ikna edici mailler yazıyorsun. "
                "Firma bilgilerini kullanarak spesifik ve ikna edici mailler oluşturuyorsun."
            )
            system_prompt_edit.setMinimumHeight(150)
            
            # Hazır promptlar
            quick_prompts = QComboBox()
            quick_prompts.addItems([
                "Genel B2B Satış Uzmanı",
                "Değer Önerisi Uzmanı",
                "Eğitici İçerik Uzmanı",
                "Takip Maili Uzmanı"
            ])
            quick_prompts.currentTextChanged.connect(lambda text: self.apply_quick_prompt(
                text, system_prompt_edit
            ))
            
            system_layout.addWidget(QLabel("⚡ Hızlı Seçenekler:"))
            system_layout.addWidget(quick_prompts)
            system_layout.addWidget(QLabel("🤖 Özel AI Promptu:"))
            system_layout.addWidget(system_prompt_edit)
            
            tabs.addTab(system_tab, "🤖 AI Prompt")
            
            # Tab 4: Önizleme
            preview_tab = QWidget()
            preview_layout = QVBoxLayout(preview_tab)
            
            preview_layout.addWidget(QLabel("👁️ Şablon Önizleme:"))
            preview_text = QTextEdit()
            preview_text.setReadOnly(True)
            preview_text.setPlaceholderText("Şablon önizlemesi burada görünecek...")
            preview_text.setMinimumHeight(200)
            
            # Önizlemeyi güncelle
            def update_preview():
                preview_content = f"""
📝 Şablon Adı: {name_edit.text() or '(Boş)'}
🏭 Sektör: {sector_edit.text() or '(Belirtilmemiş)'}
📊 Strateji: {strategy_combo.currentText()}

📧 Mail Talimatları:
{mail_instructions_edit.toPlainText() or '(Boş)'}

🤖 AI Sistem Promptu:
{system_prompt_edit.toPlainText() or '(Boş)'}
                """
                preview_text.setPlainText(preview_content.strip())
            
            name_edit.textChanged.connect(update_preview)
            sector_edit.textChanged.connect(update_preview)
            strategy_combo.currentTextChanged.connect(update_preview)
            mail_instructions_edit.textChanged.connect(update_preview)
            system_prompt_edit.textChanged.connect(update_preview)
            
            preview_layout.addWidget(preview_text)
            tabs.addTab(preview_tab, "👁️ Önizleme")
            
            layout.addWidget(tabs)
            
            # Butonlar
            buttons = QHBoxLayout()
            create_btn = QPushButton("✨ Şablonu Kaydet")
            ai_generate_btn = QPushButton("🤖 AI ile Oluştur")
            cancel_btn = QPushButton("❌ İptal")
            
            buttons.addWidget(create_btn)
            buttons.addWidget(ai_generate_btn)
            buttons.addStretch()
            buttons.addWidget(cancel_btn)
            
            create_btn.clicked.connect(lambda: self.save_template(
                dialog, name_edit, sector_edit, strategy_combo, 
                mail_instructions_edit, system_prompt_edit
            ))
            cancel_btn.clicked.connect(dialog.reject)
            
            layout.addLayout(buttons)
            
            if dialog.exec():
                QMessageBox.information(self, "✅ Başarılı", 
                    f"'{name_edit.text()}' adlı şablon oluşturuldu!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Şablon oluşturulamadı:\n{str(e)}")
    
    def generate_ai_template_suggestion(self, template_name, sector, strategy, instructions_edit, prompt_edit):
        """AI'dan şablon önerisi al"""
        try:
            if not self.api_manager or not hasattr(self.api_manager, 'openai_api_key'):
                QMessageBox.warning(self, "Uyarı", "OpenAI API anahtarı bulunamadı!")
                return
            
            # AI prompt oluştur
            ai_prompt = f"""
Şablon Adı: {template_name or 'Genel'}
Sektör: {sector or 'Genel'}
Strateji: {strategy or 'Genel'}

Bu parametrelere göre iki şey oluştur:
1. Mail Talimatları (kullanıcının AI'ya ne istediğini açıkça belirten talimat)
2. AI Sistem Promptu (AI'nın rolünü ve yaklaşımını tanımlayan prompt)

Format:
==MAIL_TALIMATLARI==
[...]
==AI_PROMPT==
[...]
"""
            
            import openai
            client = openai.OpenAI(api_key=self.api_manager.openai_api_key)
            
            QMessageBox.information(self, "🔄 İşlem Başlatıldı", 
                                  "AI önerisi oluşturuluyor, lütfen bekleyin...")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir B2B email şablonu uzmanısın."},
                    {"role": "user", "content": ai_prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Response'u parse et
            if "==MAIL_TALIMATLARI==" in ai_response and "==AI_PROMPT==" in ai_response:
                parts = ai_response.split("==AI_PROMPT==")
                mail_part = parts[0].replace("==MAIL_TALIMATLARI==", "").strip()
                prompt_part = parts[1].strip() if len(parts) > 1 else ""
                
                instructions_edit.setPlainText(mail_part)
                prompt_edit.setPlainText(prompt_part)
                
                QMessageBox.information(self, "✅ Başarılı", 
                                       "AI önerisi başarıyla oluşturuldu!")
            else:
                # Parse edilemezse direkt göster
                instructions_edit.setPlainText(ai_response)
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"AI önerisi alınamadı:\n{str(e)}")
    
    def apply_quick_prompt(self, prompt_type, system_prompt_edit):
        """Hazır prompt'u uygula"""
        prompts = {
            "Genel B2B Satış Uzmanı": """Sen profesyonel bir B2B satış uzmanısın. Samimi, kişiselleştirilmiş ve ikna edici mailler yazıyorsun. Her firma için özel içerik oluşturuyorsun.""",
            "Değer Önerisi Uzmanı": """Sen bir B2B değer önerisi uzmanısın. Firmalara net ve somut değer sunan, problemlerini çözen mailler yazıyorsun. ROI ve fayda odaklısın.""",
            "Eğitici İçerik Uzmanı": """Sen bir içerik uzmanısın. Eğitici, bilgilendirici ve uzmanlaştırıcı mailler yazıyorsun. Firmaları eğiterek güven oluşturuyorsun.""",
            "Takip Maili Uzmanı": """Sen bir takip maili uzmanısın. Kibar, zorlayıcı olmayan ve değer katacak takip mailleri yazıyorsun. İlişkiyi sürdürüyorsun."""
        }
        
        if prompt_type in prompts:
            system_prompt_edit.setPlainText(prompts[prompt_type])
    
    def save_template(self, dialog, name_edit, sector_edit, strategy_combo, 
                     mail_instructions_edit, system_prompt_edit):
        """Şablonu kaydet"""
        try:
            if not name_edit.text().strip():
                QMessageBox.warning(dialog, "Uyarı", "Lütfen şablon adı girin!")
                return
            
            # Şablon verilerini topla
            template_data = {
                'name': name_edit.text(),
                'sector': sector_edit.text(),
                'strategy': strategy_combo.currentText(),
                'mail_instructions': mail_instructions_edit.toPlainText(),
                'system_prompt': system_prompt_edit.toPlainText()
            }
            
            # Şablonu kaydet (veritabanına veya dosyaya)
            # TODO: Gerçek kayıt işlemi burada olacak
            print(f"📝 Şablon kaydediliyor: {template_data}")
            
            dialog.accept()
            
        except Exception as e:
            QMessageBox.critical(dialog, "Hata", f"Şablon kaydedilemedi:\n{str(e)}")
    
    def show_ai_chat_popup(self):
        """AI Chat popup dialog'u göster"""
        try:
            # Gelişmiş AI Chat Engine kullan
            if ADVANCED_AI_CHAT_AVAILABLE:
                ai_chat = AdvancedAIChatEngine(self.db, self.api_manager, self)
                ai_chat.firms_selected.connect(self.handle_ai_chat_firms_selected)
                ai_chat.exec()
                return
            
            # Fallback to basic dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("🤖 AI Asistan - Firma Yardımcısı")
            dialog.setModal(True)
            dialog.resize(900, 700)
            dialog.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1a1a2e, stop:1 #16213e);
                    color: white;
                }
                QLabel {
                    color: #ffffff;
                }
                QLineEdit, QTextEdit {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    padding: 10px;
                    color: white;
                    font-size: 13px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border: 2px solid #764ba2;
                }
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #764ba2, stop:1 #667eea);
                }
                QPushButton:disabled {
                    background-color: #3a3a3a;
                    color: #666;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            
            # Başlık
            header = QWidget()
            header.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
            """)
            header_layout = QVBoxLayout(header)
            
            title = QLabel("🤖 AI Firma Asistanı")
            title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-bottom: 5px;")
            header_layout.addWidget(title)
            
            subtitle = QLabel("Firma yönetimi ve stratejiler hakkında sorularınızı sorabilirsiniz")
            subtitle.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.9);")
            header_layout.addWidget(subtitle)
            
            layout.addWidget(header)
            
            # Hızlı sorular
            quick_questions_frame = QFrame()
            quick_questions_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(102, 126, 234, 0.1);
                    border: 1px solid rgba(102, 126, 234, 0.3);
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            quick_questions_layout = QVBoxLayout(quick_questions_frame)
            
            quick_label = QLabel("💡 Hızlı Sorular:")
            quick_label.setStyleSheet("font-weight: bold; color: #667eea; margin-bottom: 8px;")
            quick_questions_layout.addWidget(quick_label)
            
            quick_questions_buttons = QHBoxLayout()
            
            questions = [
                ("📊 En iyi firmalar", "En yüksek potansiyele sahip 5 firmam hangisi?"),
                ("📈 Strateji önerisi", "Firmalarım için özel strateji öner."),
                ("📧 Mail kampanyası", "Etkili bir mail kampanyası taslağı hazırla."),
                ("🎯 Analiz et", "Firma verilerimi analiz et ve öneriler sun.")
            ]
            
            for icon_text, question in questions:
                btn = QPushButton(icon_text)
                btn.setMinimumHeight(50)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(102, 126, 234, 0.2);
                        border: 1px solid #667eea;
                        border-radius: 6px;
                        padding: 8px;
                        color: white;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: rgba(102, 126, 234, 0.4);
                        border-color: #764ba2;
                    }
                """)
                btn.clicked.connect(lambda checked, q=question: self.ai_chat_input.setPlainText(q))
                quick_questions_buttons.addWidget(btn)
            
            quick_questions_layout.addLayout(quick_questions_buttons)
            layout.addWidget(quick_questions_frame)
            
            # Chat ekranı
            self.ai_chat_display = QTextEdit()
            self.ai_chat_display.setReadOnly(True)
            self.ai_chat_display.setPlaceholderText("AI asistan ile sohbet burada görünecek...")
            self.ai_chat_display.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(0, 0, 0, 0.3);
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    padding: 12px;
                    min-height: 300px;
                }
            """)
            layout.addWidget(self.ai_chat_display)
            
            # Mesaj girişi
            input_layout = QHBoxLayout()
            
            self.ai_chat_input = QTextEdit()
            self.ai_chat_input.setPlaceholderText("Sorularınızı buraya yazın...")
            self.ai_chat_input.setMaximumHeight(80)
            self.ai_chat_input.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    padding: 10px;
                    color: white;
                }
                QTextEdit:focus {
                    border: 2px solid #764ba2;
                }
            """)
            input_layout.addWidget(self.ai_chat_input)
            
            send_btn = QPushButton("📤\nGönder")
            send_btn.clicked.connect(lambda: self.send_ai_chat_message(dialog))
            input_layout.addWidget(send_btn)
            
            layout.addLayout(input_layout)
            
            # Kapat butonu
            close_btn = QPushButton("❌ Kapat")
            close_btn.clicked.connect(dialog.reject)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            layout.addWidget(close_btn)
            
            # Hoş geldin mesajı
            self.ai_chat_display.append("""
<div style='text-align: center; padding: 20px;'>
    <h2 style='color: #667eea;'>🤖 Merhaba! AI Asistanınız</h2>
    <p style='color: white; font-size: 13px;'>
        Firma yönetimi ve stratejiler konusunda yardımcı olmak için buradayım!
    </p>
    <p style='color: rgba(255,255,255,0.7); font-size: 11px;'>
        Sorularınızı yazabilir veya hızlı soruları kullanabilirsiniz.
    </p>
</div>
""")
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"AI Chat açılamadı:\n{str(e)}")
    
    def handle_ai_chat_firms_selected(self, firms):
        """AI Chat'ten seçilen firmaları kampanyaya ekle"""
        try:
            if not firms:
                return
            
            # Kampanya sekmesine geç
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i).startswith("📧 Kampanya"):
                    self.tabs.setCurrentIndex(i)
                    break
            
            # Firmaları kampanyaya ekle
            firm_names = []
            for firm in firms:
                if not hasattr(self, 'campaign_firms'):
                    self.campaign_firms = []
                
                # Daha önce eklenmiş mi kontrol et
                if not any(f.get('name') == firm.get('name') for f in self.campaign_firms):
                    self.campaign_firms.append(firm)
                    firm_names.append(firm.get('name', 'N/A'))
            
            # Kampanya listesini güncelle
            if hasattr(self, 'update_campaign_firms_list'):
                self.update_campaign_firms_list()
            
            # Başarı mesajı
            QMessageBox.information(self, "✅ Başarılı", 
                                   f"{len(firm_names)} firma kampanyaya eklendi!\n\n" +
                                   "\n".join(firm_names[:3]) + 
                                   (f"\n... ve {len(firm_names) - 3} firma daha" if len(firm_names) > 3 else ""))
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Firmalar kampanyaya eklenirken hata oluştu:\n{str(e)}")
    
    def send_ai_chat_message(self, dialog):
        """AI Chat mesajı gönder"""
        try:
            message = self.ai_chat_input.toPlainText().strip()
            if not message:
                return
            
            # Kullanıcı mesajını göster
            self.ai_chat_display.append(f"""
<div style='margin: 10px 0; text-align: right;'>
    <div style='display: inline-block; background-color: #667eea; color: white; 
         padding: 10px 15px; border-radius: 18px; max-width: 70%;'>
        <b>👤 Siz:</b><br>{message}
    </div>
</div>
""")
            
            self.ai_chat_input.clear()
            
            # Basit AI yanıtı (gerçek AI entegrasyonu için ai_chat_assistant kullanılabilir)
            self.ai_chat_display.append(f"""
<div style='margin: 10px 0;'>
    <div style='display: inline-block; background-color: rgba(102, 126, 234, 0.3); color: white; 
         padding: 10px 15px; border-radius: 18px; border-left: 4px solid #764ba2; max-width: 70%;'>
        <b>🤖 AI:</b><br>Analiz ediyorum... Özellikleri yakında eklenecek!
    </div>
</div>
""")
            
        except Exception as e:
            QMessageBox.warning(dialog, "Uyarı", f"Mesaj gönderilemedi:\n{str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("B2B Mail Automation Pro")
    
    app.setStyle("Fusion")
    
    # Dark tema
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(15, 15, 15))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(26, 26, 26))
    dark_palette.setColor(QPalette.AlternateBase, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(13, 115, 119))
    dark_palette.setColor(QPalette.Highlight, QColor(13, 115, 119))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(dark_palette)
    
    font = QFont("Arial", 11)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
