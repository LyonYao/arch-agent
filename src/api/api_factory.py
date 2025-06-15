#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API工厂模块
负责创建和管理不同的AI模型API客户端
"""

import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from src.utils.logger import get_logger
from src.api.base_api import BaseAPIClient
from src.api.qianwen_api import QianwenAPI
from src.api.gemini_api import GeminiAPI

# 加载环境变量
load_dotenv()

# 获取日志记录器
logger = get_logger(__name__)


class APIFactory:
    """API工厂类，负责创建和管理不同的AI模型API客户端"""
    
    # 支持的AI模型类型
    AI_TYPE_QIANWEN = "qianwen"
    AI_TYPE_GEMINI = "gemini"
    
    # 默认AI模型类型
    DEFAULT_AI_TYPE = AI_TYPE_QIANWEN
    
    @staticmethod
    def setup_proxy():
        """设置代理环境变量"""
        # 重新加载环境变量，确保获取最新配置
        load_dotenv(override=True)
        
        # 获取代理设置
        use_proxy = os.getenv("USE_PROXY", "False").lower() == "true"
        http_proxy = os.getenv("HTTP_PROXY", "")
        https_proxy = os.getenv("HTTPS_PROXY", "")
        
        # 清除现有代理设置
        if "HTTP_PROXY" in os.environ:
            del os.environ["HTTP_PROXY"]
        if "HTTPS_PROXY" in os.environ:
            del os.environ["HTTPS_PROXY"]
        
        # 如果启用代理，则设置代理环境变量
        if use_proxy and (http_proxy or https_proxy):
            if http_proxy:
                os.environ["HTTP_PROXY"] = http_proxy
            if https_proxy:
                os.environ["HTTPS_PROXY"] = https_proxy
            logger.info(f"已启用网络代理: HTTP={http_proxy}, HTTPS={https_proxy}")
            return True
        return False
    
    @staticmethod
    def create_api_client(ai_type: Optional[str] = None) -> BaseAPIClient:
        """
        创建API客户端
        
        Args:
            ai_type: AI模型类型，如果为None则使用配置文件中的设置
            
        Returns:
            BaseAPIClient: API客户端实例
            
        Raises:
            ValueError: 如果指定的AI模型类型不支持
        """
        # 设置代理
        APIFactory.setup_proxy()
        
        # 如果未指定AI类型，从环境变量获取
        if ai_type is None:
            ai_type = os.getenv("AI_MODEL_TYPE", APIFactory.DEFAULT_AI_TYPE).lower()
        
        logger.info(f"创建API客户端，AI类型: {ai_type}")
        
        # 根据AI类型创建对应的客户端
        if ai_type == APIFactory.AI_TYPE_QIANWEN:
            return QianwenAPI()
        elif ai_type == APIFactory.AI_TYPE_GEMINI:
            return GeminiAPI()
        else:
            raise ValueError(f"不支持的AI模型类型: {ai_type}")
    
    @staticmethod
    def get_available_models() -> List[Dict[str, str]]:
        """
        获取所有可用的AI模型信息
        
        Returns:
            List[Dict[str, str]]: 模型信息列表，每个模型包含type和name
        """
        models = [
            {"type": APIFactory.AI_TYPE_QIANWEN, "name": "阿里千问"},
            {"type": APIFactory.AI_TYPE_GEMINI, "name": "Google Gemini"}
        ]
        return models