#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gelişmiş AI Destekli Web Scraper - B2B Automation Pro
- Firma tipi tespiti (Üretici/Tedarikçi/Satıcı/Distribütör)
- Gelişmiş web scraping (JavaScript rendering, API detection)
- AI ile ürün/hizmet analizi ve kategorilendirme
- Firma güvenilirlik ve kalite skoru
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    print("⚠️ undetected-chromedriver yüklü değil, standart driver kullanılacak")

import re
import time
import random
from typing import Dict, List, Tuple, Optional, Any
import openai
from urllib.parse import urlparse, urljoin, parse_qs
import validators
import requests
import base64
import json
from datetime import datetime
import hashlib
from collections import Counter, defaultdict

try:
    from PIL import Image
    from io import BytesIO
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from ai_vision_analyzer import AIVisionAnalyzer, EcommerceImageExtractor
    AI_VISION_AVAILABLE = True
except ImportError:
    AI_VISION_AVAILABLE = False
    print("⚠️ AI Vision Analyzer yüklü değil")


class EnhancedWebScraper:
    """AI destekli gelişmiş web scraping ve firma analizi sistemi"""
    
    def __init__(self, use_proxy: bool = False, use_ai_vision: bool = True, openai_api_key: str = None):
        self.use_proxy = use_proxy
        self.use_ai_vision = use_ai_vision
        self.openai_api_key = openai_api_key
        
        if openai_api_key:
            openai.api_key = openai_api_key
        
        self.setup_company_type_analyzers()
        self.setup_quality_indicators()
        self.setup_user_agents()
        
        # AI Vision Analyzer
        if use_ai_vision and openai_api_key and AI_VISION_AVAILABLE:
            self.vision_analyzer = AIVisionAnalyzer(api_key=openai_api_key)
            print("✅ AI Vision Analyzer aktif")
        else:
            self.vision_analyzer = None
            if use_ai_vision:
                print("⚠️ AI Vision Analyzer devre dışı (API key gerekli)")
        
    def setup_company_type_analyzers(self):
        """Firma tipi tespit sistemi - ÜRETİCİ/TEDARİKÇİ/SATICI/DİSTRİBÜTÖR"""
        
        # Üretici (Manufacturer) göstergeleri
        self.manufacturer_indicators = {
            'keywords': [
                'üretici', 'üretim', 'imalat', 'fabrika', 'manufacturer', 'factory',
                'production', 'manufacturing', 'producer', 'maker', 'imalatçı',
                'üretiyoruz', 'imal ediyoruz', 'üretmekteyiz', 'fabrikamız',
                'üretim tesisimiz', 'imalathanemiz', 'atölyemiz', 'we manufacture',
                'we produce', 'our factory', 'production facility', 'manufacturing plant',
                'makine parkımız', 'üretim hattı', 'production line', 'assembly line',
                'kalite kontrol', 'quality control', 'ar-ge', 'r&d', 'araştırma geliştirme',
                'patent', 'tasarım', 'design', 'prototip', 'prototype', 'mühendislik'
            ],
            'page_indicators': [
                'üretim', 'production', 'fabrika', 'factory', 'imalat', 'manufacturing',
                'tesislerimiz', 'facilities', 'makine-parkuru', 'machinery', 'kalite',
                'quality', 'sertifikalar', 'certificates', 'ar-ge', 'r&d'
            ],
            'negative_keywords': [
                'distribütör', 'bayi', 'dealer', 'reseller', 'satış temsilcisi',
                'yetkili satıcı', 'authorized dealer', 'ithalatçı', 'importer'
            ],
            'weight': 1.0
        }
        
        # Tedarikçi (Supplier) göstergeleri
        self.supplier_indicators = {
            'keywords': [
                'tedarikçi', 'tedarik', 'supplier', 'supply', 'toptan', 'wholesale',
                'toptan satış', 'wholesale supplier', 'tedarik ediyoruz', 'we supply',
                'tedarikçiniz', 'your supplier', 'tedarik zinciri', 'supply chain',
                'stok', 'inventory', 'depo', 'warehouse', 'lojistik', 'logistics',
                'dağıtım', 'distribution', 'kargo', 'shipping', 'teslimat', 'delivery',
                'minimum sipariş', 'minimum order', 'moq', 'bulk order', 'toplu sipariş',
                'b2b satış', 'b2b sales', 'kurumsal satış', 'corporate sales',
                'fiyat listesi', 'price list', 'katalog', 'catalog'
            ],
            'page_indicators': [
                'tedarik', 'supply', 'toptan', 'wholesale', 'stok', 'inventory',
                'fiyat-listesi', 'price-list', 'katalog', 'catalog', 'urunler', 'products'
            ],
            'negative_keywords': [],
            'weight': 0.9
        }
        
        # Distribütör (Distributor) göstergeleri
        self.distributor_indicators = {
            'keywords': [
                'distribütör', 'distributor', 'dağıtıcı', 'yetkili distribütör',
                'authorized distributor', 'resmi distribütör', 'official distributor',
                'bölge distribütörü', 'regional distributor', 'ana distribütör',
                'main distributor', 'tek distribütör', 'exclusive distributor',
                'dağıtım ağı', 'distribution network', 'bayilik', 'dealership',
                'franchise', 'franchisor', 'bayi ağı', 'dealer network',
                'yetkili satış', 'authorized sales', 'marka temsilcisi', 'brand representative'
            ],
            'page_indicators': [
                'distribütor', 'distributor', 'bayilik', 'dealership', 'franchise',
                'bayi-ol', 'become-dealer', 'bayilerimiz', 'our-dealers', 'satis-aglari'
            ],
            'negative_keywords': [
                'üretici', 'manufacturer', 'imalatçı', 'producer'
            ],
            'weight': 0.85
        }
        
        # Satıcı (Retailer/Seller) göstergeleri
        self.retailer_indicators = {
            'keywords': [
                'satıcı', 'satış', 'mağaza', 'store', 'shop', 'retailer', 'seller',
                'perakende', 'retail', 'satış noktası', 'sales point', 'showroom',
                'satış mağazası', 'sales store', 'online mağaza', 'online store',
                'e-ticaret', 'e-commerce', 'alışveriş', 'shopping', 'sepet', 'cart',
                'ödeme', 'payment', 'kargo', 'shipping', 'iade', 'return',
                'müşteri hizmetleri', 'customer service', 'sipariş', 'order',
                'hemen al', 'buy now', 'satın al', 'purchase', 'fiyat', 'price'
            ],
            'page_indicators': [
                'magaza', 'store', 'shop', 'alisveris', 'shopping', 'sepet', 'cart',
                'urunler', 'products', 'kampanya', 'campaign', 'indirim', 'discount'
            ],
            'negative_keywords': [
                'üretici', 'manufacturer', 'fabrika', 'factory', 'toptan', 'wholesale'
            ],
            'weight': 0.8
        }
        
        # E-ticaret göstergeleri
        self.ecommerce_indicators = {
            'keywords': [
                'sepete ekle', 'add to cart', 'satın al', 'buy now', 'checkout',
                'ödeme', 'payment', 'kredi kartı', 'credit card', 'online ödeme',
                'online payment', 'güvenli alışveriş', 'secure shopping', 'ssl',
                'kargo ücretsiz', 'free shipping', 'hızlı teslimat', 'fast delivery'
            ],
            'technologies': [
                'woocommerce', 'shopify', 'magento', 'opencart', 'prestashop',
                'ticimax', 'ideasoft', 'n11', 'hepsiburada', 'trendyol'
            ]
        }
        
    def setup_quality_indicators(self):
        """Firma kalite ve güvenilirlik göstergeleri"""
        
        self.quality_indicators = {
            'certificates': {
                'keywords': ['iso', 'ce', 'tse', 'haccp', 'fda', 'gmp', 'ohsas', 
                           'iso 9001', 'iso 14001', 'iso 27001', 'iso 45001',
                           'sertifika', 'certificate', 'belge', 'certification',
                           'akreditasyon', 'accreditation'],
                'weight': 15
            },
            'awards': {
                'keywords': ['ödül', 'award', 'başarı', 'achievement', 'kazanan', 'winner',
                           'birinci', 'first place', 'en iyi', 'best', 'lider', 'leader'],
                'weight': 10
            },
            'references': {
                'keywords': ['referans', 'reference', 'müşterilerimiz', 'our clients',
                           'projelerimiz', 'our projects', 'çalıştığımız firmalar',
                           'portfolio', 'portföy', 'case study', 'başarı hikayeleri'],
                'weight': 12
            },
            'experience': {
                'keywords': ['yıllık tecrübe', 'years of experience', 'yıldır', 'since',
                           'kuruluş', 'established', 'founded', 'deneyim', 'experience',
                           'uzman', 'expert', 'profesyonel', 'professional'],
                'weight': 8
            },
            'technology': {
                'keywords': ['teknoloji', 'technology', 'dijital', 'digital', 'otomasyon',
                           'automation', 'yazılım', 'software', 'sistem', 'system',
                           'cnc', 'robot', 'akıllı', 'smart', 'endüstri 4.0', 'industry 4.0'],
                'weight': 10
            },
            'export': {
                'keywords': ['ihracat', 'export', 'uluslararası', 'international',
                           'global', 'dünya', 'world', 'ülke', 'country', 'countries',
                           'yurtdışı', 'abroad', 'overseas'],
                'weight': 12
            },
            'capacity': {
                'keywords': ['kapasite', 'capacity', 'üretim kapasitesi', 'production capacity',
                           'metrekare', 'square meter', 'm2', 'çalışan', 'employee',
                           'personel', 'staff', 'ekip', 'team'],
                'weight': 8
            },
            'social_proof': {
                'keywords': ['müşteri yorumu', 'customer review', 'testimonial', 'değerlendirme',
                           'rating', 'yıldız', 'star', 'memnuniyet', 'satisfaction'],
                'weight': 10
            }
        }
        
        # Web sitesi teknik kalite göstergeleri
        self.technical_quality_indicators = {
            'ssl': {'weight': 10, 'description': 'SSL Sertifikası'},
            'responsive': {'weight': 8, 'description': 'Mobil Uyumlu'},
            'fast_loading': {'weight': 7, 'description': 'Hızlı Yüklenme'},
            'modern_design': {'weight': 6, 'description': 'Modern Tasarım'},
            'seo_optimized': {'weight': 8, 'description': 'SEO Optimizasyonu'},
            'social_media_integration': {'weight': 5, 'description': 'Sosyal Medya Entegrasyonu'},
            'contact_forms': {'weight': 7, 'description': 'İletişim Formları'},
            'live_chat': {'weight': 6, 'description': 'Canlı Destek'},
            'multilingual': {'weight': 5, 'description': 'Çok Dilli'},
            'blog_content': {'weight': 4, 'description': 'Blog/İçerik'},
            'video_content': {'weight': 5, 'description': 'Video İçerik'},
            'api_integration': {'weight': 8, 'description': 'API Entegrasyonu'}
        }
        
    def setup_user_agents(self):
        """User agent listesi"""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
    def create_driver(self):
        """Selenium driver oluştur - Anti-detection ile"""
        user_agent = random.choice(self.user_agents)
        
        if UC_AVAILABLE:
            try:
                options = uc.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument(f'--user-agent={user_agent}')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--disable-notifications')
                options.add_argument('--start-maximized')
                
                driver = uc.Chrome(options=options, use_subprocess=True)
                
                # Anti-detection script
                driver.execute_script('''
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']});
                ''')
                
                return driver
                
            except Exception as e:
                print(f"⚠️ Undetected ChromeDriver hatası: {e}, standart driver kullanılıyor")
        
        # Standart ChromeDriver
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-notifications')
        options.add_argument('--start-maximized')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        
        # Anti-detection
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            '''
        })
        
        return driver
    
    def analyze_company_type(self, url: str, soup: BeautifulSoup, page_text: str, 
                            driver=None) -> Dict[str, Any]:
        """
        Firma tipini AI destekli analiz et
        Returns: {
            'primary_type': 'manufacturer|supplier|distributor|retailer',
            'secondary_types': [...],
            'confidence': 0-100,
            'indicators': {...},
            'ai_analysis': {...}
        }
        """
        print("🔍 Firma tipi analizi başlatılıyor...")
        
        results = {
            'manufacturer': 0,
            'supplier': 0,
            'distributor': 0,
            'retailer': 0,
            'ecommerce': 0
        }
        
        indicators_found = {
            'manufacturer': [],
            'supplier': [],
            'distributor': [],
            'retailer': [],
            'ecommerce': []
        }
        
        # 1. Keyword analizi
        page_text_lower = page_text.lower()
        
        # Üretici analizi
        for keyword in self.manufacturer_indicators['keywords']:
            if keyword.lower() in page_text_lower:
                results['manufacturer'] += 1
                indicators_found['manufacturer'].append(keyword)
        
        # Negatif keyword kontrolü
        for neg_keyword in self.manufacturer_indicators['negative_keywords']:
            if neg_keyword.lower() in page_text_lower:
                results['manufacturer'] -= 0.5
        
        # Tedarikçi analizi
        for keyword in self.supplier_indicators['keywords']:
            if keyword.lower() in page_text_lower:
                results['supplier'] += 1
                indicators_found['supplier'].append(keyword)
        
        # Distribütör analizi
        for keyword in self.distributor_indicators['keywords']:
            if keyword.lower() in page_text_lower:
                results['distributor'] += 1
                indicators_found['distributor'].append(keyword)
        
        # Negatif keyword kontrolü
        for neg_keyword in self.distributor_indicators['negative_keywords']:
            if neg_keyword.lower() in page_text_lower:
                results['distributor'] -= 0.5
        
        # Satıcı analizi
        for keyword in self.retailer_indicators['keywords']:
            if keyword.lower() in page_text_lower:
                results['retailer'] += 1
                indicators_found['retailer'].append(keyword)
        
        # Negatif keyword kontrolü
        for neg_keyword in self.retailer_indicators['negative_keywords']:
            if neg_keyword.lower() in page_text_lower:
                results['retailer'] -= 0.5
        
        # E-ticaret analizi
        for keyword in self.ecommerce_indicators['keywords']:
            if keyword.lower() in page_text_lower:
                results['ecommerce'] += 1
                indicators_found['ecommerce'].append(keyword)
        
        # 2. Sayfa yapısı analizi
        if driver:
            # E-ticaret öğeleri kontrolü
            try:
                cart_elements = driver.find_elements(By.CSS_SELECTOR, 
                    '[class*="cart"], [id*="cart"], [class*="sepet"], [id*="sepet"]')
                if cart_elements:
                    results['ecommerce'] += 5
                    results['retailer'] += 3
                    indicators_found['ecommerce'].append('Sepet öğesi bulundu')
                
                # Ürün listesi kontrolü
                product_elements = driver.find_elements(By.CSS_SELECTOR,
                    '[class*="product"], [class*="urun"], [class*="item"]')
                if len(product_elements) > 10:
                    results['retailer'] += 2
                    indicators_found['retailer'].append(f'{len(product_elements)} ürün öğesi bulundu')
                
                # Fiyat öğeleri kontrolü
                price_elements = driver.find_elements(By.CSS_SELECTOR,
                    '[class*="price"], [class*="fiyat"], [class*="amount"]')
                if len(price_elements) > 5:
                    results['retailer'] += 2
                    results['ecommerce'] += 1
                    indicators_found['retailer'].append(f'{len(price_elements)} fiyat öğesi bulundu')
                
            except Exception as e:
                print(f"⚠️ Sayfa öğeleri analizi hatası: {e}")
        
        # 3. URL ve sayfa başlıkları analizi
        all_links = soup.find_all('a', href=True)
        link_texts = [link.get_text().lower() for link in all_links]
        link_hrefs = [link['href'].lower() for link in all_links]
        
        # Üretici sayfaları
        for indicator in self.manufacturer_indicators['page_indicators']:
            for href in link_hrefs:
                if indicator in href:
                    results['manufacturer'] += 2
                    indicators_found['manufacturer'].append(f'Sayfa: {indicator}')
                    break
        
        # Tedarikçi sayfaları
        for indicator in self.supplier_indicators['page_indicators']:
            for href in link_hrefs:
                if indicator in href:
                    results['supplier'] += 2
                    indicators_found['supplier'].append(f'Sayfa: {indicator}')
                    break
        
        # 4. Teknoloji tespiti
        page_source = str(soup)
        for tech in self.ecommerce_indicators['technologies']:
            if tech.lower() in page_source.lower():
                results['ecommerce'] += 3
                results['retailer'] += 2
                indicators_found['ecommerce'].append(f'Teknoloji: {tech}')
        
        # 5. Meta tag analizi
        meta_description = soup.find('meta', {'name': 'description'})
        if meta_description:
            desc_content = meta_description.get('content', '').lower()
            
            if any(kw in desc_content for kw in ['üretici', 'manufacturer', 'imalat', 'fabrika']):
                results['manufacturer'] += 3
                indicators_found['manufacturer'].append('Meta description: üretici göstergesi')
            
            if any(kw in desc_content for kw in ['tedarikçi', 'supplier', 'toptan']):
                results['supplier'] += 3
                indicators_found['supplier'].append('Meta description: tedarikçi göstergesi')
        
        # 6. Skorları normalize et
        max_score = max(results.values()) if max(results.values()) > 0 else 1
        normalized_results = {k: (v / max_score * 100) for k, v in results.items()}
        
        # Primary type belirle
        primary_type = max(normalized_results, key=normalized_results.get)
        confidence = normalized_results[primary_type]
        
        # Secondary types (confidence > 30)
        secondary_types = [k for k, v in normalized_results.items() 
                          if v > 30 and k != primary_type]
        secondary_types.sort(key=lambda x: normalized_results[x], reverse=True)
        
        # Türkçe isimler
        type_names = {
            'manufacturer': 'Üretici',
            'supplier': 'Tedarikçi',
            'distributor': 'Distribütör',
            'retailer': 'Satıcı',
            'ecommerce': 'E-ticaret'
        }
        
        analysis_result = {
            'primary_type': primary_type,
            'primary_type_tr': type_names.get(primary_type, primary_type),
            'secondary_types': secondary_types,
            'secondary_types_tr': [type_names.get(t, t) for t in secondary_types],
            'confidence': round(confidence, 2),
            'scores': {k: round(v, 2) for k, v in normalized_results.items()},
            'indicators': indicators_found,
            'raw_scores': results
        }
        
        # 7. AI ile doğrulama (opsiyonel)
        if self.openai_api_key and confidence < 70:
            try:
                ai_analysis = self.ai_verify_company_type(page_text[:3000], url)
                analysis_result['ai_verification'] = ai_analysis
                
                # AI sonucunu skorlara ekle
                if ai_analysis.get('type'):
                    ai_type = ai_analysis['type'].lower()
                    if ai_type in results:
                        analysis_result['confidence'] = min(
                            (confidence + ai_analysis.get('confidence', 0)) / 2,
                            100
                        )
            except Exception as e:
                print(f"⚠️ AI doğrulama hatası: {e}")
        
        print(f"✅ Firma tipi: {analysis_result['primary_type_tr']} (Güven: {analysis_result['confidence']:.1f}%)")
        if secondary_types:
            print(f"   Ek tipler: {', '.join(analysis_result['secondary_types_tr'])}")
        
        return analysis_result
    
    def ai_verify_company_type(self, page_text: str, url: str) -> Dict:
        """AI ile firma tipini doğrula"""
        try:
            prompt = f"""Aşağıdaki web sitesi içeriğini analiz ederek firmanın tipini belirle:

URL: {url}

İçerik (ilk 3000 karakter):
{page_text}

Firma tipi seçenekleri:
1. manufacturer (üretici/imalatçı)
2. supplier (tedarikçi/toptan satıcı)
3. distributor (distribütör/bayilik)
4. retailer (perakende satıcı)
5. ecommerce (e-ticaret)

JSON formatında cevap ver:
{{
    "type": "seçilen tip",
    "confidence": 0-100 arası güven skoru,
    "reasoning": "kısa açıklama"
}}"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir B2B firma analiz uzmanısın. Firma tiplerini doğru tespit edersin."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"⚠️ AI doğrulama hatası: {e}")
            return {}
    
    def calculate_quality_score(self, url: str, soup: BeautifulSoup, 
                               page_text: str, driver=None) -> Dict[str, Any]:
        """
        Firma web sitesi kalite ve güvenilirlik skoru hesapla
        Returns: {
            'total_score': 0-100,
            'category_scores': {...},
            'indicators_found': [...],
            'technical_score': 0-100,
            'content_score': 0-100
        }
        """
        print("📊 Kalite skoru hesaplanıyor...")
        
        category_scores = {}
        indicators_found = []
        total_weighted_score = 0
        total_weight = 0
        
        page_text_lower = page_text.lower()
        
        # 1. İçerik kalitesi analizi
        for category, config in self.quality_indicators.items():
            score = 0
            found_keywords = []
            
            for keyword in config['keywords']:
                if keyword.lower() in page_text_lower:
                    score += 1
                    found_keywords.append(keyword)
            
            # Normalize et (max 100)
            normalized_score = min((score / len(config['keywords'])) * 100, 100)
            category_scores[category] = {
                'score': round(normalized_score, 2),
                'weight': config['weight'],
                'found_keywords': found_keywords
            }
            
            weighted_score = normalized_score * config['weight']
            total_weighted_score += weighted_score
            total_weight += config['weight']
            
            if found_keywords:
                indicators_found.append({
                    'category': category,
                    'keywords': found_keywords[:5]  # İlk 5 keyword
                })
        
        content_score = (total_weighted_score / total_weight) if total_weight > 0 else 0
        
        # 2. Teknik kalite analizi
        technical_scores = {}
        technical_total = 0
        technical_weight = 0
        
        # SSL kontrolü
        has_ssl = url.startswith('https://')
        technical_scores['ssl'] = {
            'has': has_ssl,
            'score': 100 if has_ssl else 0,
            'weight': self.technical_quality_indicators['ssl']['weight']
        }
        
        # Responsive design kontrolü
        viewport_meta = soup.find('meta', {'name': 'viewport'})
        is_responsive = viewport_meta is not None
        technical_scores['responsive'] = {
            'has': is_responsive,
            'score': 100 if is_responsive else 0,
            'weight': self.technical_quality_indicators['responsive']['weight']
        }
        
        # SEO optimizasyonu
        has_meta_desc = soup.find('meta', {'name': 'description'}) is not None
        has_meta_keywords = soup.find('meta', {'name': 'keywords'}) is not None
        has_og_tags = soup.find('meta', property=re.compile('^og:')) is not None
        seo_score = sum([has_meta_desc, has_meta_keywords, has_og_tags]) / 3 * 100
        technical_scores['seo_optimized'] = {
            'score': seo_score,
            'weight': self.technical_quality_indicators['seo_optimized']['weight']
        }
        
        # Sosyal medya entegrasyonu
        social_links = soup.find_all('a', href=re.compile(
            r'(facebook|twitter|instagram|linkedin|youtube|tiktok)\.com'
        ))
        has_social = len(social_links) > 0
        technical_scores['social_media_integration'] = {
            'has': has_social,
            'count': len(social_links),
            'score': min(len(social_links) * 20, 100),
            'weight': self.technical_quality_indicators['social_media_integration']['weight']
        }
        
        # İletişim formu
        has_form = soup.find('form') is not None
        technical_scores['contact_forms'] = {
            'has': has_form,
            'score': 100 if has_form else 0,
            'weight': self.technical_quality_indicators['contact_forms']['weight']
        }
        
        # Canlı destek
        live_chat_indicators = ['tawk', 'zendesk', 'intercom', 'livechat', 'crisp', 'whatsapp']
        page_source = str(soup)
        has_live_chat = any(indicator in page_source.lower() for indicator in live_chat_indicators)
        technical_scores['live_chat'] = {
            'has': has_live_chat,
            'score': 100 if has_live_chat else 0,
            'weight': self.technical_quality_indicators['live_chat']['weight']
        }
        
        # Çok dilli
        lang_indicators = ['en', 'de', 'fr', 'es', 'ar', 'ru', 'zh']
        lang_links = soup.find_all('a', href=re.compile('|'.join([f'/{lang}/' for lang in lang_indicators])))
        is_multilingual = len(lang_links) > 0
        technical_scores['multilingual'] = {
            'has': is_multilingual,
            'score': 100 if is_multilingual else 0,
            'weight': self.technical_quality_indicators['multilingual']['weight']
        }
        
        # Blog/İçerik
        blog_indicators = ['blog', 'haber', 'news', 'article', 'makale']
        has_blog = any(soup.find('a', href=re.compile(indicator)) for indicator in blog_indicators)
        technical_scores['blog_content'] = {
            'has': has_blog,
            'score': 100 if has_blog else 0,
            'weight': self.technical_quality_indicators['blog_content']['weight']
        }
        
        # Video içerik
        has_video = soup.find('video') is not None or \
                   soup.find('iframe', src=re.compile('youtube|vimeo')) is not None
        technical_scores['video_content'] = {
            'has': has_video,
            'score': 100 if has_video else 0,
            'weight': self.technical_quality_indicators['video_content']['weight']
        }
        
        # Teknik skoru hesapla
        for key, data in technical_scores.items():
            score = data.get('score', 0)
            weight = data.get('weight', 0)
            technical_total += score * weight
            technical_weight += weight
        
        technical_score = (technical_total / technical_weight) if technical_weight > 0 else 0
        
        # 3. Toplam skor (60% içerik, 40% teknik)
        total_score = (content_score * 0.6) + (technical_score * 0.4)
        
        result = {
            'total_score': round(total_score, 2),
            'content_score': round(content_score, 2),
            'technical_score': round(technical_score, 2),
            'category_scores': category_scores,
            'technical_scores': technical_scores,
            'indicators_found': indicators_found,
            'grade': self.get_quality_grade(total_score),
            'recommendations': self.get_quality_recommendations(technical_scores, category_scores)
        }
        
        print(f"✅ Kalite skoru: {total_score:.1f}/100 ({result['grade']})")
        
        return result
    
    def get_quality_grade(self, score: float) -> str:
        """Kalite notunu belirle"""
        if score >= 90:
            return 'A+ (Mükemmel)'
        elif score >= 80:
            return 'A (Çok İyi)'
        elif score >= 70:
            return 'B+ (İyi)'
        elif score >= 60:
            return 'B (Orta Üstü)'
        elif score >= 50:
            return 'C (Orta)'
        elif score >= 40:
            return 'D (Zayıf)'
        else:
            return 'F (Çok Zayıf)'
    
    def get_quality_recommendations(self, technical_scores: Dict, 
                                   category_scores: Dict) -> List[str]:
        """Kalite iyileştirme önerileri"""
        recommendations = []
        
        # Teknik öneriler
        if not technical_scores.get('ssl', {}).get('has'):
            recommendations.append('SSL sertifikası ekleyin (HTTPS)')
        
        if not technical_scores.get('responsive', {}).get('has'):
            recommendations.append('Mobil uyumlu tasarım ekleyin')
        
        if technical_scores.get('seo_optimized', {}).get('score', 0) < 50:
            recommendations.append('SEO optimizasyonu yapın (meta tags, og tags)')
        
        if not technical_scores.get('social_media_integration', {}).get('has'):
            recommendations.append('Sosyal medya hesaplarınızı ekleyin')
        
        if not technical_scores.get('contact_forms', {}).get('has'):
            recommendations.append('İletişim formu ekleyin')
        
        if not technical_scores.get('live_chat', {}).get('has'):
            recommendations.append('Canlı destek sistemi ekleyin')
        
        # İçerik önerileri
        for category, data in category_scores.items():
            if data['score'] < 30:
                category_names = {
                    'certificates': 'Sertifika ve belgelerinizi ekleyin',
                    'awards': 'Ödül ve başarılarınızı vurgulayın',
                    'references': 'Referans ve projelerinizi gösterin',
                    'experience': 'Deneyim ve uzmanlığınızı belirtin',
                    'technology': 'Kullandığınız teknolojileri vurgulayın',
                    'export': 'Uluslararası çalışmalarınızı belirtin',
                    'capacity': 'Üretim kapasitesi ve ekip bilgilerini ekleyin',
                    'social_proof': 'Müşteri yorumları ve değerlendirmeleri ekleyin'
                }
                if category in category_names:
                    recommendations.append(category_names[category])
        
        return recommendations[:10]  # En önemli 10 öneri
    
    def extract_products_services_ai(self, soup: BeautifulSoup, page_text: str,
                                    company_type: str) -> Dict[str, Any]:
        """
        AI ile ürün ve hizmet analizi
        """
        print("🛍️ Ürün/Hizmet analizi yapılıyor...")
        
        # Ürün/hizmet listelerini bul
        products = []
        services = []
        
        # 1. Başlıklar ve listeler
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        for heading in headings:
            text = heading.get_text().strip().lower()
            
            if any(kw in text for kw in ['ürün', 'product', 'çözüm', 'solution']):
                # Başlık altındaki liste öğelerini al
                next_ul = heading.find_next('ul')
                if next_ul:
                    items = [li.get_text().strip() for li in next_ul.find_all('li')]
                    products.extend(items[:20])  # Max 20 ürün
            
            if any(kw in text for kw in ['hizmet', 'service', 'servis']):
                next_ul = heading.find_next('ul')
                if next_ul:
                    items = [li.get_text().strip() for li in next_ul.find_all('li')]
                    services.extend(items[:20])
        
        # 2. Ürün kartları/grid
        product_containers = soup.find_all(['div', 'article'], 
            class_=re.compile(r'product|urun|item|card', re.I))
        
        for container in product_containers[:50]:  # Max 50 konteyner
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'a'])
            if title_elem:
                title = title_elem.get_text().strip()
                if title and len(title) > 3 and len(title) < 200:
                    products.append(title)
        
        # 3. Kategori analizi
        categories = self.extract_categories(soup, page_text)
        
        # 4. AI ile kategorilendirme (opsiyonel)
        if self.openai_api_key and (products or services):
            try:
                ai_categorization = self.ai_categorize_products(
                    products[:30], services[:30], company_type
                )
            except:
                ai_categorization = {}
        else:
            ai_categorization = {}
        
        # Temizle ve unique yap
        products = list(set([p.strip() for p in products if p.strip()]))[:50]
        services = list(set([s.strip() for s in services if s.strip()]))[:50]
        
        result = {
            'products': products,
            'services': services,
            'categories': categories,
            'product_count': len(products),
            'service_count': len(services),
            'ai_categorization': ai_categorization
        }
        
        print(f"✅ {len(products)} ürün, {len(services)} hizmet bulundu")
        
        return result
    
    def extract_categories(self, soup: BeautifulSoup, page_text: str) -> List[str]:
        """Kategori listesini çıkar"""
        categories = []
        
        # Navigasyon menülerinden
        nav_elements = soup.find_all(['nav', 'ul'], class_=re.compile(r'menu|nav|category', re.I))
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links:
                text = link.get_text().strip()
                if text and len(text) > 2 and len(text) < 50:
                    categories.append(text)
        
        # Kategori başlıklarından
        category_headings = soup.find_all(['h2', 'h3'], 
            string=re.compile(r'kategori|category|çözüm|solution', re.I))
        for heading in category_headings:
            next_list = heading.find_next(['ul', 'div'])
            if next_list:
                items = next_list.find_all(['a', 'li'])
                for item in items:
                    text = item.get_text().strip()
                    if text and len(text) > 2 and len(text) < 50:
                        categories.append(text)
        
        # Temizle ve unique yap
        categories = list(set([c.strip() for c in categories if c.strip()]))
        
        return categories[:30]  # Max 30 kategori
    
    def advanced_ecommerce_analysis(self, driver, soup: BeautifulSoup, url: str, company_name: str) -> Dict[str, Any]:
        """
        Gelişmiş e-ticaret sitesi analizi
        Kategorilere göre ürünleri çıkarır ve detaylı analiz yapar
        """
        print("🛒 Gelişmiş e-ticaret analizi başlatılıyor...")
        
        result = {
            'is_ecommerce': True,
            'categories': [],
            'category_products': {},
            'total_products': 0,
            'price_ranges': {},
            'product_quality_indicators': {},
            'ecommerce_features': {},
            'scraping_stats': {}
        }
        
        try:
            # 1. Kategori sayfalarını bul
            categories = self.extract_ecommerce_categories(driver, soup)
            result['categories'] = categories
            
            # 2. Her kategoriden ürünleri çıkar
            category_products = {}
            total_products = 0
            
            for category in categories[:8]:  # Maksimum 8 kategori
                print(f"📦 Kategori analiz ediliyor: {category['name']}")
                
                try:
                    # Kategori sayfasına git
                    if category.get('url'):
                        driver.get(category['url'])
                        time.sleep(2)
                        
                        # Sayfa yüklenmesini bekle
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        
                        # Güncel HTML'i al
                        category_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    else:
                        category_soup = soup
                    
                    # Kategorideki ürünleri çıkar
                    products = self.extract_products_from_category(category_soup, category['name'])
                    
                    if products:
                        category_products[category['name']] = products
                        total_products += len(products)
                        print(f"✅ {len(products)} ürün bulundu: {category['name']}")
                    
                except Exception as e:
                    print(f"⚠️ Kategori analiz hatası {category['name']}: {e}")
                    continue
            
            result['category_products'] = category_products
            result['total_products'] = total_products
            
            # 3. Fiyat analizi
            result['price_ranges'] = self.analyze_price_ranges(category_products)
            
            # 4. E-ticaret özellikleri
            result['ecommerce_features'] = self.analyze_ecommerce_features(driver, soup)
            
            # 5. Ürün kalite göstergeleri
            result['product_quality_indicators'] = self.analyze_product_quality_indicators(category_products)
            
            # 6. İstatistikler
            result['scraping_stats'] = {
                'categories_analyzed': len(category_products),
                'total_products_found': total_products,
                'avg_products_per_category': total_products / len(category_products) if category_products else 0,
                'scraping_time': datetime.now().isoformat()
            }
            
            print(f"✅ E-ticaret analizi tamamlandı: {total_products} ürün, {len(category_products)} kategori")
            
        except Exception as e:
            print(f"❌ E-ticaret analiz hatası: {e}")
            result['error'] = str(e)
        
        return result
    
    def extract_ecommerce_categories(self, driver, soup: BeautifulSoup) -> List[Dict]:
        """E-ticaret kategorilerini çıkar"""
        categories = []
        
        try:
            # Navigasyon menülerinden kategorileri bul
            nav_selectors = [
                'nav a[href*="kategori"]',
                'nav a[href*="category"]',
                '.menu a[href*="kategori"]',
                '.menu a[href*="category"]',
                '.category-menu a',
                '.nav-category a',
                '.main-menu a',
                '.navigation a'
            ]
            
            for selector in nav_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        try:
                            name = element.text.strip()
                            url = element.get_attribute('href')
                            
                            if name and len(name) > 2 and len(name) < 50:
                                categories.append({
                                    'name': name,
                                    'url': url if url and url.startswith('http') else None
                                })
                        except:
                            continue
                except:
                    continue
            
            # Kategori başlıklarından
            category_headings = soup.find_all(['h2', 'h3'], 
                string=re.compile(r'kategori|category|ürün|product', re.I))
            
            for heading in category_headings:
                try:
                    name = heading.get_text().strip()
                    if name and len(name) > 2 and len(name) < 50:
                        # Başlık altındaki linki bul
                        link = heading.find_next('a')
                        url = link.get('href') if link else None
                        
                        categories.append({
                            'name': name,
                            'url': url if url and url.startswith('http') else None
                        })
                except:
                    continue
            
            # Duplicate'leri kaldır
            seen = set()
            unique_categories = []
            for cat in categories:
                if cat['name'] not in seen:
                    seen.add(cat['name'])
                    unique_categories.append(cat)
            
            return unique_categories[:15]  # Maksimum 15 kategori
            
        except Exception as e:
            print(f"⚠️ Kategori çıkarma hatası: {e}")
            return []
    
    def extract_products_from_category(self, soup: BeautifulSoup, category_name: str) -> List[Dict]:
        """Kategoriden ürünleri çıkar"""
        products = []
        
        try:
            # Ürün konteynerlerini bul
            product_selectors = [
                '.product-item',
                '.product-card',
                '.product-box',
                '.item',
                '.urun',
                '.product',
                '[class*="product"]',
                '[class*="item"]',
                '[class*="card"]'
            ]
            
            for selector in product_selectors:
                try:
                    containers = soup.select(selector)
                    for container in containers[:20]:  # Maksimum 20 ürün per kategori
                        try:
                            product = self.extract_single_product(container, category_name)
                            if product:
                                products.append(product)
                        except:
                            continue
                except:
                    continue
            
            return products[:15]  # Maksimum 15 ürün per kategori
            
        except Exception as e:
            print(f"⚠️ Ürün çıkarma hatası {category_name}: {e}")
            return []
    
    def extract_single_product(self, container, category_name: str) -> Dict:
        """Tek ürün bilgilerini çıkar"""
        try:
            product = {
                'name': '',
                'price': '',
                'image_url': '',
                'description': '',
                'category': category_name,
                'url': ''
            }
            
            # Ürün adı
            name_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', 'a']
            for selector in name_selectors:
                try:
                    name_elem = container.select_one(selector)
                    if name_elem:
                        name = name_elem.get_text().strip()
                        if name and len(name) > 3:
                            product['name'] = name
                            break
                except:
                    continue
            
            # Fiyat
            price_selectors = ['.price', '.cost', '.amount', '[class*="price"]', '[class*="fiyat"]']
            for selector in price_selectors:
                try:
                    price_elem = container.select_one(selector)
                    if price_elem:
                        price = price_elem.get_text().strip()
                        if price and any(char.isdigit() for char in price):
                            product['price'] = price
                            break
                except:
                    continue
            
            # Görsel
            img_elem = container.select_one('img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src')
                if img_src:
                    if img_src.startswith('http'):
                        product['image_url'] = img_src
                    elif img_src.startswith('/'):
                        product['image_url'] = 'https://' + img_src.lstrip('/')
            
            # Ürün linki
            link_elem = container.select_one('a')
            if link_elem:
                href = link_elem.get('href')
                if href:
                    if href.startswith('http'):
                        product['url'] = href
                    elif href.startswith('/'):
                        product['url'] = 'https://' + href.lstrip('/')
            
            # Açıklama
            desc_selectors = ['.description', '.desc', '.summary', 'p']
            for selector in desc_selectors:
                try:
                    desc_elem = container.select_one(selector)
                    if desc_elem:
                        desc = desc_elem.get_text().strip()
                        if desc and len(desc) > 10:
                            product['description'] = desc[:200]  # İlk 200 karakter
                            break
                except:
                    continue
            
            # Sadece ismi olan ürünleri döndür
            if product['name']:
                return product
            
        except Exception as e:
            print(f"⚠️ Ürün çıkarma hatası: {e}")
        
        return None
    
    def analyze_price_ranges(self, category_products: Dict) -> Dict:
        """Fiyat aralıklarını analiz et"""
        price_ranges = {}
        
        try:
            for category, products in category_products.items():
                prices = []
                for product in products:
                    if product.get('price'):
                        # Fiyattan sayıları çıkar
                        price_text = product['price']
                        price_numbers = re.findall(r'[\d,]+\.?\d*', price_text)
                        if price_numbers:
                            try:
                                price = float(price_numbers[0].replace(',', ''))
                                prices.append(price)
                            except:
                                continue
                
                if prices:
                    price_ranges[category] = {
                        'min_price': min(prices),
                        'max_price': max(prices),
                        'avg_price': sum(prices) / len(prices),
                        'product_count': len(prices)
                    }
        
        except Exception as e:
            print(f"⚠️ Fiyat analiz hatası: {e}")
        
        return price_ranges
    
    def analyze_ecommerce_features(self, driver, soup: BeautifulSoup) -> Dict:
        """E-ticaret özelliklerini analiz et"""
        features = {
            'has_search': False,
            'has_filters': False,
            'has_cart': False,
            'has_wishlist': False,
            'has_reviews': False,
            'has_ratings': False,
            'has_comparison': False,
            'has_quick_view': False,
            'payment_methods': [],
            'shipping_info': False,
            'return_policy': False
        }
        
        try:
            page_source = str(soup).lower()
            
            # Arama özelliği
            search_indicators = ['search', 'ara', 'arama', 'find']
            features['has_search'] = any(indicator in page_source for indicator in search_indicators)
            
            # Filtre özelliği
            filter_indicators = ['filter', 'filtre', 'sort', 'sırala']
            features['has_filters'] = any(indicator in page_source for indicator in filter_indicators)
            
            # Sepet özelliği
            cart_indicators = ['cart', 'sepet', 'basket', 'add to cart']
            features['has_cart'] = any(indicator in page_source for indicator in cart_indicators)
            
            # İstek listesi
            wishlist_indicators = ['wishlist', 'istek', 'favorite', 'favori']
            features['has_wishlist'] = any(indicator in page_source for indicator in wishlist_indicators)
            
            # Yorumlar
            review_indicators = ['review', 'yorum', 'comment', 'rating']
            features['has_reviews'] = any(indicator in page_source for indicator in review_indicators)
            
            # Ödeme yöntemleri
            payment_methods = ['visa', 'mastercard', 'paypal', 'stripe', 'iyzico', 'garanti', 'akbank']
            for method in payment_methods:
                if method in page_source:
                    features['payment_methods'].append(method)
            
            # Kargo bilgisi
            shipping_indicators = ['shipping', 'kargo', 'delivery', 'teslimat']
            features['shipping_info'] = any(indicator in page_source for indicator in shipping_indicators)
            
            # İade politikası
            return_indicators = ['return', 'iade', 'refund', 'geri']
            features['return_policy'] = any(indicator in page_source for indicator in return_indicators)
        
        except Exception as e:
            print(f"⚠️ E-ticaret özellik analiz hatası: {e}")
        
        return features
    
    def analyze_product_quality_indicators(self, category_products: Dict) -> Dict:
        """Ürün kalite göstergelerini analiz et"""
        indicators = {
            'avg_description_length': 0,
            'products_with_images': 0,
            'products_with_prices': 0,
            'products_with_descriptions': 0,
            'total_products': 0,
            'quality_score': 0
        }
        
        try:
            total_products = 0
            total_desc_length = 0
            products_with_images = 0
            products_with_prices = 0
            products_with_descriptions = 0
            
            for category, products in category_products.items():
                for product in products:
                    total_products += 1
                    
                    if product.get('image_url'):
                        products_with_images += 1
                    
                    if product.get('price'):
                        products_with_prices += 1
                    
                    if product.get('description'):
                        products_with_descriptions += 1
                        total_desc_length += len(product['description'])
            
            if total_products > 0:
                indicators['total_products'] = total_products
                indicators['avg_description_length'] = total_desc_length / total_products
                indicators['products_with_images'] = products_with_images
                indicators['products_with_prices'] = products_with_prices
                indicators['products_with_descriptions'] = products_with_descriptions
                
                # Kalite skoru hesapla (0-100)
                quality_score = 0
                quality_score += (products_with_images / total_products) * 30  # %30 görsel
                quality_score += (products_with_prices / total_products) * 25  # %25 fiyat
                quality_score += (products_with_descriptions / total_products) * 25  # %25 açıklama
                quality_score += min(indicators['avg_description_length'] / 50, 1) * 20  # %20 açıklama kalitesi
                
                indicators['quality_score'] = round(quality_score, 2)
        
        except Exception as e:
            print(f"⚠️ Kalite analiz hatası: {e}")
        
        return indicators
    
    def analyze_images_by_category(self, selected_images: List[Dict], vision_result: Dict) -> Dict:
        """Kategorilere göre görsel analizi"""
        category_analysis = {}
        
        try:
            for img_data in selected_images:
                category = img_data.get('category', 'Unknown')
                if category not in category_analysis:
                    category_analysis[category] = {
                        'images_analyzed': 0,
                        'products': [],
                        'avg_quality_score': 0
                    }
                
                category_analysis[category]['images_analyzed'] += 1
                category_analysis[category]['products'].append({
                    'name': img_data.get('product_name', ''),
                    'price': img_data.get('price', ''),
                    'image_url': img_data.get('url', '')
                })
        
        except Exception as e:
            print(f"⚠️ Kategori görsel analiz hatası: {e}")
        
        return category_analysis
    
    def ai_categorize_products(self, products: List[str], services: List[str],
                              company_type: str) -> Dict:
        """AI ile ürün/hizmet kategorilendirme"""
        try:
            prompt = f"""Firma tipi: {company_type}

Ürünler: {', '.join(products[:20])}
Hizmetler: {', '.join(services[:20])}

Bu ürün ve hizmetleri mantıklı kategorilere ayır. JSON formatında:
{{
    "main_categories": ["kategori1", "kategori2", ...],
    "product_categories": {{"kategori": ["ürün1", "ürün2", ...]}},
    "service_categories": {{"kategori": ["hizmet1", "hizmet2", ...]}}
}}"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir ürün kategorilendirme uzmanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"⚠️ AI kategorilendirme hatası: {e}")
            return {}
    
    def detect_apis_and_integrations(self, soup: BeautifulSoup, driver=None) -> Dict[str, Any]:
        """API ve entegrasyonları tespit et"""
        print("🔌 API ve entegrasyonlar tespit ediliyor...")
        
        integrations = {
            'payment': [],
            'analytics': [],
            'marketing': [],
            'communication': [],
            'social': [],
            'other': []
        }
        
        page_source = str(soup).lower()
        
        # Ödeme sistemleri
        payment_systems = {
            'stripe': 'Stripe',
            'paypal': 'PayPal',
            'iyzico': 'Iyzico',
            'paytr': 'PayTR',
            'masterpass': 'Masterpass',
            'payu': 'PayU',
            'braintree': 'Braintree'
        }
        
        for key, name in payment_systems.items():
            if key in page_source:
                integrations['payment'].append(name)
        
        # Analytics
        analytics_systems = {
            'google-analytics': 'Google Analytics',
            'gtag': 'Google Tag Manager',
            'hotjar': 'Hotjar',
            'mixpanel': 'Mixpanel',
            'amplitude': 'Amplitude',
            'segment': 'Segment'
        }
        
        for key, name in analytics_systems.items():
            if key in page_source:
                integrations['analytics'].append(name)
        
        # Marketing
        marketing_systems = {
            'mailchimp': 'Mailchimp',
            'hubspot': 'HubSpot',
            'salesforce': 'Salesforce',
            'marketo': 'Marketo',
            'pardot': 'Pardot',
            'activecampaign': 'ActiveCampaign'
        }
        
        for key, name in marketing_systems.items():
            if key in page_source:
                integrations['marketing'].append(name)
        
        # İletişim
        communication_systems = {
            'tawk': 'Tawk.to',
            'zendesk': 'Zendesk',
            'intercom': 'Intercom',
            'livechat': 'LiveChat',
            'crisp': 'Crisp',
            'drift': 'Drift'
        }
        
        for key, name in communication_systems.items():
            if key in page_source:
                integrations['communication'].append(name)
        
        # Sosyal medya
        social_systems = {
            'facebook pixel': 'Facebook Pixel',
            'linkedin insight': 'LinkedIn Insight',
            'twitter pixel': 'Twitter Pixel',
            'tiktok pixel': 'TikTok Pixel',
            'pinterest': 'Pinterest Tag'
        }
        
        for key, name in social_systems.items():
            if key in page_source:
                integrations['social'].append(name)
        
        # API endpoint tespiti (driver ile)
        api_endpoints = []
        if driver:
            try:
                # Network isteklerini yakala (Chrome DevTools Protocol)
                logs = driver.get_log('performance')
                for log in logs:
                    message = json.loads(log['message'])
                    if 'Network.requestWillBeSent' in message.get('message', {}).get('method', ''):
                        url = message['message']['params'].get('request', {}).get('url', '')
                        if '/api/' in url or '/v1/' in url or '/v2/' in url:
                            api_endpoints.append(url)
            except:
                pass
        
        result = {
            'integrations': integrations,
            'api_endpoints': list(set(api_endpoints))[:20],
            'total_integrations': sum(len(v) for v in integrations.values()),
            'has_payment': len(integrations['payment']) > 0,
            'has_analytics': len(integrations['analytics']) > 0,
            'has_live_chat': len(integrations['communication']) > 0
        }
        
        print(f"✅ {result['total_integrations']} entegrasyon bulundu")
        
        return result
    
    def scrape_website_enhanced(self, url: str, company_name: str = "") -> Dict[str, Any]:
        """
        Gelişmiş web scraping - Ana fonksiyon
        """
        print(f"\n{'='*60}")
        print(f"🚀 Gelişmiş Web Scraping Başlatılıyor")
        print(f"🌐 URL: {url}")
        print(f"🏢 Firma: {company_name}")
        print(f"{'='*60}\n")
        
        if not url:
            return {}
        
        # URL düzelt
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        driver = None
        result = {
            'success': False,
            'url': url,
            'company_name': company_name,
            'scraped_at': datetime.now().isoformat(),
            'error': None
        }
        
        try:
            # Driver oluştur
            driver = self.create_driver()
            
            # Sayfayı yükle
            print(f"📄 Sayfa yükleniyor...")
            driver.get(url)
            time.sleep(random.uniform(2, 4))  # Anti-detection
            
            # Sayfa kaynağını al
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Metin içeriği
            page_text = soup.get_text(separator=' ', strip=True)
            
            print(f"✅ Sayfa yüklendi ({len(page_text)} karakter)\n")
            
            # 1. Firma tipi analizi
            company_type_analysis = self.analyze_company_type(url, soup, page_text, driver)
            result['company_type_analysis'] = company_type_analysis
            
            # 2. Kalite skoru
            quality_score = self.calculate_quality_score(url, soup, page_text, driver)
            result['quality_score'] = quality_score
            
            # 3. Ürün/Hizmet analizi
            products_services = self.extract_products_services_ai(
                soup, page_text, company_type_analysis['primary_type']
            )
            result['products_services'] = products_services
            
            # 4. API ve entegrasyonlar
            integrations = self.detect_apis_and_integrations(soup, driver)
            result['integrations'] = integrations
            
            # 5. Temel bilgiler (mevcut web_scraper'dan)
            result['basic_info'] = {
                'title': soup.title.string if soup.title else '',
                'meta_description': self.get_meta_tag(soup, 'description'),
                'meta_keywords': self.get_meta_tag(soup, 'keywords'),
                'language': soup.html.get('lang', 'tr') if soup.html else 'tr',
                'has_ssl': url.startswith('https://'),
                'domain': urlparse(url).netloc
            }
            
            # 6. İletişim bilgileri
            result['contact_info'] = {
                'emails': self.extract_emails(page_source),
                'phones': self.extract_phones(page_source),
                'social_media': self.extract_social_media(soup),
                'address': self.extract_address(page_text)
            }
            
            # 7. Gelişmiş E-ticaret Analizi (E-ticaret için)
            result['ecommerce_analysis'] = {}
            result['product_images_analysis'] = {}
            
            if integrations.get('has_payment', False) or integrations.get('has_ecommerce', False):
                print("\n🛒 E-ticaret sitesi tespit edildi, gelişmiş ürün analizi başlatılıyor...")
                
                try:
                    # Gelişmiş e-ticaret analizi
                    ecommerce_analysis = self.advanced_ecommerce_analysis(driver, soup, url, company_name)
                    result['ecommerce_analysis'] = ecommerce_analysis
                    
                    # AI Vision ile ürün görselleri analizi
                    if self.vision_analyzer and AI_VISION_AVAILABLE:
                        print("🖼️ AI ile ürün görselleri analiz ediliyor...")
                        
                        # Kategorilere göre ürün görsellerini çıkar
                        category_products = ecommerce_analysis.get('category_products', {})
                        all_product_images = []
                        
                        for category, products in category_products.items():
                            if len(products) > 0:
                                # Her kategoriden ilk 2 ürünün görselini al
                                for product in products[:2]:
                                    if 'image_url' in product and product['image_url']:
                                        all_product_images.append({
                                            'url': product['image_url'],
                                            'category': category,
                                            'product_name': product.get('name', ''),
                                            'price': product.get('price', '')
                                        })
                        
                        # Maksimum 10 görsel analiz et (maliyet kontrolü)
                        if all_product_images:
                            selected_images = all_product_images[:10]
                            image_urls = [img['url'] for img in selected_images]
                            
                            vision_result = self.vision_analyzer.analyze_product_images_batch(
                                image_urls,
                                max_images=10,
                                detail="high"  # Yüksek detay = daha iyi analiz
                            )
                            
                            result['product_images_analysis'] = {
                                'total_images_found': len(all_product_images),
                                'analyzed_images': vision_result.get('total_images_analyzed', 0),
                                'product_images': vision_result.get('product_images', []),
                                'category_analysis': self.analyze_images_by_category(selected_images, vision_result),
                                'total_cost': vision_result.get('total_cost', 0),
                                'usage_stats': vision_result.get('summary_stats', {})
                            }
                            
                            print(f"✅ {vision_result.get('total_images_analyzed', 0)} ürün görseli analiz edildi")
                            print(f"💰 Maliyet: ${vision_result.get('total_cost', 0):.4f}")
                        else:
                            print("⚠️ Ürün görseli bulunamadı")
                    
                except Exception as e:
                    print(f"⚠️ E-ticaret analiz hatası: {e}")
                    result['ecommerce_analysis']['error'] = str(e)
                    result['product_images_analysis']['error'] = str(e)
            
            # 8. AI ile detaylı özet oluştur
            print("\n🤖 AI özeti oluşturuluyor...")
            ai_summary = self.generate_ai_summary(result, company_name)
            result['ai_summary'] = ai_summary
            
            result['success'] = True
            
            print(f"\n{'='*60}")
            print(f"✅ Web Scraping Tamamlandı")
            print(f"📊 Firma Tipi: {company_type_analysis['primary_type_tr']}")
            print(f"⭐ Kalite Skoru: {quality_score['total_score']:.1f}/100")
            print(f"🛍️ Ürün/Hizmet: {products_services['product_count']} / {products_services['service_count']}")
            print(f"🔌 Entegrasyon: {integrations['total_integrations']}")
            print(f"🤖 AI Özeti: {len(ai_summary)} karakter")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            result['error'] = str(e)
            result['success'] = False
            
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        return result
    
    # Yardımcı fonksiyonlar
    
    def get_meta_tag(self, soup: BeautifulSoup, name: str) -> str:
        """Meta tag değerini al"""
        meta = soup.find('meta', {'name': name})
        if meta:
            return meta.get('content', '')
        return ''
    
    def extract_emails(self, page_source: str) -> List[str]:
        """Email adreslerini çıkar"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_source)
        
        # Temizle ve filtrele
        valid_emails = []
        for email in emails:
            email = email.lower().strip()
            # Geçersiz uzantıları filtrele
            if not email.endswith(('.png', '.jpg', '.gif', '.css', '.js')):
                if email not in valid_emails:
                    valid_emails.append(email)
        
        return valid_emails[:20]  # Max 20 email
    
    def extract_phones(self, page_source: str) -> List[str]:
        """Telefon numaralarını çıkar"""
        phone_patterns = [
            r'\+90\s?\d{3}\s?\d{3}\s?\d{2}\s?\d{2}',
            r'0\d{3}\s?\d{3}\s?\d{2}\s?\d{2}',
            r'\(\d{3}\)\s?\d{3}\s?\d{2}\s?\d{2}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}'
        ]
        
        phones = []
        for pattern in phone_patterns:
            found = re.findall(pattern, page_source)
            phones.extend(found)
        
        # Temizle ve unique yap
        phones = list(set([p.strip() for p in phones]))
        
        return phones[:10]  # Max 10 telefon
    
    def extract_social_media(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Sosyal medya hesaplarını çıkar"""
        social_media = {}
        
        social_patterns = {
            'facebook': r'facebook\.com/[\w\-\.]+',
            'instagram': r'instagram\.com/[\w\-\.]+',
            'twitter': r'twitter\.com/[\w\-\.]+',
            'linkedin': r'linkedin\.com/(company|in)/[\w\-\.]+',
            'youtube': r'youtube\.com/(channel|c|user)/[\w\-\.]+',
            'tiktok': r'tiktok\.com/@[\w\-\.]+',
            'pinterest': r'pinterest\.com/[\w\-\.]+',
            'whatsapp': r'wa\.me/\d+'
        }
        
        page_html = str(soup)
        
        for platform, pattern in social_patterns.items():
            match = re.search(pattern, page_html, re.I)
            if match:
                social_media[platform] = 'https://' + match.group(0)
        
        return social_media
    
    def extract_address(self, page_text: str) -> str:
        """Adres bilgisini çıkar (basit)"""
        # Adres pattern'leri (Türkiye için)
        address_indicators = ['adres:', 'address:', 'merkez:', 'office:']
        
        for indicator in address_indicators:
            idx = page_text.lower().find(indicator)
            if idx != -1:
                # Göstergeden sonraki 200 karakteri al
                address_text = page_text[idx:idx+200]
                # İlk cümleyi al
                sentences = address_text.split('.')
                if sentences:
                    return sentences[0].strip()
        
        return ''
    
    def generate_ai_summary(self, scraping_result: Dict[str, Any], company_name: str = "") -> str:
        """
        AI ile firma için detaylı özet oluştur
        """
        try:
            if not self.openai_api_key:
                return "AI özeti oluşturulamadı: OpenAI API anahtarı gerekli"
            
            # Scraping sonuçlarından bilgileri topla
            company_type = scraping_result.get('company_type_analysis', {})
            quality_score = scraping_result.get('quality_score', {})
            products_services = scraping_result.get('products_services', {})
            integrations = scraping_result.get('integrations', {})
            contact_info = scraping_result.get('contact_info', {})
            basic_info = scraping_result.get('basic_info', {})
            
            # Firma tipi bilgisi
            primary_type = company_type.get('primary_type_tr', 'Belirsiz')
            confidence = company_type.get('confidence', 0)
            
            # Kalite bilgisi
            total_score = quality_score.get('total_score', 0)
            grade = quality_score.get('grade', 'N/A')
            
            # Ürün/hizmet bilgisi
            product_count = products_services.get('product_count', 0)
            service_count = products_services.get('service_count', 0)
            categories = products_services.get('categories', [])
            
            # Entegrasyon bilgisi
            total_integrations = integrations.get('total_integrations', 0)
            has_ecommerce = integrations.get('has_payment', False)
            has_live_chat = integrations.get('has_live_chat', False)
            
            # İletişim bilgisi
            email_count = len(contact_info.get('emails', []))
            phone_count = len(contact_info.get('phones', []))
            social_count = len(contact_info.get('social_media', {}))
            
            # Temel bilgiler
            title = basic_info.get('title', '')
            meta_description = basic_info.get('meta_description', '')
            has_ssl = basic_info.get('has_ssl', False)
            domain = basic_info.get('domain', '')
            
            # E-ticaret analizi bilgileri
            ecommerce_analysis = scraping_result.get('ecommerce_analysis', {})
            product_images_analysis = scraping_result.get('product_images_analysis', {})
            
            # E-ticaret bilgileri
            is_ecommerce = ecommerce_analysis.get('is_ecommerce', False)
            total_products = ecommerce_analysis.get('total_products', 0)
            ecommerce_categories = ecommerce_analysis.get('categories', [])
            category_products = ecommerce_analysis.get('category_products', {})
            price_ranges = ecommerce_analysis.get('price_ranges', {})
            ecommerce_features = ecommerce_analysis.get('ecommerce_features', {})
            quality_indicators = ecommerce_analysis.get('product_quality_indicators', {})
            
            # AI prompt oluştur - Gelişmiş firma analizi için
            prompt = f"""Sen bir B2B firma analiz uzmanısın. Aşağıdaki web sitesi analiz sonuçlarını kullanarak firma için kapsamlı, detaylı ve profesyonel bir analiz raporu oluştur:

🏢 FIRMA KİMLİK BİLGİLERİ:
- Firma Adı: {company_name}
- Web Sitesi: {domain}
- Sayfa Başlığı: {title}
- Meta Açıklama: {meta_description}
- SSL Güvenliği: {'✅ Güvenli' if has_ssl else '❌ Güvensiz'}

🔍 FIRMA TİPİ VE İŞ MODELİ ANALİZİ:
- Ana Faaliyet Tipi: {primary_type}
- Analiz Güvenilirliği: {confidence}%
- İkincil Faaliyet Alanları: {', '.join(company_type.get('secondary_types_tr', [])) if company_type.get('secondary_types_tr') else 'Belirtilmemiş'}

⭐ WEB SİTESİ KALİTE DEĞERLENDİRMESİ:
- Genel Kalite Puanı: {total_score}/100
- Kalite Notu: {grade}
- İçerik Kalitesi: {quality_score.get('content_score', 0)}/100
- Teknik Kalite: {quality_score.get('technical_score', 0)}/100

🛍️ ÜRÜN/HİZMET PORTFÖYÜ:
- Ürün Sayısı: {product_count}
- Hizmet Sayısı: {service_count}
- Faaliyet Kategorileri: {', '.join(categories[:5]) if categories else 'Belirtilmemiş'}

🔌 TEKNİK ALTYAPI VE ENTEGRASYONLAR:
- Toplam Entegrasyon Sayısı: {total_integrations}
- E-ticaret Altyapısı: {'✅ Mevcut' if has_ecommerce else '❌ Yok'}
- Canlı Destek Sistemi: {'✅ Mevcut' if has_live_chat else '❌ Yok'}

📞 İLETİŞİM VE ERİŞİLEBİLİRLİK:
- Email Adresi Sayısı: {email_count}
- Telefon Numarası Sayısı: {phone_count}
- Aktif Sosyal Medya Platformu: {social_count}
- Web Sitesi Güvenliği: {'✅ SSL Sertifikalı' if has_ssl else '❌ SSL Yok'}

🛒 E-TİCARET ANALİZİ (Eğer e-ticaret sitesi ise):
- E-ticaret Durumu: {'✅ E-ticaret Sitesi' if is_ecommerce else '❌ Standart Web Sitesi'}
- Toplam Ürün Sayısı: {total_products}
- Kategori Sayısı: {len(ecommerce_categories)}
- Ürün Kalite Skoru: {quality_indicators.get('quality_score', 0)}/100
- Fiyat Aralıkları: {len(price_ranges)} kategori
- E-ticaret Özellikleri: {'Arama: ' + ('✅' if ecommerce_features.get('has_search') else '❌') + ', Sepet: ' + ('✅' if ecommerce_features.get('has_cart') else '❌') + ', Filtre: ' + ('✅' if ecommerce_features.get('has_filters') else '❌')}
- Ödeme Yöntemleri: {', '.join(ecommerce_features.get('payment_methods', [])) if ecommerce_features.get('payment_methods') else 'Belirtilmemiş'}
- Kategori Detayları: {', '.join([cat['name'] for cat in ecommerce_categories[:5]]) if ecommerce_categories else 'Belirtilmemiş'}

🖼️ AI GÖRSEL ANALİZİ (E-ticaret için):
- Analiz Edilen Görsel Sayısı: {product_images_analysis.get('analyzed_images', 0)}
- Toplam Bulunan Görsel: {product_images_analysis.get('total_images_found', 0)}
- Görsel Analiz Maliyeti: ${product_images_analysis.get('total_cost', 0):.4f}

Bu analiz sonuçlarını kullanarak firma için kapsamlı bir değerlendirme raporu oluştur. Rapor şu bölümleri detaylı şekilde içermeli:

1. **FİRMA GENEL TANITIMI**: 
   - Firma adı, web sitesi ve temel faaliyet alanı hakkında genel bilgi
   - Firma hakkında kısa tarihçe ve misyon vizyon değerlendirmesi
   - Web sitesi genel görünümü ve kullanıcı deneyimi değerlendirmesi

2. **İŞ MODELİ ANALİZİ**: 
   - Firma tipi, faaliyet alanları ve iş modeli değerlendirmesi
   - Gelir modeli ve iş stratejisi analizi
   - Hedef kitle ve pazar konumlandırması
   - Rekabet avantajları ve farklılaşma faktörleri

3. **DİJİTAL VARLIK DEĞERLENDİRMESİ**: 
   - Web sitesi kalitesi, teknik altyapı ve kullanıcı deneyimi
   - SEO optimizasyonu ve arama motoru uyumluluğu
   - Mobil uyumluluk ve responsive tasarım değerlendirmesi
   - Sayfa yükleme hızı ve performans analizi

4. **ÜRÜN/HİZMET PORTFÖYÜ**: 
   - Sunulan ürün ve hizmetlerin kapsamı ve çeşitliliği
   - Ürün kalitesi ve fiyatlandırma stratejisi değerlendirmesi
   - Hizmet kalitesi ve müşteri memnuniyeti göstergeleri
   - Ürün/hizmet kategorilerinin detaylı analizi

5. **TEKNİK ENTEGRASYON DURUMU**: 
   - E-ticaret, canlı destek ve diğer teknolojik entegrasyonlar
   - Ödeme sistemleri ve güvenlik önlemleri
   - CRM ve müşteri yönetim sistemleri
   - API entegrasyonları ve üçüncü parti servisler

6. **İLETİŞİM VE ERİŞİLEBİLİRLİK**: 
   - İletişim kanalları ve müşteri erişilebilirliği
   - Sosyal medya varlığı ve etkileşim kalitesi
   - Müşteri hizmetleri ve destek süreçleri
   - İletişim bilgilerinin güncelliği ve doğruluğu

7. **GENEL DEĞERLENDİRME**: 
   - Firma güvenilirliği, potansiyeli ve iyileştirme önerileri
   - Güçlü yönler ve gelişim alanları
   - Risk faktörleri ve dikkat edilmesi gereken noktalar
   - Gelecek potansiyeli ve büyüme fırsatları

8. **B2B İŞBİRLİĞİ POTANSİYELİ**: 
   - Diğer firmalarla işbirliği potansiyeli ve uygunluk
   - Ortaklık fırsatları ve stratejik işbirlikleri
   - Tedarikçi/müşteri ilişkileri potansiyeli
   - Sektörel uyumluluk ve sinerji analizi

9. **E-TİCARET DETAYLI ANALİZİ** (Eğer e-ticaret sitesi ise):
   - Ürün portföyü ve kategorilendirme analizi
   - Fiyat stratejisi ve rekabet analizi
   - E-ticaret altyapısı ve teknik özellikler
   - Müşteri deneyimi ve kullanılabilirlik değerlendirmesi
   - AI görsel analizi sonuçları ve ürün kalitesi
   - E-ticaret performans göstergeleri
   - Dijital pazarlama potansiyeli

Rapor Türkçe olmalı, 800-1200 kelime arasında olmalı ve profesyonel, objektif, analitik bir dil kullanmalı. Firma hakkında net, anlaşılır ve eyleme dönüştürülebilir bilgiler sunmalı. Her bölümde detaylı açıklamalar ve örnekler ver. 

ÖNEMLİ NOTLAR:
- Her bölümde somut veriler ve sayısal değerler kullan
- Firma için spesifik öneriler ve eylem planları sun
- Potansiyel riskleri ve fırsatları belirt
- Sektörel karşılaştırmalar yap
- Müşteri perspektifinden değerlendirme yap
- Gelecek 6-12 ay için tahminlerde bulun
- B2B işbirliği için somut adımlar öner"""

            # OpenAI API çağrısı
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir B2B firma analiz uzmanısın ve dijital pazarlama stratejisti. Web sitesi analiz sonuçlarını kullanarak firmaların iş potansiyelini, güvenilirliğini ve B2B işbirliği uygunluğunu değerlendiren kapsamlı analiz raporları oluşturursun. Raporların profesyonel, objektif, analitik ve eyleme dönüştürülebilir olmasına özen gösterirsin."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2300
            )
            
            ai_summary = response.choices[0].message.content.strip()
            print(f"✅ AI özeti oluşturuldu ({len(ai_summary)} karakter)")
            return ai_summary
            
        except Exception as e:
            print(f"❌ AI özet oluşturma hatası: {e}")
            return f"AI özeti oluşturulamadı: {str(e)}"


# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 Enhanced Web Scraper Test\n")
    
    # Test URL'leri
    test_urls = [
        "https://www.example-manufacturer.com",
        "https://www.example-supplier.com"
    ]
    
    scraper = EnhancedWebScraper(
        use_proxy=False,
        use_ai_vision=True,
        openai_api_key=None  # API key buraya
    )
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Test URL: {url}")
        print(f"{'='*60}\n")
        
        result = scraper.scrape_website_enhanced(url)
        
        if result['success']:
            print("✅ Başarılı!")
            print(f"Firma Tipi: {result['company_type_analysis']['primary_type_tr']}")
            print(f"Kalite Skoru: {result['quality_score']['total_score']}")
        else:
            print(f"❌ Hata: {result['error']}")

