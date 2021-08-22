"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from . import views as task_views

urlpatterns = [
    path('task/', task_views.task_view),
    path('task/<int:pk>', task_views.task_detail_view),
    path('user/', task_views.UserView.as_view()),
    path('user/<int:pk>', task_views.UserDetail.as_view()),
    path('user_by_username/<str:username>', task_views.UserDetailByUsername.as_view()),

    path('user_creator_tasks/<int:telegram_id>', task_views.user_creator_tasks_view),
    path('user_worker_tasks/<int:telegram_id>', task_views.user_worker_tasks_view),
    path('task_comments/<int:pk>', task_views.task_comments),

    path('tasks_for_notify/', task_views.TasksToNotifyList.as_view()),
    path('task_mark_notifyed/<int:pk>', task_views.TaskMarkNotifyed.as_view())
]
