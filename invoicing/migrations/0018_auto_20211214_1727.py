# Generated by Django 3.1.4 on 2021-12-14 20:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0017_invoiceheader_customer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': 'Customer', 'verbose_name_plural': 'Customers'},
        ),
        migrations.AlterModelOptions(
            name='invoicerange',
            options={'verbose_name': 'Invoice Range', 'verbose_name_plural': 'Invoice Ranges'},
        ),
        migrations.AlterModelOptions(
            name='invoicestamp',
            options={'verbose_name': 'Invoice Stamp', 'verbose_name_plural': 'Invoice Stamps'},
        ),
        migrations.AlterModelOptions(
            name='issuingcompanyname',
            options={'verbose_name': 'Issuing Company Name', 'verbose_name_plural': 'Issuing Company Names'},
        ),
        migrations.AlterModelOptions(
            name='stamprange',
            options={'verbose_name': 'Stamp Range', 'verbose_name_plural': 'Stamp Ranges'},
        ),
        migrations.RemoveField(
            model_name='invoiceheader',
            name='total_exempt',
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='customer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_headers', to='invoicing.customer', verbose_name='Customer'),
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='invoice_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Invoice Date'),
        ),
    ]