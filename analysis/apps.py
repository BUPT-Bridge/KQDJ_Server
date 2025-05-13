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
