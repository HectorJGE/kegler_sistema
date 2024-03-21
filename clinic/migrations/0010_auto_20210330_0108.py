# Generated by Django 3.1.4 on 2021-03-30 01:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0009_sector'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='doctors', to='clinic.sector', verbose_name='Sector'),
        ),
        migrations.AddField(
            model_name='medicalequipment',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='medical_equipments', to='clinic.sector', verbose_name='Sector'),
        ),
        migrations.AddField(
            model_name='medicalstudy',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='medical_studies', to='clinic.sector', verbose_name='Sector'),
        ),
    ]