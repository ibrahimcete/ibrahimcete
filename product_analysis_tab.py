#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ürün Analizi Sekmesi - Kendi ürünlerinizi analiz etmek için GUI
Bu sekme, ikinci özellik için kullanılacak: Bizim firmanın ürünlerini ve web sitesini analiz et
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTextEdit, QLineEdit, QFileDialog,
                               QScrollArea, QFrame, QGridLayout, QMessageBox,
                               QListWidget, QListWidgetItem, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
import os
import json


class ProductAnalysisTab(QWidget):
    """Ürün Analizi Sekmesi - Kendi ürünlerinizi AI'ya tanıtın"""
    
    # Sinyaller
    analysis_saved = Signal(dict)  # Analiz kaydedildiğinde
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.product_images = []  # Yüklenen ürün görselleri
        self.product_data = {}  # Ürün verileri
        self.init_ui()
        self.load_saved_data()
    
    def init_ui(self):
        """UI'ı oluştur"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Başlık bölümü
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0d7377, stop: 1 #14a085);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("🎯 Kendi Ürünlerinizi Tanıtın")
        title_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 24px;
        """)
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel(
            "Ürün görsellerinizi, web sitenizi ve açıklamalarınızı ekleyin. "
            "AI, bu bilgileri kullanarak taranan firmalarla eşleştirme yapacak ve "
            "kişiselleştirilmiş satış stratejileri oluşturacak."
        )
        subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 13px;
            padding-top: 5px;
        """)
        subtitle_label.setWordWrap(True)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header_frame)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # 1. WEB SİTESİ BÖLÜMÜ
        website_group = self.create_website_section()
        scroll_layout.addWidget(website_group)
        
        # 2. ÜRÜN GÖRSELLERİ BÖLÜMÜ
        images_group = self.create_images_section()
        scroll_layout.addWidget(images_group)
        
        # 3. ÜRÜN AÇIKLAMALARI BÖLÜMÜ
        description_group = self.create_description_section()
        scroll_layout.addWidget(description_group)
        
        # 4. EK BİLGİLER BÖLÜMÜ
        additional_group = self.create_additional_section()
        scroll_layout.addWidget(additional_group)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Alt butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Kaydet butonu
        save_btn = QPushButton("💾 Kaydet ve AI'ya Gönder")
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_product_data)
        button_layout.addWidget(save_btn)
        
        # Önizleme butonu
        preview_btn = QPushButton("👁️ Önizleme")
        preview_btn.setMinimumHeight(45)
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2874a6;
            }
        """)
        preview_btn.clicked.connect(self.preview_data)
        button_layout.addWidget(preview_btn)
        
        # Temizle butonu
        clear_btn = QPushButton("🗑️ Temizle")
        clear_btn.setMinimumHeight(45)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ec7063;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_all_data)
        button_layout.addWidget(clear_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_website_section(self):
        """Web sitesi bölümünü oluştur"""
        group = QGroupBox("🌐 Firmanızın Web Sitesi")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 20px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 16px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Web sitesi URL'si
        url_label = QLabel("Web Sitesi URL'si:")
        url_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: normal;")
        layout.addWidget(url_label)
        
        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("https://www.firmaniz.com")
        self.website_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #0d7377;
            }
        """)
        layout.addWidget(self.website_input)
        
        # Açıklama
        info_label = QLabel(
            "💡 AI, web sitenizi analiz ederek ürünlerinizi, hizmetlerinizi ve "
            "şirket profilinizi otomatik olarak çıkaracaktır."
        )
        info_label.setStyleSheet("""
            color: #95a5a6;
            font-size: 11px;
            font-weight: normal;
            padding: 5px;
            background-color: rgba(52, 152, 219, 0.1);
            border-radius: 4px;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        return group
    
    def create_images_section(self):
        """Ürün görselleri bölümünü oluştur"""
        group = QGroupBox("📸 Ürün Görselleri")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 20px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 16px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Buton bölümü
        button_layout = QHBoxLayout()
        
        upload_btn = QPushButton("📁 Görsel Yükle")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        upload_btn.clicked.connect(self.upload_images)
        button_layout.addWidget(upload_btn)
        
        clear_images_btn = QPushButton("🗑️ Görselleri Temizle")
        clear_images_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ec7063;
            }
        """)
        clear_images_btn.clicked.connect(self.clear_images)
        button_layout.addWidget(clear_images_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Görsel listesi
        self.images_list = QListWidget()
        self.images_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 5px;
                color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
            }
        """)
        self.images_list.setMaximumHeight(150)
        layout.addWidget(self.images_list)
        
        # Bilgi
        info_label = QLabel(
            "💡 Ürün görsellerinizi yükleyin. AI, görselleri analiz ederek ürün özelliklerini, "
            "kaliteyi ve tasarımı değerlendirecektir."
        )
        info_label.setStyleSheet("""
            color: #95a5a6;
            font-size: 11px;
            font-weight: normal;
            padding: 5px;
            background-color: rgba(52, 152, 219, 0.1);
            border-radius: 4px;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        return group
    
    def create_description_section(self):
        """Ürün açıklamaları bölümünü oluştur"""
        group = QGroupBox("📝 Ürün Açıklamaları ve Özellikler")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 20px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 16px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Ürün açıklaması
        desc_label = QLabel("Ürün Açıklaması:")
        desc_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: normal;")
        layout.addWidget(desc_label)
        
        self.product_description = QTextEdit()
        self.product_description.setPlaceholderText(
            "Ürünlerinizi detaylı bir şekilde açıklayın:\n"
            "- Ürün kategorileri\n"
            "- Özellikler ve avantajlar\n"
            "- Hedef kitle\n"
            "- Benzersiz satış noktaları\n"
            "- Kalite standartları\n"
            "- Sertifikalar"
        )
        self.product_description.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #0d7377;
            }
        """)
        self.product_description.setMinimumHeight(200)
        layout.addWidget(self.product_description)
        
        return group
    
    def create_additional_section(self):
        """Ek bilgiler bölümünü oluştur"""
        group = QGroupBox("➕ Ek Bilgiler ve Notlar")
        group.setStyleSheet("""
            QGroupBox {
                background-color: #2a2a2a;
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                padding: 20px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 16px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Ek bilgiler
        additional_label = QLabel("Ek Bilgiler ve Stratejik Notlar:")
        additional_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: normal;")
        layout.addWidget(additional_label)
        
        self.additional_info = QTextEdit()
        self.additional_info.setPlaceholderText(
            "AI'nın dikkate almasını istediğiniz ek bilgileri ekleyin:\n"
            "- Fiyatlandırma stratejisi\n"
            "- Minimum sipariş miktarları\n"
            "- Teslimat süreleri\n"
            "- Özel kampanyalar\n"
            "- Hedef sektörler\n"
            "- Rekabet avantajları\n"
            "- Satış yaklaşımı tercihleri"
        )
        self.additional_info.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #0d7377;
            }
        """)
        self.additional_info.setMinimumHeight(150)
        layout.addWidget(self.additional_info)
        
        return group
    
    def upload_images(self):
        """Ürün görsellerini yükle"""
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(
            self,
            "Ürün Görsellerini Seçin",
            "",
            "Görsel Dosyaları (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.product_images:
                    self.product_images.append(file_path)
                    # Listeye ekle
                    item = QListWidgetItem(f"📷 {os.path.basename(file_path)}")
                    item.setData(Qt.UserRole, file_path)
                    self.images_list.addItem(item)
            
            QMessageBox.information(
                self,
                "✅ Başarılı",
                f"{len(file_paths)} görsel yüklendi!"
            )
    
    def clear_images(self):
        """Tüm görselleri temizle"""
        reply = QMessageBox.question(
            self,
            "Onay",
            "Tüm görselleri silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.product_images.clear()
            self.images_list.clear()
            QMessageBox.information(self, "✅ Temizlendi", "Tüm görseller silindi!")
    
    def save_product_data(self):
        """Ürün verilerini kaydet"""
        # Verileri topla
        self.product_data = {
            "website": self.website_input.text().strip(),
            "images": self.product_images.copy(),
            "description": self.product_description.toPlainText().strip(),
            "additional_info": self.additional_info.toPlainText().strip()
        }
        
        # Validasyon
        if not self.product_data["website"] and not self.product_data["images"] and not self.product_data["description"]:
            QMessageBox.warning(
                self,
                "⚠️ Uyarı",
                "Lütfen en azından web sitesi, ürün görseli veya açıklama girin!"
            )
            return
        
        # JSON dosyasına kaydet
        try:
            with open("product_analysis_data.json", "w", encoding="utf-8") as f:
                json.dump(self.product_data, f, ensure_ascii=False, indent=2)
            
            # Sinyal gönder
            self.analysis_saved.emit(self.product_data)
            
            QMessageBox.information(
                self,
                "✅ Başarılı",
                "Ürün bilgileriniz kaydedildi!\n\n"
                "AI artık bu bilgileri kullanarak:\n"
                "• Taranan firmalarla eşleştirme yapacak\n"
                "• Uygun ürün önerileri sunacak\n"
                "• Kişiselleştirilmiş satış stratejileri oluşturacak\n"
                "• Mail taslakları hazırlarken bu verileri kullanacak"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Hata",
                f"Veriler kaydedilemedi:\n{str(e)}"
            )
    
    def preview_data(self):
        """Verilerin önizlemesini göster"""
        preview_text = "📊 ÜRÜN ANALİZİ ÖNİZLEMESİ\n"
        preview_text += "=" * 50 + "\n\n"
        
        preview_text += f"🌐 Web Sitesi:\n{self.website_input.text().strip() or 'Belirtilmemiş'}\n\n"
        
        preview_text += f"📸 Ürün Görselleri: {len(self.product_images)} adet\n"
        for img in self.product_images:
            preview_text += f"  • {os.path.basename(img)}\n"
        preview_text += "\n"
        
        preview_text += f"📝 Ürün Açıklaması:\n{self.product_description.toPlainText().strip() or 'Belirtilmemiş'}\n\n"
        
        preview_text += f"➕ Ek Bilgiler:\n{self.additional_info.toPlainText().strip() or 'Belirtilmemiş'}\n"
        
        # Önizleme dialogu
        dialog = QMessageBox(self)
        dialog.setWindowTitle("👁️ Ürün Bilgileri Önizlemesi")
        dialog.setText(preview_text)
        dialog.setIcon(QMessageBox.Information)
        dialog.exec()
    
    def clear_all_data(self):
        """Tüm verileri temizle"""
        reply = QMessageBox.question(
            self,
            "⚠️ Onay",
            "Tüm girilen verileri silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.website_input.clear()
            self.product_images.clear()
            self.images_list.clear()
            self.product_description.clear()
            self.additional_info.clear()
            self.product_data = {}
            
            QMessageBox.information(self, "✅ Temizlendi", "Tüm veriler silindi!")
    
    def load_saved_data(self):
        """Kaydedilmiş verileri yükle"""
        try:
            if os.path.exists("product_analysis_data.json"):
                with open("product_analysis_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.website_input.setText(data.get("website", ""))
                self.product_description.setPlainText(data.get("description", ""))
                self.additional_info.setPlainText(data.get("additional_info", ""))
                
                # Görselleri yükle
                images = data.get("images", [])
                for img_path in images:
                    if os.path.exists(img_path):
                        self.product_images.append(img_path)
                        item = QListWidgetItem(f"📷 {os.path.basename(img_path)}")
                        item.setData(Qt.UserRole, img_path)
                        self.images_list.addItem(item)
                
                self.product_data = data
                
        except Exception as e:
            print(f"Kaydedilmiş veri yükleme hatası: {e}")
    
    def get_product_data(self):
        """Ürün verilerini döndür"""
        return self.product_data

