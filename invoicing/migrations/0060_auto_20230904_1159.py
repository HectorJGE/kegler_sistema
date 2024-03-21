# Generated by Django 3.1.4 on 2023-09-04 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0059_customer_customer_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditnoteheader',
            name='client_phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Client Phone Number'),
        ),
        migrations.AddField(
            model_name='invoiceheader',
            name='client_phone_number',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Client Phone Number'),
        ),
    ]
