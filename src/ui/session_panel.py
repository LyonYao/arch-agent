#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
会话面板模块
实现会话管理界面
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QListWidget, QListWidgetItem,
                           QInputDialog, QMessageBox, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.core.session_manager import SessionManager, Session

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SessionPanel(QWidget):
    """会话面板，用于管理会话"""
    
    # 定义信号
    session_selected = pyqtSignal(str)  # 会话ID
    session_created = pyqtSignal(str)   # 会话ID
    
    def __init__(self, session_manager: SessionManager):
        """
        初始化会话面板
        
        Args:
            session_manager: 会话管理器
        """
        super().__init__()
        
        # 保存会话管理器
        self.session_manager = session_manager
        
        # 创建UI组件
        self._create_ui()
        
        # 加载会话列表
        self._load_sessions()
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标题标签
        title_label = QLabel("会话历史")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # 创建会话列表
        self.session_list = QListWidget()
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self._show_context_menu)
        self.session_list.itemClicked.connect(self._on_session_clicked)
        main_layout.addWidget(self.session_list)
        
        # 创建底部按钮布局
        button_layout = QHBoxLayout()
        
        # 创建新建会话按钮
        self.new_session_button = QPushButton("新建会话")
        self.new_session_button.clicked.connect(self._create_new_session)
        button_layout.addWidget(self.new_session_button)
        
        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)
    
    def _load_sessions(self):
        """加载会话列表"""
        # 清空列表
        self.session_list.clear()
        
        # 获取所有会话
        sessions = self.session_manager.get_all_sessions()
        
        # 添加到列表
        for session_info in sessions:
            self._add_session_to_list(session_info)
        
        # 如果有活动会话，选中它
        active_session = self.session_manager.get_active_session()
        if active_session:
            self._select_session_in_list(active_session.session_id)
    
    def _add_session_to_list(self, session_info: Dict[str, Any]):
        """
        将会话添加到列表
        
        Args:
            session_info: 会话信息
        """
        # 创建列表项
        item = QListWidgetItem()
        
        # 设置会话ID为用户数据
        item.setData(Qt.ItemDataRole.UserRole, session_info["session_id"])
        
        # 设置显示文本
        created_time = datetime.fromtimestamp(session_info["created_at"]).strftime("%Y-%m-%d %H:%M")
        display_text = f"{session_info['name']}\n{created_time} | {session_info['interaction_count']}次交互"
        item.setText(display_text)
        
        # 添加到列表
        self.session_list.addItem(item)
    
    def _select_session_in_list(self, session_id: str):
        """
        在列表中选中指定会话
        
        Args:
            session_id: 会话ID
        """
        # 查找会话项
        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == session_id:
                # 选中项
                self.session_list.setCurrentItem(item)
                break
    
    def _on_session_clicked(self, item: QListWidgetItem):
        """
        会话项被点击
        
        Args:
            item: 列表项
        """
        # 获取会话ID
        session_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 设置为活动会话
        if self.session_manager.set_active_session(session_id):
            # 发送信号
            self.session_selected.emit(session_id)
    
    def _create_new_session(self):
        """创建新会话"""
        # 创建新会话
        session = self.session_manager.create_session()
        
        # 重新加载会话列表
        self._load_sessions()
        
        # 选中新会话
        self._select_session_in_list(session.session_id)
        
        # 发送信号
        self.session_created.emit(session.session_id)
    
    def _show_context_menu(self, position):
        """
        显示上下文菜单
        
        Args:
            position: 鼠标位置
        """
        # 获取当前选中的项
        item = self.session_list.itemAt(position)
        if not item:
            return
        
        # 获取会话ID
        session_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 创建上下文菜单
        menu = QMenu(self)
        
        # 添加重命名操作
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(lambda: self._rename_session(session_id))
        menu.addAction(rename_action)
        
        # 添加删除操作
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_session(session_id))
        menu.addAction(delete_action)
        
        # 显示菜单
        menu.exec(self.session_list.mapToGlobal(position))
    
    def _rename_session(self, session_id: str):
        """
        重命名会话
        
        Args:
            session_id: 会话ID
        """
        # 获取会话
        session = self.session_manager.get_session(session_id)
        if not session:
            return
        
        # 显示输入对话框
        new_name, ok = QInputDialog.getText(
            self, "重命名会话", "请输入新名称:", text=session.name
        )
        
        if ok and new_name:
            # 重命名会话
            if self.session_manager.rename_session(session_id, new_name):
                # 重新加载会话列表
                self._load_sessions()
    
    def _delete_session(self, session_id: str):
        """
        删除会话
        
        Args:
            session_id: 会话ID
        """
        # 确认删除
        reply = QMessageBox.question(
            self, "删除会话", "确定要删除此会话吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 删除会话
            if self.session_manager.delete_session(session_id):
                # 重新加载会话列表
                self._load_sessions()
    
    def refresh(self):
        """刷新会话列表"""
        self._load_sessions()