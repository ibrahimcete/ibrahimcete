"""
🎤 GELİŞMİŞ SESLİ ASİSTAN SİSTEMİ
AI destekli, çok dilli, akıllı sesli komut sistemi
"""

import os
import json
import time
import threading
import queue
import wave
# Ses tanıma ve işleme
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio kütüphanesi yüklü değil")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️ SpeechRecognition kütüphanesi yüklü değil")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("⚠️ pyttsx3 kütüphanesi yüklü değil")
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import webbrowser
import subprocess
import sys

# AI ve NLP kütüphaneleri
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI kütüphanesi yüklü değil")

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers kütüphanesi yüklü değil")

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("⚠️ NLTK kütüphanesi yüklü değil")

class VoiceAssistant:
    """
    🎤 Gelişmiş Sesli Asistan
    - AI destekli komut analizi
    - Çok dilli destek
    - Akıllı yanıt sistemi
    - B2B işlemleri için özel komutlar
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.is_listening = False
        self.is_speaking = False
        self.audio_queue = queue.Queue()
        self.command_history = []
        self.user_preferences = {}
        
        # Ses tanıma sistemi
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
            except Exception as e:
                print(f"⚠️ Ses tanıma sistemi başlatılamadı: {e}")
                self.recognizer = None
                self.microphone = None
        else:
            self.recognizer = None
            self.microphone = None
        
        # Ses sentezi sistemi
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.setup_tts()
            except Exception as e:
                print(f"⚠️ Ses sentezi sistemi başlatılamadı: {e}")
                self.tts_engine = None
        else:
            self.tts_engine = None
        
        # AI modelleri
        self.ai_models = {}
        self.setup_ai_models()
        
        # Komut sistemi
        self.commands = self.setup_commands()
        self.setup_voice_commands()
        
        # Threading
        self.listening_thread = None
        self.processing_thread = None
        
        print("🎤 Gelişmiş Sesli Asistan başlatıldı")
    
    def setup_tts(self):
        """Ses sentezi ayarları"""
        voices = self.tts_engine.getProperty('voices')
        
        # Türkçe ses bul
        for voice in voices:
            if 'turkish' in voice.name.lower() or 'tr' in voice.id.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Hız ve ton ayarları
        self.tts_engine.setProperty('rate', 180)  # Konuşma hızı
        self.tts_engine.setProperty('volume', 0.9)  # Ses seviyesi
    
    def setup_ai_models(self):
        """AI modellerini yükle"""
        try:
            # OpenAI modeli
            if OPENAI_AVAILABLE and self.config.get('openai_api_key'):
                openai.api_key = self.config['openai_api_key']
                self.ai_models['openai'] = True
                print("✅ OpenAI modeli yüklendi")
            
            # Yerel sentiment analizi
            if NLTK_AVAILABLE:
                try:
                    nltk.download('vader_lexicon', quiet=True)
                    self.ai_models['sentiment'] = SentimentIntensityAnalyzer()
                    print("✅ Sentiment analizi yüklendi")
                except:
                    pass
            
            # Transformers modelleri
            if TRANSFORMERS_AVAILABLE:
                try:
                    # Türkçe NLP modeli
                    self.ai_models['qa_pipeline'] = pipeline(
                        "question-answering",
                        model="microsoft/DialoGPT-medium"
                    )
                    print("✅ Transformers modelleri yüklendi")
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ AI modelleri yüklenirken hata: {e}")
    
    def setup_commands(self):
        """Temel komut sistemi"""
        return {
            # Sistem komutları
            'sistem': {
                'keywords': ['sistem', 'bilgisayar', 'pc', 'kompüter'],
                'actions': ['sistem_bilgisi', 'kapat', 'yeniden_başlat']
            },
            # B2B komutları
            'b2b': {
                'keywords': ['firma', 'şirket', 'müşteri', 'email', 'mail', 'arama', 'bul'],
                'actions': ['firma_ara', 'email_gönder', 'müşteri_listesi']
            },
            # Web komutları
            'web': {
                'keywords': ['web', 'site', 'tarayıcı', 'aç', 'git'],
                'actions': ['web_sitesi_aç', 'arama_yap']
            },
            # Dosya komutları
            'dosya': {
                'keywords': ['dosya', 'klasör', 'aç', 'kaydet'],
                'actions': ['dosya_aç', 'klasör_aç']
            },
            # Genel komutlar
            'genel': {
                'keywords': ['merhaba', 'selam', 'nasılsın', 'teşekkür', 'sağol'],
                'actions': ['selamla', 'durum_sor', 'teşekkür_et']
            }
        }
    
    def setup_voice_commands(self):
        """Sesli komut tanımları"""
        self.voice_commands = {
            # Selamlama
            'merhaba': self.handle_greeting,
            'selam': self.handle_greeting,
            'hey': self.handle_greeting,
            
            # Sistem
            'sistem durumu': self.handle_system_status,
            'bilgisayar kapat': self.handle_shutdown,
            'yeniden başlat': self.handle_restart,
            
            # B2B İşlemleri
            'firma ara': self.handle_search_companies,
            'müşteri listesi': self.handle_customer_list,
            'email gönder': self.handle_send_email,
            'rapor oluştur': self.handle_create_report,
            
            # Web
            'web sitesi aç': self.handle_open_website,
            'arama yap': self.handle_web_search,
            'youtube aç': self.handle_open_youtube,
            
            # Dosya işlemleri
            'dosya aç': self.handle_open_file,
            'klasör aç': self.handle_open_folder,
            'masaüstü aç': self.handle_open_desktop,
            
            # Yardım
            'yardım': self.handle_help,
            'komutlar': self.handle_commands,
            'ne yapabilirsin': self.handle_capabilities,
            
            # Genel
            'teşekkürler': self.handle_thanks,
            'görüşürüz': self.handle_goodbye,
            'dur': self.handle_stop,
            'sus': self.handle_stop
        }
    
    def start_listening(self):
        """Sesli dinlemeyi başlat"""
        if self.is_listening:
            return
        
        if not SPEECH_RECOGNITION_AVAILABLE or not self.recognizer or not self.microphone:
            print("⚠️ Ses tanıma sistemi mevcut değil")
            return False
        
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self._listen_loop)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
        self.speak("🎤 Dinliyorum... Komutlarınızı söyleyin")
        print("🎤 Sesli dinleme başlatıldı")
        return True
    
    def stop_listening(self):
        """Sesli dinlemeyi durdur"""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=1)
        print("🔇 Sesli dinleme durduruldu")
    
    def _listen_loop(self):
        """Sürekli dinleme döngüsü"""
        with self.microphone as source:
            # Gürültü ayarlaması
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Kısa süre dinle
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Thread'de işle
                processing_thread = threading.Thread(
                    target=self._process_audio, 
                    args=(audio,)
                )
                processing_thread.daemon = True
                processing_thread.start()
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"⚠️ Dinleme hatası: {e}")
                time.sleep(0.1)
    
    def _process_audio(self, audio):
        """Ses verisini işle"""
        try:
            # Ses tanıma
            text = self.recognizer.recognize_google(audio, language='tr-TR')
            print(f"🎤 Algılanan: {text}")
            
            # Komut işle
            self.process_command(text)
            
        except sr.UnknownValueError:
            pass  # Anlaşılamayan ses
        except sr.RequestError as e:
            print(f"⚠️ Ses tanıma hatası: {e}")
        except Exception as e:
            print(f"⚠️ Ses işleme hatası: {e}")
    
    def process_command(self, text: str):
        """Komut işleme"""
        text = text.lower().strip()
        
        # Komut geçmişine ekle
        self.command_history.append({
            'command': text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Doğrudan komut eşleştirme
        if text in self.voice_commands:
            self.voice_commands[text]()
            return
        
        # AI destekli komut analizi
        self.analyze_command_with_ai(text)
    
    def analyze_command_with_ai(self, text: str):
        """AI ile komut analizi"""
        try:
            # OpenAI ile analiz
            if self.ai_models.get('openai'):
                response = self.analyze_with_openai(text)
                if response:
                    self.speak(response)
                    return
            
            # Yerel analiz
            self.analyze_locally(text)
            
        except Exception as e:
            print(f"⚠️ AI analiz hatası: {e}")
            self.speak("Üzgünüm, komutunuzu anlayamadım")
    
    def analyze_with_openai(self, text: str) -> Optional[str]:
        """OpenAI ile komut analizi"""
        try:
            prompt = f"""
            Sen bir Türkçe sesli asistanısın. Kullanıcının komutunu analiz et ve uygun yanıt ver.
            
            Komut: "{text}"
            
            Eğer komut:
            - Selamlama ise: Dostane bir şekilde selamla
            - B2B işlemi ise: İşlem hakkında bilgi ver
            - Sistem komutu ise: Güvenlik uyarısı ver
            - Web komutu ise: Web işlemi hakkında bilgi ver
            - Anlaşılmıyor ise: Yardım teklif et
            
            Kısa ve net yanıt ver (maksimum 2 cümle):
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️ OpenAI analiz hatası: {e}")
            return None
    
    def analyze_locally(self, text: str):
        """Yerel komut analizi"""
        # Anahtar kelime analizi
        for category, data in self.commands.items():
            for keyword in data['keywords']:
                if keyword in text:
                    self.handle_category_command(category, text)
                    return
        
        # Genel yanıt
        self.speak("Bu komutu anlayamadım. 'Yardım' diyerek komutları görebilirsiniz")
    
    def handle_category_command(self, category: str, text: str):
        """Kategori bazlı komut işleme"""
        if category == 'genel':
            self.speak("Merhaba! Size nasıl yardımcı olabilirim?")
        elif category == 'b2b':
            self.speak("B2B işlemleri için lütfen GUI'yi kullanın")
        elif category == 'web':
            self.speak("Web işlemleri için hangi siteyi açmamı istiyorsunuz?")
        elif category == 'sistem':
            self.speak("Sistem komutları güvenlik nedeniyle kısıtlıdır")
        else:
            self.speak("Bu komutu işleyemiyorum")
    
    # Komut işleyicileri
    def handle_greeting(self):
        """Selamlama"""
        greetings = [
            "Merhaba! Size nasıl yardımcı olabilirim?",
            "Selam! Ne yapmak istiyorsunuz?",
            "Hey! Hangi konuda yardıma ihtiyacınız var?"
        ]
        self.speak(greetings[time.time() % len(greetings)])
    
    def handle_system_status(self):
        """Sistem durumu"""
        import psutil
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        self.speak(f"Sistem durumu: CPU %{cpu}, RAM %{memory}")
    
    def handle_shutdown(self):
        """Bilgisayarı kapat"""
        self.speak("Güvenlik nedeniyle sistem kapatma komutu çalıştırılamaz")
    
    def handle_restart(self):
        """Yeniden başlat"""
        self.speak("Güvenlik nedeniyle yeniden başlatma komutu çalıştırılamaz")
    
    def handle_search_companies(self):
        """Firma arama"""
        self.speak("Firma arama için lütfen GUI'deki arama sekmesini kullanın")
    
    def handle_customer_list(self):
        """Müşteri listesi"""
        self.speak("Müşteri listesi için lütfen GUI'deki firmalar sekmesini kullanın")
    
    def handle_send_email(self):
        """Email gönder"""
        self.speak("Email göndermek için lütfen GUI'deki email sekmesini kullanın")
    
    def handle_create_report(self):
        """Rapor oluştur"""
        self.speak("Rapor oluşturmak için lütfen GUI'deki rapor sekmesini kullanın")
    
    def handle_open_website(self):
        """Web sitesi aç"""
        self.speak("Hangi web sitesini açmamı istiyorsunuz?")
    
    def handle_web_search(self):
        """Web arama"""
        self.speak("Web araması için hangi terimi aramamı istiyorsunuz?")
    
    def handle_open_youtube(self):
        """YouTube aç"""
        webbrowser.open("https://youtube.com")
        self.speak("YouTube açıldı")
    
    def handle_open_file(self):
        """Dosya aç"""
        self.speak("Hangi dosyayı açmamı istiyorsunuz?")
    
    def handle_open_folder(self):
        """Klasör aç"""
        self.speak("Hangi klasörü açmamı istiyorsunuz?")
    
    def handle_open_desktop(self):
        """Masaüstü aç"""
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        os.startfile(desktop_path)
        self.speak("Masaüstü açıldı")
    
    def handle_help(self):
        """Yardım"""
        help_text = """
        Kullanabileceğiniz komutlar:
        - Merhaba, Selam
        - Sistem durumu
        - Firma ara
        - Email gönder
        - Web sitesi aç
        - Dosya aç
        - Yardım
        - Görüşürüz
        """
        self.speak(help_text)
    
    def handle_commands(self):
        """Komut listesi"""
        self.handle_help()
    
    def handle_capabilities(self):
        """Yetenekler"""
        capabilities = """
        Yapabileceklerim:
        - Sesli komutları anlama
        - B2B işlemleri hakkında bilgi verme
        - Web sitelerini açma
        - Dosya işlemleri
        - Sistem durumu kontrolü
        - AI destekli yanıtlar
        """
        self.speak(capabilities)
    
    def handle_thanks(self):
        """Teşekkür"""
        responses = [
            "Rica ederim!",
            "Ne demek, her zaman!",
            "Memnuniyetle!",
            "Başka bir şey var mı?"
        ]
        self.speak(responses[time.time() % len(responses)])
    
    def handle_goodbye(self):
        """Veda"""
        self.speak("Görüşürüz! İyi günler!")
        self.stop_listening()
    
    def handle_stop(self):
        """Dur"""
        self.speak("Tamam, durdum")
        self.stop_listening()
    
    def speak(self, text: str):
        """Metni sesli olarak söyle"""
        if self.is_speaking:
            return
        
        if not PYTTSX3_AVAILABLE or not self.tts_engine:
            print(f"🔊 (Ses sentezi mevcut değil) {text}")
            return
        
        self.is_speaking = True
        
        def _speak():
            try:
                print(f"🔊 Asistan: {text}")
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"⚠️ Ses sentezi hatası: {e}")
                print(f"🔊 (Ses sentezi mevcut değil) {text}")
            finally:
                self.is_speaking = False
        
        # Thread'de konuş
        speak_thread = threading.Thread(target=_speak)
        speak_thread.daemon = True
        speak_thread.start()
    
    def get_status(self) -> Dict:
        """Asistan durumu"""
        return {
            'is_listening': self.is_listening,
            'is_speaking': self.is_speaking,
            'command_count': len(self.command_history),
            'ai_models_loaded': len(self.ai_models),
            'last_command': self.command_history[-1] if self.command_history else None
        }
    
    def get_command_history(self) -> List[Dict]:
        """Komut geçmişi"""
        return self.command_history[-10:]  # Son 10 komut
    
    def clear_history(self):
        """Geçmişi temizle"""
        self.command_history.clear()
        print("🗑️ Komut geçmişi temizlendi")
    
    def update_config(self, new_config: Dict):
        """Konfigürasyonu güncelle"""
        self.config.update(new_config)
        
        # AI modellerini yeniden yükle
        if new_config.get('openai_api_key'):
            self.setup_ai_models()
        
        print("⚙️ Konfigürasyon güncellendi")
    
    def export_data(self, filepath: str):
        """Verileri dışa aktar"""
        data = {
            'command_history': self.command_history,
            'user_preferences': self.user_preferences,
            'status': self.get_status(),
            'export_time': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 Veriler dışa aktarıldı: {filepath}")


class VoiceAssistantGUI:
    """
    🎤 Sesli Asistan GUI Yöneticisi
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.assistant = None
        self.setup_assistant()
    
    def setup_assistant(self):
        """Asistanı başlat"""
        try:
            # Config'i main window'dan al
            config = self.main_window.load_settings() if hasattr(self.main_window, 'load_settings') else {}
            
            self.assistant = VoiceAssistant(config)
            print("✅ Sesli Asistan GUI başlatıldı")
            
        except Exception as e:
            print(f"⚠️ Sesli Asistan başlatılamadı: {e}")
            self.assistant = None
    
    def start_listening(self):
        """Dinlemeyi başlat"""
        if self.assistant:
            self.assistant.start_listening()
            return True
        return False
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.assistant:
            self.assistant.stop_listening()
            return True
        return False
    
    def speak(self, text: str):
        """Metni söyle"""
        if self.assistant:
            self.assistant.speak(text)
            return True
        return False
    
    def get_status(self) -> Dict:
        """Durum bilgisi"""
        if self.assistant:
            return self.assistant.get_status()
        return {'is_listening': False, 'is_speaking': False}
    
    def get_command_history(self) -> List[Dict]:
        """Komut geçmişi"""
        if self.assistant:
            return self.assistant.get_command_history()
        return []
    
    def clear_history(self):
        """Geçmişi temizle"""
        if self.assistant:
            self.assistant.clear_history()
    
    def export_data(self, filepath: str):
        """Verileri dışa aktar"""
        if self.assistant:
            self.assistant.export_data(filepath)
            return True
        return False


# Test fonksiyonu
def test_voice_assistant():
    """Sesli asistan testi"""
    print("🎤 Sesli Asistan Test Başlatılıyor...")
    
    assistant = VoiceAssistant()
    
    # Test komutları
    test_commands = [
        "merhaba",
        "sistem durumu",
        "yardım",
        "görüşürüz"
    ]
    
    for command in test_commands:
        print(f"\n🧪 Test komutu: {command}")
        assistant.process_command(command)
        time.sleep(2)
    
    print("\n✅ Test tamamlandı")


if __name__ == "__main__":
    test_voice_assistant()
