# Generated by Django 5.1 on 2024-09-01 20:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_audituserlog_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audituserlog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_log', to=settings.AUTH_USER_MODEL),
        ),
    ]
