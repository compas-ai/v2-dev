# Generated by Django 5.0.1 on 2024-10-01 10:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0073_mentorshipsession_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('link', models.TextField()),
                ('end_time', models.TimeField()),
                ('note', models.TextField()),
                ('status', models.CharField(blank=True, choices=[('', ''), ('upcoming', 'Upcoming'), ('pending', 'Pending'), ('past', 'Past'), ('cancelled', 'Cancelled')], default='upcoming', max_length=100)),
                ('learner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boooking_learner', to='compasaiv2_app.profile')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking_session', to='compasaiv2_app.mentorshipsession')),
            ],
        ),
    ]
