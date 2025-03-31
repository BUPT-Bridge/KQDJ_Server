from .models import Users
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'permission_level': {'write_only': True},  # 权限等级只读
        }
