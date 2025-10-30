#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tracking GUI Integration Module
main.py için tracking pixel sistemi entegrasyon fonksiyonları
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

try:
    from tracking_analytics import TrackingAnalytics
    from tracking_database import TrackingDatabase
except ImportError as e:
    logging.warning(f"Tracking modülleri yüklenemedi: {e}")
    TrackingAnalytics = None
    TrackingDatabase = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrackingGUIManager:
    """GUI için tracking yönetimi"""
    
    def __init__(self):
        self.analytics = None
        self.db = None
        self.server_url = "https://web-production-24136.up.railway.app"
        
        # Tracking modüllerini başlat
        try:
            if TrackingAnalytics:
                self.analytics = TrackingAnalytics()
                logger.info("✅ Tracking Analytics başlatıldı")
            
            if TrackingDatabase:
                self.db = TrackingDatabase()
                logger.info("✅ Tracking Database başlatıldı")
        except Exception as e:
            logger.error(f"Tracking modülleri başlatma hatası: {e}")
    
    def update_server_url(self, url: str):
        """Tracking server URL'ini güncelle"""
        self.server_url = url
        logger.info(f"Tracking server URL: {url}")
    
    def check_server_health(self) -> Dict:
        """Tracking server sağlık kontrolü"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=15)
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'data': response.json()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'HTTP {response.status_code}'
                }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'offline',
                'error': 'Server bağlantısı kurulamadı'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_dashboard_stats(self, days: int = 7) -> Dict:
        """Dashboard istatistikleri al"""
        try:
            if self.analytics:
                return self.analytics.get_dashboard_stats(days=days)
            else:
                # Analytics modülü yoksa server'dan al
                response = requests.get(
                    f"{self.server_url}/api/tracking/statistics",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'overall': data,
                        'daily_breakdown': [],
                        'top_performers': [],
                        'device_breakdown': {}
                    }
                else:
                    return self._get_empty_stats()
        except Exception as e:
            logger.error(f"Dashboard stats hatası: {e}")
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict:
        """Boş istatistik şablonu"""
        return {
            'overall': {
                'total_sent': 0,
                'total_opened': 0,
                'total_clicked': 0,
                'open_rate': 0,
                'click_rate': 0,
                'ctr': 0,
                'avg_engagement': 0
            },
            'daily_breakdown': [],
            'top_performers': [],
            'device_breakdown': {
                'devices': [],
                'browsers': [],
                'operating_systems': []
            }
        }
    
    def get_engagement_analysis(self, days: int = 30) -> Dict:
        """Engagement analizi"""
        try:
            if self.analytics:
                return self.analytics.get_engagement_analysis(days=days)
            else:
                return {}
        except Exception as e:
            logger.error(f"Engagement analysis hatası: {e}")
            return {}
    
    def get_link_performance(self, days: int = 30, limit: int = 20) -> Dict:
        """Link performans analizi"""
        try:
            if self.analytics:
                return self.analytics.get_link_performance(days=days, limit=limit)
            else:
                return {
                    'top_links': [],
                    'click_time_distribution': [],
                    'device_clicks': []
                }
        except Exception as e:
            logger.error(f"Link performance hatası: {e}")
            return {
                'top_links': [],
                'click_time_distribution': [],
                'device_clicks': []
            }
    
    def get_best_send_times(self, days: int = 60) -> Dict:
        """En iyi gönderim zamanları"""
        try:
            if self.analytics:
                return self.analytics.get_best_send_times(days=days)
            else:
                return {
                    'best_days': [],
                    'best_hours': [],
                    'recommendation': 'Yeterli veri yok'
                }
        except Exception as e:
            logger.error(f"Best send times hatası: {e}")
            return {
                'best_days': [],
                'best_hours': [],
                'recommendation': 'Veri alınamadı'
            }
    
    def get_hourly_heatmap(self, days: int = 30) -> Dict:
        """Saat bazlı ısı haritası"""
        try:
            if self.analytics:
                return self.analytics.get_hourly_heatmap(days=days)
            else:
                return {
                    'open_heatmap': [],
                    'click_heatmap': [],
                    'day_names': ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']
                }
        except Exception as e:
            logger.error(f"Hourly heatmap hatası: {e}")
            return {
                'open_heatmap': [],
                'click_heatmap': [],
                'day_names': []
            }
    
    def get_firm_leaderboard(self, limit: int = 20) -> list:
        """Firma liderlik tablosu"""
        try:
            if self.analytics:
                return self.analytics.get_firm_leaderboard(limit=limit)
            else:
                return []
        except Exception as e:
            logger.error(f"Firm leaderboard hatası: {e}")
            return []
    
    def get_email_details(self, tracking_id: str) -> Optional[Dict]:
        """Belirli bir email'in detayları"""
        try:
            if self.db:
                return self.db.get_email_stats(tracking_id)
            else:
                # Database yoksa server'dan al
                response = requests.get(
                    f"{self.server_url}/api/tracking/{tracking_id}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
        except Exception as e:
            logger.error(f"Email details hatası: {e}")
            return None
    
    def export_report(self, output_file: str = "tracking_report.json") -> bool:
        """Detaylı rapor export et"""
        try:
            if self.analytics:
                return self.analytics.export_to_json(output_file)
            else:
                logger.warning("Analytics modülü yüklü değil, export yapılamadı")
                return False
        except Exception as e:
            logger.error(f"Export hatası: {e}")
            return False
    
    def generate_html_dashboard(self, stats: Dict) -> str:
        """HTML dashboard oluştur (main.py'deki QWebEngineView için)"""
        
        overall = stats.get('overall', {})
        daily_breakdown = stats.get('daily_breakdown', [])
        device_breakdown = stats.get('device_breakdown', {})
        
        # Chart.js için günlük veri
        dates = [item.get('date', '') for item in daily_breakdown[::-1]]  # Ters çevir (eskiden yeniye)
        sent_data = [item.get('sent', 0) for item in daily_breakdown[::-1]]
        opened_data = [item.get('opened', 0) for item in daily_breakdown[::-1]]
        clicked_data = [item.get('clicked', 0) for item in daily_breakdown[::-1]]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tracking Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.8;
        }}
        .stat-change {{
            font-size: 12px;
            color: #4ade80;
        }}
        .chart-container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-bottom: 30px;
        }}
        .chart-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
        }}
        canvas {{
            max-height: 400px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- İstatistik Kartları -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">📤 Gönderilen</div>
                <div class="stat-value">{overall.get('total_sent', 0)}</div>
                <div class="stat-change">Toplam email</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">👁️ Açılan</div>
                <div class="stat-value">{overall.get('total_opened', 0)}</div>
                <div class="stat-change">{overall.get('open_rate', 0)}% açılma oranı</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">🖱️ Tıklanan</div>
                <div class="stat-value">{overall.get('total_clicked', 0)}</div>
                <div class="stat-change">{overall.get('click_rate', 0)}% tıklama oranı</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">📊 CTR</div>
                <div class="stat-value">{overall.get('ctr', 0)}%</div>
                <div class="stat-change">Click-through rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">⚡ Engagement</div>
                <div class="stat-value">{overall.get('avg_engagement', 0):.1f}</div>
                <div class="stat-change">Ortalama skor</div>
            </div>
        </div>
        
        <!-- Günlük Trend Grafiği -->
        <div class="chart-container">
            <div class="chart-title">📈 Günlük Email Trend</div>
            <canvas id="dailyChart"></canvas>
        </div>
        
        <!-- Oranlar Grafiği -->
        <div class="chart-container">
            <div class="chart-title">📊 Performans Oranları</div>
            <canvas id="ratesChart"></canvas>
        </div>
    </div>
    
    <script>
        // Günlük trend grafiği
        const dailyCtx = document.getElementById('dailyChart');
        new Chart(dailyCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [
                    {{
                        label: 'Gönderilen',
                        data: {json.dumps(sent_data)},
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Açılan',
                        data: {json.dumps(opened_data)},
                        borderColor: 'rgb(34, 197, 94)',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'Tıklanan',
                        data: {json.dumps(clicked_data)},
                        borderColor: 'rgb(251, 191, 36)',
                        backgroundColor: 'rgba(251, 191, 36, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#fff'
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            color: '#fff'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }}
                    }},
                    x: {{
                        ticks: {{
                            color: '#fff'
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }}
                    }}
                }}
            }}
        }});
        
        // Oranlar grafiği
        const ratesCtx = document.getElementById('ratesChart');
        new Chart(ratesCtx, {{
            type: 'bar',
            data: {{
                labels: ['Açılma Oranı', 'Tıklama Oranı', 'CTR'],
                datasets: [{{
                    label: 'Performans (%)',
                    data: [
                        {overall.get('open_rate', 0)},
                        {overall.get('click_rate', 0)},
                        {overall.get('ctr', 0)}
                    ],
                    backgroundColor: [
                        'rgba(34, 197, 94, 0.8)',
                        'rgba(251, 191, 36, 0.8)',
                        'rgba(168, 85, 247, 0.8)'
                    ],
                    borderColor: [
                        'rgb(34, 197, 94)',
                        'rgb(251, 191, 36)',
                        'rgb(168, 85, 247)'
                    ],
                    borderWidth: 2,
                    borderRadius: 10
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            color: '#fff',
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }},
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.1)'
                        }}
                    }},
                    x: {{
                        ticks: {{
                            color: '#fff'
                        }},
                        grid: {{
                            display: false
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        return html
    
    def generate_heatmap_html(self, heatmap_data: Dict) -> str:
        """Isı haritası HTML oluştur"""
        
        open_heatmap = heatmap_data.get('open_heatmap', [])
        day_names = heatmap_data.get('day_names', ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'])
        
        # Isı haritası verisi oluştur
        heatmap_matrix = [[0 for _ in range(24)] for _ in range(7)]
        
        for item in open_heatmap:
            day = item.get('day_of_week', 0)
            hour = item.get('hour', 0)
            count = item.get('count', 0)
            if 0 <= day < 7 and 0 <= hour < 24:
                heatmap_matrix[day][hour] = count
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
        }}
        .heatmap-container {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }}
        .heatmap-title {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 30px;
            text-align: center;
        }}
        .heatmap {{
            display: grid;
            grid-template-columns: 100px repeat(24, 1fr);
            gap: 2px;
            font-size: 11px;
        }}
        .heatmap-cell {{
            padding: 8px 4px;
            text-align: center;
            border-radius: 4px;
            transition: all 0.3s;
        }}
        .heatmap-header {{
            font-weight: 600;
            background: rgba(255, 255, 255, 0.1);
        }}
        .heatmap-day {{
            font-weight: 600;
            background: rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
        }}
        .heatmap-data {{
            cursor: pointer;
        }}
        .heatmap-data:hover {{
            transform: scale(1.1);
            z-index: 10;
        }}
    </style>
</head>
<body>
    <div class="heatmap-container">
        <div class="heatmap-title">🔥 Email Açılma Isı Haritası</div>
        <div class="heatmap">
            <div class="heatmap-cell heatmap-header"></div>
            {"".join([f'<div class="heatmap-cell heatmap-header">{h:02d}:00</div>' for h in range(24)])}
            
            {"".join([
                f'''
                <div class="heatmap-cell heatmap-day">{day_names[day]}</div>
                {"".join([
                    f'''<div class="heatmap-cell heatmap-data" 
                         style="background-color: rgba(251, 191, 36, {min(heatmap_matrix[day][hour] / 10, 1)})"
                         title="{day_names[day]} {hour:02d}:00 - {heatmap_matrix[day][hour]} açılma">
                        {heatmap_matrix[day][hour] if heatmap_matrix[day][hour] > 0 else ''}
                    </div>'''
                    for hour in range(24)
                ])}
                '''
                for day in range(7)
            ])}
        </div>
    </div>
</body>
</html>
"""
        return html


# Global instance
_tracking_gui_manager = None

def get_tracking_gui_manager() -> TrackingGUIManager:
    """Singleton tracking GUI manager"""
    global _tracking_gui_manager
    if _tracking_gui_manager is None:
        _tracking_gui_manager = TrackingGUIManager()
    return _tracking_gui_manager

