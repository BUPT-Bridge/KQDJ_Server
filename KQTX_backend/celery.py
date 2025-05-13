import os
from celery import Celery

# 设置默认的Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KQTX_backend.settings')

# 创建celery实例
app = Celery('KQTX_backend')

# 使用Django的settings文件配置celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从已注册的app中加载任务
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')