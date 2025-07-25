# Generated by Django 5.2.3 on 2025-06-26 10:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_alter_task_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='tasks_image/extra/')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='tasks.task')),
            ],
        ),
    ]
