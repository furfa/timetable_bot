from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from . import models

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ["pk", "description", "creation_date", "deadline", "done"]


@api_view(['GET', 'POST', 'PUT'])
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
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    