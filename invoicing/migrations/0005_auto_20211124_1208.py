# Generated by Django 3.1.4 on 2021-11-24 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0004_delete_paymentterm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoiceheader',
            name='invoice_date',
            field=models.DateField(verbose_name='Invoice Date'),
        ),
    ]