# Generated by Django 3.1.4 on 2021-05-17 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('clinic', '0022_insuranceplanmedicalsupplyfee'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalstudyinsuranceagreement',
            name='cover_type',
            field=models.IntegerField(choices=[(0, 'Percentage'), (1, 'Amount')], default=0, verbose_name='Cover Types'),
        ),
        migrations.AddField(
            model_name='medicalstudyinsuranceagreement',
            name='coverage_amount',
            field=models.FloatField(default=0, verbose_name='Coverage Amount'),
        ),
        migrations.AddField(
            model_name='medicalstudyinsuranceagreement',
            name='currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='medical_study_insurance_agreements', to='base.currency', verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='medicalsupplyinsuranceagreement',
            name='cover_type',
            field=models.IntegerField(choices=[(0, 'Percentage'), (1, 'Amount')], default=0, verbose_name='Cover Types'),
        ),
        migrations.AddField(
            model_name='medicalsupplyinsuranceagreement',
            name='coverage_amount',
            field=models.FloatField(default=0, verbose_name='Coverage Amount'),
        ),
        migrations.AddField(
            model_name='medicalsupplyinsuranceagreement',
            name='currency',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='medical_supply_insurance_agreements', to='base.currency', verbose_name='Currency'),
        ),
    ]