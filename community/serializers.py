from rest_framework import serializers
from .models import Banners, Notice, Cover, PageView, PhoneNumber, TweetPage
"""
本文件是用于创建序列化器的文件，在序列化器中，可以：
1.定义序列化器类
2.定义序列化器字段
3.定义序列化器方法
"""
class CoverSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cover
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banners
        fields = '__all__'

class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = '__all__'

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetPage
        fields = '__all__'