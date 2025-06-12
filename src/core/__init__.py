#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心模块初始化
"""

# 导入日志工具
from src.utils.logger import logger_instance

# 设置日志级别为DEBUG，确保所有日志都被记录
logger_instance.set_level("DEBUG")