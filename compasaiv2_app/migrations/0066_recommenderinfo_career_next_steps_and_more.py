# Generated by Django 5.0.1 on 2024-09-24 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compasaiv2_app', '0065_recommenderinfo_career'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommenderinfo',
            name='career_next_steps',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='recommenderinfo',
            name='career_proficiency',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='recommenderinfo',
            name='career_skills',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='recommenderinfo',
            name='stage',
            field=models.CharField(choices=[('contact', 'Contact'), ('description', 'Description'), ('status', 'Status'), ('career', 'Career'), ('career_skills', 'Career Skills'), ('career_proficiency', 'Career Proficiency'), ('career_next_step', 'Career Next Step'), ('hours', 'Hours'), ('resources', 'Resources'), ('computers', 'Computers'), ('strengths', 'Strengths'), ('weakness', 'Weakness'), ('team', 'Team'), ('interests', 'Interests'), ('academics', 'Academics'), ('exposure', 'Exposure'), ('motivation', 'Motivation'), ('thankyou', 'ThankYou')], default='contact', max_length=100),
        ),
    ]
