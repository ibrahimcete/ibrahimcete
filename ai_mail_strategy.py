"""
AI Destekli Mail Takip Stratejisi Modülü
Her firma için özelleştirilmiş mail takip stratejisi oluşturur
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import openai
import os

class AIMailStrategy:
    """AI destekli ve manuel mail takip stratejisi yöneticisi"""
    
    def __init__(self, db_path: str = "b2b_automation.db", config_path: str = "config.json"):
        self.db_path = db_path
        self.config_path = config_path
        self.api_key = self._load_api_key()
        self.client = None
        if self.api_key:
            # Yeni OpenAI API client
            self.client = openai.OpenAI(api_key=self.api_key)
        self._init_database()
    
    def _load_api_key(self) -> str:
        """Config.json'dan OpenAI API key'i yükle"""
        try:
            # Önce config.json'dan dene
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get('openai_api_key', '')
                    if api_key:
                        return api_key
            
            # Config'de yoksa ortam değişkeninden dene
            return os.getenv("OPENAI_API_KEY", "")
        except Exception as e:
            print(f"API key yükleme hatası: {e}")
            return os.getenv("OPENAI_API_KEY", "")
    
    def _init_database(self):
        """Mail stratejisi için veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Firma mail geçmişi tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_mail_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                company_email TEXT,
                mail_subject TEXT,
                mail_content TEXT,
                sent_date TIMESTAMP,
                opened BOOLEAN DEFAULT 0,
                opened_date TIMESTAMP,
                replied BOOLEAN DEFAULT 0,
                replied_date TIMESTAMP,
                clicked BOOLEAN DEFAULT 0,
                click_count INTEGER DEFAULT 0,
                engagement_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Firma web sitesi analiz verileri
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_website_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                website_url TEXT,
                products TEXT,
                services TEXT,
                contact_info TEXT,
                campaigns TEXT,
                last_scraped TIMESTAMP,
                analysis_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # AI mail stratejisi önerileri
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_mail_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                strategy_type TEXT DEFAULT 'ai_suggested',
                recommended_mail_count INTEGER,
                send_schedule TEXT,
                content_types TEXT,
                best_send_times TEXT,
                risk_analysis TEXT,
                opportunity_analysis TEXT,
                engagement_prediction REAL,
                spam_risk_score REAL,
                ai_reasoning TEXT,
                status TEXT DEFAULT 'pending',
                approved_by_user BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Manuel stratejiler
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manual_mail_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                mail_count INTEGER,
                send_schedule TEXT,
                content_types TEXT,
                user_notes TEXT,
                created_by TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Strateji performans metrikleri
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                strategy_id INTEGER,
                strategy_type TEXT,
                total_mails_sent INTEGER DEFAULT 0,
                total_opened INTEGER DEFAULT 0,
                total_replied INTEGER DEFAULT 0,
                total_clicked INTEGER DEFAULT 0,
                open_rate REAL DEFAULT 0.0,
                reply_rate REAL DEFAULT 0.0,
                click_rate REAL DEFAULT 0.0,
                conversion_rate REAL DEFAULT 0.0,
                avg_engagement_score REAL DEFAULT 0.0,
                performance_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_company_history(self, company_name: str) -> Dict:
        """Firma mail geçmişini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_mails,
                SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as opened_count,
                SUM(CASE WHEN replied = 1 THEN 1 ELSE 0 END) as replied_count,
                SUM(CASE WHEN clicked = 1 THEN 1 ELSE 0 END) as clicked_count,
                AVG(engagement_score) as avg_engagement,
                MAX(sent_date) as last_sent_date
            FROM company_mail_history
            WHERE company_name = ?
        ''', (company_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            return {
                'total_mails': result[0] or 0,
                'opened_count': result[1] or 0,
                'replied_count': result[2] or 0,
                'clicked_count': result[3] or 0,
                'avg_engagement': round(result[4] or 0.0, 2),
                'open_rate': round((result[1] or 0) / result[0] * 100, 2) if result[0] > 0 else 0,
                'reply_rate': round((result[2] or 0) / result[0] * 100, 2) if result[0] > 0 else 0,
                'click_rate': round((result[3] or 0) / result[0] * 100, 2) if result[0] > 0 else 0,
                'last_sent_date': result[5] or 'Yok'
            }
        else:
            return {
                'total_mails': 0,
                'opened_count': 0,
                'replied_count': 0,
                'clicked_count': 0,
                'avg_engagement': 0.0,
                'open_rate': 0.0,
                'reply_rate': 0.0,
                'click_rate': 0.0,
                'last_sent_date': 'Yok'
            }
    
    def get_website_data(self, company_name: str) -> Dict:
        """Firma web sitesi verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT website_url, products, services, contact_info, campaigns, analysis_data
            FROM company_website_data
            WHERE company_name = ?
            ORDER BY last_scraped DESC
            LIMIT 1
        ''', (company_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'website_url': result[0] or '',
                'products': result[1] or '',
                'services': result[2] or '',
                'contact_info': result[3] or '',
                'campaigns': result[4] or '',
                'analysis_data': result[5] or ''
            }
        else:
            return {
                'website_url': '',
                'products': '',
                'services': '',
                'contact_info': '',
                'campaigns': '',
                'analysis_data': 'Veri yok'
            }
    
    def get_previous_mails(self, company_name: str, limit: int = 5) -> List[Dict]:
        """Önceki mail verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mail_subject, mail_content, sent_date, opened, replied, clicked, engagement_score
            FROM company_mail_history
            WHERE company_name = ?
            ORDER BY sent_date DESC
            LIMIT ?
        ''', (company_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        mails = []
        for row in results:
            mails.append({
                'subject': row[0],
                'content': row[1][:200] + '...' if row[1] and len(row[1]) > 200 else row[1],
                'sent_date': row[2],
                'opened': bool(row[3]),
                'replied': bool(row[4]),
                'clicked': bool(row[5]),
                'engagement_score': row[6]
            })
        
        return mails
    
    def analyze_with_ai(self, company_name: str) -> Dict:
        """AI ile firma verilerini analiz et ve strateji öner"""
        
        if not self.client:
            return {
                'success': False,
                'error': 'AI API anahtarı bulunamadı. Lütfen OPENAI_API_KEY ortam değişkenini ayarlayın.'
            }
        
        # Veri toplama
        history = self.get_company_history(company_name)
        website_data = self.get_website_data(company_name)
        previous_mails = self.get_previous_mails(company_name)
        
        # LLM için prompt oluştur
        prompt = f"""
Sen B2B mail pazarlama uzmanı bir AI asistanısın. Aşağıdaki firma için en etkili mail takip stratejisini öner.

FİRMA ADI: {company_name}

FİRMA MAİL GEÇMİŞİ:
- Toplam gönderilen mail: {history['total_mails']}
- Açılma oranı: {history['open_rate']}%
- Yanıt oranı: {history['reply_rate']}%
- Tıklama oranı: {history['click_rate']}%
- Ortalama etkileşim skoru: {history['avg_engagement']}
- Son mail tarihi: {history['last_sent_date']}

WEB SİTESİ VERİLERİ:
- Web sitesi: {website_data['website_url']}
- Ürünler: {website_data['products'][:300] if website_data['products'] else 'Bilgi yok'}
- Hizmetler: {website_data['services'][:300] if website_data['services'] else 'Bilgi yok'}
- Kampanyalar: {website_data['campaigns'][:200] if website_data['campaigns'] else 'Bilgi yok'}

ÖNCEKİ MAİL ÖRNEKLERİ:
{json.dumps(previous_mails[:3], indent=2, ensure_ascii=False)}

Lütfen aşağıdaki konularda detaylı analiz ve öneriler sun:

1. ÖNERILEN MAİL SAYISI: Firmaya kaç mail gönderilmeli? (1-10 arası)
2. GÖNDERİM ZAMANLARI: Hangi günler ve saatler en uygun? (haftanın günleri ve saat aralıkları)
3. MAİL İÇERİK TÜRLERİ: Hangi tür içerikler kullanılmalı? (bilgilendirme, hatırlatma, kampanya, kişiselleştirilmiş teklif vb.)
4. RİSK ANALİZİ: Spam riski, aşırı mail tehlikesi, düşük etkileşim riski vb.
5. FIRSAT ANALİZİ: Yüksek etkileşim potansiyeli, en iyi zamanlamalar, içerik fırsatları
6. ETKİLEŞİM TAHMİNİ: Bu strateji ile beklenen açılma/yanıt oranı (0-100 arası)
7. SPAM RİSK SKORU: 0-100 arası (0=çok düşük risk, 100=çok yüksek risk)

Yanıtını JSON formatında ver:
{{
    "recommended_mail_count": sayı,
    "send_schedule": [
        {{"day": "Pazartesi", "time": "09:00-11:00", "reasoning": "açıklama"}},
        ...
    ],
    "content_types": [
        {{"type": "içerik türü", "priority": "yüksek/orta/düşük", "description": "açıklama"}},
        ...
    ],
    "risk_analysis": {{
        "spam_risk": "düşük/orta/yüksek",
        "over_mailing_risk": "açıklama",
        "low_engagement_risk": "açıklama"
    }},
    "opportunity_analysis": {{
        "high_engagement_potential": "açıklama",
        "best_timing": "açıklama",
        "content_opportunities": "açıklama"
    }},
    "engagement_prediction": sayı (0-100),
    "spam_risk_score": sayı (0-100),
    "overall_reasoning": "genel stratejik açıklama"
}}
"""
        
        try:
            # OpenAI GPT-4 API çağrısı (Yeni API)
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": "Sen B2B mail pazarlama uzmanı bir AI asistanısın. Firma verilerini analiz ederek en etkili mail takip stratejilerini önerirsin. Yanıtlarını her zaman JSON formatında verirsin."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Yanıtı parse et
            content = response.choices[0].message.content
            
            # JSON parse et
            try:
                strategy_data = json.loads(content)
                
                # Veritabanına kaydet
                self._save_ai_strategy(company_name, strategy_data)
                
                return {
                    'success': True,
                    'strategy': strategy_data,
                    'raw_response': content
                }
            except json.JSONDecodeError:
                # JSON bulunamadıysa manuel parse dene
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    strategy_data = json.loads(content[json_start:json_end])
                    
                    # Veritabanına kaydet
                    self._save_ai_strategy(company_name, strategy_data)
                    
                    return {
                        'success': True,
                        'strategy': strategy_data,
                        'raw_response': content
                    }
                else:
                    return {
                        'success': False,
                        'error': 'AI yanıtı parse edilemedi',
                        'raw_response': content
                    }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'AI analizi hatası: {str(e)}'
            }
    
    def _save_ai_strategy(self, company_name: str, strategy_data: Dict):
        """AI stratejisini veritabanına kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ai_mail_strategies (
                company_name, strategy_type, recommended_mail_count,
                send_schedule, content_types, best_send_times,
                risk_analysis, opportunity_analysis,
                engagement_prediction, spam_risk_score, ai_reasoning,
                status, approved_by_user
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_name,
            'ai_suggested',
            strategy_data.get('recommended_mail_count', 3),
            json.dumps(strategy_data.get('send_schedule', []), ensure_ascii=False),
            json.dumps(strategy_data.get('content_types', []), ensure_ascii=False),
            json.dumps(strategy_data.get('send_schedule', []), ensure_ascii=False),
            json.dumps(strategy_data.get('risk_analysis', {}), ensure_ascii=False),
            json.dumps(strategy_data.get('opportunity_analysis', {}), ensure_ascii=False),
            strategy_data.get('engagement_prediction', 0),
            strategy_data.get('spam_risk_score', 0),
            strategy_data.get('overall_reasoning', ''),
            'pending',
            0
        ))
        
        conn.commit()
        conn.close()
    
    def save_manual_strategy(self, company_name: str, mail_count: int, 
                           send_schedule: List[Dict], content_types: List[str],
                           user_notes: str = '', created_by: str = 'User') -> bool:
        """Manuel strateji kaydet"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO manual_mail_strategies (
                    company_name, mail_count, send_schedule, content_types,
                    user_notes, created_by, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name,
                mail_count,
                json.dumps(send_schedule, ensure_ascii=False),
                json.dumps(content_types, ensure_ascii=False),
                user_notes,
                created_by,
                'active'
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Manuel strateji kaydetme hatası: {e}")
            return False
    
    def approve_ai_strategy(self, strategy_id: int) -> bool:
        """AI stratejisini onayla"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE ai_mail_strategies
                SET approved_by_user = 1, status = 'approved', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (strategy_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Strateji onaylama hatası: {e}")
            return False
    
    def get_active_strategy(self, company_name: str) -> Optional[Dict]:
        """Firma için aktif stratejiyi getir (AI veya manuel)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Önce onaylanmış AI stratejisini kontrol et
        cursor.execute('''
            SELECT id, strategy_type, recommended_mail_count, send_schedule,
                   content_types, engagement_prediction, spam_risk_score, ai_reasoning
            FROM ai_mail_strategies
            WHERE company_name = ? AND approved_by_user = 1 AND status = 'approved'
            ORDER BY created_at DESC
            LIMIT 1
        ''', (company_name,))
        
        result = cursor.fetchone()
        
        if result:
            conn.close()
            return {
                'type': 'ai',
                'id': result[0],
                'strategy_type': result[1],
                'mail_count': result[2],
                'schedule': json.loads(result[3]),
                'content_types': json.loads(result[4]),
                'engagement_prediction': result[5],
                'spam_risk_score': result[6],
                'reasoning': result[7]
            }
        
        # Manuel strateji kontrol et
        cursor.execute('''
            SELECT id, mail_count, send_schedule, content_types, user_notes
            FROM manual_mail_strategies
            WHERE company_name = ? AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
        ''', (company_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'type': 'manual',
                'id': result[0],
                'mail_count': result[1],
                'schedule': json.loads(result[2]),
                'content_types': json.loads(result[3]),
                'user_notes': result[4]
            }
        
        return None
    
    def get_all_strategies(self, company_name: str) -> Dict:
        """Firma için tüm stratejileri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # AI stratejileri
        cursor.execute('''
            SELECT id, recommended_mail_count, engagement_prediction, 
                   spam_risk_score, status, approved_by_user, created_at
            FROM ai_mail_strategies
            WHERE company_name = ?
            ORDER BY created_at DESC
        ''', (company_name,))
        
        ai_strategies = []
        for row in cursor.fetchall():
            ai_strategies.append({
                'id': row[0],
                'mail_count': row[1],
                'engagement_prediction': row[2],
                'spam_risk_score': row[3],
                'status': row[4],
                'approved': bool(row[5]),
                'created_at': row[6]
            })
        
        # Manuel stratejiler
        cursor.execute('''
            SELECT id, mail_count, user_notes, status, created_at
            FROM manual_mail_strategies
            WHERE company_name = ?
            ORDER BY created_at DESC
        ''', (company_name,))
        
        manual_strategies = []
        for row in cursor.fetchall():
            manual_strategies.append({
                'id': row[0],
                'mail_count': row[1],
                'user_notes': row[2],
                'status': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        
        return {
            'ai_strategies': ai_strategies,
            'manual_strategies': manual_strategies
        }
    
    def update_mail_history(self, company_name: str, company_email: str,
                          subject: str, content: str, opened: bool = False,
                          replied: bool = False, clicked: bool = False) -> bool:
        """Mail geçmişini güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            engagement_score = 0
            if opened:
                engagement_score += 30
            if clicked:
                engagement_score += 30
            if replied:
                engagement_score += 40
            
            cursor.execute('''
                INSERT INTO company_mail_history (
                    company_name, company_email, mail_subject, mail_content,
                    sent_date, opened, replied, clicked, engagement_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name, company_email, subject, content,
                datetime.now().isoformat(), opened, replied, clicked, engagement_score
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Mail geçmişi güncelleme hatası: {e}")
            return False
    
    def update_website_data(self, company_name: str, website_url: str,
                          products: str = '', services: str = '',
                          contact_info: str = '', campaigns: str = '',
                          analysis_data: str = '') -> bool:
        """Web sitesi verilerini güncelle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO company_website_data (
                    company_name, website_url, products, services,
                    contact_info, campaigns, analysis_data, last_scraped
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_name, website_url, products, services,
                contact_info, campaigns, analysis_data, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Web sitesi verisi güncelleme hatası: {e}")
            return False


# Test fonksiyonu
if __name__ == "__main__":
    strategy_manager = AIMailStrategy()
    
    # Test: Örnek firma için strateji analizi
    test_company = "Test Firma A.Ş."
    
    print(f"\n{'='*60}")
    print(f"AI Mail Stratejisi - Test")
    print(f"{'='*60}\n")
    
    # Örnek veri ekle
    strategy_manager.update_website_data(
        test_company,
        "https://test-firma.com",
        products="Yazılım geliştirme, Bulut hizmetleri",
        services="IT danışmanlık, Dijital dönüşüm",
        campaigns="Yıl sonu kampanyası %20 indirim"
    )
    
    strategy_manager.update_mail_history(
        test_company,
        "info@test-firma.com",
        "Yeni Ürün Tanıtımı",
        "Merhaba, yeni ürünümüzü tanıtmak isteriz...",
        opened=True,
        clicked=True,
        replied=False
    )
    
    # Firma geçmişini göster
    history = strategy_manager.get_company_history(test_company)
    print(f"Firma: {test_company}")
    print(f"Toplam Mail: {history['total_mails']}")
    print(f"Açılma Oranı: {history['open_rate']}%")
    print(f"Yanıt Oranı: {history['reply_rate']}%")
    print(f"\nAI analizi için hazır ✓")

