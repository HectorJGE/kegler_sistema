# Generated by Django 3.1.4 on 2023-03-29 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0038_invoiceheader_invoice_email_sended'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='invoice_email_sended',
            field=models.BooleanField(default=False, null=True, verbose_name='Invoice Sent'),
        ),
    ]
