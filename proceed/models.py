from django.db import models
import time
from datetime import datetime

# Create your models here.
class MainForm(models.Model):
    time_unix = models.BigIntegerField(verbose_name='时间')
    uuid = models.UUIDField(verbose_name='Form-UUID')

    # User 相关字段
    openid = models.CharField(max_length=100, verbose_name='用户OpenID')
    phone = models.CharField(max_length=20, verbose_name='电话号码')
    name = models.CharField(max_length=50, verbose_name='姓名')
    address = models.TextField(verbose_name='地址')
    content = models.TextField(verbose_name='内容')
    feedback_need = models.BooleanField(default=False, verbose_name='是否需要回访')
    audio = models.FileField(upload_to='audios/', null=True, blank=True, verbose_name='音频文件')
    
    # Admin 相关字段
    admin_openid = models.CharField(max_length=100, null=True, blank=True, verbose_name='管理员OpenID')
    admin_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='管理员电话')
    admin_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='管理员姓名')
    admin_way = models.CharField(max_length=50, null=True, blank=True, verbose_name='处理方式')
    admin_content = models.TextField(null=True, blank=True, verbose_name='管理员处理内容')
    feedback_summary = models.TextField(null=True, blank=True, verbose_name='回访总结')
    
    # State 相关字段
    HANDLE_STATUS_CHOICES = [
        (0, '未处理'),
        (1, '处理中'),
        (2, '已处理'),
    ]
    handle = models.IntegerField(choices=HANDLE_STATUS_CHOICES, default=0, verbose_name='处理状态')
    feedback_or_not = models.BooleanField(default=False, verbose_name='是否已回访')
    evaluation = models.IntegerField(null=True, blank=True, verbose_name='评价分数')

    def save(self, *args, **kwargs):
        # 如果是新建对象且还没有设置时间戳
        if not self.pk and not self.time_unix:  # 注意这里修改为time_unix
            # 使用当前时间的 Unix 时间戳（秒）
            self.time_unix = int(time.time())
        super().save(*args, **kwargs)
    
    # 添加辅助方法，将 Unix 时间戳转换回 datetime 对象
    def get_datetime(self):
        return datetime.fromtimestamp(self.time_unix)
    class Meta:
        verbose_name = '表单'
        verbose_name_plural = '表单'
    
    def __str__(self):
        return f"表单 {self.uuid} - {self.name} - {self.get_handle_display()}"