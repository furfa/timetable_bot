from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import models

class UserSerializer(serializers.ModelSerializer):
    telegram_id = serializers.IntegerField(source='telegram_account.telegram_id', read_only=True)
    class Meta:
        model = User
        

class TaskSerializer(serializers.ModelSerializer):
    creator_telegram_id = serializers.IntegerField(source='creator.telegram_account.telegram_id', read_only=True)
    worker_telegram_id  = serializers.IntegerField(source='worker.telegram_account.telegram_id', read_only=True)
    class Meta:
        model = models.Task
        fields = ["pk", "description", "creation_date", "deadline", "done", "creator_telegram_id", "worker_telegram_id"]

    def create(self, validated_data):
        task: models.Task = super().create(validated_data)
        print(validated_data)

        task.creator = get_object_or_404( models.TelegramAccount, telegram_id=validated_data.get("creator_telegram_id") ).user
        task.worker =  get_object_or_404( models.TelegramAccount, telegram_id=validated_data.get("worker_telegram_id") ).user

        return task
        



@api_view(['GET', 'DELETE', 'PUT'])
def task_detail_view(request, pk:int):

    try:
        task = models.Task.objects.get(pk=pk)
    except models.Task.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serialized_task = TaskSerializer(task, many=False)
        print(request.GET)
        return Response(serialized_task.data)
    
    if request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data, partial=True)
        
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def task_view(request):

    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    