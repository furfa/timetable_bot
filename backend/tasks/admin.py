from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from . import models

class TaskAdmin(admin.ModelAdmin):
    list_display = ["pk","description", "creation_date", "deadline", "comments", "done"]
    list_editable = ["description", "deadline", "comments", "done"]

admin.site.register(models.Task, TaskAdmin)


class TelegramAccountAdmin(admin.ModelAdmin):
    list_display = ["pk","user", "telegram_id"]

admin.site.register(models.TelegramAccount, TelegramAccountAdmin)

#################
#  User Admin   #
#################

class TelegramAccountInline(admin.StackedInline):
    model = models.TelegramAccount
    can_delete = False
    verbose_name_plural = 'Telegram Account'

class UserAdmin(BaseUserAdmin):
    inlines = (TelegramAccountInline, )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)