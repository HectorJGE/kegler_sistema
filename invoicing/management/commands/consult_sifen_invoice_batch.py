from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _
from invoicing.models import InvoiceHeader, SifenTransaction, CreditNoteHeader
from invoicing.views import generate_invoice_batch_request_payload, send_payload, \
    generate_credit_note_batch_request_payload
from sistema.settings import SIFEN_MIDDLEWARE_REQUEST_INVOICE_BATCH_URL


class Command(BaseCommand):
    help = _('Command to consult batches to get invoices cdc sended in batch.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the consult of batches to get invoices, and credit note CDCs.'))
        invoices = InvoiceHeader.objects.filter(invoice_batch_sended=True, invoice_batch_id__isnull=False,
                                                       invoice_cdc=None)
        credit_notes = CreditNoteHeader.objects.filter(credit_note_batch_sended=True, credit_note_batch_id__isnull=False,
                                                       credit_note_cdc=None)

        for invoice in invoices:
            try:
                if invoice.invoice_stamp.electronic_stamp:
                    # Consult SIFEN invoice Batch
                    print('Consultando lote de factura ' + invoice.invoice_number)
                    consult_sifen_dte_invoice_batch(invoice)
            except Exception as e:
                print(e)
                self.stdout.write(_(u'El lote de facturas no pudo ser consultado: Error-> ' + str(e)))

        for credit_note in credit_notes:
            try:
                if credit_note.credit_note_stamp.electronic_stamp:
                    # Consult SIFEN credit note Batch
                    print('Consultando lote de Nota de credito ' + credit_note.credit_note_number)
                    consult_sifen_dte_credit_note_batch(credit_note)
            except Exception as e:
                print(e)
                self.stdout.write(_(u'El lote de notas de crédito no pudo ser consultado: Error-> ' + str(e)))


def consult_sifen_dte_invoice_batch(invoice_header):
    # Se genera la Transacción para consultar el estado del lote de facturas
    transaction_log = SifenTransaction.objects.create(
        user=User.objects.get(username='systemuser'),
        url=None,
        invoice_header=invoice_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate sifen invoice batch request Payload
    sifen_payload = generate_invoice_batch_request_payload(invoice_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_REQUEST_INVOICE_BATCH_URL

    # Send Sifen Payload Consultar Lote
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        print('El Lote de La Factura no pudo ser consultado en la SET: Error-> ' + error)
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
            invoice_header.invoice_cdc = sifen_response['result']['cdc']
            invoice_header.save()
            print('El Lote de facturas fue consultado correctamente en la SET')

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            print('El lote de facturas no pudo ser consultado en la SET: Error-> ' + sifen_response['error'])


def consult_sifen_dte_credit_note_batch(credit_note_header):
    # Se genera la Transacción para consultar el estado del lote de notas de creditos
    transaction_log = SifenTransaction.objects.create(
        user=User.objects.get(username='systemuser'),
        url=None,
        invoice_header=None,
        credit_note_header=credit_note_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate sifen invoice batch request Payload
    sifen_payload = generate_credit_note_batch_request_payload(credit_note_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_REQUEST_INVOICE_BATCH_URL

    # Send Sifen Payload Consultar Lote
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        print('El Lote de La Factura no pudo ser consultado en la SET: Error-> ' + error)
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
            credit_note_header.credit_note_cdc = sifen_response['result']['cdc']
            credit_note_header.save()
            print('El Lote de notas de crédito fue consultado correctamente en la SET')

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            print('El lote de notas de crédito no pudo ser consultado en la SET: Error-> ' + sifen_response['error'])
