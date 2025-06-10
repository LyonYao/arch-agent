# 项目结构

```
architect_agent/
├── main.py                  # 应用程序入口点
├── requirements.txt         # 项目依赖
├── .env.example             # 环境变量示例文件
├── README.md                # 项目说明文档
├── agent-design.md          # 架构设计文档
├── src/                     # 源代码目录
│   ├── __init__.py
│   ├── api/                 # API相关模块
│   │   ├── __init__.py
│   │   └── qianwen_api.py   # 千问API调用模块
│   ├── ui/                  # 用户界面模块
│   │   ├── __init__.py
│   │   ├── main_window.py   # 主窗口
│   │   ├── input_panel.py   # 输入面板
│   │   └── output_panel.py  # 输出面板
│   ├── core/                # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── requirement_analyzer.py  # 需求分析模块
│   │   ├── architecture_generator.py  # 架构生成模块
│   │   └── aws_best_practices.py  # AWS最佳实践模块
│   ├── diagram/             # 图表生成模块
│   │   ├── __init__.py
│   │   └── diagram_generator.py  # 图表生成器
│   └── utils/               # 工具函数
│       ├── __init__.py
│       └── config.py        # 配置管理
└── resources/               # 资源文件
    ├── aws_patterns/        # AWS架构模式
    ├── icons/               # 图标资源
    └── templates/           # 模板文件
```