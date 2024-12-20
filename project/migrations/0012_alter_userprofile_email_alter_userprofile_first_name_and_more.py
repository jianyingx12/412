# Generated by Django 5.1.1 on 2024-12-11 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0011_userprofile_email_userprofile_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='first_name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='last_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
