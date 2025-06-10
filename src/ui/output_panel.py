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
                           QTextEdit, QTabWidget, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from src.diagram.diagram_generator import DiagramGenerator

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        
        # 创建UI组件
        self._create_ui()
    
    def _create_ui(self):
        """创建UI组件"""
        # 导入所需的组件
        from PyQt6.QtWidgets import QHBoxLayout, QPushButton
        
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
        self.json_tab.setFont(QLabel().font())  # 使用等宽字体
        self.tab_widget.addTab(self.json_tab, "原始JSON")
        
        # 将选项卡控件添加到主布局
        main_layout.addWidget(self.tab_widget)
    
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
                self.diagram_image = pixmap
                self.original_pixmap = pixmap  # 保存原始图像
                self.current_scale = 1.0  # 当前缩放比例
                
                # 显示图像
                self.diagram_image_label.setPixmap(pixmap)
                self.diagram_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                logger.info(f"架构图显示成功: {diagram_path}")
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
            scaled_pixmap = self.original_pixmap.scaled(
                int(self.original_pixmap.width() * self.current_scale),
                int(self.original_pixmap.height() * self.current_scale),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.diagram_image = scaled_pixmap
            self.diagram_image_label.setPixmap(scaled_pixmap)
    
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
        
        logger.info(f"架构设计已保存到: {file_path}")
    
    def export_diagram(self, file_path: str):
        """
        导出架构图
        
        Args:
            file_path: 文件路径
        """
        if not self.diagram_image:
            raise ValueError("没有可导出的架构图")
        
        # 保存图片
        self.diagram_image.save(file_path)
        logger.info(f"架构图已导出到: {file_path}")