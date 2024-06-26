# Generated by Django 3.1.4 on 2023-09-08 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0028_insurancecompany_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='tax_identification_name',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Tax Identification Name'),
        ),
        migrations.AddField(
            model_name='patient',
            name='tax_identification_name',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Tax Identification Name'),
        ),
        migrations.AddField(
            model_name='technician',
            name='tax_identification_name',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Tax Identification Name'),
        ),
        migrations.AddField(
            model_name='treatingdoctor',
            name='tax_identification_name',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Tax Identification Name'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='tax_identification_number',
            field=models.CharField(max_length=150, null=True, verbose_name='Tax Identification Number'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='tax_identification_number',
            field=models.CharField(max_length=150, null=True, verbose_name='Tax Identification Number'),
        ),
        migrations.AlterField(
            model_name='technician',
            name='tax_identification_number',
            field=models.CharField(max_length=150, null=True, verbose_name='Tax Identification Number'),
        ),
        migrations.AlterField(
            model_name='treatingdoctor',
            name='tax_identification_number',
            field=models.CharField(max_length=150, null=True, verbose_name='Tax Identification Number'),
        ),
    ]
