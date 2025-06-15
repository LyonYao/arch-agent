#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基础API客户端模块
定义AI模型API客户端的基类接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAPIClient(ABC):
    """AI模型API客户端基类"""
    
    @abstractmethod
    def __init__(self):
        """初始化API客户端"""
        pass
    
    @abstractmethod
    def generate_architecture(self, requirements: str, stream_callback=None) -> Dict[str, Any]:
        """
        根据需求生成架构设计
        
        Args:
            requirements: 用户输入的系统需求描述
            stream_callback: 流式响应回调函数，用于实时显示生成结果
            
        Returns:
            Dict: 包含架构设计的响应
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        获取当前使用的模型名称
        
        Returns:
            str: 模型名称
        """
        pass