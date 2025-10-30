#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug runner
"""

import subprocess
import sys
import os

print("🚀 Program başlatılıyor...")
print(f"📁 Çalışma dizini: {os.getcwd()}")

try:
    # Programı çalıştır
    result = subprocess.run([sys.executable, "main.py"], 
                          capture_output=True, 
                          text=True, 
                          encoding='utf-8',
                          timeout=10)
    
    print("📤 STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("📤 STDERR:")
        print(result.stderr)
        
    print(f"📊 Exit code: {result.returncode}")
    
except subprocess.TimeoutExpired:
    print("⏰ Program 10 saniye sonra timeout oldu (normal)")
except Exception as e:
    print(f"❌ Hata: {e}")
