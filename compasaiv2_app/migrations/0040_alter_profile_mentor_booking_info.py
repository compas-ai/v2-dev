# Generated by Django 5.0.1 on 2024-09-10 16:25

import compasaiv2_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0039_mentorship_booking_time_profile_mentor_booking_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='mentor_booking_info',
            field=models.JSONField(blank=True, default=compasaiv2_app.models.default_booking, null=True),
        ),
    ]
