# Generated by Django 5.0.1 on 2024-08-09 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0009_myprofileskill_active_myprofileskill_progress_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
