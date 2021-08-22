from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Task(models.Model):
    description = models.TextField(verbose_name="Описание")

    deadline = models.DateTimeField(verbose_name="Дедлайн")

    last_notify_time = models.DateTimeField(verbose_name="Дата последнего оповещения", default=now)

    creation_date = models.DateTimeField(verbose_name="Дата создания", default=now)

    TASK_STATUS = ((0, 'В работе'), (1, 'На согласовании'), (2, 'Готово'), (3, 'Снята'))
    status = models.SmallIntegerField(verbose_name="Статус", choices=TASK_STATUS, default=0)

    creator = models.ForeignKey(User, verbose_name="На контроле", on_delete=models.CASCADE, related_name="created_tasks", null=True, blank=True)

    worker = models.ForeignKey(User, verbose_name="Исполнитель", on_delete=models.CASCADE, related_name="worked_tasks", null=True, blank=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self) -> str:
        return f"{self.pk}: {self.description[:30]} : {self.TASK_STATUS[self.status][1].lower()}"

class Comment(models.Model):
    creation_date = models.DateTimeField(verbose_name="Дата создания", default=now)
    text = models.TextField(verbose_name="Текст комментария")
    creator = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE, related_name="created_comments", null=True, blank=True)
    task = models.ForeignKey(Task, verbose_name="Комментриемая задача", on_delete=models.CASCADE, related_name="comments", null=True, blank=True)

    def __str__(self) -> str:
        task_pk = "none"
        try:
            task_pk = self.task.pk
        except:
            pass

        creator_username = "none"
        try:
            creator_username = self.creator.username
        except:
            pass

        return f"id:{self.pk}: task_id:{task_pk} creator_username: {creator_username}"

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'