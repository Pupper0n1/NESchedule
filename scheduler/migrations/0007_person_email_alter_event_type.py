# Generated by Django 4.1.7 on 2023-07-08 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0006_rename_date_time_event_date_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('RTO', 'Requested Time Off'), ('PRF', 'Preferred shift'), ('VAC', 'Vacation')], max_length=3),
        ),
    ]
