from base.helper import send_email
from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _
from invoicing.models import InvoiceHeader, SifenTransaction
from invoicing.views import generate_sifen_pdf, generate_invoice_pdf_sifen_payload, send_payload, \
    invoice_base64_to_pdf, invoice_string_xml_to_xml
from sistema.settings import SIFEN_MIDDLEWARE_GENERATE_INVOICE_PDF_URL


class Command(BaseCommand):
    help = _('Command to create pdfs for those invoices that don`t have.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the creation of pdfs for those invoices that don`t have.'))
        invoices_header = InvoiceHeader.objects.filter(invoice_pdf_base64=None, invoice_xml_text__isnull=False,
                                                       invoice_cdc__isnull=False)

        for invoice in invoices_header:
            try:
                if invoice.invoice_stamp.electronic_stamp:
                    # Generate SIFEN PDF
                    print('Generando pdf de factura ' + invoice.invoice_number)
                    generate_sifen_pdf(invoice)
            except Exception as e:
                print(e)
                self.stdout.write(_(u'El pdf de la factura KUDE no pudo ser generado: Error-> ' + str(e)))


def generate_sifen_pdf(invoice_header):
    # Se genera la transaccion para el pdf
    transaction_log_pdf = SifenTransaction.objects.create(
        user=User.objects.get(username='systemuser'),
        url=None,
        invoice_header=invoice_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate payload de generar pdf
    sifen_payload_pdf = generate_invoice_pdf_sifen_payload(invoice_header, transaction_id=transaction_log_pdf.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_PDF_URL

    # Send Sifen Payload Generar PDF Factura
    transaction_log_pdf.payload = sifen_payload_pdf
    transaction_log_pdf.url = url
    transaction_log_pdf.save()
    sifen_response_pdf = send_payload(url, sifen_payload_pdf)

    # IF JSON ERROR
    if sifen_response_pdf == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        print('El PDF del KUDE no pudo ser creado: Error-> ' + error)
        transaction_log_pdf.response = error
        transaction_log_pdf.success = False
        transaction_log_pdf.save()
    else:
        print(sifen_response_pdf)
        transaction_log_pdf.response = sifen_response_pdf

        # Si la respuesta de generar pdf es exitosa
        if sifen_response_pdf['ok']:
            transaction_log_pdf.success = True
            transaction_log_pdf.save()

            invoice_header.invoice_pdf_base64 = sifen_response_pdf['result']['kudeBase64']
            invoice_header.save()
            print('El PDF del KUDE fue generado satisfactoriamente')

            # Enviar correo si es que el cliente tiene correo
            send_invoice_email(invoice_header)

        else:
            transaction_log_pdf.success = False
            transaction_log_pdf.save()
            print('No se pudo crear el PDF del KUDE: Error-> ' + sifen_response_pdf['error'])



def send_invoice_email(invoice_header):
    if invoice_header.customer.customer_email:
        asunto = invoice_header.company.sifen_business_name + \
                 ' - Factura Electrónica - ' + invoice_header.invoice_number
        recipientes = invoice_header.customer.customer_email
        prioridad = 'now'
        con_template = False
        contexto = ''
        template = ''
        mensaje = 'Hola ' + invoice_header.customer.customer_name + ':\n ' \
                  'Adjuntamos tus comprobantes legales.\n ' \
                  'Puedes consultar los datos de tu factura en https://ekuatia.set.gov.py/consultas ingresando ' \
                  'el CDC citado aquí abajo, o escaneando el Código QR que aparece en el PDF.\n' \
                  'El CDC de tu factura es: ' + invoice_header.invoice_cdc + '\n ' \
                  'Saludos\n' + invoice_header.company.sifen_business_name
        mensaje_html = ''
        files = []
        pdf_file = invoice_base64_to_pdf(invoice_header)
        xml_file = invoice_string_xml_to_xml(invoice_header)
        files.append(pdf_file)
        files.append(xml_file)
        try:
            email = send_email(
                asunto=asunto,
                recipientes=recipientes,
                prioridad=prioridad,
                con_template=con_template,
                contexto=contexto,
                template=template,
                mensaje=mensaje,
                mensaje_html=mensaje_html,
                archivos=files
            )
            print(email)
            invoice_header.invoice_email_sent = True
            invoice_header.save()
            print('La Factura fue enviada correctamente por email al cliente!')
        except Exception as e:
            print(e)
            print('La Factura no pudo ser enviada por email al cliente: Error-> ' + str(e))

