# Generated by Django 3.1.4 on 2021-03-17 02:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0006_medicalsupplyinsuranceagreement'),
        ('consultation', '0003_auto_20210317_0149'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalsupplyused',
            name='insurance_agreement_coverage_percent',
            field=models.FloatField(default=0, verbose_name='Insurance Agreement Coverage Percent'),
        ),
        migrations.AddField(
            model_name='medicalsupplyused',
            name='medical_supply_insurance_agreement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='medical_supplies_used', to='clinic.medicalsupplyinsuranceagreement', verbose_name='Medical Supply Insurance Agreement'),
        ),
    ]