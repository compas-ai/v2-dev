# Generated by Django 5.0.1 on 2024-09-10 16:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0038_mentorship'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorship',
            name='booking_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='profile',
            name='mentor_booking_info',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
