"""
本文件是用于创建模型文件的管理器，在管理器中，可以：
1.定义自定义查询方法
2.修改默认的查询集
3.添加表级操作方法
4.添加统计方法
"""

import os
from django.db import models
from django.conf import settings

class BannerManager(models.Manager):

    def get_banners(self):
        """使用 BannerSerializer 序列化查询集"""
        from .serializers import BannerSerializer
        banners = self.get_queryset().all()
        if not banners:
            raise ValueError("No banners found")
        return {'data':BannerSerializer(banners, many=True).data,
                'message':"获取成功"}

    def create_banner(self, request) -> dict:
        """
        创建新的Banner
        
        Args:
            request: HTTP请求对象，包含上传的Banner图片
            
        Returns:
            dict: 包含创建结果的信息
        """
        banner_image = request.FILES.get('banner')
        if not banner_image:
            raise ValueError("没有提供Banner图片")
        
        # 检查数量限制
        if self.count() >= 8:
            raise ValueError("Banner图片数量已达到上限（8张）")
            
        new_banner = self.create(banner_image=banner_image)
        from .serializers import BannerSerializer
        return {
            "data": BannerSerializer(new_banner).data,
            "message": "Banner添加成功"
        }

    def delete_banner(self, pk: int) -> dict:
        """
        删除指定Banner记录及其对应的图片文件

        Args:
            pk: Banner记录的主键

        Returns:
            dict: 包含删除结果的信息
        """
        obj = self.get(pk=pk)
        # 获取图片文件的相对路径
        if obj.banner_image:
            file_path = os.path.join(settings.MEDIA_ROOT, str(obj.banner_image))
            if os.path.exists(file_path):
                os.remove(file_path)
        obj.delete()
        return {"message": "Banner删除成功"}


class CoverManager(models.Manager):

    def get_cover(self):
        """获取并序列化第一个封面"""
        from .serializers import CoverSerializer

        first_cover = self.get_queryset().first()
        if first_cover:
            return CoverSerializer(first_cover).data
        raise ValueError("No cover found")


class PhoneNumberManager(models.Manager):

    def get_phone_number(self):
        """获取并序列化第一个电话号码"""
        first_phone_number = self.get_queryset().all()
        from .serializers import PhoneNumberSerializer

        if first_phone_number:
            return PhoneNumberSerializer(first_phone_number, many=True).data
        raise ValueError("No phone number found")

    def update_phone_number(
        self, phone_name: str, phone_number: str, pk: int = None
    ) -> dict:
        """
        更新或创建手机号

        Args:
            phone_name: 姓名
            phone_number: 手机号
            pk: 主键，默认为None表示创建新记录
        Returns:
            dict: 包含更新结果的信息
        """
        from .serializers import PhoneNumberSerializer
        if pk:
            # 更新已存在记录
            self.filter(pk=pk).update(
                phone_name=phone_name,
                phone_number=phone_number
            )
            obj = self.get(pk=pk)
            message = "手机号更新成功"
        else:
            # 创建新记录
            obj = self.create(phone_name=phone_name, phone_number=phone_number)
            message = "手机号创建成功"

        return PhoneNumberSerializer(obj).data

    def delete_phone_number(self, pk: int) -> dict:
        """
        删除指定手机号记录

        Args:
            phone_number: 要删除的手机号

        Returns:
            dict: 包含删除结果的信息
        """
        obj = self.get(pk=pk)
        obj.delete()
        return {"message": "手机号删除成功"}