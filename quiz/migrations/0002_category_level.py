# Generated by Django 2.0.6 on 2018-07-25 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='level',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]