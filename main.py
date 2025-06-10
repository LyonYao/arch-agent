#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
架构设计Agent主程序入口
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# 确保src目录在Python路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用程序主窗口
from src.ui.main_window import MainWindow

def main():
    """主函数，启动应用程序"""
    app = QApplication(sys.argv)
    app.setApplicationName("架构设计Agent")
    
    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                           "resources", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()