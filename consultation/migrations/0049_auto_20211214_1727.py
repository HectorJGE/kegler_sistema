# Generated by Django 3.1.4 on 2021-12-14 20:27

import consultation.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultation', '0048_auto_20211110_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultationreport',
            name='audio_report',
            field=models.FileField(blank=True, default=None, null=True, upload_to=consultation.models.consultation_report_audio_storage_path, verbose_name='Audio Report'),
        ),
    ]
