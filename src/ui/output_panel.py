#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
输出面板模块
实现显示架构设计结果的界面
"""

import os
import json
import logging
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTextEdit, QTabWidget, QScrollArea, QMessageBox,
                           QPushButton, QSplitter)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView

from src.diagram.diagram_generator import DiagramGenerator
from src.diagram.mermaid_generator import MermaidGenerator
from src.utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

class OutputPanel(QWidget):
    """输出面板，用于显示架构设计结果"""
    
    def __init__(self):
        """初始化输出面板"""
        super().__init__()
        
        # 初始化属性
        self.architecture_data = None
        self.diagram_image = None
        self.original_pixmap = None
        self.current_scale = 1.0
        self.diagram_generator = DiagramGenerator()
        self.mermaid_generator = MermaidGenerator()
        self.mermaid_preloaded = False
        self.auto_preview = True  # 自动预览开关
        
        # 创建UI组件
        self._create_ui()
        
        # 预加载Mermaid库
        self._preload_mermaid()
    
    def _create_ui(self):
        """创建UI组件"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标题标签
        title_label = QLabel("架构设计结果")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        
        # 创建概述选项卡
        self.overview_tab = QTextEdit()
        self.overview_tab.setReadOnly(True)
        self.tab_widget.addTab(self.overview_tab, "架构概述")
        
        # 创建组件选项卡
        self.components_tab = QTextEdit()
        self.components_tab.setReadOnly(True)
        self.tab_widget.addTab(self.components_tab, "架构组件")
        
        # 创建图表选项卡
        self.diagram_tab = QScrollArea()
        self.diagram_tab.setWidgetResizable(True)
        self.diagram_content = QWidget()
        self.diagram_layout = QVBoxLayout(self.diagram_content)
        
        # 添加缩放控件布局
        self.zoom_layout = QHBoxLayout()
        
        # 创建缩放按钮
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("放大")
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        self.zoom_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setToolTip("缩小")
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        self.zoom_layout.addWidget(self.zoom_out_btn)
        
        self.reset_zoom_btn = QPushButton("重置")
        self.reset_zoom_btn.setToolTip("重置缩放")
        self.reset_zoom_btn.clicked.connect(self._reset_zoom)
        self.zoom_layout.addWidget(self.reset_zoom_btn)
        
        self.zoom_layout.addStretch()
        
        # 添加缩放控件布局到主布局
        self.diagram_layout.addLayout(self.zoom_layout)
        
        # 添加图像标签
        self.diagram_image_label = QLabel("尚未生成架构图")
        self.diagram_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.diagram_layout.addWidget(self.diagram_image_label)
        self.diagram_layout.addStretch()
        self.diagram_tab.setWidget(self.diagram_content)
        self.tab_widget.addTab(self.diagram_tab, "架构图")
        
        # 创建Mermaid选项卡
        self.mermaid_tab = QWidget()
        mermaid_layout = QVBoxLayout(self.mermaid_tab)
        mermaid_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建垂直分割器，允许用户调整大小
        self.mermaid_splitter = QSplitter(Qt.Orientation.Vertical)
        self.mermaid_splitter.setHandleWidth(8)  # 增加分割条宽度，便于拖动
        self.mermaid_splitter.setChildrenCollapsible(False)  # 防止完全折叠
        
        # 创建编辑区容器
        edit_container = QWidget()
        edit_layout = QVBoxLayout(edit_container)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建Mermaid代码编辑器
        self.mermaid_editor = QTextEdit()
        self.mermaid_editor.setReadOnly(False)
        self.mermaid_editor.setFont(QFont("Courier New", 10))
        self.mermaid_editor.textChanged.connect(self._on_mermaid_text_changed)
        edit_layout.addWidget(QLabel("Mermaid代码 (可编辑):"))
        edit_layout.addWidget(self.mermaid_editor)
        
        # 创建按钮布局
        buttons_layout = QHBoxLayout()
        
        # 创建预览按钮
        preview_button = QPushButton("预览")
        preview_button.clicked.connect(self._preview_mermaid)
        buttons_layout.addWidget(preview_button)
        
        # 创建自动预览切换按钮
        self.auto_preview_button = QPushButton("自动预览: 开")
        self.auto_preview_button.setCheckable(True)
        self.auto_preview_button.setChecked(True)
        self.auto_preview_button.clicked.connect(self._toggle_auto_preview)
        buttons_layout.addWidget(self.auto_preview_button)
        
        # 创建生成图片按钮
        generate_image_button = QPushButton("生成图片")
        generate_image_button.clicked.connect(self._generate_diagram_from_mermaid)
        buttons_layout.addWidget(generate_image_button)
        
        # 添加按钮布局
        edit_layout.addLayout(buttons_layout)
        
        # 创建预览区容器
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建预览区域
        preview_header = QHBoxLayout()
        preview_header.addWidget(QLabel("预览:"))
        
        # 添加预览状态指示器
        self.preview_status = QLabel("准备中...")
        self.preview_status.setStyleSheet("color: gray; font-style: italic;")
        preview_header.addWidget(self.preview_status)
        preview_header.addStretch(1)
        
        preview_layout.addLayout(preview_header)
        
        self.mermaid_preview = QWebEngineView()
        # 连接加载完成信号
        self.mermaid_preview.loadFinished.connect(self._on_preview_load_finished)
        preview_layout.addWidget(self.mermaid_preview)
        
        # 将编辑区和预览区添加到分割器
        self.mermaid_splitter.addWidget(edit_container)
        self.mermaid_splitter.addWidget(preview_container)
        self.mermaid_splitter.setSizes([200, 300])  # 设置初始大小
        
        # 将分割器添加到布局
        mermaid_layout.addWidget(self.mermaid_splitter)
        
        # 添加到选项卡
        self.tab_widget.addTab(self.mermaid_tab, "可编辑图表")
        
        # 创建决策选项卡
        self.decisions_tab = QTextEdit()
        self.decisions_tab.setReadOnly(True)
        self.tab_widget.addTab(self.decisions_tab, "设计决策")
        
        # 创建最佳实践选项卡
        self.practices_tab = QTextEdit()
        self.practices_tab.setReadOnly(True)
        self.tab_widget.addTab(self.practices_tab, "最佳实践")
        
        # 创建JSON选项卡
        self.json_tab = QTextEdit()
        self.json_tab.setReadOnly(True)
        self.json_tab.setFont(QFont("Courier New", 10))
        self.tab_widget.addTab(self.json_tab, "原始JSON")
        
        # 将选项卡控件添加到主布局
        main_layout.addWidget(self.tab_widget)
    
    def _preload_mermaid(self):
        """预加载Mermaid库，提高首次渲染速度"""
        logger.info("预加载Mermaid库...")
        
        # 创建一个简单的HTML页面，预加载Mermaid库
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.2.3/dist/mermaid.min.js"></script>
            <script>
                // 预加载完成后设置标志
                window.onload = function() {
                    console.log("Mermaid库预加载完成");
                    window.mermaidLoaded = true;
                    
                    // 初始化Mermaid
                    mermaid.initialize({
                        startOnLoad: true,
                        theme: 'default',
                        securityLevel: 'loose'
                    });
                };
            </script>
        </head>
        <body>
            <div class="mermaid">
                graph TD
                A[预加载] --> B[完成]
            </div>
        </body>
        </html>
        """
        self.mermaid_preview.setHtml(html)
        self.mermaid_preloaded = True
    
    def _preview_mermaid(self):
        """预览Mermaid图表"""
        mermaid_code = self.mermaid_editor.toPlainText()
        logger.info(f"预览Mermaid图表，代码长度: {len(mermaid_code)}")
        
        if not mermaid_code.strip():
            logger.warning("Mermaid代码为空，无法预览")
            return
            
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.2.3/dist/mermaid.min.js"></script>
            <script>
                // 确保mermaid库加载完成后再初始化
                document.addEventListener('DOMContentLoaded', function() {{
                    mermaid.initialize({{
                        startOnLoad: true,
                        theme: 'default',
                        securityLevel: 'loose'
                    }});
                }});
                
                // 使用多种方式确保图表渲染
                window.onload = function() {{
                    setTimeout(function() {{
                        try {{
                            mermaid.run();
                            console.log("Mermaid图表渲染完成");
                            // 通知父窗口渲染完成
                            window.parent.postMessage('mermaid-rendered', '*');
                        }} catch (e) {{
                            console.error("Mermaid渲染错误:", e);
                            document.getElementById('error-message').textContent = "图表渲染错误: " + e.message;
                            document.getElementById('error-message').style.display = 'block';
                        }}
                    }}, 200); // 减少延迟，因为已经预加载了库
                }};
            </script>
            <style>
                #error-message {{
                    display: none;
                    color: red;
                    padding: 10px;
                    border: 1px solid red;
                    margin: 10px 0;
                }}
                .mermaid {{
                    width: 100%;
                }}
            </style>
        </head>
        <body>
            <div id="error-message"></div>
            <div class="mermaid">
{mermaid_code}
            </div>
        </body>
        </html>
        """
        self.mermaid_preview.setHtml(html)
    
    def display_architecture(self, architecture_data: Dict[str, Any]):
        """
        显示架构设计结果
        
        Args:
            architecture_data: 架构设计数据
        """
        try:
            self.architecture_data = architecture_data
            
            # 显示架构概述
            if "architecture_overview" in architecture_data:
                self.overview_tab.setHtml("<h3>架构概述</h3><p>{0}</p>".format(architecture_data['architecture_overview']))
            
            # 显示架构组件
            if "components" in architecture_data:
                components_html = "<h3>架构组件</h3><ul>"
                for component in architecture_data["components"]:
                    name = component.get('name', '')
                    service_type = component.get('service_type', '')
                    description = component.get('description', '')
                    components_html += "<li><b>{0}</b> ({1}): {2}</li>".format(
                        name, service_type, description)
                components_html += "</ul>"
                self.components_tab.setHtml(components_html)
            
            # 显示设计决策
            if "design_decisions" in architecture_data:
                decisions_html = "<h3>设计决策</h3><ul>"
                for decision in architecture_data["design_decisions"]:
                    decisions_html += "<li>{0}</li>".format(decision)
                decisions_html += "</ul>"
                self.decisions_tab.setHtml(decisions_html)
            
            # 显示最佳实践
            if "best_practices" in architecture_data:
                practices_html = "<h3>最佳实践</h3><ul>"
                for practice in architecture_data["best_practices"]:
                    practices_html += "<li>{0}</li>".format(practice)
                practices_html += "</ul>"
                self.practices_tab.setHtml(practices_html)
            
            # 显示原始JSON
            self.json_tab.setText(json.dumps(architecture_data, ensure_ascii=False, indent=2))
            
            # 生成并显示架构图
            if "diagram_description" in architecture_data:
                try:
                    logger.info("开始生成架构图")
                    diagram_path = self.diagram_generator.generate_diagram(architecture_data)
                    self._display_diagram(diagram_path)
                    
                    # 生成并显示Mermaid代码
                    mermaid_code = self.mermaid_generator.generate_diagram(architecture_data)
                    self.mermaid_editor.setText(mermaid_code)
                    self._preview_mermaid()
                except Exception as e:
                    logger.error(f"生成架构图失败: {str(e)}")
                    error_msg = str(e)
                    if "failed to execute" in error_msg and "dot" in error_msg:
                        self._show_graphviz_error()
                    else:
                        self.diagram_image_label.setText(f"生成架构图失败: {error_msg}")
        except Exception as e:
            logger.error(f"显示架构设计时发生错误: {str(e)}")
            self.diagram_image_label.setText(f"显示架构设计时发生错误: {str(e)}")
    
    def _show_graphviz_error(self):
        """显示Graphviz错误提示"""
        error_html = """
        <h3>需要安装Graphviz</h3>
        <p>生成架构图需要Graphviz，但系统未找到Graphviz。请按照以下步骤安装：</p>
        <h4>Windows安装步骤：</h4>
        <ol>
            <li>访问 <a href="https://graphviz.org/download/">https://graphviz.org/download/</a> 下载Windows安装包</li>
            <li>或者使用Chocolatey安装: <code>choco install graphviz</code></li>
            <li>安装完成后，将Graphviz的bin目录添加到系统PATH环境变量</li>
            <li>重启应用程序</li>
        </ol>
        <h4>Linux安装步骤：</h4>
        <ol>
            <li>Ubuntu/Debian: <code>sudo apt-get install graphviz</code></li>
            <li>CentOS/RHEL: <code>sudo yum install graphviz</code></li>
        </ol>
        <h4>macOS安装步骤：</h4>
        <ol>
            <li>使用Homebrew: <code>brew install graphviz</code></li>
        </ol>
        """
        self.diagram_image_label.setText(error_html)
        
        # 显示弹窗提示
        QMessageBox.warning(
            self,
            "需要安装Graphviz",
            "生成架构图需要Graphviz，但系统未找到Graphviz。\n\n"
            "请安装Graphviz并确保其在系统PATH中。\n"
            "Windows用户可以访问 https://graphviz.org/download/ 下载安装。\n\n"
            "安装后请重启应用程序。"
        )
    
    def _display_diagram(self, diagram_path: str):
        """
        显示架构图
        
        Args:
            diagram_path: 架构图文件路径
        """
        if os.path.exists(diagram_path):
            logger.info(f"加载架构图: {diagram_path}")
            pixmap = QPixmap(diagram_path)
            if pixmap.isNull():
                logger.error(f"无法加载图片: {diagram_path}")
                self.diagram_image_label.setText(f"无法加载图片: {diagram_path}")
            else:
                # 保存原始图像
                self.original_pixmap = pixmap
                
                # 默认显示原始大小，以保持文字清晰度
                self.diagram_image = pixmap
                self.current_scale = 1.0
                
                # 获取显示区域大小
                screen_size = self.diagram_tab.size()
                
                # 如果图像太大，适当缩小
                if pixmap.width() > screen_size.width() * 0.9 or pixmap.height() > screen_size.height() * 0.9:
                    # 计算合适的缩放比例，但不要缩放太多以保持文字清晰
                    width_ratio = screen_size.width() * 0.9 / pixmap.width()
                    height_ratio = screen_size.height() * 0.9 / pixmap.height()
                    scale_ratio = max(min(width_ratio, height_ratio), 0.7)  # 不小于70%
                    
                    # 使用高质量缩放
                    scaled_pixmap = pixmap.scaled(
                        int(pixmap.width() * scale_ratio),
                        int(pixmap.height() * scale_ratio),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.diagram_image = scaled_pixmap
                    self.current_scale = scale_ratio
                    self.diagram_image_label.setPixmap(scaled_pixmap)
                else:
                    # 否则使用原始大小
                    self.diagram_image_label.setPixmap(pixmap)
                
                self.diagram_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                logger.info(f"架构图显示成功: {diagram_path}, 缩放比例: {self.current_scale:.2f}")
                
                # 切换到架构图选项卡
                self.tab_widget.setCurrentIndex(2)  # 架构图是第三个选项卡（索引为2）
        else:
            logger.warning(f"架构图文件不存在: {diagram_path}")
            self.diagram_image_label.setText(f"架构图文件不存在: {diagram_path}")
    
    def _zoom_in(self):
        """放大图像"""
        if hasattr(self, 'original_pixmap') and self.original_pixmap is not None:
            self.current_scale *= 1.2
            self._update_scaled_image()
    
    def _zoom_out(self):
        """缩小图像"""
        if hasattr(self, 'original_pixmap') and self.original_pixmap is not None:
            self.current_scale *= 0.8
            self._update_scaled_image()
    
    def _reset_zoom(self):
        """重置缩放"""
        if hasattr(self, 'original_pixmap') and self.original_pixmap is not None:
            self.current_scale = 1.0
            self._update_scaled_image()
    
    def _update_scaled_image(self):
        """更新缩放后的图像"""
        if hasattr(self, 'original_pixmap') and self.original_pixmap is not None:
            # 使用高质量缩放
            scaled_pixmap = self.original_pixmap.scaled(
                int(self.original_pixmap.width() * self.current_scale),
                int(self.original_pixmap.height() * self.current_scale),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation  # 使用平滑变换提高质量
            )
            self.diagram_image = scaled_pixmap
            self.diagram_image_label.setPixmap(scaled_pixmap)
            logger.info(f"图像已缩放，当前比例: {self.current_scale:.2f}")
    
    def has_architecture(self) -> bool:
        """
        检查是否有架构设计数据
        
        Returns:
            bool: 是否有架构设计数据
        """
        return self.architecture_data is not None
    
    def has_diagram(self) -> bool:
        """
        检查是否有架构图
        
        Returns:
            bool: 是否有架构图
        """
        return self.diagram_image is not None
    
    def save_architecture(self, file_path: str):
        """
        保存架构设计到文件
        
        Args:
            file_path: 文件路径
        """
        if not self.architecture_data:
            raise ValueError("没有可保存的架构设计数据")
        
        # 根据文件扩展名决定保存格式
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() == ".json":
            # 保存为JSON格式
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.architecture_data, f, ensure_ascii=False, indent=2)
        elif ext.lower() == ".mmd":
            # 保存为Mermaid格式
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.mermaid_editor.toPlainText())
        else:
            # 默认保存为Markdown格式
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# 架构设计方案\n\n")
                
                # 架构概述
                if "architecture_overview" in self.architecture_data:
                    f.write("## 架构概述\n\n")
                    f.write(f"{self.architecture_data['architecture_overview']}\n\n")
                
                # 架构组件
                if "components" in self.architecture_data:
                    f.write("## 架构组件\n\n")
                    for component in self.architecture_data["components"]:
                        f.write(f"### {component.get('name', '')}\n\n")
                        f.write(f"- **服务类型**: {component.get('service_type', '')}\n")
                        f.write(f"- **描述**: {component.get('description', '')}\n\n")
                
                # 设计决策
                if "design_decisions" in self.architecture_data:
                    f.write("## 设计决策\n\n")
                    for i, decision in enumerate(self.architecture_data["design_decisions"], 1):
                        f.write(f"{i}. {decision}\n")
                    f.write("\n")
                
                # 最佳实践
                if "best_practices" in self.architecture_data:
                    f.write("## 应用的AWS最佳实践\n\n")
                    for i, practice in enumerate(self.architecture_data["best_practices"], 1):
                        f.write(f"{i}. {practice}\n")
                
                # 添加Mermaid图表
                f.write("\n## 架构图\n\n")
                f.write("```mermaid\n")
                f.write(self.mermaid_editor.toPlainText())
                f.write("\n```\n")
        
        logger.info(f"架构设计已保存到: {file_path}")
    
    def export_diagram(self, file_path: str):
        """
        导出架构图
        
        Args:
            file_path: 文件路径
        """
        # 根据文件扩展名决定导出格式
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() == ".mmd":
            # 导出为Mermaid格式
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.mermaid_editor.toPlainText())
            logger.info(f"Mermaid图表已导出到: {file_path}")
        else:
            # 导出为图片格式
            if not self.diagram_image:
                raise ValueError("没有可导出的架构图")
            
            # 保存图片，使用原始图像以保持高分辨率
            if self.original_pixmap:
                self.original_pixmap.save(file_path, quality=100)  # 使用最高质量设置
            else:
                self.diagram_image.save(file_path, quality=100)
            logger.info(f"架构图已导出到: {file_path}")
            
    def _on_mermaid_text_changed(self):
        """处理Mermaid编辑器文本变化事件，实现实时预览"""
        if self.auto_preview:
            # 使用延迟计时器，避免频繁更新
            from PyQt6.QtCore import QTimer
            if hasattr(self, '_preview_timer'):
                self._preview_timer.stop()
            else:
                self._preview_timer = QTimer()
                self._preview_timer.setSingleShot(True)
                self._preview_timer.timeout.connect(self._preview_mermaid)
            
            # 设置500毫秒延迟，减少频繁渲染
            self._preview_timer.start(500)
            
            # 更新状态指示器
            self.preview_status.setText("编辑中...")
            self.preview_status.setStyleSheet("color: orange;")
    
    def _on_preview_load_finished(self, success):
        """处理预览加载完成事件"""
        if success:
            self.preview_status.setText("预览已更新")
            self.preview_status.setStyleSheet("color: green;")
        else:
            self.preview_status.setText("预览加载失败")
            self.preview_status.setStyleSheet("color: red;")
    
    def _toggle_auto_preview(self):
        """切换自动预览状态"""
        self.auto_preview = not self.auto_preview
        self.auto_preview_button.setText(f"自动预览: {'开' if self.auto_preview else '关'}")
        
        if self.auto_preview:
            # 切换到自动预览时立即更新预览
            self._preview_mermaid()
    
    def _parse_mermaid_to_architecture_data(self, mermaid_code):
        """
        从Mermaid代码解析出架构数据
        
        Args:
            mermaid_code: Mermaid代码
            
        Returns:
            Dict: 架构数据
        """
        # 初始化节点和连接
        nodes = []
        connections = []
        
        try:
            # 解析Mermaid代码
            lines = mermaid_code.strip().split('\n')
            logger.info(f"开始解析Mermaid代码，共{len(lines)}行")
            
            # 解析节点
            for line in lines:
                line = line.strip()
                
                # 跳过空行、图表定义行、样式定义行和连接行
                if not line or line.startswith("graph") or line.startswith("classDef") or line.startswith("class") or "-->" in line:
                    continue
                
                # 解析节点定义行
                if "[" in line and "]" in line:
                    # 提取节点ID和内容
                    parts = line.split("[", 1)
                    node_id = parts[0].strip()
                    content = parts[1].split("]")[0]
                    
                    # 处理节点内容，分离名称和类型
                    if "<br/>" in content:
                        name_parts = content.split("<br/>")
                        node_name = name_parts[0].strip()
                        node_type = name_parts[1].strip()
                    else:
                        node_name = content.strip()
                        node_type = "Generic"
                    
                    # 添加节点
                    nodes.append({
                        "id": node_id,
                        "name": node_name,
                        "type": node_type
                    })
                    logger.info(f"解析到节点: ID={node_id}, 名称={node_name}, 类型={node_type}")
                
                # 解析圆柱形节点 [(内容)]
                elif "[(" in line and ")]" in line:
                    parts = line.split("[(", 1)
                    node_id = parts[0].strip()
                    content = parts[1].split(")]")[0]
                    
                    if "<br/>" in content:
                        name_parts = content.split("<br/>")
                        node_name = name_parts[0].strip()
                        node_type = name_parts[1].strip()
                    else:
                        node_name = content.strip()
                        node_type = "Database"
                    
                    nodes.append({
                        "id": node_id,
                        "name": node_name,
                        "type": node_type
                    })
                    logger.info(f"解析到圆柱形节点: ID={node_id}, 名称={node_name}, 类型={node_type}")
            
            # 解析连接
            for line in lines:
                line = line.strip()
                
                # 只处理连接行
                if "-->" in line:
                    parts = line.split("-->")
                    from_id = parts[0].strip()
                    
                    # 处理带标签的连接
                    if "|" in parts[1]:
                        label_parts = parts[1].split("|")
                        label = label_parts[1].strip()
                        to_id = label_parts[2].strip()
                    else:
                        to_id = parts[1].strip()
                        label = ""
                    
                    # 添加连接
                    connections.append({
                        "from": from_id,
                        "to": to_id,
                        "label": label
                    })
                    logger.info(f"解析到连接: {from_id} --> {to_id} (标签: {label})")
            
            # 处理特殊连接目标"all"
            all_connections = []
            for conn in connections:
                if conn["to"] == "all":
                    # 为每个节点创建一个连接
                    for node in nodes:
                        if node["id"] != conn["from"]:  # 避免自连接
                            all_connections.append({
                                "from": conn["from"],
                                "to": node["id"],
                                "label": conn["label"]
                            })
                else:
                    all_connections.append(conn)
            
            connections = all_connections
            
            # 创建并返回架构数据
            return self._create_architecture_data(nodes, connections)
            
        except Exception as e:
            logger.error(f"解析Mermaid代码失败: {str(e)}")
            # 返回一个基本的架构数据结构，避免NoneType错误
            return {
                "architecture_overview": "从Mermaid编辑器生成的架构图 (解析出错)",
                "components": [],
                "diagram_description": {
                    "nodes": [],
                    "connections": []
                }
            }

        
    def _clean_node_id(self, node_id):
        """
        清理节点ID，移除各种形状的括号和其他字符
        
        Args:
            node_id: 原始节点ID
            
        Returns:
            str: 清理后的节点ID
        """
        # 移除各种括号和空格
        for char in ["[", "]", "(", ")", "{", "}", ">", " "]:
            if char in node_id:
                node_id = node_id.split(char)[0]
        
        # 记录清理过程
        logger.debug(f"清理节点ID: 原始={node_id} -> 清理后={node_id.strip()}")
        return node_id.strip()
        
    def _create_architecture_data(self, nodes, connections):
        """
        创建架构数据结构
        
        Args:
            nodes: 节点列表
            connections: 连接列表
            
        Returns:
            Dict: 架构数据
        """
        # 创建架构数据
        architecture_data = {
            "architecture_overview": "从Mermaid编辑器生成的架构图",
            "components": [],
            "diagram_description": {
                "nodes": nodes,
                "connections": connections
            }
        }
        
        # 从节点生成组件列表
        for node in nodes:
            architecture_data["components"].append({
                "name": node["name"],
                "service_type": node["type"],
                "description": f"从Mermaid图表生成的{node['name']}组件"
            })
        
        return architecture_data
    
    def _generate_diagram_from_mermaid(self):
        """从Mermaid代码生成架构图并显示在图表选项卡中"""
        mermaid_code = self.mermaid_editor.toPlainText()
        if not mermaid_code.strip():
            logger.warning("Mermaid代码为空，无法生成图表")
            return
        
        try:
            # 显示生成中的提示
            self.diagram_image_label.setText("正在从Mermaid代码生成架构图...")
            
            # 解析Mermaid代码生成架构数据
            architecture_data = self._parse_mermaid_to_architecture_data(mermaid_code)
            if not architecture_data:
                raise ValueError("解析Mermaid代码失败，无法生成架构数据")
            
            # 记录生成的数据结构，便于调试
            nodes_count = len(architecture_data.get('diagram_description', {}).get('nodes', []))
            connections_count = len(architecture_data.get('diagram_description', {}).get('connections', []))
            logger.info(f"从Mermaid生成的架构数据: 节点数={nodes_count}, 连接数={connections_count}")
            
            # 使用架构数据更新UI
            self.architecture_data = architecture_data
            
            # 显示架构概述
            self.overview_tab.setHtml("<h3>架构概述</h3><p>{0}</p>".format(
                architecture_data['architecture_overview']))
            
            # 显示架构组件
            components_html = "<h3>架构组件</h3><ul>"
            for component in architecture_data["components"]:
                name = component.get('name', '')
                service_type = component.get('service_type', '')
                description = component.get('description', '')
                components_html += "<li><b>{0}</b> ({1}): {2}</li>".format(
                    name, service_type, description)
            components_html += "</ul>"
            self.components_tab.setHtml(components_html)
            
            # 显示原始JSON
            self.json_tab.setText(json.dumps(architecture_data, ensure_ascii=False, indent=2))
            
            # 生成并显示架构图
            try:
                logger.info("开始生成架构图")
                diagram_path = self.diagram_generator.generate_diagram(architecture_data)
                self._display_diagram(diagram_path)
                
                # 添加成功消息
                QMessageBox.information(
                    self,
                    "生成成功",
                    "已成功从Mermaid代码生成架构图并更新所有相关面板。"
                )
                
                # 切换到架构图选项卡
                self.tab_widget.setCurrentIndex(2)  # 架构图是第三个选项卡（索引为2）
            except Exception as e:
                logger.error(f"生成架构图失败: {str(e)}")
                self.diagram_image_label.setText(f"生成架构图失败: {str(e)}")
                QMessageBox.warning(
                    self,
                    "生成图片失败",
                    f"生成架构图失败: {str(e)}\n\n请检查Graphviz是否正确安装。"
                )
            
        except Exception as e:
            logger.error(f"从Mermaid代码生成图表失败: {str(e)}")
            self.diagram_image_label.setText(f"生成图表失败: {str(e)}")
            QMessageBox.critical(
                self,
                "解析失败",
                f"从Mermaid代码解析架构数据失败: {str(e)}\n\n请检查Mermaid代码格式是否正确。"
            )
    
    def clear_mermaid(self):
        """清空Mermaid编辑器和预览"""
        if hasattr(self, 'mermaid_editor'):
            self.mermaid_editor.clear()
        
        if hasattr(self, 'mermaid_preview'):
            # 清空预览，显示空白页面
            self.mermaid_preview.setHtml("<html><body><p>尚未生成架构图</p></body></html>")
            
    def resizeEvent(self, event):
        """处理窗口大小变化事件，更新分割器大小"""
        super().resizeEvent(event)
        # 如果存在mermaid分割器，保持其比例
        if hasattr(self, 'mermaid_splitter'):
            # 获取当前总高度
            total_height = self.mermaid_tab.height()
            # 保持编辑区和预览区的比例约为40:60
            self.mermaid_splitter.setSizes([int(total_height * 0.4), int(total_height * 0.6)])