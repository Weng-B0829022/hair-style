from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MessageSerializer, QASerializer
from .services import process_qa

# Create your views here.

@api_view(['GET'])
def hello_world(request):
    serializer = MessageSerializer(data={'message': 'Hello from Django!'})
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data)

@api_view(['POST'])
def ask_question(request):
    try:
        question = request.data.get('question')
        if not question:
            return Response({'error': 'Question is required'}, status=400)
        
        result = process_qa(question)
        serializer = QASerializer(data=result)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
