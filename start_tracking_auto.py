#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tracking Server Otomatik Başlatıcı
main.py çalıştığında tracking server'ı otomatik başlatır
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def check_server_running(url="http://localhost:5000"):
    """Tracking server'ın çalışıp çalışmadığını kontrol et"""
    try:
        response = requests.get(f"{url}/api/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_tracking_server():
    """Tracking server'ı başlat"""
    print("=" * 80)
    print("🚀 TRACKING SERVER BAŞLATILIYOR")
    print("=" * 80)
    
    # Config'den URL al
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        tracking_url = config.get('tracking_url', 'http://localhost:5000')
        print(f"📡 Tracking URL: {tracking_url}")
    except Exception as e:
        print(f"⚠️ Config okunamadı: {e}")
        tracking_url = "http://localhost:5000"
    
    # Server zaten çalışıyor mu kontrol et
    if check_server_running(tracking_url):
        print("✅ Tracking server ZATEN ÇALIŞIYOR!")
        return True
    
    print("⚠️ Tracking server çalışmıyor, başlatılıyor...")
    
    # Server'ı başlat
    try:
        server_path = Path(__file__).parent / "tracking_pixel_server.py"
        
        if sys.platform == 'win32':
            # Windows: Yeni konsol penceresi aç
            process = subprocess.Popen(
                [sys.executable, str(server_path)],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=str(Path(__file__).parent)
            )
        else:
            # Linux/Mac: Background'da çalıştır
            process = subprocess.Popen(
                [sys.executable, str(server_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(Path(__file__).parent)
            )
        
        print("⏳ Server başlatılıyor, 5 saniye bekleniyor...")
        
        # Server'ın başlamasını bekle (max 10 saniye)
        for i in range(10):
            time.sleep(1)
            if check_server_running(tracking_url):
                print(f"✅ Tracking server başarıyla başlatıldı! ({i+1} saniye)")
                print(f"📊 Health Check: {tracking_url}/api/health")
                print(f"📝 API Docs: {tracking_url}/docs")
                return True
            print(f"   Bekleniyor... ({i+1}/10)")
        
        print("⚠️ Server başlatıldı ama health check başarısız")
        print("💡 Manuel kontrol edin: python tracking_pixel_server.py")
        return False
        
    except Exception as e:
        print(f"❌ Server başlatılamadı: {e}")
        print("💡 Manuel başlatma: python tracking_pixel_server.py")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = start_tracking_server()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 TRACKING SERVER HAZIR!")
        print("=" * 80)
        print("\n💡 Artık mail gönderdiğinizde açılma tracking'i çalışacak!")
        print("   → Mail gönder")
        print("   → Alıcı maili açtığında tracking.db'ye kayıt düşer")
        print("   → GUI'de istatistikleri görebilirsiniz")
    else:
        print("⚠️ TRACKING SERVER BAŞLATILAMADI!")
        print("=" * 80)
        print("\n💡 Manuel başlatma:")
        print("   1. Yeni terminal/cmd aç")
        print("   2. Çalıştır: python tracking_pixel_server.py")
        print("   3. Veya: start_tracking_server.bat dosyasını çift tıkla")
    
    print("\n")

