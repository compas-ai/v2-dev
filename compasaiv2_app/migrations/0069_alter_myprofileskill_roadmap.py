# Generated by Django 5.0.1 on 2024-09-25 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0068_profile_resume_alter_recommenderinfo_stage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myprofileskill',
            name='roadmap',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
