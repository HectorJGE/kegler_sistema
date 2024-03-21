import datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from consultation.models import ConsultationEntrySheet
from scheduling.models import Appointment, AppointmentState


class Command(BaseCommand):
    help = _('Command to delete empty consultation entry sheets.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the process to delete empty consultation entry sheets.'))
        consultation_entry_sheets = ConsultationEntrySheet.objects.all()
        deleted_empty_consultation_entry_sheets = 0
        for consultation_entry_sheet in consultation_entry_sheets:
            if not consultation_entry_sheet.consultation_sheets.all():
                consultation_entry_sheet.delete()
                deleted_empty_consultation_entry_sheets += 1
                self.stdout.write(_(u'Consultation entry sheet deleted:'))
                print(consultation_entry_sheet)

        self.stdout.write(_(str(deleted_empty_consultation_entry_sheets) + u' empty consultation entry sheets deleted!'))
