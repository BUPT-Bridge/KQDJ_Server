from rest_framework import serializers
from .models import MainForm

class MainFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainForm
        fields = '__all__'
