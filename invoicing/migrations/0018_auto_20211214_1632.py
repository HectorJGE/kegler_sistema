# Generated by Django 3.1.4 on 2021-12-14 19:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0017_invoiceheader_customer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoiceheader',
            name='total_exempt',
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='customer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_headers', to='invoicing.customer', verbose_name='Customer'),
        ),
    ]
