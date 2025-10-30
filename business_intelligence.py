#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
İş Zekası Modülü - Business Intelligence Module
Bu modül, firma analizi ve iş zekası işlemleri için kullanılır.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessIntelligenceAnalyzer:
    """
    İş Zekası Analiz Sınıfı
    Firma verilerini analiz eder ve iş zekası raporları oluşturur.
    """
    
    def __init__(self, db=None, database_path=None, config=None, **kwargs):
        """
        BusinessIntelligenceAnalyzer başlatıcı
        
        Args:
            db: Veritabanı bağlantısı (opsiyonel)
            database_path: Veritabanı yolu (opsiyonel, uyumluluk için)
            config: Konfigürasyon (opsiyonel, uyumluluk için)
            **kwargs: Ek parametreler (uyumluluk için)
        """
        self.db = db
        self.database_path = database_path or "b2b_automation.db"
        self.config = config or {}
        self.analysis_cache = {}
        logger.info("İş Zekası Analiz Sistemi başlatıldı")
    
    def get_firm_data(self, firm_id):
        """Firma verilerini getir - Hata önleme ile"""
        try:
            if self.db:
                firms = self.db.get_all_firms()
                for firm in firms:
                    if firm.get('id') == firm_id:
                        return firm
            return {}
        except Exception as e:
            logger.error(f"Firma verisi getirme hatası: {e}")
            return {}
    
    def get_all_firms(self):
        """Tüm firmaları getir - Hata önleme ile"""
        try:
            if self.db:
                return self.db.get_all_firms()
            return []
        except Exception as e:
            logger.error(f"Firmalar getirme hatası: {e}")
            return []
    
    def analyze_company(self, company_data: Dict[str, Any], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Firma analizi yapar
        
        Args:
            company_data: Firma verileri
            analysis_type: Analiz türü ("comprehensive", "basic", "financial")
            
        Returns:
            Dict: Analiz sonuçları
        """
        try:
            logger.info(f"Firma analizi başlatıldı: {analysis_type}")
            
            # Temel analiz
            basic_analysis = self._perform_basic_analysis(company_data)
            
            # Analiz türüne göre ek analizler
            if analysis_type == "comprehensive":
                financial_analysis = self._perform_financial_analysis(company_data)
                market_analysis = self._perform_market_analysis(company_data)
                risk_analysis = self._perform_risk_analysis(company_data)
                
                result = {
                    "success": True,
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now().isoformat(),
                    "basic_analysis": basic_analysis,
                    "financial_analysis": financial_analysis,
                    "market_analysis": market_analysis,
                    "risk_analysis": risk_analysis,
                    "overall_score": self._calculate_overall_score(basic_analysis, financial_analysis, market_analysis, risk_analysis)
                }
            elif analysis_type == "financial":
                financial_analysis = self._perform_financial_analysis(company_data)
                result = {
                    "success": True,
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now().isoformat(),
                    "basic_analysis": basic_analysis,
                    "financial_analysis": financial_analysis,
                    "overall_score": self._calculate_financial_score(financial_analysis)
                }
            else:  # basic
                result = {
                    "success": True,
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now().isoformat(),
                    "basic_analysis": basic_analysis,
                    "overall_score": self._calculate_basic_score(basic_analysis)
                }
            
            # Cache'e kaydet
            cache_key = f"{company_data.get('name', 'unknown')}_{analysis_type}"
            self.analysis_cache[cache_key] = result
            
            logger.info(f"Firma analizi tamamlandı: {result['overall_score']}/100")
            return result
            
        except Exception as e:
            logger.error(f"Firma analizi hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _perform_basic_analysis(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Temel firma analizi"""
        try:
            name = company_data.get('name', 'Bilinmeyen Firma')
            industry = company_data.get('industry', 'Bilinmeyen Sektör')
            location = company_data.get('location', 'Bilinmeyen Konum')
            website = company_data.get('website', '')
            phone = company_data.get('phone', '')
            email = company_data.get('email', '')
            
            # Temel bilgi tamamlama skoru
            completeness_score = 0
            if name and name != 'Bilinmeyen Firma':
                completeness_score += 20
            if industry and industry != 'Bilinmeyen Sektör':
                completeness_score += 20
            if location and location != 'Bilinmeyen Konum':
                completeness_score += 20
            if website:
                completeness_score += 20
            if phone or email:
                completeness_score += 20
            
            return {
                "company_name": name,
                "industry": industry,
                "location": location,
                "website": website,
                "contact_info": {
                    "phone": phone,
                    "email": email
                },
                "completeness_score": completeness_score,
                "data_quality": "Yüksek" if completeness_score >= 80 else "Orta" if completeness_score >= 60 else "Düşük"
            }
            
        except Exception as e:
            logger.error(f"Temel analiz hatası: {e}")
            return {"error": str(e)}
    
    def _perform_financial_analysis(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finansal analiz"""
        try:
            # Finansal veriler (örnek - gerçek uygulamada veritabanından gelecek)
            revenue = company_data.get('revenue', 0)
            employees = company_data.get('employees', 0)
            founded_year = company_data.get('founded_year', 0)
            
            # Finansal skor hesaplama
            financial_score = 0
            
            if revenue > 0:
                if revenue > 10000000:  # 10M+
                    financial_score += 40
                elif revenue > 1000000:  # 1M+
                    financial_score += 30
                elif revenue > 100000:  # 100K+
                    financial_score += 20
                else:
                    financial_score += 10
            
            if employees > 0:
                if employees > 100:
                    financial_score += 30
                elif employees > 10:
                    financial_score += 20
                else:
                    financial_score += 10
            
            if founded_year > 0:
                years_in_business = datetime.now().year - founded_year
                if years_in_business > 20:
                    financial_score += 30
                elif years_in_business > 10:
                    financial_score += 20
                elif years_in_business > 5:
                    financial_score += 10
            
            return {
                "revenue": revenue,
                "employees": employees,
                "founded_year": founded_year,
                "years_in_business": datetime.now().year - founded_year if founded_year > 0 else 0,
                "financial_score": min(financial_score, 100),
                "financial_health": "Mükemmel" if financial_score >= 80 else "İyi" if financial_score >= 60 else "Orta" if financial_score >= 40 else "Zayıf"
            }
            
        except Exception as e:
            logger.error(f"Finansal analiz hatası: {e}")
            return {"error": str(e)}
    
    def _perform_market_analysis(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pazar analizi"""
        try:
            industry = company_data.get('industry', 'Bilinmeyen Sektör')
            location = company_data.get('location', 'Bilinmeyen Konum')
            
            # Sektör bazlı pazar potansiyeli (örnek veriler)
            industry_potential = {
                "Teknoloji": 90,
                "Sağlık": 85,
                "Finans": 80,
                "Eğitim": 75,
                "Perakende": 70,
                "İmalat": 65,
                "Hizmet": 60,
                "Bilinmeyen Sektör": 50
            }
            
            # Konum bazlı pazar erişimi (örnek veriler)
            location_potential = {
                "İstanbul": 95,
                "Ankara": 85,
                "İzmir": 80,
                "Bursa": 75,
                "Antalya": 70,
                "Bilinmeyen Konum": 50
            }
            
            market_score = (
                industry_potential.get(industry, 50) * 0.6 +
                location_potential.get(location, 50) * 0.4
            )
            
            return {
                "industry": industry,
                "location": location,
                "market_potential": market_score,
                "market_size": "Büyük" if market_score >= 80 else "Orta" if market_score >= 60 else "Küçük",
                "competition_level": "Düşük" if market_score >= 80 else "Orta" if market_score >= 60 else "Yüksek"
            }
            
        except Exception as e:
            logger.error(f"Pazar analizi hatası: {e}")
            return {"error": str(e)}
    
    def _perform_risk_analysis(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Risk analizi"""
        try:
            # Risk faktörleri
            risk_factors = []
            risk_score = 100  # Başlangıç skoru (düşük risk)
            
            # Eksik bilgi riski
            if not company_data.get('website'):
                risk_factors.append("Website bilgisi eksik")
                risk_score -= 10
            
            if not company_data.get('phone') and not company_data.get('email'):
                risk_factors.append("İletişim bilgisi eksik")
                risk_score -= 15
            
            # Sektör riski
            industry = company_data.get('industry', '')
            high_risk_industries = ['Yüksek Risk Sektörü', 'Belirsiz Sektör']
            if industry in high_risk_industries:
                risk_factors.append(f"Sektör riski: {industry}")
                risk_score -= 20
            
            # Finansal risk
            revenue = company_data.get('revenue', 0)
            if revenue == 0:
                risk_factors.append("Gelir bilgisi belirsiz")
                risk_score -= 15
            
            return {
                "risk_score": max(risk_score, 0),
                "risk_level": "Düşük" if risk_score >= 80 else "Orta" if risk_score >= 60 else "Yüksek",
                "risk_factors": risk_factors,
                "recommendations": self._generate_risk_recommendations(risk_factors)
            }
            
        except Exception as e:
            logger.error(f"Risk analizi hatası: {e}")
            return {"error": str(e)}
    
    def _generate_risk_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Risk önerileri oluşturur"""
        recommendations = []
        
        for factor in risk_factors:
            if "Website" in factor:
                recommendations.append("Firma website bilgilerini güncelleyin")
            elif "İletişim" in factor:
                recommendations.append("İletişim bilgilerini tamamlayın")
            elif "Sektör" in factor:
                recommendations.append("Sektör bilgilerini doğrulayın")
            elif "Gelir" in factor:
                recommendations.append("Finansal bilgileri netleştirin")
        
        if not recommendations:
            recommendations.append("Risk seviyesi düşük, mevcut durumu koruyun")
        
        return recommendations
    
    def _calculate_overall_score(self, basic: Dict, financial: Dict, market: Dict, risk: Dict) -> int:
        """Genel skor hesaplar"""
        try:
            basic_score = basic.get('completeness_score', 0)
            financial_score = financial.get('financial_score', 0)
            market_score = market.get('market_potential', 0)
            risk_score = risk.get('risk_score', 0)
            
            # Ağırlıklı ortalama
            overall = (
                basic_score * 0.25 +
                financial_score * 0.30 +
                market_score * 0.25 +
                risk_score * 0.20
            )
            
            return int(overall)
            
        except Exception as e:
            logger.error(f"Skor hesaplama hatası: {e}")
            return 0
    
    def _calculate_financial_score(self, financial: Dict) -> int:
        """Finansal skor hesaplar"""
        return financial.get('financial_score', 0)
    
    def _calculate_basic_score(self, basic: Dict) -> int:
        """Temel skor hesaplar"""
        return basic.get('completeness_score', 0)
    
    def get_analysis_summary(self, company_name: str) -> Dict[str, Any]:
        """Analiz özeti getirir"""
        try:
            # Cache'den ara
            for key, analysis in self.analysis_cache.items():
                if company_name.lower() in key.lower():
                    return {
                        "success": True,
                        "company_name": company_name,
                        "last_analysis": analysis.get('timestamp'),
                        "overall_score": analysis.get('overall_score', 0),
                        "analysis_type": analysis.get('analysis_type', 'unknown')
                    }
            
            return {
                "success": False,
                "message": f"{company_name} için analiz bulunamadı"
            }
            
        except Exception as e:
            logger.error(f"Analiz özeti hatası: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_cache(self):
        """Analiz cache'ini temizler"""
        self.analysis_cache.clear()
        logger.info("Analiz cache'i temizlendi")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Cache istatistiklerini getirir"""
        return {
            "total_analyses": len(self.analysis_cache),
            "cache_keys": list(self.analysis_cache.keys()),
            "memory_usage": f"{len(str(self.analysis_cache))} bytes"
        }


# Test fonksiyonu
def test_business_intelligence():
    """Test fonksiyonu"""
    try:
        analyzer = BusinessIntelligenceAnalyzer()
        
        # Test verisi
        test_company = {
            "name": "Test Firma A.Ş.",
            "industry": "Teknoloji",
            "location": "İstanbul",
            "website": "https://testfirma.com",
            "phone": "+90 212 123 45 67",
            "email": "info@testfirma.com",
            "revenue": 5000000,
            "employees": 50,
            "founded_year": 2015
        }
        
        # Analiz yap
        result = analyzer.analyze_company(test_company, "comprehensive")
        
        print("=== İş Zekası Test Sonuçları ===")
        print(f"Başarılı: {result['success']}")
        print(f"Genel Skor: {result['overall_score']}/100")
        print(f"Analiz Türü: {result['analysis_type']}")
        
        if result['success']:
            print(f"Temel Analiz Skoru: {result['basic_analysis']['completeness_score']}")
            print(f"Finansal Skor: {result['financial_analysis']['financial_score']}")
            print(f"Pazar Potansiyeli: {result['market_analysis']['market_potential']}")
            print(f"Risk Skoru: {result['risk_analysis']['risk_score']}")
        
        return True
        
    except Exception as e:
        print(f"Test hatası: {e}")
        return False


if __name__ == "__main__":
    # Test çalıştır
    test_business_intelligence()
