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

app.conf.update(
    task_routes={
        'analysis.tasks.analyze_form_content_async': {'queue': 'analysis'},
        'analysis.tasks.generate_solution_suggestion_async': {'queue': 'analysis'},
        'analysis.tasks.create_form_user_relation_async': {'queue': 'default'},
    },
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=5,
    task_max_retries=3
)