#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import random
import os
import re
import logging

try:
    import pandas as pd
    import openpyxl
except ImportError:
    pd = None
    print("Pandas/openpyxl kurulu değil. Excel işlemleri çalışmayacak.")

try:
    from faker import Faker
except ImportError:
    Faker = None
    print("Faker kurulu değil. Test firma oluşturma sınırlı olacak.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """Veri import/export ve test firma oluşturma yöneticisi - WhatsApp destekli"""
    
    def __init__(self):
        self.faker = Faker('tr_TR') if Faker else None
        
    def import_firms(self, file_path, file_type):
        """Firmaları dosyadan içe aktar - WhatsApp numaraları dahil"""
        try:
            if file_type == "CSV":
                return self._import_csv(file_path)
            elif file_type == "Excel":
                return self._import_excel(file_path)
            elif file_type == "XML":
                return self._import_xml(file_path)
            elif file_type == "JSON":
                return self._import_json(file_path)
            else:
                return {"imported_count": 0, "errors": ["Desteklenmeyen dosya formatı"]}
        except Exception as e:
            return {"imported_count": 0, "errors": [str(e)]}
    
    def _import_csv(self, file_path):
        """CSV dosyasından import"""
        firms = []
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        firm = self._parse_firm_data(row)
                        firms.append(firm)
                    except Exception as e:
                        errors.append(f"Satır hatası: {str(e)}")
        except Exception as e:
            errors.append(f"CSV okuma hatası: {str(e)}")
        
        return {"imported_count": len(firms), "firms": firms, "errors": errors}
    
    def _import_excel(self, file_path):
        """Excel dosyasından import"""
        if not pd:
            return {"imported_count": 0, "errors": ["Pandas kurulu değil"]}
        
        firms = []
        errors = []
        
        try:
            df = pd.read_excel(file_path)
            for index, row in df.iterrows():
                try:
                    firm = self._parse_firm_data(row.to_dict())
                    firms.append(firm)
                except Exception as e:
                    errors.append(f"Satır {index} hatası: {str(e)}")
        except Exception as e:
            errors.append(f"Excel okuma hatası: {str(e)}")
        
        return {"imported_count": len(firms), "firms": firms, "errors": errors}
    
    def _import_xml(self, file_path):
        """XML dosyasından import"""
        firms = []
        errors = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            for firm_elem in root.findall('.//firm'):
                try:
                    firm_data = {}
                    for child in firm_elem:
                        firm_data[child.tag] = child.text
                    
                    firm = self._parse_firm_data(firm_data)
                    firms.append(firm)
                except Exception as e:
                    errors.append(f"XML firma hatası: {str(e)}")
        except Exception as e:
            errors.append(f"XML okuma hatası: {str(e)}")
        
        return {"imported_count": len(firms), "firms": firms, "errors": errors}
    
    def _import_json(self, file_path):
        """JSON dosyasından import"""
        firms = []
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                if isinstance(data, list):
                    for item in data:
                        try:
                            firm = self._parse_firm_data(item)
                            firms.append(firm)
                        except Exception as e:
                            errors.append(f"JSON item hatası: {str(e)}")
                else:
                    errors.append("JSON formatı hatalı (liste bekleniyor)")
        except Exception as e:
            errors.append(f"JSON okuma hatası: {str(e)}")
        
        return {"imported_count": len(firms), "firms": firms, "errors": errors}
    
    def _parse_firm_data(self, data):
        """Ham veriyi firma formatına dönüştür - WhatsApp desteği ile"""
        # ID oluştur
        firm_id = data.get('id') or f"imported_{datetime.now().timestamp()}_{random.randint(1000, 9999)}"
        
        # Email listesini parse et
        emails = []
        if 'emails' in data:
            if isinstance(data['emails'], str):
                # Virgülle ayrılmış email listesi
                for email in data['emails'].split(','):
                    email = email.strip()
                    if email:
                        emails.append({
                            'email': email,
                            'score': 85,
                            'source': 'import',
                            'is_verified': False
                        })
            elif isinstance(data['emails'], list):
                emails = data['emails']
        
        # Telefon numarasını formatla
        phone = data.get('phone') or data.get('Telefon') or data.get('whatsapp') or ''
        whatsapp_formatted = self.format_whatsapp_number(phone) if phone else ''
        
        # WhatsApp kampanya geçmişi
        whatsapp_history = data.get('whatsapp_history', {})
        if isinstance(whatsapp_history, str) and whatsapp_history:
            try:
                whatsapp_history = json.loads(whatsapp_history)
            except:
                whatsapp_history = {}
        
        # Firma objesi oluştur
        firm = {
            'id': firm_id,
            'name': data.get('name') or data.get('Firma Adı') or 'Bilinmeyen Firma',
            'rating': float(data.get('rating', data.get('Rating', 0)) or 0),
            'phone': phone,
            'whatsapp_number': whatsapp_formatted,
            'whatsapp_verified': data.get('whatsapp_verified', False),
            'whatsapp_opt_in': data.get('whatsapp_opt_in', False),
            'whatsapp_last_contacted': data.get('whatsapp_last_contacted'),
            'whatsapp_response_rate': data.get('whatsapp_response_rate', 0),
            'whatsapp_history': whatsapp_history,
            'website': data.get('website') or data.get('Website') or '',
            'address': data.get('address') or data.get('Adres') or '',
            'lat': data.get('lat', 0.0),
            'lng': data.get('lng', 0.0),
            'emails': emails,
            'is_analyzed': bool(emails),
            'email_count': len(emails),
            'import_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'import',
            'contact_person': data.get('contact_person', ''),
            'contact_position': data.get('contact_position', ''),
            'preferred_contact_method': data.get('preferred_contact_method', 'whatsapp'),
            'tags': data.get('tags', []),
            'notes': data.get('notes', '')
        }
        
        return firm
    
    def format_whatsapp_number(self, phone):
        """Telefon numarasını WhatsApp formatına dönüştür"""
        # Sadece rakamları al
        phone = re.sub(r'\D', '', str(phone))
        
        # Türkiye için düzenleme
        if phone.startswith('0'):
            phone = phone[1:]
        
        if phone.startswith('5') and len(phone) == 10:
            phone = '90' + phone
        
        if not phone.startswith('90') and len(phone) == 10:
            phone = '90' + phone
        
        # + işareti ekle
        if not phone.startswith('+'):
            phone = '+' + phone
        
        return phone
    
    def export_firms(self, firms, file_path, file_type, include_whatsapp_data=True):
        """Firmaları dosyaya aktar - WhatsApp verileri dahil"""
        try:
            if file_type == "CSV":
                return self._export_csv(firms, file_path, include_whatsapp_data)
            elif file_type == "Excel":
                return self._export_excel(firms, file_path, include_whatsapp_data)
            elif file_type == "XML":
                return self._export_xml(firms, file_path, include_whatsapp_data)
            elif file_type == "JSON":
                return self._export_json(firms, file_path, include_whatsapp_data)
            else:
                return {"exported_count": 0, "error": "Desteklenmeyen dosya formatı"}
        except Exception as e:
            return {"exported_count": 0, "error": str(e)}
    
    def _export_csv(self, firms, file_path, include_whatsapp_data=True):
        """CSV'ye export - WhatsApp verileri ile"""
        try:
            fieldnames = [
                'Firma Adı', 'Rating', 'Telefon', 'WhatsApp Numarası', 
                'Website', 'Adres', 'Email Sayısı', 'Email Listesi', 
                'Analiz Durumu', 'Yetkili Kişi', 'Pozisyon'
            ]
            
            if include_whatsapp_data:
                fieldnames.extend([
                    'WhatsApp Doğrulanmış', 'WhatsApp Opt-in', 
                    'Son WhatsApp İletişimi', 'WhatsApp Yanıt Oranı',
                    'Tercih Edilen İletişim'
                ])
            
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                writer.writeheader()
                for firm in firms:
                    email_list = ', '.join([e['email'] for e in firm.get('emails', [])])
                    row = {
                        'Firma Adı': firm['name'],
                        'Rating': firm.get('rating', ''),
                        'Telefon': firm.get('phone', ''),
                        'WhatsApp Numarası': firm.get('whatsapp_number', ''),
                        'Website': firm.get('website', ''),
                        'Adres': firm.get('address', ''),
                        'Email Sayısı': firm.get('email_count', 0),
                        'Email Listesi': email_list,
                        'Analiz Durumu': 'Evet' if firm.get('is_analyzed') else 'Hayır',
                        'Yetkili Kişi': firm.get('contact_person', ''),
                        'Pozisyon': firm.get('contact_position', '')
                    }
                    
                    if include_whatsapp_data:
                        row.update({
                            'WhatsApp Doğrulanmış': 'Evet' if firm.get('whatsapp_verified') else 'Hayır',
                            'WhatsApp Opt-in': 'Evet' if firm.get('whatsapp_opt_in') else 'Hayır',
                            'Son WhatsApp İletişimi': firm.get('whatsapp_last_contacted', ''),
                            'WhatsApp Yanıt Oranı': f"{firm.get('whatsapp_response_rate', 0)}%",
                            'Tercih Edilen İletişim': firm.get('preferred_contact_method', '')
                        })
                    
                    writer.writerow(row)
            
            return {"exported_count": len(firms)}
        except Exception as e:
            return {"exported_count": 0, "error": str(e)}
    
    def _export_excel(self, firms, file_path, include_whatsapp_data=True):
        """Excel'e export - WhatsApp verileri ile"""
        if not pd:
            return {"exported_count": 0, "error": "Pandas kurulu değil"}
        
        try:
            data = []
            for firm in firms:
                email_list = ', '.join([e['email'] for e in firm.get('emails', [])])
                row = {
                    'Firma Adı': firm['name'],
                    'Rating': firm.get('rating', ''),
                    'Telefon': firm.get('phone', ''),
                    'WhatsApp Numarası': firm.get('whatsapp_number', ''),
                    'Website': firm.get('website', ''),
                    'Adres': firm.get('address', ''),
                    'Email Sayısı': firm.get('email_count', 0),
                    'Email Listesi': email_list,
                    'Analiz Durumu': 'Evet' if firm.get('is_analyzed') else 'Hayır',
                    'Yetkili Kişi': firm.get('contact_person', ''),
                    'Pozisyon': firm.get('contact_position', '')
                }
                
                if include_whatsapp_data:
                    row.update({
                        'WhatsApp Doğrulanmış': 'Evet' if firm.get('whatsapp_verified') else 'Hayır',
                        'WhatsApp Opt-in': 'Evet' if firm.get('whatsapp_opt_in') else 'Hayır',
                        'Son WhatsApp İletişimi': firm.get('whatsapp_last_contacted', ''),
                        'WhatsApp Yanıt Oranı': f"{firm.get('whatsapp_response_rate', 0)}%",
                        'Tercih Edilen İletişim': firm.get('preferred_contact_method', ''),
                        'Notlar': firm.get('notes', '')
                    })
                
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            return {"exported_count": len(firms)}
        except Exception as e:
            return {"exported_count": 0, "error": str(e)}
    
    def _export_xml(self, firms, file_path, include_whatsapp_data=True):
        """XML'e export - WhatsApp verileri ile"""
        try:
            root = ET.Element("firms")
            
            for firm in firms:
                firm_elem = ET.SubElement(root, "firm")
                
                ET.SubElement(firm_elem, "id").text = str(firm['id'])
                ET.SubElement(firm_elem, "name").text = firm['name']
                ET.SubElement(firm_elem, "rating").text = str(firm.get('rating', ''))
                ET.SubElement(firm_elem, "phone").text = firm.get('phone', '')
                ET.SubElement(firm_elem, "whatsapp_number").text = firm.get('whatsapp_number', '')
                ET.SubElement(firm_elem, "website").text = firm.get('website', '')
                ET.SubElement(firm_elem, "address").text = firm.get('address', '')
                
                if include_whatsapp_data:
                    whatsapp_elem = ET.SubElement(firm_elem, "whatsapp_data")
                    ET.SubElement(whatsapp_elem, "verified").text = str(firm.get('whatsapp_verified', False))
                    ET.SubElement(whatsapp_elem, "opt_in").text = str(firm.get('whatsapp_opt_in', False))
                    ET.SubElement(whatsapp_elem, "last_contacted").text = firm.get('whatsapp_last_contacted', '')
                    ET.SubElement(whatsapp_elem, "response_rate").text = str(firm.get('whatsapp_response_rate', 0))
                    ET.SubElement(whatsapp_elem, "preferred_method").text = firm.get('preferred_contact_method', '')
                
                emails_elem = ET.SubElement(firm_elem, "emails")
                for email in firm.get('emails', []):
                    email_elem = ET.SubElement(emails_elem, "email")
                    email_elem.text = email['email']
                
                # Contact info
                contact_elem = ET.SubElement(firm_elem, "contact")
                ET.SubElement(contact_elem, "person").text = firm.get('contact_person', '')
                ET.SubElement(contact_elem, "position").text = firm.get('contact_position', '')
            
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            return {"exported_count": len(firms)}
        except Exception as e:
            return {"exported_count": 0, "error": str(e)}
    
    def _export_json(self, firms, file_path, include_whatsapp_data=True):
        """JSON'a export - WhatsApp verileri ile"""
        try:
            export_data = []
            for firm in firms:
                if not include_whatsapp_data:
                    # WhatsApp verilerini çıkar
                    firm_copy = firm.copy()
                    whatsapp_fields = [
                        'whatsapp_number', 'whatsapp_verified', 'whatsapp_opt_in',
                        'whatsapp_last_contacted', 'whatsapp_response_rate', 'whatsapp_history'
                    ]
                    for field in whatsapp_fields:
                        firm_copy.pop(field, None)
                    export_data.append(firm_copy)
                else:
                    export_data.append(firm)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, ensure_ascii=False, indent=2)
            
            return {"exported_count": len(firms)}
        except Exception as e:
            return {"exported_count": 0, "error": str(e)}
    
    def create_import_template(self, file_path, file_type):
        """Import için örnek şablon oluştur - WhatsApp alanları dahil"""
        sample_data = [
            {
                'Firma Adı': 'Örnek Firma 1',
                'Rating': '4.5',
                'Telefon': '+90 555 123 4567',
                'WhatsApp Numarası': '+905551234567',
                'Website': 'www.ornekfirma1.com',
                'Adres': 'İstanbul, Türkiye',
                'Email Listesi': 'info@ornekfirma1.com, destek@ornekfirma1.com',
                'Yetkili Kişi': 'Ahmet Yılmaz',
                'Pozisyon': 'Genel Müdür',
                'WhatsApp Doğrulanmış': 'Evet',
                'WhatsApp Opt-in': 'Evet',
                'Tercih Edilen İletişim': 'whatsapp'
            },
            {
                'Firma Adı': 'Örnek Firma 2',
                'Rating': '4.8',
                'Telefon': '+90 555 987 6543',
                'WhatsApp Numarası': '+905559876543',
                'Website': 'www.ornekfirma2.com',
                'Adres': 'Ankara, Türkiye',
                'Email Listesi': 'iletisim@ornekfirma2.com',
                'Yetkili Kişi': 'Ayşe Demir',
                'Pozisyon': 'Satış Müdürü',
                'WhatsApp Doğrulanmış': 'Hayır',
                'WhatsApp Opt-in': 'Hayır',
                'Tercih Edilen İletişim': 'email'
            }
        ]
        
        if file_type == "CSV":
            return self._create_csv_template(file_path, sample_data)
        elif file_type == "Excel":
            return self._create_excel_template(file_path, sample_data)
        elif file_type == "XML":
            return self._create_xml_template(file_path)
        elif file_type == "JSON":
            return self._create_json_template(file_path)
        
        return False
    
    def _create_csv_template(self, file_path, sample_data):
        """CSV şablon oluştur"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = list(sample_data[0].keys())
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sample_data)
            return True
        except:
            return False
    
    def _create_excel_template(self, file_path, sample_data):
        """Excel şablon oluştur"""
        if not pd:
            return False
        
        try:
            df = pd.DataFrame(sample_data)
            df.to_excel(file_path, index=False)
            return True
        except:
            return False
    
    def _create_xml_template(self, file_path):
        """XML şablon oluştur"""
        try:
            root = ET.Element("firms")
            
            # Örnek firma 1
            firm1 = ET.SubElement(root, "firm")
            ET.SubElement(firm1, "name").text = "Örnek Firma 1"
            ET.SubElement(firm1, "rating").text = "4.5"
            ET.SubElement(firm1, "phone").text = "+90 555 123 4567"
            ET.SubElement(firm1, "whatsapp_number").text = "+905551234567"
            ET.SubElement(firm1, "website").text = "www.ornekfirma1.com"
            ET.SubElement(firm1, "address").text = "İstanbul, Türkiye"
            ET.SubElement(firm1, "emails").text = "info@ornekfirma1.com, destek@ornekfirma1.com"
            
            whatsapp1 = ET.SubElement(firm1, "whatsapp_data")
            ET.SubElement(whatsapp1, "verified").text = "True"
            ET.SubElement(whatsapp1, "opt_in").text = "True"
            
            contact1 = ET.SubElement(firm1, "contact")
            ET.SubElement(contact1, "person").text = "Ahmet Yılmaz"
            ET.SubElement(contact1, "position").text = "Genel Müdür"
            
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
            return True
        except:
            return False
    
    def _create_json_template(self, file_path):
        """JSON şablon oluştur"""
        try:
            sample = [
                {
                    "name": "Örnek Firma 1",
                    "rating": 4.5,
                    "phone": "+90 555 123 4567",
                    "whatsapp_number": "+905551234567",
                    "website": "www.ornekfirma1.com",
                    "address": "İstanbul, Türkiye",
                    "emails": "info@ornekfirma1.com, destek@ornekfirma1.com",
                    "contact_person": "Ahmet Yılmaz",
                    "contact_position": "Genel Müdür",
                    "whatsapp_verified": True,
                    "whatsapp_opt_in": True,
                    "preferred_contact_method": "whatsapp"
                },
                {
                    "name": "Örnek Firma 2",
                    "rating": 4.8,
                    "phone": "+90 555 987 6543",
                    "whatsapp_number": "+905559876543",
                    "website": "www.ornekfirma2.com",
                    "address": "Ankara, Türkiye",
                    "emails": "iletisim@ornekfirma2.com",
                    "contact_person": "Ayşe Demir",
                    "contact_position": "Satış Müdürü",
                    "whatsapp_verified": False,
                    "whatsapp_opt_in": False,
                    "preferred_contact_method": "email"
                }
            ]
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(sample, file, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def generate_test_firms(self, count=1, sector='mixed', options=None):
        """Test firmaları oluştur - WhatsApp destekli"""
        firms = []
        
        # WhatsApp mesaj şablonları
        whatsapp_templates = [
            "Merhaba {{name}}, ürünlerimiz hakkında bilgi almak ister misiniz?",
            "{{name}} ekibi, yeni çözümlerimizi keşfedin!",
            "Özel teklifimizden yararlanmak için bizimle iletişime geçin.",
            "{{name}} için hazırladığımız kampanyadan haberdar mısınız?"
        ]
        
        for i in range(min(count, 10)):  # Maksimum 10 test firma
            if self.faker:
                # Faker ile gerçekçi veri
                company_name = self.faker.company()
                person_name = self.faker.name()
                phone = self.faker.phone_number()
                address = self.faker.address()
            else:
                # Manuel test verileri
                company_name = f'Test Firması {i+1}'
                person_name = f'Test Kişi {i+1}'
                phone = f'+9055512345{67+i:02d}'
                address = f'Test Sokak No:{i+1}, İstanbul'
            
            # WhatsApp numarasını formatla
            whatsapp = self.format_whatsapp_number(phone)
            
            # Test firması oluştur
            test_firm = {
                'id': f'test_firm_{datetime.now().timestamp()}_{i}',
                'name': company_name,
                'rating': round(random.uniform(3.5, 5.0), 1),
                'review_count': random.randint(10, 500),
                'phone': phone,
                'whatsapp_number': whatsapp,
                'whatsapp_verified': random.choice([True, False]),
                'whatsapp_opt_in': random.choice([True, False]),
                'whatsapp_last_contacted': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S') if random.choice([True, False]) else None,
                'whatsapp_response_rate': random.randint(0, 100),
                'whatsapp_history': {
                    'messages_sent': random.randint(0, 20),
                    'messages_received': random.randint(0, 15),
                    'last_template': random.choice(whatsapp_templates),
                    'campaigns_included': random.randint(0, 5)
                },
                'website': f'www.{company_name.lower().replace(" ", "").replace(",", "").replace(".", "")}.com',
                'address': address,
                'google_maps_url': 'https://maps.google.com/test',
                'lat': 40.9876 + random.uniform(-0.1, 0.1),
                'lng': 29.0246 + random.uniform(-0.1, 0.1),
                'is_open': random.choice([True, False]),
                'photos': [],
                'types': self._get_random_types(sector),
                'emails': self._generate_test_emails(company_name, random.randint(1, 3)),
                'is_analyzed': True,
                'email_count': random.randint(1, 3),
                'popularity_score': random.randint(50, 100),
                'scraped_data': {},
                'ai_summary': f'Test firması - {sector} sektöründe faaliyet gösteriyor',
                'technologies': ['WordPress', 'Google Analytics', 'WhatsApp Business'],
                'services': ['Test Hizmeti', 'Demo Hizmeti', 'WhatsApp Destek'],
                'team_size': random.choice(['1-10', '10-50', '50-100']),
                'industry_keywords': ['test', 'demo', sector.lower()],
                'contact_person': person_name,
                'contact_position': random.choice(['Genel Müdür', 'Satış Müdürü', 'Pazarlama Müdürü', 'İK Müdürü']),
                'preferred_contact_method': random.choice(['whatsapp', 'email', 'phone']),
                'tags': self._get_random_tags(),
                'notes': f'Test notu - {datetime.now().strftime("%Y-%m-%d")}',
                'last_scraped': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'test_generator'
            }
            
            firms.append(test_firm)
        
        # Eğer sadece 1 firma isteniyorsa, sabit email'li test firması ekle
        if count == 1:
            firms[0]['emails'] = [
                {
                    'email': 'ceteibrahim5@gmail.com',
                    'position': 'Genel',
                    'score': 95,
                    'source': 'test',
                    'is_verified': True
                }
            ]
            firms[0]['whatsapp_number'] = '+905462051820'  # Sabit test numarası
        
        return firms
    
    def _get_random_types(self, sector):
        """Sektöre göre rastgele tipler"""
        sector_types = {
            'teknoloji': ['yazılım', 'donanım', 'IT hizmetleri', 'web geliştirme'],
            'sağlık': ['hastane', 'klinik', 'eczane', 'medikal cihazlar'],
            'eğitim': ['okul', 'kurs', 'eğitim danışmanlığı', 'online eğitim'],
            'perakende': ['mağaza', 'market', 'online satış', 'toptan satış'],
            'hizmet': ['danışmanlık', 'temizlik', 'güvenlik', 'lojistik'],
            'mixed': ['genel', 'çeşitli', 'hizmet', 'ticaret']
        }
        
        types = sector_types.get(sector.lower(), sector_types['mixed'])
        return random.sample(types, min(2, len(types)))
    
    def _generate_test_emails(self, company_name, count):
        """Test emailler oluştur"""
        emails = []
        domain = company_name.lower().replace(' ', '').replace(',', '').replace('.', '') + '.com'
        
        prefixes = ['info', 'contact', 'sales', 'destek', 'hello', 'admin']
        positions = ['Genel', 'Satış', 'Destek', 'Yönetim']
        
        for i in range(count):
            emails.append({
                'email': f'{random.choice(prefixes)}@{domain}',
                'position': random.choice(positions),
                'score': random.randint(60, 95),
                'source': 'test',
                'is_verified': random.choice([True, False])
            })
        
        return emails
    
    def _get_random_tags(self):
        """Rastgele etiketler oluştur"""
        all_tags = [
            'potansiyel', 'önemli', 'takip', 'yeni', 'aktif',
            'whatsapp_aktif', 'email_aktif', 'kampanya_hedefi',
            'vip', 'normal', 'düşük_öncelik'
        ]
        
        tag_count = random.randint(1, 4)
        return random.sample(all_tags, tag_count)
    
    def export_whatsapp_campaign_data(self, campaign_data, file_path):
        """WhatsApp kampanya verilerini dışa aktar"""
        try:
            # Kampanya özeti
            summary = {
                'campaign_id': campaign_data.get('campaign_id'),
                'campaign_name': campaign_data.get('name'),
                'start_time': campaign_data.get('start_time'),
                'end_time': campaign_data.get('end_time'),
                'total_recipients': campaign_data.get('total'),
                'messages_sent': campaign_data.get('sent'),
                'messages_failed': campaign_data.get('failed'),
                'delivery_rate': f"{(campaign_data.get('sent', 0) / campaign_data.get('total', 1) * 100):.2f}%",
                'response_rate': campaign_data.get('response_rate', 0),
                'template_used': campaign_data.get('template_name'),
                'results': campaign_data.get('results', [])
            }
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(summary, file, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'message': f'Kampanya verileri {file_path} dosyasına aktarıldı'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def import_whatsapp_conversations(self, file_path):
        """WhatsApp konuşma geçmişini içe aktar"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                conversations = json.load(file)
            
            # Konuşmaları işle
            processed_conversations = []
            for conv in conversations:
                processed = {
                    'phone': self.format_whatsapp_number(conv.get('phone', '')),
                    'messages': conv.get('messages', []),
                    'firm_id': conv.get('firm_id'),
                    'firm_name': conv.get('firm_name'),
                    'conversation_start': conv.get('start_date'),
                    'last_message': conv.get('last_message_date'),
                    'message_count': len(conv.get('messages', [])),
                    'tags': conv.get('tags', [])
                }
                processed_conversations.append(processed)
            
            return {
                'success': True,
                'conversations': processed_conversations,
                'count': len(processed_conversations)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_whatsapp_numbers(self, firms):
        """WhatsApp numaralarını doğrula ve formatla"""
        validated = []
        invalid = []
        
        for firm in firms:
            phone = firm.get('phone') or firm.get('whatsapp_number')
            
            if not phone:
                invalid.append({
                    'firm': firm['name'],
                    'reason': 'Telefon numarası yok'
                })
                continue
            
            # Numarayı formatla
            formatted = self.format_whatsapp_number(phone)
            
            # Basit doğrulama (Türkiye numaraları için)
            if formatted.startswith('+90') and len(formatted) == 13:
                firm['whatsapp_number'] = formatted
                firm['whatsapp_valid'] = True
                validated.append(firm)
            else:
                invalid.append({
                    'firm': firm['name'],
                    'phone': phone,
                    'reason': 'Geçersiz format'
                })
        
        return {
            'valid': validated,
            'invalid': invalid,
            'valid_count': len(validated),
            'invalid_count': len(invalid)
        }
    
    def create_whatsapp_message_templates(self):
        """Hazır WhatsApp mesaj şablonları oluştur"""
        return {
            'templates': [
                {
                    'id': 'intro_1',
                    'name': 'Tanıtım Mesajı',
                    'content': "Merhaba {{firma_adi}} 👋 B2B çözümlerimizle {{firma_sektoru}} sektöründeki verimliliğinizi artırabiliriz. İlgilenir misiniz? 🚀",
                    'variables': ['firma_adi', 'firma_sektoru'],
                    'category': 'introduction'
                },
                {
                    'id': 'follow_up_1',
                    'name': 'Takip Mesajı',
                    'content': "Merhaba {{firma_adi}} 😊 Geçen gün gönderdiğimiz mesajı görme fırsatınız oldu mu? Sorularınız varsa yardımcı olabilirim.",
                    'variables': ['firma_adi'],
                    'category': 'follow_up'
                },
                {
                    'id': 'offer_1',
                    'name': 'Özel Teklif',
                    'content': "🎉 {{firma_adi}} için özel %30 indirim! Bu fırsat sadece 48 saat geçerli. Detaylar için yazın 💬",
                    'variables': ['firma_adi'],
                    'category': 'special_offer'
                },
                {
                    'id': 'meeting_1',
                    'name': 'Toplantı Talebi',
                    'content': "Merhaba {{firma_adi}} 📅 15 dakikalık online demo için uygun olduğunuz bir zaman var mı? Size özel çözümlerimizi göstermek isteriz.",
                    'variables': ['firma_adi'],
                    'category': 'meeting_request'
                },
                {
                    'id': 'thank_you_1',
                    'name': 'Teşekkür Mesajı',
                    'content': "{{firma_adi}}, ilginiz için teşekkürler! 🙏 Size en kısa sürede detaylı bilgi göndereceğiz. İyi günler! ☀️",
                    'variables': ['firma_adi'],
                    'category': 'thank_you'
                },
                {
                    'id': 'reminder_1',
                    'name': 'Hatırlatma',
                    'content': "Merhaba {{firma_adi}} 📧 Geçen hafta gönderdiğimiz email'i incelediniz mi? Spam klasörünü kontrol etmeyi unutmayın.",
                    'variables': ['firma_adi'],
                    'category': 'reminder'
                },
                {
                    'id': 'reengagement_1',
                    'name': 'Yeniden Etkileşim',
                    'content': "{{firma_adi}} ekibi, uzun zamandır görüşmüyoruz 👋 Yeni özelliklerimiz hakkında bilgi almak ister misiniz?",
                    'variables': ['firma_adi'],
                    'category': 'reengagement'
                }
            ],
            'categories': {
                'introduction': 'Tanıtım',
                'follow_up': 'Takip',
                'special_offer': 'Özel Teklif',
                'meeting_request': 'Toplantı Talebi',
                'thank_you': 'Teşekkür',
                'reminder': 'Hatırlatma',
                'reengagement': 'Yeniden Etkileşim'
            }
        }