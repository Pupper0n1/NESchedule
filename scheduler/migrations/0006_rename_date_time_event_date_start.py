# Generated by Django 4.1.7 on 2023-07-05 22:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0005_event_time_alter_event_date_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='date_time',
            new_name='date_start',
        ),
    ]