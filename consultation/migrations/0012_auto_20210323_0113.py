# Generated by Django 3.1.4 on 2021-03-23 01:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('consultation', '0011_auto_20210323_0039'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultationsheet',
            name='delivered_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets_delivered_by_user', to=settings.AUTH_USER_MODEL, verbose_name='Delivered By'),
        ),
        migrations.AddField(
            model_name='consultationsheet',
            name='filed_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets_filed_by_user', to=settings.AUTH_USER_MODEL, verbose_name='Filed By'),
        ),
        migrations.AddField(
            model_name='consultationsheet',
            name='performed_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets_performed_by_user', to=settings.AUTH_USER_MODEL, verbose_name='Performed By'),
        ),
        migrations.AddField(
            model_name='consultationsheet',
            name='reported_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='consultation_sheets_reported_by_user', to=settings.AUTH_USER_MODEL, verbose_name='Reported By'),
        ),
    ]