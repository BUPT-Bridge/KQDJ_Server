import time

# 时间戳为 Unix 时间戳，单位为秒
def set_timestamp(instance):
    if not instance.pk and not instance.upload_time:
        instance.upload_time = int(time.time())

def format_datetime(dt: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间"""
    pass
