#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import os
import pickle
import requests
from urllib.parse import urlencode

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Google API kütüphaneleri kurulu değil. pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class CalendarManager:
    """Google Calendar API yöneticisi"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.settings = {}
        self.token_file = 'token.pickle'
        self.credentials_file = 'credentials.json'
        
    def update_settings(self, settings):
        """Ayarları güncelle"""
        self.settings = settings
        
        # Credentials dosyasını oluştur
        if settings.get('calendar_client_id') and settings.get('calendar_client_secret'):
            self._create_credentials_file(settings)
    
    def _create_credentials_file(self, settings):
        """Credentials dosyasını oluştur"""
        credentials = {
            "installed": {
                "client_id": settings['calendar_client_id'],
                "client_secret": settings['calendar_client_secret'],
                "redirect_uris": [settings.get('calendar_redirect_uri', 'http://localhost:8080/callback')],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f)
    
    def get_auth_url(self):
        """Yetkilendirme URL'si oluştur"""
        if not GOOGLE_API_AVAILABLE:
            return None
            
        if not os.path.exists(self.credentials_file):
            self._create_credentials_file(self.settings)
            
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_file, self.SCOPES)
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return auth_url
    
    def authenticate(self, auth_code=None):
        """Google Calendar'a bağlan"""
        if not GOOGLE_API_AVAILABLE:
            return False
            
        try:
            # Token varsa yükle
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Token yoksa veya geçersizse yenile
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if auth_code:
                        # Manuel auth code ile token al
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, self.SCOPES)
                        flow.fetch_token(code=auth_code)
                        self.creds = flow.credentials
                    else:
                        # Otomatik browser açma
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, self.SCOPES)
                        self.creds = flow.run_local_server(port=8080)
                
                # Token'ı kaydet
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
            
        except Exception as e:
            print(f"Authentication hatası: {str(e)}")
            return False
    
    def is_authenticated(self):
        """Kimlik doğrulama durumunu kontrol et"""
        return self.service is not None and self.creds and self.creds.valid
    
    def test_connection(self):
        """Bağlantıyı test et"""
        if not self.is_authenticated():
            return False
            
        try:
            # Calendar listesini al
            calendar_list = self.service.calendarList().list().execute()
            return True
        except:
            return False
    
    def create_event(self, appointment_data):
        """Randevu oluştur"""
        if not self.is_authenticated():
            return None
            
        try:
            # Tarih parse
            if isinstance(appointment_data['date'], str):
                start_time = datetime.fromisoformat(appointment_data['date'])
            else:
                start_time = appointment_data['date']
            
            # Bitiş zamanı hesapla
            duration = appointment_data.get('duration', 30)
            end_time = start_time + timedelta(minutes=duration)
            
            # Event objesi
            event = {
                'summary': appointment_data['title'],
                'location': appointment_data['firm'].get('address', ''),
                'description': f"""
Firma: {appointment_data['firm']['name']}
Kişi: {appointment_data.get('person', 'Belirtilmemiş')}
Tip: {appointment_data.get('type', 'Görüşme')}

Notlar:
{appointment_data.get('notes', '')}
                """.strip(),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Europe/Istanbul',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Europe/Istanbul',
                },
                'reminders': self._get_reminders(appointment_data.get('reminder')),
                'attendees': self._get_attendees(appointment_data)
            }
            
            # Event'i oluştur
            event_result = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return event_result.get('id')
            
        except Exception as e:
            print(f"Event oluşturma hatası: {str(e)}")
            return None
    
    def _get_reminders(self, reminder_text):
        """Hatırlatma ayarlarını al"""
        if not reminder_text or reminder_text == "Hatırlatma yok":
            return {'useDefault': False}
        
        # Dakika cinsinden hatırlatma süreleri
        reminder_map = {
            "10 dakika önce": 10,
            "30 dakika önce": 30,
            "1 saat önce": 60,
            "1 gün önce": 1440
        }
        
        minutes = reminder_map.get(reminder_text, 30)
        
        return {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': minutes},
                {'method': 'email', 'minutes': minutes}
            ]
        }
    
    def _get_attendees(self, appointment_data):
        """Katılımcıları al"""
        attendees = []
        
        # Firma emaillerini ekle
        firm = appointment_data.get('firm', {})
        if firm.get('emails'):
            for email_data in firm['emails'][:3]:  # İlk 3 email
                attendees.append({
                    'email': email_data['email'],
                    'optional': True
                })
        
        return attendees
    
    def check_availability(self, date_time, duration_minutes):
        """Müsaitlik kontrolü yap"""
        if not self.is_authenticated():
            return []
            
        try:
            # Tarih aralığı belirle
            start_of_day = date_time.replace(hour=9, minute=0, second=0, microsecond=0)
            end_of_day = date_time.replace(hour=18, minute=0, second=0, microsecond=0)
            
            # O gün için eventleri al
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat() + 'Z',
                timeMax=end_of_day.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Müsait slotları bul
            available_slots = []
            current_time = start_of_day
            
            for event in events:
                event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
                
                # Mevcut zaman ile event başlangıcı arasında yeterli süre var mı?
                if (event_start - current_time).total_seconds() >= duration_minutes * 60:
                    available_slots.append({
                        'start': current_time,
                        'end': current_time + timedelta(minutes=duration_minutes)
                    })
                
                # Sonraki kontrol zamanını güncelle
                event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
                current_time = max(current_time, event_end)
            
            # Son event'ten günün sonuna kadar kontrol et
            if (end_of_day - current_time).total_seconds() >= duration_minutes * 60:
                available_slots.append({
                    'start': current_time,
                    'end': current_time + timedelta(minutes=duration_minutes)
                })
            
            return available_slots[:5]  # İlk 5 müsait slot
            
        except Exception as e:
            print(f"Müsaitlik kontrolü hatası: {str(e)}")
            return []
    
    def get_upcoming_events(self, days=7):
        """Yaklaşan eventleri al"""
        if not self.is_authenticated():
            return []
            
        try:
            now = datetime.utcnow()
            time_max = now + timedelta(days=days)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event['id'],
                    'title': event.get('summary', 'Başlıksız'),
                    'start': start,
                    'location': event.get('location', ''),
                    'description': event.get('description', '')
                })
            
            return formatted_events
            
        except Exception as e:
            print(f"Event listesi hatası: {str(e)}")
            return []
    
    def update_event(self, event_id, updates):
        """Event'i güncelle"""
        if not self.is_authenticated():
            return False
            
        try:
            # Mevcut event'i al
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Güncellemeleri uygula
            for key, value in updates.items():
                if key in event:
                    event[key] = value
            
            # Event'i güncelle
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Event güncelleme hatası: {str(e)}")
            return False
    
    def delete_event(self, event_id):
        """Event'i sil"""
        if not self.is_authenticated():
            return False
            
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Event silme hatası: {str(e)}")
            return False
    
    def get_calendar_analytics(self):
        """Takvim analitiği"""
        if not self.is_authenticated():
            return {}
            
        try:
            # Son 30 günün eventlerini al
            now = datetime.utcnow()
            time_min = now - timedelta(days=30)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=now.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Analitik hesapla
            total_meetings = len(events)
            meeting_types = {}
            daily_distribution = {}
            
            for event in events:
                # Tip analizi
                summary = event.get('summary', '').lower()
                if 'demo' in summary:
                    meeting_types['demo'] = meeting_types.get('demo', 0) + 1
                elif 'satış' in summary or 'sales' in summary:
                    meeting_types['sales'] = meeting_types.get('sales', 0) + 1
                elif 'destek' in summary or 'support' in summary:
                    meeting_types['support'] = meeting_types.get('support', 0) + 1
                else:
                    meeting_types['other'] = meeting_types.get('other', 0) + 1
                
                # Günlük dağılım
                start = event['start'].get('dateTime', event['start'].get('date'))
                if 'T' in start:
                    date = start.split('T')[0]
                else:
                    date = start
                
                daily_distribution[date] = daily_distribution.get(date, 0) + 1
            
            return {
                'total_meetings': total_meetings,
                'meeting_types': meeting_types,
                'daily_distribution': daily_distribution,
                'avg_meetings_per_day': total_meetings / 30 if total_meetings > 0 else 0
            }
            
        except Exception as e:
            print(f"Analitik hatası: {str(e)}")
            return {}