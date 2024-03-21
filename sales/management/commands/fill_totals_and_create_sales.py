import datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from consultation.models import ConsultationEntrySheet
from sales.models import ConsultationEntrySheetSaleHeader, ConsultationSheetSaleDetail, ConsultationSheetSalePayment
from scheduling.models import DefaultDoctorAppointmentSchedule, Schedule


class Command(BaseCommand):
    help = _('Command to fill consultation entry sheets, consultation sheets new totals, and create sales from entry sheets')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting command to fill consultation entry sheets, consultation sheets new totals, and create sales from entry sheets'))
        sales_created = 0
        consultation_entry_sheets = ConsultationEntrySheet.objects.all()

        for consultation_entry_sheet in consultation_entry_sheets:
            consultation_sheets = consultation_entry_sheet.consultation_sheets.all()
            total_amount = 0
            total_amount_to_pay_insurance = 0
            total_amount_to_pay_patient = 0
            total_amount_paid_by_patient = 0
            patient_balance = 0

            for consultation_sheet in consultation_sheets:
                total_amount += consultation_sheet.total_amount
                total_amount_to_pay_insurance += consultation_sheet.total_ammount_to_pay_insurance
                total_amount_to_pay_patient += consultation_sheet.total_ammount_to_pay_patient_with_discount
                total_amount_paid_by_patient += consultation_sheet.amount_paid
                patient_balance += consultation_sheet.total_ammount_to_pay_patient_with_discount - consultation_sheet.amount_paid

                # filling new field patient balance on consultation sheet
                if consultation_sheet.amount_paid < 10000:
                    consultation_sheet.amount_paid = consultation_sheet.total_ammount_to_pay_patient_with_discount
                consultation_sheet.patient_balance = consultation_sheet.total_ammount_to_pay_patient_with_discount - consultation_sheet.amount_paid
                consultation_sheet.save()

            # filling new total fields on consultation entry sheet
            consultation_entry_sheet.total_amount = total_amount
            consultation_entry_sheet.total_amount_to_pay_insurance = total_amount_to_pay_insurance
            consultation_entry_sheet.total_amount_to_pay_patient = total_amount_to_pay_patient
            consultation_entry_sheet.total_amount_paid_by_patient = total_amount_paid_by_patient
            consultation_entry_sheet.patient_balance = patient_balance
            consultation_entry_sheet.save()

            sale_header = consultation_entry_sheet.sale_header if hasattr(consultation_entry_sheet, 'sale_header') else None

            if sale_header is None:
                print('Consultation Entry Sheet ID:' + str(consultation_entry_sheet.id))
                # creating new sale header
                new_sale = ConsultationEntrySheetSaleHeader.objects.create(
                    client_name=consultation_entry_sheet.patient.name + ' ' + consultation_entry_sheet.patient.last_name,
                    client_tax_identification_number=consultation_entry_sheet.patient.tax_identification_number,
                    sale_date=consultation_entry_sheet.consultation_entry_sheet_date,
                    sale_total=consultation_entry_sheet.total_amount_to_pay_patient,
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
                        unit_price=consultation_sheet.total_ammount_to_pay_patient_with_discount,
                        total_price=consultation_sheet.total_ammount_to_pay_patient_with_discount,
                        currency=consultation_sheet.currency,
                        sale_header=new_sale,
                        consultation_sheet=consultation_sheet
                    )
                    print(new_sale_detail)
                    sale_details_created += 1

                    if consultation_sheet.amount_paid > 0:
                        # creating new sale payments if consultation_sheet.amount_paid > 0
                        new_sale_payment = ConsultationSheetSalePayment.objects.create(
                            amount=consultation_sheet.amount_paid,
                            currency=consultation_sheet.currency,
                            payment_method=consultation_sheet.payment_method,
                            payment_datetime=consultation_sheet.consultation_date,
                            observations='Payment Created by fill_totals_and_create_sales command, for consultation sheets with amount_paid',
                            sale=new_sale,
                            consultation_sheet=consultation_sheet
                        )
                        print(new_sale_payment)
                        sale_payments_created += 1

                self.stdout.write(_(str(sale_details_created) + u' new sale details were succesfully created!'))
                self.stdout.write(_(str(sale_payments_created) + u' new sale payments were succesfully created!'))
            else:
                payments = sale_header.sale_payments.all()
                for payment in payments:
                    payment.amount = payment.consultation_sheet.amount_paid
                    payment.save()
                    print('Payment Updated:')
                    print(payment)

        self.stdout.write(_(str(sales_created) + u' new sales were succesfully created!'))
