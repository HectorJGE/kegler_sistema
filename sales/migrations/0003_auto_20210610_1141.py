# Generated by Django 3.1.4 on 2021-06-10 15:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_auto_20210610_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consultationentrysheetsaleheader',
            name='sale_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Sale Date'),
        ),
        migrations.AlterField(
            model_name='consultationentrysheetsaleheader',
            name='sale_total',
            field=models.FloatField(default=0, verbose_name='Sale Total'),
        ),
        migrations.AlterField(
            model_name='consultationsheetsaledetail',
            name='description',
            field=models.CharField(default='', max_length=250, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='consultationsheetsaledetail',
            name='quantity',
            field=models.IntegerField(default=1, verbose_name='Quantity'),
        ),
    ]
