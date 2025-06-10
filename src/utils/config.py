#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
处理应用程序配置
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置管理类"""
    
    @staticmethod
    def get_api_key() -> str:
        """
        获取API密钥
        
        Returns:
            str: API密钥
        """
        api_key = os.getenv("QIANWEN_API_KEY")
        if not api_key:
            raise ValueError("未设置千问API密钥，请在.env文件中设置QIANWEN_API_KEY")
        return api_key
    
    @staticmethod
    def get_api_url() -> str:
        """
        获取API URL
        
        Returns:
            str: API URL
        """
        return os.getenv(
            "QIANWEN_API_URL", 
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        )
    
    @staticmethod
    def is_debug_mode() -> bool:
        """
        检查是否为调试模式
        
        Returns:
            bool: 是否为调试模式
        """
        return os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    @staticmethod
    def get_resources_path() -> str:
        """
        获取资源目录路径
        
        Returns:
            str: 资源目录路径
        """
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "resources")
    
    @staticmethod
    def get_templates_path() -> str:
        """
        获取模板目录路径
        
        Returns:
            str: 模板目录路径
        """
        return os.path.join(Config.get_resources_path(), "templates")
    
    @staticmethod
    def get_icons_path() -> str:
        """
        获取图标目录路径
        
        Returns:
            str: 图标目录路径
        """
        return os.path.join(Config.get_resources_path(), "icons")
    
    @staticmethod
    def get_aws_patterns_path() -> str:
        """
        获取AWS模式目录路径
        
        Returns:
            str: AWS模式目录路径
        """
        return os.path.join(Config.get_resources_path(), "aws_patterns")