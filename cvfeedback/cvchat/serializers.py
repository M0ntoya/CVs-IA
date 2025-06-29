from rest_framework import serializers
from .models import UploadedCV

class UploadedCVSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedCV
        fields = ['id', 'file', 'uploaded_at']

    def create(self, validated_data):
        user = self.context['request'].user
        return UploadedCV.objects.create(user=user, **validated_data)
