#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型配置对话框模块
提供AI模型配置界面
"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QPushButton, QLineEdit, QFormLayout,
                           QGroupBox, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from dotenv import load_dotenv, set_key, find_dotenv
from src.api.api_factory import APIFactory
from src.utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class ModelConfigDialog(QDialog):
    """AI模型配置对话框"""
    
    # 定义信号：模型配置已更改
    model_config_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """初始化模型配置对话框"""
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowTitle("AI模型配置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        # 加载环境变量
        load_dotenv()
        
        # 创建UI组件
        self._create_ui()
        
        # 加载当前配置
        self._load_current_config()
    
    def _create_ui(self):
        """创建UI组件"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 模型选择组
        model_group = QGroupBox("AI模型选择")
        model_layout = QVBoxLayout(model_group)
        
        # 模型类型选择
        model_type_layout = QHBoxLayout()
        model_type_label = QLabel("模型类型:")
        self.model_type_combo = QComboBox()
        
        # 添加可用的模型类型
        available_models = APIFactory.get_available_models()
        for model in available_models:
            self.model_type_combo.addItem(model["name"], model["type"])
        
        model_type_layout.addWidget(model_type_label)
        model_type_layout.addWidget(self.model_type_combo, 1)
        model_layout.addLayout(model_type_layout)
        
        # 连接模型类型变更信号
        self.model_type_combo.currentIndexChanged.connect(self._on_model_type_changed)
        
        # 添加模型组到主布局
        main_layout.addWidget(model_group)
        
        # 代理设置组
        proxy_group = QGroupBox("网络代理设置")
        proxy_layout = QVBoxLayout(proxy_group)
        
        # 是否使用代理
        self.use_proxy_checkbox = QCheckBox("使用代理")
        proxy_layout.addWidget(self.use_proxy_checkbox)
        
        # 代理设置表单
        proxy_form_layout = QFormLayout()
        self.http_proxy_input = QLineEdit()
        self.http_proxy_input.setPlaceholderText("例如: http://127.0.0.1:7890")
        self.https_proxy_input = QLineEdit()
        self.https_proxy_input.setPlaceholderText("例如: http://127.0.0.1:7890")
        
        proxy_form_layout.addRow("HTTP代理:", self.http_proxy_input)
        proxy_form_layout.addRow("HTTPS代理:", self.https_proxy_input)
        proxy_layout.addLayout(proxy_form_layout)
        
        # 连接代理复选框信号
        self.use_proxy_checkbox.stateChanged.connect(self._on_proxy_state_changed)
        
        # 添加代理组到主布局
        main_layout.addWidget(proxy_group)
        
        # 创建千问配置组
        self.qianwen_group = QGroupBox("千问模型配置")
        qianwen_layout = QFormLayout(self.qianwen_group)
        
        self.qianwen_api_key = QLineEdit()
        self.qianwen_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.qianwen_api_key.setPlaceholderText("输入千问API密钥")
        
        self.qianwen_model = QComboBox()
        self.qianwen_model.addItems(["qwen-turbo", "qwen-plus", "qwen-max"])
        
        qianwen_layout.addRow("API密钥:", self.qianwen_api_key)
        qianwen_layout.addRow("模型版本:", self.qianwen_model)
        
        main_layout.addWidget(self.qianwen_group)
        
        # 创建Gemini配置组
        self.gemini_group = QGroupBox("Gemini模型配置")
        gemini_layout = QFormLayout(self.gemini_group)
        
        self.gemini_api_key = QLineEdit()
        self.gemini_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.gemini_api_key.setPlaceholderText("输入Gemini API密钥")
        
        self.gemini_model = QComboBox()
        self.gemini_model.addItems(["gemini-1.5-flash"])
        
        gemini_layout.addRow("API密钥:", self.gemini_api_key)
        gemini_layout.addRow("模型版本:", self.gemini_model)
        
        main_layout.addWidget(self.gemini_group)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        
        self.cancel_button = QPushButton("取消")
        self.save_button = QPushButton("保存")
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
        # 连接按钮信号
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._save_config)
    
    def _load_current_config(self):
        """加载当前配置"""
        # 获取当前AI模型类型
        current_ai_type = os.getenv("AI_MODEL_TYPE", APIFactory.DEFAULT_AI_TYPE)
        
        # 设置当前选中的模型类型
        for i in range(self.model_type_combo.count()):
            if self.model_type_combo.itemData(i) == current_ai_type:
                self.model_type_combo.setCurrentIndex(i)
                break
        
        # 加载千问配置
        self.qianwen_api_key.setText(os.getenv("QIANWEN_API_KEY", ""))
        qianwen_model = os.getenv("QIANWEN_MODEL", "qwen-plus")
        index = self.qianwen_model.findText(qianwen_model)
        if index >= 0:
            self.qianwen_model.setCurrentIndex(index)
        
        # 加载Gemini配置
        self.gemini_api_key.setText(os.getenv("GEMINI_API_KEY", ""))
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro")
        index = self.gemini_model.findText(gemini_model)
        if index >= 0:
            self.gemini_model.setCurrentIndex(index)
        
        # 加载代理配置
        use_proxy = os.getenv("USE_PROXY", "False").lower() == "true"
        self.use_proxy_checkbox.setChecked(use_proxy)
        self.http_proxy_input.setText(os.getenv("HTTP_PROXY", ""))
        self.https_proxy_input.setText(os.getenv("HTTPS_PROXY", ""))
        
        # 根据代理设置状态更新UI
        self._on_proxy_state_changed()
        
        # 根据当前选择的模型类型显示/隐藏配置组
        self._update_config_visibility()
    
    def _on_model_type_changed(self):
        """模型类型变更处理"""
        self._update_config_visibility()
    
    def _on_proxy_state_changed(self):
        """代理状态变更处理"""
        # 根据复选框状态启用/禁用代理输入框
        enabled = self.use_proxy_checkbox.isChecked()
        self.http_proxy_input.setEnabled(enabled)
        self.https_proxy_input.setEnabled(enabled)
    
    def _update_config_visibility(self):
        """更新配置组的可见性"""
        current_type = self.model_type_combo.currentData()
        
        # 显示/隐藏对应的配置组
        self.qianwen_group.setVisible(current_type == APIFactory.AI_TYPE_QIANWEN)
        self.gemini_group.setVisible(current_type == APIFactory.AI_TYPE_GEMINI)
        
        # 调整对话框大小
        self.adjustSize()
    
    def _save_config(self):
        """保存配置"""
        try:
            # 获取.env文件路径
            dotenv_path = find_dotenv()
            if not dotenv_path:
                QMessageBox.critical(self, "配置错误", "找不到.env文件，请确保项目根目录下存在.env文件")
                return
            
            # 获取当前选择的模型类型
            current_type = self.model_type_combo.currentData()
            
            # 保存AI模型类型
            set_key(dotenv_path, "AI_MODEL_TYPE", current_type)
            
            # 根据模型类型保存对应配置
            if current_type == APIFactory.AI_TYPE_QIANWEN:
                # 保存千问配置
                qianwen_api_key = self.qianwen_api_key.text().strip()
                if not qianwen_api_key:
                    QMessageBox.warning(self, "配置错误", "请输入千问API密钥")
                    return
                
                set_key(dotenv_path, "QIANWEN_API_KEY", qianwen_api_key)
                set_key(dotenv_path, "QIANWEN_MODEL", self.qianwen_model.currentText())
                
            elif current_type == APIFactory.AI_TYPE_GEMINI:
                # 保存Gemini配置
                gemini_api_key = self.gemini_api_key.text().strip()
                if not gemini_api_key:
                    QMessageBox.warning(self, "配置错误", "请输入Gemini API密钥")
                    return
                
                set_key(dotenv_path, "GEMINI_API_KEY", gemini_api_key)
                set_key(dotenv_path, "GEMINI_MODEL", self.gemini_model.currentText())
            
            # 保存代理设置
            use_proxy = str(self.use_proxy_checkbox.isChecked())
            set_key(dotenv_path, "USE_PROXY", use_proxy)
            
            if self.use_proxy_checkbox.isChecked():
                http_proxy = self.http_proxy_input.text().strip()
                https_proxy = self.https_proxy_input.text().strip()
                
                if not http_proxy or not https_proxy:
                    QMessageBox.warning(self, "配置错误", "请输入HTTP和HTTPS代理地址")
                    return
                
                set_key(dotenv_path, "HTTP_PROXY", http_proxy)
                set_key(dotenv_path, "HTTPS_PROXY", https_proxy)
            
            # 立即应用代理设置
            APIFactory.setup_proxy()
            
            # 发送配置已更改信号
            self.model_config_changed.emit(current_type)
            
            # 提示保存成功
            QMessageBox.information(self, "保存成功", f"AI模型配置已保存，当前使用: {self.model_type_combo.currentText()}")
            
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            QMessageBox.critical(self, "保存失败", f"保存配置时发生错误: {str(e)}")