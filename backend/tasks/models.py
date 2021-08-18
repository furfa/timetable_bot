from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class TelegramAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="telegram_account", null=True, blank=True)
    telegram_id = models.IntegerField()


class Comment(models.Model):
    creation_date = models.DateTimeField(default=now)
    text = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_comments", null=True, blank=True)


class Task(models.Model):
    description = models.TextField()

    deadline = models.DateTimeField()

    creation_date = models.DateTimeField(default=now)

    comments = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)

    done = models.BooleanField(default=False)

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tasks", null=True, blank=True)

    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="worked_tasks", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.pk}: {self.creation_date} : {self.done}"
