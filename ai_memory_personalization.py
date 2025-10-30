"""
🧠 AI HAFIZA VE KİŞİSELLEŞTİRME SİSTEMİ
Kullanıcı Bağlamı, Tercihler ve Öğrenme Sistemi
"""

import os
import json
import time
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

# AI ve NLP kütüphaneleri
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize, sent_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class MemoryType(Enum):
    """Hafıza tipi"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class InteractionType(Enum):
    """Etkileşim tipi"""
    VOICE_COMMAND = "voice_command"
    TEXT_QUERY = "text_query"
    BUSINESS_ANALYSIS = "business_analysis"
    DATA_EXPLORATION = "data_exploration"
    STRATEGY_DISCUSSION = "strategy_discussion"


class EmotionalState(Enum):
    """Duygusal durum"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"


@dataclass
class UserMemory:
    """Kullanıcı hafızası"""
    memory_id: str
    user_id: str
    memory_type: MemoryType
    content: str
    importance: float  # 0-1 arası
    emotional_context: EmotionalState
    business_context: str
    timestamp: datetime
    access_count: int
    last_accessed: datetime
    related_memories: List[str]
    tags: List[str]


@dataclass
class UserPreference:
    """Kullanıcı tercihi"""
    preference_id: str
    user_id: str
    category: str
    key: str
    value: Any
    confidence: float  # 0-1 arası
    learned_from: List[str]
    last_updated: datetime


@dataclass
class InteractionPattern:
    """Etkileşim kalıbı"""
    pattern_id: str
    user_id: str
    interaction_type: InteractionType
    frequency: int
    success_rate: float
    preferred_response_style: str
    common_topics: List[str]
    time_patterns: Dict[str, int]
    emotional_patterns: Dict[str, float]


@dataclass
class LearningInsight:
    """Öğrenme içgörüsü"""
    insight_id: str
    user_id: str
    insight_type: str
    description: str
    confidence: float
    supporting_evidence: List[str]
    recommendations: List[str]
    created_at: datetime


class AIMemoryPersonalization:
    """
    🧠 AI Hafıza ve Kişiselleştirme Sistemi
    Kullanıcı Bağlamı ve Öğrenme
    """
    
    def __init__(self, database_path: str = "ai_memory.db", config: Dict = None):
        self.database_path = database_path
        self.config = config or {}
        self.is_learning = False
        self.learning_thread = None
        
        # AI modelleri
        self.ai_models = {}
        self.setup_ai_models()
        
        # Veritabanı
        self.setup_database()
        
        # Hafıza yönetimi
        self.memory_cache = {}
        self.preference_cache = {}
        self.pattern_cache = {}
        
        # Öğrenme süreçleri
        self.learning_processes = {
            'memory_consolidation': self.consolidate_memories,
            'preference_learning': self.learn_preferences,
            'pattern_recognition': self.recognize_patterns,
            'insight_generation': self.generate_insights
        }
        
        print("🧠 AI Hafıza ve Kişiselleştirme sistemi başlatıldı")
    
    def setup_ai_models(self):
        """AI modellerini kur"""
        try:
            # OpenAI
            if OPENAI_AVAILABLE and self.config.get('openai_api_key'):
                openai.api_key = self.config['openai_api_key']
                self.ai_models['openai'] = True
                print("✅ OpenAI modeli yüklendi")
            
            # NLTK
            if NLTK_AVAILABLE:
                try:
                    nltk.download('vader_lexicon', quiet=True)
                    nltk.download('punkt', quiet=True)
                    self.ai_models['sentiment'] = SentimentIntensityAnalyzer()
                    print("✅ NLTK modelleri yüklendi")
                except Exception as e:
                    print(f"⚠️ NLTK modelleri yüklenirken hata: {e}")
                    
        except Exception as e:
            print(f"⚠️ AI modelleri kurulum hatası: {e}")
    
    def setup_database(self):
        """Veritabanı kurulumu"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Kullanıcı hafızası tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_memories (
                    memory_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    memory_type TEXT,
                    content TEXT,
                    importance REAL,
                    emotional_context TEXT,
                    business_context TEXT,
                    timestamp TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    related_memories TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Kullanıcı tercihleri tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    preference_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    category TEXT,
                    key TEXT,
                    value TEXT,
                    confidence REAL,
                    learned_from TEXT,
                    last_updated TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Etkileşim kalıpları tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interaction_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    interaction_type TEXT,
                    frequency INTEGER,
                    success_rate REAL,
                    preferred_response_style TEXT,
                    common_topics TEXT,
                    time_patterns TEXT,
                    emotional_patterns TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Öğrenme içgörüleri tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_insights (
                    insight_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    insight_type TEXT,
                    description TEXT,
                    confidence REAL,
                    supporting_evidence TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Kullanıcı profilleri tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    personality_traits TEXT,
                    communication_style TEXT,
                    business_focus TEXT,
                    learning_style TEXT,
                    emotional_patterns TEXT,
                    interaction_history TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Veritabanı kurulumu tamamlandı")
            
        except Exception as e:
            print(f"⚠️ Veritabanı kurulum hatası: {e}")
    
    def start_learning(self):
        """Öğrenmeyi başlat"""
        if self.is_learning:
            return
        
        self.is_learning = True
        self.learning_thread = threading.Thread(target=self._continuous_learning_loop)
        self.learning_thread.daemon = True
        self.learning_thread.start()
        
        print("🧠 Sürekli öğrenme başlatıldı")
    
    def stop_learning(self):
        """Öğrenmeyi durdur"""
        self.is_learning = False
        if self.learning_thread:
            self.learning_thread.join(timeout=1)
        
        print("⏹️ Sürekli öğrenme durduruldu")
    
    def _continuous_learning_loop(self):
        """Sürekli öğrenme döngüsü"""
        while self.is_learning:
            try:
                # Öğrenme süreçlerini çalıştır
                for process_name, process_func in self.learning_processes.items():
                    try:
                        print(f"🧠 {process_name} süreci başlatılıyor...")
                        process_func()
                        print(f"✅ {process_name} süreci tamamlandı")
                    except Exception as e:
                        print(f"⚠️ {process_name} süreci hatası: {e}")
                
                # 5 dakikada bir öğrenme yap
                time.sleep(300)
                
            except Exception as e:
                print(f"⚠️ Sürekli öğrenme döngüsü hatası: {e}")
                time.sleep(60)
    
    def store_memory(self, user_id: str, content: str, memory_type: MemoryType, 
                    importance: float = 0.5, emotional_context: EmotionalState = EmotionalState.NEUTRAL,
                    business_context: str = "", tags: List[str] = None) -> str:
        """Hafızayı kaydet"""
        try:
            memory_id = self.generate_memory_id(user_id, content)
            
            memory = UserMemory(
                memory_id=memory_id,
                user_id=user_id,
                memory_type=memory_type,
                content=content,
                importance=importance,
                emotional_context=emotional_context,
                business_context=business_context,
                timestamp=datetime.now(),
                access_count=0,
                last_accessed=datetime.now(),
                related_memories=[],
                tags=tags or []
            )
            
            # Veritabanına kaydet
            self.save_memory_to_database(memory)
            
            # Cache'e ekle
            self.memory_cache[memory_id] = memory
            
            print(f"🧠 Hafıza kaydedildi: {memory_id}")
            return memory_id
            
        except Exception as e:
            print(f"⚠️ Hafıza kaydetme hatası: {e}")
            return None
    
    def retrieve_memory(self, user_id: str, query: str, memory_type: MemoryType = None) -> List[UserMemory]:
        """Hafızayı geri getir"""
        try:
            # Cache'den ara
            relevant_memories = []
            
            for memory_id, memory in self.memory_cache.items():
                if memory.user_id == user_id:
                    if memory_type is None or memory.memory_type == memory_type:
                        # Benzerlik skoru hesapla
                        similarity_score = self.calculate_similarity(query, memory.content)
                        if similarity_score > 0.3:  # Eşik değer
                            relevant_memories.append((memory, similarity_score))
            
            # Skora göre sırala
            relevant_memories.sort(key=lambda x: x[1], reverse=True)
            
            # Erişim sayısını artır
            for memory, _ in relevant_memories[:5]:  # En fazla 5 hafıza
                memory.access_count += 1
                memory.last_accessed = datetime.now()
                self.update_memory_access(memory)
            
            return [memory for memory, _ in relevant_memories[:10]]  # En fazla 10 hafıza döndür
            
        except Exception as e:
            print(f"⚠️ Hafıza geri getirme hatası: {e}")
            return []
    
    def calculate_similarity(self, query: str, content: str) -> float:
        """Benzerlik skoru hesapla"""
        try:
            # Basit kelime benzerliği
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            
            if not query_words or not content_words:
                return 0.0
            
            intersection = query_words.intersection(content_words)
            union = query_words.union(content_words)
            
            return len(intersection) / len(union)
            
        except Exception as e:
            print(f"⚠️ Benzerlik hesaplama hatası: {e}")
            return 0.0
    
    def learn_preference(self, user_id: str, category: str, key: str, value: Any, 
                        confidence: float = 0.5, learned_from: List[str] = None) -> str:
        """Tercih öğren"""
        try:
            preference_id = self.generate_preference_id(user_id, category, key)
            
            preference = UserPreference(
                preference_id=preference_id,
                user_id=user_id,
                category=category,
                key=key,
                value=value,
                confidence=confidence,
                learned_from=learned_from or [],
                last_updated=datetime.now()
            )
            
            # Veritabanına kaydet
            self.save_preference_to_database(preference)
            
            # Cache'e ekle
            self.preference_cache[preference_id] = preference
            
            print(f"🎯 Tercih öğrenildi: {category}.{key} = {value}")
            return preference_id
            
        except Exception as e:
            print(f"⚠️ Tercih öğrenme hatası: {e}")
            return None
    
    def get_preference(self, user_id: str, category: str, key: str) -> Any:
        """Tercih al"""
        try:
            # Cache'den ara
            for preference_id, preference in self.preference_cache.items():
                if (preference.user_id == user_id and 
                    preference.category == category and 
                    preference.key == key):
                    return preference.value
            
            # Veritabanından ara
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value, confidence FROM user_preferences 
                WHERE user_id = ? AND category = ? AND key = ?
                ORDER BY confidence DESC
            ''', (user_id, category, key))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ Tercih alma hatası: {e}")
            return None
    
    def recognize_interaction_pattern(self, user_id: str, interaction_type: InteractionType,
                                    success: bool, topics: List[str], emotional_state: EmotionalState):
        """Etkileşim kalıbını tanı"""
        try:
            # Mevcut kalıbı al veya oluştur
            pattern_id = f"{user_id}_{interaction_type.value}"
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM interaction_patterns WHERE pattern_id = ?
            ''', (pattern_id,))
            
            result = cursor.fetchone()
            
            if result:
                # Mevcut kalıbı güncelle
                frequency = result[3] + 1
                success_count = result[4] * result[3] + (1 if success else 0)
                success_rate = success_count / frequency
                
                cursor.execute('''
                    UPDATE interaction_patterns 
                    SET frequency = ?, success_rate = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE pattern_id = ?
                ''', (frequency, success_rate, pattern_id))
                
            else:
                # Yeni kalıp oluştur
                cursor.execute('''
                    INSERT INTO interaction_patterns 
                    (pattern_id, user_id, interaction_type, frequency, success_rate, 
                     preferred_response_style, common_topics, time_patterns, emotional_patterns)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern_id,
                    user_id,
                    interaction_type.value,
                    1,
                    1.0 if success else 0.0,
                    "professional",
                    json.dumps(topics),
                    json.dumps({}),
                    json.dumps({emotional_state.value: 1.0})
                ))
            
            conn.commit()
            conn.close()
            
            print(f"🔍 Etkileşim kalıbı tanındı: {pattern_id}")
            
        except Exception as e:
            print(f"⚠️ Etkileşim kalıbı tanıma hatası: {e}")
    
    def consolidate_memories(self):
        """Hafızaları birleştir"""
        try:
            # Kısa vadeli hafızaları uzun vadeli hafızaya taşı
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Eski kısa vadeli hafızaları bul
            cursor.execute('''
                SELECT * FROM user_memories 
                WHERE memory_type = 'short_term' 
                AND timestamp < datetime('now', '-1 day')
                AND importance > 0.7
            ''')
            
            old_memories = cursor.fetchall()
            
            for memory_data in old_memories:
                # Uzun vadeli hafızaya taşı
                cursor.execute('''
                    UPDATE user_memories 
                    SET memory_type = 'long_term'
                    WHERE memory_id = ?
                ''', (memory_data[0],))
            
            conn.commit()
            conn.close()
            
            print(f"🧠 {len(old_memories)} hafıza birleştirildi")
            
        except Exception as e:
            print(f"⚠️ Hafıza birleştirme hatası: {e}")
    
    def learn_preferences(self):
        """Tercihleri öğren"""
        try:
            # Etkileşim kalıplarından tercihleri çıkar
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, interaction_type, success_rate, common_topics, emotional_patterns
                FROM interaction_patterns
            ''')
            
            patterns = cursor.fetchall()
            
            for pattern in patterns:
                user_id, interaction_type, success_rate, common_topics, emotional_patterns = pattern
                
                # Başarı oranına göre tercih öğren
                if success_rate > 0.8:
                    self.learn_preference(
                        user_id=user_id,
                        category="interaction",
                        key=f"{interaction_type}_style",
                        value="preferred",
                        confidence=success_rate,
                        learned_from=["interaction_patterns"]
                    )
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Tercih öğrenme hatası: {e}")
    
    def recognize_patterns(self):
        """Kalıpları tanı"""
        try:
            # Kullanıcı davranış kalıplarını analiz et
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, COUNT(*) as total_interactions,
                       AVG(success_rate) as avg_success_rate
                FROM interaction_patterns
                GROUP BY user_id
            ''')
            
            user_stats = cursor.fetchall()
            
            for user_id, total_interactions, avg_success_rate in user_stats:
                # Kullanıcı profili güncelle
                self.update_user_profile(user_id, {
                    'total_interactions': total_interactions,
                    'avg_success_rate': avg_success_rate
                })
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Kalıp tanıma hatası: {e}")
    
    def generate_insights(self):
        """İçgörüler oluştur"""
        try:
            # Kullanıcı davranışlarından içgörüler çıkar
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, interaction_type, success_rate, common_topics
                FROM interaction_patterns
                WHERE success_rate > 0.7
            ''')
            
            successful_patterns = cursor.fetchall()
            
            for pattern in successful_patterns:
                user_id, interaction_type, success_rate, common_topics = pattern
                
                # İçgörü oluştur
                insight = LearningInsight(
                    insight_id=f"insight_{int(time.time())}_{user_id}",
                    user_id=user_id,
                    insight_type="interaction_success",
                    description=f"{interaction_type} etkileşimlerinde yüksek başarı oranı ({success_rate:.2f})",
                    confidence=success_rate,
                    supporting_evidence=[f"Başarı oranı: {success_rate:.2f}"],
                    recommendations=["Bu etkileşim tipini daha sık kullanın"],
                    created_at=datetime.now()
                )
                
                # Veritabanına kaydet
                self.save_insight_to_database(insight)
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ İçgörü oluşturma hatası: {e}")
    
    def get_personalized_response(self, user_id: str, query: str) -> Dict:
        """Kişiselleştirilmiş yanıt al"""
        try:
            # Kullanıcı tercihlerini al
            preferences = self.get_user_preferences(user_id)
            
            # İlgili hafızaları al
            memories = self.retrieve_memory(user_id, query)
            
            # Etkileşim kalıplarını al
            patterns = self.get_user_patterns(user_id)
            
            # Kişiselleştirilmiş yanıt oluştur
            response = {
                'personalized': True,
                'user_preferences': preferences,
                'relevant_memories': [memory.content for memory in memories[:3]],
                'recommended_style': self.get_recommended_style(patterns),
                'context_aware': True
            }
            
            return response
            
        except Exception as e:
            print(f"⚠️ Kişiselleştirilmiş yanıt alma hatası: {e}")
            return {'personalized': False, 'error': str(e)}
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Kullanıcı tercihlerini al"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT category, key, value, confidence FROM user_preferences 
                WHERE user_id = ?
            ''', (user_id,))
            
            preferences = {}
            for category, key, value, confidence in cursor.fetchall():
                if category not in preferences:
                    preferences[category] = {}
                preferences[category][key] = {'value': value, 'confidence': confidence}
            
            conn.close()
            return preferences
            
        except Exception as e:
            print(f"⚠️ Kullanıcı tercihleri alma hatası: {e}")
            return {}
    
    def get_user_patterns(self, user_id: str) -> List[Dict]:
        """Kullanıcı kalıplarını al"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT interaction_type, frequency, success_rate, common_topics, emotional_patterns
                FROM interaction_patterns 
                WHERE user_id = ?
            ''', (user_id,))
            
            patterns = []
            for row in cursor.fetchall():
                pattern = {
                    'interaction_type': row[0],
                    'frequency': row[1],
                    'success_rate': row[2],
                    'common_topics': json.loads(row[3]) if row[3] else [],
                    'emotional_patterns': json.loads(row[4]) if row[4] else {}
                }
                patterns.append(pattern)
            
            conn.close()
            return patterns
            
        except Exception as e:
            print(f"⚠️ Kullanıcı kalıpları alma hatası: {e}")
            return []
    
    def get_recommended_style(self, patterns: List[Dict]) -> str:
        """Önerilen stil al"""
        try:
            if not patterns:
                return "professional"
            
            # En başarılı kalıbı bul
            best_pattern = max(patterns, key=lambda x: x['success_rate'])
            
            if best_pattern['success_rate'] > 0.8:
                return "confident"
            elif best_pattern['success_rate'] > 0.6:
                return "professional"
            else:
                return "supportive"
                
        except Exception as e:
            print(f"⚠️ Önerilen stil alma hatası: {e}")
            return "professional"
    
    def update_user_profile(self, user_id: str, profile_data: Dict):
        """Kullanıcı profilini güncelle"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_profiles 
                (user_id, name, personality_traits, communication_style, business_focus, 
                 learning_style, emotional_patterns, interaction_history, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                profile_data.get('name', ''),
                json.dumps(profile_data.get('personality_traits', {})),
                profile_data.get('communication_style', 'professional'),
                json.dumps(profile_data.get('business_focus', [])),
                profile_data.get('learning_style', 'visual'),
                json.dumps(profile_data.get('emotional_patterns', {})),
                json.dumps(profile_data.get('interaction_history', [])),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Kullanıcı profili güncelleme hatası: {e}")
    
    def save_memory_to_database(self, memory: UserMemory):
        """Hafızayı veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_memories 
                (memory_id, user_id, memory_type, content, importance, emotional_context,
                 business_context, timestamp, access_count, last_accessed, related_memories, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                memory.memory_id,
                memory.user_id,
                memory.memory_type.value,
                memory.content,
                memory.importance,
                memory.emotional_context.value,
                memory.business_context,
                memory.timestamp.isoformat(),
                memory.access_count,
                memory.last_accessed.isoformat(),
                json.dumps(memory.related_memories),
                json.dumps(memory.tags)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Hafıza veritabanı kaydetme hatası: {e}")
    
    def save_preference_to_database(self, preference: UserPreference):
        """Tercihi veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences 
                (preference_id, user_id, category, key, value, confidence, learned_from, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                preference.preference_id,
                preference.user_id,
                preference.category,
                preference.key,
                json.dumps(preference.value),
                preference.confidence,
                json.dumps(preference.learned_from),
                preference.last_updated.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Tercih veritabanı kaydetme hatası: {e}")
    
    def save_insight_to_database(self, insight: LearningInsight):
        """İçgörüyü veritabanına kaydet"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO learning_insights 
                (insight_id, user_id, insight_type, description, confidence, 
                 supporting_evidence, recommendations, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                insight.insight_id,
                insight.user_id,
                insight.insight_type,
                insight.description,
                insight.confidence,
                json.dumps(insight.supporting_evidence),
                json.dumps(insight.recommendations),
                insight.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ İçgörü veritabanı kaydetme hatası: {e}")
    
    def update_memory_access(self, memory: UserMemory):
        """Hafıza erişimini güncelle"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_memories 
                SET access_count = ?, last_accessed = ?
                WHERE memory_id = ?
            ''', (memory.access_count, memory.last_accessed.isoformat(), memory.memory_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Hafıza erişim güncelleme hatası: {e}")
    
    def generate_memory_id(self, user_id: str, content: str) -> str:
        """Hafıza ID'si oluştur"""
        return hashlib.md5(f"{user_id}_{content}_{int(time.time())}".encode()).hexdigest()[:16]
    
    def generate_preference_id(self, user_id: str, category: str, key: str) -> str:
        """Tercih ID'si oluştur"""
        return hashlib.md5(f"{user_id}_{category}_{key}".encode()).hexdigest()[:16]
    
    def export_learning_data(self, filepath: str):
        """Öğrenme verilerini dışa aktar"""
        try:
            conn = sqlite3.connect(self.database_path)
            
            # Tüm verileri al
            memories = pd.read_sql_query("SELECT * FROM user_memories", conn)
            preferences = pd.read_sql_query("SELECT * FROM user_preferences", conn)
            patterns = pd.read_sql_query("SELECT * FROM interaction_patterns", conn)
            insights = pd.read_sql_query("SELECT * FROM learning_insights", conn)
            
            conn.close()
            
            # Excel dosyasına kaydet
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                memories.to_excel(writer, sheet_name='Hafızalar', index=False)
                preferences.to_excel(writer, sheet_name='Tercihler', index=False)
                patterns.to_excel(writer, sheet_name='Kalıplar', index=False)
                insights.to_excel(writer, sheet_name='İçgörüler', index=False)
            
            print(f"📁 Öğrenme verileri dışa aktarıldı: {filepath}")
            
        except Exception as e:
            print(f"⚠️ Veri dışa aktarma hatası: {e}")


# Test fonksiyonu
def test_ai_memory_personalization():
    """AI hafıza ve kişiselleştirme testi"""
    print("🧠 AI Hafıza ve Kişiselleştirme Test Başlatılıyor...")
    
    memory_system = AIMemoryPersonalization()
    
    # Test kullanıcısı
    user_id = "test_user_001"
    
    # Hafıza kaydet
    memory_id = memory_system.store_memory(
        user_id=user_id,
        content="Kullanıcı B2B satış süreçleri hakkında sorular soruyor",
        memory_type=MemoryType.SHORT_TERM,
        importance=0.8,
        emotional_context=EmotionalState.POSITIVE,
        business_context="sales",
        tags=["B2B", "sales", "process"]
    )
    
    # Tercih öğren
    preference_id = memory_system.learn_preference(
        user_id=user_id,
        category="communication",
        key="response_style",
        value="detailed",
        confidence=0.9,
        learned_from=["user_feedback"]
    )
    
    # Etkileşim kalıbı tanı
    memory_system.recognize_interaction_pattern(
        user_id=user_id,
        interaction_type=InteractionType.BUSINESS_ANALYSIS,
        success=True,
        topics=["sales", "B2B", "process"],
        emotional_state=EmotionalState.POSITIVE
    )
    
    # Hafızayı geri getir
    memories = memory_system.retrieve_memory(user_id, "B2B satış")
    print(f"🧠 {len(memories)} hafıza bulundu")
    
    # Kişiselleştirilmiş yanıt al
    response = memory_system.get_personalized_response(user_id, "Satış süreçleri hakkında bilgi ver")
    print(f"🎯 Kişiselleştirilmiş yanıt: {response}")
    
    print("✅ Test tamamlandı")


if __name__ == "__main__":
    test_ai_memory_personalization()
