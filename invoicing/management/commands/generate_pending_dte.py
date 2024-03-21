from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _
from invoicing.models import InvoiceHeader, SifenTransaction, CreditNoteHeader
from invoicing.views import generate_invoice_data_for_payload, \
    generate_invoice_sifen_payload, send_payload, generate_credit_note_data_for_payload, \
    generate_credit_note_sifen_payload
from sistema.settings import SIFEN_MIDDLEWARE_GENERATE_INVOICE_URL, SIFEN_MIDDLEWARE_GENERATE_INVOICE_BATCH_URL


class Command(BaseCommand):
    help = _('Command to create dtes for those invoices that don`t have.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the creation of dtes for those invoices or credit notes without it.'))

        invoices = InvoiceHeader.objects.filter(invoice_xml_text=None, invoice_cdc=None)
        credit_notes = CreditNoteHeader.objects.filter(credit_note_xml_text=None, credit_note_cdc=None)

        for invoice in invoices:
            try:
                if invoice.invoice_stamp.electronic_stamp:
                    # Generate SIFEN DTE
                    print('Generando lote de factura ' + invoice.invoice_number)
                    generate_sifen_invoice_dte_batch(invoice)
            except Exception as e:
                print(e)
                self.stdout.write(_(u'La Factura no pudo ser enviada a la SET: Error-> ' + str(e)))

        for credit_note in credit_notes:
            try:
                if credit_note.credit_note_stamp.electronic_stamp:
                    # Generate SIFEN DTE
                    print('Generando lote de Nota de Crédito ' + credit_note.credit_note_number)
                    generate_sifen_credit_note_dte_batch(credit_note)
            except Exception as e:
                print(e)
                self.stdout.write(_(u'La Nota de Crédito no pudo ser enviada a la SET: Error-> ' + str(e)))


def generate_sifen_dte(invoice_header):
    # Generar invoice data
    transaction_log = SifenTransaction.objects.create(
        user=User.objects.get(username='systemuser'),
        invoice_header=invoice_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate invoice data for payload
    invoice_data = generate_invoice_data_for_payload( User.objects.get(username='systemuser'), invoice_header)

    # Generate sifen Payload
    sifen_payload = generate_invoice_sifen_payload(invoice_data, invoice_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_URL

    # Send Sifen Payload Generar Factura
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        print('La Factura no pudo ser enviada a la SET: Error-> ' + error)
        transaction_log.response = error
        transaction_log.success = False
        transaction_log.save()
    else:
        print(sifen_response)
        transaction_log.response = sifen_response

        # Si la respuesta es exitosa
        if sifen_response['ok']:
            transaction_log.success = True
            transaction_log.save()
            invoice_header.invoice_xml_text = sifen_response['result']['xmlQrCode']
            invoice_header.invoice_cdc = sifen_response['result']['setResponse']['ns2:rRetEnviDe']['ns2:rProtDe'][
                'ns2:Id']

            # invoice_header.invoice_pdf_base64 = sifen_response['result']['kudeBase64']

            invoice_header.save()
            print('La Factura fue enviada correctamente a la SET')

            # generate_sifen_pdf(request, invoice_header)

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            print('La Factura no pudo ser enviada a la SET: Error-> ' + sifen_response['error'])


def generate_sifen_invoice_dte_batch(invoice_header):
    # Generar invoice data
    transaction_log = SifenTransaction.objects.create(
        user=User.objects.get(username='systemuser'),
        url=None,
        invoice_header=invoice_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate invoice data for payload
    invoice_data = generate_invoice_data_for_payload(User.objects.get(username='systemuser'), invoice_header)

    # Generate sifen Payload
    sifen_payload = generate_invoice_sifen_payload(invoice_data, invoice_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_BATCH_URL

    # Send Sifen Payload Generar Factura lote
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        print('La Factura no pudo ser enviada a la SET: Error-> ' + error)
        transaction_log.response = error
        transaction_log.success = False
        transaction_log.save()
    else:
        print(sifen_response)
        transaction_log.response = sifen_response

        # Si la respuesta es exitosa
        if sifen_response['ok']:
            transaction_log.success = True
            transaction_log.save()
            invoice_header.invoice_xml_text = sifen_response['result']['xmlQrCode']
            invoice_header.invoice_batch_id = sifen_response['result']['batchId']
            invoice_header.invoice_batch_sended = True

            invoice_header.save()
            print('La Factura fue enviada correctamente a la SET')

            # generate_sifen_pdf(request, invoice_header)

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            print('La Factura no pudo ser enviada a la SET: Error-> ' + sifen_response['error'])


def generate_sifen_credit_note_dte_batch(credit_note_header):
    # Generar credit note data
    transaction_log = SifenTransaction.objects.create(
        user=User.objects.get(username='systemuser'),
        url=None,
        invoice_header=None,
        credit_note_header=credit_note_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate credit_note data for payload
    invoice_data = generate_credit_note_data_for_payload(User.objects.get(username='systemuser'), credit_note_header)

    # Generate sifen Payload
    sifen_payload = generate_credit_note_sifen_payload(invoice_data, credit_note_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_BATCH_URL

    # Send Sifen Payload Generar Nota de credito
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        print('La Nota de crédito no pudo ser enviada a la SET: Error-> ' + error)
        transaction_log.response = error
        transaction_log.success = False
        transaction_log.save()
    else:
        print(sifen_response)
        transaction_log.response = sifen_response

        # Si la respuesta es exitosa
        if sifen_response['ok']:
            transaction_log.success = True
            transaction_log.save()
            credit_note_header.credit_note_xml_text = sifen_response['result']['xmlQrCode']
            credit_note_header.credit_note_batch_id = sifen_response['result']['batchId']
            credit_note_header.credit_note_batch_sended = True
            credit_note_header.save()
            print('La nota de crédito fue enviada correctamente a la SET')

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            print('La Nota de crédito no pudo ser enviada a la SET: Error-> ' + sifen_response['error'])
