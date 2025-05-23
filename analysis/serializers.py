from rest_framework import serializers
from .models import FormUserRelation
import re

class ImportantUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormUserRelation
        fields = 'serial_number', 'username', 'create_at', 'Latitude_Longitude'


class EventsSerializer(serializers.ModelSerializer):
    solution_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = FormUserRelation
        fields = ('category', 'solution_summary')
    
    def get_solution_summary(self, obj):
        """提取解决方案摘要部分"""
        if not obj.solution_suggestion:
            return ""
        
        # 使用正则表达式提取【解决方案摘要】下面的内容，到下一个【标题】前
        pattern = r'【解决方案摘要】\s*(.*?)(?=\s*【|\s*$)'
        match = re.search(pattern, obj.solution_suggestion, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return ""
    
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormUserRelation
        fields = ('username', 'serial_number', 'avatar', 'address')

class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormUserRelation
        fields = ('avatar', 'Latitude_Longitude')