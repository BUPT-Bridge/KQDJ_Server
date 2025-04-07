from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from .manager import BannerManager, CoverManager, PhoneNumberManager, TweetPageManager
from .utils.rename import cover_upload_path, banner_upload_path
from .utils.constance import *


class Banners(models.Model):
    objects = models.Manager()
    query_manager = BannerManager()
    
    """轮播图模型"""
    banner_image = ProcessedImageField(upload_to=banner_upload_path,
                                           processors=[ResizeToFill(BANNER_WIDTH, BANNER_HEIGHT)],
                                           format='WEBP',
                                           options={'quality': 100}, blank=True, null=True,
                                           verbose_name='轮播图')
    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = '轮播图'

    def __str__(self):
        return self.banner_image.url if self.banner_image else 'No Cover Image'


class Notice(models.Model):
    """温馨提示模型"""
    content = models.TextField(verbose_name='内容', blank=True, null=True)

    class Meta:
        verbose_name = '温馨提示'
        verbose_name_plural = '温馨提示'

    def __str__(self):
        return self.content[:20]

class Cover(models.Model):
    objects = models.Manager()
    query_manager = CoverManager()
    
    """封面图模型"""
    cover_image = ProcessedImageField(upload_to=cover_upload_path,
                                           processors=[ResizeToFill(COVER_WIDTH, COVER_HEIGHT)],
                                           format='WEBP',
                                           options={'quality': 100}, blank=True, null=True,
                                           verbose_name='封面图')

    @classmethod
    def update_cover(cls, new_image):
        """更新封面图片
        
        Args:
            new_image: 新的图片文件
            
        Returns:
            json格式
        """
        old_cover = cls.objects.first()
        if old_cover and old_cover.cover_image:
            old_cover.cover_image.delete(save=False)  # 删除文件
            old_cover.delete()  # 删除记录
        new_cover = cls.objects.create(cover_image=new_image)
        from .serializers import CoverSerializer
        return {"cover": CoverSerializer(new_cover).data, "message": "封面更新成功"}   

    class Meta:
        verbose_name = '封面图'
        verbose_name_plural = '封面图'

    def __str__(self):
        return self.cover_image.url if self.cover_image else 'No Cover Image'
    

class PageView(models.Model):
    view_count = models.IntegerField(default=0, verbose_name='访问量')

    class Meta:
        verbose_name = '页面访问量'
        verbose_name_plural = '页面访问量'

    def __str__(self):
        return self.page
    
class PhoneNumber(models.Model):
    objects = models.Manager()
    query_manager = PhoneNumberManager()
    
    """手机号模型"""
    phone_name = models.CharField(max_length=20, unique=True, verbose_name='姓名')
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='手机号')
    
    class Meta:
        verbose_name = '手机号'
        verbose_name_plural = '手机号'

    def __str__(self):
        return self.phone_number

class TweetPage(models.Model):
    # 社区风采模型
    objects = models.Manager()
    query_manager = TweetPageManager()


    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')

    class Meta:
        verbose_name = '社区风采'
        verbose_name_plural = '社区风采'

    def __str__(self):
        return self.title