# Generated by Django 4.2.23 on 2025-06-23 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='canvas_json',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='result',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
