from rest_framework import serializers
from .models import FormUserRelation

class ImportantUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormUserRelation
        fields = 'serial_number', 'username', 'create_at', 'Latitude_Longitude'


class EventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormUserRelation
        fields = 'serial_number', 'title', 'category', 'solution'