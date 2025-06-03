#!/bin/bash

# 设置环境变量
echo "设置环境变量..."
export USER="s7f9z7t6b78d4"
export PASSWORD="s1h5b5k8x6s5f2sv34"

# 检查make命令是否存在
if ! command -v make &> /dev/null
then
    echo "错误：make命令未找到，请先安装make"
    exit 1
fi

# 执行make setup
echo "执行make setup..."
make setup
if [ $? -ne 0 ]; then
    echo "错误：make setup失败"
    exit 1
fi

# 执行make init
echo "执行make init..."
make init

# 使用runall目标代替run
echo "执行make runall..."
make runall
if [ $? -ne 0 ]; then
    echo "错误：make runall失败"
    exit 1
fi

echo "所有命令执行成功完成！"