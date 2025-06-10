#!/bin/bash
echo "正在创建虚拟环境..."
python3 -m venv venv
echo "正在激活虚拟环境..."
source venv/bin/activate
echo "正在安装依赖..."
pip install -r requirements.txt
echo "正在配置环境..."
cp .env.example .env
echo "请编辑.env文件，填入你的阿里千问API密钥"
echo "安装完成！使用 'python main.py' 启动应用"