# Generated by Django 5.0.1 on 2024-09-16 19:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0055_remove_group_events'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='mentor_skills',
        ),
        migrations.AddField(
            model_name='profile',
            name='mentor_skill',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mentor_skill', to='compasaiv2_app.skill'),
        ),
    ]
