# 架构设计Agent

基于阿里千问AI的AWS架构设计助手，能够根据用户需求自动生成AWS架构设计方案。

## 功能特点

- 使用大语言模型生成架构设计
- 支持多次交互调整架构设计
- 会话管理，保存历史设计方案
- 生成可视化架构图
- 提供AWS最佳实践建议
- 支持导出架构设计文档和图表

## 系统要求

- Python 3.8+
- 阿里千问API密钥/Gemini AI API Key
- Graphviz (用于生成架构图)

## 安装步骤

1. 克隆仓库
```
git clone https://github.com/yourusername/architect_agent.git
cd architect_agent
```

2. 安装依赖
```
pip install -r requirements.txt
```

3. 安装Graphviz
   - Windows: 从[Graphviz官网](https://graphviz.org/download/)下载安装，并将bin目录添加到PATH
   - macOS: `brew install graphviz`
   - Linux: `sudo apt-get install graphviz` 或 `sudo yum install graphviz`

4. 配置API密钥
   - 创建`.env`文件，添加以下内容：
   ```
   QIANWEN_API_KEY=your_api_key_here
   ```

## 使用方法

1. 启动应用程序
```
python main.py
```

2. 在输入面板中输入系统需求，或选择预设模板
3. 点击"生成架构设计"按钮
4. 查看生成的架构设计和架构图
5. 可以继续输入新的需求，点击"调整架构"按钮进行迭代优化
6. 使用工具栏的"保存架构"和"导出图表"按钮保存结果

## 会话管理

- 点击"新建会话"创建新的架构设计会话
- 在左侧会话面板中选择历史会话
- 右键点击会话可以重命名或删除会话

## 项目结构

```
architect_agent/
├── resources/           # 资源文件
│   ├── aws_patterns/    # AWS架构模式
│   ├── icons/           # 图标
│   └── templates/       # 模板
├── src/                 # 源代码
│   ├── api/             # API调用
│   ├── core/            # 核心逻辑
│   ├── diagram/         # 图表生成
│   ├── ui/              # 用户界面
│   └── utils/           # 工具函数
├── .env                 # 环境变量
├── main.py              # 主程序入口
└── requirements.txt     # 依赖列表
```

## 许可证

MIT License