from rest_framework import serializers

class QASerializer(serializers.Serializer):
    question = serializers.CharField(max_length=500)
    answer = serializers.CharField(max_length=2000)
    image_url = serializers.CharField(max_length=500)

class BeautyArticleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField(max_length=5000)
    image_url = serializers.CharField(max_length=500)

class BeautyQuerySerializer(serializers.Serializer):
    keyword = serializers.CharField(max_length=100)
    articles = BeautyArticleSerializer(many=True) 