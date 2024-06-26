# Generated by Django 3.1.4 on 2021-11-30 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoicing', '0008_stamprangeinvoiceuser_invoice'),
    ]

    operations = [
        migrations.CreateModel(
            name='StampRange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('range_invoice', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='invoicing.invoicerange')),
                ('stamp', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='invoicing.invoicestamp')),
            ],
            options={
                'permissions': (('can_undelete', 'Can undelete this object'),),
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='StampRangeInvoiceUser',
        ),
    ]
