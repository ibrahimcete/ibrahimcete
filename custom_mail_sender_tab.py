#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Özel Mail Gönderim Sekmesi
AI destekli mail düzenleme ve tracking pixel entegrasyonu
"""

import sys
import json
import uuid
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QIcon
import requests
import re

class AIEmailProcessor(QThread):
    """AI ile email düzenleme thread'i"""
    processing_finished = Signal(str, bool)  # processed_text, success
    
    def __init__(self, email_text, prompt):
        super().__init__()
        self.email_text = email_text
        self.prompt = prompt
    
    def run(self):
        try:
            # OpenAI API ile email düzenleme
            api_key = "sk-proj-your-api-key-here"  # Gerçek API key'i config'den al
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "Sen profesyonel bir email editörüsün. Verilen email metnini kullanıcının isteğine göre düzenle."
                    },
                    {
                        "role": "user", 
                        "content": f"Email metni: {self.email_text}\n\nDüzenleme isteği: {self.prompt}\n\nLütfen düzenlenmiş email metnini döndür."
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                processed_text = result['choices'][0]['message']['content']
                self.processing_finished.emit(processed_text, True)
            else:
                self.processing_finished.emit(f"API Hatası: {response.status_code}", False)
                
        except Exception as e:
            self.processing_finished.emit(f"Hata: {str(e)}", False)

class CustomMailSenderTab(QWidget):
    """Özel Mail Gönderim Sekmesi"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.email_manager = None
        self.tracking_enabled = True
        self.setup_ui()
        
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel("📧 Özel Mail Gönderim")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Ana form
        form_widget = QWidget()
        form_layout = QGridLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Email adresi
        form_layout.addWidget(QLabel("📧 Alıcı Email:"), 0, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@firma.com")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.email_input, 0, 1)
        
        # Konu
        form_layout.addWidget(QLabel("📝 Konu:"), 1, 0)
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Email konusu...")
        self.subject_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.subject_input, 1, 1)
        
        # Tracking pixel seçeneği
        self.tracking_checkbox = QCheckBox("📊 Tracking Pixel Aktif")
        self.tracking_checkbox.setChecked(True)
        self.tracking_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #2c3e50;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        form_layout.addWidget(self.tracking_checkbox, 2, 0, 1, 2)
        
        # Email içeriği
        form_layout.addWidget(QLabel("📄 Email İçeriği:"), 3, 0)
        self.email_content = QTextEdit()
        self.email_content.setPlaceholderText("Email içeriğinizi buraya yazın...")
        self.email_content.setMinimumHeight(200)
        self.email_content.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addWidget(self.email_content, 3, 1)
        
        # AI Düzenleme bölümü
        ai_group = QGroupBox("🤖 AI ile Mail Düzenleme")
        ai_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
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
        ai_layout = QVBoxLayout(ai_group)
        
        # AI prompt
        ai_layout.addWidget(QLabel("💭 AI'ya Ne Yapmasını İstiyorsunuz?"))
        self.ai_prompt = QTextEdit()
        self.ai_prompt.setPlaceholderText("Örnek: 'Daha profesyonel yap', 'Daha samimi yap', 'Kısa ve öz yap'...")
        self.ai_prompt.setMaximumHeight(80)
        self.ai_prompt.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        ai_layout.addWidget(self.ai_prompt)
        
        # AI düzenle butonu
        self.ai_edit_button = QPushButton("🤖 AI ile Düzenle")
        self.ai_edit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.ai_edit_button.clicked.connect(self.process_with_ai)
        ai_layout.addWidget(self.ai_edit_button)
        
        # AI işlem durumu
        self.ai_status_label = QLabel("")
        self.ai_status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                font-style: italic;
            }
        """)
        ai_layout.addWidget(self.ai_status_label)
        
        form_layout.addWidget(ai_group, 4, 0, 1, 2)
        
        layout.addWidget(form_widget)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        # Gönder butonu
        self.send_button = QPushButton("📤 Mail Gönder")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.send_button.clicked.connect(self.send_email)
        button_layout.addWidget(self.send_button)
        
        # Temizle butonu
        self.clear_button = QPushButton("🗑️ Temizle")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Durum etiketi
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
    def set_email_manager(self, email_manager):
        """Email manager'ı ayarla"""
        self.email_manager = email_manager
        
    def process_with_ai(self):
        """AI ile email düzenleme"""
        if not self.email_content.toPlainText().strip():
            self.show_status("⚠️ Önce email içeriği yazın!", "warning")
            return
            
        if not self.ai_prompt.toPlainText().strip():
            self.show_status("⚠️ AI'ya ne yapmasını istediğinizi yazın!", "warning")
            return
        
        # UI'yi kilitle
        self.ai_edit_button.setEnabled(False)
        self.ai_status_label.setText("🤖 AI düzenleme yapıyor...")
        
        # AI thread'ini başlat
        self.ai_processor = AIEmailProcessor(
            self.email_content.toPlainText(),
            self.ai_prompt.toPlainText()
        )
        self.ai_processor.processing_finished.connect(self.on_ai_processing_finished)
        self.ai_processor.start()
        
    def on_ai_processing_finished(self, processed_text, success):
        """AI işlemi tamamlandığında"""
        self.ai_edit_button.setEnabled(True)
        
        if success:
            self.email_content.setPlainText(processed_text)
            self.ai_status_label.setText("✅ AI düzenleme tamamlandı!")
            self.show_status("🤖 AI ile email başarıyla düzenlendi!", "success")
        else:
            self.ai_status_label.setText(f"❌ Hata: {processed_text}")
            self.show_status(f"❌ AI düzenleme hatası: {processed_text}", "error")
    
    def send_email(self):
        """Email gönder"""
        # Validasyon
        if not self.email_input.text().strip():
            self.show_status("⚠️ Email adresi girin!", "warning")
            return
            
        if not self.subject_input.text().strip():
            self.show_status("⚠️ Konu girin!", "warning")
            return
            
        if not self.email_content.toPlainText().strip():
            self.show_status("⚠️ Email içeriği yazın!", "warning")
            return
        
        if not self.email_manager:
            self.show_status("❌ Email manager bulunamadı!", "error")
            return
        
        # Email gönderimi
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.send_button.setEnabled(False)
            
            # Tracking pixel ayarları
            tracking_enabled = self.tracking_checkbox.isChecked()
            
            # Email gönder
            result = self.email_manager.send_email(
                to_email=self.email_input.text().strip(),
                subject=self.subject_input.text().strip(),
                body=self.email_content.toPlainText(),
                firm_id="custom-mail",  # Özel mail için özel firm_id
                is_follow_up=False
            )
            
            if result.get('success', False):
                self.show_status("✅ Email başarıyla gönderildi!", "success")
                if tracking_enabled:
                    self.show_status("📊 Tracking pixel aktif - Email açılmaları takip edilecek", "info")
            else:
                self.show_status(f"❌ Email gönderim hatası: {result.get('error', 'Bilinmeyen hata')}", "error")
                
        except Exception as e:
            self.show_status(f"❌ Hata: {str(e)}", "error")
        finally:
            self.progress_bar.setVisible(False)
            self.send_button.setEnabled(True)
    
    def clear_form(self):
        """Formu temizle"""
        self.email_input.clear()
        self.subject_input.clear()
        self.email_content.clear()
        self.ai_prompt.clear()
        self.ai_status_label.setText("")
        self.show_status("🗑️ Form temizlendi", "info")
    
    def show_status(self, message, status_type="info"):
        """Durum mesajı göster"""
        self.status_label.setText(message)
        
        # Renk kodları
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c", 
            "warning": "#f39c12",
            "info": "#3498db"
        }
        
        color = colors.get(status_type, "#7f8c8d")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 14px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        
        # 3 saniye sonra temizle
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
