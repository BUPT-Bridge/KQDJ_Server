.PHONY: init run clean setup cleanall migrate env
.DEFAULT_GOAL := run

init: env
	@if [ -z "$$USER" ]; then echo "错误：必须设置 USER 环境变量" && exit 1; fi
	@if [ -z "$$PASSWORD" ]; then echo "错误：必须设置 PASSWORD 环境变量" && exit 1; fi
	@echo "✅ 环境变量 USER 和 PASSWORD 已设置"

	@echo "删除迁移文件..."
	@find ./user ./proceed ./community ./analysis -path "*/migrations/*.py" -not -name "__init__.py" -delete
	@find ./user ./proceed ./community ./analysis -path "*/migrations/*.pyc" -delete
	@echo "✅ 迁移文件已删除"

	@echo "执行数据库迁移..."
	python manage.py makemigrations user proceed community analysis
	python manage.py migrate
	@echo "✅ 数据库迁移成功"

	@echo "创建超级用户..."
	@export DJANGO_SUPERUSER_PASSWORD="$$PASSWORD" && \
	python manage.py createsuperuser --noinput --username "$$USER" --email "$$USER@localhost"
	@echo "✅ 超级用户创建成功"

run: migrate
	python manage.py runserver 0.0.0.0:8051

clean:
	@echo "清理迁移文件..."
	@find ./user ./proceed ./community ./analysis -path "*/migrations/*.py" -not -name "__init__.py" -delete
	@find ./user ./proceed ./community ./analysis -path "*/migrations/*.pyc" -delete
	@echo "清理pycache..."
	@find ./user ./proceed ./community ./analysis -name "__pycache__" -type d -exec rm -rf {} \; 2>/dev/null || true
	@find ./user ./proceed ./community ./analysis -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ 清理完成"

cleanall: clean
	@echo "清理数据库..."
	@rm -rf db.sqlite3
	@echo "✅ 清理完成"

setup: env
	pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
	@echo "✅ 依赖安装完成"

migrate: env
	@echo "执行数据库迁移..."
	python manage.py makemigrations user proceed community analysis
	python manage.py migrate
	@echo "✅ 数据库迁移成功"

env:
	@echo "正在加载环境变量..."
	@if [ ! -f .env ]; then echo "错误：.env 文件不存在"; exit 1; fi
	@echo "当前环境变量值："
	@(cat .env; echo) | while IFS='=' read -r key value; do if [ -n "$$key" ]; then echo "$$key=$$value"; export "$$key=$$value"; fi done
	@echo "✅ 环境变量加载成功"