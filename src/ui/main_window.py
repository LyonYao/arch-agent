#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口模块
实现应用程序的主窗口界面
"""

import os
import sys
import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QSplitter, QMessageBox, QStatusBar, QToolBar, 
                           QFileDialog, QTabWidget, QPushButton, QLabel, QTextEdit)
from PyQt6.QtCore import Qt, QSize, QMetaObject, Q_ARG
from PyQt6.QtGui import QAction, QIcon, QFont

from src.ui.chat_panel import ChatPanel
from src.ui.output_panel import OutputPanel
from src.ui.session_panel import SessionPanel
from src.api.qianwen_api import QianwenAPI
from src.core.session_manager import SessionManager
from src.core.architecture_generator import ArchitectureGenerator

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
            # 初始化架构生成器
            self.architecture_generator = ArchitectureGenerator()
        except ValueError as e:
            QMessageBox.critical(self, "API配置错误", str(e))
            sys.exit(1)
        
        # 创建UI组件
        self._create_ui()
        self._create_toolbar()
        self._create_statusbar()
        self._create_connections()
        
        # 清理没有交互的会话
        self._cleanup_empty_sessions()
        
        # 如果没有活动会话，创建一个新会话
        if not self.session_manager.get_active_session():
            self.session_manager.create_session()
            self.session_panel.refresh()
            
        # 设置窗口大小变化事件
        self.resizeEvent = self._on_resize
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建上部主面板
        upper_panel = QWidget()
        upper_layout = QHBoxLayout(upper_panel)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建左侧会话面板
        self.session_panel = SessionPanel(self.session_manager)
        self.session_panel.setMaximumWidth(250)
        upper_layout.addWidget(self.session_panel)
        
        # 创建右侧工作区
        work_area = QWidget()
        work_layout = QVBoxLayout(work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 创建聊天面板
        self.chat_panel = ChatPanel()
        splitter.addWidget(self.chat_panel)
        
        # 创建输出面板
        self.output_panel = OutputPanel()
        splitter.addWidget(self.output_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 900])
        
        # 将分割器添加到工作区布局
        work_layout.addWidget(splitter)
        
        # 将工作区添加到上部布局
        upper_layout.addWidget(work_area, 1)  # 1表示伸展因子，使工作区占据更多空间
        
        # 创建主分割器，包含上部面板和日志控制台
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.setChildrenCollapsible(False)  # 防止完全折叠
        self.main_splitter.setHandleWidth(8)  # 增加分割条宽度，便于拖动
        
        # 将上部面板添加到主分割器
        self.main_splitter.addWidget(upper_panel)
        
        # 创建日志控制台面板
        self.log_console = LogConsole()
        
        # 创建日志控制台容器
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加日志控制台标题和按钮
        header_layout = QHBoxLayout()
        log_label = QLabel("日志控制台:")
        header_layout.addWidget(log_label)
        clear_log_button = QPushButton("清空日志")
        clear_log_button.clicked.connect(self.log_console.clear)
        header_layout.addWidget(clear_log_button)
        header_layout.addStretch(1)
        log_layout.addLayout(header_layout)
        
        # 添加日志控制台
        log_layout.addWidget(self.log_console)
        
        # 将日志容器添加到主分割器
        self.main_splitter.addWidget(log_container)
        
        # 设置分割器比例 (上部占75%，日志占25%)
        self.main_splitter.setSizes([750, 250])
        
        # 将主分割器添加到主布局
        main_layout.addWidget(self.main_splitter)
        
        # 连接分割器移动信号
        self.main_splitter.splitterMoved.connect(self._on_splitter_moved)
    
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
        
        # 导出Mermaid图表按钮
        export_mermaid_action = QAction("导出Mermaid", self)
        export_mermaid_action.setStatusTip("导出Mermaid格式的架构图")
        export_mermaid_action.triggered.connect(self._export_mermaid)
        toolbar.addAction(export_mermaid_action)
        
        toolbar.addSeparator()
        
        # 新建会话按钮
        new_session_action = QAction("新建会话", self)
        new_session_action.setStatusTip("创建新的架构设计会话")
        new_session_action.triggered.connect(self._create_new_session)
        toolbar.addAction(new_session_action)
        
        # 清理所有会话按钮
        clear_all_sessions_action = QAction("清理所有会话", self)
        clear_all_sessions_action.setStatusTip("删除所有会话")
        clear_all_sessions_action.triggered.connect(self._clear_all_sessions)
        toolbar.addAction(clear_all_sessions_action)
    
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
        
        # 立即保存用户输入到会话
        # 创建一个临时的响应对象，后续会更新
        temp_response = {"status": "processing", "user_input": message}
        self.session_manager.add_interaction(message, temp_response)
        # 刷新会话面板，显示最新会话状态
        self.session_panel.refresh()
        
        # 使用QThread处理API调用
        from PyQt6.QtCore import QThread, pyqtSignal
        
        class ApiThread(QThread):
            result_ready = pyqtSignal(dict)
            error_occurred = pyqtSignal(str)
            
            def __init__(self, architecture_generator, requirements, is_adjustment=False, context="", current_architecture=None):
                super().__init__()
                self.architecture_generator = architecture_generator
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
                        # 使用架构生成器生成架构，它会自动验证规则
                        response = self.architecture_generator.generate(adjustment_prompt)
                    else:
                        # 使用架构生成器生成架构，它会自动验证规则
                        response = self.architecture_generator.generate(self.requirements)
                    
                    self.result_ready.emit(response)
                except Exception as e:
                    self.error_occurred.emit(str(e))
        
        # 创建线程
        thread = ApiThread(
            self.architecture_generator, 
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
        
        # 检查是否有规则验证信息
        validation_info = ""
        if hasattr(self.architecture_generator, "architecture_validator"):
            validator = self.architecture_generator.architecture_validator
            if hasattr(validator, "rule_validator") and validator.rule_validator.rules:
                validation_info = f"\n\n架构已通过AI验证，符合 {len(validator.rule_validator.rules)} 条架构规则"
        
        self.chat_panel.update_thinking_message(thinking_index, f"架构设计已生成:{validation_info}\n\n{summary}")
        
        # 显示结果
        self.output_panel.display_architecture(response)
        self.statusBar.showMessage("架构设计生成完成")
        
        # 更新会话中的响应
        active_session = self.session_manager.get_active_session()
        if active_session:
            # 更新最后一个交互的响应
            self.session_manager.update_last_interaction(response)
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
    
    def _save_architecture(self):
        """保存架构设计到文件"""
        if not self.output_panel.has_architecture():
            QMessageBox.warning(self, "保存错误", "没有可保存的架构设计")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存架构设计", "", "Markdown文件 (*.md);;JSON文件 (*.json);;Mermaid文件 (*.mmd);;所有文件 (*)"
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
    
    def _export_mermaid(self):
        """导出Mermaid格式的架构图"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出Mermaid图表", "", "Mermaid文件 (*.mmd);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 确保文件扩展名为.mmd
                if not file_path.lower().endswith('.mmd'):
                    file_path += '.mmd'
                self.output_panel.export_diagram(file_path)
                self.statusBar.showMessage(f"Mermaid图表已导出到 {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出Mermaid图表时发生错误: {str(e)}")
    
    def _create_new_session(self):
        """创建新会话"""
        # 清理没有交互的会话
        self._cleanup_empty_sessions()
        
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
        self.output_panel.clear_mermaid()
        
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
            self.output_panel.clear_mermaid()
        
        self.statusBar.showMessage(f"已加载会话: {session.name}")
    
    def _cleanup_empty_sessions(self):
        """清理没有交互的会话"""
        sessions_to_delete = []
        active_session_id = None
        
        # 保存当前活动会话ID
        if self.session_manager.get_active_session():
            active_session_id = self.session_manager.get_active_session().session_id
        
        # 查找没有交互的会话
        for session_info in self.session_manager.get_all_sessions():
            session_id = session_info["session_id"]
            session = self.session_manager.get_session(session_id)
            
            # 如果会话没有交互记录，且不是当前活动会话，添加到待删除列表
            if session and len(session.interactions) == 0 and session_id != active_session_id:
                sessions_to_delete.append(session_id)
        
        # 删除空会话
        for session_id in sessions_to_delete:
            self.session_manager.delete_session(session_id)
            
        if sessions_to_delete:
            print(f"已清理 {len(sessions_to_delete)} 个空会话")
            
    def _clear_all_sessions(self):
        """清理所有会话"""
        # 弹出确认对话框
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            "确定要删除所有会话吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 删除所有会话
            count = self.session_manager.delete_all_sessions()
            
            # 刷新会话列表
            self.session_panel.refresh()
            
            # 清空输出面板
            self.output_panel.overview_tab.clear()
            self.output_panel.components_tab.clear()
            self.output_panel.decisions_tab.clear()
            self.output_panel.practices_tab.clear()
            self.output_panel.json_tab.clear()
            self.output_panel.diagram_image_label.setText("尚未生成架构图")
            self.output_panel.clear_mermaid()
            
            # 清空聊天面板
            self.chat_panel.clear()
            
            # 创建新会话
            self.session_manager.create_session()
            self.session_panel.refresh()
            
            self.statusBar.showMessage(f"已删除所有 {count} 个会话并创建新会话")
    
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
        self.output_panel.clear_mermaid()
        
        # 清空聊天面板
        self.chat_panel.clear()
        
        self.statusBar.showMessage("已创建新会话")
        
    def _on_splitter_moved(self, pos, index):
        """
        处理分割器移动事件
        
        Args:
            pos: 新位置
            index: 分割器索引
        """
        # 获取窗口总高度
        total_height = self.height()
        
        # 获取当前分割比例
        sizes = self.main_splitter.sizes()
        
        # 如果日志控制台高度超过窗口高度的50%，限制其大小
        if sizes[1] > total_height * 0.5:
            # 设置为50%的高度
            self.main_splitter.setSizes([int(total_height * 0.5), int(total_height * 0.5)])
            
        # 确保上部分至少有30%的高度
        elif sizes[0] < total_height * 0.3:
            # 设置上部分至少有30%的高度
            self.main_splitter.setSizes([int(total_height * 0.3), int(total_height * 0.7)])
            
    def _on_resize(self, event):
        """
        处理窗口大小变化事件
        
        Args:
            event: 大小变化事件
        """
        # 调用父类的resizeEvent
        super().resizeEvent(event)
        
        # 获取窗口总高度
        total_height = self.height()
        
        # 获取当前分割比例
        sizes = self.main_splitter.sizes()
        total_size = sum(sizes)
        
        if total_size > 0:
            # 计算比例
            ratio_0 = sizes[0] / total_size
            ratio_1 = sizes[1] / total_size
            
            # 根据比例重新设置大小
            self.main_splitter.setSizes([int(total_height * ratio_0), int(total_height * ratio_1)])
            
            # 确保日志控制台不超过50%
            if sizes[1] > total_height * 0.5:
                self.main_splitter.setSizes([int(total_height * 0.5), int(total_height * 0.5)])

# 日志控制台类
class LogConsole(QTextEdit):
    """日志控制台"""
    
    def __init__(self):
        """初始化日志控制台"""
        super().__init__()
        self.setReadOnly(True)
        self.setMinimumHeight(50)  # 设置最小高度
        self.setFont(QFont("Courier New", 9))
        
        # 设置样式，使其更明显
        self.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
        
        # 设置日志处理器
        self.log_handler = LogHandler(self)
        
        # 获取根日志记录器并添加处理器
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        
        # 初始化消息
        self.append("日志控制台已初始化，等待日志...")
    
    def clear(self):
        """清空日志"""
        super().clear()
        self.append("日志已清空...")

# 日志处理器类
class LogHandler(logging.Handler):
    """日志处理器"""
    
    def __init__(self, console):
        """初始化日志处理器"""
        logging.Handler.__init__(self)
        self.console = console
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
    def emit(self, record):
        """发送日志记录"""
        msg = self.format(record)
        # 使用Qt的信号槽机制在UI线程中更新文本
        QMetaObject.invokeMethod(
            self.console, 
            "append", 
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(str, msg)
        )
        # 滚动到底部
        QMetaObject.invokeMethod(
            self.console.verticalScrollBar(), 
            "setValue", 
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, self.console.verticalScrollBar().maximum())
        )