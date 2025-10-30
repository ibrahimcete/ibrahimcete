#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Tracking Test
"""

import requests
import json
import time
from datetime import datetime

def test_tracking():
    """Hızlı tracking test"""
    print("🧪 Quick Tracking Test")
    print("=" * 50)
    
    try:
        # Health check
        print("1️⃣ Testing server health...")
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data['status']}")
            print(f"📊 Total Emails: {data.get('total_emails_tracked', 0)}")
            print(f"🔒 Filtering: {data.get('filtering_enabled', False)}")
            print(f"📧 Own Emails: {data.get('own_emails_count', 0)}")
            print(f"🌐 Own IPs: {data.get('own_ips_count', 0)}")
            
            # Statistics test
            print("\n2️⃣ Testing statistics...")
            stats_response = requests.get("http://localhost:5000/api/tracking/statistics", timeout=5)
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"📤 Total Sent: {stats.get('total_sent', 0)}")
                print(f"👀 Total Opened: {stats.get('total_opened', 0)}")
                print(f"🖱️ Total Clicked: {stats.get('total_clicked', 0)}")
                print(f"📈 Open Rate: {stats.get('open_rate', 0)}%")
                print(f"📈 Click Rate: {stats.get('click_rate', 0)}%")
                print(f"⚡ Avg Engagement: {stats.get('avg_engagement', 0)}")
                
                print("\n✅ Tracking server is working!")
                return True
            else:
                print(f"❌ Statistics failed: {stats_response.status_code}")
                return False
        else:
            print(f"❌ Server Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Server not running")
        print("💡 Start server with: python tracking_pixel_main_pc.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Quick Test...")
    test_tracking()
    print("\n🎯 Test completed!")
