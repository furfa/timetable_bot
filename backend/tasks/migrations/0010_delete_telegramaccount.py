# Generated by Django 3.2.6 on 2021-08-22 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_auto_20210822_1419'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TelegramAccount',
        ),
    ]
