#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 AI Sohbet Asistanı - Akıllı B2B Danışmanınız
Tüm sistem verilerini kullanarak stratejik öneriler sunar
"""

import sys
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor, QColor
import openai
from collections import defaultdict


class AIAssistantWorker(QThread):
    """Arka planda AI sohbet işlemlerini yapar"""
    response_ready = Signal(str, dict)  # response_text, metadata
    error = Signal(str)
    thinking = Signal(bool)  # True: düşünüyor, False: bitti
    
    def __init__(self, message, conversation_history, system_context, openai_api_key, model="gpt-4-turbo-preview"):
        super().__init__()
        self.message = message
        self.conversation_history = conversation_history
        self.system_context = system_context
        self.openai_api_key = openai_api_key
        self.model = model
        # Yeni OpenAI API client
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
    
    def run(self):
        try:
            self.thinking.emit(True)
            
            # Sistem promptu oluştur
            system_prompt = self._build_system_prompt()
            
            # Mesaj geçmişini hazırla
            messages = [{"role": "system", "content": system_prompt}]
            
            # Geçmiş konuşmaları ekle (son 10 mesaj)
            for msg in self.conversation_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Yeni mesajı ekle
            messages.append({
                "role": "user",
                "content": self.message
            })
            
            # GPT API çağrısı
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            
            assistant_message = response.choices[0].message.content.strip()
            
            # Metadata
            metadata = {
                'tokens_used': response.usage.total_tokens,
                'model': self.model,
                'timestamp': datetime.now().isoformat(),
                'finish_reason': response.choices[0].finish_reason
            }
            
            self.thinking.emit(False)
            self.response_ready.emit(assistant_message, metadata)
            
        except Exception as e:
            self.thinking.emit(False)
            self.error.emit(f"AI Hatası: {str(e)}")
    
    def _build_system_prompt(self):
        """Sistem promptunu oluştur - tüm bağlamı içerir"""
        
        prompt = f"""Sen, gelişmiş bir B2B satış ve pazarlama asistanısın. Adın "B2B AI Asistan".

🎯 ROLÜN VE YETENEKLERİN:
- Kullanıcının B2B işletmesi için stratejik danışmanlık yaparsın
- Firma verileri, müşteri bilgileri, kampanya geçmişi hakkında detaylı bilgiye sahipsin
- Satış stratejileri, pazarlama önerileri, müşteri analizi yapabilirsin
- Rakip analizi, pazar trendleri hakkında öngörüler sunarsın
- Mail kampanyaları, WhatsApp mesajları için içerik önerileri verebilirsin
- Raporlar, analizler, özetler hazırlayabilirsin

📊 SİSTEM VERİLERİ (Güncel Durum):
{self._format_system_context()}

💡 İLETİŞİM TARZI:
- Profesyonel ama samimi bir dil kullan
- Türkçe konuş, açık ve net ol
- Veri odaklı öneriler sun
- Somut aksiyonlar öner
- Gerektiğinde emoji kullan ama abartma
- Kısa ve öz yanıtlar ver, gerekmedikçe uzatma

🚀 AKSİYON YETKİLERİN:
Kullanıcı isterse şunları yapabilirsin:
- Mail kampanyası taslağı hazırla
- Firma analizi yap
- Strateji raporu oluştur
- Müşteri segmentasyonu öner
- Rakip analizi yap
- Haftalık/aylık rapor hazırla

📝 ÖNEMLİ KURALLAR:
1. Her zaman güncel verilere dayanarak konuş
2. Tahmin yürütüyorsan bunu belirt
3. Kullanıcının sorusuna odaklan
4. Gerekirse detay iste
5. Önerilerin uygulanabilir olsun

Şimdi kullanıcıyla sohbet etmeye hazırsın. Yardımcı ol!"""
        
        return prompt
    
    def _format_system_context(self):
        """Sistem bağlamını formatla"""
        ctx = self.system_context
        
        formatted = f"""
📈 Firma İstatistikleri:
   • Toplam Firma: {ctx.get('total_firms', 0)}
   • Aktif Firma: {ctx.get('active_firms', 0)}
   • Bu Ay Eklenen: {ctx.get('firms_this_month', 0)}
   • Analiz Edilmiş: {ctx.get('analyzed_firms', 0)}

📧 Kampanya İstatistikleri:
   • Toplam Kampanya: {ctx.get('total_campaigns', 0)}
   • Aktif Kampanya: {ctx.get('active_campaigns', 0)}
   • Toplam Mail Gönderimi: {ctx.get('total_emails_sent', 0)}
   • Açılma Oranı: {ctx.get('open_rate', 0)}%
   • Tıklama Oranı: {ctx.get('click_rate', 0)}%

🧠 Öğrenilen Bilgiler:
   • Toplam Bilgi: {ctx.get('total_knowledge', 0)}
   • Öğrenilmiş: {ctx.get('learned_knowledge', 0)}
   • Kategoriler: {', '.join(ctx.get('knowledge_categories', []))}

🎯 Sektör Dağılımı:
{self._format_sectors(ctx.get('sector_distribution', {}))}

📊 Son Aktiviteler:
{self._format_recent_activities(ctx.get('recent_activities', []))}

💼 En İyi Performans Gösteren Firmalar:
{self._format_top_firms(ctx.get('top_firms', []))}
"""
        return formatted
    
    def _format_sectors(self, sectors):
        if not sectors:
            return "   • Veri yok"
        
        lines = []
        for sector, count in list(sectors.items())[:5]:
            lines.append(f"   • {sector}: {count} firma")
        return "\n".join(lines)
    
    def _format_recent_activities(self, activities):
        if not activities:
            return "   • Son aktivite yok"
        
        lines = []
        for activity in activities[:5]:
            lines.append(f"   • {activity.get('date', '')}: {activity.get('description', '')}")
        return "\n".join(lines)
    
    def _format_top_firms(self, firms):
        if not firms:
            return "   • Veri yok"
        
        lines = []
        for firm in firms[:5]:
            lines.append(f"   • {firm.get('name', 'İsimsiz')}: {firm.get('score', 0)} puan")
        return "\n".join(lines)


class AIContextBuilder:
    """AI için sistem bağlamını oluşturur"""
    
    def __init__(self, db):
        self.db = db
    
    def build_context(self) -> Dict:
        """Tüm sistem verilerinden bağlam oluştur"""
        
        context = {
            # Firma istatistikleri
            'total_firms': self._get_total_firms(),
            'active_firms': self._get_active_firms(),
            'firms_this_month': self._get_firms_this_month(),
            'analyzed_firms': self._get_analyzed_firms(),
            
            # Kampanya istatistikleri
            'total_campaigns': self._get_total_campaigns(),
            'active_campaigns': self._get_active_campaigns(),
            'total_emails_sent': self._get_total_emails_sent(),
            'open_rate': self._get_open_rate(),
            'click_rate': self._get_click_rate(),
            
            # Bilgi öğrenim
            'total_knowledge': self._get_total_knowledge(),
            'learned_knowledge': self._get_learned_knowledge(),
            'knowledge_categories': self._get_knowledge_categories(),
            
            # Sektör analizi
            'sector_distribution': self._get_sector_distribution(),
            
            # Son aktiviteler
            'recent_activities': self._get_recent_activities(),
            
            # En iyi firmalar
            'top_firms': self._get_top_firms(),
            
            # Sistem durumu
            'system_health': self._get_system_health()
        }
        
        return context
    
    def _get_total_firms(self):
        try:
            return len(self.db.get_all_firms())
        except:
            return 0
    
    def _get_active_firms(self):
        try:
            firms = self.db.get_all_firms()
            return len([f for f in firms if f.get('status') == 'active'])
        except:
            return 0
    
    def _get_firms_this_month(self):
        try:
            firms = self.db.get_all_firms()
            this_month = datetime.now().replace(day=1)
            count = 0
            for firm in firms:
                created = firm.get('created_at', '')
                if created:
                    try:
                        created_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        if created_date >= this_month:
                            count += 1
                    except:
                        pass
            return count
        except:
            return 0
    
    def _get_analyzed_firms(self):
        try:
            firms = self.db.get_all_firms()
            return len([f for f in firms if f.get('is_analyzed')])
        except:
            return 0
    
    def _get_total_campaigns(self):
        try:
            return len(self.db.get_all_campaigns())
        except:
            return 0
    
    def _get_active_campaigns(self):
        try:
            campaigns = self.db.get_all_campaigns()
            return len([c for c in campaigns if c.get('status') == 'active'])
        except:
            return 0
    
    def _get_total_emails_sent(self):
        try:
            stats = self.db.get_email_stats()
            return stats.get('total_sent', 0)
        except:
            return 0
    
    def _get_open_rate(self):
        try:
            stats = self.db.get_email_stats()
            total = stats.get('total_sent', 0)
            opened = stats.get('total_opened', 0)
            if total > 0:
                return round((opened / total) * 100, 1)
            return 0
        except:
            return 0
    
    def _get_click_rate(self):
        try:
            stats = self.db.get_email_stats()
            total = stats.get('total_sent', 0)
            clicked = stats.get('total_clicked', 0)
            if total > 0:
                return round((clicked / total) * 100, 1)
            return 0
        except:
            return 0
    
    def _get_total_knowledge(self):
        try:
            return len(self.db.get_all_knowledge())
        except:
            return 0
    
    def _get_learned_knowledge(self):
        try:
            knowledge = self.db.get_all_knowledge()
            return len([k for k in knowledge if k.get('is_learned')])
        except:
            return 0
    
    def _get_knowledge_categories(self):
        try:
            knowledge = self.db.get_all_knowledge()
            categories = set()
            for k in knowledge:
                cat = k.get('content_type', '')
                if cat:
                    categories.add(cat)
            return list(categories)
        except:
            return []
    
    def _get_sector_distribution(self):
        try:
            firms = self.db.get_all_firms()
            sectors = defaultdict(int)
            for firm in firms:
                sector = firm.get('sector', 'Belirtilmemiş')
                if sector:
                    sectors[sector] += 1
            return dict(sorted(sectors.items(), key=lambda x: x[1], reverse=True))
        except:
            return {}
    
    def _get_recent_activities(self):
        try:
            activities = []
            
            # Son eklenen firmalar
            firms = self.db.get_all_firms()
            recent_firms = sorted(firms, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
            for firm in recent_firms:
                activities.append({
                    'date': firm.get('created_at', '')[:10],
                    'description': f"Yeni firma eklendi: {firm.get('name', 'İsimsiz')}"
                })
            
            # Son kampanyalar
            campaigns = self.db.get_all_campaigns()
            recent_campaigns = sorted(campaigns, key=lambda x: x.get('created_at', ''), reverse=True)[:2]
            for campaign in recent_campaigns:
                activities.append({
                    'date': campaign.get('created_at', '')[:10],
                    'description': f"Kampanya oluşturuldu: {campaign.get('name', 'İsimsiz')}"
                })
            
            return sorted(activities, key=lambda x: x['date'], reverse=True)[:5]
        except:
            return []
    
    def _get_top_firms(self):
        try:
            firms = self.db.get_all_firms()
            
            # Basit skorlama sistemi
            scored_firms = []
            for firm in firms:
                score = 0
                
                # Analiz edilmişse +30
                if firm.get('is_analyzed'):
                    score += 30
                
                # Email varsa +20
                if firm.get('email'):
                    score += 20
                
                # Telefon varsa +15
                if firm.get('phone'):
                    score += 15
                
                # Website varsa +15
                if firm.get('website'):
                    score += 15
                
                # Rating varsa +20
                if firm.get('rating'):
                    score += 20
                
                scored_firms.append({
                    'name': firm.get('name', 'İsimsiz'),
                    'score': score,
                    'sector': firm.get('sector', '')
                })
            
            return sorted(scored_firms, key=lambda x: x['score'], reverse=True)[:10]
        except:
            return []
    
    def _get_system_health(self):
        """Sistem sağlığı kontrolü"""
        try:
            health = {
                'database': 'healthy',
                'api_keys': 'configured',
                'last_update': datetime.now().isoformat()
            }
            return health
        except:
            return {'status': 'unknown'}


class AIChatAssistantTab(QWidget):
    """🤖 AI Sohbet Asistanı Sekmesi"""
    
    def __init__(self, db, api_manager):
        super().__init__()
        self.db = db
        self.api_manager = api_manager
        self.conversation_history = []
        self.current_worker = None
        self.context_builder = AIContextBuilder(db)
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_context)
        self.auto_refresh_timer.start(60000)  # Her 1 dakikada bir güncelle
        
        self.init_ui()
        self.load_conversation_history()
        self.show_welcome_message()
    
    def init_ui(self):
        """Arayüzü oluştur"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Başlık
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Ana içerik - Split layout
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Sol panel - Sohbet alanı
        chat_panel = self.create_chat_panel()
        content_splitter.addWidget(chat_panel)
        
        # Sağ panel - Bağlam ve hızlı aksiyonlar
        side_panel = self.create_side_panel()
        content_splitter.addWidget(side_panel)
        
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(content_splitter)
        
        # Alt panel - Mesaj giriş
        input_panel = self.create_input_panel()
        main_layout.addWidget(input_panel)
        
        self.apply_modern_theme()
    
    def create_header(self):
        """Başlık paneli"""
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        # Başlık
        title_layout = QVBoxLayout()
        
        title = QLabel("🤖 AI Sohbet Asistanı")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Akıllı B2B danışmanınız - Stratejiler, analizler ve öneriler için benimle konuş!")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 5px;
        """)
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Durum göstergeleri
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("🟢 Çevrimiçi")
        self.status_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
        """)
        status_layout.addWidget(self.status_label)
        
        self.model_label = QLabel("Model: GPT-4 Turbo")
        self.model_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 11px;
            margin-top: 5px;
        """)
        status_layout.addWidget(self.model_label)
        
        layout.addLayout(status_layout)
        
        return header
    
    def create_chat_panel(self):
        """Sohbet paneli"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Sohbet geçmişi
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #0d0d0d;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Alt kontroller
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("🗑️ Temizle")
        clear_btn.setStyleSheet(self._button_style())
        clear_btn.clicked.connect(self.clear_conversation)
        controls_layout.addWidget(clear_btn)
        
        export_btn = QPushButton("💾 Dışa Aktar")
        export_btn.setStyleSheet(self._button_style())
        export_btn.clicked.connect(self.export_conversation)
        controls_layout.addWidget(export_btn)
        
        controls_layout.addStretch()
        
        self.token_label = QLabel("Token: 0")
        self.token_label.setStyleSheet("color: #999; font-size: 12px;")
        controls_layout.addWidget(self.token_label)
        
        layout.addLayout(controls_layout)
        
        return panel
    
    def create_side_panel(self):
        """Yan panel - Bağlam ve aksiyonlar"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Başlık
        title = QLabel("⚡ Hızlı Aksiyonlar")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Hızlı aksiyon butonları
        actions = [
            ("📊 Genel Durum Raporu", self.quick_status_report),
            ("🎯 Strateji Önerisi", self.quick_strategy),
            ("📧 Kampanya Taslağı", self.quick_campaign_draft),
            ("🔍 Firma Analizi", self.quick_firm_analysis),
            ("📈 Performans Özeti", self.quick_performance),
            ("💡 İyileştirme Önerileri", self.quick_improvements),
            ("🎨 İçerik Fikirleri", self.quick_content_ideas),
            ("🏆 En İyi Firmalar", self.quick_top_firms),
        ]
        
        for text, callback in actions:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2a2a2a;
                    color: white;
                    padding: 12px;
                    border-radius: 8px;
                    border: 1px solid #3a3a3a;
                    text-align: left;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #667eea;
                    border: 1px solid #667eea;
                }
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Bağlam bilgisi
        context_group = QGroupBox("📊 Sistem Durumu")
        context_group.setStyleSheet("""
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        context_layout = QVBoxLayout()
        
        self.context_label = QLabel("Yükleniyor...")
        self.context_label.setStyleSheet("""
            color: #999;
            font-size: 11px;
            padding: 10px;
        """)
        self.context_label.setWordWrap(True)
        context_layout.addWidget(self.context_label)
        
        refresh_context_btn = QPushButton("🔄 Yenile")
        refresh_context_btn.setStyleSheet(self._button_style())
        refresh_context_btn.clicked.connect(self.refresh_context)
        context_layout.addWidget(refresh_context_btn)
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
        return panel
    
    def create_input_panel(self):
        """Mesaj giriş paneli"""
        panel = QWidget()
        panel.setMaximumHeight(150)
        panel.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Düşünme göstergesi
        self.thinking_label = QLabel("🤔 AI düşünüyor...")
        self.thinking_label.setStyleSheet("""
            color: #667eea;
            font-size: 13px;
            font-weight: bold;
            padding: 5px;
        """)
        self.thinking_label.setVisible(False)
        layout.addWidget(self.thinking_label)
        
        # Mesaj giriş alanı
        input_layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Mesajınızı yazın... (Örn: 'Bu ayki kampanya performansımı analiz et' veya 'Yeni bir mail kampanyası için öneri ver')")
        self.message_input.setMaximumHeight(80)
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        input_layout.addWidget(self.message_input)
        
        # Gönder butonu
        send_btn = QPushButton("📤\nGönder")
        send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 15px 25px;
                border-radius: 10px;
                border: none;
                min-width: 100px;
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
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        # Kısayollar
        shortcuts_label = QLabel("💡 İpucu: Enter ile yeni satır, Ctrl+Enter ile gönder")
        shortcuts_label.setStyleSheet("""
            color: #666;
            font-size: 11px;
            margin-top: 5px;
        """)
        layout.addWidget(shortcuts_label)
        
        # Klavye kısayolu
        self.message_input.installEventFilter(self)
        
        return panel
    
    def eventFilter(self, obj, event):
        """Klavye kısayolları"""
        if obj == self.message_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def apply_modern_theme(self):
        """Modern tema"""
        self.setStyleSheet("""
            QWidget {
                background-color: #0d0d0d;
                color: white;
                font-family: 'Segoe UI', Arial;
            }
        """)
    
    def _button_style(self):
        """Buton stili"""
        return """
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                padding: 8px 15px;
                border-radius: 8px;
                border: 1px solid #4a4a4a;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """
    
    # ==================== Fonksiyonlar ====================
    
    def show_welcome_message(self):
        """Hoş geldin mesajı"""
        welcome = """
<div style='background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2); 
     padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
    <h2 style='color: white; margin: 0;'>🤖 Merhaba! Ben B2B AI Asistanınız</h2>
    <p style='color: rgba(255,255,255,0.9); margin-top: 10px; font-size: 14px;'>
        Size yardımcı olmak için buradayım! Şunları yapabilirim:
    </p>
    <ul style='color: rgba(255,255,255,0.9); font-size: 13px;'>
        <li>📊 Firma ve kampanya analizleri</li>
        <li>🎯 Strateji ve pazarlama önerileri</li>
        <li>📧 Mail ve içerik taslakları</li>
        <li>📈 Performans raporları ve özetler</li>
        <li>💡 İyileştirme ve optimizasyon fikirleri</li>
    </ul>
    <p style='color: rgba(255,255,255,0.9); margin-top: 15px; font-size: 13px;'>
        <b>Nasıl yardımcı olabilirim?</b> Sağ taraftaki hızlı aksiyonları kullanabilir 
        veya aşağıdan doğrudan soru sorabilirsiniz!
    </p>
</div>
"""
        self.chat_display.append(welcome)
        self.refresh_context()
    
    def send_message(self):
        """Mesaj gönder"""
        message = self.message_input.toPlainText().strip()
        
        if not message:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir mesaj yazın!")
            return
        
        # API key kontrol
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
        
        # Kullanıcı mesajını göster
        self.add_user_message(message)
        
        # Mesajı geçmişe ekle
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Input'u temizle
        self.message_input.clear()
        
        # AI'ya gönder
        self.thinking_label.setVisible(True)
        self.status_label.setText("🟡 Düşünüyor...")
        
        # Bağlamı hazırla
        context = self.context_builder.build_context()
        
        # Worker başlat
        self.current_worker = AIAssistantWorker(
            message=message,
            conversation_history=self.conversation_history,
            system_context=context,
            openai_api_key=api_key,
            model="gpt-4-turbo-preview"
        )
        
        self.current_worker.response_ready.connect(self.on_response_ready)
        self.current_worker.error.connect(self.on_error)
        self.current_worker.thinking.connect(self.on_thinking)
        self.current_worker.start()
    
    def on_response_ready(self, response, metadata):
        """AI yanıtı hazır"""
        # AI mesajını göster
        self.add_ai_message(response)
        
        # Geçmişe ekle
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        })
        
        # Token bilgisini güncelle
        total_tokens = sum([
            msg.get('metadata', {}).get('tokens_used', 0) 
            for msg in self.conversation_history 
            if msg.get('role') == 'assistant'
        ])
        self.token_label.setText(f"Token: {total_tokens}")
        
        # Konuşmayı kaydet
        self.save_conversation_history()
        
        self.status_label.setText("🟢 Çevrimiçi")
    
    def on_error(self, error_message):
        """Hata oluştu"""
        self.add_system_message(f"❌ Hata: {error_message}")
        self.status_label.setText("🔴 Hata")
    
    def on_thinking(self, is_thinking):
        """Düşünme durumu"""
        self.thinking_label.setVisible(is_thinking)
        if not is_thinking:
            self.status_label.setText("🟢 Çevrimiçi")
    
    def add_user_message(self, message):
        """Kullanıcı mesajı ekle"""
        timestamp = datetime.now().strftime("%H:%M")
        html = f"""
<div style='margin: 15px 0; text-align: right;'>
    <div style='display: inline-block; max-width: 70%; background-color: #667eea; 
         color: white; padding: 12px 18px; border-radius: 18px 18px 4px 18px; 
         text-align: left; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'>
        <div style='font-size: 13px; margin-bottom: 5px;'>
            <b>👤 Siz</b> <span style='opacity: 0.7; font-size: 11px;'>{timestamp}</span>
        </div>
        <div style='font-size: 14px; line-height: 1.5;'>{message}</div>
    </div>
</div>
"""
        self.chat_display.append(html)
        self.chat_display.moveCursor(QTextCursor.End)
    
    def add_ai_message(self, message):
        """AI mesajı ekle"""
        timestamp = datetime.now().strftime("%H:%M")
        
        # Markdown-style formatting
        message = message.replace('\n', '<br>')
        
        html = f"""
<div style='margin: 15px 0;'>
    <div style='display: inline-block; max-width: 70%; background-color: #2a2a2a; 
         color: white; padding: 12px 18px; border-radius: 18px 18px 18px 4px; 
         border-left: 4px solid #764ba2; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'>
        <div style='font-size: 13px; margin-bottom: 5px;'>
            <b>🤖 AI Asistan</b> <span style='opacity: 0.7; font-size: 11px;'>{timestamp}</span>
        </div>
        <div style='font-size: 14px; line-height: 1.6;'>{message}</div>
    </div>
</div>
"""
        self.chat_display.append(html)
        self.chat_display.moveCursor(QTextCursor.End)
    
    def add_system_message(self, message):
        """Sistem mesajı ekle"""
        html = f"""
<div style='margin: 10px 0; text-align: center;'>
    <div style='display: inline-block; background-color: rgba(255,255,255,0.1); 
         color: #999; padding: 8px 15px; border-radius: 15px; font-size: 12px;'>
        {message}
    </div>
</div>
"""
        self.chat_display.append(html)
        self.chat_display.moveCursor(QTextCursor.End)
    
    def refresh_context(self):
        """Bağlamı yenile"""
        context = self.context_builder.build_context()
        
        context_text = f"""
<b>Firmalar:</b> {context['total_firms']} (Aktif: {context['active_firms']})
<b>Kampanyalar:</b> {context['total_campaigns']} (Aktif: {context['active_campaigns']})
<b>Bilgi Bankası:</b> {context['learned_knowledge']}/{context['total_knowledge']} öğrenildi
<b>Email İstatistikleri:</b>
  • Gönderim: {context['total_emails_sent']}
  • Açılma: %{context['open_rate']}
  • Tıklama: %{context['click_rate']}
"""
        self.context_label.setText(context_text)
    
    def clear_conversation(self):
        """Konuşmayı temizle"""
        reply = QMessageBox.question(
            self,
            "Konuşmayı Temizle",
            "Tüm konuşma geçmişi silinecek. Emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.conversation_history = []
            self.chat_display.clear()
            self.show_welcome_message()
            self.token_label.setText("Token: 0")
            self.save_conversation_history()
            self.add_system_message("💬 Konuşma geçmişi temizlendi")
    
    def export_conversation(self):
        """Konuşmayı dışa aktar"""
        if not self.conversation_history:
            QMessageBox.information(self, "Bilgi", "Henüz konuşma geçmişi yok!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Konuşmayı Kaydet",
            f"ai_konusma_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("🤖 AI Sohbet Asistanı - Konuşma Geçmişi\n")
                        f.write("=" * 60 + "\n\n")
                        
                        for msg in self.conversation_history:
                            role = "👤 Siz" if msg['role'] == 'user' else "🤖 AI"
                            timestamp = msg.get('timestamp', '')[:19]
                            content = msg['content']
                            
                            f.write(f"{role} ({timestamp}):\n")
                            f.write(f"{content}\n")
                            f.write("-" * 60 + "\n\n")
                
                QMessageBox.information(self, "Başarılı", f"Konuşma kaydedildi:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kayıt hatası: {str(e)}")
    
    def save_conversation_history(self):
        """Konuşma geçmişini kaydet"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/ai_chat_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Konuşma kayıt hatası: {e}")
    
    def load_conversation_history(self):
        """Konuşma geçmişini yükle"""
        try:
            if os.path.exists('data/ai_chat_history.json'):
                with open('data/ai_chat_history.json', 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                
                # Son 20 mesajı göster
                for msg in self.conversation_history[-20:]:
                    if msg['role'] == 'user':
                        self.add_user_message(msg['content'])
                    elif msg['role'] == 'assistant':
                        self.add_ai_message(msg['content'])
        except Exception as e:
            print(f"Konuşma yükleme hatası: {e}")
    
    # ==================== Hızlı Aksiyonlar ====================
    
    def quick_status_report(self):
        """Genel durum raporu iste"""
        self.message_input.setPlainText("Sistemimin genel durumu hakkında detaylı bir rapor hazırlar mısın? Firma sayıları, kampanya performansları, güçlü ve zayıf yönler neler?")
        self.send_message()
    
    def quick_strategy(self):
        """Strateji önerisi iste"""
        self.message_input.setPlainText("Mevcut verilerime bakarak önümüzdeki ay için bir satış ve pazarlama stratejisi öner. Hangi firmalara odaklanmalıyım?")
        self.send_message()
    
    def quick_campaign_draft(self):
        """Kampanya taslağı iste"""
        self.message_input.setPlainText("Yeni bir email kampanyası hazırlamak istiyorum. Mevcut firmalarım için etkili bir kampanya taslağı ve konu başlığı önerir misin?")
        self.send_message()
    
    def quick_firm_analysis(self):
        """Firma analizi iste"""
        self.message_input.setPlainText("En yüksek potansiyele sahip 5 firmamı analiz et ve her biri için özel yaklaşım stratejisi öner.")
        self.send_message()
    
    def quick_performance(self):
        """Performans özeti iste"""
        self.message_input.setPlainText("Son kampanyalarımın performans özetini çıkar. Açılma ve tıklama oranlarını değerlendir, iyileştirme önerileri sun.")
        self.send_message()
    
    def quick_improvements(self):
        """İyileştirme önerileri iste"""
        self.message_input.setPlainText("Sistemimi daha verimli kullanmak için neler yapabilirim? Eksik olan veya geliştirilmesi gereken alanlar neler?")
        self.send_message()
    
    def quick_content_ideas(self):
        """İçerik fikirleri iste"""
        self.message_input.setPlainText("Firmalarıma göndermek için 5 farklı email içerik fikri öner. Her biri için konu başlığı ve ana mesaj nedir?")
        self.send_message()
    
    def quick_top_firms(self):
        """En iyi firmalar analizi"""
        self.message_input.setPlainText("En iyi performans gösteren ve en yüksek potansiyele sahip firmalarımı listele. Her biri için neden öne çıktığını açıkla.")
        self.send_message()


# Test
if __name__ == "__main__":
    print("🤖 AI Chat Assistant Module")
    print("Bu modül main.py içinde kullanılacak")

