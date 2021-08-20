from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import models
from .serializers import *


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
        try:
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        except models.TelegramAccount.DoesNotExist:
            return Response("NO USER", status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def user_view(request):
    if request.method == 'GET':
        serialized_users = UserSerializer(User.objects.all(), many=True)
        return Response(serialized_users.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def task_view(request):

    if request.method == 'GET':
        serialized_task = TaskSerializer( models.Task.objects.all(), many=True)
        return Response(serialized_task.data)

    if request.method == 'POST':
        print(request.data)

        serializer = TaskSerializer(data=request.data)
        
        if serializer.is_valid():
            task:models.Task = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_tasks_view(request, telegram_id, creator=True):
    try:
        user = models.TelegramAccount.objects.get(telegram_id=telegram_id).user
    except models.TelegramAccount.DoesNotExist:
        return Response(status=404)

    if request.method == "GET":
        tasks = []

        if creator:
            tasks = user.created_tasks.filter(done=False)
        else:
            tasks = user.worked_tasks.filter(done=False)

        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

def user_creator_tasks_view(request, telegram_id):
    return user_tasks_view(request, telegram_id, creator=True)

def user_worker_tasks_view(request, telegram_id):
    return user_tasks_view(request, telegram_id, creator=False)

@api_view(['GET', 'POST'])
def task_comments(request, pk):
    try:
        task = models.Task.objects.get(pk=pk)
    except models.Task.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        comments = []

        if task.comments:
            comments = task.comments.all()

        serialized_comments = CommentSerializer(comments, many=True)
        return Response(serialized_comments.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer_comment = CommentSerializer(data={**request.data, "task": TaskSerializer(task).data}  )

        if serializer_comment.is_valid():
            serializer_comment.save()

            return Response(serializer_comment.data, status=status.HTTP_201_CREATED)