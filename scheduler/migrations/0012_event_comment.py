# Generated by Django 4.1.7 on 2023-07-28 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0011_alter_person_options_rename_date_start_event_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
