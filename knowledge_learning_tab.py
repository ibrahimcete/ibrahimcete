#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firma Bilgi Öğretim Sekmesi - AI Powered Knowledge Learning
Firmanız hakkında her türlü bilgiyi yükleyin ve AI'a öğretin!
"""

import sys
import json
import os
import base64
from datetime import datetime
from typing import Dict, List
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QImage, QColor
import openai
import requests

# BeautifulSoup
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("BeautifulSoup4 bulunamadı. URL analizi devre dışı.")

# PDF okuma için
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("PyPDF2 bulunamadı. PDF okuma devre dışı.")

# Görsel analiz için
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow bulunamadı. Görsel analiz devre dışı.")


class KnowledgeLearningWorker(QThread):
    """Arka planda AI öğrenme işlemlerini yapar"""
    progress = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, knowledge_data, task_type, openai_api_key):
        super().__init__()
        self.knowledge_data = knowledge_data
        self.task_type = task_type
        self.openai_api_key = openai_api_key
        # Yeni OpenAI API client
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
    
    def run(self):
        try:
            if self.task_type == "learn_text":
                self.learn_text_content()
            elif self.task_type == "learn_pdf":
                self.learn_pdf_content()
            elif self.task_type == "learn_image":
                self.learn_image_content()
            elif self.task_type == "learn_url":
                self.learn_url_content()
            elif self.task_type == "analyze_all":
                self.analyze_all_knowledge()
        except Exception as e:
            self.error.emit(f"Öğrenme hatası: {str(e)}")
    
    def learn_text_content(self):
        """Metin içeriğini analiz et ve öğren"""
        content = self.knowledge_data.get('content', '')
        title = self.knowledge_data.get('title', 'İsimsiz')
        
        self.progress.emit(f"📝 {title} analiz ediliyor...")
        
        # GPT ile detaylı analiz
        messages = [
            {
                "role": "system",
                "content": """Sen bir B2B firma bilgi analisti uzmanısın. 
                Verilen içeriği detaylıca analiz et ve aşağıdaki formatta özetle:
                
                1. Önemli Bilgiler: (Ürünler, hizmetler, kampanyalar, fiyatlar)
                2. Hedef Kitle: (Kim için?)
                3. Öne Çıkan Özellikler: (USP - Unique Selling Points)
                4. Aksiyon Önerileri: (Mail/WhatsApp kampanyalarında nasıl kullanılabilir?)
                5. Anahtar Kelimeler: (Etiketler)
                
                Profesyonel ve detaylı bir analiz yap."""
            },
            {
                "role": "user",
                "content": f"Başlık: {title}\n\nİçerik:\n{content}"
            }
        ]
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        
        analysis = response.choices[0].message.content.strip()
        
        # Kısa özet oluştur
        summary_messages = [
            {
                "role": "system",
                "content": "Verilen analizi 4-5 cümleyle özetle. Kısa ve öz ol."
            },
            {
                "role": "user",
                "content": analysis
            }
        ]
        
        summary_response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=summary_messages,
            temperature=0.3,
            max_tokens=150
        )
        
        summary = summary_response.choices[0].message.content.strip()
        
        self.progress.emit(f"✅ {title} öğrenildi!")
        
        self.finished.emit({
            'id': self.knowledge_data.get('id'),
            'analysis': analysis,
            'summary': summary,
            'tokens_used': response.usage.total_tokens + summary_response.usage.total_tokens
        })
    
    def learn_pdf_content(self):
        """PDF içeriğini oku ve öğren"""
        if not PDF_AVAILABLE:
            self.error.emit("PDF okuma için PyPDF2 kurulu değil!")
            return
        
        file_path = self.knowledge_data.get('file_path', '')
        title = self.knowledge_data.get('title', 'İsimsiz PDF')
        
        self.progress.emit(f"📄 {title} okunuyor...")
        
        try:
            # PDF'den metin çıkar
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n\n"
                    
                    if page_num % 5 == 0:
                        self.progress.emit(f"📄 Sayfa {page_num + 1}/{len(pdf_reader.pages)} okundu...")
            
            # Metin çok uzunsa özetle
            if len(text_content) > 10000:
                self.progress.emit("📝 İçerik çok uzun, özetleniyor...")
                
                messages = [
                    {
                        "role": "system",
                        "content": "Verilen PDF içeriğini özetle. Önemli bilgileri koru."
                    },
                    {
                        "role": "user",
                        "content": text_content[:15000]  # İlk 10000 karakter
                    }
                ]
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo-16k",
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2000
                )
                
                text_content = response.choices[0].message.content.strip()
            
            # Şimdi içeriği öğren
            self.knowledge_data['content'] = text_content
            self.learn_text_content()
            
        except Exception as e:
            self.error.emit(f"PDF okuma hatası: {str(e)}")
    
    def learn_image_content(self):
        """Görsel içeriğini analiz et (GPT-4o)"""
        file_path = self.knowledge_data.get('file_path', '')
        title = self.knowledge_data.get('title', 'İsimsiz Görsel')
        
        self.progress.emit(f"🖼️ {title} analiz ediliyor...")
        
        try:
            # Görseli base64'e çevir
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # GPT-4 Vision ile analiz
            messages = [
                {
                    "role": "system",
                    "content": """Sen bir görsel analiz uzmanısın. 
                    Verilen görseli detaylıca analiz et ve şunları belirt:
                    
                    1. Görselde ne var? (Ürün, kampanya, grafik, vs)
                    2. Önemli detaylar (Fiyatlar, özellikler, metinler)
                    3. Pazarlama değeri (Bu görsel kampanyalarda nasıl kullanılabilir?)
                    4. Hedef kitle
                    
                    Profesyonel ve detaylı bir analiz yap."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Görsel Başlık: {title}\n\nBu görseli analiz et:"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=3000
            )
            
            analysis = response.choices[0].message.content.strip()
            
            # Kısa özet
            summary = analysis[:200] + "..." if len(analysis) > 200 else analysis
            
            self.progress.emit(f"✅ {title} öğrenildi!")
            
            self.finished.emit({
                'id': self.knowledge_data.get('id'),
                'analysis': analysis,
                'summary': summary,
                'tokens_used': response.usage.total_tokens
            })
            
        except Exception as e:
            self.error.emit(f"Görsel analiz hatası: {str(e)}")
    
    def learn_url_content(self):
        """Web sitesi/link içeriğini öğren"""
        url = self.knowledge_data.get('url', '')
        title = self.knowledge_data.get('title', 'İsimsiz Link')
        
        self.progress.emit(f"🌐 {url} analiz ediliyor...")
        
        if not BS4_AVAILABLE:
            self.error.emit("URL analizi için BeautifulSoup4 kurulu değil!")
            return
        
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Metni çıkar
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Çok uzunsa kısalt
            if len(text_content) > 8000:
                text_content = text_content[:8000]
            
            self.knowledge_data['content'] = text_content
            self.learn_text_content()
            
        except Exception as e:
            self.error.emit(f"URL okuma hatası: {str(e)}")
    
    def analyze_all_knowledge(self):
        """Tüm öğrenilen bilgileri birleştirerek genel analiz yap"""
        all_knowledge = self.knowledge_data.get('all_items', [])
        
        self.progress.emit("🧠 Tüm bilgiler birleştiriliyor ve analiz ediliyor...")
        
        # Tüm özetleri birleştir
        combined_summary = "\n\n".join([
            f"- {item.get('title', 'İsimsiz')}: {item.get('ai_summary', 'Özet yok')}"
            for item in all_knowledge if item.get('is_learned')
        ])
        
        messages = [
            {
                "role": "system",
                "content": """Sen bir B2B strateji uzmanısın. 
                Firmanın tüm öğrenilmiş bilgilerini analiz et ve:
                
                1. Firma Profili Özeti (Kim, ne yapıyor?)
                2. Güçlü Yönler (Neyle öne çıkıyor?)
                3. Kampanya Stratejisi (Hangi mesajlar kullanılmalı?)
                4. Hedef Müşteri Profili (Kime satış yapmalı?)
                5. Öneriler (İyileştirme noktaları)
                
                Kapsamlı bir rapor hazırla."""
            },
            {
                "role": "user",
                "content": f"Firma Bilgileri:\n\n{combined_summary}"
            }
        ]
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )
        
        analysis = response.choices[0].message.content.strip()
        
        self.progress.emit("✅ Genel analiz tamamlandı!")
        
        self.finished.emit({
            'type': 'general_analysis',
            'analysis': analysis,
            'tokens_used': response.usage.total_tokens
        })


class KnowledgeLearningTab(QWidget):
    """Firma Bilgi Öğretim Sekmesi"""
    
    def __init__(self, db, api_manager):
        super().__init__()
        self.db = db
        self.api_manager = api_manager
        self.current_worker = None
        self.init_ui()
        self.load_knowledge_list()
    
    def init_ui(self):
        """Arayüzü oluştur"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Başlık
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Ana içerik - Split layout
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Sol panel - Veri yükleme
        left_panel = self.create_upload_panel()
        content_splitter.addWidget(left_panel)
        
        # Sağ panel - Öğrenilen bilgiler listesi
        right_panel = self.create_knowledge_list_panel()
        content_splitter.addWidget(right_panel)
        
        content_splitter.setStretchFactor(0, 2)
        content_splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(content_splitter)
        
        # Alt panel - İlerleme ve kontroller
        bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(bottom_panel)
        
        self.apply_modern_theme()
    
    def create_header(self):
        """Başlık paneli"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(header_widget)
        
        title = QLabel("🧠 Firma Bilgi Öğretim Merkezi")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Firmanız hakkında her türlü bilgiyi yükleyin, AI öğrensin ve kampanyalarınızda kullansın!")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 5px;
        """)
        layout.addWidget(subtitle)
        
        # İstatistikler
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        try:
            all_knowledge = self.db.get_all_knowledge()
            learned_count = sum(1 for k in all_knowledge if k.get('is_learned'))
            pending_count = len(all_knowledge) - learned_count
            
            self.add_stat_badge(stats_layout, "📚 Toplam Bilgi", str(len(all_knowledge)))
            self.add_stat_badge(stats_layout, "✅ Öğrenildi", str(learned_count))
            self.add_stat_badge(stats_layout, "⏳ Bekliyor", str(pending_count))
        except:
            pass
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        return header_widget
    
    def add_stat_badge(self, layout, label, value):
        """İstatistik rozeti ekle"""
        badge = QLabel(f"{label}: {value}")
        badge.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
        """)
        layout.addWidget(badge)
    
    def create_upload_panel(self):
        """Veri yükleme paneli"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Panel başlığı
        title = QLabel("📤 Yeni Bilgi Ekle")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Sekmeli yükleme bölümü
        upload_tabs = QTabWidget()
        upload_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #2a2a2a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: white;
                padding: 10px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #667eea;
            }
        """)
        
        # Sekme 1: Metin
        text_tab = self.create_text_upload_tab()
        upload_tabs.addTab(text_tab, "📝 Metin")
        
        # Sekme 2: Dosya
        file_tab = self.create_file_upload_tab()
        upload_tabs.addTab(file_tab, "📄 Dosya")
        
        # Sekme 3: Link
        url_tab = self.create_url_upload_tab()
        upload_tabs.addTab(url_tab, "🌐 Link")
        
        # Sekme 4: Görsel
        image_tab = self.create_image_upload_tab()
        upload_tabs.addTab(image_tab, "🖼️ Görsel")
        
        layout.addWidget(upload_tabs)
        
        # Hızlı öğrenme butonu
        learn_all_btn = QPushButton("🚀 Tüm Bekleyen Bilgileri Öğren")
        learn_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f093fb, stop:1 #f5576c);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f5576c, stop:1 #f093fb);
            }
        """)
        learn_all_btn.clicked.connect(self.learn_all_pending)
        layout.addWidget(learn_all_btn)
        
        return panel
    
    def create_text_upload_tab(self):
        """Metin yükleme sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title_layout = QHBoxLayout()
        title_label = QLabel("Başlık:")
        title_label.setStyleSheet("color: white; font-size: 13px;")
        self.text_title_input = QLineEdit()
        self.text_title_input.setPlaceholderText("Örn: Yaz Kampanyası 2024")
        self.text_title_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.text_title_input)
        layout.addLayout(title_layout)
        
        # İçerik
        content_label = QLabel("İçerik:")
        content_label.setStyleSheet("color: white; font-size: 13px; margin-top: 10px;")
        layout.addWidget(content_label)
        
        self.text_content_input = QTextEdit()
        self.text_content_input.setPlaceholderText(
            "Buraya firmanız hakkında bilgi, ürün açıklaması, kampanya detayı, "
            "fiyat listesi, hizmet açıklaması... her türlü metni yazabilirsiniz.\n\n"
            "Örnek:\n"
            "Yaz Kampanyası 2024\n"
            "Tüm ürünlerde %30 indirim!\n"
            "Kampanya tarihleri: 15 Haziran - 15 Ağustos\n"
            "Minimum sipariş tutarı: 1000 TL"
        )
        self.text_content_input.setStyleSheet("""
            QTextEdit {
                background-color: #3a3a3a;
                color: white;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.text_content_input)
        
        # Etiketler
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Etiketler:")
        tags_label.setStyleSheet("color: white; font-size: 13px;")
        self.text_tags_input = QLineEdit()
        self.text_tags_input.setPlaceholderText("kampanya, indirim, yaz (virgülle ayırın)")
        self.text_tags_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
            }
        """)
        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.text_tags_input)
        layout.addLayout(tags_layout)
        
        # Ekle butonu
        add_btn = QPushButton("➕ Ekle ve Öğren")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
        """)
        add_btn.clicked.connect(self.add_text_knowledge)
        layout.addWidget(add_btn)
        
        return tab
    
    def create_file_upload_tab(self):
        """Dosya yükleme sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("📄 PDF, DOCX, TXT dosyalarını yükleyin")
        info_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            padding: 15px;
            background-color: rgba(102, 126, 234, 0.2);
            border-radius: 8px;
        """)
        layout.addWidget(info_label)
        
        # Dosya seçimi
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("Dosya seçilmedi")
        self.file_path_label.setStyleSheet("color: #999; font-size: 12px;")
        file_layout.addWidget(self.file_path_label)
        
        select_file_btn = QPushButton("📁 Dosya Seç")
        select_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(select_file_btn)
        layout.addLayout(file_layout)
        
        layout.addStretch()
        
        # Yükle butonu
        upload_btn = QPushButton("📤 Yükle ve Öğren")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
        """)
        upload_btn.clicked.connect(self.upload_file_knowledge)
        layout.addWidget(upload_btn)
        
        return tab
    
    def create_url_upload_tab(self):
        """Link yükleme sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("🌐 Web sitesi, sosyal medya, blog linki ekleyin")
        info_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            padding: 15px;
            background-color: rgba(102, 126, 234, 0.2);
            border-radius: 8px;
        """)
        layout.addWidget(info_label)
        
        # Başlık
        title_layout = QHBoxLayout()
        title_label = QLabel("Başlık:")
        title_label.setStyleSheet("color: white; font-size: 13px;")
        self.url_title_input = QLineEdit()
        self.url_title_input.setPlaceholderText("Örn: Firma Web Sitesi")
        self.url_title_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.url_title_input)
        layout.addLayout(title_layout)
        
        # URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        url_label.setStyleSheet("color: white; font-size: 13px;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://ornek.com/sayfa")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: white;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
            }
        """)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        layout.addStretch()
        
        # Ekle butonu
        add_btn = QPushButton("🌐 Ekle ve Öğren")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
        """)
        add_btn.clicked.connect(self.add_url_knowledge)
        layout.addWidget(add_btn)
        
        return tab
    
    def create_image_upload_tab(self):
        """Görsel yükleme sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        
        info_label = QLabel("🖼️ Ürün görselleri, kataloglar, infografikler yükleyin")
        info_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            padding: 15px;
            background-color: rgba(102, 126, 234, 0.2);
            border-radius: 8px;
        """)
        layout.addWidget(info_label)
        
        # Görsel önizleme
        self.image_preview = QLabel("Görsel seçilmedi")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 2px dashed #4a4a4a;
                border-radius: 8px;
                color: #999;
                min-height: 200px;
            }
        """)
        layout.addWidget(self.image_preview)
        
        # Dosya seçimi butonları
        buttons_layout = QHBoxLayout()
        
        select_image_btn = QPushButton("🖼️ Tek Görsel Seç")
        select_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        select_image_btn.clicked.connect(self.select_image)
        buttons_layout.addWidget(select_image_btn)
        
        select_multiple_images_btn = QPushButton("📁 Toplu Görsel Seç")
        select_multiple_images_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        select_multiple_images_btn.clicked.connect(self.select_multiple_images)
        buttons_layout.addWidget(select_multiple_images_btn)
        
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
        
        # Yükle butonu
        upload_btn = QPushButton("🖼️ Yükle ve Analiz Et (GPT-4o)")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
        """)
        upload_btn.clicked.connect(self.upload_image_knowledge)
        layout.addWidget(upload_btn)
        
        return tab
    
    def create_knowledge_list_panel(self):
        """Öğrenilen bilgiler listesi paneli"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Panel başlığı ve arama
        header_layout = QHBoxLayout()
        
        title = QLabel("📚 Öğrenilen Bilgiler")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Arama
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Ara...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: white;
                padding: 8px 15px;
                border-radius: 20px;
                border: 1px solid #3a3a3a;
                min-width: 200px;
            }
        """)
        self.search_input.textChanged.connect(self.search_knowledge)
        header_layout.addWidget(self.search_input)
        
        layout.addLayout(header_layout)
        
        # Filtre butonları
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        self.filter_all_btn = QPushButton("Tümü")
        self.filter_learned_btn = QPushButton("✅ Öğrenildi")
        self.filter_pending_btn = QPushButton("⏳ Bekliyor")
        
        for btn in [self.filter_all_btn, self.filter_learned_btn, self.filter_pending_btn]:
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 15px;
                    border: 1px solid #3a3a3a;
                }
                QPushButton:checked {
                    background-color: #667eea;
                    border: 1px solid #667eea;
                }
            """)
            filter_layout.addWidget(btn)
        
        self.filter_all_btn.setChecked(True)
        self.filter_all_btn.clicked.connect(lambda: self.filter_knowledge('all'))
        self.filter_learned_btn.clicked.connect(lambda: self.filter_knowledge('learned'))
        self.filter_pending_btn.clicked.connect(lambda: self.filter_knowledge('pending'))
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Liste
        self.knowledge_list = QListWidget()
        self.knowledge_list.setStyleSheet("""
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                padding: 5px;
            }
            QListWidget::item {
                background-color: #1a1a1a;
                color: white;
                padding: 15px;
                margin: 5px;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
            QListWidget::item:hover {
                background-color: #2a2a2a;
                border: 1px solid #667eea;
            }
            QListWidget::item:selected {
                background-color: #667eea;
                border: 1px solid #764ba2;
            }
        """)
        self.knowledge_list.itemDoubleClicked.connect(self.view_knowledge_detail)
        layout.addWidget(self.knowledge_list)
        
        # Alt butonlar
        actions_layout = QHBoxLayout()
        
        view_btn = QPushButton("👁️ Görüntüle")
        view_btn.clicked.connect(self.view_selected_knowledge)
        
        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.clicked.connect(self.delete_selected_knowledge)
        
        for btn in [view_btn, delete_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 8px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
            actions_layout.addWidget(btn)
        
        layout.addLayout(actions_layout)
        
        return panel
    
    def create_bottom_panel(self):
        """Alt panel - İlerleme ve kontroller"""
        panel = QWidget()
        panel.setMaximumHeight(120)
        panel.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # İlerleme etiketi
        self.progress_label = QLabel("Hazır")
        self.progress_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(self.progress_label)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                text-align: center;
                color: white;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Kontrol butonları
        controls_layout = QHBoxLayout()
        
        self.analyze_all_btn = QPushButton("🧠 Genel Analiz Yap")
        self.analyze_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4facfe, stop:1 #00f2fe);
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00f2fe, stop:1 #4facfe);
            }
        """)
        self.analyze_all_btn.clicked.connect(self.analyze_all_knowledge)
        controls_layout.addWidget(self.analyze_all_btn)
        
        # Ek analiz butonu
        self.deep_analyze_btn = QPushButton("🧠 Tüm Bilgileri Birleştir ve Analiz Et")
        self.deep_analyze_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #764ba2, stop:1 #667eea);
            }
        """)
        self.deep_analyze_btn.clicked.connect(self.deep_analyze_all_knowledge)
        controls_layout.addWidget(self.deep_analyze_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        return panel
    
    def apply_modern_theme(self):
        """Modern tema uygula"""
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                color: white;
                font-family: 'Segoe UI', Arial;
            }
        """)
    
    # ==================== Fonksiyonlar ====================
    
    def add_text_knowledge(self):
        """Metin bilgisi ekle"""
        title = self.text_title_input.text().strip()
        content = self.text_content_input.toPlainText().strip()
        tags_text = self.text_tags_input.text().strip()
        
        if not title or not content:
            QMessageBox.warning(self, "Uyarı", "Başlık ve içerik boş olamaz!")
            return
        
        tags = [tag.strip() for tag in tags_text.split(',')] if tags_text else []
        
        # Veritabanına ekle
        knowledge_id = self.db.add_knowledge(
            title=title,
            content_type='text',
            content=content,
            tags=tags
        )
        
        if knowledge_id:
            self.progress_label.setText(f"✅ '{title}' eklendi, öğreniliyor...")
            
            # Öğren
            self.start_learning(knowledge_id, 'text', {
                'id': knowledge_id,
                'title': title,
                'content': content
            })
            
            # Formu temizle
            self.text_title_input.clear()
            self.text_content_input.clear()
            self.text_tags_input.clear()
        else:
            QMessageBox.critical(self, "Hata", "Bilgi eklenemedi!")
    
    def select_file(self):
        """Dosya seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Dosya Seç",
            "",
            "Tüm Dosyalar (*.pdf *.docx *.txt);;PDF (*.pdf);;Word (*.docx);;Metin (*.txt)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            self.file_path_label.setStyleSheet("color: #667eea; font-size: 12px; font-weight: bold;")
    
    def upload_file_knowledge(self):
        """Dosya bilgisi yükle"""
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            QMessageBox.warning(self, "Uyarı", "Önce bir dosya seçin!")
            return
        
        file_name = os.path.basename(self.selected_file_path)
        file_size = os.path.getsize(self.selected_file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Veritabanına ekle
        knowledge_id = self.db.add_knowledge(
            title=file_name,
            content_type='file',
            file_path=self.selected_file_path
        )
        
        if knowledge_id:
            # Dosyayı kaydet
            self.db.save_uploaded_file(
                file_name=file_name,
                file_type=file_ext,
                file_size=file_size,
                file_path=self.selected_file_path,
                knowledge_id=knowledge_id
            )
            
            self.progress_label.setText(f"✅ '{file_name}' yüklendi, öğreniliyor...")
            
            # PDF ise öğren
            if file_ext == '.pdf' and PDF_AVAILABLE:
                self.start_learning(knowledge_id, 'pdf', {
                    'id': knowledge_id,
                    'title': file_name,
                    'file_path': self.selected_file_path
                })
            else:
                self.progress_label.setText(f"⚠️ {file_ext} dosyaları henüz desteklenmiyor")
                self.load_knowledge_list()
        else:
            QMessageBox.critical(self, "Hata", "Dosya yüklenemedi!")
    
    def add_url_knowledge(self):
        """URL bilgisi ekle"""
        title = self.url_title_input.text().strip()
        url = self.url_input.text().strip()
        
        if not title or not url:
            QMessageBox.warning(self, "Uyarı", "Başlık ve URL boş olamaz!")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Veritabanına ekle
        knowledge_id = self.db.add_knowledge(
            title=title,
            content_type='url',
            url=url
        )
        
        if knowledge_id:
            self.progress_label.setText(f"✅ '{title}' eklendi, öğreniliyor...")
            
            # Öğren
            self.start_learning(knowledge_id, 'url', {
                'id': knowledge_id,
                'title': title,
                'url': url
            })
            
            # Formu temizle
            self.url_title_input.clear()
            self.url_input.clear()
        else:
            QMessageBox.critical(self, "Hata", "URL eklenemedi!")
    
    def select_image(self):
        """Görsel seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Görsel Seç",
            "",
            "Görseller (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:
            self.selected_image_paths = [file_path]  # Liste olarak sakla
            
            # Önizleme göster
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview.setPixmap(scaled_pixmap)
            self.image_preview.setStyleSheet("""
                QLabel {
                    background-color: #2a2a2a;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
    
    def select_multiple_images(self):
        """Toplu görsel seç"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Toplu Görsel Seç",
            "",
            "Görseller (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_paths:
            self.selected_image_paths = file_paths
            
            # Önizleme metnini güncelle
            self.image_preview.clear()
            self.image_preview.setText(f"✅ {len(file_paths)} görsel seçildi")
            self.image_preview.setStyleSheet("""
                QLabel {
                    background-color: #2a2a2a;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    padding: 10px;
                    color: #667eea;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
    
    def upload_image_knowledge(self):
        """Görsel bilgisi yükle (tek veya toplu)"""
        if not hasattr(self, 'selected_image_paths') or not self.selected_image_paths:
            QMessageBox.warning(self, "Uyarı", "Önce görsel seçin!")
            return
        
        # Tek veya çoklu görsel kontrolü
        if len(self.selected_image_paths) == 1:
            # Tek görsel yükle
            self._upload_single_image(self.selected_image_paths[0])
        else:
            # Toplu görsel yükle
            self._upload_multiple_images(self.selected_image_paths)
    
    def _upload_single_image(self, file_path):
        """Tek bir görsel yükle ve analiz et"""
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Veritabanına ekle
        knowledge_id = self.db.add_knowledge(
            title=file_name,
            content_type='image',
            file_path=file_path
        )
        
        if knowledge_id:
            # Dosyayı kaydet
            self.db.save_uploaded_file(
                file_name=file_name,
                file_type=file_ext,
                file_size=file_size,
                file_path=file_path,
                knowledge_id=knowledge_id
            )
            
            self.progress_label.setText(f"✅ '{file_name}' yüklendi, analiz ediliyor...")
            
            # Görseli analiz et
            self.start_learning(knowledge_id, 'image', {
                'id': knowledge_id,
                'title': file_name,
                'file_path': file_path
            })
        else:
            QMessageBox.critical(self, "Hata", "Görsel yüklenemedi!")
    
    def _upload_multiple_images(self, file_paths):
        """Toplu görsel yükle ve analiz et"""
        total = len(file_paths)
        
        reply = QMessageBox.question(
            self,
            "Toplu Yükleme",
            f"{total} adet görsel yüklenecek ve analiz edilecek. Devam edilsin mi?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.progress_label.setText(f"📤 {total} görsel yükleniyor...")
        uploaded_count = 0
        
        for idx, file_path in enumerate(file_paths, 1):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Veritabanına ekle
            knowledge_id = self.db.add_knowledge(
                title=file_name,
                content_type='image',
                file_path=file_path
            )
            
            if knowledge_id:
                # Dosyayı kaydet
                self.db.save_uploaded_file(
                    file_name=file_name,
                    file_type=file_ext,
                    file_size=file_size,
                    file_path=file_path,
                    knowledge_id=knowledge_id
                )
                uploaded_count += 1
                self.progress_label.setText(f"📤 {idx}/{total} görsel yüklendi...")
        
        self.progress_label.setText(f"✅ {uploaded_count} görsel başarıyla yüklendi! İlk görsel analiz ediliyor...")
        self.load_knowledge_list()
        
        # İlk görseli analiz et (diğerleri sonra öğrenilecek)
        if uploaded_count > 0:
            first_file = file_paths[0]
            first_knowledge = self.db.get_all_knowledge(filter_learned=False)
            if first_knowledge:
                first = first_knowledge[0]
                self.start_learning(first.get('id'), 'image', {
                    'id': first.get('id'),
                    'title': first.get('title'),
                    'file_path': first.get('file_path')
                })
        
        QMessageBox.information(
            self,
            "Başarılı",
            f"{uploaded_count} görsel yüklendi!\n\n"
            f"İlk görsel şimdi analiz ediliyor.\n"
            f"Diğer görselleri '🚀 Tüm Bekleyen Bilgileri Öğren' butonu ile analiz edebilirsiniz."
        )
    
    def start_learning(self, knowledge_id, learning_type, knowledge_data):
        """Öğrenme işlemini başlat"""
        # OpenAI API anahtarı kontrol
        try:
            with open("config.json", "r") as f:
                settings = json.load(f)
                api_key = settings.get('openai_api_key')
                
                if not api_key:
                    QMessageBox.warning(self, "Uyarı", "OpenAI API anahtarı ayarlanmamış!")
                    return
        except:
            QMessageBox.critical(self, "Hata", "Ayarlar dosyası okunamadı!")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Worker thread başlat
        task_map = {
            'text': 'learn_text',
            'pdf': 'learn_pdf',
            'image': 'learn_image',
            'url': 'learn_url'
        }
        
        self.current_worker = KnowledgeLearningWorker(
            knowledge_data,
            task_map.get(learning_type, 'learn_text'),
            api_key
        )
        
        self.current_worker.progress.connect(self.on_learning_progress)
        self.current_worker.finished.connect(self.on_learning_finished)
        self.current_worker.error.connect(self.on_learning_error)
        self.current_worker.start()
    
    def on_learning_progress(self, message):
        """Öğrenme ilerlemesi"""
        self.progress_label.setText(message)
    
    def on_learning_finished(self, result):
        """Öğrenme tamamlandı"""
        self.progress_bar.setVisible(False)
        
        knowledge_id = result.get('id')
        analysis = result.get('analysis', '')
        summary = result.get('summary', '')
        tokens_used = result.get('tokens_used', 0)
        
        # Veritabanını güncelle
        if knowledge_id:
            self.db.update_knowledge_learning(knowledge_id, analysis, summary)
            
            # Oturumu kaydet
            self.db.save_learning_session(
                session_type='single_learning',
                knowledge_ids=[knowledge_id],
                prompt=f"Bilgi ID: {knowledge_id}",
                ai_response=analysis,
                tokens_used=tokens_used
            )
        
        self.progress_label.setText(f"✅ Öğrenme tamamlandı! ({tokens_used} token kullanıldı)")
        
        # Listeyi güncelle
        self.load_knowledge_list()
        
        # Sonucu göster
        if result.get('type') == 'general_analysis':
            self.show_general_analysis(analysis)
    
    def on_learning_error(self, error_message):
        """Öğrenme hatası"""
        self.progress_bar.setVisible(False)
        self.progress_label.setText(f"❌ Hata: {error_message}")
        QMessageBox.critical(self, "Hata", error_message)
    
    def load_knowledge_list(self):
        """Bilgi listesini yükle"""
        self.knowledge_list.clear()
        
        all_knowledge = self.db.get_all_knowledge()
        
        for knowledge in all_knowledge:
            item_text = f"{knowledge.get('title', 'İsimsiz')}\n"
            
            if knowledge.get('is_learned'):
                item_text += f"✅ Öğrenildi - {knowledge.get('ai_summary', '')[:100]}..."
            else:
                item_text += "⏳ Öğrenme bekliyor..."
            
            item_text += f"\n📅 {knowledge.get('created_at', '')}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, knowledge)
            self.knowledge_list.addItem(item)
    
    def filter_knowledge(self, filter_type):
        """Bilgileri filtrele"""
        # Butonları güncelle
        self.filter_all_btn.setChecked(filter_type == 'all')
        self.filter_learned_btn.setChecked(filter_type == 'learned')
        self.filter_pending_btn.setChecked(filter_type == 'pending')
        
        # Listeyi yükle
        self.knowledge_list.clear()
        
        if filter_type == 'all':
            all_knowledge = self.db.get_all_knowledge()
        elif filter_type == 'learned':
            all_knowledge = self.db.get_all_knowledge(filter_learned=True)
        else:  # pending
            all_knowledge = self.db.get_all_knowledge(filter_learned=False)
        
        for knowledge in all_knowledge:
            item_text = f"{knowledge.get('title', 'İsimsiz')}\n"
            
            if knowledge.get('is_learned'):
                item_text += f"✅ {knowledge.get('ai_summary', '')[:100]}..."
            else:
                item_text += "⏳ Öğrenme bekliyor..."
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, knowledge)
            self.knowledge_list.addItem(item)
    
    def search_knowledge(self):
        """Bilgileri ara"""
        search_text = self.search_input.text().strip()
        
        if not search_text:
            self.load_knowledge_list()
            return
        
        self.knowledge_list.clear()
        
        results = self.db.search_knowledge(search_text)
        
        for knowledge in results:
            item_text = f"{knowledge.get('title', 'İsimsiz')}\n"
            
            if knowledge.get('is_learned'):
                item_text += f"✅ {knowledge.get('ai_summary', '')[:100]}..."
            else:
                item_text += "⏳ Öğrenme bekliyor..."
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, knowledge)
            self.knowledge_list.addItem(item)
    
    def view_selected_knowledge(self):
        """Seçili bilgiyi görüntüle"""
        current_item = self.knowledge_list.currentItem()
        if current_item:
            self.view_knowledge_detail(current_item)
    
    def view_knowledge_detail(self, item):
        """Bilgi detayını göster"""
        knowledge = item.data(Qt.UserRole)
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"📚 {knowledge.get('title', 'İsimsiz')}")
        dialog.setMinimumSize(700, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Başlık
        title = QLabel(knowledge.get('title', 'İsimsiz'))
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            padding: 10px;
            background-color: #667eea;
            border-radius: 8px;
        """)
        layout.addWidget(title)
        
        # Detaylar
        info_text = f"""
        <div style='color: white; font-size: 13px; line-height: 1.6;'>
        <p><b>Tip:</b> {knowledge.get('content_type', 'Bilinmiyor')}</p>
        <p><b>Durum:</b> {'✅ Öğrenildi' if knowledge.get('is_learned') else '⏳ Bekliyor'}</p>
        <p><b>Oluşturulma:</b> {knowledge.get('created_at', '')}</p>
        """
        
        if knowledge.get('learned_at'):
            info_text += f"<p><b>Öğrenilme:</b> {knowledge.get('learned_at', '')}</p>"
        
        info_text += "</div>"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("padding: 10px;")
        layout.addWidget(info_label)
        
        # Özet
        if knowledge.get('ai_summary'):
            summary_group = QGroupBox("📝 Özet")
            summary_group.setStyleSheet("""
                QGroupBox {
                    color: white;
                    font-weight: bold;
                    border: 1px solid #3a3a3a;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
            summary_layout = QVBoxLayout()
            
            summary_text = QTextEdit()
            summary_text.setPlainText(knowledge.get('ai_summary', ''))
            summary_text.setReadOnly(True)
            summary_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2a2a2a;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 12px;
                }
            """)
            summary_layout.addWidget(summary_text)
            summary_group.setLayout(summary_layout)
            layout.addWidget(summary_group)
        
        # Detaylı Analiz
        if knowledge.get('ai_analysis'):
            analysis_group = QGroupBox("🧠 Detaylı Analiz")
            analysis_group.setStyleSheet("""
                QGroupBox {
                    color: white;
                    font-weight: bold;
                    border: 1px solid #3a3a3a;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
            """)
            analysis_layout = QVBoxLayout()
            
            analysis_text = QTextEdit()
            analysis_text.setPlainText(knowledge.get('ai_analysis', ''))
            analysis_text.setReadOnly(True)
            analysis_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2a2a2a;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 12px;
                }
            """)
            analysis_layout.addWidget(analysis_text)
            analysis_group.setLayout(analysis_layout)
            layout.addWidget(analysis_group)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def delete_selected_knowledge(self):
        """Seçili bilgiyi sil"""
        current_item = self.knowledge_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek bilgiyi seçin!")
            return
        
        knowledge = current_item.data(Qt.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Silme Onayı",
            f"'{knowledge.get('title', 'İsimsiz')}' bilgisini silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db.delete_knowledge(knowledge.get('id')):
                self.progress_label.setText(f"✅ '{knowledge.get('title', '')}' silindi")
                self.load_knowledge_list()
            else:
                QMessageBox.critical(self, "Hata", "Bilgi silinemedi!")
    
    def learn_all_pending(self):
        """Tüm bekleyen bilgileri öğren"""
        pending_knowledge = self.db.get_all_knowledge(filter_learned=False)
        
        if not pending_knowledge:
            QMessageBox.information(self, "Bilgi", "Öğrenilecek bekleyen bilgi yok!")
            return
        
        reply = QMessageBox.question(
            self,
            "Toplu Öğrenme",
            f"{len(pending_knowledge)} adet bilgi öğrenilecek. Devam edilsin mi?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.progress_label.setText(f"🚀 {len(pending_knowledge)} bilgi öğreniliyor...")
            
            # İlk bilgiyi öğren (Diğerleri sırayla)
            # TODO: Burada queue sistemi kurup tümünü sırayla öğret
            if pending_knowledge:
                first = pending_knowledge[0]
                self.start_learning(
                    first.get('id'),
                    first.get('content_type'),
                    first
                )
    
    def analyze_all_knowledge(self):
        """Tüm öğrenilen bilgileri birleştirerek genel analiz yap"""
        learned_knowledge = self.db.get_all_knowledge(filter_learned=True)
        
        if not learned_knowledge:
            QMessageBox.warning(self, "Uyarı", "Öğrenilmiş bilgi yok!")
            return
        
        try:
            with open("config.json", "r") as f:
                settings = json.load(f)
                api_key = settings.get('openai_api_key')
                
                if not api_key:
                    QMessageBox.warning(self, "Uyarı", "OpenAI API anahtarı ayarlanmamış!")
                    return
        except:
            QMessageBox.critical(self, "Hata", "Ayarlar dosyası okunamadı!")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_label.setText(f"🧠 {len(learned_knowledge)} bilgi analiz ediliyor...")
        
        # Worker başlat
        self.current_worker = KnowledgeLearningWorker(
            {'all_items': learned_knowledge},
            'analyze_all',
            api_key
        )
        
        self.current_worker.progress.connect(self.on_learning_progress)
        self.current_worker.finished.connect(self.on_learning_finished)
        self.current_worker.error.connect(self.on_learning_error)
        self.current_worker.start()
    
    def deep_analyze_all_knowledge(self):
        """Tüm bilgileri birleştirerek detaylı analiz yap"""
        learned_knowledge = self.db.get_all_knowledge(filter_learned=True)
        
        if not learned_knowledge:
            QMessageBox.warning(self, "Uyarı", "Öğrenilmiş bilgi yok!")
            return
        
        if len(learned_knowledge) < 2:
            QMessageBox.information(
                self,
                "Bilgi",
                "Detaylı analiz için en az 2 öğrenilmiş bilgi gereklidir.\n"
                "Lütfen önce daha fazla bilgi ekleyin ve öğretin."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "Detaylı Analiz",
            f"🧠 Tüm öğrenilmiş {len(learned_knowledge)} bilgi birleştirilerek detaylı analiz yapılacak.\n\n"
            f"Bu işlem daha fazla token harcayabilir. Devam edilsin mi?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            with open("config.json", "r") as f:
                settings = json.load(f)
                api_key = settings.get('openai_api_key')
                
                if not api_key:
                    QMessageBox.warning(self, "Uyarı", "OpenAI API anahtarı ayarlanmamış!")
                    return
        except:
            QMessageBox.critical(self, "Hata", "Ayarlar dosyası okunamadı!")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_label.setText(f"🧠 Tüm bilgiler birleştiriliyor ve analiz ediliyor...")
        
        # Worker başlat
        self.current_worker = KnowledgeLearningWorker(
            {'all_items': learned_knowledge},
            'analyze_all',
            api_key
        )
        
        self.current_worker.progress.connect(self.on_learning_progress)
        self.current_worker.finished.connect(self.on_learning_finished)
        self.current_worker.error.connect(self.on_learning_error)
        self.current_worker.start()
    
    def show_general_analysis(self, analysis):
        """Genel analiz sonucunu göster"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🧠 Genel Firma Analizi")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Başlık
        title = QLabel("🧠 Firma Bilgileri Genel Analizi")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            border-radius: 10px;
        """)
        layout.addWidget(title)
        
        # Analiz metni
        analysis_text = QTextEdit()
        analysis_text.setPlainText(analysis)
        analysis_text.setReadOnly(True)
        analysis_text.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                padding: 15px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(analysis_text)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

