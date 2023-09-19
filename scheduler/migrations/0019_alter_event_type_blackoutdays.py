# Generated by Django 4.1.7 on 2023-08-22 02:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0018_boutique_max_rto_cs_weekday_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='type',
            field=models.CharField(choices=[('RTO', 'Requested Time Off'), ('SWP', 'Swap Shift'), ('OTH', 'Other'), ('BLK', '')], max_length=3),
        ),
        migrations.CreateModel(
            name='BlackoutDays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('boutique', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='scheduler.boutique')),
            ],
        ),
    ]