#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr
from datetime import datetime
import json
import uuid
from typing import Dict, Optional, List
import requests
import time
import re


class EmailManager:
    """Email gönderimi ve tracking yönetimi - Geliştirilmiş versiyon"""
    
    def __init__(self):
        self.settings = {}
        self.tracking_base_url = None
        self.main_api_url = None
        self.email_templates = self.load_email_templates()
    
    def update_settings(self, settings: dict):
        """Email ayarlarını güncelle"""
        self.settings = settings
        # Cloud mail server URL'i (artık Raspberry Pi yok)
        self.tracking_base_url = settings.get('tracking_url', 'https://web-production-24136.up.railway.app')
        self.main_api_url = settings.get('main_api_url', 'http://localhost:8000')

    def send_email(self, to_email: str, subject: str, body: str, 
                        firm_id: str, is_follow_up: bool = False) -> Dict:
        """
        Email gönder
        
        Args:
            to_email: Alıcı email adresi
            subject: Email konusu
            body: Email içeriği (HTML)
            firm_id: Firma ID'si
            is_follow_up: Takip maili mi?
        
        Returns:
            Gönderim sonucu
        """
        try:
            # Email ID oluştur
            email_id = str(uuid.uuid4())
            
            # Email validasyonu
            if not self.validate_email_address(to_email):
                return {
                    'success': False,
                    'error': 'Geçersiz email adresi',
                    'timestamp': datetime.now().isoformat(),
                    'to_email': to_email
                }
            
            # Tracking pixel ekle (1x1 transparent pixel)
            if self.tracking_base_url:
                tracking_id = f"{str(firm_id)}-{str(email_id)}"
                
                print("=" * 80)
                print("📍 ADIM 1: TRACKING PIXEL EKLEME")
                print("=" * 80)
                print(f"   Firm ID: {firm_id}")
                print(f"   Email ID: {email_id}")
                print(f"   Tracking ID: {tracking_id}")
                print(f"   Alıcı: {to_email}")
                print(f"   Tracking Base URL: {self.tracking_base_url}")
                
                # 1x1 PIXEL TRACKING - Basit ve çalışır!
                # Gelişmiş tracking pixel - Gmail bypass teknikleri
                tracking_pixel = f'''
                <!-- Gmail External Image Loading Bypass - Multi-Layer Approach -->
                
                <!-- Layer 1: Hidden div with image -->
                <div style="display:none; font-size:0; line-height:0; max-height:0; overflow:hidden; width:0; height:0;">
                    <img src="{self.tracking_base_url}/track/{tracking_id}.png" 
                         width="1" height="1" 
                         style="display:block; width:1px; height:1px; border:0; margin:0; padding:0; opacity:0.01;" 
                         alt="" 
                         onload="this.style.display='block';"
                         onerror="this.style.display='none';" />
                </div>
                
                <!-- Layer 2: Absolute positioned pixel -->
                <img src="{self.tracking_base_url}/track/{tracking_id}.png" 
                     width="1" height="1" 
                     style="display:block; width:1px; height:1px; border:0; margin:0; padding:0; opacity:0.01; position:absolute; left:-9999px; top:-9999px; visibility:hidden;" 
                     alt="" 
                     loading="eager"
                     decoding="async" />
                
                <!-- Layer 3: CSS background image -->
                <div style="background-image:url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01; visibility:hidden;"></div>
                
                <!-- Layer 4: Inline style with data URI fallback -->
                <div style="width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01; visibility:hidden;">
                    <img src="{self.tracking_base_url}/track/{tracking_id}.png" 
                         style="width:1px; height:1px; border:0; margin:0; padding:0;" 
                         alt="" />
                </div>
                
                <!-- Layer 5: JavaScript-based tracking (if supported) -->
                <script type="text/javascript">
                try {{
                    var img = new Image();
                    img.src = '{self.tracking_base_url}/track/{tracking_id}.png';
                    img.style.display = 'none';
                    img.style.width = '1px';
                    img.style.height = '1px';
                    document.body.appendChild(img);
                }} catch(e) {{}}
                </script>
                
                <!-- Layer 6: Meta refresh fallback -->
                <meta http-equiv="refresh" content="0;url={self.tracking_base_url}/track/{tracking_id}.png" style="display:none;" />
                '''

                print(f"\n📍 ADIM 2: TRACKING PIXEL HTML OLUŞTURULDU")
                print(f"   Pixel HTML: {tracking_pixel[:100]}...")
                
                # Link tracking
                body = self.add_link_tracking(body, firm_id, email_id)
                
                # ULTRA AGRESIF GMAIL BYPASS TEKNIKLERI
                gmail_bypass = f'''
                <!-- ULTRA AGRESIF GMAIL BYPASS - 20+ TEKNIK -->
                
                <!-- Technique 1: Data URI with base64 -->
                <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" 
                     style="width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;" 
                     onload="this.src='{self.tracking_base_url}/track/{tracking_id}.png';" />
                
                <!-- Technique 2: CSS @import -->
                <style>
                @import url('{self.tracking_base_url}/track/{tracking_id}.png');
                </style>
                
                <!-- Technique 3: CSS content property -->
                <div style="content:url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 4: CSS mask -->
                <div style="mask:url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 5: CSS clip-path -->
                <div style="clip-path:url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 6: CSS filter -->
                <div style="filter:url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 7: CSS border-image -->
                <div style="border-image:url('{self.tracking_base_url}/track/{tracking_id}.png') 1; width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 8: CSS list-style-image -->
                <div style="list-style-image:url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 9: CSS cursor -->
                <div style="cursor:url('{self.tracking_base_url}/track/{tracking_id}.png'), auto; width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 10: CSS shape-outside -->
                <div style="shape-outside:url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 11: Background with !important -->
                <div style="background-image:url('{self.tracking_base_url}/track/{tracking_id}.png') !important; width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 12: Multiple img tags with different attributes -->
                <img src="{self.tracking_base_url}/track/{tracking_id}.png" width="1" height="1" style="display:none;" alt="" />
                <img src="{self.tracking_base_url}/track/{tracking_id}.png" width="1" height="1" style="visibility:hidden;" alt="" />
                <img src="{self.tracking_base_url}/track/{tracking_id}.png" width="1" height="1" style="opacity:0;" alt="" />
                
                <!-- Technique 13: Object tag -->
                <object data="{self.tracking_base_url}/track/{tracking_id}.png" width="1" height="1" style="display:none;"></object>
                
                <!-- Technique 14: Embed tag -->
                <embed src="{self.tracking_base_url}/track/{tracking_id}.png" width="1" height="1" style="display:none;" />
                
                <!-- Technique 15: Iframe -->
                <iframe src="{self.tracking_base_url}/track/{tracking_id}.png" width="1" height="1" style="display:none; border:0;"></iframe>
                
                <!-- Technique 16: Link tag with rel -->
                <link rel="icon" href="{self.tracking_base_url}/track/{tracking_id}.png" />
                <link rel="shortcut icon" href="{self.tracking_base_url}/track/{tracking_id}.png" />
                <link rel="apple-touch-icon" href="{self.tracking_base_url}/track/{tracking_id}.png" />
                
                <!-- Technique 17: Meta refresh -->
                <meta http-equiv="refresh" content="0;url={self.tracking_base_url}/track/{tracking_id}.png" style="display:none;" />
                
                <!-- Technique 18: CSS animation -->
                <style>
                @keyframes track {{
                    0% {{ background-image: url('{self.tracking_base_url}/track/{tracking_id}.png'); }}
                    100% {{ background-image: url('{self.tracking_base_url}/track/{tracking_id}.png'); }}
                }}
                .track-anim {{ animation: track 0.1s infinite; width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01; }}
                </style>
                <div class="track-anim"></div>
                
                <!-- Technique 19: CSS hover -->
                <div style="width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;" 
                     onmouseover="this.style.backgroundImage='url({self.tracking_base_url}/track/{tracking_id}.png)'"></div>
                
                <!-- Technique 20: CSS focus -->
                <div style="width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;" 
                     onfocus="this.style.backgroundImage='url({self.tracking_base_url}/track/{tracking_id}.png)'" 
                     tabindex="0"></div>
                
                <!-- Technique 21: CSS active -->
                <div style="width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;" 
                     onmousedown="this.style.backgroundImage='url({self.tracking_base_url}/track/{tracking_id}.png)'"></div>
                
                <!-- Technique 22: CSS visited -->
                <a href="{self.tracking_base_url}/track/{tracking_id}.png" style="display:none; width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></a>
                
                <!-- Technique 23: CSS before/after pseudo elements -->
                <style>
                .track-before::before {{ content: url('{self.tracking_base_url}/track/{tracking_id}.png'); }}
                .track-after::after {{ content: url('{self.tracking_base_url}/track/{tracking_id}.png'); }}
                </style>
                <div class="track-before" style="width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                <div class="track-after" style="width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 24: CSS transform -->
                <div style="transform: url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 25: CSS box-shadow -->
                <div style="box-shadow: 0 0 0 1px url('{self.tracking_base_url}/track/{tracking_id}.png'); width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01;"></div>
                
                <!-- Technique 26: Advanced JavaScript tracking -->
                <script type="text/javascript">
                (function() {{
                    var methods = [
                        function() {{ var img = new Image(); img.src = '{self.tracking_base_url}/track/{tracking_id}.png'; }},
                        function() {{ var xhr = new XMLHttpRequest(); xhr.open('GET', '{self.tracking_base_url}/track/{tracking_id}.png'); xhr.send(); }},
                        function() {{ var link = document.createElement('link'); link.rel = 'preload'; link.href = '{self.tracking_base_url}/track/{tracking_id}.png'; document.head.appendChild(link); }},
                        function() {{ var script = document.createElement('script'); script.src = '{self.tracking_base_url}/track/{tracking_id}.png'; document.head.appendChild(script); }},
                        function() {{ var iframe = document.createElement('iframe'); iframe.src = '{self.tracking_base_url}/track/{tracking_id}.png'; iframe.style.display = 'none'; document.body.appendChild(iframe); }}
                    ];
                    
                    methods.forEach(function(method) {{
                        try {{ method(); }} catch(e) {{}}
                    }});
                    
                    // Fallback with setTimeout
                    setTimeout(function() {{
                        try {{
                            var img = new Image();
                            img.src = '{self.tracking_base_url}/track/{tracking_id}.png';
                            img.style.display = 'none';
                            document.body.appendChild(img);
                        }} catch(e) {{}}
                    }}, 100);
                }})();
                </script>
                
                <!-- Technique 27: CSS @font-face -->
                <style>
                @font-face {{
                    font-family: 'track';
                    src: url('{self.tracking_base_url}/track/{tracking_id}.png');
                }}
                .track-font {{ font-family: 'track'; width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01; }}
                </style>
                <div class="track-font">.</div>
                
                <!-- Technique 28: CSS @media query -->
                <style>
                @media screen {{
                    .track-media {{ background-image: url('{self.tracking_base_url}/track/{tracking_id}.png'); }}
                }}
                .track-media {{ width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01; }}
                </style>
                <div class="track-media"></div>
                
                <!-- Technique 29: CSS @supports -->
                <style>
                @supports (display: flex) {{
                    .track-supports {{ background-image: url('{self.tracking_base_url}/track/{tracking_id}.png'); }}
                }}
                .track-supports {{ width:1px; height:1px; position:absolute; left:-9999px; top:-9999px; opacity:0.01; }}
                </style>
                <div class="track-supports"></div>
                
                <!-- Technique 30: CSS @page -->
                <style>
                @page {{
                    background-image: url('{self.tracking_base_url}/track/{tracking_id}.png');
                }}
                </style>
                '''
                
                # Gmail bypass tekniklerini tracking pixel'e ekle
                tracking_pixel += gmail_bypass
                
                # Body'nin SONUNA tracking pixel ekle
                original_body_length = len(body)
                if '</body>' in body:
                    body = body.replace('</body>', f'{tracking_pixel}</body>')
                    print(f"\n📍 ADIM 3: PIXEL </body> TAG'İNDEN ÖNCE EKLENDİ")
                else:
                    body += tracking_pixel
                    print(f"\n📍 ADIM 3: PIXEL BODY SONUNA EKLENDİ")
                
                new_body_length = len(body)
                print(f"   Önceki body uzunluğu: {original_body_length}")
                print(f"   Yeni body uzunluğu: {new_body_length}")
                print(f"   Pixel eklendi mi: {'✅ EVET' if new_body_length > original_body_length else '❌ HAYIR'}")
                
                # Body'de pixel var mı kontrol et
                if tracking_id in body and '/track/' in body:
                    print(f"\n✅ DOĞRULAMA: Tracking pixel body'de mevcut!")
                    print(f"   Pixel URL: {self.tracking_base_url}/track/{tracking_id}.png")
                else:
                    print(f"\n❌ HATA: Tracking pixel body'de bulunamadı!")
                
                print("=" * 80)
            else:
                print("\n⚠️ WARNING: tracking_base_url ayarlanmamış, pixel eklenemiyor!")
                print(f"   tracking_base_url: {self.tracking_base_url}")
            
            # Email mesajını oluştur
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            
            # From adresi formatla
            from_name = self.settings.get('from_name', 'B2B Sales Team')
            from_email = self.settings.get('smtp_email')
            message["From"] = formataddr((from_name, from_email))
            message["To"] = to_email
            
            # Email headers
            message["X-Email-ID"] = str(email_id)
            message["X-Firm-ID"] = str(firm_id)
            message["X-Is-Follow-Up"] = str(is_follow_up)
            message["X-Mailer"] = "B2B Automation Pro"
            
            # Unsubscribe link ekle (CAN-SPAM uyumluluğu)
            unsubscribe_link = f"{self.tracking_base_url}/unsubscribe/{str(firm_id)}/{str(email_id)}" if self.tracking_base_url else "#"
            
            # Email footer ekle
            footer_html = f"""
            <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; 
                            font-size: 12px; color: #666; text-align: center;">
                <p>Bu email size özel olarak gönderilmiştir.</p>
                <p>
                    <a href="{unsubscribe_link}" style="color: #999;">Abonelikten çık</a> | 
                    <a href="#" style="color: #999;">Gizlilik Politikası</a>
                </p>
            </div>
            """
            
            if '</body>' in body:
                body = body.replace('</body>', f'{footer_html}</body>')
            else:
                body += footer_html
            
            # HTML içeriği ekle
            html_part = MIMEText(body, "html", "utf-8")
            message.attach(html_part)
            
            # Text version oluştur
            text_content = self.html_to_text(body)
            text_part = MIMEText(text_content, "plain", "utf-8")
            message.attach(text_part)
            
            # SMTP bağlantısı
            context = ssl.create_default_context()
            
            smtp_server = self.settings.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.settings.get('smtp_port', 587)
            if isinstance(smtp_port, str):
                smtp_port = int(smtp_port)
            smtp_email = self.settings.get('smtp_email')
            smtp_password = self.settings.get('smtp_password')
            
            # Rate limiting
            time.sleep(0.5)  # Her mail arasında 0.5 saniye bekle
            
            server = None
            try:
                print(f"🔍 DEBUG: SMTP bağlantısı kuruluyor: {smtp_server}:{smtp_port}")
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)
                print(f"🔍 DEBUG: SMTP bağlantısı kuruldu")
                
                server.ehlo()
                print(f"🔍 DEBUG: EHLO tamamlandı")
                
                server.starttls(context=context)
                print(f"🔍 DEBUG: STARTTLS tamamlandı")
                
                server.ehlo()
                print(f"🔍 DEBUG: EHLO (TLS) tamamlandı")
                
                server.login(smtp_email, smtp_password)
                print(f"🔍 DEBUG: Login tamamlandı")
                
                # Email gönder
                server.send_message(message)
                print(f"🔍 DEBUG: Email gönderildi")
                
            except smtplib.SMTPException as e:
                print(f"❌ DEBUG: SMTP hatası: {str(e)}")
                raise Exception(f"SMTP hatası: {str(e)}")
            except Exception as e:
                print(f"❌ DEBUG: Email gönderim hatası: {str(e)}")
                raise Exception(f"Email gönderim hatası: {str(e)}")
            finally:
                # Bağlantıyı düzgün kapat
                if server:
                    try:
                        server.quit()
                        print(f"🔍 DEBUG: SMTP bağlantısı kapatıldı")
                    except:
                        pass
            
            # Tracking server'a bilgi gönder
            if self.tracking_base_url:
                tracking_id = f"{firm_id}-{email_id}"
                print("\n📍 ADIM 4: TRACKING SERVER'A KAYIT GÖNDERİLİYOR")
                print(f"   Tracking ID: {tracking_id}")
                print(f"   Server URL: {self.tracking_base_url}/api/tracking/register")
                self.register_email_sent(tracking_id, firm_id, to_email, subject, body) 
            
            return {
                'success': True,
                'email_id': email_id,
                'timestamp': datetime.now().isoformat(),
                'to_email': to_email,
                'subject': subject,
                'body': body
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'error': 'SMTP kimlik doğrulama hatası. Email ve şifrenizi kontrol edin.',
                'timestamp': datetime.now().isoformat(),
                'to_email': to_email
            }
        except smtplib.SMTPServerDisconnected:
            return {
                'success': False,
                'error': 'SMTP sunucusu bağlantısı kesildi.',
                'timestamp': datetime.now().isoformat(),
                'to_email': to_email
            }
        except smtplib.SMTPRecipientsRefused:
            return {
                'success': False,
                'error': 'Alıcı email adresi reddedildi.',
                'timestamp': datetime.now().isoformat(),
                'to_email': to_email
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'to_email': to_email
            }

    def validate_email_address(self, email: str) -> bool:
        """Email adresinin geçerliliğini kontrol et"""
        # Basit email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False
        
        # Blacklist kontrolü
        blacklist_domains = ['example.com', 'test.com', 'demo.com']
        domain = email.split('@')[1]
        
        if domain in blacklist_domains:
            return False
        
        return True
    
    def add_link_tracking(self, html: str, firm_id: str, email_id: str) -> str:
        """HTML içindeki linklere tracking ekle"""
        if not self.tracking_base_url:
            return html
        
        # Basit link tracking - tüm href'leri wrap et
        # Not: Bu basit bir implementasyon, gerçek uygulamada daha sofistike olmalı
        
        import re
        
        def replace_link(match):
            url = match.group(1)
            # Mailto ve anchor linklerini atla
            if url.startswith(('mailto:', '#', 'tel:')):
                return match.group(0)
            
            # Tracking URL oluştur
            tracking_id = f"{str(firm_id)}-{str(email_id)}"
            tracked_url = f"{self.tracking_base_url}/click/{tracking_id}?url={url}"
            return f'href="{tracked_url}"'
        
        # href="..." pattern'ini bul ve değiştir
        pattern = r'href="([^"]+)"'
        tracked_html = re.sub(pattern, replace_link, html)
        
        return tracked_html
    
    def send_bulk_emails(self, email_list: List[Dict], template: dict, 
                        firm_data_list: List[Dict], batch_size: int = 10) -> List[Dict]:
        """
        Toplu email gönderimi (batch processing ile)
        
        Args:
            email_list: Email adresleri ve bilgileri
            template: Email şablonu
            firm_data_list: Firma verileri listesi
            batch_size: Her batch'te gönderilecek email sayısı
        
        Returns:
            Gönderim sonuçları
        """
        results = []
        total = len(email_list)
        
        for i in range(0, total, batch_size):
            batch_emails = email_list[i:i+batch_size]
            batch_firms = firm_data_list[i:i+batch_size]
            
            print(f"📮 Batch {i//batch_size + 1}/{(total//batch_size) + 1} gönderiliyor...")
            
            for email_data, firm_data in zip(batch_emails, batch_firms):
                # Her email için özel içerik oluştur
                personalized_content = self.personalize_email(template, firm_data, email_data)
                
                # Email gönder
                result = self.send_email(
                    to_email=email_data['email'],
                    subject=personalized_content['subject'],
                    body=personalized_content['body'],
                    firm_id=firm_data['id']
                )
                
                results.append(result)
                
                # Her emailden sonra kısa bekleme
                if result['success']:
                    time.sleep(0.5)  # Başarılı gönderimde 0.5 saniye
                else:
                    time.sleep(0.2)  # Hata durumunda 0.2 saniye
            
            # Batch'ler arası bekleme
            if i + batch_size < total:
                print(f"⏳ Sonraki batch için 10 saniye bekleniyor...")
                time.sleep(10)
        
        return results
    
    def personalize_email(self, template: dict, firm_data: dict, email_data: dict = None) -> dict:
        """
        Email içeriğini kişiselleştir
        
        Args:
            template: Email şablonu
            firm_data: Firma verileri
            email_data: Email alıcı bilgileri
        
        Returns:
            Kişiselleştirilmiş içerik
        """
        subject = template.get('subject', '')
        body = template.get('body', '')
        
        # Firma bilgileri
        replacements = {
            '{{firma_adi}}': firm_data.get('name', ''),
            '{{firma_adresi}}': firm_data.get('address', ''),
            '{{firma_sektoru}}': ', '.join(firm_data.get('types', [])[:2]),
            '{{firma_website}}': firm_data.get('website', ''),
            '{{firma_rating}}': str(firm_data.get('rating', '')),
            '{{firma_telefon}}': firm_data.get('phone', ''),
            '{{firma_teknolojiler}}': ', '.join(firm_data.get('technologies', [])[:3]),
            '{{firma_hizmetler}}': ', '.join(firm_data.get('services', [])[:3]),
            '{{firma_ozet}}': firm_data.get('ai_summary', ''),
        }
        
        # Email alıcı bilgileri
        if email_data:
            replacements.update({
                '{{kisi_adi}}': email_data.get('first_name', ''),
                '{{kisi_soyadi}}': email_data.get('last_name', ''),
                '{{kisi_pozisyon}}': email_data.get('position', ''),
                '{{kisi_email}}': email_data.get('email', '')
            })
        
        # Tarih ve zaman
        now = datetime.now()
        replacements.update({
            '{{gun}}': now.strftime('%d'),
            '{{ay}}': now.strftime('%B'),
            '{{yil}}': now.strftime('%Y'),
            '{{gun_adi}}': self.get_turkish_day_name(now.strftime('%A'))
        })
        
        # Placeholder'ları değiştir
        for placeholder, value in replacements.items():
            subject = subject.replace(placeholder, value)
            body = body.replace(placeholder, value)
        
        # Boş placeholder'ları temizle
        subject = re.sub(r'\{\{[^}]+\}\}', '', subject)
        body = re.sub(r'\{\{[^}]+\}\}', '', body)
        
        return {
            'subject': subject.strip(),
            'body': body.strip()
        }
    
    def get_turkish_day_name(self, english_day: str) -> str:
        """İngilizce gün adını Türkçe'ye çevir"""
        days = {
            'Monday': 'Pazartesi',
            'Tuesday': 'Salı',
            'Wednesday': 'Çarşamba',
            'Thursday': 'Perşembe',
            'Friday': 'Cuma',
            'Saturday': 'Cumartesi',
            'Sunday': 'Pazar'
        }
        return days.get(english_day, english_day)
    
    def html_to_text(self, html: str) -> str:
        """HTML'i düz metne çevir"""
        import re
        from html.parser import HTMLParser
        
        class HTMLTextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_parts = []
                self.skip = False
            
            def handle_starttag(self, tag, attrs):
                if tag in ['script', 'style']:
                    self.skip = True
                elif tag == 'br':
                    self.text_parts.append('\n')
                elif tag == 'p':
                    self.text_parts.append('\n\n')
            
            def handle_endtag(self, tag):
                if tag in ['script', 'style']:
                    self.skip = False
            
            def handle_data(self, data):
                if not self.skip:
                    self.text_parts.append(data)
            
            def get_text(self):
                return ''.join(self.text_parts)
        
        # HTML parser kullan
        parser = HTMLTextExtractor()
        parser.feed(html)
        text = parser.get_text()
        
        # Temizleme
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Çoklu boş satırları temizle
        text = re.sub(r' +', ' ', text)  # Çoklu boşlukları temizle
        
        return text.strip()
    
    def register_email_sent(self, tracking_id: str, firm_id: str,
                            to_email: str, subject: str, body: str):
        """
        Gönderilen e-postanın bilgilerini Tracking Pixel Server'a kaydeder.
        Server otomatik olarak ana API'ye bildirim gönderir.
        
        YENİ: FastAPI tabanlı tracking_pixel_server.py ile uyumlu
        """
        try:
            # Tracking server URL'i kontrol et
            if not self.tracking_base_url:
                print("⚠️ Tracking URL ('tracking_url') ayarlanmamış, tracking kaydı yapılamıyor.")
                return

            # Tracking pixel server'a istek at
            url = f"{self.tracking_base_url}/api/tracking/register"
            
            # Gönderilecek veri (Pydantic EmailRegistration modeline uygun)
            data = {
                'tracking_id': str(tracking_id),
                'firm_id': str(firm_id),
                'to_email': str(to_email),
                'subject': str(subject),
                'body': str(body)[:5000],  # Body'yi kısalt (database performansı için)
                'sent_at': datetime.now().isoformat()
            }

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'B2B-Email-Manager/2.0'
            }
            
            # İsteği gönder
            print(f"\n📍 ADIM 5: HTTP POST İSTEĞİ GÖNDERİLİYOR")
            print(f"   URL: {url}")
            print(f"   Data: {data}")
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            print(f"\n📍 ADIM 6: TRACKING SERVER YANITI")
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"   Response Length: {len(response.text)} bytes")
            print(f"   Response (ilk 200 karakter): {response.text[:200]}")

            if response.status_code not in [200, 201]:
                print(f"   ❌ HATA: Tracking kaydı sunucu hatası!")
                print(f"   Tam yanıt: {response.text}")
            else:
                # JSON parse et - hata varsa yakala
                try:
                    result = response.json()
                    print(f"   ✅ BAŞARILI: Tracking kaydı server'a gönderildi!")
                    print(f"   Tracking ID: {tracking_id}")
                    print(f"   Status: {result.get('status', 'unknown')}")
                    print(f"   Message: {result.get('message', 'N/A')}")
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON PARSE HATASI!")
                    print(f"   Hata: {e}")
                    print(f"   Response body: {response.text}")
                    print(f"   Content-Type: {response.headers.get('Content-Type')}")
                    print(f"   ⚠️ Server JSON yerine başka formatta yanıt döndü!")
                except Exception as e:
                    print(f"   ❌ Beklenmedik hata: {e}")
                    print(f"   Response: {response.text[:500]}")

        except requests.exceptions.ConnectionError as e:
            print(f"⚠️ Tracking server'a bağlanılamadı: {str(e)}")
            print(f"   → URL: {self.tracking_base_url}")
            print(f"   → Lütfen tracking_pixel_server.py'nin çalıştığından emin olun!")
        except requests.exceptions.Timeout:
            print(f"⚠️ Tracking server zaman aşımı (timeout)")
            print(f"   → Server yavaş yanıt veriyor veya yanıt vermiyor")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Tracking server iletişim hatası: {str(e)}")
        except Exception as e:
            print(f"⚠️ Tracking kaydı sırasında beklenmedik bir hata oluştu: {str(e)}")
    
    def get_email_statistics(self) -> Dict:
        """
        Email istatistiklerini al
        
        Returns:
            İstatistikler
        """
        try:
            if not self.tracking_base_url:
                return {}
            
            url = f"{self.tracking_base_url}/api/statistics"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"⚠️ İstatistik alma hatası: {str(e)}")
            return {}
    
    def get_email_tracking_data(self, email_id: str) -> Dict:
        """
        Belirli bir email'in tracking verilerini al
        
        Args:
            email_id: Email ID
        
        Returns:
            Tracking verileri
        """
        try:
            if not self.tracking_base_url:
                return {}
            
            url = f"{self.tracking_base_url}/api/tracking/{email_id}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"⚠️ Tracking verisi alma hatası: {str(e)}")
            return {}
    
    def load_email_templates(self) -> Dict:
        """Hazır email şablonlarını yükle"""
        return {
            'intro': {
                'name': 'Tanıtım Maili',
                'subject': '{{firma_adi}} için Özel B2B Çözümlerimiz',
                'body': '''
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: linear-gradient(135deg, #0d7377 0%, #14a1a5 100%); 
                                 color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
                        .content { background-color: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
                        .button { display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #0d7377 0%, #14a1a5 100%); 
                                 color: white; text-decoration: none; border-radius: 25px; margin-top: 20px;
                                 font-weight: bold; }
                        .button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
                        .feature { margin: 15px 0; padding-left: 30px; position: relative; }
                        .feature:before { content: "✓"; position: absolute; left: 0; color: #0d7377; 
                                         font-weight: bold; font-size: 20px; }
                        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1 style="margin: 0;">B2B Çözüm Ortağınız</h1>
                            <p style="margin: 10px 0 0 0; opacity: 0.9;">İşinizi bir üst seviyeye taşıyın</p>
                        </div>
                        <div class="content">
                            <h2>Merhaba {{firma_adi}} Ekibi,</h2>
                            
                            <p>{{firma_adresi}} bölgesinde <strong>{{firma_rating}} yıldızlı</strong> 
                            başarınızla öne çıkan firmanızı yakından takip ediyoruz.</p>
                            
                            <p>{{firma_sektoru}} sektöründe faaliyet gösteren işletmenize özel olarak 
                            hazırladığımız B2B çözümlerimizle, verimliliğinizi <strong>%30'a kadar</strong> 
                            artırabileceğinizi biliyor muydunuz?</p>
                            
                            <h3>Size Özel Avantajlarımız:</h3>
                            <div class="feature">Sektörünüze özel kişiselleştirilmiş çözümler</div>
                            <div class="feature">{{firma_teknolojiler}} ile tam uyumlu entegrasyon</div>
                            <div class="feature">7/24 Türkçe teknik destek</div>
                            <div class="feature">İlk ay için %30 özel indirim</div>
                            
                            <p>Sizin gibi başarılı firmalarla çalışmak bizim için büyük bir onur olur.</p>
                            
                            <center>
                                <a href="https://calendly.com/b2b-sales/demo" class="button">
                                    15 Dakikalık Demo İçin Tıklayın
                                </a>
                            </center>
                            
                            <p style="margin-top: 30px;">Sorularınız için bize her zaman ulaşabilirsiniz.</p>
                            
                            <p>Saygılarımla,<br>
                            <strong>{{gonderen_adi|B2B Satış Ekibi}}</strong><br>
                            Tel: {{gonderen_telefon|0555 123 45 67}}<br>
                            Email: {{gonderen_email|info@b2bsolutions.com}}</p>
                        </div>
                    </div>
                </body>
                </html>
                '''
            },
            
            'follow_up': {
                'name': 'Takip Maili',
                'subject': 'Re: {{firma_adi}} için Özel Teklifimiz',
                'body': '''
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .content { padding: 20px; }
                        .highlight { background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; 
                                    margin: 20px 0; border-radius: 5px; }
                        .button { display: inline-block; padding: 10px 25px; background-color: #28a745; 
                                 color: white; text-decoration: none; border-radius: 20px; margin-top: 15px; }
                        .emoji { font-size: 20px; margin-right: 5px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="content">
                            <h2>Merhaba {{firma_adi}} Ekibi,</h2>
                            
                            <p><span class="emoji">👋</span>Umarım güzel bir {{gun_adi}} geçiriyorsunuzdur!</p>
                            
                            <p>Geçen hafta gönderdiğimiz B2B çözümlerimiz hakkındaki maili 
                            inceleme fırsatınız oldu mu? <span class="emoji">👀</span></p>
                            
                            <div class="highlight">
                                <strong>🎯 Hızlı Hatırlatma:</strong><br>
                                {{firma_sektoru}} sektöründeki diğer müşterilerimiz, bizimle çalışmaya 
                                başladıktan sonra ortalama <strong>%30 verimlilik artışı</strong> yaşadı.
                            </div>
                            
                            <p>Size nasıl yardımcı olabileceğimizi göstermek için <strong>10 dakikalık</strong> 
                            kısa bir demo yapmak isteriz.</p>
                            
                            <p>Bu hafta uygun olduğunuz bir zaman var mı? <span class="emoji">📅</span></p>
                            
                            <center>
                                <a href="https://calendly.com/b2b-sales/quick-demo" class="button">
                                    Hemen Randevu Al
                                </a>
                            </center>
                            
                            <p style="margin-top: 30px;">İyi çalışmalar,<br>
                            <strong>{{gonderen_adi|B2B Satış Ekibi}}</strong></p>
                            
                            <p style="font-size: 12px; color: #666; margin-top: 30px;">
                            PS: Eğer şu an için ilgilenmiyorsanız, lütfen bana kısa bir geri dönüş 
                            yapın ki sizi gereksiz yere rahatsız etmeyelim. 🙏
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                '''
            },
            
            'meeting_request': {
                'name': 'Toplantı Talebi',
                'subject': '{{firma_adi}} & B2B Solutions - Görüşme Talebi',
                'body': '''
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .calendar { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                                   padding: 25px; border-radius: 10px; margin: 20px 0; }
                        .time-slot { background-color: white; padding: 12px; margin: 8px 0; 
                                    border-radius: 5px; border: 2px solid #e9ecef; cursor: pointer;
                                    transition: all 0.3s; }
                        .time-slot:hover { border-color: #0d7377; transform: translateX(5px); }
                        .cta { background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); 
                              color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 25px; display: inline-block; font-weight: bold; }
                        .benefit { margin: 10px 0; padding-left: 25px; position: relative; }
                        .benefit:before { content: "→"; position: absolute; left: 0; color: #007bff; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Merhaba {{firma_adi}} Ekibi,</h2>
                        
                        <p>B2B çözümlerimize gösterdiğiniz ilgi için teşekkür ederiz! 🎉</p>
                        
                        <p>{{firma_teknolojiler}} kullanarak oluşturduğunuz altyapıya tam uyumlu 
                        çözümlerimizi size özel olarak tanıtmak istiyoruz.</p>
                        
                        <div class="calendar">
                            <h3>📅 Uygun Olduğunuz Zamanı Seçin:</h3>
                            <div class="time-slot">✓ Pazartesi, 10:00 - 10:30 (Online Demo)</div>
                            <div class="time-slot">✓ Salı, 14:00 - 14:30 (Online Demo)</div>
                            <div class="time-slot">✓ Çarşamba, 11:00 - 11:30 (Online Demo)</div>
                            <div class="time-slot">✓ Perşembe, 15:00 - 15:30 (Online Demo)</div>
                            <div class="time-slot">✓ Cuma, 13:00 - 13:30 (Online Demo)</div>
                        </div>
                        
                        <h3>Görüşmede Neler Konuşacağız?</h3>
                        <div class="benefit">İşletmenizin mevcut ihtiyaçlarını anlama</div>
                        <div class="benefit">Size özel hazırlanmış çözüm önerilerimiz</div>
                        <div class="benefit">Canlı demo ve kullanım senaryoları</div>
                        <div class="benefit">ROI hesaplaması ve fiyatlandırma</div>
                        <div class="benefit">Sorularınız ve özel istekleriniz</div>
                        
                        <p><strong>Not:</strong> Görüşme tamamen size özel olacak ve 
                        {{firma_hizmetler}} alanlarındaki ihtiyaçlarınıza odaklanacağız.</p>
                        
                        <center style="margin: 30px 0;">
                            <a href="https://calendly.com/b2b-sales/demo-meeting" class="cta">
                                📅 Hemen Randevu Oluştur
                            </a>
                        </center>
                        
                        <p>Görüşmek üzere! 🤝<br>
                        <strong>{{gonderen_adi|B2B Satış Ekibi}}</strong><br>
                        <em>{{gonderen_unvan|Kıdemli Satış Danışmanı}}</em></p>
                    </div>
                </body>
                </html>
                '''
            },
            
            'special_offer': {
                'name': 'Özel Teklif',
                'subject': '🎁 {{firma_adi}} için Özel İndirim Fırsatı!',
                'body': '''
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .offer-box { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                                    color: white; padding: 30px; border-radius: 10px; text-align: center;
                                    margin: 20px 0; }
                        .offer-title { font-size: 36px; font-weight: bold; margin: 0; }
                        .offer-subtitle { font-size: 18px; opacity: 0.9; margin: 10px 0; }
                        .countdown { background-color: rgba(255,255,255,0.2); padding: 15px; 
                                   border-radius: 5px; display: inline-block; margin: 20px 0; }
                        .cta-button { background-color: white; color: #ee5a24; padding: 15px 40px;
                                     text-decoration: none; border-radius: 30px; font-weight: bold;
                                     display: inline-block; margin-top: 20px; }
                        .feature-list { background-color: #f8f9fa; padding: 20px; border-radius: 10px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="offer-box">
                            <h1 class="offer-title">%40 İNDİRİM!</h1>
                            <p class="offer-subtitle">{{firma_adi}} için Özel Kampanya</p>
                            <div class="countdown">
                                ⏰ Bu teklif sadece 48 saat geçerli!
                            </div>
                        </div>
                        
                        <h2>Merhaba {{firma_adi}} Ekibi,</h2>
                        
                        <p>{{firma_rating}} yıldızlı başarınızı kutlamak ve sizinle çalışmaya başlamak 
                        için <strong>özel bir teklif</strong> hazırladık!</p>
                        
                        <div class="feature-list">
                            <h3>🎁 Özel Teklife Dahil Olanlar:</h3>
                            <ul>
                                <li>Tüm B2B çözümlerimizde <strong>%40 indirim</strong></li>
                                <li>6 aylık <strong>ücretsiz</strong> premium destek</li>
                                <li>{{firma_teknolojiler}} için özel entegrasyon paketi</li>
                                <li>Sınırsız kullanıcı lisansı</li>
                                <li>Özel eğitim ve onboarding desteği</li>
                            </ul>
                        </div>
                        
                        <p>Bu özel teklif, <strong>sadece {{gun}} {{ay}}</strong> tarihine kadar geçerli!</p>
                        
                        <center>
                            <a href="https://b2bsolutions.com/special-offer/{{firma_adi}}" class="cta-button">
                                🎯 Özel Teklifi Görüntüle
                            </a>
                        </center>
                        
                        <p style="margin-top: 30px;">Bu fırsatı kaçırmayın! Sorularınız için bize 
                        hemen ulaşabilirsiniz.</p>
                        
                        <p>Saygılarımla,<br>
                        <strong>{{gonderen_adi|İbrahim Çete}}</strong><br>
                        📞 Direkt Hat: {{gonderen_telefon|0546 205 18 20}}</p>
                    </div>
                </body>
                </html>
                '''
            }
        }
    
    def create_email_template(self, template_type: str) -> Dict:
        """
        Hazır email şablonları döndür
        
        Args:
            template_type: Şablon tipi
        
        Returns:
            Email şablonu
        """
        templates = self.load_email_templates()
        return templates.get(template_type, templates['intro'])
    
    def test_smtp_connection(self) -> Dict:
        """
        SMTP bağlantısını test et
        
        Returns:
            Test sonucu
        """
        try:
            smtp_server = self.settings.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.settings.get('smtp_port', 587)
            if isinstance(smtp_port, str):
                smtp_port = int(smtp_port)
            smtp_email = self.settings.get('smtp_email')
            smtp_password = self.settings.get('smtp_password')
            
            if not smtp_email or not smtp_password:
                return {
                    'success': False,
                    'error': 'Email veya şifre eksik',
                    'message': 'SMTP ayarlarını kontrol edin.'
                }
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(smtp_email, smtp_password)
            
            return {
                'success': True,
                'message': f'SMTP bağlantısı başarılı!\n\nSunucu: {smtp_server}:{smtp_port}\nEmail: {smtp_email}'
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'error': 'Kimlik doğrulama hatası',
                'message': 'Email adresi veya app password hatalı.\n\nGmail için 2FA açık olmalı ve App Password kullanmalısınız.'
            }
        except smtplib.SMTPServerDisconnected:
            return {
                'success': False,
                'error': 'Bağlantı hatası',
                'message': f'SMTP sunucusuna bağlanılamadı.\n\nSunucu: {smtp_server}\nPort: {smtp_port}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'SMTP bağlantı hatası!'
            }