#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import re
from typing import List, Dict, Optional, Tuple, Callable, Any
import openai
from datetime import datetime, timedelta
import logging
import hashlib
from apollo_manager import ApolloManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIManager:
    """Tüm API işlemlerini yöneten sınıf - WhatsApp ve Snov.io entegrasyonlu"""
    
    def __init__(self, db=None):
        self.settings = {}
        self.snov_access_token = None
        self.snov_token_expiry = 0
        self.is_cancelled = False
        self.apollo_manager = None
        self.db = db
        
    
    def set_database(self, db):
        """Database instance'ını ayarla"""
        self.db = db
    
    def update_settings(self, settings: dict):
        """API ayarlarını güncelle"""
        self.settings = settings
        
        # OpenAI API key'i ayarla
        if settings.get('openai_api_key'):
            openai.api_key = settings['openai_api_key']
        
        # Apollo.io manager'ı başlat
        if settings.get('apollo_api_key'):
            self.apollo_manager = ApolloManager(settings['apollo_api_key'])
        else:
            self.apollo_manager = None
    
    def cancel_operation(self):
        """Mevcut işlemi iptal et"""
        self.is_cancelled = True
    
    def reset_cancel_flag(self):
        """İptal flag'ini sıfırla"""
        self.is_cancelled = False
    
    def get_company_knowledge(self) -> str:
        """Öğrenilmiş firma bilgilerini getir (mail oluşturma için)"""
        if not self.db:
            return ""
        
        try:
            # Öğrenilmiş tüm bilgileri getir
            learned_knowledge = self.db.get_all_knowledge(filter_learned=True)
            
            if not learned_knowledge:
                return ""
            
            # Bilgileri düzenli bir formatta birleştir
            knowledge_text = "\n\n📚 FİRMAMIZ HAKKINDA ÖĞRENİLEN BİLGİLER:\n"
            knowledge_text += "=" * 60 + "\n"
            
            for item in learned_knowledge[:10]:  # Son 10 öğrenilen bilgiyi kullan
                title = item.get('title', 'İsimsiz')
                summary = item.get('ai_summary', '')
                content_type = item.get('content_type', 'text')
                
                knowledge_text += f"\n📌 {title} ({content_type})\n"
                if summary:
                    knowledge_text += f"   → {summary[:300]}...\n" if len(summary) > 300 else f"   → {summary}\n"
            
            knowledge_text += "\n" + "=" * 60 + "\n"
            knowledge_text += "Bu bilgileri mail içeriğinde kullanabilirsin (ürün isimleri, kampanyalar, özellikler vb.)\n"
            
            return knowledge_text
            
        except Exception as e:
            logger.error(f"Knowledge base okuma hatası: {e}")
            return ""
    
    # ========== GOOGLE MAPS BÖLÜMÜ ==========
    
    def search_google_maps_batch(self, query: str, location: str, 
                                max_results: int = 20,
                                batch_size: int = 20,
                                progress_callback: Callable = None,
                                existing_firm_ids: set = None) -> List[Dict]:
        """Google Maps API ile batch işletme arama"""
        try:
            self.reset_cancel_flag()
            
            api_key = self.settings.get('google_api_key')
            if not api_key:
                raise ValueError("Google Maps API key eksik!")
            
            all_firms = []
            existing_ids = existing_firm_ids or set()
            next_page_token = None
            total_processed = 0
            duplicates_skipped = 0
            
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            
            while len(all_firms) < max_results and not self.is_cancelled:
                if progress_callback:
                    progress_callback(f"🔍 Arama yapılıyor... ({len(all_firms)}/{max_results})")
                
                search_params = {
                    "query": f"{query} in {location}",
                    "language": "tr",
                    "key": api_key
                }
                
                if next_page_token:
                    search_params["pagetoken"] = next_page_token
                
                response = requests.get(search_url, params=search_params)
                
                if response.status_code != 200:
                    raise Exception(f"Google Maps API HTTP hatası: {response.status_code}")
                
                data = response.json()
                
                if data.get('status') not in ['OK', 'ZERO_RESULTS']:
                    raise Exception(f"Google Maps API hatası: {data.get('status')}")
                
                results = data.get('results', [])
                
                if not results:
                    break
                
                batch_firms = []
                for i, place in enumerate(results):
                    if self.is_cancelled:
                        break
                    
                    if place['place_id'] in existing_ids:
                        duplicates_skipped += 1
                        if progress_callback:
                            progress_callback(f"⭕️ {place.get('name', 'İsimsiz')} zaten mevcut (place_id: {place['place_id']}), atlanıyor...")
                        logger.info(f"Duplicate company skipped: {place.get('name', 'İsimsiz')} (place_id: {place['place_id']})")
                        continue
                    
                    if progress_callback:
                        progress_callback(f"🔍 İşleniyor: {place.get('name', 'İsimsiz')} ({total_processed + 1}/{max_results})")
                    
                    try:
                        firm = self.get_place_details(place, api_key)
                        if firm:
                            # WhatsApp numarasını formatla
                            if firm.get('phone'):
                                firm['whatsapp_number'] = self.format_whatsapp_number(firm['phone'])
                                firm['whatsapp_opt_in'] = False  # Varsayılan olarak opt-in yok
                            
                            batch_firms.append(firm)
                            existing_ids.add(firm['place_id'])
                            total_processed += 1
                            
                            if total_processed >= max_results:
                                break
                        
                        time.sleep(0.2)
                        
                    except Exception as e:
                        logger.warning(f"Firma detayı alınamadı: {str(e)}")
                
                all_firms.extend(batch_firms)
                
                next_page_token = data.get('next_page_token')
                if not next_page_token or len(all_firms) >= max_results:
                    break
                
                if progress_callback:
                    progress_callback("⏳ Sonraki sayfa için bekleniyor...")
                time.sleep(2)
            
            all_firms.sort(key=lambda x: x['popularity_score'], reverse=True)
            
            # Duplicate sayısını hesapla
            total_processed = len(all_firms)
            
            if progress_callback:
                if duplicates_skipped > 0:
                    progress_callback(f"✅ Toplam {len(all_firms)} yeni firma bulundu! ({duplicates_skipped} duplikat atlandı)")
                else:
                    progress_callback(f"✅ Toplam {len(all_firms)} yeni firma bulundu!")
            
            logger.info(f"Google Maps search completed: {len(all_firms)} new firms, {duplicates_skipped} duplicates skipped")
            return all_firms[:max_results]
            
        except Exception as e:
            if self.is_cancelled:
                if progress_callback:
                    progress_callback("❌ İşlem iptal edildi!")
                return []
            
            logger.error(f"Google Maps API hatası: {str(e)}")
            raise
    
    def get_place_details(self, place: dict, api_key: str) -> Optional[Dict]:
        """Tek bir yerin detaylarını al"""
        try:
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                "place_id": place['place_id'],
                "fields": "name,rating,user_ratings_total,formatted_address,formatted_phone_number,website,types,price_level,opening_hours,url,photos",
                "language": "tr",
                "key": api_key
            }
            
            response = requests.get(details_url, params=details_params)
            data = response.json()
            
            if data.get('status') == 'OK':
                result = data.get('result', {})
                
                firm = {
                    'id': place['place_id'],
                    'place_id': place['place_id'],  # place_id'yi ayrıca ekle
                    'name': result.get('name', place.get('name', '')),
                    'rating': result.get('rating', 0),
                    'review_count': result.get('user_ratings_total', 0),
                    'address': result.get('formatted_address', place.get('formatted_address', '')),
                    'phone': result.get('formatted_phone_number', ''),
                    'website': result.get('website', ''),
                    'types': result.get('types', place.get('types', [])),
                    'price_level': result.get('price_level', 0),
                    'is_open': result.get('opening_hours', {}).get('open_now', None),
                    'google_maps_url': result.get('url', ''),
                    'lat': place.get('geometry', {}).get('location', {}).get('lat', 0),
                    'lng': place.get('geometry', {}).get('location', {}).get('lng', 0),
                    'photos': [],
                    'preferred_contact_method': None  # Daha sonra belirlenecek
                }
                
                # Fotoğraf URL'lerini al
                photos = result.get('photos', [])
                for photo in photos[:3]:
                    photo_ref = photo.get('photo_reference')
                    if photo_ref:
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}"
                        firm['photos'].append(photo_url)
                
                # Popülerlik skoru hesapla
                if firm['rating'] and firm['review_count']:
                    popularity_score = (firm['rating'] * firm['review_count']) / 100
                    firm['popularity_score'] = round(popularity_score, 2)
                else:
                    firm['popularity_score'] = 0
                
                return firm
            
            return None
            
        except Exception as e:
            logger.error(f"Place details hatası: {str(e)}")
            return None
    
    def search_google_maps(self, query: str, location: str) -> List[Dict]:
        """Google Maps API ile işletme arama (geriye uyumluluk için)"""
        return self.search_google_maps_batch(query, location, max_results=20)
    
    # ========== SNOV.IO BÖLÜMÜ ==========
    
    def get_snov_access_token(self) -> str:
        """Snov.io access token al veya yenile"""
        if self.snov_access_token and time.time() < self.snov_token_expiry:
            return self.snov_access_token
        
        try:
            client_id = self.settings.get('snov_client_id')
            client_secret = self.settings.get('snov_client_secret')
            
            if not client_id or not client_secret:
                logger.warning("Snov.io API credentials eksik!")
                return None
            
            auth_url = "https://api.snov.io/v1/oauth/access_token"
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            response = requests.post(auth_url, data=auth_data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self.snov_access_token = token_data['access_token']
            self.snov_token_expiry = time.time() + (55 * 60)
            
            return self.snov_access_token
            
        except Exception as e:
            logger.error(f"Snov.io token hatası: {str(e)}")
            return None
    
    def find_emails_combined(self, company_name: str, domain: str = None) -> List[Dict]:
        """Snov.io ve Apollo.io ile email bul"""
        emails = []
        
        # Snov.io ile arama
        if self.settings.get('snov_client_id') and self.settings.get('snov_client_secret'):
            logger.info(f"Snov.io ile email aranıyor: {company_name}")
            snov_emails = self.find_emails_snov_improved(company_name, domain)
            if snov_emails:
                emails.extend(snov_emails)
                logger.info(f"Snov.io'dan {len(snov_emails)} email bulundu")
        else:
            logger.warning("Snov.io API bilgileri eksik")
        
        # Apollo.io ile arama
        if self.settings.get('apollo_api_key'):
            logger.info(f"Apollo.io ile email aranıyor: {company_name}")
            apollo_contacts = self.find_apollo_contacts(company_name, domain)
            if apollo_contacts:
                # Apollo.io formatını Snov.io formatına çevir
                apollo_emails = []
                for contact in apollo_contacts:
                    apollo_emails.append({
                        'email': contact['email'],
                        'first_name': contact['first_name'],
                        'last_name': contact['last_name'],
                        'position': contact['position'],
                        'source': 'apollo.io',
                        'type': self.determine_email_type(contact['email'], contact['position']),
                        'status': 'verified',  # Apollo.io genelde doğrulanmış veriler sunar
                        'is_verified': True,
                        'score': contact['score'],
                        'phone': contact.get('phone', ''),
                        'whatsapp_number': contact.get('whatsapp_number', ''),
                        'linkedin_url': contact.get('linkedin_url', '')
                    })
                
                emails.extend(apollo_emails)
                logger.info(f"Apollo.io'dan {len(apollo_emails)} email bulundu")
        else:
            logger.warning("Apollo.io API key eksik")
        
        # Duplicate email'leri temizle
        unique_emails = {}
        for email_data in emails:
            email_key = email_data['email'].lower()
            if email_key not in unique_emails:
                unique_emails[email_key] = email_data
            else:
                # Daha yüksek skorlu olanı tut
                if email_data.get('score', 0) > unique_emails[email_key].get('score', 0):
                    unique_emails[email_key] = email_data
        
        final_emails = list(unique_emails.values())
        final_emails.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Toplam {len(final_emails)} benzersiz email bulundu")
        return final_emails
    
    def find_emails_snov_improved(self, company_name: str, domain: str = None) -> List[Dict]:
        """Geliştirilmiş Snov.io email bulma"""
        try:
            access_token = self.get_snov_access_token()
            if not access_token:
                return []
            
            all_emails = []
            
            if not domain:
                logger.info(f"Domain aranıyor: {company_name}")
                domain = self.find_company_domain_snov_improved(company_name, access_token)
                
                if not domain:
                    clean_name = company_name.lower().replace(' ', '').replace('-', '')
                    possible_domains = [
                        f"{clean_name}.com",
                        f"{clean_name}.com.tr", 
                        f"{clean_name}.net",
                        f"www.{clean_name}.com"
                    ]
                    
                    for test_domain in possible_domains:
                        logger.info(f"Domain tahmini deneniyor: {test_domain}")
                        prospects = self.find_prospects_by_domain_snov_improved(test_domain, access_token)
                        if prospects:
                            domain = test_domain
                            break
            else:
                domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
                if domain.startswith('www.'):
                    domain = domain[4:]
            
            if domain:
                logger.info(f"Yetkililer aranıyor: {domain}")
                prospects = self.find_prospects_by_domain_snov_improved(domain, access_token)
                
                if not prospects:
                    logger.warning(f"Yetkili bulunamadı: {domain}")
                    prospects = self.find_prospects_v1_fallback(domain, access_token)
                
                logger.info(f"{len(prospects)} yetkili bulundu")
                
                for prospect in prospects[:15]:
                    first_name = prospect.get('first_name', '')
                    last_name = prospect.get('last_name', '')
                    position = prospect.get('position', '')
                    email = prospect.get('email', '')
                    
                    if email:
                        logger.info(f"Email bulundu (direkt): {email}")
                        
                        is_valid, status = self.verify_email_snov(email, access_token)
                        
                        all_emails.append({
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'position': position,
                            'source': 'snov.io',
                            'type': self.determine_email_type(email, position),
                            'status': status,
                            'is_verified': is_valid,
                            'score': self.calculate_email_score({
                                'position': position,
                                'status': status
                            })
                        })
                    
                    elif first_name and last_name:
                        full_name = f"{first_name} {last_name}"
                        logger.info(f"Email aranıyor: {full_name}")
                        
                        email_info = self.find_email_by_name_snov(first_name, last_name, domain, access_token)
                        
                        if email_info and email_info.get('email'):
                            email = email_info['email']
                            logger.info(f"Email bulundu (isimden): {email}")
                            
                            is_valid, status = self.verify_email_snov(email, access_token)
                            
                            all_emails.append({
                                'email': email,
                                'first_name': first_name,
                                'last_name': last_name,
                                'position': position,
                                'source': 'snov.io',
                                'type': self.determine_email_type(email, position),
                                'status': status,
                                'is_verified': is_valid,
                                'score': self.calculate_email_score({
                                    'position': position,
                                    'status': status
                                })
                            })
                        else:
                            logger.warning(f"Email bulunamadı: {full_name}")
            
            if not all_emails and domain:
                logger.info("Genel email pattern'leri deneniyor...")
                common_emails = [
                    f"info@{domain}",
                    f"contact@{domain}",
                    f"sales@{domain}",
                    f"hello@{domain}",
                    f"iletisim@{domain}",
                    f"bilgi@{domain}"
                ]
                
                for email in common_emails:
                    is_valid, status = self.verify_email_snov(email, access_token)
                    if is_valid:
                        all_emails.append({
                            'email': email,
                            'first_name': '',
                            'last_name': '',
                            'position': 'General Contact',
                            'source': 'pattern_guess',
                            'type': 'info',
                            'is_verified': True,
                            'status': status,
                            'score': 50
                        })
                        logger.info(f"Pattern email doğrulandı: {email}")
            
            unique_emails = {}
            for email_data in all_emails:
                if email_data['email'] not in unique_emails:
                    unique_emails[email_data['email']] = email_data
            
            return list(unique_emails.values())
            
        except Exception as e:
            logger.error(f"Snov.io email arama hatası: {str(e)}")
            return []
    
    def find_company_domain_snov_improved(self, company_name: str, access_token: str) -> Optional[str]:
        """Geliştirilmiş Snov.io domain bulma"""
        try:
            url = "https://api.snov.io/v2/company-domain-by-name/start"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            company_variations = [
                company_name,
                company_name.lower(),
                company_name.upper(),
                company_name.replace(' ', ''),
                company_name.replace(' ', '-')
            ]
            
            for variation in company_variations[:3]:
                data = {
                    'names': [variation]
                }
                
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                
                if not result.get('success'):
                    logger.warning(f"Domain arama başarısız ({variation}): {result}")
                    continue
                
                task_hash = result.get('data', {}).get('task_hash')
                if not task_hash:
                    continue
                
                time.sleep(5)
                
                result_url = "https://api.snov.io/v2/company-domain-by-name/result"
                params = {'task_hash': task_hash}
                
                response = requests.get(result_url, params=params, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get('status') == 'completed':
                    data = result.get('data', [])
                    if data and isinstance(data, list) and len(data) > 0:
                        first_result = data[0]
                        if isinstance(first_result, dict) and 'result' in first_result:
                            domain_info = first_result['result']
                            if isinstance(domain_info, dict) and 'domain' in domain_info:
                                found_domain = domain_info['domain']
                                logger.info(f"Domain bulundu: {found_domain} (variation: {variation})")
                                return found_domain
            
            return None
            
        except Exception as e:
            logger.error(f"Domain arama hatası: {str(e)}")
            return None
    
    def find_prospects_by_domain_snov_improved(self, domain: str, access_token: str) -> List[Dict]:
        """Geliştirilmiş Snov.io prospect bulma"""
        try:
            clean_domain = domain.lower().strip()
            if clean_domain.startswith('www.'):
                clean_domain = clean_domain[4:]
            
            url = "https://api.snov.io/v2/domain-search/prospects/start"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'domain': clean_domain,
                'type': 'all',
                'limit': 100
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            task_hash = result.get('meta', {}).get('task_hash')
            if not task_hash:
                return self.find_prospects_v1_fallback(clean_domain, access_token)
            
            time.sleep(5)
            
            result_url = f"https://api.snov.io/v2/domain-search/prospects/result/{task_hash}"
            
            response = requests.get(result_url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            retry_count = 0
            while result.get('status') == 'processing' and retry_count < 3:
                time.sleep(3)
                response = requests.get(result_url, headers=headers)
                result = response.json()
                retry_count += 1
            
            if result.get('status') == 'completed':
                prospects = result.get('data', [])
                logger.info(f"Toplam {len(prospects)} prospect bulundu")
                return prospects
            
            return []
            
        except Exception as e:
            logger.error(f"Prospect arama hatası: {str(e)}")
            return []
    
    def find_prospects_v1_fallback(self, domain: str, access_token: str) -> List[Dict]:
        """V1 API fallback"""
        try:
            url = "https://api.snov.io/v1/get-domain-emails-with-info"
            data = {
                'access_token': access_token,
                'domain': domain,
                'type': 'all',
                'limit': 100
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                emails = result.get('emails', [])
                logger.info(f"V1 API ile {len(emails)} email bulundu")
                
                prospects = []
                for email_data in emails:
                    prospects.append({
                        'first_name': email_data.get('first_name', ''),
                        'last_name': email_data.get('last_name', ''),
                        'position': email_data.get('position', ''),
                        'email': email_data.get('email', '')
                    })
                
                return prospects
            
            return []
            
        except Exception as e:
            logger.error(f"V1 fallback hatası: {str(e)}")
            return []
    
    def find_email_by_name_snov(self, first_name: str, last_name: str, domain: str, access_token: str) -> Optional[Dict]:
        """Snov.io ile isim ve domain'den email bul"""
        try:
            url = "https://api.snov.io/v2/emails-by-domain-by-name/start"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                'rows': [{
                    'first_name': first_name,
                    'last_name': last_name,
                    'domain': domain
                }]
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            task_hash = result.get('data', {}).get('task_hash')
            if not task_hash:
                return None
            
            time.sleep(3)
            
            result_url = "https://api.snov.io/v2/emails-by-domain-by-name/result"
            params = {'task_hash': task_hash}
            
            response = requests.get(result_url, params=params, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') == 'completed':
                data = result.get('data', [])
                if data and len(data) > 0:
                    person = data[0]
                    emails = person.get('result', [])
                    if emails and len(emails) > 0:
                        return emails[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Email bulma hatası: {str(e)}")
            return None
    
    def verify_email_snov(self, email: str, access_token: str) -> Tuple[bool, str]:
        """Snov.io ile email'i doğrula"""
        try:
            url = "https://api.snov.io/v2/email-verification/start"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                'emails': [email]
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            task_hash = result.get('data', {}).get('task_hash')
            if not task_hash:
                return False, "unknown"
            
            time.sleep(3)
            
            result_url = "https://api.snov.io/v2/email-verification/result"
            params = {'task_hash': task_hash}
            
            response = requests.get(result_url, params=params, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('status') == 'completed':
                data = result.get('data', [])
                if data and len(data) > 0:
                    verification = data[0]
                    result_info = verification.get('result', {})
                    is_valid = (
                        result_info.get('is_valid_format', False) and 
                        result_info.get('smtp_status') == 'valid'
                    )
                    return is_valid, result_info.get('smtp_status', 'unknown')
            
            return False, "unknown"
            
        except Exception as e:
            logger.error(f"Email doğrulama hatası: {str(e)}")
            return False, "error"
    
    def find_emails_snov(self, company_name: str, domain: str = None) -> List[Dict]:
        """Eski fonksiyon - yeni fonksiyona yönlendir"""
        return self.find_emails_snov_improved(company_name, domain)
    
    def determine_email_type(self, email: str, position: str = "") -> str:
        """Email tipini belirle"""
        email_lower = email.lower()
        local_part = email_lower.split('@')[0]
        position_lower = position.lower()
        
        if position:
            if any(title in position_lower for title in ['ceo', 'cto', 'cfo', 'coo', 'cmo', 'genel müdür', 'başkan', 'president']):
                return 'c_level'
            elif any(title in position_lower for title in ['founder', 'kurucu', 'owner', 'sahip', 'partner', 'ortak']):
                return 'founder'
            elif any(title in position_lower for title in ['director', 'direktör', 'vp', 'vice president', 'head of', 'müdür']):
                return 'director'
            elif any(title in position_lower for title in ['manager', 'yönetici', 'lead', 'supervisor', 'uzman', 'specialist']):
                return 'manager'
            elif any(title in position_lower for title in ['sales', 'satış', 'business development', 'bd', 'pazarlama', 'marketing']):
                return 'sales'
        
        if any(title in local_part for title in ['ceo', 'cto', 'cfo', 'coo', 'cmo', 'founder', 'owner']):
            return 'c_level'
        elif any(dept in local_part for dept in ['sales', 'satis', 'pazarlama', 'marketing', 'business']):
            return 'sales'
        elif any(dept in local_part for dept in ['support', 'destek', 'help', 'yardim', 'musteri']):
            return 'support'
        elif any(dept in local_part for dept in ['info', 'bilgi', 'general', 'genel', 'contact', 'iletisim']):
            return 'info'
        elif re.match(r'^[a-z]+[\.\-_][a-z]+$', local_part):
            return 'personal'
        
        return 'general'
    
    def calculate_email_score(self, person_data: dict) -> int:
        """Email skorunu hesapla"""
        score = 50
        
        position = person_data.get('position', '').lower()
        
        if any(title in position for title in ['ceo', 'cto', 'cfo', 'coo', 'cmo', 'genel müdür', 'başkan', 'president']):
            score = 100
        elif any(title in position for title in ['founder', 'kurucu', 'owner', 'sahip', 'partner', 'ortak']):
            score = 95
        elif any(title in position for title in ['director', 'direktör', 'vp', 'vice president', 'head of', 'müdür']):
            score = 90
        elif any(title in position for title in ['manager', 'yönetici', 'lead', 'supervisor', 'uzman', 'specialist']):
            score = 80
        elif any(title in position for title in ['sales', 'satış', 'business development', 'bd', 'pazarlama', 'marketing']):
            score = 75
        elif any(title in position for title in ['hr', 'human resources', 'insan kaynakları', 'ik']):
            score = 60
        
        if person_data.get('status') == 'verified':
            score += 10
        
        return min(score, 100)
    
    # ========== GPT VE WHATSAPP BÖLÜMÜ ==========
    
    def generate_whatsapp_message_gpt(self, firm_data: dict, template: dict = None, 
                                     message_type: str = 'intro') -> Dict:
        """GPT ile WhatsApp mesajı oluştur"""
        try:
            # Template yoksa varsayılan kullan
            if not template:
                template = self.get_default_whatsapp_template(message_type)
            
            # Firma bilgilerini hazırla
            firm_context = f"""
            Firma Adı: {firm_data.get('name')}
            Sektör: {', '.join(firm_data.get('types', [])[:3])}
            Rating: {firm_data.get('rating', 'N/A')}/5
            Telefon: {firm_data.get('phone', '')}
            WhatsApp: {firm_data.get('whatsapp_number', '')}
            Website: {firm_data.get('website', 'Yok')}
            Konum: {firm_data.get('address', '')}
            Yetkili: {firm_data.get('contact_person', 'Değerli Müşterimiz')}
            Pozisyon: {firm_data.get('contact_position', '')}
            """
            
            # GPT promptu
            messages = [
                {
                    "role": "system",
                    "content": "Sen WhatsApp üzerinden B2B pazarlama yapan deneyimli bir satış uzmanısın. Kısa, samimi ve etkili mesajlar yazıyorsun."
                },
                {
                    "role": "user",
                    "content": f"""
                    Aşağıdaki firma için bir WhatsApp mesajı yaz:
                    
                    {firm_context}
                    
                    Mesaj Tipi: {message_type}
                    Template: {template.get('content', '')}
                    
                    Kurallar:
                    - Maksimum 150 karakter (WhatsApp için ideal)
                    - Samimi ve profesyonel dil
                    - Uygun emoji kullan (abartma)
                    - Net bir call-to-action içer
                    - Firma'ya özel detaylar kullan
                    
                    Sadece mesaj metnini döndür, başka bir şey ekleme.
                    """
                }
            ]
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,
                max_tokens=100
            )
            
            message = response.choices[0].message.content.strip()
            
            # Template değişkenlerini yerine koy
            message = message.replace('{{firma_adi}}', firm_data.get('name', ''))
            message = message.replace('{{firma_sektoru}}', ', '.join(firm_data.get('types', [])[:2]))
            message = message.replace('{{yetkili}}', firm_data.get('contact_person', 'Değerli Müşterimiz'))
            
            return {
                'success': True,
                'message': message,
                'type': message_type,
                'firm_id': firm_data.get('id'),
                'firm_name': firm_data.get('name'),
                'to_number': firm_data.get('whatsapp_number')
            }
            
        except Exception as e:
            logger.error(f"GPT WhatsApp mesajı oluşturma hatası: {str(e)}")
            return self.generate_fallback_whatsapp_message(firm_data, message_type)
    
    def generate_fallback_whatsapp_message(self, firm_data: dict, message_type: str) -> Dict:
        """GPT çalışmazsa kullanılacak fallback WhatsApp mesajı"""
        templates = {
            'intro': f"Merhaba {firm_data.get('name', 'Değerli Müşterimiz')} 👋 B2B çözümlerimizle verimliliğinizi artırabiliriz. İlgilenir misiniz? 🚀",
            'follow_up': f"Merhaba {firm_data.get('name', '')} 😊 Mesajımızı görme fırsatınız oldu mu? Sorularınız varsa yardımcı olabilirim.",
            'offer': f"🎉 {firm_data.get('name', '')} için özel %30 indirim! Detaylar için yazın 💬",
            'meeting': f"Merhaba {firm_data.get('name', '')} 📅 15 dakikalık demo için uygun musunuz?",
            'thank_you': f"{firm_data.get('name', '')}, ilginiz için teşekkürler! 🙏 Size dönüş yapacağız.",
            'reminder': f"Merhaba {firm_data.get('name', '')} 📧 Email'imizi incelediniz mi? Spam klasörünü kontrol edin.",
            'reengagement': f"{firm_data.get('name', '')} ekibi, yeni özelliklerimizi görmek ister misiniz? 👋"
        }
        
        message = templates.get(message_type, templates['intro'])
        
        return {
            'success': True,
            'message': message,
            'type': message_type,
            'firm_id': firm_data.get('id'),
            'firm_name': firm_data.get('name'),
            'to_number': firm_data.get('whatsapp_number')
        }
    
    def get_default_whatsapp_template(self, message_type: str) -> Dict:
        """Varsayılan WhatsApp template'ini getir"""
        templates = {
            'intro': {
                'name': 'Tanıtım',
                'content': "Merhaba {{firma_adi}} 👋 {{firma_sektoru}} sektöründe verimliliğinizi artırabiliriz. İlgilenir misiniz? 🚀"
            },
            'follow_up': {
                'name': 'Takip',
                'content': "Merhaba {{firma_adi}} 😊 Mesajımızı görme fırsatınız oldu mu?"
            },
            'offer': {
                'name': 'Özel Teklif',
                'content': "🎉 {{firma_adi}} için özel %30 indirim! Detaylar için yazın 💬"
            },
            'meeting': {
                'name': 'Toplantı Talebi',
                'content': "Merhaba {{firma_adi}} 📅 15 dakikalık demo için uygun musunuz?"
            },
            'thank_you': {
                'name': 'Teşekkür',
                'content': "{{firma_adi}}, ilginiz için teşekkürler! 🙏 Size dönüş yapacağız."
            },
            'reminder': {
                'name': 'Hatırlatma',
                'content': "Merhaba {{firma_adi}} 📧 Email'imizi incelediniz mi?"
            },
            'reengagement': {
                'name': 'Yeniden Etkileşim',
                'content': "{{firma_adi}} ekibi, yeni özelliklerimizi görmek ister misiniz? 👋"
            }
        }
        
        return templates.get(message_type, templates['intro'])
    
    def format_whatsapp_number(self, phone: str) -> str:
        """Telefon numarasını WhatsApp formatına dönüştür"""
        phone = re.sub(r'\D', '', str(phone))
        
        if phone.startswith('0'):
            phone = phone[1:]
        
        if phone.startswith('5') and len(phone) == 10:
            phone = '90' + phone
        
        if not phone.startswith('90') and len(phone) == 10:
            phone = '90' + phone
        
        if not phone.startswith('+'):
            phone = '+' + phone
        
        return phone
    
    def generate_email_gpt(self, firm_data: dict, template: dict) -> Dict:
        """GPT ile email oluştur - 🆕 Knowledge Base Bilgileri Dahil"""
        try:
            emails = firm_data.get('emails', [])
            primary_email = emails[0] if emails else {'email': 'info@example.com', 'position': ''}
            
            # 🆕 Firma bilgilerimizi knowledge base'den al
            company_knowledge = self.get_company_knowledge()
            
            firm_context = f"""
            Firma Adı: {firm_data.get('name')}
            Sektör: {', '.join(firm_data.get('types', [])[:3])}
            Website: {firm_data.get('website', 'Yok')}
            Konum: {firm_data.get('address', '')}
            Rating: {firm_data.get('rating', 'N/A')}/5 ({firm_data.get('review_count', 0)} değerlendirme)
            Telefon: {firm_data.get('phone', 'Yok')}
            WhatsApp: {firm_data.get('whatsapp_number', 'Yok')}
            
            Alıcı Email: {primary_email['email']}
            Alıcı Pozisyon: {primary_email.get('position', 'Bilinmiyor')}
            
            Web Analiz Özeti: {firm_data.get('ai_summary', 'Henüz analiz edilmedi')}
            Kullanılan Teknolojiler: {', '.join(firm_data.get('technologies', [])[:5])}
            Sunulan Hizmetler: {', '.join(firm_data.get('services', [])[:5])}
            Tahmini Çalışan Sayısı: {firm_data.get('team_size', 'Bilinmiyor')}
            {company_knowledge}
            """
            
            messages = [
                {
                    "role": "system",
                    "content": template.get('system_prompt', 'Sen deneyimli bir B2B satış uzmanısın.')
                },
                {
                    "role": "user",
                    "content": f"""
                    Aşağıdaki firma bilgilerini kullanarak kişiselleştirilmiş bir B2B satış maili yaz:
                    
                    {firm_context}
                    
                    Talimatlar: {template.get('instructions', 'Profesyonel bir tanıtım maili yaz.')}
                    
                    ÖNEMLİ KURALLAR:
                    1. WhatsApp numarası varsa, email'de WhatsApp üzerinden de iletişime geçebileceklerini belirt.
                    2. 🆕 Yukarıdaki "FİRMAMIZ HAKKINDA ÖĞRENİLEN BİLGİLER" bölümünde verilen bilgileri MUTLAKA kullan!
                    3. Ürün isimlerini, kampanyaları, özel teklifleri ve diğer firma bilgilerini mail içeriğine dahil et.
                    4. Öğrenilen bilgilerden alıcının ilgisini çekebilecek detayları öne çıkar.
                    
                    Yanıtını SADECE şu JSON formatında ver (başka hiçbir metin ekleme):
                    {{
                        "subject": "Mail konusu",
                        "body": "Mail içeriği (HTML formatında)"
                    }}
                    """
                }
            ]
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.8,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            
            try:
                # JSON parse et
                email_content = json.loads(content)
                print(f"🔍 DEBUG: GPT JSON parse başarılı: {email_content}")
            except json.JSONDecodeError as e:
                print(f"❌ DEBUG: JSON parse hatası: {str(e)}")
                print(f"🔍 DEBUG: Raw content: {content}")
                
                # JSON parse edilemezse, içeriği temizle
                if "```json" in content:
                    # JSON blok içinden çıkar
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    if end > start:
                        json_content = content[start:end].strip()
                        try:
                            email_content = json.loads(json_content)
                            print(f"🔍 DEBUG: JSON blok parse başarılı: {email_content}")
                        except:
                            pass
                
                # Hala parse edilemezse fallback
                if 'email_content' not in locals():
                    lines = content.strip().split('\n')
                    subject = lines[0] if lines else f"{firm_data['name']} için Özel Çözümümüz"
                    body = '\n'.join(lines[1:]) if len(lines) > 1 else content
                    
                    email_content = {
                        "subject": subject.replace('"', '').strip(),
                        "body": f"<p>{body}</p>"
                    }
            
            if not email_content['body'].startswith('<'):
                email_content['body'] = f"<p>{email_content['body']}</p>"
            
            email_content['firm_id'] = firm_data['id']
            email_content['firm_name'] = firm_data['name']
            email_content['to_email'] = primary_email['email']
            
            return email_content
            
        except Exception as e:
            logger.error(f"GPT email oluşturma hatası: {str(e)}")
            return self.generate_fallback_email(firm_data)
    
    def generate_fallback_email(self, firm_data: dict) -> Dict:
        """GPT çalışmazsa kullanılacak fallback email - 🆕 Knowledge Base Dahil"""
        emails = firm_data.get('emails', [])
        primary_email = emails[0] if emails else {'email': 'info@example.com'}
        
        rating_text = ""
        if firm_data.get('rating', 0) >= 4.5:
            rating_text = f"{firm_data['rating']} yıldızlı müşteri memnuniyetiniz ile "
        elif firm_data.get('rating', 0) >= 4.0:
            rating_text = "yüksek müşteri memnuniyetiniz ile "
        
        tech_text = ""
        technologies = firm_data.get('technologies', [])
        if technologies:
            tech_text = f"Kullandığınız {', '.join(technologies[:2])} gibi teknolojilerle uyumlu "
        
        whatsapp_text = ""
        if firm_data.get('whatsapp_number'):
            whatsapp_text = f"""
            <p>Ayrıca WhatsApp üzerinden de bize ulaşabilirsiniz: 
            <strong>{firm_data.get('whatsapp_number')}</strong></p>
            """
        
        # 🆕 Knowledge base'den ürün/kampanya bilgilerini al
        knowledge_bullets = ""
        if self.db:
            try:
                learned_knowledge = self.db.get_all_knowledge(filter_learned=True)
                if learned_knowledge and len(learned_knowledge) > 0:
                    knowledge_bullets = "<p><strong>Size özel sunabileceğimiz çözümler:</strong></p><ul>"
                    for item in learned_knowledge[:3]:  # İlk 3 öğrenilen bilgi
                        title = item.get('title', '')
                        if title:
                            knowledge_bullets += f"<li>{title}</li>"
                    knowledge_bullets += "</ul>"
            except Exception as e:
                logger.warning(f"Fallback email için knowledge okuma hatası: {e}")
        
        return {
            "subject": f"{firm_data['name']} için Özel B2B Çözümümüz",
            "body": f"""
            <p>Merhaba {firm_data['name']} Ekibi,</p>
            
            <p>{firm_data.get('address', 'Bölgenizdeki')} konumunda {rating_text}öne çıkan 
            firmanızı yakından takip ediyoruz.</p>
            
            <p>{tech_text}çözümlerimizle, işletmenizin verimliliğini %30'a kadar 
            artırabileceğimizi düşünüyoruz.</p>
            
            {knowledge_bullets}
            
            <p>Size özel hazırlayacağımız demo ile, sektörünüzdeki diğer firmalarla 
            elde ettiğimiz başarıları paylaşmak isteriz.</p>
            
            <p><strong>Bu hafta 15 dakikalık bir görüşme için uygun musunuz?</strong></p>
            
            {whatsapp_text}
            
            <p>Saygılarımla,<br>
            <strong>İbrahim Çete</strong><br>
            Tel: 0546 205 18 20<br>
            WhatsApp: +90 546 205 18 20<br>
            Email: ibrahimcete@trsatis.com</p>
            """,
            "firm_id": firm_data['id'],
            "firm_name": firm_data['name'],
            "to_email": primary_email['email']
        }
    
    def generate_follow_up_email(self, open_data: dict) -> Dict:
        """Takip maili oluştur"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Sen deneyimli bir B2B satış uzmanısın. Nazik ve etkili takip mailleri yazıyorsun."
                },
                {
                    "role": "user",
                    "content": f"""
                    {open_data['firm_name']} firması daha önce gönderdiğimiz maili açtı ama henüz yanıt vermedi.
                    Email: {open_data.get('to_email', '')}
                    
                    Çok kısa, samimi ve etkili bir takip maili yaz:
                    - Maksimum 3-4 cümle
                    - Baskıcı olma, nazik ol
                    - WhatsApp iletişim seçeneğini de sun
                    
                    Yanıtını SADECE şu JSON formatında ver (başka hiçbir metin ekleme):
                    {{
                        "subject": "Mail konusu",
                        "body": "Mail içeriği (HTML formatında)"
                    }}
                    """
                }
            ]
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.9,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except:
                return self.generate_fallback_followup(open_data)
            
        except Exception as e:
            logger.error(f"Takip maili oluşturma hatası: {str(e)}")
            return self.generate_fallback_followup(open_data)
    
    def generate_fallback_followup(self, open_data: dict) -> Dict:
        """Fallback takip maili"""
        return {
            "subject": f"Re: {open_data['firm_name']} için Özel Teklifimiz",
            "body": f"""
            <p>Merhaba {open_data['firm_name']} Ekibi,</p>
            
            <p>Geçen hafta gönderdiğimiz maili incelediğinizi gördük. 👀</p>
            
            <p>Merak ettiğiniz bir konu var mı? Size nasıl yardımcı olabileceğimizi 
            konuşmak için 10 dakikanızı ayırabilir misiniz?</p>
            
            <p>WhatsApp üzerinden de bize ulaşabilirsiniz: +90 546 205 18 20</p>
            
            <p>İyi günler,<br>
            B2B Satış Ekibi</p>
            """
        }
    
    # ========== TEST FONKSİYONLARI ==========
    
    def test_google_maps_api(self) -> Dict:
        """Google Maps API bağlantısını test et"""
        try:
            api_key = self.settings.get('google_api_key')
            if not api_key:
                return {
                    'success': False,
                    'error': 'API key bulunamadı',
                    'message': 'Lütfen Google Maps API key\'inizi ayarlar bölümünden girin.'
                }
            
            test_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            test_params = {
                "query": "restaurant in Istanbul",
                "key": api_key
            }
            
            response = requests.get(test_url, params=test_params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'OK':
                return {
                    'success': True,
                    'message': 'Google Maps API bağlantısı başarılı!',
                    'quota_info': 'API çalışıyor ve kotanız var.'
                }
            elif data.get('status') == 'REQUEST_DENIED':
                return {
                    'success': False,
                    'error': 'API erişimi reddedildi',
                    'message': data.get('error_message', 'API key geçersiz veya kısıtlı.')
                }
            elif data.get('status') == 'OVER_QUERY_LIMIT':
                return {
                    'success': False,
                    'error': 'Kota limiti aşıldı',
                    'message': 'Günlük API kullanım limitiniz dolmuş.'
                }
            else:
                return {
                    'success': False,
                    'error': data.get('status', 'Bilinmeyen hata'),
                    'message': data.get('error_message', 'API yanıtı beklenmedik.')
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Zaman aşımı',
                'message': 'API yanıt vermedi. İnternet bağlantınızı kontrol edin.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'API bağlantı hatası.'
            }
    
    def test_openai_api(self) -> Dict:
        """OpenAI API bağlantısını test et"""
        try:
            if not self.settings.get('openai_api_key'):
                return {
                    'success': False,
                    'error': 'API key bulunamadı',
                    'message': 'Lütfen OpenAI API key\'inizi ayarlar bölümünden girin.'
                }
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'API connection successful' in Turkish"}
                ],
                max_tokens=50
            )
            
            return {
                'success': True,
                'message': 'OpenAI API bağlantısı başarılı!',
                'response': response.choices[0].message.content
            }
            
        except openai.error.AuthenticationError:
            return {
                'success': False,
                'error': 'Kimlik doğrulama hatası',
                'message': 'API key geçersiz. Lütfen kontrol edin.'
            }
        except openai.error.RateLimitError:
            return {
                'success': False,
                'error': 'Rate limit',
                'message': 'API kullanım limitiniz dolmuş.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'OpenAI API bağlantı hatası.'
            }
    
    def test_snov_api(self) -> Dict:
        """Snov.io API bağlantısını test et"""
        try:
            if not self.settings.get('snov_client_id') or not self.settings.get('snov_client_secret'):
                return {
                    'success': False,
                    'error': 'API bilgileri eksik',
                    'message': 'Lütfen Snov.io Client ID ve Secret\'ınızı girin.'
                }
            
            token = self.get_snov_access_token()
            if token:
                try:
                    balance_url = "https://api.snov.io/v1/get-balance"
                    response = requests.get(balance_url, params={'access_token': token})
                    balance_data = response.json()
                    
                    balance = balance_data.get('data', {}).get('balance', 0)
                    
                    return {
                        'success': True,
                        'message': f'Snov.io API bağlantısı başarılı! Kalan kredi: {balance}',
                        'token_preview': token[:20] + '...',
                        'balance': balance
                    }
                except:
                    return {
                        'success': True,
                        'message': 'Snov.io API bağlantısı başarılı!',
                        'token_preview': token[:20] + '...'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Token alınamadı',
                    'message': 'API bilgileri geçersiz olabilir.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Snov.io API bağlantı hatası.'
            }
    
    def test_apollo_api(self) -> Dict:
        """Apollo.io API bağlantısını test et"""
        try:
            if not self.settings.get('apollo_api_key'):
                return {
                    'success': False,
                    'error': 'API key eksik',
                    'message': 'Lütfen Apollo.io API key\'inizi ayarlar bölümünden girin.'
                }
            
            # Apollo.io manager'ı başlat
            apollo_manager = ApolloManager(self.settings['apollo_api_key'])
            result = apollo_manager.test_api_connection()
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Apollo.io API bağlantı hatası.'
            }
    
    
    def debug_snov_search(self, company_name: str, test_domain: str = None):
        """Snov.io arama sürecini debug et"""
        logger.info(f"=== SNOV.IO DEBUG: {company_name} ===")
        
        token = self.get_snov_access_token()
        if not token:
            logger.error("Token alınamadı!")
            return
        
        if not test_domain:
            domain = self.find_company_domain_snov_improved(company_name, token)
            logger.info(f"Bulunan domain: {domain}")
        else:
            domain = test_domain
            logger.info(f"Test domain kullanılıyor: {domain}")
        
        if domain:
            test_domains = [domain, f"www.{domain}"]
            if domain.endswith('.com'):
                test_domains.append(domain.replace('.com', '.com.tr'))
            
            for td in test_domains:
                logger.info(f"\nDenenen domain: {td}")
                prospects = self.find_prospects_by_domain_snov_improved(td, token)
                logger.info(f"Bulunan prospect sayısı: {len(prospects)}")
                
                if prospects:
                    for p in prospects[:3]:
                        logger.info(f"  - {p.get('first_name')} {p.get('last_name')} ({p.get('position')}) - Email: {p.get('email', 'YOK')}")
    
    # ========== APOLLO.IO BÖLÜMÜ ==========
    
    def search_apollo_people(self, company_domain: str = None, 
                           titles: List[str] = None,
                           location: str = None,
                           max_results: int = 50) -> List[Dict]:
        """Apollo.io ile kişi arama"""
        try:
            if not self.apollo_manager:
                logger.warning("Apollo.io API key eksik!")
                return []
            
            if company_domain:
                people = self.apollo_manager.search_people_by_company(
                    company_domain=company_domain,
                    titles=titles,
                    location=location,
                    max_results=max_results
                )
            else:
                # Genel arama
                result = self.apollo_manager.search_people(
                    person_titles=titles,
                    person_locations=[location] if location else None,
                    per_page=min(25, max_results)
                )
                people = result.get('people', [])
            
            # Verileri işle
            processed_people = self.apollo_manager.process_people_data(people)
            
            logger.info(f"Apollo.io'dan {len(processed_people)} kişi bulundu")
            return processed_people
            
        except Exception as e:
            logger.error(f"Apollo.io kişi arama hatası: {str(e)}")
            return []
    
    def search_apollo_companies(self, location: str = None,
                              industry: str = None,
                              employee_range: str = None,
                              max_results: int = 50) -> List[Dict]:
        """Apollo.io ile şirket arama"""
        try:
            if not self.apollo_manager:
                logger.warning("Apollo.io API key eksik!")
                return []
            
            companies = self.apollo_manager.search_companies_by_location(
                location=location,
                industry=industry,
                employee_range=employee_range,
                max_results=max_results
            )
            
            # Verileri işle
            processed_companies = self.apollo_manager.process_organization_data(companies)
            
            logger.info(f"Apollo.io'dan {len(processed_companies)} şirket bulundu")
            return processed_companies
            
        except Exception as e:
            logger.error(f"Apollo.io şirket arama hatası: {str(e)}")
            return []
    
    def enrich_company_with_apollo(self, company_name: str, domain: str = None) -> Dict:
        """Mevcut şirket bilgilerini Apollo.io ile zenginleştir"""
        try:
            if not self.apollo_manager:
                logger.warning("Apollo.io API key eksik!")
                return {}
            
            # Önce şirket arama
            companies = self.search_apollo_companies(
                location="Turkey",  # Türkiye'de arama
                max_results=10
            )
            
            # Domain ile eşleşen şirket bul
            matching_company = None
            if domain:
                for company in companies:
                    if company.get('domain') == domain or domain in company.get('domain', ''):
                        matching_company = company
                        break
            
            if not matching_company and company_name:
                # İsim ile eşleşen şirket bul
                for company in companies:
                    if company_name.lower() in company.get('name', '').lower():
                        matching_company = company
                        break
            
            if not matching_company:
                logger.warning(f"Apollo.io'da eşleşen şirket bulunamadı: {company_name}")
                return {}
            
            # Şirket için kişi arama
            people = self.search_apollo_people(
                company_domain=matching_company.get('domain'),
                titles=['CEO', 'CTO', 'CFO', 'Marketing Manager', 'Sales Manager'],
                max_results=20
            )
            
            # Sonuçları birleştir
            enriched_data = {
                'company': matching_company,
                'people': people,
                'total_people': len(people),
                'source': 'apollo.io',
                'enriched_at': datetime.now().isoformat()
            }
            
            logger.info(f"Apollo.io ile zenginleştirildi: {matching_company.get('name')} - {len(people)} kişi")
            return enriched_data
            
        except Exception as e:
            logger.error(f"Apollo.io zenginleştirme hatası: {str(e)}")
            return {}
    
    def find_apollo_contacts(self, company_name: str, domain: str = None) -> List[Dict]:
        """Apollo.io ile şirket yetkililerini bul"""
        try:
            if not self.apollo_manager:
                logger.warning("Apollo.io API key eksik!")
                return []
            
            # Domain varsa direkt kullan, yoksa şirket adından bul
            search_domain = domain
            if not search_domain:
                # Şirket adından domain tahmin et
                clean_name = company_name.lower().replace(' ', '').replace('-', '')
                possible_domains = [
                    f"{clean_name}.com",
                    f"{clean_name}.com.tr",
                    f"{clean_name}.net"
                ]
                
                for test_domain in possible_domains:
                    people = self.search_apollo_people(
                        company_domain=test_domain,
                        max_results=5
                    )
                    if people:
                        search_domain = test_domain
                        break
            
            if not search_domain:
                logger.warning(f"Domain bulunamadı: {company_name}")
                return []
            
            # Kişi arama
            people = self.search_apollo_people(
                company_domain=search_domain,
                titles=['CEO', 'CTO', 'CFO', 'Marketing Manager', 'Sales Manager', 'Founder'],
                max_results=25
            )
            
            # Email formatına çevir
            contacts = []
            for person in people:
                if person.get('email'):
                    contact = {
                        'email': person['email'],
                        'first_name': person.get('first_name', ''),
                        'last_name': person.get('last_name', ''),
                        'full_name': person.get('full_name', ''),
                        'position': person.get('title', ''),
                        'phone': person.get('phone', ''),
                        'whatsapp_number': person.get('whatsapp_number', ''),
                        'linkedin_url': person.get('linkedin_url', ''),
                        'source': 'apollo.io',
                        'score': self._calculate_apollo_contact_score(person)
                    }
                    contacts.append(contact)
            
            # Skora göre sırala
            contacts.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Apollo.io'dan {len(contacts)} yetkili bulundu: {company_name}")
            return contacts
            
        except Exception as e:
            logger.error(f"Apollo.io yetkili arama hatası: {str(e)}")
            return []
    
    def _calculate_apollo_contact_score(self, person: Dict) -> int:
        """Apollo.io kişi skorunu hesapla"""
        score = 50
        
        title = person.get('title', '').lower()
        
        # Pozisyon skorları
        if any(title_word in title for title_word in ['ceo', 'chief executive', 'genel müdür', 'başkan']):
            score = 100
        elif any(title_word in title for title_word in ['cto', 'chief technology', 'teknoloji müdürü']):
            score = 95
        elif any(title_word in title for title_word in ['cfo', 'chief financial', 'finans müdürü']):
            score = 90
        elif any(title_word in title for title_word in ['founder', 'kurucu', 'owner', 'sahip']):
            score = 95
        elif any(title_word in title for title_word in ['director', 'direktör', 'vp', 'vice president']):
            score = 85
        elif any(title_word in title for title_word in ['manager', 'yönetici', 'head of']):
            score = 75
        elif any(title_word in title for title_word in ['sales', 'satış', 'marketing', 'pazarlama']):
            score = 70
        
        # Email varsa bonus
        if person.get('email'):
            score += 10
        
        # Telefon varsa bonus
        if person.get('phone'):
            score += 5
        
        # LinkedIn varsa bonus
        if person.get('linkedin_url'):
            score += 5
        
        return min(score, 100)
    
    def test_apollo_api(self) -> Dict:
        """Apollo.io API bağlantısını test et"""
        try:
            if not self.apollo_manager:
                return {
                    'success': False,
                    'error': 'API key eksik',
                    'message': 'Lütfen Apollo.io API key\'inizi ayarlar bölümünden girin.'
                }
            
            return self.apollo_manager.test_api_connection()
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Apollo.io API test hatası.'
            }
    
    def get_apollo_usage_stats(self) -> Dict:
        """Apollo.io kullanım istatistiklerini al"""
        try:
            if not self.apollo_manager:
                return {
                    'success': False,
                    'error': 'API key eksik',
                    'message': 'Apollo.io API key gerekli.'
                }
            
            return self.apollo_manager.get_api_usage_stats()
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Apollo.io kullanım istatistikleri alınamadı.'
            }