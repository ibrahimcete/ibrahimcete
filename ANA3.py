# -*- coding: utf-8 -*-

import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QFrame, QMessageBox,
    QProgressBar, QComboBox, QSplitter, QTableWidget, QTableWidgetItem,
    QToolBar, QSizePolicy, QGraphicsDropShadowEffect, QGridLayout, QScrollArea,
    QTabWidget, QSplashScreen, QSlider
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QObject, QPropertyAnimation, QEasingCurve, QTimer, QSize, QPointF
from PySide6.QtGui import QPalette, QColor, QFont, QPainter, QLinearGradient, QPixmap, QRadialGradient, QKeySequence, QShortcut
try:
    import speech_recognition as sr  # Opsiyonel: tek seferlik kayıt için
    _SR_AVAILABLE = True
except Exception:
    _SR_AVAILABLE = False
try:
    from voice_assistant import VoiceAssistantGUI  # Sürekli dinleme ve TTS
    _VOICE_GUI_AVAILABLE = True
except Exception:
    _VOICE_GUI_AVAILABLE = False

# TTS fallback için pyttsx3
try:
    import pyttsx3
    TTS_PYTHON_AVAILABLE = True
except ImportError:
    TTS_PYTHON_AVAILABLE = False
    pyttsx3 = None

from automation_engine import AutomationEngine
from monitoring_error_handler import logger
from datetime import datetime
import time

# Opsiyonel ana sistem bileşenleri (main.py'deki mimariye yakın)
try:
    from database import Database
    DATABASE_AVAILABLE = True
except Exception:
    Database = None
    DATABASE_AVAILABLE = False

try:
    from api_manager import APIManager
    API_MANAGER_AVAILABLE = True
except Exception:
    APIManager = None
    API_MANAGER_AVAILABLE = False

try:
    from analytics_dashboard import AnalyticsDashboard
    ANALYTICS_AVAILABLE = True
except Exception:
    AnalyticsDashboard = None
    ANALYTICS_AVAILABLE = False

try:
    from automation_builder import AutomationBuilder
    AUTOMATION_AVAILABLE = True
except Exception:
    AutomationBuilder = None
    AUTOMATION_AVAILABLE = False

try:
    from tracking_gui_integration import get_tracking_gui_manager
    TRACKING_GUI_AVAILABLE = True
except Exception:
    get_tracking_gui_manager = None
    TRACKING_GUI_AVAILABLE = False

# E-posta yöneticisi (opsiyonel)
try:
    from email_manager import EmailManager
    EMAIL_AVAILABLE = True
except Exception:
    EmailManager = None
    EMAIL_AVAILABLE = False

# Try to import main2.py managers
try:
    import sys
    sys.path.insert(0, '')
    
    # Import main2 managers if available
    try:
        from main2 import GPTManager, VapiManager, WhatsAppAutoSender
        MAIN2_MANAGERS_AVAILABLE = True
    except:
        # Fallback: Try to import as module directly
        import importlib.util
        spec = importlib.util.spec_from_file_location("main2", "main2.py")
        if spec and spec.loader:
            main2_module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(main2_module)
                GPTManager = getattr(main2_module, 'GPTManager', None)
                VapiManager = getattr(main2_module, 'VapiManager', None)
                WhatsAppAutoSender = getattr(main2_module, 'WhatsAppAutoSender', None)
                MAIN2_MANAGERS_AVAILABLE = True
            except:
                MAIN2_MANAGERS_AVAILABLE = False
        else:
            MAIN2_MANAGERS_AVAILABLE = False
except Exception as e:
    print(f"Main2 modülleri yüklenemedi: {e}")
    MAIN2_MANAGERS_AVAILABLE = False
    GPTManager = None
    VapiManager = None
    WhatsAppAutoSender = None

# GUI için geri bildirim sinyali
class FeedbackSignal(QObject):
    message_received = Signal(str)

# Özel Widget'lar - Modern Görünüm için
class StatCard(QFrame):
    """İstatistik kartları için özel widget"""
    def __init__(self, title, value, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.color = color
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: white; font-size: 12px; font-weight: normal;")
        
        # Değer
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: white; font-size: 32px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
        # Gölge efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {color};
                border-radius: 12px;
            }}
        """)
    
    def update_value(self, value):
        self.value_label.setText(str(value))

class ModernButton(QPushButton):
    """Modern buton tasarımı"""
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.base_color = color
        self.setMinimumHeight(45)
        
        # Gölge efekti
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

class ModernSplashScreen(QSplashScreen):
    """Gelişmiş animasyonlu splash ekranı"""
    def __init__(self):
        # Splash pixmap oluştur
        splash_pix = QPixmap(700, 400)
        splash_pix.fill(Qt.transparent)
        super().__init__(splash_pix, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        self.progress = 0
        self.setWindowOpacity(0.0)
        
        # Fade-in animasyonu
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(800)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Progress timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        
    def start_animation(self):
        """Animasyonu başlat"""
        self.fade_anim.start()
        self.timer.start(30)  # 30ms'de bir güncelle
        
    def update_progress(self):
        """Progress'i güncelle"""
        self.progress += 2
        if self.progress > 100:
            self.progress = 100
            self.timer.stop()
        self.repaint()
        
    def drawContents(self, painter):
        """Splash içeriğini çiz"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Arka plan gradient
        gradient = QRadialGradient(QPointF(350, 200), 400)
        gradient.setColorAt(0.0, QColor(88, 88, 214, 255))
        gradient.setColorAt(0.3, QColor(48, 162, 76, 240))
        gradient.setColorAt(0.6, QColor(202, 113, 55, 230))
        gradient.setColorAt(1.0, QColor(15, 15, 30, 250))
        painter.fillRect(0, 0, 700, 400, gradient)
        
        # Ana başlık
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 28, QFont.Bold))
        painter.drawText(0, 80, 700, 60, Qt.AlignCenter, "🚀 B2B Otomasyon Motoru")
        
        # Alt başlık
        painter.setFont(QFont("Segoe UI", 16))
        painter.setPen(QColor(230, 230, 230))
        painter.drawText(0, 140, 700, 30, Qt.AlignCenter, "v3.0 Gelişmiş Kontrol Paneli")
        
        # Progress bar arka plan
        bar_x, bar_y = 150, 250
        bar_width, bar_height = 400, 30
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(30, 30, 50, 180))
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 15, 15)
        
        # Progress bar dolgu
        if self.progress > 0:
            progress_width = int((bar_width - 4) * (self.progress / 100))
            grad = QLinearGradient(bar_x, bar_y, bar_x + progress_width, bar_y)
            grad.setColorAt(0.0, QColor(88, 88, 214))
            grad.setColorAt(0.5, QColor(48, 162, 76))
            grad.setColorAt(1.0, QColor(202, 113, 55))
            painter.setBrush(grad)
            painter.drawRoundedRect(bar_x + 2, bar_y + 2, progress_width, bar_height - 4, 13, 13)
        
        # Progress text
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
        painter.drawText(bar_x, bar_y, bar_width, bar_height, Qt.AlignCenter, f"%{self.progress}")
        
        # Durum mesajı
        status_messages = [
            "Modüller yükleniyor...",
            "Motor başlatılıyor...",
            "NLP sistemi hazırlanıyor...",
            "Veritabanı bağlantısı kuruluyor...",
            "Son kontroller yapılıyor...",
            "Hazır!"
        ]
        msg_index = min(int(self.progress / 20), len(status_messages) - 1)
        painter.setFont(QFont("Segoe UI", 12))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(0, 300, 700, 30, Qt.AlignCenter, status_messages[msg_index])
        
        # Alt bilgi
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(0, 360, 700, 20, Qt.AlignCenter, "© 2024 - Tüm hakları saklıdır")

class AutomationGUI(QMainWindow):
    """
    Otomasyon motoru için PySide6 tabanlı gelişmiş kullanıcı arayüzü.
    Modern dashboard tasarımı ile 7/24 çalışma için optimize edilmiş.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 B2B Otomasyon Motoru v3.0 - Kontrol Paneli")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        self.feedback_signal = FeedbackSignal()
        self.feedback_signal.message_received.connect(self.update_log_display)

        # Log arama için tampon
        self.log_buffer = []  # ham metin satırları
        self.log_filter_text = ""

        # İstatistik kartları için değişkenler
        self.stats = {
            'firms_found': 0,
            'firms_analyzed': 0,
            'emails_sent': 0,
            'workflows_completed': 0
        }

        # Main2.py yöneticilerini çok erken başlat (attribute errors'ı önlemek için)
        self.gpt_manager = None
        self.vapi_manager = None
        self.whatsapp_auto_sender = None
        self.ai_memory = None
        self.user_id = "default_user"
        self._chat_context = []  # (role, content) geçmişi
        self.learning_enabled = False
        self.last_assistant_reply = ""
        self.persona = "professional"  # professional | friendly | concise

        # Ana sistem bileşenleri
        self.db = None
        self.api_manager = None
        self.analytics_dashboard = None
        self.automation_builder = None
        self.tracking_gui_manager = None

        # Ses özelliklerini UI'dan önce ayarla (Ayarlar sekmesi ihtiyaç duyar)
        self.voice_gui = None
        self.voice_listening = False
        self.voice_tts_enabled = True

        self.initUI()
        self.apply_modern_styles()
        self.setup_menu()

        # Sesli Asistan Entegrasyonu
        self.voice_gui = None
        self.voice_listening = False
        self.voice_tts_enabled = True
        if _VOICE_GUI_AVAILABLE:
            try:
                self.voice_gui = VoiceAssistantGUI(self)
            except Exception:
                self.voice_gui = None

        # Otomasyon motorunu başlat
        try:
            self.engine = AutomationEngine(feedback_callback=self.emit_feedback)
            if not self.engine.is_ready:
                logger.error("Motor başlatılamadı!")
                self.update_log_display("❌ Motor başlatılamadı!")
        except Exception as e:
            logger.critical(f"Motor oluşturma hatası: {e}", exc_info=True)
            self.update_log_display(f"❌ Motor hatası: {e}")
        
        # Ana sistem bileşenlerini başlat (main.py ile uyumlu)
        try:
            if DATABASE_AVAILABLE:
                self.db = Database()
                self.update_log_display("✅ Database başlatıldı")
        except Exception as e:
            self.db = None
            self.update_log_display(f"⚠️ Database başlatılamadı: {e}")

        try:
            if API_MANAGER_AVAILABLE:
                self.api_manager = APIManager(db=self.db)
                self.update_log_display("✅ API Manager başlatıldı")
        except Exception as e:
            self.api_manager = None
            self.update_log_display(f"⚠️ API Manager başlatılamadı: {e}")

        try:
            if ANALYTICS_AVAILABLE and self.db:
                self.analytics_dashboard = AnalyticsDashboard(self.db)
                self.update_log_display("✅ Analytics Dashboard başlatıldı")
        except Exception as e:
            self.analytics_dashboard = None
            self.update_log_display(f"⚠️ Analytics Dashboard başlatılamadı: {e}")

        try:
            if AUTOMATION_AVAILABLE:
                self.automation_builder = AutomationBuilder()
                self.update_log_display("✅ Automation Builder başlatıldı")
        except Exception as e:
            self.automation_builder = None
            self.update_log_display(f"⚠️ Automation Builder başlatılamadı: {e}")

        try:
            if TRACKING_GUI_AVAILABLE:
                self.tracking_gui_manager = get_tracking_gui_manager()
                if self.tracking_gui_manager:
                    # Varsayılan bir server URL set edilebilir
                    try:
                        self.tracking_gui_manager.update_server_url("https://web-production-24136.up.railway.app")
                    except Exception:
                        pass
                self.update_log_display("✅ Tracking GUI Manager başlatıldı")
        except Exception as e:
            self.tracking_gui_manager = None
            self.update_log_display(f"⚠️ Tracking GUI Manager başlatılamadı: {e}")

        # Main2.py managers'ı başlat
        if MAIN2_MANAGERS_AVAILABLE:
            try:
                if GPTManager:
                    self.gpt_manager = GPTManager()
                    self.update_log_display("✅ GPT Manager yüklendi")
                
                if VapiManager:
                    self.vapi_manager = VapiManager()
                    self.update_log_display("✅ Vapi Manager yüklendi")
                
                # Load main2 config
                self.load_main2_config()
                # AI Memory Personalization isteğe bağlı
                try:
                    from ai_memory_personalization import AIMemoryPersonalization
                    api_key = None
                    try:
                        if hasattr(self, 'config') and isinstance(self.config, dict):
                            api_key = self.config.get('openai_api_key')
                            if self.config.get('user_id'):
                                self.user_id = str(self.config.get('user_id'))
                    except Exception:
                        api_key = None
                    cfg = {'openai_api_key': api_key} if api_key else {}
                    self.ai_memory = AIMemoryPersonalization(config=cfg)
                    self.update_log_display("✅ AI Memory sistemi yüklendi")
                except Exception as mem_e:
                    self.ai_memory = None
                    logger.warning(f"AI Memory sistemi başlatılamadı: {mem_e}")
                
            except Exception as e:
                logger.warning(f"Main2 managers başlatılamadı: {e}")
                self.update_log_display(f"⚠️ Main2 managers başlatılamadı: {e}")
        else:
            self.update_log_display("ℹ️ Main2 özellikleri kullanılamıyor")

        # Havalı fade + scale (büyüme) animasyonu
        try:
            self.setWindowOpacity(0.0)
            self.resize(0, 0)

            # Fade efekti
            self._fade_anim = QPropertyAnimation(self, b"windowOpacity")
            self._fade_anim.setDuration(1000)
            self._fade_anim.setStartValue(0.0)
            self._fade_anim.setEndValue(1.0)
            self._fade_anim.setEasingCurve(QEasingCurve.OutCubic)

            # Boyut animasyonu
            start_size = QSize(int(self.width() * 0.85), int(self.height() * 0.85))
            end_size = self.size()
            self._size_anim = QPropertyAnimation(self, b"size")
            self._size_anim.setDuration(1000)
            self._size_anim.setStartValue(start_size)
            self._size_anim.setEndValue(end_size)
            self._size_anim.setEasingCurve(QEasingCurve.OutBack)

            # Animasyonları birlikte oynat (PySide6 ile tür uyumlu)
            from PySide6.QtCore import QParallelAnimationGroup
            self._anim_group = QParallelAnimationGroup()
            self._anim_group.addAnimation(self._fade_anim)
            self._anim_group.addAnimation(self._size_anim)
            self._anim_group.start(QPropertyAnimation.DeleteWhenStopped)
        except Exception as e:
            print("Animasyon hatası:", e)
            self.setWindowOpacity(1.0)


    def initUI(self):
        """Kullanıcı arayüzünü oluşturur - Modern Dashboard Tasarımı"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Üst araç çubuğu
        self.setup_modern_toolbar()

        # Sekmeli yapı: Dashboard + Chat Asistanı
        tabs = QTabWidget()
        tabs.setObjectName("mainTabs")
        tabs.setStyleSheet("QTabWidget::pane{ border: 0px; } QTabBar::tab { padding: 10px 16px; }")

        dashboard_widget = QWidget()
        dashboard_layout = QGridLayout(dashboard_widget)
        dashboard_layout.setSpacing(15)

        # SOL/ORTA/SAĞ paneller
        left_panel = self.create_left_panel()
        center_panel = self.create_center_panel()
        right_panel = self.create_right_panel()
        dashboard_layout.addWidget(left_panel, 0, 0, 2, 1)
        dashboard_layout.addWidget(center_panel, 0, 1, 2, 1)
        dashboard_layout.addWidget(right_panel, 0, 2, 2, 1)
        dashboard_layout.setColumnStretch(0, 2)
        dashboard_layout.setColumnStretch(1, 3)
        dashboard_layout.setColumnStretch(2, 2)

        tabs.addTab(dashboard_widget, "📊 Dashboard")

        chat_widget = self.create_chat_assistant_panel()
        tabs.addTab(chat_widget, "🤖 Chat Asistanı")
        
        # Ana Sistem tabı (main.py bileşenleri)
        core_widget = self.create_core_system_panel()
        tabs.addTab(core_widget, "🧩 Ana Sistem")
        
        # Main2 features tab
        if MAIN2_MANAGERS_AVAILABLE:
            main2_widget = self.create_main2_features_panel()
            tabs.addTab(main2_widget, "🔧 Main2 Özellikleri")
        
        # AI NLP tab
        ai_nlp_widget = self.create_ai_nlp_panel()
        tabs.addTab(ai_nlp_widget, "🧠 AI NLP")

        # Ayarlar tabı
        settings_widget = self.create_settings_panel()
        tabs.addTab(settings_widget, "⚙️ Ayarlar")

        # Tanılama (Diagnostics) tabı
        diag_widget = self.create_diagnostics_panel()
        tabs.addTab(diag_widget, "🩺 Tanılama")

        main_layout.addWidget(tabs)

        # Alt durum çubuğu
        self.create_status_bar()
        
        # Otomatik güncelleme timer'ları
        self.status_timer = self.startTimer(5000)  # 5 saniye
        self.stats_timer = self.startTimer(2000)   # 2 saniye - istatistikler için

    def create_left_panel(self):
        """Sol panel - İstatistikler ve Hızlı Komutlar"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Başlık
        header = QLabel("📊 KONTROL PANELİ")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(header)

        # İstatistik Kartları
        stats_container = QWidget()
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(12)

        self.stat_cards = {
            'found': StatCard("🔍 Bulunan Firma", "0", "#5858D6"),    # Mor
            'analyzed': StatCard("📊 Analiz Edilen", "0", "#30A24C"), # Yeşil
            'sent': StatCard("📧 Gönderilen Email", "0", "#CA7137"),  # Turuncu
            'completed': StatCard("✅ Tamamlanan İş", "0", "#C43D4B") # Kırmızı
        }

        for card in self.stat_cards.values():
            stats_layout.addWidget(card)

        layout.addWidget(stats_container)

        # Hızlı Komut Bölümü
        quick_header = QLabel("⚡ HIZLI KOMUTLAR")
        quick_header.setStyleSheet("font-size: 14px; font-weight: bold; color: white; padding: 10px 0;")
        layout.addWidget(quick_header)

        # Hızlı komut butonları
        quick_buttons = [
            ("🏢 Kayseri Mobilya", "#5858D6", 
             "Kayseri'deki mobilya firmalarını bul, analiz et ve 'Yaz Tanıtımı' kampanyasını gönder"),
            ("💻 Ankara Yazılım", "#30A24C", 
             "Ankara'daki yazılım firmalarını bul ve 'Yeni Teklif' kampanyasını gönder"),
            ("🏭 İstanbul İmalat", "#CA7137", 
             "İstanbul'daki imalat firmalarını bul ve analiz et"),
        ]

        for text, color, command in quick_buttons:
            btn = ModernButton(text, color)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 13px;
                    font-weight: bold;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {self._lighten_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self._darken_color(color)};
                }}
            """)
            btn.clicked.connect(lambda checked, cmd=command: self._quick_command(cmd))
            layout.addWidget(btn)

        layout.addStretch()
        return panel

    def create_diagnostics_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        title = QLabel("🩺 Sistem Tanılama ve Testler")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(title)

        grid = QGridLayout()
        row = 0
        # Çevre ve modüller
        items = [
            ("Database", lambda: bool(self.db)),
            ("APIManager", lambda: bool(self.api_manager)),
            ("AnalyticsDashboard", lambda: bool(self.analytics_dashboard)),
            ("AutomationBuilder", lambda: bool(self.automation_builder)),
            ("Tracking GUI", lambda: bool(self.tracking_gui_manager)),
            ("GPTManager", lambda: bool(self.gpt_manager and getattr(self.gpt_manager, 'client', None))),
            ("VapiManager", lambda: bool(self.vapi_manager)),
            ("WhatsAppAutoSender", lambda: bool(self.whatsapp_auto_sender)),
        ]
        for name, fn in items:
            label = QLabel(name)
            status = QLabel("Hazır" if fn() else "YOK")
            status.setStyleSheet("color: #30A24C;" if fn() else "color: #C43D4B;")
            grid.addWidget(label, row, 0)
            grid.addWidget(status, row, 1)
            row += 1
        layout.addLayout(grid)

        # Toplu test düğmesi
        run_all = QPushButton("Tüm Testleri Çalıştır")
        def _run_all():
            msgs = []
            try:
                self._test_openai_api(); msgs.append("OpenAI OK")
            except Exception as e:
                msgs.append(f"OpenAI FAIL: {e}")
            try:
                self._test_vapi_api(); msgs.append("Vapi OK")
            except Exception as e:
                msgs.append(f"Vapi FAIL: {e}")
            try:
                self._test_email_api(); msgs.append("Email OK")
            except Exception as e:
                msgs.append(f"Email FAIL: {e}")
            self.chat_history.append("🩺 " + "; ".join(msgs))
        run_all.clicked.connect(_run_all)
        layout.addWidget(run_all)

        layout.addStretch()
        return panel

    def create_center_panel(self):
        """Orta panel - Komut girişi ve Log görüntüleme"""
        panel = QFrame()
        panel.setObjectName("centerPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Komut Girişi Bölümü
        command_section = QFrame()
        command_section.setObjectName("commandSection")
        command_layout = QVBoxLayout(command_section)
        command_layout.setSpacing(10)

        cmd_header = QLabel("🎯 KOMUT MERKEZİ")
        cmd_header.setStyleSheet("font-size: 16px; font-weight: bold; color: white; padding: 10px;")
        command_layout.addWidget(cmd_header)

        # Komut geçmişi ve giriş
        input_container = QHBoxLayout()
        
        self.command_history = QComboBox()
        self.command_history.setEditable(False)
        self.command_history.setMinimumWidth(200)
        self.command_history.setPlaceholderText("📋 Geçmiş")
        self.command_history.activated.connect(self._pick_history_command)
        input_container.addWidget(self.command_history)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("💬 Komutunuzu buraya yazın (örn: Kayseri'deki mobilya firmalarını bul)...")
        self.command_input.returnPressed.connect(self.send_command)
        input_container.addWidget(self.command_input, 3)

        self.send_button = ModernButton("🚀 Gönder", "#5858D6")
        self.send_button.clicked.connect(self.send_command)
        input_container.addWidget(self.send_button)

        command_layout.addLayout(input_container)

        # Kontrol Butonları
        control_container = QHBoxLayout()
        control_container.setSpacing(10)

        self.pause_button = ModernButton("⏸️ Duraklat", "#CA7137")
        self.pause_button.clicked.connect(self.pause_workflow)
        self.pause_button.setEnabled(False)
        control_container.addWidget(self.pause_button)

        self.resume_button = ModernButton("▶️ Devam", "#30A24C")
        self.resume_button.clicked.connect(self.resume_workflow)
        self.resume_button.setEnabled(False)
        control_container.addWidget(self.resume_button)

        self.stop_button = ModernButton("⏹️ Durdur", "#C43D4B")
        self.stop_button.clicked.connect(self.stop_workflow)
        self.stop_button.setEnabled(False)
        control_container.addWidget(self.stop_button)

        command_layout.addLayout(control_container)
        layout.addWidget(command_section)

        # Log Görüntüleme Bölümü
        log_section = QFrame()
        log_section.setObjectName("logSection")
        log_layout = QVBoxLayout(log_section)
        log_layout.setSpacing(10)

        log_header_container = QHBoxLayout()
        log_header = QLabel("📝 MOTOR LOGLARI")
        log_header.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        log_header_container.addWidget(log_header)

        # Log arama alanı
        self.log_search = QLineEdit()
        self.log_search.setPlaceholderText("🔎 Loglarda ara...")
        self.log_search.textChanged.connect(self.filter_logs)
        self.log_search.setMaximumWidth(250)
        log_header_container.addWidget(self.log_search)

        # Log kontrol butonları
        self.clear_logs_btn = QPushButton("🗑️ Temizle")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.clear_logs_btn.setMaximumWidth(100)
        log_header_container.addWidget(self.clear_logs_btn)

        self.copy_logs_btn = QPushButton("📋 Kopyala")
        self.copy_logs_btn.clicked.connect(self.copy_logs)
        self.copy_logs_btn.setMaximumWidth(100)
        log_header_container.addWidget(self.copy_logs_btn)

        self.reset_filter_btn = QPushButton("✖️ Filtreyi Temizle")
        self.reset_filter_btn.clicked.connect(lambda: self.log_search.setText(""))
        self.reset_filter_btn.setMaximumWidth(140)
        log_header_container.addWidget(self.reset_filter_btn)

        log_layout.addLayout(log_header_container)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        log_layout.addWidget(self.log_display)

        layout.addWidget(log_section, 2)

        # Hoş geldin mesajı
        self.log_display.append("="*80)
        self.log_display.append(" 🚀 OTOMASYON MOTORU v3.0 - KONTROL PANELİ 🚀 ".center(80))
        self.log_display.append("="*80)
        self.log_display.append("✨ Hoş Geldiniz! Motor başarıyla başlatıldı ve komutlarınızı bekliyor.")
        self.log_display.append("💡 Hızlı başlamak için sol paneldeki hızlı komutları kullanabilirsiniz.")
        self.log_display.append("="*80)

        return panel

    def create_right_panel(self):
        """Sağ panel - İş Akışı Detayları ve İlerleme"""
        panel = QFrame()
        panel.setObjectName("rightPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Başlık
        header = QLabel("⚙️ İŞ AKIŞI DETAYLARI")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(header)

        # İlerleme bölümü
        progress_container = QFrame()
        progress_container.setObjectName("progressContainer")
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setSpacing(8)

        progress_label = QLabel("📈 Genel İlerleme")
        progress_label.setStyleSheet("color: white; font-size: 12px;")
        progress_layout.addWidget(progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(progress_container)

        # Durum etiketi
        self.status_label = QLabel("🟢 Durum: Hazır")
        self.status_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: bold;
            padding: 12px;
            background-color: rgba(48, 162, 76, 0.2);
            border-radius: 8px;
            border-left: 4px solid #30A24C;
        """)
        layout.addWidget(self.status_label)

        # İş akışı tablosu
        table_label = QLabel("📋 Aktif İş Akışları")
        table_label.setStyleSheet("color: white; font-size: 13px; font-weight: bold; padding-top: 10px;")
        layout.addWidget(table_label)

        self.workflow_table = QTableWidget(0, 7)
        self.workflow_table.setHorizontalHeaderLabels([
            "ID", "Adım", "Durum", "İlerleme", "Bulunan", "Analiz", "Gönderilen"
        ])
        self.workflow_table.horizontalHeader().setStretchLastSection(True)
        self.workflow_table.setAlternatingRowColors(True)
        self.workflow_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.workflow_table)

        layout.addStretch()
        return panel

    def create_status_bar(self):
        """Alt durum çubuğu"""
        statusbar = self.statusBar()
        statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #1a1a2e;
                color: white;
                border-top: 2px solid #2a2a3e;
                padding: 5px;
            }
        """)
        
        # Sistem bilgileri
        self.statusbar_label = QLabel("🟢 Sistem Aktif | Motor: Çalışıyor")
        self.statusbar_time = QLabel()
        self.update_statusbar_time()
        
        statusbar.addWidget(self.statusbar_label)
        statusbar.addPermanentWidget(self.statusbar_time)
        
        # Zamanı sürekli güncelle
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_statusbar_time)
        self.time_timer.start(1000)  # Her saniye

    def update_statusbar_time(self):
        """Durum çubuğundaki zamanı güncelle"""
        current_time = datetime.now().strftime("🕐 %H:%M:%S | 📅 %d.%m.%Y")
        self.statusbar_time.setText(current_time)

    def setup_modern_toolbar(self):
        """Modern toolbar tasarımı"""
        toolbar = QToolBar("Araçlar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5858D6, stop:0.5 #30A24C, stop:1 #CA7137);
                border: none;
                padding: 5px;
                spacing: 10px;
            }
            QToolBar QToolButton {
                color: white;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                padding: 8px;
                margin: 2px;
            }
            QToolBar QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.addToolBar(toolbar)

        # Toolbar aksiyonları
        actions = [
            ("🚀 Gönder", self.send_command),
            ("⏸️ Duraklat", self.pause_workflow),
            ("▶️ Devam", self.resume_workflow),
            ("⏹️ Durdur", self.stop_workflow),
            ("⚙️ Motor Döngüsü", self.start_engine_loop_ui),
            ("🛑 Motoru Kapat", self.stop_engine_ui),
            ("🗑️ Temizle", self.clear_logs),
            ("💾 Kaydet", self.save_logs),
            ("📤 Tabloyu Dışa Aktar", self.export_workflows_csv),
        ]

        for text, func in actions:
            action = toolbar.addAction(text)
            action.triggered.connect(func)
            toolbar.addSeparator()

    def start_engine_loop_ui(self):
        try:
            if hasattr(self, 'engine') and self.engine:
                self.engine.start_engine_loop()
                self.update_log_display("⚙️ Motor döngüsü başlatıldı")
        except Exception as e:
            self.update_log_display(f"❌ Motor döngüsü başlatılamadı: {e}")

    def stop_engine_ui(self):
        try:
            if hasattr(self, 'engine') and self.engine:
                self.engine.stop_engine()
                self.update_log_display("🛑 Motor kapatıldı")
        except Exception as e:
            self.update_log_display(f"❌ Motor kapatılamadı: {e}")

    def create_chat_assistant_panel(self):
        """Chat Asistan sekmesi - NLP ile konuşarak otomasyonu tetikleme"""
        panel = QFrame()
        panel.setObjectName("chatPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        # Başlık barı
        header = QHBoxLayout()
        title = QLabel("🤖 AI Chat Asistanı")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white; padding: 6px;")
        self.chat_online_dot = QLabel("🟢")
        self.chat_online_dot.setToolTip("Çevrimiçi")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.chat_online_dot)
        layout.addLayout(header)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Asistan ile konuşma geçmişi burada görünecek...")
        layout.addWidget(self.chat_history)

        # Chat araçları: Öğrenme toggle + geri bildirim + bağlam + temizle
        tools_bar = QHBoxLayout()
        self.learning_toggle_btn = QPushButton("🧠 Öğrenme: Kapalı")
        self.learning_toggle_btn.setToolTip("Sürekli öğrenmeyi aç/kapat")
        self.learning_toggle_btn.clicked.connect(self.toggle_learning_mode)
        self.feedback_up_btn = QPushButton("👍 İyi Cevap")
        self.feedback_up_btn.setToolTip("Bu yanıt iyiydi")
        self.feedback_up_btn.clicked.connect(lambda: self.give_chat_feedback(True))
        self.feedback_down_btn = QPushButton("👎 Kötü Cevap")
        self.feedback_down_btn.setToolTip("Bu yanıt kötüydü")
        self.feedback_down_btn.clicked.connect(lambda: self.give_chat_feedback(False))
        self.show_context_btn = QPushButton("🧩 Bağlamı Göster")
        self.show_context_btn.setToolTip("Hafızadan ilgili bağlamı göster")
        self.show_context_btn.clicked.connect(self.show_memory_context)
        self.clear_chat_btn = QPushButton("🧹 Sohbeti Temizle")
        self.clear_chat_btn.setToolTip("Tüm sohbet geçmişini temizle")
        self.clear_chat_btn.clicked.connect(self.clear_chat_history)
        self.copy_last_btn = QPushButton("📋 Son Yanıtı Kopyala")
        self.copy_last_btn.setToolTip("Son asistan yanıtını panoya kopyala")
        self.copy_last_btn.clicked.connect(self._copy_last_reply)
        self.export_chat_btn = QPushButton("📤 Sohbeti Dışa Aktar")
        self.export_chat_btn.setToolTip("Sohbet geçmişini dosyaya kaydet")
        self.export_chat_btn.clicked.connect(self._export_chat_transcript)
        tools_bar.addWidget(self.learning_toggle_btn)
        tools_bar.addWidget(self.feedback_up_btn)
        tools_bar.addWidget(self.feedback_down_btn)
        tools_bar.addStretch()
        tools_bar.addWidget(self.show_context_btn)
        tools_bar.addWidget(self.clear_chat_btn)
        tools_bar.addWidget(self.copy_last_btn)
        tools_bar.addWidget(self.export_chat_btn)
        
        layout.addLayout(tools_bar)

        # Sesli konuşma barı (gelişmiş)
        voice_bar = QHBoxLayout()
        self.voice_toggle_btn = QPushButton("🎤 Dinlemeyi Başlat")
        self.voice_toggle_btn.clicked.connect(self.toggle_voice_listen)
        self.voice_once_btn = QPushButton("🎙️ Tek Seferlik")
        self.voice_once_btn.clicked.connect(self.capture_voice_once)
        self.tts_toggle_btn = QPushButton("🔊 TTS: Açık")
        self.tts_toggle_btn.clicked.connect(self.toggle_tts)
        # Dil / TTS sesi
        self.voice_lang_combo = QComboBox()
        self.voice_lang_combo.addItems(["tr-TR", "en-US"]) 
        self.tts_voice_combo = QComboBox()
        self.tts_voice_combo.addItems(["default", "female", "male"]) 
        self.tts_voice_combo.currentTextChanged.connect(self._apply_tts_voice)
        # Seviye ve süre
        self.voice_level = QProgressBar()
        self.voice_level.setRange(0, 100)
        self.voice_level.setFixedWidth(120)
        self.voice_timer_label = QLabel("00:00")
        self.voice_status = QLabel("🔇 Hazır")
        self.voice_status.setStyleSheet("color: #e0f2f7;")
        # Gelişmiş ses: gürültü azaltma, hassasiyet, kaydet/çal, dosyadan çözümle
        self.noise_reduce_btn = QPushButton("🔇 Gürültü Azaltma: Kapalı")
        self.noise_reduce_btn.setCheckable(True)
        self.noise_reduce_btn.clicked.connect(self.toggle_noise_reduction)
        self.sensitivity_label = QLabel("Hassasiyet")
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(50, 4000)
        self.sensitivity_slider.setValue(300)
        self.sensitivity_slider.setFixedWidth(120)
        self.sensitivity_slider.valueChanged.connect(self._apply_sensitivity)
        self.save_audio_btn = QPushButton("💾 Kaydı Kaydet: Kapalı")
        self.save_audio_btn.setCheckable(True)
        self.save_audio_btn.clicked.connect(self.toggle_save_recording)
        self.play_last_btn = QPushButton("▶️ Son Kaydı Çal")
        self.play_last_btn.clicked.connect(self.play_last_recording)
        self.transcribe_file_btn = QPushButton("📁 Dosyadan Çözümle")
        self.transcribe_file_btn.clicked.connect(self.transcribe_from_file)
        voice_bar.addWidget(self.voice_toggle_btn)
        voice_bar.addWidget(self.voice_once_btn)
        voice_bar.addWidget(QLabel("Dil:"))
        voice_bar.addWidget(self.voice_lang_combo)
        voice_bar.addWidget(QLabel("TTS:"))
        voice_bar.addWidget(self.tts_voice_combo)
        voice_bar.addWidget(self.tts_toggle_btn)
        voice_bar.addWidget(self.noise_reduce_btn)
        voice_bar.addWidget(self.sensitivity_label)
        voice_bar.addWidget(self.sensitivity_slider)
        voice_bar.addWidget(self.save_audio_btn)
        voice_bar.addWidget(self.play_last_btn)
        voice_bar.addWidget(self.transcribe_file_btn)
        voice_bar.addWidget(self.voice_level)
        voice_bar.addWidget(self.voice_timer_label)
        voice_bar.addStretch()
        voice_bar.addWidget(self.voice_status)
        layout.addLayout(voice_bar)

        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Örn: Ankara'da yazılım firmalarını bul ve 50 tane listele")
        self.chat_input.returnPressed.connect(self.handle_chat_message)
        chat_input_layout.addWidget(self.chat_input, 3)

        self.chat_send_btn = QPushButton("Gönder")
        self.chat_send_btn.clicked.connect(self.handle_chat_message)
        chat_input_layout.addWidget(self.chat_send_btn)

        layout.addLayout(chat_input_layout)
        # Kısayollar
        try:
            sc = QShortcut(QKeySequence("Ctrl+Enter"), panel)
            sc.activated.connect(self.handle_chat_message)
            sc2 = QShortcut(QKeySequence("Ctrl+Return"), panel)
            sc2.activated.connect(self.handle_chat_message)
        except Exception:
            pass
        return panel

    def clear_chat_history(self):
        """Sohbet geçmişini temizle."""
        self.chat_history.clear()
        self.last_assistant_reply = ""

    def _copy_last_reply(self):
        try:
            if not self.last_assistant_reply:
                QMessageBox.information(self, "Sohbet", "Kopyalanacak yanıt yok.")
                return
            QApplication.clipboard().setText(self.last_assistant_reply)
            self.chat_history.append("📋 Son yanıt kopyalandı")
        except Exception:
            pass

    def _export_chat_transcript(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getSaveFileName(self, "Sohbeti Dışa Aktar",
                                                 f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                                 "Text Files (*.txt)")
            if not path:
                return
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.chat_history.toPlainText())
            QMessageBox.information(self, "Sohbet", "✅ Sohbet kaydedildi")
        except Exception as e:
            QMessageBox.critical(self, "Sohbet", f"❌ Kaydetme hatası: {e}")

    def toggle_learning_mode(self):
        """Sürekli öğrenme modunu aç/kapat."""
        self.learning_enabled = not self.learning_enabled
        self.learning_toggle_btn.setText("🧠 Öğrenme: Açık" if self.learning_enabled else "🧠 Öğrenme: Kapalı")
        if self.ai_memory:
            try:
                if self.learning_enabled:
                    self.ai_memory.start_learning()
                    self.chat_history.append("🧠 Öğrenme modu açıldı.")
                else:
                    self.ai_memory.stop_learning()
                    self.chat_history.append("🧠 Öğrenme modu kapatıldı.")
            except Exception as e:
                self.chat_history.append(f"⚠️ Öğrenme modu değiştirilemedi: {e}")

    def give_chat_feedback(self, is_positive: bool):
        """Son asistan cevabına geri bildirim ver ve öğrenmeye kaydet."""
        if not self.last_assistant_reply:
            QMessageBox.information(self, "Geri Bildirim", "Değerlendirilecek bir asistan cevabı yok.")
            return
        try:
            # Optimizer'a NLP geri bildirimi (serbest metin)
            if hasattr(self, 'engine') and self.engine and self.engine.optimizer:
                fb_text = f"CHAT_FEEDBACK | reply={self.last_assistant_reply[:120]}"
                self.engine.optimizer.add_nlp_feedback(fb_text, {"mode": "chat"}, is_positive)
            # Hafızaya tercih olarak kaydet (basit)
            if self.ai_memory and is_positive:
                from ai_memory_personalization import InteractionType, EmotionalState
                self.ai_memory.recognize_interaction_pattern(
                    user_id=self.user_id,
                    interaction_type=InteractionType.TEXT_QUERY,
                    success=True,
                    topics=[],
                    emotional_state=EmotionalState.POSITIVE if is_positive else EmotionalState.NEUTRAL
                )
            self.chat_history.append("✅ Geri bildirim kaydedildi" if is_positive else "⚠️ Olumsuz geri bildirim kaydedildi")
        except Exception as e:
            self.chat_history.append(f"⚠️ Geri bildirim kaydedilemedi: {e}")

    def show_memory_context(self):
        """Son kullanıcı girdisine göre ilgili hafıza parçalarını göster."""
        try:
            query = self.chat_input.text().strip()
            if not query:
                QMessageBox.information(self, "Bağlam", "Önce giriş kutusuna bir konu yazın.")
                return
            if not self.ai_memory:
                QMessageBox.information(self, "Bağlam", "AI Memory sistemi etkin değil.")
                return
            memories = self.ai_memory.retrieve_memory(self.user_id, query)
            if not memories:
                self.chat_history.append("🧩 İlgili bağlam bulunamadı.")
                return
            self.chat_history.append("🧩 Bağlam önerileri:")
            for m in memories[:3]:
                self.chat_history.append(f"• {m.content}")
        except Exception as e:
            self.chat_history.append(f"⚠️ Bağlam gösterilemedi: {e}")

    def toggle_voice_listen(self):
        """Sürekli dinlemeyi başlat/durdur (voice_assistant üzerinden)."""
        if not self.voice_gui:
            QMessageBox.information(self, "Sesli Asistan", "Sesli asistan modülü yüklenemedi.")
            return
        try:
            if not self.voice_listening:
                ok = self.voice_gui.start_listening()
                if ok:
                    self.voice_listening = True
                    self.voice_toggle_btn.setText("🔇 Dinlemeyi Durdur")
                    self.voice_status.setText("🎧 Dinliyorum...")
                    # Basit bir animasyon ile seviye ve süreyi güncelle
                    self._start_voice_indicators()
                    # TTS ile bildir
                    self._speak_with_fallback("Dinliyorum, komutlarınızı söyleyin")
                else:
                    QMessageBox.warning(self, "Ses", "Dinleme başlatılamadı.")
            else:
                ok = self.voice_gui.stop_listening()
                if ok is not False:
                    self.voice_listening = False
                    self.voice_toggle_btn.setText("🎤 Dinlemeyi Başlat")
                    self.voice_status.setText("🔇 Hazır")
                    self._stop_voice_indicators()
        except Exception as e:
            QMessageBox.critical(self, "Ses", f"Hata: {e}")

    def capture_voice_once(self):
        """Tek seferlik konuşmayı yazıya çevirip metin alanına koyar."""
        if not _SR_AVAILABLE:
            QMessageBox.information(self, "Ses", "SpeechRecognition yüklü değil.")
            return
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.voice_status.setText("🎙️ Dinliyor...")
                QApplication.processEvents()
                # Hassasiyet ve gürültü azaltma
                try:
                    recognizer.energy_threshold = int(self.sensitivity_slider.value()) if hasattr(self, 'sensitivity_slider') else 300
                except Exception:
                    pass
                nr = self.noise_reduce_btn.isChecked() if hasattr(self, 'noise_reduce_btn') else False
                recognizer.adjust_for_ambient_noise(source, duration=1.2 if nr else 0.6)
                lang = self.voice_lang_combo.currentText() if hasattr(self, 'voice_lang_combo') else 'tr-TR'
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)
            try:
                lang = self.voice_lang_combo.currentText() if hasattr(self, 'voice_lang_combo') else 'tr-TR'
                # İsteğe bağlı kaydet
                self._maybe_save_audio(audio)
                text = recognizer.recognize_google(audio, language=lang)
                self.chat_input.setText(text)
                self._append_user_message(text)
                self.handle_chat_message()
            except sr.UnknownValueError:
                self._append_bot_message("Ses anlaşılamadı, tekrar deneyin.")
            except sr.RequestError as e:
                self._append_bot_message(f"Ses tanıma hatası: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Ses", f"Hata: {e}")
        finally:
            self.voice_status.setText("🔇 Hazır")

    def toggle_noise_reduction(self):
        try:
            on = self.noise_reduce_btn.isChecked()
            self.noise_reduce_btn.setText("🔇 Gürültü Azaltma: Açık" if on else "🔇 Gürültü Azaltma: Kapalı")
        except Exception:
            pass

    def _apply_sensitivity(self):
        try:
            val = int(self.sensitivity_slider.value())
            # Anlık olarak recognizer’a uygulanması tek seferlikte yapılır; burada sadece label’a yansıtabiliriz
            self.sensitivity_label.setText(f"Hassasiyet ({val})")
        except Exception:
            pass

    def toggle_save_recording(self):
        try:
            on = self.save_audio_btn.isChecked()
            self.save_audio_btn.setText("💾 Kaydı Kaydet: Açık" if on else "💾 Kaydı Kaydet: Kapalı")
        except Exception:
            pass

    def _maybe_save_audio(self, audio):
        try:
            if not self.save_audio_btn.isChecked():
                return
            data = audio.get_wav_data()
            from pathlib import Path
            out_dir = Path("recordings")
            out_dir.mkdir(exist_ok=True)
            filename = out_dir / f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            with open(filename, 'wb') as f:
                f.write(data)
            self.last_audio_path = str(filename)
            self.chat_history.append(f"💾 Ses kaydedildi: {filename}")
        except Exception as e:
            self._append_bot_message(f"Kayıt kaydedilemedi: {e}")

    def play_last_recording(self):
        try:
            import os
            if not hasattr(self, 'last_audio_path') or not self.last_audio_path:
                QMessageBox.information(self, "Ses", "Çalınacak kayıt yok.")
                return
            # Windows: varsayılan medya oynatıcıyla aç
            os.startfile(self.last_audio_path)
        except Exception as e:
            self._append_bot_message(f"Çalma hatası: {e}")

    def transcribe_from_file(self):
        try:
            if not _SR_AVAILABLE:
                QMessageBox.information(self, "Ses", "SpeechRecognition yüklü değil.")
                return
            from PySide6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getOpenFileName(self, "Ses Dosyası Seç", "", "Audio Files (*.wav *.mp3 *.flac *.m4a)")
            if not path:
                return
            recognizer = sr.Recognizer()
            with sr.AudioFile(path) as source:
                audio = recognizer.record(source)
            lang = self.voice_lang_combo.currentText() if hasattr(self, 'voice_lang_combo') else 'tr-TR'
            text = recognizer.recognize_google(audio, language=lang)
            self._append_user_message(f"[Dosya] {path}\n{text}")
            self.chat_input.setText(text)
            self.handle_chat_message()
        except Exception as e:
            self._append_bot_message(f"Dosyadan çözümleme hatası: {e}")

    def _apply_tts_voice(self):
        try:
            voice_name = self.tts_voice_combo.currentText()
            if self.voice_gui and hasattr(self.voice_gui, 'set_tts_voice'):
                self.voice_gui.set_tts_voice(voice_name)
        except Exception:
            pass

    def _start_voice_indicators(self):
        try:
            self._voice_start_time = time.time()
            if not hasattr(self, '_voice_timer'):
                self._voice_timer = QTimer()
                self._voice_timer.timeout.connect(self._update_voice_indicators)
            self._voice_timer.start(200)
        except Exception:
            pass

    def _stop_voice_indicators(self):
        try:
            if hasattr(self, '_voice_timer'):
                self._voice_timer.stop()
            if hasattr(self, 'voice_level'):
                self.voice_level.setValue(0)
            if hasattr(self, 'voice_timer_label'):
                self.voice_timer_label.setText("00:00")
        except Exception:
            pass

    def _update_voice_indicators(self):
        try:
            # Pseudo seviye animasyonu (gerçek VAD yoksa)
            import random
            level = random.randint(10, 90)
            self.voice_level.setValue(level)
            # Süre
            elapsed = int(time.time() - getattr(self, '_voice_start_time', time.time()))
            mm = elapsed // 60
            ss = elapsed % 60
            self.voice_timer_label.setText(f"{mm:02d}:{ss:02d}")
        except Exception:
            pass

    def toggle_tts(self):
        """Metin okuma (TTS) açık/kapalı."""
        self.voice_tts_enabled = not self.voice_tts_enabled
        self.tts_toggle_btn.setText("🔊 TTS: Açık" if self.voice_tts_enabled else "🔈 TTS: Kapalı")

    def _speak_with_fallback(self, text: str):
        """TTS ile metni seslendir; voice_gui yoksa pyttsx3 fallback kullan."""
        if not self.voice_tts_enabled:
            return
        # Önce voice_gui'yi dene
        if self.voice_gui:
            try:
                self.voice_gui.speak(text)
                return
            except Exception:
                pass
        # Fallback: pyttsx3 (thread'de çalıştır)
        if TTS_PYTHON_AVAILABLE and pyttsx3:
            def _speak_thread():
                try:
                    engine = pyttsx3.init()
                    # Türkçe için varsa dil ayarı   
                    try:
                        voices = engine.getProperty('voices')
                        # Türkçe ses bul
                        for voice in voices:
                            name_lower = voice.name.lower()
                            if 'turkish' in name_lower or 'türkçe' in name_lower or 'tr' in name_lower:
                                engine.setProperty('voice', voice.id)
                                break
                    except Exception:
                        pass
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    logger.warning(f"TTS fallback hatası: {e}")
            threading.Thread(target=_speak_thread, daemon=True).start()

    def emit_feedback(self, message):
        """Motor thread'inden gelen mesajı ana thread'e iletmek için sinyal yollar"""
        self.feedback_signal.message_received.emit(message)

    @Slot(str)
    def update_log_display(self, message):
        """GUI thread'inde log ekranını günceller"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Mesaj tipine göre emoji ve renk
        if "hata" in message.lower() or "başarısız" in message.lower():
            icon = "❌"
            color = "#C43D4B"
        elif "başarı" in message.lower() or "tamamlandı" in message.lower():
            icon = "✅"
            color = "#30A24C"
        elif "uyarı" in message.lower():
            icon = "⚠️"
            color = "#CA7137"
        elif "bilgi" in message.lower() or "başlat" in message.lower():
            icon = "ℹ️"
            color = "#5858D6"
        else:
            icon = "📢"
            color = "#e0f2f7"
        
        formatted_message = f'[{timestamp}] {icon} {message}'
        # Tamponu güncelle
        self.log_buffer.append(formatted_message)
        # Filtre uygula ve göster
        self._render_logs()
        
        # Otomatik aşağı kaydır
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )
        
        # Durum güncellemeleri
        self._update_button_states(message)

    def _render_logs(self):
        """Tampondaki logları filtreye göre render et"""
        self.log_display.clear()
        if not self.log_filter_text:
            for line in self.log_buffer[-1000:]:
                self.log_display.append(line)
        else:
            filter_l = self.log_filter_text.lower()
            for line in self.log_buffer[-2000:]:
                if filter_l in line.lower():
                    self.log_display.append(line)
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )

    def filter_logs(self, text):
        """Loglarda arama/filtreleme uygula"""
        self.log_filter_text = text.strip()
        self._render_logs()

    def _update_button_states(self, message):
        """Mesaja göre buton durumlarını güncelle"""
        msg_lower = message.lower()
        
        if "iş akışı başlatıldı" in msg_lower:
            self.stop_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
            self.send_button.setEnabled(False)
            self.status_label.setText("🟡 Durum: Çalışıyor")
            self.status_label.setStyleSheet("""
                color: white; font-size: 13px; font-weight: bold; padding: 12px;
                background-color: rgba(202, 113, 55, 0.2); border-radius: 8px;
                border-left: 4px solid #CA7137;
            """)
        elif "duraklatıldı" in msg_lower:
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)
            self.status_label.setText("🟠 Durum: Duraklatıldı")
            self.status_label.setStyleSheet("""
                color: white; font-size: 13px; font-weight: bold; padding: 12px;
                background-color: rgba(202, 113, 55, 0.2); border-radius: 8px;
                border-left: 4px solid #CA7137;
            """)
        elif "devam ettiriliyor" in msg_lower or "kaldığı yerden devam" in msg_lower:
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
            self.status_label.setText("🟡 Durum: Devam Ediyor")
            self.status_label.setStyleSheet("""
                color: white; font-size: 13px; font-weight: bold; padding: 12px;
                background-color: rgba(48, 162, 76, 0.2); border-radius: 8px;
                border-left: 4px solid #30A24C;
            """)
        elif any(word in msg_lower for word in ["tamamlandı", "durduruldu", "başarısız", "hata oluştu"]):
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(False)
            self.send_button.setEnabled(True)
            if "başarısız" in msg_lower or "hata" in msg_lower:
                self.status_label.setText("🔴 Durum: Hata")
                self.status_label.setStyleSheet("""
                    color: white; font-size: 13px; font-weight: bold; padding: 12px;
                    background-color: rgba(196, 61, 75, 0.2); border-radius: 8px;
                    border-left: 4px solid #C43D4B;
                """)
            else:
                self.status_label.setText("🟢 Durum: Hazır")
                self.status_label.setStyleSheet("""
                    color: white; font-size: 13px; font-weight: bold; padding: 12px;
                    background-color: rgba(48, 162, 76, 0.2); border-radius: 8px;
                    border-left: 4px solid #30A24C;
                """)

    def send_command(self):
        """Komut giriş alanındaki metni motora gönderir"""
        command = self.command_input.text().strip()
        if command:
            # Motor kontrolü
            if not hasattr(self, 'engine') or not self.engine or not self.engine.is_ready:
                self.update_log_display("❌ Motor hazır değil! Lütfen bekleyin.")
                return
                
            # NLP ayrıştır + eksik slotları tamamla + iş akışı başlat
            try:
                parsed = self.engine.nlp_parser.parse_command(command)
                final_parsed = self._resolve_missing_slots(parsed, original_text=command)
                if final_parsed:
                    self._start_workflow_from_parsed(final_parsed, original_text=command, original_parsed=parsed)
                else:
                    self.update_log_display("ℹ️ İşlem iptal edildi.")
                    return
            except Exception as e:
                self.update_log_display(f"❌ Komut işleme hatası: {e}")
            threading.Thread(target=self.engine.process_command, args=(command,), daemon=True).start()
            self.command_input.clear()
            self.send_button.setEnabled(False)
            self._add_history(command)
        else:
            QMessageBox.warning(self, "⚠️ Uyarı", "Lütfen bir komut girin.")

    def pause_workflow(self):
        """Çalışan iş akışını duraklatır"""
        if not hasattr(self, 'engine') or not self.engine or not self.engine.is_ready:
            self.update_log_display("❌ Motor hazır değil!")
            return
        if self.engine.orchestrator.pause_workflow():
            pass
        else:
            self.update_log_display("ℹ️ Duraklatılacak aktif bir iş akışı yok.")

    def resume_workflow(self):
        """Duraklatılmış iş akışını devam ettirir"""
        if not hasattr(self, 'engine') or not self.engine or not self.engine.is_ready:
            self.update_log_display("❌ Motor hazır değil!")
            return
        if (self.engine.orchestrator.current_workflow and 
            self.engine.orchestrator.current_workflow.get('status') == 'paused'):
            self.update_log_display("⏳ İş akışı devam ettiriliyor...")
            threading.Thread(
                target=self.engine.orchestrator.resume_workflow,
                args=(self.emit_feedback,),
                daemon=True
            ).start()
        else:
            self.update_log_display("ℹ️ Devam ettirilecek duraklatılmış bir iş akışı yok.")

    def stop_workflow(self):
        """Çalışan iş akışını durdurur"""
        if not hasattr(self, 'engine') or not self.engine or not self.engine.is_ready:
            self.update_log_display("❌ Motor hazır değil!")
            return
        reply = QMessageBox.question(
            self, "⚠️ Onay",
            "Mevcut iş akışını durdurmak istediğinizden emin misiniz?\n"
            "İşlem kaldığı yerden devam ettirilemez.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.engine.orchestrator.stop_workflow():
                pass
            else:
                self.update_log_display("ℹ️ Durdurulacak aktif bir iş akışı yok.")
                
    def timerEvent(self, event):
        """Periyodik durum kontrolü"""
        if event.timerId() == self.status_timer:
            if hasattr(self, 'engine') and self.engine and self.engine.is_ready and self.engine.orchestrator:
                status = self.engine.orchestrator.get_workflow_status()
                try:
                    progress_val = int(status.get('progress', 0))
                except Exception:
                    progress_val = 0
                self.progress_bar.setValue(progress_val)
                self.refresh_workflow_table(status.get('details'))
        elif event.timerId() == self.stats_timer:
            self.update_statistics()

    def update_statistics(self):
        """İstatistik kartlarını güncelle"""
        if hasattr(self, 'engine') and self.engine and self.engine.is_ready and self.engine.orchestrator:
            status = self.engine.orchestrator.get_workflow_status()
            details = status.get('details', {})
            found = len(details.get('found_firms', []))
            analyzed = len(details.get('analyzed_firms', []))
            sent = len(details.get('sent_emails', []))
            self.stat_cards['found'].update_value(found)
            self.stat_cards['analyzed'].update_value(analyzed)
            self.stat_cards['sent'].update_value(sent)
            if status.get('status') == 'completed':
                current = int(self.stat_cards['completed'].value_label.text())
                self.stat_cards['completed'].update_value(current + 1)

    def refresh_workflow_table(self, details):
        """İş akışı tablosunu güncelle"""
        self.workflow_table.setRowCount(0)
        if not details:
            return
        
        row = self.workflow_table.rowCount()
        self.workflow_table.insertRow(row)
        
        def set_item(col, text, color=None):
            item = QTableWidgetItem(str(text))
            if color:
                item.setForeground(QColor(color))
            self.workflow_table.setItem(row, col, item)
        
        set_item(0, details.get('id', '-'))
        set_item(1, details.get('current_step', '-'))
        
        status = details.get('status', '-')
        status_color = {
            'running': '#CA7137',
            'paused': '#CA7137',
            'completed': '#30A24C',
            'failed': '#C43D4B'
        }.get(status, '#e0f2f7')
        set_item(2, status, status_color)
        
        set_item(3, f"{details.get('progress', 0)}%")
        set_item(4, len(details.get('found_firms', [])))
        set_item(5, len(details.get('analyzed_firms', [])))
        set_item(6, len(details.get('sent_emails', [])))

    def _quick_command(self, text):
        self.command_input.setText(text)
        self.send_command()

    def _add_history(self, text):
        existing_index = self.command_history.findText(text)
        if existing_index != -1:
            self.command_history.removeItem(existing_index)
        self.command_history.insertItem(0, text)
        if self.command_history.count() > 20:
            self.command_history.removeItem(self.command_history.count() - 1)

    def _pick_history_command(self, index):
        if 0 <= index < self.command_history.count():
            self.command_input.setText(self.command_history.itemText(index))

    def _lighten_color(self, color):
        """Rengi açıklaştır"""
        c = QColor(color)
        h, s, v, a = c.getHsv()
        return QColor.fromHsv(h, max(0, s - 30), min(255, v + 30), a).name()

    def _darken_color(self, color):
        """Rengi koyulaştır"""
        c = QColor(color)
        h, s, v, a = c.getHsv()
        return QColor.fromHsv(h, min(255, s + 30), max(0, v - 30), a).name()

    def toggle_theme(self):
        """Tema değiştir"""
        self.dark_mode = not getattr(self, 'dark_mode', True)
        if self.dark_mode:
            self.apply_modern_styles()
        else:
            self.setStyleSheet("")

    def clear_logs(self):
        """Logları temizle"""
        self.log_buffer.clear()
        self._render_logs()
        self.log_display.append("🗑️ Loglar temizlendi.")

    def copy_logs(self):
        """Logları panoya kopyala"""
        self.log_display.selectAll()
        self.log_display.copy()
        cursor = self.log_display.textCursor()
        cursor.clearSelection()
        self.log_display.setTextCursor(cursor)
        self.update_log_display("📋 Loglar panoya kopyalandı.")

    def export_workflows_csv(self):
        """Aktif iş akışı tablosunu CSV'ye aktar"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        path, _ = QFileDialog.getSaveFileName(
            self, "📤 Tabloyu Dışa Aktar",
            f"workflows_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = [self.workflow_table.horizontalHeaderItem(c).text() for c in range(self.workflow_table.columnCount())]
                writer.writerow(headers)
                for r in range(self.workflow_table.rowCount()):
                    row_vals = []
                    for c in range(self.workflow_table.columnCount()):
                        item = self.workflow_table.item(r, c)
                        row_vals.append(item.text() if item else '')
                    writer.writerow(row_vals)
            QMessageBox.information(self, "✅ Başarılı", "Tablo CSV olarak kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"CSV kaydedilemedi: {e}")

    def save_logs(self):
        """Logları dosyaya kaydet"""
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "💾 Logları Kaydet",
            f"automation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                QMessageBox.information(self, "✅ Başarılı", "Loglar başarıyla kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "❌ Hata", f"Loglar kaydedilemedi: {e}")

    def edit_telegram_settings(self):
        """Telegram ayarlarını düzenle"""
        from PySide6.QtWidgets import QInputDialog
        import json, os
        
        bot_token, ok1 = QInputDialog.getText(
            self, "📱 Telegram Bot Token",
            "Bot Token:"
        )
        if not ok1:
            return
        
        chat_id, ok2 = QInputDialog.getText(
            self, "📱 Telegram Chat ID",
            "Chat ID:"
        )
        if not ok2:
            return
        
        config = {}
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
        except Exception:
            config = {}
        
        config['telegram_bot_token'] = bot_token
        config['telegram_chat_id'] = chat_id
        
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "✅ Başarılı", "Telegram ayarları kaydedildi.")
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Ayarlar kaydedilemedi: {e}")

    def handle_chat_message(self):
        """Chat mesajını al, ekrana yaz ve NLP üzerinden motora komut gönder"""
        text = self.chat_input.text().strip()
        if not text:
            return
        self._append_user_message(text)
        self.chat_input.clear()
        # İsteğe bağlı TTS ile onay
        if self.voice_tts_enabled and self.voice_gui:
            try:
                self.voice_gui.speak(f"Komut alındı: {text}")
            except Exception:
                pass
        
        # Önce hızlı sistem komutlarını dene (ayar aç, tts, öğrenme, tema vb.)
        try:
            if self._process_quick_system_commands(text):
                return
        except Exception:
            pass

        # Doğal eylem komutları: e-posta / WhatsApp
        try:
            lt = text.lower()
            if any(k in lt for k in ["mail at", "e-posta gönder", "email gönder", "mail gönder"]):
                self._interactive_send_email()
                return
            if any(k in lt for k in ["whatsapp'tan yaz", "whatsapptan yaz", "whatsappdan yaz", "whatsapp gönder", "wp den yaz", "wp'den yaz", "whatsapp yaz"]):
                self._interactive_send_whatsapp()
                return
        except Exception:
            pass

        # Özel yönlendirme komutları (gpt:/whatsapp:/vapi:/analytics:/builder:)
            try:
                routed = self._route_special_commands(text)
                if routed:
                    return
            except Exception:
                pass
        
        # Motor kontrolü
        if not hasattr(self, 'engine') or not self.engine or not self.engine.is_ready:
            self.chat_history.append("❌ Motor hazır değil! Lütfen bekleyin.")
            return
            
        try:
            parsed = self.engine.nlp_parser.parse_command(text)
            self.chat_history.append(f"🤖 Asistan (NLP): {parsed}")
            # Sohbet modu: intent yok/hata/bilgi_sor/sohbet → GPT ile yanıtla
            intent = parsed.get('intent') if isinstance(parsed, dict) else None
            if intent in (None, 'hata', 'bilgi_sor', 'sohbet'):
                reply = self._generate_chat_reply(text)
                # Basit duygu analizi (varsa)
                try:
                    sentiment = self._analyze_sentiment(text)
                    if sentiment:
                        self.chat_history.append(f"🧭 Duygu: {sentiment}")
                except Exception:
                    pass
                self._append_bot_message(reply)
                self._speak_with_fallback(reply)
                self.last_assistant_reply = reply
                self._learn_from_interaction(user_text=text, assistant_text=reply, intent='chat')
                return
            # Aksi halde otomasyon komutu
            final_parsed = self._resolve_missing_slots(parsed, original_text=text, via_chat=True)
            if final_parsed:
                self._start_workflow_from_parsed(final_parsed, original_text=text, original_parsed=parsed)
                try:
                    if hasattr(self.engine, 'optimizer') and self.engine.optimizer:
                        self.engine.optimizer.add_nlp_feedback(text, parsed, True)
                except Exception:
                    pass
            else:
                msg = "Daha net bir komut verebilir misiniz?"
                self._append_bot_message(msg)
                self._speak_with_fallback(msg)
        except Exception as e:
            self._append_bot_message(f"Hata: {e}")

    def _route_special_commands(self, text: str) -> bool:
        t = text.strip()
        lower = t.lower()
        # gpt: Soru
        if lower.startswith("gpt:"):
            q = t[4:].strip()
            if not q:
                return True
            try:
                reply = self._quick_gpt_ask(q)
                self.chat_history.append(f"💡 GPT: {reply}")
            except Exception as e:
                self.chat_history.append(f"❌ GPT hata: {e}")
            return True
        # whatsapp: +90... | mesaj
        if lower.startswith("whatsapp:"):
            payload = t[len("whatsapp:"):].strip()
            try:
                parts = payload.split("|", 1)
                phone = parts[0].strip()
                msg = parts[1].strip() if len(parts) > 1 else ''
                if not getattr(self, 'whatsapp_auto_sender', None) and WhatsAppAutoSender:
                    self.whatsapp_auto_sender = WhatsAppAutoSender()
                if getattr(self, 'whatsapp_auto_sender', None):
                    ok = self.whatsapp_auto_sender.send_message(phone, msg)
                    self.chat_history.append("✅ WhatsApp gönderildi" if ok else "❌ WhatsApp gönderilemedi")
                else:
                    self.chat_history.append("ℹ️ WhatsApp sender mevcut değil")
            except Exception as e:
                self.chat_history.append(f"❌ WhatsApp hata: {e}")
            return True
        # vapi: ... (rezerve)
        if lower.startswith("vapi:"):
            self.chat_history.append("ℹ️ Vapi komutları yakında eklenecek")
            return True
        # analytics: refresh
        if lower.startswith("analytics:"):
            try:
                self._reload_analytics()
                self.chat_history.append("📊 Analytics yenilendi")
            except Exception as e:
                self.chat_history.append(f"❌ Analytics hata: {e}")
            return True
        # builder: reset
        if lower.startswith("builder:"):
            try:
                self._reload_automation_builder()
                self.chat_history.append("🧱 Automation Builder yenilendi")
            except Exception as e:
                self.chat_history.append(f"❌ Builder hata: {e}")
            return True
        return False

    def _process_quick_system_commands(self, text: str) -> bool:
        """Basit doğal dilli sistem komutlarını işle. İşlendiyse True döner."""
        t = text.lower()
        # Ayarlar
        if any(kw in t for kw in ["ayarları aç", "ayarları göster", "settings", "ayarlar"]):
            try:
                # Ayarlar sekmesine geç
                mw = self.findChild(QTabWidget, "mainTabs")
                if mw:
                    for i in range(mw.count()):
                        if mw.tabText(i).startswith("⚙️"):
                            mw.setCurrentIndex(i)
                            break
                self.chat_history.append("⚙️ Ayarlar açıldı.")
            except Exception:
                pass
            return True
        # TTS
        if any(kw in t for kw in ["tts aç", "ses aç", "sesli aç"]):
            if not self.voice_tts_enabled:
                self.toggle_tts()
            self.chat_history.append("🔊 TTS açıldı.")
            return True
        if any(kw in t for kw in ["tts kapat", "ses kapat", "sesli kapat"]):
            if self.voice_tts_enabled:
                self.toggle_tts()
            self.chat_history.append("🔈 TTS kapatıldı.")
            return True
        # Öğrenme
        if any(kw in t for kw in ["öğrenmeyi aç", "learning aç"]):
            if not self.learning_enabled:
                self.toggle_learning_mode()
            self.chat_history.append("🧠 Öğrenme modu açıldı.")
            return True
        if any(kw in t for kw in ["öğrenmeyi kapat", "learning kapat"]):
            if self.learning_enabled:
                self.toggle_learning_mode()
            self.chat_history.append("🧠 Öğrenme modu kapatıldı.")
            return True
        # Tema
        if any(kw in t for kw in ["tema değiştir", "karanlık tema", "dark mode", "light mode"]):
            self.toggle_theme()
            self.chat_history.append("🎨 Tema değiştirildi.")
            return True
        # Ana sistem reset
        if any(kw in t for kw in ["ana sistemi yeniden başlat", "core reset", "sistem reset"]):
            try:
                self._reload_database()
                self._reload_api_manager()
                self._reload_analytics()
                self._reload_automation_builder()
                self._reload_tracking_gui()
                self.chat_history.append("🧩 Ana sistem yeniden başlatıldı.")
            except Exception as e:
                self.chat_history.append(f"⚠️ Ana sistem yeniden başlatılamadı: {e}")
            return True
        # GPT modeli değiştirme
        if t.startswith("modeli ") or t.startswith("modeli:"):
            try:
                parts = text.split(maxsplit=1)
                if len(parts) == 2:
                    model = parts[1].strip()
                    if self.gpt_manager:
                        self.gpt_manager.model = model
                        self.chat_history.append(f"🧠 Model güncellendi: {model}")
                        if hasattr(self, 'settings_model'):
                            self.settings_model.setText(model)
                        return True
            except Exception:
                pass
        return False

    def _interactive_send_email(self):
        """Kullanıcıdan alıcı/konu/içerik alarak e-posta gönderir."""
        from PySide6.QtWidgets import QInputDialog
        try:
            if not EMAIL_AVAILABLE:
                QMessageBox.information(self, "E-posta", "EmailManager modülü bulunamadı.")
                return
            to_addr, ok = QInputDialog.getText(self, "E-posta", "Alıcı e-posta(lar) (virgülle):")
            if not ok or not to_addr.strip():
                return
            subject, ok = QInputDialog.getText(self, "E-posta", "Konu:")
            if not ok:
                return
            # Çok satırlı içerik
            try:
                body, ok = QInputDialog.getMultiLineText(self, "E-posta", "İçerik (boş bırakılırsa GPT taslak yazabilir):")
            except Exception:
                body, ok = QInputDialog.getText(self, "E-posta", "İçerik:")
            if not ok:
                return
            # İçerik yoksa GPT'den taslak iste (varsa)
            if (not body or not body.strip()) and self.gpt_manager and getattr(self.gpt_manager, 'client', None):
                use_draft = QMessageBox.question(self, "Taslak", "İçerik boş. GPT ile taslak oluşturulsun mu?",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if use_draft == QMessageBox.Yes:
                    try:
                        body = self._generate_email_draft(subject)
                    except Exception as e:
                        self.update_log_display(f"⚠️ Taslak oluşturulamadı: {e}")
                        body = body or ""
            # Önizleme ve onay
            to_list = [x.strip() for x in to_addr.split(',') if x.strip()]
            if not to_list:
                return
            if not self._confirm_email_preview(to_list, subject.strip(), body):
                self.chat_history.append("📧 Gönderim iptal edildi")
                return
            # Zamanlama sor
            delay_ms = self._ask_schedule_delay_ms()
            # Gönder
            try:
                em = EmailManager()
                def do_send():
                    total_ok = True
                    for addr in to_list:
                        ok_one = False
                        if hasattr(em, 'send_email'):
                            ok_one = em.send_email(addr, subject.strip(), body)
                        elif hasattr(em, 'send'):
                            ok_one = em.send(addr, subject.strip(), body)
                        total_ok = total_ok and bool(ok_one)
                    if total_ok:
                        self.update_log_display("✅ E-posta gönderildi")
                        self.chat_history.append("📧 E-posta gönderildi")
                        try:
                            # İstatistik kartını artır
                            current = int(self.stat_cards['sent'].value_label.text())
                            self.stat_cards['sent'].update_value(current + len(to_list))
                        except Exception:
                            pass
                    else:
                        self.update_log_display("❌ E-posta gönderilemedi")
                if delay_ms > 0:
                    QTimer.singleShot(delay_ms, do_send)
                    self.chat_history.append("⏰ E-posta zamanlandı")
                else:
                    do_send()
            except Exception as e:
                QMessageBox.critical(self, "E-posta", f"Gönderilemedi: {e}")
        except Exception as e:
            self.update_log_display(f"❌ E-posta hata: {e}")

    def _interactive_send_whatsapp(self):
        """Kullanıcıdan telefon/mesaj alarak WhatsApp gönderir."""
        from PySide6.QtWidgets import QInputDialog
        try:
            if not WhatsAppAutoSender:
                QMessageBox.information(self, "WhatsApp", "WhatsAppAutoSender mevcut değil.")
                return
            phone, ok = QInputDialog.getText(self, "WhatsApp", "Alıcı Telefon(lar) (+90..., virgülle):")
            if not ok or not phone.strip():
                return
            try:
                msg, ok = QInputDialog.getMultiLineText(self, "WhatsApp", "Mesaj:")
            except Exception:
                msg, ok = QInputDialog.getText(self, "WhatsApp", "Mesaj:")
            if not ok:
                return
            # Önizleme ve onay
            phones = [x.strip() for x in phone.split(',') if x.strip()]
            if not phones:
                return
            if not self._confirm_whatsapp_preview(phones, msg):
                self.chat_history.append("💬 WhatsApp gönderimi iptal edildi")
                return
            delay_ms = self._ask_schedule_delay_ms()
            if not getattr(self, 'whatsapp_auto_sender', None):
                try:
                    self.whatsapp_auto_sender = WhatsAppAutoSender()
                except Exception as e:
                    QMessageBox.critical(self, "WhatsApp", f"Başlatılamadı: {e}")
                    return
            def do_send_wp():
                total_ok = True
                for p in phones:
                    ok_send = self.whatsapp_auto_sender.send_message(p, msg)
                    total_ok = total_ok and bool(ok_send)
                if total_ok:
                    self.update_log_display("✅ WhatsApp mesajı gönderildi")
                    self.chat_history.append("💬 WhatsApp mesajı gönderildi")
                else:
                    self.update_log_display("❌ WhatsApp mesajı gönderilemedi")
            if delay_ms > 0:
                QTimer.singleShot(delay_ms, do_send_wp)
                self.chat_history.append("⏰ WhatsApp mesajı zamanlandı")
            else:
                do_send_wp()
        except Exception as e:
            self.update_log_display(f"❌ WhatsApp hata: {e}")

    def _confirm_email_preview(self, to_list, subject, body) -> bool:
        try:
            preview = f"Alıcılar: {', '.join(to_list)}\nKonu: {subject}\n\n{body}"
            ret = QMessageBox.question(self, "E-posta Önizleme", preview,
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return ret == QMessageBox.Yes
        except Exception:
            return True

    def _confirm_whatsapp_preview(self, phones, msg) -> bool:
        try:
            preview = f"Alıcılar: {', '.join(phones)}\n\n{msg}"
            ret = QMessageBox.question(self, "WhatsApp Önizleme", preview,
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return ret == QMessageBox.Yes
        except Exception:
            return True

    def _ask_schedule_delay_ms(self) -> int:
        """Kullanıcıdan zamanlama alır; şimdi için 0 ms, aksi halde hedef zamana göre ms döner."""
        from PySide6.QtWidgets import QInputDialog
        try:
            sched, ok = QInputDialog.getText(self, "Zamanlama", "Gönderim zamanı (boş=hemen, HH:MM veya YYYY-MM-DD HH:MM):")
            if not ok or not sched.strip():
                return 0
            txt = sched.strip()
            from datetime import datetime
            target = None
            try:
                if len(txt) <= 5:  # HH:MM
                    today = datetime.now().strftime('%Y-%m-%d')
                    target = datetime.strptime(f"{today} {txt}", "%Y-%m-%d %H:%M")
                else:
                    target = datetime.strptime(txt, "%Y-%m-%d %H:%M")
            except Exception:
                return 0
            now = datetime.now()
            delta = (target - now).total_seconds()
            return int(max(0, delta) * 1000)
        except Exception:
            return 0

    def _generate_email_draft(self, subject: str) -> str:
        """Basit GPT tabanlı e-posta taslağı üretir."""
        if not self.gpt_manager or not getattr(self.gpt_manager, 'client', None):
            return ""
        sysmsg = "Profesyonel, kısa, ikna edici Türkçe e-posta taslağı yaz. Selam ve kapanış ekle."
        messages = [{"role": "system", "content": sysmsg},
                    {"role": "user", "content": f"Konu: {subject}\nLütfen 4-6 cümlelik taslak yaz."}]
        resp = self.gpt_manager.client.chat.completions.create(
            model=self.gpt_manager.model,
            messages=messages,
            temperature=0.7,
            max_tokens=250
        )
        return resp.choices[0].message.content.strip()

    def _generate_chat_reply(self, text: str) -> str:
        """GPT tabanlı doğal sohbet yanıtı üretir; yoksa basit kural tabanlı yanıt döner."""
        # Hafızadan ilgili notları getir
        try:
            memory_snippets = []
            if self.ai_memory:
                memories = self.ai_memory.retrieve_memory(self.user_id, text)
                memory_snippets = [m.content for m in memories[:3]]
        except Exception:
            memory_snippets = []

        # Persona temelli sistem mesajı
        persona_map = {
            'professional': "Profesyonel ve net yanıtlar ver. Gerektiğinde kısa maddeler kullan.",
            'friendly': "Sıcak ve samimi bir tonla, kısa ve anlaşılır yanıtlar ver.",
            'concise': "Mümkün olduğunca kısa ve direkt yanıt ver."
        }
        style = persona_map.get(getattr(self, 'persona', 'professional'), persona_map['professional'])
        system_prompt = (
            f"Sen B2B otomasyon asistanısın. {style} "
            "Takip sorusu gerekli ise sor. Türkçe yanıtla."
        )
        context_lines = ("\n".join(f"- {m}" for m in memory_snippets)) if memory_snippets else ""
        user_with_context = text if not context_lines else f"Kullanıcı bağlamı:\n{context_lines}\n\nSoru: {text}"

        # GPT mevcutsa kullan
        try:
            if self.gpt_manager and hasattr(self.gpt_manager, 'client') and self.gpt_manager.client:
                messages = [{"role": "system", "content": system_prompt}]
                # Son 6 mesajı ekle
                for role, content in self._chat_context[-6:]:
                    messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": user_with_context})
                resp = self.gpt_manager.client.chat.completions.create(
                    model=self.gpt_manager.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                reply = resp.choices[0].message.content.strip()
                # Token kullanımı bilgisi
                try:
                    usage = getattr(resp, 'usage', None)
                    if usage:
                        used = []
                        for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
                            val = getattr(usage, key, None) if hasattr(usage, key) else usage.get(key) if isinstance(usage, dict) else None
                            if val is not None:
                                used.append(f"{key}={val}")
                        if used:
                            self.chat_history.append("🧮 Kullanım: " + ", ".join(used))
                except Exception:
                    pass
                # Konuşma bağlamını güncelle
                self._chat_context.append(("user", text))
                self._chat_context.append(("assistant", reply))
                if len(self._chat_context) > 30:
                    self._chat_context = self._chat_context[-30:]
                return reply
        except Exception as e:
            try:
                logger.warning(f"GPT sohbet yanıtı üretilemedi: {e}")
            except Exception:
                pass

        # Basit fallback
        if text.endswith("?"):
            return "Bu konuda neyi merak ediyorsunuz, biraz daha açabilir misiniz?"
        return "Anladım. Biraz daha detay verebilir misiniz?"

    def _append_user_message(self, text: str):
        ts = datetime.now().strftime("%H:%M")
        html = (
            f"<div style='margin:8px 0; display:flex; justify-content:flex-end;'>"
            f"<div style='max-width:70%; background:#2a2a3e; color:#e0f2f7; padding:10px 12px;"
            f" border-radius:12px 12px 2px 12px; box-shadow:0 2px 8px rgba(0,0,0,0.25);'>"
            f"<div style='font-size:13px; white-space:pre-wrap;'>{self._escape_html(text)}</div>"
            f"<div style='text-align:right; font-size:10px; opacity:0.7; margin-top:6px;'>{ts}</div>"
            f"</div></div>"
        )
        self.chat_history.append(html)

    def _append_bot_message(self, text: str, sentiment: str = ""):
        ts = datetime.now().strftime("%H:%M")
        tag = f"<span style='margin-left:6px; font-size:10px; opacity:0.7;'>({sentiment})</span>" if sentiment else ""
        html = (
            f"<div style='margin:8px 0; display:flex; justify-content:flex-start;'>"
            f"<div style='max-width:70%; background:#1f1f2b; color:#e0f2f7; padding:10px 12px;"
            f" border-radius:12px 12px 12px 2px; border:1px solid #2a2a3e; box-shadow:0 2px 8px rgba(0,0,0,0.25);'>"
            f"<div style='font-size:12px; margin-bottom:4px; opacity:0.8;'>🤖 Asistan {tag}</div>"
            f"<div style='font-size:13px; white-space:pre-wrap;'>{self._escape_html(text)}</div>"
            f"<div style='text-align:right; font-size:10px; opacity:0.7; margin-top:6px;'>{ts}</div>"
            f"</div></div>"
        )
        self.chat_history.append(html)

    def _escape_html(self, s: str) -> str:
        try:
            return (s.replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace("\n", "<br>"))
        except Exception:
            return s

    def _learn_from_interaction(self, user_text: str, assistant_text: str, intent: str = 'chat'):
        """Sohbet etkileşiminden hafıza ve kalıp öğrenmesi yap."""
        try:
            # Kısa vadeli hafıza olarak kullanıcı niyeti ve yanıtı sakla
            if self.ai_memory:
                from ai_memory_personalization import MemoryType, EmotionalState, InteractionType
                # Duygu tespiti
                emo = EmotionalState.NEUTRAL
                try:
                    sentiment = self._analyze_sentiment(user_text)
                    if sentiment == 'positive':
                        emo = EmotionalState.POSITIVE
                    elif sentiment == 'negative':
                        emo = EmotionalState.NEGATIVE
                except Exception:
                    pass
                self.ai_memory.store_memory(
                    user_id=self.user_id,
                    content=f"User: {user_text}\nAssistant: {assistant_text}",
                    memory_type=MemoryType.SHORT_TERM,
                    importance=0.6,
                    emotional_context=emo,
                    business_context="assistant_chat",
                    tags=[intent]
                )
                # Basit etkileşim kalıbı güncellemesi
                self.ai_memory.recognize_interaction_pattern(
                    user_id=self.user_id,
                    interaction_type=InteractionType.TEXT_QUERY,
                    success=True,
                    topics=[],
                    emotional_state=emo
                )
        except Exception:
            pass

    def _analyze_sentiment(self, text: str) -> str:
        """NLTK mevcutsa sentiment skorunu pozitif/negatif/nötr olarak döndürür."""
        if not self.ai_memory:
            return ""
        try:
            analyzer = self.ai_memory.ai_models.get('sentiment') if hasattr(self.ai_memory, 'ai_models') else None
            if not analyzer:
                return ""
            scores = analyzer.polarity_scores(text)
            comp = scores.get('compound', 0)
            if comp >= 0.3:
                return 'positive'
            if comp <= -0.3:
                return 'negative'
            return 'neutral'
        except Exception:
            return ""

    def _resolve_missing_slots(self, parsed: dict, original_text: str, via_chat: bool = False):
        """NLP çıktısında eksik olan alanları GUI üzerinden kullanıcıya sorarak tamamlar."""
        if not parsed or parsed.get('intent') in (None, 'hata'):
            return None
        intent = parsed.get('intent')
        filled = dict(parsed)
        from PySide6.QtWidgets import QInputDialog
        if intent in ("firma_ara", "firma_ara_ve_kampanya"):
            if not filled.get('query'):
                q, ok = QInputDialog.getText(self, "Arama Sorgusu", "Hangi sektör/anahtar kelime?")
                if not ok or not q.strip():
                    return None
                filled['query'] = q.strip()
            if not filled.get('location'):
                loc, ok = QInputDialog.getText(self, "Konum", "Hangi şehir/bölge?")
                if not ok or not loc.strip():
                    return None
                filled['location'] = loc.strip()
            if not filled.get('max_results'):
                n, ok = QInputDialog.getInt(self, "Maksimum Sonuç", "Kaç firma bulunsun?", 50, 1, 500, 1)
                if not ok:
                    return None
                filled['max_results'] = int(n)
        if intent in ("kampanya_gonder", "firma_ara_ve_kampanya"):
            if not filled.get('campaign_name'):
                camp, ok = QInputDialog.getText(self, "Kampanya Adı", "Kampanya adı/konusu?")
                if not ok or not camp.strip():
                    return None
                filled['campaign_name'] = camp.strip()
        if intent == "analiz_et" and not filled.get('target_firm_name'):
            firm, ok = QInputDialog.getText(self, "Hedef Firma", "Analiz edilecek firma adı?")
            if not ok or not firm.strip():
                return None
            filled['target_firm_name'] = firm.strip()
        return filled

    def _start_workflow_from_parsed(self, parsed: dict, original_text: str, original_parsed: dict):
        """Doldurulmuş NLP sonucundan iş akışı başlatır ve öğrenmeyi kaydeder."""
        if not hasattr(self, 'engine') or not self.engine or not self.engine.is_ready:
            self.update_log_display("❌ Motor hazır değil!")
            return

        if parsed.get('campaign_name') and not parsed.get('campaign_template'):
            campaign_name = parsed.get('campaign_name')
            parsed['campaign_template'] = {
                'subject': campaign_name,
                'instructions': f"{campaign_name} için alıcıya özel, kısa ve ikna edici bir tanıtım içeriği üret."
            }

        try:
            workflow_id = f"workflow_{int(time.time())}"
            ok = self.engine.orchestrator.start_new_workflow(workflow_id, parsed, self.emit_feedback)

            if ok:
                self.update_log_display(f"🚀 Yeni iş akışı '{workflow_id}' başlatıldı.")
                try:
                    self.engine.optimizer.add_nlp_feedback(original_text, original_parsed, True, correct_data=parsed)
                except Exception:
                    pass
            else:
                self.update_log_display("⚠️ Yeni iş akışı başlatılamadı (mevcut iş akışı çalışıyor olabilir).")

        except Exception as e:
            self.update_log_display(f"❌ İş akışı başlatma hatası: {e}")
            return False

    def apply_modern_styles(self):
        """Modern ve renkli stil uygulaması"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f1e;
            }
            
            QFrame#leftPanel, QFrame#centerPanel, QFrame#rightPanel {
                background-color: #1a1a2e;
                border-radius: 15px;
                border: 1px solid #2a2a3e;
            }
            
            QFrame#commandSection, QFrame#logSection, QFrame#progressContainer {
                background-color: rgba(42, 42, 62, 0.5);
                border-radius: 10px;
                padding: 15px;
            }
            
            QLabel {
                color: #ecf0f1;
            }
            
            QLineEdit {
                background-color: #2a2a3e;
                color: white;
                border: 2px solid #3a3a4e;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #5858D6;
                background-color: #2f2f3e;
            }
            QLineEdit[placeholderText*="ara"] {
                min-width: 200px;
                padding-left: 10px;
            }
            
            QComboBox {
                background-color: #2a2a3e;
                color: white;
                border: 2px solid #3a3a4e;
                border-radius: 8px;
                padding: 8px;
            }
            QComboBox:hover {
                border: 2px solid #5858D6;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a3e;
                color: white;
                selection-background-color: #5858D6;
            }
            
            QTextEdit {
                background-color: #16161e;
                color: #e0f2f7;
                border: 2px solid #2a2a3e;
                border-radius: 10px;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
            QFrame#chatPanel {
                background-color: #121223;
                border: 1px solid #2a2a3e;
                border-radius: 12px;
            }
            QFrame#chatPanel QLabel {
                color: #e8eaf6;
            }
            
            QTableWidget {
                background-color: #16161e;
                color: #e0f2f7;
                gridline-color: #2a2a3e;
                border: 2px solid #2a2a3e;
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #5858D6;
            }
            QHeaderView::section {
                background-color: #2a2a3e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            
            QPushButton {
                background-color: #5858D6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6868E6;
            }
            QPushButton:pressed {
                background-color: #4848C6;
            }
            QPushButton:disabled {
                background-color: #3a3a4e;
                color: #5a5a6e;
            }
            QPushButton#danger {
                background-color: #C43D4B;
            }
            QPushButton#warning {
                background-color: #CA7137;
            }
            
            QProgressBar {
                background-color: #2a2a3e;
                color: white;
                border: 2px solid #3a3a4e;
                border-radius: 10px;
                text-align: center;
                height: 30px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5858D6, stop:0.5 #30A24C, stop:1 #CA7137);
                border-radius: 8px;
            }
            
            QScrollBar:vertical {
                background-color: #1a1a2e;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a4e;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5858D6;
            }
        """)

    def setup_menu(self):
        """Menü çubuğu"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1a1a2e;
                color: white;
                padding: 5px;
            }
            QMenuBar::item:selected {
                background-color: #5858D6;
            }
            QMenu {
                background-color: #2a2a3e;
                color: white;
            }
            QMenu::item:selected {
                background-color: #5858D6;
            }
        """)
        
        file_menu = menubar.addMenu("📁 Dosya")
        view_menu = menubar.addMenu("👁️ Görünüm")
        settings_menu = menubar.addMenu("⚙️ Ayarlar")
        help_menu = menubar.addMenu("❓ Yardım")

        save_logs_action = file_menu.addAction("💾 Logları Kaydet...")
        save_logs_action.triggered.connect(self.save_logs)

        self.dark_mode = True
        toggle_theme_action = view_menu.addAction("🎨 Tema Değiştir")
        toggle_theme_action.triggered.connect(self.toggle_theme)

        edit_tokens_action = settings_menu.addAction("📱 Telegram Ayarları...")
        edit_tokens_action.triggered.connect(self.edit_telegram_settings)

        about_action = help_menu.addAction("ℹ️ Hakkında")
        about_action.triggered.connect(self.show_about)

    def show_about(self):
        """Hakkında penceresi"""
        QMessageBox.about(
            self,
            "ℹ️ Hakkında",
            """
            <h2>🚀 B2B Otomasyon Motoru v3.0</h2>
            <p><b>Gelişmiş Kontrol Paneli</b></p>
            <p>Modern, renkli ve kullanıcı dostu arayüz ile<br>
            7/24 kesintisiz otomasyon yönetimi.</p>
            <hr>
            <p><b>Özellikler:</b></p>
            <ul>
                <li>🎯 Akıllı komut yönetimi</li>
                <li>📊 Gerçek zamanlı istatistikler</li>
                <li>⚡ Hızlı komut kısayolları</li>
                <li>📝 Detaylı log takibi</li>
                <li>🎨 Modern ve renkli tasarım</li>
                <li>🔧 Main2 entegrasyonu (WhatsApp, Vapi AI, GPT)</li>
            </ul>
            """
        )
    
    def cleanup_resources(self):
        """Kapatmadan önce tüm kaynakları temizle."""
        try:
            if hasattr(self, 'engine') and self.engine:
                self.engine.stop_engine()
        except Exception:
            pass
        # Tracking GUI özel temizlik gerekiyorsa burada yapılabilir
        # API Manager/DB kapatma kullanıcı koduna bağlı; burada sadece referanslar temizlenir
        try:
            self.tracking_gui_manager = None
            self.analytics_dashboard = None
            self.api_manager = None
            self.automation_builder = None
        except Exception:
            pass

    def closeEvent(self, event):
        """Pencere kapanırken kaynakları güvenli şekilde kapat."""
        try:
            self.cleanup_resources()
        finally:
            super().closeEvent(event)
    
    def load_main2_config(self):
        """Main2 config dosyasını yükle"""
        try:
            import json
            import os
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Uygulama geneli için sakla
                self.config = config
                    
                # GPT API key
                if self.gpt_manager and config.get('openai_api_key'):
                    self.gpt_manager.set_api_key(config['openai_api_key'])
                    # Model varsayılanı
                    try:
                        if config.get('gpt_model'):
                            self.gpt_manager.model = config.get('gpt_model')
                    except Exception:
                        pass
                    
                # Vapi API key
                if self.vapi_manager and config.get('vapi_api_key'):
                    self.vapi_manager.set_api_key(config['vapi_api_key'])
                    self.vapi_manager.set_phone_number_id(config.get('vapi_phone_number_id'))
                # user_id
                try:
                    if config.get('user_id'):
                        self.user_id = str(config.get('user_id'))
                except Exception:
                    pass
                    
        except Exception as e:
            logger.warning(f"Main2 config yüklenemedi: {e}")
    
    def create_main2_features_panel(self):
        """Main2 özellikleri paneli"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Başlık
        title = QLabel("🔧 Main2 Özellikleri")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(title)
        
        # GPT Manager bölümü
        if self.gpt_manager:
            gpt_section = QFrame()
            gpt_layout = QVBoxLayout(gpt_section)
            
            gpt_header = QLabel("🧠 GPT Manager")
            gpt_header.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
            gpt_layout.addWidget(gpt_header)
            
            # API Key girişi
            api_key_layout = QHBoxLayout()
            api_label = QLabel("OpenAI API Key:")
            api_input = QLineEdit()
            api_input.setPlaceholderText("API Key'inizi girin")
            api_input.setEchoMode(QLineEdit.Password)
            
            save_key_btn = QPushButton("Kaydet")
            save_key_btn.clicked.connect(lambda: self.save_gpt_api_key(api_input.text()))
            
            api_key_layout.addWidget(api_label)
            api_key_layout.addWidget(api_input)
            api_key_layout.addWidget(save_key_btn)
            gpt_layout.addLayout(api_key_layout)

            # Hızlı GPT prompt
            prompt_row = QHBoxLayout()
            self.quick_gpt_prompt = QLineEdit()
            self.quick_gpt_prompt.setPlaceholderText("GPT'ye hızlı soru sor...")
            ask_btn = QPushButton("Sor")
            def _ask_gpt():
                q = self.quick_gpt_prompt.text().strip()
                if not q:
                    return
                try:
                    reply = self._quick_gpt_ask(q)
                    if reply:
                        self.chat_history.append(f"💡 GPT: {reply}")
                except Exception as e:
                    self.update_log_display(f"❌ GPT hata: {e}")
            ask_btn.clicked.connect(_ask_gpt)
            prompt_row.addWidget(self.quick_gpt_prompt)
            prompt_row.addWidget(ask_btn)
            gpt_layout.addLayout(prompt_row)

            # Main2 yöneticilerini yeniden yükle
            reload_row = QHBoxLayout()
            main2_reload_btn = QPushButton("Main2 Yöneticilerini Yeniden Yükle")
            main2_reload_btn.clicked.connect(self._reload_main2_managers)
            reload_row.addStretch()
            reload_row.addWidget(main2_reload_btn)
            gpt_layout.addLayout(reload_row)
            
            layout.addWidget(gpt_section)
        
        # Vapi Manager bölümü
        if self.vapi_manager:
            vapi_section = QFrame()
            vapi_layout = QVBoxLayout(vapi_section)
            
            vapi_header = QLabel("📞 Vapi Manager")
            vapi_header.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
            vapi_layout.addWidget(vapi_header)
            
            # API Key girişi
            vapi_key_layout = QHBoxLayout()
            vapi_label = QLabel("Vapi API Key:")
            vapi_input = QLineEdit()
            vapi_input.setPlaceholderText("Vapi API Key'inizi girin")
            vapi_input.setEchoMode(QLineEdit.Password)
            
            vapi_save_btn = QPushButton("Kaydet")
            vapi_save_btn.clicked.connect(lambda: self.save_vapi_api_key(vapi_input.text()))
            
            vapi_key_layout.addWidget(vapi_label)
            vapi_key_layout.addWidget(vapi_input)
            vapi_key_layout.addWidget(vapi_save_btn)
            vapi_layout.addLayout(vapi_key_layout)
            
            # Test bağlantısı butonu
            test_btn = QPushButton("Bağlantıyı Test Et")
            test_btn.clicked.connect(self.test_vapi_connection)
            vapi_layout.addWidget(test_btn)

            # WhatsApp test mesajı (mümkünse)
            try:
                if WhatsAppAutoSender:
                    wa_section = QFrame()
                    wa_layout = QHBoxLayout(wa_section)
                    self.wa_phone = QLineEdit()
                    self.wa_phone.setPlaceholderText("Alıcı Telefon (+90...)")
                    self.wa_text = QLineEdit()
                    self.wa_text.setPlaceholderText("Mesaj metni")
                    wa_send_btn = QPushButton("WhatsApp Gönder")
                    wa_send_btn.clicked.connect(self._send_whatsapp_test)
                    wa_layout.addWidget(self.wa_phone)
                    wa_layout.addWidget(self.wa_text)
                    wa_layout.addWidget(wa_send_btn)
                    vapi_layout.addWidget(wa_section)
            except Exception:
                pass
            
            layout.addWidget(vapi_section)
        
        layout.addStretch()
        return panel

    def _reload_main2_managers(self):
        try:
            import importlib, os
            # main2.py dosyasını yeniden yüklemeyi dene
            if 'main2' in sys.modules:
                importlib.reload(sys.modules['main2'])
                mod = sys.modules['main2']
                self.update_log_display("🔄 main2 modülü yeniden yüklendi")
            else:
                import importlib.util
                spec = importlib.util.spec_from_file_location("main2", "main2.py")
                if not spec or not spec.loader:
                    raise RuntimeError("main2 bulunamadı")
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sys.modules['main2'] = mod
                self.update_log_display("📦 main2 modülü yüklendi")
            # Yöneticileri yeniden oluştur
            self.gpt_manager = getattr(mod, 'GPTManager', None)() if getattr(mod, 'GPTManager', None) else None
            self.vapi_manager = getattr(mod, 'VapiManager', None)() if getattr(mod, 'VapiManager', None) else None
            self.whatsapp_auto_sender = getattr(mod, 'WhatsAppAutoSender', None)() if getattr(mod, 'WhatsAppAutoSender', None) else None
            # Config’i tekrar uygula
            try:
                self.load_main2_config()
            except Exception:
                pass
            self.update_log_display("✅ Main2 yöneticileri yeniden yüklendi")
        except Exception as e:
            self.update_log_display(f"❌ Main2 yeniden yüklenemedi: {e}")

    def _quick_gpt_ask(self, question: str) -> str:
        if not self.gpt_manager or not getattr(self.gpt_manager, 'client', None):
            raise RuntimeError("GPT yapılandırılmadı")
        messages = [{"role": "system", "content": "Kısa ve net yanıt ver. Türkçe konuş."},
                    {"role": "user", "content": question}]
        resp = self.gpt_manager.client.chat.completions.create(
            model=self.gpt_manager.model,
            messages=messages,
            temperature=0.5,
            max_tokens=200
        )
        return resp.choices[0].message.content.strip()

    def _send_whatsapp_test(self):
        try:
            phone = self.wa_phone.text().strip()
            text = self.wa_text.text().strip()
            if not phone or not text:
                QMessageBox.information(self, "WhatsApp", "Telefon ve mesaj zorunludur.")
                return
            if not WhatsAppAutoSender:
                QMessageBox.warning(self, "WhatsApp", "WhatsAppAutoSender mevcut değil.")
                return
            if not getattr(self, 'whatsapp_auto_sender', None):
                try:
                    self.whatsapp_auto_sender = WhatsAppAutoSender()
                except Exception as e:
                    QMessageBox.critical(self, "WhatsApp", f"Başlatılamadı: {e}")
                    return
            ok = self.whatsapp_auto_sender.send_message(phone, text)
            if ok:
                self.update_log_display("✅ WhatsApp test mesajı gönderildi")
            else:
                self.update_log_display("❌ WhatsApp mesajı gönderilemedi")
        except Exception as e:
            self.update_log_display(f"❌ WhatsApp hata: {e}")
    
    def save_gpt_api_key(self, api_key):
        """GPT API key'i kaydet"""
        if not self.gpt_manager:
            return
        
        if self.gpt_manager.set_api_key(api_key):
            self.update_log_display("✅ GPT API key kaydedildi")
            QMessageBox.information(self, "Başarılı", "GPT API key başarıyla kaydedildi")
        else:
            self.update_log_display("❌ GPT API key kaydedilemedi")
            QMessageBox.warning(self, "Hata", "GPT API key kaydedilemedi")
    
    def save_vapi_api_key(self, api_key):
        """Vapi API key'i kaydet"""
        if not self.vapi_manager:
            return
        
        if self.vapi_manager.set_api_key(api_key):
            self.update_log_display("✅ Vapi API key kaydedildi")
            QMessageBox.information(self, "Başarılı", "Vapi API key başarıyla kaydedildi")
        else:
            self.update_log_display("❌ Vapi API key kaydedilemedi")
            QMessageBox.warning(self, "Hata", "Vapi API key kaydedilemedi")
    
    def test_vapi_connection(self):
        """Vapi bağlantısını test et"""
        if not self.vapi_manager:
            QMessageBox.warning(self, "Hata", "Vapi Manager bulunamadı")
            return
        
        self.update_log_display("🔄 Vapi bağlantısı test ediliyor...")
        
        result = self.vapi_manager.test_connection()
        
        if result:
            self.update_log_display("✅ Vapi bağlantısı başarılı!")
            QMessageBox.information(self, "Başarılı", "Vapi bağlantısı başarılı!")
        else:
            self.update_log_display("❌ Vapi bağlantısı başarısız!")
            QMessageBox.warning(self, "Hata", "Vapi bağlantısı başarısız. Lütfen API key'inizi kontrol edin.")
    
    def create_ai_nlp_panel(self):
        """AI NLP özellikleri paneli"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Başlık
        title = QLabel("🧠 Gelişmiş AI NLP Parser")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(title)
        
        # İstatistikler
        stats_section = QFrame()
        stats_layout = QVBoxLayout(stats_section)
        
        stats_header = QLabel("📊 NLP İstatistikleri")
        stats_header.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        stats_layout.addWidget(stats_header)
        
        self.nlp_stats_label = QLabel("Yükleniyor...")
        self.nlp_stats_label.setStyleSheet("color: #e0f2f7; padding: 10px;")
        stats_layout.addWidget(self.nlp_stats_label)
        
        refresh_stats_btn = QPushButton("🔄 İstatistikleri Yenile")
        refresh_stats_btn.clicked.connect(self.update_nlp_statistics)
        stats_layout.addWidget(refresh_stats_btn)
        
        layout.addWidget(stats_section)
        
        # Özellikler
        features_section = QFrame()
        features_layout = QVBoxLayout(features_section)
        
        features_header = QLabel("✨ AI NLP Özellikleri")
        features_header.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        features_layout.addWidget(features_header)
        
        features_text = """
        <ul style='color: #e0f2f7; margin: 10px;'>
            <li>🧠 Kendi kendini eğiten pattern matching</li>
            <li>📊 Güven skoru ile çok katmanlı analiz</li>
            <li>🎯 Context-aware parsing (bağlam farkındalığı)</li>
            <li>🔍 Gelişmiş entity recognition</li>
            <li>📈 Otomatik iyileştirme mekanizması</li>
            <li>💾 Öğrenme verilerini otomatik kaydetme</li>
            <li>⚡ Yüksek performanslı analiz</li>
            <li>🌐 Gemini API'sız tam bağımsız çalışma</li>
        </ul>
        """
        
        features_label = QLabel(features_text)
        features_label.setStyleSheet("color: #e0f2f7; padding: 10px;")
        features_layout.addWidget(features_label)
        
        layout.addWidget(features_section)
        
        layout.addStretch()
        return panel

    def create_settings_panel(self):
        """Ayarlar sekmesi - API anahtarları, kullanıcı, model ve tercihler."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)

        title = QLabel("⚙️ Uygulama Ayarları")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(title)

        # API Ayarları
        api_section = QFrame()
        api_layout = QVBoxLayout(api_section)
        api_layout.setSpacing(8)
        api_header = QLabel("🔑 API Ayarları")
        api_header.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        api_layout.addWidget(api_header)
        # OpenAI key
        row1 = QHBoxLayout()
        self.settings_openai_key = QLineEdit()
        self.settings_openai_key.setPlaceholderText("OpenAI API Key")
        self.settings_openai_key.setEchoMode(QLineEdit.Password)
        row1.addWidget(QLabel("OpenAI:"))
        row1.addWidget(self.settings_openai_key)
        test_openai_btn = QPushButton("Test")
        test_openai_btn.clicked.connect(self._test_openai_api)
        row1.addWidget(test_openai_btn)
        api_layout.addLayout(row1)
        # Vapi key
        row2 = QHBoxLayout()
        self.settings_vapi_key = QLineEdit()
        self.settings_vapi_key.setPlaceholderText("Vapi API Key")
        self.settings_vapi_key.setEchoMode(QLineEdit.Password)
        row2.addWidget(QLabel("Vapi:"))
        row2.addWidget(self.settings_vapi_key)
        test_vapi_btn = QPushButton("Test")
        test_vapi_btn.clicked.connect(self._test_vapi_api)
        row2.addWidget(test_vapi_btn)
        api_layout.addLayout(row2)
        # Vapi phone id
        row3 = QHBoxLayout()
        self.settings_vapi_phone = QLineEdit()
        self.settings_vapi_phone.setPlaceholderText("Vapi Phone Number ID")
        row3.addWidget(QLabel("Vapi Phone ID:"))
        row3.addWidget(self.settings_vapi_phone)
        api_layout.addLayout(row3)
        # Email test
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Email:"))
        email_test_btn = QPushButton("Test")
        email_test_btn.clicked.connect(self._test_email_api)
        row4.addStretch()
        row4.addWidget(email_test_btn)
        api_layout.addLayout(row4)
        layout.addWidget(api_section)

        # Kullanıcı ve Model
        um_section = QFrame()
        um_layout = QVBoxLayout(um_section)
        um_layout.setSpacing(8)
        um_header = QLabel("👤 Kullanıcı & 🧠 Model")
        um_header.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        um_layout.addWidget(um_header)
        r4 = QHBoxLayout()
        self.settings_user_id = QLineEdit()
        self.settings_user_id.setPlaceholderText("Kullanıcı ID")
        r4.addWidget(QLabel("User ID:"))
        r4.addWidget(self.settings_user_id)
        um_layout.addLayout(r4)
        r5 = QHBoxLayout()
        self.settings_model = QLineEdit()
        self.settings_model.setPlaceholderText("GPT Model (örn: gpt-4o-mini)")
        r5.addWidget(QLabel("Model:"))
        r5.addWidget(self.settings_model)
        um_layout.addLayout(r5)
        layout.addWidget(um_section)

        # Tercihler
        pref_section = QFrame()
        pref_layout = QHBoxLayout(pref_section)
        self.settings_tts_toggle = QPushButton("🔊 TTS: Açık" if self.voice_tts_enabled else "🔈 TTS: Kapalı")
        self.settings_tts_toggle.clicked.connect(self.toggle_tts)
        self.settings_learning_toggle = QPushButton("🧠 Öğrenme: Açık" if self.learning_enabled else "🧠 Öğrenme: Kapalı")
        self.settings_learning_toggle.clicked.connect(self.toggle_learning_mode)
        self.settings_theme_toggle = QPushButton("🎨 Tema Değiştir")
        self.settings_theme_toggle.clicked.connect(self.toggle_theme)
        # Persona seçimi
        self.settings_persona = QComboBox()
        self.settings_persona.addItems(["professional", "friendly", "concise"])
        try:
            self.settings_persona.setCurrentText(getattr(self, 'persona', 'professional'))
        except Exception:
            pass
        pref_layout.addWidget(self.settings_tts_toggle)
        pref_layout.addWidget(self.settings_learning_toggle)
        pref_layout.addWidget(self.settings_theme_toggle)
        pref_layout.addWidget(QLabel("Persona:"))
        pref_layout.addWidget(self.settings_persona)
        pref_layout.addStretch()
        layout.addWidget(pref_section)

        # Kaydet / Uygula
        save_bar = QHBoxLayout()
        self.settings_save_btn = QPushButton("💾 Kaydet ve Uygula")
        self.settings_save_btn.clicked.connect(self.save_settings_from_panel)
        self.settings_reload_cfg_btn = QPushButton("🔄 Konfigürasyonu Yeniden Yükle")
        self.settings_reload_cfg_btn.clicked.connect(self.load_main2_config)
        save_bar.addStretch()
        save_bar.addWidget(self.settings_save_btn)
        save_bar.addWidget(self.settings_reload_cfg_btn)
        layout.addLayout(save_bar)

        # Mevcut config ile alanları doldur
        self._prefill_settings_fields()
        layout.addStretch()
        return panel

    def _prefill_settings_fields(self):
        try:
            # Mümkünse mevcut self.config'ten doldur
            cfg = getattr(self, 'config', {}) if hasattr(self, 'config') else {}
            self.settings_openai_key.setText(str(cfg.get('openai_api_key', '')))
            self.settings_vapi_key.setText(str(cfg.get('vapi_api_key', '')))
            self.settings_vapi_phone.setText(str(cfg.get('vapi_phone_number_id', '')))
            self.settings_user_id.setText(str(cfg.get('user_id', getattr(self, 'user_id', ''))))
            # Model
            current_model = ''
            try:
                if self.gpt_manager and hasattr(self.gpt_manager, 'model'):
                    current_model = self.gpt_manager.model or ''
            except Exception:
                current_model = ''
            self.settings_model.setText(current_model)
        except Exception:
            pass

    def save_settings_from_panel(self):
        """Ayarları config.json'a kaydedip anında uygula."""
        try:
            import json, os
            cfg = {}
            if os.path.exists('config.json'):
                try:
                    with open('config.json', 'r', encoding='utf-8') as f:
                        cfg = json.load(f)
                except Exception:
                    cfg = {}
            # Formdan oku
            cfg['openai_api_key'] = self.settings_openai_key.text().strip()
            cfg['vapi_api_key'] = self.settings_vapi_key.text().strip()
            cfg['vapi_phone_number_id'] = self.settings_vapi_phone.text().strip()
            cfg['user_id'] = self.settings_user_id.text().strip() or self.user_id
            model_val = self.settings_model.text().strip()
            persona_val = self.settings_persona.currentText()
            cfg['gpt_model'] = model_val
            cfg['persona'] = persona_val
            # Yaz
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            # Belleğe al
            self.config = cfg
            self.user_id = cfg.get('user_id', self.user_id)
            self.persona = cfg.get('persona', self.persona)
            # Anında uygula
            if self.gpt_manager and cfg.get('openai_api_key'):
                try:
                    self.gpt_manager.set_api_key(cfg['openai_api_key'])
                except Exception:
                    pass
            if self.vapi_manager and cfg.get('vapi_api_key'):
                try:
                    self.vapi_manager.set_api_key(cfg['vapi_api_key'])
                    self.vapi_manager.set_phone_number_id(cfg.get('vapi_phone_number_id'))
                except Exception:
                    pass
            if self.gpt_manager and model_val:
                try:
                    self.gpt_manager.model = model_val
                except Exception:
                    pass
            QMessageBox.information(self, "Ayarlar", "Ayarlar kaydedildi ve uygulandı.")
        except Exception as e:
            QMessageBox.critical(self, "Ayarlar", f"Ayarlar kaydedilemedi: {e}")

    def _test_openai_api(self):
        try:
            key = self.settings_openai_key.text().strip()
            if not key:
                QMessageBox.information(self, "OpenAI", "Lütfen API key girin.")
                return
            if not self.gpt_manager:
                QMessageBox.information(self, "OpenAI", "GPT Manager yok.")
                return
            self.gpt_manager.set_api_key(key)
            msg = [{"role": "user", "content": "ping"}]
            resp = self.gpt_manager.client.chat.completions.create(model=self.gpt_manager.model, messages=msg, max_tokens=1)
            QMessageBox.information(self, "OpenAI", "✅ Bağlantı başarılı")
        except Exception as e:
            QMessageBox.critical(self, "OpenAI", f"❌ Test başarısız: {e}")

    def _test_vapi_api(self):
        try:
            if not self.vapi_manager:
                QMessageBox.information(self, "Vapi", "Vapi Manager yok.")
                return
            ok = self.vapi_manager.test_connection()
            if ok:
                QMessageBox.information(self, "Vapi", "✅ Bağlantı başarılı")
            else:
                QMessageBox.critical(self, "Vapi", "❌ Test başarısız")
        except Exception as e:
            QMessageBox.critical(self, "Vapi", f"❌ Test hatası: {e}")

    def _test_email_api(self):
        try:
            if not EMAIL_AVAILABLE:
                QMessageBox.information(self, "E-posta", "EmailManager bulunamadı.")
                return
            # Sadece sınıfın örneklenebilirliğini test edelim
            em = EmailManager()
            if hasattr(em, 'send_email') or hasattr(em, 'send'):
                QMessageBox.information(self, "E-posta", "✅ EmailManager hazır görünüyor")
            else:
                QMessageBox.critical(self, "E-posta", "❌ Uygun gönderim fonksiyonu yok")
        except Exception as e:
            QMessageBox.critical(self, "E-posta", f"❌ Test başarısız: {e}")

    def create_core_system_panel(self):
        """Ana sistem (main.py) bileşenlerini kontrol paneli."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        title = QLabel("🧩 Ana Sistem Bileşenleri")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; padding: 10px;")
        layout.addWidget(title)

        # Database
        db_section = QFrame()
        db_layout = QHBoxLayout(db_section)
        db_label = QLabel("Veritabanı: ")
        self.core_db_status = QLabel("Hazır" if self.db else "YOK")
        self.core_db_status.setStyleSheet("color: #30A24C;" if self.db else "color: #C43D4B;")
        db_reload = QPushButton("Yeniden Başlat")
        db_reload.clicked.connect(self._reload_database)
        db_layout.addWidget(db_label)
        db_layout.addWidget(self.core_db_status)
        db_layout.addStretch()
        db_layout.addWidget(db_reload)
        layout.addWidget(db_section)

        # API Manager
        api_section = QFrame()
        api_layout = QHBoxLayout(api_section)
        api_label = QLabel("API Manager: ")
        self.core_api_status = QLabel("Hazır" if self.api_manager else "YOK")
        self.core_api_status.setStyleSheet("color: #30A24C;" if self.api_manager else "color: #C43D4B;")
        api_reload = QPushButton("Yeniden Başlat")
        api_reload.clicked.connect(self._reload_api_manager)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.core_api_status)
        api_layout.addStretch()
        api_layout.addWidget(api_reload)
        layout.addWidget(api_section)

        # Analytics Dashboard
        an_section = QFrame()
        an_layout = QHBoxLayout(an_section)
        an_label = QLabel("Analytics Dashboard: ")
        self.core_an_status = QLabel("Hazır" if self.analytics_dashboard else "YOK")
        self.core_an_status.setStyleSheet("color: #30A24C;" if self.analytics_dashboard else "color: #C43D4B;")
        an_reload = QPushButton("Yeniden Başlat")
        an_reload.clicked.connect(self._reload_analytics)
        an_layout.addWidget(an_label)
        an_layout.addWidget(self.core_an_status)
        an_layout.addStretch()
        an_layout.addWidget(an_reload)
        layout.addWidget(an_section)

        # Automation Builder
        ab_section = QFrame()
        ab_layout = QHBoxLayout(ab_section)
        ab_label = QLabel("Automation Builder: ")
        self.core_ab_status = QLabel("Hazır" if self.automation_builder else "YOK")
        self.core_ab_status.setStyleSheet("color: #30A24C;" if self.automation_builder else "color: #C43D4B;")
        ab_reload = QPushButton("Yeniden Başlat")
        ab_reload.clicked.connect(self._reload_automation_builder)
        ab_layout.addWidget(ab_label)
        ab_layout.addWidget(self.core_ab_status)
        ab_layout.addStretch()
        ab_layout.addWidget(ab_reload)
        layout.addWidget(ab_section)

        # Tracking GUI
        tr_section = QFrame()
        tr_layout = QHBoxLayout(tr_section)
        tr_label = QLabel("Tracking GUI: ")
        self.core_tr_status = QLabel("Hazır" if self.tracking_gui_manager else "YOK")
        self.core_tr_status.setStyleSheet("color: #30A24C;" if self.tracking_gui_manager else "color: #C43D4B;")
        tr_reload = QPushButton("Yeniden Başlat")
        tr_reload.clicked.connect(self._reload_tracking_gui)
        tr_layout.addWidget(tr_label)
        tr_layout.addWidget(self.core_tr_status)
        tr_layout.addStretch()
        tr_layout.addWidget(tr_reload)
        layout.addWidget(tr_section)

        # Durum yenile
        refresh_row = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Durumu Yenile")
        refresh_btn.clicked.connect(self._refresh_core_status)
        refresh_row.addStretch()
        refresh_row.addWidget(refresh_btn)
        layout.addLayout(refresh_row)

        layout.addStretch()
        return panel

    def _reload_database(self):
        try:
            if DATABASE_AVAILABLE:
                self.db = Database()
                self.update_log_display("✅ Database yeniden başlatıldı")
                try:
                    self.core_db_status.setText("Hazır")
                    self.core_db_status.setStyleSheet("color: #30A24C;")
                except Exception:
                    pass
            else:
                self.update_log_display("ℹ️ Database modülü bulunamadı")
        except Exception as e:
            self.update_log_display(f"❌ Database başlatılamadı: {e}")

    def _reload_api_manager(self):
        try:
            if API_MANAGER_AVAILABLE:
                self.api_manager = APIManager(db=self.db)
                self.update_log_display("✅ API Manager yeniden başlatıldı")
                try:
                    self.core_api_status.setText("Hazır")
                    self.core_api_status.setStyleSheet("color: #30A24C;")
                except Exception:
                    pass
            else:
                self.update_log_display("ℹ️ API Manager modülü bulunamadı")
        except Exception as e:
            self.update_log_display(f"❌ API Manager başlatılamadı: {e}")

    def _reload_analytics(self):
        try:
            if ANALYTICS_AVAILABLE and self.db:
                self.analytics_dashboard = AnalyticsDashboard(self.db)
                self.update_log_display("✅ Analytics Dashboard yeniden başlatıldı")
                try:
                    self.core_an_status.setText("Hazır")
                    self.core_an_status.setStyleSheet("color: #30A24C;")
                except Exception:
                    pass
            else:
                self.update_log_display("ℹ️ Analytics modülü veya DB yok")
        except Exception as e:
            self.update_log_display(f"❌ Analytics başlatılamadı: {e}")

    def _reload_automation_builder(self):
        try:
            if AUTOMATION_AVAILABLE:
                self.automation_builder = AutomationBuilder()
                self.update_log_display("✅ Automation Builder yeniden başlatıldı")
                try:
                    self.core_ab_status.setText("Hazır")
                    self.core_ab_status.setStyleSheet("color: #30A24C;")
                except Exception:
                    pass
            else:
                self.update_log_display("ℹ️ Automation Builder modülü bulunamadı")
        except Exception as e:
            self.update_log_display(f"❌ Automation Builder başlatılamadı: {e}")

    def _reload_tracking_gui(self):
        try:
            if TRACKING_GUI_AVAILABLE:
                self.tracking_gui_manager = get_tracking_gui_manager()
                self.update_log_display("✅ Tracking GUI Manager yeniden başlatıldı")
                try:
                    self.core_tr_status.setText("Hazır")
                    self.core_tr_status.setStyleSheet("color: #30A24C;")
                except Exception:
                    pass
            else:
                self.update_log_display("ℹ️ Tracking GUI modülü bulunamadı")
        except Exception as e:
            self.update_log_display(f"❌ Tracking GUI Manager başlatılamadı: {e}")

    def _refresh_core_status(self):
        try:
            self.core_db_status.setText("Hazır" if self.db else "YOK")
            self.core_db_status.setStyleSheet("color: #30A24C;" if self.db else "color: #C43D4B;")
            self.core_api_status.setText("Hazır" if self.api_manager else "YOK")
            self.core_api_status.setStyleSheet("color: #30A24C;" if self.api_manager else "color: #C43D4B;")
            self.core_an_status.setText("Hazır" if self.analytics_dashboard else "YOK")
            self.core_an_status.setStyleSheet("color: #30A24C;" if self.analytics_dashboard else "color: #C43D4B;")
            self.core_ab_status.setText("Hazır" if self.automation_builder else "YOK")
            self.core_ab_status.setStyleSheet("color: #30A24C;" if self.automation_builder else "color: #C43D4B;")
            self.core_tr_status.setText("Hazır" if self.tracking_gui_manager else "YOK")
            self.core_tr_status.setStyleSheet("color: #30A24C;" if self.tracking_gui_manager else "color: #C43D4B;")
            self.update_log_display("🧩 Ana sistem durumu güncellendi")
        except Exception:
            pass
    
    def update_nlp_statistics(self):
        """NLP istatistiklerini güncelle"""
        try:
            # NLP parser'ın istatistiklerini al
            if hasattr(self, 'engine') and self.engine and self.engine.nlp_parser:
                if hasattr(self.engine.nlp_parser, 'sl_parser'):
                    stats = self.engine.nlp_parser.sl_parser.get_statistics()
                    
                    stats_text = f"""
                    <ul style='color: #e0f2f7;'>
                        <li><b>Öğrenilen Pattern:</b> {stats['total_patterns']}</li>
                        <li><b>Başarılı Parse:</b> {stats['total_successful_parses']}</li>
                        <li><b>Ortalama Güven Skoru:</b> {stats['average_confidence']:.2%}</li>
                        <li><b>Hafıza Boyutu:</b> {stats['context_memory_size']}</li>
                        <li><b>Entity Veritabanı:</b> {stats['entity_database_size']}</li>
                    </ul>
                    """
                    self.nlp_stats_label.setText(stats_text)
                    self.update_log_display("📊 NLP istatistikleri güncellendi")
                else:
                    self.nlp_stats_label.setText("⏳ Standart NLP modunda çalışıyor")
        except Exception as e:
            logger.error(f"NLP istatistik güncellenemedi: {e}")
            self.nlp_stats_label.setText(f"Hata: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Font ayarı
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Gelişmiş splash ekranı
    splash = ModernSplashScreen()
    splash.show()
    splash.start_animation()
    app.processEvents()

    # Motor başlatma kontrolü
    try:
        # Splash animasyonunu tamamla
        import time
        start_time = time.time()
        while splash.progress < 100:
            app.processEvents()
            time.sleep(0.02)
        
        # Ana pencereyi oluştur
        window = AutomationGUI()
        splash.finish(window)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        splash.close()
        logger.critical(f"Uygulama başlatılamadı: {e}")
        QMessageBox.critical(None, "Kritik Hata", f"Uygulama başlatılamadı: {e}")
        sys.exit(1)