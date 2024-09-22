# Generated by Django 5.0.1 on 2024-08-02 00:20

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.CharField(choices=[('learner', 'Learner'), ('mentor', 'Mentor')], default='learner', max_length=100)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('referral_code', models.CharField(default=0, max_length=10)),
                ('username', models.CharField(blank=True, max_length=100)),
                ('display_name', models.CharField(blank=True, max_length=100)),
                ('profile_picture', models.ImageField(blank=True, upload_to='profile_dp_image')),
                ('email', models.EmailField(blank=True, max_length=100)),
                ('phone_number', models.CharField(blank=True, max_length=100)),
                ('joined', models.DateTimeField(default=datetime.datetime.now)),
                ('tier', models.CharField(choices=[('Free', 'Free'), ('Subscription', 'Subscription')], default='Free', max_length=100)),
                ('about', models.TextField(blank=True)),
                ('referred_profiles', models.ManyToManyField(related_name='referred_users', to='compasaiv2_app.profile')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecommenderInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField()),
                ('skills', models.TextField(blank=True)),
                ('hours', models.IntegerField(default=0)),
                ('resources', models.TextField(blank=True)),
                ('computers', models.IntegerField(default=0)),
                ('strengths', models.TextField(blank=True)),
                ('weakness', models.TextField(blank=True)),
                ('team', models.CharField(default='', max_length=20)),
                ('interests', models.TextField(blank=True)),
                ('academics', models.TextField(blank=True)),
                ('exposure', models.TextField(blank=True)),
                ('motivation', models.TextField(blank=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_recommender', to='compasaiv2_app.profile')),
            ],
        ),
    ]
