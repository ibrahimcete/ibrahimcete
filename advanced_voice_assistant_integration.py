"""
🚀 GELİŞMİŞ SESLİ ASİSTAN ENTEGRASYONU
Tüm AI Modüllerini Birleştiren Ana Sistem
"""

import os
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
import queue

# Ana modüller
try:
    from ai_conversational_intelligence import AIConversationalIntelligence
    from business_intelligence_analyzer import BusinessIntelligenceAnalyzer
    from ai_memory_personalization import AIMemoryPersonalization
    from crm_data_integration import CRMDataIntegration
    ADVANCED_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Gelişmiş modüller yüklenemedi: {e}")
    ADVANCED_MODULES_AVAILABLE = False

# Sesli asistan modülü
try:
    from voice_assistant import VoiceAssistant, VoiceAssistantGUI
    VOICE_ASSISTANT_AVAILABLE = True
except ImportError:
    VOICE_ASSISTANT_AVAILABLE = False
    print("⚠️ Sesli asistan modülü yüklenemedi")


class AdvancedVoiceAssistantIntegration:
    """
    🚀 Gelişmiş Sesli Asistan Entegrasyonu
    Tüm AI Modüllerini Birleştiren Ana Sistem
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.is_active = False
        
        # Ana modüller
        self.conversational_intelligence = None
        self.business_intelligence = None
        self.memory_personalization = None
        self.crm_integration = None
        self.voice_assistant = None
        
        # Entegrasyon durumu
        self.integration_status = {
            'conversational_intelligence': False,
            'business_intelligence': False,
            'memory_personalization': False,
            'crm_integration': False,
            'voice_assistant': False
        }
        
        # Sistem durumu
        self.system_status = {
            'is_learning': False,
            'is_analyzing': False,
            'is_integrating': False,
            'is_listening': False,
            'last_activity': None
        }
        
        # Modülleri başlat
        self.initialize_modules()
        
        print("🚀 Gelişmiş Sesli Asistan Entegrasyonu başlatıldı")
    
    def initialize_modules(self):
        """Modülleri başlat"""
        try:
            # 1. Konuşma Zekası
            if ADVANCED_MODULES_AVAILABLE:
                try:
                    self.conversational_intelligence = AIConversationalIntelligence(self.config)
                    self.integration_status['conversational_intelligence'] = True
                    print("✅ Konuşma Zekası başlatıldı")
                except Exception as e:
                    print(f"⚠️ Konuşma Zekası başlatılamadı: {e}")
            
            # 2. İş Zekası
            if ADVANCED_MODULES_AVAILABLE:
                try:
                    self.business_intelligence = BusinessIntelligenceAnalyzer(
                        database_path="business_intelligence.db",
                        config=self.config
                    )
                    self.integration_status['business_intelligence'] = True
                    print("✅ İş Zekası başlatıldı")
                except Exception as e:
                    print(f"⚠️ İş Zekası başlatılamadı: {e}")
            
            # 3. Hafıza ve Kişiselleştirme
            if ADVANCED_MODULES_AVAILABLE:
                try:
                    self.memory_personalization = AIMemoryPersonalization(
                        database_path="ai_memory.db",
                        config=self.config
                    )
                    self.integration_status['memory_personalization'] = True
                    print("✅ Hafıza ve Kişiselleştirme başlatıldı")
                except Exception as e:
                    print(f"⚠️ Hafıza ve Kişiselleştirme başlatılamadı: {e}")
            
            # 4. CRM Entegrasyonu
            if ADVANCED_MODULES_AVAILABLE:
                try:
                    self.crm_integration = CRMDataIntegration(
                        database_path="crm_integration.db",
                        config=self.config
                    )
                    self.integration_status['crm_integration'] = True
                    print("✅ CRM Entegrasyonu başlatıldı")
                except Exception as e:
                    print(f"⚠️ CRM Entegrasyonu başlatılamadı: {e}")
            
            # 5. Sesli Asistan
            if VOICE_ASSISTANT_AVAILABLE:
                try:
                    self.voice_assistant = VoiceAssistant(self.config)
                    self.integration_status['voice_assistant'] = True
                    print("✅ Sesli Asistan başlatıldı")
                except Exception as e:
                    print(f"⚠️ Sesli Asistan başlatılamadı: {e}")
            
        except Exception as e:
            print(f"⚠️ Modül başlatma hatası: {e}")
    
    def start_advanced_system(self):
        """Gelişmiş sistemi başlat"""
        if self.is_active:
            return
        
        self.is_active = True
        
        try:
            # 1. Konuşma zekasını başlat
            if self.conversational_intelligence:
                self.conversational_intelligence.start_conversation()
                self.system_status['is_listening'] = True
                print("🧠 Konuşma zekası aktif")
            
            # 2. İş zekasını başlat
            if self.business_intelligence:
                self.business_intelligence.start_continuous_analysis()
                self.system_status['is_analyzing'] = True
                print("📊 İş zekası aktif")
            
            # 3. Hafıza sistemini başlat
            if self.memory_personalization:
                self.memory_personalization.start_learning()
                self.system_status['is_learning'] = True
                print("🧠 Hafıza sistemi aktif")
            
            # 4. CRM entegrasyonunu başlat
            if self.crm_integration:
                self.crm_integration.start_integration()
                self.system_status['is_integrating'] = True
                print("🔗 CRM entegrasyonu aktif")
            
            # 5. Sesli asistanı başlat
            if self.voice_assistant:
                self.voice_assistant.start_listening()
                print("🎤 Sesli asistan aktif")
            
            self.system_status['last_activity'] = datetime.now().isoformat()
            print("🚀 Gelişmiş sistem tamamen aktif!")
            
        except Exception as e:
            print(f"⚠️ Gelişmiş sistem başlatma hatası: {e}")
    
    def stop_advanced_system(self):
        """Gelişmiş sistemi durdur"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        try:
            # 1. Konuşma zekasını durdur
            if self.conversational_intelligence:
                self.conversational_intelligence.stop_conversation()
                self.system_status['is_listening'] = False
                print("🧠 Konuşma zekası durduruldu")
            
            # 2. İş zekasını durdur
            if self.business_intelligence:
                self.business_intelligence.stop_continuous_analysis()
                self.system_status['is_analyzing'] = False
                print("📊 İş zekası durduruldu")
            
            # 3. Hafıza sistemini durdur
            if self.memory_personalization:
                self.memory_personalization.stop_learning()
                self.system_status['is_learning'] = False
                print("🧠 Hafıza sistemi durduruldu")
            
            # 4. CRM entegrasyonunu durdur
            if self.crm_integration:
                self.crm_integration.stop_integration()
                self.system_status['is_integrating'] = False
                print("🔗 CRM entegrasyonu durduruldu")
            
            # 5. Sesli asistanı durdur
            if self.voice_assistant:
                self.voice_assistant.stop_listening()
                print("🎤 Sesli asistan durduruldu")
            
            print("⏹️ Gelişmiş sistem durduruldu")
            
        except Exception as e:
            print(f"⚠️ Gelişmiş sistem durdurma hatası: {e}")
    
    def process_advanced_command(self, command: str, user_id: str = "default") -> Dict:
        """Gelişmiş komut işleme"""
        try:
            # 1. Hafıza sisteminden kişiselleştirilmiş yanıt al
            personalized_response = None
            if self.memory_personalization:
                personalized_response = self.memory_personalization.get_personalized_response(user_id, command)
            
            # 2. Konuşma zekası ile komutu analiz et
            conversational_response = None
            if self.conversational_intelligence:
                # Konuşma zekası komut işleme
                conversational_response = self.conversational_intelligence.process_advanced_command(command)
            
            # 3. İş zekası ile veri analizi yap
            business_insights = None
            if self.business_intelligence:
                business_insights = self.business_intelligence.get_business_insights()
            
            # 4. CRM entegrasyonu ile veri al
            crm_data = None
            if self.crm_integration:
                crm_data = self.crm_integration.get_integration_status()
            
            # 5. Birleşik yanıt oluştur
            response = {
                'command': command,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'personalized_response': personalized_response,
                'conversational_response': conversational_response,
                'business_insights': business_insights,
                'crm_data': crm_data,
                'system_status': self.system_status
            }
            
            # 6. Hafızaya kaydet
            if self.memory_personalization:
                self.memory_personalization.store_memory(
                    user_id=user_id,
                    content=command,
                    memory_type="short_term",
                    importance=0.7,
                    business_context="voice_command"
                )
            
            return response
            
        except Exception as e:
            print(f"⚠️ Gelişmiş komut işleme hatası: {e}")
            return {'error': str(e)}
    
    def get_system_status(self) -> Dict:
        """Sistem durumu"""
        return {
            'is_active': self.is_active,
            'integration_status': self.integration_status,
            'system_status': self.system_status,
            'modules_available': ADVANCED_MODULES_AVAILABLE,
            'voice_assistant_available': VOICE_ASSISTANT_AVAILABLE,
            'last_activity': self.system_status['last_activity']
        }
    
    def get_business_insights(self) -> List[Dict]:
        """İş içgörülerini al"""
        try:
            insights = []
            
            # İş zekası içgörüleri
            if self.business_intelligence:
                business_insights = self.business_intelligence.get_business_insights()
                insights.extend(business_insights)
            
            # CRM entegrasyonu içgörüleri
            if self.crm_integration:
                # CRM içgörüleri burada alınabilir
                pass
            
            return insights
            
        except Exception as e:
            print(f"⚠️ İş içgörüleri alma hatası: {e}")
            return []
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Kullanıcı profilini al"""
        try:
            profile = {}
            
            # Hafıza sisteminden profil al
            if self.memory_personalization:
                preferences = self.memory_personalization.get_user_preferences(user_id)
                patterns = self.memory_personalization.get_user_patterns(user_id)
                
                profile = {
                    'preferences': preferences,
                    'patterns': patterns,
                    'personalized': True
                }
            
            return profile
            
        except Exception as e:
            print(f"⚠️ Kullanıcı profili alma hatası: {e}")
            return {}
    
    def export_all_data(self, filepath: str):
        """Tüm verileri dışa aktar"""
        try:
            # Tüm modüllerden veri al
            all_data = {
                'system_status': self.get_system_status(),
                'business_insights': self.get_business_insights(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            # JSON dosyasına kaydet
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 Tüm veriler dışa aktarıldı: {filepath}")
            
        except Exception as e:
            print(f"⚠️ Veri dışa aktarma hatası: {e}")
    
    def test_system_integration(self):
        """Sistem entegrasyonunu test et"""
        try:
            print("🧪 Sistem entegrasyonu testi başlatılıyor...")
            
            # Test komutları
            test_commands = [
                "Hangi firmalar bizim son emailimizi açtı?",
                "Piyasa trendleri nasıl?",
                "En iyi müşteri adaylarımız kimler?",
                "Rekabet analizi yapabilir misin?",
                "Sistem durumu nedir?"
            ]
            
            # Sistemi başlat
            self.start_advanced_system()
            
            # Test komutlarını çalıştır
            for command in test_commands:
                print(f"\n🧪 Test komutu: {command}")
                response = self.process_advanced_command(command)
                print(f"📊 Yanıt: {response.get('conversational_response', 'Yanıt alınamadı')}")
                time.sleep(1)
            
            # Sistemi durdur
            self.stop_advanced_system()
            
            print("✅ Sistem entegrasyonu testi tamamlandı")
            
        except Exception as e:
            print(f"⚠️ Sistem entegrasyonu testi hatası: {e}")


class AdvancedVoiceAssistantGUI:
    """
    🎤 Gelişmiş Sesli Asistan GUI Yöneticisi
    Tüm modülleri entegre eden GUI sistemi
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.advanced_system = None
        self.setup_advanced_system()
    
    def setup_advanced_system(self):
        """Gelişmiş sistemi başlat"""
        try:
            # Config'i main window'dan al
            config = self.main_window.load_settings() if hasattr(self.main_window, 'load_settings') else {}
            
            self.advanced_system = AdvancedVoiceAssistantIntegration(config)
            print("✅ Gelişmiş Sesli Asistan GUI başlatıldı")
            
        except Exception as e:
            print(f"⚠️ Gelişmiş Sesli Asistan GUI başlatılamadı: {e}")
            self.advanced_system = None
    
    def start_advanced_listening(self):
        """Gelişmiş dinlemeyi başlat"""
        if self.advanced_system:
            self.advanced_system.start_advanced_system()
            return True
        return False
    
    def stop_advanced_listening(self):
        """Gelişmiş dinlemeyi durdur"""
        if self.advanced_system:
            self.advanced_system.stop_advanced_system()
            return True
        return False
    
    def process_advanced_command(self, command: str, user_id: str = "default"):
        """Gelişmiş komut işle"""
        if self.advanced_system:
            return self.advanced_system.process_advanced_command(command, user_id)
        return None
    
    def get_system_status(self):
        """Sistem durumu"""
        if self.advanced_system:
            return self.advanced_system.get_system_status()
        return {'is_active': False}
    
    def get_business_insights(self):
        """İş içgörülerini al"""
        if self.advanced_system:
            return self.advanced_system.get_business_insights()
        return []
    
    def get_user_profile(self, user_id: str = "default"):
        """Kullanıcı profilini al"""
        if self.advanced_system:
            return self.advanced_system.get_user_profile(user_id)
        return {}
    
    def export_all_data(self, filepath: str):
        """Tüm verileri dışa aktar"""
        if self.advanced_system:
            return self.advanced_system.export_all_data(filepath)
        return False


# Test fonksiyonu
def test_advanced_voice_assistant_integration():
    """Gelişmiş sesli asistan entegrasyonu testi"""
    print("🚀 Gelişmiş Sesli Asistan Entegrasyonu Test Başlatılıyor...")
    
    # Test konfigürasyonu
    config = {
        'openai_api_key': 'test-key'  # Gerçek API anahtarı gerekli
    }
    
    advanced_system = AdvancedVoiceAssistantIntegration(config)
    
    # Sistem entegrasyonunu test et
    advanced_system.test_system_integration()
    
    print("✅ Test tamamlandı")


if __name__ == "__main__":
    test_advanced_voice_assistant_integration()
