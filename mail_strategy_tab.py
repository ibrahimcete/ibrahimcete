"""
Mail Takip Stratejisi Yönetim Sekmesi - PySide6 Version
AI destekli ve manuel mail stratejisi yönetimi için GUI
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QTextEdit, QSlider, QCheckBox,
    QComboBox, QFrame, QScrollArea, QMessageBox, QGroupBox,
    QRadioButton, QButtonGroup, QTabWidget, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import threading
import json
from datetime import datetime
from typing import Optional, Dict
from ai_mail_strategy import AIMailStrategy


class AIAnalysisThread(QThread):
    """AI analizi için thread"""
    finished = Signal(dict)
    
    def __init__(self, strategy_manager, company_name):
        super().__init__()
        self.strategy_manager = strategy_manager
        self.company_name = company_name
    
    def run(self):
        result = self.strategy_manager.analyze_with_ai(self.company_name)
        self.finished.emit(result)


class MailStrategyTab(QWidget):
    """Mail takip stratejisi yönetim sekmesi - PySide6"""
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        
        self.strategy_manager = AIMailStrategy()
        self.current_company = None
        self.current_ai_strategy = None
        self.ai_thread = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Arayüzü oluştur"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Sol panel - Firma seçimi ve kontroller
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Sağ panel - Strateji detayları
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel, 3)
        
    def _create_left_panel(self):
        """Sol panel oluştur"""
        panel = QFrame()
        panel.setMaximumWidth(350)
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Başlık
        title = QLabel("🎯 Mail Stratejisi Yöneticisi")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Firma seçimi
        firma_group = QGroupBox("Firma Seçimi")
        firma_layout = QVBoxLayout()
        
        # Arama
        search_layout = QHBoxLayout()
        self.company_search = QLineEdit()
        self.company_search.setPlaceholderText("🔍 Firma ara...")
        search_layout.addWidget(self.company_search)
        
        search_btn = QPushButton("Ara")
        search_btn.clicked.connect(self._search_companies)
        search_layout.addWidget(search_btn)
        firma_layout.addLayout(search_layout)
        
        # Firma listesi
        self.companies_list = QListWidget()
        self.companies_list.setMaximumHeight(150)
        self.companies_list.itemClicked.connect(self._on_company_select)
        firma_layout.addWidget(self.companies_list)
        
        # Seçili firma
        self.selected_label = QLabel("Seçili: Firma seçilmedi")
        self.selected_label.setStyleSheet("color: gray;")
        firma_layout.addWidget(self.selected_label)
        
        # Firmaları yükle
        load_btn = QPushButton("📂 Firmaları Yükle")
        load_btn.clicked.connect(self._load_companies)
        firma_layout.addWidget(load_btn)
        
        firma_group.setLayout(firma_layout)
        layout.addWidget(firma_group)
        
        # Strateji Modu
        mode_group = QGroupBox("Strateji Modu")
        mode_layout = QVBoxLayout()
        
        self.mode_button_group = QButtonGroup()
        
        self.ai_radio = QRadioButton("🤖 AI Destekli (Önerilen)")
        self.ai_radio.setChecked(True)
        self.ai_radio.toggled.connect(self._on_mode_change)
        self.mode_button_group.addButton(self.ai_radio)
        mode_layout.addWidget(self.ai_radio)
        
        self.manual_radio = QRadioButton("✍️ Manuel Kontrol")
        self.manual_radio.toggled.connect(self._on_mode_change)
        self.mode_button_group.addButton(self.manual_radio)
        mode_layout.addWidget(self.manual_radio)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # İstatistikler
        stats_group = QGroupBox("Firma İstatistikleri")
        stats_layout = QVBoxLayout()
        
        self.stat_total = QLabel("Toplam Mail: 0")
        self.stat_open = QLabel("Açılma Oranı: 0%")
        self.stat_reply = QLabel("Yanıt Oranı: 0%")
        self.stat_engagement = QLabel("Etkileşim: 0/100")
        
        for stat in [self.stat_total, self.stat_open, self.stat_reply, self.stat_engagement]:
            stat.setStyleSheet("padding: 5px; background-color: #2b2b2b; border-radius: 3px;")
            stats_layout.addWidget(stat)
        
        self.last_update = QLabel("Son güncelleme: -")
        self.last_update.setStyleSheet("color: gray; font-size: 9pt;")
        stats_layout.addWidget(self.last_update)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Yardım butonu
        help_btn = QPushButton("ℹ️ Yardım")
        help_btn.clicked.connect(self._show_help)
        layout.addWidget(help_btn)
        
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self):
        """Sağ panel oluştur"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # AI Önerileri sekmesi
        self.ai_tab = self._create_ai_tab()
        self.tab_widget.addTab(self.ai_tab, "🤖 AI Önerileri")
        
        # Manuel Strateji sekmesi
        self.manual_tab = self._create_manual_tab()
        self.tab_widget.addTab(self.manual_tab, "✍️ Manuel Strateji")
        
        # Performans sekmesi
        self.performance_tab = self._create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "📊 Performans")
        
        # Geçmiş sekmesi
        self.history_tab = self._create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📜 Geçmiş")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def _create_ai_tab(self):
        """AI önerileri sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Kontrol butonları
        controls = QHBoxLayout()
        
        self.ai_analyze_btn = QPushButton("🤖 AI Analizi Yap")
        self.ai_analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #1f538d;
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #2d6ba8;
            }
        """)
        self.ai_analyze_btn.clicked.connect(self._run_ai_analysis)
        controls.addWidget(self.ai_analyze_btn)
        
        self.ai_approve_btn = QPushButton("✅ Stratejiyi Onayla")
        self.ai_approve_btn.setEnabled(False)
        self.ai_approve_btn.clicked.connect(self._approve_strategy)
        controls.addWidget(self.ai_approve_btn)
        
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.clicked.connect(self._refresh_ai_data)
        controls.addWidget(refresh_btn)
        
        layout.addLayout(controls)
        
        # Progress bar
        self.ai_progress = QProgressBar()
        self.ai_progress.setVisible(False)
        self.ai_progress.setRange(0, 0)  # Indefinite
        layout.addWidget(self.ai_progress)
        
        # Sonuçlar alanı
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.ai_results_widget = QWidget()
        self.ai_results_layout = QVBoxLayout(self.ai_results_widget)
        
        # Başlangıç mesajı
        welcome = QLabel("👈 Bir firma seçin ve AI analizi yapın")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: gray; font-size: 12pt; padding: 50px;")
        self.ai_results_layout.addWidget(welcome)
        self.ai_results_layout.addStretch()
        
        scroll.setWidget(self.ai_results_widget)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_manual_tab(self):
        """Manuel strateji sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Mail sayısı
        mail_group = QGroupBox("📧 Gönderilecek Mail Sayısı")
        mail_layout = QVBoxLayout()
        
        self.mail_count_slider = QSlider(Qt.Horizontal)
        self.mail_count_slider.setMinimum(1)
        self.mail_count_slider.setMaximum(10)
        self.mail_count_slider.setValue(3)
        self.mail_count_slider.valueChanged.connect(self._update_mail_count_label)
        mail_layout.addWidget(self.mail_count_slider)
        
        self.mail_count_label = QLabel("3 mail")
        self.mail_count_label.setStyleSheet("font-size: 11pt; font-weight: bold;")
        mail_layout.addWidget(self.mail_count_label)
        
        mail_group.setLayout(mail_layout)
        content_layout.addWidget(mail_group)
        
        # Gönderim zamanlaması
        schedule_group = QGroupBox("📅 Gönderim Zamanlaması")
        schedule_layout = QVBoxLayout()
        
        add_layout = QHBoxLayout()
        
        self.schedule_day = QComboBox()
        self.schedule_day.addItems(["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        add_layout.addWidget(self.schedule_day)
        
        self.schedule_time = QLineEdit()
        self.schedule_time.setPlaceholderText("09:00")
        self.schedule_time.setMaximumWidth(80)
        add_layout.addWidget(self.schedule_time)
        
        add_btn = QPushButton("➕ Ekle")
        add_btn.clicked.connect(self._add_schedule)
        add_layout.addWidget(add_btn)
        
        schedule_layout.addLayout(add_layout)
        
        self.schedule_list = QListWidget()
        self.schedule_list.setMaximumHeight(100)
        schedule_layout.addWidget(self.schedule_list)
        
        remove_btn = QPushButton("🗑️ Seçili Zamanlamayı Sil")
        remove_btn.setStyleSheet("background-color: #8B0000; color: white;")
        remove_btn.clicked.connect(self._remove_schedule)
        schedule_layout.addWidget(remove_btn)
        
        schedule_group.setLayout(schedule_layout)
        content_layout.addWidget(schedule_group)
        
        # İçerik türleri
        content_group = QGroupBox("📝 Mail İçerik Türleri")
        content_types_layout = QVBoxLayout()
        
        self.content_checkboxes = {}
        content_types = [
            "Bilgilendirme",
            "Hatırlatma",
            "Kampanya/Promosyon",
            "Kişiselleştirilmiş Teklif",
            "Ürün Tanıtımı",
            "Etkinlik Daveti"
        ]
        
        for content_type in content_types:
            cb = QCheckBox(content_type)
            self.content_checkboxes[content_type] = cb
            content_types_layout.addWidget(cb)
        
        content_group.setLayout(content_types_layout)
        content_layout.addWidget(content_group)
        
        # Notlar
        notes_group = QGroupBox("📋 Notlar")
        notes_layout = QVBoxLayout()
        
        self.manual_notes = QTextEdit()
        self.manual_notes.setMaximumHeight(80)
        self.manual_notes.setPlaceholderText("Strateji ile ilgili notlarınız...")
        notes_layout.addWidget(self.manual_notes)
        
        notes_group.setLayout(notes_layout)
        content_layout.addWidget(notes_group)
        
        # Kaydet butonu
        save_btn = QPushButton("💾 Manuel Stratejiyi Kaydet")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d6a2e;
                color: white;
                padding: 12px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #3d7a3e;
            }
        """)
        save_btn.clicked.connect(self._save_manual_strategy)
        content_layout.addWidget(save_btn)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_performance_tab(self):
        """Performans sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.performance_widget = QWidget()
        self.performance_layout = QVBoxLayout(self.performance_widget)
        
        welcome = QLabel("📊 Performans verileri firma seçildikten sonra gösterilecek")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: gray; font-size: 12pt; padding: 50px;")
        self.performance_layout.addWidget(welcome)
        self.performance_layout.addStretch()
        
        scroll.setWidget(self.performance_widget)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_history_tab(self):
        """Geçmiş sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        
        welcome = QLabel("📜 Mail geçmişi firma seçildikten sonra gösterilecek")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: gray; font-size: 12pt; padding: 50px;")
        self.history_layout.addWidget(welcome)
        self.history_layout.addStretch()
        
        scroll.setWidget(self.history_widget)
        layout.addWidget(scroll)
        
        return tab
    
    # Event handlers
    
    def _load_companies(self):
        """Firmaları yükle - Veritabanından gerçek firmalar"""
        import sqlite3
        import os
        
        try:
            # database.py dosyasından database path'i al
            db_path = None
            if hasattr(self, 'parent') and self.parent:
                # Main window'dan database'i al
                if hasattr(self.parent, 'db') and self.parent.db:
                    # Database sınıfından path al
                    if hasattr(self.parent.db, 'db_path'):
                        db_path = self.parent.db.db_path
                    elif hasattr(self.parent.db, 'path'):
                        db_path = self.parent.db.path
            
            # Path bulunamadıysa varsayılan db path'i dene
            if not db_path or not os.path.exists(db_path):
                possible_paths = ['ai_center.db', 'b2b_automation.db', 'tracking.db']
                for path in possible_paths:
                    if os.path.exists(path):
                        db_path = path
                        break
            
            if not db_path or not os.path.exists(db_path):
                QMessageBox.warning(
                    self, 
                    "Uyarı", 
                    "Veritabanı bulunamadı!\n\n"
                    "Lütfen önce programı çalıştırın."
                )
                return
            
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # firms tablosundan direkt çek
            try:
                cursor.execute('''
                    SELECT DISTINCT name FROM firms 
                    WHERE name IS NOT NULL AND name != ''
                    ORDER BY name
                ''')
                companies = [row[0] for row in cursor.fetchall()]
            except Exception as e:
                print(f"Firms tablosundan okuma hatası: {e}")
                companies = []
            
            # Eğer firms tablosu boşsa, diğer tablolardan da dene
            if not companies:
                companies_set = set()
                
                # 1. contacts tablosundan
                try:
                    cursor.execute('''
                        SELECT DISTINCT company FROM contacts 
                        WHERE company IS NOT NULL AND company != ''
                    ''')
                    companies_set.update([row[0] for row in cursor.fetchall()])
                except:
                    pass
                
                # 2. Mail geçmişinden
                try:
                    cursor.execute('''
                        SELECT DISTINCT company_name FROM company_mail_history
                        WHERE company_name IS NOT NULL AND company_name != ''
                    ''')
                    companies_set.update([row[0] for row in cursor.fetchall()])
                except:
                    pass
                
                companies = sorted(list(companies_set))
            
            conn.close()
            
            if not companies:
                QMessageBox.warning(
                    self, 
                    "Uyarı", 
                    "Veritabanında firma bulunamadı!\n\n"
                    "Lütfen önce firma ekleyin."
                )
                return
            
            self.companies_list.clear()
            self.companies_list.addItems(companies)
            
            QMessageBox.information(
                self, 
                "✅ Başarılı", 
                f"{len(companies)} firma veritabanından yüklendi!"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Hata", f"Firmalar yüklenirken hata:\n{e}")
            print(f"Firma yükleme hatası: {e}")
    
    def _search_companies(self):
        """Firma ara"""
        search_term = self.company_search.text().lower()
        
        for i in range(self.companies_list.count()):
            item = self.companies_list.item(i)
            if search_term in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def _on_company_select(self, item):
        """Firma seçildiğinde"""
        self.current_company = item.text()
        self.selected_label.setText(f"Seçili: {self.current_company}")
        self.selected_label.setStyleSheet("color: white; font-weight: bold;")
        self._load_company_data()
    
    def _load_company_data(self):
        """Firma verilerini yükle"""
        if not self.current_company:
            return
        
        history = self.strategy_manager.get_company_history(self.current_company)
        
        self.stat_total.setText(f"Toplam Mail: {history['total_mails']}")
        self.stat_open.setText(f"Açılma Oranı: {history['open_rate']}%")
        self.stat_reply.setText(f"Yanıt Oranı: {history['reply_rate']}%")
        self.stat_engagement.setText(f"Etkileşim: {history['avg_engagement']}/100")
        
        self.last_update.setText(f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}")
        
        self._update_performance_tab()
        self._update_history_tab()
    
    def _on_mode_change(self):
        """Mod değiştiğinde"""
        if self.ai_radio.isChecked():
            self.tab_widget.setCurrentIndex(0)  # AI tab
        else:
            self.tab_widget.setCurrentIndex(1)  # Manuel tab
    
    def _run_ai_analysis(self):
        """AI analizi çalıştır"""
        if not self.current_company:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir firma seçin!")
            return
        
        # Önceki sonuçları temizle
        self._clear_layout(self.ai_results_layout)
        
        # Loading göster
        loading = QLabel("🤖 AI analizi yapılıyor...\nLütfen bekleyin...")
        loading.setAlignment(Qt.AlignCenter)
        loading.setStyleSheet("color: orange; font-size: 13pt; padding: 50px;")
        self.ai_results_layout.addWidget(loading)
        
        self.ai_progress.setVisible(True)
        self.ai_analyze_btn.setEnabled(False)
        
        # Thread'de AI analizi yap
        self.ai_thread = AIAnalysisThread(self.strategy_manager, self.current_company)
        self.ai_thread.finished.connect(self._show_ai_results)
        self.ai_thread.start()
    
    def _show_ai_results(self, result: Dict):
        """AI sonuçlarını göster"""
        self.ai_progress.setVisible(False)
        self.ai_analyze_btn.setEnabled(True)
        
        # Önceki içeriği temizle
        self._clear_layout(self.ai_results_layout)
        
        if not result.get('success'):
            error_label = QLabel(f"❌ Hata: {result.get('error', 'Bilinmeyen hata')}")
            error_label.setStyleSheet("color: red; font-size: 12pt; padding: 20px;")
            error_label.setWordWrap(True)
            self.ai_results_layout.addWidget(error_label)
            self.ai_results_layout.addStretch()
            return
        
        strategy = result.get('strategy', {})
        self.current_ai_strategy = strategy
        
        # Başlık
        title = QLabel("✅ AI Analizi Tamamlandı")
        title.setStyleSheet("color: green; font-size: 16pt; font-weight: bold; padding: 10px;")
        self.ai_results_layout.addWidget(title)
        
        # Sonuç kartları
        self._add_result_card(
            "📧 Önerilen Mail Sayısı",
            f"{strategy.get('recommended_mail_count', 0)} mail",
            strategy.get('overall_reasoning', '')[:200] + "..."
        )
        
        # Gönderim zamanları
        schedule = strategy.get('send_schedule', [])
        schedule_text = "\n".join([
            f"• {s.get('day', 'Bilinmiyor')} {s.get('time', 'Bilinmiyor')}: {s.get('reasoning', '')[:50]}..."
            for s in schedule[:5]
        ])
        self._add_result_card("📅 Önerilen Gönderim Zamanları", schedule_text or "Veri yok")
        
        # İçerik türleri
        content_types = strategy.get('content_types', [])
        content_text = "\n".join([
            f"• [{c.get('priority', '-').upper()}] {c.get('type', 'Bilinmiyor')}"
            for c in content_types[:5]
        ])
        self._add_result_card("📝 Önerilen İçerik Türleri", content_text or "Veri yok")
        
        # Risk analizi
        risk = strategy.get('risk_analysis', {})
        risk_text = f"""Spam Riski: {risk.get('spam_risk', 'Bilinmiyor')}
Aşırı Mail Riski: {str(risk.get('over_mailing_risk', 'Veri yok'))[:100]}
Düşük Etkileşim Riski: {str(risk.get('low_engagement_risk', 'Veri yok'))[:100]}"""
        self._add_result_card("⚠️ Risk Analizi", risk_text, "#4a2020")
        
        # Fırsat analizi
        opp = strategy.get('opportunity_analysis', {})
        opp_text = f"""Yüksek Etkileşim Potansiyeli: {str(opp.get('high_engagement_potential', 'Veri yok'))[:100]}
En İyi Zamanlama: {str(opp.get('best_timing', 'Veri yok'))[:100]}
İçerik Fırsatları: {str(opp.get('content_opportunities', 'Veri yok'))[:100]}"""
        self._add_result_card("🎯 Fırsat Analizi", opp_text, "#204a20")
        
        # Tahminler
        predictions_text = f"""Etkileşim Tahmini: {strategy.get('engagement_prediction', 0)}/100
Spam Risk Skoru: {strategy.get('spam_risk_score', 0)}/100"""
        self._add_result_card("📊 Tahminler", predictions_text)
        
        self.ai_results_layout.addStretch()
        
        # Onayla butonunu aktif et
        self.ai_approve_btn.setEnabled(True)
    
    def _add_result_card(self, title: str, content: str, bg_color: str = "#2b2b2b"):
        """Sonuç kartı ekle"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"background-color: {bg_color}; border-radius: 5px; padding: 10px;")
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)
        
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("font-size: 10pt;")
        layout.addWidget(content_label)
        
        self.ai_results_layout.addWidget(card)
    
    def _approve_strategy(self):
        """Stratejiyi onayla"""
        if not self.current_company or not self.current_ai_strategy:
            QMessageBox.warning(self, "Uyarı", "Önce AI analizi yapın!")
            return
        
        reply = QMessageBox.question(
            self,
            "Onay",
            "Bu AI stratejisini onaylamak istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Başarılı", "Strateji onaylandı ve aktif edildi!")
            self.ai_approve_btn.setEnabled(False)
    
    def _refresh_ai_data(self):
        """AI verilerini yenile"""
        self._load_company_data()
    
    def _update_mail_count_label(self, value):
        """Mail sayısı etiketini güncelle"""
        self.mail_count_label.setText(f"{value} mail")
    
    def _add_schedule(self):
        """Zamanlama ekle"""
        day = self.schedule_day.currentText()
        time = self.schedule_time.text()
        
        if not time:
            QMessageBox.warning(self, "Uyarı", "Lütfen saat girin!")
            return
        
        schedule_text = f"{day} - {time}"
        self.schedule_list.addItem(schedule_text)
        self.schedule_time.clear()
    
    def _remove_schedule(self):
        """Zamanlamayı sil"""
        current_item = self.schedule_list.currentItem()
        if current_item:
            self.schedule_list.takeItem(self.schedule_list.row(current_item))
    
    def _save_manual_strategy(self):
        """Manuel stratejiyi kaydet"""
        if not self.current_company:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir firma seçin!")
            return
        
        mail_count = self.mail_count_slider.value()
        
        # Zamanlamaları al
        schedules = []
        for i in range(self.schedule_list.count()):
            schedule_text = self.schedule_list.item(i).text()
            parts = schedule_text.split(" - ")
            if len(parts) == 2:
                schedules.append({"day": parts[0], "time": parts[1]})
        
        # İçerik türlerini al
        content_types = [
            name for name, cb in self.content_checkboxes.items() if cb.isChecked()
        ]
        
        notes = self.manual_notes.toPlainText()
        
        # Kaydet
        success = self.strategy_manager.save_manual_strategy(
            self.current_company,
            mail_count,
            schedules,
            content_types,
            notes
        )
        
        if success:
            QMessageBox.information(self, "Başarılı", "Manuel strateji kaydedildi!")
        else:
            QMessageBox.critical(self, "Hata", "Strateji kaydedilemedi!")
    
    def _update_performance_tab(self):
        """Performans sekmesini güncelle"""
        self._clear_layout(self.performance_layout)
        
        if not self.current_company:
            return
        
        history = self.strategy_manager.get_company_history(self.current_company)
        
        title = QLabel(f"📊 {self.current_company} - Performans Özeti")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        self.performance_layout.addWidget(title)
        
        metrics = [
            ("Toplam Mail", history['total_mails'], "blue"),
            ("Açılma Oranı", f"{history['open_rate']}%", "green"),
            ("Yanıt Oranı", f"{history['reply_rate']}%", "orange"),
            ("Tıklama Oranı", f"{history['click_rate']}%", "purple"),
        ]
        
        for metric, value, color in metrics:
            card = QFrame()
            card.setFrameStyle(QFrame.StyledPanel)
            card_layout = QHBoxLayout(card)
            
            label = QLabel(metric)
            label.setStyleSheet("font-size: 11pt;")
            card_layout.addWidget(label)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {color};")
            card_layout.addWidget(value_label, alignment=Qt.AlignRight)
            
            self.performance_layout.addWidget(card)
        
        self.performance_layout.addStretch()
    
    def _update_history_tab(self):
        """Geçmiş sekmesini güncelle"""
        self._clear_layout(self.history_layout)
        
        if not self.current_company:
            return
        
        mails = self.strategy_manager.get_previous_mails(self.current_company, 10)
        
        title = QLabel(f"📜 {self.current_company} - Mail Geçmişi")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        self.history_layout.addWidget(title)
        
        if not mails:
            no_data = QLabel("Henüz mail geçmişi yok")
            no_data.setStyleSheet("color: gray; padding: 20px;")
            self.history_layout.addWidget(no_data)
            self.history_layout.addStretch()
            return
        
        for mail in mails:
            card = QFrame()
            card.setFrameStyle(QFrame.StyledPanel)
            card_layout = QVBoxLayout(card)
            
            subject = QLabel(mail['subject'] or "Başlık yok")
            subject.setStyleSheet("font-weight: bold; font-size: 11pt;")
            card_layout.addWidget(subject)
            
            status_text = f"📅 {mail['sent_date']} | "
            status_text += "✅ Açıldı " if mail['opened'] else "❌ Açılmadı "
            status_text += "| 💬 Yanıtlandı " if mail['replied'] else "| ⏳ Bekliyor "
            status_text += f"| ⭐ {mail['engagement_score']}/100"
            
            status = QLabel(status_text)
            status.setStyleSheet("color: gray; font-size: 9pt;")
            card_layout.addWidget(status)
            
            self.history_layout.addWidget(card)
        
        self.history_layout.addStretch()
    
    def _show_help(self):
        """Yardım göster"""
        help_text = """🎯 AI Destekli Mail Takip Stratejisi Yöneticisi

📌 ÖZELLİKLER:

1. 🤖 AI Destekli Mod:
   - Firma geçmişini analiz eder
   - Web sitesi verilerini inceler
   - En uygun stratejiyi önerir
   - Risk ve fırsat analizi yapar

2. ✍️ Manuel Mod:
   - Tamamen kendi kontrolünüz
   - Özel zamanlama ve içerik seçimi

3. 📊 Performans Takibi:
   - Açılma, yanıt, tıklama oranları
   - Etkileşim skorları

🚀 NASIL KULLANILIR:

1. Bir firma seçin
2. AI veya Manuel mod seçin
3. AI Modu: "AI Analizi Yap" tıklayın
4. Önerileri inceleyin ve onaylayın

💡 İPUCU: AI önerilerini başlangıç noktası olarak
kullanıp, manuel düzenlemeler yapabilirsiniz!
"""
        QMessageBox.information(self, "Yardım", help_text)
    
    def _clear_layout(self, layout):
        """Layout içeriğini temizle"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# Test
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = MailStrategyTab()
    window.setWindowTitle("Mail Strateji Yöneticisi - Test")
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())
