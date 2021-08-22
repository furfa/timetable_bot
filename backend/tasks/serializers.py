from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from pprint import pprint

from . import models


class UserSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    username = serializers.CharField(allow_blank=True, required=False)
    first_name = serializers.CharField(allow_blank=True, required=False)
    last_name = serializers.CharField(allow_blank=True, required=False)

    def to_representation(self, value):
        if isinstance(value, User):
            return {
                "telegram_id": value.id,
                "username" : value.username
            }


        raise Exception('Unexpected type of user ')

    def create(self, validated_data):
        val_telegram_id = validated_data["telegram_id"]
        val_username = validated_data["username"]
        val_first_name = validated_data["first_name"]
        val_last_name = validated_data["last_name"]

        user, status1 = User.objects.get_or_create(id=val_telegram_id)

        user.username = val_username
        user.first_name = val_first_name
        user.last_name = val_last_name
        
        user.save()

        return user
"""
    def update(self, instance, validated_data):
        new_tg_acc = models.TelegramAccount.objects.create(telegram_id=validated_data["telegram_id"])

        instance.telegram_account = new_tg_acc
        instance.save()
        return instance
"""

class TaskSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    worker = UserSerializer()

    def update(self, instance, validated_data):
        try:
            creator = validated_data.pop("creator")
            instance.creator = User.objects.get(id=creator["telegram_id"] )
        except KeyError:
            pass
        
        try:
            worker = validated_data.pop("worker")
            instance.worker = User.objects.get(id=worker["telegram_id"] )
        except KeyError:
            pass


        instance.save()

        return super().update(instance, validated_data)
    def create(self, validated_data):
        creator = validated_data.pop("creator")
        worker = validated_data.pop("worker")

        task = super().create(validated_data) 

        if creator_telegram_id := creator.get("telegram_id"):
            task.creator = User.objects.get(id=creator_telegram_id)
        else:
            raise ValueError

        if worker_telegram_id := worker.get("telegram_id"):
            task.worker = User.objects.get(id=worker_telegram_id)
        else: 
            raise ValueError

        task.save()

        return task
    class Meta:
        model = models.Task
        fields = ["pk", "description", "creation_date", "deadline", "status", "creator", "worker"]

class CommentSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    task = TaskSerializer(read_only=True)

    def create(self, validated_data):
        pprint(validated_data)
        creator = validated_data.pop("creator")

        task = validated_data.pop("task_object")

        comment = super().create(validated_data)

        if creator_telegram_id := creator.get("telegram_id"):
            comment.creator = User.objects.get(id=creator_telegram_id )

        comment.task = task 

        comment.save()
        
        return comment

    class Meta:
        model = models.Comment
        fields = ["creation_date", "text", "creator", "task"]
