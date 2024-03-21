# Generated by Django 3.1.4 on 2021-03-23 01:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('consultation', '0013_consultationsheet_received_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultationsheet',
            name='consultation_state',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets', to='consultation.consultationstate', verbose_name='Consultation State'),
            preserve_default=False,
        ),
    ]