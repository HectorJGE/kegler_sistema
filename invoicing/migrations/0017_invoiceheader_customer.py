# Generated by Django 3.1.4 on 2021-12-07 19:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0016_auto_20211207_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceheader',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_headers', to='invoicing.customer', verbose_name='Customer'),
        ),
    ]
