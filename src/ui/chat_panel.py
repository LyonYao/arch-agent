#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
聊天面板模块
实现聊天式用户输入界面
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal

from src.ui.chat_history_panel import ChatHistoryPanel
from src.ui.chat_input_panel import ChatInputPanel

class ChatPanel(QWidget):
    """聊天面板，用于聊天式用户输入"""
    
    # 定义信号
    message_sent = pyqtSignal(str)  # 消息发送信号，参数为消息文本
    
    def __init__(self):
        """初始化聊天面板"""
        super().__init__()
        
        # 创建UI组件
        self._create_ui()
        
        # 创建信号连接
        self._create_connections()
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 创建聊天历史面板
        self.history_panel = ChatHistoryPanel()
        splitter.addWidget(self.history_panel)
        
        # 创建聊天输入面板
        self.input_panel = ChatInputPanel()
        splitter.addWidget(self.input_panel)
        
        # 设置分割器比例
        splitter.setSizes([600, 100])
        
        # 将分割器添加到主布局
        main_layout.addWidget(splitter)
    
    def _create_connections(self):
        """创建信号连接"""
        # 连接输入面板的消息发送信号
        self.input_panel.message_sent.connect(self._on_message_sent)
    
    def _on_message_sent(self, message):
        """
        处理消息发送
        
        Args:
            message: 消息文本
        """
        # 添加用户消息到历史面板
        self.history_panel.add_user_message(message)
        
        # 转发消息发送信号
        self.message_sent.emit(message)
    
    def add_thinking_message(self):
        """
        添加思考中消息
        
        Returns:
            int: 消息索引
        """
        return self.history_panel.add_thinking_message()
    
    def update_thinking_message(self, index, text):
        """
        更新思考中消息
        
        Args:
            index: 消息索引
            text: 新消息文本
        """
        self.history_panel.update_thinking_message(index, text)
    
    def set_enabled(self, enabled):
        """
        设置聊天面板是否可用
        
        Args:
            enabled: 是否可用
        """
        self.input_panel.set_enabled(enabled)
    
    def clear(self):
        """清空聊天面板"""
        self.history_panel.clear()