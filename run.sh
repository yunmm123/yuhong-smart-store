#!/bin/bash
# 雨虹渠道智慧运营助手 - 启动脚本

echo "========================================"
echo "  雨虹渠道智慧运营助手"
echo "  东方雨虹渠道智慧运营解决方案"
echo "========================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3.9+"
    exit 1
fi

# 安装依赖
echo "正在安装依赖..."
pip3 install -r requirements.txt -q

# 启动应用
echo "启动应用..."
echo "访问地址: http://localhost:5000"
python3 src/app.py
