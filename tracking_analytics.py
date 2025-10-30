#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tracking Analytics - Detaylı Email Tracking Raporlama ve Analiz
Raspberry Pi uyumlu performanslı analytics modülü
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from collections import defaultdict
from tracking_database import TrackingDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrackingAnalytics:
    """Email tracking analytics ve raporlama"""
    
    def __init__(self, db_path: str = "tracking.db"):
        self.db = TrackingDatabase(db_path)
        logger.info("📊 Tracking Analytics başlatıldı")
    
    # ==================== GENEL İSTATİSTİKLER ====================
    
    def get_dashboard_stats(self, days: int = 7) -> Dict:
        """
        Dashboard için özet istatistikler
        
        Args:
            days: Son kaç günün verisi (default: 7)
        
        Returns:
            Dashboard istatistikleri
        """
        start_date = datetime.now() - timedelta(days=days)
        
        # Genel istatistikler
        overall_stats = self.db.get_overall_stats(start_date=start_date)
        
        # Günlük dağılım
        daily_stats = self._get_daily_breakdown(days)
        
        # En iyi performans gösterenler
        top_performers = self.db.get_top_performers(limit=5)
        
        # Cihaz/tarayıcı dağılımı
        device_breakdown = self._get_device_breakdown(days)
        
        return {
            'period': f'Son {days} gün',
            'overall': overall_stats,
            'daily_breakdown': daily_stats,
            'top_performers': top_performers,
            'device_breakdown': device_breakdown,
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_daily_breakdown(self, days: int = 7) -> List[Dict]:
        """Günlük istatistik dağılımı"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        DATE(sent_at) as date,
                        COUNT(*) as sent,
                        SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as opened,
                        SUM(CASE WHEN clicked = 1 THEN 1 ELSE 0 END) as clicked
                    FROM email_tracking
                    WHERE sent_at >= DATE('now', '-' || ? || ' days')
                    GROUP BY DATE(sent_at)
                    ORDER BY date DESC
                """, (days,))
                
                results = []
                for row in cursor.fetchall():
                    sent = row['sent'] or 0
                    opened = row['opened'] or 0
                    clicked = row['clicked'] or 0
                    
                    results.append({
                        'date': row['date'],
                        'sent': sent,
                        'opened': opened,
                        'clicked': clicked,
                        'open_rate': round((opened / sent * 100) if sent > 0 else 0, 2),
                        'click_rate': round((clicked / sent * 100) if sent > 0 else 0, 2),
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Daily breakdown hatası: {e}")
            return []
    
    def _get_device_breakdown(self, days: int = 7) -> Dict:
        """Cihaz ve tarayıcı dağılımı"""
        try:
            with self.db.get_cursor() as cursor:
                # Cihaz türü dağılımı
                cursor.execute("""
                    SELECT 
                        device_type,
                        COUNT(*) as count
                    FROM pixel_opens
                    WHERE opened_at >= DATE('now', '-' || ? || ' days')
                    AND device_type IS NOT NULL
                    GROUP BY device_type
                    ORDER BY count DESC
                """, (days,))
                
                device_stats = [dict(row) for row in cursor.fetchall()]
                
                # Tarayıcı dağılımı
                cursor.execute("""
                    SELECT 
                        browser,
                        COUNT(*) as count
                    FROM pixel_opens
                    WHERE opened_at >= DATE('now', '-' || ? || ' days')
                    AND browser IS NOT NULL
                    GROUP BY browser
                    ORDER BY count DESC
                    LIMIT 5
                """, (days,))
                
                browser_stats = [dict(row) for row in cursor.fetchall()]
                
                # OS dağılımı
                cursor.execute("""
                    SELECT 
                        os,
                        COUNT(*) as count
                    FROM pixel_opens
                    WHERE opened_at >= DATE('now', '-' || ? || ' days')
                    AND os IS NOT NULL
                    GROUP BY os
                    ORDER BY count DESC
                    LIMIT 5
                """, (days,))
                
                os_stats = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'devices': device_stats,
                    'browsers': browser_stats,
                    'operating_systems': os_stats
                }
                
        except Exception as e:
            logger.error(f"Device breakdown hatası: {e}")
            return {'devices': [], 'browsers': [], 'operating_systems': []}
    
    # ==================== DETAYLI ANALİZLER ====================
    
    def get_engagement_analysis(self, days: int = 30) -> Dict:
        """
        Engagement analizi (açılma/tıklama davranışları)
        
        Args:
            days: Son kaç günün verisi
        
        Returns:
            Engagement analiz raporu
        """
        try:
            with self.db.get_cursor() as cursor:
                start_date = datetime.now() - timedelta(days=days)
                
                # Engagement score dağılımı
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN engagement_score >= 80 THEN 'Çok Yüksek (80-100)'
                            WHEN engagement_score >= 60 THEN 'Yüksek (60-79)'
                            WHEN engagement_score >= 40 THEN 'Orta (40-59)'
                            WHEN engagement_score >= 20 THEN 'Düşük (20-39)'
                            ELSE 'Çok Düşük (0-19)'
                        END as engagement_level,
                        COUNT(*) as count,
                        AVG(open_count) as avg_opens,
                        AVG(click_count) as avg_clicks
                    FROM email_tracking
                    WHERE sent_at >= ?
                    GROUP BY engagement_level
                    ORDER BY MIN(engagement_score) DESC
                """, (start_date,))
                
                engagement_distribution = [dict(row) for row in cursor.fetchall()]
                
                # Açılma zamanı analizi (saat bazlı)
                cursor.execute("""
                    SELECT 
                        CAST(strftime('%H', first_opened_at) AS INTEGER) as hour,
                        COUNT(*) as count
                    FROM email_tracking
                    WHERE first_opened_at >= ?
                    AND first_opened_at IS NOT NULL
                    GROUP BY hour
                    ORDER BY hour
                """, (start_date,))
                
                open_time_distribution = [dict(row) for row in cursor.fetchall()]
                
                # Tekrar açılma oranı
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_opened,
                        SUM(CASE WHEN open_count > 1 THEN 1 ELSE 0 END) as reopened,
                        AVG(open_count) as avg_open_count
                    FROM email_tracking
                    WHERE sent_at >= ?
                    AND opened = 1
                """, (start_date,))
                
                reopen_stats = dict(cursor.fetchone())
                
                return {
                    'engagement_distribution': engagement_distribution,
                    'open_time_distribution': open_time_distribution,
                    'reopen_stats': reopen_stats,
                    'period': f'Son {days} gün',
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Engagement analysis hatası: {e}")
            return {}
    
    def get_link_performance(self, days: int = 30, limit: int = 20) -> Dict:
        """
        Link performans analizi
        
        Args:
            days: Son kaç günün verisi
            limit: Kaç link gösterilecek
        
        Returns:
            Link performans raporu
        """
        try:
            with self.db.get_cursor() as cursor:
                start_date = datetime.now() - timedelta(days=days)
                
                # En çok tıklanan linkler
                cursor.execute("""
                    SELECT 
                        link_url,
                        COUNT(*) as total_clicks,
                        COUNT(DISTINCT tracking_id) as unique_emails,
                        COUNT(DISTINCT ip_address) as unique_ips
                    FROM link_clicks
                    WHERE clicked_at >= ?
                    GROUP BY link_url
                    ORDER BY total_clicks DESC
                    LIMIT ?
                """, (start_date, limit))
                
                top_links = [dict(row) for row in cursor.fetchall()]
                
                # Tıklama zamanı dağılımı
                cursor.execute("""
                    SELECT 
                        CAST(strftime('%H', clicked_at) AS INTEGER) as hour,
                        COUNT(*) as count
                    FROM link_clicks
                    WHERE clicked_at >= ?
                    GROUP BY hour
                    ORDER BY hour
                """, (start_date,))
                
                click_time_distribution = [dict(row) for row in cursor.fetchall()]
                
                # Cihaz bazlı tıklama oranları
                cursor.execute("""
                    SELECT 
                        device_type,
                        COUNT(*) as count
                    FROM link_clicks
                    WHERE clicked_at >= ?
                    AND device_type IS NOT NULL
                    GROUP BY device_type
                    ORDER BY count DESC
                """, (start_date,))
                
                device_clicks = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'top_links': top_links,
                    'click_time_distribution': click_time_distribution,
                    'device_clicks': device_clicks,
                    'period': f'Son {days} gün',
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Link performance hatası: {e}")
            return {}
    
    def get_firm_leaderboard(self, limit: int = 20) -> List[Dict]:
        """
        Firma başarı sıralaması
        
        Args:
            limit: Kaç firma gösterilecek
        
        Returns:
            Firma listesi (en yüksek engagement'tan düşüğe)
        """
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        firm_id,
                        COUNT(*) as total_sent,
                        SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as total_opened,
                        SUM(CASE WHEN clicked = 1 THEN 1 ELSE 0 END) as total_clicked,
                        AVG(engagement_score) as avg_engagement,
                        MAX(sent_at) as last_sent
                    FROM email_tracking
                    GROUP BY firm_id
                    ORDER BY avg_engagement DESC
                    LIMIT ?
                """, (limit,))
                
                firms = []
                for row in cursor.fetchall():
                    total_sent = row['total_sent'] or 0
                    total_opened = row['total_opened'] or 0
                    total_clicked = row['total_clicked'] or 0
                    
                    firms.append({
                        'firm_id': row['firm_id'],
                        'total_sent': total_sent,
                        'total_opened': total_opened,
                        'total_clicked': total_clicked,
                        'avg_engagement': round(row['avg_engagement'] or 0, 2),
                        'open_rate': round((total_opened / total_sent * 100) if total_sent > 0 else 0, 2),
                        'click_rate': round((total_clicked / total_sent * 100) if total_sent > 0 else 0, 2),
                        'last_sent': row['last_sent']
                    })
                
                return firms
                
        except Exception as e:
            logger.error(f"Firm leaderboard hatası: {e}")
            return []
    
    # ==================== ZAMANA DAYALI ANALİZLER ====================
    
    def get_hourly_heatmap(self, days: int = 30) -> Dict:
        """
        Saat bazlı ısı haritası (hangi saatlerde daha çok açılma/tıklama var)
        
        Returns:
            Günlük saat dağılımı
        """
        try:
            with self.db.get_cursor() as cursor:
                start_date = datetime.now() - timedelta(days=days)
                
                # Açılma ısı haritası
                cursor.execute("""
                    SELECT 
                        CAST(strftime('%w', first_opened_at) AS INTEGER) as day_of_week,
                        CAST(strftime('%H', first_opened_at) AS INTEGER) as hour,
                        COUNT(*) as count
                    FROM email_tracking
                    WHERE first_opened_at >= ?
                    AND first_opened_at IS NOT NULL
                    GROUP BY day_of_week, hour
                    ORDER BY day_of_week, hour
                """, (start_date,))
                
                open_heatmap = [dict(row) for row in cursor.fetchall()]
                
                # Tıklama ısı haritası
                cursor.execute("""
                    SELECT 
                        CAST(strftime('%w', clicked_at) AS INTEGER) as day_of_week,
                        CAST(strftime('%H', clicked_at) AS INTEGER) as hour,
                        COUNT(*) as count
                    FROM link_clicks
                    WHERE clicked_at >= ?
                    GROUP BY day_of_week, hour
                    ORDER BY day_of_week, hour
                """, (start_date,))
                
                click_heatmap = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'open_heatmap': open_heatmap,
                    'click_heatmap': click_heatmap,
                    'period': f'Son {days} gün',
                    'day_names': ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']
                }
                
        except Exception as e:
            logger.error(f"Hourly heatmap hatası: {e}")
            return {}
    
    def get_best_send_times(self, days: int = 60) -> Dict:
        """
        En iyi gönderim zamanları önerisi
        
        Args:
            days: Analiz için kullanılacak veri süresi
        
        Returns:
            Önerilen gönderim zamanları
        """
        try:
            with self.db.get_cursor() as cursor:
                start_date = datetime.now() - timedelta(days=days)
                
                # Gün bazlı analiz
                cursor.execute("""
                    SELECT 
                        CASE CAST(strftime('%w', sent_at) AS INTEGER)
                            WHEN 0 THEN 'Pazar'
                            WHEN 1 THEN 'Pazartesi'
                            WHEN 2 THEN 'Salı'
                            WHEN 3 THEN 'Çarşamba'
                            WHEN 4 THEN 'Perşembe'
                            WHEN 5 THEN 'Cuma'
                            WHEN 6 THEN 'Cumartesi'
                        END as day_name,
                        COUNT(*) as total_sent,
                        SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as total_opened,
                        AVG(engagement_score) as avg_engagement
                    FROM email_tracking
                    WHERE sent_at >= ?
                    GROUP BY day_name
                    ORDER BY avg_engagement DESC
                """, (start_date,))
                
                day_performance = []
                for row in cursor.fetchall():
                    total_sent = row['total_sent'] or 0
                    total_opened = row['total_opened'] or 0
                    
                    day_performance.append({
                        'day_name': row['day_name'],
                        'total_sent': total_sent,
                        'total_opened': total_opened,
                        'open_rate': round((total_opened / total_sent * 100) if total_sent > 0 else 0, 2),
                        'avg_engagement': round(row['avg_engagement'] or 0, 2)
                    })
                
                # Saat bazlı analiz
                cursor.execute("""
                    SELECT 
                        CAST(strftime('%H', sent_at) AS INTEGER) as hour,
                        COUNT(*) as total_sent,
                        SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as total_opened,
                        AVG(engagement_score) as avg_engagement
                    FROM email_tracking
                    WHERE sent_at >= ?
                    GROUP BY hour
                    ORDER BY avg_engagement DESC
                """, (start_date,))
                
                hour_performance = []
                for row in cursor.fetchall():
                    total_sent = row['total_sent'] or 0
                    total_opened = row['total_opened'] or 0
                    
                    hour_performance.append({
                        'hour': row['hour'],
                        'total_sent': total_sent,
                        'total_opened': total_opened,
                        'open_rate': round((total_opened / total_sent * 100) if total_sent > 0 else 0, 2),
                        'avg_engagement': round(row['avg_engagement'] or 0, 2)
                    })
                
                # En iyi 3 gün ve saat
                best_days = sorted(day_performance, key=lambda x: x['avg_engagement'], reverse=True)[:3]
                best_hours = sorted(hour_performance, key=lambda x: x['avg_engagement'], reverse=True)[:3]
                
                return {
                    'best_days': best_days,
                    'best_hours': best_hours,
                    'all_day_performance': day_performance,
                    'all_hour_performance': hour_performance,
                    'recommendation': self._generate_send_time_recommendation(best_days, best_hours),
                    'period': f'Son {days} gün',
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Best send times hatası: {e}")
            return {}
    
    def _generate_send_time_recommendation(self, best_days: List[Dict], best_hours: List[Dict]) -> str:
        """Gönderim zamanı önerisi metni oluştur"""
        if not best_days or not best_hours:
            return "Yeterli veri yok"
        
        day_names = ', '.join([d['day_name'] for d in best_days])
        hour_ranges = ', '.join([f"{h['hour']:02d}:00-{h['hour']+1:02d}:00" for h in best_hours])
        
        return (f"📅 En iyi günler: {day_names}\n"
                f"⏰ En iyi saatler: {hour_ranges}\n"
                f"💡 Öneri: Bu günlerde, bu saat aralıklarında mail göndererek "
                f"engagement oranlarınızı artırabilirsiniz.")
    
    # ==================== EXPORT ====================
    
    def export_to_json(self, output_file: str = "tracking_report.json"):
        """Detaylı raporu JSON olarak export et"""
        try:
            report = {
                'dashboard': self.get_dashboard_stats(days=30),
                'engagement_analysis': self.get_engagement_analysis(days=30),
                'link_performance': self.get_link_performance(days=30),
                'firm_leaderboard': self.get_firm_leaderboard(limit=50),
                'best_send_times': self.get_best_send_times(days=60),
                'hourly_heatmap': self.get_hourly_heatmap(days=30),
                'generated_at': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Rapor export edildi: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Export hatası: {e}")
            return False


# ==================== TEST ====================

if __name__ == "__main__":
    print("=" * 80)
    print("📊 Tracking Analytics Test")
    print("=" * 80)
    
    analytics = TrackingAnalytics()
    
    # Dashboard istatistikleri
    print("\n📈 Dashboard İstatistikleri (Son 7 gün):")
    dashboard = analytics.get_dashboard_stats(days=7)
    print(json.dumps(dashboard['overall'], indent=2, ensure_ascii=False))
    
    # En iyi gönderim zamanları
    print("\n⏰ En İyi Gönderim Zamanları:")
    send_times = analytics.get_best_send_times(days=30)
    if 'recommendation' in send_times:
        print(send_times['recommendation'])
    
    # Firma sıralaması
    print("\n🏆 Firma Liderlik Tablosu (Top 10):")
    leaderboard = analytics.get_firm_leaderboard(limit=10)
    for i, firm in enumerate(leaderboard, 1):
        print(f"  {i}. {firm['firm_id']} - Engagement: {firm['avg_engagement']}, "
              f"Open Rate: {firm['open_rate']}%")
    
    # Rapor export
    print("\n💾 Rapor export ediliyor...")
    analytics.export_to_json("tracking_report_test.json")
    
    print("\n✅ Test tamamlandı!")

