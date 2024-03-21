# Generated by Django 3.1.4 on 2021-03-17 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
        ('clinic', '0007_auto_20210317_0329'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='medicalstudyinsuranceagreement',
            unique_together={('medical_study', 'insurance_plan')},
        ),
        migrations.AlterUniqueTogether(
            name='medicalsupplyinsuranceagreement',
            unique_together={('medical_supply', 'insurance_plan')},
        ),
    ]
