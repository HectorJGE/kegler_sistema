from django.db import migrations
from datetime import datetime

def load_initial_data(apps, schema_editor):
    Currency = apps.get_model('base', 'Currency')

    initial_data = [
        {
            "name": "Guarani",
            "code": "PYG",
            "sufix": "Gs",
            "created_at": datetime(2021, 1, 1, 10, 0, 0),
            "updated_at": datetime(2021, 1, 1, 10, 0, 0)
        }
    ]

    for data in initial_data:
        Currency.objects.create(**data)

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
