#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApolloManager:
    """Apollo.io API işlemlerini yöneten sınıf"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.apollo.io/api/v1"
        self.headers = {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }
        
    def update_api_key(self, api_key: str):
        """API key'i güncelle"""
        self.api_key = api_key
        
    def _make_request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """Apollo.io API'ye istek gönder"""
        if not self.api_key:
            raise ValueError("Apollo.io API key eksik!")
            
        url = f"{self.base_url}{endpoint}"
        
        # Add API key to headers
        headers = self.headers.copy()
        headers['X-Api-Key'] = self.api_key
        
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=params)
        else:
            # Debug: Print request data
            logger.debug(f"Apollo API Request: {endpoint}")
            logger.debug(f"Request data: {data}")
            
            response = requests.post(url, headers=headers, json=data)
        
        # Better error handling
        if response.status_code == 422:
            logger.error(f"Apollo API 422 Error: {response.text}")
            logger.error(f"Request data that caused error: {data}")
            raise requests.exceptions.HTTPError(f"422 Client Error: Unprocessable Entity - {response.text}")
        
        response.raise_for_status()
        return response.json()
    
    # ========== PEOPLE SEARCH BÖLÜMÜ ==========
    
    def search_people(self, 
                     person_titles: List[str] = None,
                     q_organization_domains: List[str] = None,
                     organization_locations: List[str] = None,
                     person_locations: List[str] = None,
                     page: int = 1,
                     per_page: int = 25,
                     sort_by_field: str = None,
                     sort_ascending: bool = True) -> Dict:
        """
        Apollo.io People Search API'sini kullanarak kişi arama
        
        Args:
            person_titles: Aranacak pozisyonlar (örn: ['CEO', 'CTO', 'Marketing Manager'])
            q_organization_domains: Firma domainleri (örn: ['google.com', 'microsoft.com'])
            organization_locations: Firma lokasyonları (örn: ['Istanbul, Turkey'])
            person_locations: Kişi lokasyonları (örn: ['Istanbul, Turkey'])
            page: Sayfa numarası (1'den başlar)
            per_page: Sayfa başına sonuç (max 25)
            sort_by_field: Sıralama alanı
            sort_ascending: Artan sıralama (True/False)
            
        Returns:
            API yanıtı dict formatında
        """
        try:
            data = {
                'page': page,
                'per_page': per_page
            }
            
            if person_titles:
                data['person_titles'] = person_titles
            if q_organization_domains:
                data['q_organization_domains'] = q_organization_domains
            if organization_locations:
                data['organization_locations'] = organization_locations
            if person_locations:
                data['person_locations'] = person_locations
            if sort_by_field:
                data['sort_by_field'] = sort_by_field
            if sort_ascending is not None:
                data['sort_ascending'] = sort_ascending
                
            result = self._make_request('POST', '/mixed_people/search', data=data)
            
            logger.info(f"Apollo.io People Search: {len(result.get('people', []))} kişi bulundu")
            return result
            
        except Exception as e:
            logger.error(f"Apollo.io People Search hatası: {str(e)}")
            raise
    
    def search_people_by_company(self, company_domain: str, 
                                titles: List[str] = None,
                                location: str = None,
                                max_results: int = 50) -> List[Dict]:
        """
        Belirli bir şirket için kişi arama (kolay kullanım için)
        
        Args:
            company_domain: Şirket domaini (örn: 'google.com')
            titles: Aranacak pozisyonlar (varsayılan: ['CEO', 'CTO', 'CFO', 'Marketing Manager'])
            location: Lokasyon (örn: 'Istanbul, Turkey')
            max_results: Maksimum sonuç sayısı
            
        Returns:
            Kişi listesi
        """
        if not titles:
            titles = ['CEO', 'CTO', 'CFO', 'Marketing Manager', 'Sales Manager', 'Founder']
        
        all_people = []
        page = 1
        per_page = min(25, max_results)
        
        while len(all_people) < max_results:
            try:
                # Parameter validation
                if not company_domain or not company_domain.strip():
                    logger.warning("Company domain is empty or invalid")
                    break
                
                # Clean domain
                domain = company_domain.strip().lower()
                if not domain.startswith(('http://', 'https://')):
                    domain = f"https://{domain}"
                
                # Extract domain from URL
                from urllib.parse import urlparse
                parsed = urlparse(domain)
                clean_domain = parsed.netloc or parsed.path
                
                if not clean_domain:
                    logger.warning(f"Could not extract domain from: {company_domain}")
                    break
                
                data = {
                    'q_organization_domains': [clean_domain],
                    'page': page,
                    'per_page': per_page
                }
                
                # Only add titles if they exist and are valid
                if titles and isinstance(titles, list) and len(titles) > 0:
                    data['person_titles'] = [str(title).strip() for title in titles if title and str(title).strip()]
                
                # Only add location if it exists and is valid
                if location and str(location).strip():
                    data['person_locations'] = [str(location).strip()]
                
                result = self._make_request('POST', '/mixed_people/search', data=data)
                people = result.get('people', [])
                
                if not people:
                    break
                    
                all_people.extend(people)
                page += 1
                
                # Rate limiting için kısa bekleme
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Sayfa {page} arama hatası: {str(e)}")
                break
        
        return all_people[:max_results]
    
    def search_people_by_industry(self, industry: str, 
                                 location: str = None,
                                 titles: List[str] = None,
                                 max_results: int = 50) -> List[Dict]:
        """
        Sektöre göre kişi arama
        
        Args:
            industry: Sektör adı (örn: 'Technology', 'Healthcare')
            location: Lokasyon (örn: 'Istanbul, Turkey')
            titles: Aranacak pozisyonlar
            max_results: Maksimum sonuç sayısı
            
        Returns:
            Kişi listesi
        """
        if not titles:
            titles = ['CEO', 'CTO', 'CFO', 'Marketing Manager', 'Sales Manager']
        
        all_people = []
        page = 1
        per_page = min(25, max_results)
        
        while len(all_people) < max_results:
            try:
                data = {
                    'person_titles': titles,
                    'page': page,
                    'per_page': per_page
                }
                
                if location:
                    data['person_locations'] = [location]
                
                # Industry için genel arama
                data['q_organization_domains'] = [f"{industry.lower()}.com"]
                
                result = self._make_request('POST', '/mixed_people/search', data=data)
                people = result.get('people', [])
                
                if not people:
                    break
                    
                all_people.extend(people)
                page += 1
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Sektör arama hatası: {str(e)}")
                break
        
        return all_people[:max_results]
    
    # ========== ORGANIZATION SEARCH BÖLÜMÜ ==========
    
    def search_organizations(self,
                           q_organization_domains: List[str] = None,
                           organization_locations: List[str] = None,
                           organization_num_employees_ranges: List[str] = None,
                           organization_industry_tag_ids: List[str] = None,
                           page: int = 1,
                           per_page: int = 25) -> Dict:
        """
        Apollo.io Organization Search API'sini kullanarak organizasyon arama
        
        Args:
            q_organization_domains: Firma domainleri
            organization_locations: Firma lokasyonları
            organization_num_employees_ranges: Çalışan sayısı aralıkları
            organization_industry_tag_ids: Sektör ID'leri
            page: Sayfa numarası
            per_page: Sayfa başına sonuç
            
        Returns:
            API yanıtı dict formatında
        """
        try:
            data = {
                'page': page,
                'per_page': per_page
            }
            
            if q_organization_domains:
                data['q_organization_domains'] = q_organization_domains
            if organization_locations:
                data['organization_locations'] = organization_locations
            if organization_num_employees_ranges:
                data['organization_num_employees_ranges'] = organization_num_employees_ranges
            if organization_industry_tag_ids:
                data['organization_industry_tag_ids'] = organization_industry_tag_ids
                
            result = self._make_request('POST', '/mixed_people/search', data=data)
            
            logger.info(f"Apollo.io Organization Search: {len(result.get('organizations', []))} organizasyon bulundu")
            return result
            
        except Exception as e:
            logger.error(f"Apollo.io Organization Search hatası: {str(e)}")
            raise
    
    def search_companies_by_location(self, location: str, 
                                   industry: str = None,
                                   employee_range: str = None,
                                   max_results: int = 50) -> List[Dict]:
        """
        Lokasyona göre şirket arama
        
        Args:
            location: Lokasyon (örn: 'Istanbul, Turkey')
            industry: Sektör (opsiyonel)
            employee_range: Çalışan sayısı aralığı (örn: '1,10' veya '11,50')
            max_results: Maksimum sonuç sayısı
            
        Returns:
            Şirket listesi
        """
        all_organizations = []
        page = 1
        per_page = min(25, max_results)
        
        while len(all_organizations) < max_results:
            try:
                data = {
                    'organization_locations': [location],
                    'page': page,
                    'per_page': per_page
                }
                
                if industry:
                    # Industry için domain arama
                    data['q_organization_domains'] = [f"{industry.lower()}.com"]
                
                if employee_range:
                    data['organization_num_employees_ranges'] = [employee_range]
                
                result = self._make_request('POST', '/mixed_people/search', data=data)
                organizations = result.get('organizations', [])
                
                if not organizations:
                    break
                    
                all_organizations.extend(organizations)
                page += 1
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Şirket arama hatası: {str(e)}")
                break
        
        return all_organizations[:max_results]
    
    # ========== DATA PROCESSING BÖLÜMÜ ==========
    
    def process_people_data(self, people_data: List[Dict]) -> List[Dict]:
        """
        Apollo.io'dan gelen kişi verilerini işle ve standart formata çevir
        
        Args:
            people_data: Apollo.io'dan gelen ham kişi verileri
            
        Returns:
            İşlenmiş kişi listesi
        """
        processed_people = []
        
        for person in people_data:
            try:
                processed_person = {
                    'id': person.get('id'),
                    'first_name': person.get('first_name', ''),
                    'last_name': person.get('last_name', ''),
                    'full_name': f"{person.get('first_name', '')} {person.get('last_name', '')}".strip(),
                    'title': person.get('title', ''),
                    'email': person.get('email', ''),
                    'phone_numbers': person.get('phone_numbers', []),
                    'linkedin_url': person.get('linkedin_url', ''),
                    'twitter_url': person.get('twitter_url', ''),
                    'facebook_url': person.get('facebook_url', ''),
                    'github_url': person.get('github_url', ''),
                    'organization': {
                        'id': person.get('organization', {}).get('id'),
                        'name': person.get('organization', {}).get('name', ''),
                        'domain': person.get('organization', {}).get('primary_domain', ''),
                        'website_url': person.get('organization', {}).get('website_url', ''),
                        'industry': person.get('organization', {}).get('industry', ''),
                        'employee_count': person.get('organization', {}).get('estimated_num_employees', 0),
                        'location': person.get('organization', {}).get('city', '') + ', ' + person.get('organization', {}).get('state', ''),
                        'linkedin_url': person.get('organization', {}).get('linkedin_url', ''),
                        'twitter_url': person.get('organization', {}).get('twitter_url', ''),
                        'facebook_url': person.get('organization', {}).get('facebook_url', '')
                    },
                    'city': person.get('city', ''),
                    'state': person.get('state', ''),
                    'country': person.get('country', ''),
                    'location': f"{person.get('city', '')}, {person.get('state', '')}, {person.get('country', '')}".strip(', '),
                    'photo_url': person.get('photo_url', ''),
                    'headline': person.get('headline', ''),
                    'employment_history': person.get('employment_history', []),
                    'education': person.get('education', []),
                    'source': 'apollo.io',
                    'last_updated': datetime.now().isoformat()
                }
                
                # Telefon numarasını formatla
                if processed_person['phone_numbers']:
                    primary_phone = processed_person['phone_numbers'][0].get('raw_number', '')
                    processed_person['phone'] = primary_phone
                    processed_person['whatsapp_number'] = self._format_whatsapp_number(primary_phone)
                else:
                    processed_person['phone'] = ''
                    processed_person['whatsapp_number'] = ''
                
                processed_people.append(processed_person)
                
            except Exception as e:
                logger.error(f"Kişi verisi işleme hatası: {str(e)}")
                continue
        
        return processed_people
    
    def process_organization_data(self, org_data: List[Dict]) -> List[Dict]:
        """
        Apollo.io'dan gelen organizasyon verilerini işle
        
        Args:
            org_data: Apollo.io'dan gelen ham organizasyon verileri
            
        Returns:
            İşlenmiş organizasyon listesi
        """
        processed_orgs = []
        
        for org in org_data:
            try:
                processed_org = {
                    'id': org.get('id'),
                    'name': org.get('name', ''),
                    'domain': org.get('primary_domain', ''),
                    'website_url': org.get('website_url', ''),
                    'industry': org.get('industry', ''),
                    'employee_count': org.get('estimated_num_employees', 0),
                    'location': f"{org.get('city', '')}, {org.get('state', '')}, {org.get('country', '')}".strip(', '),
                    'city': org.get('city', ''),
                    'state': org.get('state', ''),
                    'country': org.get('country', ''),
                    'linkedin_url': org.get('linkedin_url', ''),
                    'twitter_url': org.get('twitter_url', ''),
                    'facebook_url': org.get('facebook_url', ''),
                    'description': org.get('short_description', ''),
                    'founded_year': org.get('founded_year'),
                    'annual_revenue': org.get('annual_revenue'),
                    'keywords': org.get('keywords', []),
                    'phone': org.get('phone', ''),
                    'whatsapp_number': self._format_whatsapp_number(org.get('phone', '')),
                    'source': 'apollo.io',
                    'last_updated': datetime.now().isoformat()
                }
                
                processed_orgs.append(processed_org)
                
            except Exception as e:
                logger.error(f"Organizasyon verisi işleme hatası: {str(e)}")
                continue
        
        return processed_orgs
    
    def _format_whatsapp_number(self, phone: str) -> str:
        """Telefon numarasını WhatsApp formatına dönüştür"""
        if not phone:
            return ''
            
        import re
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
    
    # ========== TEST FONKSİYONLARI ==========
    
    def test_api_connection(self) -> Dict:
        """Apollo.io API bağlantısını test et"""
        try:
            if not self.api_key:
                return {
                    'success': False,
                    'error': 'API key eksik',
                    'message': 'Lütfen Apollo.io API key\'inizi girin.'
                }
            
            # Basit bir arama yaparak API'yi test et
            test_data = {
                'person_titles': ['CEO'],
                'page': 1,
                'per_page': 1
            }
            
            result = self._make_request('POST', '/mixed_people/search', data=test_data)
            
            return {
                'success': True,
                'message': 'Apollo.io API bağlantısı başarılı!',
                'api_key_preview': self.api_key[:10] + '...',
                'test_result': f"{len(result.get('people', []))} kişi bulundu"
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Kimlik doğrulama hatası',
                    'message': 'API key geçersiz. Lütfen kontrol edin.'
                }
            elif e.response.status_code == 429:
                return {
                    'success': False,
                    'error': 'Rate limit',
                    'message': 'API kullanım limitiniz dolmuş.'
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {e.response.status_code}',
                    'message': f'API hatası: {e.response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Apollo.io API bağlantı hatası.'
            }
    
    def get_api_usage_stats(self) -> Dict:
        """API kullanım istatistiklerini al"""
        try:
            # Apollo.io'da usage stats endpoint'i yoksa basit bir test yap
            result = self.test_api_connection()
            return {
                'success': result['success'],
                'message': result['message'],
                'api_key': self.api_key[:10] + '...' if self.api_key else 'Yok'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Kullanım istatistikleri alınamadı.'
            }
