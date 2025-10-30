#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Maliyet Takip Widget'ı
OpenAI API kullanım ve maliyet takibi için kompakt widget
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QProgressBar, QToolTip, QDialog)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QPalette
import json
from datetime import datetime


class APICostWidget(QWidget):
    """API Maliyet Takip Widget'ı - Kompakt ve şık"""
    
    # Signals
    reset_requested = Signal()
    details_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Maliyet verileri
        self.total_cost = 0.0
        self.budget_limit = 10.0  # Varsayılan $10 limit
        self.total_requests = 0
        self.total_images = 0
        self.session_start = datetime.now()
        
        self.setup_ui()
        self.apply_styles()
        
        # Otomatik güncelleme timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(5000)  # 5 saniyede bir güncelle
    
    def setup_ui(self):
        """UI'ı oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Başlık
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel("💰 API Maliyet")
        self.title_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Detay butonu
        self.details_btn = QPushButton("📊")
        self.details_btn.setFixedSize(24, 24)
        self.details_btn.setToolTip("Detaylı istatistikler")
        self.details_btn.clicked.connect(self.details_requested.emit)
        title_layout.addWidget(self.details_btn)
        
        # Reset butonu
        self.reset_btn = QPushButton("🔄")
        self.reset_btn.setFixedSize(24, 24)
        self.reset_btn.setToolTip("İstatistikleri sıfırla")
        self.reset_btn.clicked.connect(self.reset_requested.emit)
        title_layout.addWidget(self.reset_btn)
        
        layout.addLayout(title_layout)
        
        # Maliyet göstergesi
        cost_layout = QHBoxLayout()
        
        self.cost_label = QLabel("$0.0000")
        self.cost_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        cost_layout.addWidget(self.cost_label)
        
        cost_layout.addStretch()
        
        self.budget_label = QLabel("/ $10.00")
        self.budget_label.setFont(QFont("Segoe UI", 8))
        cost_layout.addWidget(self.budget_label)
        
        layout.addLayout(cost_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)
        
        # İstatistikler (kompakt)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        # İstek sayısı
        self.requests_label = QLabel("📡 0")
        self.requests_label.setFont(QFont("Segoe UI", 8))
        self.requests_label.setToolTip("Toplam API çağrısı")
        stats_layout.addWidget(self.requests_label)
        
        # Görsel sayısı
        self.images_label = QLabel("🖼️ 0")
        self.images_label.setFont(QFont("Segoe UI", 8))
        self.images_label.setToolTip("Analiz edilen görsel")
        stats_layout.addWidget(self.images_label)
        
        stats_layout.addStretch()
        
        # Durum
        self.status_label = QLabel("✅")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setToolTip("Bütçe durumu: İyi")
        stats_layout.addWidget(self.status_label)
        
        layout.addLayout(stats_layout)
        
        # Kalan bütçe (küçük)
        self.remaining_label = QLabel("Kalan: $10.00")
        self.remaining_label.setFont(QFont("Segoe UI", 7))
        self.remaining_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.remaining_label)
        
        self.setLayout(layout)
    
    def apply_styles(self):
        """Stil uygula"""
        self.setStyleSheet("""
            APICostWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
            }
            QLabel {
                color: #212529;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #e9ecef;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #28a745;
            }
        """)
    
    def update_cost(self, cost: float, requests: int = 1, images: int = 0):
        """
        Maliyet güncelle
        
        Args:
            cost: Eklenen maliyet (USD)
            requests: Eklenen istek sayısı
            images: Eklenen görsel sayısı
        """
        self.total_cost = max(0.0, self.total_cost + cost)  # Negatif değerleri önle
        self.total_requests = max(0, self.total_requests + requests)
        self.total_images = max(0, self.total_images + images)
        
        self.update_display()
    
    def update_display(self):
        """Görüntüyü güncelle"""
        # Maliyet
        self.cost_label.setText(f"${self.total_cost:.4f}")
        
        # Progress bar
        progress = min(int((self.total_cost / self.budget_limit) * 100), 100)
        self.progress_bar.setValue(progress)
        
        # Progress bar rengi
        if progress < 50:
            color = "#28a745"  # Yeşil
            status = "✅"
            status_tip = "Bütçe durumu: İyi"
        elif progress < 80:
            color = "#ffc107"  # Sarı
            status = "⚠️"
            status_tip = "Bütçe durumu: Dikkat"
        else:
            color = "#dc3545"  # Kırmızı
            status = "🔴"
            status_tip = "Bütçe durumu: Limit yaklaşıyor!"
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: #e9ecef;
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
                background-color: {color};
            }}
        """)
        
        # Durum
        self.status_label.setText(status)
        self.status_label.setToolTip(status_tip)
        
        # İstatistikler
        self.requests_label.setText(f"📡 {self.total_requests}")
        self.images_label.setText(f"🖼️ {self.total_images}")
        
        # Kalan bütçe
        remaining = max(self.budget_limit - self.total_cost, 0)
        self.remaining_label.setText(f"Kalan: ${remaining:.4f}")
        
        # Bütçe limiti
        self.budget_label.setText(f"/ ${self.budget_limit:.2f}")
    
    def set_budget_limit(self, limit: float):
        """Bütçe limitini ayarla"""
        self.budget_limit = limit
        self.update_display()
    
    def reset_stats(self):
        """İstatistikleri sıfırla"""
        self.total_cost = 0.0
        self.total_requests = 0
        self.total_images = 0
        self.session_start = datetime.now()
        self.update_display()
    
    def get_stats(self) -> dict:
        """İstatistikleri al"""
        # Division by zero önleme
        avg_cost_request = 0.0
        if self.total_requests > 0:
            avg_cost_request = self.total_cost / self.total_requests
        
        avg_cost_image = 0.0
        if self.total_images > 0:
            avg_cost_image = self.total_cost / self.total_images
        
        usage_pct = 0.0
        if self.budget_limit > 0:
            usage_pct = min((self.total_cost / self.budget_limit) * 100, 100)
        
        return {
            'total_cost': self.total_cost,
            'total_requests': self.total_requests,
            'total_images': self.total_images,
            'budget_limit': self.budget_limit,
            'remaining_budget': max(self.budget_limit - self.total_cost, 0),
            'usage_percentage': usage_pct,
            'session_start': self.session_start.isoformat(),
            'average_cost_per_request': avg_cost_request,
            'average_cost_per_image': avg_cost_image
        }
    
    def load_stats(self, stats: dict):
        """İstatistikleri yükle"""
        self.total_cost = stats.get('total_cost', 0.0)
        self.total_requests = stats.get('total_requests', 0)
        self.total_images = stats.get('total_images', 0)
        self.budget_limit = stats.get('budget_limit', 10.0)
        
        session_start_str = stats.get('session_start')
        if session_start_str:
            try:
                self.session_start = datetime.fromisoformat(session_start_str)
            except:
                pass
        
        self.update_display()
    
    def save_stats(self, filename: str = "api_cost_stats.json"):
        """İstatistikleri kaydet"""
        try:
            stats = self.get_stats()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ İstatistik kayıt hatası: {e}")
            return False
    
    def load_stats_from_file(self, filename: str = "api_cost_stats.json"):
        """İstatistikleri dosyadan yükle"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            self.load_stats(stats)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"❌ İstatistik yükleme hatası: {e}")
            return False


class APICostDetailsDialog(QDialog):
    """Detaylı API maliyet istatistikleri dialog'u"""
    
    def __init__(self, stats: dict, parent=None):
        super().__init__(parent)
        self.stats = stats
        self.setWindowTitle("📊 API Maliyet Detayları")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """UI'ı oluştur"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #212529;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Başlık
        title = QLabel("📊 API Kullanım İstatistikleri")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: #212529; padding-bottom: 10px;")
        layout.addWidget(title)
        
        # Ayırıcı
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #dee2e6;")
        layout.addWidget(line)
        
        # Maliyet bilgileri
        cost_info = f"""
        <h3>💰 Maliyet Bilgileri</h3>
        <p><b>Toplam Harcama:</b> ${self.stats['total_cost']:.4f}</p>
        <p><b>Bütçe Limiti:</b> ${self.stats['budget_limit']:.2f}</p>
        <p><b>Kalan Bütçe:</b> ${self.stats['remaining_budget']:.4f}</p>
        <p><b>Kullanım Oranı:</b> %{self.stats['usage_percentage']:.1f}</p>
        
        <h3>📊 Kullanım İstatistikleri</h3>
        <p><b>Toplam İstek:</b> {self.stats['total_requests']}</p>
        <p><b>Analiz Edilen Görsel:</b> {self.stats['total_images']}</p>
        <p><b>İstek Başına Ort. Maliyet:</b> ${self.stats['average_cost_per_request']:.4f}</p>
        <p><b>Görsel Başına Ort. Maliyet:</b> ${self.stats['average_cost_per_image']:.4f}</p>
        
        <h3>⏱️ Oturum Bilgileri</h3>
        <p><b>Başlangıç:</b> {self.stats['session_start']}</p>
        """
        
        info_label = QLabel(cost_info)
        info_label.setWordWrap(True)
        info_label.setTextFormat(Qt.RichText)
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Stil
        self.setStyleSheet("""
            APICostDetailsDialog {
                background-color: white;
            }
            QLabel {
                color: #212529;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)


# Test
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Widget oluştur
    widget = APICostWidget()
    widget.setFixedWidth(250)
    widget.show()
    
    # Test verileri ekle
    import random
    
    def add_random_cost():
        cost = random.uniform(0.001, 0.01)
        widget.update_cost(cost, requests=1, images=random.randint(0, 2))
    
    # Timer ile rastgele maliyet ekle
    test_timer = QTimer()
    test_timer.timeout.connect(add_random_cost)
    test_timer.start(2000)
    
    # Detay dialog göster
    def show_details():
        dialog = APICostDetailsDialog(widget.get_stats())
        dialog.show()
    
    widget.details_requested.connect(show_details)
    widget.reset_requested.connect(widget.reset_stats)
    
    sys.exit(app.exec())

