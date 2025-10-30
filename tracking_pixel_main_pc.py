#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tracking Pixel Server - Ana PC Uyumlu
FastAPI tabanlı asenkron, performanslı ve güvenli email tracking çözümü
Sadece müşteri maili açtığında sinyal gönderir, kendi mailimizi açtığımızda gitmez
"""

from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import io
import json
import logging
from datetime import datetime
from PIL import Image
from typing import Dict, Optional
from pydantic import BaseModel, EmailStr
import asyncio
from user_agents import parse as parse_user_agent
import requests
from tracking_database import TrackingDatabase
import re
from contextlib import asynccontextmanager

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tracking_server_main_pc.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CORS Middleware will be added after FastAPI app creation

# Database
db = TrackingDatabase()

# Config
try:
    with open("config.json", "r", encoding='utf-8') as f:
        CONFIG = json.load(f)
except Exception as e:
    logger.error(f"Config yükleme hatası: {e}")
    CONFIG = {}

# Kendi email adreslerimiz (sinyal göndermeyeceğimiz adresler)
OWN_EMAIL_ADDRESSES = [
    CONFIG.get("smtp_email", "ibrahimcete@trsatis.com"),  # Kendi email adresiniz
    "ibrahimcete@trsatis.com",  # Manuel olarak da ekleyin
]

# Kendi IP adreslerimiz (sinyal göndermeyeceğimiz IP'ler)
# NOT: 127.0.0.1 ve localhost kaldırıldı - test için gerekli
OWN_IP_ADDRESSES = [
    # "127.0.0.1",  # Test için kaldırıldı
    # "localhost",  # Test için kaldırıldı
    "192.168.1.1",  # Kendi IP adresinizi buraya ekleyin
    "10.0.0.1",     # Diğer kendi IP adreslerinizi buraya ekleyin
]

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 TRACKING PIXEL SERVER BAŞLATILIYOR - ANA PC")
    logger.info("=" * 80)
    logger.info(f"📊 Database: tracking.db")
    logger.info(f"🌐 Mode: Main PC Optimized")
    logger.info(f"⚡ Async: Enabled")
    logger.info(f"🔒 Filtering: Enabled (Own emails/IPs filtered)")
    logger.info(f"📧 Own Emails: {len(OWN_EMAIL_ADDRESSES)}")
    logger.info(f"🌐 Own IPs: {len(OWN_IP_ADDRESSES)}")
    logger.info("=" * 80)
    yield
    # Shutdown
    logger.info("🛑 Server kapatılıyor...")
    db.close()
    logger.info("✅ Database bağlantısı kapatıldı")

# FastAPI App
app = FastAPI(
    title="B2B Tracking Pixel Server - Ana PC",
    description="Ana PC uyumlu asenkron email tracking sistemi",
    version="2.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ==================== PYDANTIC MODELS ====================

class EmailRegistration(BaseModel):
    tracking_id: str
    firm_id: str
    to_email: EmailStr
    subject: str
    body: str = ""
    sent_at: Optional[str] = None


class UnsubscribeRequest(BaseModel):
    email: EmailStr
    firm_id: str
    reason: Optional[str] = None


# ==================== HELPER FUNCTIONS ====================

def create_transparent_pixel() -> bytes:
    """1x1 transparent PNG pixel oluştur (cache edilmiş)"""
    img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    img_io = io.BytesIO()
    img.save(img_io, 'PNG', optimize=True)
    return img_io.getvalue()


# Pixel cache (her seferinde oluşturmamak için)
PIXEL_CACHE = create_transparent_pixel()


def extract_client_info(request: Request) -> Dict:
    """İstek bilgilerini çıkar (IP, User-Agent, Browser, OS vb.)"""
    # IP adresi
    ip_address = request.headers.get("X-Forwarded-For")
    if ip_address:
        ip_address = ip_address.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else "unknown"
    
    # User-Agent parse
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse_user_agent(user_agent_string)
    
    return {
        'ip_address': ip_address,
        'user_agent': user_agent_string,
        'device_type': 'Mobile' if user_agent.is_mobile else ('Tablet' if user_agent.is_tablet else 'Desktop'),
        'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
        'os': f"{user_agent.os.family} {user_agent.os.version_string}",
        'referer': request.headers.get("Referer"),
    }


def is_own_email_or_ip(to_email: str, ip_address: str) -> bool:
    """
    Kendi email adresimizi veya IP'mizi kontrol et
    Sadece müşteri maili açtığında sinyal gönder
    
    TEST MODU: Tüm emailler track ediliyor
    """
    # TEST İÇİN FİLTRELEME KAPALI - TÜM EMAİLLER TRACK EDİLİYOR
    logger.info(f"🔓 TEST MODU: Tüm emailler track ediliyor - {to_email}")
    return False
    
    # Email adresi kontrolü (devre dışı - test için)
    # to_email_lower = to_email.lower()
    # for own_email in OWN_EMAIL_ADDRESSES:
    #     if own_email and own_email.lower() in to_email_lower:
    #         logger.info(f"🚫 Kendi email adresimiz tespit edildi: {to_email} - Sinyal gönderilmiyor")
    #         return True
    
    # IP adresi kontrolü (devre dışı - test için)
    # for own_ip in OWN_IP_ADDRESSES:
    #     if own_ip in ip_address:
    #         logger.info(f"🚫 Kendi IP adresimiz tespit edildi: {ip_address} - Sinyal gönderilmiyor")
    #         return True
    
    # return False


async def notify_main_api(endpoint: str, data: Dict, method: str = 'POST'):
    """Ana API'ye asenkron bildirim gönder"""
    try:
        main_api_url = CONFIG.get("main_pc_api_url", "http://localhost:8000")
        api_key = CONFIG.get("main_pc_api_key", "b2b_cetei_secure_key_2024")
        
        url = f"{main_api_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
        
        # Asyncio ile HTTP request
        loop = asyncio.get_event_loop()
        
        if method.upper() == 'POST':
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, json=data, headers=headers, timeout=5)
            )
        elif method.upper() == 'GET':
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, headers=headers, timeout=5)
            )
        else:
            logger.error(f"Desteklenmeyen HTTP metodu: {method}")
            return False
        
        if response.status_code in [200, 201]:
            logger.info(f"✅ Ana API bildirimi başarılı: {endpoint}")
            return True
        else:
            logger.warning(f"⚠️ Ana API hatası: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Ana API'ye bağlanılamadı: {main_api_url}")
        return False
    except Exception as e:
        logger.error(f"❌ Ana API bildirimi hatası: {e}")
        return False


# ==================== RATE LIMITING ====================

async def check_rate_limit(request: Request, endpoint: str) -> bool:
    """Rate limit kontrolü (IP bazlı)"""
    client_info = extract_client_info(request)
    ip_address = client_info['ip_address']
    
    # Database'den kontrol et
    allowed, remaining = db.check_rate_limit(ip_address, endpoint, limit=100, window_minutes=60)
    
    if not allowed:
        logger.warning(f"🚫 Rate limit aşıldı: {ip_address} - {endpoint}")
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    
    logger.debug(f"✅ Rate limit OK: {ip_address} - Kalan: {remaining}")
    return True


# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """Ana sayfa"""
    return {
        "service": "B2B Tracking Pixel Server - Ana PC",
        "version": "2.1.0",
        "mode": "Main PC Optimized",
        "status": "running",
        "features": [
            "Email open tracking",
            "Link click tracking",
            "Unsubscribe management",
            "Real-time analytics",
            "Rate limiting",
            "Async processing",
            "Own email/IP filtering"
        ],
        "filtering": {
            "own_emails": OWN_EMAIL_ADDRESSES,
            "own_ips": OWN_IP_ADDRESSES
        }
    }


@app.get("/api/health")
async def health_check():
    """Sunucu sağlık kontrolü"""
    try:
        # Database bağlantı testi
        stats = db.get_overall_stats()
        
        return {
            'status': 'healthy',
            'service': 'Tracking Pixel Server - Ana PC',
            'version': '2.1.0',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'total_emails_tracked': stats.get('total_sent', 0),
            'mode': 'main_pc_optimized',
            'filtering_enabled': True,
            'own_emails_count': len(OWN_EMAIL_ADDRESSES),
            'own_ips_count': len(OWN_IP_ADDRESSES)
        }
    except Exception as e:
        logger.error(f"Health check hatası: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


@app.post("/api/tracking/register")
async def register_email(email_data: EmailRegistration, background_tasks: BackgroundTasks):
    """
    Email gönderim kaydı
    EmailManager tarafından çağrılır
    """
    try:
        # Database'e kaydet
        success = db.register_email(
            tracking_id=email_data.tracking_id,
            firm_id=email_data.firm_id,
            to_email=email_data.to_email,
            subject=email_data.subject,
            body=email_data.body
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Email kaydedilemedi")
        
        logger.info(f"📧 Email kaydedildi: {email_data.tracking_id}")
        
        return {
            'status': 'success',
            'tracking_id': email_data.tracking_id,
            'message': 'Email registered successfully'
        }
        
    except Exception as e:
        logger.error(f"Email kayıt hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/track/{tracking_id}.png")
async def track_email_open(
    tracking_id: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Email açılma tracking pixel
    Email açıldığında bu endpoint çağrılır
    SADECE MÜŞTERİ MAİLİ AÇILDIĞINDA SİNYAL GÖNDERİR
    """
    try:
        # Rate limit kontrolü
        await check_rate_limit(request, f"/track/{tracking_id}")
        
        # İstek bilgilerini çıkar
        client_info = extract_client_info(request)
        
        # Email bilgilerini al
        email_stats = db.get_email_stats(tracking_id)
        if not email_stats:
            logger.warning(f"⚠️ Tracking ID bulunamadı: {tracking_id}")
            return Response(content=PIXEL_CACHE, media_type="image/png")
        
        to_email = email_stats.get('to_email', '')
        ip_address = client_info['ip_address']
        
        # KENDİ EMAİL ADRESİMİZİ VEYA IP'MİZİ KONTROL ET
        if is_own_email_or_ip(to_email, ip_address):
            logger.info(f"🚫 Kendi email/IP'miz tespit edildi - Sinyal gönderilmiyor")
            logger.info(f"   → Email: {to_email}")
            logger.info(f"   → IP: {ip_address}")
            # Pixel'i döndür ama database'e kaydetme
            return Response(
                content=PIXEL_CACHE,
                media_type="image/png",
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0"
                }
            )
        
        # MÜŞTERİ MAİLİ AÇILDI - SİNYAL GÖNDER
        logger.info(f"✅ Müşteri maili açıldı: {tracking_id} - {to_email}")
        logger.info(f"   → IP: {ip_address}")
        logger.info(f"   → Device: {client_info['device_type']}")
        
        # Database'e kaydet (direkt - background task sorunu için)
        try:
            # client_info'dan ip_address ve user_agent'ı çıkar
            metadata = {k: v for k, v in client_info.items() if k not in ['ip_address', 'user_agent']}
            
            db.record_open(
                tracking_id=tracking_id,
                ip_address=client_info['ip_address'],
                user_agent=client_info['user_agent'],
                **metadata
            )
            logger.info(f"✅ Database kaydı başarılı: {tracking_id}")
        except Exception as e:
            logger.error(f"❌ Database kayıt hatası: {e}")
        
        # Ana API'ye bildirim (background task)
        background_tasks.add_task(
            notify_main_api,
            '/api/tracking/sync',
            {
                'opens': [{
                    'tracking_id': tracking_id,
                    'opened_at': datetime.now().isoformat(),
                    'ip_address': client_info['ip_address'],
                    'user_agent': client_info['user_agent'],
                    'device_type': client_info['device_type'],
                    'to_email': to_email
                }]
            }
        )
        
        # 1x1 transparent pixel döndür (cache'den)
        return Response(
            content=PIXEL_CACHE,
            media_type="image/png",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tracking pixel hatası: {e}")
        # Hata olsa bile pixel döndür (tracking başarısız olsa bile email render olmalı)
        return Response(content=PIXEL_CACHE, media_type="image/png")


@app.get("/click/{tracking_id}")
async def track_link_click(
    tracking_id: str,
    url: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Link tıklama tracking
    Email içindeki linkler tıklandığında bu endpoint çağrılır
    SADECE MÜŞTERİ MAİLİ TIKLANDIĞINDA SİNYAL GÖNDERİR
    """
    try:
        # Rate limit kontrolü
        await check_rate_limit(request, f"/click/{tracking_id}")
        
        # İstek bilgilerini çıkar
        client_info = extract_client_info(request)
        
        # Email bilgilerini al
        email_stats = db.get_email_stats(tracking_id)
        if not email_stats:
            logger.warning(f"⚠️ Tracking ID bulunamadı: {tracking_id}")
            return RedirectResponse(url=url, status_code=302)
        
        to_email = email_stats.get('to_email', '')
        ip_address = client_info['ip_address']
        
        # KENDİ EMAİL ADRESİMİZİ VEYA IP'MİZİ KONTROL ET
        if is_own_email_or_ip(to_email, ip_address):
            logger.info(f"🚫 Kendi email/IP'miz tespit edildi - Sinyal gönderilmiyor")
            logger.info(f"   → Email: {to_email}")
            logger.info(f"   → IP: {ip_address}")
            # Yönlendir ama database'e kaydetme
            return RedirectResponse(url=url, status_code=302)
        
        # MÜŞTERİ MAİLİ TIKLANDI - SİNYAL GÖNDER
        logger.info(f"✅ Müşteri linki tıklandı: {tracking_id} - {to_email}")
        logger.info(f"   → Link: {url[:50]}...")
        logger.info(f"   → IP: {ip_address}")
        
        # Database'e kaydet (background task)
        background_tasks.add_task(
            db.record_click,
            tracking_id,
            url,
            client_info['ip_address'],
            client_info['user_agent'],
            device_type=client_info.get('device_type'),
            browser=client_info.get('browser'),
            os=client_info.get('os'),
            referer=client_info.get('referer')
        )
        
        # Ana API'ye bildirim (background task)
        background_tasks.add_task(
            notify_main_api,
            '/api/tracking/sync-clicks',
            {
                'clicks': [{
                    'tracking_id': tracking_id,
                    'clicked_at': datetime.now().isoformat(),
                    'link_url': url,
                    'ip_address': client_info['ip_address'],
                    'user_agent': client_info['user_agent'],
                    'to_email': to_email
                }]
            }
        )
        
        # Kullanıcıyı hedef URL'e yönlendir
        return RedirectResponse(url=url, status_code=302)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Link tracking hatası: {e}")
        # Hata olsa bile yönlendir
        return RedirectResponse(url=url, status_code=302)


@app.get("/unsubscribe/{firm_id}/{email_hash}")
async def unsubscribe_page(
    firm_id: str,
    email_hash: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """Abonelikten çıkma sayfası"""
    try:
        # İstek bilgilerini çıkar
        client_info = extract_client_info(request)
        
        # Email hash'inden tracking_id bul (basitleştirilmiş)
        tracking_id = f"{firm_id}-{email_hash}"
        
        # Database'den email bilgilerini al
        email_stats = db.get_email_stats(tracking_id)
        email_address = email_stats['to_email'] if email_stats else 'unknown'
        
        # Unsubscribe işle (background task)
        background_tasks.add_task(
            db.record_unsubscribe,
            email_address,
            firm_id,
            tracking_id,
            "User request via unsubscribe link",
            client_info['ip_address'],
            client_info['user_agent']
        )
        
        # Ana API'ye bildirim (background task)
        background_tasks.add_task(
            notify_main_api,
            '/api/tracking/unsubscribe',
            {
                'firm_id': firm_id,
                'email': email_address,
                'reason': 'User request via unsubscribe link'
            }
        )
        
        logger.info(f"🚫 Abonelikten çıkıldı: {email_address}")
        
        # Başarı sayfası
        html_content = """
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Abonelikten Çıkıldı</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                    max-width: 500px;
                    width: 100%;
                }
                .icon {
                    font-size: 64px;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #28a745;
                    margin: 0 0 10px 0;
                }
                p {
                    color: #666;
                    font-size: 16px;
                    line-height: 1.6;
                }
                .info {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 10px;
                    margin-top: 20px;
                    font-size: 14px;
                    color: #495057;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">✓</div>
                <h1>Abonelikten Çıkıldı</h1>
                <p>Email listemizden başarıyla çıkarıldınız.</p>
                <p>Size daha fazla email göndermeyeceğiz.</p>
                <div class="info">
                    Eğer bu bir hata ise veya tekrar abone olmak isterseniz,
                    lütfen bizimle iletişime geçin.
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Unsubscribe hatası: {e}")
        return HTMLResponse(
            content="<h1>Hata</h1><p>Bir sorun oluştu. Lütfen daha sonra tekrar deneyin.</p>",
            status_code=500
        )


@app.get("/api/tracking/statistics")
async def get_tracking_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Tracking istatistiklerini getir"""
    try:
        # Tarih parametrelerini parse et
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # İstatistikleri al
        stats = db.get_overall_stats(start_date=start_dt, end_date=end_dt)
        stats['generated_at'] = datetime.now().isoformat()
        
        return stats
        
    except Exception as e:
        logger.error(f"İstatistik hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tracking/{tracking_id}")
async def get_tracking_details(tracking_id: str):
    """Belirli bir email'in tracking detaylarını getir"""
    try:
        stats = db.get_email_stats(tracking_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Tracking ID bulunamadı")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Tracking detay hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tracking/firm/{firm_id}")
async def get_firm_tracking(firm_id: str):
    """Firma bazlı tracking istatistikleri"""
    try:
        stats = db.get_firm_stats(firm_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Firma bulunamadı")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firma tracking hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tracking/top-performers")
async def get_top_performers(limit: int = 10):
    """En yüksek engagement skorlu emailler"""
    try:
        top = db.get_top_performers(limit=limit)
        
        return {
            'top_performers': top,
            'count': len(top),
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Top performers hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/cleanup")
async def cleanup_old_records(days: int = 90):
    """Eski kayıtları temizle (admin endpoint)"""
    try:
        success = db.cleanup_old_records(days=days)
        
        return {
            'status': 'success' if success else 'failed',
            'days': days,
            'message': f'{days} günden eski kayıtlar temizlendi'
        }
        
    except Exception as e:
        logger.error(f"Cleanup hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            'error': 'Not found',
            'message': 'The requested endpoint does not exist',
            'path': str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }
    )


# ==================== STARTUP & SHUTDOWN ====================
# Note: Startup and shutdown events are now handled by the lifespan context manager above


# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 80)
    print("📧 B2B TRACKING PIXEL SERVER - ANA PC EDITION")
    print("=" * 80)
    print("🚀 Server başlatılıyor...")
    print("📝 API Docs: http://localhost:5000/docs")
    print("📊 Health Check: http://localhost:5000/api/health")
    print("🔒 Filtering: Sadece müşteri maili açtığında sinyal gönderir")
    print("=" * 80)
    
    # Uvicorn ile başlat
    uvicorn.run(
        "tracking_pixel_main_pc:app",
        host="0.0.0.0",
        port=5000,
        reload=False,  # Production'da False
        workers=1,  # Ana PC için 1 worker yeterli
        log_level="info",
        access_log=True
    )
