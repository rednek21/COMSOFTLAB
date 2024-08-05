from rest_framework import serializers

from .models import EmailMessage, File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class EmailMessageSerializer(serializers.ModelSerializer):
    attachments = FileSerializer(many=True, read_only=True)

    class Meta:
        model = EmailMessage
        fields = '__all__'
