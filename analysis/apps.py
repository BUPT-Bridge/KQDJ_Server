from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analysis'
    
    def ready(self):
        """
        应用启动时执行的操作
        在这里导入信号处理器，确保它们被注册
        """
        import analysis.signals  # 导入信号处理器模块
        
        # 只在主进程中启动定时任务，避免在Django多进程环境中重复启动
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            # 启动定时任务
            from analysis.tasks import start_periodic_tasks
            start_periodic_tasks()
