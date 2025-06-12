#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志控制台面板
显示应用程序的日志信息
"""

import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSlot, QObject, pyqtSignal

class LogHandler(QObject, logging.Handler):
    """自定义日志处理器，将日志发送到Qt信号"""
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
    def emit(self, record):
        """发送日志记录"""
        msg = self.format(record)
        self.log_signal.emit(msg)

class LogConsole(QWidget):
    """日志控制台面板"""
    
    def __init__(self):
        """初始化日志控制台"""
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.log_text)
        
        # 创建日志处理器
        self.log_handler = LogHandler()
        self.log_handler.log_signal.connect(self.append_log)
        
        # 设置日志处理器
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        
        # 初始化消息
        self.log_text.append("日志控制台已初始化，等待日志...")
    
    @pyqtSlot(str)
    def append_log(self, message):
        """添加日志消息"""
        self.log_text.append(message)
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
    
    def clear(self):
        """清空日志"""
        self.log_text.clear()
        self.log_text.append("日志已清空...")