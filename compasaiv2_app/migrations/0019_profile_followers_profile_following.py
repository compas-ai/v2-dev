# Generated by Django 5.0.1 on 2024-08-30 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0018_alter_profile_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='followers',
            field=models.ManyToManyField(related_name='followers_users', to='compasaiv2_app.profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(related_name='following_users', to='compasaiv2_app.profile'),
        ),
    ]
