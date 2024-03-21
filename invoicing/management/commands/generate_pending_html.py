from base.helper import send_email
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _
from invoicing.models import InvoiceHeader, SifenTransaction, CreditNoteHeader
from invoicing.views import generate_sifen_pdf, generate_invoice_pdf_sifen_payload, send_payload, \
    invoice_base64_to_pdf, invoice_string_xml_to_xml, send_invoice_email_html, generate_credit_note_pdf_sifen_payload, \
    send_credit_note_email_html
from sistema.settings import SIFEN_MIDDLEWARE_GENERATE_INVOICE_PDF_URL, SIFEN_MIDDLEWARE_GENERATE_INVOICE_HTML_URL


class Command(BaseCommand):
    help = _('Command to create pdfs for those invoices that don`t have.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the creation of pdfs for those invoices that don`t have.'))
        invoices = InvoiceHeader.objects.filter(invoice_kude_html=None, invoice_xml_text__isnull=False,
                                                       invoice_cdc__isnull=False)
        credit_notes = CreditNoteHeader.objects.filter(credit_note_kude_html=None, credit_note_xml_text__isnull=False,
                                                       credit_note_cdc__isnull=False)

        for invoice in invoices:
            try:
                if invoice.invoice_stamp.electronic_stamp:
                    # Generate SIFEN PDF
                    print('Generando KUDE HTML de factura ' + invoice.invoice_number)
                    generate_sifen_invoice_html(invoice)
            except Exception as e:
                print(e)
                self.stdout.write(_(u'El KUDE HTML de la factura no pudo ser generado: Error-> ' + str(e)))

        for credit_note in credit_notes:
            try:
                if credit_note.credit_note_stamp.electronic_stamp:
                    # Generate SIFEN PDF
                    print('Generando KUDE HTML de nota de crédito ' + credit_note.credit_note_number)
                    generate_sifen_credit_note_html(credit_note)
            except Exception as e:
                print(e)
                self.stdout.write(_(u'El KUDE HTML de la nota de credito no pudo ser generado: Error-> ' + str(e)))


def generate_sifen_invoice_html(invoice_header):
    # Se genera la transaccion para el pdf
    transaction_log_html = SifenTransaction.objects.create(
        user=User.objects.get(username='systemuser'),
        url=None,
        invoice_header=invoice_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate payload de generar pdf, or html
    sifen_payload_html = generate_invoice_pdf_sifen_payload(invoice_header, transaction_id=transaction_log_html.id)
    # url to endpoint
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_HTML_URL

    # Send Sifen Payload Generar PDF, o HTML Factura
    transaction_log_html.payload = sifen_payload_html
    transaction_log_html.url = url
    transaction_log_html.save()
    sifen_response_html = send_payload(url, sifen_payload_html)

    # IF JSON ERROR
    if sifen_response_html == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        print('El HTML del KUDE no pudo ser creado: Error-> ' + error)
        transaction_log_html.response = error
        transaction_log_html.success = False
        transaction_log_html.save()
    else:
        print(sifen_response_html)
        transaction_log_html.response = sifen_response_html

        # Si la respuesta de generar html es exitosa
        if sifen_response_html['ok']:
            transaction_log_html.success = True
            transaction_log_html.save()

            invoice_header.invoice_kude_html = sifen_response_html['result']['kudeHtml']
            invoice_header.save()
            print('El HTML del KUDE fue generado satisfactoriamente')

            # Enviar correo si es que el cliente tiene correo
            if not invoice_header.invoice_email_sent:
                send_invoice_email_html(None, invoice_header)

        else:
            transaction_log_html.success = False
            transaction_log_html.save()
            print('No se pudo crear el PDF del KUDE: Error-> ' + sifen_response_html['error'])


def generate_sifen_credit_note_html(credit_note_header):
    # Se genera la transaccion para el html
    transaction_log_html = SifenTransaction.objects.create(
        user=User.objects.get(username='systemuser'),
        url=None,
        invoice_header=None,
        credit_note_header=credit_note_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate payload de generar html
    sifen_payload_html = generate_credit_note_pdf_sifen_payload(credit_note_header, transaction_id=transaction_log_html.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_HTML_URL

    # Send Sifen Payload Generar HTML Nota de credito
    transaction_log_html.payload = sifen_payload_html
    transaction_log_html.url = url
    transaction_log_html.save()
    sifen_response_html = send_payload(url, sifen_payload_html)

    # IF JSON ERROR
    if sifen_response_html == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        print('El HTML del KUDE no pudo ser creado: Error-> ' + error)
        transaction_log_html.response = error
        transaction_log_html.success = False
        transaction_log_html.save()
    else:
        print(sifen_response_html)
        transaction_log_html.response = sifen_response_html

        # Si la respuesta de generar html es exitosa
        if sifen_response_html['ok']:
            transaction_log_html.success = True
            transaction_log_html.save()

            credit_note_header.credit_note_kude_html = sifen_response_html['result']['kudeHtml']
            credit_note_header.save()
            print('El HTML del KUDE fue generado satisfactoriamente')

            # Enviar correo si es que el cliente tiene correo
            if not credit_note_header.credit_note_email_sent:
                send_credit_note_email_html(None, credit_note_header)

        else:
            transaction_log_html.success = False
            transaction_log_html.save()
            print('No se pudo crear el HTML del KUDE: Error-> ' + sifen_response_html['error'])
