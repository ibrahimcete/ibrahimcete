#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Vision Analyzer - Ürün Görselleri Analizi
OpenAI GPT-4 Vision ile e-ticaret ürün görselleri analizi
"""

import base64
import json
import time
from typing import Dict, List, Any, Optional
from io import BytesIO
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI kütüphanesi yüklü değil")

try:
    from PIL import Image
    import requests
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False
    print("⚠️ PIL veya requests yüklü değil")


class AIVisionAnalyzer:
    """AI Vision ile ürün görselleri analizi"""
    
    def __init__(self, api_key: str = None):
        """
        Args:
            api_key: OpenAI API anahtarı
        """
        self.api_key = api_key
        if api_key and OPENAI_AVAILABLE:
            openai.api_key = api_key
        
        # Maliyet bilgileri (GPT-4 Vision fiyatları)
        self.pricing = {
            'gpt-4-vision-preview': {
                'input_per_1k': 0.01,      # $0.01 per 1K tokens
                'output_per_1k': 0.03,     # $0.03 per 1K tokens
                'image_base': 0.00765,     # Base cost per image (low detail)
                'image_high': 0.01445      # High detail per image
            },
            'gpt-4o': {
                'input_per_1k': 0.005,     # $0.005 per 1K tokens
                'output_per_1k': 0.015,    # $0.015 per 1K tokens
                'image_base': 0.00765,
                'image_high': 0.01445
            }
        }
        
        # Maliyet takibi
        self.usage_stats = {
            'total_cost': 0.0,
            'total_images': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'requests': [],
            'session_start': datetime.now().isoformat()
        }
    
    def encode_image_from_url(self, image_url: str, max_size: tuple = (1024, 1024)) -> Optional[str]:
        """
        URL'den görsel indir ve base64'e çevir
        
        Args:
            image_url: Görsel URL'i
            max_size: Maksimum boyut (maliyet optimizasyonu için)
        
        Returns:
            Base64 encoded görsel veya None
        """
        try:
            # Görseli indir
            response = requests.get(image_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # PIL Image'e çevir
            image = Image.open(BytesIO(response.content))
            
            # RGB'ye çevir (RGBA ise)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Boyutu küçült (maliyet optimizasyonu)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Base64'e çevir
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=85, optimize=True)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            print(f"⚠️ Görsel yükleme hatası ({image_url}): {e}")
            return None
    
    def analyze_product_image(self, image_url: str, detail: str = "low") -> Dict[str, Any]:
        """
        Tek bir ürün görselini analiz et
        
        Args:
            image_url: Görsel URL'i
            detail: "low" veya "high" (maliyet etkiler)
        
        Returns:
            Analiz sonucu ve maliyet bilgisi
        """
        if not self.api_key or not OPENAI_AVAILABLE:
            return {
                'success': False,
                'error': 'OpenAI API key gerekli',
                'cost': 0
            }
        
        # Görseli hazırla
        base64_image = self.encode_image_from_url(image_url)
        
        if not base64_image:
            return {
                'success': False,
                'error': 'Görsel yüklenemedi',
                'cost': 0
            }
        
        try:
            start_time = time.time()
            
            # GPT-4 Vision API çağrısı
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Bu ürün görselini analiz et ve aşağıdaki bilgileri JSON formatında ver:

{
    "product_name": "Ürün adı",
    "category": "Kategori",
    "description": "Kısa açıklama",
    "features": ["özellik1", "özellik2"],
    "colors": ["renk1", "renk2"],
    "materials": ["malzeme1", "malzeme2"],
    "style": "Modern/Klasik/vb",
    "quality_indicators": ["kalite göstergesi1", "gösterge2"],
    "price_estimate": "Düşük/Orta/Yüksek",
    "target_audience": "Hedef kitle",
    "is_product_image": true/false,
    "confidence": 0-100
}

Eğer bu bir ürün görseli değilse (logo, banner, vb.), is_product_image: false olarak işaretle."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": detail
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            elapsed_time = time.time() - start_time
            
            # Yanıtı parse et
            content = response.choices[0].message.content
            
            # JSON'u çıkar
            try:
                # Markdown code block'ları temizle
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(content)
            except json.JSONDecodeError:
                analysis = {
                    'raw_response': content,
                    'is_product_image': True,
                    'confidence': 50
                }
            
            # Maliyet hesapla
            usage = response.usage
            cost = self.calculate_cost(
                model="gpt-4-vision-preview",
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                images=1,
                detail=detail
            )
            
            # İstatistikleri güncelle
            self.update_usage_stats(
                cost=cost,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                images=1,
                elapsed_time=elapsed_time
            )
            
            result = {
                'success': True,
                'analysis': analysis,
                'cost': cost,
                'tokens': {
                    'input': usage.prompt_tokens,
                    'output': usage.completion_tokens,
                    'total': usage.total_tokens
                },
                'elapsed_time': elapsed_time,
                'image_url': image_url
            }
            
            print(f"✅ Görsel analiz edildi - Maliyet: ${cost:.4f}")
            
            return result
            
        except Exception as e:
            print(f"❌ AI Vision hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'cost': 0
            }
    
    def analyze_product_images_batch(self, image_urls: List[str], 
                                     max_images: int = 10,
                                     detail: str = "low") -> Dict[str, Any]:
        """
        Birden fazla ürün görselini toplu analiz et
        
        Args:
            image_urls: Görsel URL listesi
            max_images: Maksimum analiz edilecek görsel sayısı
            detail: "low" veya "high"
        
        Returns:
            Toplu analiz sonuçları
        """
        print(f"\n🖼️ {len(image_urls)} görsel analiz edilecek (max: {max_images})")
        
        results = []
        total_cost = 0
        product_images = []
        
        for i, url in enumerate(image_urls[:max_images], 1):
            print(f"\n[{i}/{min(len(image_urls), max_images)}] Analiz ediliyor...")
            
            result = self.analyze_product_image(url, detail=detail)
            results.append(result)
            
            if result['success']:
                total_cost += result['cost']
                
                # Sadece ürün görsellerini kaydet
                analysis = result.get('analysis', {})
                if analysis.get('is_product_image', False):
                    product_images.append({
                        'url': url,
                        'analysis': analysis,
                        'cost': result['cost']
                    })
            
            # Rate limiting (API limitleri için)
            if i < min(len(image_urls), max_images):
                time.sleep(1)
        
        summary = {
            'success': True,
            'total_images_analyzed': len(results),
            'product_images_found': len(product_images),
            'total_cost': total_cost,
            'results': results,
            'product_images': product_images,
            'summary_stats': self.get_usage_summary()
        }
        
        print(f"\n✅ Toplu analiz tamamlandı")
        print(f"   • Toplam görsel: {len(results)}")
        print(f"   • Ürün görseli: {len(product_images)}")
        print(f"   • Toplam maliyet: ${total_cost:.4f}")
        
        return summary
    
    def calculate_cost(self, model: str, input_tokens: int, 
                      output_tokens: int, images: int = 0, 
                      detail: str = "low") -> float:
        """
        API çağrısı maliyetini hesapla
        
        Args:
            model: Model adı
            input_tokens: Input token sayısı
            output_tokens: Output token sayısı
            images: Görsel sayısı
            detail: Görsel detay seviyesi
        
        Returns:
            Maliyet (USD)
        """
        if model not in self.pricing:
            model = "gpt-4-vision-preview"
        
        pricing = self.pricing[model]
        
        # Token maliyeti
        input_cost = (input_tokens / 1000) * pricing['input_per_1k']
        output_cost = (output_tokens / 1000) * pricing['output_per_1k']
        
        # Görsel maliyeti
        if detail == "high":
            image_cost = images * pricing['image_high']
        else:
            image_cost = images * pricing['image_base']
        
        total_cost = input_cost + output_cost + image_cost
        
        return total_cost
    
    def update_usage_stats(self, cost: float, input_tokens: int, 
                          output_tokens: int, images: int, 
                          elapsed_time: float):
        """İstatistikleri güncelle"""
        self.usage_stats['total_cost'] += cost
        self.usage_stats['total_images'] += images
        self.usage_stats['total_input_tokens'] += input_tokens
        self.usage_stats['total_output_tokens'] += output_tokens
        
        self.usage_stats['requests'].append({
            'timestamp': datetime.now().isoformat(),
            'cost': cost,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'images': images,
            'elapsed_time': elapsed_time
        })
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Kullanım özetini al"""
        return {
            'total_cost': round(self.usage_stats['total_cost'], 4),
            'total_images': self.usage_stats['total_images'],
            'total_input_tokens': self.usage_stats['total_input_tokens'],
            'total_output_tokens': self.usage_stats['total_output_tokens'],
            'total_requests': len(self.usage_stats['requests']),
            'session_start': self.usage_stats['session_start'],
            'average_cost_per_image': round(
                self.usage_stats['total_cost'] / max(self.usage_stats['total_images'], 1),
                4
            )
        }
    
    def reset_usage_stats(self):
        """İstatistikleri sıfırla"""
        self.usage_stats = {
            'total_cost': 0.0,
            'total_images': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'requests': [],
            'session_start': datetime.now().isoformat()
        }
        print("✅ İstatistikler sıfırlandı")
    
    def save_usage_stats(self, filename: str = "ai_vision_usage.json"):
        """İstatistikleri dosyaya kaydet"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.usage_stats, f, ensure_ascii=False, indent=2)
            print(f"✅ İstatistikler '{filename}' dosyasına kaydedildi")
        except Exception as e:
            print(f"❌ Kayıt hatası: {e}")
    
    def load_usage_stats(self, filename: str = "ai_vision_usage.json"):
        """İstatistikleri dosyadan yükle"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.usage_stats = json.load(f)
            print(f"✅ İstatistikler '{filename}' dosyasından yüklendi")
        except FileNotFoundError:
            print(f"⚠️ '{filename}' dosyası bulunamadı")
        except Exception as e:
            print(f"❌ Yükleme hatası: {e}")


class EcommerceImageExtractor:
    """E-ticaret sitelerinden ürün görselleri çıkarma"""
    
    def __init__(self, driver=None):
        """
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
    
    def extract_product_images(self, soup, url: str) -> List[Dict[str, str]]:
        """
        E-ticaret sitesinden ürün görsellerini çıkar
        
        Args:
            soup: BeautifulSoup object
            url: Site URL'i
        
        Returns:
            Ürün görselleri listesi
        """
        from urllib.parse import urljoin
        import re
        
        product_images = []
        
        # E-ticaret göstergeleri
        ecommerce_indicators = [
            'product', 'item', 'urun', 'catalog', 'shop',
            'store', 'magaza', 'sepet', 'cart'
        ]
        
        # Ürün görseli class/id pattern'leri
        product_patterns = [
            r'product.*image',
            r'item.*image',
            r'urun.*resim',
            r'catalog.*img',
            r'shop.*image',
            r'gallery.*image'
        ]
        
        # Tüm img tag'lerini bul
        all_images = soup.find_all('img')
        
        for img in all_images:
            # Görsel URL'i al
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            
            if not img_url:
                continue
            
            # Tam URL'e çevir
            img_url = urljoin(url, img_url)
            
            # Küçük görselleri filtrele (logo, icon vb.)
            width = img.get('width')
            height = img.get('height')
            
            try:
                if width and int(width) < 100:
                    continue
                if height and int(height) < 100:
                    continue
            except:
                pass
            
            # Class ve ID kontrol et
            img_class = ' '.join(img.get('class', [])).lower()
            img_id = img.get('id', '').lower()
            img_alt = img.get('alt', '').lower()
            
            # Ürün görseli mi kontrol et
            is_product_image = False
            
            # Pattern kontrolü
            for pattern in product_patterns:
                if re.search(pattern, img_class, re.I) or re.search(pattern, img_id, re.I):
                    is_product_image = True
                    break
            
            # Indicator kontrolü
            if not is_product_image:
                for indicator in ecommerce_indicators:
                    if indicator in img_class or indicator in img_id or indicator in img_alt:
                        is_product_image = True
                        break
            
            # Parent element kontrolü
            if not is_product_image:
                parent = img.parent
                if parent:
                    parent_class = ' '.join(parent.get('class', [])).lower()
                    parent_id = parent.get('id', '').lower()
                    
                    for indicator in ecommerce_indicators:
                        if indicator in parent_class or indicator in parent_id:
                            is_product_image = True
                            break
            
            if is_product_image:
                product_images.append({
                    'url': img_url,
                    'alt': img.get('alt', ''),
                    'class': img_class,
                    'id': img_id
                })
        
        # Tekrarları temizle
        seen_urls = set()
        unique_images = []
        
        for img in product_images:
            if img['url'] not in seen_urls:
                seen_urls.add(img['url'])
                unique_images.append(img)
        
        print(f"🖼️ {len(unique_images)} ürün görseli bulundu")
        
        return unique_images


# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 AI Vision Analyzer Test\n")
    
    # API key (test için)
    api_key = input("OpenAI API Key girin (test için): ").strip()
    
    if not api_key:
        print("❌ API key gerekli")
        exit()
    
    # Analyzer oluştur
    analyzer = AIVisionAnalyzer(api_key=api_key)
    
    # Test görseli
    test_image_url = input("Test görsel URL'i girin: ").strip()
    
    if test_image_url:
        print("\n🔍 Görsel analiz ediliyor...\n")
        
        result = analyzer.analyze_product_image(test_image_url, detail="low")
        
        if result['success']:
            print("\n✅ Analiz Başarılı!\n")
            print(json.dumps(result['analysis'], indent=2, ensure_ascii=False))
            print(f"\n💰 Maliyet: ${result['cost']:.4f}")
            print(f"⏱️ Süre: {result['elapsed_time']:.2f} saniye")
        else:
            print(f"\n❌ Hata: {result['error']}")
    
    # Özet istatistikler
    print("\n📊 Kullanım Özeti:")
    summary = analyzer.get_usage_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))

