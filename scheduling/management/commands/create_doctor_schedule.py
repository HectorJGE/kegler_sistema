import datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scheduling.models import DefaultDoctorAppointmentSchedule, Schedule


class Command(BaseCommand):
    help = _('Command to create doctors schedules for the month.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the creation of the doctors schedules for the month.'))
        today = datetime.datetime.today()
        today = timezone.make_aware(today)
        days = list(range(0, 27))
        first_day = True
        created = 0
        for day in days:
            if first_day:
                first_day = False
                schedule_date = today
            else:
                schedule_date = today + datetime.timedelta(days=day)

            weekday = schedule_date.weekday()
            doctors_default_schedules = DefaultDoctorAppointmentSchedule.objects.filter(day=weekday)
            for doctor_default_schedule in doctors_default_schedules:
                existing_schedules = Schedule.objects.filter(
                    doctor=doctor_default_schedule.doctor,
                    schedule_date=schedule_date,
                    start_time=doctor_default_schedule.start_time,
                    end_time=doctor_default_schedule.end_time
                ).first()

                if existing_schedules is None:
                    new_schedule = Schedule.objects.create(
                        schedule_date=schedule_date,
                        start_time=doctor_default_schedule.start_time,
                        end_time=doctor_default_schedule.end_time,
                        doctor=doctor_default_schedule.doctor
                    )
                    self.stdout.write(_(u'Doctors schedule created:'))
                    print(new_schedule)
                    created = created + 1
        self.stdout.write(_(str(created) + u' new doctors schedules were succesfully created!'))
