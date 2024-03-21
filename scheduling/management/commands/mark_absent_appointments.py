import datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from scheduling.models import Appointment, AppointmentState


class Command(BaseCommand):
    help = _('Command to mark missed appointments.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the process to mark missed appointments.'))
        now = timezone.now()
        scheduled_state = AppointmentState.objects.get(state_code=AppointmentState.SCHEDULED_STATE)
        absent_state = AppointmentState.objects.get(state_code=AppointmentState.ABSENT_STATE)
        missed_appointments = Appointment.objects.filter(appointment_date_start__lt=now, appointment_state=scheduled_state)
        missed_appointments_marked = 0
        for appointment in missed_appointments:
            appointment.appointment_state = absent_state
            appointment.save()
            missed_appointments_marked += 1
            self.stdout.write(_(u'Appointment marked as absent:'))
            print(appointment)

        self.stdout.write(_(str(missed_appointments_marked) + u' missed appointments marked as absent!'))
