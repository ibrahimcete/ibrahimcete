#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import hashlib
import threading
from contextlib import contextmanager
import logging
import pandas as pd
from collections import defaultdict
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """B2B Mail Automation Pro - Birleşik Database Yönetimi (main.py + main3.py uyumlu)"""
    
    def __init__(self, db_path: str = "b2b_automation.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.conn = None
        self.cursor = None
        self._connection_retries = 3
        self._retry_delay = 1
        
        try:
            self.connect()
            self.create_tables()
            self.migrate_database()
            self._create_indexes()
            logger.info("Database başlatıldı")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
        
    def connect(self):
        """Veritabanına bağlan - retry mekanizması ile"""
        for attempt in range(self._connection_retries):
            try:
                if self.conn:
                    try:
                        self.conn.close()
                    except:
                        pass
                
                self.conn = sqlite3.connect(
                    self.db_path, 
                    check_same_thread=False,
                    timeout=30.0,
                    isolation_level=None  # Autocommit mode
                )
                self.conn.row_factory = sqlite3.Row
                
                # SQLite pragmas for better performance and safety
                self.conn.execute("PRAGMA journal_mode=WAL")
                self.conn.execute("PRAGMA synchronous=NORMAL")
                self.conn.execute("PRAGMA foreign_keys=ON")
                self.conn.execute("PRAGMA temp_store=MEMORY")
                self.conn.execute("PRAGMA cache_size=10000")
                
                self.cursor = self.conn.cursor()
                logger.info(f"Veritabanı bağlantısı başarılı (deneme {attempt + 1})")
                return
                
            except sqlite3.Error as e:
                logger.error(f"SQLite bağlantı hatası (deneme {attempt + 1}): {e}")
                if attempt < self._connection_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                    continue
                else:
                    raise
            except Exception as e:
                logger.error(f"Database bağlantı hatası (deneme {attempt + 1}): {e}")
                if attempt < self._connection_retries - 1:
                    time.sleep(self._retry_delay * (attempt + 1))
                    continue
                else:
                    raise
    
    def ensure_connection(self):
        """Bağlantının aktif olduğundan emin ol"""
        try:
            if not self.conn:
                self.connect()
                return
            
            # Connection test
            self.conn.execute("SELECT 1")
            
        except (sqlite3.Error, AttributeError):
            logger.warning("Bağlantı kopmuş, yeniden bağlanılıyor...")
            self.connect()
    
    def migrate_database(self):
        """Veritabanı şemasını güncelle"""
        with self.lock:
            try:
                # Mevcut sütunları kontrol et ve eksikleri ekle
                self.cursor.execute("PRAGMA table_info(firms)")
                columns = [column[1] for column in self.cursor.fetchall()]
                
                if 'place_id' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN place_id TEXT")
                    logger.info("place_id sütunu eklendi")
                
                if 'email' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN email TEXT")
                    logger.info("email sütunu eklendi")
                
                if 'status' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN status TEXT DEFAULT 'active'")
                    logger.info("status sütunu eklendi")
                
                if 'sector' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN sector TEXT")
                    logger.info("sector sütunu eklendi")
                
                if 'address' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN address TEXT")
                    logger.info("address sütunu eklendi")
                
                if 'summary' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN summary TEXT")
                    logger.info("summary sütunu eklendi")
                
                if 'website' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN website TEXT")
                    logger.info("website sütunu eklendi")
                
                if 'contact_person' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN contact_person TEXT")
                    logger.info("contact_person sütunu eklendi")
                
                if 'last_contact_date' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN last_contact_date TIMESTAMP")
                    logger.info("last_contact_date sütunu eklendi")
                
                if 'rating' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN rating REAL")
                    logger.info("rating sütunu eklendi")

                if 'domain' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN domain TEXT;")
                    logger.info("domain sütunu eklendi")
                
                if 'review_count' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN review_count INTEGER")
                    logger.info("review_count sütunu eklendi")
                
                if 'business_hours' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN business_hours TEXT")
                    logger.info("business_hours sütunu eklendi")
                
                if 'ai_summary' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN ai_summary TEXT")
                    logger.info("ai_summary sütunu eklendi")
                
                if 'created_at' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    logger.info("created_at sütunu eklendi")
                
                if 'updated_at' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    logger.info("updated_at sütunu eklendi")
                
                if 'is_analyzed' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN is_analyzed INTEGER DEFAULT 0")
                    logger.info("is_analyzed sütunu eklendi")
                
                if 'last_action' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN last_action TEXT DEFAULT ''")
                    logger.info("last_action sütunu eklendi")
                
                if 'ai_vision_analysis' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN ai_vision_analysis TEXT")
                    logger.info("ai_vision_analysis sütunu eklendi")
                
                # 🆕 Gelişmiş Web Scraping Alanları
                if 'company_type' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN company_type TEXT")
                    logger.info("company_type sütunu eklendi")
                
                if 'company_type_confidence' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN company_type_confidence REAL")
                    logger.info("company_type_confidence sütunu eklendi")
                
                if 'company_type_analysis' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN company_type_analysis TEXT")
                    logger.info("company_type_analysis sütunu eklendi")
                
                if 'quality_score' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN quality_score REAL")
                    logger.info("quality_score sütunu eklendi")
                
                if 'quality_grade' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN quality_grade TEXT")
                    logger.info("quality_grade sütunu eklendi")
                
                if 'quality_analysis' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN quality_analysis TEXT")
                    logger.info("quality_analysis sütunu eklendi")
                
                if 'products_list' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN products_list TEXT")
                    logger.info("products_list sütunu eklendi")
                
                if 'services_list' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN services_list TEXT")
                    logger.info("services_list sütunu eklendi")
                
                if 'product_categories' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN product_categories TEXT")
                    logger.info("product_categories sütunu eklendi")
                
                if 'integrations_data' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN integrations_data TEXT")
                    logger.info("integrations_data sütunu eklendi")
                
                if 'has_ecommerce' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN has_ecommerce INTEGER DEFAULT 0")
                    logger.info("has_ecommerce sütunu eklendi")
                
                if 'technical_score' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN technical_score REAL")
                    logger.info("technical_score sütunu eklendi")
                
                if 'content_score' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN content_score REAL")
                    logger.info("content_score sütunu eklendi")
                
                if 'last_scraped_at' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN last_scraped_at TIMESTAMP")
                    logger.info("last_scraped_at sütunu eklendi")
                
                if 'google_maps_url' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN google_maps_url TEXT")
                    logger.info("google_maps_url sütunu eklendi")
                
                if 'is_open' not in columns:
                    self.cursor.execute("ALTER TABLE firms ADD COLUMN is_open INTEGER")
                    logger.info("is_open sütunu eklendi")
                
                # Messages tablosu kontrolü
                self.cursor.execute("PRAGMA table_info(messages)")
                columns = [column[1] for column in self.cursor.fetchall()]
                
                if 'scheduled_date' not in columns:
                    self.cursor.execute("ALTER TABLE messages ADD COLUMN scheduled_date TIMESTAMP")
                    logger.info("scheduled_date sütunu eklendi")
                
                # Email logs tablosu kontrolü
                self.cursor.execute("PRAGMA table_info(email_logs)")
                email_columns = [column[1] for column in self.cursor.fetchall()]
                
                if 'created_at' not in email_columns:
                    self.cursor.execute("ALTER TABLE email_logs ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    logger.info("created_at sütunu eklendi")
                
                if 'updated_at' not in email_columns:
                    self.cursor.execute("ALTER TABLE email_logs ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    logger.info("updated_at sütunu eklendi")
                
                if 'campaign_id' not in email_columns:
                    self.cursor.execute("ALTER TABLE email_logs ADD COLUMN campaign_id INTEGER")
                    logger.info("campaign_id sütunu eklendi")
                
                if 'opened_at' not in email_columns:
                    self.cursor.execute("ALTER TABLE email_logs ADD COLUMN opened_at TIMESTAMP")
                    logger.info("opened_at sütunu eklendi")
                
                if 'replied_at' not in email_columns:
                    self.cursor.execute("ALTER TABLE email_logs ADD COLUMN replied_at TIMESTAMP")
                    logger.info("replied_at sütunu eklendi")
                
                # social_media_details sütunu zaten create_tables'da tanımlanmış
                # Bu sütun için migrasyon gerekmiyor
                
                self.conn.commit()
                logger.info("Veritabanı migrasyonu tamamlandı")
                
            except Exception as e:
                logger.error(f"Veritabanı migrasyonu hatası: {str(e)}")
    
    def create_tables(self):
        """Tabloları oluştur - main3.py uyumlu (güncellenmiş ve eksiksiz)"""
        with self.lock:
            try:
                self.ensure_connection()

                # ✅ Firmalar tablosu (tüm eksik sütunlar eklendi)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS firms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT,
                        email TEXT,
                        address TEXT,
                        sector TEXT,
                        summary TEXT,
                        ai_summary TEXT,
                        website TEXT,
                        contact_person TEXT,
                        last_contact_date TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        place_id TEXT,
                        rating REAL,
                        review_count INTEGER,
                        business_hours TEXT,
                        last_action TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_analyzed INTEGER DEFAULT 0,

                        -- 🔹 Yeni sütunlar (update_firm sorgusuna uyumlu)
                        domain TEXT,
                        title TEXT,
                        description TEXT,
                        keywords TEXT,
                        emails TEXT,
                        phone_numbers TEXT,
                        social_media TEXT,
                        business_info TEXT,
                        text_content TEXT,
                        services TEXT,
                        products TEXT,
                        pricing TEXT,
                        about_text TEXT,
                        team_size_estimate TEXT,
                        industry_keywords TEXT,
                        contact_page_url TEXT,
                        advanced_features TEXT,
                        scraped_data TEXT,
                        company_score REAL,
                        ai_vision_analysis TEXT,
                        
                        -- 🆕 Gelişmiş Web Scraping Alanları
                        company_type TEXT,
                        company_type_confidence REAL,
                        company_type_analysis TEXT,
                        quality_score REAL,
                        quality_grade TEXT,
                        quality_analysis TEXT,
                        products_list TEXT,
                        services_list TEXT,
                        product_categories TEXT,
                        integrations_data TEXT,
                        has_ecommerce INTEGER DEFAULT 0,
                        technical_score REAL,
                        content_score REAL,
                        last_scraped_at TIMESTAMP,
                        google_maps_url TEXT,
                        social_media_details TEXT,
                        is_open INTEGER
                    )
                """)

                # Kategoriler tablosu
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        description TEXT,
                        color TEXT DEFAULT '#3498db',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Firma kategorileri tablosu (many-to-many)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS firm_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firm_id INTEGER,
                        category_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms(id) ON DELETE CASCADE,
                        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                        UNIQUE(firm_id, category_id)
                    )
                """)

                # Mesajlar tablosu
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firm_id INTEGER,
                        direction TEXT,
                        content TEXT,
                        platform TEXT,
                        status TEXT,
                        scheduled_date TIMESTAMP,
                        sent_date TIMESTAMP,
                        read_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id) ON DELETE CASCADE
                    )
                """)

                # Aramalar tablosu
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firm_id INTEGER,
                        call_id TEXT,
                        phone_number_id TEXT,
                        assistant_id TEXT,
                        duration INTEGER,
                        status TEXT,
                        recording_url TEXT,
                        transcript TEXT,
                        notes TEXT,
                        cost REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id) ON DELETE CASCADE
                    )
                """)

                # Email logları
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS email_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firm_id INTEGER,
                        email TEXT,
                        subject TEXT,
                        content TEXT,
                        status TEXT,
                        opened INTEGER DEFAULT 0,
                        clicked INTEGER DEFAULT 0,
                        replied INTEGER DEFAULT 0,
                        sent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id) ON DELETE CASCADE
                    )
                """)

                # Ayarlar tablosu
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Şablonlar tablosu
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        content TEXT,
                        category TEXT,
                        variables TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Aktiviteler tablosu
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firm_id INTEGER,
                        activity_type TEXT,
                        description TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id) ON DELETE CASCADE
                    )
                """)

                # Zamanlanmış görevler
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scheduled_tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_type TEXT,
                        firm_id INTEGER,
                        data TEXT,
                        scheduled_date TIMESTAMP,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id) ON DELETE CASCADE
                    )
                """)

                # 🧠 Firma Bilgi Öğretim Sistemi - Knowledge Base
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content_type TEXT NOT NULL,
                        content TEXT,
                        file_path TEXT,
                        url TEXT,
                        ai_analysis TEXT,
                        ai_summary TEXT,
                        tags TEXT,
                        metadata TEXT,
                        embedding TEXT,
                        is_learned INTEGER DEFAULT 0,
                        learning_status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        learned_at TIMESTAMP
                    )
                """)
                
                # 📧 Email Tracking - Eksik tablo
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS email_tracking (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tracking_id TEXT UNIQUE NOT NULL,
                        firm_id INTEGER,
                        to_email TEXT NOT NULL,
                        subject TEXT,
                        body TEXT,
                        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        opened INTEGER DEFAULT 0,
                        first_opened_at TIMESTAMP,
                        last_opened_at TIMESTAMP,
                        open_count INTEGER DEFAULT 0,
                        clicked INTEGER DEFAULT 0,
                        first_clicked_at TIMESTAMP,
                        last_clicked_at TIMESTAMP,
                        click_count INTEGER DEFAULT 0,
                        user_agent TEXT,
                        ip_address TEXT,
                        device_type TEXT,
                        browser TEXT,
                        os TEXT,
                        location TEXT,
                        status TEXT DEFAULT 'sent',
                        unsubscribed INTEGER DEFAULT 0,
                        unsubscribed_at TIMESTAMP,
                        bounced INTEGER DEFAULT 0,
                        bounced_at TIMESTAMP,
                        engagement_score REAL DEFAULT 0.0,
                        campaign_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id) ON DELETE CASCADE
                    )
                """)
                
                # 📞 Communication Log - Eksik tablo
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS communication_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firm_id INTEGER,
                        communication_type TEXT NOT NULL,
                        communication_method TEXT,
                        subject TEXT,
                        content TEXT,
                        status TEXT,
                        direction TEXT,
                        from_email TEXT,
                        to_email TEXT,
                        phone_number TEXT,
                        sent_at TIMESTAMP,
                        received_at TIMESTAMP,
                        opened_at TIMESTAMP,
                        clicked_at TIMESTAMP,
                        replied_at TIMESTAMP,
                        notes TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id) ON DELETE CASCADE
                    )
                """)

                # Öğrenme oturumları
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_type TEXT NOT NULL,
                        knowledge_ids TEXT,
                        prompt TEXT,
                        ai_response TEXT,
                        tokens_used INTEGER,
                        status TEXT DEFAULT 'completed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 🤖 AI Sohbet Asistanı - Konuşma Geçmişi
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_chat_conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        metadata TEXT,
                        tokens_used INTEGER,
                        model TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # AI Sohbet Oturumları
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ai_chat_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        title TEXT,
                        message_count INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active'
                    )
                """)

                # Yüklenmiş dosyalar
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS uploaded_files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name TEXT NOT NULL,
                        file_type TEXT,
                        file_size INTEGER,
                        file_path TEXT,
                        knowledge_id INTEGER,
                        upload_status TEXT DEFAULT 'completed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (knowledge_id) REFERENCES knowledge_base (id) ON DELETE CASCADE
                    )
                """)

                # 📱 WhatsApp Günlük Limit Kontrolü
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_daily_limits (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        messages_sent INTEGER DEFAULT 0,
                        messages_approved INTEGER DEFAULT 0,
                        messages_skipped INTEGER DEFAULT 0,
                        messages_failed INTEGER DEFAULT 0,
                        daily_limit INTEGER DEFAULT 50,
                        last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(date)
                    )
                """)

                # 📱 WhatsApp Mesaj Gönderim Logları
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS whatsapp_send_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        firm_id INTEGER,
                        firm_name TEXT,
                        phone_number TEXT,
                        message_content TEXT,
                        message_translation TEXT,
                        approval_status TEXT,
                        send_status TEXT,
                        error_message TEXT,
                        retry_count INTEGER DEFAULT 0,
                        sent_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (firm_id) REFERENCES firms (id) ON DELETE CASCADE
                    )
                """)

                self.conn.commit()
                logger.info("Tablolar başarıyla oluşturuldu")

            except Exception as e:
                logger.error(f"Tablo oluşturma hatası: {e}")


    def _create_indexes(self):
        """Veritabanı indekslerini oluştur (güncel)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Firms tablosu indeksleri
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_firms_name ON firms(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_firms_phone ON firms(phone)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_firms_email ON firms(email)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_firms_sector ON firms(sector)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_firms_status ON firms(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_firms_place_id ON firms(place_id)")

                # Messages tablosu indeksleri
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_firm_id ON messages(firm_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_platform ON messages(platform)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_scheduled_date ON messages(scheduled_date)")

                # Calls tablosu indeksleri
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_firm_id ON calls(firm_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_calls_created_at ON calls(created_at)")

                # Email logs indeksleri
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_logs_firm_id ON email_logs(firm_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_logs_status ON email_logs(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_logs_sent_date ON email_logs(sent_date)")

                # Activities indeksleri
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_firm_id ON activities(firm_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at)")

                # Scheduled tasks indeksleri
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_status ON scheduled_tasks(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_scheduled_date ON scheduled_tasks(scheduled_date)")

                conn.commit()
                logger.info("İndeksler başarıyla oluşturuldu")

        except Exception as e:
            logger.error(f"İndeks oluşturma hatası: {e}")

    
    @contextmanager
    def get_connection(self):
        """Thread-safe database connection context manager"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # ==================== MAIN3.PY UYUMLULUĞU İÇİN EKLENMİŞ METODLAR ====================
    
    def save_firm(self, firm_data):
        """Firma kaydet veya güncelle - main3.py uyumlu"""
        print(f"🔒 DB.save_firm başladı: {firm_data.get('name', 'İsimsiz')}")  # DEBUG
        with self.lock:
            print(f"🔓 Lock alındı")  # DEBUG
            try:
                print(f"🔍 ensure_connection çağrılıyor")  # DEBUG
                self.ensure_connection()
                print(f"✅ Connection sağlandı")  # DEBUG
                
                # Place ID varsa kontrol et
                if 'place_id' in firm_data and firm_data['place_id']:
                    print(f"🔍 Place ID kontrolü: {firm_data['place_id']}")  # DEBUG
                    self.cursor.execute(
                        "SELECT id FROM firms WHERE place_id = ?", 
                        (firm_data['place_id'],)
                    )
                    existing = self.cursor.fetchone()
                    print(f"📊 Place ID sorgu sonucu: {existing}")  # DEBUG
                    if existing:
                        print(f"🔄 Güncelleme yapılacak: {existing['id']}")  # DEBUG
                        # Güncelle
                        return self.update_firm(existing['id'], **firm_data)
                
                print(f"➕ Yeni firma eklenecek")  # DEBUG
                # Yeni firma ekle
                result = self.add_firm(**firm_data)
                print(f"✅ add_firm sonucu: {result}")  # DEBUG
                return result
            except Exception as e:
                print(f"❌ save_firm hatası: {e}")  # DEBUG
                logger.error(f"Firma kaydetme hatası: {e}")
                return None
    
    def get_existing_place_ids(self):
        """Mevcut place ID'leri getir - main3.py uyumlu"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("SELECT place_id FROM firms WHERE place_id IS NOT NULL")
                return [row[0] for row in self.cursor.fetchall()]
            except Exception as e:
                logger.error(f"Place ID getirme hatası: {e}")
                return []
    
    def get_duplicate_prevention_stats(self):
        """Duplikat önleme istatistiklerini getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                # Toplam firma sayısı
                self.cursor.execute("SELECT COUNT(*) FROM firms")
                total_firms = self.cursor.fetchone()[0]
                
                # Place ID'si olan firma sayısı
                self.cursor.execute("SELECT COUNT(*) FROM firms WHERE place_id IS NOT NULL")
                firms_with_place_id = self.cursor.fetchone()[0]
                
                # Duplikat önleme oranı
                duplicate_prevention_rate = (firms_with_place_id / total_firms * 100) if total_firms > 0 else 0
                
                return {
                    'total_firms': total_firms,
                    'firms_with_place_id': firms_with_place_id,
                    'duplicate_prevention_rate': round(duplicate_prevention_rate, 1)
                }
            except Exception as e:
                logger.error(f"Duplikat önleme istatistik hatası: {e}")
                return {
                    'total_firms': 0,
                    'firms_with_place_id': 0,
                    'duplicate_prevention_rate': 0
                }
    
    def add_firm(self, name, phone, email="", address="", sector="", summary="", 
                 ai_summary="", website="", contact_person="", place_id=None, rating=None, 
                 review_count=None, business_hours=None, emails=None, **kwargs):
        """Yeni firma ekle - main3.py uyumlu"""
        print(f"➕ add_firm başladı: {name}")  # DEBUG
        # NOT: Lock save_firm'de alınmış, burada tekrar almıyoruz
        try:
            print(f"🔍 ensure_connection çağrılıyor (add_firm)")  # DEBUG
            self.ensure_connection()
            print(f"📝 INSERT sorgusu çalıştırılıyor")  # DEBUG
            print(f"🔍 AI Summary to be saved: {ai_summary[:100] if ai_summary else 'None'}...")  # DEBUG
            
            # Emails listesini JSON string'e çevir
            emails_json = json.dumps(emails or []) if emails else "[]"
            print(f"🔍 Emails JSON: {emails_json}")  # DEBUG
            
            self.cursor.execute("""
                INSERT INTO firms (name, phone, email, address, sector, summary, ai_summary,
                                 website, contact_person, place_id, rating, 
                                 review_count, business_hours, emails)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, phone, email, address, sector, summary, ai_summary, website, 
                  contact_person, place_id, rating, review_count, business_hours, emails_json))
            print(f"💾 Commit yapılıyor")  # DEBUG
            self.conn.commit()
            firm_id = self.cursor.lastrowid
            print(f"✅ Firma eklendi, ID: {firm_id}")  # DEBUG
            
            # Aktivite kaydet (ama lock kullanmadan)
            print(f"📝 Aktivite kaydediliyor")  # DEBUG
            try:
                # save_activity de lock kullanıyor, o yüzden geçici olarak atlayalım
                pass  # self.save_activity(firm_id, "firm_added", f"'{name}' firması eklendi")
            except:
                pass
            
            return firm_id
        except Exception as e:
            print(f"❌ add_firm hatası: {e}")  # DEBUG
            logger.error(f"Firma ekleme hatası: {e}")
            return None
    
    def update_firm(self, firm_id, **kwargs):
        """Firma güncelle - main3.py uyumlu"""
        print(f"🔄 update_firm başladı: ID {firm_id}")  # DEBUG
        # NOT: Lock save_firm'de alınmış, burada tekrar almıyoruz
        try:
            import json
            fields = []
            values = []
            for key, value in kwargs.items():
                if key not in ['id', 'created_at']:  # Bu alanları güncelleme
                    fields.append(f"{key} = ?")
                    # Convert lists and dicts to JSON strings for SQLite storage
                    if isinstance(value, (list, dict)):
                        value = json.dumps(value, ensure_ascii=False)
                    values.append(value)
            
            values.append(firm_id)
            query = f"UPDATE firms SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            
            print(f"📝 UPDATE sorgusu: {query}")  # DEBUG
            self.cursor.execute(query, values)
            print(f"💾 UPDATE commit yapılıyor")  # DEBUG
            self.conn.commit()
            print(f"✅ UPDATE tamamlandı")  # DEBUG
            
            # Aktivite kaydet - geçici olarak atlayalım (deadlock önlemek için)
            try:
                pass  # self.save_activity(firm_id, "firm_updated", "Firma bilgileri güncellendi")
            except:
                pass
            
            return True
        except Exception as e:
            print(f"❌ update_firm hatası: {e}")  # DEBUG
            logger.error(f"Firma güncelleme hatası: {e}")
            return False
    
    def delete_firm(self, firm_id):
        """Firma sil - main3.py uyumlu"""
        with self.lock:
            try:
                # Önce firma adını al
                self.cursor.execute("SELECT name FROM firms WHERE id = ?", (firm_id,))
                firm = self.cursor.fetchone()
                
                self.cursor.execute("DELETE FROM firms WHERE id = ?", (firm_id,))
                self.conn.commit()
                
                logger.info(f"Firma silindi: {firm['name'] if firm else firm_id}")
                return True
            except Exception as e:
                logger.error(f"Firma silme hatası: {e}")
                return False
    
    def get_firms(self, search_text="", sector="", status="", limit=None):
        """Firmaları getir (filtreleme ile) - main3.py uyumlu"""
        with self.lock:
            try:
                query = """SELECT 
                    id, name, phone, COALESCE(email, '') as email, 
                    COALESCE(address, '') as address, COALESCE(sector, '') as sector,
                    COALESCE(summary, '') as summary, COALESCE(ai_summary, '') as ai_summary,
                    COALESCE(website, '') as website,
                    COALESCE(contact_person, '') as contact_person,
                    COALESCE(last_contact_date, '') as last_contact_date,
                    COALESCE(status, 'active') as status,
                    place_id, rating, review_count, business_hours,
                    created_at, updated_at
                FROM firms WHERE 1=1"""
                params = []
                
                if search_text:
                    query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)"
                    search_param = f"%{search_text}%"
                    params.extend([search_param, search_param, search_param])
                
                if sector and sector != "Tüm Sektörler":
                    query += " AND sector = ?"
                    params.append(sector)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                query += " ORDER BY created_at DESC"
                
                if limit:
                    query += f" LIMIT {limit}"
                
                self.cursor.execute(query, params)
                rows = self.cursor.fetchall()
                
                # Row objelerini dict'e çevir
                firms = []
                for row in rows:
                    firm_dict = dict(row)
                    firms.append(firm_dict)
                return firms
            except Exception as e:
                logger.error(f"Firma getirme hatası: {e}")
                return []
    
    def get_firm_by_id(self, firm_id):
        """ID'ye göre firma getir - main3.py uyumlu"""
        with self.lock:
            try:
                import json
                self.cursor.execute("SELECT * FROM firms WHERE id = ?", (firm_id,))
                row = self.cursor.fetchone()
                if row:
                    firm_data = dict(row)
                    # Convert JSON strings back to lists/dicts for complex fields
                    complex_fields = ['emails', 'phone_numbers', 'social_media', 'services', 'products', 
                                    'pricing', 'industry_keywords', 'advanced_features', 'scraped_data',
                                    'business_info', 'social_media']
                    for field in complex_fields:
                        if field in firm_data and firm_data[field] is not None:
                            try:
                                if isinstance(firm_data[field], str):
                                    firm_data[field] = json.loads(firm_data[field])
                            except (json.JSONDecodeError, TypeError):
                                # If JSON parsing fails, set to appropriate default
                                if field in ['emails', 'phone_numbers', 'services', 'products', 'pricing', 'industry_keywords', 'advanced_features', 'scraped_data']:
                                    firm_data[field] = []  # Default to empty list for list fields
                                else:
                                    firm_data[field] = {}  # Default to empty dict for dict fields
                        elif field in firm_data and firm_data[field] is None:
                            # Handle None values explicitly
                            if field in ['emails', 'phone_numbers', 'services', 'products', 'pricing', 'industry_keywords', 'advanced_features', 'scraped_data']:
                                firm_data[field] = []  # Default to empty list for list fields
                            else:
                                firm_data[field] = {}  # Default to empty dict for dict fields
                    return firm_data
                return None
            except Exception as e:
                logger.error(f"Firma getirme hatası: {e}")
                return None
    
    def get_firms_by_filter(self, filters):
        """Filtrelere göre firmaları getir - main.py uyumlu"""
        with self.lock:
            try:
                query = """SELECT 
                    f.id, f.name, f.phone, f.email, f.address, f.sector,
                    f.summary, f.website, f.contact_person, f.last_contact_date,
                    f.status, f.place_id, f.rating, f.review_count, f.business_hours,
                    f.created_at, f.updated_at, f.is_analyzed, f.emails
                FROM firms f
                WHERE 1=1"""
                params = []
                
                # Analiz edilmiş firmalar filtresi
                if filters.get('analyzed_only'):
                    query += " AND f.is_analyzed = 1"
                
                # Email'i olan firmalar filtresi
                if filters.get('has_emails'):
                    query += " AND f.email IS NOT NULL AND f.email != ''"
                
                # Minimum rating filtresi
                if filters.get('min_rating'):
                    query += " AND f.rating >= ?"
                    params.append(filters['min_rating'])
                
                query += " ORDER BY f.created_at DESC"
                
                self.cursor.execute(query, params)
                rows = self.cursor.fetchall()
                
                # Row objelerini dict'e çevir ve JSON parse et
                firms = []
                for row in rows:
                    firm_dict = dict(row)
                    
                    # Emails JSON string ise parse et
                    if 'emails' in firm_dict and firm_dict['emails']:
                        try:
                            if isinstance(firm_dict['emails'], str):
                                firm_dict['emails'] = json.loads(firm_dict['emails'])
                        except:
                            firm_dict['emails'] = []
                    else:
                        firm_dict['emails'] = []
                    
                    firms.append(firm_dict)
                return firms
            except Exception as e:
                logger.error(f"Filtreli firma getirme hatası: {e}")
                return []
    
    def save_message(self, firm_id, direction, content, platform="whatsapp", 
                    status="sent", scheduled_date=None):
        """Mesaj kaydet - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    INSERT INTO messages (firm_id, direction, content, platform, 
                                        status, scheduled_date, sent_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (firm_id, direction, content, platform, status, 
                      scheduled_date, datetime.now() if not scheduled_date else None))
                self.conn.commit()
                
                # Son iletişim tarihini güncelle
                if not scheduled_date:
                    self.cursor.execute("""
                        UPDATE firms SET last_contact_date = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (firm_id,))
                    self.conn.commit()
                
                # Aktivite kaydet
                self.save_activity(firm_id, "message_sent", 
                                 f"{platform} üzerinden mesaj gönderildi")
                
                return True
            except Exception as e:
                logger.error(f"Mesaj kaydetme hatası: {e}")
                return False
    
    def get_messages(self, firm_id=None, limit=100):
        """Mesajları getir - main3.py uyumlu"""
        with self.lock:
            try:
                if firm_id:
                    self.cursor.execute("""
                        SELECT m.*, f.name as firm_name 
                        FROM messages m
                        LEFT JOIN firms f ON m.firm_id = f.id
                        WHERE m.firm_id = ?
                        ORDER BY m.created_at DESC
                        LIMIT ?
                    """, (firm_id, limit))
                else:
                    self.cursor.execute("""
                        SELECT m.*, f.name as firm_name 
                        FROM messages m
                        LEFT JOIN firms f ON m.firm_id = f.id
                        ORDER BY m.created_at DESC
                        LIMIT ?
                    """, (limit,))
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Mesaj getirme hatası: {e}")
                return []
    
    def get_scheduled_messages(self):
        """Zamanlanmış mesajları getir - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT m.*, f.name as firm_name 
                    FROM messages m
                    LEFT JOIN firms f ON m.firm_id = f.id
                    WHERE m.scheduled_date IS NOT NULL 
                    AND m.scheduled_date <= datetime('now')
                    AND m.status = 'scheduled'
                    ORDER BY m.scheduled_date ASC
                """)
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Zamanlanmış mesaj getirme hatası: {e}")
                return []
    
    def save_call(self, firm_id, call_id="", phone_number_id="", assistant_id="",
                  duration=0, status="completed", recording_url="", 
                  transcript="", notes="", cost=0.0):
        """Arama kaydet - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    INSERT INTO calls (firm_id, call_id, phone_number_id, assistant_id,
                                     duration, status, recording_url, transcript, notes, cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (firm_id, call_id, phone_number_id, assistant_id, duration, 
                      status, recording_url, transcript, notes, cost))
                self.conn.commit()
                
                # Aktivite kaydet
                self.save_activity(firm_id, "call_made", "Arama yapıldı")
                
                return True
            except Exception as e:
                logger.error(f"Arama kaydetme hatası: {e}")
                return False
    
    def get_calls(self, firm_id=None):
        """Aramaları getir - main3.py uyumlu"""
        with self.lock:
            try:
                if firm_id:
                    self.cursor.execute("""
                        SELECT c.*, f.name as firm_name 
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        WHERE c.firm_id = ?
                        ORDER BY c.created_at DESC
                    """, (firm_id,))
                else:
                    self.cursor.execute("""
                        SELECT c.*, f.name as firm_name 
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        ORDER BY c.created_at DESC
                    """)
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Arama getirme hatası: {e}")
                return []
    
    def save_email_log(self, firm_id, email, subject, content, status="sent"):
        """Email log kaydet - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    INSERT INTO email_logs (firm_id, email, subject, content, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (firm_id, email, subject, content, status))
                self.conn.commit()
                
                # Aktivite kaydet
                self.save_activity(firm_id, "email_sent", "Email gönderildi")
                
                return True
            except Exception as e:
                logger.error(f"Email log kaydetme hatası: {e}")
                return False
    
    def save_template(self, name, content, category="genel", variables=None):
        """Şablon kaydet - main3.py uyumlu"""
        with self.lock:
            try:
                variables_json = json.dumps(variables) if variables else None
                self.cursor.execute("""
                    INSERT INTO templates (name, content, category, variables)
                    VALUES (?, ?, ?, ?)
                """, (name, content, category, variables_json))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Şablon kaydetme hatası: {e}")
                return False
    
    def get_templates(self, category=None):
        """Şablonları getir - main3.py uyumlu"""
        with self.lock:
            try:
                if category:
                    self.cursor.execute("""
                        SELECT * FROM templates WHERE category = ? ORDER BY name
                    """, (category,))
                else:
                    self.cursor.execute("""
                        SELECT * FROM templates ORDER BY name
                    """)
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Şablon getirme hatası: {e}")
                return []
    
    def save_activity(self, firm_id, activity_type, description, metadata=None):
        """Aktivite kaydet - main3.py uyumlu"""
        with self.lock:
            try:
                metadata_json = json.dumps(metadata) if metadata else None
                self.cursor.execute("""
                    INSERT INTO activities (firm_id, activity_type, description, metadata)
                    VALUES (?, ?, ?, ?)
                """, (firm_id, activity_type, description, metadata_json))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Aktivite kaydetme hatası: {e}")
                return False
    
    def get_recent_activities(self, limit=10):
        """Son aktiviteleri getir - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT a.*, f.name as firm_name 
                    FROM activities a
                    LEFT JOIN firms f ON a.firm_id = f.id
                    ORDER BY a.created_at DESC
                    LIMIT ?
                """, (limit,))
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Aktivite getirme hatası: {e}")
                return []
    
    def save_scheduled_task(self, task_type, firm_id, data, scheduled_date):
        """Zamanlanmış görev kaydet - main3.py uyumlu"""
        with self.lock:
            try:
                data_json = json.dumps(data) if data else None
                self.cursor.execute("""
                    INSERT INTO scheduled_tasks (task_type, firm_id, data, scheduled_date)
                    VALUES (?, ?, ?, ?)
                """, (task_type, firm_id, data_json, scheduled_date))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Zamanlanmış görev kaydetme hatası: {e}")
                return False
    
    def get_pending_tasks(self):
        """Bekleyen görevleri getir - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT st.*, f.name as firm_name
                    FROM scheduled_tasks st
                    LEFT JOIN firms f ON st.firm_id = f.id
                    WHERE st.status = 'pending'
                    AND st.scheduled_date <= datetime('now')
                    ORDER BY st.scheduled_date ASC
                """)
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Bekleyen görev getirme hatası: {e}")
                return []
    
    def update_task_status(self, task_id, status):
        """Görev durumunu güncelle - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    UPDATE scheduled_tasks 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, task_id))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Görev durumu güncelleme hatası: {e}")
                return False
    
    def get_statistics(self):
        """İstatistikleri getir - main3.py uyumlu"""
        with self.lock:
            try:
                stats = {}
                
                # Toplam firma sayısı
                self.cursor.execute("SELECT COUNT(*) FROM firms")
                stats['total_firms'] = self.cursor.fetchone()[0]
                
                # Aktif firma sayısı
                self.cursor.execute("SELECT COUNT(*) FROM firms WHERE status = 'active'")
                stats['active_firms'] = self.cursor.fetchone()[0]
                
                # Analiz edilmiş firma sayısı
                self.cursor.execute("SELECT COUNT(*) FROM firms WHERE is_analyzed = 1")
                stats['analyzed_firms'] = self.cursor.fetchone()[0]
                
                # Toplam mesaj sayısı
                self.cursor.execute("SELECT COUNT(*) FROM messages")
                stats['total_messages'] = self.cursor.fetchone()[0]
                
                # Bugünkü mesajlar
                self.cursor.execute("""
                    SELECT COUNT(*) FROM messages 
                    WHERE DATE(created_at) = DATE('now')
                """)
                stats['today_messages'] = self.cursor.fetchone()[0]
                
                # Toplam arama sayısı
                self.cursor.execute("SELECT COUNT(*) FROM calls")
                stats['total_calls'] = self.cursor.fetchone()[0]
                
                # Bugünkü aramalar
                self.cursor.execute("""
                    SELECT COUNT(*) FROM calls 
                    WHERE DATE(created_at) = DATE('now')
                """)
                stats['today_calls'] = self.cursor.fetchone()[0]
                
                # Email istatistikleri
                self.cursor.execute("SELECT COUNT(*) FROM email_logs")
                stats['total_emails'] = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM email_logs WHERE status = 'sent'")
                stats['total_sent'] = self.cursor.fetchone()[0]
                
                # Açılma oranı
                self.cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN COUNT(*) > 0 THEN 
                                ROUND((COUNT(CASE WHEN opened_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)), 1)
                            ELSE 0 
                        END as open_rate
                    FROM email_logs WHERE status = 'sent'
                """)
                result = self.cursor.fetchone()
                stats['open_rate'] = result[0] if result else 0
                
                # Yanıt oranı
                self.cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN COUNT(*) > 0 THEN 
                                ROUND((COUNT(CASE WHEN replied_at IS NOT NULL THEN 1 END) * 100.0 / COUNT(*)), 1)
                            ELSE 0 
                        END as reply_rate
                    FROM email_logs WHERE status = 'sent'
                """)
                result = self.cursor.fetchone()
                stats['reply_rate'] = result[0] if result else 0
                
                return stats
            except Exception as e:
                logger.error(f"İstatistik getirme hatası: {e}")
                return {}
    
    def get_email_statistics(self):
        """Email istatistikleri - main3.py uyumlu"""
        with self.lock:
            try:
                stats = {}
                
                # Toplam email
                self.cursor.execute("SELECT COUNT(*) FROM email_logs")
                stats['total_emails'] = self.cursor.fetchone()[0]
                
                # Açılan emailler
                self.cursor.execute("SELECT COUNT(*) FROM email_logs WHERE opened = 1")
                stats['opened_emails'] = self.cursor.fetchone()[0]
                
                # Tıklanan emailler
                self.cursor.execute("SELECT COUNT(*) FROM email_logs WHERE clicked = 1")
                stats['clicked_emails'] = self.cursor.fetchone()[0]
                
                # Yanıtlanan emailler
                self.cursor.execute("SELECT COUNT(*) FROM email_logs WHERE replied = 1")
                stats['replied_emails'] = self.cursor.fetchone()[0]
                
                return stats
            except Exception as e:
                logger.error(f"Email istatistik hatası: {e}")
                return {}
    
    def get_today_statistics(self):
        """Bugünkü istatistikler - main3.py uyumlu"""
        with self.lock:
            try:
                stats = {}
                
                # Bugünkü firmalar
                self.cursor.execute("""
                    SELECT COUNT(*) FROM firms 
                    WHERE DATE(created_at) = DATE('now')
                """)
                stats['today_firms'] = self.cursor.fetchone()[0]
                
                # Bugünkü mesajlar
                self.cursor.execute("""
                    SELECT COUNT(*) FROM messages 
                    WHERE DATE(created_at) = DATE('now')
                """)
                stats['today_messages'] = self.cursor.fetchone()[0]
                
                # Bugünkü aramalar
                self.cursor.execute("""
                    SELECT COUNT(*) FROM calls 
                    WHERE DATE(created_at) = DATE('now')
                """)
                stats['today_calls'] = self.cursor.fetchone()[0]
                
                return stats
            except Exception as e:
                logger.error(f"Bugünkü istatistik hatası: {e}")
                return {}
    
    def get_weekly_comparison(self):
        """Haftalık karşılaştırma - main3.py uyumlu"""
        with self.lock:
            try:
                stats = {}
                
                # Bu hafta
                self.cursor.execute("""
                    SELECT COUNT(*) FROM firms 
                    WHERE DATE(created_at) >= DATE('now', '-7 days')
                """)
                stats['this_week_firms'] = self.cursor.fetchone()[0]
                
                # Geçen hafta
                self.cursor.execute("""
                    SELECT COUNT(*) FROM firms 
                    WHERE DATE(created_at) >= DATE('now', '-14 days')
                    AND DATE(created_at) < DATE('now', '-7 days')
                """)
                stats['last_week_firms'] = self.cursor.fetchone()[0]
                
                return stats
            except Exception as e:
                logger.error(f"Haftalık karşılaştırma hatası: {e}")
                return {}
    
    def get_monthly_statistics(self):
        """Aylık istatistikler - main3.py uyumlu"""
        with self.lock:
            try:
                stats = {}
                
                # Bu ay
                self.cursor.execute("""
                    SELECT COUNT(*) FROM firms 
                    WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
                """)
                stats['this_month_firms'] = self.cursor.fetchone()[0]
                
                # Geçen ay
                self.cursor.execute("""
                    SELECT COUNT(*) FROM firms 
                    WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', '-1 month')
                """)
                stats['last_month_firms'] = self.cursor.fetchone()[0]
                
                return stats
            except Exception as e:
                logger.error(f"Aylık istatistik hatası: {e}")
                return {}
    
    def get_daily_stats(self, days=7):
        """Günlük istatistikler - main3.py uyumlu"""
        with self.lock:
            try:
                stats = []
                
                for i in range(days):
                    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    
                    # O günkü firmalar
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM firms 
                        WHERE DATE(created_at) = ?
                    """, (date,))
                    firm_count = self.cursor.fetchone()[0]
                    
                    # O günkü mesajlar
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM messages 
                        WHERE DATE(created_at) = ?
                    """, (date,))
                    message_count = self.cursor.fetchone()[0]
                    
                    stats.append({
                        'date': date,
                        'firms': firm_count,
                        'messages': message_count
                    })
                
                return stats
            except Exception as e:
                logger.error(f"Günlük istatistik hatası: {e}")
                return []
    
    def get_daily_statistics(self, days=7):
        """Günlük istatistikler - main.py uyumlu"""
        with self.lock:
            try:
                stats = {
                    'sent': [],
                    'opened': [],
                    'replied': []
                }
                
                for i in range(days):
                    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    
                    # O günkü gönderilen emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE DATE(sent_date) = ? AND status = 'sent'
                    """, (date,))
                    sent_count = self.cursor.fetchone()[0]
                    
                    # O günkü açılan emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE DATE(opened_at) = ? AND opened = 1
                    """, (date,))
                    opened_count = self.cursor.fetchone()[0]
                    
                    # O günkü yanıtlanan emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE DATE(replied_at) = ? AND replied = 1
                    """, (date,))
                    replied_count = self.cursor.fetchone()[0]
                    
                    stats['sent'].append(sent_count)
                    stats['opened'].append(opened_count)
                    stats['replied'].append(replied_count)
                
                return stats
            except Exception as e:
                logger.error(f"Günlük istatistik hatası: {e}")
                return {'sent': [0] * days, 'opened': [0] * days, 'replied': [0] * days}
    
    def get_hourly_statistics(self, hours=24):
        """Saatlik istatistikler"""
        with self.lock:
            try:
                stats = {
                    'sent': [],
                    'opened': [],
                    'replied': []
                }
                
                for i in range(hours):
                    hour = (datetime.now() - timedelta(hours=i)).strftime('%Y-%m-%d %H:00:00')
                    
                    # O saatteki gönderilen emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE strftime('%Y-%m-%d %H', sent_date) = strftime('%Y-%m-%d %H', ?) 
                        AND status = 'sent'
                    """, (hour,))
                    sent_count = self.cursor.fetchone()[0]
                    
                    # O saatteki açılan emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE strftime('%Y-%m-%d %H', opened_at) = strftime('%Y-%m-%d %H', ?) 
                        AND opened = 1
                    """, (hour,))
                    opened_count = self.cursor.fetchone()[0]
                    
                    # O saatteki yanıtlanan emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE strftime('%Y-%m-%d %H', replied_at) = strftime('%Y-%m-%d %H', ?) 
                        AND replied = 1
                    """, (hour,))
                    replied_count = self.cursor.fetchone()[0]
                    
                    stats['sent'].append(sent_count)
                    stats['opened'].append(opened_count)
                    stats['replied'].append(replied_count)
                
                return stats
            except Exception as e:
                logger.error(f"Saatlik istatistik hatası: {e}")
                return {'sent': [0] * hours, 'opened': [0] * hours, 'replied': [0] * hours}
    
    def get_monthly_statistics(self, months=12):
        """Aylık istatistikler"""
        with self.lock:
            try:
                stats = {
                    'sent': [],
                    'opened': [],
                    'replied': []
                }
                
                for i in range(months):
                    month = (datetime.now() - timedelta(days=i*30)).strftime('%Y-%m')
                    
                    # O aydaki gönderilen emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE strftime('%Y-%m', sent_date) = ? AND status = 'sent'
                    """, (month,))
                    sent_count = self.cursor.fetchone()[0]
                    
                    # O aydaki açılan emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE strftime('%Y-%m', opened_at) = ? AND opened = 1
                    """, (month,))
                    opened_count = self.cursor.fetchone()[0]
                    
                    # O aydaki yanıtlanan emailler
                    self.cursor.execute("""
                        SELECT COUNT(*) FROM email_logs 
                        WHERE strftime('%Y-%m', replied_at) = ? AND replied = 1
                    """, (month,))
                    replied_count = self.cursor.fetchone()[0]
                    
                    stats['sent'].append(sent_count)
                    stats['opened'].append(opened_count)
                    stats['replied'].append(replied_count)
                
                return stats
            except Exception as e:
                logger.error(f"Aylık istatistik hatası: {e}")
                return {'sent': [0] * months, 'opened': [0] * months, 'replied': [0] * months}
    
    def get_tracking_statistics(self, period="7d", campaign=None):
        """Tracking istatistikleri"""
        with self.lock:
            try:
                stats = {
                    'total_sent': 0,
                    'total_opened': 0,
                    'total_replied': 0,
                    'open_rate': 0,
                    'reply_rate': 0
                }
                
                # Tarih filtresi
                if period == "24h":
                    date_filter = "DATE(sent_date) = DATE('now')"
                elif period == "7d":
                    date_filter = "DATE(sent_date) >= DATE('now', '-7 days')"
                elif period == "30d":
                    date_filter = "DATE(sent_date) >= DATE('now', '-30 days')"
                else:
                    date_filter = "1=1"
                
                # Kampanya filtresi
                campaign_filter = ""
                if campaign:
                    campaign_filter = " AND campaign_id = ?"
                
                # Toplam gönderilen
                query = f"SELECT COUNT(*) FROM email_logs WHERE {date_filter}{campaign_filter}"
                params = [campaign] if campaign else []
                self.cursor.execute(query, params)
                stats['total_sent'] = self.cursor.fetchone()[0]
                
                # Toplam açılan
                query = f"SELECT COUNT(*) FROM email_logs WHERE {date_filter} AND opened = 1{campaign_filter}"
                self.cursor.execute(query, params)
                stats['total_opened'] = self.cursor.fetchone()[0]
                
                # Toplam yanıtlanan
                query = f"SELECT COUNT(*) FROM email_logs WHERE {date_filter} AND replied = 1{campaign_filter}"
                self.cursor.execute(query, params)
                stats['total_replied'] = self.cursor.fetchone()[0]
                
                # Oranlar
                if stats['total_sent'] > 0:
                    stats['open_rate'] = round((stats['total_opened'] / stats['total_sent']) * 100, 1)
                    stats['reply_rate'] = round((stats['total_replied'] / stats['total_sent']) * 100, 1)
                
                return stats
            except Exception as e:
                logger.error(f"Tracking istatistik hatası: {e}")
                return stats
    
    def get_recent_email_activities(self, limit=10):
        """Son email aktivitelerini getir"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT e.*, f.name as firm_name
                    FROM email_logs e
                    LEFT JOIN firms f ON e.firm_id = f.id
                    ORDER BY e.sent_date DESC
                    LIMIT ?
                """, (limit,))
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Son email aktiviteleri getirme hatası: {e}")
                return []
    
    def _empty_stats(self):
        """Boş istatistik - main3.py uyumlu"""
        return {
            'total_firms': 0,
            'active_firms': 0,
            'total_messages': 0,
            'today_messages': 0,
            'total_calls': 0,
            'today_calls': 0
        }
    
    def get_all_calls(self):
        """Tüm aramaları getir - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT c.*, f.name as firm_name, f.phone as firm_phone
                    FROM calls c
                    LEFT JOIN firms f ON c.firm_id = f.id
                    ORDER BY c.created_at DESC
                """)
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Tüm aramalar getirme hatası: {e}")
                return []
    
    def update_call_analysis(self, call_id, analysis_json):
        """Arama analizi güncelle - main3.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    UPDATE calls 
                    SET notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (analysis_json, call_id))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Arama analizi güncelleme hatası: {e}")
                return False
    
    def get_calls_by_analysis(self, sentiment=None):
        """Analiz bazlı aramalar - main3.py uyumlu"""
        with self.lock:
            try:
                if sentiment:
                    self.cursor.execute("""
                        SELECT c.*, f.name as firm_name
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        WHERE c.notes LIKE ?
                        ORDER BY c.created_at DESC
                    """, (f'%{sentiment}%',))
                else:
                    self.cursor.execute("""
                        SELECT c.*, f.name as firm_name
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        WHERE c.notes IS NOT NULL AND c.notes != ''
                        ORDER BY c.created_at DESC
                    """)
                return self.cursor.fetchall()
            except Exception as e:
                logger.error(f"Analiz bazlı arama getirme hatası: {e}")
                return []
    
    def get_all_emails(self, firm_filter="Tümü", period="7 gün"):
        """Tüm email loglarını getir - main.py uyumlu"""
        with self.lock:
            try:
                query = """SELECT 
                    el.*, f.name as firm_name
                FROM email_logs el
                LEFT JOIN firms f ON el.firm_id = f.id
                WHERE 1=1"""
                params = []
                
                if firm_filter != "Tümü":
                    query += " AND f.name LIKE ?"
                    params.append(f"%{firm_filter}%")
                
                if period != "Tümü":
                    if period == "24 saat":
                        query += " AND COALESCE(el.created_at, el.sent_date) >= datetime('now', '-1 day')"
                    elif period == "7 gün":
                        query += " AND COALESCE(el.created_at, el.sent_date) >= datetime('now', '-7 days')"
                    elif period == "30 gün":
                        query += " AND COALESCE(el.created_at, el.sent_date) >= datetime('now', '-30 days')"
                
                query += " ORDER BY COALESCE(el.created_at, el.sent_date) DESC"
                
                self.cursor.execute(query, params)
                rows = self.cursor.fetchall()
                
                # Row objelerini dict'e çevir
                emails = []
                for row in rows:
                    email_dict = dict(row)
                    emails.append(email_dict)
                return emails
            except Exception as e:
                logger.error(f"Email logları getirme hatası: {e}")
                return []
    
    def get_recent_email_activities(self, minutes=5):
        """Son dakikalardaki email aktivitelerini getir - main.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT el.*, f.name as firm_name,
                           'email_activity' as type,
                           'Email gönderildi' as description,
                           COALESCE(el.created_at, el.sent_date) as time
                    FROM email_logs el
                    LEFT JOIN firms f ON el.firm_id = f.id
                    WHERE COALESCE(el.created_at, el.sent_date) >= datetime('now', '-{} minutes')
                    ORDER BY COALESCE(el.created_at, el.sent_date) DESC
                """.format(minutes))
                
                rows = self.cursor.fetchall()
                
                # Row objelerini dict'e çevir
                activities = []
                for row in rows:
                    activity_dict = dict(row)
                    activities.append(activity_dict)
                return activities
            except Exception as e:
                logger.error(f"Son email aktiviteleri getirme hatası: {e}")
                return []
    
    def get_recent_activities(self, limit=10):
        """Son aktiviteleri getir - main.py uyumlu"""
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT a.*, f.name as firm_name 
                    FROM activities a
                    LEFT JOIN firms f ON a.firm_id = f.id
                    ORDER BY a.created_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = self.cursor.fetchall()
                
                # Row objelerini dict'e çevir
                activities = []
                for row in rows:
                    activity_dict = dict(row)
                    activities.append(activity_dict)
                return activities
            except Exception as e:
                logger.error(f"Son aktiviteleri getirme hatası: {e}")
                return []

    # ==================== KATEGORİ YÖNETİMİ ====================
    
    def create_category(self, name, description="", color="#3498db"):
        """Yeni kategori oluştur"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    INSERT INTO categories (name, description, color)
                    VALUES (?, ?, ?)
                """, (name, description, color))
                self.conn.commit()
                category_id = self.cursor.lastrowid
                logger.info(f"Kategori oluşturuldu: {name} (ID: {category_id})")
                return category_id
            except Exception as e:
                logger.error(f"Kategori oluşturma hatası: {e}")
                return None
    
    def get_categories(self):
        """Tüm kategorileri getir"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("SELECT * FROM categories ORDER BY name")
                return [dict(row) for row in self.cursor.fetchall()]
            except Exception as e:
                logger.error(f"Kategorileri getirme hatası: {e}")
                return []
    
    def update_category(self, category_id, name=None, description=None, color=None):
        """Kategori güncelle"""
        with self.lock:
            try:
                self.ensure_connection()
                updates = []
                values = []
                
                if name is not None:
                    updates.append("name = ?")
                    values.append(name)
                if description is not None:
                    updates.append("description = ?")
                    values.append(description)
                if color is not None:
                    updates.append("color = ?")
                    values.append(color)
                
                if not updates:
                    return True
                
                values.append(category_id)
                query = f"UPDATE categories SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                self.cursor.execute(query, values)
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Kategori güncelleme hatası: {e}")
                return False
    
    def delete_category(self, category_id):
        """Kategori sil"""
        with self.lock:
            try:
                self.ensure_connection()
                # Önce firma-kategori ilişkilerini sil
                self.cursor.execute("DELETE FROM firm_categories WHERE category_id = ?", (category_id,))
                # Kategoriyi sil
                self.cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                self.conn.commit()
                logger.info(f"Kategori silindi: ID {category_id}")
                return True
            except Exception as e:
                logger.error(f"Kategori silme hatası: {e}")
                return False
    
    def assign_firm_to_category(self, firm_id, category_id):
        """Firmayı kategoriye ata"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    INSERT OR IGNORE INTO firm_categories (firm_id, category_id)
                    VALUES (?, ?)
                """, (firm_id, category_id))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Firma-kategori atama hatası: {e}")
                return False
    
    def remove_firm_from_category(self, firm_id, category_id):
        """Firmayı kategoriden çıkar"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    DELETE FROM firm_categories 
                    WHERE firm_id = ? AND category_id = ?
                """, (firm_id, category_id))
                self.conn.commit()
                return True
            except Exception as e:
                logger.error(f"Firma-kategori çıkarma hatası: {e}")
                return False
    
    def get_firm_categories(self, firm_id):
        """Firmanın kategorilerini getir"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    SELECT c.* FROM categories c
                    JOIN firm_categories fc ON c.id = fc.category_id
                    WHERE fc.firm_id = ?
                    ORDER BY c.name
                """, (firm_id,))
                return [dict(row) for row in self.cursor.fetchall()]
            except Exception as e:
                logger.error(f"Firma kategorilerini getirme hatası: {e}")
                return []
    
    def get_category_firms(self, category_id):
        """Kategorideki firmaları getir"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    SELECT f.* FROM firms f
                    JOIN firm_categories fc ON f.id = fc.firm_id
                    WHERE fc.category_id = ?
                    ORDER BY f.name
                """, (category_id,))
                return [dict(row) for row in self.cursor.fetchall()]
            except Exception as e:
                logger.error(f"Kategori firmalarını getirme hatası: {e}")
                return []
    
    def get_category_stats(self):
        """Kategori istatistiklerini getir"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    SELECT 
                        c.id,
                        c.name,
                        c.color,
                        COUNT(fc.firm_id) as firm_count
                    FROM categories c
                    LEFT JOIN firm_categories fc ON c.id = fc.category_id
                    GROUP BY c.id, c.name, c.color
                    ORDER BY firm_count DESC, c.name
                """)
                return [dict(row) for row in self.cursor.fetchall()]
            except Exception as e:
                logger.error(f"Kategori istatistikleri hatası: {e}")
                return []

    # ==================== YÖNLENDİRME METODLARI ====================
    
    def update_firm_action(self, firm_id, action):
        """Firma son işlemini güncelle (whatsapp_yonlendirildi, cagri_yonlendirildi)"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute(
                    "UPDATE firms SET last_action = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                    (action, firm_id)
                )
                self.conn.commit()
                logger.info(f"Firma {firm_id} → {action} olarak işaretlendi")
                return True
            except Exception as e:
                logger.error(f"Firma action güncelleme hatası: {e}")
                return False
    
    def get_firms_by_action(self, action):
        """Son işleme göre firmaları getir"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute("""
                    SELECT * FROM firms 
                    WHERE last_action = ? 
                    ORDER BY updated_at DESC
                """, (action,))
                return [dict(row) for row in self.cursor.fetchall()]
            except Exception as e:
                logger.error(f"Firma action getirme hatası: {e}")
                return []
    
    def clear_firm_actions(self, action):
        """Belirli action'ları temizle"""
        with self.lock:
            try:
                self.ensure_connection()
                self.cursor.execute(
                    "UPDATE firms SET last_action = '' WHERE last_action = ?", 
                    (action,)
                )
                self.conn.commit()
                logger.info(f"{action} action'ları temizlendi")
                return True
            except Exception as e:
                logger.error(f"Action temizleme hatası: {e}")
                return False

    # ==================== ÇAĞRI ANALİZİ VERİTABANI METODLARI ====================
    
    def get_all_calls(self):
        """Tüm çağrıları getir - main2.py uyumluluğu için"""
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.*, f.name as firm_name 
                    FROM calls c
                    LEFT JOIN firms f ON c.firm_id = f.id
                    ORDER BY c.created_at DESC
                """)
                rows = cursor.fetchall()
                # Row objelerini dict'e çevir - güvenli yöntem
                calls = []
                for row in rows:
                    try:
                        # Row keys'lerini kullanarak dictionary oluştur
                        call_dict = {}
                        for key in row.keys():
                            call_dict[key] = row[key]
                        calls.append(call_dict)
                    except Exception as row_error:
                        logger.warning(f"Row dönüştürme hatası: {row_error}")
                        # Fallback: manuel dictionary oluştur
                        call_dict = {
                            'id': row[0] if len(row) > 0 else None,
                            'firm_id': row[1] if len(row) > 1 else None,
                            'call_id': row[2] if len(row) > 2 else '',
                            'phone_number': row[3] if len(row) > 3 else '',
                            'assistant_id': row[4] if len(row) > 4 else '',
                            'duration': row[5] if len(row) > 5 else 0,
                            'status': row[6] if len(row) > 6 else 'unknown',
                            'recording_url': row[7] if len(row) > 7 else '',
                            'transcript': row[8] if len(row) > 8 else '',
                            'notes': row[9] if len(row) > 9 else '',
                            'cost': row[10] if len(row) > 10 else 0.0,
                            'ai_analysis': row[11] if len(row) > 11 else '',
                            'created_at': row[12] if len(row) > 12 else '',
                            'updated_at': row[13] if len(row) > 13 else '',
                            'firm_name': row[14] if len(row) > 14 else 'Bilinmeyen Firma'
                        }
                        calls.append(call_dict)
                return calls
            except Exception as e:
                logger.error(f"Çağrıları getirme hatası: {e}")
                return []
    
    def get_calls_by_analysis(self, sentiment=None):
        """Analiz sonucuna göre çağrıları getir - main2.py uyumluluğu için"""
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                if sentiment:
                    cursor.execute("""
                        SELECT c.*, f.name as firm_name 
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        WHERE c.ai_analysis LIKE ?
                        ORDER BY c.created_at DESC
                    """, (f'%"sentiment": "{sentiment}"%',))
                else:
                    cursor.execute("""
                        SELECT c.*, f.name as firm_name 
                        FROM calls c
                        LEFT JOIN firms f ON c.firm_id = f.id
                        WHERE c.ai_analysis IS NULL OR c.ai_analysis = ''
                        ORDER BY c.created_at DESC
                    """)
                rows = cursor.fetchall()
                # Row objelerini dict'e çevir - güvenli yöntem
                calls = []
                for row in rows:
                    try:
                        # Row keys'lerini kullanarak dictionary oluştur
                        call_dict = {}
                        for key in row.keys():
                            call_dict[key] = row[key]
                        calls.append(call_dict)
                    except Exception as row_error:
                        logger.warning(f"Row dönüştürme hatası: {row_error}")
                        # Fallback: manuel dictionary oluştur
                        call_dict = {
                            'id': row[0] if len(row) > 0 else None,
                            'firm_id': row[1] if len(row) > 1 else None,
                            'call_id': row[2] if len(row) > 2 else '',
                            'phone_number': row[3] if len(row) > 3 else '',
                            'assistant_id': row[4] if len(row) > 4 else '',
                            'duration': row[5] if len(row) > 5 else 0,
                            'status': row[6] if len(row) > 6 else 'unknown',
                            'recording_url': row[7] if len(row) > 7 else '',
                            'transcript': row[8] if len(row) > 8 else '',
                            'notes': row[9] if len(row) > 9 else '',
                            'cost': row[10] if len(row) > 10 else 0.0,
                            'ai_analysis': row[11] if len(row) > 11 else '',
                            'created_at': row[12] if len(row) > 12 else '',
                            'updated_at': row[13] if len(row) > 13 else '',
                            'firm_name': row[14] if len(row) > 14 else 'Bilinmeyen Firma'
                        }
                        calls.append(call_dict)
                return calls
            except Exception as e:
                logger.error(f"Analiz bazlı çağrı getirme hatası: {e}")
                return []

    def close(self):
        """Database bağlantısını kapat"""
        # SQLite connection'ları context manager ile otomatik kapanır
        logger.info("Database bağlantısı kapatıldı")
    
    # ==================== KNOWLEDGE BASE METODLARI ====================
    
    def add_knowledge(self, title, content_type, content=None, file_path=None, url=None, tags=None, metadata=None):
        """Bilgi tabanına yeni içerik ekle"""
        with self.lock:
            try:
                self.ensure_connection()
                
                tags_json = json.dumps(tags) if tags else None
                metadata_json = json.dumps(metadata) if metadata else None
                
                self.cursor.execute("""
                    INSERT INTO knowledge_base 
                    (title, content_type, content, file_path, url, tags, metadata, learning_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
                """, (title, content_type, content, file_path, url, tags_json, metadata_json))
                
                self.conn.commit()
                knowledge_id = self.cursor.lastrowid
                logger.info(f"Bilgi eklendi: {title} (ID: {knowledge_id})")
                return knowledge_id
                
            except Exception as e:
                logger.error(f"Bilgi ekleme hatası: {e}")
                return None
    
    def update_knowledge_learning(self, knowledge_id, ai_analysis, ai_summary, embedding=None):
        """Öğrenilen bilgiyi güncelle"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("""
                    UPDATE knowledge_base 
                    SET ai_analysis = ?, ai_summary = ?, embedding = ?, 
                        is_learned = 1, learning_status = 'completed', 
                        learned_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (ai_analysis, ai_summary, embedding, knowledge_id))
                
                self.conn.commit()
                logger.info(f"Bilgi öğrenildi: ID {knowledge_id}")
                return True
                
            except Exception as e:
                logger.error(f"Bilgi öğrenme güncelleme hatası: {e}")
                return False
    
    def get_all_knowledge(self, filter_learned=None):
        """Tüm bilgileri getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                if filter_learned is None:
                    self.cursor.execute("""
                        SELECT * FROM knowledge_base 
                        ORDER BY created_at DESC
                    """)
                else:
                    self.cursor.execute("""
                        SELECT * FROM knowledge_base 
                        WHERE is_learned = ?
                        ORDER BY created_at DESC
                    """, (1 if filter_learned else 0,))
                
                rows = self.cursor.fetchall()
                knowledge_list = []
                for row in rows:
                    knowledge_dict = {}
                    for key in row.keys():
                        knowledge_dict[key] = row[key]
                    knowledge_list.append(knowledge_dict)
                
                return knowledge_list
                
            except Exception as e:
                logger.error(f"Bilgi getirme hatası: {e}")
                return []
    
    def delete_knowledge(self, knowledge_id):
        """Bilgiyi sil"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("DELETE FROM knowledge_base WHERE id = ?", (knowledge_id,))
                self.conn.commit()
                logger.info(f"Bilgi silindi: ID {knowledge_id}")
                return True
                
            except Exception as e:
                logger.error(f"Bilgi silme hatası: {e}")
                return False
    
    def save_learning_session(self, session_type, knowledge_ids, prompt, ai_response, tokens_used=0):
        """Öğrenme oturumunu kaydet"""
        with self.lock:
            try:
                self.ensure_connection()
                
                knowledge_ids_json = json.dumps(knowledge_ids) if knowledge_ids else None
                
                self.cursor.execute("""
                    INSERT INTO learning_sessions 
                    (session_type, knowledge_ids, prompt, ai_response, tokens_used, status)
                    VALUES (?, ?, ?, ?, ?, 'completed')
                """, (session_type, knowledge_ids_json, prompt, ai_response, tokens_used))
                
                self.conn.commit()
                session_id = self.cursor.lastrowid
                logger.info(f"Öğrenme oturumu kaydedildi: ID {session_id}")
                return session_id
                
            except Exception as e:
                logger.error(f"Öğrenme oturumu kaydetme hatası: {e}")
                return None
    
    def get_learning_history(self, limit=50):
        """Öğrenme geçmişini getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("""
                    SELECT * FROM learning_sessions 
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = self.cursor.fetchall()
                sessions = []
                for row in rows:
                    session_dict = {}
                    for key in row.keys():
                        session_dict[key] = row[key]
                    sessions.append(session_dict)
                
                return sessions
                
            except Exception as e:
                logger.error(f"Öğrenme geçmişi getirme hatası: {e}")
                return []
    
    def save_uploaded_file(self, file_name, file_type, file_size, file_path, knowledge_id=None):
        """Yüklenmiş dosyayı kaydet"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("""
                    INSERT INTO uploaded_files 
                    (file_name, file_type, file_size, file_path, knowledge_id, upload_status)
                    VALUES (?, ?, ?, ?, ?, 'completed')
                """, (file_name, file_type, file_size, file_path, knowledge_id))
                
                self.conn.commit()
                file_id = self.cursor.lastrowid
                logger.info(f"Dosya kaydedildi: {file_name} (ID: {file_id})")
                return file_id
                
            except Exception as e:
                logger.error(f"Dosya kaydetme hatası: {e}")
                return None
    
    def get_uploaded_files(self, knowledge_id=None):
        """Yüklenmiş dosyaları getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                if knowledge_id:
                    self.cursor.execute("""
                        SELECT * FROM uploaded_files 
                        WHERE knowledge_id = ?
                        ORDER BY created_at DESC
                    """, (knowledge_id,))
                else:
                    self.cursor.execute("""
                        SELECT * FROM uploaded_files 
                        ORDER BY created_at DESC
                    """)
                
                rows = self.cursor.fetchall()
                files = []
                for row in rows:
                    file_dict = {}
                    for key in row.keys():
                        file_dict[key] = row[key]
                    files.append(file_dict)
                
                return files
                
            except Exception as e:
                logger.error(f"Dosya getirme hatası: {e}")
                return []
    
    def search_knowledge(self, search_text):
        """Bilgi tabanında arama yap"""
        with self.lock:
            try:
                self.ensure_connection()
                
                search_pattern = f"%{search_text}%"
                self.cursor.execute("""
                    SELECT * FROM knowledge_base 
                    WHERE title LIKE ? OR content LIKE ? OR ai_summary LIKE ? OR tags LIKE ?
                    ORDER BY created_at DESC
                """, (search_pattern, search_pattern, search_pattern, search_pattern))
                
                rows = self.cursor.fetchall()
                knowledge_list = []
                for row in rows:
                    knowledge_dict = {}
                    for key in row.keys():
                        knowledge_dict[key] = row[key]
                    knowledge_list.append(knowledge_dict)
                
                return knowledge_list
                
            except Exception as e:
                logger.error(f"Bilgi arama hatası: {e}")
                return []
    
    # 🆕 Gelişmiş Web Scraping Fonksiyonları
    
    def update_firm_enhanced_scraping(self, firm_id: int, scraping_data: Dict) -> bool:
        """Gelişmiş web scraping verilerini güncelle"""
        with self.lock:
            try:
                self.ensure_connection()
                
                # JSON alanlarını serialize et
                company_type_analysis = json.dumps(scraping_data.get('company_type_analysis', {}), ensure_ascii=False)
                quality_analysis = json.dumps(scraping_data.get('quality_score', {}), ensure_ascii=False)
                products_list = json.dumps(scraping_data.get('products_services', {}).get('products', []), ensure_ascii=False)
                services_list = json.dumps(scraping_data.get('products_services', {}).get('services', []), ensure_ascii=False)
                product_categories = json.dumps(scraping_data.get('products_services', {}).get('categories', []), ensure_ascii=False)
                integrations_data = json.dumps(scraping_data.get('integrations', {}), ensure_ascii=False)
                
                # Temel değerler
                company_type = scraping_data.get('company_type_analysis', {}).get('primary_type_tr', '')
                company_type_confidence = scraping_data.get('company_type_analysis', {}).get('confidence', 0)
                quality_score = scraping_data.get('quality_score', {}).get('total_score', 0)
                quality_grade = scraping_data.get('quality_score', {}).get('grade', '')
                technical_score = scraping_data.get('quality_score', {}).get('technical_score', 0)
                content_score = scraping_data.get('quality_score', {}).get('content_score', 0)
                has_ecommerce = 1 if scraping_data.get('integrations', {}).get('has_payment', False) else 0
                
                self.cursor.execute("""
                    UPDATE firms SET
                        company_type = ?,
                        company_type_confidence = ?,
                        company_type_analysis = ?,
                        quality_score = ?,
                        quality_grade = ?,
                        quality_analysis = ?,
                        products_list = ?,
                        services_list = ?,
                        product_categories = ?,
                        integrations_data = ?,
                        has_ecommerce = ?,
                        technical_score = ?,
                        content_score = ?,
                        last_scraped_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    company_type, company_type_confidence, company_type_analysis,
                    quality_score, quality_grade, quality_analysis,
                    products_list, services_list, product_categories,
                    integrations_data, has_ecommerce,
                    technical_score, content_score,
                    firm_id
                ))
                
                self.conn.commit()
                logger.info(f"Firma {firm_id} gelişmiş scraping verileri güncellendi")
                return True
                
            except Exception as e:
                logger.error(f"Gelişmiş scraping güncelleme hatası: {e}")
                return False
    
    def get_firms_by_company_type(self, company_type: str) -> List[Dict]:
        """Firma tipine göre firmaları getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("""
                    SELECT * FROM firms 
                    WHERE company_type = ? AND status = 'active'
                    ORDER BY quality_score DESC
                """, (company_type,))
                
                rows = self.cursor.fetchall()
                firms = []
                for row in rows:
                    firm_dict = {}
                    for key in row.keys():
                        firm_dict[key] = row[key]
                    firms.append(firm_dict)
                
                return firms
                
            except Exception as e:
                logger.error(f"Firma tipi sorgulama hatası: {e}")
                return []
    
    def get_top_quality_firms(self, limit: int = 10) -> List[Dict]:
        """En yüksek kalite skoruna sahip firmaları getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("""
                    SELECT * FROM firms 
                    WHERE quality_score IS NOT NULL AND status = 'active'
                    ORDER BY quality_score DESC
                    LIMIT ?
                """, (limit,))
                
                rows = self.cursor.fetchall()
                firms = []
                for row in rows:
                    firm_dict = {}
                    for key in row.keys():
                        firm_dict[key] = row[key]
                    firms.append(firm_dict)
                
                return firms
                
            except Exception as e:
                logger.error(f"Top kalite firmaları sorgulama hatası: {e}")
                return []
    
    def get_firms_with_ecommerce(self) -> List[Dict]:
        """E-ticaret özelliği olan firmaları getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("""
                    SELECT * FROM firms 
                    WHERE has_ecommerce = 1 AND status = 'active'
                    ORDER BY quality_score DESC
                """)
                
                rows = self.cursor.fetchall()
                firms = []
                for row in rows:
                    firm_dict = {}
                    for key in row.keys():
                        firm_dict[key] = row[key]
                    firms.append(firm_dict)
                
                return firms
                
            except Exception as e:
                logger.error(f"E-ticaret firmaları sorgulama hatası: {e}")
                return []
    
    def get_enhanced_scraping_statistics(self) -> Dict:
        """Gelişmiş scraping istatistikleri"""
        with self.lock:
            try:
                self.ensure_connection()
                
                stats = {}
                
                # Firma tipi dağılımı
                self.cursor.execute("""
                    SELECT company_type, COUNT(*) as count 
                    FROM firms 
                    WHERE company_type IS NOT NULL AND status = 'active'
                    GROUP BY company_type
                """)
                company_types = {}
                for row in self.cursor.fetchall():
                    company_types[row[0]] = row[1]
                stats['company_types'] = company_types
                
                # Ortalama kalite skoru
                self.cursor.execute("""
                    SELECT AVG(quality_score) as avg_score 
                    FROM firms 
                    WHERE quality_score IS NOT NULL AND status = 'active'
                """)
                result = self.cursor.fetchone()
                stats['avg_quality_score'] = round(result[0], 2) if result[0] else 0
                
                # E-ticaret firma sayısı
                self.cursor.execute("""
                    SELECT COUNT(*) FROM firms 
                    WHERE has_ecommerce = 1 AND status = 'active'
                """)
                stats['ecommerce_firms'] = self.cursor.fetchone()[0]
                
                # Toplam taranan firma
                self.cursor.execute("""
                    SELECT COUNT(*) FROM firms 
                    WHERE last_scraped_at IS NOT NULL AND status = 'active'
                """)
                stats['scraped_firms'] = self.cursor.fetchone()[0]
                
                # Kalite dağılımı (A, B, C, D, F)
                self.cursor.execute("""
                    SELECT quality_grade, COUNT(*) as count 
                    FROM firms 
                    WHERE quality_grade IS NOT NULL AND status = 'active'
                    GROUP BY quality_grade
                """)
                quality_grades = {}
                for row in self.cursor.fetchall():
                    quality_grades[row[0]] = row[1]
                stats['quality_grades'] = quality_grades
                
                return stats
                
            except Exception as e:
                logger.error(f"Gelişmiş istatistik hatası: {e}")
                return {}
    
    # 🤖 AI Sohbet Asistanı Fonksiyonları
    
    def save_ai_chat_message(self, session_id: str, role: str, content: str, metadata: Dict = None, tokens_used: int = 0, model: str = None) -> bool:
        """AI sohbet mesajını kaydet"""
        with self.lock:
            try:
                self.ensure_connection()
                
                metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
                
                self.cursor.execute("""
                    INSERT INTO ai_chat_conversations 
                    (session_id, role, content, metadata, tokens_used, model, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (session_id, role, content, metadata_json, tokens_used, model, datetime.now()))
                
                # Oturumu güncelle
                self.cursor.execute("""
                    INSERT OR REPLACE INTO ai_chat_sessions 
                    (session_id, message_count, total_tokens, last_activity)
                    VALUES (
                        ?,
                        COALESCE((SELECT message_count FROM ai_chat_sessions WHERE session_id = ?), 0) + 1,
                        COALESCE((SELECT total_tokens FROM ai_chat_sessions WHERE session_id = ?), 0) + ?,
                        ?
                    )
                """, (session_id, session_id, session_id, tokens_used, datetime.now()))
                
                return True
                
            except Exception as e:
                logger.error(f"AI chat mesaj kayıt hatası: {e}")
                return False
    
    def get_ai_chat_history(self, session_id: str = None, limit: int = 100) -> List[Dict]:
        """AI sohbet geçmişini getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                if session_id:
                    self.cursor.execute("""
                        SELECT * FROM ai_chat_conversations 
                        WHERE session_id = ?
                        ORDER BY created_at ASC
                        LIMIT ?
                    """, (session_id, limit))
                else:
                    self.cursor.execute("""
                        SELECT * FROM ai_chat_conversations 
                        ORDER BY created_at DESC
                        LIMIT ?
                    """, (limit,))
                
                rows = self.cursor.fetchall()
                messages = []
                for row in rows:
                    msg = dict(row)
                    if msg.get('metadata'):
                        try:
                            msg['metadata'] = json.loads(msg['metadata'])
                        except:
                            pass
                    messages.append(msg)
                
                return messages
                
            except Exception as e:
                logger.error(f"AI chat geçmiş getirme hatası: {e}")
                return []
    
    def get_ai_chat_sessions(self, limit: int = 50) -> List[Dict]:
        """AI sohbet oturumlarını getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("""
                    SELECT * FROM ai_chat_sessions 
                    ORDER BY last_activity DESC
                    LIMIT ?
                """, (limit,))
                
                rows = self.cursor.fetchall()
                return [dict(row) for row in rows]
                
            except Exception as e:
                logger.error(f"AI chat oturum getirme hatası: {e}")
                return []
    
    def delete_ai_chat_session(self, session_id: str) -> bool:
        """AI sohbet oturumunu sil"""
        with self.lock:
            try:
                self.ensure_connection()
                
                self.cursor.execute("DELETE FROM ai_chat_conversations WHERE session_id = ?", (session_id,))
                self.cursor.execute("DELETE FROM ai_chat_sessions WHERE session_id = ?", (session_id,))
                
                return True
                
            except Exception as e:
                logger.error(f"AI chat oturum silme hatası: {e}")
                return False
    
    def get_ai_chat_stats(self) -> Dict:
        """AI sohbet istatistiklerini getir"""
        with self.lock:
            try:
                self.ensure_connection()
                
                stats = {}
                
                # Toplam oturum sayısı
                self.cursor.execute("SELECT COUNT(*) FROM ai_chat_sessions")
                stats['total_sessions'] = self.cursor.fetchone()[0]
                
                # Toplam mesaj sayısı
                self.cursor.execute("SELECT COUNT(*) FROM ai_chat_conversations")
                stats['total_messages'] = self.cursor.fetchone()[0]
                
                # Toplam token kullanımı
                self.cursor.execute("SELECT SUM(total_tokens) FROM ai_chat_sessions")
                result = self.cursor.fetchone()[0]
                stats['total_tokens'] = result if result else 0
                
                # Bugünkü mesajlar
                today = datetime.now().date()
                self.cursor.execute("""
                    SELECT COUNT(*) FROM ai_chat_conversations 
                    WHERE DATE(created_at) = ?
                """, (today,))
                stats['today_messages'] = self.cursor.fetchone()[0]
                
                # En aktif oturum
                self.cursor.execute("""
                    SELECT session_id, message_count 
                    FROM ai_chat_sessions 
                    ORDER BY message_count DESC 
                    LIMIT 1
                """)
                row = self.cursor.fetchone()
                if row:
                    stats['most_active_session'] = {
                        'session_id': row[0],
                        'message_count': row[1]
                    }
                
                return stats
                
            except Exception as e:
                logger.error(f"AI chat istatistik hatası: {e}")
                return {}

    def update_email_tracking(self, tracking_id: str, opened_at: str = None, 
                             open_count: int = 1, ip_address: str = None, 
                             user_agent: str = None, clicked_at: str = None, 
                             clicked_url: str = None, click_count: int = 1):
        """Email tracking verilerini güncelle - API server için"""
        with self.lock:
            try:
                # Email log'u bul
                self.cursor.execute("""
                    SELECT id, opened_date, open_count, clicked_date, click_count
                    FROM email_logs 
                    WHERE tracking_id = ?
                """, (tracking_id,))
                
                email_log = self.cursor.fetchone()
                if not email_log:
                    logger.warning(f"Email log bulunamadı: {tracking_id}")
                    return False
                
                # Açılma bilgilerini güncelle
                if opened_at:
                    if email_log['opened_date']:
                        # Zaten açılmış, sayıyı artır
                        new_count = (email_log['open_count'] or 0) + open_count
                        self.cursor.execute("""
                            UPDATE email_logs 
                            SET open_count = ?, opened_date = ?
                            WHERE tracking_id = ?
                        """, (new_count, opened_at, tracking_id))
                    else:
                        # İlk açılma
                        self.cursor.execute("""
                            UPDATE email_logs 
                            SET opened_date = ?, open_count = ?
                            WHERE tracking_id = ?
                        """, (opened_at, open_count, tracking_id))
                
                # Tıklama bilgilerini güncelle
                if clicked_at:
                    if email_log['clicked_date']:
                        # Zaten tıklanmış, sayıyı artır
                        new_count = (email_log['click_count'] or 0) + click_count
                        self.cursor.execute("""
                            UPDATE email_logs 
                            SET click_count = ?, clicked_date = ?
                            WHERE tracking_id = ?
                        """, (new_count, clicked_at, tracking_id))
                    else:
                        # İlk tıklama
                        self.cursor.execute("""
                            UPDATE email_logs 
                            SET clicked_date = ?, click_count = ?
                            WHERE tracking_id = ?
                        """, (clicked_at, click_count, tracking_id))
                
                self.conn.commit()
                logger.info(f"Email tracking güncellendi: {tracking_id}")
                return True
                
            except Exception as e:
                logger.error(f"Email tracking güncelleme hatası: {e}")
                return False

    # 📱 WhatsApp Günlük Limit Kontrolü Fonksiyonları
    
    def get_whatsapp_daily_limit(self, date: str = None) -> Dict:
        """Günlük WhatsApp limit bilgilerini al"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        with self.lock:
            try:
                self.cursor.execute("""
                    SELECT * FROM whatsapp_daily_limits 
                    WHERE date = ?
                """, (date,))
                
                result = self.cursor.fetchone()
                if result:
                    return dict(result)
                else:
                    # Yeni gün için kayıt oluştur
                    self.cursor.execute("""
                        INSERT INTO whatsapp_daily_limits (date, daily_limit)
                        VALUES (?, 50)
                    """, (date,))
                    self.conn.commit()
                    
                    return {
                        'date': date,
                        'messages_sent': 0,
                        'messages_approved': 0,
                        'messages_skipped': 0,
                        'messages_failed': 0,
                        'daily_limit': 50
                    }
                    
            except Exception as e:
                logger.error(f"WhatsApp günlük limit alma hatası: {e}")
                return {
                    'date': date,
                    'messages_sent': 0,
                    'messages_approved': 0,
                    'messages_skipped': 0,
                    'messages_failed': 0,
                    'daily_limit': 50
                }
    
    def update_whatsapp_daily_limit(self, date: str = None, 
                                   messages_sent: int = 0, 
                                   messages_approved: int = 0,
                                   messages_skipped: int = 0,
                                   messages_failed: int = 0) -> bool:
        """WhatsApp günlük limit sayacını güncelle"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        with self.lock:
            try:
                # Mevcut kaydı al
                current = self.get_whatsapp_daily_limit(date)
                
                # Yeni değerleri hesapla
                new_sent = current['messages_sent'] + messages_sent
                new_approved = current['messages_approved'] + messages_approved
                new_skipped = current['messages_skipped'] + messages_skipped
                new_failed = current['messages_failed'] + messages_failed
                
                # Güncelle
                self.cursor.execute("""
                    UPDATE whatsapp_daily_limits 
                    SET messages_sent = ?, messages_approved = ?, 
                        messages_skipped = ?, messages_failed = ?,
                        last_reset = CURRENT_TIMESTAMP
                    WHERE date = ?
                """, (new_sent, new_approved, new_skipped, new_failed, date))
                
                self.conn.commit()
                logger.info(f"WhatsApp günlük limit güncellendi: {date}")
                return True
                
            except Exception as e:
                logger.error(f"WhatsApp günlük limit güncelleme hatası: {e}")
                return False
    
    def can_send_whatsapp_message(self, date: str = None) -> Tuple[bool, str]:
        """WhatsApp mesaj gönderilebilir mi kontrol et"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            limit_info = self.get_whatsapp_daily_limit(date)
            
            if limit_info['messages_sent'] >= limit_info['daily_limit']:
                return False, f"Günlük limit aşıldı ({limit_info['messages_sent']}/{limit_info['daily_limit']})"
            
            return True, f"Gönderilebilir ({limit_info['messages_sent']}/{limit_info['daily_limit']})"
            
        except Exception as e:
            logger.error(f"WhatsApp limit kontrolü hatası: {e}")
            return False, "Limit kontrolü yapılamadı"
    
    def log_whatsapp_message(self, firm_id: int, firm_name: str, phone_number: str,
                           message_content: str, message_translation: str,
                           approval_status: str, send_status: str,
                           error_message: str = None, retry_count: int = 0) -> bool:
        """WhatsApp mesaj gönderim logunu kaydet"""
        with self.lock:
            try:
                sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if send_status == "sent" else None
                
                self.cursor.execute("""
                    INSERT INTO whatsapp_send_logs 
                    (firm_id, firm_name, phone_number, message_content, message_translation,
                     approval_status, send_status, error_message, retry_count, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (firm_id, firm_name, phone_number, message_content, message_translation,
                      approval_status, send_status, error_message, retry_count, sent_at))
                
                self.conn.commit()
                logger.info(f"WhatsApp mesaj logu kaydedildi: {firm_name}")
                return True
                
            except Exception as e:
                logger.error(f"WhatsApp mesaj logu kaydetme hatası: {e}")
                return False
    
    def get_whatsapp_send_stats(self, date: str = None) -> Dict:
        """WhatsApp gönderim istatistiklerini al"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        with self.lock:
            try:
                # Günlük limit bilgisi
                limit_info = self.get_whatsapp_daily_limit(date)
                
                # Günlük log istatistikleri
                self.cursor.execute("""
                    SELECT 
                        COUNT(*) as total_logs,
                        SUM(CASE WHEN send_status = 'sent' THEN 1 ELSE 0 END) as sent_count,
                        SUM(CASE WHEN send_status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                        SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) as approved_count,
                        SUM(CASE WHEN approval_status = 'skipped' THEN 1 ELSE 0 END) as skipped_count
                    FROM whatsapp_send_logs 
                    WHERE DATE(created_at) = ?
                """, (date,))
                
                log_stats = self.cursor.fetchone()
                
                return {
                    'date': date,
                    'daily_limit': limit_info['daily_limit'],
                    'messages_sent': limit_info['messages_sent'],
                    'messages_approved': limit_info['messages_approved'],
                    'messages_skipped': limit_info['messages_skipped'],
                    'messages_failed': limit_info['messages_failed'],
                    'total_logs': log_stats['total_logs'] or 0,
                    'sent_count': log_stats['sent_count'] or 0,
                    'failed_count': log_stats['failed_count'] or 0,
                    'approved_count': log_stats['approved_count'] or 0,
                    'skipped_count': log_stats['skipped_count'] or 0,
                    'remaining_limit': limit_info['daily_limit'] - limit_info['messages_sent']
                }
                
            except Exception as e:
                logger.error(f"WhatsApp istatistik alma hatası: {e}")
                return {
                    'date': date,
                    'daily_limit': 50,
                    'messages_sent': 0,
                    'messages_approved': 0,
                    'messages_skipped': 0,
                    'messages_failed': 0,
                    'total_logs': 0,
                    'sent_count': 0,
                    'failed_count': 0,
                    'approved_count': 0,
                    'skipped_count': 0,
                    'remaining_limit': 50
                }


if __name__ == "__main__":
    # Test database
    db = Database()
    
    # Test istatistikleri
    stats = db.get_statistics()
    print(f"\n=== DATABASE İSTATİSTİKLERİ ===")
    print(f"Toplam Firma: {stats.get('total_firms', 0)}")
    print(f"Aktif Firma: {stats.get('active_firms', 0)}")
    print(f"Toplam Mesaj: {stats.get('total_messages', 0)}")
    print(f"Bugünkü Mesaj: {stats.get('today_messages', 0)}")
    print(f"Toplam Arama: {stats.get('total_calls', 0)}")
    print(f"Bugünkü Arama: {stats.get('today_calls', 0)}")
    
    # Email istatistikleri
    email_stats = db.get_email_statistics()
    print(f"\n=== EMAIL İSTATİSTİKLERİ ===")
    print(f"Toplam Email: {email_stats.get('total_emails', 0)}")
    print(f"Açılan Email: {email_stats.get('opened_emails', 0)}")
    print(f"Tıklanan Email: {email_stats.get('clicked_emails', 0)}")
    print(f"Yanıtlanan Email: {email_stats.get('replied_emails', 0)}")
    
    print("\n✅ Database hazır ve çalışıyor!")