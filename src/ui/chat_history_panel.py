#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
聊天历史面板模块
实现聊天历史记录显示
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, 
                           QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ChatMessage(QFrame):
    """聊天消息组件"""
    
    def __init__(self, text, is_user=True, parent=None):
        """
        初始化聊天消息
        
        Args:
            text: 消息文本
            is_user: 是否为用户消息
            parent: 父组件
        """
        super().__init__(parent)
        
        # 设置样式
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet(
            "background-color: #e6f7ff;" if is_user else "background-color: #f0f0f0;"
        )
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建标签
        sender = QLabel("用户" if is_user else "系统")
        sender.setStyleSheet("font-weight: bold; color: #0066cc;" if is_user else "font-weight: bold; color: #666666;")
        layout.addWidget(sender)
        
        # 创建消息文本
        message = QLabel(text)
        message.setWordWrap(True)
        message.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(message)

class ChatHistoryPanel(QWidget):
    """聊天历史面板，用于显示聊天历史记录"""
    
    def __init__(self):
        """初始化聊天历史面板"""
        super().__init__()
        
        # 创建UI组件
        self._create_ui()
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建聊天历史区域
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 创建聊天内容容器
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)
        
        # 添加欢迎消息
        welcome_message = ChatMessage("欢迎使用架构设计Agent！请输入您的系统需求，或选择下方的需求模板。", False)
        self.chat_layout.addWidget(welcome_message)
        
        # 添加弹性空间
        self.chat_layout.addStretch()
        
        # 设置聊天容器
        self.chat_scroll.setWidget(self.chat_container)
        main_layout.addWidget(self.chat_scroll)
    
    def add_user_message(self, text):
        """
        添加用户消息
        
        Args:
            text: 消息文本
        """
        # 创建消息组件
        message = ChatMessage(text, True)
        
        # 移除弹性空间
        self.chat_layout.removeItem(self.chat_layout.itemAt(self.chat_layout.count() - 1))
        
        # 添加消息
        self.chat_layout.addWidget(message)
        
        # 重新添加弹性空间
        self.chat_layout.addStretch()
        
        # 滚动到底部
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())
    
    def add_system_message(self, text):
        """
        添加系统消息
        
        Args:
            text: 消息文本
        """
        # 创建消息组件
        message = ChatMessage(text, False)
        
        # 移除弹性空间
        self.chat_layout.removeItem(self.chat_layout.itemAt(self.chat_layout.count() - 1))
        
        # 添加消息
        self.chat_layout.addWidget(message)
        
        # 重新添加弹性空间
        self.chat_layout.addStretch()
        
        # 滚动到底部
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())
    
    def add_thinking_message(self):
        """
        添加思考中消息
        
        Returns:
            int: 消息索引
        """
        # 创建带有动画效果的思考消息
        thinking_text = "正在思考中"
        message = ChatMessage(thinking_text + "...", False)
        
        # 移除弹性空间
        self.chat_layout.removeItem(self.chat_layout.itemAt(self.chat_layout.count() - 1))
        
        # 添加消息
        self.chat_layout.addWidget(message)
        
        # 重新添加弹性空间
        self.chat_layout.addStretch()
        
        # 滚动到底部
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())
        
        # 启动动画计时器
        from PyQt6.QtCore import QTimer
        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(lambda: self._update_thinking_animation(message, thinking_text))
        self.thinking_dots = 0
        self.thinking_timer.start(500)  # 每500毫秒更新一次
        
        return self.chat_layout.count() - 2  # 返回消息索引（减去弹性空间）
    
    def _update_thinking_animation(self, message_widget, base_text):
        """更新思考动画"""
        self.thinking_dots = (self.thinking_dots + 1) % 4
        dots = "." * self.thinking_dots
        # 找到消息文本标签（第二个子部件）
        for i in range(message_widget.layout().count()):
            item = message_widget.layout().itemAt(i)
            if item and isinstance(item.widget(), QLabel) and i == 1:
                item.widget().setText(base_text + "." * self.thinking_dots + " " * (3 - self.thinking_dots))
    
    def update_thinking_message(self, index, text):
        """
        更新思考中消息
        
        Args:
            index: 消息索引
            text: 新消息文本
        """
        # 获取消息组件
        item = self.chat_layout.itemAt(index)
        if item and item.widget():
            # 停止思考动画计时器
            if hasattr(self, 'thinking_timer') and self.thinking_timer.isActive():
                self.thinking_timer.stop()
            
            # 移除旧消息
            old_message = item.widget()
            self.chat_layout.removeWidget(old_message)
            old_message.deleteLater()
            
            # 添加新消息
            message = ChatMessage(text, False)
            self.chat_layout.insertWidget(index, message)
            
            # 滚动到底部
            self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())
    
    def clear(self):
        """清空聊天历史"""
        # 移除所有消息
        while self.chat_layout.count() > 1:  # 保留弹性空间
            item = self.chat_layout.itemAt(0)
            if item and item.widget():
                widget = item.widget()
                self.chat_layout.removeWidget(widget)
                widget.deleteLater()
        
        # 添加欢迎消息
        welcome_message = ChatMessage("欢迎使用架构设计Agent！请输入您的系统需求，或选择下方的需求模板。", False)
        self.chat_layout.insertWidget(0, welcome_message)