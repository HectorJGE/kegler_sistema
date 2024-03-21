from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _

from base.models import Currency
from clinic.models import InsurancePlan, InsurancePlanMedicalSupplyFee
from stock.models import Product


class Command(BaseCommand):
    help = _('Command to create missing medical supplies fees')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the creation of missing medical supplies fees.'))
        created = 0
        medical_supplies = Product.objects.all()
        insurance_plans = InsurancePlan.objects.all()
        currency = Currency.objects.get(code='PYG')
        for medical_supply in medical_supplies:
            for insurance_plan in insurance_plans:
                medical_supply_fee = InsurancePlanMedicalSupplyFee.objects.filter(
                    insurance_plan=insurance_plan,
                    medical_supply=medical_supply
                ).first()
                if medical_supply_fee is None:
                    new_medical_supply_fee = InsurancePlanMedicalSupplyFee.objects.create(
                        insurance_plan=insurance_plan,
                        medical_supply=medical_supply,
                        price=0,
                        currency=currency
                    )
                    self.stdout.write(_(u'Medical Supply fee created:'))
                    print(new_medical_supply_fee)
                    created = created + 1

        self.stdout.write(_(str(created) + u' new medical supplies fees were succesfully created!'))
