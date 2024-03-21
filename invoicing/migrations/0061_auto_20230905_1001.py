# Generated by Django 3.1.4 on 2023-09-05 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0060_auto_20230904_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditnoteheader',
            name='credit_note_kude_html',
            field=models.TextField(blank=True, null=True, verbose_name='Credit Note KUDE HTML'),
        ),
        migrations.AddField(
            model_name='invoiceheader',
            name='invoice_kude_html',
            field=models.TextField(blank=True, null=True, verbose_name='Invoice KUDE HTML'),
        ),
    ]