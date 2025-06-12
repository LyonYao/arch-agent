#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志工具模块
提供统一的日志记录功能
"""

import os
import sys
import logging
import datetime
from typing import Optional

class Logger:
    """日志工具类"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """初始化日志工具"""
        # 确保只初始化一次
        if Logger._instance is not None:
            return
        
        # 创建日志目录
        self.log_dir = os.path.join(os.path.expanduser("~"), ".architect_agent", "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建日志文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"app_{timestamp}.log")
        
        # 配置根日志记录器
        self._setup_logging()
        
        # 获取根日志记录器
        self.logger = logging.getLogger()
        
        # 记录初始化信息
        self.logger.info(f"日志系统初始化完成，日志文件: {self.log_file}")
    
    def _setup_logging(self, level: str = "INFO"):
        """
        设置日志配置
        
        Args:
            level: 日志级别，默认为INFO
        """
        # 获取日志级别
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加文件处理器
        root_logger.addHandler(file_handler)
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    def set_level(self, level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        for handler in self.logger.handlers:
            handler.setLevel(log_level)
    
    def get_log_file(self) -> str:
        """
        获取日志文件路径
        
        Returns:
            str: 日志文件路径
        """
        return self.log_file

# 初始化日志工具
logger_instance = Logger.get_instance()

# 提供便捷的获取日志实例的函数
def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，默认为None（使用调用模块的名称）
        
    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)