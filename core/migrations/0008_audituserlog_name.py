# Generated by Django 5.1 on 2024-09-01 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_audituserlog_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='audituserlog',
            name='name',
            field=models.CharField(default='anonymous', max_length=255),
            preserve_default=False,
        ),
    ]
