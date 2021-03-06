# Generated by Django 2.0.6 on 2018-08-11 21:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_auto_20180810_1817'),
    ]

    operations = [
        migrations.CreateModel(
            name='studyResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, unique=True, verbose_name='Resource Name')),
                ('path', models.FileField(blank=True, max_length=1024, null=True, upload_to='')),
                ('level', models.IntegerField(blank=True, null=True)),
                ('pic', models.ImageField(blank=True, null=True, upload_to='study/uploaded/', verbose_name='Resource Figure')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.Category')),
            ],
        ),
    ]
