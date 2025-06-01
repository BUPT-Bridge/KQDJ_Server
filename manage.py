#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def load_env():
    """加载环境变量"""
    try:
        # 确保utils.env_loader在PYTHONPATH中可用
        project_path = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_path)
        
        # 加载环境变量
        from utils.env_loader import env_vars
        print("环境变量已加载")
    except Exception as e:
        print(f"加载环境变量时出错: {e}")
        raise

def main():
    """Run administrative tasks."""
    load_env()  # 加载环境变量
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KQTX_backend.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
