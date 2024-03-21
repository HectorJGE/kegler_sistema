# Generated by Django 3.1.4 on 2023-08-24 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0052_auto_20230824_0037'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creditnoteheader',
            name='invoice_total',
        ),
        migrations.AddField(
            model_name='creditnoteheader',
            name='credit_note_total',
            field=models.FloatField(default=0, verbose_name='Credit Note Total'),
        ),
        migrations.AlterField(
            model_name='invoiceheader',
            name='invoice_total',
            field=models.FloatField(default=0, verbose_name='Invoice Total'),
        ),
    ]
