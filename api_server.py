#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B2B Mail Automation - Ana PC API Server
Raspberry Pi tracking server ile iletişim için

Bu dosya, orijinal yapıyı korur ve şu eklemeleri içerir:
 - /api/extension/health  -> 3rd-party extension health check istekleri için 200 döner
 - /api/tracking/sync-sent -> Raspberry Pi'nin "sent_emails" verisini senkronize etmesi için yeni endpoint

Diğer tüm endpoint'ler ve davranış orijinal dosya ile aynıdır.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
import json
import logging
from datetime import datetime
from functools import wraps
import os
import uuid

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
        logging.FileHandler('api_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Config yükle
def load_config():
    """Konfigürasyon dosyasını yükle"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Config yükleme hatası: {e}")
        return {
            "main_pc_api_key": "b2b_cetei_secure_key_2024"
        }

CONFIG = load_config()
API_KEY = CONFIG.get("main_pc_api_key", "b2b_cetei_secure_key_2024")

# API key kontrolü decorator
def require_api_key(f):
    """API anahtarı gerektiren endpoint'ler için decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if not provided_key:
            logger.warning(f"API key eksik - IP: {request.remote_addr}")
            return jsonify({
                'error': 'API key required',
                'message': 'X-API-Key header must be provided'
            }), 401

        if provided_key != API_KEY:
            logger.warning(f"Geçersiz API key - IP: {request.remote_addr}")
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid'
            }), 403

        return f(*args, **kwargs)
    return decorated_function

# Ana endpoint'ler

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sunucu sağlık kontrolü"""
    try:
        db_status = db.check_connection() if hasattr(db, 'check_connection') else True
        return jsonify({
            'status': 'healthy',
            'service': 'B2B Mail Automation API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected' if db_status else 'disconnected'
        })
    except Exception as e:
        logger.error(f"Health check hatası: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# 3rd-party extension / health probe (404 log'larını önlemek için eklendi)
@app.route('/api/extension/health', methods=['GET'])
def extension_health_check():
    return jsonify({'status': 'ok', 'service': 'extension-health'}), 200

@app.route('/api/tracking/email-info/<tracking_id>', methods=['GET'])
@require_api_key
def get_email_info(tracking_id):
    """
    Tracking ID'ye göre email bilgilerini getir
    Raspberry Pi tracking server bu bilgileri kullanacak
    """
    try:
        parts = tracking_id.split('-')
        if len(parts) < 2:
            return jsonify({'error': 'Invalid tracking ID format'}), 400

        # Email log'unu bul
        email_log = db.get_email_by_tracking_id(tracking_id)

        if email_log:
            system_email = CONFIG.get('smtp_email', '')
            return jsonify({
                'tracking_id': tracking_id,
                'from_email': system_email,
                'to_email': email_log.get('to_email'),
                'subject': email_log.get('subject'),
                'sent_at': email_log.get('sent_at'),
                'firm_id': email_log.get('firm_id'),
                'firm_name': email_log.get('firm_name', '')
            })
        else:
            logger.warning(f"Email bulunamadı: {tracking_id}")
            return jsonify({'error': 'Email not found'}), 404
    except Exception as e:
        logger.error(f"Email bilgisi alma hatası: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/tracking/sync', methods=['POST'])
@require_api_key
def sync_email_opens():
    """Email açılmalarını senkronize et (opens beklenir)"""
    try:
        data = request.json
        if not data or 'opens' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'opens field is required'
            }), 400

        opens = data.get('opens', [])
        synced_count = 0
        errors = []

        for open_data in opens:
            try:
                tracking_id = open_data.get('tracking_id')
                if not tracking_id:
                    errors.append('Missing tracking_id')
                    continue

                success = db.update_email_tracking(
                    tracking_id=tracking_id,
                    opened_at=open_data.get('opened_at'),
                    open_count=open_data.get('open_count', 1),
                    ip_address=open_data.get('ip_address'),
                    user_agent=open_data.get('user_agent')
                )

                if success:
                    synced_count += 1
                    logger.info(f"Email açılması senkronize edildi: {tracking_id}")
                else:
                    errors.append(f"Failed to update {tracking_id}")
            except Exception as e:
                errors.append(f"Error processing {open_data.get('tracking_id', 'unknown')}: {str(e)}")

        response = {
            'status': 'success',
            'synced_count': synced_count,
            'total_received': len(opens)
        }
        if errors:
            response['errors'] = errors
            logger.warning(f"Senkronizasyon hataları: {errors}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Senkronizasyon hatası: {e}")
        return jsonify({
            'error': 'Sync failed',
            'message': str(e)
        }), 500

@app.route('/api/tracking/sync-clicks', methods=['POST'])
@require_api_key
def sync_link_clicks():
    """Link tıklamalarını senkronize et"""
    try:
        data = request.json
        if not data or 'clicks' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'clicks field is required'
            }), 400

        clicks = data.get('clicks', [])
        synced_count = 0
        errors = []

        for click_data in clicks:
            try:
                tracking_id = click_data.get('tracking_id')
                if not tracking_id:
                    errors.append('Missing tracking_id')
                    continue

                success = db.update_email_tracking(
                    tracking_id=tracking_id,
                    clicked_at=click_data.get('clicked_at'),
                    clicked_url=click_data.get('link_url'),
                    click_count=click_data.get('click_count', 1),
                    ip_address=click_data.get('ip_address'),
                    user_agent=click_data.get('user_agent')
                )

                if success:
                    synced_count += 1
                    logger.info(f"Link tıklaması senkronize edildi: {tracking_id}")
                else:
                    errors.append(f"Failed to update {tracking_id}")
            except Exception as e:
                errors.append(f"Error processing click: {str(e)}")

        response = {
            'status': 'success',
            'synced_count': synced_count,
            'total_received': len(clicks)
        }
        if errors:
            response['errors'] = errors
            logger.warning(f"Click senkronizasyon hataları: {errors}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Click senkronizasyon hatası: {e}")
        return jsonify({
            'error': 'Sync failed',
            'message': str(e)
        }), 500

@app.route('/api/tracking/sync-sent', methods=['POST'])
@require_api_key
def sync_sent_emails():
    """Raspberry Pi'nin gönderilen email kayıtlarını senkronize etmesi için yeni endpoint"""
    try:
        data = request.json
        if not data or 'sent_emails' not in data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'sent_emails field is required'
            }), 400

        sent_list = data.get('sent_emails', [])
        synced_count = 0
        errors = []

        for s in sent_list:
            try:
                tracking_id = s.get('tracking_id')
                if not tracking_id:
                    errors.append('Missing tracking_id')
                    continue

                # db.register_email_sent fonksiyonunu kullan
                success = db.register_email_sent(
                    email_id=s.get('email_id', str(uuid.uuid4())),
                    firm_id=s.get('firm_id'),
                    to_email=s.get('to_email'),
                    subject=s.get('subject') or '',
                    body=s.get('body') or ''
                )

                if success:
                    synced_count += 1
                    logger.info(f"Sent email senkronize edildi: {tracking_id}")
                else:
                    errors.append(f"Failed to register sent email: {tracking_id}")
            except Exception as e:
                errors.append(f"Error processing sent email: {str(e)}")

        response = {
            'status': 'success',
            'synced_count': synced_count,
            'total_received': len(sent_list)
        }
        if errors:
            response['errors'] = errors
            logger.warning(f"Sent email senkronizasyon hataları: {errors}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Sent email sync hatası: {e}")
        return jsonify({
            'error': 'Sync failed',
            'message': str(e)
        }), 500

@app.route('/api/tracking/register', methods=['POST'])
@require_api_key
def register_email_sent():
    """
    Gönderilen email'i kaydet
    Email Manager tarafından çağrılır
    """
    try:
        data = request.json
        required_fields = ['tracking_id', 'firm_id', 'to_email', 'subject']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing required field',
                    'field': field
                }), 400

        success = db.register_email_sent(
            email_id=data.get('email_id', str(uuid.uuid4())),
            firm_id=data['firm_id'],
            to_email=data['to_email'],
            subject=data['subject'],
            body=data.get('body', ''),
        )

        if success:
            logger.info(f"Email kaydedildi: {data['tracking_id']}")
            return jsonify({
                'status': 'success',
                'tracking_id': data['tracking_id']
            })
        else:
            return jsonify({
                'error': 'Failed to register email'
            }), 500
    except Exception as e:
        logger.error(f"Email kayıt hatası: {e}")
        return jsonify({
            'error': 'Registration failed',
            'message': str(e)
        }), 500

@app.route('/api/tracking/statistics', methods=['GET'])
@require_api_key
def get_tracking_statistics():
    """Tracking istatistiklerini getir"""
    try:
        period = request.args.get('period', 'week')
        stats = db.get_tracking_statistics(period)
        return jsonify({
            'period': period,
            'statistics': stats,
            'generated_at': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"İstatistik hatası: {e}")
        return jsonify({
            'error': 'Failed to get statistics',
            'message': str(e)
        }), 500

@app.route('/api/tracking/email/<tracking_id>', methods=['GET'])
@require_api_key
def get_email_tracking_details(tracking_id):
    """Belirli bir email'in tracking detaylarını getir"""
    try:
        details = db.get_email_tracking_details(tracking_id)
        if details:
            return jsonify(details)
        else:
            return jsonify({'error': 'Tracking data not found'}), 404
    except Exception as e:
        logger.error(f"Tracking detay hatası: {e}")
        return jsonify({
            'error': 'Failed to get tracking details',
            'message': str(e)
        }), 500

@app.route('/api/tracking/unsubscribe', methods=['POST'])
@require_api_key
def handle_unsubscribe():
    """Email abonelikten çıkma işlemi"""
    try:
        data = request.json
        if not data or 'firm_id' not in data or 'email' not in data:
            return jsonify({
                'error': 'Missing required fields',
                'message': 'firm_id and email are required'
            }), 400

        success = db.add_unsubscribe(
            firm_id=data['firm_id'],
            email=data['email'],
            reason=data.get('reason', 'User request')
        )

        if success:
            logger.info(f"Unsubscribe kaydedildi: {data['email']}")
            return jsonify({
                'status': 'success',
                'message': 'Successfully unsubscribed'
            })
        else:
            return jsonify({
                'error': 'Failed to process unsubscribe'
            }), 500
    except Exception as e:
        logger.error(f"Unsubscribe hatası: {e}")
        return jsonify({
            'error': 'Unsubscribe failed',
            'message': str(e)
        }), 500

@app.route('/api/config/tracking-url', methods=['GET'])
def get_tracking_url():
    """Raspberry Pi tracking URL'ini döndür"""
    try:
        tracking_url = CONFIG.get('tracking_url', '')
        if not tracking_url:
            tracking_url = 'http://raspberry-pi-ip:5000'
        return jsonify({
            'tracking_url': tracking_url,
            'status': 'configured' if tracking_url else 'not_configured'
        })
    except Exception as e:
        logger.error(f"Config hatası: {e}")
        return jsonify({
            'error': 'Failed to get tracking URL',
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

if __name__ == '__main__':
    # Server bilgilerini göster
    print("=" * 60)
    print("🚀 B2B Mail Automation API Server")
    print("=" * 60)
    print(f"📡 API URL: http://localhost:8000")
    print(f"🔑 API Key: {API_KEY[:10]}..." if API_KEY else "⚠️  API Key not configured!")
    print(f"📁 Config: config.json")
    print(f"📊 Database: Connected" if db else "⚠️  Database not connected!")
    print("=" * 60)
    print("📝 Available endpoints:")
    print("  - GET  /api/health")
    print("  - GET  /api/extension/health")
    print("  - GET  /api/tracking/email-info/<tracking_id>")
    print("  - POST /api/tracking/sync")
    print("  - POST /api/tracking/sync-clicks")
    print("  - POST /api/tracking/sync-sent")
    print("  - POST /api/tracking/register")
    print("  - GET  /api/tracking/statistics")
    print("  - GET  /api/tracking/email/<tracking_id>")
    print("  - POST /api/tracking/unsubscribe")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=8000,
        debug=False,
        threaded=True
    )
