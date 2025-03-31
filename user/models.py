from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from .utils.constance import *

GLOABL_AVATAR_WIDTH = 60
GLOABL_AVATAR_HEIGHT = 60

# Create your models here.
class Users(models.Model):
    # Django 会自动创建 id 字段作为主键，所以不需要显式定义
    openid = models.CharField(max_length=100, unique=True, verbose_name='微信OpenID')
    username = models.CharField(max_length=50, verbose_name='用户名', blank=True, null=True)
    password = models.CharField(max_length=50, verbose_name='密码', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='手机号', blank=True, null=True)
    avatar = ProcessedImageField(upload_to='picture/avatars',
                                           processors=[ResizeToFill(GLOABL_AVATAR_WIDTH, GLOABL_AVATAR_HEIGHT)],
                                           format='WEBP',
                                           options={'quality': 60}, blank=True, null=True,
                                           verbose_name='头像')
    permission_level = models.IntegerField(
        choices=PERMISSION_CHOICES, default=COMMON_USER, 
        verbose_name='权限等级')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.username} (权限: {self.get_permission_level_display()})"