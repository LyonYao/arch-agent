#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口模块
实现应用程序的主窗口界面
"""

import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QSplitter, QMessageBox, QStatusBar, QToolBar, 
                           QFileDialog, QTabWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

from src.ui.chat_panel import ChatPanel
from src.ui.output_panel import OutputPanel
from src.ui.session_panel import SessionPanel
from src.api.qianwen_api import QianwenAPI
from src.core.session_manager import SessionManager

class MainWindow(QMainWindow):
    """应用程序主窗口"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("架构设计Agent")
        self.setMinimumSize(1200, 800)
        
        # 初始化会话管理器
        self.session_manager = SessionManager()
        
        # 初始化API客户端
        try:
            self.api_client = QianwenAPI()
        except ValueError as e:
            QMessageBox.critical(self, "API配置错误", str(e))
            sys.exit(1)
        
        # 创建UI组件
        self._create_ui()
        self._create_toolbar()
        self._create_statusbar()
        self._create_connections()
        
        # 如果没有活动会话，创建一个新会话
        if not self.session_manager.get_active_session():
            self.session_manager.create_session()
            self.session_panel.refresh()
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建左侧会话面板
        self.session_panel = SessionPanel(self.session_manager)
        self.session_panel.setMaximumWidth(250)
        main_layout.addWidget(self.session_panel)
        
        # 创建右侧主面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建聊天面板
        self.chat_panel = ChatPanel()
        splitter.addWidget(self.chat_panel)
        
        # 创建输出面板
        self.output_panel = OutputPanel()
        splitter.addWidget(self.output_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 800])
        
        # 将分割器添加到右侧布局
        right_layout.addWidget(splitter)
        
        # 将右侧面板添加到主布局
        main_layout.addWidget(right_panel, 1)  # 1表示伸展因子，使右侧面板占据更多空间
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # 保存架构按钮
        save_action = QAction("保存架构", self)
        save_action.setStatusTip("保存架构设计到文件")
        save_action.triggered.connect(self._save_architecture)
        toolbar.addAction(save_action)
        
        # 导出图表按钮
        export_diagram_action = QAction("导出图表", self)
        export_diagram_action.setStatusTip("导出架构图")
        export_diagram_action.triggered.connect(self._export_diagram)
        toolbar.addAction(export_diagram_action)
        
        toolbar.addSeparator()
        
        # 新建会话按钮
        new_session_action = QAction("新建会话", self)
        new_session_action.setStatusTip("创建新的架构设计会话")
        new_session_action.triggered.connect(self._create_new_session)
        toolbar.addAction(new_session_action)
    
    def _create_statusbar(self):
        """创建状态栏"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("就绪")
    
    def _create_connections(self):
        """创建信号连接"""
        # 聊天面板
        self.chat_panel.message_sent.connect(self._process_message)
        
        # 会话面板
        self.session_panel.session_selected.connect(self._on_session_selected)
        self.session_panel.session_created.connect(self._on_session_created)
    
    # 保存线程引用，防止线程被垃圾回收
    api_threads = []
    
    def _process_message(self, message):
        """
        处理用户消息
        
        Args:
            message: 用户输入的消息
        """
        if not message:
            return
        
        # 获取当前会话
        active_session = self.session_manager.get_active_session()
        if not active_session:
            return
        
        # 更新状态
        self.statusBar.showMessage("正在处理...")
        
        # 添加思考中消息
        thinking_index = self.chat_panel.add_thinking_message()
        
        # 禁用输入面板
        self.chat_panel.set_enabled(False)
        
        # 检查是否是第一次交互
        is_first_interaction = len(active_session.interactions) == 0
        
        # 使用QThread处理API调用
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class ApiThread(QThread):
            result_ready = pyqtSignal(dict)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, api_client, requirements, is_adjustment=False, context="", current_architecture=None):
                super().__init__()
                self.api_client = api_client
                self.requirements = requirements
                self.is_adjustment = is_adjustment
                self.context = context
                self.current_architecture = current_architecture
            
            def run(self):
                try:
                    if self.is_adjustment:
                        # 构建调整提示
                        adjustment_prompt = f"""基于以下历史交互和当前架构，根据新的需求调整架构设计：

历史交互：
{self.context}

当前架构概述：
{self.current_architecture.get('architecture_overview', '无架构概述')}

新的调整需求：
{self.requirements}

请保持原有架构的基本结构，根据新需求进行必要的调整。
"""
                        response = self.api_client.generate_architecture(adjustment_prompt)
                    else:
                        response = self.api_client.generate_architecture(self.requirements)
                    
                    self.result_ready.emit(response)
                except Exception as e:
                    self.error_occurred.emit(str(e))
        
        # 创建线程
        thread = ApiThread(
            self.api_client, 
            message,
            is_adjustment=not is_first_interaction,
            context=active_session.get_context_for_next_interaction() if not is_first_interaction else "",
            current_architecture=active_session.current_architecture if not is_first_interaction else None
        )
        
        # 保存线程引用，防止被垃圾回收
        MainWindow.api_threads.append(thread)
        
        # 添加线程完成后的清理
        thread.finished.connect(lambda: MainWindow.api_threads.remove(thread) if thread in MainWindow.api_threads else None)
        
        # 连接信号
        thread.result_ready.connect(
            lambda response: self._handle_api_response(response, message, thinking_index)
        )
        thread.error_occurred.connect(
            lambda error: self._handle_api_error(error, thinking_index)
        )
        
        # 启动线程
        thread.start()
    
    def _handle_api_response(self, response, requirements, thinking_index):
        """处理API响应"""
        if "error" in response:
            self._handle_api_error(response["error"], thinking_index)
            return
        
        # 更新思考中消息为成功消息
        overview = response.get("architecture_overview", "")
        summary = overview[:200] + "..." if len(overview) > 200 else overview
        self.chat_panel.update_thinking_message(thinking_index, f"架构设计已生成:\n\n{summary}")
        
        # 显示结果
        self.output_panel.display_architecture(response)
        self.statusBar.showMessage("架构设计生成完成")
        
        # 保存到当前会话
        active_session = self.session_manager.get_active_session()
        if active_session:
            self.session_manager.add_interaction(requirements, response)
            self.session_panel.refresh()
        
        # 启用输入面板
        self.chat_panel.set_enabled(True)
    
    def _handle_api_error(self, error, thinking_index):
        """处理API错误"""
        # 更新思考中消息为错误消息
        self.chat_panel.update_thinking_message(thinking_index, f"处理失败: {error}")
        self.statusBar.showMessage("处理失败")
        
        # 启用输入面板
        self.chat_panel.set_enabled(True)
    
    # 这些方法已被_process_message中的线程处理替代，可以删除
    
    def _save_architecture(self):
        """保存架构设计到文件"""
        if not self.output_panel.has_architecture():
            QMessageBox.warning(self, "保存错误", "没有可保存的架构设计")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存架构设计", "", "Markdown文件 (*.md);;JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            try:
                self.output_panel.save_architecture(file_path)
                self.statusBar.showMessage(f"架构设计已保存到 {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存错误", f"保存文件时发生错误: {str(e)}")
    
    def _export_diagram(self):
        """导出架构图"""
        if not self.output_panel.has_diagram():
            QMessageBox.warning(self, "导出错误", "没有可导出的架构图")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出架构图", "", "PNG图片 (*.png);;SVG图片 (*.svg);;所有文件 (*)"
        )
        
        if file_path:
            try:
                self.output_panel.export_diagram(file_path)
                self.statusBar.showMessage(f"架构图已导出到 {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出图表时发生错误: {str(e)}")
    
    def _create_new_session(self):
        """创建新会话"""
        # 创建新会话
        self.session_manager.create_session()
        
        # 刷新会话列表
        self.session_panel.refresh()
        
        # 清空输出面板
        self.output_panel.overview_tab.clear()
        self.output_panel.components_tab.clear()
        self.output_panel.decisions_tab.clear()
        self.output_panel.practices_tab.clear()
        self.output_panel.json_tab.clear()
        self.output_panel.diagram_image_label.setText("尚未生成架构图")
        
        self.statusBar.showMessage("已创建新会话")
    
    def _on_session_selected(self, session_id):
        """
        会话被选中
        
        Args:
            session_id: 会话ID
        """
        # 获取会话
        session = self.session_manager.get_session(session_id)
        if not session:
            return
        
        # 清空聊天面板
        self.chat_panel.clear()
        
        # 重建聊天历史
        if session.interactions:
            for interaction in session.interactions:
                # 添加用户消息
                self.chat_panel.history_panel.add_user_message(interaction["user_input"])
                
                # 添加系统响应
                if "architecture_overview" in interaction["ai_response"]:
                    overview = interaction["ai_response"]["architecture_overview"]
                    summary = overview[:200] + "..." if len(overview) > 200 else overview
                    self.chat_panel.history_panel.add_system_message(f"架构设计已生成/调整:\n\n{summary}")
        
        # 如果会话有架构设计，显示最新的架构设计
        if session.current_architecture:
            self.output_panel.display_architecture(session.current_architecture)
        else:
            # 清空输出面板
            self.output_panel.overview_tab.clear()
            self.output_panel.components_tab.clear()
            self.output_panel.decisions_tab.clear()
            self.output_panel.practices_tab.clear()
            self.output_panel.json_tab.clear()
            self.output_panel.diagram_image_label.setText("尚未生成架构图")
        
        self.statusBar.showMessage(f"已加载会话: {session.name}")
    
    def _on_session_created(self, session_id):
        """
        会话被创建
        
        Args:
            session_id: 会话ID
        """
        # 清空输出面板
        self.output_panel.overview_tab.clear()
        self.output_panel.components_tab.clear()
        self.output_panel.decisions_tab.clear()
        self.output_panel.practices_tab.clear()
        self.output_panel.json_tab.clear()
        self.output_panel.diagram_image_label.setText("尚未生成架构图")
        
        # 清空聊天面板
        self.chat_panel.clear()
        
        self.statusBar.showMessage("已创建新会话")