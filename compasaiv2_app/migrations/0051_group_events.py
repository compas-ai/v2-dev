# Generated by Django 5.0.1 on 2024-09-15 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0050_group_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='events',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
