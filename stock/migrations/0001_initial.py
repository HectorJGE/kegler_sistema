# Generated by Django 3.1.4 on 2021-03-12 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
            ],
            options={
                'verbose_name': 'Cart',
                'verbose_name_plural': 'Carts',
            },
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('default_deposit', models.BooleanField(default=False, verbose_name='Default Deposit')),
            ],
            options={
                'verbose_name': 'Deposit',
                'verbose_name_plural': 'Deposits',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('purchase_price', models.FloatField(verbose_name='Purchase price')),
                ('sale_price', models.FloatField(verbose_name='Sale price')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='base.currency', verbose_name='Currency')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('type', models.IntegerField(choices=[(0, 'IN'), (1, 'OUT')], verbose_name='Movement Type')),
                ('quantity', models.FloatField(verbose_name='Quantity')),
                ('description', models.TextField(verbose_name='Description')),
                ('deposit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stock_movements', to='stock.deposit', verbose_name='Deposit')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stock_movements', to='stock.product', verbose_name='Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stock_movements', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Stock Movement',
                'verbose_name_plural': 'Stock Movements',
            },
        ),
        migrations.CreateModel(
            name='CartDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('quantity', models.FloatField(verbose_name='Quantity')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cart_details', to='stock.cart', verbose_name='Cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cart_details', to='stock.product', verbose_name='Product')),
            ],
            options={
                'verbose_name': 'Cart Detail',
                'verbose_name_plural': 'Cart Details',
            },
        ),
        migrations.AddField(
            model_name='cart',
            name='deposit_in',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='carts_deposit_in', to='stock.deposit', verbose_name='Deposit In'),
        ),
        migrations.AddField(
            model_name='cart',
            name='deposit_out',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='carts_deposit_out', to='stock.deposit', verbose_name='Deposit Out'),
        ),
        migrations.CreateModel(
            name='ProductDepositQuantity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('quantity', models.FloatField(verbose_name='Quantity')),
                ('deposit', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_deposit_quantity', to='stock.deposit', verbose_name='Deposit')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_deposit_quantity', to='stock.product', verbose_name='Product')),
            ],
            options={
                'verbose_name': 'Product Deposit Quantity',
                'verbose_name_plural': 'Products Deposits Quantitys',
                'unique_together': {('deposit', 'product')},
            },
        ),
    ]
