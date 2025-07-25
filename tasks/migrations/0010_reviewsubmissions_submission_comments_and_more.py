# Generated by Django 5.2.3 on 2025-07-07 06:33

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0013_staffuser'),
        ('tasks', '0009_task_assigned_to_task_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewSubmissions',
            fields=[
            ],
            options={
                'verbose_name': '🕵️ Review Submissions',
                'verbose_name_plural': '🕵️ Review Submissions',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='submission',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=10),
        ),
    ]
