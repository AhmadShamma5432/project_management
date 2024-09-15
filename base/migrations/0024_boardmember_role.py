# Generated by Django 5.1 on 2024-09-08 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_card_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardmember',
            name='role',
            field=models.CharField(choices=[('Admin', 'Admin'), ('Manager', 'Manager'), ('Member', 'Member')], default='Member', max_length=255),
            preserve_default=False,
        ),
    ]
