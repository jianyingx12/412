# Generated by Django 5.1.1 on 2024-12-08 05:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_remove_medicine_common_uses'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='user_profile',
        ),
    ]