# Generated by Django 5.0.1 on 2024-09-30 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0071_alter_mentorshipsession_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mentorshipsession',
            name='session',
            field=models.CharField(blank=True, choices=[('', ''), ('coffee_chat', 'Coffee Chat'), ('office_hours', 'Office Hours'), ('speed_networking', 'Speed Networking'), ('mock_interview', 'Mock Interview'), ('check_ins', 'Check Ins')], default='', max_length=100),
        ),
    ]
