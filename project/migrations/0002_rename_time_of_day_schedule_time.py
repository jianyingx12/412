# Generated by Django 5.1.1 on 2024-12-03 04:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='time_of_day',
            new_name='time',
        ),
    ]
