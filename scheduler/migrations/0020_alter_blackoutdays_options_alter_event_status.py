# Generated by Django 4.1.7 on 2023-10-05 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0019_alter_event_type_blackoutdays'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blackoutdays',
            options={'verbose_name_plural': 'Blackout Days'},
        ),
        migrations.AlterField(
            model_name='event',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('D', 'Denied'), ('O', 'Other'), ('H', 'Hidden')], default='Pending', max_length=1),
        ),
    ]
