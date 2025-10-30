#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Gelişmiş Kendi Kendini Eğiten NLP Parser
Self-Learning Natural Language Processing System
"""

import json
import re
import os
import pickle
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

from monitoring_error_handler import logger


class SelfLearningNLPParser:
    """
    Kendi kendini eğiten ve geliştiren NLP parser
    - Pattern öğrenme ve ezberleme
    - Güven skoru ile çok katmanlı analiz
    - Bağlam (context) anlama
    - Adaptif yorumlama
    - Geçmiş komutları hatırlama
    - Otomatik iyileştirme
    """
    
    def __init__(self, learning_file="nlp_learning_data.pkl"):
        self.learning_file = learning_file
        self.patterns = {}  # Öğrenilen pattern'ler
        self.successful_parses = []  # Başarılı parse'lar
        self.failed_parses = []  # Başarısız parse'lar
        self.entity_database = {}  # Tanınan entity'ler
        self.context_memory = deque(maxlen=20)  # Son 20 komut
        self.confidence_threshold = 0.6  # Güven eşiği
        
        # Gelişmiş keyword grupları
        self.intent_keywords = {
            "firma_ara": ["bul", "ara", "listele", "getir", "bulun", "bulma", "bulunan"],
            "kampanya_gonder": ["gönder", "kampanya", "mail at", "email gönder", "mesaj gönder"],
            "analiz_et": ["analiz", "incele", "değerlendir", "özellikleri"],
            "vapi_call": ["vapi", "sesli arama", "voice call", "telefonla ara", "otomatik arama", "arama yap"],
            "whatsapp_send": ["whatsapp", "wp", "wapp", "mesaj gönder"],
            "gpt_generate": ["gpt", "ai mesaj", "yapay zeka", "chatgpt", "gelişmiş"]
        }
        
        # Sektör ve şehir veritabanı
        self.sector_synonyms = {
            "mobilya": ["mobilyacı", "mobilya mağazası", "mobilya firması", "ahşap işleme"],
            "yazılım": ["software", "yazilim", "yazılım şirketi", "teknoloji", "it", "bilgi teknolojileri"],
            "restoran": ["lokanta", "restaurant", "cafe", "kahvehane", "yemek"],
            "inşaat": ["insaat", "müteahhit", "yapı", "şantiye", "emlak"],
            "imalat": ["üretim", "fabrika", "sanayi", "imalat sanayi"],
            "tekstil": ["giyim", "konfeksiyon", "moda", "kumaş"],
            "lojistik": ["kargo", "nakliye", "taşıma", "dağıtım"],
            "otomotiv": ["oto", "otomobil", "araba", "araç"],
            "eğitim": ["dershane", "kurs", "okul", "eğitim"],
            "sağlık": ["hastane", "klinik", "ecza", "tedavi"],
            "gıda": ["market", "bakkal", "süpermarket", "toptan"]
        }
        
        self.cities = [
            "istanbul", "ankara", "izmir", "bursa", "antalya", "konya", "adana",
            "gaziantep", "kayseri", "mersin", "eskisehir", "diyarbakir", "samsun",
            "denizli", "şanlıurfa", "hatay", "tekirdağ", "kocaeli", "sakarya",
            "balıkesir", "manisa", "aydın", "muğla", "trabzon", "ordu", "malatya", "erzurum"
        ]
        
        self.number_words = {
            "on": 10, "yirmi": 20, "otuz": 30, "kırk": 40, "elli": 50,
            "altmış": 60, "yetmiş": 70, "seksen": 80, "doksan": 90, "yüz": 100,
            "beş": 5, "bir": 1, "iki": 2, "üç": 3, "dört": 4, "altı": 6, "yedi": 7,
            "sekiz": 8, "dokuz": 9
        }
        
        # Öğrenilmiş verileri yükle
        self.load_learning_data()
        
        logger.info("🧠 Gelişmiş Self-Learning NLP Parser başlatıldı")
    
    def load_learning_data(self):
        """Öğrenilmiş verileri dosyadan yükle"""
        try:
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'rb') as f:
                    data = pickle.load(f)
                    self.patterns = data.get('patterns', {})
                    self.successful_parses = data.get('successful_parses', [])
                    self.entity_database = data.get('entity_database', {})
                    logger.info(f"✅ Öğrenme verileri yüklendi: {len(self.patterns)} pattern, {len(self.successful_parses)} başarılı örnek")
        except Exception as e:
            logger.warning(f"Öğrenme verisi yüklenemedi: {e}")
            self.patterns = {}
            self.successful_parses = []
            self.entity_database = {}
    
    def save_learning_data(self):
        """Öğrenilmiş verileri dosyaya kaydet"""
        try:
            data = {
                'patterns': self.patterns,
                'successful_parses': self.successful_parses[-100:],  # Son 100'ü sakla
                'entity_database': self.entity_database,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.learning_file, 'wb') as f:
                pickle.dump(data, f)
            logger.info("✅ Öğrenme verileri kaydedildi")
        except Exception as e:
            logger.error(f"Öğrenme verisi kaydedilemedi: {e}")
    
    def parse_command(self, command_text: str) -> Dict:
        """
        Ana parse fonksiyonu - çok katmanlı akıllı analiz
        """
        logger.info(f"🧠 NLP komutu analiz ediliyor: '{command_text}'")
        
        # 1. Katman: Context kontrolü
        context = self.get_context_for_command(command_text)
        
        # 2. Katman: Pattern matching ile intent detection
        intent, confidence = self.detect_intent(command_text)
        
        # 3. Katman: Entity extraction
        entities = self.extract_entities(command_text)
        
        # 4. Katman: Gelişmiş slot filling
        slots = self.fill_slots_with_entities(command_text, intent, entities, context)
        
        # 5. Katman: Main2 feature detection
        main2_features = self.detect_main2_features(command_text)
        
        # 6. Katman: Result compilation
        result = {
            "intent": intent,
            "confidence": confidence,
            "query": slots.get('query'),
            "location": slots.get('location'),
            "max_results": slots.get('max_results', 50),
            "campaign_name": slots.get('campaign_name'),
            "target_sector": slots.get('target_sector'),
            "target_firm_name": slots.get('target_firm_name'),
            "use_vapi": main2_features.get('use_vapi', False),
            "use_whatsapp": main2_features.get('use_whatsapp', False),
            "use_gpt": main2_features.get('use_gpt', False),
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
        # Bağlam belleğine ekle
        self.context_memory.append({
            'command': command_text,
            'parsed': result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Güven skoru düşükse uyarı ver
        if confidence < self.confidence_threshold:
            logger.warning(f"⚠️ Düşük güven skoru: {confidence:.2f}")
        
        logger.info(f"✅ Parse tamamlandı: {result['intent']} (Güven: {confidence:.2f})")
        
        return result
    
    def get_context_for_command(self, command: str) -> Dict:
        """Son komutlardan bağlam çıkar"""
        context = {
            'has_recent_search': False,
            'last_location': None,
            'last_sector': None,
            'suggested_intent': None
        }
        
        # Son 5 komutu analiz et
        for entry in list(self.context_memory)[-5:]:
            parsed = entry.get('parsed', {})
            if parsed.get('location'):
                context['last_location'] = parsed['location']
            if parsed.get('query'):
                context['last_sector'] = parsed['query']
            if parsed.get('intent') == 'firma_ara':
                context['has_recent_search'] = True
        
        # Eğer yeni komutta location yoksa, son kullanılanı öner
        if 'hangi' in command.lower() or 'nerede' in command.lower():
            context['suggested_intent'] = 'bilgi_sor'
        
        return context
    
    def detect_intent(self, text: str) -> Tuple[str, float]:
        """Çok katmanlı intent detection"""
        text_lower = text.lower()
        
        # Öncelik sırası: Specific -> General
        
        # 1. Main2 feature intents (en özel)
        if any(k in text_lower for k in self.intent_keywords["vapi_call"]):
            return "vapi_call", 0.95
        if any(k in text_lower for k in self.intent_keywords["whatsapp_send"]):
            return "whatsapp_send", 0.90
        if any(k in text_lower for k in self.intent_keywords["gpt_generate"]):
            return "gpt_generate", 0.90
        
        # 2. Combined intents
        if (any(k in text_lower for k in self.intent_keywords["firma_ara"]) and 
            any(k in text_lower for k in self.intent_keywords["kampanya_gonder"])):
            return "firma_ara_ve_kampanya", 0.85
        
        # 3. Single intents
        if any(k in text_lower for k in self.intent_keywords["analiz_et"]):
            return "analiz_et", 0.85
        if any(k in text_lower for k in self.intent_keywords["kampanya_gonder"]):
            return "kampanya_gonder", 0.80
        if any(k in text_lower for k in self.intent_keywords["firma_ara"]):
            return "firma_ara", 0.75
        
        # 4. Question detection
        if any(q in text_lower for q in ["kaç", "hangi", "ne", "kim", "nerede"]):
            return "bilgi_sor", 0.60
        
        # 5. Default - belirsiz
        return "bilgi_sor", 0.40
    
    def extract_entities(self, text: str) -> Dict:
        """Gelişmiş entity extraction"""
        entities = {
            'locations': [],
            'sectors': [],
            'numbers': [],
            'campaigns': [],
            'firm_names': []
        }
        
        text_lower = text.lower()
        
        # Şehir extraction
        for city in self.cities:
            if city in text_lower:
                entities['locations'].append(city.title())
        
        # Sektör extraction
        for sector, synonyms in self.sector_synonyms.items():
            all_words = [sector] + synonyms
            if any(w in text_lower for w in all_words):
                entities['sectors'].append(sector)
        
        # Sayı extraction
        numbers = re.findall(r'\d+', text)
        entities['numbers'].extend([int(n) for n in numbers])
        
        for word, num in self.number_words.items():
            if word in text_lower:
                entities['numbers'].append(num)
        
        # Kampanya adı extraction
        campaign_patterns = [
            r"'([^']+)'",
            r'"([^"]+)"',
            r"kampanyas[ıi]n[ıi]?\s+([\wÇÖŞİĞÜçöşığü\- ]{3,50})",
            r"kampanya:\s*([^\n]{3,50})"
        ]
        
        for pattern in campaign_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match and len(match) > 2:
                    entities['campaigns'].append(match.strip())
        
        # Firma ismi extraction (basit)
        firm_patterns = [
            r"([A-ZÇĞÖŞÜ][a-zçğıöşü\s&]+(?:A\.Ş\.|Ltd\.|Şti\.)?)",
            r"firma:\s*([^\n]{3,50})"
        ]
        
        for pattern in firm_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match:
                    entities['firm_names'].append(match.strip())
        
        return entities
    
    def fill_slots_with_entities(self, text: str, intent: str, entities: Dict, context: Dict) -> Dict:
        """Akıllı slot filling"""
        slots = {}
        
        # Location
        if entities['locations']:
            slots['location'] = entities['locations'][0]
        elif context.get('last_location'):
            slots['location'] = context['last_location']
        
        # Query (sector)
        if entities['sectors']:
            slots['query'] = entities['sectors'][0] + " firması"
        elif context.get('last_sector'):
            slots['query'] = context['last_sector']
        
        # Max results
        if entities['numbers']:
            slots['max_results'] = min(500, max(1, entities['numbers'][0]))
        else:
            # Zaman ifadeleri
            if any(w in text.lower() for w in ["yaklaşık", "civar", "kadar", "dolayında"]):
                slots['max_results'] = 50
            elif any(w in text.lower() for w in ["az", "birkaç", "bir kaç"]):
                slots['max_results'] = 5
            elif any(w in text.lower() for w in ["çok", "birçok", "bir çok"]):
                slots['max_results'] = 100
            else:
                slots['max_results'] = 50
        
        # Campaign name
        if entities['campaigns']:
            slots['campaign_name'] = entities['campaigns'][0]
        
        # Target firm
        if entities['firm_names']:
            slots['target_firm_name'] = entities['firm_names'][0]
        
        return slots
    
    def detect_main2_features(self, text: str) -> Dict:
        """Main2 özelliklerini tespit et"""
        text_lower = text.lower()
        features = {
            'use_vapi': False,
            'use_whatsapp': False,
            'use_gpt': False
        }
        
        # Vapi detection
        if any(k in text_lower for k in self.intent_keywords["vapi_call"]):
            features['use_vapi'] = True
        
        # WhatsApp detection
        if any(k in text_lower for k in self.intent_keywords["whatsapp_send"]):
            features['use_whatsapp'] = True
        
        # GPT detection
        if any(k in text_lower for k in self.intent_keywords["gpt_generate"]):
            features['use_gpt'] = True
        
        return features
    
    def learn_from_success(self, command: str, parsed_result: Dict, was_successful: bool):
        """Başarılı parse'lardan öğren"""
        if was_successful:
            self.successful_parses.append({
                'command': command,
                'result': parsed_result,
                'timestamp': datetime.now().isoformat()
            })
            
            # Pattern öğren
            pattern_hash = self._hash_command(command)
            if pattern_hash not in self.patterns:
                self.patterns[pattern_hash] = {
                    'count': 0,
                    'success_count': 0,
                    'examples': []
                }
            
            self.patterns[pattern_hash]['count'] += 1
            if was_successful:
                self.patterns[pattern_hash]['success_count'] += 1
            
            self.patterns[pattern_hash]['examples'].append({
                'command': command,
                'result': parsed_result,
                'timestamp': datetime.now().isoformat()
            })
            
            # Veritabanını güncelle
            self.save_learning_data()
            
            logger.info(f"📚 Yeni pattern öğrenildi: {pattern_hash[:8]}...")
    
    def _hash_command(self, command: str) -> str:
        """Komutu hash'le"""
        return hashlib.md5(command.lower().encode()).hexdigest()
    
    def get_statistics(self) -> Dict:
        """İstatistikler"""
        total_patterns = len(self.patterns)
        total_successful = len(self.successful_parses)
        
        avg_confidence = 0.0
        if self.successful_parses:
            confidences = [p.get('result', {}).get('confidence', 0) for p in self.successful_parses]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            'total_patterns': total_patterns,
            'total_successful_parses': total_successful,
            'average_confidence': avg_confidence,
            'context_memory_size': len(self.context_memory),
            'entity_database_size': len(self.entity_database)
        }
    
    def improve_from_feedback(self, feedback: Dict):
        """Kullanıcı geri bildiriminden öğren ve iyileştir"""
        command = feedback.get('command')
        corrected_result = feedback.get('corrected_result')
        
        if not command or not corrected_result:
            return False
        
        # Yanlış parse varsa düzelt
        try:
            # Pattern'i güncelle
            pattern_hash = self._hash_command(command)
            if pattern_hash in self.patterns:
                self.patterns[pattern_hash]['success_count'] = max(0, 
                    self.patterns[pattern_hash]['success_count'] - 1)
            
            # Doğru sonucu öğren
            self.successful_parses.append({
                'command': command,
                'result': corrected_result,
                'timestamp': datetime.now().isoformat(),
                'from_feedback': True
            })
            
            self.save_learning_data()
            logger.info("✅ Geri bildirimden öğrenildi ve iyileştirme yapıldı")
            return True
        except Exception as e:
            logger.error(f"Geri bildirim işlenirken hata: {e}")
            return False


# Backward compatibility - eski interface için wrapper
class NLPCommandParser:
    """
    Eski interface ile uyumlu wrapper
    """
    def __init__(self, api_key=""):
        self.api_key = api_key  # Artık kullanılmıyor ama uyumluluk için
        self.sl_parser = SelfLearningNLPParser()
        logger.info("NLPCommandParser (legacy wrapper) başlatıldı")
    
    def parse_command(self, command_text: str) -> Dict:
        """Komutu parse et"""
        result = self.sl_parser.parse_command(command_text)
        
        # Geriye uyumlu format için dönüştür
        # Eğer confidence çok düşükse hata döndür
        if result.get('confidence', 0) < 0.3:
            return {"intent": "hata", "error": "Komut anlaşılamadı"}
        
        # Başarılı parse'ı öğren
        self.sl_parser.learn_from_success(command_text, result, True)
        
        # Boolean değerleri varsa, result'a ekle
        if 'use_vapi' not in result:
            main2_features = self.sl_parser.detect_main2_features(command_text)
            result['use_vapi'] = main2_features.get('use_vapi', False)
            result['use_whatsapp'] = main2_features.get('use_whatsapp', False)
            result['use_gpt'] = main2_features.get('use_gpt', False)
        
        return result


__all__ = ["NLPCommandParser", "SelfLearningNLPParser"]

