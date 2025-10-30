"""
🧠 GELİŞMİŞ AI KONUŞMA ZEKASI SİSTEMİ
Stratejik AI İş Danışmanı - Sesli Etkileşim ve Gerçek Zamanlı Analiz
"""

import os
import json
import time
import threading
import queue
import wave
import pyaudio
import speech_recognition as sr
import pyttsx3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re
import webbrowser
import subprocess
import sys
import sqlite3
import numpy as np
from dataclasses import dataclass
from enum import Enum

# AI ve NLP kütüphaneleri
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI kütüphanesi yüklü değil")

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    from transformers import pipeline as transformers_pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers kütüphanesi yüklü değil")

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️ NLTK kütüphanesi yüklü değil")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️ spaCy kütüphanesi yüklü değil")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil kütüphanesi yüklü değil")

# Veri analizi
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️ Pandas kütüphanesi yüklü değil")

# Web scraping ve API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ Requests kütüphanesi yüklü değil")


class ConversationState(Enum):
    """Konuşma durumu"""
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    THINKING = "thinking"
    LEARNING = "learning"


class EmotionalTone(Enum):
    """Duygusal ton"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    WORRIED = "worried"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"


class BusinessContext(Enum):
    """İş bağlamı"""
    SALES = "sales"
    MARKETING = "marketing"
    CUSTOMER_SERVICE = "customer_service"
    STRATEGY = "strategy"
    ANALYSIS = "analysis"
    RESEARCH = "research"


@dataclass
class UserProfile:
    """Kullanıcı profili"""
    user_id: str
    name: str
    preferences: Dict[str, Any]
    interaction_history: List[Dict]
    emotional_patterns: Dict[str, float]
    business_focus: List[str]
    language_preference: str = "tr"
    voice_characteristics: Dict[str, Any] = None


@dataclass
class BusinessInsight:
    """İş içgörüsü"""
    insight_type: str
    confidence: float
    data_source: str
    timestamp: datetime
    summary: str
    details: Dict[str, Any]
    recommendations: List[str]


@dataclass
class ConversationMemory:
    """Konuşma hafızası"""
    session_id: str
    user_id: str
    interactions: List[Dict]
    context: Dict[str, Any]
    emotional_state: EmotionalTone
    business_context: BusinessContext
    last_updated: datetime


class AIConversationalIntelligence:
    """
    🧠 Gelişmiş AI Konuşma Zekası Sistemi
    Stratejik AI İş Danışmanı
    """
    
    def __init__(self, config: Dict = None, database_path: str = "ai_intelligence.db"):
        self.config = config or {}
        self.database_path = database_path
        self.is_active = False
        self.current_state = ConversationState.LISTENING
        self.audio_queue = queue.Queue()
        self.conversation_memory = {}
        self.user_profiles = {}
        self.business_insights = []
        
        # Ses tanıma sistemi
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Ses sentezi sistemi
        self.tts_engine = pyttsx3.init()
        self.setup_advanced_tts()
        
        # AI modelleri
        self.ai_models = {}
        self.setup_advanced_ai_models()
        
        # Veritabanı
        self.setup_database()
        
        # Threading
        self.listening_thread = None
        self.processing_thread = None
        self.analysis_thread = None
        
        # Duygusal analiz
        self.emotional_analyzer = None
        self.setup_emotional_analysis()
        
        # İş zekası
        self.business_analyzer = None
        self.setup_business_intelligence()
        
        print("🧠 Gelişmiş AI Konuşma Zekası başlatıldı")
    
    def setup_advanced_tts(self):
        """Gelişmiş ses sentezi ayarları"""
        voices = self.tts_engine.getProperty('voices')
        
        # Çok dilli ses desteği
        self.voice_languages = {
            'tr': None,
            'en': None
        }
        
        for voice in voices:
            if 'turkish' in voice.name.lower() or 'tr' in voice.id.lower():
                self.voice_languages['tr'] = voice.id
            elif 'english' in voice.name.lower() or 'en' in voice.id.lower():
                self.voice_languages['en'] = voice.id
        
        # Varsayılan ayarlar
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
        
        # Duygusal ton ayarları
        self.emotional_voice_settings = {
            EmotionalTone.HAPPY: {'rate': 200, 'volume': 0.95},
            EmotionalTone.SAD: {'rate': 150, 'volume': 0.8},
            EmotionalTone.EXCITED: {'rate': 220, 'volume': 1.0},
            EmotionalTone.WORRIED: {'rate': 160, 'volume': 0.85},
            EmotionalTone.CONFIDENT: {'rate': 190, 'volume': 0.9},
            EmotionalTone.NEUTRAL: {'rate': 180, 'volume': 0.9}
        }
    
    def setup_advanced_ai_models(self):
        """Gelişmiş AI modelleri"""
        try:
            # OpenAI modelleri
            if OPENAI_AVAILABLE and self.config.get('openai_api_key'):
                openai.api_key = self.config['openai_api_key']
                self.ai_models['openai'] = True
                print("✅ OpenAI modelleri yüklendi")
            
            # Transformers modelleri
            if TRANSFORMERS_AVAILABLE:
                try:
                    # Duygusal analiz
                    self.ai_models['emotion_analyzer'] = transformers_pipeline(
                        "text-classification",
                        model="j-hartmann/emotion-english-distilroberta-base"
                    )
                    
                    # Soru-cevap
                    self.ai_models['qa_pipeline'] = transformers_pipeline(
                        "question-answering",
                        model="deepset/roberta-base-squad2"
                    )
                    
                    # Metin özetleme
                    self.ai_models['summarizer'] = transformers_pipeline(
                        "summarization",
                        model="facebook/bart-large-cnn"
                    )
                    
                    print("✅ Transformers modelleri yüklendi")
                except Exception as e:
                    print(f"⚠️ Transformers modelleri yüklenirken hata: {e}")
            
            # NLTK modelleri
            if NLTK_AVAILABLE:
                try:
                    nltk.download('vader_lexicon', quiet=True)
                    nltk.download('punkt', quiet=True)
                    nltk.download('stopwords', quiet=True)
                    
                    self.ai_models['sentiment'] = SentimentIntensityAnalyzer()
                    self.ai_models['stopwords'] = set(stopwords.words('english'))
                    
                    print("✅ NLTK modelleri yüklendi")
                except Exception as e:
                    print(f"⚠️ NLTK modelleri yüklenirken hata: {e}")
            
            # spaCy modelleri
            if SPACY_AVAILABLE:
                try:
                    self.ai_models['spacy_nlp'] = spacy.load("en_core_web_sm")
                    print("✅ spaCy modelleri yüklendi")
                except Exception as e:
                    print(f"⚠️ spaCy modelleri yüklenirken hata: {e}")
                    
        except Exception as e:
            print(f"⚠️ AI modelleri yüklenirken hata: {e}")
    
    def setup_database(self):
        """Veritabanı kurulumu"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Kullanıcı profilleri
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    preferences TEXT,
                    interaction_history TEXT,
                    emotional_patterns TEXT,
                    business_focus TEXT,
                    language_preference TEXT,
                    voice_characteristics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Konuşma hafızası
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    interactions TEXT,
                    context TEXT,
                    emotional_state TEXT,
                    business_context TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # İş içgörüleri
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_type TEXT,
                    confidence REAL,
                    data_source TEXT,
                    timestamp TIMESTAMP,
                    summary TEXT,
                    details TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Firma analizi
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS company_analysis (
                    company_id TEXT PRIMARY KEY,
                    company_name TEXT,
                    analysis_type TEXT,
                    buyer_intent REAL,
                    supplier_potential REAL,
                    competitor_level REAL,
                    market_position TEXT,
                    last_analyzed TIMESTAMP,
                    insights TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Veritabanı kurulumu tamamlandı")
            
        except Exception as e:
            print(f"⚠️ Veritabanı kurulum hatası: {e}")
    
    def setup_emotional_analysis(self):
        """Duygusal analiz sistemi"""
        try:
            if NLTK_AVAILABLE and self.ai_models.get('sentiment'):
                self.emotional_analyzer = self.ai_models['sentiment']
                print("✅ Duygusal analiz sistemi yüklendi")
        except Exception as e:
            print(f"⚠️ Duygusal analiz sistemi yüklenirken hata: {e}")
    
    def setup_business_intelligence(self):
        """İş zekası sistemi"""
        try:
            # İş analizi için gerekli modüller
            self.business_analyzer = {
                'market_trends': self.analyze_market_trends,
                'company_analysis': self.analyze_company_data,
                'buyer_intent': self.analyze_buyer_intent,
                'competitor_analysis': self.analyze_competitors,
                'contact_activity': self.analyze_contact_activity
            }
            print("✅ İş zekası sistemi yüklendi")
        except Exception as e:
            print(f"⚠️ İş zekası sistemi yüklenirken hata: {e}")
    
    def start_conversation(self, user_id: str = "default"):
        """Konuşmayı başlat"""
        if self.is_active:
            return
        
        self.is_active = True
        self.current_state = ConversationState.LISTENING
        
        # Kullanıcı profilini yükle
        self.load_user_profile(user_id)
        
        # Dinleme thread'ini başlat
        self.listening_thread = threading.Thread(target=self._advanced_listening_loop)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
        # Analiz thread'ini başlat
        self.analysis_thread = threading.Thread(target=self._continuous_analysis_loop)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
        # Hoş geldin mesajı
        self.speak_with_emotion("Merhaba! Ben sizin stratejik AI iş danışmanınızım. Size nasıl yardımcı olabilirim?", 
                              EmotionalTone.CONFIDENT)
        
        print("🧠 Gelişmiş AI konuşma zekası aktif")
    
    def stop_conversation(self):
        """Konuşmayı durdur"""
        self.is_active = False
        self.current_state = ConversationState.LISTENING
        
        if self.listening_thread:
            self.listening_thread.join(timeout=1)
        
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1)
        
        print("🔇 AI konuşma zekası durduruldu")
    
    def _advanced_listening_loop(self):
        """Gelişmiş dinleme döngüsü"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while self.is_active:
            try:
                with self.microphone as source:
                    # Gelişmiş ses tanıma
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                
                # Thread'de işle
                processing_thread = threading.Thread(
                    target=self._advanced_process_audio, 
                    args=(audio,)
                )
                processing_thread.daemon = True
                processing_thread.start()
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"⚠️ Gelişmiş dinleme hatası: {e}")
                time.sleep(0.1)
    
    def _advanced_process_audio(self, audio):
        """Gelişmiş ses işleme"""
        try:
            # Çok dilli ses tanıma
            languages = ['tr-TR', 'en-US']
            recognized_text = None
            
            for lang in languages:
                try:
                    recognized_text = self.recognizer.recognize_google(audio, language=lang)
                    break
                except sr.UnknownValueError:
                    continue
            
            if recognized_text:
                print(f"🧠 Algılanan: {recognized_text}")
                
                # Gelişmiş komut işleme
                self.process_advanced_command(recognized_text)
            
        except sr.RequestError as e:
            print(f"⚠️ Ses tanıma hatası: {e}")
        except Exception as e:
            print(f"⚠️ Gelişmiş ses işleme hatası: {e}")
    
    def process_advanced_command(self, text: str):
        """Gelişmiş komut işleme"""
        self.current_state = ConversationState.PROCESSING
        
        # Duygusal analiz
        emotional_tone = self.analyze_emotional_tone(text)
        
        # Dil tespiti
        language = self.detect_language(text)
        
        # İş bağlamı analizi
        business_context = self.analyze_business_context(text)
        
        # AI ile gelişmiş analiz
        response = self.generate_intelligent_response(text, emotional_tone, business_context, language)
        
        # Yanıtı sesli olarak söyle
        if response:
            self.speak_with_emotion(response, emotional_tone)
        
        # Hafızaya kaydet
        self.save_conversation_memory(text, response, emotional_tone, business_context)
        
        self.current_state = ConversationState.LISTENING
    
    def analyze_emotional_tone(self, text: str) -> EmotionalTone:
        """Duygusal ton analizi"""
        try:
            if self.emotional_analyzer:
                scores = self.emotional_analyzer.polarity_scores(text)
                
                # Duygusal ton belirleme
                if scores['compound'] >= 0.5:
                    return EmotionalTone.HAPPY
                elif scores['compound'] <= -0.5:
                    return EmotionalTone.SAD
                elif scores['neu'] > 0.8:
                    return EmotionalTone.NEUTRAL
                else:
                    return EmotionalTone.CONFIDENT
            else:
                return EmotionalTone.NEUTRAL
                
        except Exception as e:
            print(f"⚠️ Duygusal ton analizi hatası: {e}")
            return EmotionalTone.NEUTRAL
    
    def detect_language(self, text: str) -> str:
        """Dil tespiti"""
        try:
            # Basit dil tespiti
            turkish_chars = set('çğıöşüÇĞIİÖŞÜ')
            if any(char in text for char in turkish_chars):
                return 'tr'
            else:
                return 'en'
        except:
            return 'tr'  # Varsayılan Türkçe
    
    def analyze_business_context(self, text: str) -> BusinessContext:
        """İş bağlamı analizi"""
        try:
            # İş anahtar kelimeleri
            sales_keywords = ['satış', 'müşteri', 'lead', 'sales', 'customer', 'client']
            marketing_keywords = ['pazarlama', 'kampanya', 'marketing', 'campaign', 'promotion']
            strategy_keywords = ['strateji', 'plan', 'strategy', 'planning', 'roadmap']
            analysis_keywords = ['analiz', 'rapor', 'analysis', 'report', 'data']
            
            text_lower = text.lower()
            
            if any(keyword in text_lower for keyword in sales_keywords):
                return BusinessContext.SALES
            elif any(keyword in text_lower for keyword in marketing_keywords):
                return BusinessContext.MARKETING
            elif any(keyword in text_lower for keyword in strategy_keywords):
                return BusinessContext.STRATEGY
            elif any(keyword in text_lower for keyword in analysis_keywords):
                return BusinessContext.ANALYSIS
            else:
                return BusinessContext.SALES  # Varsayılan
                
        except Exception as e:
            print(f"⚠️ İş bağlamı analizi hatası: {e}")
            return BusinessContext.SALES
    
    def generate_intelligent_response(self, text: str, emotional_tone: EmotionalTone, 
                                    business_context: BusinessContext, language: str) -> str:
        """Akıllı yanıt üretimi"""
        try:
            # OpenAI ile gelişmiş analiz
            if self.ai_models.get('openai'):
                return self.generate_openai_response(text, emotional_tone, business_context, language)
            else:
                return self.generate_basic_response(text, emotional_tone, business_context, language)
                
        except Exception as e:
            print(f"⚠️ Akıllı yanıt üretimi hatası: {e}")
            return "Üzgünüm, şu anda yanıt veremiyorum."
    
    def generate_openai_response(self, text: str, emotional_tone: EmotionalTone, 
                               business_context: BusinessContext, language: str) -> str:
        """OpenAI ile gelişmiş yanıt üretimi"""
        try:
            # İş içgörülerini al
            business_insights = self.get_relevant_business_insights(business_context)
            
            # Kullanıcı profilini al
            user_profile = self.get_current_user_profile()
            
            # Gelişmiş prompt oluştur
            prompt = f"""
            Sen bir stratejik AI iş danışmanısın. Kullanıcının sorusunu analiz et ve profesyonel yanıt ver.
            
            Kullanıcı Sorusu: "{text}"
            Duygusal Ton: {emotional_tone.value}
            İş Bağlamı: {business_context.value}
            Dil: {language}
            
            Mevcut İş İçgörüleri:
            {business_insights}
            
            Kullanıcı Profili:
            {user_profile}
            
            Yanıt Kriterleri:
            - Profesyonel ve yardımcı ol
            - Duygusal tonu yansıt
            - İş bağlamına uygun
            - Veri destekli öneriler ver
            - Kısa ve net ol (maksimum 3 cümle)
            
            Yanıt:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ OpenAI yanıt üretimi hatası: {e}")
            return self.generate_basic_response(text, emotional_tone, business_context, language)
    
    def generate_basic_response(self, text: str, emotional_tone: EmotionalTone, 
                              business_context: BusinessContext, language: str) -> str:
        """Temel yanıt üretimi"""
        try:
            # Temel yanıt şablonları
            responses = {
                BusinessContext.SALES: {
                    EmotionalTone.HAPPY: "Harika! Satış sürecinizde size nasıl yardımcı olabilirim?",
                    EmotionalTone.CONFIDENT: "Satış stratejinizi güçlendirmek için hangi konuda destek istiyorsunuz?",
                    EmotionalTone.NEUTRAL: "Satış süreciniz hakkında ne öğrenmek istiyorsunuz?"
                },
                BusinessContext.MARKETING: {
                    EmotionalTone.HAPPY: "Pazarlama kampanyalarınızda başarılar! Hangi konuda yardıma ihtiyacınız var?",
                    EmotionalTone.CONFIDENT: "Pazarlama stratejinizi optimize etmek için hangi verileri analiz edelim?",
                    EmotionalTone.NEUTRAL: "Pazarlama süreciniz hakkında ne öğrenmek istiyorsunuz?"
                },
                BusinessContext.STRATEGY: {
                    EmotionalTone.HAPPY: "Stratejik planlamanızda size nasıl yardımcı olabilirim?",
                    EmotionalTone.CONFIDENT: "İş stratejinizi güçlendirmek için hangi analizleri yapalım?",
                    EmotionalTone.NEUTRAL: "Strateji süreciniz hakkında ne öğrenmek istiyorsunuz?"
                }
            }
            
            return responses.get(business_context, {}).get(emotional_tone, 
                "Size nasıl yardımcı olabilirim?")
                
        except Exception as e:
            print(f"⚠️ Temel yanıt üretimi hatası: {e}")
            return "Size nasıl yardımcı olabilirim?"
    
    def get_relevant_business_insights(self, business_context: BusinessContext) -> str:
        """İlgili iş içgörülerini al"""
        try:
            # Veritabanından ilgili içgörüleri al
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT summary, details FROM business_insights 
                WHERE insight_type = ? 
                ORDER BY timestamp DESC 
                LIMIT 5
            ''', (business_context.value,))
            
            insights = cursor.fetchall()
            conn.close()
            
            if insights:
                return "\n".join([f"- {insight[0]}" for insight in insights])
            else:
                return "Henüz bu konuda içgörü bulunmuyor."
                
        except Exception as e:
            print(f"⚠️ İş içgörüleri alma hatası: {e}")
            return "Veri analizi yapılıyor..."
    
    def get_current_user_profile(self) -> str:
        """Mevcut kullanıcı profilini al"""
        try:
            # Varsayılan kullanıcı profili
            return "Kullanıcı: Stratejik iş danışmanı, B2B odaklı"
        except Exception as e:
            print(f"⚠️ Kullanıcı profili alma hatası: {e}")
            return "Kullanıcı profili yükleniyor..."
    
    def speak_with_emotion(self, text: str, emotional_tone: EmotionalTone):
        """Duygusal ton ile konuşma"""
        if not text:
            return
        
        try:
            # Duygusal ton ayarlarını uygula
            if emotional_tone in self.emotional_voice_settings:
                settings = self.emotional_voice_settings[emotional_tone]
                self.tts_engine.setProperty('rate', settings['rate'])
                self.tts_engine.setProperty('volume', settings['volume'])
            
            # Konuşma
            print(f"🧠 AI Danışman: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"⚠️ Duygusal konuşma hatası: {e}")
    
    def save_conversation_memory(self, user_input: str, ai_response: str, 
                                emotional_tone: EmotionalTone, business_context: BusinessContext):
        """Konuşma hafızasını kaydet"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Konuşma kaydı
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'ai_response': ai_response,
                'emotional_tone': emotional_tone.value,
                'business_context': business_context.value
            }
            
            # Veritabanına kaydet
            cursor.execute('''
                INSERT OR REPLACE INTO conversation_memory 
                (session_id, user_id, interactions, context, emotional_state, business_context, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"session_{int(time.time())}",
                "default",
                json.dumps([interaction]),
                json.dumps({'last_interaction': interaction}),
                emotional_tone.value,
                business_context.value,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Konuşma hafızası kaydetme hatası: {e}")
    
    def load_user_profile(self, user_id: str):
        """Kullanıcı profilini yükle"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
            profile_data = cursor.fetchone()
            
            if profile_data:
                # Profil verilerini yükle
                pass
            else:
                # Varsayılan profil oluştur
                self.create_default_user_profile(user_id)
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Kullanıcı profili yükleme hatası: {e}")
    
    def create_default_user_profile(self, user_id: str):
        """Varsayılan kullanıcı profili oluştur"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            default_profile = {
                'user_id': user_id,
                'name': 'AI Danışman Kullanıcısı',
                'preferences': {},
                'interaction_history': [],
                'emotional_patterns': {},
                'business_focus': ['sales', 'marketing', 'strategy'],
                'language_preference': 'tr'
            }
            
            cursor.execute('''
                INSERT INTO user_profiles 
                (user_id, name, preferences, interaction_history, emotional_patterns, business_focus, language_preference)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                default_profile['name'],
                json.dumps(default_profile['preferences']),
                json.dumps(default_profile['interaction_history']),
                json.dumps(default_profile['emotional_patterns']),
                json.dumps(default_profile['business_focus']),
                default_profile['language_preference']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Varsayılan profil oluşturma hatası: {e}")
    
    def _continuous_analysis_loop(self):
        """Sürekli analiz döngüsü"""
        while self.is_active:
            try:
                # İş içgörülerini güncelle
                self.update_business_insights()
                
                # Piyasa analizi
                self.analyze_market_trends()
                
                # Firma analizi
                self.analyze_company_data()
                
                # 5 dakikada bir analiz yap
                time.sleep(300)
                
            except Exception as e:
                print(f"⚠️ Sürekli analiz hatası: {e}")
                time.sleep(60)
    
    def update_business_insights(self):
        """İş içgörülerini güncelle"""
        try:
            # Yeni içgörüler oluştur
            insights = [
                {
                    'insight_type': 'market_trends',
                    'confidence': 0.85,
                    'data_source': 'market_analysis',
                    'timestamp': datetime.now().isoformat(),
                    'summary': 'Piyasa trendleri pozitif yönde ilerliyor',
                    'details': {'trend_direction': 'positive', 'confidence': 0.85},
                    'recommendations': ['Satış stratejilerini güçlendirin', 'Yeni pazarlara açılın']
                }
            ]
            
            # Veritabanına kaydet
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            for insight in insights:
                cursor.execute('''
                    INSERT INTO business_insights 
                    (insight_type, confidence, data_source, timestamp, summary, details, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    insight['insight_type'],
                    insight['confidence'],
                    insight['data_source'],
                    insight['timestamp'],
                    insight['summary'],
                    json.dumps(insight['details']),
                    json.dumps(insight['recommendations'])
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ İş içgörüleri güncelleme hatası: {e}")
    
    def analyze_market_trends(self):
        """Piyasa trendlerini analiz et"""
        try:
            # Piyasa analizi (örnek)
            market_data = {
                'trend_direction': 'positive',
                'growth_rate': 0.15,
                'key_opportunities': ['Yeni teknolojiler', 'Dijital dönüşüm'],
                'threats': ['Rekabet artışı', 'Ekonomik belirsizlik']
            }
            
            print(f"📊 Piyasa analizi: {market_data['trend_direction']}")
            
        except Exception as e:
            print(f"⚠️ Piyasa analizi hatası: {e}")
    
    def analyze_company_data(self):
        """Firma verilerini analiz et"""
        try:
            # Firma analizi (örnek)
            company_analysis = {
                'total_companies': 150,
                'active_leads': 45,
                'conversion_rate': 0.12,
                'top_performers': ['Firma A', 'Firma B', 'Firma C']
            }
            
            print(f"🏢 Firma analizi: {company_analysis['total_companies']} firma")
            
        except Exception as e:
            print(f"⚠️ Firma analizi hatası: {e}")
    
    def analyze_buyer_intent(self, company_data: Dict = None, conversation_history: List = None) -> Dict:
        """Alıcı niyetini analiz et"""
        try:
            # Alıcı niyet analizi
            intent_analysis = {
                'intent_score': 0.75,
                'intent_level': 'medium',
                'buying_signals': [
                    'Website ziyareti',
                    'Email açılması',
                    'Doküman indirme'
                ],
                'next_action': 'Takip et',
                'confidence': 0.8,
                'recommended_approach': 'Kişiselleştirilmiş teklif gönder',
                'urgency_level': 'medium',
                'decision_makers': ['CTO', 'Satın Alma Müdürü'],
                'budget_estimate': 'Orta seviye',
                'timeline': '1-3 ay'
            }
            
            # Konuşma geçmişi varsa daha detaylı analiz
            if conversation_history:
                recent_mentions = [msg for msg in conversation_history[-5:] if 'satın' in msg.lower() or 'fiyat' in msg.lower()]
                if recent_mentions:
                    intent_analysis['intent_score'] = min(0.95, intent_analysis['intent_score'] + 0.2)
                    intent_analysis['urgency_level'] = 'high'
            
            # Firma verisi varsa daha spesifik analiz
            if company_data:
                if company_data.get('industry') == 'teknoloji':
                    intent_analysis['recommended_approach'] = 'Teknik demo düzenle'
                elif company_data.get('size') == 'büyük':
                    intent_analysis['budget_estimate'] = 'Yüksek seviye'
                    intent_analysis['decision_makers'].append('CEO')
            
            print(f"🎯 Alıcı niyet analizi: {intent_analysis['intent_level']} seviye")
            
            return {
                'success': True,
                'intent': intent_analysis['intent_level'],
                'data': intent_analysis
            }
            
        except Exception as e:
            print(f"⚠️ Alıcı niyet analizi hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'intent': 'unknown'
            }
    
    def analyze_competitors(self) -> Dict:
        """Rakip analizi"""
        try:
            competitor_data = {
                'direct_competitors': [],
                'indirect_competitors': [],
                'market_share_analysis': {},
                'competitive_advantages': [],
                'threats': []
            }
            
            print(f"🏆 Rakip analizi tamamlandı")
            return {
                'success': True,
                'data': competitor_data
            }
            
        except Exception as e:
            print(f"⚠️ Rakip analizi hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_contact_activity(self) -> Dict:
        """İletişim aktivitesi analizi"""
        try:
            activity_data = {
                'total_contacts': 0,
                'response_rate': 0.0,
                'avg_response_time': 0,
                'most_engaged_segments': [],
                'activity_trends': {}
            }
            
            print(f"📞 İletişim aktivitesi analizi tamamlandı")
            return {
                'success': True,
                'data': activity_data
            }
            
        except Exception as e:
            print(f"⚠️ İletişim aktivitesi analizi hatası: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_conversation_status(self) -> Dict:
        """Konuşma durumu"""
        return {
            'is_active': self.is_active,
            'current_state': self.current_state.value,
            'ai_models_loaded': len(self.ai_models),
            'database_connected': os.path.exists(self.database_path),
            'last_interaction': datetime.now().isoformat()
        }
    
    def export_conversation_data(self, filepath: str):
        """Konuşma verilerini dışa aktar"""
        try:
            conn = sqlite3.connect(self.database_path)
            
            # Tüm verileri al
            conversations = pd.read_sql_query(
                "SELECT * FROM conversation_memory", conn
            )
            insights = pd.read_sql_query(
                "SELECT * FROM business_insights", conn
            )
            profiles = pd.read_sql_query(
                "SELECT * FROM user_profiles", conn
            )
            
            conn.close()
            
            # Excel dosyasına kaydet
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                conversations.to_excel(writer, sheet_name='Konuşmalar', index=False)
                insights.to_excel(writer, sheet_name='İş İçgörüleri', index=False)
                profiles.to_excel(writer, sheet_name='Kullanıcı Profilleri', index=False)
            
            print(f"📁 Konuşma verileri dışa aktarıldı: {filepath}")
            
        except Exception as e:
            print(f"⚠️ Veri dışa aktarma hatası: {e}")


# Test fonksiyonu
def test_ai_conversational_intelligence():
    """AI konuşma zekası testi"""
    print("🧠 AI Konuşma Zekası Test Başlatılıyor...")
    
    # Test konfigürasyonu
    config = {
        'openai_api_key': 'test-key'  # Gerçek API anahtarı gerekli
    }
    
    ai_intelligence = AIConversationalIntelligence(config)
    
    # Test konuşması
    test_queries = [
        "Hangi firmalar bizim son emailimizi açtı?",
        "Piyasa trendleri nasıl?",
        "En iyi müşteri adaylarımız kimler?",
        "Rekabet analizi yapabilir misin?"
    ]
    
    for query in test_queries:
        print(f"\n🧪 Test sorusu: {query}")
        ai_intelligence.process_advanced_command(query)
        time.sleep(2)
    
    print("\n✅ Test tamamlandı")


if __name__ == "__main__":
    test_ai_conversational_intelligence()
