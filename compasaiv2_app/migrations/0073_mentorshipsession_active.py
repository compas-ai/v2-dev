# Generated by Django 5.0.1 on 2024-09-30 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0072_alter_mentorshipsession_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentorshipsession',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
