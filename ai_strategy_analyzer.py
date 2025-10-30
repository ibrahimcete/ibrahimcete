#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# OpenAI entegrasyonu
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """Strateji türleri"""
    AGGRESSIVE = "aggressive"  # Agresif takip
    CONSERVATIVE = "conservative"  # Muhafazakar yaklaşım
    EDUCATIONAL = "educational"  # Eğitici içerik
    PROMOTIONAL = "promotional"  # Promosyonel
    RELATIONSHIP = "relationship"  # İlişki odaklı
    TECHNICAL = "technical"  # Teknik odaklı

@dataclass
class FirmAnalysis:
    """Firma analiz sonucu"""
    firm_id: int
    firm_name: str
    sector: str
    ai_confidence: float
    strategy_recommendations: List[Dict]
    risk_assessment: Dict
    opportunity_score: float
    recommended_strategy: StrategyType
    ai_instructions: str
    custom_prompt: str
    analysis_date: str

@dataclass
class StrategyRecommendation:
    """Strateji önerisi"""
    strategy_type: StrategyType
    confidence: float
    reasoning: str
    expected_success_rate: float
    risk_level: str
    mail_frequency: int
    content_focus: List[str]
    timing_recommendations: Dict

class AIStrategyAnalyzer:
    """AI destekli strateji analizi ve öneri sistemi"""
    
    def __init__(self, database_path: str = "b2b_automation.db", knowledge_db_path: str = "ai_intelligence.db"):
        self.database_path = database_path
        self.knowledge_db_path = knowledge_db_path
        self.openai_client = None
        
        # OpenAI client'ı başlat
        self._setup_openai()
        
        # Veritabanı bağlantılarını test et
        self._test_connections()
    
    def _setup_openai(self):
        """OpenAI client'ını kur"""
        try:
            if OPENAI_AVAILABLE:
                # Önce ortam değişkeninden dene
                api_key = os.getenv('OPENAI_API_KEY')
                
                # Eğer ortam değişkeninde yoksa, config.json'dan dene
                if not api_key:
                    try:
                        with open('config.json', 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            api_key = config.get('openai_api_key')
                    except:
                        pass
                
                # Eğer hala yoksa, ai_center_settings.json'dan dene
                if not api_key:
                    try:
                        with open('ai_center_settings.json', 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                            api_key = settings.get('openai_api_key')
                    except:
                        pass
                
                if api_key:
                    self.openai_client = OpenAI(api_key=api_key)
                    logger.info("✅ OpenAI client başarıyla kuruldu")
                else:
                    logger.warning("⚠️ OpenAI API anahtarı bulunamadı. Lütfen OPENAI_API_KEY ortam değişkenini ayarlayın veya config.json dosyasına ekleyin.")
                    # Basit analiz moduna geç
                    self.openai_client = None
            else:
                logger.warning("⚠️ OpenAI kütüphanesi yüklü değil")
                self.openai_client = None
        except Exception as e:
            logger.error(f"❌ OpenAI kurulum hatası: {e}")
            self.openai_client = None
    
    def _test_connections(self):
        """Veritabanı bağlantılarını test et"""
        try:
            # Ana veritabanı testi
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM firms")
            firm_count = cursor.fetchone()[0]
            conn.close()
            logger.info(f"✅ Ana veritabanı bağlantısı başarılı - {firm_count} firma bulundu")
            
            # AI bilgi veritabanı testi
            if os.path.exists(self.knowledge_db_path):
                conn = sqlite3.connect(self.knowledge_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                logger.info(f"✅ AI bilgi veritabanı bağlantısı başarılı - {len(tables)} tablo bulundu")
            else:
                logger.warning("⚠️ AI bilgi veritabanı bulunamadı")
                
        except Exception as e:
            logger.error(f"❌ Veritabanı bağlantı hatası: {e}")
    
    def get_firm_data(self, firm_id: int) -> Optional[Dict]:
        """Firma verilerini getir"""
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Önce sütun isimlerini al
            cursor.execute("PRAGMA table_info(firms)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Firma verilerini getir
            cursor.execute("""
                SELECT id, name, phone, email, address, sector, summary, ai_summary, 
                       website, contact_person, last_contact_date, status, place_id, 
                       rating, review_count, business_hours, last_action, created_at, 
                       updated_at, is_analyzed, domain, title, description, keywords, 
                       emails, phone_numbers, social_media, business_info, text_content, 
                       services, products, pricing, about_text, team_size_estimate, 
                       industry_keywords, contact_page_url, advanced_features, 
                       scraped_data, company_score, ai_vision_analysis, company_type, 
                       company_type_confidence, company_type_analysis, quality_score, 
                       quality_grade, quality_analysis, products_list, services_list, 
                       product_categories, integrations_data, has_ecommerce, 
                       technical_score, content_score, last_scraped_at, 
                       google_maps_url, social_media_details, is_open
                FROM firms WHERE id = ?
            """, (firm_id,))
            
            row = cursor.fetchone()
            
            if not row:
                logger.warning(f"❌ Firma {firm_id} bulunamadı")
                return None
            
            # Dictionary oluştur
            firm_data = dict(zip(columns, row))
            
            # JSON alanları parse et
            json_fields = ['emails', 'phone_numbers', 'social_media', 'business_info', 
                          'services', 'products', 'advanced_features', 'scraped_data', 
                          'ai_vision_analysis', 'company_type_analysis', 'quality_analysis',
                          'products_list', 'services_list', 'product_categories', 
                          'integrations_data', 'social_media_details']
            
            for field in json_fields:
                if firm_data.get(field) and isinstance(firm_data[field], str):
                    try:
                        firm_data[field] = json.loads(firm_data[field])
                    except:
                        pass
            
            return firm_data
            
        except Exception as e:
            logger.error(f"❌ Firma verisi getirme hatası: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def get_ai_learned_data(self, firm_name: str) -> Optional[Dict]:
        """AI'nin öğrendiği firma bilgilerini getir"""
        conn = None
        try:
            if not os.path.exists(self.knowledge_db_path):
                return None
                
            conn = sqlite3.connect(self.knowledge_db_path)
            cursor = conn.cursor()
            
            # AI öğrenme verilerini ara
            cursor.execute("""
                SELECT * FROM business_insights 
                WHERE summary LIKE ? OR details LIKE ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (f"%{firm_name}%", f"%{firm_name}%"))
            
            insights = cursor.fetchall()
            
            # Kullanıcı profillerini ara
            cursor.execute("""
                SELECT * FROM user_profiles 
                WHERE business_focus LIKE ? OR preferences LIKE ?
                ORDER BY updated_at DESC
                LIMIT 5
            """, (f"%{firm_name}%", f"%{firm_name}%"))
            
            profiles = cursor.fetchall()
            
            return {
                'insights': insights,
                'profiles': profiles,
                'total_insights': len(insights),
                'total_profiles': len(profiles)
            }
            
        except Exception as e:
            logger.error(f"❌ AI öğrenme verisi getirme hatası: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def analyze_firm_with_ai(self, firm_id: int) -> Optional[FirmAnalysis]:
        """Firmayı AI ile detaylı analiz et"""
        try:
            # Firma verilerini al
            firm_data = self.get_firm_data(firm_id)
            if not firm_data:
                logger.error(f"❌ Firma {firm_id} bulunamadı")
                return None
            
            # AI öğrenme verilerini al
            ai_learned_data = self.get_ai_learned_data(firm_data['name'])
            
            if not self.openai_client:
                logger.warning("⚠️ OpenAI client mevcut değil, basit analiz yapılıyor")
                return self._create_basic_analysis(firm_data, ai_learned_data)
            
            # AI analizi yap
            analysis_result = self._perform_ai_analysis(firm_data, ai_learned_data)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Firma analiz hatası: {e}")
            return None
    
    def _perform_ai_analysis(self, firm_data: Dict, ai_learned_data: Optional[Dict]) -> FirmAnalysis:
        """AI ile detaylı analiz yap - Müşteri özeti ile bilgi öğretim verilerini karşılaştırır"""
        try:
            # Detaylı veri karşılaştırması yap
            comparison_analysis = self._compare_customer_data_with_learned_knowledge(firm_data, ai_learned_data)
            
            # AI prompt oluştur - Karşılaştırmalı analiz odaklı
            prompt = f"""
Sen bir B2B strateji uzmanısın. Aşağıdaki iki farklı veri kaynağını karşılaştırarak en uygun pazarlama stratejisini öner.

🏢 MÜŞTERİ DETAYLI ÖZETİ (Web Scraping + AI Analiz):
- Firma Adı: {firm_data.get('name', 'Bilinmiyor')}
- Sektör: {firm_data.get('sector', 'Bilinmiyor')}
- Web Sitesi: {firm_data.get('website', 'Yok')}
- AI Özeti: {firm_data.get('ai_summary', 'Yok')}
- Kalite Skoru: {firm_data.get('quality_score', 0)}/100
- Kalite Notu: {firm_data.get('quality_grade', 'Bilinmiyor')}
- Ürünler: {firm_data.get('products', 'Yok')}
- Hizmetler: {firm_data.get('services', 'Yok')}
- E-ticaret: {'Evet' if firm_data.get('has_ecommerce') else 'Hayır'}
- Teknik Skor: {firm_data.get('technical_score', 0)}/100
- İçerik Skoru: {firm_data.get('content_score', 0)}/100
- Şirket Tipi: {firm_data.get('company_type', 'Bilinmiyor')}
- Güven Skoru: {firm_data.get('company_type_confidence', 0)}%
- İş Bilgileri: {firm_data.get('business_info', 'Yok')}
- Hakkında Metni: {firm_data.get('about_text', 'Yok')}
- Takım Büyüklüğü: {firm_data.get('team_size_estimate', 'Bilinmiyor')}

🧠 BİLGİ ÖĞRETİM VERİLERİ (AI'nin Öğrendiği Bilgiler):
{self._format_detailed_ai_learned_data(ai_learned_data)}

📊 VERİ KARŞILAŞTIRMA ANALİZİ:
{comparison_analysis}

Lütfen aşağıdaki konularda DETAYLI KARŞILAŞTIRMALI analiz yap:

1. VERİ TUTARLILIĞI ANALİZİ:
   - Web scraping verileri ile AI öğrenme verileri arasındaki tutarlılık
   - Çelişen bilgiler ve bunların değerlendirmesi
   - Eksik bilgiler ve tamamlanması gereken alanlar

2. MÜŞTERİ PROFİLİ DERİNLEMESİNE ANALİZİ:
   - İki veri kaynağından çıkan birleşik müşteri profili
   - Güçlü yönler (her iki kaynaktan)
   - Zayıflıklar ve gelişim alanları
   - Pazar konumu ve rekabet avantajları

3. STRATEJİ ÖNERİLERİ (Veri Karşılaştırmasına Dayalı):
   - En uygun strateji türü (aggressive, conservative, educational, promotional, relationship, technical)
   - Güven skoru (veri tutarlılığına göre 0-100)
   - Beklenen başarı oranı (0-100)
   - Önerilen yaklaşım gerekçesi

4. RİSK DEĞERLENDİRMESİ (Çoklu Veri Kaynağına Dayalı):
   - Spam riski (müşteri profiline göre)
   - Aşırı takip riski (etkileşim geçmişine göre)
   - Düşük etkileşim riski (içerik uyumuna göre)

5. FIRSAT ANALİZİ (Karşılaştırmalı):
   - Yüksek etkileşim potansiyeli
   - En iyi zamanlamalar
   - İçerik fırsatları
   - Kişiselleştirme fırsatları

6. AI TALİMATLARI (Veri Karşılaştırmasına Dayalı):
   - Mail yazımı için özel talimatlar
   - Sistem promptu
   - İçerik odak noktaları
   - Kişiselleştirme stratejisi

Yanıtını JSON formatında ver:
{{
    "data_comparison": {{
        "consistency_score": 0-100,
        "conflicting_data": ["string"],
        "missing_data": ["string"],
        "data_quality": "high/medium/low"
    }},
    "firm_analysis": {{
        "firm_type": "string",
        "strengths": ["string"],
        "weaknesses": ["string"],
        "market_position": "string",
        "personalization_opportunities": ["string"]
    }},
    "strategy_recommendations": [
        {{
            "strategy_type": "string",
            "confidence": 0-100,
            "reasoning": "string",
            "expected_success_rate": 0-100,
            "risk_level": "low/medium/high",
            "mail_frequency": 1-10,
            "content_focus": ["string"],
            "timing_recommendations": {{"days": ["string"], "hours": ["string"]}},
            "personalization_level": "high/medium/low"
        }}
    ],
    "risk_assessment": {{
        "spam_risk": 0-100,
        "over_contact_risk": 0-100,
        "low_engagement_risk": 0-100,
        "data_reliability_risk": 0-100
    }},
    "opportunity_analysis": {{
        "high_engagement_potential": 0-100,
        "best_timing": "string",
        "content_opportunities": ["string"],
        "personalization_opportunities": ["string"]
    }},
    "ai_instructions": "string",
    "custom_prompt": "string",
    "comparison_insights": "string"
}}
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Sen bir B2B strateji uzmanısın. Detaylı analiz yap ve JSON formatında yanıt ver."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            # JSON yanıtı parse et
            response_content = response.choices[0].message.content.strip()
            if not response_content:
                logger.error("❌ AI yanıtı boş")
                return self._create_basic_analysis(firm_data, ai_learned_data)
            
            # Markdown kod bloklarını temizle
            if response_content.startswith('```json'):
                response_content = response_content[7:]  # ```json kısmını çıkar
            if response_content.startswith('```'):
                response_content = response_content[3:]   # ``` kısmını çıkar
            if response_content.endswith('```'):
                response_content = response_content[:-3]  # Son ``` kısmını çıkar
            
            response_content = response_content.strip()
            
            try:
                ai_response = json.loads(response_content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ AI yanıtı JSON parse edilemedi: {e}")
                logger.error(f"Yanıt içeriği: {response_content[:200]}...")
                return self._create_basic_analysis(firm_data, ai_learned_data)
            
            # En iyi stratejiyi belirle
            best_strategy = self._determine_best_strategy(ai_response['strategy_recommendations'])
            
            # FirmAnalysis objesi oluştur
            analysis = FirmAnalysis(
                firm_id=firm_data['id'],
                firm_name=firm_data['name'],
                sector=firm_data.get('sector', 'Bilinmiyor'),
                ai_confidence=ai_response['strategy_recommendations'][0]['confidence'] if ai_response['strategy_recommendations'] else 50,
                strategy_recommendations=ai_response['strategy_recommendations'],
                risk_assessment=ai_response['risk_assessment'],
                opportunity_score=ai_response['opportunity_analysis']['high_engagement_potential'],
                recommended_strategy=best_strategy,
                ai_instructions=ai_response['ai_instructions'],
                custom_prompt=ai_response['custom_prompt'],
                analysis_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ AI analiz hatası: {e}")
            return self._create_basic_analysis(firm_data, ai_learned_data)
    
    def _prepare_analysis_data(self, firm_data: Dict, ai_learned_data: Optional[Dict]) -> str:
        """Analiz için veri özetini hazırla"""
        summary_parts = []
        
        # Temel bilgiler
        summary_parts.append(f"Firma: {firm_data.get('name', 'Bilinmiyor')}")
        summary_parts.append(f"Sektör: {firm_data.get('sector', 'Bilinmiyor')}")
        summary_parts.append(f"Web: {firm_data.get('website', 'Yok')}")
        
        # Kalite bilgileri
        if firm_data.get('quality_score'):
            summary_parts.append(f"Kalite Skoru: {firm_data['quality_score']}/100")
        if firm_data.get('quality_grade'):
            summary_parts.append(f"Kalite Notu: {firm_data['quality_grade']}")
        
        # Ürün/Hizmet bilgileri
        if firm_data.get('products'):
            summary_parts.append(f"Ürünler: {str(firm_data['products'])[:200]}...")
        if firm_data.get('services'):
            summary_parts.append(f"Hizmetler: {str(firm_data['services'])[:200]}...")
        
        return "\n".join(summary_parts)
    
    def _format_ai_learned_data(self, ai_learned_data: Optional[Dict]) -> str:
        """AI öğrenme verilerini formatla"""
        if not ai_learned_data:
            return "AI öğrenme verisi bulunamadı"
        
        formatted = []
        formatted.append(f"Toplam İçgörü: {ai_learned_data['total_insights']}")
        formatted.append(f"Toplam Profil: {ai_learned_data['total_profiles']}")
        
        # İçgörüleri ekle
        if ai_learned_data['insights']:
            formatted.append("\nAI İçgörüleri:")
            for insight in ai_learned_data['insights'][:3]:  # İlk 3'ü al
                formatted.append(f"- {insight[6] if len(insight) > 6 else 'İçgörü'}")  # summary alanı
        
        return "\n".join(formatted)
    
    def _format_detailed_ai_learned_data(self, ai_learned_data: Optional[Dict]) -> str:
        """Detaylı AI öğrenme verilerini formatla"""
        if not ai_learned_data:
            return "AI öğrenme verisi bulunamadı"
        
        formatted = []
        formatted.append(f"📊 Toplam İçgörü: {ai_learned_data['total_insights']}")
        formatted.append(f"👤 Toplam Profil: {ai_learned_data['total_profiles']}")
        
        # İçgörüleri detaylı ekle
        if ai_learned_data['insights']:
            formatted.append("\n🧠 AI İçgörüleri:")
            for i, insight in enumerate(ai_learned_data['insights'][:5], 1):
                insight_type = insight[1] if len(insight) > 1 else 'Genel'
                confidence = insight[2] if len(insight) > 2 else 'N/A'
                summary = insight[6] if len(insight) > 6 else 'Özet yok'
                details = insight[7] if len(insight) > 7 else 'Detay yok'
                
                formatted.append(f"  {i}. {insight_type} (Güven: {confidence}%)")
                formatted.append(f"     Özet: {summary[:100]}...")
                if details and details != 'Detay yok':
                    formatted.append(f"     Detay: {details[:150]}...")
                formatted.append("")
        
        # Profilleri ekle
        if ai_learned_data['profiles']:
            formatted.append("👥 Kullanıcı Profilleri:")
            for i, profile in enumerate(ai_learned_data['profiles'][:3], 1):
                name = profile[1] if len(profile) > 1 else 'İsimsiz'
                business_focus = profile[5] if len(profile) > 5 else 'Odak yok'
                preferences = profile[2] if len(profile) > 2 else 'Tercih yok'
                
                formatted.append(f"  {i}. {name}")
                formatted.append(f"     İş Odağı: {business_focus}")
                formatted.append(f"     Tercihler: {preferences[:100]}...")
                formatted.append("")
        
        return "\n".join(formatted)
    
    def _compare_customer_data_with_learned_knowledge(self, firm_data: Dict, ai_learned_data: Optional[Dict]) -> str:
        """Müşteri verileri ile öğrenilen bilgileri karşılaştır"""
        try:
            comparison_points = []
            
            # Temel bilgi karşılaştırması
            firm_name = firm_data.get('name', 'Bilinmiyor')
            firm_sector = firm_data.get('sector', 'Bilinmiyor')
            firm_website = firm_data.get('website', 'Yok')
            
            comparison_points.append(f"🏢 Firma: {firm_name}")
            comparison_points.append(f"🏭 Sektör: {firm_sector}")
            comparison_points.append(f"🌐 Website: {firm_website}")
            
            # Veri tutarlılığı analizi
            consistency_score = 0
            total_checks = 0
            
            if ai_learned_data and ai_learned_data.get('insights'):
                total_checks += 1
                # Sektör tutarlılığı kontrolü
                sector_mentioned = any(firm_sector.lower() in str(insight).lower() 
                                    for insight in ai_learned_data['insights'])
                if sector_mentioned:
                    consistency_score += 1
                    comparison_points.append("✅ Sektör bilgisi tutarlı")
                else:
                    comparison_points.append("⚠️ Sektör bilgisi çelişkili")
            
            # Kalite değerlendirmesi
            quality_score = firm_data.get('quality_score', 0)
            if quality_score is None:
                quality_score = 0
            
            if quality_score >= 80:
                comparison_points.append("⭐ Yüksek kaliteli firma (80+ skor)")
            elif quality_score >= 60:
                comparison_points.append("📊 Orta kaliteli firma (60-79 skor)")
            else:
                comparison_points.append("📉 Düşük kaliteli firma (<60 skor)")
            
            # E-ticaret durumu
            has_ecommerce = firm_data.get('has_ecommerce', False)
            if has_ecommerce:
                comparison_points.append("🛒 E-ticaret firması - Online satış potansiyeli yüksek")
            else:
                comparison_points.append("🏢 Geleneksel firma - B2B odaklı yaklaşım gerekli")
            
            # AI öğrenme verisi analizi
            if ai_learned_data:
                insights_count = ai_learned_data.get('total_insights', 0)
                profiles_count = ai_learned_data.get('total_profiles', 0)
                
                if insights_count > 0:
                    comparison_points.append(f"🧠 AI {insights_count} içgörü öğrenmiş")
                if profiles_count > 0:
                    comparison_points.append(f"👤 AI {profiles_count} profil analiz etmiş")
                
                # Veri zenginliği değerlendirmesi
                if insights_count >= 5 and profiles_count >= 2:
                    comparison_points.append("📈 Zengin veri seti - Yüksek kişiselleştirme potansiyeli")
                elif insights_count >= 2 or profiles_count >= 1:
                    comparison_points.append("📊 Orta veri seti - Temel kişiselleştirme mümkün")
                else:
                    comparison_points.append("📉 Sınırlı veri seti - Genel yaklaşım önerilir")
            else:
                comparison_points.append("❌ AI öğrenme verisi yok - Sadece web scraping verisi mevcut")
            
            # Tutarlılık skoru hesapla
            if total_checks > 0:
                consistency_percentage = (consistency_score / total_checks) * 100
                comparison_points.append(f"🎯 Veri Tutarlılık Skoru: {consistency_percentage:.1f}%")
            
            # Strateji önerisi
            if quality_score >= 80 and ai_learned_data and ai_learned_data.get('total_insights', 0) >= 3:
                comparison_points.append("🚀 ÖNERİ: Agresif strateji - Yüksek kalite + zengin veri")
            elif quality_score >= 60:
                comparison_points.append("📚 ÖNERİ: Eğitici strateji - Orta kalite, bilgilendirici yaklaşım")
            else:
                comparison_points.append("🛡️ ÖNERİ: Muhafazakar strateji - Düşük kalite, dikkatli yaklaşım")
            
            return "\n".join(comparison_points)
            
        except Exception as e:
            logger.error(f"Veri karşılaştırma hatası: {e}")
            return "Veri karşılaştırma yapılamadı"
    
    def _determine_best_strategy(self, recommendations: List[Dict]) -> StrategyType:
        """En iyi stratejiyi belirle"""
        if not recommendations:
            return StrategyType.CONSERVATIVE
        
        # En yüksek güven skoruna sahip stratejiyi seç
        best_rec = max(recommendations, key=lambda x: x['confidence'])
        strategy_name = best_rec['strategy_type'].lower()
        
        # StrategyType enum'una çevir
        strategy_map = {
            'aggressive': StrategyType.AGGRESSIVE,
            'conservative': StrategyType.CONSERVATIVE,
            'educational': StrategyType.EDUCATIONAL,
            'promotional': StrategyType.PROMOTIONAL,
            'relationship': StrategyType.RELATIONSHIP,
            'technical': StrategyType.TECHNICAL
        }
        
        return strategy_map.get(strategy_name, StrategyType.CONSERVATIVE)
    
    def _create_basic_analysis(self, firm_data: Dict, ai_learned_data: Optional[Dict]) -> FirmAnalysis:
        """OpenAI olmadan basit analiz oluştur"""
        # Basit strateji belirleme
        quality_score = firm_data.get('quality_score', 50)
        if quality_score is None:
            quality_score = 50
            
        has_ecommerce = firm_data.get('has_ecommerce', False)
        
        # Veri karşılaştırması yap
        comparison_insights = self._compare_customer_data_with_learned_knowledge(firm_data, ai_learned_data)
        
        if quality_score > 80:
            strategy = StrategyType.AGGRESSIVE
            confidence = 75
            success_rate = 70
        elif quality_score > 60:
            strategy = StrategyType.EDUCATIONAL
            confidence = 65
            success_rate = 60
        else:
            strategy = StrategyType.CONSERVATIVE
            confidence = 55
            success_rate = 50
        
        # AI öğrenme verisi varsa güven skorunu artır
        if ai_learned_data and ai_learned_data.get('total_insights', 0) > 0:
            confidence += 10
            success_rate += 10
        
        return FirmAnalysis(
            firm_id=firm_data['id'],
            firm_name=firm_data['name'],
            sector=firm_data.get('sector', 'Bilinmiyor'),
            ai_confidence=confidence,
            strategy_recommendations=[{
                'strategy_type': strategy.value,
                'confidence': confidence,
                'reasoning': f'Basit analiz sonucu - Kalite: {quality_score}, E-ticaret: {has_ecommerce}',
                'expected_success_rate': success_rate,
                'risk_level': 'medium',
                'mail_frequency': 3,
                'content_focus': ['genel', 'sektörel'],
                'timing_recommendations': {'days': ['Pazartesi', 'Çarşamba', 'Cuma'], 'hours': ['09:00-11:00']},
                'personalization_level': 'medium'
            }],
            risk_assessment={
                'spam_risk': 30, 
                'over_contact_risk': 20, 
                'low_engagement_risk': 40,
                'data_reliability_risk': 25
            },
            opportunity_score=50.0,
            recommended_strategy=strategy,
            ai_instructions=f'Genel B2B mail stratejisi uygula. Firma: {firm_data["name"]}, Sektör: {firm_data.get("sector", "Bilinmiyor")}',
            custom_prompt='Profesyonel ve samimi bir ton kullan. Firma bilgilerini kişiselleştir.',
            analysis_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def get_all_firms_for_analysis(self) -> List[Dict]:
        """Analiz için tüm firmaları getir"""
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, sector, quality_score, is_analyzed, last_scraped_at
                FROM firms 
                WHERE status = 'active' 
                ORDER BY quality_score DESC, last_scraped_at DESC
            """)
            
            firms = []
            for row in cursor.fetchall():
                firms.append({
                    'id': row[0],
                    'name': row[1],
                    'sector': row[2],
                    'quality_score': row[3],
                    'is_analyzed': row[4],
                    'last_scraped_at': row[5]
                })
            
            return firms
            
        except Exception as e:
            logger.error(f"❌ Firma listesi getirme hatası: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def save_analysis_to_database(self, analysis: FirmAnalysis) -> bool:
        """Analiz sonucunu veritabanına kaydet"""
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Analiz tablosu oluştur (yoksa)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS firm_ai_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    firm_id INTEGER,
                    analysis_date TEXT,
                    strategy_type TEXT,
                    ai_confidence REAL,
                    opportunity_score REAL,
                    ai_instructions TEXT,
                    custom_prompt TEXT,
                    strategy_recommendations TEXT,
                    risk_assessment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (firm_id) REFERENCES firms (id)
                )
            """)
            
            # Analizi kaydet
            cursor.execute("""
                INSERT INTO firm_ai_analysis 
                (firm_id, analysis_date, strategy_type, ai_confidence, opportunity_score,
                 ai_instructions, custom_prompt, strategy_recommendations, risk_assessment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.firm_id,
                analysis.analysis_date,
                analysis.recommended_strategy.value,
                analysis.ai_confidence,
                analysis.opportunity_score,
                analysis.ai_instructions,
                analysis.custom_prompt,
                json.dumps(analysis.strategy_recommendations, ensure_ascii=False),
                json.dumps(analysis.risk_assessment, ensure_ascii=False)
            ))
            
            conn.commit()
            
            logger.info(f"✅ Analiz kaydedildi: {analysis.firm_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Analiz kaydetme hatası: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_analysis_for_campaign(self, firm_id: int) -> Optional[Dict]:
        """Kampanya için analiz verilerini getir"""
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Önce tablo var mı kontrol et
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='firm_ai_analysis'
            """)
            
            if not cursor.fetchone():
                logger.warning("firm_ai_analysis tablosu bulunamadı, oluşturuluyor...")
                # Tabloyu oluştur
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS firm_ai_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firm_id INTEGER,
                        analysis_date TEXT,
                        strategy_type TEXT,
                        ai_confidence REAL,
                        opportunity_score REAL,
                        ai_instructions TEXT,
                        custom_prompt TEXT,
                        strategy_recommendations TEXT,
                        risk_assessment TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id)
                    )
                """)
                conn.commit()
                return None
            
            cursor.execute("""
                SELECT strategy_type, ai_instructions, custom_prompt, strategy_recommendations
                FROM firm_ai_analysis 
                WHERE firm_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (firm_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'strategy_type': row[0],
                'ai_instructions': row[1],
                'custom_prompt': row[2],
                'strategy_recommendations': json.loads(row[3]) if row[3] else []
            }
            
        except Exception as e:
            logger.error(f"❌ Kampanya analiz verisi getirme hatası: {e}")
            return None
        finally:
            if conn:
                conn.close()
