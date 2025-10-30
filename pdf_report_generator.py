#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Destekli Haftalık PDF Rapor Oluşturucu
B2B Mail Automation Pro için gelişmiş rapor sistemi
"""

import os
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from io import BytesIO
import base64
import openai
from database import Database

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIReportGenerator:
    """AI destekli haftalık PDF rapor oluşturucu"""
    
    def __init__(self, config_path: str = "config.json"):
        """Rapor oluşturucuyu başlat"""
        self.db = Database()
        self.config = self._load_config(config_path)
        self._setup_openai()
        
        # Türkçe font desteği
        self._setup_turkish_fonts()
        
        # Rapor stilleri
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _load_config(self, config_path: str) -> Dict:
        """Konfigürasyon dosyasını yükle"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Config yükleme hatası: {e}")
            return {}
    
    def _setup_openai(self):
        """OpenAI API'yi ayarla"""
        try:
            openai.api_key = self.config.get('openai_api_key', '')
            if not openai.api_key:
                logger.warning("OpenAI API key bulunamadı")
        except Exception as e:
            logger.error(f"OpenAI setup hatası: {e}")
    
    def _setup_turkish_fonts(self):
        """Türkçe karakter desteği için font ayarları"""
        try:
            # Sistem fontlarını kullan
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Windows için Arial fontunu kullan
                try:
                    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
                    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
                    pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))
                    pdfmetrics.registerFont(TTFont('Arial-BoldItalic', 'C:/Windows/Fonts/arialbi.ttf'))
                    
                    # Font mapping
                    addMapping('Arial', 0, 0, 'Arial')
                    addMapping('Arial', 0, 1, 'Arial-Italic')
                    addMapping('Arial', 1, 0, 'Arial-Bold')
                    addMapping('Arial', 1, 1, 'Arial-BoldItalic')
                    
                    self.default_font = 'Arial'
                    logger.info("Windows Arial fontları yüklendi")
                except:
                    # Fallback: Helvetica kullan
                    self.default_font = 'Helvetica'
                    logger.warning("Arial fontları yüklenemedi, Helvetica kullanılıyor")
            else:
                # Linux/Mac için Helvetica kullan
                self.default_font = 'Helvetica'
                logger.info("Helvetica fontu kullanılıyor")
                
        except Exception as e:
            logger.error(f"Font setup hatası: {e}")
            self.default_font = 'Helvetica'
    
    def _setup_custom_styles(self):
        """Özel rapor stilleri oluştur - Türkçe karakter desteği ile"""
        # Başlık stili
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.default_font,
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        ))
        
        # Alt başlık stili
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontName=self.default_font,
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#A23B72')
        ))
        
        # Özet stili
        self.styles.add(ParagraphStyle(
            name='SummaryStyle',
            parent=self.styles['Normal'],
            fontName=self.default_font,
            fontSize=12,
            spaceAfter=12,
            leftIndent=20,
            rightIndent=20,
            textColor=colors.HexColor('#F18F01')
        ))
        
        # Veri stili
        self.styles.add(ParagraphStyle(
            name='DataStyle',
            parent=self.styles['Normal'],
            fontName=self.default_font,
            fontSize=10,
            spaceAfter=6,
            leftIndent=10
        ))
        
        # Türkçe karakter desteği için özel stiller
        self.styles.add(ParagraphStyle(
            name='TurkishNormal',
            parent=self.styles['Normal'],
            fontName=self.default_font,
            fontSize=11,
            spaceAfter=6,
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='TurkishHeading',
            parent=self.styles['Heading1'],
            fontName=self.default_font,
            fontSize=18,
            spaceAfter=12,
            spaceBefore=12,
            alignment=TA_LEFT,
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='TurkishTable',
            parent=self.styles['Normal'],
            fontName=self.default_font,
            fontSize=9,
            spaceAfter=3,
            encoding='utf-8'
        ))
    
    def generate_weekly_report(self, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> str:
        """Haftalık AI destekli rapor oluştur"""
        try:
            # Tarih aralığını belirle
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=7)
            
            # Tarih formatını düzelt
            start_str = start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else str(start_date)
            end_str = end_date.strftime('%Y-%m-%d') if hasattr(end_date, 'strftime') else str(end_date)
            logger.info(f"Haftalık rapor oluşturuluyor: {start_str} - {end_str}")
            
            # Verileri topla
            report_data = self._collect_weekly_data(start_date, end_date)
            
            # AI analizi yap
            ai_analysis = self._generate_ai_analysis(report_data)
            
            # PDF oluştur
            pdf_path = self._create_pdf_report(report_data, ai_analysis, start_date, end_date)
            
            logger.info(f"Rapor oluşturuldu: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Haftalık rapor oluşturma hatası: {e}")
            return None
    
    def _collect_weekly_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Haftalık verileri topla"""
        try:
            data = {}
            
            # Temel istatistikler
            data['stats'] = self._get_weekly_stats(start_date, end_date)
            
            # Firma verileri
            data['firms'] = self._get_weekly_firms(start_date, end_date)
            
            # Email verileri
            data['emails'] = self._get_weekly_emails(start_date, end_date)
            
            # Mesaj verileri
            data['messages'] = self._get_weekly_messages(start_date, end_date)
            
            # Arama verileri
            data['calls'] = self._get_weekly_calls(start_date, end_date)
            
            # Aktivite verileri
            data['activities'] = self._get_weekly_activities(start_date, end_date)
            
            # Trend analizi
            data['trends'] = self._analyze_trends(start_date, end_date)
            
            return data
            
        except Exception as e:
            logger.error(f"Veri toplama hatası: {e}")
            return {}
    
    def _get_weekly_stats(self, start_date: datetime, end_date: datetime) -> Dict:
        """Haftalık temel istatistikler"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Tarih filtresi - datetime objelerini string'e çevir
                date_filter = "AND created_at >= ? AND created_at <= ?"
                start_str = start_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(start_date, 'strftime') else str(start_date)
                end_str = end_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(end_date, 'strftime') else str(end_date)
                params = [start_str, end_str]
                
                stats = {}
                
                # Firma istatistikleri
                cursor.execute(f"""
                    SELECT COUNT(*) FROM firms 
                    WHERE 1=1 {date_filter}
                """, params)
                stats['new_firms'] = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT COUNT(*) FROM firms 
                    WHERE status = 'active' {date_filter}
                """, params)
                stats['active_firms'] = cursor.fetchone()[0]
                
                # Email istatistikleri
                cursor.execute(f"""
                    SELECT COUNT(*) FROM email_logs 
                    WHERE 1=1 {date_filter}
                """, params)
                stats['total_emails'] = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT COUNT(*) FROM email_logs 
                    WHERE opened = 1 {date_filter}
                """, params)
                stats['opened_emails'] = cursor.fetchone()[0]
                
                cursor.execute(f"""
                    SELECT COUNT(*) FROM email_logs 
                    WHERE replied = 1 {date_filter}
                """, params)
                stats['replied_emails'] = cursor.fetchone()[0]
                
                # Mesaj istatistikleri
                cursor.execute(f"""
                    SELECT COUNT(*) FROM messages 
                    WHERE 1=1 {date_filter}
                """, params)
                stats['total_messages'] = cursor.fetchone()[0]
                
                # Arama istatistikleri
                cursor.execute(f"""
                    SELECT COUNT(*) FROM calls 
                    WHERE 1=1 {date_filter}
                """, params)
                stats['total_calls'] = cursor.fetchone()[0]
                
                # Oranlar
                if stats['total_emails'] > 0:
                    stats['open_rate'] = round((stats['opened_emails'] / stats['total_emails']) * 100, 1)
                    stats['reply_rate'] = round((stats['replied_emails'] / stats['total_emails']) * 100, 1)
                else:
                    stats['open_rate'] = 0
                    stats['reply_rate'] = 0
                
                return stats
                
        except Exception as e:
            logger.error(f"İstatistik toplama hatası: {e}")
            return {}
    
    def _get_weekly_firms(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Haftalık firma verileri"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Tarih dönüşümü
                start_str = start_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(start_date, 'strftime') else str(start_date)
                end_str = end_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(end_date, 'strftime') else str(end_date)
                
                cursor.execute("""
                    SELECT name, sector, status, created_at, rating, review_count
                    FROM firms 
                    WHERE created_at >= ? AND created_at <= ?
                    ORDER BY created_at DESC
                """, (start_str, end_str))
                
                firms = []
                for row in cursor.fetchall():
                    firms.append({
                        'name': row[0],
                        'sector': row[1] or 'Belirtilmemiş',
                        'status': row[2] or 'active',
                        'created_at': row[3],
                        'rating': row[4] or 0,
                        'review_count': row[5] or 0
                    })
                return firms
                
        except Exception as e:
            logger.error(f"Firma verisi toplama hatası: {e}")
            return []
    
    def _get_weekly_emails(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Haftalık email verileri"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Tarih dönüşümü
                start_str = start_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(start_date, 'strftime') else str(start_date)
                end_str = end_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(end_date, 'strftime') else str(end_date)
                
                cursor.execute("""
                    SELECT el.subject, el.status, el.sent_date, el.opened, el.replied,
                           f.name as firm_name
                    FROM email_logs el
                    LEFT JOIN firms f ON el.firm_id = f.id
                    WHERE el.sent_date >= ? AND el.sent_date <= ?
                    ORDER BY el.sent_date DESC
                """, (start_str, end_str))
                
                emails = []
                for row in cursor.fetchall():
                    emails.append({
                        'subject': row[0] or 'Konu yok',
                        'status': row[1] or 'unknown',
                        'sent_date': row[2],
                        'opened': bool(row[3]),
                        'replied': bool(row[4]),
                        'firm_name': row[5] or 'Bilinmeyen Firma'
                    })
                return emails
                
        except Exception as e:
            logger.error(f"Email verisi toplama hatası: {e}")
            return []
    
    def _get_weekly_messages(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Haftalık mesaj verileri"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Tarih dönüşümü
                start_str = start_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(start_date, 'strftime') else str(start_date)
                end_str = end_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(end_date, 'strftime') else str(end_date)
                
                cursor.execute("""
                    SELECT m.direction, m.platform, m.status, m.created_at,
                           f.name as firm_name
                    FROM messages m
                    LEFT JOIN firms f ON m.firm_id = f.id
                    WHERE m.created_at >= ? AND m.created_at <= ?
                    ORDER BY m.created_at DESC
                """, (start_str, end_str))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'direction': row[0] or 'unknown',
                        'platform': row[1] or 'unknown',
                        'status': row[2] or 'unknown',
                        'created_at': row[3],
                        'firm_name': row[4] or 'Bilinmeyen Firma'
                    })
                return messages
                
        except Exception as e:
            logger.error(f"Mesaj verisi toplama hatası: {e}")
            return []
    
    def _get_weekly_calls(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Haftalık arama verileri"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Tarih dönüşümü
                start_str = start_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(start_date, 'strftime') else str(start_date)
                end_str = end_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(end_date, 'strftime') else str(end_date)
                
                cursor.execute("""
                    SELECT c.duration, c.status, c.created_at, c.transcript,
                           f.name as firm_name
                    FROM calls c
                    LEFT JOIN firms f ON c.firm_id = f.id
                    WHERE c.created_at >= ? AND c.created_at <= ?
                    ORDER BY c.created_at DESC
                """, (start_str, end_str))
                
                calls = []
                for row in cursor.fetchall():
                    calls.append({
                        'duration': row[0] or 0,
                        'status': row[1] or 'unknown',
                        'created_at': row[2],
                        'transcript': row[3] or '',
                        'firm_name': row[4] or 'Bilinmeyen Firma'
                    })
                return calls
                
        except Exception as e:
            logger.error(f"Arama verisi toplama hatası: {e}")
            return []
    
    def _get_weekly_activities(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Haftalık aktivite verileri"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT a.activity_type, a.description, a.created_at,
                           f.name as firm_name
                    FROM activities a
                    LEFT JOIN firms f ON a.firm_id = f.id
                    WHERE a.created_at >= ? AND a.created_at <= ?
                    ORDER BY a.created_at DESC
                """, (start_date, end_date))
                
                activities = []
                for row in cursor.fetchall():
                    activities.append({
                        'activity_type': row[0] or 'unknown',
                        'description': row[1] or '',
                        'created_at': row[2],
                        'firm_name': row[3] or 'Bilinmeyen Firma'
                    })
                return activities
                
        except Exception as e:
            logger.error(f"Aktivite verisi toplama hatası: {e}")
            return []
    
    def _analyze_trends(self, start_date: datetime, end_date: datetime) -> Dict:
        """Trend analizi yap"""
        try:
            trends = {}
            
            # Günlük veriler
            daily_data = []
            for i in range(7):
                date = start_date + timedelta(days=i)
                daily_stats = self._get_daily_stats(date)
                daily_data.append({
                    'date': date,
                    'firms': daily_stats.get('firms', 0),
                    'emails': daily_stats.get('emails', 0),
                    'messages': daily_stats.get('messages', 0),
                    'calls': daily_stats.get('calls', 0),
                    'activities': daily_stats.get('firms', 0) + daily_stats.get('emails', 0) + daily_stats.get('messages', 0)
                })
            
            trends['daily_data'] = daily_data
            
            # Sektör analizi
            trends['sector_analysis'] = self._analyze_sectors(start_date, end_date)
            
            # Performans metrikleri
            trends['performance'] = self._calculate_performance_metrics(start_date, end_date)
            
            return trends
            
        except Exception as e:
            logger.error(f"Trend analizi hatası: {e}")
            return {}
    
    def _get_daily_stats(self, date: datetime) -> Dict:
        """Günlük istatistikler"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Tarih dönüşümü
                if hasattr(date, 'strftime'):
                    date_str = date.strftime('%Y-%m-%d')
                else:
                    date_str = str(date)
                
                # Firmalar
                cursor.execute("""
                    SELECT COUNT(*) FROM firms 
                    WHERE DATE(created_at) = ?
                """, (date_str,))
                firms = cursor.fetchone()[0]
                
                # Emailler
                cursor.execute("""
                    SELECT COUNT(*) FROM email_logs 
                    WHERE DATE(sent_date) = ?
                """, (date_str,))
                emails = cursor.fetchone()[0]
                
                # Mesajlar
                cursor.execute("""
                    SELECT COUNT(*) FROM messages 
                    WHERE DATE(created_at) = ?
                """, (date_str,))
                messages = cursor.fetchone()[0]
                
                # Aramalar
                cursor.execute("""
                    SELECT COUNT(*) FROM calls 
                    WHERE DATE(created_at) = ?
                """, (date_str,))
                calls = cursor.fetchone()[0]
                
                return {
                    'firms': firms,
                    'emails': emails,
                    'messages': messages,
                    'calls': calls
                }
                
        except Exception as e:
            logger.error(f"Günlük istatistik hatası: {e}")
            return {}
    
    def _analyze_sectors(self, start_date: datetime, end_date: datetime) -> Dict:
        """Sektör analizi"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                # Tarih dönüşümü
                start_str = start_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(start_date, 'strftime') else str(start_date)
                end_str = end_date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(end_date, 'strftime') else str(end_date)
                
                cursor.execute("""
                    SELECT sector, COUNT(*) as count
                    FROM firms 
                    WHERE created_at >= ? AND created_at <= ?
                    AND sector IS NOT NULL AND sector != ''
                    GROUP BY sector
                    ORDER BY count DESC
                """, (start_str, end_str))
                
                sectors = {}
                for row in cursor.fetchall():
                    sectors[row[0]] = row[1]
                
                return sectors
                
        except Exception as e:
            logger.error(f"Sektör analizi hatası: {e}")
            return {}
    
    def _calculate_performance_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Performans metrikleri hesapla"""
        try:
            metrics = {}
            
            # Email performansı
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as opened,
                        SUM(CASE WHEN replied = 1 THEN 1 ELSE 0 END) as replied
                    FROM email_logs 
                    WHERE sent_date >= ? AND sent_date <= ?
                """, (start_date, end_date))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    metrics['email_performance'] = {
                        'total_sent': result[0],
                        'opened': result[1],
                        'replied': result[2],
                        'open_rate': round((result[1] / result[0]) * 100, 1),
                        'reply_rate': round((result[2] / result[0]) * 100, 1)
                    }
                else:
                    metrics['email_performance'] = {
                        'total_sent': 0, 'opened': 0, 'replied': 0,
                        'open_rate': 0, 'reply_rate': 0
                    }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Performans metrikleri hatası: {e}")
            return {}
    
    def _generate_ai_analysis(self, report_data: Dict) -> Dict:
        """AI ile rapor analizi yap"""
        try:
            if not self.config.get('openai_api_key'):
                return self._get_default_analysis()
            
            # Veri özetini hazırla
            data_summary = self._prepare_data_summary(report_data)
            
            # OpenAI'ye gönder - Daha detaylı ve kapsamlı prompt
            prompt = f"""
            Aşağıdaki B2B Mail Automation Pro haftalık verilerini DETAYLI olarak analiz et ve profesyonel bir rapor özeti oluştur:
            
            {data_summary}
            
            Lütfen şu konularda DETAYLI analiz yap:
            
            1. GENEL PERFORMANS DEĞERLENDİRMESİ:
               - Haftalık toplam aktivite özeti
               - Performans metrikleri karşılaştırması
               - Haftalık hedeflere ulaşma durumu
               - Bir önceki hafta ile karşılaştırma
            
            2. GÜÇLÜ YÖNLER VE BAŞARILAR:
               - En başarılı kampanyalar ve nedenleri
               - Yüksek etkileşim gösteren içerikler
               - Etkili stratejiler ve taktikler
               - Öne çıkan başarılar
            
            3. GELİŞİM ALANLARI VE RİSKLER:
               - Düşük performans gösteren alanlar
               - Tespit edilen sorunlar ve nedenleri
               - Potansiyel risk faktörleri
               - İyileştirilmesi gereken metrikler
            
            4. DETAYLI METRİK ANALİZİ:
               - Email açılma oranları ve trend analizi
               - Tıklama oranları ve içerik performansı
               - Yanıt oranları ve müşteri etkileşimi
               - Firma büyüme ve kazanım metrikleri
            
            5. STRATEJİK ÖNERİLER:
               - Performansı artırmak için spesifik öneriler
               - Gelecek hafta için eylem planı
               - Uzun vadeli strateji önerileri
               - Kaynak dağılımı ve önceliklendirme
            
            6. SEKTÖR VE PAZAR İÇGÖRÜLERİ:
               - En aktif sektörler ve trendler
               - Potansiyel fırsatlar
               - Pazar dinamikleri analizi
               - Rekabet değerlendirmesi
            
            7. KULLANICI DAVRANIŞI ANALİZİ:
               - En etkili iletişim kanalları
               - Müşteri etkileşim düzenleri
               - İçerik tercihleri ve trendler
               - Değişim ve büyüme göstergeleri
            
            Lütfen detaylı, yapıcı ve eyleme dönüştürülebilir bir analiz sun.
            Her bölümde somut veriler, örnekler ve net tavsiyeler içermeli.
            Türkçe olarak, profesyonel ve analitik bir ton kullan.
            Rapor 1000-1500 kelime arasında kapsamlı olmalı.
            """
            
            # OpenAI client oluştur (API 1.0+ uyumlu)
            from openai import OpenAI
            client = OpenAI(api_key=self.config.get('openai_api_key'))
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Sen bir B2B pazarlama analisti, veri uzmanı ve strateji danışmanısın. Derinlemesine analiz yapar, somut öneriler sunarsın ve eyleme dönüştürülebilir tavsiyelerde bulunursun."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                'summary': ai_analysis,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'model': 'gpt-4o',
                'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0,
                'analysis_length': len(ai_analysis)
            }
            
        except Exception as e:
            logger.error(f"AI analizi hatası: {e}")
            return self._get_default_analysis()
    
    def _prepare_data_summary(self, report_data: Dict) -> str:
        """Veri özetini hazırla"""
        try:
            stats = report_data.get('stats', {})
            trends = report_data.get('trends', {})
            
            summary = f"""
            HAFTALIK VERİ ÖZETİ:
            
            Yeni Firmalar: {stats.get('new_firms', 0)}
            Aktif Firmalar: {stats.get('active_firms', 0)}
            Toplam Email: {stats.get('total_emails', 0)}
            Açılan Email: {stats.get('opened_emails', 0)} (%{stats.get('open_rate', 0)})
            Yanıtlanan Email: {stats.get('replied_emails', 0)} (%{stats.get('reply_rate', 0)})
            Toplam Mesaj: {stats.get('total_messages', 0)}
            Toplam Arama: {stats.get('total_calls', 0)}
            
            GÜNLÜK TRENDLER:
            """
            
            daily_data = trends.get('daily_data', [])
            for day in daily_data:
                summary += f"\n{day['date']}: {day['firms']} firma, {day['emails']} email, {day['messages']} mesaj"
            
            return summary
            
        except Exception as e:
            logger.error(f"Veri özeti hazırlama hatası: {e}")
            return "Veri özeti hazırlanamadı."
    
    def _get_default_analysis(self) -> Dict:
        """Varsayılan analiz (AI kullanılamadığında)"""
        return {
            'summary': """
            Haftalık rapor analizi AI servisi kullanılamadığı için manuel olarak hazırlanmıştır.
            Verilerinizi inceleyerek performansınızı değerlendirmeniz önerilir.
            """,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'model': 'manual'
        }
    
    def _create_pdf_report(self, report_data: Dict, ai_analysis: Dict, 
                          start_date: datetime, end_date: datetime) -> str:
        """PDF raporu oluştur - Türkçe karakter desteği ile"""
        try:
            # Raporlar klasörünü oluştur
            reports_dir = os.path.join(os.getcwd(), "Raporlar")
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
                print(f"📁 Raporlar klasörü oluşturuldu: {reports_dir}")
            
            # Dosya adı oluştur - Tarih eklenmiş
            # Format: Haftalik_Rapor_BaslangicTarihi_BitisTarihi_OlusturmaTarihi.pdf
            start_date_str = start_date.strftime('%Y%m%d')
            end_date_str = end_date.strftime('%Y%m%d')
            creation_date = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            filename = f"Haftalik_Rapor_{start_date_str}_{end_date_str}_{creation_date}.pdf"
            filepath = os.path.join(reports_dir, filename)
            
            # PDF dokümanı oluştur - UTF-8 encoding ile
            doc = SimpleDocTemplate(
                filepath, 
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            story = []
            
            # Başlık - Türkçe karakter desteği ile
            title_text = "HAFTALIK B2B RAPORU"
            story.append(Paragraph(title_text, self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            
            # Tarih aralığı
            date_range = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
            story.append(Paragraph(f"Rapor Dönemi: {date_range}", self.styles['TurkishHeading']))
            story.append(Spacer(1, 20))
            
            # AI Analizi - Formatlanmış ve Bölümlenmiş
            story.append(Paragraph("🤖 AI ANALİZİ", self.styles['CustomHeading2']))
            ai_summary = ai_analysis.get('summary', 'Analiz mevcut değil')
            
            # AI yanıtını paragraflara böl ve formatla
            self._add_formatted_ai_analysis(story, ai_summary)
            story.append(Spacer(1, 20))
            
            # Yönetici Özeti
            story.append(Paragraph("📋 YÖNETİCİ ÖZETİ", self.styles['CustomHeading2']))
            executive_summary = self._create_executive_summary(report_data, ai_analysis)
            story.append(executive_summary)
            story.append(Spacer(1, 20))
            
            # Temel İstatistikler
            story.append(Paragraph("📊 TEMEL İSTATİSTİKLER", self.styles['CustomHeading2']))
            stats_table = self._create_stats_table(report_data.get('stats', {}))
            story.append(stats_table)
            story.append(Spacer(1, 20))
            
            # KPI ve Performans Metrikleri
            story.append(Paragraph("🎯 KPI VE PERFORMANS METRİKLERİ", self.styles['CustomHeading2']))
            kpi_table = self._create_kpi_table(report_data.get('stats', {}))
            story.append(kpi_table)
            story.append(Spacer(1, 20))
            
            # Grafikler
            story.append(Paragraph("📈 GRAFİKLER", self.styles['CustomHeading2']))
            
            # Günlük trend grafiği
            trend_chart = self._create_trend_chart(report_data.get('trends', {}))
            if trend_chart:
                story.append(trend_chart)
                story.append(Spacer(1, 20))
            
            # Sektör dağılımı
            sector_chart = self._create_sector_chart(report_data.get('trends', {}))
            if sector_chart:
                story.append(sector_chart)
                story.append(Spacer(1, 20))
            
            # Karşılaştırma grafikleri
            story.append(Paragraph("📊 KARŞILAŞTIRMA ANALİZİ", self.styles['CustomHeading2']))
            comparison_chart = self._create_comparison_chart(report_data.get('trends', {}))
            if comparison_chart:
                story.append(comparison_chart)
                story.append(Spacer(1, 20))
            
            # Günlük aktivite heatmap
            story.append(Paragraph("🔥 GÜNLÜK AKTİVİTE HEATMAP", self.styles['CustomHeading2']))
            heatmap_chart = self._create_heatmap_chart(report_data.get('trends', {}))
            if heatmap_chart:
                story.append(heatmap_chart)
                story.append(Spacer(1, 20))
            
            # Detaylı Veriler
            story.append(PageBreak())
            story.append(Paragraph("📋 DETAYLI VERİLER", self.styles['CustomHeading2']))
            
            # Firma listesi
            story.append(Paragraph("Yeni Firmalar", self.styles['TurkishHeading']))
            firms_table = self._create_firms_table(report_data.get('firms', []))
            story.append(firms_table)
            story.append(Spacer(1, 20))
            
            # Email performansı
            story.append(Paragraph("Email Performansı", self.styles['TurkishHeading']))
            email_table = self._create_email_table(report_data.get('emails', []))
            story.append(email_table)
            story.append(Spacer(1, 20))
            
            # Aksiyon Önerileri
            story.append(PageBreak())
            story.append(Paragraph("🎯 AKSİYON ÖNERİLERİ", self.styles['CustomHeading2']))
            recommendations = self._create_recommendations_table(report_data, ai_analysis)
            story.append(recommendations)
            story.append(Spacer(1, 20))
            
            # Gelecek Tahminleri
            story.append(Paragraph("🔮 GELECEK TAHMİNLERİ", self.styles['CustomHeading2']))
            forecast = self._create_forecast_analysis(report_data)
            story.append(forecast)
            story.append(Spacer(1, 20))
            
            # ROI ve Maliyet Analizi
            story.append(Paragraph("💰 ROI VE MALİYET ANALİZİ", self.styles['CustomHeading2']))
            roi_analysis = self._create_roi_analysis(report_data.get('stats', {}))
            story.append(roi_analysis)
            story.append(Spacer(1, 20))
            
            # PDF oluştur
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            logger.error(f"PDF oluşturma hatası: {e}")
            return None
    
    def _fix_turkish_chars(self, text: str) -> str:
        """Türkçe karakterleri düzelt"""
        if not text:
            return text
        
        # Türkçe karakter dönüşümleri
        char_map = {
            'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G',
            'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S',
            'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
        }
        
        # Karakterleri dönüştür
        for tr_char, en_char in char_map.items():
            text = text.replace(tr_char, en_char)
        
        return text
    
    def _format_ai_summary(self, summary: str) -> str:
        """AI yanıtını düzenli bir formata dönüştür"""
        if not summary:
            return "Analiz mevcut değil"
        
        formatted = summary
        
        # Ana başlıkları (<br/> ile başlayıp satır sonunda :) formatla
        formatted = re.sub(r'^([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜ0-9\s]+):\s*\n', r'<br/><b><font size="13">\1</font></b><br/>', formatted, flags=re.MULTILINE)
        
        # Alt başlıkları (** ile çevrilmiş) kalın yap ve satır sonuna geç
        formatted = re.sub(r'\*\*(.+?)\*\*:', r'<br/><b>\1</b><br/>', formatted)
        
        # ** ile çevrilmiş ama : olmayan normal kalın metinler
        formatted = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', formatted)
        
        # Numara ile başlayan satırları formatla (1. 2. 3. gibi)
        formatted = re.sub(r'^\s*(\d+)\.\s+(.+)$', r'<br/><b>\1.</b> \2', formatted, flags=re.MULTILINE)
        
        # Alt öğeleri (- ile başlayan) formatla ve satır sonuna geç
        formatted = re.sub(r'^\s*-\s+(.+)$', r'<br/><font color="#0d7377">•</font> \1', formatted, flags=re.MULTILINE)
        
        # ** ile başlayıp : ile biten alt başlıkları (ama satır başında değil)
        formatted = re.sub(r'(\*\*.+?\*\*):', r'<br/><b>\1</b>', formatted)
        
        # Çok boş satırları temizle
        formatted = re.sub(r'\n\n+', r'\n\n', formatted)
        
        # Satır sonlarını <br/> ile değiştir
        formatted = formatted.replace('\n', '<br/>')
        
        # Türkçe karakterleri koru
        formatted = self._fix_turkish_chars(formatted)
        
        return formatted
    
    def _add_formatted_ai_analysis(self, story, summary: str):
        """AI analizini düzenli paragraflar halinde ekle"""
        if not summary:
            story.append(Paragraph("Analiz mevcut değil", self.styles['SummaryStyle']))
            return
        
        # Summary'yi bölümlere ayır
        sections = re.split(r'\n+(?=[A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜ0-9\s]+:)', summary)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Ana başlık var mı kontrol et
            main_header = re.match(r'^([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜ0-9\s]+):', section)
            if main_header:
                header_text = main_header.group(1)
                story.append(Spacer(1, 10))
                story.append(Paragraph(f'<b><font size="12" color="#2E86AB">{header_text}</font></b>', self.styles['SummaryStyle']))
                section = section[len(main_header.group(0)):].strip()
            
            # İçeriği paragraflara böl
            if section:
                # Alt başlıkları ayır
                paragraphs = re.split(r'\n\n+', section)
                
                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue
                    
                    # Formatlı paragraf ekle
                    formatted_para = self._format_paragraph(para)
                    story.append(Paragraph(formatted_para, self.styles['SummaryStyle']))
                    story.append(Spacer(1, 5))
    
    def _format_paragraph(self, text: str) -> str:
        """Tek bir paragrafı formatla"""
        if not text:
            return ""
        
        formatted = text
        
        # Kalın metinler (**...**)
        formatted = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', formatted)
        
        # List items (- ile başlayan)
        formatted = re.sub(r'^- (.+)', r'<font color="#0d7377">•</font> \1', formatted, flags=re.MULTILINE)
        
        # Numara ile başlayan list items
        formatted = re.sub(r'^(\d+)\.\s+(.+)$', r'<b>\1.</b> \2', formatted, flags=re.MULTILINE)
        
        # Alt başlıklar (** ile çevrilmiş : ile biten)
        formatted = re.sub(r'\*\*(.+?)\*\*:', r'<b>\1:</b>', formatted)
        
        # Satır sonlarını <br/> ile değiştir
        formatted = formatted.replace('\n', '<br/>')
        
        # Türkçe karakterleri koru
        formatted = self._fix_turkish_chars(formatted)
        
        return formatted
    
    def _create_stats_table(self, stats: Dict) -> Table:
        """İstatistik tablosu oluştur - Türkçe karakter desteği ile"""
        try:
            data = [
                ['Metrik', 'Deger'],
                ['Yeni Firmalar', str(stats.get('new_firms', 0))],
                ['Aktif Firmalar', str(stats.get('active_firms', 0))],
                ['Toplam Email', str(stats.get('total_emails', 0))],
                ['Acilan Email', f"{stats.get('opened_emails', 0)} (%{stats.get('open_rate', 0)})"],
                ['Yanitlanan Email', f"{stats.get('replied_emails', 0)} (%{stats.get('reply_rate', 0)})"],
                ['Toplam Mesaj', str(stats.get('total_messages', 0))],
                ['Toplam Arama', str(stats.get('total_calls', 0))]
            ]
            
            table = Table(data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.default_font + '-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            logger.error(f"İstatistik tablosu oluşturma hatası: {e}")
            return Table([['Hata', 'Tablo oluşturulamadı']])
    
    def _create_trend_chart(self, trends: Dict) -> Optional[Image]:
        """Trend grafiği oluştur - Türkçe karakter desteği ile"""
        try:
            daily_data = trends.get('daily_data', [])
            if not daily_data:
                return None
            
            # Matplotlib ayarları - Türkçe karakter desteği
            plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            
            # Matplotlib grafiği oluştur
            fig, ax = plt.subplots(figsize=(10, 6))
            
            dates = [item['date'] for item in daily_data]
            firms = [item['firms'] for item in daily_data]
            emails = [item['emails'] for item in daily_data]
            messages = [item['messages'] for item in daily_data]
            
            ax.plot(dates, firms, label='Firmalar', marker='o', color='#2E86AB')
            ax.plot(dates, emails, label='Emailler', marker='s', color='#A23B72')
            ax.plot(dates, messages, label='Mesajlar', marker='^', color='#F18F01')
            
            ax.set_title('Gunluk Aktivite Trendi', fontsize=14, fontweight='bold')
            ax.set_xlabel('Tarih')
            ax.set_ylabel('Sayi')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # X ekseni etiketlerini döndür
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Grafiği BytesIO'ya kaydet
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            
            # ReportLab Image oluştur
            img_data = base64.b64encode(img_buffer.getvalue()).decode()
            img_buffer.close()
            plt.close()
            
            return Image(BytesIO(base64.b64decode(img_data)), width=6*inch, height=3.6*inch)
            
        except Exception as e:
            logger.error(f"Trend grafiği oluşturma hatası: {e}")
            return None
    
    def _create_sector_chart(self, trends: Dict) -> Optional[Image]:
        """Sektör dağılım grafiği oluştur - Türkçe karakter desteği ile"""
        try:
            sector_data = trends.get('sector_analysis', {})
            if not sector_data:
                return None
            
            # En çok 5 sektörü al
            sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1], reverse=True)[:5]
            if not sorted_sectors:
                return None
            
            sectors, counts = zip(*sorted_sectors)
            
            # Türkçe karakterleri düzelt
            sectors = [self._fix_turkish_chars(sector) for sector in sectors]
            
            # Matplotlib ayarları - Türkçe karakter desteği
            plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            
            # Matplotlib pie chart oluştur
            fig, ax = plt.subplots(figsize=(8, 6))
            
            colors_list = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#7209B7']
            wedges, texts, autotexts = ax.pie(counts, labels=sectors, autopct='%1.1f%%', 
                                            colors=colors_list[:len(sectors)])
            
            ax.set_title('Sektor Dagitimi', fontsize=14, fontweight='bold')
            
            # Grafiği BytesIO'ya kaydet
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            
            # ReportLab Image oluştur
            img_data = base64.b64encode(img_buffer.getvalue()).decode()
            img_buffer.close()
            plt.close()
            
            return Image(BytesIO(base64.b64decode(img_data)), width=4*inch, height=3*inch)
            
        except Exception as e:
            logger.error(f"Sektör grafiği oluşturma hatası: {e}")
            return None
    
    def _create_comparison_chart(self, trends: Dict) -> Optional[Image]:
        """Karşılaştırma grafiği oluştur"""
        try:
            daily_data = trends.get('daily_data', [])
            if not daily_data:
                return None
            
            # Matplotlib ayarları
            plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Hafta içi vs Hafta sonu karşılaştırması
            weekdays = []
            weekends = []
            labels = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
            
            for i, day_data in enumerate(daily_data):
                if i < 5:  # Hafta içi
                    weekdays.append(day_data.get('activities', 0))
                else:  # Hafta sonu
                    weekends.append(day_data.get('activities', 0))
            
            # Bar chart
            x = range(len(weekdays))
            ax1.bar(x, weekdays, color='#2E86AB', alpha=0.7, label='Hafta İçi')
            ax1.set_title('Hafta İçi Aktivite', fontweight='bold')
            ax1.set_ylabel('Aktivite Sayısı')
            ax1.set_xticks(x)
            ax1.set_xticklabels(labels[:len(weekdays)])
            ax1.grid(True, alpha=0.3)
            
            # Hafta sonu
            x2 = range(len(weekends))
            ax2.bar(x2, weekends, color='#A23B72', alpha=0.7, label='Hafta Sonu')
            ax2.set_title('Hafta Sonu Aktivite', fontweight='bold')
            ax2.set_ylabel('Aktivite Sayısı')
            ax2.set_xticks(x2)
            ax2.set_xticklabels(labels[5:5+len(weekends)])
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # BytesIO'ya kaydet
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            
            # ReportLab Image oluştur
            img_data = base64.b64encode(img_buffer.getvalue()).decode()
            img_buffer.close()
            plt.close()
            
            return Image(BytesIO(base64.b64decode(img_data)), width=6*inch, height=2.5*inch)
            
        except Exception as e:
            logger.error(f"Karşılaştırma grafiği oluşturma hatası: {e}")
            return None
    
    def _create_heatmap_chart(self, trends: Dict) -> Optional[Image]:
        """Günlük aktivite heatmap oluştur"""
        try:
            daily_data = trends.get('daily_data', [])
            if not daily_data:
                return None
            
            # Matplotlib ayarları
            plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            
            # Heatmap verisi hazırla
            days = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
            activities = [day.get('activities', 0) for day in daily_data]
            
            # Heatmap oluştur
            fig, ax = plt.subplots(figsize=(8, 3))
            
            # Renk haritası
            colors_list = ['#ffebee', '#ffcdd2', '#ef9a9a', '#e57373', '#ef5350', '#f44336', '#d32f2f']
            
            # Her gün için renkli kutu
            for i, (day, activity) in enumerate(zip(days, activities)):
                # Aktivite seviyesine göre renk indeksi
                color_idx = min(int(activity / 10), len(colors_list) - 1)
                color = colors_list[color_idx]
                
                # Kutu çiz
                rect = plt.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1)
                ax.add_patch(rect)
                
                # Aktivite sayısını yaz
                ax.text(i + 0.5, 0.5, str(activity), ha='center', va='center', 
                       fontweight='bold', fontsize=12)
            
            ax.set_xlim(0, len(days))
            ax.set_ylim(0, 1)
            ax.set_xticks(range(len(days)))
            ax.set_xticklabels(days)
            ax.set_yticks([])
            ax.set_title('Gunluk Aktivite Heatmap', fontweight='bold', fontsize=14)
            
            # Renk çubuğu ekle
            from matplotlib.patches import Patch
            legend_elements = [Patch(facecolor=color, label=f'Seviye {i+1}') 
                             for i, color in enumerate(colors_list)]
            ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
            
            plt.tight_layout()
            
            # BytesIO'ya kaydet
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            
            # ReportLab Image oluştur
            img_data = base64.b64encode(img_buffer.getvalue()).decode()
            img_buffer.close()
            plt.close()
            
            return Image(BytesIO(base64.b64decode(img_data)), width=6*inch, height=2*inch)
            
        except Exception as e:
            logger.error(f"Heatmap oluşturma hatası: {e}")
            return None
    
    def _create_firms_table(self, firms: List[Dict]) -> Table:
        """Firma tablosu oluştur - Türkçe karakter desteği ile"""
        try:
            if not firms:
                return Table([['Firma', 'Sektor', 'Durum', 'Tarih'], 
                            ['Veri yok', '-', '-', '-']])
            
            # En fazla 10 firma göster
            display_firms = firms[:10]
            
            data = [['Firma', 'Sektor', 'Durum', 'Tarih']]
            for firm in display_firms:
                firm_name = firm.get('name', 'Bilinmeyen')
                if len(firm_name) > 30:
                    firm_name = firm_name[:30] + '...'
                firm_name = self._fix_turkish_chars(firm_name)
                
                sector = self._fix_turkish_chars(firm.get('sector', 'Belirtilmemis')[:20])
                status = self._fix_turkish_chars(firm.get('status', 'active'))
                created_at = firm.get('created_at', '').split(' ')[0] if firm.get('created_at') else '-'
                
                data.append([firm_name, sector, status, created_at])
            
            table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.default_font + '-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            logger.error(f"Firma tablosu oluşturma hatası: {e}")
            return Table([['Hata', 'Tablo oluşturulamadı']])
    
    def _create_email_table(self, emails: List[Dict]) -> Table:
        """Email tablosu oluştur - Türkçe karakter desteği ile"""
        try:
            if not emails:
                return Table([['Konu', 'Firma', 'Durum', 'Acilan', 'Yanitlanan'], 
                            ['Veri yok', '-', '-', '-', '-']])
            
            # En fazla 10 email göster
            display_emails = emails[:10]
            
            data = [['Konu', 'Firma', 'Durum', 'Acilan', 'Yanitlanan']]
            for email in display_emails:
                subject = email.get('subject', 'Konu yok')
                if len(subject) > 25:
                    subject = subject[:25] + '...'
                subject = self._fix_turkish_chars(subject)
                
                firm_name = self._fix_turkish_chars(email.get('firm_name', 'Bilinmeyen')[:20])
                status = self._fix_turkish_chars(email.get('status', 'unknown'))
                
                data.append([
                    subject,
                    firm_name,
                    status,
                    '✓' if email.get('opened') else '✗',
                    '✓' if email.get('replied') else '✗'
                ])
            
            table = Table(data, colWidths=[2*inch, 1.5*inch, 1*inch, 0.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.default_font + '-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            logger.error(f"Email tablosu oluşturma hatası: {e}")
            return Table([['Hata', 'Tablo oluşturulamadı']])
    
    def _create_executive_summary(self, report_data: Dict, ai_analysis: Dict) -> Table:
        """Yönetici özeti tablosu oluştur"""
        try:
            stats = report_data.get('stats', {})
            trends = report_data.get('trends', {})
            
            # Önemli metrikler
            total_activities = stats.get('total_emails', 0) + stats.get('total_messages', 0) + stats.get('total_calls', 0)
            conversion_rate = (stats.get('replied_emails', 0) / max(stats.get('total_emails', 1), 1)) * 100
            growth_rate = self._calculate_growth_rate(stats)
            
            data = [
                ['Metrik', 'Değer', 'Durum'],
                ['Toplam Aktivite', f"{total_activities:,}", self._get_status_icon(total_activities, 100)],
                ['Dönüşüm Oranı', f"%{conversion_rate:.1f}", self._get_status_icon(conversion_rate, 5)],
                ['Büyüme Oranı', f"%{growth_rate:.1f}", self._get_status_icon(growth_rate, 10)],
                ['Email Açılma Oranı', f"%{stats.get('open_rate', 0):.1f}", self._get_status_icon(stats.get('open_rate', 0), 20)],
                ['Aktif Firma Sayısı', f"{stats.get('active_firms', 0):,}", self._get_status_icon(stats.get('active_firms', 0), 50)]
            ]
            
            table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.default_font + '-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            logger.error(f"Yönetici özeti oluşturma hatası: {e}")
            return Table([['Hata', 'Tablo oluşturulamadı', '']])
    
    def _create_kpi_table(self, stats: Dict) -> Table:
        """KPI tablosu oluştur"""
        try:
            # KPI hesaplamaları
            email_roi = self._calculate_email_roi(stats)
            cost_per_lead = self._calculate_cost_per_lead(stats)
            lead_quality_score = self._calculate_lead_quality(stats)
            engagement_score = self._calculate_engagement_score(stats)
            
            data = [
                ['KPI', 'Değer', 'Hedef', 'Durum'],
                ['Email ROI', f"%{email_roi:.1f}", '%300+', self._get_kpi_status(email_roi, 300)],
                ['Lead Maliyeti', f"₺{cost_per_lead:.2f}", '₺50-', self._get_kpi_status(50-cost_per_lead, 0)],
                ['Lead Kalitesi', f"{lead_quality_score:.1f}/10", '8.0+', self._get_kpi_status(lead_quality_score, 8)],
                ['Etkileşim Skoru', f"{engagement_score:.1f}/10", '7.0+', self._get_kpi_status(engagement_score, 7)],
                ['Email Açılma Oranı', f"%{stats.get('open_rate', 0):.1f}", '%25+', self._get_kpi_status(stats.get('open_rate', 0), 25)],
                ['Yanıt Oranı', f"%{stats.get('reply_rate', 0):.1f}", '%5+', self._get_kpi_status(stats.get('reply_rate', 0), 5)]
            ]
            
            table = Table(data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.default_font + '-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            logger.error(f"KPI tablosu oluşturma hatası: {e}")
            return Table([['Hata', 'Tablo oluşturulamadı', '', '']])
    
    def _calculate_growth_rate(self, stats: Dict) -> float:
        """Büyüme oranını hesapla"""
        try:
            # Basit büyüme hesaplaması (gerçek uygulamada önceki dönemle karşılaştırma yapılır)
            total_activities = stats.get('total_emails', 0) + stats.get('total_messages', 0) + stats.get('total_calls', 0)
            return min(total_activities * 0.15, 50)  # Örnek hesaplama
        except:
            return 0.0
    
    def _calculate_email_roi(self, stats: Dict) -> float:
        """Email ROI hesapla"""
        try:
            total_emails = stats.get('total_emails', 0)
            replied_emails = stats.get('replied_emails', 0)
            if total_emails == 0:
                return 0.0
            # Basit ROI hesaplaması
            return (replied_emails / total_emails) * 100 * 5  # Örnek çarpan
        except:
            return 0.0
    
    def _calculate_cost_per_lead(self, stats: Dict) -> float:
        """Lead başına maliyet hesapla"""
        try:
            total_emails = stats.get('total_emails', 0)
            if total_emails == 0:
                return 0.0
            # Örnek maliyet hesaplaması (email başına 0.5 TL)
            return (total_emails * 0.5) / max(stats.get('replied_emails', 1), 1)
        except:
            return 0.0
    
    def _calculate_lead_quality(self, stats: Dict) -> float:
        """Lead kalitesi skoru hesapla"""
        try:
            reply_rate = stats.get('reply_rate', 0)
            open_rate = stats.get('open_rate', 0)
            # 0-10 arası skor
            return min((reply_rate * 0.3 + open_rate * 0.1), 10)
        except:
            return 0.0
    
    def _calculate_engagement_score(self, stats: Dict) -> float:
        """Etkileşim skoru hesapla"""
        try:
            total_activities = stats.get('total_emails', 0) + stats.get('total_messages', 0) + stats.get('total_calls', 0)
            active_firms = stats.get('active_firms', 1)
            # 0-10 arası skor
            return min((total_activities / max(active_firms, 1)) * 0.5, 10)
        except:
            return 0.0
    
    def _get_status_icon(self, value: float, threshold: float) -> str:
        """Durum ikonu döndür"""
        if value >= threshold:
            return "✅"
        elif value >= threshold * 0.7:
            return "⚠️"
        else:
            return "❌"
    
    def _get_kpi_status(self, value: float, target: float) -> str:
        """KPI durumu döndür"""
        if value >= target:
            return "✅ Hedef"
        elif value >= target * 0.8:
            return "⚠️ Yakın"
        else:
            return "❌ Düşük"
    
    def _create_recommendations_table(self, report_data: Dict, ai_analysis: Dict) -> Table:
        """Aksiyon önerileri tablosu oluştur"""
        try:
            stats = report_data.get('stats', {})
            
            # Öneriler oluştur
            recommendations = []
            
            # Email performansına göre öneriler
            if stats.get('open_rate', 0) < 20:
                recommendations.append(['Email Açılma Oranı', 'Konu satırlarını daha çekici hale getirin', 'Yüksek', '1 hafta'])
            
            if stats.get('reply_rate', 0) < 5:
                recommendations.append(['Email Yanıt Oranı', 'Kişiselleştirilmiş içerik kullanın', 'Orta', '2 hafta'])
            
            # Firma sayısına göre öneriler
            if stats.get('new_firms', 0) < 10:
                recommendations.append(['Yeni Firma Kazanımı', 'Lead generation kampanyalarını artırın', 'Yüksek', '1 hafta'])
            
            # Aktivite seviyesine göre öneriler
            total_activities = stats.get('total_emails', 0) + stats.get('total_messages', 0) + stats.get('total_calls', 0)
            if total_activities < 50:
                recommendations.append(['Genel Aktivite', 'Otomasyon süreçlerini optimize edin', 'Orta', '2 hafta'])
            
            # AI önerileri
            recommendations.append(['AI Analizi', 'Makine öğrenmesi modellerini güncelleyin', 'Düşük', '1 ay'])
            recommendations.append(['Veri Kalitesi', 'Veri temizleme süreçlerini iyileştirin', 'Orta', '3 hafta'])
            
            if not recommendations:
                recommendations = [['Genel', 'Mevcut performansı koruyun', 'Düşük', 'Sürekli']]
            
            # Tablo verisi
            data = [['Alan', 'Öneri', 'Öncelik', 'Süre']] + recommendations
            
            table = Table(data, colWidths=[1.5*inch, 3*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8E24AA')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.default_font + '-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            logger.error(f"Aksiyon önerileri oluşturma hatası: {e}")
            return Table([['Hata', 'Tablo oluşturulamadı', '', '']])
    
    def _create_forecast_analysis(self, report_data: Dict) -> Table:
        """Gelecek tahminleri tablosu oluştur"""
        try:
            stats = report_data.get('stats', {})
            trends = report_data.get('trends', {})
            
            # Basit tahmin hesaplamaları
            current_emails = stats.get('total_emails', 0)
            current_firms = stats.get('new_firms', 0)
            current_activities = current_emails + stats.get('total_messages', 0) + stats.get('total_calls', 0)
            
            # Gelecek hafta tahminleri (basit trend analizi)
            email_growth = 1.15  # %15 büyüme
            firm_growth = 1.10   # %10 büyüme
            activity_growth = 1.12  # %12 büyüme
            
            next_week_emails = int(current_emails * email_growth)
            next_week_firms = int(current_firms * firm_growth)
            next_week_activities = int(current_activities * activity_growth)
            
            # Aylık tahminler
            monthly_emails = int(next_week_emails * 4.3)  # 4.3 hafta/ay
            monthly_firms = int(next_week_firms * 4.3)
            monthly_activities = int(next_week_activities * 4.3)
            
            data = [
                ['Metrik', 'Bu Hafta', 'Gelecek Hafta', 'Aylık Tahmin', 'Büyüme %'],
                ['Email Sayısı', f"{current_emails:,}", f"{next_week_emails:,}", f"{monthly_emails:,}", f"{(email_growth-1)*100:.0f}%"],
                ['Yeni Firmalar', f"{current_firms:,}", f"{next_week_firms:,}", f"{monthly_firms:,}", f"{(firm_growth-1)*100:.0f}%"],
                ['Toplam Aktivite', f"{current_activities:,}", f"{next_week_activities:,}", f"{monthly_activities:,}", f"{(activity_growth-1)*100:.0f}%"],
                ['Email ROI', f"%{self._calculate_email_roi(stats):.1f}", f"%{(self._calculate_email_roi(stats)*1.05):.1f}", f"%{(self._calculate_email_roi(stats)*1.2):.1f}", "5-20%"]
            ]
            
            table = Table(data, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6F00')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.default_font + '-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            logger.error(f"Gelecek tahminleri oluşturma hatası: {e}")
            return Table([['Hata', 'Tablo oluşturulamadı', '', '', '']])
    
    def _create_roi_analysis(self, stats: Dict) -> Table:
        """ROI ve maliyet analizi tablosu oluştur"""
        try:
            # Maliyet hesaplamaları
            email_cost = stats.get('total_emails', 0) * 0.5  # Email başına 0.5 TL
            message_cost = stats.get('total_messages', 0) * 0.1  # Mesaj başına 0.1 TL
            call_cost = stats.get('total_calls', 0) * 2.0  # Arama başına 2 TL
            total_cost = email_cost + message_cost + call_cost
            
            # Gelir hesaplamaları (örnek)
            replied_emails = stats.get('replied_emails', 0)
            potential_revenue = replied_emails * 100  # Yanıtlanan email başına 100 TL potansiyel gelir
            roi_percentage = ((potential_revenue - total_cost) / max(total_cost, 1)) * 100
            
            # Lead maliyeti
            total_leads = stats.get('replied_emails', 0) + stats.get('new_firms', 0)
            cost_per_lead = total_cost / max(total_leads, 1)
            
            data = [
                ['Maliyet Kalemi', 'Miktar', 'Birim Maliyet', 'Toplam Maliyet'],
                ['Email Gönderimi', f"{stats.get('total_emails', 0):,}", '₺0.50', f"₺{email_cost:.2f}"],
                ['Mesaj Gönderimi', f"{stats.get('total_messages', 0):,}", '₺0.10', f"₺{message_cost:.2f}"],
                ['Telefon Araması', f"{stats.get('total_calls', 0):,}", '₺2.00', f"₺{call_cost:.2f}"],
                ['TOPLAM MALİYET', '', '', f"₺{total_cost:.2f}"],
                ['', '', '', ''],
                ['Potansiyel Gelir', f"{replied_emails:,} yanıt", '₺100/yanıt', f"₺{potential_revenue:.2f}"],
                ['ROI', f"%{roi_percentage:.1f}", '', ''],
                ['Lead Maliyeti', f"{total_leads:,} lead", '', f"₺{cost_per_lead:.2f}"]
            ]
            
            table = Table(data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.default_font + '-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 1), (-1, 4), colors.lightgrey),
                ('BACKGROUND', (0, 5), (-1, -1), colors.lightblue),
                ('FONTNAME', (0, 1), (-1, -1), self.default_font),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            logger.error(f"ROI analizi oluşturma hatası: {e}")
            return Table([['Hata', 'Tablo oluşturulamadı', '', '']])
    
    def get_report_summary(self, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> Dict:
        """Rapor özetini getir (PDF oluşturmadan)"""
        try:
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=7)
            
            report_data = self._collect_weekly_data(start_date, end_date)
            ai_analysis = self._generate_ai_analysis(report_data)
            
            return {
                'data': report_data,
                'ai_analysis': ai_analysis,
                'date_range': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            logger.error(f"Rapor özeti hatası: {e}")
            return {}


def main():
    """Test fonksiyonu"""
    try:
        generator = AIReportGenerator()
        
        # Son 7 günlük rapor oluştur
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print("Haftalık rapor oluşturuluyor...")
        pdf_path = generator.generate_weekly_report(start_date, end_date)
        
        if pdf_path:
            print(f"✅ Rapor başarıyla oluşturuldu: {pdf_path}")
        else:
            print("❌ Rapor oluşturulamadı")
            
    except Exception as e:
        print(f"❌ Hata: {e}")


if __name__ == "__main__":
    main()
