# Generated by Django 3.1.4 on 2021-11-29 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0007_auto_20211129_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='stamprangeinvoiceuser',
            name='invoice',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='invoicing.invoiceheader'),
            preserve_default=False,
        ),
    ]
