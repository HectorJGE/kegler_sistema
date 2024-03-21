# Generated by Django 3.1.4 on 2021-08-10 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0023_auto_20210517_1530'),
        ('consultation', '0036_remove_consultation_patient_insurance_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultation',
            name='medical_equipment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='clinic.medicalequipment', verbose_name='Medical Equipment'),
        ),
    ]
