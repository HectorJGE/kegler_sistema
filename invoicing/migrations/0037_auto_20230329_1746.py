# Generated by Django 3.1.4 on 2023-03-29 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0036_invoiceheader_client_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='customer_email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Customer Email'),
        ),
    ]
