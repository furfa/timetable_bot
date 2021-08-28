from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
import django

from . import models


class CommentInline(admin.TabularInline):
    """
        Инлайн для коммента(отображается в задаче)
    """
    model = models.Comment
    extra = 1
    pass
@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    """
        Админка для задачи
    """
    
    formfield_overrides = {
        django.db.models.TextField: {'widget': django.forms.Textarea(attrs={'rows':4, 'cols':40})},
    }

    list_display  = ("pk","description", "creation_date", "deadline", "status", "creator", "worker")
    list_editable = ("description", "deadline", "status")
    list_filter   = ("status", "creator", "worker")
    search_fields = (
        "description",
        "creator__first_name",
        "creator__last_name", 
        "creator__username",
        "worker__first_name",
        "worker__last_name",
        "worker__username"
    )
    inlines = (CommentInline, )

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    """
        Админка для Комментария
    """
    list_display = ["creation_date", "text", "creator", "task"]
    search_fields = ("text", "creator__username")
    list_filter   = ("creator", )


#################
#  User Admin   #
#################

class UserAdmin(BaseUserAdmin):
    list_display = ["id", "username", "last_name", "first_name", "is_staff"]
    list_editable = ["is_staff"]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)