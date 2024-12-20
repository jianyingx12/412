# Generated by Django 5.1.1 on 2024-11-23 01:29

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
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=100)),
                ('common_uses', models.TextField()),
                ('dosage_info', models.TextField()),
                ('side_effects', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('severity_level', models.CharField(max_length=100)),
                ('medicine1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interaction1', to='project.medicine')),
                ('medicine2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interaction2', to='project.medicine')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField()),
                ('weight', models.FloatField()),
                ('allergies', models.TextField()),
                ('medical_conditions', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dosage', models.CharField(max_length=100)),
                ('frequency', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('time_of_day', models.TimeField()),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.medicine')),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.userprofile')),
            ],
        ),
    ]
