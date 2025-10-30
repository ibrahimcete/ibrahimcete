#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from urllib.parse import urlparse, urljoin
import validators
import dns.resolver
import requests
import base64
import json
from datetime import datetime
import hashlib
try:
    from PIL import Image
    from io import BytesIO
    import pytesseract
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR kütüphaneleri yüklü değil, görsel analiz sınırlı olacak")


class WebScraper:
    """AI destekli gelişmiş web scraping işlemleri - B2B Enhanced Version"""
    
    def __init__(self, use_proxy: bool = False, use_ai_vision: bool = True):
        self.use_proxy = use_proxy
        self.use_ai_vision = use_ai_vision
        self.setup_driver()
        self.setup_sector_analyzers()
        
        # Email pattern'leri - GELİŞTİRİLDİ
        self.email_patterns = [
            # Standart email formatı
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            # Boşluklu emailler
            r'[a-zA-Z0-9._%+-]+\s*@\s*[a-zA-Z0-9.-]+\s*\.\s*[a-zA-Z]{2,}',
            # Obfuscated formatlar
            r'[a-zA-Z0-9._%+-]+\[at\][a-zA-Z0-9.-]+\[dot\][a-zA-Z]{2,}',
            r'[a-zA-Z0-9._%+-]+\(at\)[a-zA-Z0-9.-]+\(dot\)[a-zA-Z]{2,}',
            r'[a-zA-Z0-9._%+-]+\s*\[\s*at\s*\]\s*[a-zA-Z0-9.-]+\s*\[\s*dot\s*\]\s*[a-zA-Z]{2,}',
            # HTML attribute'larında
            r'href="mailto:([^"]+)"',
            r'data-email="([^"]+)"',
            r'href=\'mailto:([^\']+)\'',
            # JavaScript string'lerinde
            r'["\']([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["\']',
            # YENİ - Daha karmaşık obfuscation
            r'([a-zA-Z0-9._%+-]+)\s*@\s*([a-zA-Z0-9.-]+)\s*\.\s*([a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+)<!--.*?-->@<!--.*?-->([a-zA-Z0-9.-]+)<!--.*?-->.<!--.*?-->([a-zA-Z]{2,})'
        ]
        
        # Anti-detection için user agent listesi
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Proxy listesi (örnek)
        self.proxies = [
            # 'http://proxy1:port',
            # 'http://proxy2:port'
        ]
    
    def setup_sector_analyzers(self):
        """Sektör bazlı analiz parametreleri - YENİ"""
        self.sector_analyzers = {
            'mobilya': {
                'keywords': ['mobilya', 'furniture', 'koltuk', 'masa', 'sandalye', 'dolap', 'yatak'],
                'analyze_features': ['malzeme', 'renk', 'boyut', 'stil', 'fiyat_segmenti', 'üretim_yöntemi'],
                'image_focus': ['material_texture', 'color_palette', 'design_style', 'quality_indicators']
            },
            'tekstil': {
                'keywords': ['tekstil', 'textile', 'kumaş', 'fabric', 'iplik', 'örme', 'dokuma'],
                'analyze_features': ['kumaş_tipi', 'desen', 'renk', 'gramaj', 'üretim_kapasitesi', 'sertifikalar'],
                'image_focus': ['fabric_pattern', 'weave_type', 'color_quality', 'texture_detail']
            },
            'yazılım': {
                'keywords': ['yazılım', 'software', 'teknoloji', 'app', 'uygulama', 'sistem', 'digital'],
                'analyze_features': ['teknoloji_stack', 'proje_büyüklüğü', 'sektör_deneyimi', 'müşteri_segmenti'],
                'image_focus': ['ui_screenshots', 'architecture_diagrams', 'tech_logos', 'dashboard_views']
            },
            'üretim': {
                'keywords': ['üretim', 'imalat', 'manufacturing', 'fabrika', 'sanayi', 'endüstri'],
                'analyze_features': ['makine_parkı', 'kapasite', 'kalite_belgeleri', 'ihracat_oranı', 'hammadde'],
                'image_focus': ['machinery', 'production_line', 'facility_size', 'product_quality']
            },
            'gıda': {
                'keywords': ['gıda', 'food', 'yiyecek', 'içecek', 'restoran', 'cafe', 'catering'],
                'analyze_features': ['ürün_çeşitliliği', 'hijyen_sertifikaları', 'üretim_kapasitesi', 'dağıtım_ağı'],
                'image_focus': ['product_presentation', 'packaging', 'facility_cleanliness', 'menu_variety']
            }
        }
    
    def setup_driver(self):
        """Chrome driver'ı hazırla"""
        pass  # ChromeOptions'ı create_driver'da oluşturacağız
    
    def create_driver(self):
        """Yeni driver instance'ı oluştur - Anti-detection ile"""
        # Random user agent seç
        user_agent = random.choice(self.user_agents)
        
        # Önce undetected-chromedriver'ı dene
        if UC_AVAILABLE:
            try:
                # Undetected ChromeDriver options
                options = uc.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument(f'--user-agent={user_agent}')
                
                # Proxy kullanımı
                if self.use_proxy and self.proxies:
                    proxy = random.choice(self.proxies)
                    options.add_argument(f'--proxy-server={proxy}')
                
                # Driver oluştur
                driver = uc.Chrome(options=options, use_subprocess=True)
                
                # Ekstra anti-detection
                driver.execute_script('''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                ''')
                
                print("✅ Undetected ChromeDriver başarıyla yüklendi")
                return driver
                
            except Exception as e:
                print(f"⚠️ Undetected driver hatası: {str(e)}")
                # Standart driver'a geç
        
        # Standart Selenium ChromeDriver
        print("🔄 Standart ChromeDriver kullanılıyor...")
        chrome_options = Options()
        
        # Temel ayarlar
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={user_agent}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Headless mode (opsiyonel)
        # chrome_options.add_argument('--headless=new')
        
        # Proxy kullanımı
        if self.use_proxy and self.proxies:
            proxy = random.choice(self.proxies)
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # Anti-detection ayarları
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Performans optimizasyonları
        prefs = {
            "profile.managed_default_content_settings.images": 1,  # Resimleri yükle
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Anti-detection JavaScript
            driver.execute_script('''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['tr-TR', 'tr', 'en-US', 'en']
                });
            ''')
            
            return driver
            
        except Exception as e:
            print(f"❌ ChromeDriver başlatılamadı: {str(e)}")
            raise
    
    def simulate_human_behavior(self, driver):
        """İnsan davranışını simüle et - YENİ"""
        try:
            # Pencere boyutunu al
            window_size = driver.get_window_size()
            max_x = window_size['width'] - 100
            max_y = window_size['height'] - 100
            
            actions = ActionChains(driver)
            
            # Güvenli mouse hareketleri
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, min(800, max_x))
                y = random.randint(100, min(600, max_y))
                
                # Mevcut pozisyonu sıfırla
                actions.move_to_element_with_offset(driver.find_element(By.TAG_NAME, 'body'), 0, 0)
                actions.move_by_offset(x, y).perform()
                time.sleep(random.uniform(0.1, 0.3))
            
            # Rastgele scroll
            scroll_count = random.randint(2, 4)
            for _ in range(scroll_count):
                scroll_amount = random.randint(200, 500)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                time.sleep(random.uniform(0.5, 1.0))
            
            # Sayfanın başına dön
            driver.execute_script("window.scrollTo(0, 0)")
            
        except Exception as e:
            # Hata durumunda sadece basit scroll yap
            try:
                driver.execute_script("window.scrollBy(0, 300)")
                time.sleep(0.5)
                driver.execute_script("window.scrollTo(0, 0)")
            except:
                pass
    
    def wait_for_page_load(self, driver, timeout=15):
        """Sayfa tamamen yüklenene kadar bekle - GELİŞTİRİLDİ"""
        try:
            # DOM hazır olana kadar bekle
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # jQuery varsa AJAX istekleri için bekle
            try:
                WebDriverWait(driver, 5).until(
                    lambda d: d.execute_script(
                        'return typeof jQuery !== "undefined" ? jQuery.active == 0 : true'
                    )
                )
            except:
                pass
            
            # Lazy-load içerikler için scroll
            self.scroll_for_lazy_content(driver)
            
            # Dinamik içerik için ekstra bekleme
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"⚠️ Sayfa yükleme bekleme hatası: {str(e)}")
    
    def scroll_for_lazy_content(self, driver):
        """Lazy-load içerikleri yüklemek için scroll - YENİ"""
        try:
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            for i in range(3):  # Max 3 kez dene
                # Sayfanın sonuna scroll
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
                
                # Yeni içerik yüklendi mi kontrol et
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Başa dön
            driver.execute_script("window.scrollTo(0, 0);")
            
        except Exception as e:
            print(f"⚠️ Lazy content scroll hatası: {str(e)}")
    
    def extract_images_for_ai_analysis(self, driver, soup, limit=10):
        """AI analizi için görselleri topla - YENİ"""
        images_data = []
        
        try:
            # Ürün/hizmet görselleri bul
            img_selectors = [
                'img[class*="product"]',
                'img[class*="gallery"]',
                'img[class*="portfolio"]',
                'img[alt*="ürün"]',
                'img[alt*="product"]',
                '.product img',
                '.gallery img',
                'main img',
                'article img'
            ]
            
            all_images = []
            for selector in img_selectors:
                images = driver.find_elements(By.CSS_SELECTOR, selector)
                all_images.extend(images)
            
            # Unique ve büyük görselleri filtrele
            seen_srcs = set()
            for img in all_images[:limit * 2]:  # Daha fazla kontrol et
                try:
                    src = img.get_attribute('src') or img.get_attribute('data-src')
                    if not src or src in seen_srcs:
                        continue
                    
                    # Tam URL'e çevir
                    if not src.startswith('http'):
                        src = urljoin(driver.current_url, src)
                    
                    # Boyut kontrolü
                    width = img.get_attribute('width') or img.size.get('width', 0)
                    height = img.get_attribute('height') or img.size.get('height', 0)
                    
                    try:
                        width = int(width) if width else 0
                        height = int(height) if height else 0
                    except:
                        width, height = 0, 0
                    
                    # Küçük görselleri atla
                    if width < 200 or height < 200:
                        continue
                    
                    seen_srcs.add(src)
                    
                    # Görsel verisini al
                    alt_text = img.get_attribute('alt') or ''
                    title = img.get_attribute('title') or ''
                    
                    images_data.append({
                        'url': src,
                        'alt': alt_text,
                        'title': title,
                        'width': width,
                        'height': height,
                        'context': self.get_image_context(img, driver)
                    })
                    
                    if len(images_data) >= limit:
                        break
                        
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"⚠️ Görsel toplama hatası: {str(e)}")
        
        return images_data
    
    def get_image_context(self, img_element, driver):
        """Görselin etrafındaki metni al - YENİ"""
        try:
            # Parent element'leri kontrol et
            parent = driver.execute_script("return arguments[0].parentElement;", img_element)
            grandparent = driver.execute_script("return arguments[0].parentElement.parentElement;", img_element)
            
            # Yakın metinleri topla
            context_parts = []
            
            # Aynı container'daki metinler
            if parent:
                texts = driver.execute_script("""
                    return Array.from(arguments[0].querySelectorAll('h1, h2, h3, h4, h5, p, span'))
                        .map(el => el.innerText.trim())
                        .filter(text => text.length > 10 && text.length < 200);
                """, parent)
                context_parts.extend(texts[:3])
            
            # Bir üst container
            if grandparent and len(context_parts) < 2:
                texts = driver.execute_script("""
                    return Array.from(arguments[0].querySelectorAll('h1, h2, h3, h4, h5, p'))
                        .map(el => el.innerText.trim())
                        .filter(text => text.length > 10 && text.length < 200);
                """, grandparent)
                context_parts.extend(texts[:2])
            
            return ' | '.join(context_parts[:3])
            
        except:
            return ""
    
    def analyze_images_with_ai(self, images_data: List[Dict], sector: str = None) -> Dict:
        """GPT-4 Vision ile görsel analizi - YENİ"""
        if not self.use_ai_vision or not images_data:
            return {}
        
        try:
            # En önemli 5 görseli seç
            selected_images = images_data[:5]
            
            # Sektör bazlı analiz promptu
            sector_prompts = {
                'mobilya': "Malzeme tipi (ahşap/metal/plastik), renk paleti, tasarım stili (modern/klasik/minimalist), kalite seviyesi, hedef müşteri segmenti",
                'tekstil': "Kumaş tipi, desen/pattern, renk kalitesi, dokuma/örme tipi, bitim kalitesi",
                'üretim': "Makine tipi ve modernliği, üretim kapasitesi tahmini, fabrika düzeni, kalite kontrol sistemleri",
                'yazılım': "UI/UX kalitesi, kullanılan teknolojiler (logolardan), hedef platform, profesyonellik seviyesi",
                'gıda': "Ürün sunumu, paketleme kalitesi, hijyen standartları, ürün çeşitliliği"
            }
            
            base_prompt = f"""
            Bu görselleri analiz et ve şu bilgileri çıkar:
            
            1. Genel Gözlemler:
            - Ne tür ürünler/hizmetler görüyorsun?
            - Kalite seviyesi (düşük/orta/yüksek/premium)
            - Hedef müşteri kitlesi
            
            2. Detaylı Özellikler:
            {sector_prompts.get(sector, "Ürün/hizmet özellikleri, kullanılan malzemeler, tasarım detayları")}
            
            3. Profesyonellik:
            - Fotoğraf kalitesi ve profesyonelliği
            - Sunum şekli
            - Marka imajı
            
            Kısa ve net cevaplar ver. Türkçe yanıtla.
            """
            
            # API çağrısı için görselleri hazırla
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": base_prompt}
                    ]
                }
            ]
            
            # Görselleri ekle
            for img in selected_images:
                try:
                    # Görseli indir ve base64'e çevir
                    response = requests.get(img['url'], timeout=5)
                    if response.status_code == 200:
                        image_base64 = base64.b64encode(response.content).decode('utf-8')
                        
                        messages[0]["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        })
                        
                        # Context varsa ekle
                        if img.get('context'):
                            messages[0]["content"].append({
                                "type": "text",
                                "text": f"Görsel bağlamı: {img['context']}"
                            })
                except:
                    continue
            
            # GPT-4 Vision çağrısı
            try:
                # gpt-4o ile görsel analizi
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
            except Exception as e:
                if "model" in str(e).lower():
                    # Model bulunamazsa gpt-4-turbo'yu dene
                    try:
                        response = openai.chat.completions.create(
                            model="gpt-4-turbo",
                            messages=messages,
                            max_tokens=1000,
                            temperature=0.7
                        )
                    except:
                        # GPT-4-turbo de yoksa GPT-4'ü kullan
                        response = openai.chat.completions.create(
                            model="gpt-4",
                            messages=messages,
                            max_tokens=1000,
                            temperature=0.7
                        )
                else:
                    raise e
            
            ai_analysis = response.choices[0].message['content'].strip() if isinstance(response.choices[0].message, dict) else response.choices[0].message.content.strip()
            
            # Analizi yapılandır
            analysis_result = {
                'raw_analysis': ai_analysis,
                'extracted_features': self.parse_ai_vision_response(ai_analysis, sector),
                'images_analyzed': len(selected_images),
                'confidence_score': self.calculate_vision_confidence(ai_analysis)
            }
            
            return analysis_result
            
        except Exception as e:
            print(f"⚠️ AI görsel analizi hatası: {str(e)}")
            return {}
    
    def parse_ai_vision_response(self, ai_response: str, sector: str = None) -> Dict:
        """AI yanıtını yapılandır - YENİ"""
        features = {
            'quality_level': '',
            'target_audience': '',
            'materials': [],
            'colors': [],
            'style': '',
            'price_segment': '',
            'special_features': []
        }
        
        try:
            # Kalite seviyesi
            quality_patterns = [
                (r'(düşük|low)\s*kalite', 'düşük'),
                (r'(orta|medium|standart)\s*kalite', 'orta'),
                (r'(yüksek|high|iyi)\s*kalite', 'yüksek'),
                (r'(premium|lüks|luxury)', 'premium')
            ]
            
            for pattern, level in quality_patterns:
                if re.search(pattern, ai_response, re.I):
                    features['quality_level'] = level
                    break
            
            # Malzemeler
            material_keywords = ['ahşap', 'metal', 'plastik', 'cam', 'kumaş', 'deri', 'mermer', 
                               'granit', 'alüminyum', 'çelik', 'pamuk', 'polyester', 'ipek']
            
            for material in material_keywords:
                if material in ai_response.lower():
                    features['materials'].append(material)
            
            # Renkler
            color_keywords = ['beyaz', 'siyah', 'gri', 'kahverengi', 'mavi', 'yeşil', 'kırmızı',
                            'sarı', 'turuncu', 'mor', 'pembe', 'bej', 'krem', 'lacivert']
            
            for color in color_keywords:
                if color in ai_response.lower():
                    features['colors'].append(color)
            
            # Hedef kitle
            audience_patterns = [
                (r'(kurumsal|corporate|b2b)', 'Kurumsal/B2B'),
                (r'(bireysel|b2c|son kullanıcı)', 'Bireysel/B2C'),
                (r'(lüks|luxury|premium) segment', 'Lüks Segment'),
                (r'(orta gelir|middle class)', 'Orta Gelir'),
                (r'(genç|young|yeni nesil)', 'Genç Kitle')
            ]
            
            for pattern, audience in audience_patterns:
                if re.search(pattern, ai_response, re.I):
                    features['target_audience'] = audience
                    break
            
            # Stil
            style_keywords = {
                'modern': 'Modern',
                'klasik': 'Klasik',
                'minimalist': 'Minimalist',
                'industrial': 'Endüstriyel',
                'vintage': 'Vintage',
                'rustik': 'Rustik'
            }
            
            for keyword, style in style_keywords.items():
                if keyword in ai_response.lower():
                    features['style'] = style
                    break
            
        except Exception as e:
            print(f"⚠️ AI yanıt parse hatası: {str(e)}")
        
        return features
    
    def calculate_vision_confidence(self, ai_response: str) -> float:
        """AI görsel analizi güven skoru - YENİ"""
        score = 0.5  # Base score
        
        # Detaylı cevap = yüksek güven
        if len(ai_response) > 500:
            score += 0.2
        elif len(ai_response) > 200:
            score += 0.1
        
        # Spesifik terimler = yüksek güven
        specific_terms = ['malzeme', 'renk', 'boyut', 'kalite', 'tasarım', 'özellik']
        for term in specific_terms:
            if term in ai_response.lower():
                score += 0.05
        
        # Sayısal değerler = yüksek güven
        if re.search(r'\d+', ai_response):
            score += 0.1
        
        return min(score, 1.0)
    
    def detect_sector(self, soup: BeautifulSoup, page_text: str) -> str:
        """Firma sektörünü otomatik tespit et - YENİ"""
        sector_scores = {}
        
        # Her sektör için puan hesapla
        for sector, config in self.sector_analyzers.items():
            score = 0
            keywords = config['keywords']
            
            # Keyword eşleşmeleri
            for keyword in keywords:
                # Title'da
                if keyword in soup.title.text.lower() if soup.title else '':
                    score += 5
                
                # H1-H3 başlıklarda
                for tag in ['h1', 'h2', 'h3']:
                    headers = soup.find_all(tag)
                    for header in headers:
                        if keyword in header.text.lower():
                            score += 3
                
                # Genel metinde
                occurrences = page_text.lower().count(keyword)
                score += min(occurrences * 0.5, 10)  # Max 10 puan
            
            sector_scores[sector] = score
        
        # En yüksek skorlu sektörü döndür
        if sector_scores:
            detected_sector = max(sector_scores, key=sector_scores.get)
            if sector_scores[detected_sector] > 5:  # Minimum eşik
                return detected_sector
        
        return 'genel'
    
    def extract_advanced_business_info(self, soup: BeautifulSoup, sector: str) -> Dict:
        """Sektöre özel gelişmiş iş bilgisi çıkarma - YENİ"""
        business_info = {
            'sector': sector,
            'detailed_services': [],
            'technical_capabilities': [],
            'certifications': [],
            'client_references': [],
            'competitive_advantages': [],
            'company_values': [],
            'sustainability': '',
            'innovation_level': '',
            'export_info': '',
            'production_capacity': ''
        }
        
        try:
            # Sertifikalar
            cert_patterns = ['ISO', 'CE', 'TSE', 'OHSAS', 'HACCP', 'GMP', 'FSC', 'OEKO-TEX']
            page_text = soup.get_text()
            
            for cert in cert_patterns:
                if re.search(rf'{cert}[\s-]?\d*', page_text, re.I):
                    matches = re.findall(rf'{cert}[\s-]?\d*', page_text, re.I)
                    business_info['certifications'].extend(matches[:3])
            
            # Müşteri referansları
            ref_sections = soup.find_all(['div', 'section'], class_=re.compile('reference|referans|client|müşteri|portfolio', re.I))
            for section in ref_sections[:2]:
                # Logo veya isim ara
                ref_items = section.find_all(['img', 'h3', 'h4', 'span'])
                for item in ref_items[:10]:
                    if item.name == 'img':
                        alt = item.get('alt', '')
                        if alt and len(alt) > 2:
                            business_info['client_references'].append(alt)
                    else:
                        text = item.text.strip()
                        if 10 < len(text) < 50:
                            business_info['client_references'].append(text)
            
            # Rekabet avantajları
            advantage_keywords = ['avantaj', 'fark', 'üstün', 'özel', 'unique', 'advantage', 'neden biz']
            for keyword in advantage_keywords:
                pattern = rf'{keyword}[^.]*[.:]\s*([^.]+\.)'
                matches = re.findall(pattern, page_text, re.I)
                for match in matches[:3]:
                    if 20 < len(match) < 200:
                        business_info['competitive_advantages'].append(match.strip())
            
            # Şirket değerleri
            value_keywords = ['değer', 'value', 'ilke', 'principle', 'misyon', 'vizyon']
            for keyword in value_keywords:
                elements = soup.find_all(text=re.compile(keyword, re.I))
                for elem in elements[:2]:
                    parent = elem.parent
                    if parent:
                        text = parent.get_text(strip=True)
                        if 30 < len(text) < 300:
                            business_info['company_values'].append(text)
            
            # Sürdürülebilirlik
            sustain_keywords = ['sürdürülebilir', 'sustainable', 'yeşil', 'green', 'çevre', 'environment', 'eko']
            for keyword in sustain_keywords:
                if keyword in page_text.lower():
                    # Context'i al
                    pattern = rf'[^.]*{keyword}[^.]*\.'
                    match = re.search(pattern, page_text, re.I)
                    if match:
                        business_info['sustainability'] = match.group(0)[:300]
                        break
            
            # İnovasyon seviyesi
            innovation_keywords = ['ar-ge', 'r&d', 'inovasyon', 'innovation', 'yenilik', 'patent', 'teknoloji']
            innovation_score = 0
            for keyword in innovation_keywords:
                if keyword in page_text.lower():
                    innovation_score += page_text.lower().count(keyword)
            
            if innovation_score > 10:
                business_info['innovation_level'] = 'Yüksek'
            elif innovation_score > 5:
                business_info['innovation_level'] = 'Orta'
            else:
                business_info['innovation_level'] = 'Standart'
            
            # İhracat bilgisi
            export_keywords = ['ihracat', 'export', 'yurtdışı', 'global', 'ülke', 'country']
            for keyword in export_keywords:
                pattern = rf'{keyword}[^.]*(\d+)[^.]*'
                match = re.search(pattern, page_text, re.I)
                if match:
                    business_info['export_info'] = match.group(0)[:200]
                    break
            
            # Üretim kapasitesi (sektöre göre)
            if sector in ['üretim', 'tekstil', 'mobilya']:
                capacity_patterns = [
                    r'(\d+\.?\d*)\s*(ton|adet|m2|metre|parça|birim)\/?(gün|ay|yıl)',
                    r'kapasit\w*\s*[:]\s*(\d+\.?\d*)',
                    r'üretim\s*[:]\s*(\d+\.?\d*)',
                    r'(\d+\.?\d*)\s*ünite'
                ]
                
                for pattern in capacity_patterns:
                    match = re.search(pattern, page_text, re.I)
                    if match:
                        business_info['production_capacity'] = match.group(0)
                        break
            
        except Exception as e:
            print(f"⚠️ Gelişmiş iş bilgisi çıkarma hatası: {str(e)}")
        
        return business_info
    
    def extract_hidden_emails(self, driver, soup) -> List[Dict]:
        """JavaScript ve gizli email'leri bul - YENİ"""
        hidden_emails = []
        
        try:
            # 1. JavaScript değişkenlerinden
            js_email_patterns = [
                r'var\s+\w*email\w*\s*=\s*["\']([^"\']+)["\']',
                r'const\s+\w*email\w*\s*=\s*["\']([^"\']+)["\']',
                r'email:\s*["\']([^"\']+)["\']',
                r'contact:\s*\{[^}]*email:\s*["\']([^"\']+)["\'][^}]*\}'
            ]
            
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    for pattern in js_email_patterns:
                        matches = re.findall(pattern, script.string, re.I)
                        for match in matches:
                            email = self.clean_email(match)
                            if self.validate_email_improved(email):
                                hidden_emails.append({
                                    'email': email,
                                    'type': 'hidden_js',
                                    'source': 'javascript'
                                })
            
            # 2. Data attribute'larından
            data_attrs = driver.execute_script("""
                return Array.from(document.querySelectorAll('*'))
                    .map(el => Array.from(el.attributes)
                        .filter(attr => attr.name.startsWith('data-') && attr.value.includes('@'))
                        .map(attr => attr.value))
                    .flat();
            """)
            
            for attr_value in data_attrs:
                email_match = re.search(self.email_patterns[0], attr_value)
                if email_match:
                    email = self.clean_email(email_match.group(0))
                    if self.validate_email_improved(email):
                        hidden_emails.append({
                            'email': email,
                            'type': 'data_attribute',
                            'source': 'html_attribute'
                        })
            
            # 3. AJAX endpoint'lerini kontrol
            ajax_endpoints = [
                '/api/contact',
                '/api/info',
                '/wp-json/contact/v1/info',
                '/.well-known/contact.json'
            ]
            
            base_url = driver.current_url
            for endpoint in ajax_endpoints:
                try:
                    api_url = urljoin(base_url, endpoint)
                    response = requests.get(api_url, timeout=3, headers={'User-Agent': random.choice(self.user_agents)})
                    
                    if response.status_code == 200:
                        # JSON response'da email ara
                        try:
                            data = response.json()
                            json_str = json.dumps(data)
                            email_matches = re.findall(self.email_patterns[0], json_str)
                            for match in email_matches:
                                email = self.clean_email(match)
                                if self.validate_email_improved(email):
                                    hidden_emails.append({
                                        'email': email,
                                        'type': 'api_endpoint',
                                        'source': endpoint
                                    })
                        except:
                            pass
                except:
                    continue
            
            # 4. Meta tag'lerden
            meta_emails = soup.find_all('meta', attrs={'name': re.compile('contact|email', re.I)})
            for meta in meta_emails:
                content = meta.get('content', '')
                if '@' in content:
                    email = self.clean_email(content)
                    if self.validate_email_improved(email):
                        hidden_emails.append({
                            'email': email,
                            'type': 'meta_tag',
                            'source': 'html_meta'
                        })
            
        except Exception as e:
            print(f"⚠️ Gizli email bulma hatası: {str(e)}")
        
        return hidden_emails
    
    def extract_structured_data(self, soup) -> Dict:
        """JSON-LD ve schema.org verilerini çıkar - YENİ"""
        structured_data = {
            'organization': {},
            'contact': {},
            'social_profiles': [],
            'opening_hours': '',
            'location': {}
        }
        
        try:
            # JSON-LD script'lerini bul
            json_lds = soup.find_all('script', type='application/ld+json')
            
            for json_ld in json_lds:
                try:
                    data = json.loads(json_ld.string)
                    
                    # Organization schema
                    if data.get('@type') in ['Organization', 'Corporation', 'LocalBusiness']:
                        structured_data['organization'] = {
                            'name': data.get('name', ''),
                            'description': data.get('description', ''),
                            'url': data.get('url', ''),
                            'logo': data.get('logo', ''),
                            'foundingDate': data.get('foundingDate', ''),
                            'numberOfEmployees': data.get('numberOfEmployees', '')
                        }
                        
                        # Contact bilgileri
                        if 'contactPoint' in data:
                            contact = data['contactPoint']
                            if isinstance(contact, dict):
                                structured_data['contact'] = {
                                    'telephone': contact.get('telephone', ''),
                                    'email': contact.get('email', ''),
                                    'contactType': contact.get('contactType', '')
                                }
                        
                        # Sosyal medya
                        if 'sameAs' in data:
                            structured_data['social_profiles'] = data['sameAs'] if isinstance(data['sameAs'], list) else [data['sameAs']]
                        
                        # Adres
                        if 'address' in data:
                            addr = data['address']
                            if isinstance(addr, dict):
                                structured_data['location'] = {
                                    'streetAddress': addr.get('streetAddress', ''),
                                    'addressLocality': addr.get('addressLocality', ''),
                                    'addressRegion': addr.get('addressRegion', ''),
                                    'postalCode': addr.get('postalCode', ''),
                                    'addressCountry': addr.get('addressCountry', '')
                                }
                        
                        # Çalışma saatleri
                        if 'openingHoursSpecification' in data:
                            hours = data['openingHoursSpecification']
                            if isinstance(hours, list):
                                structured_data['opening_hours'] = ', '.join([
                                    f"{h.get('dayOfWeek', '')}: {h.get('opens', '')}-{h.get('closes', '')}"
                                    for h in hours[:5]
                                ])
                    
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"⚠️ Structured data çıkarma hatası: {str(e)}")
        
        return structured_data
    
    def calculate_company_score(self, data: Dict) -> Dict:
        """Firma için detaylı skorlama - YENİ"""
        scores = {
            'overall': 0,
            'digital_presence': 0,
            'professionalism': 0,
            'market_position': 0,
            'innovation': 0,
            'details': {}
        }
        
        try:
            # Dijital varlık skoru
            digital_factors = {
                'has_ssl': 10,
                'responsive_design': 10,
                'social_media_count': len(data.get('social_media', {})) * 5,
                'structured_data': 10 if data.get('advanced_features', {}).get('structured_data', {}).get('organization') else 0,
                'email_variety': min(len(data.get('emails', [])) * 3, 15),
                'content_quality': 10 if len(data.get('text_content', '')) > 1000 else 5
            }
            
            scores['digital_presence'] = min(sum(digital_factors.values()), 100)
            scores['details']['digital_factors'] = digital_factors
            
            # Profesyonellik skoru
            prof_factors = {
                'has_about': 10 if data.get('about_text') else 0,
                'has_services': 10 if data.get('services') else 0,
                'has_team': 10 if data.get('team_size_estimate') != 'Bilinmiyor' else 0,
                'certifications': min(len(data.get('business_info', {}).get('certifications', [])) * 10, 30),
                'image_quality': data.get('ai_vision_analysis', {}).get('confidence_score', 0.5) * 20,
                'contact_info': 10 if data.get('phone_numbers') else 5
            }
            
            scores['professionalism'] = min(sum(prof_factors.values()), 100)
            scores['details']['professionalism_factors'] = prof_factors
            
            # Pazar konumu
            market_factors = {
                'client_references': min(len(data.get('business_info', {}).get('client_references', [])) * 5, 25),
                'export_activity': 20 if data.get('business_info', {}).get('export_info') else 0,
                'pricing_transparency': 15 if data.get('pricing') else 0,
                'competitive_advantages': min(len(data.get('business_info', {}).get('competitive_advantages', [])) * 10, 30)
            }
            
            scores['market_position'] = min(sum(market_factors.values()), 100)
            scores['details']['market_factors'] = market_factors
            
            # İnovasyon skoru
            innovation_level = data.get('business_info', {}).get('innovation_level', 'Standart')
            innovation_map = {'Yüksek': 80, 'Orta': 50, 'Standart': 20}
            scores['innovation'] = innovation_map.get(innovation_level, 20)
            
            # Genel skor
            scores['overall'] = (
                scores['digital_presence'] * 0.25 +
                scores['professionalism'] * 0.35 +
                scores['market_position'] * 0.25 +
                scores['innovation'] * 0.15
            )
            
        except Exception as e:
            print(f"⚠️ Skorlama hatası: {str(e)}")
        
        return scores
    
    def generate_enhanced_ai_summary(self, data: Dict) -> str:
        """Gelişmiş AI özeti - YENİ"""
        try:
            # OpenAI API key kontrolü
            if not openai.api_key:
                return self.generate_enhanced_simple_summary(data)
            
            # Tüm veriyi birleştir
            context = f"""
            TEMEL BİLGİLER:
            Website: {data.get('website')}
            Başlık: {data.get('title')}
            Sektör: {data.get('business_info', {}).get('sector', 'Belirtilmemiş')}
            Takım Büyüklüğü: {data.get('team_size_estimate')}
            
            HİZMETLER VE ÜRÜNLER:
            Ana Hizmetler: {', '.join(data.get('services', [])[:5])}
            Ürünler: {', '.join([p.get('name', '') for p in data.get('products', [])[:5]])}
            Fiyat Bilgisi: {', '.join([p.get('price', '') for p in data.get('pricing', [])[:3]])}
            
            DETAYLI ANALİZ:
            Teknolojiler: {data.get('advanced_features', {}).get('technologies_used', [])}
            Sertifikalar: {data.get('business_info', {}).get('certifications', [])}
            İnovasyon Seviyesi: {data.get('business_info', {}).get('innovation_level')}
            İhracat: {data.get('business_info', {}).get('export_info', 'Bilgi yok')}
            Müşteri Referansları: {len(data.get('business_info', {}).get('client_references', []))} adet
            
            GÖRSEL ANALİZ (AI):
            {data.get('ai_vision_analysis', {}).get('raw_analysis', 'Görsel analiz yapılmadı')}
            
            REKABET AVANTAJLARI:
            {', '.join(data.get('business_info', {}).get('competitive_advantages', [])[:3])}
            
            SKORLAMA:
            Genel Skor: {data.get('company_score', {}).get('overall', 0):.1f}/100
            Dijital Varlık: {data.get('company_score', {}).get('digital_presence', 0)}/100
            Profesyonellik: {data.get('company_score', {}).get('professionalism', 0)}/100
            """
            
            # GPT ile analiz
            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": """Sen uzman bir B2B iş analisti ve pazar araştırmacısısın. 
                            Firmaları detaylı analiz edip, potansiyel iş fırsatlarını belirlersin.
                            Analizlerinde somut, aksiyona yönelik ve değer katan bilgiler verirsin."""
                        },
                        {
                            "role": "user",
                            "content": f"""
                            Aşağıdaki firma verilerini analiz et ve kapsamlı bir B2B değerlendirmesi yap:
                            
                            {context}
                            
                            Lütfen şu başlıkları içeren detaylı bir analiz hazırla:
                            
                            1. FİRMA PROFİLİ (2 cümle)
                            - Ne yapıyor, hangi sektörde, büyüklük
                            
                            2. ÜRÜN/HİZMET ANALİZİ (3 cümle)
                            - Ana ürünler, kalite seviyesi, hedef kitle
                            - Fiyat segmenti ve rekabetçilik
                            
                            3. PAZAR KONUMU (2 cümle)
                            - Rakiplere göre durumu
                            - Güçlü ve zayıf yönler
                            
                            4. İŞ FIRSATLARI (3 madde)
                            - Bu firma ile nasıl iş yapılabilir
                            - Potansiyel işbirliği alanları
                            - Dikkat edilmesi gerekenler
                            
                            5. RİSK VE FIRSATLAR (2 madde)
                            - Ana riskler
                            - Ana fırsatlar
                            
                            6. TAVSİYE (1 cümle)
                            - Bu firma ile çalışılmalı mı? Neden?
                            
                            Maksimum 300 kelime kullan. Net, somut ve aksiyona yönelik ol.
                            """
                        }
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
            except Exception as e:
                if "model" in str(e).lower():
                    # GPT-4 yoksa GPT-3.5 kullan
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "Sen bir B2B iş analisti uzmanısın. Firmaları analiz edip öz ve bilgilendirici özetler çıkarıyorsun."
                            },
                            {
                                "role": "user",
                                "content": f"""
                                Aşağıdaki firma verilerini analiz et ve kısa bir B2B özeti hazırla:
                                
                                {context}
                                
                                Özet şunları içermeli:
                                1. Firma ne yapıyor? (1 cümle)
                                2. Ana hizmetleri/ürünleri (1 cümle)
                                3. Pazar konumu ve potansiyeli (1 cümle)
                                4. İş yapma önerisi (1 cümle)
                                
                                Maksimum 150 kelime kullan.
                                """
                            }
                        ],
                        temperature=0.7,
                        max_tokens=400
                    )
                else:
                    raise e
            
            return response.choices[0].message['content'].strip() if isinstance(response.choices[0].message, dict) else response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ Gelişmiş AI özet hatası: {str(e)}")
            return self.generate_enhanced_simple_summary(data)
    
    def generate_enhanced_simple_summary(self, data: Dict) -> str:
        """AI olmadan gelişmiş özet - YENİ"""
        score = data.get('company_score', {}).get('overall', 0)
        sector = data.get('business_info', {}).get('sector', 'genel')
        
        summary = f"""
        📊 FİRMA ANALİZİ
        
        Firma: {data.get('title', 'Bilinmiyor')}
        Sektör: {sector.capitalize()}
        Büyüklük: {data.get('team_size_estimate', 'Bilinmiyor')}
        Genel Skor: {score:.1f}/100
        
        🎯 HİZMETLER:
        {', '.join(data.get('services', ['Belirtilmemiş'])[:5])}
        
        💡 ÖZEL BİLGİLER:
        • İnovasyon: {data.get('business_info', {}).get('innovation_level', 'Standart')}
        • Sertifikalar: {', '.join(data.get('business_info', {}).get('certifications', ['Yok'])[:3])}
        • Email Sayısı: {len(data.get('emails', []))} adet bulundu
        
        🔍 DEĞERLENDİRME:
        """
        
        if score > 70:
            summary += "✅ Yüksek potansiyelli, profesyonel bir firma. İşbirliği için uygun."
        elif score > 50:
            summary += "⚡ Orta seviye bir firma. Detaylı değerlendirme gerekli."
        else:
            summary += "⚠️ Dijital varlığı zayıf. Dikkatli yaklaşılmalı."
        
        # Sektöre özel notlar
        sector_notes = {
            'mobilya': "\n📌 NOT: Ürün kalitesi ve tasarım görsellere göre değerlendirilmeli.",
            'yazılım': "\n📌 NOT: Teknik yetkinlik ve referanslar önemli.",
            'üretim': "\n📌 NOT: Kapasite ve kalite belgeleri kritik.",
            'tekstil': "\n📌 NOT: Minimum sipariş miktarı ve teslim süreleri sorulmalı."
        }
        
        summary += sector_notes.get(sector, "\n📌 NOT: Detaylı görüşme ile bilgiler teyit edilmeli.")
        
        return summary
    
    def scrape_website(self, url: str, company_name: str = "") -> Dict:
        """
        Web sitesini AI destekli tara ve detaylı bilgi topla - GELİŞTİRİLMİŞ
        
        Args:
            url: Website URL'i
            company_name: Firma adı
        
        Returns:
            Toplanan tüm bilgiler
        """
        if not url:
            return {}
        
        # URL'i düzelt
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        driver = None
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                driver = self.create_driver()
                print(f"🌐 {url} sitesi AI destekli analiz ediliyor...")
                
                # Anti-detection için random delay
                time.sleep(random.uniform(1, 3))
                
                driver.get(url)
                
                # İnsan davranışı simülasyonu
                self.simulate_human_behavior(driver)
                
                # Sayfa yüklenmesini bekle
                self.wait_for_page_load(driver, timeout=20)
                
                # Sayfa kaynağını al
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                page_text = self.get_text_content(soup)
                
                # Domain'i al
                domain = self.clean_domain(url)
                
                # Sektörü tespit et
                detected_sector = self.detect_sector(soup, page_text)
                print(f"🏭 Tespit edilen sektör: {detected_sector}")
                
                # Temel bilgileri topla - DATABASE UYUMLU
                data = {
                    'website': url,
                    'domain': domain,
                    'title': self.get_page_title(soup),
                    'description': self.get_meta_description(soup),
                    'keywords': self.get_meta_keywords(soup),
                    'emails': [],
                    'phone_numbers': self.extract_phone_numbers(page_source),
                    'social_media': self.extract_social_media(soup),
                    'business_info': self.extract_advanced_business_info(soup, detected_sector),
                    'text_content': page_text,
                    'services': self.extract_services(soup),
                    'products': self.extract_products(soup),
                    'pricing': self.extract_pricing_info(soup),
                    'about_text': self.extract_about_text(soup),
                    'team_size_estimate': self.estimate_team_size(soup),
                    'industry_keywords': self.extract_industry_keywords(soup),
                    'contact_page_url': None,
                    # Yeni özellikler - ayrı dictionary'de saklayacağız
                    'advanced_features': {
                        'technologies_used': self.detect_technologies(soup, driver),
                        'structured_data': self.extract_structured_data(soup),
                        'images_data': []
                    }
                }
                
                # Ana sayfadan email topla - GELİŞTİRİLDİ
                main_page_emails = self.extract_emails_advanced(page_source, domain)
                data['emails'].extend(main_page_emails)
                
                # Gizli email'leri bul - YENİ
                hidden_emails = self.extract_hidden_emails(driver, soup)
                for email in hidden_emails:
                    self.add_email_if_unique(data['emails'], email)
                
                # AI için görselleri topla
                if self.use_ai_vision:
                    print("🖼️ Görseller toplanıyor AI analizi için...")
                    data['advanced_features']['images_data'] = self.extract_images_for_ai_analysis(driver, soup)
                
                # Alt sayfaları tara
                subpages_data = self.scrape_important_subpages(driver, url, domain)
                
                # Alt sayfalardaki emailleri ekle
                for subpage_name, subpage_info in subpages_data.items():
                    if 'emails' in subpage_info:
                        for email in subpage_info['emails']:
                            self.add_email_if_unique(data['emails'], email)
                    
                    # Contact page URL'i kaydet
                    if 'contact' in subpage_name and subpage_info.get('url'):
                        data['contact_page_url'] = subpage_info['url']
                
                # Scraped data'yı kaydet
                data['scraped_data'] = subpages_data
                
                # Email'leri skorla ve sırala
                data['emails'] = self.score_and_sort_emails(data['emails'])
                
                # AI görsel analizi
                if self.use_ai_vision and data['advanced_features']['images_data']:
                    print("🤖 AI ile görsel analiz yapılıyor...")
                    data['ai_vision_analysis'] = self.analyze_images_with_ai(
                        data['advanced_features']['images_data'], 
                        detected_sector
                    )
                
                # Firma skorlaması - YENİ
                data['company_score'] = self.calculate_company_score(data)
                
                # Facebook ve Instagram analizi
                if 'facebook' in data['social_media'] or 'instagram' in data['social_media']:
                    print("📱 Facebook ve Instagram analizi yapılıyor...")
                    data['social_media_details'] = {}
                    
                    # Facebook analizi
                    if 'facebook' in data['social_media']:
                        fb_data = self.scrape_facebook_page(data['social_media']['facebook'])
                        data['social_media_details']['facebook'] = fb_data
                    
                    # Instagram analizi
                    if 'instagram' in data['social_media']:
                        ig_data = self.scrape_instagram_profile(data['social_media']['instagram'])
                        data['social_media_details']['instagram'] = ig_data
                
                # Gelişmiş AI özeti
                print("📝 AI destekli detaylı özet oluşturuluyor...")
                data['ai_summary'] = self.generate_enhanced_ai_summary(data)
                
                print(f"✅ Analiz tamamlandı!")
                print(f"📧 {len(data['emails'])} email bulundu")
                print(f"🏆 Firma skoru: {data['company_score']['overall']:.1f}/100")
                
                # Sosyal medya özeti
                if 'social_analysis' in data['social_media']:
                    social_score = data['social_media']['social_analysis']['overall_social_score']
                    print(f"📱 Sosyal medya skoru: {social_score}/100")
                
                return data
                
            except Exception as e:
                retry_count += 1
                print(f"❌ Web scraping hatası (Deneme {retry_count}/{max_retries}): {str(e)}")
                
                if retry_count < max_retries:
                    print("⏳ Tekrar denenecek...")
                    time.sleep(random.uniform(3, 5))
                else:
                    # Son denemede de hata varsa basit veri döndür
                    domain = self.clean_domain(url) if url else "example.com"
                    return {
                        'website': url,
                        'domain': domain,
                        'emails': [],
                        'ai_summary': f"Hata nedeniyle site analiz edilemedi: {str(e)}",
                        'phone_numbers': [],
                        'social_media': {},
                        'services': [],
                        'products': [],
                        'business_info': {},
                        'pricing': [],
                        'about_text': '',
                        'team_size_estimate': 'Bilinmiyor',
                        'industry_keywords': [],
                        'text_content': '',
                        'scraped_data': {},
                        'company_score': {'overall': 0},
                        'advanced_features': {}  # Boş advanced features
                    }
            finally:
                if driver:
                    driver.quit()
    
    def detect_technologies(self, soup: BeautifulSoup, driver) -> List[str]:
        """Website'de kullanılan teknolojileri tespit et - YENİ"""
        technologies = []
        
        try:
            # JavaScript framework'leri
            js_frameworks = {
                'React': ['_react', 'react-app', '__REACT', 'data-reactroot'],
                'Angular': ['ng-app', 'ng-scope', 'angular', '__ANGULAR__'],
                'Vue': ['v-for', 'v-if', '__VUE__', 'data-v-'],
                'jQuery': ['jquery', 'jQuery', '$'],
                'Bootstrap': ['bootstrap', 'btn-primary', 'container-fluid'],
                'Tailwind': ['tailwind', 'tw-', 'text-gray-'],
                'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
                'Shopify': ['shopify', 'myshopify', 'cdn.shopify'],
                'Wix': ['wix', 'parastorage', 'wixstatic'],
                'Laravel': ['laravel', 'csrf-token']
            }
            
            # HTML içinde ara
            html_content = str(soup)
            for tech, patterns in js_frameworks.items():
                for pattern in patterns:
                    if pattern in html_content:
                        technologies.append(tech)
                        break
            
            # Meta generator
            generator = soup.find('meta', attrs={'name': 'generator'})
            if generator:
                content = generator.get('content', '').lower()
                technologies.append(content.split()[0].capitalize())
            
            # JavaScript global değişkenleri kontrol et
            try:
                js_techs = driver.execute_script("""
                    const techs = [];
                    if (typeof React !== 'undefined') techs.push('React');
                    if (typeof angular !== 'undefined') techs.push('Angular');
                    if (typeof Vue !== 'undefined') techs.push('Vue');
                    if (typeof jQuery !== 'undefined' || typeof $ !== 'undefined') techs.push('jQuery');
                    if (typeof wp !== 'undefined') techs.push('WordPress');
                    if (typeof Shopify !== 'undefined') techs.push('Shopify');
                    return techs;
                """)
                technologies.extend(js_techs)
            except:
                pass
            
            # Analytics ve tracking
            if re.search(r'google-analytics|gtag|ga\(', html_content):
                technologies.append('Google Analytics')
            if 'facebook.com/tr' in html_content:
                technologies.append('Facebook Pixel')
            if 'googletagmanager' in html_content:
                technologies.append('Google Tag Manager')
            
            # Hosting/CDN
            if 'cloudflare' in html_content:
                technologies.append('Cloudflare')
            if 'amazonaws' in html_content:
                technologies.append('AWS')
            
            # Unique liste
            technologies = list(set(technologies))
            
        except Exception as e:
            print(f"⚠️ Teknoloji tespiti hatası: {str(e)}")
        
        return technologies
    
    # Mevcut fonksiyonların geri kalanı aynı kalacak...
    # (clean_domain, add_email_if_unique, extract_emails_advanced, vb.)
    # Bunlar zaten kodunuzda var ve değişmeyecek
    
    def clean_domain(self, url_or_domain: str) -> str:
        """URL veya domain'den temiz domain çıkar"""
        if not url_or_domain:
            return ""
            
        # URL parse et
        if url_or_domain.startswith(('http://', 'https://')):
            parsed = urlparse(url_or_domain)
            domain = parsed.netloc
        else:
            domain = url_or_domain
        
        # www. ve alt domainleri temizle
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Port numarasını kaldır
        if ':' in domain:
            domain = domain.split(':')[0]
        
        return domain.lower().strip()
    
    def add_email_if_unique(self, email_list: List[Dict], new_email: Dict) -> None:
        """Email listesine duplicate kontrolü ile ekle"""
        email_addr = new_email['email'].lower()
        
        # Mevcut email'i bul
        existing = next((e for e in email_list if e['email'].lower() == email_addr), None)
        
        if existing:
            # Daha yüksek skorlu ise güncelle
            if new_email.get('score', 0) > existing.get('score', 0):
                existing.update(new_email)
        else:
            email_list.append(new_email)
    
    def clean_email(self, email: str) -> str:
        """Email adresini temizle"""
        # Obfuscated format dönüşümleri
        email = re.sub(r'\s*\[\s*at\s*\]\s*', '@', email, flags=re.IGNORECASE)
        email = re.sub(r'\s*\(\s*at\s*\)\s*', '@', email, flags=re.IGNORECASE)
        email = re.sub(r'\s*\[\s*dot\s*\]\s*', '.', email, flags=re.IGNORECASE)
        email = re.sub(r'\s*\(\s*dot\s*\)\s*', '.', email, flags=re.IGNORECASE)
        
        # Boşlukları kaldır
        email = re.sub(r'\s+', '', email)
        
        # mailto: prefix'ini kaldır
        email = email.replace('mailto:', '')
        
        # Küçük harfe çevir
        email = email.lower()
        
        # Başındaki ve sonundaki gereksiz karakterleri kaldır
        email = email.strip(' .,;:!?<>"\'()[]{}')
        
        return email
    
    def validate_email_improved(self, email: str) -> bool:
        """Email adresini doğrula"""
        # Daha esnek email regex
        email_regex = r'^[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9][a-zA-Z0-9.\-]*\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return False
        
        # Domain kontrolü
        try:
            local, domain = email.split('@')
            
            # Local part kontrolü
            if len(local) < 1 or len(local) > 64:
                return False
            
            # Domain kontrolü
            if len(domain) < 4:  # x.co gibi kısa domainler için minimum
                return False
            
            # Çok fazla nokta kontrolü
            if '..' in email:
                return False
                
        except:
            return False
        
        # Yaygın geçersiz emailler
        invalid_patterns = [
            'example.', 'test.', 'demo.', 'sample.',
            '.png', '.jpg', '.jpeg', '.gif', '.pdf',
            'yourname@', 'email@', 'name@', '@domain',
            'noreply@', 'donotreply@', 'no-reply@'
        ]
        
        for pattern in invalid_patterns:
            if pattern in email:
                return False
        
        # Uzunluk kontrolü
        if len(email) < 6 or len(email) > 254:
            return False
        
        return True
    
    def determine_email_type(self, email: str) -> str:
        """Email tipini belirle"""
        email_lower = email.lower()
        local_part = email_lower.split('@')[0]
        
        # C-Level
        if any(title in local_part for title in ['ceo', 'cto', 'cfo', 'coo', 'cmo', 'founder', 'owner']):
            return 'c_level'
        
        # Departman bazlı
        departments = {
            'sales': ['sales', 'satis', 'pazarlama', 'marketing', 'business'],
            'support': ['support', 'destek', 'help', 'yardim', 'musteri'],
            'info': ['info', 'bilgi', 'general', 'genel', 'contact', 'iletisim'],
            'hr': ['hr', 'ik', 'kariyer', 'career', 'jobs', 'ise-alim'],
            'tech': ['tech', 'it', 'dev', 'engineering', 'yazilim', 'bilgi-islem']
        }
        
        for dept, keywords in departments.items():
            if any(kw in local_part for kw in keywords):
                return dept
        
        # Kişisel email formatı kontrolü
        if re.match(r'^[a-z]+[\.\-_][a-z]+$', local_part):
            return 'personal'
        
        return 'general'
    
    def calculate_email_score_by_type(self, email_type: str) -> int:
        """Email tipine göre skor hesapla"""
        scores = {
            'c_level': 100,
            'personal': 85,
            'sales': 80,
            'info': 70,
            'support': 60,
            'hr': 50,
            'tech': 65,
            'general': 55
        }
        return scores.get(email_type, 50)
    
    def guess_position_from_email(self, email: str) -> str:
        """Email adresinden pozisyon tahmin et"""
        email_local = email.split('@')[0].lower()
        
        positions = {
            'ceo': 'CEO',
            'cto': 'CTO',
            'cfo': 'CFO',
            'founder': 'Founder',
            'owner': 'Owner',
            'director': 'Director',
            'manager': 'Manager',
            'sales': 'Sales',
            'marketing': 'Marketing',
            'support': 'Support',
            'info': 'General',
            'admin': 'Admin'
        }
        
        for key, position in positions.items():
            if key in email_local:
                return position
        
        return ''
    
    def score_and_sort_emails(self, emails: List[Dict]) -> List[Dict]:
        """Email'leri skorla ve sırala"""
        # Önce duplicate'leri temizle
        unique_emails = {}
        for email in emails:
            email_addr = email['email'].lower()
            if email_addr not in unique_emails or email['score'] > unique_emails[email_addr]['score']:
                unique_emails[email_addr] = email
        
        # Listeye çevir ve sırala
        sorted_emails = sorted(unique_emails.values(), key=lambda x: x['score'], reverse=True)
        
        return sorted_emails
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Telefon numaralarını çıkar"""
        phone_patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b',
            r'\b0\d{3}[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b',
            r'\b\+90[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b',
            r'\b\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b',
            r'\b0[-.\s]?\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b',
            r'\b\+90[-.\s]?\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2}\b'
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        # Temizleme ve doğrulama
        valid_phones = []
        seen_numbers = set()
        
        for phone in phones:
            # Sadece rakamları al
            digits = re.sub(r'\D', '', phone)
            
            # Türkiye telefon numarası uzunluğu kontrolü
            if 10 <= len(digits) <= 12 and digits not in seen_numbers:
                seen_numbers.add(digits)
                valid_phones.append(phone)
        
        return valid_phones[:5]  # Max 5 telefon
    
    def extract_social_media(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Sosyal medya linklerini çıkar - Facebook ve Instagram için geliştirildi"""
        social_media = {}
        
        social_patterns = {
            'facebook': [
                r'facebook\.com/[\w\-\.]+', 
                r'fb\.com/[\w\-\.]+',
                r'facebook\.com/pages/[\w\-\.]+',
                r'facebook\.com/groups/[\w\-\.]+',
                r'facebook\.com/events/[\w\-\.]+'
            ],
            'instagram': [
                r'instagram\.com/[\w\-\.]+',
                r'instagr\.am/[\w\-\.]+',
                r'instagram\.com/p/[\w\-\.]+',
                r'instagram\.com/stories/[\w\-\.]+'
            ],
            'twitter': [r'twitter\.com/[\w\-\.]+', r'x\.com/[\w\-\.]+'],
            'linkedin': [r'linkedin\.com/company/[\w\-\.]+', r'linkedin\.com/in/[\w\-\.]+'],
            'youtube': [r'youtube\.com/(c/|channel/|user/|@)[\w\-\.]+'],
            'tiktok': [r'tiktok\.com/@[\w\-\.]+'],
            'pinterest': [r'pinterest\.com/[\w\-\.]+'],
            'github': [r'github\.com/[\w\-\.]+'],
            'medium': [r'medium\.com/@?[\w\-\.]+'],
            'behance': [r'behance\.net/[\w\-\.]+']
        }
        
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            
            for platform, patterns in social_patterns.items():
                if platform not in social_media:
                    for pattern in patterns:
                        match = re.search(pattern, href, re.IGNORECASE)
                        if match:
                            # URL'i düzelt
                            if not match.group(0).startswith('http'):
                                social_media[platform] = 'https://' + match.group(0)
                            else:
                                social_media[platform] = match.group(0)
                            break
        
        # Facebook ve Instagram için özel analiz
        if 'facebook' in social_media or 'instagram' in social_media:
            social_media['social_analysis'] = self.analyze_social_media_presence(social_media)
        
        return social_media
    
    def analyze_social_media_presence(self, social_media: Dict[str, str]) -> Dict[str, Any]:
        """Facebook ve Instagram varlığını analiz et"""
        analysis = {
            'facebook': {
                'has_page': False,
                'page_type': None,
                'engagement_potential': 'low',
                'business_indicators': []
            },
            'instagram': {
                'has_profile': False,
                'profile_type': None,
                'engagement_potential': 'low',
                'business_indicators': []
            },
            'overall_social_score': 0,
            'recommendations': []
        }
        
        try:
            # Facebook analizi
            if 'facebook' in social_media:
                fb_url = social_media['facebook']
                analysis['facebook']['has_page'] = True
                
                # Sayfa tipini belirle
                if '/pages/' in fb_url:
                    analysis['facebook']['page_type'] = 'business_page'
                    analysis['facebook']['engagement_potential'] = 'high'
                    analysis['facebook']['business_indicators'].append('Resmi işletme sayfası')
                elif '/groups/' in fb_url:
                    analysis['facebook']['page_type'] = 'group'
                    analysis['facebook']['engagement_potential'] = 'medium'
                    analysis['facebook']['business_indicators'].append('Topluluk grubu')
                elif '/events/' in fb_url:
                    analysis['facebook']['page_type'] = 'event'
                    analysis['facebook']['engagement_potential'] = 'medium'
                    analysis['facebook']['business_indicators'].append('Etkinlik sayfası')
                else:
                    analysis['facebook']['page_type'] = 'profile'
                    analysis['facebook']['engagement_potential'] = 'low'
                    analysis['facebook']['business_indicators'].append('Kişisel profil')
            
            # Instagram analizi
            if 'instagram' in social_media:
                ig_url = social_media['instagram']
                analysis['instagram']['has_profile'] = True
                
                # Profil tipini belirle
                if '/p/' in ig_url:
                    analysis['instagram']['profile_type'] = 'post'
                    analysis['instagram']['engagement_potential'] = 'medium'
                    analysis['instagram']['business_indicators'].append('Gönderi paylaşımı')
                elif '/stories/' in ig_url:
                    analysis['instagram']['profile_type'] = 'story'
                    analysis['instagram']['engagement_potential'] = 'medium'
                    analysis['instagram']['business_indicators'].append('Hikaye paylaşımı')
                else:
                    analysis['instagram']['profile_type'] = 'profile'
                    analysis['instagram']['engagement_potential'] = 'high'
                    analysis['instagram']['business_indicators'].append('İşletme profili')
            
            # Genel sosyal medya skoru hesapla
            score = 0
            if analysis['facebook']['has_page']:
                score += 30
                if analysis['facebook']['page_type'] == 'business_page':
                    score += 20
            if analysis['instagram']['has_profile']:
                score += 30
                if analysis['instagram']['profile_type'] == 'profile':
                    score += 20
            
            analysis['overall_social_score'] = min(score, 100)
            
            # Öneriler oluştur
            if analysis['facebook']['has_page'] and analysis['instagram']['has_profile']:
                analysis['recommendations'].append('✅ Hem Facebook hem Instagram varlığı mevcut - güçlü dijital varlık')
            elif analysis['facebook']['has_page']:
                analysis['recommendations'].append('📘 Facebook sayfası mevcut - Instagram profili eklenebilir')
            elif analysis['instagram']['has_profile']:
                analysis['recommendations'].append('📷 Instagram profili mevcut - Facebook sayfası eklenebilir')
            else:
                analysis['recommendations'].append('⚠️ Sosyal medya varlığı sınırlı - Facebook ve Instagram profilleri oluşturulmalı')
            
            # İşletme göstergeleri
            if analysis['facebook']['page_type'] == 'business_page':
                analysis['recommendations'].append('💼 Resmi Facebook işletme sayfası - profesyonel yaklaşım')
            if analysis['instagram']['profile_type'] == 'profile':
                analysis['recommendations'].append('📱 Instagram işletme profili - görsel pazarlama potansiyeli')
            
        except Exception as e:
            print(f"⚠️ Sosyal medya analizi hatası: {str(e)}")
        
        return analysis
    
    def detect_facebook_login_requirement(self, driver) -> bool:
        """Facebook'ta login gerektiren durumları tespit et"""
        try:
            # Login gerektiren sayfa göstergeleri
            login_indicators = [
                # Login sayfası göstergeleri
                'input[name="email"]',
                'input[name="pass"]',
                'button[data-testid="royal_login_button"]',
                'a[href*="/login"]',
                'div[data-testid="login_form"]',
                
                # "Giriş yap" metinleri
                'text="Giriş yap"',
                'text="Log in"',
                'text="Sign in"',
                'text="Giriş"',
                
                # Hesap gerektiren içerik göstergeleri
                'div[data-testid="login_required"]',
                'div[class*="login"]',
                'div[class*="signin"]',
                
                # Sayfa erişim kısıtlaması
                'div[data-testid="page_access_required"]',
                'div[class*="access_required"]',
                'div[class*="private"]'
            ]
            
            # Sayfa kaynağını kontrol et
            page_source = driver.page_source.lower()
            login_keywords = [
                'giriş yap', 'log in', 'sign in', 'login required',
                'hesap gerekli', 'account required', 'private page',
                'gizli sayfa', 'restricted access', 'access denied'
            ]
            
            # Sayfa kaynağında login göstergeleri var mı?
            for keyword in login_keywords:
                if keyword in page_source:
                    return True
            
            # DOM elementlerinde login göstergeleri var mı?
            for selector in login_indicators:
                try:
                    if selector.startswith('text='):
                        # Metin tabanlı arama
                        text = selector.replace('text=', '')
                        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                        if elements:
                            return True
                    else:
                        # CSS selector arama
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            return True
                except:
                    continue
            
            # URL'de login göstergeleri var mı?
            current_url = driver.current_url.lower()
            if any(indicator in current_url for indicator in ['/login', '/signin', '/auth']):
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Login tespiti hatası: {str(e)}")
            return False
    
    def extract_facebook_public_data(self, driver, facebook_url: str, facebook_data: Dict) -> Dict[str, Any]:
        """Facebook'tan sadece genel erişilebilir bilgileri çıkar"""
        try:
            print("📋 Facebook genel bilgileri çıkarılıyor...")
            
            # Sayfa başlığını al
            try:
                page_title = driver.title
                if page_title and 'facebook' not in page_title.lower():
                    facebook_data['page_name'] = page_title
            except:
                pass
            
            # URL'den sayfa adını çıkar
            try:
                if '/pages/' in facebook_url:
                    page_name = facebook_url.split('/pages/')[-1].split('/')[0]
                    facebook_data['page_name'] = page_name.replace('-', ' ').title()
                    facebook_data['page_type'] = 'business_page'
                elif '/groups/' in facebook_url:
                    group_name = facebook_url.split('/groups/')[-1].split('/')[0]
                    facebook_data['page_name'] = group_name.replace('-', ' ').title()
                    facebook_data['page_type'] = 'group'
                else:
                    # Profil URL'si
                    profile_name = facebook_url.split('/')[-1]
                    facebook_data['page_name'] = profile_name.replace('.', ' ').title()
                    facebook_data['page_type'] = 'profile'
            except:
                pass
            
            # Meta bilgilerini al
            try:
                # Meta description
                meta_desc = driver.find_element(By.CSS_SELECTOR, 'meta[name="description"]')
                if meta_desc:
                    description = meta_desc.get_attribute('content')
                    if description:
                        facebook_data['contact_info']['description'] = description
            except:
                pass
            
            # Open Graph bilgileri
            try:
                og_title = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]')
                if og_title:
                    title = og_title.get_attribute('content')
                    if title and title != facebook_data['page_name']:
                        facebook_data['page_name'] = title
            except:
                pass
            
            # Sayfa tipini URL'den belirle
            if not facebook_data['page_type']:
                if '/pages/' in facebook_url:
                    facebook_data['page_type'] = 'business_page'
                elif '/groups/' in facebook_url:
                    facebook_data['page_type'] = 'group'
                else:
                    facebook_data['page_type'] = 'profile'
            
            # Başarılı olarak işaretle
            facebook_data['success'] = True
            facebook_data['error'] = 'Login gerekli - Sadece genel bilgiler alındı'
            
            print(f"✅ Facebook genel bilgileri alındı: {facebook_data['page_name']}")
            
        except Exception as e:
            facebook_data['error'] = f"Genel bilgi çıkarma hatası: {str(e)}"
            print(f"❌ Facebook genel bilgi çıkarma hatası: {str(e)}")
        
        finally:
            if 'driver' in locals():
                driver.quit()
        
        return facebook_data
    
    def extract_facebook_alternative_data(self, facebook_url: str) -> Dict[str, Any]:
        """Facebook'tan alternatif yöntemlerle veri çıkar"""
        alternative_data = {
            'success': False,
            'data_source': 'alternative',
            'page_info': {},
            'contact_info': {},
            'business_info': {},
            'error': None
        }
        
        try:
            print("🔍 Facebook alternatif veri çıkarma yöntemleri deneniyor...")
            
            # 1. Facebook Graph API (sınırlı)
            graph_data = self.try_facebook_graph_api(facebook_url)
            if graph_data:
                alternative_data['page_info'].update(graph_data)
                alternative_data['success'] = True
            
            # 2. Web scraping ile genel bilgiler
            web_data = self.try_facebook_web_scraping(facebook_url)
            if web_data:
                alternative_data['contact_info'].update(web_data)
                alternative_data['success'] = True
            
            # 3. URL analizi ile temel bilgiler
            url_data = self.analyze_facebook_url(facebook_url)
            if url_data:
                alternative_data['business_info'].update(url_data)
                alternative_data['success'] = True
            
            # 4. Meta tag'lerden bilgi çıkarma
            meta_data = self.extract_facebook_meta_data(facebook_url)
            if meta_data:
                alternative_data['page_info'].update(meta_data)
                alternative_data['success'] = True
            
        except Exception as e:
            alternative_data['error'] = f"Alternatif veri çıkarma hatası: {str(e)}"
            print(f"❌ Facebook alternatif veri çıkarma hatası: {str(e)}")
        
        return alternative_data
    
    def try_facebook_graph_api(self, facebook_url: str) -> Dict[str, Any]:
        """Facebook Graph API ile sınırlı veri çek (genel erişim)"""
        try:
            # Facebook Graph API genel erişim endpoint'i
            # Not: Bu sadece genel bilgiler için çalışır
            import requests
            
            # URL'den sayfa ID'sini çıkar
            page_id = self.extract_facebook_page_id(facebook_url)
            if not page_id:
                return {}
            
            # Graph API endpoint
            api_url = f"https://graph.facebook.com/v18.0/{page_id}"
            params = {
                'fields': 'name,about,website,phone,emails,location',
                'access_token': 'public'  # Genel erişim
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data.get('name', ''),
                    'about': data.get('about', ''),
                    'website': data.get('website', ''),
                    'phone': data.get('phone', ''),
                    'emails': data.get('emails', []),
                    'location': data.get('location', {})
                }
            
        except Exception as e:
            print(f"⚠️ Facebook Graph API hatası: {str(e)}")
        
        return {}
    
    def try_facebook_web_scraping(self, facebook_url: str) -> Dict[str, Any]:
        """Web scraping ile genel bilgileri çek"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(facebook_url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Meta bilgileri
                meta_data = {}
                
                # Title
                title = soup.find('title')
                if title:
                    meta_data['title'] = title.text.strip()
                
                # Meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    meta_data['description'] = meta_desc.get('content', '')
                
                # Open Graph bilgileri
                og_title = soup.find('meta', attrs={'property': 'og:title'})
                if og_title:
                    meta_data['og_title'] = og_title.get('content', '')
                
                og_desc = soup.find('meta', attrs={'property': 'og:description'})
                if og_desc:
                    meta_data['og_description'] = og_desc.get('content', '')
                
                return meta_data
            
        except Exception as e:
            print(f"⚠️ Facebook web scraping hatası: {str(e)}")
        
        return {}
    
    def analyze_facebook_url(self, facebook_url: str) -> Dict[str, Any]:
        """Facebook URL'sini analiz ederek temel bilgileri çıkar"""
        try:
            url_data = {}
            
            # URL'den sayfa tipini belirle
            if '/pages/' in facebook_url:
                url_data['page_type'] = 'business_page'
                # Sayfa adını çıkar
                page_name = facebook_url.split('/pages/')[-1].split('/')[0]
                url_data['page_name'] = page_name.replace('-', ' ').title()
            elif '/groups/' in facebook_url:
                url_data['page_type'] = 'group'
                group_name = facebook_url.split('/groups/')[-1].split('/')[0]
                url_data['group_name'] = group_name.replace('-', ' ').title()
            else:
                url_data['page_type'] = 'profile'
                profile_name = facebook_url.split('/')[-1]
                url_data['profile_name'] = profile_name.replace('.', ' ').title()
            
            # URL'den domain bilgisi
            from urllib.parse import urlparse
            parsed_url = urlparse(facebook_url)
            url_data['domain'] = parsed_url.netloc
            
            return url_data
            
        except Exception as e:
            print(f"⚠️ Facebook URL analizi hatası: {str(e)}")
            return {}
    
    def extract_facebook_meta_data(self, facebook_url: str) -> Dict[str, Any]:
        """Facebook sayfasından meta verileri çıkar"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(facebook_url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                meta_data = {}
                
                # Tüm meta tag'leri al
                meta_tags = soup.find_all('meta')
                for tag in meta_tags:
                    name = tag.get('name') or tag.get('property')
                    content = tag.get('content')
                    
                    if name and content:
                        meta_data[name] = content
                
                return meta_data
            
        except Exception as e:
            print(f"⚠️ Facebook meta veri çıkarma hatası: {str(e)}")
            return {}
    
    def extract_facebook_page_id(self, facebook_url: str) -> str:
        """Facebook URL'sinden sayfa ID'sini çıkar"""
        try:
            # URL'den sayfa ID'sini çıkarmaya çalış
            if '/pages/' in facebook_url:
                # Sayfa URL'si: https://www.facebook.com/pages/PageName/123456789
                parts = facebook_url.split('/pages/')[-1].split('/')
                if len(parts) > 1:
                    return parts[1]  # ID kısmı
            
            # Alternatif formatlar
            if 'facebook.com/' in facebook_url:
                # Profil URL'si: https://www.facebook.com/username
                username = facebook_url.split('facebook.com/')[-1].split('/')[0]
                return username
            
        except Exception as e:
            print(f"⚠️ Facebook sayfa ID çıkarma hatası: {str(e)}")
        
        return ""
    
    def scrape_facebook_page(self, facebook_url: str) -> Dict[str, Any]:
        """Facebook sayfasından temel bilgileri çek - Login gerektiren durumları tespit eder"""
        facebook_data = {
            'success': False,
            'page_name': '',
            'page_type': '',
            'followers_count': 0,
            'likes_count': 0,
            'recent_posts': [],
            'contact_info': {},
            'requires_login': False,
            'public_data_only': False,
            'error': None
        }
        
        try:
            print(f"📘 Facebook sayfası analiz ediliyor: {facebook_url}")
            
            # Driver oluştur
            driver = self.create_driver()
            driver.get(facebook_url)
            
            # Sayfa yüklenmesini bekle
            self.wait_for_page_load(driver, timeout=15)
            
            # Login gerektiren durumları tespit et
            login_required = self.detect_facebook_login_requirement(driver)
            if login_required:
                print("⚠️ Facebook sayfası giriş gerektiriyor - Alternatif yöntemler deneniyor")
                facebook_data['requires_login'] = True
                facebook_data['public_data_only'] = True
                
                # Alternatif yöntemlerle veri çıkarmaya çalış
                alternative_data = self.extract_facebook_alternative_data(facebook_url)
                if alternative_data['success']:
                    # Alternatif verileri ana veriye ekle
                    facebook_data.update(alternative_data)
                    facebook_data['success'] = True
                    print("✅ Facebook alternatif yöntemlerle veri alındı")
                else:
                    # Son çare olarak genel bilgileri al
                    return self.extract_facebook_public_data(driver, facebook_url, facebook_data)
            
            # Sayfa adını al
            try:
                page_name_elem = driver.find_element(By.CSS_SELECTOR, 'h1[data-testid="page_profile_name"]')
                facebook_data['page_name'] = page_name_elem.text.strip()
            except:
                try:
                    page_name_elem = driver.find_element(By.CSS_SELECTOR, 'h1')
                    facebook_data['page_name'] = page_name_elem.text.strip()
                except:
                    facebook_data['page_name'] = 'Bilinmeyen'
            
            # Sayfa tipini belirle
            if '/pages/' in facebook_url:
                facebook_data['page_type'] = 'business_page'
            elif '/groups/' in facebook_url:
                facebook_data['page_type'] = 'group'
            else:
                facebook_data['page_type'] = 'profile'
            
            # Takipçi sayısını al (basit yaklaşım)
            try:
                followers_elem = driver.find_element(By.XPATH, "//span[contains(text(), 'takipçi') or contains(text(), 'follower')]")
                followers_text = followers_elem.text
                # Sayıyı çıkar
                import re
                numbers = re.findall(r'[\d,]+', followers_text)
                if numbers:
                    facebook_data['followers_count'] = int(numbers[0].replace(',', ''))
            except:
                pass
            
            # Beğeni sayısını al
            try:
                likes_elem = driver.find_element(By.XPATH, "//span[contains(text(), 'beğeni') or contains(text(), 'like')]")
                likes_text = likes_elem.text
                numbers = re.findall(r'[\d,]+', likes_text)
                if numbers:
                    facebook_data['likes_count'] = int(numbers[0].replace(',', ''))
            except:
                pass
            
            # İletişim bilgilerini al
            try:
                contact_elements = driver.find_elements(By.XPATH, "//span[contains(text(), '@') or contains(text(), 'www.')]")
                for elem in contact_elements[:3]:
                    text = elem.text.strip()
                    if '@' in text:
                        facebook_data['contact_info']['email'] = text
                    elif 'www.' in text:
                        facebook_data['contact_info']['website'] = text
            except:
                pass
            
            facebook_data['success'] = True
            print(f"✅ Facebook analizi tamamlandı: {facebook_data['page_name']}")
            
        except Exception as e:
            facebook_data['error'] = str(e)
            print(f"❌ Facebook analizi hatası: {str(e)}")
        
        finally:
            if 'driver' in locals():
                driver.quit()
        
        return facebook_data
    
    def scrape_instagram_profile(self, instagram_url: str) -> Dict[str, Any]:
        """Instagram profilinden temel bilgileri çek"""
        instagram_data = {
            'success': False,
            'username': '',
            'full_name': '',
            'followers_count': 0,
            'following_count': 0,
            'posts_count': 0,
            'bio': '',
            'is_business': False,
            'contact_info': {},
            'error': None
        }
        
        try:
            print(f"📷 Instagram profili analiz ediliyor: {instagram_url}")
            
            # Driver oluştur
            driver = self.create_driver()
            driver.get(instagram_url)
            
            # Sayfa yüklenmesini bekle
            self.wait_for_page_load(driver, timeout=15)
            
            # Kullanıcı adını al
            try:
                username_elem = driver.find_element(By.CSS_SELECTOR, 'h2')
                instagram_data['username'] = username_elem.text.strip()
            except:
                # URL'den kullanıcı adını çıkar
                import re
                match = re.search(r'instagram\.com/([^/?]+)', instagram_url)
                if match:
                    instagram_data['username'] = match.group(1)
            
            # Tam adı al
            try:
                full_name_elem = driver.find_element(By.CSS_SELECTOR, 'h1')
                instagram_data['full_name'] = full_name_elem.text.strip()
            except:
                pass
            
            # Bio'yu al
            try:
                bio_elem = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="user-bio"]')
                instagram_data['bio'] = bio_elem.text.strip()
            except:
                pass
            
            # İstatistikleri al
            try:
                stats_elements = driver.find_elements(By.CSS_SELECTOR, 'span[title]')
                for elem in stats_elements:
                    title = elem.get_attribute('title')
                    if 'takipçi' in title or 'follower' in title:
                        instagram_data['followers_count'] = int(title.replace(',', '').replace(' takipçi', '').replace(' followers', ''))
                    elif 'takip' in title or 'following' in title:
                        instagram_data['following_count'] = int(title.replace(',', '').replace(' takip', '').replace(' following', ''))
                    elif 'gönderi' in title or 'post' in title:
                        instagram_data['posts_count'] = int(title.replace(',', '').replace(' gönderi', '').replace(' posts', ''))
            except:
                pass
            
            # İşletme profili kontrolü
            try:
                business_elem = driver.find_element(By.XPATH, "//span[contains(text(), 'İşletme') or contains(text(), 'Business')]")
                instagram_data['is_business'] = True
            except:
                instagram_data['is_business'] = False
            
            # İletişim bilgilerini bio'dan çıkar
            if instagram_data['bio']:
                bio_text = instagram_data['bio']
                # Email ara
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', bio_text)
                if email_match:
                    instagram_data['contact_info']['email'] = email_match.group(0)
                
                # Website ara
                website_match = re.search(r'https?://[^\s]+', bio_text)
                if website_match:
                    instagram_data['contact_info']['website'] = website_match.group(0)
            
            instagram_data['success'] = True
            print(f"✅ Instagram analizi tamamlandı: {instagram_data['username']}")
            
        except Exception as e:
            instagram_data['error'] = str(e)
            print(f"❌ Instagram analizi hatası: {str(e)}")
        
        finally:
            if 'driver' in locals():
                driver.quit()
        
        return instagram_data
    
    def scrape_facebook_only(self, facebook_url: str, company_name: str = "") -> Dict[str, Any]:
        """Sadece Facebook sayfasından firma bilgilerini çıkar - Website yoksa"""
        print(f"\n{'='*70}")
        print(f"📘 FACEBOOK-ONLY SCRAPING BAŞLATILIYOR")
        print(f"{'='*70}")
        print(f"📍 Facebook URL: {facebook_url}")
        print(f"🏢 Firma: {company_name}")
        print(f"{'='*70}\n")
        
        facebook_data = {
            'success': False,
            'website': facebook_url,  # Facebook URL'ini website olarak kaydet
            'domain': 'facebook.com',
            'title': company_name or 'Facebook Sayfası',
            'description': '',
            'keywords': '',
            'emails': [],
            'phone_numbers': [],
            'social_media': {'facebook': facebook_url},
            'business_info': {},
            'text_content': '',
            'services': [],
            'products': [],
            'pricing': [],
            'about_text': '',
            'team_size_estimate': 'Bilinmiyor',
            'industry_keywords': [],
            'contact_page_url': None,
            'scraped_data': {},
            'company_score': {'overall': 0},
            'advanced_features': {},
            'ai_summary': '',
            'facebook_details': {},
            'error': None
        }
        
        try:
            # Facebook sayfasını tara
            fb_details = self.scrape_facebook_page(facebook_url)
            facebook_data['facebook_details'] = fb_details
            
            if not fb_details['success']:
                facebook_data['error'] = fb_details.get('error', 'Facebook sayfası taranamadı')
                return facebook_data
            
            # Facebook'tan temel bilgileri çıkar
            driver = self.create_driver()
            driver.get(facebook_url)
            self.wait_for_page_load(driver, timeout=15)
            
            # Sayfa kaynağını al
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            page_text = self.get_text_content(soup)
            
            # Temel bilgileri güncelle
            facebook_data['text_content'] = page_text
            facebook_data['title'] = fb_details.get('page_name', company_name or 'Facebook Sayfası')
            
            # Facebook'tan email ve telefon çıkar
            facebook_emails = self.extract_emails_advanced(page_source, 'facebook.com')
            facebook_data['emails'].extend(facebook_emails)
            
            facebook_phones = self.extract_phone_numbers(page_source)
            facebook_data['phone_numbers'].extend(facebook_phones)
            
            # Facebook'tan hizmet/ürün bilgilerini çıkar
            facebook_services = self.extract_facebook_services(soup)
            facebook_data['services'].extend(facebook_services)
            
            # Facebook'tan hakkımızda bilgisini çıkar
            facebook_about = self.extract_facebook_about(soup)
            facebook_data['about_text'] = facebook_about
            
            # Facebook'tan iletişim bilgilerini çıkar
            facebook_contact = self.extract_facebook_contact_info(soup, driver)
            facebook_data['business_info'].update(facebook_contact)
            
            # Sektör tespiti
            detected_sector = self.detect_sector_from_facebook(soup, page_text)
            facebook_data['business_info']['sector'] = detected_sector
            facebook_data['industry_keywords'] = self.extract_industry_keywords(soup)
            
            # Takım büyüklüğü tahmini
            facebook_data['team_size_estimate'] = self.estimate_team_size_from_facebook(soup)
            
            # Firma skorlaması
            facebook_data['company_score'] = self.calculate_facebook_company_score(facebook_data, fb_details)
            
            # AI özeti
            facebook_data['ai_summary'] = self.generate_facebook_ai_summary(facebook_data, fb_details)
            
            facebook_data['success'] = True
            
            print(f"✅ Facebook-only scraping tamamlandı!")
            print(f"📧 {len(facebook_data['emails'])} email bulundu")
            print(f"📞 {len(facebook_data['phone_numbers'])} telefon bulundu")
            print(f"🏆 Firma skoru: {facebook_data['company_score']['overall']:.1f}/100")
            
        except Exception as e:
            facebook_data['error'] = str(e)
            print(f"❌ Facebook-only scraping hatası: {str(e)}")
        
        finally:
            if 'driver' in locals():
                driver.quit()
        
        return facebook_data
    
    def extract_facebook_services(self, soup: BeautifulSoup) -> List[str]:
        """Facebook sayfasından hizmet/ürün bilgilerini çıkar"""
        services = []
        
        try:
            # Facebook'ta hizmetler genelde bu alanlarda bulunur
            service_selectors = [
                'div[data-testid="page_section_services"]',
                'div[data-testid="page_section_about"]',
                'div[data-testid="page_section_info"]',
                'div[data-testid="page_section_contact"]',
                'div[data-testid="page_section_posts"]'
            ]
            
            for selector in service_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text().strip()
                    if text and len(text) > 20:
                        # Hizmet ile ilgili anahtar kelimeleri ara
                        service_keywords = [
                            'hizmet', 'service', 'ürün', 'product', 'çözüm', 'solution',
                            'yapıyoruz', 'we do', 'sunarız', 'we offer', 'veriyoruz', 'we provide'
                        ]
                        
                        for keyword in service_keywords:
                            if keyword in text.lower():
                                # Metni cümlelere böl
                                sentences = text.split('.')
                                for sentence in sentences:
                                    sentence = sentence.strip()
                                    if len(sentence) > 10 and len(sentence) < 200:
                                        if any(kw in sentence.lower() for kw in service_keywords):
                                            services.append(sentence)
                                break
            
            # Duplicate'leri temizle
            services = list(set(services))
            
        except Exception as e:
            print(f"⚠️ Facebook hizmet çıkarma hatası: {str(e)}")
        
        return services[:10]  # Max 10 hizmet
    
    def extract_facebook_about(self, soup: BeautifulSoup) -> str:
        """Facebook sayfasından hakkımızda bilgisini çıkar"""
        about_text = ""
        
        try:
            # Facebook'ta hakkımızda bilgisi genelde bu alanlarda bulunur
            about_selectors = [
                'div[data-testid="page_section_about"]',
                'div[data-testid="page_section_info"]',
                'div[data-testid="page_section_description"]',
                'div[data-testid="page_section_bio"]'
            ]
            
            for selector in about_selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    if text and len(text) > 50:
                        about_text = text[:1000]  # Max 1000 karakter
                        break
            
            # Eğer hakkımızda bulunamazsa, genel sayfa metninden çıkar
            if not about_text:
                page_text = soup.get_text()
                about_keywords = [
                    'hakkımızda', 'about', 'biz kimiz', 'who we are',
                    'misyon', 'mission', 'vizyon', 'vision'
                ]
                
                for keyword in about_keywords:
                    if keyword in page_text.lower():
                        # Anahtar kelimenin etrafındaki metni al
                        start = page_text.lower().find(keyword)
                        if start != -1:
                            end = min(start + 500, len(page_text))
                            about_text = page_text[start:end].strip()
                            break
            
        except Exception as e:
            print(f"⚠️ Facebook hakkımızda çıkarma hatası: {str(e)}")
        
        return about_text
    
    def extract_facebook_contact_info(self, soup: BeautifulSoup, driver) -> Dict[str, Any]:
        """Facebook sayfasından iletişim bilgilerini çıkar"""
        contact_info = {
            'address': '',
            'phone': '',
            'email': '',
            'website': '',
            'working_hours': ''
        }
        
        try:
            # Facebook'ta iletişim bilgileri genelde bu alanlarda bulunur
            contact_selectors = [
                'div[data-testid="page_section_contact"]',
                'div[data-testid="page_section_info"]',
                'div[data-testid="page_section_about"]'
            ]
            
            for selector in contact_selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text()
                    
                    # Adres ara
                    if not contact_info['address']:
                        address_keywords = ['adres', 'address', 'konum', 'location']
                        for keyword in address_keywords:
                            if keyword in text.lower():
                                # Adres bilgisini çıkar
                                lines = text.split('\n')
                                for line in lines:
                                    if keyword in line.lower() and len(line.strip()) > 10:
                                        contact_info['address'] = line.strip()
                                        break
                    
                    # Telefon ara
                    if not contact_info['phone']:
                        phone_match = re.search(r'(\+90\s?)?(\d{3}[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2})', text)
                        if phone_match:
                            contact_info['phone'] = phone_match.group(0)
                    
                    # Email ara
                    if not contact_info['email']:
                        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
                        if email_match:
                            contact_info['email'] = email_match.group(0)
                    
                    # Website ara
                    if not contact_info['website']:
                        website_match = re.search(r'https?://[^\s]+', text)
                        if website_match:
                            contact_info['website'] = website_match.group(0)
            
            # JavaScript ile daha detaylı bilgi çekmeye çalış
            try:
                # Facebook'ta gizli iletişim bilgileri JavaScript ile yüklenebilir
                js_contact = driver.execute_script("""
                    const contactInfo = {};
                    
                    // İletişim bilgilerini ara
                    const contactElements = document.querySelectorAll('[data-testid*="contact"], [data-testid*="info"]');
                    contactElements.forEach(el => {
                        const text = el.textContent;
                        if (text.includes('@')) {
                            const emailMatch = text.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/);
                            if (emailMatch) contactInfo.email = emailMatch[0];
                        }
                        if (text.includes('+90') || text.includes('0')) {
                            const phoneMatch = text.match(/(\\+90\\s?)?(\\d{3}[-.\\s]?\\d{3}[-.\\s]?\\d{2}[-.\\s]?\\d{2})/);
                            if (phoneMatch) contactInfo.phone = phoneMatch[0];
                        }
                    });
                    
                    return contactInfo;
                """)
                
                if js_contact.get('email') and not contact_info['email']:
                    contact_info['email'] = js_contact['email']
                if js_contact.get('phone') and not contact_info['phone']:
                    contact_info['phone'] = js_contact['phone']
                    
            except Exception as e:
                print(f"⚠️ JavaScript iletişim bilgisi çıkarma hatası: {str(e)}")
            
        except Exception as e:
            print(f"⚠️ Facebook iletişim bilgisi çıkarma hatası: {str(e)}")
        
        return contact_info
    
    def detect_sector_from_facebook(self, soup: BeautifulSoup, page_text: str) -> str:
        """Facebook sayfasından sektör tespit et"""
        try:
            # Facebook'ta sektör bilgisi genelde sayfa kategorisinde bulunur
            category_element = soup.select_one('div[data-testid="page_section_category"]')
            if category_element:
                category_text = category_element.get_text().strip()
                if category_text:
                    return category_text
            
            # Sayfa metninden sektör tespit et
            return self.detect_sector(soup, page_text)
            
        except Exception as e:
            print(f"⚠️ Facebook sektör tespiti hatası: {str(e)}")
            return 'genel'
    
    def estimate_team_size_from_facebook(self, soup: BeautifulSoup) -> str:
        """Facebook sayfasından takım büyüklüğü tahmin et"""
        try:
            # Facebook'ta takım büyüklüğü genelde sayfa bilgilerinde bulunur
            page_text = soup.get_text()
            
            # Takım büyüklüğü anahtar kelimeleri
            team_keywords = {
                '1-10': ['1-10', '1-5', 'küçük', 'small', 'startup'],
                '11-50': ['11-50', 'orta', 'medium', 'büyüyen'],
                '51-200': ['51-200', 'büyük', 'large', 'kurumsal'],
                '200+': ['200+', 'çok büyük', 'very large', 'holding']
            }
            
            for size, keywords in team_keywords.items():
                for keyword in keywords:
                    if keyword in page_text.lower():
                        return size
            
            return 'Bilinmiyor'
            
        except Exception as e:
            print(f"⚠️ Facebook takım büyüklüğü tahmini hatası: {str(e)}")
            return 'Bilinmiyor'
    
    def calculate_facebook_company_score(self, facebook_data: Dict, fb_details: Dict) -> Dict[str, int]:
        """Facebook sayfasından firma skorlaması"""
        scores = {
            'overall': 0,
            'digital_presence': 0,
            'professionalism': 0,
            'market_position': 0,
            'innovation': 0
        }
        
        try:
            # Dijital varlık skoru (Facebook varlığı)
            if fb_details.get('success'):
                scores['digital_presence'] = 60  # Facebook sayfası var
                if fb_details.get('followers_count', 0) > 1000:
                    scores['digital_presence'] += 20
                if fb_details.get('likes_count', 0) > 500:
                    scores['digital_presence'] += 20
            
            # Profesyonellik skoru
            if facebook_data.get('about_text'):
                scores['professionalism'] = 40
            if facebook_data.get('services'):
                scores['professionalism'] += 30
            if facebook_data.get('emails'):
                scores['professionalism'] += 30
            
            # Pazar konumu skoru
            if facebook_data.get('business_info', {}).get('sector') != 'genel':
                scores['market_position'] = 50
            if facebook_data.get('industry_keywords'):
                scores['market_position'] += 30
            if facebook_data.get('team_size_estimate') != 'Bilinmiyor':
                scores['market_position'] += 20
            
            # İnovasyon skoru
            if facebook_data.get('services'):
                scores['innovation'] = 40
            if facebook_data.get('about_text') and len(facebook_data['about_text']) > 100:
                scores['innovation'] += 30
            if facebook_data.get('emails'):
                scores['innovation'] += 30
            
            # Genel skor
            scores['overall'] = (
                scores['digital_presence'] * 0.3 +
                scores['professionalism'] * 0.4 +
                scores['market_position'] * 0.2 +
                scores['innovation'] * 0.1
            )
            
        except Exception as e:
            print(f"⚠️ Facebook skorlama hatası: {str(e)}")
        
        return scores
    
    def generate_facebook_ai_summary(self, facebook_data: Dict, fb_details: Dict) -> str:
        """Facebook sayfası için AI özeti oluştur"""
        try:
            page_name = fb_details.get('page_name', 'Bilinmeyen')
            followers = fb_details.get('followers_count', 0)
            likes = fb_details.get('likes_count', 0)
            sector = facebook_data.get('business_info', {}).get('sector', 'genel')
            services = facebook_data.get('services', [])
            emails = facebook_data.get('emails', [])
            score = facebook_data.get('company_score', {}).get('overall', 0)
            
            summary = f"""
📘 FACEBOOK SAYFASI ANALİZİ

🏢 Firma: {page_name}
📱 Platform: Facebook
🏭 Sektör: {sector.capitalize()}
🏆 Genel Skor: {score:.1f}/100

📊 SOSYAL MEDYA İSTATİSTİKLERİ:
• Takipçi: {followers:,}
• Beğeni: {likes:,}
• Platform: Facebook Only

🎯 HİZMETLER:
{', '.join(services[:5]) if services else 'Belirtilmemiş'}

📧 İLETİŞİM:
• Email: {len(emails)} adet bulundu
• Telefon: {len(facebook_data.get('phone_numbers', []))} adet bulundu

🔍 DEĞERLENDİRME:
"""
            
            if score > 70:
                summary += "✅ Güçlü Facebook varlığı, profesyonel sayfa. İşbirliği için uygun."
            elif score > 50:
                summary += "⚡ Orta seviye Facebook sayfası. Detaylı değerlendirme gerekli."
            else:
                summary += "⚠️ Facebook varlığı sınırlı. Website bilgisi eksik."
            
            summary += f"\n\n📌 NOT: Bu firma sadece Facebook sayfası üzerinden faaliyet gösteriyor. Website bilgisi mevcut değil."
            
            return summary
            
        except Exception as e:
            print(f"⚠️ Facebook AI özet hatası: {str(e)}")
            return "Facebook sayfası analiz edilemedi."
    
    def get_text_content(self, soup: BeautifulSoup) -> str:
        """Sayfa metin içeriğini al"""
        # Script ve style taglerini kaldır
        for script in soup(["script", "style", "noscript", "iframe"]):
            script.decompose()
        
        # Metin al
        text = soup.get_text()
        
        # Temizle
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Gereksiz boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        
        # Maksimum 5000 karakter
        return text[:5000]
    
    def extract_services(self, soup: BeautifulSoup) -> List[str]:
        """Hizmetleri çıkarmaya çalış"""
        services = []
        seen_services = set()
        
        # Hizmet ile ilgili başlıkları ara
        service_keywords = [
            'hizmet', 'service', 'çözüm', 'solution', 
            'ürün', 'product', 'ne yapıyoruz', 'what we do',
            'faaliyet', 'neler sunuyoruz'
        ]
        
        for keyword in service_keywords:
            # Başlıkları kontrol et
            for tag in ['h1', 'h2', 'h3', 'h4']:
                headers = soup.find_all(tag, text=re.compile(keyword, re.I))
                for header in headers:
                    # Sonraki elementleri al
                    next_element = header.find_next_sibling()
                    
                    # 5 element veya başka bir başlığa kadar devam et
                    count = 0
                    while next_element and count < 5:
                        if next_element.name == 'ul':
                            # Liste elemanlarını al
                            items = next_element.find_all('li')
                            for item in items[:10]:
                                service = item.text.strip()
                                if service and 10 < len(service) < 150 and service.lower() not in seen_services:
                                    seen_services.add(service.lower())
                                    services.append(service)
                        
                        elif next_element.name in ['p', 'div']:
                            # Paragraf içeriğini kontrol et
                            text = next_element.text.strip()
                            if text and 20 < len(text) < 200:
                                # Noktalı cümleleri ayır
                                sentences = re.split(r'[.•·]', text)
                                for sentence in sentences[:3]:
                                    service = sentence.strip()
                                    if service and 10 < len(service) < 150 and service.lower() not in seen_services:
                                        seen_services.add(service.lower())
                                        services.append(service)
                        
                        elif next_element.name in ['h1', 'h2', 'h3', 'h4']:
                            # Başka bir başlığa ulaştık, dur
                            break
                        
                        next_element = next_element.find_next_sibling()
                        count += 1
        
        # Service/hizmet kartları
        service_cards = soup.find_all(['div', 'article'], class_=re.compile('service|hizmet|solution|çözüm', re.I))
        for card in service_cards[:10]:
            title = card.find(['h3', 'h4', 'h5'])
            if title:
                service = title.text.strip()
                if service and 10 < len(service) < 150 and service.lower() not in seen_services:
                    seen_services.add(service.lower())
                    services.append(service)
        
        return services[:15]  # İlk 15 hizmet
    
    def extract_about_text(self, soup: BeautifulSoup) -> str:
        """Hakkımızda metnini çıkar"""
        about_keywords = [
            'hakkımızda', 'about', 'biz kimiz', 'who we are', 
            'kurumsal', 'corporate', 'hikayemiz', 'our story',
            'misyon', 'mission', 'vizyon', 'vision', 'firmamız'
        ]
        
        about_text = ""
        
        for keyword in about_keywords:
            if about_text:  # Zaten metin bulduysa dur
                break
            
            # Başlık ara
            for tag in ['h1', 'h2', 'h3', 'h4']:
                headers = soup.find_all(tag, text=re.compile(keyword, re.I))
                for header in headers:
                    # Sonraki paragrafları al
                    text_parts = []
                    next_element = header.find_next_sibling()
                    
                    while next_element and len(' '.join(text_parts)) < 1500:
                        if next_element.name == 'p':
                            paragraph = next_element.text.strip()
                            if paragraph and len(paragraph) > 50:
                                text_parts.append(paragraph)
                        elif next_element.name in ['h1', 'h2', 'h3', 'h4']:
                            # Başka bir başlık, dur
                            break
                        elif next_element.name == 'div':
                            # Div içindeki p'leri al
                            div_paragraphs = next_element.find_all('p')
                            for p in div_paragraphs[:3]:
                                para_text = p.text.strip()
                                if para_text and len(para_text) > 50:
                                    text_parts.append(para_text)
                        
                        next_element = next_element.find_next_sibling()
                    
                    if text_parts:
                        about_text = ' '.join(text_parts)
                        break
        
        return about_text[:1500]  # Max 1500 karakter
    
    def extract_products(self, soup: BeautifulSoup) -> List[Dict]:
        """Ürün bilgilerini detaylı çıkar"""
        products = []
        
        # Ürün kartları
        product_cards = soup.find_all(['div', 'article'], class_=re.compile('product|ürün|item|package|paket', re.I))
        
        for card in product_cards[:20]:  # Max 20 ürün
            product = {
                'name': '',
                'description': '',
                'price': '',
                'features': []
            }
            
            # Ürün adı
            name_elem = card.find(['h2', 'h3', 'h4', 'h5'], class_=re.compile('title|name|başlık|isim', re.I))
            if not name_elem:
                name_elem = card.find(['h2', 'h3', 'h4', 'h5'])
            if name_elem:
                product['name'] = name_elem.text.strip()
            
            # Ürün açıklaması
            desc_elem = card.find(['p', 'div'], class_=re.compile('desc|açıklama|summary|özet', re.I))
            if desc_elem:
                product['description'] = desc_elem.text.strip()[:300]
            
            # Fiyat
            price_pattern = r'(\d+[\.,]?\d*)\s*(TL|₺|USD|\$|EUR|€)'
            price_match = re.search(price_pattern, card.text)
            if price_match:
                product['price'] = price_match.group(0)
            
            # Özellikler
            features_list = card.find('ul')
            if features_list:
                features = features_list.find_all('li')
                for feature in features[:5]:
                    product['features'].append(feature.text.strip())
            
            if product['name']:
                products.append(product)
        
        return products
    
    def extract_pricing_info(self, soup: BeautifulSoup) -> List[Dict]:
        """Fiyat bilgilerini çıkar"""
        pricing_info = []
        
        # Fiyat tabloları
        pricing_tables = soup.find_all(['table', 'div'], class_=re.compile('pricing|fiyat|price|plan', re.I))
        
        # Fiyat pattern'leri
        price_patterns = [
            (r'(\d+[\.,]?\d*)\s*(TL|₺)\s*\/?\s*(ay|aylık|month|yıl|yıllık|year)?', 'TL'),
            (r'(\d+[\.,]?\d*)\s*(USD|\$)\s*\/?\s*(ay|aylık|month|yıl|yıllık|year)?', 'USD'),
            (r'(\d+[\.,]?\d*)\s*(EUR|€)\s*\/?\s*(ay|aylık|month|yıl|yıllık|year)?', 'EUR'),
            (r'(aylık|monthly)\s*(\d+[\.,]?\d*)\s*(TL|₺|USD|\$|EUR|€)', 'period_first'),
            (r'başlangıç fiyatı\s*[:]\s*(\d+[\.,]?\d*)', 'starting_price')
        ]
        
        # Sayfadaki tüm metni al
        page_text = soup.get_text()
        
        for pattern, price_type in price_patterns:
            matches = re.findall(pattern, page_text, re.I)
            for match in matches[:10]:  # Max 10 fiyat
                if isinstance(match, tuple):
                    price_str = ' '.join(str(m) for m in match if m)
                else:
                    price_str = str(match)
                    
                pricing_info.append({
                    'price': price_str,
                    'type': price_type,
                    'context': self.get_price_context(page_text, price_str)
                })
        
        # Ücretsiz/demo bilgisi
        free_keywords = ['ücretsiz', 'free', 'demo', 'deneme', 'trial', 'bedava']
        for keyword in free_keywords:
            if keyword in page_text.lower():
                context_match = re.search(rf'[^.]*{keyword}[^.]*', page_text, re.I)
                if context_match:
                    pricing_info.append({
                        'price': 'Ücretsiz/Demo',
                        'type': 'free',
                        'context': context_match.group(0)[:200]
                    })
                    break
        
        return pricing_info
    
    def get_price_context(self, text: str, price: str) -> str:
        """Fiyatın bağlamını al"""
        try:
            # Fiyatın etrafındaki metni al
            index = text.find(price)
            if index != -1:
                start = max(0, index - 50)
                end = min(len(text), index + len(price) + 50)
                return text[start:end].strip()
        except:
            pass
        return ""
    
    def estimate_team_size(self, soup: BeautifulSoup) -> str:
        """Takım büyüklüğünü tahmin et"""
        text = soup.get_text().lower()
        
        # Doğrudan belirtilen sayılar
        patterns = [
            (r'(\d+)\+?\s*(çalışan|employee|kişi|person|ekip|team|personel|staff)', 'exact'),
            (r'(\d+)\s*-\s*(\d+)\s*(çalışan|employee|kişi|person)', 'range'),
            (r'(küçük|small|orta|medium|büyük|large|kurumsal|enterprise)\s*(ölçek|scale|boy|size|ekip|team)', 'size')
        ]
        
        for pattern, pattern_type in patterns:
            match = re.search(pattern, text)
            if match:
                if pattern_type == 'exact':
                    number = int(match.group(1))
                    return f"{number}+ çalışan"
                elif pattern_type == 'range':
                    return f"{match.group(1)}-{match.group(2)} çalışan"
                elif pattern_type == 'size':
                    size_word = match.group(1)
                    if size_word in ['küçük', 'small']:
                        return "1-10 çalışan"
                    elif size_word in ['orta', 'medium']:
                        return "11-50 çalışan"
                    elif size_word in ['büyük', 'large']:
                        return "51-200 çalışan"
                    elif size_word in ['kurumsal', 'enterprise']:
                        return "200+ çalışan"
        
        # Ofis/şube sayısından tahmin
        office_patterns = [
            r'(\d+)\s*(ofis|office|şube|branch|lokasyon|location|mağaza|store|bayi)',
            r'(\d+)\s*(ülke|country|şehir|city)'
        ]
        
        for pattern in office_patterns:
            match = re.search(pattern, text)
            if match:
                count = int(match.group(1))
                if count >= 50:
                    return "1000+ çalışan (tahmini)"
                elif count >= 20:
                    return "500+ çalışan (tahmini)"
                elif count >= 10:
                    return "200+ çalışan (tahmini)"
                elif count >= 5:
                    return "100-200 çalışan (tahmini)"
                elif count >= 2:
                    return "20-100 çalışan (tahmini)"
        
        # Global/uluslararası kelimelerden tahmin
        global_keywords = ['global', 'uluslararası', 'international', 'dünya çapında', 'worldwide']
        if any(keyword in text for keyword in global_keywords):
            return "200+ çalışan (tahmini)"
        
        # Kurumsal kelimelerden tahmin
        corporate_keywords = ['kurumsal', 'enterprise', 'corporate', 'holding']
        if any(keyword in text for keyword in corporate_keywords):
            return "50+ çalışan (tahmini)"
        
        # Startup kelimelerden tahmin
        startup_keywords = ['startup', 'girişim', 'start-up', 'yeni kuruldu', 'newly founded']
        if any(keyword in text for keyword in startup_keywords):
            return "1-20 çalışan (tahmini)"
        
        # Takım üyelerini say
        team_members = self.extract_team_members(soup)
        if team_members:
            member_count = len(team_members)
            if member_count >= 20:
                return "50+ çalışan (tahmini)"
            elif member_count >= 10:
                return "20-50 çalışan (tahmini)"
            elif member_count >= 5:
                return "10-20 çalışan (tahmini)"
        
        return "Bilinmiyor"
    
    def extract_industry_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Sektör anahtar kelimelerini çıkar"""
        text = soup.get_text().lower()
        
        # Sektör kategorileri ve anahtar kelimeleri
        industry_categories = {
            'teknoloji': ['yazılım', 'software', 'teknoloji', 'technology', 'bilişim', 'it', 'dijital', 'digital', 'mobil', 'mobile', 'web', 'uygulama', 'application', 'app', 'sistem', 'system'],
            'danışmanlık': ['danışmanlık', 'consulting', 'consultancy', 'müşavirlik', 'advisory', 'strateji', 'strategy'],
            'pazarlama': ['pazarlama', 'marketing', 'reklam', 'advertising', 'ajans', 'agency', 'pr', 'halkla ilişkiler', 'dijital pazarlama', 'seo', 'sem', 'sosyal medya'],
            'üretim': ['üretim', 'manufacturing', 'imalat', 'production', 'fabrika', 'factory', 'sanayi', 'industry', 'endüstri'],
            'ticaret': ['ticaret', 'trade', 'satış', 'sales', 'dağıtım', 'distribution', 'toptan', 'wholesale', 'perakende', 'retail', 'ithalat', 'ihracat', 'export', 'import'],
            'e-ticaret': ['e-ticaret', 'e-commerce', 'online satış', 'online shop', 'mağaza', 'store', 'marketplace', 'pazar yeri'],
            'finans': ['finans', 'finance', 'sigorta', 'insurance', 'bankacılık', 'banking', 'yatırım', 'investment', 'kredi', 'credit', 'finansal'],
            'sağlık': ['sağlık', 'health', 'medikal', 'medical', 'tıp', 'medicine', 'hastane', 'hospital', 'klinik', 'clinic', 'ilaç', 'pharmaceutical', 'tedavi', 'treatment'],
            'eğitim': ['eğitim', 'education', 'öğretim', 'training', 'okul', 'school', 'üniversite', 'university', 'kurs', 'course', 'akademi', 'academy', 'öğrenci', 'student'],
            'turizm': ['turizm', 'tourism', 'otel', 'hotel', 'konaklama', 'accommodation', 'restoran', 'restaurant', 'cafe', 'kafe', 'yiyecek', 'food', 'içecek', 'beverage'],
            'lojistik': ['lojistik', 'logistics', 'taşımacılık', 'transportation', 'kargo', 'cargo', 'nakliye', 'shipping', 'depo', 'warehouse', 'dağıtım', 'tedarik', 'supply'],
            'inşaat': ['inşaat', 'construction', 'gayrimenkul', 'real estate', 'emlak', 'property', 'mimarlık', 'architecture', 'mühendislik', 'engineering', 'proje', 'yapı'],
            'hukuk': ['hukuk', 'law', 'avukat', 'lawyer', 'attorney', 'legal', 'dava', 'case', 'mahkeme', 'court'],
            'otomotiv': ['otomotiv', 'automotive', 'otomobil', 'automobile', 'araç', 'vehicle', 'araba', 'car', 'motor', 'yedek parça'],
            'enerji': ['enerji', 'energy', 'elektrik', 'electric', 'güneş', 'solar', 'rüzgar', 'wind', 'yenilenebilir', 'renewable'],
            'tarım': ['tarım', 'agriculture', 'çiftçi', 'farmer', 'hayvancılık', 'livestock', 'gıda', 'food', 'organik', 'organic']
        }
        
        found_keywords = []
        keyword_counts = {}
        
        # Her kategori için anahtar kelimeleri say
        for category, keywords in industry_categories.items():
            count = 0
            for keyword in keywords:
                occurrences = text.count(keyword)
                if occurrences > 0:
                    count += occurrences
                    if keyword not in keyword_counts:
                        keyword_counts[keyword] = 0
                    keyword_counts[keyword] += occurrences
            
            if count > 3:  # En az 3 kez geçmeli
                found_keywords.append(category)
        
        # En çok geçen spesifik kelimeleri de ekle
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        for keyword, count in sorted_keywords[:5]:
            if count >= 2 and keyword not in found_keywords and len(keyword) > 3:
                found_keywords.append(keyword)
        
        return found_keywords[:8]  # Max 8 anahtar kelime
    
    def get_page_title(self, soup: BeautifulSoup) -> str:
        """Sayfa başlığını al"""
        try:
            # Title tag'ini bul
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.text.strip()
            
            # Alternatif olarak h1 başlığını dene
            h1_tag = soup.find('h1')
            if h1_tag:
                return h1_tag.text.strip()
            
            # Meta og:title'ı dene
            og_title = soup.find('meta', property='og:title')
            if og_title:
                return og_title.get('content', '').strip()
            
            return "Başlık Bulunamadı"
        except Exception as e:
            print(f"Başlık alma hatası: {str(e)}")
            return "Başlık Bulunamadı"
    
    def get_meta_description(self, soup: BeautifulSoup) -> str:
        """Meta description al"""
        try:
            # Meta description tag'ini bul
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                return meta_desc.get('content', '').strip()
            
            # Alternatif olarak og:description'ı dene
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                return og_desc.get('content', '').strip()
            
            return ""
        except Exception as e:
            print(f"Description alma hatası: {str(e)}")
            return ""
    
    def get_meta_keywords(self, soup: BeautifulSoup) -> str:
        """Meta keywords al"""
        try:
            # Meta keywords tag'ini bul
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                return meta_keywords.get('content', '').strip()
            
            return ""
        except Exception as e:
            print(f"Keywords alma hatası: {str(e)}")
            return ""
    
    def scrape_important_subpages(self, driver, base_url: str, domain: str) -> Dict:
        """Önemli alt sayfaları daha detaylı tara"""
        subpages_data = {}
        
        # Taranacak sayfa tipleri ve URL pattern'leri
        important_pages = {
            'contact': ['iletisim', 'contact', 'bizeulasin', 'bize-ulasin', 'contact-us', 'iletişim'],
            'about': ['hakkimizda', 'about', 'kurumsal', 'corporate', 'about-us', 'hakkımızda'],
            'team': ['ekip', 'team', 'ekibimiz', 'our-team', 'kadromuz', 'takım'],
            'services': ['hizmetler', 'services', 'urunler', 'products', 'çözümler', 'solutions'],
            'pricing': ['fiyat', 'pricing', 'ücret', 'price', 'paket', 'plan']
        }
        
        try:
            # Driver hala açık mı kontrol et
            try:
                _ = driver.current_url
            except:
                print("❌ Driver kapalı, alt sayfa taraması yapılamıyor")
                return subpages_data
            
            # Ana sayfadaki tüm linkleri al
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_links = soup.find_all('a', href=True)
            
            visited_urls = set()
            
            for page_type, patterns in important_pages.items():
                found = False
                
                for link in all_links:
                    if found:
                        break
                    
                    href = link.get('href', '')
                    link_text = link.text.lower().strip()
                    
                    # Pattern kontrolü
                    for pattern in patterns:
                        if pattern in link_text or pattern in href.lower():
                            full_url = urljoin(base_url, href)
                            
                            # URL kontrolü
                            if self.should_scrape_url(full_url, base_url, visited_urls):
                                visited_urls.add(full_url)
                                found = True
                                
                                print(f"📄 {page_type.capitalize()} sayfası taranıyor: {full_url}")
                                
                                try:
                                    # Driver kontrolü
                                    try:
                                        _ = driver.current_url
                                    except:
                                        print("❌ Driver kapalı, tarama durduruluyor")
                                        return subpages_data
                                    
                                    # İnsan davranışı simülasyonu
                                    time.sleep(random.uniform(2, 4))
                                    
                                    # Sayfayı ziyaret et
                                    driver.get(full_url)
                                    self.wait_for_page_load(driver)
                                    
                                    # İçeriği al
                                    page_soup = BeautifulSoup(driver.page_source, 'html.parser')
                                    page_text = self.get_text_content(page_soup)
                                    page_source = driver.page_source
                                    
                                    # Email ve telefon ara
                                    page_emails = self.extract_emails_advanced(page_source, domain)
                                    
                                    # Gizli emailleri de bul
                                    hidden_emails = self.extract_hidden_emails(driver, page_soup)
                                    page_emails.extend(hidden_emails)
                                    
                                    page_phones = self.extract_phone_numbers(page_source)
                                    
                                    # Özel içerik çıkarma
                                    special_content = {}
                                    
                                    if page_type == 'contact':
                                        # Adres bilgisi ara
                                        address = self.extract_address(page_soup)
                                        if address:
                                            special_content['address'] = address
                                        
                                        # Çalışma saatleri
                                        hours = self.extract_working_hours(page_soup)
                                        if hours:
                                            special_content['working_hours'] = hours
                                    
                                    elif page_type == 'team':
                                        # Takım üyeleri
                                        team_members = self.extract_team_members(page_soup)
                                        if team_members:
                                            special_content['team_members'] = team_members
                                            # Team member email'lerini de ekle
                                            for member in team_members:
                                                if member.get('email'):
                                                    page_emails.append({
                                                        'email': member['email'],
                                                        'type': 'personal',
                                                        'source': 'team_page',
                                                        'status': 'found',
                                                        'score': 90,
                                                        'first_name': member.get('name', '').split()[0] if member.get('name') else '',
                                                        'last_name': member.get('name', '').split()[-1] if member.get('name') else '',
                                                        'position': member.get('position', '')
                                                    })
                                    
                                    elif page_type == 'pricing':
                                        # Fiyat bilgileri
                                        pricing = self.extract_pricing_info(page_soup)
                                        if pricing:
                                            special_content['pricing_details'] = pricing
                                    
                                    subpages_data[f'{page_type}_page'] = {
                                        'url': full_url,
                                        'text': page_text[:3000],
                                        'emails': page_emails,
                                        'phones': page_phones,
                                        **special_content
                                    }
                                    
                                    break
                                    
                                except Exception as e:
                                    print(f"⚠️ {page_type} sayfası tarama hatası: {str(e)}")
                                    # Eğer window kapalıysa döngüden çık
                                    if "no such window" in str(e) or "target window already closed" in str(e):
                                        print("❌ Tarayıcı penceresi kapandı, tarama durduruluyor")
                                        return subpages_data
                
        except Exception as e:
            print(f"❌ Alt sayfa tarama genel hatası: {str(e)}")
        
        finally:
            # Ana sayfaya geri dön
            try:
                if driver:
                    driver.get(base_url)
            except:
                pass
        
        return subpages_data
    
    def should_scrape_url(self, url: str, base_url: str, visited_urls: set) -> bool:
        """URL'in taranıp taranmayacağını kontrol et"""
        # Zaten ziyaret edilmişse
        if url in visited_urls:
            return False
        
        # Dosya uzantıları kontrolü
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Domain kontrolü
        try:
            base_domain = urlparse(base_url).netloc
            url_domain = urlparse(url).netloc
            if base_domain != url_domain:
                return False
        except:
            return False
        
        # URL derinliği kontrolü (max 3 seviye)
        try:
            path = urlparse(url).path.strip('/')
            if path.count('/') > 3:
                return False
        except:
            pass
        
        return True
    
    def extract_address(self, soup: BeautifulSoup) -> str:
        """Adres bilgisini çıkar"""
        # Yaygın adres pattern'leri
        address_keywords = ['adres', 'address', 'konum', 'location', 'ofis', 'office', 'merkez', 'center']
        
        for keyword in address_keywords:
            # Başlık ara
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b']:
                headers = soup.find_all(tag, text=re.compile(keyword, re.I))
                for header in headers:
                    # Sonraki elementi al
                    next_sibling = header.find_next_sibling()
                    if next_sibling:
                        address = next_sibling.text.strip()
                        if len(address) > 10 and len(address) < 300:
                            return address
            
            # Div veya p içinde ara
            for tag in ['div', 'p', 'span', 'address']:
                elements = soup.find_all(tag)
                for elem in elements:
                    text = elem.text.lower()
                    if keyword in text and ('mahalle' in text or 'sokak' in text or 'cadde' in text or 'bulvar' in text):
                        address = elem.text.strip()
                        if len(address) > 20 and len(address) < 300:
                            return address
        
        return ""
    
    def extract_working_hours(self, soup: BeautifulSoup) -> str:
        """Çalışma saatlerini çıkar"""
        hours_keywords = ['çalışma saatleri', 'working hours', 'açık saatler', 'open hours', 'mesai', 'iş saatleri']
        
        for keyword in hours_keywords:
            # Text içinde ara
            text = soup.get_text()
            pattern = rf'{keyword}[^\n]*[\n\r]{{0,2}}[^\n]*'
            match = re.search(pattern, text, re.I)
            if match:
                hours_text = match.group(0)
                # Gün ve saat pattern'i
                if re.search(r'(pazartesi|monday|pzt|pazar|sunday|paz)', hours_text, re.I):
                    return hours_text[:500]
        
        return ""
    
    def extract_team_members(self, soup: BeautifulSoup) -> List[Dict]:
        """Takım üyelerini çıkar"""
        team_members = []
        
        # Takım kartları genelde bu class'larda olur
        team_cards = soup.find_all(['div', 'article', 'li'], class_=re.compile('team|member|person|staff|ekip|çalışan', re.I))
        
        for card in team_cards[:20]:  # Max 20 kişi
            member = {}
            
            # İsim
            name_elem = card.find(['h2', 'h3', 'h4', 'h5', 'span'], class_=re.compile('name|title|isim|ad', re.I))
            if not name_elem:
                name_elem = card.find(['h2', 'h3', 'h4', 'h5'])
            
            if name_elem:
                member['name'] = name_elem.text.strip()
            
            # Pozisyon
            position_elem = card.find(['p', 'span', 'div'], class_=re.compile('position|role|title|görev|pozisyon', re.I))
            if position_elem:
                member['position'] = position_elem.text.strip()
            
            # Email
            email_match = re.search(self.email_patterns[0], card.text)
            if email_match:
                email = self.clean_email(email_match.group(0))
                if self.validate_email_improved(email):
                    member['email'] = email
            
            # LinkedIn
            linkedin_link = card.find('a', href=re.compile('linkedin.com', re.I))
            if linkedin_link:
                member['linkedin'] = linkedin_link.get('href')
            
            if member.get('name'):
                team_members.append(member)
        
        return team_members
    
    def extract_emails_advanced(self, text: str, domain: str) -> List[Dict]:
        """Gelişmiş email çıkarma ve doğrulama"""
        found_emails = []
        unique_emails = set()  # Duplicate kontrolü için
        
        # Tüm pattern'leri dene
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                # Tuple ise ilk elemanı al (gruplu regex için)
                if isinstance(match, tuple):
                    match = match[0]
                
                # Email'i temizle
                email = self.clean_email(match)
                
                # Duplicate ve validation kontrolü
                if email and self.validate_email_improved(email) and email.lower() not in unique_emails:
                    unique_emails.add(email.lower())
                    
                    # Email tipini belirle
                    email_type = self.determine_email_type(email)
                    
                    found_emails.append({
                        'email': email,
                        'type': email_type,
                        'source': 'website',
                        'status': 'found',  # Gerçek email
                        'score': self.calculate_email_score_by_type(email_type),
                        'first_name': '',
                        'last_name': '',
                        'position': self.guess_position_from_email(email)
                    })
        
        # JavaScript ve HTML attribute'larından email ara
        js_emails = self.extract_emails_from_html_attributes(text)
        for email in js_emails:
            if email.lower() not in unique_emails:
                unique_emails.add(email.lower())
                found_emails.append({
                    'email': email,
                    'type': self.determine_email_type(email),
                    'source': 'html_attribute',
                    'status': 'found',
                    'score': 65,
                    'first_name': '',
                    'last_name': '',
                    'position': self.guess_position_from_email(email)
                })
        
        return found_emails
    
    def extract_emails_from_html_attributes(self, html: str) -> List[str]:
        """HTML attribute'larından email çıkar"""
        emails = []
        
        # Çeşitli HTML pattern'leri
        patterns = [
            r'href="mailto:([^"]+)"',
            r'href=\'mailto:([^\']+)\'',
            r'data-email="([^"]+)"',
            r'data-mail="([^"]+)"',
            r'onclick=".*?\'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\'.*?"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                email = self.clean_email(match)
                if self.validate_email_improved(email):
                    emails.append(email)
        
        # Encoded emails
        encoded_pattern = r'&#\d+;'
        if re.search(encoded_pattern, html):
            try:
                # HTML entity decode
                import html as html_lib
                decoded = html_lib.unescape(html)
                
                # Decoded metinde email ara
                decoded_emails = re.findall(self.email_patterns[0], decoded, re.IGNORECASE)
                for email in decoded_emails:
                    clean = self.clean_email(email)
                    if self.validate_email_improved(clean):
                        emails.append(clean)
            except:
                pass
        
        return list(set(emails))  # Unique
    
    def get_price_context(self, text: str, price: str) -> str:
        """Fiyatın bağlamını al"""
        try:
            # Fiyatın etrafındaki metni al
            index = text.find(price)
            if index != -1:
                start = max(0, index - 50)
                end = min(len(text), index + len(price) + 50)
                return text[start:end].strip()
        except:
            pass
        return ""