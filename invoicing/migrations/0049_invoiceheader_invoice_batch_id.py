# Generated by Django 3.1.4 on 2023-08-22 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0048_auto_20230822_0752'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceheader',
            name='invoice_batch_id',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Invoice Batch ID'),
        ),
    ]
