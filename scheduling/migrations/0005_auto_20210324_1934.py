# Generated by Django 3.1.4 on 2021-03-24 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0004_auto_20210324_1931'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='appointmentstateuserlog',
            unique_together={('appointment', 'appointment_state')},
        ),
    ]