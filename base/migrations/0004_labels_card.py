# Generated by Django 5.1 on 2024-09-03 10:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Labels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('starts_Date', models.DateField(blank=True)),
                ('finish_Date', models.DateField(blank=True)),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='card_list', to='base.list')),
            ],
        ),
    ]
