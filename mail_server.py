#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mail Server - Cloud-Based Email Tracking System
Bulut ortamında çalışan mail gönderim ve tracking sistemi
Raspberry Pi entegrasyonu kaldırılmıştır - tamamen Cloud PC tabanlı
"""

from flask import Flask, request, jsonify, send_file, redirect
from flask_cors import CORS
import json
import logging
import requests
from datetime import datetime
from functools import wraps
import os
import io
from PIL import Image
import uuid
import threading
from database import Database

# Flask uygulaması
app = Flask(__name__)
CORS(app)  # Cross-origin isteklere izin ver

# Database bağlantısı
db = Database()

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mail_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Config yükle
def load_config():
    """Konfigürasyon dosyasını yükle"""
    try:
        with open("config.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Config yükleme hatası: {e}")
        return {
            "main_pc_api_url": "http://localhost:8000",
            "main_pc_api_key": "b2b_cetei_secure_key_2024",
            "mail_server_port": 5000
        }

CONFIG = load_config()
MAIN_API_URL = CONFIG.get("main_pc_api_url", "http://localhost:8000")
API_KEY = CONFIG.get("main_pc_api_key", "b2b_cetei_secure_key_2024")
MAIL_SERVER_PORT = CONFIG.get("mail_server_port", 5000)

# Tracking verileri için in-memory storage (geçici)
tracking_data = {}
tracking_lock = threading.Lock()

# ==================== HELPER FUNCTIONS ====================

def notify_main_api(endpoint: str, data: dict, method: str = 'POST'):
    """
    Ana PC API'sine bildirim gönder
    Cloud ortamında çalıştığımız için doğrudan HTTP üzerinden iletişim
    """
    try:
        url = f"{MAIN_API_URL}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        if method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        else:
            logger.error(f"Desteklenmeyen HTTP metodu: {method}")
            return False
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Ana API bildirimi başarılı: {endpoint}")
            return True
        else:
            logger.warning(f"⚠️ Ana API bildirimi hatası: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Ana PC API'sine bağlanılamadı: {MAIN_API_URL}")
        return False
    except Exception as e:
        logger.error(f"❌ Ana API bildirimi hatası: {e}")
        return False

def create_tracking_pixel():
    """1x1 transparent PNG pixel oluştur"""
    img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sunucu sağlık kontrolü"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'Cloud Mail Tracking Server',
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat(),
            'main_api_connected': notify_main_api('/api/health', {}, method='GET'),
            'mode': 'cloud'
        })
    except Exception as e:
        logger.error(f"Health check hatası: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/tracking/register', methods=['POST'])
def register_email_sent():
    """
    Email gönderim kaydı
    EmailManager tarafından çağrılır ve otomatik olarak ana API'ye bildirim gönderir
    """
    try:
        data = request.json
        
        # Gerekli alanları kontrol et
        required_fields = ['tracking_id', 'firm_id', 'to_email', 'subject']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing required field',
                    'field': field
                }), 400
        
        tracking_id = data['tracking_id']
        
        # Tracking verisini kaydet (in-memory)
        with tracking_lock:
            tracking_data[tracking_id] = {
                'tracking_id': tracking_id,
                'firm_id': data['firm_id'],
                'to_email': data['to_email'],
                'subject': data['subject'],
                'body': data.get('body', ''),
                'sent_at': data.get('sent_at', datetime.now().isoformat()),
                'opened_at': None,
                'opened_count': 0,
                'clicked_at': None,
                'click_count': 0,
                'clicks': []
            }
        
        logger.info(f"📧 Email kaydedildi: {tracking_id} → {data['to_email']}")
        
        # ANA API'YE OTOMATIK BİLDİRİM GÖNDER
        notification_data = {
            'tracking_id': tracking_id,
            'firm_id': data['firm_id'],
            'to_email': data['to_email'],
            'subject': data['subject'],
            'body': data.get('body', ''),
            'sent_at': data.get('sent_at', datetime.now().isoformat())
        }
        
        # Ana API'ye email gönderim bilgisini kaydet
        notify_success = notify_main_api('/api/tracking/register', notification_data)
        
        if not notify_success:
            logger.warning(f"⚠️ Ana API bildirimi başarısız oldu, ancak tracking devam ediyor")
        
        return jsonify({
            'status': 'success',
            'tracking_id': tracking_id,
            'main_api_notified': notify_success,
            'message': 'Email kaydedildi ve ana API bilgilendirildi'
        })
        
    except Exception as e:
        logger.error(f"Email kayıt hatası: {e}")
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 500

@app.route('/track/<tracking_id>.png', methods=['GET'])
def track_email_open(tracking_id):
    """
    Email açılma tracking pixel endpoint
    Email açıldığında bu endpoint çağrılır ve ana API'ye bildirim gönderilir
    """
    try:
        # IP ve User-Agent bilgilerini al
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Tracking verisini güncelle
        with tracking_lock:
            if tracking_id in tracking_data:
                tracking_data[tracking_id]['opened_count'] += 1
                if not tracking_data[tracking_id]['opened_at']:
                    tracking_data[tracking_id]['opened_at'] = datetime.now().isoformat()
                
                logger.info(f"👀 Email açıldı: {tracking_id} (#{tracking_data[tracking_id]['opened_count']})")
                
                # Ana API'ye bildirim gönder
                open_data = {
                    'opens': [{
                        'tracking_id': tracking_id,
                        'opened_at': tracking_data[tracking_id]['opened_at'],
                        'open_count': tracking_data[tracking_id]['opened_count'],
                        'ip_address': ip_address,
                        'user_agent': user_agent
                    }]
                }
                
                notify_main_api('/api/tracking/sync', open_data)
            else:
                logger.warning(f"⚠️ Bilinmeyen tracking ID: {tracking_id}")
        
        # 1x1 transparent pixel döndür
        pixel = create_tracking_pixel()
        return send_file(pixel, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Email açılma tracking hatası: {e}")
        # Hata olsa bile pixel döndür
        pixel = create_tracking_pixel()
        return send_file(pixel, mimetype='image/png')

@app.route('/click/<tracking_id>', methods=['GET'])
def track_link_click(tracking_id):
    """
    Link tıklama tracking endpoint
    Email içindeki linkler tıklandığında bu endpoint çağrılır
    """
    try:
        # Hedef URL'i al
        target_url = request.args.get('url', 'https://google.com')
        
        # IP ve User-Agent bilgilerini al
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Tracking verisini güncelle
        with tracking_lock:
            if tracking_id in tracking_data:
                tracking_data[tracking_id]['click_count'] += 1
                tracking_data[tracking_id]['clicked_at'] = datetime.now().isoformat()
                tracking_data[tracking_id]['clicks'].append({
                    'url': target_url,
                    'clicked_at': datetime.now().isoformat(),
                    'ip_address': ip_address,
                    'user_agent': user_agent
                })
                
                logger.info(f"🖱️ Link tıklandı: {tracking_id} → {target_url}")
                
                # Ana API'ye bildirim gönder
                click_data = {
                    'clicks': [{
                        'tracking_id': tracking_id,
                        'clicked_at': tracking_data[tracking_id]['clicked_at'],
                        'link_url': target_url,
                        'click_count': tracking_data[tracking_id]['click_count'],
                        'ip_address': ip_address,
                        'user_agent': user_agent
                    }]
                }
                
                notify_main_api('/api/tracking/sync-clicks', click_data)
            else:
                logger.warning(f"⚠️ Bilinmeyen tracking ID: {tracking_id}")
        
        # Kullanıcıyı hedef URL'e yönlendir
        return redirect(target_url, code=302)
        
    except Exception as e:
        logger.error(f"Link tıklama tracking hatası: {e}")
        # Hata olsa bile yönlendir
        target_url = request.args.get('url', 'https://google.com')
        return redirect(target_url, code=302)

@app.route('/unsubscribe/<firm_id>/<email_id>', methods=['GET'])
def unsubscribe(firm_id, email_id):
    """
    Abonelikten çıkma endpoint
    """
    try:
        # Tracking ID'den email adresini bul
        email_address = None
        with tracking_lock:
            tracking_id = f"{firm_id}-{email_id}"
            if tracking_id in tracking_data:
                email_address = tracking_data[tracking_id]['to_email']
        
        if email_address:
            # Ana API'ye unsubscribe bilgisi gönder
            unsubscribe_data = {
                'firm_id': firm_id,
                'email': email_address,
                'reason': 'User request via unsubscribe link'
            }
            
            notify_main_api('/api/tracking/unsubscribe', unsubscribe_data)
            
            logger.info(f"🚫 Abonelikten çıkıldı: {email_address}")
            
            return """
            <html>
                <head>
                    <title>Abonelikten Çıkıldı</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .container { max-width: 600px; margin: 0 auto; }
                        h1 { color: #28a745; }
                        p { color: #666; font-size: 16px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>✓ Abonelikten Çıkıldı</h1>
                        <p>Email listemizden başarıyla çıkarıldınız.</p>
                        <p>Size daha fazla email göndermeyeceğiz.</p>
                    </div>
                </body>
            </html>
            """
        else:
            return """
            <html>
                <head>
                    <title>Hata</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .container { max-width: 600px; margin: 0 auto; }
                        h1 { color: #dc3545; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>⚠️ Hata</h1>
                        <p>Geçersiz abonelik linki.</p>
                    </div>
                </body>
            </html>
            """, 400
            
    except Exception as e:
        logger.error(f"Unsubscribe hatası: {e}")
        return f"Hata: {str(e)}", 500

@app.route('/api/tracking/statistics', methods=['GET'])
def get_tracking_statistics():
    """Tracking istatistiklerini getir"""
    try:
        with tracking_lock:
            total_emails = len(tracking_data)
            opened_emails = sum(1 for t in tracking_data.values() if t['opened_at'] is not None)
            clicked_emails = sum(1 for t in tracking_data.values() if t['click_count'] > 0)
            
            total_opens = sum(t['opened_count'] for t in tracking_data.values())
            total_clicks = sum(t['click_count'] for t in tracking_data.values())
            
            open_rate = round((opened_emails / total_emails * 100), 2) if total_emails > 0 else 0
            click_rate = round((clicked_emails / total_emails * 100), 2) if total_emails > 0 else 0
        
        return jsonify({
            'total_emails': total_emails,
            'opened_emails': opened_emails,
            'clicked_emails': clicked_emails,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'open_rate': open_rate,
            'click_rate': click_rate,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"İstatistik hatası: {e}")
        return jsonify({
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500

@app.route('/api/tracking/<tracking_id>', methods=['GET'])
def get_tracking_details(tracking_id):
    """Belirli bir email'in tracking detaylarını getir"""
    try:
        with tracking_lock:
            if tracking_id in tracking_data:
                data = tracking_data[tracking_id].copy()
                return jsonify(data)
            else:
                return jsonify({
                    'error': 'Tracking ID not found',
                    'tracking_id': tracking_id
                }), 404
                
    except Exception as e:
        logger.error(f"Tracking detay hatası: {e}")
        return jsonify({
            'error': 'Failed to get tracking details',
            'message': str(e)
        }), 500

@app.route('/api/tracking/all', methods=['GET'])
def get_all_tracking():
    """Tüm tracking verilerini getir (admin için)"""
    try:
        with tracking_lock:
            all_data = list(tracking_data.values())
        
        return jsonify({
            'total': len(all_data),
            'tracking_data': all_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Tüm tracking verilerini getirme hatası: {e}")
        return jsonify({
            'error': 'Failed to get tracking data',
            'message': str(e)
        }), 500

@app.route('/api/sync/status', methods=['GET'])
def get_sync_status():
    """Ana API ile senkronizasyon durumunu kontrol et"""
    try:
        # Ana API'ye bağlantıyı test et
        main_api_status = notify_main_api('/api/health', {}, method='GET')
        
        return jsonify({
            'mail_server': 'online',
            'main_api_connected': main_api_status,
            'main_api_url': MAIN_API_URL,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Sync status hatası: {e}")
        return jsonify({
            'error': 'Failed to get sync status',
            'message': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Server bilgilerini göster
    print("=" * 80)
    print("📧 CLOUD MAIL TRACKING SERVER")
    print("=" * 80)
    print(f"🌐 Server URL: http://localhost:{MAIL_SERVER_PORT}")
    print(f"📡 Ana API URL: {MAIN_API_URL}")
    print(f"🔑 API Key: {API_KEY[:10]}..." if API_KEY else "⚠️  API Key not configured!")
    print(f"🚀 Mode: CLOUD (Raspberry Pi entegrasyonu kaldırıldı)")
    print("=" * 80)
    print("📝 Available endpoints:")
    print(f"  - POST   /api/tracking/register         → Email gönderim kaydı")
    print(f"  - GET    /track/<tracking_id>.png       → Email açılma tracking")
    print(f"  - GET    /click/<tracking_id>?url=...   → Link tıklama tracking")
    print(f"  - GET    /unsubscribe/<firm>/<email>    → Abonelikten çıkma")
    print(f"  - GET    /api/tracking/statistics       → İstatistikler")
    print(f"  - GET    /api/tracking/<tracking_id>    → Tracking detayları")
    print(f"  - GET    /api/tracking/all              → Tüm tracking verileri")
    print(f"  - GET    /api/sync/status               → Ana API senkronizasyon durumu")
    print(f"  - GET    /api/health                    → Health check")
    print("=" * 80)
    
    # Ana API bağlantısını test et
    print("\n🔍 Ana API bağlantısı test ediliyor...")
    if notify_main_api('/api/health', {}, method='GET'):
        print("✅ Ana API bağlantısı başarılı!")
    else:
        print("⚠️  Ana API'ye bağlanılamadı. Server yine de başlatılıyor...")
        print(f"    Lütfen şu URL'nin çalıştığından emin olun: {MAIN_API_URL}")
    
    print("\n" + "=" * 80)
    print("🚀 Server başlatılıyor...")
    print("=" * 80 + "\n")
    
    # Flask server'ı başlat
    app.run(
        host='0.0.0.0',
        port=MAIL_SERVER_PORT,
        debug=False,
        threaded=True
    )

