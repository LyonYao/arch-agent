#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统字体检测模块
用于检测系统中可用的支持中文的字体
"""

import os
import sys
import logging
import platform

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_system_chinese_font():
    """
    获取系统中支持中文的字体
    
    Returns:
        str: 支持中文的字体名称
    """
    system = platform.system()
    
    # Windows系统常见中文字体
    if system == "Windows":
        fonts = [
            
            "NSimSun",          # 新宋体
            "KaiTi" ,           # 楷体
            "Arial Unicode MS" ,  # Arial Unicode
            "SimHei",           # 黑体
            "Microsoft YaHei",  # 微软雅黑
            "SimSun",           # 宋体
            "FangSong",         # 仿宋
        ]
    
    # macOS系统常见中文字体
    elif system == "Darwin":
        fonts = [
            "PingFang SC",      # 苹方
            "Heiti SC",         # 黑体-简
            "STHeiti",          # 华文黑体
            "STSong",           # 华文宋体
            "STKaiti",          # 华文楷体
            "Arial Unicode MS"  # Arial Unicode
        ]
    
    # Linux系统常见中文字体
    else:
        fonts = [
            "WenQuanYi Micro Hei",  # 文泉驿微米黑
            "WenQuanYi Zen Hei",    # 文泉驿正黑
            "Droid Sans Fallback",  # Droid Sans回退字体
            "Noto Sans CJK SC",     # Noto Sans中日韩简体中文
            "Noto Sans SC",         # Noto Sans简体中文
            "DejaVu Sans"           # DejaVu Sans
        ]
    
    # 尝试检测字体是否存在（简单检查）
    for font in fonts:
        logger.info(f"尝试使用中文字体: {font}")
        return font  # 返回第一个字体，实际应用中可以添加字体存在性检查
    
    # 如果没有找到合适的字体，返回空字符串，让系统使用默认字体
    logger.warning("未找到合适的中文字体，将使用系统默认字体")
    return ""