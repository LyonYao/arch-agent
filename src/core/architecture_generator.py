#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
架构生成器模块
负责生成架构设计
"""

import os
from typing import Dict, Any, Optional
from src.api.api_factory import APIFactory
from src.utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class ArchitectureGenerator:
    """架构生成器类"""
    
    def __init__(self):
        """初始化架构生成器"""
        # 创建API客户端
        self.api_client = APIFactory.create_api_client()
        logger.info(f"初始化架构生成器，使用模型: {self.api_client.model_name}")
        
        # 初始化架构验证器（如果需要）
        try:
            from src.core.architecture_validator import ArchitectureValidator
            self.architecture_validator = ArchitectureValidator()
            logger.info("初始化架构验证器")
        except ImportError:
            logger.warning("架构验证器模块不可用")
            self.architecture_validator = None
    
    def generate(self, requirements: str, stream_callback=None) -> Dict[str, Any]:
        """
        生成架构设计
        
        Args:
            requirements: 用户输入的系统需求描述
            stream_callback: 流式响应回调函数，用于实时显示生成结果
            
        Returns:
            Dict: 包含架构设计的响应
        """
        logger.info("开始生成架构设计")
        
        # 调用API生成架构
        response = self.api_client.generate_architecture(requirements, stream_callback)
        
        # 如果有错误，直接返回
        if "error" in response:
            logger.error(f"生成架构失败: {response['error']}")
            return response
        
        # 如果有架构验证器，验证架构
        if self.architecture_validator:
            logger.info("验证生成的架构")
            validation_result = self.architecture_validator.validate(response)
            
            # 如果验证失败，记录警告但仍返回原始架构
            if not validation_result["valid"]:
                logger.warning(f"架构验证失败: {validation_result['message']}")
                response["validation_warnings"] = validation_result["message"]
        
        logger.info("架构生成完成")
        return response
    
    def update_api_client(self, ai_type: Optional[str] = None):
        """
        更新API客户端
        
        Args:
            ai_type: AI模型类型，如果为None则使用配置文件中的设置
        """
        self.api_client = APIFactory.create_api_client(ai_type)
        logger.info(f"更新架构生成器API客户端，使用模型: {self.api_client.model_name}")
        
        # 同时更新架构验证器的API客户端
        if hasattr(self, 'architecture_validator') and self.architecture_validator:
            self.architecture_validator.api_client = self.api_client
            # 更新规则验证器的API客户端
            if hasattr(self.architecture_validator, 'rule_validator'):
                self.architecture_validator.rule_validator.api_client = self.api_client
            logger.info(f"更新架构验证器API客户端，使用模型: {self.api_client.model_name}")