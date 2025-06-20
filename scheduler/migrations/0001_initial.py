# Generated by Django 5.2.1 on 2025-06-12 17:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('event_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'events',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('room_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('capacity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('type', models.CharField(max_length=50)),
                ('features', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'rooms',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RoomBooking',
            fields=[
                ('booking_id', models.AutoField(primary_key=True, serialize=False)),
                ('booking_date', models.DateField()),
            ],
            options={
                'db_table': 'roombookings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Timeslot',
            fields=[
                ('timeslot_id', models.AutoField(primary_key=True, serialize=False)),
                ('day', models.CharField(max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
            options={
                'db_table': 'timeslots',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('role', models.CharField(max_length=20)),
                ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
    ]
