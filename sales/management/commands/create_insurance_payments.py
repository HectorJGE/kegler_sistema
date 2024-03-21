import datetime

from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _

from consultation.models import ConsultationEntrySheet
from invoicing.models import PaymentMethod
from sales.models import ConsultationEntrySheetSaleHeader, ConsultationSheetSaleDetail, ConsultationSheetSalePayment


class Command(BaseCommand):
    help = _('Command to create insurance sale and payments in consultation sheets.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting create insurance payments in consultation sheets.'))
        consultation_entry_sheets = ConsultationEntrySheet.objects.all()
        sales_created = 0
        payment_method_insurance = PaymentMethod.objects.get(abbreviation='CS')
        sale_details_created = 0
        sale_payments_created = 0

        for consultation_entry_sheet in consultation_entry_sheets:

            if consultation_entry_sheet.total_amount_to_pay_insurance > 0 and consultation_entry_sheet.patient.insurance_plan:
                consultation_sheets = consultation_entry_sheet.consultation_sheets.all()
                previous_insurance_sales_created = consultation_entry_sheet.sale_header.filter(client_name=consultation_entry_sheet.patient.insurance_plan.insurance_company.name)
                if not previous_insurance_sales_created:

                    print('Consultation Entry Sheet ID:' + str(consultation_entry_sheet.id))
                    # creating new sale header
                    new_sale = ConsultationEntrySheetSaleHeader.objects.create(
                        client_name=consultation_entry_sheet.patient.insurance_plan.insurance_company.name,
                        client_tax_identification_number=consultation_entry_sheet.patient.insurance_plan.insurance_company.tax_identification_number,
                        sale_date=consultation_entry_sheet.consultation_entry_sheet_date,
                        sale_total=consultation_entry_sheet.total_amount_to_pay_insurance,
                        currency=consultation_entry_sheet.currency,
                        consultation_entry_sheet=consultation_entry_sheet
                    )
                    self.stdout.write(_(u'Sale created:'))
                    print(new_sale)
                    sales_created += 1

                    sale_details_created = 0
                    sale_payments_created = 0
                    for consultation_sheet in consultation_sheets:
                        # creating new sale details
                        new_sale_detail = ConsultationSheetSaleDetail.objects.create(
                            quantity=1,
                            description=consultation_sheet.medical_study.name,
                            unit_price=consultation_sheet.total_ammount_to_pay_insurance,
                            total_price=consultation_sheet.total_ammount_to_pay_insurance,
                            currency=consultation_sheet.currency,
                            sale_header=new_sale,
                            consultation_sheet=consultation_sheet
                        )
                        print(new_sale_detail)
                        sale_details_created += 1

                        if consultation_sheet.amount_paid > 0:
                            new_sale_payment = ConsultationSheetSalePayment.objects.create(
                                amount=consultation_sheet.total_ammount_to_pay_insurance,
                                currency=consultation_sheet.currency,
                                payment_method=payment_method_insurance,
                                payment_datetime=consultation_sheet.consultation_date,
                                observations='Payment Created by create_insurance_payments command, for consultation sheets with total_amount_to_pay_insurance > 0',
                                sale=new_sale,
                                consultation_sheet=consultation_sheet
                            )
                            print(new_sale_payment)
                            sale_payments_created += 1

                self.stdout.write(_(str(sale_details_created) + u' new sale details were succesfully created!'))
                self.stdout.write(_(str(sale_payments_created) + u' new sale payments were succesfully created!'))

        self.stdout.write(_(str(sales_created) + u' new sales were succesfully created!'))
