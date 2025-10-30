#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import uuid
import threading
import time
import queue
import traceback
import ast
import croniter
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import pickle
import hashlib
import requests


# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockType(Enum):
    """Blok tipleri"""
    TRIGGER = "trigger"
    CONDITION = "condition"
    ACTION = "action"
    DELAY = "delay"
    CODE = "code"
    LOOP = "loop"
    API = "api"
    WEBHOOK = "webhook"
    SUBFLOW = "subflow"
    VARIABLE = "variable"
    FILTER = "filter"
    TRANSFORM = "transform"
    JOIN = "join"
    SPLIT = "split"
    ERROR_HANDLER = "error_handler"


class TriggerType(Enum):
    """Tetikleyici tipleri"""
    NEW_FIRM = "new_firm"
    EMAIL_OPENED = "email_opened"
    EMAIL_CLICKED = "email_clicked"
    EMAIL_REPLIED = "email_replied"
    WHATSAPP_MESSAGE = "whatsapp_message"
    SCHEDULED = "scheduled"
    WEBHOOK = "webhook"
    API_CALL = "api_call"
    MANUAL = "manual"
    FIRM_UPDATED = "firm_updated"
    CAMPAIGN_COMPLETED = "campaign_completed"
    CUSTOM_EVENT = "custom_event"


class ExecutionStatus(Enum):
    """Yürütme durumları"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class Variable:
    """Değişken tanımı"""
    name: str
    type: str
    value: Any
    scope: str = "flow"  # flow, global, local
    readonly: bool = False
    description: str = ""


@dataclass
class ExecutionContext:
    """Akış yürütme bağlamı"""
    flow_id: str
    execution_id: str
    variables: Dict[str, Variable]
    current_block: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    logs: List[Dict] = None
    parent_context: Optional['ExecutionContext'] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []
    
    def get_variable(self, name: str) -> Any:
        """Değişken değerini al"""
        if name in self.variables:
            return self.variables[name].value
        elif self.parent_context:
            return self.parent_context.get_variable(name)
        return None
    
    def set_variable(self, name: str, value: Any, var_type: str = "any"):
        """Değişken değerini set et"""
        if name in self.variables and self.variables[name].readonly:
            raise ValueError(f"Cannot modify readonly variable: {name}")
        
        self.variables[name] = Variable(name=name, type=var_type, value=value)
    
    def log(self, message: str, level: str = "info", data: Any = None):
        """Log ekle"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "block": self.current_block,
            "data": data
        }
        self.logs.append(log_entry)
        logger.log(getattr(logging, level.upper()), f"[{self.execution_id}] {message}")


class Block:
    """Gelişmiş blok sınıfı"""
    
    def __init__(self, block_id: str, block_type: BlockType, config: Dict):
        self.id = block_id
        self.type = block_type
        self.config = config
        self.title = config.get("title", "Untitled Block")
        self.description = config.get("description", "")
        self.enabled = config.get("enabled", True)
        self.retry_count = config.get("retry_count", 0)
        self.retry_delay = config.get("retry_delay", 5)
        self.timeout = config.get("timeout", 300)  # 5 dakika
        self.error_handler = config.get("error_handler")
        self.inputs = []
        self.outputs = []
        
    def validate(self) -> List[str]:
        """Blok konfigürasyonunu doğrula"""
        errors = []
        
        # Temel validasyonlar
        if not self.title:
            errors.append("Block title is required")
        
        # Tip bazlı validasyonlar
        if self.type == BlockType.CODE:
            if "code" not in self.config:
                errors.append("Code block requires 'code' field")
            else:
                try:
                    ast.parse(self.config["code"])
                except SyntaxError as e:
                    errors.append(f"Code syntax error: {str(e)}")
        
        elif self.type == BlockType.API:
            if "url" not in self.config:
                errors.append("API block requires 'url' field")
            if "method" not in self.config:
                errors.append("API block requires 'method' field")
        
        elif self.type == BlockType.LOOP:
            if "condition" not in self.config and "count" not in self.config:
                errors.append("Loop block requires either 'condition' or 'count'")
        
        return errors
    
    def execute(self, context: ExecutionContext) -> Any:
        """Bloğu yürüt"""
        context.current_block = self.id
        context.log(f"Executing block: {self.title}")
        
        if not self.enabled:
            context.log("Block is disabled, skipping", "warning")
            return None
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.retry_count:
            try:
                # Timeout kontrolü
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError(f"Block execution timed out after {self.timeout} seconds")
                
                if hasattr(signal, 'SIGALRM'):
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(self.timeout)
                
                try:
                    result = self._execute_logic(context)
                    if hasattr(signal, 'SIGALRM'):
                        signal.alarm(0)  # Timeout'u iptal et
                    
                    context.log(f"Block executed successfully", "info", {"result": str(result)[:200]})
                    return result
                    
                except Exception as e:
                    if hasattr(signal, 'SIGALRM'):
                        signal.alarm(0)
                    raise e
                    
            except Exception as e:
                last_error = e
                retry_count += 1
                
                if retry_count <= self.retry_count:
                    context.log(f"Block execution failed, retrying ({retry_count}/{self.retry_count})", 
                              "warning", {"error": str(e)})
                    time.sleep(self.retry_delay)
                else:
                    context.log(f"Block execution failed after {retry_count} attempts", 
                              "error", {"error": str(e), "traceback": traceback.format_exc()})
                    
                    if self.error_handler:
                        return self._handle_error(context, e)
                    else:
                        raise e
        
        raise last_error
    
    def _execute_logic(self, context: ExecutionContext) -> Any:
        """Blok tipine göre yürütme mantığı"""
        if self.type == BlockType.CODE:
            return self._execute_code(context)
        elif self.type == BlockType.API:
            return self._execute_api(context)
        elif self.type == BlockType.CONDITION:
            return self._execute_condition(context)
        elif self.type == BlockType.LOOP:
            return self._execute_loop(context)
        elif self.type == BlockType.VARIABLE:
            return self._execute_variable(context)
        elif self.type == BlockType.TRANSFORM:
            return self._execute_transform(context)
        elif self.type == BlockType.FILTER:
            return self._execute_filter(context)
        else:
            # Varsayılan davranış
            return self.config
    
    def _execute_code(self, context: ExecutionContext) -> Any:
        """Kod bloğunu yürüt"""
        code = self.config.get("code", "")
        
        # Güvenli bir execution ortamı oluştur
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "sorted": sorted,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "any": any,
                "all": all,
            },
            "datetime": datetime,
            "timedelta": timedelta,
            "json": json,
            "requests": requests,
            "context": context,
            "variables": {k: v.value for k, v in context.variables.items()},
            "set_variable": context.set_variable,
            "get_variable": context.get_variable,
            "log": context.log,
        }
        
        # Kod yürütme
        try:
            exec_locals = {}
            exec(code, safe_globals, exec_locals)
            
            # Return değerini al
            if "result" in exec_locals:
                return exec_locals["result"]
            elif "return_value" in exec_locals:
                return exec_locals["return_value"]
            else:
                return exec_locals
                
        except Exception as e:
            context.log(f"Code execution error: {str(e)}", "error")
            raise
    
    def _execute_api(self, context: ExecutionContext) -> Any:
        """API çağrısı yap"""
        url = self._resolve_template(self.config.get("url", ""), context)
        method = self.config.get("method", "GET").upper()
        headers = self.config.get("headers", {})
        body = self.config.get("body", {})
        auth = self.config.get("auth", {})
        
        # Template'leri çöz
        headers = {k: self._resolve_template(v, context) for k, v in headers.items()}
        
        if isinstance(body, str):
            body = self._resolve_template(body, context)
        elif isinstance(body, dict):
            body = {k: self._resolve_template(v, context) if isinstance(v, str) else v 
                   for k, v in body.items()}
        
        # Auth ayarları
        auth_obj = None
        if auth.get("type") == "basic":
            auth_obj = (auth.get("username"), auth.get("password"))
        elif auth.get("type") == "bearer":
            headers["Authorization"] = f"Bearer {auth.get('token')}"
        
        # İstek gönder
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method in ["POST", "PUT", "PATCH"] and isinstance(body, dict) else None,
                data=body if method in ["POST", "PUT", "PATCH"] and isinstance(body, str) else None,
                auth=auth_obj,
                timeout=30
            )
            
            # Yanıtı işle
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text
            }
            
            try:
                result["json"] = response.json()
            except:
                pass
            
            # Başarı kontrolü
            if not (200 <= response.status_code < 300):
                context.log(f"API request failed with status {response.status_code}", "warning")
            
            return result
            
        except Exception as e:
            context.log(f"API request error: {str(e)}", "error")
            raise
    
    def _execute_condition(self, context: ExecutionContext) -> bool:
        """Koşul kontrolü"""
        condition = self.config.get("condition", "")
        
        if isinstance(condition, str):
            # String koşul - template çöz ve eval et
            condition = self._resolve_template(condition, context)
            
            try:
                # Güvenli eval
                safe_dict = {
                    "variables": {k: v.value for k, v in context.variables.items()},
                    "get": context.get_variable,
                    "True": True,
                    "False": False,
                    "None": None,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                }
                
                result = eval(condition, {"__builtins__": {}}, safe_dict)
                return bool(result)
                
            except Exception as e:
                context.log(f"Condition evaluation error: {str(e)}", "error")
                return False
        
        elif isinstance(condition, dict):
            # Yapılandırılmış koşul
            operator = condition.get("operator", "equals")
            left = self._resolve_value(condition.get("left"), context)
            right = self._resolve_value(condition.get("right"), context)
            
            if operator == "equals":
                return left == right
            elif operator == "not_equals":
                return left != right
            elif operator == "greater_than":
                return left > right
            elif operator == "less_than":
                return left < right
            elif operator == "contains":
                return str(right) in str(left)
            elif operator == "starts_with":
                return str(left).startswith(str(right))
            elif operator == "ends_with":
                return str(left).endswith(str(right))
            elif operator == "regex":
                import re
                return bool(re.match(right, str(left)))
            elif operator == "in":
                return left in right
            elif operator == "not_in":
                return left not in right
            else:
                context.log(f"Unknown operator: {operator}", "warning")
                return False
        
        return True
    
    def _execute_loop(self, context: ExecutionContext) -> List[Any]:
        """Döngü yürüt"""
        results = []
        
        if "count" in self.config:
            # Sayaç bazlı döngü
            count = int(self._resolve_value(self.config["count"], context))
            for i in range(count):
                context.set_variable("loop_index", i)
                context.set_variable("loop_count", count)
                
                # Alt blokları yürüt (bu kısım flow executor'da yapılacak)
                results.append({"index": i})
        
        elif "items" in self.config:
            # Liste bazlı döngü
            items = self._resolve_value(self.config["items"], context)
            if not isinstance(items, list):
                items = [items]
            
            for i, item in enumerate(items):
                context.set_variable("loop_index", i)
                context.set_variable("loop_item", item)
                context.set_variable("loop_count", len(items))
                
                results.append({"index": i, "item": item})
        
        elif "condition" in self.config:
            # Koşul bazlı döngü (while)
            max_iterations = self.config.get("max_iterations", 1000)
            i = 0
            
            while i < max_iterations:
                if not self._execute_condition(context):
                    break
                
                context.set_variable("loop_index", i)
                results.append({"index": i})
                i += 1
            
            if i >= max_iterations:
                context.log(f"Loop reached maximum iterations ({max_iterations})", "warning")
        
        return results
    
    def _execute_variable(self, context: ExecutionContext) -> Any:
        """Değişken işlemleri"""
        operation = self.config.get("operation", "set")
        name = self.config.get("name", "")
        
        if operation == "set":
            value = self._resolve_value(self.config.get("value"), context)
            var_type = self.config.get("type", "any")
            context.set_variable(name, value, var_type)
            return value
        
        elif operation == "get":
            return context.get_variable(name)
        
        elif operation == "increment":
            current = context.get_variable(name) or 0
            increment = self.config.get("increment", 1)
            new_value = current + increment
            context.set_variable(name, new_value)
            return new_value
        
        elif operation == "append":
            current = context.get_variable(name) or []
            if not isinstance(current, list):
                current = [current]
            value = self._resolve_value(self.config.get("value"), context)
            current.append(value)
            context.set_variable(name, current)
            return current
        
        elif operation == "delete":
            if name in context.variables:
                del context.variables[name]
            return None
    
    def _execute_transform(self, context: ExecutionContext) -> Any:
        """Veri dönüşümü"""
        input_data = self._resolve_value(self.config.get("input"), context)
        transform_type = self.config.get("transform_type", "custom")
        
        if transform_type == "json_parse":
            return json.loads(input_data)
        
        elif transform_type == "json_stringify":
            return json.dumps(input_data)
        
        elif transform_type == "split":
            delimiter = self.config.get("delimiter", ",")
            return str(input_data).split(delimiter)
        
        elif transform_type == "join":
            delimiter = self.config.get("delimiter", ",")
            return delimiter.join(map(str, input_data))
        
        elif transform_type == "map":
            # Basit mapping
            mapping = self.config.get("mapping", {})
            if isinstance(input_data, list):
                return [self._apply_mapping(item, mapping, context) for item in input_data]
            else:
                return self._apply_mapping(input_data, mapping, context)
        
        elif transform_type == "custom":
            # Kod ile dönüşüm
            code = self.config.get("code", "return input_data")
            safe_globals = {
                "input_data": input_data,
                "json": json,
                "datetime": datetime,
                "context": context,
            }
            exec_locals = {}
            exec(f"result = {code}", safe_globals, exec_locals)
            return exec_locals.get("result", input_data)
        
        return input_data
    
    def _execute_filter(self, context: ExecutionContext) -> Any:
        """Veri filtreleme"""
        input_data = self._resolve_value(self.config.get("input"), context)
        filter_type = self.config.get("filter_type", "custom")
        
        if not isinstance(input_data, list):
            return input_data
        
        if filter_type == "condition":
            # Koşul bazlı filtreleme
            condition = self.config.get("condition", {})
            filtered = []
            
            for item in input_data:
                # Geçici olarak item'i context'e ekle
                old_item = context.get_variable("filter_item")
                context.set_variable("filter_item", item)
                
                if self._execute_condition(context):
                    filtered.append(item)
                
                # Eski değeri geri yükle
                if old_item is not None:
                    context.set_variable("filter_item", old_item)
                else:
                    context.variables.pop("filter_item", None)
            
            return filtered
        
        elif filter_type == "unique":
            # Benzersiz değerler
            seen = set()
            unique = []
            for item in input_data:
                key = str(item)
                if key not in seen:
                    seen.add(key)
                    unique.append(item)
            return unique
        
        elif filter_type == "first_n":
            n = self.config.get("n", 10)
            return input_data[:n]
        
        elif filter_type == "last_n":
            n = self.config.get("n", 10)
            return input_data[-n:]
        
        return input_data
    
    def _resolve_template(self, template: str, context: ExecutionContext) -> str:
        """Template string'i çöz"""
        if not isinstance(template, str):
            return template
        
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            value = context.get_variable(var_name)
            return str(value) if value is not None else match.group(0)
        
        # {{variable}} formatını değiştir
        result = re.sub(r'\{\{(\w+)\}\}', replace_var, template)
        
        # ${variable} formatını da destekle
        result = re.sub(r'\$\{(\w+)\}', replace_var, result)
        
        return result
    
    def _resolve_value(self, value: Any, context: ExecutionContext) -> Any:
        """Değer çözümleme"""
        if isinstance(value, str):
            # Variable reference kontrolü
            if value.startswith("{{") and value.endswith("}}"):
                var_name = value[2:-2].strip()
                return context.get_variable(var_name)
            elif value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1].strip()
                return context.get_variable(var_name)
            else:
                return self._resolve_template(value, context)
        
        elif isinstance(value, dict):
            # Dict içindeki değerleri recursive olarak çöz
            return {k: self._resolve_value(v, context) for k, v in value.items()}
        
        elif isinstance(value, list):
            # List içindeki değerleri recursive olarak çöz
            return [self._resolve_value(v, context) for v in value]
        
        return value
    
    def _apply_mapping(self, data: Any, mapping: Dict, context: ExecutionContext) -> Dict:
        """Mapping uygula"""
        result = {}
        
        for key, value in mapping.items():
            if isinstance(value, str):
                # Basit field mapping
                if value.startswith("$."):
                    # JSONPath benzeri erişim
                    path = value[2:].split(".")
                    current = data
                    for part in path:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            current = None
                            break
                    result[key] = current
                else:
                    result[key] = self._resolve_value(value, context)
            else:
                result[key] = value
        
        return result
    
    def _handle_error(self, context: ExecutionContext, error: Exception) -> Any:
        """Hata yönetimi"""
        handler_config = self.error_handler
        
        if isinstance(handler_config, str):
            # Basit hata mesajı
            context.log(f"Error handled: {handler_config}", "warning")
            return None
        
        elif isinstance(handler_config, dict):
            action = handler_config.get("action", "log")
            
            if action == "log":
                context.log(f"Error logged: {str(error)}", "error")
                return None
            
            elif action == "retry":
                # Retry logic zaten execute metodunda var
                pass
            
            elif action == "skip":
                context.log("Skipping block due to error", "warning")
                return None
            
            elif action == "fail":
                raise error
            
            elif action == "default_value":
                return handler_config.get("value")
            
            elif action == "goto":
                # Flow executor'da handle edilecek
                return {"__goto__": handler_config.get("target")}
        
        return None


class Flow:
    """Gelişmiş akış sınıfı"""
    
    def __init__(self, flow_id: str, name: str, config: Dict):
        self.id = flow_id
        self.name = name
        self.description = config.get("description", "")
        self.version = config.get("version", "1.0.0")
        self.tags = config.get("tags", [])
        self.status = config.get("status", "inactive")
        self.blocks = {}
        self.connections = []
        self.variables = {}
        self.settings = config.get("settings", {})
        self.created_at = config.get("created_at", datetime.now().isoformat())
        self.updated_at = config.get("updated_at", datetime.now().isoformat())
        
        # Blokları yükle
        for block_data in config.get("blocks", []):
            block = Block(
                block_id=block_data["id"],
                block_type=BlockType(block_data["type"]),
                config=block_data
            )
            self.blocks[block.id] = block
        
        # Bağlantıları yükle
        self.connections = config.get("connections", [])
        
        # Global değişkenleri yükle
        for var_data in config.get("variables", []):
            var = Variable(**var_data)
            self.variables[var.name] = var
    
    def validate(self) -> List[str]:
        """Akış doğrulama"""
        errors = []
        
        # Blok validasyonları
        for block_id, block in self.blocks.items():
            block_errors = block.validate()
            errors.extend([f"Block '{block.title}': {e}" for e in block_errors])
        
        # Bağlantı validasyonları
        block_ids = set(self.blocks.keys())
        for conn in self.connections:
            if conn["from"] not in block_ids:
                errors.append(f"Connection from non-existent block: {conn['from']}")
            if conn["to"] not in block_ids:
                errors.append(f"Connection to non-existent block: {conn['to']}")
        
        # Döngü kontrolü
        if self._has_circular_dependency():
            errors.append("Flow contains circular dependencies")
        
        # Başlangıç bloğu kontrolü
        start_blocks = self._find_start_blocks()
        if len(start_blocks) == 0:
            errors.append("Flow has no start blocks")
        elif len(start_blocks) > 1 and not self.settings.get("allow_multiple_starts", False):
            errors.append("Flow has multiple start blocks")
        
        return errors
    
    def _has_circular_dependency(self) -> bool:
        """Döngüsel bağımlılık kontrolü"""
        visited = set()
        rec_stack = set()
        
        def visit(block_id):
            if block_id in rec_stack:
                return True
            if block_id in visited:
                return False
            
            visited.add(block_id)
            rec_stack.add(block_id)
            
            # Çıkış bağlantılarını kontrol et
            for conn in self.connections:
                if conn["from"] == block_id:
                    if visit(conn["to"]):
                        return True
            
            rec_stack.remove(block_id)
            return False
        
        for block_id in self.blocks:
            if block_id not in visited:
                if visit(block_id):
                    return True
        
        return False
    
    def _find_start_blocks(self) -> List[str]:
        """Başlangıç bloklarını bul"""
        incoming = {block_id: 0 for block_id in self.blocks}
        
        for conn in self.connections:
            if conn["to"] in incoming:
                incoming[conn["to"]] += 1
        
        # Trigger blokları her zaman başlangıç bloğudur
        start_blocks = []
        for block_id, block in self.blocks.items():
            if block.type == BlockType.TRIGGER or incoming[block_id] == 0:
                start_blocks.append(block_id)
        
        return start_blocks
    
    def get_next_blocks(self, block_id: str, condition_result: Any = None) -> List[str]:
        """Bir bloktan sonraki blokları bul"""
        next_blocks = []
        
        for conn in self.connections:
            if conn["from"] == block_id:
                # Koşul kontrolü
                if "condition" in conn:
                    if conn["condition"] == "True" and condition_result:
                        next_blocks.append(conn["to"])
                    elif conn["condition"] == "False" and not condition_result:
                        next_blocks.append(conn["to"])
                    elif conn["condition"] == condition_result:
                        next_blocks.append(conn["to"])
                else:
                    next_blocks.append(conn["to"])
        
        return next_blocks
    
    def to_dict(self) -> Dict:
        """Flow'u dictionary'e dönüştür"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "tags": self.tags,
            "status": self.status,
            "blocks": [
                {
                    "id": block.id,
                    "type": block.type.value,
                    **block.config
                }
                for block in self.blocks.values()
            ],
            "connections": self.connections,
            "variables": [asdict(var) for var in self.variables.values()],
            "settings": self.settings,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class FlowExecutor:
    """Akış yürütücü"""
    
    def __init__(self, database=None):
        self.database = database
        self.running_flows = {}
        self.execution_queue = queue.Queue()
        self.executor_thread = None
        self.running = False
        self.execution_history = []
        self.webhooks = {}
        self.scheduled_triggers = {}
        
    def start(self):
        """Executor'ı başlat"""
        if not self.running:
            self.running = True
            self.executor_thread = threading.Thread(target=self._executor_loop, daemon=True)
            self.executor_thread.start()
            logger.info("Flow executor started")
    
    def stop(self):
        """Executor'ı durdur"""
        self.running = False
        if self.executor_thread:
            self.executor_thread.join(timeout=5)
        logger.info("Flow executor stopped")
    
    def _executor_loop(self):
        """Ana yürütme döngüsü"""
        while self.running:
            try:
                # Kuyruktan execution al
                task = self.execution_queue.get(timeout=1)
                
                if task["type"] == "execute_flow":
                    self._execute_flow_task(task)
                elif task["type"] == "execute_block":
                    self._execute_block_task(task)
                
            except queue.Empty:
                # Zamanlanmış tetikleyicileri kontrol et
                self._check_scheduled_triggers()
            except Exception as e:
                logger.error(f"Executor loop error: {str(e)}", exc_info=True)
    
    def execute_flow(self, flow: Flow, trigger_data: Dict = None, parent_context: ExecutionContext = None) -> str:
        """Akış yürütmeyi başlat"""
        execution_id = str(uuid.uuid4())
        
        # Yürütme bağlamı oluştur
        context = ExecutionContext(
            flow_id=flow.id,
            execution_id=execution_id,
            variables={**flow.variables},
            parent_context=parent_context
        )
        
        # Trigger verilerini ekle
        if trigger_data:
            context.set_variable("trigger", trigger_data)
        
        # Kuyruğa ekle
        self.execution_queue.put({
            "type": "execute_flow",
            "flow": flow,
            "context": context
        })
        
        # Çalışan akışlara ekle
        self.running_flows[execution_id] = {
            "flow": flow,
            "context": context,
            "status": "queued"
        }
        
        return execution_id
    
    def _execute_flow_task(self, task: Dict):
        """Akış yürütme görevi"""
        flow = task["flow"]
        context = task["context"]
        
        try:
            context.status = ExecutionStatus.RUNNING
            context.start_time = datetime.now()
            context.log(f"Starting flow execution: {flow.name}")
            
            # Başlangıç bloklarını bul
            start_blocks = flow._find_start_blocks()
            
            # Her başlangıç bloğunu yürüt
            for block_id in start_blocks:
                self._execute_block_recursive(flow, block_id, context)
            
            # Yürütme tamamlandı
            context.status = ExecutionStatus.SUCCESS
            context.end_time = datetime.now()
            context.log("Flow execution completed successfully")
            
        except Exception as e:
            context.status = ExecutionStatus.FAILED
            context.end_time = datetime.now()
            context.error = str(e)
            context.log(f"Flow execution failed: {str(e)}", "error", 
                       {"traceback": traceback.format_exc()})
        
        finally:
            # Geçmişe ekle
            self.execution_history.append({
                "execution_id": context.execution_id,
                "flow_id": flow.id,
                "flow_name": flow.name,
                "status": context.status.value,
                "start_time": context.start_time.isoformat() if context.start_time else None,
                "end_time": context.end_time.isoformat() if context.end_time else None,
                "error": context.error,
                "logs": context.logs
            })
            
            # Database'e kaydet
            if self.database and hasattr(self.database, 'save_flow_execution'):
                self.database.save_flow_execution(context)
            
            # Çalışan akışlardan kaldır
            if context.execution_id in self.running_flows:
                del self.running_flows[context.execution_id]
    
    def _execute_block_recursive(self, flow: Flow, block_id: str, context: ExecutionContext):
        """Bloğu ve takip eden blokları recursive olarak yürüt"""
        if block_id not in flow.blocks:
            context.log(f"Block not found: {block_id}", "error")
            return
        
        block = flow.blocks[block_id]
        
        try:
            # Bloğu yürüt
            result = block.execute(context)
            
            # Özel kontroller
            if isinstance(result, dict) and "__goto__" in result:
                # Belirli bir bloğa git
                next_block = result["__goto__"]
                if next_block in flow.blocks:
                    self._execute_block_recursive(flow, next_block, context)
                return
            
            # Sonraki blokları bul
            if block.type == BlockType.CONDITION:
                # Koşul sonucuna göre
                next_blocks = flow.get_next_blocks(block_id, result)
            elif block.type == BlockType.LOOP:
                # Döngü içeriğini yürüt
                loop_blocks = flow.get_next_blocks(block_id)
                for loop_result in result:
                    # Her iterasyon için loop değişkenlerini güncelle
                    for key, value in loop_result.items():
                        context.set_variable(f"loop_{key}", value)
                    
                    # Loop içindeki blokları yürüt
                    for next_block in loop_blocks:
                        self._execute_block_recursive(flow, next_block, context)
                
                # Loop'tan sonraki blokları bul
                # (Loop connection'larında özel bir marker olabilir)
                return
            else:
                # Normal akış
                next_blocks = flow.get_next_blocks(block_id)
            
            # Sonraki blokları yürüt
            for next_block in next_blocks:
                self._execute_block_recursive(flow, next_block, context)
            
        except Exception as e:
            context.log(f"Block execution error: {str(e)}", "error")
            
            # Error handler varsa
            if block.error_handler:
                error_result = block._handle_error(context, e)
                if isinstance(error_result, dict) and "__goto__" in error_result:
                    next_block = error_result["__goto__"]
                    if next_block in flow.blocks:
                        self._execute_block_recursive(flow, next_block, context)
            else:
                raise
    
    def _execute_block_task(self, task: Dict):
        """Tek blok yürütme görevi"""
        # Parallel execution veya sub-flow için kullanılabilir
        pass
    
    def _check_scheduled_triggers(self):
        """Zamanlanmış tetikleyicileri kontrol et"""
        current_time = datetime.now()
        
        for trigger_id, trigger_info in list(self.scheduled_triggers.items()):
            if "cron" in trigger_info:
                # Cron ifadesi
                cron = croniter.croniter(trigger_info["cron"], trigger_info.get("last_run", datetime.now()))
                next_run = cron.get_next(datetime)
                
                if next_run <= current_time:
                    # Tetikle
                    flow = trigger_info["flow"]
                    self.execute_flow(flow, {"trigger": "scheduled", "time": current_time.isoformat()})
                    trigger_info["last_run"] = current_time
            
            elif "interval" in trigger_info:
                # Interval bazlı
                last_run = trigger_info.get("last_run", datetime.now())
                interval = timedelta(seconds=trigger_info["interval"])
                
                if last_run + interval <= current_time:
                    # Tetikle
                    flow = trigger_info["flow"]
                    self.execute_flow(flow, {"trigger": "scheduled", "time": current_time.isoformat()})
                    trigger_info["last_run"] = current_time
    
    def register_webhook(self, webhook_id: str, flow: Flow):
        """Webhook kaydı"""
        self.webhooks[webhook_id] = flow
    
    def trigger_webhook(self, webhook_id: str, data: Dict):
        """Webhook tetikle"""
        if webhook_id in self.webhooks:
            flow = self.webhooks[webhook_id]
            self.execute_flow(flow, {"trigger": "webhook", "webhook_id": webhook_id, "data": data})
    
    def register_scheduled_trigger(self, trigger_id: str, flow: Flow, schedule: str):
        """Zamanlanmış tetikleyici kaydı"""
        if schedule.startswith("cron:"):
            # Cron formatı
            cron_expr = schedule[5:]
            self.scheduled_triggers[trigger_id] = {
                "flow": flow,
                "cron": cron_expr,
                "last_run": None
            }
        elif schedule.startswith("interval:"):
            # Interval formatı (saniye)
            interval = int(schedule[9:])
            self.scheduled_triggers[trigger_id] = {
                "flow": flow,
                "interval": interval,
                "last_run": datetime.now()
            }
    
    def pause_execution(self, execution_id: str):
        """Yürütmeyi duraklat"""
        if execution_id in self.running_flows:
            context = self.running_flows[execution_id]["context"]
            context.status = ExecutionStatus.PAUSED
            context.log("Execution paused")
    
    def resume_execution(self, execution_id: str):
        """Yürütmeyi devam ettir"""
        if execution_id in self.running_flows:
            context = self.running_flows[execution_id]["context"]
            context.status = ExecutionStatus.RUNNING
            context.log("Execution resumed")
    
    def cancel_execution(self, execution_id: str):
        """Yürütmeyi iptal et"""
        if execution_id in self.running_flows:
            context = self.running_flows[execution_id]["context"]
            context.status = ExecutionStatus.CANCELLED
            context.end_time = datetime.now()
            context.log("Execution cancelled")
            del self.running_flows[execution_id]
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict]:
        """Yürütme durumunu al"""
        if execution_id in self.running_flows:
            info = self.running_flows[execution_id]
            context = info["context"]
            
            return {
                "execution_id": execution_id,
                "flow_id": info["flow"].id,
                "flow_name": info["flow"].name,
                "status": context.status.value,
                "start_time": context.start_time.isoformat() if context.start_time else None,
                "current_block": context.current_block,
                "variables": {k: v.value for k, v in context.variables.items()},
                "logs": context.logs[-10:]  # Son 10 log
            }
        
        # Geçmişte ara
        for execution in self.execution_history:
            if execution["execution_id"] == execution_id:
                return execution
        
        return None


class AdvancedAutomationBuilder:
    """Gelişmiş otomasyon sistemi"""
    
    def __init__(self, database=None):
        self.database = database
        self.flows = {}
        self.flow_file = 'automation_flows_v2.json'
        self.executor = FlowExecutor(database)
        self.load_flows()
        self.executor.start()
    
    def load_flows(self):
        """Akışları yükle"""
        if os.path.exists(self.flow_file):
            try:
                with open(self.flow_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for flow_id, flow_data in data.items():
                    flow = Flow(flow_id, flow_data["name"], flow_data)
                    self.flows[flow_id] = flow
                    
                    # Aktif akışları executor'a kaydet
                    if flow.status == "active":
                        self._register_flow_triggers(flow)
                        
            except Exception as e:
                logger.error(f"Error loading flows: {str(e)}")
                self.flows = {}
        else:
            # Varsayılan akışları oluştur
            self._create_default_flows()
            self.save_flows()
    
    def save_flows(self):
        """Akışları kaydet"""
        try:
            data = {flow_id: flow.to_dict() for flow_id, flow in self.flows.items()}
            
            with open(self.flow_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error saving flows: {str(e)}")
            return False
    
    def _create_default_flows(self):
        """Varsayılan gelişmiş akışlar"""
        # Gelişmiş hoşgeldin serisi
        welcome_flow = {
            "name": "Gelişmiş Hoşgeldin Serisi",
            "description": "AI destekli kişiselleştirilmiş hoşgeldin kampanyası",
            "version": "2.0.0",
            "tags": ["onboarding", "welcome", "ai"],
            "status": "active",
            "blocks": [
                {
                    "id": "trigger_new_firm",
                    "type": "trigger",
                    "title": "Yeni Firma Eklendi",
                    "trigger_type": "new_firm",
                    "enabled": True
                },
                {
                    "id": "enrich_data",
                    "type": "api",
                    "title": "Firma Verilerini Zenginleştir",
                    "url": "https://api.example.com/enrich",
                    "method": "POST",
                    "body": {
                        "company_name": "{{trigger.firm_name}}",
                        "website": "{{trigger.website}}"
                    },
                    "timeout": 30
                },
                {
                    "id": "ai_personalization",
                    "type": "code",
                    "title": "AI ile Kişiselleştirme",
                    "code": """
# AI ile kişiselleştirilmiş mesaj oluştur
import json

firm_data = variables.get('trigger')
enriched_data = variables.get('enrich_result', {})

# Firma özelliklerine göre segment belirle
if enriched_data.get('employee_count', 0) > 100:
    segment = 'enterprise'
elif enriched_data.get('employee_count', 0) > 20:
    segment = 'mid_market'
else:
    segment = 'small_business'

# Sektöre göre yaklaşım belirle
industry = enriched_data.get('industry', 'general')
industry_approaches = {
    'technology': 'technical_benefits',
    'retail': 'sales_increase',
    'manufacturing': 'efficiency_gains',
    'general': 'value_proposition'
}

approach = industry_approaches.get(industry, 'value_proposition')

# Personalization context oluştur
personalization_context = {
    'firm_name': firm_data.get('name'),
    'segment': segment,
    'industry': industry,
    'approach': approach,
    'technologies': enriched_data.get('technologies', []),
    'pain_points': enriched_data.get('potential_pain_points', [])
}

set_variable('personalization_context', personalization_context)
result = personalization_context
                    """
                },
                {
                    "id": "check_best_time",
                    "type": "code",
                    "title": "En İyi Gönderim Zamanını Hesapla",
                    "code": """
from datetime import datetime, timedelta

# Sektör ve segment bazlı en iyi gönderim zamanları
best_times = {
    'enterprise': {'hour': 10, 'day_offset': 1},
    'mid_market': {'hour': 14, 'day_offset': 1},
    'small_business': {'hour': 9, 'day_offset': 0}
}

segment = get_variable('personalization_context').get('segment', 'small_business')
timing = best_times.get(segment, {'hour': 10, 'day_offset': 1})

# Gönderim zamanını hesapla
now = datetime.now()
send_date = now + timedelta(days=timing['day_offset'])
send_date = send_date.replace(hour=timing['hour'], minute=0, second=0)

# Hafta sonu kontrolü
if send_date.weekday() >= 5:  # Cumartesi veya Pazar
    days_until_monday = 7 - send_date.weekday()
    send_date += timedelta(days=days_until_monday)

set_variable('scheduled_send_time', send_date.isoformat())
result = send_date.isoformat()
                    """
                },
                {
                    "id": "wait_for_best_time",
                    "type": "delay",
                    "title": "En İyi Zamana Kadar Bekle",
                    "delay_type": "until",
                    "until": "{{scheduled_send_time}}"
                },
                {
                    "id": "generate_email",
                    "type": "api",
                    "title": "AI ile Email Oluştur",
                    "url": "https://api.openai.com/v1/chat/completions",
                    "method": "POST",
                    "headers": {
                        "Authorization": "Bearer {{openai_api_key}}",
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "model": "gpt-4",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Sen B2B satış uzmanısın. Kişiselleştirilmiş, ikna edici ve samimi satış mailleri yazıyorsun."
                            },
                            {
                                "role": "user",
                                "content": "Şu bilgilere göre bir hoşgeldin maili yaz: {{personalization_context}}"
                            }
                        ],
                        "temperature": 0.7
                    }
                },
                {
                    "id": "send_email",
                    "type": "action",
                    "title": "Email Gönder",
                    "action_type": "send_email",
                    "config": {
                        "to": "{{trigger.primary_email}}",
                        "subject": "{{email_subject}}",
                        "body": "{{email_body}}",
                        "track_opens": True,
                        "track_clicks": True
                    }
                },
                {
                    "id": "wait_for_open",
                    "type": "delay",
                    "title": "24 Saat Bekle",
                    "duration": 24,
                    "unit": "hours"
                },
                {
                    "id": "check_email_opened",
                    "type": "condition",
                    "title": "Email Açıldı mı?",
                    "condition": {
                        "operator": "equals",
                        "left": "{{email_opened}}",
                        "right": True
                    }
                },
                {
                    "id": "send_follow_up",
                    "type": "action",
                    "title": "Takip Maili Gönder",
                    "action_type": "send_email",
                    "enabled": True,
                    "config": {
                        "template": "follow_up_not_opened"
                    }
                },
                {
                    "id": "send_whatsapp",
                    "type": "action",
                    "title": "WhatsApp Mesajı Gönder",
                    "action_type": "send_whatsapp",
                    "config": {
                        "template": "welcome_opened",
                        "delay_hours": 48
                    }
                }
            ],
            "connections": [
                {"from": "trigger_new_firm", "to": "enrich_data"},
                {"from": "enrich_data", "to": "ai_personalization"},
                {"from": "ai_personalization", "to": "check_best_time"},
                {"from": "check_best_time", "to": "wait_for_best_time"},
                {"from": "wait_for_best_time", "to": "generate_email"},
                {"from": "generate_email", "to": "send_email"},
                {"from": "send_email", "to": "wait_for_open"},
                {"from": "wait_for_open", "to": "check_email_opened"},
                {"from": "check_email_opened", "to": "send_follow_up", "condition": "False"},
                {"from": "check_email_opened", "to": "send_whatsapp", "condition": "True"}
            ],
            "variables": [
                {
                    "name": "openai_api_key",
                    "type": "string",
                    "value": "",
                    "scope": "global",
                    "readonly": True,
                    "description": "OpenAI API anahtarı"
                }
            ],
            "settings": {
                "max_execution_time": 86400,  # 24 saat
                "retry_on_failure": True,
                "notification_email": "admin@example.com"
            }
        }
        
        self.flows["advanced_welcome"] = Flow("advanced_welcome", welcome_flow["name"], welcome_flow)
        
        # Lead scoring ve otomatik takip
        lead_scoring_flow = {
            "name": "Lead Scoring ve Otomatik Takip",
            "description": "Firma davranışlarına göre lead scoring ve otomatik takip",
            "version": "1.0.0",
            "tags": ["lead_scoring", "automation", "ai"],
            "status": "active",
            "blocks": [
                {
                    "id": "trigger_behavior",
                    "type": "trigger",
                    "title": "Davranış Tetikleyici",
                    "trigger_type": "custom_event",
                    "events": ["email_opened", "link_clicked", "website_visited", "demo_requested"]
                },
                {
                    "id": "calculate_score",
                    "type": "code",
                    "title": "Lead Score Hesapla",
                    "code": """
# Lead scoring algoritması
event = get_variable('trigger')
firm_id = event.get('firm_id')

# Mevcut skoru al
current_score = get_variable(f'lead_score_{firm_id}') or 0

# Event bazlı skorlama
score_weights = {
    'email_opened': 5,
    'link_clicked': 10,
    'website_visited': 15,
    'demo_requested': 50,
    'replied_email': 30,
    'whatsapp_replied': 25
}

event_type = event.get('event_type')
score_increment = score_weights.get(event_type, 0)

# Zaman bazlı çarpan (yeni eventler daha değerli)
days_since_last = (datetime.now() - datetime.fromisoformat(event.get('timestamp', datetime.now().isoformat()))).days
time_multiplier = max(0.5, 1 - (days_since_last * 0.1))

# Nihai skor
new_score = current_score + (score_increment * time_multiplier)
set_variable(f'lead_score_{firm_id}', new_score)

# Segment belirleme
if new_score >= 100:
    segment = 'hot'
elif new_score >= 50:
    segment = 'warm'
else:
    segment = 'cold'

set_variable('lead_segment', segment)
result = {'score': new_score, 'segment': segment}
                    """
                },
                {
                    "id": "check_segment",
                    "type": "condition",
                    "title": "Segment Kontrolü",
                    "condition": {
                        "operator": "equals",
                        "left": "{{lead_segment}}",
                        "right": "hot"
                    }
                },
                {
                    "id": "notify_sales",
                    "type": "action",
                    "title": "Satış Ekibini Bilgilendir",
                    "action_type": "send_notification",
                    "config": {
                        "channel": "slack",
                        "message": "🔥 HOT LEAD: {{trigger.firm_name}} - Score: {{lead_score}}"
                    }
                },
                {
                    "id": "create_task",
                    "type": "action",
                    "title": "Takip Görevi Oluştur",
                    "action_type": "create_task",
                    "config": {
                        "title": "Urgent: Contact {{trigger.firm_name}}",
                        "priority": "high",
                        "due_date": "+1 day"
                    }
                }
            ],
            "connections": [
                {"from": "trigger_behavior", "to": "calculate_score"},
                {"from": "calculate_score", "to": "check_segment"},
                {"from": "check_segment", "to": "notify_sales", "condition": "True"},
                {"from": "notify_sales", "to": "create_task"}
            ]
        }
        
        self.flows["lead_scoring"] = Flow("lead_scoring", lead_scoring_flow["name"], lead_scoring_flow)
    
    def create_flow(self, flow_data: Dict) -> str:
        """Yeni akış oluştur"""
        flow_id = f"flow_{uuid.uuid4().hex[:8]}"
        
        flow = Flow(flow_id, flow_data.get("name", "Untitled Flow"), flow_data)
        
        # Validasyon
        errors = flow.validate()
        if errors:
            raise ValueError(f"Flow validation failed: {', '.join(errors)}")
        
        self.flows[flow_id] = flow
        self.save_flows()
        
        # Aktifse executor'a kaydet
        if flow.status == "active":
            self._register_flow_triggers(flow)
        
        return flow_id
    
    def update_flow(self, flow_id: str, flow_data: Dict) -> bool:
        """Akışı güncelle"""
        if flow_id not in self.flows:
            return False
        
        old_flow = self.flows[flow_id]
        
        # Yeni flow oluştur
        new_flow = Flow(flow_id, flow_data.get("name", old_flow.name), flow_data)
        
        # Validasyon
        errors = new_flow.validate()
        if errors:
            raise ValueError(f"Flow validation failed: {', '.join(errors)}")
        
        # Eski tetikleyicileri kaldır
        if old_flow.status == "active":
            self._unregister_flow_triggers(old_flow)
        
        # Güncelle
        self.flows[flow_id] = new_flow
        new_flow.updated_at = datetime.now().isoformat()
        self.save_flows()
        
        # Yeni tetikleyicileri kaydet
        if new_flow.status == "active":
            self._register_flow_triggers(new_flow)
        
        return True
    
    def delete_flow(self, flow_id: str) -> bool:
        """Akışı sil"""
        if flow_id not in self.flows:
            return False
        
        flow = self.flows[flow_id]
        
        # Tetikleyicileri kaldır
        if flow.status == "active":
            self._unregister_flow_triggers(flow)
        
        del self.flows[flow_id]
        self.save_flows()
        
        return True
    
    def _register_flow_triggers(self, flow: Flow):
        """Akış tetikleyicilerini kaydet"""
        for block in flow.blocks.values():
            if block.type == BlockType.TRIGGER:
                trigger_type = block.config.get("trigger_type")
                
                if trigger_type == "scheduled":
                    schedule = block.config.get("schedule", "")
                    if schedule:
                        self.executor.register_scheduled_trigger(
                            f"{flow.id}_{block.id}",
                            flow,
                            schedule
                        )
                
                elif trigger_type == "webhook":
                    webhook_id = block.config.get("webhook_id", f"{flow.id}_{block.id}")
                    self.executor.register_webhook(webhook_id, flow)
    
    def _unregister_flow_triggers(self, flow: Flow):
        """Akış tetikleyicilerini kaldır"""
        # Scheduled triggers
        triggers_to_remove = []
        for trigger_id in self.executor.scheduled_triggers:
            if trigger_id.startswith(flow.id):
                triggers_to_remove.append(trigger_id)
        
        for trigger_id in triggers_to_remove:
            del self.executor.scheduled_triggers[trigger_id]
        
        # Webhooks
        webhooks_to_remove = []
        for webhook_id, webhook_flow in self.executor.webhooks.items():
            if webhook_flow.id == flow.id:
                webhooks_to_remove.append(webhook_id)
        
        for webhook_id in webhooks_to_remove:
            del self.executor.webhooks[webhook_id]
    
    def execute_flow(self, flow_id: str, trigger_data: Dict = None) -> str:
        """Akışı manuel olarak yürüt"""
        if flow_id not in self.flows:
            raise ValueError(f"Flow not found: {flow_id}")
        
        flow = self.flows[flow_id]
        return self.executor.execute_flow(flow, trigger_data)
    
    def test_flow(self, flow_id: str, test_data: Dict = None) -> Dict:
        """Akışı test et"""
        if flow_id not in self.flows:
            return {"success": False, "error": "Flow not found"}
        
        flow = self.flows[flow_id]
        
        # Test execution context
        test_context = ExecutionContext(
            flow_id=flow.id,
            execution_id=f"test_{uuid.uuid4().hex[:8]}",
            variables={**flow.variables}
        )
        
        if test_data:
            test_context.set_variable("test_data", test_data)
        
        # Dry run - sadece validate et
        results = {
            "success": True,
            "flow_name": flow.name,
            "validation": [],
            "blocks": []
        }
        
        # Flow validasyon
        errors = flow.validate()
        if errors:
            results["validation"] = errors
            results["success"] = False
        
        # Her bloğu test et
        for block in flow.blocks.values():
            block_result = {
                "block_id": block.id,
                "block_type": block.type.value,
                "title": block.title,
                "validation": []
            }
            
            # Blok validasyon
            block_errors = block.validate()
            if block_errors:
                block_result["validation"] = block_errors
            
            # Basit simülasyon
            try:
                if block.type == BlockType.CODE:
                    # Kod syntax kontrolü
                    ast.parse(block.config.get("code", ""))
                    block_result["status"] = "valid"
                else:
                    block_result["status"] = "valid"
            except Exception as e:
                block_result["status"] = "error"
                block_result["error"] = str(e)
            
            results["blocks"].append(block_result)
        
        return results
    
    def get_flow_statistics(self, flow_id: str) -> Optional[Dict]:
        """Akış istatistikleri"""
        if flow_id not in self.flows:
            return None
        
        flow = self.flows[flow_id]
        
        # Execution history'den istatistik topla
        executions = [e for e in self.executor.execution_history if e["flow_id"] == flow_id]
        
        stats = {
            "flow_id": flow_id,
            "flow_name": flow.name,
            "status": flow.status,
            "version": flow.version,
            "created_at": flow.created_at,
            "updated_at": flow.updated_at,
            "total_blocks": len(flow.blocks),
            "block_types": {},
            "total_executions": len(executions),
            "successful_executions": sum(1 for e in executions if e["status"] == "success"),
            "failed_executions": sum(1 for e in executions if e["status"] == "failed"),
            "average_duration": 0,
            "last_execution": None
        }
        
        # Blok tiplerini say
        for block in flow.blocks.values():
            block_type = block.type.value
            stats["block_types"][block_type] = stats["block_types"].get(block_type, 0) + 1
        
        # Ortalama süre hesapla
        durations = []
        for execution in executions:
            if execution.get("start_time") and execution.get("end_time"):
                start = datetime.fromisoformat(execution["start_time"])
                end = datetime.fromisoformat(execution["end_time"])
                durations.append((end - start).total_seconds())
        
        if durations:
            stats["average_duration"] = sum(durations) / len(durations)
        
        # Son yürütme
        if executions:
            stats["last_execution"] = executions[-1]
        
        return stats
    
    def get_execution_logs(self, execution_id: str) -> Optional[List[Dict]]:
        """Yürütme loglarını al"""
        execution = self.executor.get_execution_status(execution_id)
        if execution:
            return execution.get("logs", [])
        return None
    
    def import_flow(self, flow_data: Dict) -> str:
        """Akış import et"""
        # ID'yi yeniden oluştur
        new_flow_id = f"flow_{uuid.uuid4().hex[:8]}"
        flow_data["status"] = "inactive"  # Import edilen akışlar inactive başlar
        
        return self.create_flow(flow_data)
    
    def export_flow(self, flow_id: str) -> Optional[Dict]:
        """Akış export et"""
        if flow_id not in self.flows:
            return None
        
        flow = self.flows[flow_id]
        export_data = flow.to_dict()
        
        # Sensitive bilgileri temizle
        export_data.pop("id", None)
        for var in export_data.get("variables", []):
            if var.get("readonly"):
                var["value"] = ""
        
        return export_data
    
    def get_block_templates(self) -> Dict:
        """Gelişmiş blok şablonları"""
        return {
            "triggers": [
                {
                    "type": "trigger",
                    "subtype": "new_firm",
                    "title": "Yeni Firma Eklendi",
                    "description": "Sisteme yeni firma eklendiğinde tetiklenir",
                    "config": {"trigger_type": "new_firm"}
                },
                {
                    "type": "trigger",
                    "subtype": "scheduled",
                    "title": "Zamanlanmış Tetikleyici",
                    "description": "Belirli zamanlarda veya periyodik olarak tetiklenir",
                    "config": {
                        "trigger_type": "scheduled",
                        "schedule": "cron: 0 9 * * MON-FRI"  # Hafta içi her gün saat 9
                    }
                },
                {
                    "type": "trigger",
                    "subtype": "webhook",
                    "title": "Webhook Tetikleyici",
                    "description": "Dış sistemlerden gelen webhook çağrılarında tetiklenir",
                    "config": {
                        "trigger_type": "webhook",
                        "webhook_id": "",
                        "auth_required": True
                    }
                },
                {
                    "type": "trigger",
                    "subtype": "email_event",
                    "title": "Email Event",
                    "description": "Email açıldığında, tıklandığında veya yanıtlandığında",
                    "config": {
                        "trigger_type": "email_event",
                        "events": ["opened", "clicked", "replied"]
                    }
                }
            ],
            "conditions": [
                {
                    "type": "condition",
                    "title": "Basit Koşul",
                    "description": "İki değeri karşılaştır",
                    "config": {
                        "condition": {
                            "operator": "equals",
                            "left": "{{variable}}",
                            "right": "value"
                        }
                    }
                },
                {
                    "type": "condition",
                    "title": "Gelişmiş Koşul",
                    "description": "Kompleks mantıksal ifadeler",
                    "config": {
                        "condition": "variables.score > 50 and variables.segment == 'enterprise'"
                    }
                },
                {
                    "type": "condition",
                    "title": "Regex Koşul",
                    "description": "Pattern matching",
                    "config": {
                        "condition": {
                            "operator": "regex",
                            "left": "{{email}}",
                            "right": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                        }
                    }
                }
            ],
            "actions": [
                {
                    "type": "action",
                    "subtype": "send_email",
                    "title": "Email Gönder",
                    "description": "Kişiselleştirilmiş email gönder",
                    "config": {
                        "action_type": "send_email",
                        "template": "",
                        "personalization": True,
                        "track_opens": True,
                        "track_clicks": True
                    }
                },
                {
                    "type": "action",
                    "subtype": "api_call",
                    "title": "API Çağrısı",
                    "description": "Harici API'ye istek gönder",
                    "config": {
                        "action_type": "api_call",
                        "url": "",
                        "method": "POST",
                        "headers": {},
                        "body": {}
                    }
                },
                {
                    "type": "action",
                    "subtype": "update_data",
                    "title": "Veri Güncelle",
                    "description": "Firma veya lead verilerini güncelle",
                    "config": {
                        "action_type": "update_data",
                        "entity": "firm",
                        "updates": {}
                    }
                }
            ],
            "code": [
                {
                    "type": "code",
                    "title": "Python Kodu",
                    "description": "Özel Python kodu çalıştır",
                    "config": {
                        "code": "# Kodunuzu buraya yazın\nresult = None"
                    }
                },
                {
                    "type": "code",
                    "title": "Data Transformation",
                    "description": "Veri dönüştürme kodu",
                    "config": {
                        "code": """
# Input data'yı dönüştür
input_data = get_variable('input_data')

# Transformation logic
transformed = {
    'processed': True,
    'data': input_data
}

set_variable('output_data', transformed)
result = transformed
"""
                    }
                }
            ],
            "loops": [
                {
                    "type": "loop",
                    "title": "For Each Loop",
                    "description": "Liste üzerinde döngü",
                    "config": {
                        "items": "{{firm_list}}"
                    }
                },
                {
                    "type": "loop",
                    "title": "While Loop",
                    "description": "Koşul sağlandığı sürece döngü",
                    "config": {
                        "condition": "variables.counter < 10",
                        "max_iterations": 100
                    }
                },
                {
                    "type": "loop",
                    "title": "Repeat N Times",
                    "description": "Belirli sayıda tekrarla",
                    "config": {
                        "count": 5
                    }
                }
            ],
            "utilities": [
                {
                    "type": "variable",
                    "title": "Set Variable",
                    "description": "Değişken tanımla veya güncelle",
                    "config": {
                        "operation": "set",
                        "name": "variable_name",
                        "value": "",
                        "type": "string"
                    }
                },
                {
                    "type": "transform",
                    "title": "JSON Transform",
                    "description": "JSON verisi dönüştür",
                    "config": {
                        "transform_type": "json_parse",
                        "input": "{{json_string}}"
                    }
                },
                {
                    "type": "filter",
                    "title": "Filter List",
                    "description": "Liste filtrele",
                    "config": {
                        "filter_type": "condition",
                        "input": "{{list}}",
                        "condition": {
                            "operator": "greater_than",
                            "left": "{{filter_item.score}}",
                            "right": 50
                        }
                    }
                }
            ],
            "error_handling": [
                {
                    "type": "error_handler",
                    "title": "Try-Catch Block",
                    "description": "Hata yakalama ve yönetimi",
                    "config": {
                        "error_handler": {
                            "action": "log",
                            "message": "An error occurred"
                        }
                    }
                }
            ]
        }
    
    def trigger_event(self, event_type: str, event_data: Dict):
        """Olay tetikle"""
        # Tüm aktif flow'ları kontrol et
        for flow in self.flows.values():
            if flow.status != "active":
                continue
            
            # Trigger bloklarını kontrol et
            for block in flow.blocks.values():
                if block.type == BlockType.TRIGGER:
                    trigger_type = block.config.get("trigger_type")
                    
                    if trigger_type == event_type:
                        # Flow'u yürüt
                        self.executor.execute_flow(flow, {
                            "trigger": event_type,
                            "data": event_data,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    elif trigger_type == "custom_event":
                        events = block.config.get("events", [])
                        if event_type in events:
                            self.executor.execute_flow(flow, {
                                "trigger": event_type,
                                "data": event_data,
                                "timestamp": datetime.now().isoformat()
                            })
    
    def stop(self):
        """Automation builder'ı durdur"""
        self.executor.stop()
        self.save_flows()
