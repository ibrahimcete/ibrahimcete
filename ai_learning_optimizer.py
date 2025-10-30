import json
import os
from datetime import datetime
from monitoring_error_handler import logger


class AILearningOptimizer:
    LEARNING_DATA_FILE = "ai_learning_data.json"

    def __init__(self, db=None):
        self.db = db
        self.learning_data = self._load_learning_data()
        logger.info("AILearningOptimizer başlatıldı.")

    def _load_learning_data(self):
        if os.path.exists(self.LEARNING_DATA_FILE):
            try:
                with open(self.LEARNING_DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Öğrenme verisi yüklenemedi: {e}")
                return {"campaign_performance": {}, "nlp_feedback": []}
        return {"campaign_performance": {}, "nlp_feedback": []}

    def _save_learning_data(self):
        try:
            with open(self.LEARNING_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=4, ensure_ascii=False, default=str)
        except IOError as e:
            logger.error(f"Öğrenme verisi kaydedilemedi: {e}")

    def track_campaign_result(self, campaign_name, firm_id, action_type, success, details=None):
        timestamp = datetime.now().isoformat()
        campaign_key = str(campaign_name)
        firm_key = str(firm_id)
        if campaign_key not in self.learning_data["campaign_performance"]:
            self.learning_data["campaign_performance"][campaign_key] = {'sent': 0, 'interactions': []}
        interaction_log = {
            "firm_id": firm_key,
            "action": action_type,
            "success": success,
            "timestamp": timestamp,
            "details": details or {}
        }
        self.learning_data["campaign_performance"][campaign_key].setdefault('interactions', []).append(interaction_log)
        if action_type == 'sent':
             self.learning_data["campaign_performance"][campaign_key]['sent'] = self.learning_data["campaign_performance"][campaign_key].get('sent', 0) + 1
        elif action_type in ['opened', 'clicked', 'replied']:
             stat_key = f"{action_type}_count"
             self.learning_data["campaign_performance"][campaign_key][stat_key] = self.learning_data["campaign_performance"][campaign_key].get(stat_key, 0) + 1
        logger.info(f"Kampanya sonucu takip edildi: Kampanya='{campaign_name}', Firma='{firm_id}', Eylem='{action_type}'")
        self._save_learning_data()

    def get_campaign_performance(self, campaign_name):
        campaign_key = str(campaign_name)
        data = self.learning_data["campaign_performance"].get(campaign_key)
        if not data or not data.get('interactions'):
            return {"message": "Bu kampanya için veri bulunamadı."}
        interactions = data.get('interactions', [])
        sent = data.get('sent', len(interactions))
        opened = sum(1 for i in interactions if i['action'] == 'opened')
        clicked = sum(1 for i in interactions if i['action'] == 'clicked')
        replied = sum(1 for i in interactions if i['action'] == 'replied')
        performance = {
            "campaign_name": campaign_name,
            "total_sent": sent,
            "opened_count": opened,
            "clicked_count": clicked,
            "replied_count": replied,
            "open_rate": (opened / sent * 100) if sent > 0 else 0,
            "click_rate": (clicked / sent * 100) if sent > 0 else 0,
            "reply_rate": (replied / sent * 100) if sent > 0 else 0,
        }
        logger.info(f"Kampanya performansı hesaplandı: {campaign_name}")
        return performance

    def suggest_template(self, target_sector, goal):
        best_campaign = None
        max_reply_rate = -1
        for name, data in self.learning_data["campaign_performance"].items():
            perf = self.get_campaign_performance(name)
            if perf and 'reply_rate' in perf and perf['reply_rate'] > max_reply_rate:
                max_reply_rate = perf['reply_rate']
                best_campaign = name
        if best_campaign:
             logger.info(f"Şablon önerisi: En yüksek yanıt oranına sahip '{best_campaign}' kampanyası.")
             return best_campaign
        else:
             logger.info("Şablon önerisi için yeterli veri yok.")
             return None

    def add_nlp_feedback(self, command_text, parsed_data, is_correct, correct_data=None):
        feedback = {
            "command": command_text,
            "parsed": parsed_data,
            "is_correct": is_correct,
            "correct_data": correct_data if not is_correct else None,
            "timestamp": datetime.now().isoformat()
        }
        self.learning_data["nlp_feedback"].append(feedback)
        logger.info(f"NLP geri bildirimi eklendi: Komut='{command_text}', Doğru mu={is_correct}")
        self._save_learning_data()

    def get_nlp_feedback_summary(self):
        total = len(self.learning_data["nlp_feedback"])
        correct = sum(1 for fb in self.learning_data["nlp_feedback"] if fb['is_correct'])
        accuracy = (correct / total * 100) if total > 0 else 0
        return {"total_feedback": total, "correct_count": correct, "accuracy": accuracy}

__all__ = ["AILearningOptimizer"]
