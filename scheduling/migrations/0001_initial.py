# Generated by Django 3.1.4 on 2021-03-12 13:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
        ('clinic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppointmentState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('state_code', models.IntegerField(choices=[(0, 'Scheduled'), (1, 'Consulted'), (2, 'Canceled'), (3, 'Absent'), (4, 'In Progress')], verbose_name='State code')),
            ],
            options={
                'verbose_name': 'Appointment State',
                'verbose_name_plural': 'Appointment States',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('schedule_date', models.DateField(verbose_name='Schedule Date')),
                ('start_time', models.TimeField(verbose_name='Start Time')),
                ('end_time', models.TimeField(verbose_name='End Time')),
                ('canceled', models.BooleanField(default=False, verbose_name='Canceled')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='schedules', to='clinic.doctor', verbose_name='Doctor')),
            ],
            options={
                'verbose_name': 'Schedule',
                'verbose_name_plural': 'Schedules',
            },
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('contact_number', models.CharField(max_length=15, verbose_name='Contact Number')),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Contact Email')),
                ('appointment_date_start', models.DateTimeField(verbose_name='Appointment date start')),
                ('appointment_date_end', models.DateTimeField(verbose_name='Appointment date end')),
                ('estimated_cost', models.FloatField(blank=True, default=0, null=True, verbose_name='Estimated Cost')),
                ('observations', models.TextField(blank=True, null=True, verbose_name='Observations')),
                ('appointment_state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='scheduling.appointmentstate', verbose_name='Appointment State')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='base.currency', verbose_name='Currency')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='clinic.doctor', verbose_name='Doctor')),
                ('insurance_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='clinic.insuranceplan', verbose_name='Insurance Plan')),
                ('medical_equipment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='clinic.medicalequipment', verbose_name='Medical Equipment')),
                ('medical_study', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='clinic.medicalstudy', verbose_name='Medical Study')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='appointments', to='clinic.patient', verbose_name='Patient')),
            ],
            options={
                'verbose_name': 'Appointment',
                'verbose_name_plural': 'Appointments',
            },
        ),
        migrations.CreateModel(
            name='DefaultDoctorAppointmentSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, db_index=True, default=None, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('day', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')], verbose_name='Day of the week')),
                ('start_time', models.TimeField(verbose_name='Start Time')),
                ('end_time', models.TimeField(verbose_name='End Time')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='default_doctor_schedules', to='clinic.doctor', verbose_name='Doctor')),
            ],
            options={
                'verbose_name': 'Default Doctor Appointment Schedule',
                'verbose_name_plural': 'Default Doctor Appointments Schedules',
                'unique_together': {('doctor', 'day', 'start_time', 'end_time')},
            },
        ),
    ]
