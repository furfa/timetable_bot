from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.utils.timezone import now
from django.db.models import Q

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from loguru import logger

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
        except User.DoesNotExist:
            return Response("NO USER", status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserView(generics.ListAPIView, generics.CreateAPIView):
    serializer_class = UserSerializer
    def get_queryset(self):
        return User.objects.all()


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
        user = User.objects.get(id=telegram_id)
    except User.DoesNotExist:
        return Response(status=404)

    if request.method == "GET":
        tasks = []

        if creator:
            tasks = user.created_tasks.filter(Q(status=0) | Q(status=1))
        else:
            tasks = user.worked_tasks.filter(status=0)

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
        serializer_comment = CommentSerializer(data=request.data)

        if serializer_comment.is_valid():
            serializer_comment.save(task_object=task)

            pprint(serializer_comment.data)

            return Response(serializer_comment.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

class TasksToNotifyList(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self) -> QuerySet[models.Task]:

        date_now = now()

        if date_now.hour < 7: # Хардкод времени после которого уведомлять
            return []
        
        return models.Task.objects.filter(
            Q(
                status = 0
            ) & ~Q(
                last_notify_time__year = date_now.year,
                last_notify_time__month = date_now.month,
                last_notify_time__day = date_now.day
            )
        )


class TaskMarkNotifyed(generics.RetrieveAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return models.Task.objects.all()

    def get_object(self):
        ret_obj = super().get_object()
        
        ret_obj.last_notify_time = now()
        ret_obj.save()

        return ret_obj

class UserDetail(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()

class UserDetailByUsername(UserDetail):

    def get_object(self):
        queryset = self.get_queryset()

        obj = queryset.get(username=self.kwargs["username"])
        return obj