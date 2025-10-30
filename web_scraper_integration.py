#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web Scraper Entegrasyon Modülü
Mevcut web_scraper.py ile yeni enhanced_web_scraper.py'yi birleştirir
"""

import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Mevcut web scraper
try:
    from web_scraper import WebScraper
    LEGACY_SCRAPER_AVAILABLE = True
except ImportError:
    LEGACY_SCRAPER_AVAILABLE = False
    print("⚠️ Mevcut web_scraper yüklenemedi")

# Yeni gelişmiş scraper
try:
    from enhanced_web_scraper import EnhancedWebScraper
    ENHANCED_SCRAPER_AVAILABLE = True
except ImportError:
    ENHANCED_SCRAPER_AVAILABLE = False
    print("⚠️ Gelişmiş web_scraper yüklenemedi")

# Database
try:
    from database import Database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("⚠️ Database modülü yüklenemedi")


class UnifiedWebScraper:
    """
    Birleşik Web Scraper - Hem eski hem yeni özellikleri destekler
    """
    
    def __init__(self, use_enhanced: bool = True, openai_api_key: str = None, cost_tracker=None):
        """
        Args:
            use_enhanced: True ise gelişmiş scraper kullanılır
            openai_api_key: OpenAI API anahtarı
            cost_tracker: APICostWidget instance (maliyet takibi için)
        """
        self.use_enhanced = use_enhanced and ENHANCED_SCRAPER_AVAILABLE
        self.openai_api_key = openai_api_key
        self.cost_tracker = cost_tracker
        
        # Scraper'ları başlat
        if self.use_enhanced:
            print("🚀 Gelişmiş Web Scraper aktif")
            self.enhanced_scraper = EnhancedWebScraper(
                use_proxy=False,
                use_ai_vision=True,
                openai_api_key=openai_api_key
            )
        
        if LEGACY_SCRAPER_AVAILABLE:
            print("📡 Standart Web Scraper yedek olarak hazır")
            self.legacy_scraper = WebScraper(use_proxy=False, use_ai_vision=True)
        
        # Database bağlantısı
        if DATABASE_AVAILABLE:
            self.db = Database()
        else:
            self.db = None
    
    def scrape_website(self, url: str, company_name: str = "", 
                      firm_id: Optional[int] = None,
                      save_to_db: bool = True) -> Dict[str, Any]:
        """
        Web sitesini tara - Birleşik fonksiyon
        
        Args:
            url: Website URL'i
            company_name: Firma adı
            firm_id: Veritabanı firma ID'si (varsa)
            save_to_db: Sonuçları veritabanına kaydet
        
        Returns:
            Scraping sonuçları
        """
        print(f"\n{'='*70}")
        print(f"🌐 WEB SCRAPING BAŞLATILIYOR")
        print(f"{'='*70}")
        print(f"📍 URL: {url}")
        print(f"🏢 Firma: {company_name}")
        print(f"🔧 Mod: {'Gelişmiş' if self.use_enhanced else 'Standart'}")
        print(f"{'='*70}\n")
        
        result = {
            'success': False,
            'url': url,
            'company_name': company_name,
            'firm_id': firm_id,
            'scraped_at': datetime.now().isoformat(),
            'scraper_type': 'enhanced' if self.use_enhanced else 'legacy',
            'data': {}
        }
        
        try:
            # URL tipini kontrol et - Facebook sayfası mı?
            if self._is_facebook_url(url):
                print("📘 Facebook sayfası tespit edildi - Facebook-only scraping başlatılıyor...")
                if self.use_enhanced:
                    # Facebook-only scraping
                    enhanced_result = self.enhanced_scraper.scrape_facebook_only(url, company_name)
                else:
                    # Legacy scraper ile Facebook scraping
                    enhanced_result = self.legacy_scraper.scrape_facebook_only(url, company_name)
            else:
                # Normal website scraping
                if self.use_enhanced:
                    # Gelişmiş scraper kullan
                    enhanced_result = self.enhanced_scraper.scrape_website_enhanced(url, company_name)
                    
                    if enhanced_result.get('success'):
                        result['success'] = True
                        result['data'] = enhanced_result
                        
                        # Özet bilgileri
                        result['summary'] = self._create_summary(enhanced_result)
                        
                        # Maliyet takibi
                        if self.cost_tracker:
                            self._update_cost_tracker(enhanced_result)
                        
                        # Veritabanına kaydet
                        if save_to_db and self.db and firm_id:
                            self._save_to_database(firm_id, enhanced_result)
                        
                        self._print_results(enhanced_result)
                    else:
                        raise Exception(enhanced_result.get('error', 'Bilinmeyen hata'))
                else:
                    # Standart scraper kullan (fallback)
                    if LEGACY_SCRAPER_AVAILABLE:
                        legacy_result = self.legacy_scraper.scrape_website(url, company_name)
                        
                        if legacy_result:
                            result['success'] = True
                            result['data'] = legacy_result
                            result['summary'] = {
                                'emails_found': len(legacy_result.get('emails', [])),
                                'phones_found': len(legacy_result.get('phone_numbers', [])),
                                'has_website': bool(legacy_result.get('website'))
                            }
                            
                            print(f"✅ Standart scraping tamamlandı")
                            print(f"📧 Email: {result['summary']['emails_found']}")
                            print(f"📞 Telefon: {result['summary']['phones_found']}")
                        else:
                            raise Exception("Standart scraper veri döndürmedi")
                    else:
                        raise Exception("Hiçbir scraper mevcut değil")
        
        except Exception as e:
            print(f"\n❌ HATA: {str(e)}\n")
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def _is_facebook_url(self, url: str) -> bool:
        """URL'nin Facebook sayfası olup olmadığını kontrol et"""
        if not url:
            return False
        
        facebook_patterns = [
            'facebook.com/',
            'fb.com/',
            'm.facebook.com/',
            'www.facebook.com/'
        ]
        
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in facebook_patterns)
    
    def _create_summary(self, enhanced_result: Dict) -> Dict:
        """Gelişmiş scraping sonuçlarından özet oluştur"""
        summary = {}
        
        # Firma tipi
        company_type = enhanced_result.get('company_type_analysis', {})
        summary['company_type'] = company_type.get('primary_type_tr', 'Belirsiz')
        summary['company_type_confidence'] = company_type.get('confidence', 0)
        
        # Kalite skoru
        quality = enhanced_result.get('quality_score', {})
        summary['quality_score'] = quality.get('total_score', 0)
        summary['quality_grade'] = quality.get('grade', 'N/A')
        
        # Ürün/Hizmet
        products_services = enhanced_result.get('products_services', {})
        summary['products_count'] = products_services.get('product_count', 0)
        summary['services_count'] = products_services.get('service_count', 0)
        
        # Entegrasyonlar
        integrations = enhanced_result.get('integrations', {})
        summary['total_integrations'] = integrations.get('total_integrations', 0)
        summary['has_ecommerce'] = integrations.get('has_payment', False)
        summary['has_live_chat'] = integrations.get('has_live_chat', False)
        
        # İletişim
        contact = enhanced_result.get('contact_info', {})
        summary['emails_found'] = len(contact.get('emails', []))
        summary['phones_found'] = len(contact.get('phones', []))
        summary['social_media_count'] = len(contact.get('social_media', {}))
        
        # Sosyal medya analizi
        social_media = enhanced_result.get('social_media', {})
        if 'social_analysis' in social_media:
            social_analysis = social_media['social_analysis']
            summary['social_score'] = social_analysis.get('overall_social_score', 0)
            summary['has_facebook'] = social_analysis.get('facebook', {}).get('has_page', False)
            summary['has_instagram'] = social_analysis.get('instagram', {}).get('has_profile', False)
            summary['social_recommendations'] = social_analysis.get('recommendations', [])
        
        # Sosyal medya detayları
        social_details = enhanced_result.get('social_media_details', {})
        if 'facebook' in social_details:
            fb_data = social_details['facebook']
            summary['facebook_followers'] = fb_data.get('followers_count', 0)
            summary['facebook_likes'] = fb_data.get('likes_count', 0)
            summary['facebook_page_type'] = fb_data.get('page_type', '')
        
        if 'instagram' in social_details:
            ig_data = social_details['instagram']
            summary['instagram_followers'] = ig_data.get('followers_count', 0)
            summary['instagram_posts'] = ig_data.get('posts_count', 0)
            summary['instagram_is_business'] = ig_data.get('is_business', False)
        
        # Facebook-only scraping için özel özet
        if enhanced_result.get('facebook_details'):
            fb_details = enhanced_result['facebook_details']
            summary['is_facebook_only'] = True
            summary['facebook_page_name'] = fb_details.get('page_name', '')
            summary['facebook_followers'] = fb_details.get('followers_count', 0)
            summary['facebook_likes'] = fb_details.get('likes_count', 0)
            summary['facebook_page_type'] = fb_details.get('page_type', '')
        else:
            summary['is_facebook_only'] = False
        
        return summary
    
    def _save_to_database(self, firm_id: int, enhanced_result: Dict):
        """Gelişmiş scraping sonuçlarını veritabanına kaydet"""
        try:
            print(f"\n💾 Veritabanına kaydediliyor (Firma ID: {firm_id})...")
            
            success = self.db.update_firm_enhanced_scraping(firm_id, enhanced_result)
            
            if success:
                print(f"✅ Veritabanına kaydedildi")
            else:
                print(f"⚠️ Veritabanına kaydetme başarısız")
        
        except Exception as e:
            print(f"❌ Veritabanı kayıt hatası: {e}")
    
    def _update_cost_tracker(self, enhanced_result: Dict):
        """Maliyet takipçisini güncelle"""
        try:
            # Görsel analizi maliyeti
            image_analysis = enhanced_result.get('product_images_analysis', {})
            if image_analysis:
                cost = image_analysis.get('total_cost', 0)
                images = image_analysis.get('analyzed_images', 0)
                
                if cost > 0:
                    self.cost_tracker.update_cost(cost, requests=1, images=images)
                    print(f"💰 Maliyet güncellendi: ${cost:.4f}")
        
        except Exception as e:
            print(f"⚠️ Maliyet takip hatası: {e}")
    
    def _print_results(self, enhanced_result: Dict):
        """Sonuçları güzel formatta yazdır"""
        print(f"\n{'='*70}")
        print(f"📊 SCRAPING SONUÇLARI")
        print(f"{'='*70}\n")
        
        # Firma Tipi
        company_type = enhanced_result.get('company_type_analysis', {})
        print(f"🏭 Firma Tipi:")
        print(f"   • Tip: {company_type.get('primary_type_tr', 'Belirsiz')}")
        print(f"   • Güven: {company_type.get('confidence', 0):.1f}%")
        if company_type.get('secondary_types_tr'):
            print(f"   • Ek: {', '.join(company_type.get('secondary_types_tr', []))}")
        
        # Kalite Skoru
        quality = enhanced_result.get('quality_score', {})
        print(f"\n⭐ Kalite Skoru:")
        print(f"   • Toplam: {quality.get('total_score', 0):.1f}/100")
        print(f"   • Not: {quality.get('grade', 'N/A')}")
        print(f"   • İçerik: {quality.get('content_score', 0):.1f}/100")
        print(f"   • Teknik: {quality.get('technical_score', 0):.1f}/100")
        
        # Ürün/Hizmet
        products_services = enhanced_result.get('products_services', {})
        print(f"\n🛍️ Ürün/Hizmet:")
        print(f"   • Ürün: {products_services.get('product_count', 0)}")
        print(f"   • Hizmet: {products_services.get('service_count', 0)}")
        print(f"   • Kategori: {len(products_services.get('categories', []))}")
        
        # Entegrasyonlar
        integrations = enhanced_result.get('integrations', {})
        print(f"\n🔌 Entegrasyonlar:")
        print(f"   • Toplam: {integrations.get('total_integrations', 0)}")
        if integrations.get('integrations'):
            for category, items in integrations['integrations'].items():
                if items:
                    print(f"   • {category.title()}: {', '.join(items)}")
        
        # İletişim
        contact = enhanced_result.get('contact_info', {})
        print(f"\n📞 İletişim:")
        print(f"   • Email: {len(contact.get('emails', []))}")
        print(f"   • Telefon: {len(contact.get('phones', []))}")
        print(f"   • Sosyal Medya: {len(contact.get('social_media', {}))}")
        
        # Facebook-only scraping kontrolü
        if enhanced_result.get('facebook_details'):
            fb_details = enhanced_result['facebook_details']
            print(f"\n📘 Facebook-Only Analizi:")
            print(f"   • Sayfa Adı: {fb_details.get('page_name', 'Bilinmeyen')}")
            print(f"   • Sayfa Tipi: {fb_details.get('page_type', 'profil')}")
            if fb_details.get('followers_count', 0) > 0:
                print(f"   • Takipçi: {fb_details['followers_count']:,}")
            if fb_details.get('likes_count', 0) > 0:
                print(f"   • Beğeni: {fb_details['likes_count']:,}")
            
            # Facebook'tan çıkarılan bilgiler
            if enhanced_result.get('services'):
                print(f"\n🎯 Facebook'tan Çıkarılan Hizmetler:")
                for i, service in enumerate(enhanced_result['services'][:5], 1):
                    print(f"   {i}. {service}")
            
            if enhanced_result.get('about_text'):
                print(f"\n📝 Hakkımızda (Facebook'tan):")
                about_text = enhanced_result['about_text'][:200] + "..." if len(enhanced_result['about_text']) > 200 else enhanced_result['about_text']
                print(f"   {about_text}")
            
            print(f"\n📌 NOT: Bu firma sadece Facebook sayfası üzerinden faaliyet gösteriyor.")
        
        # Normal sosyal medya analizi
        social_media = enhanced_result.get('social_media', {})
        if 'social_analysis' in social_media:
            social_analysis = social_media['social_analysis']
            print(f"\n📱 Sosyal Medya Analizi:")
            print(f"   • Genel Skor: {social_analysis.get('overall_social_score', 0)}/100")
            
            # Facebook
            fb_data = social_analysis.get('facebook', {})
            if fb_data.get('has_page'):
                print(f"   • Facebook: ✅ {fb_data.get('page_type', 'profil')}")
                social_details = enhanced_result.get('social_media_details', {})
                if 'facebook' in social_details:
                    fb_details = social_details['facebook']
                    if fb_details.get('followers_count', 0) > 0:
                        print(f"     - Takipçi: {fb_details['followers_count']:,}")
                    if fb_details.get('likes_count', 0) > 0:
                        print(f"     - Beğeni: {fb_details['likes_count']:,}")
            else:
                print(f"   • Facebook: ❌ Sayfa bulunamadı")
            
            # Instagram
            ig_data = social_analysis.get('instagram', {})
            if ig_data.get('has_profile'):
                print(f"   • Instagram: ✅ {ig_data.get('profile_type', 'profil')}")
                social_details = enhanced_result.get('social_media_details', {})
                if 'instagram' in social_details:
                    ig_details = social_details['instagram']
                    if ig_details.get('followers_count', 0) > 0:
                        print(f"     - Takipçi: {ig_details['followers_count']:,}")
                    if ig_details.get('posts_count', 0) > 0:
                        print(f"     - Gönderi: {ig_details['posts_count']:,}")
                    if ig_details.get('is_business'):
                        print(f"     - İşletme Profili: ✅")
            else:
                print(f"   • Instagram: ❌ Profil bulunamadı")
            
            # Sosyal medya önerileri
            social_recs = social_analysis.get('recommendations', [])
            if social_recs:
                print(f"\n📱 Sosyal Medya Önerileri:")
                for i, rec in enumerate(social_recs[:3], 1):
                    print(f"   {i}. {rec}")
        
        # Öneriler
        recommendations = quality.get('recommendations', [])
        if recommendations:
            print(f"\n💡 İyileştirme Önerileri:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n{'='*70}\n")
    
    def get_statistics(self) -> Dict:
        """Gelişmiş scraping istatistiklerini getir"""
        if not self.db:
            return {}
        
        try:
            stats = self.db.get_enhanced_scraping_statistics()
            return stats
        except Exception as e:
            print(f"❌ İstatistik hatası: {e}")
            return {}
    
    def get_firms_by_type(self, company_type: str) -> list:
        """Firma tipine göre firmaları getir"""
        if not self.db:
            return []
        
        try:
            firms = self.db.get_firms_by_company_type(company_type)
            return firms
        except Exception as e:
            print(f"❌ Firma sorgulama hatası: {e}")
            return []
    
    def get_top_quality_firms(self, limit: int = 10) -> list:
        """En kaliteli firmaları getir"""
        if not self.db:
            return []
        
        try:
            firms = self.db.get_top_quality_firms(limit)
            return firms
        except Exception as e:
            print(f"❌ Top firma sorgulama hatası: {e}")
            return []


# Test fonksiyonu
if __name__ == "__main__":
    print("🧪 Unified Web Scraper Test\n")
    
    # Scraper oluştur
    scraper = UnifiedWebScraper(
        use_enhanced=True,
        openai_api_key=None  # API key buraya
    )
    
    # Test URL
    test_url = "https://www.example.com"
    
    # Scraping yap
    result = scraper.scrape_website(
        url=test_url,
        company_name="Test Firma",
        firm_id=None,
        save_to_db=False
    )
    
    if result['success']:
        print("\n✅ Test başarılı!")
        print(f"\nÖzet:")
        for key, value in result.get('summary', {}).items():
            print(f"  {key}: {value}")
    else:
        print(f"\n❌ Test başarısız: {result.get('error')}")
    
    # İstatistikler
    print("\n📊 Sistem İstatistikleri:")
    stats = scraper.get_statistics()
    if stats:
        print(f"  Taranan Firma: {stats.get('scraped_firms', 0)}")
        print(f"  Ortalama Kalite: {stats.get('avg_quality_score', 0)}")
        print(f"  E-ticaret Firma: {stats.get('ecommerce_firms', 0)}")
        
        if stats.get('company_types'):
            print(f"\n  Firma Tipleri:")
            for ctype, count in stats['company_types'].items():
                print(f"    • {ctype}: {count}")

