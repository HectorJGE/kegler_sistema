import datetime

from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _

from base.models import Currency
from clinic.models import MedicalStudy, InsurancePlan, InsurancePlanMedicalStudyFee


class Command(BaseCommand):
    help = _('Command to create missing medical studies fees.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the creation of missing medical studies fees.'))
        created = 0
        medical_studies = MedicalStudy.objects.all()
        insurance_plans = InsurancePlan.objects.all()
        currency = Currency.objects.get(code='PYG')
        for medical_study in medical_studies:
            for insurance_plan in insurance_plans:
                medical_study_fee = InsurancePlanMedicalStudyFee.objects.filter(
                    insurance_plan=insurance_plan,
                    medical_study=medical_study
                ).first()
                if medical_study_fee is None:
                    new_medical_study_fee = InsurancePlanMedicalStudyFee.objects.create(
                        insurance_plan=insurance_plan,
                        medical_study=medical_study,
                        price=0,
                        currency=currency
                    )
                    self.stdout.write(_(u'Medical Study fee created:'))
                    print(new_medical_study_fee)
                    created = created + 1

        self.stdout.write(_(str(created) + u' new medical studies were succesfully created!'))
