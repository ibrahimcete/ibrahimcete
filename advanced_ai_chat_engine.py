#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gelişmiş AI Chat Engine - Firmalar için Akıllı Asistan
Bu modül, veritabanına tam erişimli gelişmiş bir AI chat sistemi sağlar.
"""

import sys
import json
import sqlite3
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QLineEdit, QLabel, QScrollArea, QFrame, QListWidget, QListWidgetItem,
    QDialog, QApplication, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRectF
from PySide6.QtGui import QFont, QIcon, QColor, QPainter, QBrush, QPen, QCursor

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI kütüphanesi bulunamadı")


class FloatingChatButton(QPushButton):
    """Yuvarlak, floating chat butonu"""
    
    def __init__(self, parent=None):
        super().__init__("💬", parent)
        self.setFixedSize(60, 60)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 0.5 #764ba2, stop: 1 #f093fb);
                border: none;
                border-radius: 30px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #5a67d8, stop: 0.5 #6b46c1, stop: 1 #d672c0);
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #4c51bf, stop: 0.5 #5b21b6, stop: 1 #c85fac);
            }
        """)
        
        # Pulse animation
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_animation)
        self.pulse_timer.start(2000)
        self.pulse_state = 0
    
    def pulse_animation(self):
        """Pulse animasyonu"""
        self.pulse_state += 1
        if self.pulse_state % 2 == 0:
            self.setStyleSheet(self.styleSheet().replace("font-size: 24px", "font-size: 22px"))
        else:
            self.setStyleSheet(self.styleSheet().replace("font-size: 22px", "font-size: 24px"))


class ChatMessage(QFrame):
    """Chat mesaj widget'ı"""
    
    def __init__(self, message, is_user=True, timestamp=None, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        self.setup_ui()
    
    def setup_ui(self):
        """UI'ı oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # Mesaj container
        message_frame = QFrame()
        if self.is_user:
            message_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #667eea, stop: 1 #764ba2);
                    border-radius: 15px;
                    padding: 12px;
                    margin-left: 50px;
                }
            """)
        else:
            message_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #2a2a2a, stop: 1 #1a1a1a);
                    border-radius: 15px;
                    padding: 12px;
                    margin-right: 50px;
                    border: 1px solid #333;
                }
            """)
        
        message_layout = QVBoxLayout(message_frame)
        
        # Mesaj metni
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: white; font-size: 13px; padding: 5px;")
        message_layout.addWidget(message_label)
        
        # Timestamp
        time_label = QLabel(self.timestamp.strftime("%H:%M"))
        time_label.setStyleSheet("color: #aaa; font-size: 10px;")
        time_label.setAlignment(Qt.AlignRight)
        message_layout.addWidget(time_label)
        
        layout.addWidget(message_frame)


class AdvancedAIChatEngine(QDialog):
    """Gelişmiş AI Chat Engine - Ana Dialog"""
    
    # Signals
    firms_selected = Signal(list)  # Seçilen firmaları gönder
    
    def __init__(self, db_connection, api_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_connection
        self.api_manager = api_manager
        self.chat_history = []
        self.suggested_firms = []
        
        self.setWindowTitle("🤖 Gelişmiş AI Chat Asistanı")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)
        
        self.setup_ui()
        self.load_system_context()
        
    def setup_ui(self):
        """UI'ı oluştur"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 0.5 #764ba2, stop: 1 #f093fb);
                border: none;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("🤖 Gelişmiş AI Chat Asistanı")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("✖️")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 0, 0.3);
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        main_layout.addWidget(header)
        
        # Main content - splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Chat
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # Welcome message
        welcome = QLabel("💬 Merhaba! Size nasıl yardımcı olabilirim?\n\n"
                         "Örnek: 'Mail adresi olan ve teknoloji sektöründeki firmaları göster'")
        welcome.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 13px;
            }
        """)
        welcome.setWordWrap(True)
        left_layout.addWidget(welcome)
        
        # Chat scroll area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                background-color: #e9ecef;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #667eea;
                border-radius: 5px;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(15, 15, 15, 15)
        
        self.chat_scroll.setWidget(self.chat_widget)
        left_layout.addWidget(self.chat_scroll)
        
        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #667eea;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        # Buttons for quick actions
        quick_actions = QHBoxLayout()
        
        quick_btn = QPushButton("📧 Email'li Firmalar")
        quick_btn.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #5a67d8;
            }
        """)
        quick_btn.clicked.connect(lambda: self.send_quick_query("Email adresi olan firmaları göster"))
        
        quick_btn2 = QPushButton("🏭 Teknoloji Sektörü")
        quick_btn2.setStyleSheet(quick_btn.styleSheet())
        quick_btn2.clicked.connect(lambda: self.send_quick_query("Teknoloji sektöründeki firmaları göster"))
        
        quick_btn3 = QPushButton("⭐ Yüksek Rating")
        quick_btn3.setStyleSheet(quick_btn.styleSheet())
        quick_btn3.clicked.connect(lambda: self.send_quick_query("Rating'i yüksek olan firmaları göster"))
        
        quick_actions.addWidget(quick_btn)
        quick_actions.addWidget(quick_btn2)
        quick_actions.addWidget(quick_btn3)
        quick_actions.addStretch()
        
        input_layout.addLayout(quick_actions)
        
        # Text input
        input_row = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Mesajınızı yazın...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 10px;
                font-size: 13px;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        
        send_btn = QPushButton("📤")
        send_btn.setFixedSize(45, 45)
        send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                border: none;
                border-radius: 22px;
                color: white;
                font-size: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #5a67d8, stop: 1 #6b46c1);
            }
        """)
        send_btn.clicked.connect(self.send_message)
        
        input_row.addWidget(self.message_input)
        input_row.addWidget(send_btn)
        
        input_layout.addLayout(input_row)
        left_layout.addWidget(input_frame)
        
        splitter.addWidget(left_widget)
        
        # Right panel - Suggested firms
        right_widget = QWidget()
        right_widget.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        right_title = QLabel("🎯 AI Önerileri")
        right_title.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        right_layout.addWidget(right_title)
        
        # Suggested firms list
        self.suggested_list = QListWidget()
        self.suggested_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #e9ecef;
                padding: 8px;
            }
            QListWidget::item:hover {
                background: #f8f9fa;
            }
            QListWidget::item:selected {
                background: #667eea;
                color: white;
            }
        """)
        right_layout.addWidget(self.suggested_list)
        
        # Action buttons
        action_layout = QVBoxLayout()
        
        add_to_campaign_btn = QPushButton("📧 Kampanyaya Ekle")
        add_to_campaign_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #5a67d8, stop: 1 #6b46c1);
            }
        """)
        add_to_campaign_btn.clicked.connect(self.add_suggested_to_campaign)
        
        clear_btn = QPushButton("🗑️ Temizle")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #dc3545;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        clear_btn.clicked.connect(self.clear_suggestions)
        
        action_layout.addWidget(add_to_campaign_btn)
        action_layout.addWidget(clear_btn)
        
        right_layout.addLayout(action_layout)
        
        splitter.addWidget(right_widget)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Başlangıç mesajı
        self.add_system_message("Merhaba! Ben gelişmiş AI chat asistanınız. "
                               "Firma veritabanınızdan veri çekebilir, sorgular yapabilir "
                               "ve en uygun firmaları önerebilirim. Size nasıl yardımcı olabilirim?")
    
    def load_system_context(self):
        """Sistem bağlamını yükle - veritabanı istatistikleri"""
        if not self.db:
            return
        
        try:
            # Veritabanından istatistikleri al
            cursor = self._get_cursor()
            if not cursor:
                return
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_firms,
                    SUM(CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END) as firms_with_email,
                    COUNT(DISTINCT sector) as unique_sectors
                FROM firms
            """)
            
            stats = cursor.fetchone()
            if stats:
                self.system_context = {
                    'total_firms': stats[0] or 0,
                    'firms_with_email': stats[1] or 0,
                    'unique_sectors': stats[2] or 0
                }
            else:
                self.system_context = {
                    'total_firms': 0,
                    'firms_with_email': 0,
                    'unique_sectors': 0
                }
                
        except Exception as e:
            print(f"System context yüklenirken hata: {e}")
            self.system_context = {
                'total_firms': 0,
                'firms_with_email': 0,
                'unique_sectors': 0
            }
    
    def _get_cursor(self):
        """Veritabanı cursor'unu al"""
        try:
            if hasattr(self.db, 'cursor'):
                return self.db.cursor
            elif hasattr(self.db, 'execute'):
                return self.db
            else:
                # SQLite connection from file
                if isinstance(self.db, str):
                    import sqlite3
                    return sqlite3.connect(self.db)
                return None
        except Exception as e:
            print(f"Cursor alınırken hata: {e}")
            return None
    
    def add_system_message(self, message):
        """Sistem mesajı ekle"""
        msg = ChatMessage(f"🤖 AI: {message}", is_user=False)
        self.chat_layout.addWidget(msg)
        self.scroll_to_bottom()
    
    def add_user_message(self, message):
        """Kullanıcı mesajı ekle"""
        msg = ChatMessage(message, is_user=True)
        self.chat_layout.addWidget(msg)
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Chat'i en alta kaydır"""
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
    
    def send_quick_query(self, query):
        """Hızlı sorgu gönder"""
        self.message_input.setText(query)
        self.send_message()
    
    def send_message(self):
        """Mesaj gönder"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        # Kullanıcı mesajını ekle
        self.add_user_message(message)
        self.message_input.clear()
        
        # AI yanıtını al
        self.get_ai_response(message)
    
    def get_ai_response(self, user_message):
        """AI'dan yanıt al ve firmaları öner"""
        try:
            # SQL sorgusu oluştur
            sql_query, suggested_firms = self.analyze_query_and_get_firms(user_message)
            
            # Sonuçları göster
            if suggested_firms:
                response_text = f"🎯 {len(suggested_firms)} firma bulundu!\n\n"
                
                # Öne çıkan bilgiler
                for i, firm in enumerate(suggested_firms[:5], 1):
                    email_status = "✅ Email: Var" if firm.get('email') else "❌ Email: Yok"
                    response_text += f"{i}. {firm.get('name', 'N/A')} - {email_status}\n"
                
                if len(suggested_firms) > 5:
                    response_text += f"\n... ve {len(suggested_firms) - 5} firma daha"
                
                self.add_system_message(response_text)
                
                # Önerilen firmaları listeye ekle
                self.suggested_firms = suggested_firms
                self.update_suggested_list()
            else:
                self.add_system_message("❌ Üzgünüm, veritabanında bu kriterlere uygun firma bulunamadı. "
                                       "Başka bir sorgu deneyebilirsiniz.")
        
        except Exception as e:
            self.add_system_message(f"❌ Hata oluştu: {str(e)}")
    
    def analyze_query_and_get_firms(self, query):
        """Sorguyu analiz et ve uygun firmaları getir"""
        cursor = self._get_cursor()
        if not cursor:
            return None, []
        
        # Basit keyword-based parsing (GPT için prompt hazırlığı)
        query_lower = query.lower()
        
        # SQL sorgusu oluştur
        conditions = []
        
        # Email kontrolü
        if "email" in query_lower or "mail" in query_lower:
            conditions.append("(email IS NOT NULL AND email != '' OR emails IS NOT NULL AND emails != '[]')")
        
        # Sektör kontrolü
        if "teknoloji" in query_lower or "technology" in query_lower:
            conditions.append("sector LIKE '%Teknoloji%'")
        elif "inşaat" in query_lower:
            conditions.append("sector LIKE '%İnşaat%'")
        elif "gıda" in query_lower:
            conditions.append("sector LIKE '%Gıda%'")
        elif "finans" in query_lower:
            conditions.append("sector LIKE '%Finans%'")
        
        # Rating kontrolü
        if "yüksek" in query_lower and "rating" in query_lower:
            conditions.append("rating >= 8")
        elif "düşük" in query_lower and "rating" in query_lower:
            conditions.append("rating < 5")
        
        # Website kontrolü
        if "website" in query_lower or "web" in query_lower:
            conditions.append("website IS NOT NULL AND website != ''")
        
        # SQL sorgusunu oluştur
        sql_query = "SELECT id, name, sector, email, phone, website, rating, address, summary FROM firms"
        
        if conditions:
            sql_query += " WHERE " + " AND ".join(conditions)
        
        sql_query += " ORDER BY rating DESC LIMIT 20"
        
        # Sorguyu çalıştır
        try:
            cursor.execute(sql_query)
            firms = cursor.fetchall()
            
            # Firmaları dict'e çevir
            suggested_firms = []
            for firm in firms:
                suggested_firms.append({
                    'id': firm[0],
                    'name': firm[1],
                    'sector': firm[2],
                    'email': firm[3],
                    'phone': firm[4],
                    'website': firm[5],
                    'rating': firm[6],
                    'address': firm[7],
                    'summary': firm[8]
                })
            
            return sql_query, suggested_firms
            
        except Exception as e:
            print(f"SQL sorgusu hatası: {e}")
            return None, []
    
    def update_suggested_list(self):
        """Önerilen firma listesini güncelle"""
        self.suggested_list.clear()
        
        for firm in self.suggested_firms:
            email_status = "✅" if firm.get('email') else "❌"
            item_text = f"{email_status} {firm.get('name')} ({firm.get('sector', 'N/A')})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, firm.get('id'))
            self.suggested_list.addItem(item)
    
    def clear_suggestions(self):
        """Önerileri temizle"""
        self.suggested_list.clear()
        self.suggested_firms = []
        self.add_system_message("✅ Öneriler temizlendi.")
    
    def add_suggested_to_campaign(self):
        """Önerilen firmaları kampanyaya ekle"""
        if not self.suggested_firms:
            QMessageBox.warning(self, "Uyarı", "Kampanyaya eklenecek firma seçilmedi!")
            return
        
        # Signal gönder
        self.firms_selected.emit(self.suggested_firms)
        
        self.add_system_message(f"✅ {len(self.suggested_firms)} firma kampanyaya eklendi!")
        QMessageBox.information(self, "Başarılı", 
                               f"{len(self.suggested_firms)} firma kampanyaya eklendi!")


# Test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Mock database
    import sqlite3
    db = sqlite3.connect("b2b_automation.db")
    
    chat = AdvancedAIChatEngine(db)
    chat.show()
    
    sys.exit(app.exec())

