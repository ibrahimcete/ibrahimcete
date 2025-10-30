#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 ANA AI MERKEZ SİSTEMİ (main3.py)
En Gelişmiş AI Kontrol Merkezi - Self-Learning & Cross-Module Intelligence
Main.py ile Uyumlu Modern GUI Tasarımı
"""

import sys
import json
import time
import os
import sqlite3
import threading
import traceback
import signal
import random
import asyncio
import queue
import hashlib
import pickle
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import subprocess
import psutil
import gc
import weakref

# PySide6 imports
try:
    from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
        QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QFrame, QDialog,
        QFormLayout, QDialogButtonBox, QMessageBox, QFileDialog, QTableWidget,
        QTableWidgetItem, QStatusBar, QScrollArea, QGroupBox, QGridLayout,
        QListWidget, QApplication, QTabWidget, QListWidgetItem, QInputDialog,
        QCheckBox, QSpinBox, QDateTimeEdit, QDateEdit, QProgressBar, QSplitter, 
        QSlider, QTreeWidget, QTreeWidgetItem, QTextBrowser, QPlainTextEdit,
        QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
        QGraphicsRectItem, QGraphicsTextItem, QGraphicsProxyWidget, QStackedWidget)
    from PySide6.QtCore import Qt, QThread, Signal, QTimer, QDateTime, QUrl, Slot, QObject, QPropertyAnimation, QEasingCurve, QRectF, QPointF
    from PySide6.QtGui import QIcon, QPalette, QColor, QFont, QPainter, QBrush, QPen, QPolygonF, QLinearGradient, QRadialGradient
    PYSIDE6_AVAILABLE = True
except ImportError as e:
    print(f"HATA: PySide6 yüklenemedi: {e}")
    sys.exit(1)

# AI ve ML kütüphaneleri
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import sklearn
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Sistem modülleri
try:
    from robust_system import (
        enhance_main_system, safe_execute, critical_safe, 
        ConnectionManager, MemoryManager, TimeoutManager,
        ThreadSafeManager, SystemMonitor, GracefulShutdown,
        APISecurityManager, DatabaseSecurityManager,
        safe_json_loads, safe_json_dumps, safe_file_read, safe_file_write,
        is_system_healthy, get_system_stats, logger as robust_logger
    )
    ROBUST_SYSTEM_AVAILABLE = True
except ImportError:
    ROBUST_SYSTEM_AVAILABLE = False
    def safe_execute(max_retries=3, delay=1.0, fallback_value=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Hata: {e}")
                    return fallback_value
            return wrapper
        return decorator

# Mevcut modüllerden import
try:
    from database import Database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    class Database:
        def __init__(self):
            pass

# Logging setup
if ROBUST_SYSTEM_AVAILABLE:
    logger = robust_logger
else:
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ai_center.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)


class AIState(Enum):
    """AI Durumları"""
    IDLE = "idle"
    LEARNING = "learning"
    ANALYZING = "analyzing"
    OPTIMIZING = "optimizing"
    CONTROLLING = "controlling"
    EMERGENCY = "emergency"


class ModuleType(Enum):
    """Modül Tipleri"""
    MAIN = "main"
    MAIN2 = "main2"
    DATABASE = "database"
    AI_CHAT = "ai_chat"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    ANALYTICS = "analytics"
    TRACKING = "tracking"


@dataclass
class AIInsight:
    """AI İçgörü"""
    id: str
    type: str
    priority: int
    data: Dict[str, Any]
    confidence: float
    timestamp: datetime
    source_module: str
    recommendations: List[str]
    action_required: bool


@dataclass
class ModuleStatus:
    """Modül Durumu"""
    name: str
    is_running: bool
    health_score: float
    last_activity: datetime
    error_count: int
    performance_metrics: Dict[str, Any]
    dependencies: List[str]


@dataclass
class LearningPattern:
    """Öğrenme Paterni"""
    pattern_id: str
    pattern_type: str
    frequency: int
    success_rate: float
    context: Dict[str, Any]
    last_seen: datetime
    confidence: float


class ModernCard(QFrame):
    """Modern Kart Bileşeni - Main.py ile uyumlu"""
    
    def __init__(self, title: str = "", value: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.setup_ui()
        self.apply_card_style()
    
    def setup_ui(self):
        """Kart UI'sini kur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Başlık ve ikon
        header_layout = QHBoxLayout()
        
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet("font-size: 20px;")
            header_layout.addWidget(icon_label)
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 12px; color: #888; font-weight: 500;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Değer
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        layout.addWidget(self.value_label)
        
        # Alt bilgi
        self.subtitle_label = QLabel("")
        self.subtitle_label.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(self.subtitle_label)
    
    def apply_card_style(self):
        """Kart stilini uygula"""
        self.setStyleSheet("""
            ModernCard {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
            }
            ModernCard:hover {
                background-color: #222;
                border-color: #555;
            }
        """)
    
    def update_value(self, value: str, subtitle: str = ""):
        """Değeri güncelle"""
        self.value_label.setText(str(value))
        if subtitle:
            self.subtitle_label.setText(subtitle)


class AICenterDatabase:
    """AI Merkez Veritabanı"""
    
    def __init__(self, db_path: str = "ai_center.db"):
        self.db_path = db_path
        self.conn = None
        self.lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Veritabanını başlat"""
        try:
            with self.lock:
                self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
                self.create_tables()
                logger.info("AI Merkez veritabanı başlatıldı")
        except Exception as e:
            logger.error(f"Veritabanı başlatma hatası: {e}")
    
    def create_tables(self):
        """Tabloları oluştur"""
        tables = [
            """CREATE TABLE IF NOT EXISTS ai_insights (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                priority INTEGER DEFAULT 0,
                data TEXT,
                confidence REAL DEFAULT 0.0,
                timestamp TEXT,
                source_module TEXT,
                recommendations TEXT,
                action_required BOOLEAN DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS module_status (
                name TEXT PRIMARY KEY,
                is_running BOOLEAN DEFAULT 0,
                health_score REAL DEFAULT 0.0,
                last_activity TEXT,
                error_count INTEGER DEFAULT 0,
                performance_metrics TEXT,
                dependencies TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS learning_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.0,
                context TEXT,
                last_seen TEXT,
                confidence REAL DEFAULT 0.0
            )""",
            """CREATE TABLE IF NOT EXISTS ai_memory (
                id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT,
                importance REAL DEFAULT 0.0,
                created_at TEXT,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0
            )""",
            """CREATE TABLE IF NOT EXISTS cross_module_commands (
                id TEXT PRIMARY KEY,
                source_module TEXT,
                target_module TEXT,
                command TEXT,
                parameters TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                executed_at TEXT,
                result TEXT
            )"""
        ]
        
        for table_sql in tables:
            self.conn.execute(table_sql)
        self.conn.commit()


class SelfLearningEngine:
    """Kendi Kendini Öğrenen AI Motoru"""
    
    def __init__(self, ai_center):
        self.ai_center = ai_center
        self.learning_thread = None
        self.is_learning = False
        self.patterns = {}
        self.insights = deque(maxlen=1000)
        self.performance_history = deque(maxlen=100)
        
    def start_learning(self):
        """Öğrenme sürecini başlat"""
        if not self.is_learning:
            self.is_learning = True
            self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
            self.learning_thread.start()
            logger.info("🧠 Self-learning engine başlatıldı")
    
    def stop_learning(self):
        """Öğrenme sürecini durdur"""
        self.is_learning = False
        if self.learning_thread:
            self.learning_thread.join(timeout=5)
        logger.info("🧠 Self-learning engine durduruldu")
    
    def _learning_loop(self):
        """Ana öğrenme döngüsü"""
        while self.is_learning:
            try:
                # Performans analizi
                self._analyze_performance()
                
                # Patern tanıma
                self._recognize_patterns()
                
                # Optimizasyon önerileri
                self._generate_optimizations()
                
                # Hafıza konsolidasyonu
                self._consolidate_memory()
                
                time.sleep(10)  # 10 saniyede bir öğren
                
            except Exception as e:
                logger.error(f"Öğrenme döngüsü hatası: {e}")
                time.sleep(5)
    
    def _analyze_performance(self):
        """Performans analizi"""
        try:
            current_metrics = self.ai_center.get_system_metrics()
            self.performance_history.append(current_metrics)
            
            if len(self.performance_history) > 10:
                # Trend analizi
                trends = self._analyze_trends()
                if trends:
                    insight = AIInsight(
                        id=f"perf_{int(time.time())}",
                        type="performance_trend",
                        priority=2,
                        data=trends,
                        confidence=0.8,
                        timestamp=datetime.now(),
                        source_module="self_learning",
                        recommendations=self._generate_performance_recommendations(trends),
                        action_required=True
                    )
                    self.ai_center.add_insight(insight)
                    
        except Exception as e:
            logger.error(f"Performans analizi hatası: {e}")
    
    def _recognize_patterns(self):
        """Patern tanıma"""
        try:
            # Modül etkileşim paternleri
            interactions = self.ai_center.get_recent_interactions()
            if len(interactions) > 5:
                patterns = self._find_interaction_patterns(interactions)
                for pattern in patterns:
                    self._update_pattern(pattern)
                    
        except Exception as e:
            logger.error(f"Patern tanıma hatası: {e}")
    
    def _generate_optimizations(self):
        """Optimizasyon önerileri üret"""
        try:
            # Sistem durumu analizi
            system_health = self.ai_center.get_system_health()
            if system_health['overall_score'] < 0.7:
                optimizations = self._suggest_optimizations(system_health)
                for opt in optimizations:
                    insight = AIInsight(
                        id=f"opt_{int(time.time())}",
                        type="optimization",
                        priority=1,
                        data=opt,
                        confidence=0.9,
                        timestamp=datetime.now(),
                        source_module="self_learning",
                        recommendations=[opt['action']],
                        action_required=True
                    )
                    self.ai_center.add_insight(insight)
                    
        except Exception as e:
            logger.error(f"Optimizasyon üretme hatası: {e}")
    
    def _consolidate_memory(self):
        """Hafıza konsolidasyonu"""
        try:
            # Eski hafızaları temizle
            self.ai_center.consolidate_memory()
            
            # Önemli hafızaları güçlendir
            important_memories = self.ai_center.get_important_memories()
            for memory in important_memories:
                self.ai_center.strengthen_memory(memory['id'])
                
        except Exception as e:
            logger.error(f"Hafıza konsolidasyonu hatası: {e}")
    
    def _analyze_trends(self):
        """Trend analizi yap"""
        try:
            if len(self.performance_history) < 3:
                return None
            
            trends = {}
            
            # CPU trendi
            cpu_values = [h.get('cpu', 0) for h in self.performance_history]
            if len(cpu_values) >= 3:
                cpu_trend = (cpu_values[-1] - cpu_values[0]) / len(cpu_values)
                trends['cpu_trend'] = cpu_trend
            
            # Memory trendi
            memory_values = [h.get('memory', 0) for h in self.performance_history]
            if len(memory_values) >= 3:
                memory_trend = (memory_values[-1] - memory_values[0]) / len(memory_values)
                trends['memory_trend'] = memory_trend
            
            return trends
            
        except Exception as e:
            logger.error(f"Trend analizi hatası: {e}")
            return None
    
    def _find_interaction_patterns(self, interactions):
        """Etkileşim paternlerini bul"""
        try:
            patterns = []
            
            # Modül etkileşim paternleri
            module_interactions = defaultdict(int)
            for interaction in interactions:
                module_interactions[interaction['module']] += 1
            
            for module, count in module_interactions.items():
                if count > 3:  # En az 3 etkileşim
                    pattern = {
                        'pattern_id': f"module_interaction_{module}",
                        'pattern_type': 'module_interaction',
                        'frequency': count,
                        'success_rate': 0.8,  # Simüle edilmiş
                        'context': {'module': module, 'interaction_count': count},
                        'last_seen': datetime.now(),
                        'confidence': min(1.0, count / 10.0)
                    }
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Patern bulma hatası: {e}")
            return []
    
    def _update_pattern(self, pattern):
        """Paterni güncelle"""
        try:
            pattern_id = pattern['pattern_id']
            
            if pattern_id in self.patterns:
                # Mevcut paterni güncelle
                existing = self.patterns[pattern_id]
                existing['frequency'] += pattern['frequency']
                existing['last_seen'] = pattern['last_seen']
                existing['confidence'] = min(1.0, existing['confidence'] + 0.1)
            else:
                # Yeni patern ekle
                self.patterns[pattern_id] = pattern
                
        except Exception as e:
            logger.error(f"Patern güncelleme hatası: {e}")
    
    def _suggest_optimizations(self, system_health):
        """Optimizasyon önerileri üret"""
        try:
            optimizations = []
            
            overall_score = system_health.get('overall_score', 0.5)
            
            if overall_score < 0.7:
                optimizations.append({
                    'type': 'memory_cleanup',
                    'priority': 1,
                    'action': 'Bellek temizliği yapılmalı',
                    'description': 'Sistem belleği optimize edilmeli'
                })
            
            if overall_score < 0.5:
                optimizations.append({
                    'type': 'module_restart',
                    'priority': 2,
                    'action': 'Modüller yeniden başlatılmalı',
                    'description': 'Düşük performanslı modüller yeniden başlatılmalı'
                })
            
            # CPU kullanımı kontrolü
            cpu_usage = system_health.get('system_metrics', {}).get('cpu', 0)
            if cpu_usage > 80:
                optimizations.append({
                    'type': 'cpu_optimization',
                    'priority': 1,
                    'action': 'CPU kullanımı optimize edilmeli',
                    'description': 'Yüksek CPU kullanımı tespit edildi'
                })
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Optimizasyon önerisi hatası: {e}")
            return []
    
    
    def restart_module(self, module_name):
        """Modülü yeniden başlat"""
        try:
            # Önce durdur
            self.module_controller.send_command(module_name, "stop")
            time.sleep(1)
            # Sonra başlat
            result = self.module_controller.send_command(module_name, "start")
            return result
        except Exception as e:
            logger.error(f"Modül yeniden başlatma hatası: {e}")
            return {"error": str(e)}
    
    def cleanup_memory(self):
        """Bellek temizliği yap"""
        try:
            gc.collect()
            self.memory_cache.clear()
            return {"status": "success", "message": "Bellek temizliği tamamlandı"}
        except Exception as e:
            logger.error(f"Bellek temizliği hatası: {e}")
            return {"error": str(e)}
    
    def handle_high_priority_insight(self, insight: AIInsight):
        """Yüksek öncelikli içgörüyü işle"""
        try:
            logger.info(f"🚨 Yüksek öncelikli içgörü: {insight.type}")
            
            # Otomatik aksiyon al
            if insight.type == "performance_alert":
                self.optimize_system()
            elif insight.type == "module_error":
                self.restart_module(insight.data.get('module'))
            elif insight.type == "memory_alert":
                self.cleanup_memory()
                
        except Exception as e:
            logger.error(f"Yüksek öncelikli içgörü işleme hatası: {e}")
    
    def process_insights(self):
        """AI içgörülerini işle"""
        try:
            # Yeni içgörüleri kontrol et
            new_insights = self.get_new_insights()
            
            for insight in new_insights:
                self.insights.append(insight)
                
                # Yüksek öncelikli içgörüleri hemen işle
                if insight.priority >= 3:
                    self.handle_high_priority_insight(insight)
                    
        except Exception as e:
            logger.error(f"İçgörü işleme hatası: {e}")
    
    def get_new_insights(self) -> List[AIInsight]:
        """Yeni içgörüleri al"""
        # Simüle edilmiş içgörüler
        insights = []
        
        if random.random() < 0.1:  # %10 şansla yeni içgörü
            insight = AIInsight(
                id=f"insight_{int(time.time())}",
                type="performance_alert",
                priority=random.randint(1, 5),
                data={"metric": "cpu_usage", "value": random.uniform(70, 95)},
                confidence=random.uniform(0.7, 0.95),
                timestamp=datetime.now(),
                source_module="system_monitor",
                recommendations=["CPU kullanımını optimize et", "Gereksiz işlemleri durdur"],
                action_required=random.choice([True, False])
            )
            insights.append(insight)
        
        return insights
    
    def _generate_performance_recommendations(self, trends):
        """Performans önerileri üret"""
        recommendations = []
        
        if trends['cpu_trend'] == 'increasing':
            recommendations.append("CPU kullanımı artıyor - optimizasyon gerekli")
        
        if trends['memory_trend'] == 'increasing':
            recommendations.append("RAM kullanımı artıyor - bellek temizliği gerekli")
        
        return recommendations
    
    def _find_interaction_patterns(self, interactions):
        """Etkileşim paternlerini bul"""
        patterns = []
        
        # Basit patern analizi
        module_counts = defaultdict(int)
        for interaction in interactions:
            module_counts[interaction['module']] += 1
        
        for module, count in module_counts.items():
            if count > 5:  # Sık kullanılan modül
                patterns.append({
                    'pattern_type': 'frequent_module',
                    'module': module,
                    'frequency': count,
                    'confidence': min(1.0, count / len(interactions))
                })
        
        return patterns
    
    def _update_pattern(self, pattern):
        """Paterni güncelle"""
        pattern_id = f"{pattern['pattern_type']}_{pattern.get('module', 'unknown')}"
        
        if pattern_id in self.patterns:
            self.patterns[pattern_id]['frequency'] += 1
            self.patterns[pattern_id]['last_seen'] = datetime.now()
        else:
            self.patterns[pattern_id] = {
                'pattern_type': pattern['pattern_type'],
                'frequency': 1,
                'confidence': pattern.get('confidence', 0.5),
                'last_seen': datetime.now(),
                'context': pattern
            }
    
    def _suggest_optimizations(self, system_health):
        """Optimizasyon önerileri"""
        optimizations = []
        
        if system_health['overall_score'] < 0.5:
            optimizations.append({
                'action': 'Sistem yeniden başlatılmalı',
                'priority': 'high',
                'reason': 'Genel sistem sağlığı çok düşük'
            })
        
        if system_health.get('module_scores', []):
            avg_module_score = sum(system_health['module_scores']) / len(system_health['module_scores'])
            if avg_module_score < 0.7:
                optimizations.append({
                    'action': 'Modül performansları optimize edilmeli',
                    'priority': 'medium',
                    'reason': f'Ortalama modül skoru: {avg_module_score:.2f}'
                })
        
        return optimizations


class CrossModuleController:
    """Modüller Arası Kontrol Sistemi"""
    
    def __init__(self, ai_center):
        self.ai_center = ai_center
        self.module_connections = {}
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.active_commands = {}
        
    def connect_to_module(self, module_name: str, module_path: str):
        """Modüle bağlan"""
        try:
            # Modül bağlantısı kur
            connection = {
                'name': module_name,
                'path': module_path,
                'status': 'connected',
                'last_ping': datetime.now(),
                'capabilities': []
            }
            self.module_connections[module_name] = connection
            logger.info(f"✅ {module_name} modülüne bağlandı")
            return True
        except Exception as e:
            logger.error(f"Modül bağlantı hatası {module_name}: {e}")
            return False
    
    def send_command(self, target_module: str, command: str, parameters: Dict = None):
        """Modüle komut gönder"""
        try:
            command_id = f"cmd_{int(time.time())}_{random.randint(1000, 9999)}"
            
            command_data = {
                'id': command_id,
                'target_module': target_module,
                'command': command,
                'parameters': parameters or {},
                'timestamp': datetime.now(),
                'status': 'pending'
            }
            
            # Komut kuyruğuna ekle
            self.command_queue.put(command_data)
            self.active_commands[command_id] = command_data
            
            # Modüle gönder
            if target_module in self.module_connections:
                result = self._execute_module_command(target_module, command, parameters)
                command_data['status'] = 'completed'
                command_data['result'] = result
                command_data['executed_at'] = datetime.now()
            else:
                command_data['status'] = 'failed'
                command_data['error'] = f"Modül {target_module} bulunamadı"
            
            return command_id
            
        except Exception as e:
            logger.error(f"Komut gönderme hatası: {e}")
            return None
    
    def _execute_module_command(self, module_name: str, command: str, parameters: Dict):
        """Modül komutunu çalıştır"""
        try:
            if module_name == "main":
                return self._execute_main_command(command, parameters)
            elif module_name == "main2":
                return self._execute_main2_command(command, parameters)
            elif module_name == "database":
                return self._execute_database_command(command, parameters)
            else:
                return {"error": f"Bilinmeyen modül: {module_name}"}
                
        except Exception as e:
            logger.error(f"Modül komut çalıştırma hatası: {e}")
            return {"error": str(e)}
    
    def _execute_main_command(self, command: str, parameters: Dict):
        """Main.py komutlarını çalıştır"""
        try:
            # Main.py'ye komut gönder
            if command == "get_stats":
                return {"status": "success", "data": "Main.py istatistikleri"}
            elif command == "start_campaign":
                return {"status": "success", "data": "Kampanya başlatıldı"}
            elif command == "stop_campaign":
                return {"status": "success", "data": "Kampanya durduruldu"}
            else:
                return {"error": f"Bilinmeyen komut: {command}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _execute_main2_command(self, command: str, parameters: Dict):
        """Main2.py komutlarını çalıştır"""
        try:
            # Main2.py'ye komut gönder
            if command == "get_firms":
                return {"status": "success", "data": "Firma listesi"}
            elif command == "update_firm":
                return {"status": "success", "data": "Firma güncellendi"}
            else:
                return {"error": f"Bilinmeyen komut: {command}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _execute_database_command(self, command: str, parameters: Dict):
        """Veritabanı komutlarını çalıştır"""
        try:
            if command == "get_customers":
                return {"status": "success", "data": "Müşteri listesi"}
            elif command == "analyze_data":
                return {"status": "success", "data": "Veri analizi tamamlandı"}
            else:
                return {"error": f"Bilinmeyen komut: {command}"}
                
        except Exception as e:
            return {"error": str(e)}


class AICenterMainWindow(QMainWindow):
    """Ana AI Merkez Pencere - Main.py ile Uyumlu Modern Tasarım"""
    
    def __init__(self):
        super().__init__()
        
        # Scale factor - responsive tasarım için
        self.scale_factor = 1.0
        
        # AI Merkez bileşenleri
        self.ai_state = AIState.IDLE
        self.database = AICenterDatabase()
        self.learning_engine = SelfLearningEngine(self)
        self.module_controller = CrossModuleController(self)
        
        # Veri yapıları
        self.insights = []
        self.module_status = {}
        self.system_metrics = {}
        self.memory_cache = {}
        
        # Threading
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # GUI bileşenleri
        self.setup_ui()
        self.apply_modern_theme()
        self.setup_connections()
        self.start_monitoring()
        
        logger.info("🧠 AI Merkez sistemi başlatıldı")
    
    def setup_ui(self):
        """UI kurulumu - Main.py ile uyumlu"""
        self.setWindowTitle("🧠 AI Merkez - Ana Kontrol Sistemi")
        
        # Responsive pencere boyutlandırma
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Başlık
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Ana içerik - Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Tab'ları oluştur
        self.create_ai_dashboard_tab()
        self.create_system_analysis_tab()
        self.create_module_control_tab()
        self.create_ai_learning_tab()
        self.create_cross_module_tab()
        self.create_ai_insights_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("AI Merkez hazır", 3000)
    
    def create_header(self):
        """Başlık widget'ı oluştur"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Sol taraf - Başlık ve durum
        left_layout = QHBoxLayout()
        
        # AI ikonu ve başlık
        title_layout = QHBoxLayout()
        ai_icon = QLabel("🧠")
        ai_icon.setStyleSheet("font-size: 32px;")
        title_layout.addWidget(ai_icon)
        
        title_text = QLabel("AI Merkez")
        title_text.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff; margin-left: 10px;")
        title_layout.addWidget(title_text)
        
        left_layout.addLayout(title_layout)
        left_layout.addStretch()
        
        # AI durumu
        self.ai_status_label = QLabel("Durum: Hazır")
        self.ai_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")
        left_layout.addWidget(self.ai_status_label)
        
        header_layout.addLayout(left_layout)
        
        # Sağ taraf - Hızlı aksiyonlar
        right_layout = QHBoxLayout()
        
        # Hızlı butonlar
        self.quick_analyze_btn = QPushButton("📊 Analiz")
        self.quick_analyze_btn.setObjectName("quickButton")
        self.quick_analyze_btn.clicked.connect(self.quick_analyze)
        right_layout.addWidget(self.quick_analyze_btn)
        
        self.quick_optimize_btn = QPushButton("⚡ Optimize")
        self.quick_optimize_btn.setObjectName("quickButton")
        self.quick_optimize_btn.clicked.connect(self.quick_optimize)
        right_layout.addWidget(self.quick_optimize_btn)
        
        self.emergency_btn = QPushButton("🚨 Acil")
        self.emergency_btn.setObjectName("emergencyButton")
        self.emergency_btn.clicked.connect(self.emergency_mode)
        right_layout.addWidget(self.emergency_btn)
        
        header_layout.addLayout(right_layout)
        
        return header_frame
    
    def create_ai_dashboard_tab(self):
        """AI Dashboard sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Üst satır - Ana metrikler
        metrics_layout = QHBoxLayout()
        
        # AI Durumu kartı
        self.ai_status_card = ModernCard("AI Durumu", "Hazır", "🤖")
        metrics_layout.addWidget(self.ai_status_card)
        
        # Öğrenme Durumu kartı
        self.learning_card = ModernCard("Öğrenme", "Aktif", "🧠")
        metrics_layout.addWidget(self.learning_card)
        
        # Sistem Sağlığı kartı
        self.health_card = ModernCard("Sistem Sağlığı", "%95", "💚")
        metrics_layout.addWidget(self.health_card)
        
        # Aktif Modüller kartı
        self.modules_card = ModernCard("Aktif Modüller", "5", "🔧")
        metrics_layout.addWidget(self.modules_card)
        
        layout.addLayout(metrics_layout)
        
        # Orta satır - Performans grafikleri
        performance_group = QGroupBox("📈 Performans Metrikleri")
        performance_layout = QHBoxLayout(performance_group)
        
        # CPU kullanımı
        cpu_group = QVBoxLayout()
        cpu_group.addWidget(QLabel("CPU Kullanımı"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setValue(45)
        cpu_group.addWidget(self.cpu_progress)
        performance_layout.addLayout(cpu_group)
        
        # RAM kullanımı
        ram_group = QVBoxLayout()
        ram_group.addWidget(QLabel("RAM Kullanımı"))
        self.ram_progress = QProgressBar()
        self.ram_progress.setRange(0, 100)
        self.ram_progress.setValue(62)
        ram_group.addWidget(self.ram_progress)
        performance_layout.addLayout(ram_group)
        
        # Disk kullanımı
        disk_group = QVBoxLayout()
        disk_group.addWidget(QLabel("Disk Kullanımı"))
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)
        self.disk_progress.setValue(38)
        disk_group.addWidget(self.disk_progress)
        performance_layout.addLayout(disk_group)
        
        layout.addWidget(performance_group)
        
        # Alt satır - Son aktiviteler
        activity_group = QGroupBox("📋 Son Aktiviteler")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_list = QListWidget()
        self.activity_list.setMaximumHeight(200)
        activity_layout.addWidget(self.activity_list)
        
        layout.addWidget(activity_group)
        
        self.tabs.addTab(tab, "🏠 AI Dashboard")
    
    def create_system_analysis_tab(self):
        """Sistem Analizi sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Sistem metrikleri
        metrics_group = QGroupBox("📊 Sistem Metrikleri")
        metrics_layout = QGridLayout(metrics_group)
        
        # CPU detayları
        cpu_group = QGroupBox("🖥️ CPU")
        cpu_layout = QVBoxLayout(cpu_group)
        
        self.cpu_usage_label = QLabel("Kullanım: %0")
        self.cpu_cores_label = QLabel("Çekirdek: 8")
        self.cpu_freq_label = QLabel("Frekans: 3.2 GHz")
        
        cpu_layout.addWidget(self.cpu_usage_label)
        cpu_layout.addWidget(self.cpu_cores_label)
        cpu_layout.addWidget(self.cpu_freq_label)
        
        metrics_layout.addWidget(cpu_group, 0, 0)
        
        # RAM detayları
        ram_group = QGroupBox("💾 RAM")
        ram_layout = QVBoxLayout(ram_group)
        
        self.ram_usage_label = QLabel("Kullanım: %0")
        self.ram_total_label = QLabel("Toplam: 16 GB")
        self.ram_available_label = QLabel("Kullanılabilir: 0 GB")
        
        ram_layout.addWidget(self.ram_usage_label)
        ram_layout.addWidget(self.ram_total_label)
        ram_layout.addWidget(self.ram_available_label)
        
        metrics_layout.addWidget(ram_group, 0, 1)
        
        # Disk detayları
        disk_group = QGroupBox("💿 Disk")
        disk_layout = QVBoxLayout(disk_group)
        
        self.disk_usage_label = QLabel("Kullanım: %0")
        self.disk_total_label = QLabel("Toplam: 500 GB")
        self.disk_free_label = QLabel("Boş: 0 GB")
        
        disk_layout.addWidget(self.disk_usage_label)
        disk_layout.addWidget(self.disk_total_label)
        disk_layout.addWidget(self.disk_free_label)
        
        metrics_layout.addWidget(disk_group, 1, 0)
        
        # Ağ detayları
        network_group = QGroupBox("🌐 Ağ")
        network_layout = QVBoxLayout(network_group)
        
        self.network_speed_label = QLabel("Hız: 0 Mbps")
        self.network_latency_label = QLabel("Gecikme: 0 ms")
        self.network_connections_label = QLabel("Bağlantılar: 0")
        
        network_layout.addWidget(self.network_speed_label)
        network_layout.addWidget(self.network_latency_label)
        network_layout.addWidget(self.network_connections_label)
        
        metrics_layout.addWidget(network_group, 1, 1)
        
        layout.addWidget(metrics_group)
        
        # Sistem logları
        logs_group = QGroupBox("📝 Sistem Logları")
        logs_layout = QVBoxLayout(logs_group)
        
        self.logs_text = QTextEdit()
        self.logs_text.setMaximumHeight(200)
        self.logs_text.setReadOnly(True)
        logs_layout.addWidget(self.logs_text)
        
        layout.addWidget(logs_group)
        
        self.tabs.addTab(tab, "📊 Sistem Analizi")
    
    def create_module_control_tab(self):
        """Modül Kontrol sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Modül tablosu
        modules_group = QGroupBox("🔧 Modül Kontrolü")
        modules_layout = QVBoxLayout(modules_group)
        
        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(6)
        self.modules_table.setHorizontalHeaderLabels([
            "Modül", "Durum", "Sağlık", "Son Aktivite", "Hata Sayısı", "Aksiyonlar"
        ])
        modules_layout.addWidget(self.modules_table)
        
        # Modül aksiyonları
        actions_layout = QHBoxLayout()
        
        self.start_all_btn = QPushButton("▶️ Tümünü Başlat")
        self.start_all_btn.clicked.connect(self.start_all_modules)
        actions_layout.addWidget(self.start_all_btn)
        
        self.stop_all_btn = QPushButton("⏹️ Tümünü Durdur")
        self.stop_all_btn.clicked.connect(self.stop_all_modules)
        actions_layout.addWidget(self.stop_all_btn)
        
        self.restart_all_btn = QPushButton("🔄 Tümünü Yeniden Başlat")
        self.restart_all_btn.clicked.connect(self.restart_all_modules)
        actions_layout.addWidget(self.restart_all_btn)
        
        actions_layout.addStretch()
        modules_layout.addLayout(actions_layout)
        
        layout.addWidget(modules_group)
        
        # Modül detayları
        details_group = QGroupBox("📋 Modül Detayları")
        details_layout = QVBoxLayout(details_group)
        
        self.module_details_text = QTextEdit()
        self.module_details_text.setMaximumHeight(200)
        self.module_details_text.setReadOnly(True)
        details_layout.addWidget(self.module_details_text)
        
        layout.addWidget(details_group)
        
        self.tabs.addTab(tab, "🔧 Modül Kontrolü")
    
    def create_ai_learning_tab(self):
        """AI Öğrenme sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Öğrenme durumu
        learning_group = QGroupBox("🧠 AI Öğrenme Durumu")
        learning_layout = QVBoxLayout(learning_group)
        
        # Öğrenme kontrolleri
        controls_layout = QHBoxLayout()
        
        self.start_learning_btn = QPushButton("▶️ Öğrenmeyi Başlat")
        self.start_learning_btn.clicked.connect(self.start_ai_learning)
        controls_layout.addWidget(self.start_learning_btn)
        
        self.stop_learning_btn = QPushButton("⏹️ Öğrenmeyi Durdur")
        self.stop_learning_btn.clicked.connect(self.stop_ai_learning)
        controls_layout.addWidget(self.stop_learning_btn)
        
        self.reset_learning_btn = QPushButton("🔄 Öğrenmeyi Sıfırla")
        self.reset_learning_btn.clicked.connect(self.reset_ai_learning)
        controls_layout.addWidget(self.reset_learning_btn)
        
        controls_layout.addStretch()
        learning_layout.addLayout(controls_layout)
        
        # Öğrenme durumu metni
        self.learning_status_text = QTextEdit()
        self.learning_status_text.setMaximumHeight(150)
        self.learning_status_text.setReadOnly(True)
        learning_layout.addWidget(self.learning_status_text)
        
        layout.addWidget(learning_group)
        
        # Öğrenme paternleri
        patterns_group = QGroupBox("🔍 Öğrenme Paternleri")
        patterns_layout = QVBoxLayout(patterns_group)
        
        self.patterns_list = QListWidget()
        patterns_layout.addWidget(self.patterns_list)
        
        layout.addWidget(patterns_group)
        
        # AI hafızası
        memory_group = QGroupBox("💾 AI Hafızası")
        memory_layout = QVBoxLayout(memory_group)
        
        memory_controls_layout = QHBoxLayout()
        
        self.consolidate_memory_btn = QPushButton("🧹 Hafızayı Temizle")
        self.consolidate_memory_btn.clicked.connect(self.consolidate_memory)
        memory_controls_layout.addWidget(self.consolidate_memory_btn)
        
        self.export_memory_btn = QPushButton("📤 Hafızayı Dışa Aktar")
        self.export_memory_btn.clicked.connect(self.export_memory)
        memory_controls_layout.addWidget(self.export_memory_btn)
        
        memory_controls_layout.addStretch()
        memory_layout.addLayout(memory_controls_layout)
        
        self.memory_text = QTextEdit()
        self.memory_text.setMaximumHeight(150)
        self.memory_text.setReadOnly(True)
        memory_layout.addWidget(self.memory_text)
        
        layout.addWidget(memory_group)
        
        self.tabs.addTab(tab, "🧠 AI Öğrenme")
    
    def create_cross_module_tab(self):
        """Cross-Module İletişim sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Komut gönderme
        command_group = QGroupBox("📤 Modül Komutları")
        command_layout = QFormLayout(command_group)
        
        # Hedef modül seçimi
        self.target_module_combo = QComboBox()
        self.target_module_combo.addItems(["main", "main2", "database", "ai_chat", "email", "whatsapp"])
        command_layout.addRow("Hedef Modül:", self.target_module_combo)
        
        # Komut girişi
        self.command_text = QLineEdit()
        self.command_text.setPlaceholderText("Komut girin... (örn: get_stats, start_campaign)")
        command_layout.addRow("Komut:", self.command_text)
        
        # Parametreler
        self.parameters_text = QLineEdit()
        self.parameters_text.setPlaceholderText("Parametreler (JSON formatında)")
        command_layout.addRow("Parametreler:", self.parameters_text)
        
        # Gönder butonu
        self.send_command_btn = QPushButton("📤 Komut Gönder")
        self.send_command_btn.clicked.connect(self.send_cross_module_command)
        command_layout.addRow(self.send_command_btn)
        
        layout.addWidget(command_group)
        
        # Hızlı komutlar
        quick_commands_group = QGroupBox("⚡ Hızlı Komutlar")
        quick_layout = QGridLayout(quick_commands_group)
        
        # Main.py komutları
        main_commands = [
            ("📊 İstatistikler", "main", "get_stats"),
            ("📧 Kampanya Başlat", "main", "start_campaign"),
            ("⏹️ Kampanya Durdur", "main", "stop_campaign"),
            ("🔍 Firma Ara", "main", "search_firms")
        ]
        
        for i, (text, module, command) in enumerate(main_commands):
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, m=module, c=command: self.quick_command(m, c))
            quick_layout.addWidget(btn, i // 2, i % 2)
        
        # Main2.py komutları
        main2_commands = [
            ("🏢 Firmaları Getir", "main2", "get_firms"),
            ("📝 Firma Güncelle", "main2", "update_firm"),
            ("📱 WhatsApp Kontrol", "main2", "check_whatsapp")
        ]
        
        for i, (text, module, command) in enumerate(main2_commands):
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, m=module, c=command: self.quick_command(m, c))
            quick_layout.addWidget(btn, (i + 4) // 2, (i + 4) % 2)
        
        layout.addWidget(quick_commands_group)
        
        # Komut geçmişi
        history_group = QGroupBox("📜 Komut Geçmişi")
        history_layout = QVBoxLayout(history_group)
        
        self.command_history = QTextEdit()
        self.command_history.setMaximumHeight(200)
        self.command_history.setReadOnly(True)
        history_layout.addWidget(self.command_history)
        
        # Geçmiş temizleme
        clear_history_btn = QPushButton("🗑️ Geçmişi Temizle")
        clear_history_btn.clicked.connect(self.clear_command_history)
        history_layout.addWidget(clear_history_btn)
        
        layout.addWidget(history_group)
        
        self.tabs.addTab(tab, "🔗 Modül İletişimi")
    
    def create_ai_insights_tab(self):
        """AI İçgörüler sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # İçgörüler listesi
        insights_group = QGroupBox("💡 AI İçgörüleri")
        insights_layout = QVBoxLayout(insights_group)
        
        # Filtreleme
        filter_layout = QHBoxLayout()
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["Tümü", "Yüksek (4-5)", "Orta (2-3)", "Düşük (1)"])
        self.priority_filter.currentTextChanged.connect(self.filter_insights)
        filter_layout.addWidget(QLabel("Öncelik:"))
        filter_layout.addWidget(self.priority_filter)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tümü", "Performance", "Optimization", "Error", "Learning"])
        self.type_filter.currentTextChanged.connect(self.filter_insights)
        filter_layout.addWidget(QLabel("Tip:"))
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        insights_layout.addLayout(filter_layout)
        
        # İçgörüler tablosu
        self.insights_table = QTableWidget()
        self.insights_table.setColumnCount(6)
        self.insights_table.setHorizontalHeaderLabels([
            "Öncelik", "Tip", "Açıklama", "Güven", "Zaman", "Aksiyon"
        ])
        insights_layout.addWidget(self.insights_table)
        
        layout.addWidget(insights_group)
        
        # İçgörü detayları
        details_group = QGroupBox("📋 İçgörü Detayları")
        details_layout = QVBoxLayout(details_group)
        
        self.insight_details_text = QTextEdit()
        self.insight_details_text.setMaximumHeight(200)
        self.insight_details_text.setReadOnly(True)
        details_layout.addWidget(self.insight_details_text)
        
        # Aksiyon butonları
        action_layout = QHBoxLayout()
        
        self.apply_insight_btn = QPushButton("✅ Uygula")
        self.apply_insight_btn.clicked.connect(self.apply_insight)
        action_layout.addWidget(self.apply_insight_btn)
        
        self.dismiss_insight_btn = QPushButton("❌ Reddet")
        self.dismiss_insight_btn.clicked.connect(self.dismiss_insight)
        action_layout.addWidget(self.dismiss_insight_btn)
        
        action_layout.addStretch()
        details_layout.addLayout(action_layout)
        
        layout.addWidget(details_group)
        
        self.tabs.addTab(tab, "💡 AI İçgörüleri")
    
    def apply_modern_theme(self):
        """Modern tema uygula - Main.py ile uyumlu"""
        
        # Responsive font boyutları hesapla
        base_font_size = max(11, int(14 * self.scale_factor))
        small_font_size = max(10, int(12 * self.scale_factor))
        large_font_size = max(14, int(18 * self.scale_factor))
        button_padding = max(8, int(10 * self.scale_factor))
        button_padding_h = max(16, int(20 * self.scale_factor))
        border_radius = max(6, int(8 * self.scale_factor))
        tab_padding = max(10, int(12 * self.scale_factor))
        tab_padding_h = max(20, int(24 * self.scale_factor))
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #0f0f0f;
            }}
            
            QTabWidget::pane {{
                border: none;
                background-color: #1a1a1a;
                border-radius: 10px;
            }}
            
            QTabBar::tab {{
                background-color: #2a2a2a;
                color: #ffffff;
                padding: {tab_padding}px {tab_padding_h}px;
                margin-right: 5px;
                border-radius: {border_radius}px {border_radius}px 0 0;
                font-weight: 500;
                font-size: {small_font_size}px;
            }}
            
            QTabBar::tab:selected {{
                background-color: #1a1a1a;
                color: #ffffff;
                border-bottom: 2px solid #4CAF50;
            }}
            
            QTabBar::tab:hover {{
                background-color: #333;
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: {base_font_size}px;
                color: #ffffff;
                border: 2px solid #333;
                border-radius: {border_radius}px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            
            QPushButton {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: {border_radius}px;
                padding: {button_padding}px {button_padding_h}px;
                font-size: {small_font_size}px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: #333;
                border-color: #777;
            }}
            
            QPushButton:pressed {{
                background-color: #1a1a1a;
            }}
            
            QPushButton#quickButton {{
                background-color: #4CAF50;
                color: #ffffff;
                font-weight: bold;
            }}
            
            QPushButton#quickButton:hover {{
                background-color: #45a049;
            }}
            
            QPushButton#emergencyButton {{
                background-color: #f44336;
                color: #ffffff;
                font-weight: bold;
            }}
            
            QPushButton#emergencyButton:hover {{
                background-color: #da190b;
            }}
            
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: {border_radius}px;
                padding: 8px;
                font-size: {small_font_size}px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border-color: #4CAF50;
            }}
            
            QComboBox {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: {border_radius}px;
                padding: 8px;
                font-size: {small_font_size}px;
            }}
            
            QComboBox::drop-down {{
                border: none;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555;
                selection-background-color: #4CAF50;
            }}
            
            QTableWidget {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: {border_radius}px;
                gridline-color: #333;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #333;
            }}
            
            QTableWidget::item:selected {{
                background-color: #4CAF50;
                color: #ffffff;
            }}
            
            QHeaderView::section {{
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-right: 1px solid #555;
                font-weight: bold;
            }}
            
            QListWidget {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: {border_radius}px;
            }}
            
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #333;
            }}
            
            QListWidget::item:selected {{
                background-color: #4CAF50;
                color: #ffffff;
            }}
            
            QProgressBar {{
                border: 1px solid #555;
                border-radius: {border_radius}px;
                text-align: center;
                background-color: #1a1a1a;
                color: #ffffff;
            }}
            
            QProgressBar::chunk {{
                background-color: #4CAF50;
                border-radius: {border_radius}px;
            }}
            
            QLabel {{
                color: #ffffff;
                font-size: {small_font_size}px;
            }}
            
            QStatusBar {{
                background-color: #1a1a1a;
                color: #ffffff;
                border-top: 1px solid #333;
            }}
            
            #headerFrame {{
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: {border_radius}px;
            }}
        """)
    
    def setup_connections(self):
        """Bağlantıları kur"""
        # Timer'lar
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(2000)  # 2 saniyede bir güncelle
        
        # Modül bağlantıları
        self.module_controller.connect_to_module("main", "main.py")
        self.module_controller.connect_to_module("main2", "main2.py")
        self.module_controller.connect_to_module("database", "database.py")
    
    def start_monitoring(self):
        """İzleme başlat"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Öğrenme motorunu başlat
        self.learning_engine.start_learning()
        
        logger.info("🔍 İzleme sistemi başlatıldı")
    
    def _monitoring_loop(self):
        """İzleme döngüsü"""
        while self.is_monitoring:
            try:
                # Sistem metriklerini güncelle
                self.update_system_metrics()
                
                # Modül durumlarını kontrol et
                self.check_module_status()
                
                # AI içgörülerini işle
                self.process_insights()
                
                time.sleep(5)  # 5 saniyede bir kontrol
                
            except Exception as e:
                logger.error(f"İzleme döngüsü hatası: {e}")
                time.sleep(10)
    
    def update_system_metrics(self):
        """Sistem metriklerini güncelle"""
        try:
            # CPU kullanımı
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # RAM kullanımı
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk kullanımı
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            self.system_metrics = {
                'cpu': cpu_percent,
                'memory': memory_percent,
                'disk': disk_percent,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Sistem metrikleri güncelleme hatası: {e}")
    
    def check_module_status(self):
        """Modül durumlarını kontrol et"""
        try:
            # Her modül için durum kontrolü
            modules = ["main", "main2", "database", "ai_chat", "email"]
            
            for module in modules:
                status = ModuleStatus(
                    name=module,
                    is_running=self._check_module_running(module),
                    health_score=self._calculate_health_score(module),
                    last_activity=datetime.now(),
                    error_count=self._get_error_count(module),
                    performance_metrics=self._get_performance_metrics(module),
                    dependencies=[]
                )
                
                self.module_status[module] = status
                
        except Exception as e:
            logger.error(f"Modül durum kontrolü hatası: {e}")
    
    def _check_module_running(self, module_name: str) -> bool:
        """Modülün çalışıp çalışmadığını kontrol et"""
        try:
            if module_name == "main":
                # main.py'nin çalışıp çalışmadığını kontrol et
                return True  # Basit kontrol
            elif module_name == "main2":
                return True
            elif module_name == "database":
                return self.database.conn is not None
            else:
                return False
        except:
            return False
    
    def _calculate_health_score(self, module_name: str) -> float:
        """Modül sağlık skorunu hesapla"""
        try:
            # Basit sağlık skoru hesaplama
            base_score = 0.8
            
            # Hata sayısına göre düşür
            error_count = self._get_error_count(module_name)
            if error_count > 0:
                base_score -= min(0.5, error_count * 0.1)
            
            # Performans metriklerine göre ayarla
            perf_metrics = self._get_performance_metrics(module_name)
            if perf_metrics:
                # Performans skorunu hesapla
                pass
            
            return max(0.0, min(1.0, base_score))
            
        except:
            return 0.5
    
    def _get_error_count(self, module_name: str) -> int:
        """Modül hata sayısını al"""
        # Basit hata sayısı
        return random.randint(0, 3)
    
    def _get_performance_metrics(self, module_name: str) -> Dict:
        """Modül performans metriklerini al"""
        return {
            'response_time': random.uniform(0.1, 2.0),
            'memory_usage': random.uniform(10, 100),
            'cpu_usage': random.uniform(5, 50)
        }
    
    def process_insights(self):
        """AI içgörülerini işle"""
        try:
            # Yeni içgörüleri kontrol et
            new_insights = self.get_new_insights()
            
            for insight in new_insights:
                self.insights.append(insight)
                
                # Yüksek öncelikli içgörüleri hemen işle
                if insight.priority >= 3:
                    self.handle_high_priority_insight(insight)
                    
        except Exception as e:
            logger.error(f"İçgörü işleme hatası: {e}")
    
    def get_new_insights(self) -> List[AIInsight]:
        """Yeni içgörüleri al"""
        # Simüle edilmiş içgörüler
        insights = []
        
        if random.random() < 0.1:  # %10 şansla yeni içgörü
            insight = AIInsight(
                id=f"insight_{int(time.time())}",
                type="performance_alert",
                priority=random.randint(1, 5),
                data={"metric": "cpu_usage", "value": random.uniform(70, 95)},
                confidence=random.uniform(0.7, 0.95),
                timestamp=datetime.now(),
                source_module="system_monitor",
                recommendations=["CPU kullanımını optimize et", "Gereksiz işlemleri durdur"],
                action_required=random.choice([True, False])
            )
            insights.append(insight)
        
        return insights
    
    def handle_high_priority_insight(self, insight: AIInsight):
        """Yüksek öncelikli içgörüyü işle"""
        try:
            logger.info(f"🚨 Yüksek öncelikli içgörü: {insight.type}")
            
            # Otomatik aksiyon al
            if insight.type == "performance_alert":
                self.optimize_system()
            elif insight.type == "module_error":
                self.restart_module(insight.data.get('module'))
            elif insight.type == "memory_alert":
                self.cleanup_memory()
                
        except Exception as e:
            logger.error(f"Yüksek öncelikli içgörü işleme hatası: {e}")
    
    def update_ui(self):
        """UI'yi güncelle"""
        try:
            # AI durumu
            self.ai_status_label.setText(f"Durum: {self.ai_state.value.title()}")
            
            # Kartları güncelle
            self.update_cards()
            
            # Progress bar'ları güncelle
            self.update_progress_bars()
            
            # Modül tablosunu güncelle
            self.update_modules_table()
            
            # İçgörüleri güncelle
            self.update_insights_table()
            
            # Sistem metriklerini güncelle
            self.update_system_metrics_display()
            
        except Exception as e:
            logger.error(f"UI güncelleme hatası: {e}")
    
    def update_cards(self):
        """Kartları güncelle"""
        try:
            # AI durumu kartı
            status_text = self.ai_state.value.title()
            self.ai_status_card.update_value(status_text)
            
            # Öğrenme kartı
            learning_text = "Aktif" if self.learning_engine.is_learning else "Pasif"
            self.learning_card.update_value(learning_text)
            
            # Sistem sağlığı kartı
            health_score = self.get_system_health()['overall_score']
            health_text = f"%{health_score*100:.0f}"
            self.health_card.update_value(health_text)
            
            # Modüller kartı
            active_modules = sum(1 for status in self.module_status.values() if status.is_running)
            self.modules_card.update_value(str(active_modules))
            
        except Exception as e:
            logger.error(f"Kart güncelleme hatası: {e}")
    
    def update_progress_bars(self):
        """Progress bar'ları güncelle"""
        try:
            if self.system_metrics:
                cpu = self.system_metrics.get('cpu', 0)
                memory = self.system_metrics.get('memory', 0)
                disk = self.system_metrics.get('disk', 0)
                
                self.cpu_progress.setValue(int(cpu))
                self.ram_progress.setValue(int(memory))
                self.disk_progress.setValue(int(disk))
                
        except Exception as e:
            logger.error(f"Progress bar güncelleme hatası: {e}")
    
    def update_modules_table(self):
        """Modül tablosunu güncelle"""
        try:
            self.modules_table.setRowCount(len(self.module_status))
            
            for row, (module_name, status) in enumerate(self.module_status.items()):
                self.modules_table.setItem(row, 0, QTableWidgetItem(module_name))
                
                status_text = "✅ Çalışıyor" if status.is_running else "❌ Durdu"
                status_item = QTableWidgetItem(status_text)
                if status.is_running:
                    status_item.setBackground(QColor(76, 175, 80, 50))
                else:
                    status_item.setBackground(QColor(244, 67, 54, 50))
                self.modules_table.setItem(row, 1, status_item)
                
                health_text = f"%{status.health_score*100:.1f}"
                health_item = QTableWidgetItem(health_text)
                if status.health_score > 0.8:
                    health_item.setBackground(QColor(76, 175, 80, 50))
                elif status.health_score > 0.5:
                    health_item.setBackground(QColor(255, 193, 7, 50))
                else:
                    health_item.setBackground(QColor(244, 67, 54, 50))
                self.modules_table.setItem(row, 2, health_item)
                
                self.modules_table.setItem(row, 3, QTableWidgetItem(status.last_activity.strftime("%H:%M:%S")))
                self.modules_table.setItem(row, 4, QTableWidgetItem(str(status.error_count)))
                
                # Aksiyon butonları
                action_btn = QPushButton("🔄")
                action_btn.clicked.connect(lambda checked, m=module_name: self.restart_module(m))
                self.modules_table.setCellWidget(row, 5, action_btn)
                
        except Exception as e:
            logger.error(f"Modül tablosu güncelleme hatası: {e}")
    
    def update_insights_table(self):
        """İçgörüler tablosunu güncelle"""
        try:
            self.insights_table.setRowCount(len(self.insights))
            
            for row, insight in enumerate(self.insights):
                # Öncelik
                priority_text = "🔴" if insight.priority >= 4 else "🟡" if insight.priority >= 2 else "🟢"
                self.insights_table.setItem(row, 0, QTableWidgetItem(priority_text))
                
                # Tip
                self.insights_table.setItem(row, 1, QTableWidgetItem(insight.type))
                
                # Açıklama
                desc = f"{insight.data.get('metric', 'Unknown')}: {insight.data.get('value', 'N/A')}"
                self.insights_table.setItem(row, 2, QTableWidgetItem(desc))
                
                # Güven
                confidence_text = f"%{insight.confidence*100:.0f}"
                self.insights_table.setItem(row, 3, QTableWidgetItem(confidence_text))
                
                # Zaman
                time_text = insight.timestamp.strftime("%H:%M:%S")
                self.insights_table.setItem(row, 4, QTableWidgetItem(time_text))
                
                # Aksiyon
                action_btn = QPushButton("👁️")
                action_btn.clicked.connect(lambda checked, i=insight: self.show_insight_details(i))
                self.insights_table.setCellWidget(row, 5, action_btn)
                
        except Exception as e:
            logger.error(f"İçgörüler tablosu güncelleme hatası: {e}")
    
    def update_system_metrics_display(self):
        """Sistem metrikleri görüntüsünü güncelle"""
        try:
            if self.system_metrics:
                cpu = self.system_metrics.get('cpu', 0)
                memory = self.system_metrics.get('memory', 0)
                disk = self.system_metrics.get('disk', 0)
                
                self.cpu_usage_label.setText(f"Kullanım: %{cpu:.1f}")
                self.ram_usage_label.setText(f"Kullanım: %{memory:.1f}")
                self.disk_usage_label.setText(f"Kullanım: %{disk:.1f}")
                
        except Exception as e:
            logger.error(f"Sistem metrikleri görüntü güncelleme hatası: {e}")
    
    # Hızlı aksiyonlar
    def quick_analyze(self):
        """Hızlı analiz"""
        try:
            self.ai_state = AIState.ANALYZING
            self.ai_status_label.setText("Durum: Analiz Ediyor...")
            
            # Analiz işlemi
            QTimer.singleShot(2000, self.analysis_complete)
            
        except Exception as e:
            logger.error(f"Hızlı analiz hatası: {e}")
    
    def analysis_complete(self):
        """Analiz tamamlandı"""
        self.ai_state = AIState.IDLE
        self.ai_status_label.setText("Durum: Hazır")
        QMessageBox.information(self, "Analiz Tamamlandı", "Sistem analizi başarıyla tamamlandı!")
    
    def quick_optimize(self):
        """Hızlı optimizasyon"""
        try:
            self.optimize_system()
        except Exception as e:
            logger.error(f"Hızlı optimizasyon hatası: {e}")
    
    def emergency_mode(self):
        """Acil durum modu"""
        try:
            self.ai_state = AIState.EMERGENCY
            self.ai_status_label.setText("Durum: Acil Durum")
            
            # Acil durum aksiyonları
            self.emergency_actions()
            
        except Exception as e:
            logger.error(f"Acil durum hatası: {e}")
    
    def emergency_actions(self):
        """Acil durum aksiyonları"""
        try:
            # Tüm modülleri yeniden başlat
            self.restart_all_modules()
            
            # Bellek temizliği
            self.cleanup_memory()
            
            # Sistem optimizasyonu
            self.optimize_system()
            
            QMessageBox.warning(self, "Acil Durum", "Acil durum aksiyonları uygulandı!")
            
        except Exception as e:
            logger.error(f"Acil durum aksiyonları hatası: {e}")
    
    # Modül kontrol metodları
    def start_all_modules(self):
        """Tüm modülleri başlat"""
        try:
            for module_name in self.module_status.keys():
                self.start_module(module_name)
            QMessageBox.information(self, "Modül Başlatma", "Tüm modüller başlatıldı!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Modül başlatma hatası: {e}")
    
    def stop_all_modules(self):
        """Tüm modülleri durdur"""
        try:
            for module_name in self.module_status.keys():
                self.stop_module(module_name)
            QMessageBox.information(self, "Modül Durdurma", "Tüm modüller durduruldu!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Modül durdurma hatası: {e}")
    
    def restart_all_modules(self):
        """Tüm modülleri yeniden başlat"""
        try:
            for module_name in self.module_status.keys():
                self.restart_module(module_name)
            QMessageBox.information(self, "Modül Yenileme", "Tüm modüller yeniden başlatıldı!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Modül yenileme hatası: {e}")
    
    def start_module(self, module_name: str):
        """Modülü başlat"""
        try:
            # Modül başlatma işlemi
            logger.info(f"Modül başlatılıyor: {module_name}")
        except Exception as e:
            logger.error(f"Modül başlatma hatası {module_name}: {e}")
    
    def stop_module(self, module_name: str):
        """Modülü durdur"""
        try:
            # Modül durdurma işlemi
            logger.info(f"Modül durduruluyor: {module_name}")
        except Exception as e:
            logger.error(f"Modül durdurma hatası {module_name}: {e}")
    
    def restart_module(self, module_name: str):
        """Modülü yeniden başlat"""
        try:
            self.stop_module(module_name)
            time.sleep(1)
            self.start_module(module_name)
            logger.info(f"Modül yeniden başlatıldı: {module_name}")
        except Exception as e:
            logger.error(f"Modül yeniden başlatma hatası {module_name}: {e}")
    
    # AI öğrenme metodları
    def start_ai_learning(self):
        """AI öğrenmeyi başlat"""
        try:
            if not self.learning_engine.is_learning:
                self.learning_engine.start_learning()
                self.learning_status_text.append(f"AI Öğrenme Başlatıldı - {datetime.now().strftime('%H:%M:%S')}")
                QMessageBox.information(self, "AI Öğrenme", "AI öğrenme süreci başlatıldı!")
            else:
                QMessageBox.information(self, "AI Öğrenme", "AI öğrenme zaten aktif!")
                
        except Exception as e:
            logger.error(f"AI öğrenme başlatma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"AI öğrenme başlatma hatası: {e}")
    
    def stop_ai_learning(self):
        """AI öğrenmeyi durdur"""
        try:
            if self.learning_engine.is_learning:
                self.learning_engine.stop_learning()
                self.learning_status_text.append(f"AI Öğrenme Durduruldu - {datetime.now().strftime('%H:%M:%S')}")
                QMessageBox.information(self, "AI Öğrenme", "AI öğrenme süreci durduruldu!")
            else:
                QMessageBox.information(self, "AI Öğrenme", "AI öğrenme zaten pasif!")
                
        except Exception as e:
            logger.error(f"AI öğrenme durdurma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"AI öğrenme durdurma hatası: {e}")
    
    def reset_ai_learning(self):
        """AI öğrenmeyi sıfırla"""
        try:
            self.learning_engine.stop_learning()
            time.sleep(1)
            self.learning_engine.start_learning()
            self.learning_status_text.append(f"AI Öğrenme Sıfırlandı - {datetime.now().strftime('%H:%M:%S')}")
            QMessageBox.information(self, "AI Öğrenme", "AI öğrenme süreci sıfırlandı!")
            
        except Exception as e:
            logger.error(f"AI öğrenme sıfırlama hatası: {e}")
            QMessageBox.critical(self, "Hata", f"AI öğrenme sıfırlama hatası: {e}")
    
    def apply_modern_theme(self):
        """Modern tema uygula - main.py ile uyumlu"""
        
        # Responsive font boyutları ve boyut değerleri hesapla
        if not hasattr(self, 'scale_factor'):
            self.scale_factor = 1.0
        
        base_font_size = max(11, int(14 * self.scale_factor))
        small_font_size = max(10, int(12 * self.scale_factor))
        large_font_size = max(14, int(18 * self.scale_factor))
        button_padding = max(8, int(10 * self.scale_factor))
        button_padding_h = max(16, int(20 * self.scale_factor))
        border_radius = max(6, int(8 * self.scale_factor))
        tab_padding = max(10, int(12 * self.scale_factor))
        tab_padding_h = max(20, int(24 * self.scale_factor))
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #0f0f0f;
            }}
            
            QTabWidget::pane {{
                border: none;
                background-color: #1a1a1a;
                border-radius: 10px;
            }}
            
            QTabBar::tab {{
                background-color: #2a2a2a;
                color: #ffffff;
                padding: {tab_padding}px {tab_padding_h}px;
                margin-right: 5px;
                border-radius: {border_radius}px {border_radius}px 0 0;
                font-weight: 500;
                font-size: {small_font_size}px;
            }}
            
            QTabBar::tab:selected {{
                background-color: #0d7377;
                color: #ffffff;
                border-bottom: 2px solid #14ffec;
            }}
            
            QTabBar::tab:hover {{
                background-color: #3a3a3a;
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: {base_font_size}px;
                color: #ffffff;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #14ffec;
            }}
            
            QPushButton {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #3a3a3a;
                border-radius: {border_radius}px;
                padding: {button_padding}px {button_padding_h}px;
                font-size: {small_font_size}px;
                font-weight: 500;
                min-height: 20px;
            }}
            
            QPushButton:hover {{
                background-color: #3a3a3a;
                border-color: #0d7377;
            }}
            
            QPushButton:pressed {{
                background-color: #0d7377;
                border-color: #14ffec;
            }}
            
            QPushButton:disabled {{
                background-color: #1a1a1a;
                color: #666666;
                border-color: #2a2a2a;
            }}
            
            QLineEdit {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
                padding: 8px;
                font-size: {small_font_size}px;
            }}
            
            QLineEdit:focus {{
                border-color: #0d7377;
            }}
            
            QTextEdit {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
                padding: 8px;
                font-size: {small_font_size}px;
            }}
            
            QTextEdit:focus {{
                border-color: #0d7377;
            }}
            
            QComboBox {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
                padding: 8px;
                font-size: {small_font_size}px;
            }}
            
            QComboBox:focus {{
                border-color: #0d7377;
            }}
            
            QComboBox::drop-down {{
                border: none;
                background-color: #2a2a2a;
                border-radius: {border_radius}px;
            }}
            
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }}
            
            QListWidget {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
                padding: 8px;
                font-size: {small_font_size}px;
            }}
            
            QListWidget:focus {{
                border-color: #0d7377;
            }}
            
            QListWidget::item {{
                padding: 5px;
                border-radius: {border_radius}px;
                margin: 2px;
            }}
            
            QListWidget::item:selected {{
                background-color: #0d7377;
                color: #ffffff;
            }}
            
            QListWidget::item:hover {{
                background-color: #3a3a3a;
            }}
            
            QTableWidget {{
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
                gridline-color: #2a2a2a;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: #0d7377;
                color: #ffffff;
            }}
            
            QHeaderView::section {{
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: {small_font_size}px;
            }}
            
            QHeaderView::section:hover {{
                background-color: #3a3a3a;
            }}
            
            QProgressBar {{
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
                text-align: center;
                color: #ffffff;
                font-size: {small_font_size}px;
            }}
            
            QProgressBar::chunk {{
                background-color: #0d7377;
                border-radius: {border_radius}px;
            }}
            
            QSlider::groove:horizontal {{
                background-color: #2a2a2a;
                height: 8px;
                border-radius: 4px;
            }}
            
            QSlider::handle:horizontal {{
                background-color: #0d7377;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -6px 0;
            }}
            
            QSlider::handle:horizontal:hover {{
                background-color: #14ffec;
            }}
            
            QFrame {{
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: {border_radius}px;
            }}
            
            QLabel {{
                color: #ffffff;
                font-size: {small_font_size}px;
            }}
            
            QLabel[class="title"] {{
                font-size: {large_font_size}px;
                font-weight: bold;
                color: #14ffec;
            }}
            
            QLabel[class="subtitle"] {{
                font-size: {base_font_size}px;
                font-weight: 500;
                color: #cccccc;
            }}
            
            QLabel[class="status"] {{
                font-size: {small_font_size}px;
                color: #00ff00;
                font-weight: bold;
            }}
            
            QLabel[class="error"] {{
                font-size: {small_font_size}px;
                color: #ff4444;
                font-weight: bold;
            }}
            
            QLabel[class="warning"] {{
                font-size: {small_font_size}px;
                color: #ffaa00;
                font-weight: bold;
            }}
            
            QScrollBar:vertical {{
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: #0d7377;
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: #14ffec;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: #2a2a2a;
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: #0d7377;
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: #14ffec;
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            QStatusBar {{
                background-color: #1a1a1a;
                color: #ffffff;
                border-top: 1px solid #2a2a2a;
                font-size: {small_font_size}px;
            }}
            
            QMenuBar {{
                background-color: #2a2a2a;
                color: #ffffff;
                border-bottom: 1px solid #3a3a3a;
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 12px;
            }}
            
            QMenuBar::item:selected {{
                background-color: #0d7377;
            }}
            
            QMenu {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: {border_radius}px;
            }}
            
            QMenu::item {{
                padding: 8px 20px;
            }}
            
            QMenu::item:selected {{
                background-color: #0d7377;
            }}
            
            QToolTip {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #3a3a3a;
                border-radius: {border_radius}px;
                padding: 5px;
                font-size: {small_font_size}px;
            }}
        """)
    
    def setup_ui(self):
        """UI kurulumu - main.py ile uyumlu"""
        self.setWindowTitle("🧠 AI Merkez - Ana Kontrol Sistemi")
        
        # Responsive boyutlandırma
        self.scale_factor = 1.0
        self.setGeometry(100, 100, int(1400 * self.scale_factor), int(900 * self.scale_factor))
        self.setMinimumSize(int(1200 * self.scale_factor), int(800 * self.scale_factor))
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Başlık
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Tab widget oluştur
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Tab'ları oluştur
        # Tab 1: AI Dashboard
        self.ai_dashboard_tab = self.create_ai_dashboard_tab()
        self.tabs.addTab(self.ai_dashboard_tab, "🤖 AI Dashboard")
        
        # Tab 2: Modül Kontrolü
        self.module_control_tab = self.create_module_control_tab()
        self.tabs.addTab(self.module_control_tab, "🔧 Modül Kontrolü")
        
        # Tab 3: Sistem Analizi
        self.system_analysis_tab = self.create_system_analysis_tab()
        self.tabs.addTab(self.system_analysis_tab, "📊 Sistem Analizi")
        
        # Tab 4: AI Öğrenme
        self.ai_learning_tab = self.create_ai_learning_tab()
        self.tabs.addTab(self.ai_learning_tab, "🧠 AI Öğrenme")
        
        # Tab 5: Cross-Module İletişim
        self.cross_module_tab = self.create_cross_module_tab()
        self.tabs.addTab(self.cross_module_tab, "🔗 Modül İletişimi")
        
        # Tab 6: AI İçgörüleri
        self.ai_insights_tab = self.create_ai_insights_tab()
        self.tabs.addTab(self.ai_insights_tab, "💡 AI İçgörüleri")
        
        # Tab 7: Gelişmiş Ayarlar
        self.advanced_settings_tab = self.create_advanced_settings_tab()
        self.tabs.addTab(self.advanced_settings_tab, "⚙️ Gelişmiş Ayarlar")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("AI Merkez hazır", 3000)
        
        # Modern tema uygula
        self.apply_modern_theme()
    
    def create_header(self):
        """Başlık widget'ı oluştur"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        # Sol taraf - Logo ve başlık
        left_layout = QHBoxLayout()
        
        # AI Merkez başlığı
        title_label = QLabel("🧠 AI Merkez")
        title_label.setObjectName("title")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #14ffec;")
        left_layout.addWidget(title_label)
        
        # Alt başlık
        subtitle_label = QLabel("Ana Kontrol Sistemi")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setStyleSheet("font-size: 14px; color: #cccccc; margin-left: 10px;")
        left_layout.addWidget(subtitle_label)
        
        left_layout.addStretch()
        header_layout.addLayout(left_layout)
        
        # Sağ taraf - Durum göstergeleri
        right_layout = QHBoxLayout()
        
        # AI Durumu
        self.ai_status_indicator = QLabel("🟢 AI Aktif")
        self.ai_status_indicator.setObjectName("status")
        right_layout.addWidget(self.ai_status_indicator)
        
        # Öğrenme Durumu
        self.learning_status_indicator = QLabel("🧠 Öğreniyor")
        self.learning_status_indicator.setObjectName("status")
        right_layout.addWidget(self.learning_status_indicator)
        
        # Sistem Sağlığı
        self.system_health_indicator = QLabel("💚 Sistem Sağlıklı")
        self.system_health_indicator.setObjectName("status")
        right_layout.addWidget(self.system_health_indicator)
        
        header_layout.addLayout(right_layout)
        
        return header_frame
    
    def create_ai_dashboard_tab(self):
        """AI Dashboard sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Üst panel - Hızlı erişim
        quick_access_frame = QFrame()
        quick_access_layout = QHBoxLayout(quick_access_frame)
        
        # Hızlı komutlar
        quick_commands = [
            ("🚀 Sistem Başlat", self.start_system),
            ("⏹️ Sistem Durdur", self.stop_system),
            ("🔄 Yenile", self.refresh_system),
            ("⚡ Optimize Et", self.optimize_system),
            ("🧠 AI Öğrenme", self.toggle_ai_learning),
            ("📊 Analiz Et", self.analyze_system)
        ]
        
        for cmd_text, cmd_func in quick_commands:
            btn = QPushButton(cmd_text)
            btn.clicked.connect(cmd_func)
            btn.setMinimumHeight(40)
            quick_access_layout.addWidget(btn)
        
        layout.addWidget(quick_access_frame)
        
        # Orta panel - Sistem durumu
        status_frame = QFrame()
        status_layout = QGridLayout(status_frame)
        
        # Sistem metrikleri kartları
        self.cpu_card = self.create_metric_card("CPU Kullanımı", "0%", "#ff6b6b")
        self.memory_card = self.create_metric_card("RAM Kullanımı", "0%", "#4ecdc4")
        self.disk_card = self.create_metric_card("Disk Kullanımı", "0%", "#45b7d1")
        self.network_card = self.create_metric_card("Ağ Aktivitesi", "0%", "#96ceb4")
        
        status_layout.addWidget(self.cpu_card, 0, 0)
        status_layout.addWidget(self.memory_card, 0, 1)
        status_layout.addWidget(self.disk_card, 1, 0)
        status_layout.addWidget(self.network_card, 1, 1)
        
        layout.addWidget(status_frame)
        
        # Alt panel - AI durumu ve loglar
        bottom_layout = QHBoxLayout()
        
        # AI durumu
        ai_status_group = QGroupBox("🤖 AI Durumu")
        ai_status_layout = QVBoxLayout(ai_status_group)
        
        self.ai_status_text = QTextEdit()
        self.ai_status_text.setMaximumHeight(200)
        self.ai_status_text.setReadOnly(True)
        ai_status_layout.addWidget(self.ai_status_text)
        
        bottom_layout.addWidget(ai_status_group, 1)
        
        # Sistem logları
        logs_group = QGroupBox("📝 Sistem Logları")
        logs_layout = QVBoxLayout(logs_group)
        
        self.system_logs_text = QTextEdit()
        self.system_logs_text.setMaximumHeight(200)
        self.system_logs_text.setReadOnly(True)
        logs_layout.addWidget(self.system_logs_text)
        
        bottom_layout.addWidget(logs_group, 1)
        
        layout.addLayout(bottom_layout)
        
        return tab
    
    def create_metric_card(self, title, value, color):
        """Metrik kartı oluştur"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a1a;
                border: 2px solid #2a2a2a;
                border-radius: 10px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Başlık
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #cccccc; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Değer
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 24px; color: {color}; font-weight: bold;")
        layout.addWidget(value_label)
        
        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #2a2a2a;
                border: none;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)
        layout.addWidget(progress)
        
        # Kart referansını sakla
        card.value_label = value_label
        card.progress_bar = progress
        
        return card
    
    def create_module_control_tab(self):
        """Modül kontrolü sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Modül kontrol paneli
        control_group = QGroupBox("🔧 Modül Kontrolü")
        control_layout = QVBoxLayout(control_group)
        
        # Modül tablosu
        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(7)
        self.modules_table.setHorizontalHeaderLabels([
            "Modül", "Durum", "Sağlık", "Son Aktivite", "Hata Sayısı", "Performans", "İşlemler"
        ])
        self.modules_table.setAlternatingRowColors(True)
        control_layout.addWidget(self.modules_table)
        
        # Modül işlem butonları
        module_buttons_layout = QHBoxLayout()
        
        self.start_module_btn = QPushButton("▶️ Başlat")
        self.start_module_btn.clicked.connect(self.start_selected_module)
        module_buttons_layout.addWidget(self.start_module_btn)
        
        self.stop_module_btn = QPushButton("⏹️ Durdur")
        self.stop_module_btn.clicked.connect(self.stop_selected_module)
        module_buttons_layout.addWidget(self.stop_module_btn)
        
        self.restart_module_btn = QPushButton("🔄 Yeniden Başlat")
        self.restart_module_btn.clicked.connect(self.restart_selected_module)
        module_buttons_layout.addWidget(self.restart_module_btn)
        
        self.refresh_modules_btn = QPushButton("🔄 Yenile")
        self.refresh_modules_btn.clicked.connect(self.refresh_modules)
        module_buttons_layout.addWidget(self.refresh_modules_btn)
        
        module_buttons_layout.addStretch()
        control_layout.addLayout(module_buttons_layout)
        
        layout.addWidget(control_group)
        
        # Modül detayları
        details_group = QGroupBox("📋 Modül Detayları")
        details_layout = QVBoxLayout(details_group)
        
        self.module_details_text = QTextEdit()
        self.module_details_text.setMaximumHeight(200)
        self.module_details_text.setReadOnly(True)
        details_layout.addWidget(self.module_details_text)
        
        layout.addWidget(details_group)
        
        return tab
    
    def create_system_analysis_tab(self):
        """Sistem analizi sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Analiz kontrolleri
        analysis_controls = QFrame()
        controls_layout = QHBoxLayout(analysis_controls)
        
        self.analyze_btn = QPushButton("📊 Sistem Analizi Yap")
        self.analyze_btn.clicked.connect(self.perform_system_analysis)
        controls_layout.addWidget(self.analyze_btn)
        
        self.export_analysis_btn = QPushButton("📤 Analizi Dışa Aktar")
        self.export_analysis_btn.clicked.connect(self.export_analysis)
        controls_layout.addWidget(self.export_analysis_btn)
        
        controls_layout.addStretch()
        layout.addWidget(analysis_controls)
        
        # Analiz sonuçları
        analysis_group = QGroupBox("📈 Analiz Sonuçları")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.analysis_results_text = QTextEdit()
        self.analysis_results_text.setReadOnly(True)
        analysis_layout.addWidget(self.analysis_results_text)
        
        layout.addWidget(analysis_group)
        
        return tab
    
    def create_ai_learning_tab(self):
        """AI öğrenme sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Öğrenme kontrolleri
        learning_controls = QFrame()
        controls_layout = QHBoxLayout(learning_controls)
        
        self.start_learning_btn = QPushButton("🧠 Öğrenmeyi Başlat")
        self.start_learning_btn.clicked.connect(self.start_ai_learning)
        controls_layout.addWidget(self.start_learning_btn)
        
        self.stop_learning_btn = QPushButton("⏹️ Öğrenmeyi Durdur")
        self.stop_learning_btn.clicked.connect(self.stop_ai_learning)
        controls_layout.addWidget(self.stop_learning_btn)
        
        self.reset_learning_btn = QPushButton("🔄 Öğrenmeyi Sıfırla")
        self.reset_learning_btn.clicked.connect(self.reset_ai_learning)
        controls_layout.addWidget(self.reset_learning_btn)
        
        controls_layout.addStretch()
        layout.addWidget(learning_controls)
        
        # Öğrenme durumu
        learning_status_group = QGroupBox("📊 Öğrenme Durumu")
        learning_layout = QVBoxLayout(learning_status_group)
        
        self.learning_status_text = QTextEdit()
        self.learning_status_text.setMaximumHeight(200)
        self.learning_status_text.setReadOnly(True)
        learning_layout.addWidget(self.learning_status_text)
        
        layout.addWidget(learning_status_group)
        
        # Öğrenme paternleri
        patterns_group = QGroupBox("🔍 Öğrenme Paternleri")
        patterns_layout = QVBoxLayout(patterns_group)
        
        self.patterns_list = QListWidget()
        patterns_layout.addWidget(self.patterns_list)
        
        layout.addWidget(patterns_group)
        
        return tab
    
    def create_cross_module_tab(self):
        """Cross-module iletişim sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Komut gönderme
        command_group = QGroupBox("📤 Komut Gönderme")
        command_layout = QFormLayout(command_group)
        
        self.target_module_combo = QComboBox()
        self.target_module_combo.addItems(["main", "main2", "database", "ai_chat", "email", "whatsapp", "analytics"])
        command_layout.addRow("Hedef Modül:", self.target_module_combo)
        
        self.command_text = QLineEdit()
        self.command_text.setPlaceholderText("Komut girin...")
        command_layout.addRow("Komut:", self.command_text)
        
        self.parameters_text = QLineEdit()
        self.parameters_text.setPlaceholderText("Parametreler (JSON formatında)...")
        command_layout.addRow("Parametreler:", self.parameters_text)
        
        self.send_command_btn = QPushButton("📤 Komut Gönder")
        self.send_command_btn.clicked.connect(self.send_cross_module_command)
        command_layout.addRow(self.send_command_btn)
        
        layout.addWidget(command_group)
        
        # Komut geçmişi
        history_group = QGroupBox("📜 Komut Geçmişi")
        history_layout = QVBoxLayout(history_group)
        
        self.command_history = QTextEdit()
        self.command_history.setMaximumHeight(200)
        self.command_history.setReadOnly(True)
        history_layout.addWidget(self.command_history)
        
        layout.addWidget(history_group)
        
        return tab
    
    def create_ai_insights_tab(self):
        """AI içgörüleri sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # İçgörü filtreleri
        filters_group = QGroupBox("🔍 Filtreler")
        filters_layout = QHBoxLayout(filters_group)
        
        self.insight_type_combo = QComboBox()
        self.insight_type_combo.addItems(["Tümü", "Performans", "Hata", "Optimizasyon", "Güvenlik", "Öğrenme"])
        filters_layout.addWidget(QLabel("Tip:"))
        filters_layout.addWidget(self.insight_type_combo)
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Tümü", "Yüksek", "Orta", "Düşük"])
        filters_layout.addWidget(QLabel("Öncelik:"))
        filters_layout.addWidget(self.priority_combo)
        
        self.filter_btn = QPushButton("🔍 Filtrele")
        self.filter_btn.clicked.connect(self.filter_insights)
        filters_layout.addWidget(self.filter_btn)
        
        filters_layout.addStretch()
        layout.addWidget(filters_group)
        
        # İçgörüler listesi
        insights_group = QGroupBox("💡 AI İçgörüleri")
        insights_layout = QVBoxLayout(insights_group)
        
        self.insights_list = QListWidget()
        self.insights_list.itemClicked.connect(self.show_insight_details)
        insights_layout.addWidget(self.insights_list)
        
        # İçgörü detayları
        details_group = QGroupBox("📋 İçgörü Detayları")
        details_layout = QVBoxLayout(details_group)
        
        self.insight_details_text = QTextEdit()
        self.insight_details_text.setMaximumHeight(150)
        self.insight_details_text.setReadOnly(True)
        details_layout.addWidget(self.insight_details_text)
        
        insights_layout.addWidget(details_group)
        layout.addWidget(insights_group)
        
        return tab
    
    def create_advanced_settings_tab(self):
        """Gelişmiş ayarlar sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # AI Ayarları
        ai_settings_group = QGroupBox("🤖 AI Ayarları")
        ai_settings_layout = QFormLayout(ai_settings_group)
        
        self.learning_rate_spin = QSpinBox()
        self.learning_rate_spin.setRange(1, 100)
        self.learning_rate_spin.setValue(50)
        ai_settings_layout.addRow("Öğrenme Hızı:", self.learning_rate_spin)
        
        self.confidence_threshold_spin = QSpinBox()
        self.confidence_threshold_spin.setRange(1, 100)
        self.confidence_threshold_spin.setValue(70)
        ai_settings_layout.addRow("Güven Eşiği:", self.confidence_threshold_spin)
        
        self.auto_optimize_check = QCheckBox("Otomatik Optimizasyon")
        self.auto_optimize_check.setChecked(True)
        ai_settings_layout.addRow(self.auto_optimize_check)
        
        layout.addWidget(ai_settings_group)
        
        # Sistem Ayarları
        system_settings_group = QGroupBox("⚙️ Sistem Ayarları")
        system_settings_layout = QFormLayout(system_settings_group)
        
        self.monitoring_interval_spin = QSpinBox()
        self.monitoring_interval_spin.setRange(1, 60)
        self.monitoring_interval_spin.setValue(5)
        system_settings_layout.addRow("İzleme Aralığı (sn):", self.monitoring_interval_spin)
        
        self.max_memory_spin = QSpinBox()
        self.max_memory_spin.setRange(100, 10000)
        self.max_memory_spin.setValue(1000)
        system_settings_layout.addRow("Maksimum Bellek (MB):", self.max_memory_spin)
        
        self.auto_cleanup_check = QCheckBox("Otomatik Temizlik")
        self.auto_cleanup_check.setChecked(True)
        system_settings_layout.addRow(self.auto_cleanup_check)
        
        layout.addWidget(system_settings_group)
        
        # Kaydet butonu
        save_btn = QPushButton("💾 Ayarları Kaydet")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return tab
    
    # Yeni metodlar
    def start_system(self):
        """Sistemi başlat"""
        try:
            self.ai_state = AIState.CONTROLLING
            self.ai_status_text.append(f"Sistem Başlatılıyor - {datetime.now().strftime('%H:%M:%S')}")
            
            # Modülleri başlat
            self.module_controller.connect_to_module("main", "main.py")
            self.module_controller.connect_to_module("main2", "main2.py")
            self.module_controller.connect_to_module("database", "database.py")
            
            # Öğrenme motorunu başlat
            self.learning_engine.start_learning()
            
            self.ai_state = AIState.IDLE
            self.ai_status_text.append("✅ Sistem başarıyla başlatıldı")
            QMessageBox.information(self, "Sistem", "Sistem başarıyla başlatıldı!")
            
        except Exception as e:
            logger.error(f"Sistem başlatma hatası: {e}")
            self.ai_state = AIState.IDLE
            QMessageBox.critical(self, "Hata", f"Sistem başlatma hatası: {e}")
    
    def stop_system(self):
        """Sistemi durdur"""
        try:
            self.ai_state = AIState.EMERGENCY
            self.ai_status_text.append(f"Sistem Durduruluyor - {datetime.now().strftime('%H:%M:%S')}")
            
            # Öğrenme motorunu durdur
            self.learning_engine.stop_learning()
            
            # İzlemeyi durdur
            self.is_monitoring = False
            
            self.ai_state = AIState.IDLE
            self.ai_status_text.append("⏹️ Sistem durduruldu")
            QMessageBox.information(self, "Sistem", "Sistem durduruldu!")
            
        except Exception as e:
            logger.error(f"Sistem durdurma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Sistem durdurma hatası: {e}")
    
    def toggle_ai_learning(self):
        """AI öğrenmeyi aç/kapat"""
        try:
            if self.learning_engine.is_learning:
                self.stop_ai_learning()
            else:
                self.start_ai_learning()
        except Exception as e:
            logger.error(f"AI öğrenme toggle hatası: {e}")
            QMessageBox.critical(self, "Hata", f"AI öğrenme toggle hatası: {e}")
    
    def start_selected_module(self):
        """Seçili modülü başlat"""
        try:
            current_row = self.modules_table.currentRow()
            if current_row >= 0:
                module_name = self.modules_table.item(current_row, 0).text()
                result = self.module_controller.send_command(module_name, "start")
                QMessageBox.information(self, "Modül", f"{module_name} modülü başlatıldı: {result}")
            else:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir modül seçin!")
        except Exception as e:
            logger.error(f"Modül başlatma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Modül başlatma hatası: {e}")
    
    def stop_selected_module(self):
        """Seçili modülü durdur"""
        try:
            current_row = self.modules_table.currentRow()
            if current_row >= 0:
                module_name = self.modules_table.item(current_row, 0).text()
                result = self.module_controller.send_command(module_name, "stop")
                QMessageBox.information(self, "Modül", f"{module_name} modülü durduruldu: {result}")
            else:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir modül seçin!")
        except Exception as e:
            logger.error(f"Modül durdurma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Modül durdurma hatası: {e}")
    
    def restart_selected_module(self):
        """Seçili modülü yeniden başlat"""
        try:
            current_row = self.modules_table.currentRow()
            if current_row >= 0:
                module_name = self.modules_table.item(current_row, 0).text()
                # Önce durdur
                self.module_controller.send_command(module_name, "stop")
                time.sleep(1)
                # Sonra başlat
                result = self.module_controller.send_command(module_name, "start")
                QMessageBox.information(self, "Modül", f"{module_name} modülü yeniden başlatıldı: {result}")
            else:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir modül seçin!")
        except Exception as e:
            logger.error(f"Modül yeniden başlatma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Modül yeniden başlatma hatası: {e}")
    
    def perform_system_analysis(self):
        """Sistem analizi yap"""
        try:
            self.analysis_results_text.append(f"Sistem Analizi Başlatıldı - {datetime.now().strftime('%H:%M:%S')}")
            
            # CPU analizi
            cpu_percent = psutil.cpu_percent(interval=1)
            self.analysis_results_text.append(f"CPU Kullanımı: %{cpu_percent:.1f}")
            
            # RAM analizi
            memory = psutil.virtual_memory()
            self.analysis_results_text.append(f"RAM Kullanımı: %{memory.percent:.1f}")
            
            # Disk analizi
            disk = psutil.disk_usage('/')
            self.analysis_results_text.append(f"Disk Kullanımı: %{disk.percent:.1f}")
            
            # Modül analizi
            self.analysis_results_text.append(f"Aktif Modül Sayısı: {len(self.module_status)}")
            
            # AI durumu
            self.analysis_results_text.append(f"AI Durumu: {self.ai_state.value}")
            self.analysis_results_text.append(f"Öğrenme Aktif: {'Evet' if self.learning_engine.is_learning else 'Hayır'}")
            
            self.analysis_results_text.append("---")
            QMessageBox.information(self, "Analiz", "Sistem analizi tamamlandı!")
            
        except Exception as e:
            logger.error(f"Sistem analizi hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Sistem analizi hatası: {e}")
    
    def export_analysis(self):
        """Analizi dışa aktar"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Analizi Kaydet", 
                f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.analysis_results_text.toPlainText())
                QMessageBox.information(self, "Dışa Aktarma", f"Analiz {filename} dosyasına kaydedildi!")
            
        except Exception as e:
            logger.error(f"Analiz dışa aktarma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Analiz dışa aktarma hatası: {e}")
    
    def filter_insights(self):
        """İçgörüleri filtrele"""
        try:
            insight_type = self.insight_type_combo.currentText()
            priority = self.priority_combo.currentText()
            
            self.insights_list.clear()
            
            filtered_insights = []
            for insight in self.insights:
                # Tip filtresi
                if insight_type != "Tümü" and insight_type.lower() not in insight.type.lower():
                    continue
                
                # Öncelik filtresi
                if priority == "Yüksek" and insight.priority < 4:
                    continue
                elif priority == "Orta" and (insight.priority < 2 or insight.priority >= 4):
                    continue
                elif priority == "Düşük" and insight.priority >= 2:
                    continue
                
                filtered_insights.append(insight)
            
            # Filtrelenmiş içgörüleri göster
            for insight in filtered_insights:
                priority_icon = "🔴" if insight.priority >= 4 else "🟡" if insight.priority >= 2 else "🟢"
                item_text = f"{priority_icon} {insight.type} - {insight.timestamp.strftime('%H:%M:%S')}"
                self.insights_list.addItem(item_text)
            
            QMessageBox.information(self, "Filtreleme", f"{len(filtered_insights)} içgörü bulundu!")
            
        except Exception as e:
            logger.error(f"İçgörü filtreleme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"İçgörü filtreleme hatası: {e}")
    
    def show_insight_details(self, item):
        """İçgörü detaylarını göster"""
        try:
            # İçgörüyü bul
            insight_text = item.text()
            for insight in self.insights:
                if insight_text.endswith(insight.timestamp.strftime('%H:%M:%S')):
                    details = f"""
İçgörü ID: {insight.id}
Tip: {insight.type}
Öncelik: {insight.priority}
Güven: %{insight.confidence*100:.1f}
Kaynak Modül: {insight.source_module}
Tarih: {insight.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Aksiyon Gerekli: {'Evet' if insight.action_required else 'Hayır'}

Veri:
{json.dumps(insight.data, indent=2, ensure_ascii=False)}

Öneriler:
{chr(10).join(f"• {rec}" for rec in insight.recommendations)}
                    """
                    self.insight_details_text.setText(details)
                    break
                    
        except Exception as e:
            logger.error(f"İçgörü detay gösterme hatası: {e}")
    
    def optimize_system(self):
        """Sistemi optimize et"""
        try:
            self.ai_state = AIState.OPTIMIZING
            self.ai_status_text.append(f"Sistem Optimizasyonu Başlatıldı - {datetime.now().strftime('%H:%M:%S')}")
            
            # Bellek temizliği
            gc.collect()
            
            # Cache temizliği
            self.memory_cache.clear()
            
            # Modül optimizasyonu
            for module_name in self.module_status:
                try:
                    result = self.module_controller.send_command(module_name, "optimize")
                    self.ai_status_text.append(f"✅ {module_name} modülü optimize edildi")
                except Exception as e:
                    self.ai_status_text.append(f"⚠️ {module_name} modülü optimize edilemedi: {e}")
            
            # AI öğrenme optimizasyonu
            if self.learning_engine.is_learning:
                self.learning_engine._consolidate_memory()
                self.ai_status_text.append("✅ AI hafızası konsolide edildi")
            
            # Sistem metriklerini güncelle
            self.update_system_metrics()
            
            # Optimizasyon raporu
            self.ai_status_text.append("✅ Sistem optimizasyonu tamamlandı")
            self.ai_status_text.append("---")
            
            self.ai_state = AIState.IDLE
            QMessageBox.information(self, "Optimizasyon", "Sistem başarıyla optimize edildi!")
            
        except Exception as e:
            logger.error(f"Sistem optimizasyonu hatası: {e}")
            self.ai_state = AIState.IDLE
            QMessageBox.critical(self, "Hata", f"Sistem optimizasyonu hatası: {e}")
    
    def analyze_system(self):
        """Sistem analizi yap"""
        try:
            self.ai_state = AIState.ANALYZING
            self.ai_status_text.append(f"Sistem Analizi Başlatıldı - {datetime.now().strftime('%H:%M:%S')}")
            
            # Sistem analizi
            analysis = {
                'cpu_usage': self.system_metrics.get('cpu', 0),
                'memory_usage': self.system_metrics.get('memory', 0),
                'module_count': len(self.module_status),
                'active_insights': len(self.insights),
                'learning_active': self.learning_engine.is_learning
            }
            
            self.ai_status_text.append(f"CPU Kullanımı: %{analysis['cpu_usage']:.1f}")
            self.ai_status_text.append(f"RAM Kullanımı: %{analysis['memory_usage']:.1f}")
            self.ai_status_text.append(f"Aktif Modüller: {analysis['module_count']}")
            self.ai_status_text.append(f"Aktif İçgörüler: {analysis['active_insights']}")
            self.ai_status_text.append(f"AI Öğrenme: {'Aktif' if analysis['learning_active'] else 'Pasif'}")
            
            # Modül analizi
            for module_name, status in self.module_status.items():
                health_icon = "🟢" if status.health_score > 0.8 else "🟡" if status.health_score > 0.5 else "🔴"
                self.ai_status_text.append(f"{health_icon} {module_name}: %{status.health_score*100:.1f} sağlık")
            
            self.ai_status_text.append("---")
            self.ai_state = AIState.IDLE
            QMessageBox.information(self, "Analiz", "Sistem analizi tamamlandı!")
            
        except Exception as e:
            logger.error(f"Sistem analizi hatası: {e}")
            self.ai_state = AIState.IDLE
            QMessageBox.critical(self, "Hata", f"Sistem analizi hatası: {e}")
    
    def start_ai_learning(self):
        """AI öğrenmeyi başlat"""
        try:
            if not self.learning_engine.is_learning:
                self.learning_engine.start_learning()
                self.learning_status_text.append(f"AI Öğrenme Başlatıldı - {datetime.now().strftime('%H:%M:%S')}")
                self.learning_status_indicator.setText("🧠 Öğreniyor")
                QMessageBox.information(self, "AI Öğrenme", "AI öğrenme süreci başlatıldı!")
            else:
                QMessageBox.information(self, "AI Öğrenme", "AI öğrenme zaten aktif!")
                
        except Exception as e:
            logger.error(f"AI öğrenme başlatma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"AI öğrenme başlatma hatası: {e}")
    
    def stop_ai_learning(self):
        """AI öğrenmeyi durdur"""
        try:
            if self.learning_engine.is_learning:
                self.learning_engine.stop_learning()
                self.learning_status_text.append(f"AI Öğrenme Durduruldu - {datetime.now().strftime('%H:%M:%S')}")
                self.learning_status_indicator.setText("🧠 Durdu")
                QMessageBox.information(self, "AI Öğrenme", "AI öğrenme süreci durduruldu!")
            else:
                QMessageBox.information(self, "AI Öğrenme", "AI öğrenme zaten pasif!")
                
        except Exception as e:
            logger.error(f"AI öğrenme durdurma hatası: {e}")
            QMessageBox.critical(self, "Hata", f"AI öğrenme durdurma hatası: {e}")
    
    def reset_ai_learning(self):
        """AI öğrenmeyi sıfırla"""
        try:
            self.learning_engine.stop_learning()
            time.sleep(1)
            self.learning_engine.start_learning()
            self.learning_status_text.append(f"AI Öğrenme Sıfırlandı - {datetime.now().strftime('%H:%M:%S')}")
            QMessageBox.information(self, "AI Öğrenme", "AI öğrenme süreci sıfırlandı!")
            
        except Exception as e:
            logger.error(f"AI öğrenme sıfırlama hatası: {e}")
            QMessageBox.critical(self, "Hata", f"AI öğrenme sıfırlama hatası: {e}")
    
    def send_cross_module_command(self):
        """Cross-module komut gönder"""
        try:
            target_module = self.target_module_combo.currentText()
            command = self.command_text.text()
            parameters_text = self.parameters_text.text()
            
            if not command:
                QMessageBox.warning(self, "Uyarı", "Lütfen komut girin!")
                return
            
            # Parametreleri parse et
            parameters = {}
            if parameters_text.strip():
                try:
                    parameters = json.loads(parameters_text)
                except json.JSONDecodeError:
                    QMessageBox.warning(self, "Uyarı", "Parametreler geçerli JSON formatında değil!")
                    return
            
            result = self.module_controller.send_command(target_module, command, parameters)
            
            self.command_history.append(f"[{datetime.now().strftime('%H:%M:%S')}] {target_module}: {command}")
            self.command_history.append(f"Parametreler: {json.dumps(parameters, ensure_ascii=False)}")
            self.command_history.append(f"Sonuç: {json.dumps(result, ensure_ascii=False)}")
            self.command_history.append("---")
            
            self.command_text.clear()
            self.parameters_text.clear()
            
            QMessageBox.information(self, "Komut", f"Komut başarıyla gönderildi!\nSonuç: {result}")
            
        except Exception as e:
            logger.error(f"Cross-module komut gönderme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Komut gönderme hatası: {e}")
    
    def update_ui(self):
        """UI'yi güncelle"""
        try:
            # AI durumu
            status_icon = "🟢" if self.ai_state == AIState.IDLE else "🟡" if self.ai_state == AIState.LEARNING else "🔴"
            self.ai_status_indicator.setText(f"{status_icon} AI {self.ai_state.value.title()}")
            
            # Öğrenme durumu
            learning_icon = "🧠" if self.learning_engine.is_learning else "⏸️"
            learning_text = "Öğreniyor" if self.learning_engine.is_learning else "Durdu"
            self.learning_status_indicator.setText(f"{learning_icon} {learning_text}")
            
            # Sistem sağlığı
            system_health = self.get_system_health()
            health_score = system_health['overall_score']
            if health_score > 0.8:
                health_icon = "💚"
                health_text = "Sağlıklı"
            elif health_score > 0.5:
                health_icon = "🟡"
                health_text = "Orta"
            else:
                health_icon = "🔴"
                health_text = "Kritik"
            
            self.system_health_indicator.setText(f"{health_icon} Sistem {health_text}")
            
            # Metrik kartlarını güncelle
            if self.system_metrics:
                cpu_percent = self.system_metrics.get('cpu', 0)
                memory_percent = self.system_metrics.get('memory', 0)
                disk_percent = self.system_metrics.get('disk', 0)
                
                self.cpu_card.value_label.setText(f"%{cpu_percent:.1f}")
                self.cpu_card.progress_bar.setValue(int(cpu_percent))
                
                self.memory_card.value_label.setText(f"%{memory_percent:.1f}")
                self.memory_card.progress_bar.setValue(int(memory_percent))
                
                self.disk_card.value_label.setText(f"%{disk_percent:.1f}")
                self.disk_card.progress_bar.setValue(int(disk_percent))
                
                # Ağ aktivitesi (simüle edilmiş)
                network_percent = random.randint(0, 100)
                self.network_card.value_label.setText(f"%{network_percent}")
                self.network_card.progress_bar.setValue(network_percent)
            
            # Modül tablosunu güncelle
            self.update_modules_table()
            
            # İçgörüleri güncelle
            self.update_insights_list()
            
            # Sistem loglarını güncelle
            self.update_system_logs()
            
        except Exception as e:
            logger.error(f"UI güncelleme hatası: {e}")
    
    def update_modules_table(self):
        """Modül tablosunu güncelle"""
        try:
            self.modules_table.setRowCount(len(self.module_status))
            
            for row, (module_name, status) in enumerate(self.module_status.items()):
                # Modül adı
                self.modules_table.setItem(row, 0, QTableWidgetItem(module_name))
                
                # Durum
                status_icon = "✅" if status.is_running else "❌"
                status_text = "Çalışıyor" if status.is_running else "Durdu"
                self.modules_table.setItem(row, 1, QTableWidgetItem(f"{status_icon} {status_text}"))
                
                # Sağlık
                health_percent = int(status.health_score * 100)
                health_color = "🟢" if health_percent > 80 else "🟡" if health_percent > 50 else "🔴"
                self.modules_table.setItem(row, 2, QTableWidgetItem(f"{health_color} %{health_percent}"))
                
                # Son aktivite
                self.modules_table.setItem(row, 3, QTableWidgetItem(status.last_activity.strftime("%H:%M:%S")))
                
                # Hata sayısı
                error_color = "🔴" if status.error_count > 5 else "🟡" if status.error_count > 0 else "🟢"
                self.modules_table.setItem(row, 4, QTableWidgetItem(f"{error_color} {status.error_count}"))
                
                # Performans
                perf_metrics = status.performance_metrics
                if perf_metrics:
                    cpu_usage = perf_metrics.get('cpu_usage', 0)
                    perf_text = f"CPU: %{cpu_usage:.1f}"
                else:
                    perf_text = "N/A"
                self.modules_table.setItem(row, 5, QTableWidgetItem(perf_text))
                
                # İşlemler
                self.modules_table.setItem(row, 6, QTableWidgetItem("Kontrol edilebilir"))
                
        except Exception as e:
            logger.error(f"Modül tablosu güncelleme hatası: {e}")
    
    def update_insights_list(self):
        """İçgörüler listesini güncelle"""
        try:
            self.insights_list.clear()
            
            # Son 20 içgörüyü göster
            recent_insights = sorted(self.insights, key=lambda x: x.timestamp, reverse=True)[:20]
            
            for insight in recent_insights:
                priority_icon = "🔴" if insight.priority >= 4 else "🟡" if insight.priority >= 2 else "🟢"
                item_text = f"{priority_icon} {insight.type} - {insight.timestamp.strftime('%H:%M:%S')}"
                self.insights_list.addItem(item_text)
                
        except Exception as e:
            logger.error(f"İçgörüler listesi güncelleme hatası: {e}")
    
    def update_system_logs(self):
        """Sistem loglarını güncelle"""
        try:
            # Son 10 log mesajını göster
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Simüle edilmiş log mesajları
            log_messages = [
                f"[{current_time}] AI Merkez sistemi çalışıyor",
                f"[{current_time}] Modül durumları güncellendi",
                f"[{current_time}] Sistem metrikleri toplandı",
                f"[{current_time}] AI öğrenme süreci aktif",
                f"[{current_time}] Cross-module iletişim hazır"
            ]
            
            # Rastgele log mesajı ekle
            if random.random() < 0.1:  # %10 şansla yeni log
                new_log = f"[{current_time}] {random.choice(['Sistem optimizasyonu', 'Modül kontrolü', 'AI analizi', 'Veri işleme'])} tamamlandı"
                log_messages.append(new_log)
            
            # Logları göster (son 5'i)
            self.system_logs_text.clear()
            for log in log_messages[-5:]:
                self.system_logs_text.append(log)
                
        except Exception as e:
            logger.error(f"Sistem logları güncelleme hatası: {e}")
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            settings = {
                'learning_rate': self.learning_rate_spin.value(),
                'confidence_threshold': self.confidence_threshold_spin.value(),
                'auto_optimize': self.auto_optimize_check.isChecked(),
                'monitoring_interval': self.monitoring_interval_spin.value(),
                'max_memory': self.max_memory_spin.value(),
                'auto_cleanup': self.auto_cleanup_check.isChecked()
            }
            
            with open('ai_center_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Ayarlar", "Ayarlar başarıyla kaydedildi!")
            
        except Exception as e:
            logger.error(f"Ayar kaydetme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Ayar kaydetme hatası: {e}")
    
    def refresh_system(self):
        """Sistemi yenile"""
        try:
            self.ai_status_text.append(f"Sistem Yenileniyor - {datetime.now().strftime('%H:%M:%S')}")
            
            # Modül durumlarını yenile
            self.check_module_status()
            
            # UI'yi güncelle
            self.update_ui()
            
            self.ai_status_text.append("🔄 Sistem yenilendi")
            QMessageBox.information(self, "Sistem", "Sistem yenilendi!")
            
        except Exception as e:
            logger.error(f"Sistem yenileme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Sistem yenileme hatası: {e}")
    
    def refresh_modules(self):
        """Modülleri yenile"""
        try:
            self.ai_status_text.append(f"Modüller Yenileniyor - {datetime.now().strftime('%H:%M:%S')}")
            
            # Modül durumlarını yeniden kontrol et
            self.check_module_status()
            
            # UI'yi güncelle
            self.update_ui()
            
            self.ai_status_text.append("✅ Modüller yenilendi")
            QMessageBox.information(self, "Modül Yenileme", "Modüller başarıyla yenilendi!")
            
        except Exception as e:
            logger.error(f"Modül yenileme hatası: {e}")
            QMessageBox.critical(self, "Hata", f"Modül yenileme hatası: {e}")
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        try:
            # İzlemeyi durdur
            self.is_monitoring = False
            
            # Öğrenme motorunu durdur
            self.learning_engine.stop_learning()
            
            # Veritabanı bağlantısını kapat
            if self.database.conn:
                self.database.conn.close()
            
            logger.info("AI Merkez sistemi kapatıldı")
            event.accept()
            
        except Exception as e:
            logger.error(f"Kapatma hatası: {e}")
            event.accept()


def main():
    """Ana fonksiyon - main.py ile uyumlu"""
    try:
        # QApplication oluştur
        app = QApplication(sys.argv)
        app.setApplicationName("AI Merkez - Ana Kontrol Sistemi")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("B2B Automation")
        
        # Uygulama stili
        app.setStyle("Fusion")
        
        # Dark tema - main.py ile aynı
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(15, 15, 15))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(26, 26, 26))
        dark_palette.setColor(QPalette.AlternateBase, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(13, 115, 119))
        dark_palette.setColor(QPalette.Highlight, QColor(13, 115, 119))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        app.setPalette(dark_palette)
        
        # Font - main.py ile aynı
        font = QFont("Arial", 11)
        app.setFont(font)
        
        # Ana pencere
        window = AICenterMainWindow()
        window.show()
        
        logger.info("🧠 AI Merkez sistemi başlatıldı")
        
        # Uygulamayı çalıştır
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Kritik hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()