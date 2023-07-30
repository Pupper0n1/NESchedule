# Generated by Django 4.1.7 on 2023-07-27 20:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0010_alter_boutique_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'verbose_name_plural': 'People'},
        ),
        migrations.RenameField(
            model_name='event',
            old_name='date_start',
            new_name='date',
        ),
        migrations.RemoveField(
            model_name='event',
            name='date_end',
        ),
    ]