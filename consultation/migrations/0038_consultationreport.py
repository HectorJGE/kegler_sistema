# Generated by Django 3.1.4 on 2021-08-11 15:25

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0025_auto_20210810_1804'),
        ('consultation', '0037_auto_20210810_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultationReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('report_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Report Date')),
                ('notes', models.TextField(verbose_name='Notes')),
                ('report', models.TextField(verbose_name='Report')),
                ('consultation', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_reports', to='consultation.consultation', verbose_name='Consultation')),
                ('consultation_sheet', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_reports', to='consultation.consultationsheet', verbose_name='Consultation Sheet')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_reports', to='clinic.doctor', verbose_name='Doctor')),
                ('medical_equipment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_reports', to='clinic.medicalequipment', verbose_name='Medical Equipment')),
                ('medical_study', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_reports', to='clinic.medicalstudy', verbose_name='Medical Study')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_reports', to='clinic.patient', verbose_name='Patient')),
                ('technician', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_reports', to='clinic.technician', verbose_name='Technician')),
                ('treating_doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_reports', to='clinic.treatingdoctor', verbose_name='Treating Doctor')),
            ],
            options={
                'verbose_name': 'Consultation Report',
                'verbose_name_plural': 'Consultations Reports',
            },
        ),
    ]
