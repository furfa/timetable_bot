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

class UserSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()

    def to_representation(self, value):
        
        if isinstance(value, User):

            return {
                "telegram_id": value.telegram_account.telegram_id
            }

        raise Exception('Unexpected type of user ')

    def create(self, validated_data):
        

        user = User.objects.create(username=validated_data["telegram_id"])

        tg_acc = models.TelegramAccount.objects.create(user=user, telegram_id=validated_data["telegram_id"])
        return user

    def update(self, instance, validated_data):
        new_tg_acc = models.TelegramAccount.objects.create(telegram_id=validated_data["telegram_id"])

        instance.telegram_account = new_tg_acc
        instance.save()
        return instance

class TaskSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    worker = UserSerializer()

    def update(self, instance, validated_data):
        try:
            creator = validated_data.pop("creator")
            instance.creator = models.TelegramAccount.objects.get(telegram_id=creator["telegram_id"] ).user
        except KeyError:
            pass
        except models.TelegramAccount.DoesNotExist as e:
            raise e
        
        try:
            worker = validated_data.pop("worker")
            instance.worker = models.TelegramAccount.objects.get(telegram_id=worker["telegram_id"] ).user
        except KeyError:
            pass
        except models.TelegramAccount.DoesNotExist as e:
            raise e

        instance.save()

        return super().update(instance, validated_data)
    def create(self, validated_data):
        creator = validated_data.pop("creator")
        worker = validated_data.pop("worker")

        task = super().create(validated_data) 

        if creator_telegram_id := creator.get("telegram_id"):
            task.creator = models.TelegramAccount.objects.get(telegram_id=creator_telegram_id ).user
        else:
            raise ValueError

        if worker_telegram_id := worker.get("telegram_id"):
            task.worker = models.TelegramAccount.objects.get(telegram_id=worker_telegram_id ).user
        else: 
            raise ValueError

        task.save()

        return task
    class Meta:
        model = models.Task
        fields = ["pk", "description", "creation_date", "deadline", "done", "creator", "worker"]
        

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

@api_view(['POST'])
def task_view(request):

    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        
        if serializer.is_valid():
            task:models.Task = serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['GET'])
def user_tasks_view(request, telegram_id):
    try:
        user = models.TelegramAccount.objects.get(telegram_id=telegram_id).user
    except models.TelegramAccount.DoesNotExist:
        return Response(status=404)

    if request.method == "GET":
        serializer = TaskSerializer(user.created_tasks.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
