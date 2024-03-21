# Generated by Django 3.1.4 on 2021-03-12 13:30

import consultation.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
        ('scheduling', '0001_initial'),
        ('clinic', '0001_initial'),
        ('stock', '0001_initial'),
        ('invoicing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Consultation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('consultation_date', models.DateTimeField(auto_now_add=True, verbose_name='Consultation Date')),
                ('notes', models.TextField(verbose_name='Notes')),
                ('insurance_plan_cover_percentage', models.FloatField(verbose_name='Insurance Plan Cover Percentage')),
                ('total_cost', models.FloatField(verbose_name='Total Cost')),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='scheduling.appointment', verbose_name='Appointment')),
            ],
            options={
                'verbose_name': 'Consultation',
                'verbose_name_plural': 'Consultations',
            },
        ),
        migrations.CreateModel(
            name='ConsultationFileType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('extension', models.CharField(max_length=10, verbose_name='Extension')),
                ('type', models.IntegerField(choices=[(0, 'Image'), (1, 'Sound'), (2, 'Video'), (3, 'Text')], verbose_name='Types')),
            ],
            options={
                'verbose_name': 'Consultation File Type',
                'verbose_name_plural': 'Consultation File Types',
            },
        ),
        migrations.CreateModel(
            name='ConsultationSheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('consultation_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Consultation Date')),
                ('payment_reference', models.CharField(blank=True, max_length=100, null=True, verbose_name='Payment Reference')),
                ('medical_study_ammount', models.FloatField(default=0, verbose_name='Medical Study Ammount')),
                ('medical_supplies_ammount', models.FloatField(default=0, verbose_name='Medical Supplies Ammount')),
                ('total_amount', models.FloatField(default=0, verbose_name='Total Amount')),
                ('appointment', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='scheduling.appointment', verbose_name='Appointment')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='base.currency', verbose_name='Currency')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='clinic.doctor', verbose_name='Doctor')),
                ('medical_study', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='clinic.medicalstudy', verbose_name='Medical Study')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='clinic.patient', verbose_name='Patient')),
                ('patient_insurance_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='clinic.insuranceplan', verbose_name='Patient Insurance Plan')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='invoicing.paymentmethod', verbose_name='Payment Method')),
                ('treating_doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='clinic.treatingdoctor', verbose_name='Treating Doctor')),
            ],
            options={
                'verbose_name': 'Consultation Sheet',
                'verbose_name_plural': 'Consultation Sheets',
            },
        ),
        migrations.CreateModel(
            name='ConsultationSheetDocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Consultation Sheet Document Type',
                'verbose_name_plural': 'Consultation Sheet Document Types',
            },
        ),
        migrations.CreateModel(
            name='CosultationState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=10, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Consultation State',
                'verbose_name_plural': 'Consultation States',
            },
        ),
        migrations.CreateModel(
            name='MedicalSupplyUsed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('quantity', models.FloatField(verbose_name='Quantity')),
                ('price', models.FloatField(default=0, verbose_name='Price')),
                ('consultation_sheet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='medical_supplies_used', to='consultation.consultationsheet', verbose_name='Consultation Sheet')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='medical_supplies_used', to='base.currency', verbose_name='Currency')),
                ('medical_supply', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='medical_supplies_used', to='stock.product', verbose_name='Medical Supply')),
            ],
            options={
                'verbose_name': 'Medical Supply Used',
                'verbose_name_plural': 'Medical Supplies Used',
            },
        ),
        migrations.CreateModel(
            name='ConsultationVideoFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('file_name', models.CharField(max_length=250, verbose_name='File Name')),
                ('consultation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultation_video_files', to='consultation.consultation', verbose_name='Consultation')),
                ('consultation_file_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='consultation.consultationfiletype')),
            ],
            options={
                'verbose_name': 'Consultation Video File',
                'verbose_name_plural': 'Consultation Video Files',
            },
        ),
        migrations.CreateModel(
            name='ConsultationTextFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('file_name', models.CharField(max_length=250, verbose_name='File Name')),
                ('consultation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultation_text_files', to='consultation.consultation', verbose_name='Consultation')),
                ('consultation_file_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='consultation.consultationfiletype')),
            ],
            options={
                'verbose_name': 'Consultation Text File',
                'verbose_name_plural': 'Consultation Text Files',
            },
        ),
        migrations.CreateModel(
            name='ConsultationSoundFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('file_name', models.CharField(max_length=250, verbose_name='File Name')),
                ('consultation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consultation_sound_files', to='consultation.consultation', verbose_name='Consultation')),
                ('consultation_file_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='consultation.consultationfiletype')),
            ],
            options={
                'verbose_name': 'Consultation Sound File',
                'verbose_name_plural': 'Consultation Sound Files',
            },
        ),
        migrations.CreateModel(
            name='ConsultationSheetDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('document_name', models.CharField(max_length=250, verbose_name='Document Name')),
                ('file', models.FileField(upload_to=consultation.models.consultation_sheet_document_storage_path, verbose_name='File')),
                ('consultation_sheet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheet_documents', to='consultation.consultationsheet', verbose_name='Consultation')),
                ('document_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheet_documents', to='consultation.consultationsheetdocumenttype', verbose_name='Document Type')),
            ],
            options={
                'verbose_name': 'Consultation Sheet Document',
                'verbose_name_plural': 'Consultation Sheet Documents',
            },
        ),
        migrations.CreateModel(
            name='ConsultationImageFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('file_name', models.CharField(max_length=250, verbose_name='File Name')),
                ('consultation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consult_image_files', to='consultation.consultation', verbose_name='Consultation')),
                ('consultation_file_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='consultation.consultationfiletype')),
            ],
            options={
                'verbose_name': 'Consultation Image File',
                'verbose_name_plural': 'Consultation Image Files',
            },
        ),
        migrations.AddField(
            model_name='consultation',
            name='consultation_state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='consultation.cosultationstate', verbose_name='Consultation State'),
        ),
        migrations.AddField(
            model_name='consultation',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='base.currency', verbose_name='Currency'),
        ),
        migrations.AddField(
            model_name='consultation',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='clinic.doctor', verbose_name='Doctor'),
        ),
        migrations.AddField(
            model_name='consultation',
            name='medical_equipment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='clinic.medicalequipment', verbose_name='Medical Equipment'),
        ),
        migrations.AddField(
            model_name='consultation',
            name='medical_study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='clinic.medicalstudy', verbose_name='Medical Study'),
        ),
        migrations.AddField(
            model_name='consultation',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='clinic.patient', verbose_name='Patient'),
        ),
        migrations.AddField(
            model_name='consultation',
            name='patient_insurance_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='clinic.insuranceplan', verbose_name='Patient Insurance Plan'),
        ),
        migrations.AddField(
            model_name='consultation',
            name='technician',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='clinic.technician', verbose_name='Technician'),
        ),
        migrations.AddField(
            model_name='consultation',
            name='treating_doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consults', to='clinic.treatingdoctor', verbose_name='Treating Doctor'),
        ),
    ]