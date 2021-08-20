from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

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

class CommentSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    task = TaskSerializer()

    def create(self, validated_data):
        creator = validated_data.pop("creator")
        task = validated_data.pop("task")

        comment = super().create(validated_data)

        if creator_telegram_id := creator.get("telegram_id"):
            comment.creator = models.TelegramAccount.objects.get(telegram_id=creator_telegram_id ).user


        print(task)
        comment.task = models.Task.objects.get(description=task["description"])  # TODO: Надо делать по pk почему-о его нет в дикте

        comment.save()
        
        return comment

    class Meta:
        model = models.Comment
        fields = ["creation_date", "text", "creator", "task"]
