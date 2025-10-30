#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gelişmiş Firma Detay Analiz Sekmesi - AI Destekli Firma Analizi
Bu modül her firmanın detaylı analizini yapar ve AI ile gelişmiş sohbet sistemi sunar.
"""

import sys
import json
import sqlite3
from datetime import datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve, QUrl, QObject, Slot, QPointF, QRectF, QDateTime, QEvent
from PySide6.QtGui import QIcon, QAction, QPalette, QColor, QFont, QPainter, QPen, QBrush, QPolygonF
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings

# AI modüllerini import et
try:
    from ai_strategy_analyzer import AIStrategyAnalyzer
    AI_STRATEGY_AVAILABLE = True
except ImportError:
    AI_STRATEGY_AVAILABLE = False
    print("⚠️ AI Strategy Analyzer yüklenemedi")

try:
    from ai_chat_assistant import AIChatAssistantTab
    AI_CHAT_AVAILABLE = True
except ImportError:
    AI_CHAT_AVAILABLE = False
    print("⚠️ AI Chat Assistant yüklenemedi")

class SimpleAIChat:
    """Basit AI Chat fallback sınıfı"""
    def __init__(self, api_manager):
        self.api_manager = api_manager
    
    def ask_question(self, question, context=""):
        """Basit AI yanıt sistemi"""
        try:
            # Eğer API manager varsa OpenAI kullan
            if self.api_manager and hasattr(self.api_manager, 'openai_api_key'):
                return self._get_openai_response(question, context)
            else:
                return self._get_fallback_response(question, context)
        except Exception as e:
            return f"AI yanıt alınırken hata oluştu: {e}"
    
    def _get_openai_response(self, question, context):
        """OpenAI ile yanıt al"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_manager.openai_api_key)
            
            prompt = f"""
            Sen bir B2B pazarlama uzmanısın. Aşağıdaki firma bilgileri ve soruya göre yanıt ver:
            
            Firma Bilgileri:
            {context}
            
            Soru: {question}
            
            Lütfen kısa, net ve faydalı bir yanıt ver.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return self._get_fallback_response(question, context)
    
    def _get_fallback_response(self, question, context):
        """Fallback yanıt sistemi"""
        # Basit anahtar kelime tabanlı yanıtlar
        question_lower = question.lower()
        
        if "sektör" in question_lower or "sector" in question_lower:
            return "Bu firmanın sektörüne göre özel pazarlama stratejileri geliştirmenizi öneririm. Sektörel trendleri takip edin ve rakiplerinizi analiz edin."
        
        elif "email" in question_lower or "mail" in question_lower:
            return "Email pazarlama için kişiselleştirilmiş içerikler hazırlayın. A/B testleri yaparak en etkili yaklaşımı bulun."
        
        elif "performans" in question_lower or "performance" in question_lower:
            return "Performansı artırmak için metrikleri düzenli takip edin. Email açılma oranları, tıklama oranları ve dönüşüm oranlarını analiz edin."
        
        elif "strateji" in question_lower or "strategy" in question_lower:
            return "Bu firma için özel bir strateji geliştirin. Firma büyüklüğü, sektör ve konumunu dikkate alarak yaklaşımınızı belirleyin."
        
        elif "iletişim" in question_lower or "communication" in question_lower:
            return "İletişim geçmişini inceleyin ve en etkili iletişim kanallarını belirleyin. Düzenli takip yapın."
        
        else:
            return f"Bu firma hakkında '{question}' sorusuna yanıt vermek için daha fazla bilgiye ihtiyacım var. Detaylı analiz yaparak size daha iyi yardımcı olabilirim."

class ModernCard(QWidget):
    """Modern kart widget'ı"""
    def __init__(self, title, value, color, icon):
        super().__init__()
        self.title = title
        self.value = value
        self.color = color
        self.icon = icon
        self.value_label = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Kart container
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {self.color}, 0.8), stop: 1 {self.color}, 0.6));
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        
        # İkon ve başlık
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet("font-size: 24px; color: white;")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Değer
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.value_label)
    
    def update_value(self, new_value):
        self.value = new_value
        if self.value_label:
            self.value_label.setText(new_value)

class ChatMessage(QWidget):
    """Chat mesaj widget'ı"""
    def __init__(self, message, is_user=True, timestamp=None):
        super().__init__()
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Mesaj container
        message_frame = QFrame()
        if self.is_user:
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #14a085;
                    border-radius: 15px;
                    padding: 10px;
                    margin-left: 50px;
                }
            """)
        else:
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #2a2a2a;
                    border-radius: 15px;
                    padding: 10px;
                    margin-right: 50px;
                }
            """)
        
        message_layout = QVBoxLayout(message_frame)
        
        # Mesaj metni
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white; font-size: 14px; padding: 5px;")
        message_layout.addWidget(message_label)
        
        # Timestamp
        time_label = QLabel(self.timestamp.strftime("%H:%M"))
        time_label.setStyleSheet("color: #888; font-size: 10px;")
        time_label.setAlignment(Qt.AlignRight)
        message_layout.addWidget(time_label)
        
        layout.addWidget(message_frame)

class FirmaDetayAnalyzer(QWidget):
    """Gelişmiş Firma Detay Analiz Sekmesi - Ana Widget"""
    
    def __init__(self, db_connection=None, api_manager=None):
        super().__init__()
        self.db = db_connection
        self.api_manager = api_manager
        self.current_firma = None
        self.ai_analyzer = None
        self.ai_chat = None
        self.chat_history = []
        
        # AI modüllerini başlat
        self.init_ai_modules()
        
        # UI'yi oluştur
        self.init_ui()
        
        # Verileri yükle
        self.load_firmalar()
    
    def init_ai_modules(self):
        """AI modüllerini başlat"""
        try:
            if AI_STRATEGY_AVAILABLE and self.api_manager:
                # Database objesi yerine path string'i ver
                db_path = "b2b_automation.db"  # Varsayılan path
                if hasattr(self.db, 'database_path'):
                    db_path = self.db.database_path
                elif hasattr(self.db, 'connection') and hasattr(self.db.connection, 'database'):
                    db_path = self.db.connection.database
                
                self.ai_analyzer = AIStrategyAnalyzer(db_path)
                print("✅ AI Strategy Analyzer başlatıldı")
            
            if AI_CHAT_AVAILABLE and self.api_manager:
                # AI Chat Assistant'ı başlat - sadece AI yanıt alma için
                try:
                    self.ai_chat = AIChatAssistantTab(self.db, self.api_manager)
                    print("✅ AI Chat Assistant başlatıldı")
                except Exception as e:
                    print(f"⚠️ AI Chat Assistant başlatılamadı: {e}")
                    self.ai_chat = SimpleAIChat(self.api_manager)
                    print("✅ Basit AI Chat sistemi başlatıldı")
            else:
                # Fallback AI Chat sistemi
                self.ai_chat = SimpleAIChat(self.api_manager)
                print("✅ Basit AI Chat sistemi başlatıldı")
                
        except Exception as e:
            print(f"⚠️ AI modülleri başlatılamadı: {e}")
            # Fallback sistemi
            self.ai_chat = SimpleAIChat(self.api_manager)
    
    def init_ui(self):
        """Ana UI'yi oluştur"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Sol panel - Firma listesi ve arama
        left_panel = self.create_firma_list_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Sağ panel - Firma detayları ve AI analiz
        right_panel = self.create_firma_detail_panel()
        main_layout.addWidget(right_panel, 2)
    
    def create_firma_list_panel(self):
        """Sol panel - Çok daha gelişmiş firma listesi ve arama"""
        panel = QWidget()
        panel.setMaximumWidth(450)
        layout = QVBoxLayout(panel)
        
        # Başlık - Çok daha etkileyici
        title_label = QLabel("🏢 Gelişmiş Firma Yönetimi")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 0.5 #764ba2, stop: 1 #f093fb);
                border-radius: 15px;
                margin-bottom: 15px;
                border: 2px solid #5a67d8;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
        """)
        layout.addWidget(title_label)
        
        # Arama ve filtreleme - Çok daha gelişmiş
        search_group = QGroupBox("🔍 Gelişmiş Arama ve Filtreleme")
        search_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2d3748;
                border: 3px solid #667eea;
                border-radius: 12px;
                margin-top: 15px;
                padding-top: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f7fafc, stop: 1 #edf2f7);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background: white;
                border-radius: 5px;
            }
        """)
        
        search_layout = QVBoxLayout(search_group)
        
        # Arama kutusu - Çok daha gelişmiş
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Firma adı, sektör, adres veya telefon ara...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                background: white;
                color: #2d3748;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background: #f7fafc;
            }
            QLineEdit:hover {
                border-color: #a0aec0;
            }
        """)
        self.search_input.textChanged.connect(self.filter_firmalar)
        search_layout.addWidget(self.search_input)
        
        # Filtre butonları
        filter_layout = QHBoxLayout()
        
        self.filter_all_btn = QPushButton("Tümü")
        self.filter_all_btn.setCheckable(True)
        self.filter_all_btn.setChecked(True)
        self.filter_all_btn.clicked.connect(lambda: self.filter_by_type("all"))
        
        self.filter_with_email_btn = QPushButton("Email'li")
        self.filter_with_email_btn.setCheckable(True)
        self.filter_with_email_btn.clicked.connect(lambda: self.filter_by_type("with_email"))
        
        self.filter_recent_btn = QPushButton("Son Eklenen")
        self.filter_recent_btn.setCheckable(True)
        self.filter_recent_btn.clicked.connect(lambda: self.filter_by_type("recent"))
        
        # Modern buton stili
        button_style = """
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                color: #4a5568;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #f7fafc;
                border-color: #a0aec0;
            }
            QPushButton:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border-color: #5a67d8;
            }
            QPushButton:pressed {
                background: #4c51bf;
            }
        """
        
        self.filter_all_btn.setText("📊 Tümü")
        self.filter_all_btn.setStyleSheet(button_style)
        
        self.filter_with_email_btn.setText("📧 Email'li")
        self.filter_with_email_btn.setStyleSheet(button_style)
        
        self.filter_recent_btn.setText("🕒 Son Eklenen")
        self.filter_recent_btn.setStyleSheet(button_style)
        
        filter_layout.addWidget(self.filter_all_btn)
        filter_layout.addWidget(self.filter_with_email_btn)
        filter_layout.addWidget(self.filter_recent_btn)
        
        search_layout.addLayout(filter_layout)
        layout.addWidget(search_group)
        
        # Firma listesi - Çok daha gelişmiş
        self.firma_list = QListWidget()
        self.firma_list.itemClicked.connect(self.on_firma_selected)
        self.firma_list.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8fafc, stop: 1 #f1f5f9);
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 10px;
                font-size: 13px;
                color: #2d3748;
            }
            QListWidget::item {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                margin: 3px;
                min-height: 20px;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f4ff, stop: 1 #e6f3ff);
                border-color: #667eea;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border-color: #5a67d8;
            }
            QListWidget::item:selected:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5a67d8, stop: 1 #6b46c1);
            }
        """)
        layout.addWidget(self.firma_list)
        
        # İstatistik kartları
        stats_group = QGroupBox("📊 İstatistikler")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #14a085;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        stats_layout = QVBoxLayout(stats_group)
        
        self.total_firmalar_card = ModernCard("Toplam Firma", "0", "rgba(52, 152, 219", "📊")
        self.aktif_firmalar_card = ModernCard("Aktif Firma", "0", "rgba(46, 204, 113", "✅")
        self.email_sayisi_card = ModernCard("Email Sayısı", "0", "rgba(155, 89, 182", "📧")
        
        stats_layout.addWidget(self.total_firmalar_card)
        stats_layout.addWidget(self.aktif_firmalar_card)
        stats_layout.addWidget(self.email_sayisi_card)
        
        layout.addWidget(stats_group)
        
        return panel
    
    def create_firma_detail_panel(self):
        """Sağ panel - Firma detayları ve AI analiz"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Tab widget
        self.detail_tabs = QTabWidget()
        self.detail_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1a1a1a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: white;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background-color: #14a085;
            }
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
        """)
        
        # Tab 1: Genel Bilgiler
        self.general_tab = self.create_general_tab()
        self.detail_tabs.addTab(self.general_tab, "📋 Genel Bilgiler")
        
        # Tab 2: AI Analiz
        self.ai_analysis_tab = self.create_ai_analysis_tab()
        self.detail_tabs.addTab(self.ai_analysis_tab, "🤖 AI Analiz")
        
        # Tab 3: AI Chat
        self.ai_chat_tab = self.create_ai_chat_tab()
        self.detail_tabs.addTab(self.ai_chat_tab, "💬 AI Sohbet")
        
        # Tab 4: İletişim Geçmişi
        self.communication_tab = self.create_communication_tab()
        self.detail_tabs.addTab(self.communication_tab, "📞 İletişim")
        
        # Tab 5: Performans Metrikleri
        self.performance_tab = self.create_performance_tab()
        self.detail_tabs.addTab(self.performance_tab, "📈 Performans")
        
        # Tab 6: AI Öneriler
        self.ai_suggestions_tab = self.create_ai_suggestions_tab()
        self.detail_tabs.addTab(self.ai_suggestions_tab, "💡 AI Öneriler")
        
        layout.addWidget(self.detail_tabs)
        
        return panel
    
    def create_general_tab(self):
        """Genel bilgiler sekmesi - Çok daha gelişmiş"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # Firma bilgileri container
        self.firma_info_widget = QWidget()
        self.firma_info_layout = QVBoxLayout(self.firma_info_widget)
        self.firma_info_layout.setSpacing(15)
        self.firma_info_layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık - Çok daha etkileyici
        self.firma_title = QLabel("🏢 Firma Seçin")
        self.firma_title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: white;
                padding: 25px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 0.5 #764ba2, stop: 1 #f093fb);
                border-radius: 15px;
                margin-bottom: 20px;
                border: 3px solid #5a67d8;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
        """)
        self.firma_info_layout.addWidget(self.firma_title)
        
        # Bilgi kartları
        self.info_cards_layout = QGridLayout()
        
        # Temel bilgiler
        self.sector_card = ModernCard("Sektör", "-", "rgba(52, 152, 219", "🏭")
        self.location_card = ModernCard("Konum", "-", "rgba(46, 204, 113", "📍")
        self.website_card = ModernCard("Website", "-", "rgba(155, 89, 182", "🌐")
        self.phone_card = ModernCard("Telefon", "-", "rgba(241, 196, 15", "📞")
        
        self.info_cards_layout.addWidget(self.sector_card, 0, 0)
        self.info_cards_layout.addWidget(self.location_card, 0, 1)
        self.info_cards_layout.addWidget(self.website_card, 1, 0)
        self.info_cards_layout.addWidget(self.phone_card, 1, 1)
        
        self.firma_info_layout.addLayout(self.info_cards_layout)
        
        # Email listesi - Çok daha büyük ve gelişmiş
        self.email_section = QGroupBox("📧 Email Adresleri ve İletişim Bilgileri")
        self.email_section.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #2d3748;
                border: 3px solid #667eea;
                border-radius: 15px;
                margin-top: 20px;
                padding-top: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f8fafc, stop: 1 #f1f5f9);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 15px 0 15px;
                background: white;
                border-radius: 8px;
                border: 2px solid #667eea;
            }
        """)
        
        email_layout = QVBoxLayout(self.email_section)
        email_layout.setSpacing(15)
        
        # Email listesi - Çok daha büyük
        self.email_list = QListWidget()
        self.email_list.setMinimumHeight(200)  # Çok daha büyük
        self.email_list.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8fafc);
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
                font-size: 14px;
                color: #2d3748;
            }
            QListWidget::item {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f0f4ff, stop: 1 #e6f3ff);
                border: 1px solid #cbd5e0;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                min-height: 25px;
                font-weight: bold;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border-color: #5a67d8;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5a67d8, stop: 1 #6b46c1);
                color: white;
                border-color: #4c51bf;
            }
        """)
        email_layout.addWidget(self.email_list)
        
        self.firma_info_layout.addWidget(self.email_section)
        
        # Firma Özeti - Çok daha detaylı ve gelişmiş
        self.summary_section = QGroupBox("📋 Detaylı Firma Özeti")
        self.summary_section.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #2d3748;
                border: 3px solid #f093fb;
                border-radius: 15px;
                margin-top: 20px;
                padding-top: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #fdf2f8, stop: 1 #fce7f3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 15px 0 15px;
                background: white;
                border-radius: 8px;
                border: 2px solid #f093fb;
            }
        """)
        
        summary_layout = QVBoxLayout(self.summary_section)
        summary_layout.setSpacing(15)
        
        # Özet metni - Çok daha büyük ve detaylı
        self.summary_text = QTextEdit()
        self.summary_text.setMinimumHeight(150)  # Çok daha büyük
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8fafc);
                border: 2px solid #f1f5f9;
                border-radius: 12px;
                padding: 20px;
                font-size: 14px;
                color: #2d3748;
                line-height: 1.6;
            }
            QTextEdit:focus {
                border-color: #f093fb;
            }
        """)
        self.summary_text.setPlaceholderText("Firma seçildiğinde detaylı özet burada görünecek...")
        summary_layout.addWidget(self.summary_text)
        
        # Özet istatistikleri
        self.summary_stats_layout = QHBoxLayout()
        
        # Özet kartları
        self.summary_length_card = ModernCard("Özet Uzunluğu", "0", "rgba(240, 147, 251", "📏")
        self.summary_keywords_card = ModernCard("Anahtar Kelimeler", "0", "rgba(236, 72, 153", "🔑")
        self.summary_sentiment_card = ModernCard("Duygu Analizi", "Nötr", "rgba(168, 85, 247", "😊")
        
        self.summary_stats_layout.addWidget(self.summary_length_card)
        self.summary_stats_layout.addWidget(self.summary_keywords_card)
        self.summary_stats_layout.addWidget(self.summary_sentiment_card)
        
        summary_layout.addLayout(self.summary_stats_layout)
        self.firma_info_layout.addWidget(self.summary_section)
        
        # Add widget to scroll area
        scroll.setWidget(self.firma_info_widget)
        main_layout.addWidget(scroll)
        
        return widget
    
    def create_ai_analysis_tab(self):
        """AI analiz sekmesi - Çok daha gelişmiş"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # AI analiz sonuçları
        self.ai_analysis_widget = QWidget()
        ai_layout = QVBoxLayout(self.ai_analysis_widget)
        ai_layout.setSpacing(15)
        
        # Analiz başlığı - Çok daha etkileyici
        analysis_title = QLabel("🤖 Gelişmiş AI Destekli Firma Analizi")
        analysis_title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: white;
                padding: 25px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 0.5 #764ba2, stop: 1 #f093fb);
                border-radius: 15px;
                margin-bottom: 20px;
                border: 3px solid #5a67d8;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
        """)
        ai_layout.addWidget(analysis_title)
        
        # Analiz butonları
        analyze_buttons_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("🔍 Detaylı Analiz")
        analyze_btn.clicked.connect(self.analyze_firma)
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #14a085;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0d7377;
            }
            QPushButton:pressed {
                background-color: #0a5d61;
            }
        """)
        
        quick_analyze_btn = QPushButton("⚡ Hızlı Analiz")
        quick_analyze_btn.clicked.connect(self.quick_analyze_firma)
        quick_analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        
        analyze_buttons_layout.addWidget(analyze_btn)
        analyze_buttons_layout.addWidget(quick_analyze_btn)
        analyze_buttons_layout.addStretch()
        
        ai_layout.addLayout(analyze_buttons_layout)
        
        # Analiz sonuçları
        self.analysis_results = QTextEdit()
        self.analysis_results.setReadOnly(True)
        self.analysis_results.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 20px;
                color: white;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        ai_layout.addWidget(self.analysis_results)
        
        layout.addWidget(self.ai_analysis_widget)
        
        return widget
    
    def create_ai_chat_tab(self):
        """AI chat sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Chat başlığı
        chat_title = QLabel("💬 AI ile Sohbet")
        chat_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #14a085;
                padding: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: 10px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(chat_title)
        
        # Chat mesajları
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #444;
                border-radius: 8px;
                background-color: #1a1a1a;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #14a085;
                border-radius: 6px;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_scroll.setWidget(self.chat_widget)
        
        layout.addWidget(self.chat_scroll)
        
        # Mesaj gönderme
        message_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Bu firma hakkında soru sorun...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 2px solid #333;
                border-radius: 8px;
                background-color: #2a2a2a;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #14a085;
            }
        """)
        message_layout.addWidget(self.message_input)
        
        send_btn = QPushButton("📤 Gönder")
        send_btn.clicked.connect(self.send_message)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #14a085;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0d7377;
            }
        """)
        message_layout.addWidget(send_btn)
        
        layout.addLayout(message_layout)
        
        return widget
    
    def create_communication_tab(self):
        """İletişim geçmişi sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # İletişim geçmişi başlığı
        comm_title = QLabel("📞 İletişim Geçmişi")
        comm_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #14a085;
                padding: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: 10px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(comm_title)
        
        # İletişim listesi
        self.communication_list = QListWidget()
        self.communication_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 15px;
                color: white;
                border-bottom: 1px solid #444;
                background-color: #1a1a1a;
                border-radius: 6px;
                margin-bottom: 5px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
        """)
        layout.addWidget(self.communication_list)
        
        return widget
    
    def create_performance_tab(self):
        """Performans metrikleri sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performans başlığı
        perf_title = QLabel("📈 Performans Metrikleri")
        perf_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #14a085;
                padding: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: 10px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(perf_title)
        
        # Performans kartları
        perf_cards_layout = QGridLayout()
        
        self.email_open_rate_card = ModernCard("Email Açılma", "%0", "rgba(46, 204, 113", "👁️")
        self.email_click_rate_card = ModernCard("Tıklama Oranı", "%0", "rgba(52, 152, 219", "🖱️")
        self.response_rate_card = ModernCard("Yanıt Oranı", "%0", "rgba(155, 89, 182", "💬")
        self.conversion_rate_card = ModernCard("Dönüşüm Oranı", "%0", "rgba(241, 196, 15", "🎯")
        
        perf_cards_layout.addWidget(self.email_open_rate_card, 0, 0)
        perf_cards_layout.addWidget(self.email_click_rate_card, 0, 1)
        perf_cards_layout.addWidget(self.response_rate_card, 1, 0)
        perf_cards_layout.addWidget(self.conversion_rate_card, 1, 1)
        
        layout.addLayout(perf_cards_layout)
        
        # AI Analiz Durumu
        ai_status_card = ModernCard("AI Analiz", "Bekliyor", "rgba(102, 126, 234", "🤖")
        perf_cards_layout.addWidget(ai_status_card, 2, 0)
        
        # AI Güven Skoru
        ai_confidence_card = ModernCard("AI Güven", "N/A", "rgba(240, 147, 251", "⭐")
        perf_cards_layout.addWidget(ai_confidence_card, 2, 1)
        
        self.ai_status_card = ai_status_card
        self.ai_confidence_card = ai_confidence_card
        self.perf_detail = None
        # Kart değerlerini takip et
        self.email_open_rate = "0"
        self.email_click_rate = "0"
        self.response_rate = "0"
        self.conversion_rate = "0"
        
        # Detaylı performans
        perf_detail_group = QGroupBox("📊 Detaylı Performans Analizi")
        perf_detail_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #14a085;
                border: 2px solid #14a085;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        perf_detail_layout = QVBoxLayout(perf_detail_group)
        
        perf_detail = QTextEdit()
        perf_detail.setReadOnly(True)
        perf_detail.setPlaceholderText("Firma seçildiğinde detaylı performans analizi burada görüntülenecek...")
        perf_detail.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 20px;
                color: white;
                font-size: 14px;
                min-height: 150px;
            }
        """)
        perf_detail_layout.addWidget(perf_detail)
        self.perf_detail = perf_detail
        
        layout.addWidget(perf_detail_group)
        
        return widget
    
    def create_ai_suggestions_tab(self):
        """AI öneriler sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AI öneriler başlığı
        suggestions_title = QLabel("💡 AI Öneriler")
        suggestions_title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #14a085;
                padding: 20px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: 10px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(suggestions_title)
        
        # Öneri butonu
        suggest_btn = QPushButton("💡 AI Önerilerini Al")
        suggest_btn.clicked.connect(self.get_ai_suggestions)
        suggest_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        layout.addWidget(suggest_btn)
        
        # AI önerileri
        self.ai_suggestions = QTextEdit()
        self.ai_suggestions.setReadOnly(True)
        self.ai_suggestions.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 20px;
                color: white;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.ai_suggestions)
        
        return widget
    
    def load_firmalar(self):
        """Veritabanından firmaları yükle"""
        if not self.db:
            return
        
        try:
            # Veritabanı bağlantısını kontrol et ve cursor al
            cursor = self._get_database_cursor()
            if not cursor:
                raise Exception("Veritabanı cursor'u alınamadı")
            
            cursor.execute("""
                SELECT id, name, sector, address, website, phone, emails
                FROM firms 
                ORDER BY name
            """)
            
            firmalar = cursor.fetchall()
            
            # İstatistikleri güncelle
            self.update_statistics(firmalar)
            
            # Firma listesini güncelle
            self.firma_list.clear()
            for firma in firmalar:
                item = QListWidgetItem(firma[1])  # name
                item.setData(Qt.UserRole, firma[0])  # id
                self.firma_list.addItem(item)
                
        except Exception as e:
            print(f"Firmalar yüklenirken hata: {e}")
            # Fallback - boş liste göster
            self.firma_list.clear()
            self.total_firmalar_card.update_value("0")
            self.aktif_firmalar_card.update_value("0")
            self.email_sayisi_card.update_value("0")
    
    def _get_database_cursor(self):
        """Veritabanı cursor'unu güvenli şekilde al"""
        try:
            # Eğer db bir sqlite3.Connection ise
            if hasattr(self.db, 'execute'):
                return self.db
            
            # Eğer db bir Database objesi ise (database.Database)
            elif hasattr(self.db, 'cursor') and hasattr(self.db, 'conn'):
                # Database sınıfının cursor'unu kullan
                # Thread-safe çalışma için lock kullan
                if hasattr(self.db, 'lock'):
                    with self.db.lock:
                        self.db.ensure_connection()
                        return self.db.cursor
                else:
                    self.db.ensure_connection()
                    return self.db.cursor
            
            # Eğer db bir Database objesi ise ve connection property'si varsa
            elif hasattr(self.db, 'connection'):
                return self.db.connection
            
            # Eğer db bir cursor ise
            elif hasattr(self.db, 'execute'):
                return self.db
            
            # Eğer db bir string path ise
            elif isinstance(self.db, str):
                import sqlite3
                conn = sqlite3.connect(self.db)
                return conn
            
            # Eğer db bir dict ise (connection bilgileri)
            elif isinstance(self.db, dict):
                import sqlite3
                db_path = self.db.get('path', 'b2b_automation.db')
                conn = sqlite3.connect(db_path)
                return conn
            
            else:
                print(f"Bilinmeyen veritabanı tipi: {type(self.db)}")
                return None
                
        except Exception as e:
            print(f"Veritabanı cursor alınırken hata: {e}")
            return None
    
    def update_statistics(self, firmalar):
        """İstatistikleri güncelle"""
        total_firmalar = len(firmalar)
        aktif_firmalar = len([f for f in firmalar if f[6]])  # emails var mı
        total_emails = sum(len(f[6].split(',')) if f[6] else 0 for f in firmalar)
        
        self.total_firmalar_card.update_value(str(total_firmalar))
        self.aktif_firmalar_card.update_value(str(aktif_firmalar))
        self.email_sayisi_card.update_value(str(total_emails))
    
    def filter_firmalar(self, text):
        """Firma listesini filtrele"""
        for i in range(self.firma_list.count()):
            item = self.firma_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def filter_by_type(self, filter_type):
        """Firma listesini türe göre filtrele"""
        # Tüm filtre butonlarını sıfırla
        for btn in [self.filter_all_btn, self.filter_with_email_btn, self.filter_recent_btn]:
            btn.setChecked(False)
        
        # Seçilen butonu işaretle
        if filter_type == "all":
            self.filter_all_btn.setChecked(True)
            # Tüm firmaları göster
            for i in range(self.firma_list.count()):
                self.firma_list.item(i).setHidden(False)
        elif filter_type == "with_email":
            self.filter_with_email_btn.setChecked(True)
            # Sadece email'i olan firmaları göster
            # Bu filtreleme için veritabanından tekrar veri çekmek gerekir
            self.load_firmalar_with_filter("with_email")
        elif filter_type == "recent":
            self.filter_recent_btn.setChecked(True)
            # Son eklenen firmaları göster
            self.load_firmalar_with_filter("recent")
    
    def load_firmalar_with_filter(self, filter_type):
        """Filtreye göre firmaları yükle"""
        if not self.db:
            return
        
        try:
            cursor = self._get_database_cursor()
            if not cursor:
                raise Exception("Veritabanı cursor'u alınamadı")
            
            if filter_type == "with_email":
                cursor.execute("""
                    SELECT id, name, sector, address, website, phone, emails
                    FROM firms 
                    WHERE emails IS NOT NULL AND emails != ''
                    ORDER BY name
                """)
            elif filter_type == "recent":
                cursor.execute("""
                    SELECT id, name, sector, address, website, phone, emails
                    FROM firms 
                    ORDER BY created_at DESC
                    LIMIT 50
                """)
            
            firmalar = cursor.fetchall()
            
            # Firma listesini güncelle
            self.firma_list.clear()
            for firma in firmalar:
                item = QListWidgetItem(firma[1])  # name
                item.setData(Qt.UserRole, firma[0])  # id
                self.firma_list.addItem(item)
                
        except Exception as e:
            print(f"Filtrelenmiş firmalar yüklenirken hata: {e}")
    
    def on_firma_selected(self, item):
        """Firma seçildiğinde"""
        firma_id = item.data(Qt.UserRole)
        self.load_firma_details(firma_id)
    
    def load_firm_by_name(self, firm_name):
        """İsme göre firma yükle"""
        try:
            # Firma listesinde ara
            for i in range(self.firma_list.count()):
                item = self.firma_list.item(i)
                if item.text() == firm_name:
                    # Firma ID'sini al
                    firma_id = item.data(Qt.UserRole)
                    if firma_id:
                        self.firma_list.setCurrentItem(item)
                        self.load_firma_details(firma_id)
                        return True
            return False
        except Exception as e:
            print(f"Firma isimle yüklenirken hata: {e}")
            return False
    
    def load_firma_details(self, firma_id):
        """Seçilen firmanın detaylarını yükle"""
        if not self.db:
            return
        
        try:
            cursor = self._get_database_cursor()
            if not cursor:
                raise Exception("Veritabanı cursor'u alınamadı")
            
            cursor.execute("""
                SELECT id, name, COALESCE(sector, '') as sector, 
                       COALESCE(address, '') as address, 
                       COALESCE(website, '') as website, 
                       COALESCE(phone, '') as phone, 
                       COALESCE(emails, '[]') as emails, 
                       COALESCE(summary, '') as summary, 
                       COALESCE(ai_summary, '') as ai_summary,
                       COALESCE(created_at, '') as created_at, 
                       COALESCE(last_contact_date, '') as last_contact_date,
                       COALESCE(email, '') as email
                FROM firms 
                WHERE id = ?
            """, (firma_id,))
            
            firma = cursor.fetchone()
            if not firma:
                return
            
            self.current_firma = firma
            
            # Genel bilgileri güncelle
            self.firma_title.setText(firma[1])  # name
            
            # Bilgi kartlarını güncelle
            self.sector_card.update_value(firma[2] or "-")  # sector
            self.location_card.update_value(firma[3] or "-")  # address
            self.website_card.update_value(firma[4] or "-")  # website
            self.phone_card.update_value(firma[5] or "-")  # phone
            
            # Email listesini güncelle - JSON formatını parse et
            self.email_list.clear()
            import json
            
            # emails is a JSON string, need to parse it
            emails_data = firma[6] if firma[6] else '[]'
            try:
                if isinstance(emails_data, str):
                    emails_list = json.loads(emails_data)
                else:
                    emails_list = emails_data
                
                # If it's a list of dicts with 'email' key
                if isinstance(emails_list, list) and emails_list:
                    for email_obj in emails_list:
                        if isinstance(email_obj, dict) and 'email' in email_obj:
                            email = email_obj['email']
                            position = email_obj.get('position', 'Genel')
                            item = QListWidgetItem(f"📧 {email} ({position})")
                            self.email_list.addItem(item)
                        elif isinstance(email_obj, str):
                            item = QListWidgetItem(f"📧 {email_obj}")
                            self.email_list.addItem(item)
                
                # If no emails in list, try the single email field
                if self.email_list.count() == 0 and firma[11]:
                    item = QListWidgetItem(f"📧 {firma[11]}")
                    self.email_list.addItem(item)
                    
            except Exception as e:
                print(f"Email parse hatası: {e}")
                # Fallback: try to parse as comma-separated
                if ',' in str(emails_data):
                    emails = str(emails_data).split(',')
                    for email in emails:
                        if email.strip():
                            item = QListWidgetItem(f"📧 {email.strip()}")
                            self.email_list.addItem(item)
                elif firma[11]:  # single email field
                    item = QListWidgetItem(f"📧 {firma[11]}")
                    self.email_list.addItem(item)
                else:
                    self.email_list.addItem("📧 Email adresi bulunamadı")
            
            if self.email_list.count() == 0:
                self.email_list.addItem("📧 Email adresi bulunamadı")
            
            # Detaylı özeti güncelle - Çok daha gelişmiş
            self.update_detailed_summary(firma)
            
            # İletişim geçmişini yükle
            self.load_communication_history(firma_id)
            
            # Performans metriklerini yükle
            self.load_performance_metrics(firma_id)
            
            # Chat geçmişini temizle
            self.clear_chat()
            
        except Exception as e:
            print(f"Firma detayları yüklenirken hata: {e}")
    
    def update_detailed_summary(self, firma):
        """Detaylı firma özetini güncelle - Çok daha gelişmiş"""
        try:
            # Temel bilgiler
            name = firma[1] or "Bilinmiyor"
            sector = firma[2] or "Belirtilmemiş"
            address = firma[3] or "Belirtilmemiş"
            website = firma[4] or "Belirtilmemiş"
            phone = firma[5] or "Belirtilmemiş"
            emails = firma[6] or ""
            summary = firma[7] or ""
            ai_summary = firma[8] or ""
            created_at = firma[9] or ""
            last_contact = firma[10] or ""
            single_email = firma[11] if len(firma) > 11 else ""
            
            # Email sayısı - parse JSON emails
            import json
            try:
                if isinstance(emails, str):
                    emails_data = json.loads(emails) if emails else []
                else:
                    emails_data = emails
                email_count = len(emails_data) if isinstance(emails_data, list) else 0
            except:
                email_count = 1 if single_email else 0
            
            # Use ai_summary if available, otherwise use summary
            firm_summary = ai_summary if ai_summary else summary
            
            # Detaylı özet oluştur
            detailed_summary = f"""
🏢 **{name}** - Detaylı Firma Profili

📊 **Temel Bilgiler:**
• **Sektör:** {sector}
• **Adres:** {address}
• **Website:** {website}
• **Telefon:** {phone}
• **Email Sayısı:** {email_count} adet

📧 **İletişim Bilgileri:**
{single_email if single_email else (str(emails_data) if email_count > 0 else "Email adresi bulunamadı")}

📝 **Firma Özeti:**
{firm_summary if firm_summary else "Firma hakkında detaylı bilgi bulunmuyor. AI analizi ile daha fazla bilgi elde edebilirsiniz."}

📅 **Kayıt Bilgileri:**
• **Kayıt Tarihi:** {created_at if created_at else "Bilinmiyor"}
• **Son İletişim:** {last_contact if last_contact else "Henüz iletişim kurulmamış"}

🎯 **AI Önerileri:**
• Bu firma {sector} sektöründe faaliyet gösteriyor
• {'Email pazarlama için uygun' if email_count > 0 else 'Email adresi eklenmesi önerilir'}
• Detaylı analiz için AI sekmesini kullanın
• AI sohbet ile firma hakkında sorular sorabilirsiniz

💡 **Sonraki Adımlar:**
1. AI analizi ile firma potansiyelini değerlendirin
2. Email kampanyaları için strateji geliştirin
3. İletişim geçmişini takip edin
4. Performans metriklerini analiz edin
            """
            
            self.summary_text.setHtml(detailed_summary)
            
            # Özet istatistiklerini güncelle
            word_count = len(detailed_summary.split())
            keyword_count = len([word for word in detailed_summary.split() if len(word) > 4])
            
            self.summary_length_card.update_value(f"{word_count} kelime")
            self.summary_keywords_card.update_value(f"{keyword_count} anahtar")
            
            # Basit duygu analizi
            sentiment = "Pozitif" if any(word in detailed_summary.lower() for word in ["başarılı", "büyük", "gelişmiş", "iyi"]) else "Nötr"
            self.summary_sentiment_card.update_value(sentiment)
            
        except Exception as e:
            print(f"Detaylı özet güncellenirken hata: {e}")
            self.summary_text.setText(f"Hata: {e}")
    
    def load_communication_history(self, firma_id):
        """İletişim geçmişini yükle"""
        if not self.db:
            return
        
        try:
            cursor = self._get_database_cursor()
            if not cursor:
                raise Exception("Veritabanı cursor'u alınamadı")
            
            cursor.execute("""
                SELECT action, timestamp, details
                FROM communication_log 
                WHERE firma_id = ?
                ORDER BY timestamp DESC
                LIMIT 50
            """, (firma_id,))
            
            communications = cursor.fetchall()
            
            self.communication_list.clear()
            for comm in communications:
                item_text = f"{comm[0]} - {comm[1]}"
                if comm[2]:
                    item_text += f"\n{comm[2]}"
                
                item = QListWidgetItem(item_text)
                self.communication_list.addItem(item)
                
        except Exception as e:
            print(f"İletişim geçmişi yüklenirken hata: {e}")
            # Fallback - boş liste göster
            self.communication_list.clear()
    
    def load_performance_metrics(self, firma_id):
        """Performans metriklerini yükle"""
        if not self.db:
            return
        
        try:
            cursor = self._get_database_cursor()
            if not cursor:
                raise Exception("Veritabanı cursor'u alınamadı")
            
            # Email açılma oranı
            # Email metrikleri
            email_open_rate = "0"
            email_click_rate = "0"
            response_rate = "0"
            conversion_rate = "0"
            
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total, 
                           SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as opened
                    FROM email_tracking 
                    WHERE firma_id = ?
                """, (firma_id,))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    open_rate = (result[1] / result[0]) * 100
                    email_open_rate = f"{open_rate:.1f}"
                    self.email_open_rate_card.update_value(f"%{open_rate:.1f}")
            except:
                pass
            
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total, 
                           SUM(CASE WHEN clicked = 1 THEN 1 ELSE 0 END) as clicked
                    FROM email_tracking 
                    WHERE firma_id = ?
                """, (firma_id,))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    click_rate = (result[1] / result[0]) * 100
                    email_click_rate = f"{click_rate:.1f}"
                    self.email_click_rate_card.update_value(f"%{click_rate:.1f}")
            except:
                pass
            
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total, 
                           SUM(CASE WHEN replied = 1 THEN 1 ELSE 0 END) as replied
                    FROM email_tracking 
                    WHERE firma_id = ?
                """, (firma_id,))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    response_rate_val = (result[1] / result[0]) * 100
                    response_rate = f"{response_rate_val:.1f}"
                    self.response_rate_card.update_value(f"%{response_rate_val:.1f}")
            except:
                pass
            
            try:
                cursor.execute("""
                    SELECT COUNT(*) as total, 
                           SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as converted
                    FROM email_tracking 
                    WHERE firma_id = ?
                """, (firma_id,))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    conversion_rate_val = (result[1] / result[0]) * 100
                    conversion_rate = f"{conversion_rate_val:.1f}"
                    self.conversion_rate_card.update_value(f"%{conversion_rate_val:.1f}")
            except:
                pass
            
            # Değerleri sakla
            self.email_open_rate = email_open_rate
            self.email_click_rate = email_click_rate
            self.response_rate = response_rate
            self.conversion_rate = conversion_rate
            
            # AI analiz durumu ve güven skoru
            try:
                cursor.execute("""
                    SELECT ai_confidence, is_analyzed, ai_summary
                    FROM firms 
                    WHERE id = ?
                """, (firma_id,))
                ai_result = cursor.fetchone()
                
                if ai_result and hasattr(self, 'ai_status_card') and hasattr(self, 'ai_confidence_card'):
                    is_analyzed = ai_result[1] or 0
                    ai_confidence = ai_result[0] or 0
                    
                    if is_analyzed == 1:
                        self.ai_status_card.update_value("✅ Analiz Edildi")
                    else:
                        self.ai_status_card.update_value("⏳ Bekliyor")
                    
                    if ai_confidence:
                        self.ai_confidence_card.update_value(f"{ai_confidence:.1f}/1.0")
                    else:
                        self.ai_confidence_card.update_value("N/A")
            except:
                if hasattr(self, 'ai_status_card') and hasattr(self, 'ai_confidence_card'):
                    self.ai_status_card.update_value("❌ Hata")
                    self.ai_confidence_card.update_value("N/A")
            
            # Detaylı performans raporu
            if hasattr(self, 'perf_detail') and self.perf_detail:
                ai_status_text = "✅ Analiz Edildi" if ai_result and ai_result[1] == 1 else "⏳ Bekliyor"
                ai_confidence_text = f"{ai_result[0]:.2f}" if ai_result and ai_result[0] else "N/A"
                
                report = f"""📊 PERFORMANS ÖZETİ

📧 EMAIL METRİKLERİ:
• Açılma Oranı: %{email_open_rate}
• Tıklama Oranı: %{email_click_rate}  
• Yanıt Oranı: %{response_rate}
• Dönüşüm Oranı: %{conversion_rate}

🤖 AI ANALİZ DURUMU:
• Durum: {ai_status_text}
• Güven Skoru: {ai_confidence_text}

💡 ÖNERİLER:
• Email açılma oranını artırmak için kişiselleştirme yapın
• Tıklama oranını optimize etmek için CTA'ları güçlendirin
• AI analizi ile daha fazla içgörü elde edin
• Mail gönderme sıklığını optimize edin
                """
                self.perf_detail.setPlainText(report)
                
        except Exception as e:
            print(f"Performans metrikleri yüklenirken hata: {e}")
            # Fallback - varsayılan değerler
            self.email_open_rate_card.update_value("%0")
            self.email_click_rate_card.update_value("%0")
            self.response_rate_card.update_value("%0")
            self.conversion_rate_card.update_value("%0")
            if hasattr(self, 'ai_status_card'):
                self.ai_status_card.update_value("❌ Hata")
            if hasattr(self, 'ai_confidence_card'):
                self.ai_confidence_card.update_value("N/A")
    
    def analyze_firma(self):
        """AI ile detaylı firma analizi yap"""
        if not self.current_firma:
            self.analysis_results.setText("Lütfen önce bir firma seçin.")
            return
        
        if not self.ai_analyzer:
            self.analysis_results.setText("AI analiz modülü mevcut değil.")
            return
        
        try:
            # Firma ID'sini al
            firma_id = self.current_firma[0]
            
            # AI analizi başlat
            self.analysis_results.setText("🤖 AI detaylı analizi yapılıyor...")
            
            # Analiz sonucunu al
            analysis_result = self.ai_analyzer.analyze_firm_with_ai(firma_id)
            
            if analysis_result:
                # FirmAnalysis objesini string'e çevir
                analysis_text = self._format_analysis_result(analysis_result)
                self.analysis_results.setText(analysis_text)
            else:
                self.analysis_results.setText("Analiz tamamlandı ancak sonuç alınamadı.")
                
        except Exception as e:
            self.analysis_results.setText(f"Analiz sırasında hata oluştu: {e}")
    
    def _format_analysis_result(self, analysis_result):
        """FirmAnalysis objesini string'e çevir"""
        try:
            # Strategy recommendations'ı formatla
            strategy_text = ""
            if hasattr(analysis_result, 'strategy_recommendations') and analysis_result.strategy_recommendations:
                for i, rec in enumerate(analysis_result.strategy_recommendations, 1):
                    if isinstance(rec, dict):
                        strategy_text += f"{i}. {rec.get('reasoning', 'Öneri')}\n"
                    else:
                        strategy_text += f"{i}. {str(rec)}\n"
            else:
                strategy_text = "Strateji önerileri mevcut değil."
            
            # Risk assessment'ı formatla
            risk_text = ""
            if hasattr(analysis_result, 'risk_assessment') and analysis_result.risk_assessment:
                if isinstance(analysis_result.risk_assessment, dict):
                    risk_text = str(analysis_result.risk_assessment)
                else:
                    risk_text = str(analysis_result.risk_assessment)
            else:
                risk_text = "Risk değerlendirmesi mevcut değil."
            
            result_text = f"""
🤖 AI DETAYLI ANALİZ SONUCU

📊 Firma: {analysis_result.firm_name}
🏭 Sektör: {analysis_result.sector}
🎯 AI Güven Skoru: {analysis_result.ai_confidence:.2f}/1.0
📈 Fırsat Skoru: {analysis_result.opportunity_score:.2f}/10

🎯 STRATEJİ ÖNERİLERİ:
{strategy_text}

⚠️ RİSK DEĞERLENDİRMESİ:
{risk_text}

🤖 AI TALİMATLARI:
{analysis_result.ai_instructions}

📝 ÖZEL PROMPT:
{analysis_result.custom_prompt}

📊 ÖNERİLEN STRATEJİ: {analysis_result.recommended_strategy}
🕒 Analiz Tarihi: {analysis_result.analysis_date}
            """
            return result_text
        except Exception as e:
            return f"Analiz sonucu formatlanırken hata: {e}"
    
    def quick_analyze_firma(self):
        """AI ile hızlı firma analizi yap"""
        if not self.current_firma:
            self.analysis_results.setText("Lütfen önce bir firma seçin.")
            return
        
        try:
            # Hızlı analiz sonucu
            firma_name = self.current_firma[1]
            sector = self.current_firma[2] or "Belirtilmemiş"
            address = self.current_firma[3] or "Belirtilmemiş"
            
            quick_analysis = f"""
🚀 HIZLI ANALİZ SONUCU

📊 Firma: {firma_name}
🏭 Sektör: {sector}
📍 Adres: {address}

💡 ÖNERİLER:
• Bu firma {sector} sektöründe faaliyet gösteriyor
• {address} adresinde bulunuyor
• Detaylı analiz için "Detaylı Analiz" butonunu kullanın
• AI ile sohbet ederek daha fazla bilgi alabilirsiniz

🎯 SONRAKI ADIMLAR:
1. Firma hakkında AI'ya sorular sorun
2. Performans metriklerini inceleyin
3. İletişim geçmişini kontrol edin
4. AI önerilerini alın
            """
            
            self.analysis_results.setText(quick_analysis)
                
        except Exception as e:
            self.analysis_results.setText(f"Hızlı analiz sırasında hata oluştu: {e}")
    
    def send_message(self):
        """AI'ya mesaj gönder"""
        if not self.current_firma:
            self.add_chat_message("Lütfen önce bir firma seçin.", is_user=False)
            return
        
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Kullanıcı mesajını ekle
        self.add_chat_message(message, is_user=True)
        
        # Mesaj kutusunu temizle
        self.message_input.clear()
        
        # AI'dan yanıt al
        self.get_ai_response(message)
    
    def add_chat_message(self, message, is_user=True):
        """Chat'e mesaj ekle"""
        chat_message = ChatMessage(message, is_user)
        self.chat_layout.addWidget(chat_message)
        
        # Scroll'u en alta kaydır
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
    
    def get_ai_response(self, message):
        """AI'dan yanıt al"""
        if not self.ai_chat:
            self.add_chat_message("AI sohbet modülü mevcut değil.", is_user=False)
            return
        
        try:
            # Firma verilerini hazırla
            firma_context = f"""
            Firma: {self.current_firma[1]}
            Sektör: {self.current_firma[2]}
            Adres: {self.current_firma[3]}
            Website: {self.current_firma[4]}
            Telefon: {self.current_firma[5]}
            Email: {self.current_firma[6]}
            Özet: {self.current_firma[7]}
            """
            
            # AI'dan yanıt al
            if hasattr(self.ai_chat, 'ask_question'):
                response = self.ai_chat.ask_question(message, firma_context)
            else:
                # AI Chat Assistant'ın kendi sistemini kullan
                response = self._get_ai_response_from_assistant(message, firma_context)
            
            if response:
                self.add_chat_message(response, is_user=False)
            else:
                self.add_chat_message("AI'dan yanıt alınamadı.", is_user=False)
            
        except Exception as e:
            self.add_chat_message(f"Hata: {e}", is_user=False)
    
    def _get_ai_response_from_assistant(self, message, context):
        """AI Chat Assistant'tan yanıt al"""
        try:
            # AI Chat Assistant'ın worker'ını kullan
            if hasattr(self.ai_chat, 'context_builder'):
                system_context = self.ai_chat.context_builder.build_context()
            else:
                system_context = {}
            
            # OpenAI API key'i al
            api_key = None
            if self.api_manager and hasattr(self.api_manager, 'openai_api_key'):
                api_key = self.api_manager.openai_api_key
            else:
                # Config dosyasından oku
                try:
                    with open("config.json", "r") as f:
                        settings = json.load(f)
                        api_key = settings.get('openai_api_key')
                except:
                    pass
            
            if not api_key:
                return "OpenAI API anahtarı bulunamadı."
            
            # Basit OpenAI çağrısı
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            prompt = f"""
            Sen bir B2B pazarlama uzmanısın. Aşağıdaki firma bilgileri ve soruya göre yanıt ver:
            
            Firma Bilgileri:
            {context}
            
            Sistem Bağlamı:
            {system_context}
            
            Soru: {message}
            
            Lütfen kısa, net ve faydalı bir yanıt ver.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI yanıt alınırken hata oluştu: {e}"
    
    def clear_chat(self):
        """Chat'i temizle"""
        # Tüm chat widget'larını sil
        for i in reversed(range(self.chat_layout.count())):
            child = self.chat_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
    
    def get_ai_suggestions(self):
        """AI önerilerini al"""
        if not self.current_firma:
            self.ai_suggestions.setText("Lütfen önce bir firma seçin.")
            return
        
        try:
            firma_name = self.current_firma[1]
            sector = self.current_firma[2] or "Belirtilmemiş"
            location = self.current_firma[3] or "Belirtilmemiş"
            
            suggestions = f"""
💡 AI ÖNERİLERİ - {firma_name}

🎯 GENEL ÖNERİLER:
• {sector} sektöründe faaliyet gösteren bu firma için özel stratejiler geliştirin
• {location} konumundaki firma için yerel pazarlama yaklaşımları düşünün
• Firma büyüklüğüne göre iletişim tonunu ayarlayın

📧 EMAIL STRATEJİSİ:
• Kişiselleştirilmiş email şablonları kullanın
• Sektöre özel içerikler hazırlayın
• Takip email'leri için zamanlama planlayın

🤝 İLETİŞİM ÖNERİLERİ:
• Firma kültürüne uygun yaklaşım sergileyin
• Sektörel trendleri takip edin
• Rekabet analizi yapın

📈 PERFORMANS İYİLEŞTİRME:
• A/B testleri yapın
• Email açılma oranlarını optimize edin
• Geri bildirimleri değerlendirin

🚀 SONRAKI ADIMLAR:
1. Detaylı analiz yapın
2. AI ile sohbet ederek daha fazla bilgi alın
3. Performans metriklerini takip edin
4. İletişim geçmişini inceleyin
            """
            
            self.ai_suggestions.setText(suggestions)
                
        except Exception as e:
            self.ai_suggestions.setText(f"Öneriler alınırken hata oluştu: {e}")

# Test için ana fonksiyon
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Test veritabanı bağlantısı
    try:
        import sqlite3
        db = sqlite3.connect("b2b_automation.db")
        print("✅ Test veritabanı bağlandı")
    except:
        db = None
        print("⚠️ Test veritabanı bağlanamadı")
    
    # Widget'ı oluştur
    widget = FirmaDetayAnalyzer(db)
    widget.show()
    
    sys.exit(app.exec())