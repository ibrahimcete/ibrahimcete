#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Server Başlatma Script'i
Ana API ve Mail Server'ı başlatır
"""

import subprocess
import time
import sys
import os
import requests
from threading import Thread

def start_api_server():
    """Ana API server'ı başlat"""
    print("🚀 Ana API Server başlatılıyor...")
    try:
        subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"❌ Ana API Server başlatma hatası: {e}")

def start_mail_server():
    """Mail server'ı başlat"""
    print("📧 Mail Server başlatılıyor...")
    try:
        subprocess.Popen(
            [sys.executable, "mail_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"❌ Mail Server başlatma hatası: {e}")

def check_server(url, name, max_retries=10):
    """Server'ın ayağa kalkıp kalkmadığını kontrol et"""
    for i in range(max_retries):
        try:
            response = requests.get(f"{url}/api/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ {name} hazır!")
                return True
        except:
            pass
        
        print(f"⏳ {name} bekleniyor... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print(f"❌ {name} başlatılamadı!")
    return False

def main():
    """Ana fonksiyon"""
    print("=" * 80)
    print("🎯 B2B Mail Automation - Server Başlatma")
    print("=" * 80)
    print()
    
    # Ana API Server'ı başlat
    start_api_server()
    time.sleep(3)
    
    # Mail Server'ı başlat
    start_mail_server()
    time.sleep(3)
    
    print()
    print("=" * 80)
    print("🔍 Server'lar kontrol ediliyor...")
    print("=" * 80)
    print()
    
    # Server'ları kontrol et
    api_ok = check_server("http://localhost:8000", "Ana API Server")
    mail_ok = check_server("http://localhost:5000", "Mail Server")
    
    print()
    print("=" * 80)
    
    if api_ok and mail_ok:
        print("✅ TÜM SERVER'LAR BAŞARILI BİR ŞEKİLDE BAŞLATILDI!")
        print()
        print("📡 Ana API Server: http://localhost:8000")
        print("📧 Mail Server:    http://localhost:5000")
        print()
        print("Artık ana uygulamayı başlatabilirsiniz:")
        print("  python main.py")
    else:
        print("⚠️ BAZI SERVER'LAR BAŞLATILAMADI!")
        print()
        print("Lütfen logları kontrol edin:")
        print("  - api_server.log")
        print("  - mail_server.log")
    
    print("=" * 80)
    print()
    print("Server'ları durdurmak için Ctrl+C yapın veya:")
    print("  - Windows: taskkill /F /IM python.exe")
    print("  - Linux/Mac: pkill -f 'python.*server.py'")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 İşlem kullanıcı tarafından iptal edildi.")
        sys.exit(0)

