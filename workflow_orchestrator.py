# -*- coding: utf-8 -*-

import json
import os
import time
import threading
from datetime import datetime
from monitoring_error_handler import logger
from task_executor import TaskExecutor

class WorkflowOrchestrator:
    """
    Otomasyon iş akışlarını yöneten, adımları takip eden ve
    kaldığı yerden devam etmeyi sağlayan sınıf.
    """
    DEFAULT_STATE_FILE = "workflow_state.json"

    def __init__(self, task_executor: TaskExecutor, state_file=DEFAULT_STATE_FILE):
        if not isinstance(task_executor, TaskExecutor):
             raise TypeError("task_executor, TaskExecutor sınıfından olmalıdır.")
        self.task_executor = task_executor
        self.state_file = state_file
        self.current_workflow = None
        self._worker_thread = None
        self.load_state()
        logger.info("WorkflowOrchestrator başlatıldı.")

    def _run_async(self, progress_callback=None):
        if self._worker_thread and self._worker_thread.is_alive():
            logger.warning("İş akışı iş parçacığı zaten çalışıyor.")
            return
        self._worker_thread = threading.Thread(target=self.run_workflow, args=(progress_callback,), daemon=True)
        self._worker_thread.start()

    def save_state(self):
        if self.current_workflow:
            try:
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_workflow, f, indent=4, ensure_ascii=False, default=str)
                logger.info(f"İş akışı durumu kaydedildi: {self.state_file}")
            except Exception as e:
                logger.error(f"İş akışı durumu kaydedilemedi: {e}")
        else:
             try:
                if os.path.exists(self.state_file):
                    os.remove(self.state_file)
                logger.info("Aktif iş akışı yok, durum dosyası temizlendi.")
             except Exception as e:
                 logger.error(f"Durum dosyası temizlenemedi: {e}")

    def load_state(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.current_workflow = json.load(f)
                logger.info(f"İş akışı durumu yüklendi: {self.state_file}")
                if self.current_workflow and 'start_time' in self.current_workflow:
                     try:
                           self.current_workflow['start_time'] = datetime.fromisoformat(self.current_workflow['start_time'])
                     except (TypeError, ValueError):
                           logger.warning("State dosyasındaki 'start_time' datetime'a çevrilemedi.")
            else:
                self.current_workflow = None
                logger.info("Kaydedilmiş iş akışı durumu bulunamadı.")
        except json.JSONDecodeError:
            logger.error(f"İş akışı durum dosyası okunamadı (JSON format hatası): {self.state_file}")
            self.current_workflow = None
            try:
                 os.rename(self.state_file, f"{self.state_file}.invalid_{int(time.time())}")
            except Exception as e:
                 logger.error(f"Hatalı state dosyası yeniden adlandırılamadı: {e}")
        except Exception as e:
            logger.error(f"İş akışı durumu yüklenemedi: {e}")
            self.current_workflow = None

    def start_new_workflow(self, workflow_id, command_data, progress_callback=None):
        if self.current_workflow and self.current_workflow.get('status') == 'running':
            logger.warning(f"Yeni iş akışı başlatılamadı. Mevcut iş akışı ({self.current_workflow.get('id')}) zaten çalışıyor.")
            if progress_callback:
                progress_callback(f"⚠️ Yeni iş akışı başlatılamadı. Mevcut iş akışı ({self.current_workflow.get('id')}) zaten çalışıyor.")
            return False

        self.current_workflow = {
            'id': workflow_id,
            'command': command_data,
            'status': 'starting',
            'current_step': 'search',
            'start_time': datetime.now(),
            'found_firms': [],
            'analyzed_firms': [],
            'sent_emails': [],
            'failed_steps': {},
            'progress': 0,
            'last_update': datetime.now()
        }
        logger.info(f"Yeni iş akışı başlatılıyor: {workflow_id}")
        self.save_state()
        self._run_async(progress_callback)
        return True

    def resume_workflow(self, progress_callback=None):
        if not self.current_workflow:
            logger.info("Devam ettirilecek yarım kalmış iş akışı bulunamadı.")
            if progress_callback:
                progress_callback("ℹ️ Devam ettirilecek iş akışı yok.")
            return False
        status = self.current_workflow.get('status')
        if status == 'completed' or status == 'failed':
             logger.info(f"İş akışı ({self.current_workflow.get('id')}) zaten tamamlanmış veya başarısız olmuş. Durum: {status}")
             if progress_callback:
                  progress_callback(f"ℹ️ İş akışı zaten {status} durumunda.")
             self.current_workflow = None
             self.save_state()
             return False
        logger.info(f"İş akışı ({self.current_workflow.get('id')}) kaldığı yerden devam ettiriliyor. Adım: {self.current_workflow.get('current_step')}")
        self.current_workflow['status'] = 'running'
        self.save_state()
        self._run_async(progress_callback)
        return True

    def run_workflow(self, progress_callback=None):
        if not self.current_workflow or self.current_workflow.get('status') != 'running':
             if self.current_workflow and self.current_workflow.get('status') == 'starting':
                  self.current_workflow['status'] = 'running'
             else:
                  logger.warning("Çalıştırılacak aktif bir iş akışı bulunamadı.")
                  return
        try:
            while self.current_workflow.get('status') == 'running':
                step = self.current_workflow['current_step']
                command_data = self.current_workflow['command']
                if progress_callback:
                    progress_callback(f"🔄 Adım yürütülüyor: {step}...")
                if step == 'search':
                    if not self.current_workflow.get('found_firms'):
                        query = command_data.get('query')
                        location = command_data.get('location')
                        max_results = command_data.get('max_results', 50)
                        if not query or not location:
                             raise ValueError("Arama için 'query' ve 'location' gerekli.")
                        found_firms_data = self.task_executor.execute_search(
                            query, location, max_results, progress_callback
                        )
                        if found_firms_data is None:
                            raise RuntimeError("Arama adımı başarısız oldu.")
                        elif isinstance(found_firms_data, list):
                             self.current_workflow['found_firms'] = [{'id': f['id'], 'name': f['name'], 'website': f.get('website')} for f in found_firms_data if f.get('id')]
                             self.current_workflow['current_step'] = 'analyze'
                             self.current_workflow['progress'] = 33
                             logger.info(f"Arama adımı tamamlandı. {len(self.current_workflow['found_firms'])} firma bulundu.")
                        else:
                             raise TypeError(f"execute_search beklenmedik bir tip döndürdü: {type(found_firms_data)}")
                    else:
                        logger.info("Arama adımı daha önce tamamlanmış, analiz adımına geçiliyor.")
                        self.current_workflow['current_step'] = 'analyze'
                        self.current_workflow['progress'] = 33
                elif step == 'analyze':
                     firms_to_analyze = [f for f in self.current_workflow.get('found_firms', [])
                                         if f.get('id') not in self.current_workflow.get('analyzed_firms', [])]
                     if not firms_to_analyze:
                          logger.info("Analiz edilecek yeni firma yok, kampanya adımına geçiliyor.")
                          self.current_workflow['current_step'] = 'campaign'
                          self.current_workflow['progress'] = 66
                     else:
                          logger.info(f"{len(firms_to_analyze)} firma analiz edilecek.")
                          analyzed_count = 0
                          for i, firm_info in enumerate(firms_to_analyze):
                               if self.current_workflow.get('status') != 'running':
                                    logger.info("Analiz adımı durduruldu.")
                                    break
                               firm_data_to_analyze = firm_info
                               analysis_result = self.task_executor.execute_analysis(
                                    firm_data_to_analyze, progress_callback
                               )
                               if analysis_result:
                                    self.current_workflow.setdefault('analyzed_firms', []).append(firm_info['id'])
                                    analyzed_count += 1
                               else:
                                    logger.warning(f"Firma analizi başarısız: {firm_info.get('name')}")
                                    self.current_workflow.setdefault('failed_steps', {}).setdefault('analyze', []).append(firm_info.get('id'))
                               step_progress = int((i + 1) / len(firms_to_analyze) * 33)
                               self.current_workflow['progress'] = 33 + step_progress
                               self.save_state()
                          logger.info(f"Analiz adımı tamamlandı. {analyzed_count} firma analiz edildi.")
                          if self.current_workflow.get('status') == 'running':
                                self.current_workflow['current_step'] = 'campaign'
                                self.current_workflow['progress'] = 66
                elif step == 'campaign':
                     template = command_data.get('campaign_template', {'instructions': 'Varsayılan kampanya içeriği.'})
                     firms_to_send_ids = [f_id for f_id in self.current_workflow.get('analyzed_firms', [])
                                            if f_id not in self.current_workflow.get('sent_emails', [])]
                     if not firms_to_send_ids:
                           logger.info("Email gönderilecek uygun firma bulunamadı.")
                           self.current_workflow['status'] = 'completed'
                     else:
                          logger.info(f"{len(firms_to_send_ids)} firmaya kampanya gönderilecek.")
                          firms_data_to_send = []
                          if self.task_executor.db:
                              for firm_id in firms_to_send_ids:
                                   firm_detail = self.task_executor.db.get_firm_by_id(firm_id)
                                   if firm_detail:
                                       firms_data_to_send.append(firm_detail)
                                   else:
                                        logger.warning(f"Kampanya için firma detayı bulunamadı: ID={firm_id}")
                          else:
                               logger.error("Veritabanı bağlantısı yok, kampanya gönderilemiyor.")
                               raise RuntimeError("Veritabanı bağlantısı yok.")
                          if not firms_data_to_send:
                               logger.warning("Email gönderilecek firma verisi bulunamadı.")
                               self.current_workflow['status'] = 'completed'
                          else:
                               campaign_result = self.task_executor.execute_campaign(
                                    firms_data_to_send, template, progress_callback
                               )
                               if campaign_result is None:
                                    raise RuntimeError("Kampanya adımı başarısız oldu.")
                               if 'results' in campaign_result and 'sent' in campaign_result['results']:
                                    sent_list = self.current_workflow.setdefault('sent_emails', [])
                                    for sent_item in campaign_result['results']['sent']:
                                           pass
                               if 'results' in campaign_result and 'failed' in campaign_result['results']:
                                    fail_list = self.current_workflow.setdefault('failed_steps', {}).setdefault('campaign', [])
                                    for failed_item in campaign_result['results']['failed']:
                                         fail_list.append(failed_item.get('firm', 'Bilinmeyen'))
                               self.current_workflow['progress'] = 100
                               self.current_workflow['status'] = 'completed'
                               logger.info("Kampanya adımı tamamlandı.")
                else:
                    raise ValueError(f"Bilinmeyen iş akışı adımı: {step}")
                self.current_workflow['last_update'] = datetime.now()
                self.save_state()
                if self.current_workflow.get('status') == 'completed':
                    logger.info(f"İş akışı ({self.current_workflow.get('id')}) başarıyla tamamlandı.")
                    if progress_callback:
                        progress_callback(f"🎉 İş akışı tamamlandı!")
                    self.current_workflow = None
                    self.save_state()
                    break
                elif self.current_workflow.get('status') == 'paused':
                     logger.info(f"İş akışı ({self.current_workflow.get('id')}) duraklatıldı.")
                     if progress_callback:
                           progress_callback(f"⏸️ İş akışı duraklatıldı.")
                     break
        except Exception as e:
            self.current_workflow['status'] = 'failed'
            self.current_workflow['failed_steps'][step] = str(e)
            self.current_workflow['last_update'] = datetime.now()
            logger.critical(f"İş akışı hatası ({self.current_workflow.get('id')}) - Adım: {step}. Hata: {e}", exc_info=True)
            self.save_state()
            if progress_callback:
                progress_callback(f"❌ İş akışı hatası: {e}")

    def pause_workflow(self):
         if self.current_workflow and self.current_workflow.get('status') == 'running':
              self.current_workflow['status'] = 'paused'
              self.save_state()
              logger.info(f"İş akışı ({self.current_workflow.get('id')}) duraklatıldı.")
              return True
         return False

    def stop_workflow(self):
         if self.current_workflow:
              workflow_id = self.current_workflow.get('id')
              self.current_workflow['status'] = 'stopped'
              logger.info(f"İş akışı ({workflow_id}) durduruluyor.")
              self.current_workflow = None
              self.save_state()
              logger.info(f"İş akışı ({workflow_id}) durduruldu ve temizlendi.")
              return True
         return False

    def get_workflow_status(self):
        if not self.current_workflow:
            return {'status': 'idle', 'message': 'Aktif iş akışı yok.'}
        status = self.current_workflow.get('status', 'unknown')
        step = self.current_workflow.get('current_step', 'N/A')
        progress = self.current_workflow.get('progress', 0)
        found_count = len(self.current_workflow.get('found_firms', []))
        analyzed_count = len(self.current_workflow.get('analyzed_firms', []))
        sent_count = len(self.current_workflow.get('sent_emails', []))
        message = f"Durum: {status.upper()} | Adım: {step} | İlerleme: %{progress} | "
        message += f"Bulunan: {found_count} | Analiz Edilen: {analyzed_count} | Email Gönderilen: {sent_count}"
        return {'status': status, 'step': step, 'progress': progress, 'message': message, 'details': self.current_workflow}

__all__ = ["WorkflowOrchestrator"]


