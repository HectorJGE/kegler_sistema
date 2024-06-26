# Generated by Django 3.1.4 on 2021-03-12 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Payment Method',
                'verbose_name_plural': 'Payment Method',
            },
        ),
        migrations.CreateModel(
            name='PaymentTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Payment Term',
                'verbose_name_plural': 'Payment Terms',
            },
        ),
        migrations.CreateModel(
            name='InvoiceHeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('invoice_number', models.CharField(max_length=25, verbose_name='Invoice Number')),
                ('client_name', models.CharField(max_length=150, verbose_name='Client Name')),
                ('client_tax_identification_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Client Tax Identification Number')),
                ('invoice_date', models.DateTimeField(verbose_name='Invoice Date')),
                ('invoice_total', models.FloatField(verbose_name='Invoice Total')),
                ('invoice_total_letters', models.CharField(max_length=250, verbose_name='Invoice Total Letters')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_headers', to='base.currency', verbose_name='Currency')),
                ('payment_term', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_headers', to='invoicing.paymentterm', verbose_name='Payment Term')),
            ],
            options={
                'verbose_name': 'Invoice Header',
                'verbose_name_plural': 'Invoice Headers',
            },
        ),
        migrations.CreateModel(
            name='InvoiceDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('quantity', models.IntegerField(default=0, verbose_name='Quantity')),
                ('description', models.CharField(max_length=250, verbose_name='Description')),
                ('unit_price', models.FloatField(verbose_name='Unit price')),
                ('total_price', models.FloatField(verbose_name='Total Price')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_details', to='base.currency', verbose_name='Currency')),
                ('invoice_header', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice_details', to='invoicing.invoiceheader', verbose_name='Invoice Header')),
            ],
            options={
                'verbose_name': 'Invoice Detail',
                'verbose_name_plural': 'Invoice Details',
            },
        ),
    ]
