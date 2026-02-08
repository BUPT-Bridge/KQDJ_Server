import time

# 时间戳为 Unix 时间戳，单位为秒
def set_timestamp(instance, field_name='upload_time'):
    """为模型实例设置时间戳"""
    if not instance.pk and not getattr(instance, field_name, None):
        setattr(instance, field_name, int(time.time()))

def format_datetime(dt: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间"""
    pass
