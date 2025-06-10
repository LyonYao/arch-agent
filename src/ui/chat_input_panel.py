#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
聊天输入面板模块
实现聊天输入界面
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTextEdit, QPushButton, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal

class ChatInputPanel(QWidget):
    """聊天输入面板，用于用户输入消息"""
    
    # 定义信号
    message_sent = pyqtSignal(str)  # 消息发送信号，参数为消息文本
    
    def __init__(self):
        """初始化聊天输入面板"""
        super().__init__()
        
        # 创建UI组件
        self._create_ui()
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建模板选择区域
        template_layout = QHBoxLayout()
        
        template_label = QLabel("需求模板:")
        template_layout.addWidget(template_label)
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("无")
        self.template_combo.addItem("Web应用")
        self.template_combo.addItem("移动应用后端")
        self.template_combo.addItem("数据分析平台")
        self.template_combo.addItem("IoT解决方案")
        self.template_combo.addItem("架构调整")
        self.template_combo.currentIndexChanged.connect(self._load_template)
        template_layout.addWidget(self.template_combo)
        
        template_layout.addStretch()
        
        main_layout.addLayout(template_layout)
        
        # 创建输入框
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("请输入系统需求或调整需求...")
        self.input_edit.setMaximumHeight(100)
        main_layout.addWidget(self.input_edit)
        
        # 创建发送按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self._send_message)
        button_layout.addWidget(self.send_button)
        
        main_layout.addLayout(button_layout)
    
    def _send_message(self):
        """发送消息"""
        # 获取输入文本
        text = self.input_edit.toPlainText().strip()
        if not text:
            return
        
        # 清空输入框
        self.input_edit.clear()
        
        # 发送信号
        self.message_sent.emit(text)
    
    def set_enabled(self, enabled):
        """
        设置输入面板是否可用
        
        Args:
            enabled: 是否可用
        """
        self.input_edit.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.template_combo.setEnabled(enabled)
    
    def _load_template(self, index):
        """加载需求模板"""
        if index == 0:  # "无"
            return
        
        templates = {
            1: """我需要一个高可用的Web应用架构，用于电子商务网站。
该网站预计每月有约100万访问量，需要能够处理峰值流量。
系统需要包含产品目录、用户账户、购物车和支付处理功能。
安全性和可扩展性是关键要求。""",
            
            2: """我需要为一个移动应用设计后端架构。
该应用将有iOS和Android版本，预计用户数量为50万。
需要支持用户认证、数据同步、推送通知和API访问。
应用数据需要实时更新，并且需要考虑未来的扩展性。""",
            
            3: """我需要设计一个数据分析平台，用于处理和分析大量的销售和市场数据。
系统每天需要处理约500GB的数据，并提供实时和批处理分析功能。
需要支持数据可视化、报表生成和数据导出功能。
成本效益和性能是主要考虑因素。""",
            
            4: """我需要一个IoT解决方案架构，用于工业设备监控。
系统将连接约1000个传感器设备，这些设备每分钟发送一次数据。
需要实时数据处理、异常检测和警报功能。
数据安全和系统可靠性至关重要。""",
            
            5: """请对当前架构进行以下调整：
1. 增加数据备份和恢复机制
2. 提高系统安全性，特别是针对敏感数据的保护
3. 优化成本，减少不必要的资源使用
"""
        }
        
        if index in templates:
            self.input_edit.setPlainText(templates[index])