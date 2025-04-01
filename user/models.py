from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
import time
import os
from .utils.constance import *
from .utils.rename import avatar_upload_path
from .manager import UsersManager

GLOABL_AVATAR_WIDTH = 120
GLOABL_AVATAR_HEIGHT = 120

# Create your models here.
class Users(models.Model):
    objects = models.Manager()
    query_manager = UsersManager()

    openid = models.CharField(max_length=100, unique=True, verbose_name='微信OpenID')
    username = models.CharField(max_length=50, verbose_name='用户名', blank=True, null=True)
    password = models.CharField(max_length=50, verbose_name='密码', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='手机号', blank=True, null=True)
    avatar = ProcessedImageField(upload_to=avatar_upload_path,
                                           processors=[ResizeToFill(GLOABL_AVATAR_WIDTH, GLOABL_AVATAR_HEIGHT)],
                                           format='WEBP',
                                           options={'quality': 100}, blank=True, null=True,
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