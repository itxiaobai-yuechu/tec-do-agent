from datetime import datetime
import json
import os
from typing import Dict, Any, Optional, List
import logging


class Config:
    """配置管理类，用于读取和管理config.json配置文件"""

    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，默认为config.json
        """
        self.config_file = config_file
        self.config_data = {}
        self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                logging.info(f"成功加载配置文件: {self.config_file}")
            else:
                logging.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
                self.config_data = self.get_default_config()
        except json.JSONDecodeError as e:
            logging.error(f"配置文件格式错误: {e}")
            self.config_data = self.get_default_config()
        except Exception as e:
            logging.error(f"加载配置文件时发生错误: {e}")
            self.config_data = self.get_default_config()

    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            logging.info(f"配置已保存到: {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"保存配置文件时发生错误: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持嵌套配置访问

        Args:
            key: 配置键名，支持点号分隔的嵌套键，如 "database.host" 或 "api.openai.key"
            default: 默认值

        Returns:
            配置值或默认值

        Examples:
            config.get("openai_api_key")  # 获取顶级配置
            config.get("database.host", "localhost")  # 获取嵌套配置
            config.get("api.openai.model", "gpt-3.5-turbo")  # 获取深层嵌套配置
        """
        if "." not in key:
            return self.config_data.get(key, default)

        # 处理嵌套键
        keys = key.split(".")
        current = self.config_data

        try:
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return default
            return current
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值，支持嵌套配置设置

        Args:
            key: 配置键名，支持点号分隔的嵌套键，如 "database.host" 或 "api.openai.key"
            value: 配置值

        Examples:
            config.set("openai_api_key", "sk-...")  # 设置顶级配置
            config.set("database.host", "localhost")  # 设置嵌套配置
            config.set("api.openai.model", "gpt-4")  # 设置深层嵌套配置
        """
        if "." not in key:
            self.config_data[key] = value
            return

        # 处理嵌套键
        keys = key.split(".")
        current = self.config_data

        # 遍历到最后一个键之前，确保路径存在
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]

        # 设置最终值
        current[keys[-1]] = value

    def has(self, key: str) -> bool:
        """
        检查配置键是否存在，支持嵌套配置检查

        Args:
            key: 配置键名，支持点号分隔的嵌套键

        Returns:
            如果键存在返回True，否则返回False

        Examples:
            config.has("openai_api_key")  # 检查顶级配置
            config.has("database.host")  # 检查嵌套配置
        """
        if "." not in key:
            return key in self.config_data

        # 处理嵌套键
        keys = key.split(".")
        current = self.config_data

        try:
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return False
            return True
        except (KeyError, TypeError):
            return False

    def validate_config(self) -> List[str]:
        """
        验证配置的有效性

        Returns:
            错误信息列表
        """
        errors = []

        # 检查必需的配置项
        if not self.get("openai_api_key"):
            errors.append("OpenAI API Key 未设置")

        # 检查端口号范围
        port = self.get("server_port", 7860)
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("服务器端口号必须在1-65535之间")

        # 检查语言设置
        language = self.get("language", "auto")
        valid_languages = ["auto", "en_US", "ja_JP", "zh_CN"]
        if language not in valid_languages:
            errors.append(f"不支持的语言设置: {language}")

        return errors

    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "openai_api_key": "",
            "openai_api_base": "",
            "default_model": "gpt-3.5-turbo",
            "language": "auto",
            "users": [],
            "local_embedding": False,
            "hide_local_models": True,
            "hide_history_when_not_logged_in": False,
            "chat_name_method_index": 2,
            "bot_avatar": "default",
            "user_avatar": "default",
            "websearch_engine": "duckduckgo",
            "serper_search_api_key": "",
            "local_models": {},
            "multi_api_key": False,
            "api_key_list": [],
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "autobrowser": False,
            "log_dir": "./log",
            # 嵌套配置示例
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "ad_agent",
                "user": "admin"
            },
            "api": {
                "openai": {
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 2048,
                    "temperature": 0.7
                },
                "search": {
                    "engine": "duckduckgo",
                    "max_results": 10
                }
            },
            "ui": {
                "theme": "light",
                "language": "zh_CN",
                "auto_save": True
            }
        }

    def reload(self) -> None:
        """重新加载配置文件"""
        self.load_config()

    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config_data.copy()


# 全局配置实例
conf = Config()


def setup_logging():
    """配置日志记录"""
    # 创建日志目录
    log_dir = conf.get('log_dir')
    os.makedirs(log_dir, exist_ok=True)

    # 使用日期作为文件名
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{date_str}.log")

    # 创建logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # 清除现有的handlers
    logger.handlers.clear()

    # 创建文件handler，只记录ERROR及以上级别
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))

    # 创建控制台handler，只记录INFO级别
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))

    # 添加handlers到logger
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger


# 创建全局logger实例
logger = setup_logging()
