from rest_framework import serializers
from .models import MainForm, ImageModel, HandleImageModel, Order
from .utils.handle_timestamp import timestamp_to_beijing_str
"""
本文件是用于创建序列化器的文件，在序列化器中，可以：
1.定义序列化器类
2.定义序列化器字段
3.定义序列化器方法
"""
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['image', 'source', 'upload_time']

class HandleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HandleImageModel
        fields = ['image', 'upload_time']

class MainFormSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)  # 通过related_name获取关联图片
    handle_images = HandleImageSerializer(many=True, read_only=True)  # 通过related_name获取处理反馈图片

    class Meta:
        model = MainForm
        fields = '__all__'

class MainFormSerializerSimple(serializers.ModelSerializer):

    class Meta:
        model = MainForm
        fields = ['uuidx', 'type', 'title', 'upload_time', 'serial_number']


class OrderSerializer(serializers.ModelSerializer):
    dispatch_time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'serial_number', 'title', 'dispatch_time', 'dispatch_time_formatted', 'dispatch_openid', 'main_form']
    
    def get_dispatch_time_formatted(self, obj):
        """将时间戳转换为格式化字符串"""
        return timestamp_to_beijing_str(obj.dispatch_time, format="%Y年%m月%d日 %H:%M")