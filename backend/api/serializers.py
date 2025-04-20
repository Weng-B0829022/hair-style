from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=200)

class QASerializer(serializers.Serializer):
    question = serializers.CharField(max_length=500)
    answer = serializers.CharField(max_length=2000)
    image_url = serializers.CharField(max_length=500) 