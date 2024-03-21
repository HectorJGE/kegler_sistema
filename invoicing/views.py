import base64
import io
import json
import locale
import tempfile
from io import BytesIO

from babel.dates import format_date
from datatableview.views import DatatableView
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from datatableview import Datatable, columns
from datetime import date, datetime, timedelta
from django.db import transaction
from django.template import RequestContext, loader
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import *
from pip._vendor import requests

from base.helper import send_email
from clinic.models import Patient, MedicalStudyType, Sector
from consultation.models import *
from reports.forms import InsurancesAgreementsReportFiltersForm
from .forms import *
from .models import *
from sistema.settings import *
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class InvoiceDatatable(Datatable):
    actions = columns.DisplayColumn(_('Actions'), processor='get_actions')
    invoice_date = columns.DisplayColumn(_('Invoice date'), processor='get_invoice_date')
    details = columns.DisplayColumn(_('Details'), processor='get_details')
    # invoice_pdf_base64 = columns.DisplayColumn(_('PDF SIFEN'), processor='get_pdf')
    invoice_kude_html = columns.DisplayColumn(_('KUDE HTML'), processor='get_kude')
    invoice_email_sent = columns.DisplayColumn(_('Invoice Email Sent'), processor='get_email_sent')
    credit_note = columns.DisplayColumn(_('Credit Note'), processor='get_credit_note')

    class Meta:
        model = InvoiceHeader
        columns = ['actions',
                   'id',
                   'company',
                   'invoice_number',
                   'client_name',
                   'client_tax_identification_number',
                   'invoice_date',
                   'details',
                   'payment_term',
                   'invoice_total',
                   'invoice_email_sent',
                   'invoice_kude_html',
                   'credit_note',
                   ]

        search_fields = ['id',
                         'invoice_number',
                         'company',
                         'client_name',
                         'client_tax_identification_number',
                         'invoice_date',
                         'invoice_total'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_actions(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        detail_url = reverse('invoice_detail', args=[rid])
        update_url = reverse('invoice_update', args=[rid])
        delete_url = reverse('invoice_delete', args=[rid])
        print_url = reverse('invoice.print', args=[rid])
        print_preview_url = reverse('invoice.print_invoice_preview_html', args=[rid])

        str_div_print = ""
        str_div_edit = ""
        str_div_delete = ""

        if instance.invoice_cdc is None:
            str_div_print = """
                        <div class="col ">
                            <a href="{}" target="_blank" class="btn btn-info btn-circle">
                                <i class="fas fa-print"></i>
                            </a>
                        </div>
            """.format(print_preview_url)

            str_div_edit = """
                                <div class="col ">
                                    <a href="{}" class="btn btn-info btn-circle">
                                        <i class="fas fa-pencil-alt"></i>
                                    </a>
                                </div>
                    """.format(update_url)

            str_div_delete = """
                                <div class="col ">
                                    <a href="{}" class="btn btn-info btn-circle">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                    """.format(delete_url)

        str_div_detail = """
                    <div class="col ">
                        <a href="{}" class="btn btn-info btn-circle">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
        """.format(detail_url)

        str_div_container = """
               <div class="container">
                       <div class="row">
                           {}
                           {}
                           {}
                           {}
                       </div>
               </div>
        """.format(str_div_print, str_div_detail, str_div_edit, str_div_delete)

        return str_div_container

    @staticmethod
    def get_details(instance, view, *args, **kwargs):
        details = instance.invoice_details.all()

        a = "<div><ul>"
        b = ""
        c = "</ul></div>"
        for detail in details:
            b += "<li>" + str(detail.description) + "</li>"
        result = a + b + c
        return """{}""".format(result)

    @staticmethod
    def get_pdf(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        send_invoice_to_sifen_url = reverse('invoice.send_to_sifen', args=[rid])
        generate_sifen_pdf_url = reverse('invoice.generate_sifen_pdf', args=[rid])
        download_invoice_pdf = reverse('invoice.download_invoice_pdf', args=[rid])
        consult_invoice_batch_sifen_url = reverse('invoice.consult_invoice_batch_sifen', args=[rid])

        pdf_base_64 = instance.invoice_pdf_base64

        # Si tiene timbrado electrónico
        if instance.invoice_stamp.electronic_stamp:
            # si no tiene pdf, si no tiene cdc, si no fue enviado por lote, aparece el botón enviar
            if pdf_base_64 is None and instance.invoice_cdc is None and instance.invoice_batch_sended is False:
                result = """
                <div class="col ">
                            <p>Enviar DE</p>
                            <a href="{}" class="btn btn-info btn-circle">
                                <i class="fas fa-upload"></i>
                            </a>
                        </div>
                """.format(send_invoice_to_sifen_url)
            # si fue enviado por lote, y si tiene lote id aparece el botón consultar lote
            elif (instance.invoice_batch_sended is True and instance.invoice_batch_id is not None
                  and instance.invoice_cdc is None):
                result = """
                            <div class="col ">
                                        <p>Consultar envío de Lote</p>
                                        <a href="{}" class="btn btn-info btn-circle">
                                            <i class="fas fa-upload"></i>
                                        </a>
                                    </div>
                            """.format(consult_invoice_batch_sifen_url)
            # si no tiene pdf y tiene cdc aparece el botón generar kude
            elif pdf_base_64 is None and instance.invoice_cdc is not None:
                result = """
                            <div class="col ">
                                        <p>Generar y Enviar PDF KUDE</p>
                                        <a href="{}" class="btn btn-info btn-circle">
                                            <i class="fas fa-upload"></i>
                                        </a>
                                    </div>
                            """.format(generate_sifen_pdf_url)

            else:
                result = """
                <a href="{}"> Descargar PDF SIFEN
                </a>
                """.format(download_invoice_pdf)
        else:
            result = """ """
        return result

    @staticmethod
    def get_kude(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        send_invoice_to_sifen_url = reverse('invoice.send_to_sifen', args=[rid])
        generate_sifen_html_url = reverse('invoice.generate_sifen_html', args=[rid])
        show_invoice_html = reverse('invoice.show_invoice_html', args=[rid])
        consult_invoice_batch_sifen_url = reverse('invoice.consult_invoice_batch_sifen', args=[rid])

        kude_html = instance.invoice_kude_html

        # Si tiene timbrado electrónico
        if instance.invoice_stamp.electronic_stamp:
            # si no tiene html, si no tiene cdc, si no fue enviado por lote, aparece el botón enviar
            if kude_html is None and instance.invoice_cdc is None and instance.invoice_batch_sended is False:
                result = """
                <div class="col ">
                            <p>Enviar DE</p>
                            <a href="{}" class="btn btn-info btn-circle">
                                <i class="fas fa-upload"></i>
                            </a>
                        </div>
                """.format(send_invoice_to_sifen_url)
            # si fue enviado por lote, y si tiene lote id aparece el botón consultar lote
            elif (instance.invoice_batch_sended is True and instance.invoice_batch_id is not None
                  and instance.invoice_cdc is None):
                result = """
                            <div class="col ">
                                        <p>Consultar envío de Lote</p>
                                        <a href="{}" class="btn btn-info btn-circle">
                                            <i class="fas fa-upload"></i>
                                        </a>
                                    </div>
                            """.format(consult_invoice_batch_sifen_url)
            # si no tiene kude_html y tiene cdc aparece el botón generar kude
            elif kude_html is None and instance.invoice_cdc is not None:
                result = """
                            <div class="col ">
                                        <p>Generar y Enviar KUDE HTML</p>
                                        <a href="{}" class="btn btn-info btn-circle">
                                            <i class="fas fa-upload"></i>
                                        </a>
                                    </div>
                            """.format(generate_sifen_html_url)

            else:
                result = """
                <a href="{}" target="_blank"> Mostrar KUDE HTML
                </a>
                """.format(show_invoice_html)
        else:
            result = """ """
        return result

    @staticmethod
    def get_invoice_date(instance, view, *args, **kwargs):
        return datetime.strftime(instance.invoice_date, '%d/%m/%Y')

    @staticmethod
    def get_email_sent(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        invoice_email_send_to_client_url = reverse('invoice.email_send_to_client', args=[rid])
        result = ''
        if instance.invoice_email_sent and instance.invoice_kude_html is not None:
            result = """
                <div class="col ">
                            <b>Si</b>
                            <a href="{}"> (Reenviar)
                    </a>
                </div>
                
                """.format(invoice_email_send_to_client_url)

        elif not instance.invoice_email_sent and instance.invoice_kude_html is not None:
            result = """
                <div class="col ">
                    <b>No</b>
                    <a href="{}"> (Reenviar)
                    </a>
                </div>
                
                """.format(invoice_email_send_to_client_url)
        else:
            result = """
                            <div class="col ">
                                <b>No</b>
                            </div>

                            """
        return result

    @staticmethod
    def get_credit_note(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        try:
            credit_note_headers = CreditNoteHeader.objects.filter(invoice_header=instance)
            credit_note_urls = []
            for credit_note_header in credit_note_headers:
                credit_note_urls.append(
                    reverse('credit_note_detail', args=[credit_note_header.id])
                )

        except CreditNoteHeader.DoesNotExist:
            credit_note_urls = []

        if not credit_note_urls:
            create_credit_note_url = reverse('credit_note.create_from_invoice', args=[rid])
            result = """
                    <div class="col ">
                                <b>Sin nota de crédito</b>
                                <a href="{}"><b>(Crear)</b></a>
                            </div>
                    """.format(create_credit_note_url)

        else:
            links = ''
            i = 0
            for cn in credit_note_headers:
                links = links + """<li><a href="{}"> {}</a></li>""".format(
                    credit_note_urls[i], str(cn)
                )
                i = i+1

            result = """<div class="col "><ul>{}</ul></div>""".format(links)

        return result


class CreditNoteDatatable(Datatable):
    actions = columns.DisplayColumn(_('Actions'), processor='get_actions')
    credit_note_date = columns.DisplayColumn(_('Credit note date'), processor='get_credit_note_date')
    details = columns.DisplayColumn(_('Details'), processor='get_details')
    # credit_note_pdf_base64 = columns.DisplayColumn(_('PDF SIFEN'), processor='get_pdf')
    credit_note_kude_html = columns.DisplayColumn(_('KUDE HTML'), processor='get_kude')
    credit_note_email_sent = columns.DisplayColumn(_('Credit Note Email Sent'), processor='get_email_sent')

    class Meta:
        model = CreditNoteHeader
        columns = ['actions',
                   'id',
                   'company',
                   'invoice_header',
                   'credit_note_number',
                   'client_name',
                   'client_tax_identification_number',
                   'credit_note_date',
                   'details',
                   'credit_note_total',
                   'credit_note_email_sent',
                   # 'credit_note_pdf_base64'
                   'credit_note_kude_html'
                   ]

        search_fields = ['id',
                         'credit_note_number',
                         'company',
                         'client_name',
                         'client_tax_identification_number',
                         'credit_note_date',
                         'credit_note_total'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_actions(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        detail_url = reverse('credit_note_detail', args=[rid])
        update_url = reverse('credit_note_update', args=[rid])
        delete_url = reverse('credit_note_delete', args=[rid])

        str_div_edit = ""
        str_div_delete = ""

        if instance.credit_note_cdc is None:
            str_div_edit = """
                                <div class="col ">
                                    <a href="{}" class="btn btn-info btn-circle">
                                        <i class="fas fa-pencil-alt"></i>
                                    </a>
                                </div>
                    """.format(update_url)

            str_div_delete = """
                                <div class="col ">
                                    <a href="{}" class="btn btn-info btn-circle">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </div>
                    """.format(delete_url)

        str_div_detail = """
                    <div class="col ">
                        <a href="{}" class="btn btn-info btn-circle">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
        """.format(detail_url)

        str_div_container = """
               <div class="container">
                       <div class="row">
                           {}
                           {}
                           {}
                       </div>
               </div>
        """.format(str_div_detail, str_div_edit, str_div_delete)

        return str_div_container

    @staticmethod
    def get_details(instance, view, *args, **kwargs):
        details = instance.credit_note_details.all()

        a = "<div><ul>"
        b = ""
        c = "</ul></div>"
        for detail in details:
            b += "<li>" + str(detail.description) + "</li>"
        result = a + b + c
        return """{}""".format(result)

    @staticmethod
    def get_pdf(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        send_credit_note_to_sifen_url = reverse('credit_note.send_to_sifen', args=[rid])
        generate_sifen_pdf_url = reverse('credit_note.generate_sifen_pdf', args=[rid])
        download_credit_note_pdf = reverse('credit_note.download_pdf', args=[rid])
        consult_credit_note_batch_sifen_url = reverse('credit_note.consult_credit_note_batch_sifen', args=[rid])

        pdf_base_64 = instance.credit_note_pdf_base64
        # Si tiene timbrado electrónico
        if instance.credit_note_stamp.electronic_stamp:
            # si no tiene pdf, si no tiene cdc, si no fue enviado por lote, aparece el botón enviar
            if pdf_base_64 is None and instance.credit_note_cdc is None and instance.credit_note_batch_sended is False:
                result = """
                <div class="col ">
                            <p>Enviar DE</p>
                            <a href="{}" class="btn btn-info btn-circle">
                                <i class="fas fa-upload"></i>
                            </a>
                        </div>
                """.format(send_credit_note_to_sifen_url)
            # si fue enviado por lote, y si tiene lote id aparece el botón consultar lote
            elif (instance.credit_note_batch_sended is True and instance.credit_note_batch_id is not None
                  and instance.credit_note_cdc is None):
                result = """
                            <div class="col ">
                                        <p>Consultar envío de Lote</p>
                                        <a href="{}" class="btn btn-info btn-circle">
                                            <i class="fas fa-upload"></i>
                                        </a>
                                    </div>
                            """.format(consult_credit_note_batch_sifen_url)
            # si no tiene pdf y tiene cdc aparece el botón generar kude
            elif pdf_base_64 is None and instance.credit_note_cdc is not None:
                result = """
                            <div class="col ">
                                        <p>Generar y Enviar PDF KUDE</p>
                                        <a href="{}" class="btn btn-info btn-circle">
                                            <i class="fas fa-upload"></i>
                                        </a>
                                    </div>
                            """.format(generate_sifen_pdf_url)

            else:
                result = """
                <a href="{}"> Descargar PDF SIFEN
                </a>
                """.format(download_credit_note_pdf)
        else:
            result = """ """
        return result

    @staticmethod
    def get_kude(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        send_credit_note_to_sifen_url = reverse('credit_note.send_to_sifen', args=[rid])
        generate_sifen_html_url = reverse('credit_note.generate_sifen_html', args=[rid])
        show_credit_note_html = reverse('credit_note.show_credit_note_html', args=[rid])
        consult_credit_note_batch_sifen_url = reverse('credit_note.consult_credit_note_batch_sifen', args=[rid])

        kude_html = instance.credit_note_kude_html

        # Si tiene timbrado electrónico
        if instance.credit_note_stamp.electronic_stamp:
            # si no tiene html, si no tiene cdc, si no fue enviado por lote, aparece el botón enviar
            if kude_html is None and instance.credit_note_cdc is None and instance.credit_note_batch_sended is False:
                result = """
                    <div class="col ">
                                <p>Enviar DE</p>
                                <a href="{}" class="btn btn-info btn-circle">
                                    <i class="fas fa-upload"></i>
                                </a>
                            </div>
                    """.format(send_credit_note_to_sifen_url)
            # si fue enviado por lote, y si tiene lote id aparece el botón consultar lote
            elif (instance.credit_note_batch_sended is True and instance.credit_note_batch_id is not None
                  and instance.credit_note_cdc is None):
                result = """
                                <div class="col ">
                                            <p>Consultar envío de Lote</p>
                                            <a href="{}" class="btn btn-info btn-circle">
                                                <i class="fas fa-upload"></i>
                                            </a>
                                        </div>
                                """.format(consult_credit_note_batch_sifen_url)
            # si no tiene pdf y tiene cdc aparece el botón generar kude
            elif kude_html is None and instance.credit_note_cdc is not None:
                result = """
                                <div class="col ">
                                            <p>Generar y Enviar KUDE HTML</p>
                                            <a href="{}" class="btn btn-info btn-circle">
                                                <i class="fas fa-upload"></i>
                                            </a>
                                        </div>
                                """.format(generate_sifen_html_url)

            else:
                result = """
                    <a href="{}" target="_blank"> Mostrar KUDE HTML
                    </a>
                    """.format(show_credit_note_html)
        else:
            result = """ """
        return result

    @staticmethod
    def get_credit_note_date(instance, view, *args, **kwargs):
        return datetime.strftime(instance.credit_note_date, '%d/%m/%Y')

    @staticmethod
    def get_email_sent(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        credit_note_email_send_to_client_url = reverse('credit_note.email_send_to_client', args=[rid])
        result = ''
        if instance.credit_note_email_sent and instance.credit_note_kude_html is not None:
            result = """
                <div class="col ">
                            <b>Si</b>
                        <a href="{}"> (Reenviar)
                    </a>
                </div>

                """.format(credit_note_email_send_to_client_url)

        elif not instance.credit_note_email_sent and instance.credit_note_kude_html is not None:
            result = """
                <div class="col ">
                    <b>No</b>
                    <a href="{}"> (Reenviar)
                    </a>
                </div>

                """.format(credit_note_email_send_to_client_url)
        else:
            result = """
                            <div class="col ">
                                <b>No</b>
                            </div>

                            """
        return result


class InvoiceDataTableView(DatatableView):
    model = InvoiceHeader
    datatable_class = InvoiceDatatable
    template_name = "invoicing/invoice_list.html"


class CreditNoteDataTableView(DatatableView):
    model = CreditNoteHeader
    datatable_class = CreditNoteDatatable
    template_name = "invoicing/credit_note/credit_note_list.html"


class InvoiceListView(ListView):
    model = InvoiceHeader
    template_name = "invoicing/invoice_list.html"
    context_object_name = 'invoice'


class InvoiceDetailsView(DetailView):
    model = InvoiceHeader
    template_name = "invoicing/invoice_detail.html"
    context_object_name = 'invoice'


class CreditNoteDetailsView(DetailView):
    model = CreditNoteHeader
    template_name = "invoicing/credit_note/credit_note_detail.html"
    context_object_name = 'credit_note'


class InvoiceUpdateView(UpdateView):
    model = InvoiceHeader
    template_name = "invoicing/invoice_update.html"
    form_class = InvoiceUpdateForm
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super(InvoiceUpdateView, self).get_context_data(**kwargs)

        if self.request.POST:
            context.update(
                {
                    'detail_formset': InvoiceDetailsFormSet(self.request.POST, instance=self.get_object()),
                }
            )
        else:
            context.update(
                {
                    'detail_formset': InvoiceDetailsFormSet(instance=self.get_object()),
                }
            )
        return context

    def get_initial(self):
        customer = self.object.customer
        initial = {
            'client_tax_payer': customer.is_taxpayer
        }
        return initial

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        details_formset = context['detail_formset']

        # Validate RUC
        customer_tax_payer = form.cleaned_data['client_tax_payer']
        if customer_tax_payer:
            response = validate_ruc_set(form.data['client_tax_identification_number'])

            if not response['ok']:
                messages.error(self.request, 'RUC inválido en la SET: Error-> ' + response['error'])
                return self.render_to_response(self.get_context_data(form=form))

        invoice_header = form.save()
        customer_name = invoice_header.client_name
        customer_ruc = invoice_header.client_tax_identification_number
        customer_email = invoice_header.client_email
        customer_address = invoice_header.client_address
        customer_phone_number = invoice_header.client_phone_number

        # Verifica si existe ya un cliente guardado en la factura.
        # En caso de no contar con eso, busca un cliente con ese ruc, si no hay ese cliente lo crea si hay lo actualiza

        # Si la factura no viene con un cliente seteado
        if invoice_header.customer is None:
            customer = Customer.objects.filter(customer_tax_id_number=customer_ruc).first()
            patient = Patient.objects.filter(tax_identification_number=customer_ruc).first()
            if customer:
                print("cliente ya existe")
                # Se actualizan los datos del customer
                customer.customer_tax_id_number = customer_ruc
                customer.customer_name = customer_name
                customer.customer_email = customer_email
                customer.customer_address = customer_address
                customer.customer_phone_number = customer_phone_number
                customer.is_taxpayer = customer_tax_payer
                customer.patient = patient
                customer.save()

                invoice_header.customer = customer
                invoice_header.save()
            else:
                patient = Patient.objects.filter(tax_identification_number=customer_ruc).first()
                customer = Customer.objects.create(
                    customer_name=customer_name,
                    customer_tax_id_number=customer_ruc,
                    patient=patient,
                    customer_email=customer_email,
                    customer_address=customer_address,
                    customer_phone_number=customer_phone_number,
                    is_taxpayer=customer_tax_payer
                )
                invoice_header.customer = customer
                invoice_header.save()

        # Si la factura ya viene con un cliente seteado
        else:
            patient = Patient.objects.filter(tax_identification_number=customer_ruc).first()
            if patient is None:
                ruc_str_sin_dv = customer_ruc.split("-")[0]
                patient = Patient.objects.filter(document_number=ruc_str_sin_dv).first()

            customer = invoice_header.customer
            # Se actualizan los datos del customer
            customer.patient = patient
            customer.customer_tax_id_number = customer_ruc
            customer.customer_name = customer_name
            customer.customer_email = customer_email
            customer.customer_address = customer_address
            customer.customer_phone_number = customer_phone_number
            customer.is_taxpayer = customer_tax_payer

            customer.save()

            if patient:
                patient.tax_identification_number = customer.customer_tax_id_number
                patient.tax_identification_name = customer.customer_name
                patient.is_taxpayer = customer.is_taxpayer
                patient.save()

            invoice_header.customer = customer
            invoice_header.save()

        if details_formset.is_valid():
            details_formset.instance = invoice_header
            details_formset.save()
            messages.success(self.request, 'Factura modificada satisfactoriamente.')
            return HttpResponseRedirect(
                reverse('invoice_list'))
        else:
            messages.error(self.request, 'Error al tratar de modificar.')
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        print("Formulario no valido")
        error = form.errors
        print(error)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('invoice_list')


class CreditNoteUpdateView(UpdateView):
    model = CreditNoteHeader
    template_name = "invoicing/credit_note/credit_note_update.html"
    form_class = CreditNoteHeaderUpdateForm
    context_object_name = 'credit_note'

    def get_context_data(self, **kwargs):
        context = super(CreditNoteUpdateView, self).get_context_data(**kwargs)

        if self.request.POST:
            context.update(
                {
                    'detail_formset': CreditNoteDetailsFormSet(self.request.POST, instance=self.get_object()),
                }
            )
        else:
            context.update(
                {
                    'detail_formset': CreditNoteDetailsFormSet(instance=self.get_object()),
                }
            )
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        details_formset = context['detail_formset']

        # Validate RUC
        response = validate_ruc_set(form.data['client_tax_identification_number'])

        if not response['ok']:
            messages.error(self.request, 'RUC ivalido en la SET: Error-> ' + response['error'])
            return self.render_to_response(self.get_context_data(form=form))

        credit_note_header = form.save()
        customer_name = credit_note_header.client_name
        customer_ruc = credit_note_header.client_tax_identification_number
        customer_email = credit_note_header.client_email
        customer_address = credit_note_header.client_address
        customer_phone_number = credit_note_header.client_phone_number
        patient = None

        # Verifica si existe ya un cliente guardado en la nota de credito. En caso de no contar con eso, busca un clien
        if credit_note_header.customer is None:
            customer = Customer.objects.filter(customer_tax_id_number=customer_ruc).first()
            if customer:
                print("El cliente ya existe")
                # Se actualizan los datos del customer
                customer.customer_email = customer_email
                customer.customer_address = customer_address
                customer.customer_phone_number = customer_phone_number
                customer.save()

                credit_note_header.customer = customer
                credit_note_header.save()
            else:
                customer = Customer.objects.create(
                    customer_name=customer_name,
                    customer_tax_id_number=customer_ruc,
                    patient=patient,
                    customer_email=customer_email,
                    customer_address=customer_address,
                    customer_phone_number=customer_phone_number
                )
                credit_note_header.customer = customer
                credit_note_header.save()

        if details_formset.is_valid():
            details_formset.instance = credit_note_header
            details_formset.save()
            messages.success(self.request, 'Nota de Crédito modificada satisfactoriamente.')
            return HttpResponseRedirect(
                reverse('credit_note_list'))
        else:
            messages.error(self.request, 'Error al tratar de modificar la nota de crédito.')
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        print("Formulario no valido")
        error = form.errors
        print(error)
        messages.error(self.request, 'Error al tratar de modificar la nota de crédito.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('credit_note_list')


class InvoiceDeleteView(DeleteView):
    template_name = "invoicing/invoice_delete.html"
    model = InvoiceHeader
    context_object_name = 'invoice'

    def post(self, request, *args, **kwargs):
        invoice_id = kwargs['pk']
        invoice = get_object_or_404(InvoiceHeader, pk=invoice_id)
        details = invoice.invoice_details
        entry_sheets = invoice.consultation_entry_sheets

        if details:
            for det in details.all():
                det.delete()

        if entry_sheets:
            for es in entry_sheets.all():
                es.invoice = None
                es.save()

        invoice.delete()

        messages.success(self.request, "La factura fue eliminada satisfactoriamente.")
        return HttpResponseRedirect(reverse('invoice_list'))


class CreditNoteDeleteView(DeleteView):
    template_name = "invoicing/credit_note/credit_note_delete.html"
    model = CreditNoteHeader
    context_object_name = 'credit_note'

    def post(self, request, *args, **kwargs):
        credit_note_id = kwargs['pk']
        credit_note = get_object_or_404(CreditNoteHeader, pk=credit_note_id)
        details = credit_note.credit_note_details
        if details:
            for det in details.all():
                det.delete()

        credit_note.delete()

        messages.success(self.request, "La Nota de crédito fue eliminada satisfactoriamente.")
        return HttpResponseRedirect(reverse('credit_note_list'))


class InvoiceLastNumber(View):

    def get(self, request, *args, **kwargs):
        company = IssuingCompanyName.objects.filter(pk=request.GET.get('company_id')).get()
        laststamp = InvoiceStamp.objects.filter(company_name=company).last()

        trfu = StampRange.objects.filter(stamp=laststamp, user=request.user).last()

        invoice_number_start = trfu.range_invoice.sucursal_number + '-' + trfu.range_invoice.boca_number

        last_invoice_header = InvoiceHeader.objects.filter(
            invoice_number__startswith=invoice_number_start,
            invoice_stamp=laststamp
        ).last()

        hoy = date.today()
        message = ''
        if hoy > laststamp.endDate:
            message += "El ultimo timbrado agregado ha expirado, favor agregar un nuevo timbrado."

        try:
            ultimonumero = last_invoice_header.invoice_number.split("-")
            unro = int(ultimonumero[2]) + 1
            stamplastnumber = int(trfu.range_invoice.end_number)
            if unro > stamplastnumber:
                message += "El numero de la factura ha sobrepasado al nro maximo del timbrado, agregue un nuevo timbrado o suba el nro. maximo. "
            ultima_factura = str(
                trfu.range_invoice.sucursal_number + '-' + trfu.range_invoice.boca_number + '-' + str(unro).zfill(6))
        except:
            ultima_factura = trfu.range_invoice.sucursal_number + '-' + trfu.range_invoice.boca_number + '-' + trfu.range_invoice.start_number

        response = []

        if message == '':
            invoice_data = {
                'invoice_number': ultima_factura,
                'stamp_id': laststamp.id,
                'msg': message,
            }
        else:
            invoice_data = {
                'invoice_number': 0,
                'stamp_id': 0,
                'msg': message,
            }
        response.append(invoice_data)

        return JsonResponse(response, status=200, safe=False)


class CreditNoteGetLastNumberView(View):

    def get(self, request, *args, **kwargs):
        company = IssuingCompanyName.objects.filter(pk=request.GET.get('company_id')).get()
        laststamp = CreditNoteStamp.objects.filter(company_name=company).last()

        trncu = CreditNoteStampRange.objects.filter(stamp=laststamp, user=request.user).last()

        credit_note_number_start = trncu.range_credit_note.sucursal_number + '-' + trncu.range_credit_note.boca_number

        last_credit_note_header = CreditNoteHeader.objects.filter(
            credit_note_number__startswith=credit_note_number_start,
            credit_note_stamp=laststamp
        ).last()

        hoy = date.today()
        message = ''
        if hoy > laststamp.endDate:
            message += "El ultimo timbrado agregado ha expirado, favor agregar un nuevo timbrado."

        try:
            ultimonumero = last_credit_note_header.credit_note_number.split("-")
            unro = int(ultimonumero[2]) + 1
            stamplastnumber = int(trncu.range_credit_note.end_number)
            if unro > stamplastnumber:
                message += "El numero de la nota de crédito ha sobrepasado al nro maximo del timbrado, agregue un nuevo timbrado o suba el nro. maximo. "
            ultima_nota_de_credito = str(
                trncu.range_credit_note.sucursal_number + '-' + trncu.range_credit_note.boca_number + '-' + str(unro).zfill(
                    6))
        except Exception as e:
            print(f"¡Error! Se produjo una excepción: {e}")
            ultima_nota_de_credito = trncu.range_credit_note.sucursal_number + '-' + trncu.range_credit_note.boca_number + '-' + trncu.range_credit_note.start_number

        response = []

        if message == '':
            credit_note_data = {
                'credit_note_number': ultima_nota_de_credito,
                'stamp_id': laststamp.id,
                'msg': message,
            }
        else:
            credit_note_data = {
                'credit_note_number': 0,
                'stamp_id': 0,
                'msg': message,
            }
        response.append(credit_note_data)

        return JsonResponse(response, status=200, safe=False)


class GetInvoiceDataJsonView(View):

    def get(self, request, *args, **kwargs):
        invoice_header = InvoiceHeader.objects.get(pk=kwargs['invoice_id'])

        customer = {
            'customer_name': invoice_header.customer.customer_name,
            'customer_tax_id_number': invoice_header.customer.customer_tax_id_number,
            'customer_email': invoice_header.customer.customer_email,
            'customer_address': invoice_header.customer.customer_address,
            'customer_phone_number': invoice_header.customer.customer_phone_number,
            'is_taxpayer': invoice_header.customer.is_taxpayer
        }

        details = []
        for d in invoice_header.invoice_details.all():
            detail = {
                'quantity': d.quantity,
                'description': d.description,
                'unit_price': d.unit_price,
                'exempt': d.exempt,
                'tax_5': d.tax_5,
                'tax_10': d.tax_10
            }
            details.append(detail)

        invoice_data = {
            'customer': customer,
            'invoice_details': details
        }

        return JsonResponse(invoice_data, status=200, safe=False)


class GetInvoicesByCompanyJsonView(View):

    def get(self, request, *args, **kwargs):
        # Todos los Invoices
        all_invoices = InvoiceHeader.objects.filter(company_id=kwargs['company_id']).order_by('-id')
        invoice_list = []
        for invoice in all_invoices:
            credit_notes = invoice.credit_notes.all()
            credit_notes_total = 0
            for credit_note in credit_notes:
                credit_notes_total += credit_note.credit_note_total
            if invoice.invoice_total > credit_notes_total:
                invoice = {
                    'invoice_id': invoice.pk,
                    'invoice_descripction': str(invoice),
                }
                invoice_list.append(invoice)

        return JsonResponse(invoice_list, status=200, safe=False)


class InvoiceCreationFromConsultationSheetView(LoginRequiredMixin, CreateView):
    model = InvoiceHeader
    form_class = InvoiceHeaderForm
    template_name = 'invoicing/invoice_create_from_consultation_sheet.html'

    def get_consultation_entrysheet(self):
        consultation_entrysheet = get_object_or_404(ConsultationEntrySheet,
                                                    pk=self.kwargs['consultation_entry_sheet_id'])
        return consultation_entrysheet

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreationFromConsultationSheetView, self).get_context_data(**kwargs)
        if self.request.POST:
            context.update(
                {
                    'detail_formset': InvoiceDetailsFormSet(self.request.POST),
                }
            )
        else:
            consultation_entrysheet = self.get_consultation_entrysheet()
            consultation_sheets = consultation_entrysheet.consultation_sheets.all()
            details = []
            for c in consultation_sheets:
                if c.total_ammount_to_pay_patient_with_discount > 0:
                    detail = {
                        'quantity': '1',
                        'description': c.medical_study.name,
                        'unit_price': int(c.total_ammount_to_pay_patient_with_discount),
                        'exempt': '0',
                        'tax_5': '0',
                        'tax_10': '0'
                    }
                    details.append(detail)
            formset = inlineformset_factory(
                InvoiceHeader, InvoiceDetails, InvoiceDetailsForm,
                extra=len(details),
                can_delete=True, )
            context.update(
                {
                    'detail_formset': formset(initial=details),
                }
            )

        return context

    def get_initial(self):
        initial = super(InvoiceCreationFromConsultationSheetView, self).get_initial()

        consultation_entrysheet = self.get_consultation_entrysheet()
        default_currency = Currency.objects.first()
        ruc = consultation_entrysheet.patient.tax_identification_number
        if ruc is None:
            ruc = consultation_entrysheet.patient.document_number
        patient_fullname = consultation_entrysheet.patient.name + ' ' + consultation_entrysheet.patient.last_name
        client_email = consultation_entrysheet.patient.email
        client_address = consultation_entrysheet.patient.address
        client_phone_number = consultation_entrysheet.patient.phone_number
        client_is_taxpayer = consultation_entrysheet.patient.is_taxpayer

        initial['currency'] = default_currency
        initial['client_name'] = patient_fullname
        initial['client_tax_identification_number'] = ruc
        initial['client_email'] = client_email
        initial['client_address'] = client_address
        initial['client_phone_number'] = client_phone_number
        initial['client_tax_payer'] = client_is_taxpayer
        initial['invoice_date'] = date.today()
        first_study = consultation_entrysheet.consultation_sheets.first()

        if first_study.medical_study.type.name == 'IRM':
            initial['company'] = IssuingCompanyName.objects.get(company_name='IRM S.A.')
        else:
            initial['company'] = IssuingCompanyName.objects.get(company_name='INSTITUTO IRIBAS S.A.')

        return initial

    def form_valid(self, form):
        context = self.get_context_data()
        details_formset = context['detail_formset']

        # Validate RUC
        customer_tax_payer = form.cleaned_data['client_tax_payer']
        if customer_tax_payer:
            response = validate_ruc_set(form.data['client_tax_identification_number'])

            if not response['ok']:
                messages.error(self.request, 'RUC inválido en la SET: Error-> ' + response['error'])
                return self.render_to_response(self.get_context_data(form=form))

        invoice_header = form.save()
        customer_name = invoice_header.client_name
        customer_ruc = invoice_header.client_tax_identification_number
        customer_email = invoice_header.client_email
        customer_address = invoice_header.client_address
        customer_phone_number = invoice_header.client_phone_number

        patient = None
        customer = Customer.objects.filter(customer_tax_id_number=customer_ruc).first()
        if customer:
            print("cliente ya existe")
            # Se actualizan los datos del customer
            customer.customer_email = customer_email
            customer.customer_address = customer_address
            customer.customer_phone_number = customer_phone_number
            customer.is_taxpayer = customer_tax_payer
            customer.save()

            invoice_header.customer = customer
            invoice_header.save()
        else:
            customer = Customer.objects.create(
                customer_name=customer_name,
                customer_tax_id_number=customer_ruc,
                patient=patient,
                customer_email=customer_email,
                customer_address=customer_address,
                customer_phone_number=customer_phone_number,
                is_taxpayer=customer_tax_payer,
            )
            invoice_header.customer = customer
            invoice_header.save()

        # update patient tax info
        if customer.patient:
            patient = customer.patient
            patient.tax_identification_number = customer.customer_tax_id_number
            patient.tax_identification_name = customer.customer_name
            patient.is_taxpayer = customer.is_taxpayer

        consultation_entry_sheet = self.get_consultation_entrysheet()
        consultation_entry_sheet.invoice = invoice_header
        consultation_entry_sheet.save()

        if details_formset.is_valid():
            details_formset.instance = invoice_header
            details_formset.save()
            messages.success(self.request, 'Factura creada satisfactoriamente.')

            try:
                # Generate SIFEN DTE
                # Envío directo(Solo funciona con env=test en sifen middleware)
                # generate_sifen_dte(self.request, invoice_header)
                # Envío por lote(Solo funciona con env=production en sifen middleware)
                # generate_sifen_dte_batch(self.request, invoice_header)
                pass
            except Exception as e:
                print(e)
                messages.error(self.request, 'La Factura no pudo ser enviada a la SET: Error-> '
                               + str(e))

            return HttpResponseRedirect(
                reverse('invoice_list'))
        else:
            return self.render_to_response(self.get_context_data(form=form))


class CreditNoteCreationFromInvoiceView(LoginRequiredMixin, CreateView):
    model = CreditNoteHeader
    form_class = CreditNoteHeaderCreateForm
    template_name = 'invoicing/credit_note/credit_note_create_from_invoice.html'

    def get_invoice_header(self):
        invoice_header = get_object_or_404(InvoiceHeader, pk=self.kwargs['invoice_header_id'])
        return invoice_header

    def get_context_data(self, **kwargs):
        context = super(CreditNoteCreationFromInvoiceView, self).get_context_data(**kwargs)
        if self.request.POST:
            context.update(
                {
                    'detail_formset': CreditNoteDetailsFormSet(self.request.POST),
                }
            )
        else:
            invoice_header = self.get_invoice_header()
            invoice_details = invoice_header.invoice_details.all()
            details = []
            for d in invoice_details:
                detail = {
                    'quantity': d.quantity,
                    'description': d.description,
                    'unit_price': d.unit_price,
                    'exempt': d.exempt,
                    'tax_5': d.tax_5,
                    'tax_10': d.tax_10
                }
                details.append(detail)
            formset = inlineformset_factory(
                CreditNoteHeader, CreditNoteDetail, CreditNoteDetailForm,
                extra=len(details),
                can_delete=True, )
            context.update(
                {
                    'detail_formset': formset(initial=details),
                    'invoice': invoice_header
                }
            )

        return context

    def get_initial(self):
        initial = super(CreditNoteCreationFromInvoiceView, self).get_initial()

        invoice_header = self.get_invoice_header()
        default_currency = Currency.objects.first()
        ruc = invoice_header.customer.customer_tax_id_number
        email = invoice_header.customer.customer_email
        address = invoice_header.customer.customer_address
        phone_number = invoice_header.customer.customer_phone_number
        is_taxpayer = invoice_header.customer.is_taxpayer

        initial['currency'] = default_currency
        initial['client_name'] = invoice_header.customer.customer_name
        initial['client_tax_identification_number'] = ruc
        initial['client_email'] = email
        initial['client_address'] = address
        initial['client_phone_number'] = phone_number
        initial['client_tax_payer'] = is_taxpayer
        initial['invoice_date'] = date.today()
        initial['company'] = invoice_header.company
        initial['invoice_header'] = invoice_header
        initial['credit_note_date'] = date.today()

        return initial

    def form_valid(self, form):
        context = self.get_context_data()
        details_formset = context['detail_formset']

        # Validate RUC
        customer_tax_payer = form.cleaned_data['client_tax_payer']
        if customer_tax_payer:
            response = validate_ruc_set(form.data['client_tax_identification_number'])

            if not response['ok']:
                messages.error(self.request, 'RUC inválido en la SET: Error-> ' + response['error'])
                return self.render_to_response(self.get_context_data(form=form))

        credit_note_header = form.save()
        customer_name = credit_note_header.client_name
        customer_ruc = credit_note_header.client_tax_identification_number
        customer_email = credit_note_header.client_email
        customer_address = credit_note_header.client_address
        customer_phone_number = credit_note_header.client_phone_number

        patient = None
        customer = Customer.objects.filter(customer_tax_id_number=customer_ruc).first()
        if customer:
            print("cliente ya existe")
            # Se actualizan los datos del customer
            customer.customer_email = customer_email
            customer.customer_address = customer_address
            customer.customer_phone_number = customer_phone_number
            customer.save()

            credit_note_header.customer = customer
            credit_note_header.save()
        else:
            customer = Customer.objects.create(
                customer_name=customer_name,
                customer_tax_id_number=customer_ruc,
                patient=patient,
                customer_email=customer_email,
                customer_address=customer_address,
                customer_phone_number=customer_phone_number
            )
            credit_note_header.customer = customer
            credit_note_header.save()

        if details_formset.is_valid():
            details_formset.instance = credit_note_header
            details_formset.save()
            messages.success(self.request, 'Nota de Crédito creada satisfactoriamente.')

            try:
                # Generate SIFEN DTE
                # Envío directo(Solo funciona con env=test en sifen middleware)
                # generate_sifen_dte(self.request, invoice_header)
                # Envío por lote(Solo funciona con env=production en sifen middleware)
                # generate_sifen_dte_batch(self.request, credit_note_header)
                pass
            except Exception as e:
                print(e)
                messages.error(self.request, 'La Nota de Crédito no pudo ser enviada a la SET: Error-> '
                               + str(e))

            return HttpResponseRedirect(
                reverse('credit_note_list'))
        else:
            return self.render_to_response(self.get_context_data(form=form))


class InvoiceCreationView(CreateView):
    model = InvoiceHeader
    form_class = InvoiceHeaderForm
    template_name = 'invoicing/invoice_create.html'

    def get_form_kwargs(self):
        kwargs = super(InvoiceCreationView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = {
            'invoice_date': datetime.now()
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreationView, self).get_context_data(**kwargs)
        if self.request.POST:
            context.update(
                {
                    'detail_formset': InvoiceDetailsFormSet(self.request.POST),
                }
            )
        else:
            context.update(
                {
                    'detail_formset': InvoiceDetailsFormSet(),
                }
            )

        return context

    def get_invoice(self):
        invoice = get_object_or_404(InvoiceHeader, pk=self.kwargs['invoiceheader_id'])
        return invoice

    @transaction.atomic()
    def form_valid(self, form):
        context = self.get_context_data()
        details_formset = context['detail_formset']

        # Validate RUC
        customer_tax_payer = form.cleaned_data['client_tax_payer']
        if customer_tax_payer:
            response = validate_ruc_set(form.data['client_tax_identification_number'])

            if not response['ok']:
                messages.error(self.request, 'RUC inválido en la SET: Error-> ' + response['error'])
                return self.render_to_response(self.get_context_data(form=form))

        invoice_header = form.save()
        customer_name = invoice_header.client_name
        customer_ruc = invoice_header.client_tax_identification_number
        customer_email = invoice_header.client_email
        customer_address = invoice_header.client_address
        customer_phone_number = invoice_header.client_phone_number
        patient = None
        customer = Customer.objects.filter(customer_tax_id_number=customer_ruc).first()
        if customer:
            print("cliente ya existe")
            # Se actualizan los datos del customer
            customer.customer_email = customer_email
            customer.customer_address = customer_address
            customer.customer_phone_number = customer_phone_number
            customer.save()

            invoice_header.customer = customer
            invoice_header.save()
        else:
            customer = Customer.objects.create(
                customer_name=customer_name,
                customer_tax_id_number=customer_ruc,
                patient=patient,
                customer_email=customer_email,
                customer_address=customer_address,
                customer_phone_number=customer_phone_number,
                is_taxpayer=customer_tax_payer
            )
            invoice_header.customer = customer
            invoice_header.save()

        if details_formset.is_valid():
            details_formset.instance = invoice_header
            details_formset.save()
            messages.success(self.request, 'Factura creada satisfactoriamente.')

            try:
                # Generate SIFEN DTE
                # Envío directo(Solo funciona con env=test en sifen middleware)
                # generate_sifen_dte(self.request, invoice_header)
                # Envío por lote(Solo funciona con env=production en sifen middleware)
                # generate_sifen_dte_batch(self.request, invoice_header)
                pass
            except Exception as e:
                print(e)
                messages.error(self.request, 'La Factura no pudo ser enviada a la SET: Error-> '
                               + str(e))

            return HttpResponseRedirect(
                reverse('invoice_list'))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        print("Formulario no valido")
        error = form.errors
        print(error)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('invoice_list')


class CreditNoteCreationView(CreateView):
    model = CreditNoteHeader
    form_class = CreditNoteHeaderCreateForm
    template_name = 'invoicing/credit_note/credit_note_create.html'

    def get_initial(self):
        initial = {
            'credit_note_date': datetime.now()
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super(CreditNoteCreationView, self).get_context_data(**kwargs)
        if self.request.POST:
            context.update(
                {
                    'detail_formset': CreditNoteDetailsFormSet(self.request.POST),
                }
            )
        else:
            context.update(
                {
                    'detail_formset': CreditNoteDetailsFormSet(),
                }
            )

        return context

    def get_credit_note(self):
        invoice = get_object_or_404(CreditNoteHeader, pk=self.kwargs['creditnoteheader_id'])
        return invoice

    @transaction.atomic()
    def form_valid(self, form):
        context = self.get_context_data()
        details_formset = context['detail_formset']

        # Validate RUC
        response = validate_ruc_set(form.data['client_tax_identification_number'])

        if not response['ok']:
            messages.error(self.request, 'RUC ivalido en la SET: Error-> ' + response['error'])
            return self.render_to_response(self.get_context_data(form=form))

        credit_note_header = form.save()
        customer_name = credit_note_header.client_name
        customer_ruc = credit_note_header.client_tax_identification_number
        customer_email = credit_note_header.client_email
        customer_address = credit_note_header.client_address
        customer_phone_number = credit_note_header.client_phone_number

        patient = None
        customer = Customer.objects.filter(customer_tax_id_number=customer_ruc).first()
        if customer:
            print("Cliente ya existe")
            # Se actualizan los datos del customer
            customer.customer_email = customer_email
            customer.customer_address = customer_address
            customer.customer_phone_number = customer_phone_number
            customer.save()

            credit_note_header.customer = customer
            credit_note_header.save()
        else:
            customer = Customer.objects.create(
                customer_name=customer_name,
                customer_tax_id_number=customer_ruc,
                patient=patient,
                customer_email=customer_email,
                customer_address=customer_address,
                customer_phone_number=customer_phone_number
            )
            credit_note_header.customer = customer
            credit_note_header.save()

        if details_formset.is_valid():
            details_formset.instance = credit_note_header
            details_formset.save()
            messages.success(self.request, 'Nota de Crédito creada satisfactoriamente.')

            try:
                # Generate SIFEN DTE
                # Envío directo(Solo funciona con env=test en sifen middleware)
                # generate_sifen_dte(self.request, invoice_header)
                # Envío por lote(Solo funciona con env=production en sifen middleware)
                # generate_sifen_dte_batch(self.request, credit_note_header)
                pass
            except Exception as e:
                print(e)
                messages.error(self.request, 'La Nota de Crédito no pudo ser enviada a la SET: Error-> '
                               + str(e))

            return HttpResponseRedirect(
                reverse('credit_note_list'))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        print("Formulario no valido")
        error = form.errors
        print(error)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('credit_note_list')


# Customer Query to use in AJAX
class CustomerQuery(View):
    model = Customer

    def get(self, request, *args, **kwargs):
        customer_list_json = []
        customers = Customer.objects.filter(customer_name__istartswith=request.GET.get('term'))
        if customers:
            for customer in customers:
                customer_json = {
                    'label': customer.customer_name + ' - ' + customer.customer_tax_id_number,
                    'value': customer.id,
                    'ruc': customer.customer_tax_id_number,
                    'name': customer.customer_name,
                    'email': customer.customer_email,
                    'address': customer.customer_address,
                    'phone_number': customer.customer_phone_number,
                    'is_taxpayer': customer.is_taxpayer,
                }
                customer_list_json.append(customer_json)
        else:
            customers = Customer.objects.filter(customer_tax_id_number__istartswith=request.GET.get('term'))
            for customer in customers:
                customer_json = {
                    'label': customer.customer_name + ' - ' + customer.customer_tax_id_number,
                    'value': customer.id,
                    'name': customer.customer_name,
                    'ruc': customer.customer_tax_id_number,
                    'email': customer.customer_email,
                    'address': customer.customer_address,
                    'phone_number': customer.customer_phone_number,
                    'is_taxpayer': customer.is_taxpayer,
                }
                customer_list_json.append(customer_json)
        return JsonResponse(customer_list_json, status=200, safe=False)


# Invoice Print View
class InvoicePrintView(LoginRequiredMixin, TemplateView):
    template_name = "invoicing/invoice_print.html"

    def get_context_data(self, **kwargs):
        context = super(InvoicePrintView, self).get_context_data(**kwargs)
        invoice_header = InvoiceHeader.objects.get(pk=kwargs['pk'])
        invoice_number = invoice_header.invoice_number.split('-')
        invoice_num = invoice_number[2]
        invoice_header.invoice_number = invoice_num
        details = invoice_header.invoice_details.all()
        context.update(
            {
                'invoice': invoice_header,
                'details': details,

            }
        )
        return context


# Credit Note Print View
class CreditNotePrintView(LoginRequiredMixin, TemplateView):
    template_name = "invoicing/credit_note/credit_note_print.html"

    def get_context_data(self, **kwargs):
        context = super(CreditNotePrintView, self).get_context_data(**kwargs)
        credit_note_header = CreditNoteHeader.objects.get(pk=kwargs['pk'])
        credit_note_number = credit_note_header.credit_note_number.split('-')
        credit_note_num = credit_note_number[2]
        credit_note_header.credit_note_number = credit_note_num
        details = credit_note_header.credit_note_details.all()
        context.update(
            {
                'credit_note': credit_note_header,
                'details': details,

            }
        )
        return context


# Create Invoice Insurance
class InvoiceCreateFromInsuranceReportView(CreateView):
    model = InvoiceHeader
    form_class = InvoiceHeaderForm
    template_name = 'invoicing/invoice_create_from_insurance_report.html'

    def get_queryset(self):
        queryset = []
        form = InsurancesAgreementsReportFiltersForm(self.request.GET)
        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            if form.is_valid():
                start = form.cleaned_data.get('date_time_start')
                end = form.cleaned_data.get('date_time_end')
                queryset = ConsultationSheet.objects.filter(
                    consultation_date__range=[start, end],
                    total_ammount_to_pay_insurance__gt=0
                ).order_by('medical_study__sector', 'consultation_date')

                # Insurance Plan Filter
                insurance_plan = form.cleaned_data.get('insurance_plan', None)
                if insurance_plan:
                    queryset = queryset.filter(patient_insurance_plan=insurance_plan)

                # Sector Filter
                sector = form.cleaned_data.get('sector', None)
                if sector:
                    queryset = queryset.filter(medical_study__sector=sector)

                # Study Type Filter
                study_type = form.cleaned_data.get('study_type', None)
                if study_type:
                    queryset = queryset.filter(medical_study__type=study_type)

                # Insurance Invoice Filter
                invoice_filter = form.cleaned_data.get('invoice_filter', None)
                if invoice_filter is not None:
                    # Que no tienen facturas de seguro
                    if int(invoice_filter) == InsurancesAgreementsReportFiltersForm.INSURANCE_ENTRY_SHEETS_TO_PAY_WITHOUT_INVOICES:
                        queryset = queryset.filter(consultation_entry_sheet__insurance_invoice=None)
                    # Que tienen facturas de Seguro
                    if int(invoice_filter) == InsurancesAgreementsReportFiltersForm.INSURANCE_ENTRY_SHEETS_TO_PAY_WITH_INVOICES:
                        queryset = queryset.filter(consultation_entry_sheet__insurance_invoice__isnull=False)
                    # Que tienen o no factura de seguro
                    if int(invoice_filter) == InsurancesAgreementsReportFiltersForm.ALL_INSURANCE_ENTRY_SHEETS_TO_PAY:
                        pass

        return queryset

    def get_context_data(self, **kwargs):
        elements = self.get_queryset()


        totals_sectors = []

        sectors = Sector.objects.all()

        for sector in sectors:
            total_sector = {
                'total_name': sector.name,
                'total': 0
            }
            totals_sectors.append(total_sector)

        total_to_be_billed_insurance = 0
        for element in elements:
            total_to_be_billed_insurance += element.total_ammount_to_pay_insurance

            for total_sector in totals_sectors:
                if element.medical_study.sector and element.medical_study.sector.name == total_sector['total_name']:
                    total_sector['total'] += element.total_ammount_to_pay_insurance

        context = super(InvoiceCreateFromInsuranceReportView, self).get_context_data(**kwargs)
        if self.request.POST:
            context.update(
                {
                    'detail_formset': InvoiceDetailsFormSet(self.request.POST),
                }
            )
        else:
            details = []

            for sector in totals_sectors:
                if sector['total'] != 0:
                    detail = {
                        'quantity': '1',
                        'description': sector['total_name'],
                        'unit_price': int(sector['total']),
                        'exempt': '0',
                        'tax_5': '0',
                        'tax_10': int(total_to_be_billed_insurance)
                    }
                    details.append(detail)

            formset = inlineformset_factory(
                InvoiceHeader, InvoiceDetails, InvoiceDetailsForm,
                extra=len(details),
                can_delete=True, )
            context.update(
                {
                    'detail_formset': formset(initial=details),
                }
            )

        return context

    def get_initial(self):
        initial = super(InvoiceCreateFromInsuranceReportView, self).get_initial()
        form = InsurancesAgreementsReportFiltersForm(self.request.GET)

        element = self.get_queryset().first()
        default_currency = Currency.objects.first()
        ruc = element.patient.insurance_plan.insurance_company.tax_identification_number
        email = element.patient.insurance_plan.insurance_company.email
        address = element.patient.insurance_plan.insurance_company.address
        phone_number = element.patient.insurance_plan.insurance_company.phone_number
        if ruc is None:
            ruc = 'Sin Nombre'

        initial['currency'] = default_currency
        initial['payment_term'] = InvoiceHeader.CONDITIONS[1][1]
        initial['client_name'] = element.patient.insurance_plan.insurance_company.name
        initial['client_tax_identification_number'] = ruc
        initial['client_email'] = email
        initial['client_address'] = address
        initial['client_phone_number'] = phone_number
        initial['client_tax_payer'] = True
        initial['invoice_date'] = date.today()
        if form.is_valid():
            if form.cleaned_data.get('study_type').name == "IRIBAS":
                company_name = "IRIBAS S.A."
            else:
                company_name = "IRM S.A."

            initial['company'] = IssuingCompanyName.objects.get(company_name=company_name)

        return initial

    def get_consultation_entrysheets(self):
        elements = self.get_queryset()
        consultation_entry_sheets_set = set()

        # Recorremos la lista de ConsultationSheet y obtenemos los ConsultationEntrySheet relacionados.
        for consultation_sheet in elements:
            if consultation_sheet.consultation_entry_sheet:
                consultation_entry_sheets_set.add(consultation_sheet.consultation_entry_sheet)

        return consultation_entry_sheets_set

    def form_valid(self, form):
        context = self.get_context_data()
        details_formset = context['detail_formset']

        # Validate RUC
        customer_tax_payer = form.data['client_tax_payer']
        if customer_tax_payer:
            response = validate_ruc_set(form.data['client_tax_identification_number'])

            if not response['ok']:
                messages.error(self.request, 'RUC inválido en la SET: Error-> ' + response['error'])
                return self.render_to_response(self.get_context_data(form=form))

        invoice_header = form.save()
        customer_name = invoice_header.client_name
        customer_ruc = invoice_header.client_tax_identification_number
        customer_email = invoice_header.client_email
        customer_address = invoice_header.client_address
        customer_phone_number = invoice_header.client_phone_number
        patient = None
        customer = Customer.objects.filter(customer_tax_id_number=customer_ruc).first()
        if customer:
            print("cliente ya existe")
            # Se actualizan los datos del customer
            customer.customer_email = customer_email
            customer.customer_address = customer_address
            customer.customer_phone_number = customer_phone_number
            customer.save()

            invoice_header.customer = customer
            invoice_header.save()
        else:
            customer = Customer.objects.create(
                customer_name=customer_name,
                customer_tax_id_number=customer_ruc,
                patient=patient,
                customer_email=customer_email,
                customer_address=customer_address,
                customer_phone_number=customer_phone_number,
            )
            invoice_header.customer = customer
            invoice_header.save()

        # Se asigna el invoice a los consultation entry sheets del reporte
        consultation_entry_sheets = self.get_consultation_entrysheets()
        for consultation_entry_sheet in consultation_entry_sheets:
            consultation_entry_sheet.insurance_invoice = invoice_header
            consultation_entry_sheet.save()

        if details_formset.is_valid():
            details_formset.instance = invoice_header
            details_formset.save()
            messages.success(self.request, 'Factura creada satisfactoriamente.')

            try:
                # Generate SIFEN DTE
                # generate_sifen_dte(self.request, invoice_header)
                # generate_sifen_dte_batch(self.request, invoice_header)
                pass
            except Exception as e:
                print(e)
                messages.error(self.request, 'La Factura no pudo ser enviada a la SET: Error-> '
                               + str(e))

            return HttpResponseRedirect(
                reverse('invoice_list'))
        else:
            return self.render_to_response(self.get_context_data(form=form))


# Download invoice sifen pdf
class InvoiceDownloadPdfview(DetailView):
    model = InvoiceHeader

    def get(self, request, *args, **kwargs):
        invoice_header = self.get_object()
        # Obtener el contenido del PDF base64
        pdf_base64 = invoice_header.invoice_pdf_base64

        # Decodificar el contenido base64 en una cadena de bytes
        pdf_bytes = base64.b64decode(pdf_base64)

        # Crear una respuesta HTTP con el PDF descargable
        response = HttpResponse(content_type='application/pdf')
        filename = invoice_header.invoice_number
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'

        # Escribir los bytes del PDF directamente en la respuesta
        response.write(pdf_bytes)

        return response


# Show invoice sifen html
class InvoiceShowHtmlView(DetailView):
    model = InvoiceHeader

    def get(self, request, *args, **kwargs):
        invoice_header = self.get_object()
        invoice_html = invoice_header.invoice_kude_html

        # Crear una respuesta HTTP con el contenido HTML renderizado
        response = HttpResponse(content_type='text/html')
        response.write(invoice_html)

        return response


# PRINT invoice sifen html
class PrintInvoicePreviewHtmlView(DetailView):
    model = InvoiceHeader
    template_name = 'invoicing/invoice_print_preview.html'
    context_object_name = 'invoice_header'


# Show credit note sifen html
class CreditNoteShowHtmlView(DetailView):
    model = CreditNoteHeader

    def get(self, request, *args, **kwargs):
        credit_note_header = self.get_object()
        credit_note_html = credit_note_header.credit_note_kude_html

        # Crear una respuesta HTTP con el contenido HTML renderizado
        response = HttpResponse(content_type='text/html')
        response.write(credit_note_html)

        return response


# Download credit note sifen pdf
class CreditNoteDownloadPdfview(DetailView):
    model = CreditNoteHeader

    def get(self, request, *args, **kwargs):
        credit_note_header = self.get_object()
        # Obtener el contenido del PDF base64
        pdf_base64 = credit_note_header.credit_note_pdf_base64

        # Decodificar el contenido base64 en una cadena de bytes
        pdf_bytes = base64.b64decode(pdf_base64)

        # Crear una respuesta HTTP con el PDF descargable
        response = HttpResponse(content_type='application/pdf')
        filename = credit_note_header.credit_note_number
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'

        # Escribir los bytes del PDF directamente en la respuesta
        response.write(pdf_bytes)

        return response


# Send Invoice To sifen
class InvoiceSendToSifenView(DetailView):
    model = InvoiceHeader

    def get(self, request, *args, **kwargs):
        invoice_header = self.get_object()

        try:
            if invoice_header.invoice_stamp.electronic_stamp:
                # Generate SIFEN DTE
                # Envío directo(Solo funciona con env=test en sifen middleware)
                # generate_sifen_dte(self.request, invoice_header)
                # Envío por lote(Solo funciona con env=production en sifen middleware)
                generate_sifen_dte_batch(self.request, invoice_header)
        except Exception as e:
            print(e)
            messages.error(self.request, 'La Factura no pudo ser enviada a la SET: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('invoice_list'))


# Send Credit Note to sifen
class CreditNoteSendToSifenView(DetailView):
    model = CreditNoteHeader

    def get(self, request, *args, **kwargs):
        credit_note_header = self.get_object()

        try:
            if credit_note_header.credit_note_stamp.electronic_stamp:
                # Generate SIFEN DTE
                # Envío directo(Solo funciona con env=test en sifen middleware)
                # generate_sifen_credit_note_dte(self.request, credit_note_header)
                # Envío en lote (Solo funciona con env=production en sifen middleware)
                generate_sifen_credit_note_dte_batch(self.request, credit_note_header)
        except Exception as e:
            print(e)
            messages.error(self.request, 'La Nota de crédito no pudo ser enviada a la SET: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('credit_note_list'))


class InvoiceGenerateSifenPdfView(DetailView):
    model = InvoiceHeader

    def get(self, request, *args, **kwargs):
        invoice_header = self.get_object()

        try:
            if invoice_header.invoice_stamp.electronic_stamp:
                # Generate SIFEN PDF
                generate_sifen_pdf(self.request, invoice_header)
        except Exception as e:
            print(e)
            messages.error(self.request, 'El pdf de la factura KUDE no pudo ser generado: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('invoice_list'))


class InvoiceGenerateSifenHtmlView(DetailView):
    model = InvoiceHeader

    def get(self, request, *args, **kwargs):
        invoice_header = self.get_object()

        try:
            if invoice_header.invoice_stamp.electronic_stamp:
                # Generate SIFEN Invoice HTML
                generate_sifen_invoice_html(self.request, invoice_header)
        except Exception as e:
            print(e)
            messages.error(self.request, 'El html de la factura KUDE no pudo ser generado: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('invoice_list'))


class CreditNoteGenerateSifenHtmlView(DetailView):
    model = CreditNoteHeader

    def get(self, request, *args, **kwargs):
        credit_note_header = self.get_object()

        try:
            if credit_note_header.credit_note_stamp.electronic_stamp:
                # Generate SIFEN Credit note HTML
                generate_sifen_credit_note_html(self.request, credit_note_header)
        except Exception as e:
            print(e)
            messages.error(self.request, 'El HTML KUD de la Nota de Crédito no pudo ser generado: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('credit_note_list'))


class CreditNoteGenerateSifenPdfView(DetailView):
    model = CreditNoteHeader

    def get(self, request, *args, **kwargs):
        credit_note_header = self.get_object()

        try:
            if credit_note_header.credit_note_stamp.electronic_stamp:
                # Generate SIFEN PDF
                generate_sifen_credit_note_pdf(self.request, credit_note_header)

        except Exception as e:
            print(e)
            messages.error(self.request, 'El pdf de la nota de crédito KUDE no pudo ser generado: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('credit_note_list'))


class CreditNoteGenerateSifenHtmlView(DetailView):
    model = CreditNoteHeader

    def get(self, request, *args, **kwargs):
        credit_note_header = self.get_object()

        try:
            if credit_note_header.credit_note_stamp.electronic_stamp:
                # Generate SIFEN HTML
                generate_sifen_credit_note_html(self.request, credit_note_header)

        except Exception as e:
            print(e)
            messages.error(self.request, 'El pdf de la nota de crédito KUDE no pudo ser generado: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('credit_note_list'))


class InvoiceConsultBatchToSifenView(DetailView):
    model = InvoiceHeader

    def get(self, request, *args, **kwargs):
        invoice_header = self.get_object()

        try:
            if invoice_header.invoice_stamp.electronic_stamp:
                # Consult INVOICE BATCH SIFEN
                consult_sifen_dte_batch(self.request, invoice_header)
        except Exception as e:
            print(e)
            messages.error(self.request, 'El lote no pudo ser consultado: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('invoice_list'))


class CreditNoteConsultBatchToSifenView(DetailView):
    model = CreditNoteHeader

    def get(self, request, *args, **kwargs):
        credit_note_header = self.get_object()

        try:
            if credit_note_header.credit_note_stamp.electronic_stamp:
                # Consult CREDIT NOTE BATCH SIFEN
                consult_sifen_credit_note_dte_batch(self.request, credit_note_header)
        except Exception as e:
            print(e)
            messages.error(self.request, 'El lote no pudo ser consultado: Error-> '
                           + str(e))

        return HttpResponseRedirect(
            reverse('credit_note_list'))


class InvoiceEmailSendToClientView(DetailView):
    model = InvoiceHeader

    def get(self, request, *args, **kwargs):
        invoice_header = self.get_object()

        send_invoice_email_html(request, invoice_header)

        return HttpResponseRedirect(
            reverse('invoice_list'))


class CreditNoteEmailSendToClientView(DetailView):
    model = CreditNoteHeader

    def get(self, request, *args, **kwargs):
        credit_note_header = self.get_object()

        send_credit_note_email_html(request, credit_note_header)

        return HttpResponseRedirect(
            reverse('credit_note_list'))


def get_spanish_month_name_by_number(month_number):
    month_number = month_number
    months_names = [
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Diciembre',
    ]
    return months_names[month_number]


def send_payload(url, payload_dict):
    headers = {'Content-type': 'application/json'}
    try:
        payload = json.dumps(payload_dict)
        json_payload = json.loads(payload)
    except json.JSONDecodeError:
        return "JSON DECODE ERROR"

    try:
        print('Enviando Payload a: ' + url)
        response = requests.post(url, data=payload, headers=headers)
    except Exception as e:
        print(e)
        response = e
        return response

    return response.json()


def generate_invoice_sifen_payload(data, invoice_header, transaction_id):
    sifen_payload = {
        "client_params": {
            "logo": invoice_header.company.sifen_logo,
            "password": invoice_header.company.sifen_password,
            "id_csc": invoice_header.company.sifen_id_csc,
            "csc": invoice_header.company.sifen_csc
        },
        "params": {
            "version": 150,
            "fechaFirmaDigital": invoice_header.company.sifen_digital_signature_date,
            "ruc": invoice_header.company.sifen_ruc,
            "razonSocial": invoice_header.company.sifen_business_name,
            "nombreFantasia": invoice_header.company.sifen_fantasy_name,
            "actividadesEconomicas": [
                {
                    "codigo": invoice_header.company.sifen_economic_activity_code,
                    "descripcion": invoice_header.company.sifen_economic_activity_description
                }
            ],
            "timbradoNumero": invoice_header.company.sifen_stamp_number,
            "timbradoFecha": invoice_header.company.sifen_stamp_date,
            "tipoContribuyente": 2,
            "tipoRegimen": 8,
            "establecimientos": [
                {
                    "codigo": invoice_header.company.sifen_establishment_code,
                    "direccion": invoice_header.company.sifen_establishment_direction,
                    "numeroCasa": invoice_header.company.sifen_establishment_house_number,
                    "complementoDireccion1": invoice_header.company.sifen_establishment_street_name_1,
                    "complementoDireccion2": invoice_header.company.sifen_establishment_street_name_2,
                    "departamento": int(invoice_header.company.sifen_establishment_department_code),
                    "departamentoDescripcion": invoice_header.company.sifen_establishment_department_description,
                    "distrito": int(invoice_header.company.sifen_establishment_district_code),
                    "distritoDescripcion": invoice_header.company.sifen_establishment_district_description,
                    "ciudad": int(invoice_header.company.sifen_establishment_city_code),
                    "ciudadDescripcion": invoice_header.company.sifen_establishment_city_description,
                    "telefono": invoice_header.company.sifen_establishment_phone,
                    "email": invoice_header.company.sifen_establishment_email,
                    "denominacion": invoice_header.company.sifen_establishment_denomination
                }
            ]
        },
        "data": {
            "tipoDocumento": 1,
            "codigoSeguridadAleatorio": transaction_id,
            "establecimiento": invoice_header.company.sifen_establishment_code,
            "punto": data['punto'],
            "numero": data['numero'],
            "descripcion": "asdasdasdas",
            "observacion": "asdasdasdas",
            "fecha": data['fecha'],
            "tipoEmision": 1,
            "tipoTransaccion": 2,
            "tipoImpuesto": 1,
            "moneda": "PYG",
            "condicionAnticipo": 1,
            "condicionTipoCambio": 1,
            "descuentoGlobal": 0,
            "anticipoGlobal": 0,
            "cambio": 6700,
            "cliente": data['cliente'],
            "usuario": data['usuario'],
            "factura": data['factura'],
            "condicion": data['condicion'],
            "items": data['items']
        }
    }
    sifen_payload['data']['cliente'] = data['cliente']
    sifen_payload['data']['usuario'] = data['usuario']
    sifen_payload['data']['factura'] = data['factura']
    sifen_payload['data']['condicion'] = data['condicion']
    sifen_payload['data']['items'] = data['items']
    return sifen_payload


def generate_credit_note_sifen_payload(data, credit_note_header, transaction_id):
    sifen_payload = {
        "client_params": {
            "logo": credit_note_header.company.sifen_logo,
            "password": credit_note_header.company.sifen_password,
            "id_csc": credit_note_header.company.sifen_id_csc,
            "csc": credit_note_header.company.sifen_csc
        },
        "params": {
            "version": 150,
            "fechaFirmaDigital": credit_note_header.company.sifen_digital_signature_date,
            "ruc": credit_note_header.company.sifen_ruc,
            "razonSocial": credit_note_header.company.sifen_business_name,
            "nombreFantasia": credit_note_header.company.sifen_fantasy_name,
            "actividadesEconomicas": [
                {
                    "codigo": credit_note_header.company.sifen_economic_activity_code,
                    "descripcion": credit_note_header.company.sifen_economic_activity_description
                }
            ],
            "timbradoNumero": credit_note_header.company.sifen_stamp_number,
            "timbradoFecha": credit_note_header.company.sifen_stamp_date,
            "tipoContribuyente": 2,
            "tipoRegimen": 8,
            "establecimientos": [
                {
                    "codigo": credit_note_header.company.sifen_establishment_code,
                    "direccion": credit_note_header.company.sifen_establishment_direction,
                    "numeroCasa": credit_note_header.company.sifen_establishment_house_number,
                    "complementoDireccion1": credit_note_header.company.sifen_establishment_street_name_1,
                    "complementoDireccion2": credit_note_header.company.sifen_establishment_street_name_2,
                    "departamento": int(credit_note_header.company.sifen_establishment_department_code),
                    "departamentoDescripcion": credit_note_header.company.sifen_establishment_department_description,
                    "distrito": int(credit_note_header.company.sifen_establishment_district_code),
                    "distritoDescripcion": credit_note_header.company.sifen_establishment_district_description,
                    "ciudad": int(credit_note_header.company.sifen_establishment_city_code),
                    "ciudadDescripcion": credit_note_header.company.sifen_establishment_city_description,
                    "telefono": credit_note_header.company.sifen_establishment_phone,
                    "email": credit_note_header.company.sifen_establishment_email,
                    "denominacion": credit_note_header.company.sifen_establishment_denomination
                }
            ]
        },
        "data": {
            "tipoDocumento": 5,  # 5 es para Nota de crédito o debito
            "codigoSeguridadAleatorio": transaction_id,
            "establecimiento": credit_note_header.company.sifen_establishment_code,
            "punto": data['punto'],
            "numero": data['numero'],
            "descripcion": "asdasdasdas",
            "observacion": "asdasdasdas",
            "fecha": data['fecha'],
            "tipoEmision": 1,
            "tipoTransaccion": 2,
            "tipoImpuesto": 1,
            "moneda": "PYG",
            "condicionAnticipo": 1,
            "condicionTipoCambio": 1,
            "descuentoGlobal": 0,
            "anticipoGlobal": 0,
            "cambio": 6700,
            "cliente": data['cliente'],
            "usuario": data['usuario'],
            # Nota Credito
            "notaCreditoDebito": data['notaCreditoDebito'],
            "documentoAsociado": data['documentoAsociado'],
            "condicion": data['condicion'],

            "items": data['items']
        }
    }
    sifen_payload['data']['cliente'] = data['cliente']
    sifen_payload['data']['usuario'] = data['usuario']
    # Nota de credito
    sifen_payload['data']['notaCreditoDebito'] = data['notaCreditoDebito']
    sifen_payload['data']['documentoAsociado'] = data['documentoAsociado']
    sifen_payload['data']['condicion'] = data['condicion']

    sifen_payload['data']['items'] = data['items']
    return sifen_payload


def generate_invoice_pdf_sifen_payload(invoice_header, transaction_id):
    sifen_payload = {
        "params": {
            "ruc": invoice_header.company.sifen_ruc,
            "cdc": invoice_header.invoice_cdc,
            "id_transaccion": transaction_id,
            "logo": invoice_header.company.sifen_logo,
            'xml_text': invoice_header.invoice_xml_text,
        }
    }
    return sifen_payload


def generate_credit_note_pdf_sifen_payload(credit_note_header, transaction_id):
    sifen_payload = {
        "params": {
            "ruc": credit_note_header.company.sifen_ruc,
            "cdc": credit_note_header.credit_note_cdc,
            "id_transaccion": transaction_id,
            "logo": credit_note_header.company.sifen_logo,
            'xml_text': credit_note_header.credit_note_xml_text,
            'nro_documento_padre': credit_note_header.invoice_header.invoice_number
        }
    }
    return sifen_payload


def generate_ruc_validation_sifen_payload(ruc_str, transaction_id):
    empresa = IssuingCompanyName.objects.all().first()
    sifen_payload = {
        "params": {
            "ruc": empresa.sifen_ruc,  # ruc de la empresa que consulta
            "ruc_busqueda": ruc_str,  # ruc consultado
            "password": empresa.sifen_password,  # password de la empresa que consulta
            "id_transaccion": transaction_id
        }
    }
    return sifen_payload


def generate_credit_note_batch_request_payload(credit_note_batch_header, transaction_id):
    sifen_payload = {
        "params": {
            "ruc": credit_note_batch_header.company.sifen_ruc,
            "id_lote": credit_note_batch_header.credit_note_batch_id,
            "password": credit_note_batch_header.company.sifen_password,
            "id_transaccion": transaction_id,
        }
    }
    return sifen_payload


def generate_invoice_batch_request_payload(invoice_header, transaction_id):
    sifen_payload = {
        "params": {
            "ruc": invoice_header.company.sifen_ruc,
            "id_lote": invoice_header.invoice_batch_id,
            "password": invoice_header.company.sifen_password,
            "id_transaccion": transaction_id,
        }
    }
    return sifen_payload


def generate_invoice_data_for_payload(user, invoice):
    # Se preparan los datos de la factura para generar el payload

    invoice_datetime = datetime.combine(invoice.invoice_date, datetime.now().time()).replace(tzinfo=None)
    un_dia = timedelta(days=2)
    invoice_date_send = invoice_datetime + un_dia

    treinta_dias = timedelta(days=30)
    invoice_date_30_days = invoice_datetime + treinta_dias

    if len(invoice.customer.customer_phone_number) < 10:
        celular = ''
    else:
        celular = invoice.customer.customer_phone_number

    # tipoOperacion --> iTiOpe 1=B2B 2=B2C 3=BTG 4=B2F
    if invoice.customer.customer_type == Customer.INDIVIDUAL:
        tipo_operacion = 2
    elif invoice.customer.customer_type == Customer.LEGAL_ENTITY:
        tipo_operacion = 1
    else:
        tipo_operacion = 2

    payment_term = 1 if invoice.payment_term == 'CONTADO' else 2
    if payment_term == 1:
        condition = {
            "tipo": 1,
            "entregas": [
                {
                    "tipo": 1,
                    "monto": str(invoice.invoice_total),
                    "moneda": "PYG",
                    "cambio": 0
                }
            ]
        }
    else:
        condition = {
            "tipo": 2,
            "credito": {
                "tipo": 1,
                "plazo": "30 días",
                "cuotas": 1,
                "montoEntrega": str(invoice.invoice_total),
                "infoCuotas": [
                    {
                        "moneda": "PYG",
                        "monto": str(invoice.invoice_total),
                        "vencimiento": invoice_date_30_days.strftime('%Y-%m-%d'),
                    }
                ]
            }
        }

    items = []

    invoice_point_of_sale = split_invoice_number(invoice.invoice_number)[0]
    invoice_establishment = split_invoice_number(invoice.invoice_number)[1]
    invoice_number = split_invoice_number(invoice.invoice_number)[2]

    for detail in invoice.invoice_details.all():
        if detail.tax_10:
            iva = 10
        else:
            iva = 5

        item = {
            "codigo": "S-001",
            "descripcion": detail.description,
            "observacion": "",
            "partidaArancelaria": 0,
            "ncm": "",
            "unidadMedida": "",
            "cantidad": detail.quantity,
            "precioUnitario": detail.unit_price,
            "cambio": 0,
            "descuento": 0,
            "anticipo": 0,
            "pais": "PRY",
            "paisDescripcion": "Paraguay",
            "tolerancia": 1,
            "toleranciaCantidad": 1,
            "toleranciaPorcentaje": 1,
            "cdcAnticipo": "",
            "ivaTipo": 1,
            "ivaBase": 100,
            "iva": iva,
            "lote": "S-001",
            "vencimiento": "",
            "numeroSerie": "",
            "numeroPedido": "",
            "numeroSeguimiento": "",
            "registroSenave": "",
            "registroEntidadComercial": ""
        }
        items.append(item)

    invoice_data = {
        "punto": invoice_establishment,
        "numero": invoice_number,
        "fecha": invoice_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
        "cliente": {
            "contribuyente": invoice.customer.is_taxpayer,
            "ruc": invoice.customer.customer_tax_id_number,
            "razonSocial": invoice.customer.customer_name,
            "nombreFantasia": invoice.customer.customer_name,
            "tipoOperacion": tipo_operacion,  # tipoOperacion --> iTiOpe 1=B2B 2=B2C 3=BTG 4=B2F
            "direccion": invoice.customer.customer_address,
            "numeroCasa": "1234",
            "departamento": 1,
            "departamentoDescripcion": "CAPITAL",
            "distrito": 1,
            "distritoDescripcion": "Asunción",
            "ciudad": 1,
            "ciudadDescripcion": "Asunción",
            "pais": "PRY",
            "paisDescripcion": "Paraguay",
            "tipoContribuyente": 1,
            "documentoTipo": 1,
            "documentoNumero": invoice.customer.customer_tax_id_number,
            "telefono": invoice.customer.customer_phone_number,
            "celular": celular,
            "email": invoice.customer.customer_email,
            "codigo": zerofill(invoice.customer.id, 3)
        },
        "usuario": {
            "documentoTipo": 1,
            "documentoNumero": user.id,
            "nombre": user.get_full_name(),
            "cargo": "Operador"
        },
        "factura": {
            "presencia": 1,
            "fechaEnvio": invoice_date_send.strftime('%Y-%m-%d'),
        },
        "condicion": condition,
        "items": items
    }
    return invoice_data


def generate_credit_note_data_for_payload(user, credit_note):
    # Se preparan los datos de la nota de credito para generar el payload
    credit_note_datetime = datetime.combine(credit_note.credit_note_date, datetime.now().time()).replace(tzinfo=None)

    # tipoOperacion --> iTiOpe 1=B2B 2=B2C 3=BTG 4=B2F
    if credit_note.customer.customer_type == Customer.INDIVIDUAL:
        tipo_operacion = 2
    elif credit_note.customer.customer_type == Customer.LEGAL_ENTITY:
        tipo_operacion = 1
    else:
        tipo_operacion = 2

    if len(credit_note.customer.customer_phone_number) < 10:
        celular = ''
    else:
        celular = credit_note.customer.customer_phone_number

    # ver si hay que reemplazar esta parte

    condition = {
        "tipo": 1,
        "entregas": [
            {
                "tipo": 1,
                "monto": str(credit_note.credit_note_total),
                "moneda": "PYG",
                "cambio": 0
            }
        ]
    }

    items = []

    credit_note_point_of_sale = split_invoice_number(credit_note.credit_note_number)[0]
    credit_note_establishment = split_invoice_number(credit_note.credit_note_number)[1]
    credit_note_number = split_invoice_number(credit_note.credit_note_number)[2]

    for detail in credit_note.credit_note_details.all():
        if detail.tax_10:
            iva = 10
        else:
            iva = 5

        item = {
            "codigo": "S-001",
            "descripcion": detail.description,
            "observacion": "",
            "partidaArancelaria": 0,
            "ncm": "",
            "unidadMedida": "",
            "cantidad": detail.quantity,
            "precioUnitario": detail.unit_price,
            "cambio": 0,
            "descuento": 0,
            "anticipo": 0,
            "pais": "PRY",
            "paisDescripcion": "Paraguay",
            "tolerancia": 1,
            "toleranciaCantidad": 1,
            "toleranciaPorcentaje": 1,
            "cdcAnticipo": "",
            "ivaTipo": 1,
            "ivaBase": 100,
            "iva": iva,
            "lote": "S-001",
            "vencimiento": "",
            "numeroSerie": "",
            "numeroPedido": "",
            "numeroSeguimiento": "",
            "registroSenave": "",
            "registroEntidadComercial": ""
        }
        items.append(item)

    credit_note_data = {
        "punto": credit_note_establishment,
        "numero": credit_note_number,
        "fecha": credit_note_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
        "cliente": {
            "contribuyente": credit_note.customer.is_taxpayer,
            "ruc": credit_note.customer.customer_tax_id_number,
            "razonSocial": credit_note.customer.customer_name,
            "nombreFantasia": credit_note.customer.customer_name,
            "tipoOperacion": tipo_operacion,  # iTiOpe 1=B2B 2=B2C 3=BTG 4=B2F
            "direccion": credit_note.customer.customer_address,
            "numeroCasa": "1234",
            "departamento": 1,
            "departamentoDescripcion": "CAPITAL",
            "distrito": 1,
            "distritoDescripcion": "Asunción",
            "ciudad": 1,
            "ciudadDescripcion": "Asunción",
            "pais": "PRY",
            "paisDescripcion": "Paraguay",
            "tipoContribuyente": 1,
            "documentoTipo": 1,
            "documentoNumero": credit_note.customer.customer_tax_id_number,
            "telefono": credit_note.customer.customer_phone_number,
            "celular": celular,
            "email": credit_note.customer.customer_email,
            "codigo": zerofill(credit_note.customer.id, 3)
        },
        "usuario": {
            "documentoTipo": 1,
            "documentoNumero": user.id,
            "nombre": user.get_full_name(),
            "cargo": "Operador"
        },
        # Nota de crédito
        "notaCreditoDebito": {
            "motivo": 1,
        },
        "documentoAsociado": {
            "formato": 1,  # iTipDocAso
            "cdc": credit_note.invoice_header.invoice_cdc,
        },
        "condicion": condition,
        "items": items
    }
    return credit_note_data


def generate_sifen_dte(request, invoice_header):
    # Generar invoice data
    transaction_log = SifenTransaction.objects.create(
        user=request.user,
        invoice_header=invoice_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate invoice data for payload
    invoice_data = generate_invoice_data_for_payload(request.user, invoice_header)

    # Generate sifen Payload
    sifen_payload = generate_invoice_sifen_payload(invoice_data, invoice_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_URL

    # Send Sifen Payload Generar Factura
    transaction_log.payload = sifen_payload
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        messages.error(request, 'La Factura no pudo ser enviada a la SET: Error-> ' + error)
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

            invoice_header.save()
            messages.success(request, 'La Factura fue enviada correctamente a la SET')

            # generate_sifen_pdf(request, invoice_header)

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            messages.error(request, 'La Factura no pudo ser enviada a la SET: Error-> '
                           + sifen_response['error'])


def generate_sifen_credit_note_dte(request, credit_note_header):
    # Generar credit note data
    transaction_log = SifenTransaction.objects.create(
        user=request.user,
        credit_note_header=credit_note_header,
        url=None,
        payload=None,
        response=None,
        success=False
    )

    # Generate credit note data for payload
    credit_note_data = generate_credit_note_data_for_payload(request.user, credit_note_header)

    # Generate sifen Payload
    sifen_payload = generate_credit_note_sifen_payload(credit_note_data, credit_note_header,
                                                       transaction_id=transaction_log.id)
    # el url de crear factura es el mismo que el de nota de credito lo que varia es el payload enviado
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_URL

    # Send Sifen Payload Generar Nota de credito
    transaction_log.url = url
    transaction_log.payload = sifen_payload
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        messages.error(request, 'La Nota de crédito no pudo ser enviada a la SET: Error-> ' + error)
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
            credit_note_header.credit_note_cdc = \
                sifen_response['result']['setResponse']['ns2:rRetEnviDe']['ns2:rProtDe'][
                    'ns2:Id']

            credit_note_header.save()
            messages.success(request, 'La Nota de crédito fue enviada correctamente a la SET')

            # generate_sifen_pdf(request, invoice_header)

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            messages.error(request, 'La Nota de crédito no pudo ser enviada a la SET: Error-> '
                           + sifen_response['error'])


def generate_sifen_dte_batch(request, invoice_header):
    # Generar invoice data
    transaction_log = SifenTransaction.objects.create(
        user=request.user,
        url=None,
        invoice_header=invoice_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate invoice data for payload
    invoice_data = generate_invoice_data_for_payload(request.user, invoice_header)

    # Generate sifen Payload
    sifen_payload = generate_invoice_sifen_payload(invoice_data, invoice_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_BATCH_URL

    # Send Sifen Payload Generar Factura
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        messages.error(request, 'La Factura no pudo ser enviada a la SET: Error-> ' + error)
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
            messages.success(request, 'La Factura fue enviada correctamente a la SET')

            # generate_sifen_pdf(request, invoice_header)

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            messages.error(request, 'La Factura no pudo ser enviada a la SET: Error-> '
                           + sifen_response['error'])


def generate_sifen_credit_note_dte_batch(request, credit_note_header):
    # Generar credit note data
    transaction_log = SifenTransaction.objects.create(
        user=request.user,
        url=None,
        invoice_header=None,
        credit_note_header=credit_note_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate credit_note data for payload
    invoice_data = generate_credit_note_data_for_payload(request.user, credit_note_header)

    # Generate sifen Payload
    sifen_payload = generate_credit_note_sifen_payload(invoice_data, credit_note_header,
                                                       transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_BATCH_URL

    # Send Sifen Payload Generar Nota de credito
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        messages.error(request, 'La Nota de crédito no pudo ser enviada a la SET: Error-> ' + error)
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
            messages.success(request, 'La nota de crédito fue enviada correctamente a la SET')

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            messages.error(request, 'La Nota de crédito no pudo ser enviada a la SET: Error-> '
                           + sifen_response['error'])


def generate_sifen_pdf(request, invoice_header):
    # Se genera la transaccion para el pdf
    transaction_log_pdf = SifenTransaction.objects.create(
        user=request.user,
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
        messages.error(request, 'El PDF del KUDE no pudo ser creado: Error-> ' + error)
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
            messages.success(request, 'El PDF del KUDE fue generado satisfactoriamente')

            # Enviar correo si es que el cliente tiene correo
            if not invoice_header.invoice_email_sent:
                send_invoice_email(request, invoice_header)

        else:
            transaction_log_pdf.success = False
            transaction_log_pdf.save()
            messages.error(request, 'No se pudo crear el PDF del KUDE: Error-> '
                           + sifen_response_pdf['error'])


def generate_sifen_invoice_html(request, invoice_header):
    # Se genera la transaccion para el pdf
    transaction_log_html = SifenTransaction.objects.create(
        user=request.user,
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
        messages.error(request, 'El HTML del KUDE no pudo ser creado: Error-> ' + error)
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
            messages.success(request, 'El HTML del KUDE fue generado satisfactoriamente')

            # Enviar correo si es que el cliente tiene correo
            if not invoice_header.invoice_email_sent:
                send_invoice_email_html(request, invoice_header)

        else:
            transaction_log_html.success = False
            transaction_log_html.save()
            messages.error(request, 'No se pudo crear el PDF del KUDE: Error-> '
                           + sifen_response_html['error'])


def generate_sifen_credit_note_pdf(request, credit_note_header):
    # Se genera la transaccion para el pdf
    transaction_log_pdf = SifenTransaction.objects.create(
        user=request.user,
        url=None,
        invoice_header=None,
        credit_note_header=credit_note_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate payload de generar pdf
    sifen_payload_pdf = generate_credit_note_pdf_sifen_payload(credit_note_header,
                                                               transaction_id=transaction_log_pdf.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_PDF_URL

    # Send Sifen Payload Generar PDF Factura
    transaction_log_pdf.payload = sifen_payload_pdf
    transaction_log_pdf.url = url
    transaction_log_pdf.save()
    sifen_response_pdf = send_payload(url, sifen_payload_pdf)

    # IF JSON ERROR
    if sifen_response_pdf == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        messages.error(request, 'El PDF del KUDE no pudo ser creado: Error-> ' + error)
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

            credit_note_header.credit_note_pdf_base64 = sifen_response_pdf['result']['kudeBase64']
            credit_note_header.save()
            messages.success(request, 'El PDF del KUDE fue generado satisfactoriamente')

            # Enviar correo si es que el cliente tiene correo
            if not credit_note_header.credit_note_email_sent:
                send_credit_note_email(request, credit_note_header)

        else:
            transaction_log_pdf.success = False
            transaction_log_pdf.save()
            messages.error(request, 'No se pudo crear el PDF del KUDE: Error-> '
                           + sifen_response_pdf['error'])


def generate_sifen_credit_note_html(request, credit_note_header):
    # Se genera la transaccion para el html
    transaction_log_html = SifenTransaction.objects.create(
        user=request.user,
        url=None,
        invoice_header=None,
        credit_note_header=credit_note_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate payload de generar html
    sifen_payload_html = generate_credit_note_pdf_sifen_payload(credit_note_header,
                                                                transaction_id=transaction_log_html.id)
    url = SIFEN_MIDDLEWARE_GENERATE_INVOICE_HTML_URL

    # Send Sifen Payload Generar HTML Nota de credito
    transaction_log_html.payload = sifen_payload_html
    transaction_log_html.url = url
    transaction_log_html.save()
    sifen_response_html = send_payload(url, sifen_payload_html)

    # IF JSON ERROR
    if sifen_response_html == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        messages.error(request, 'El HTML del KUDE no pudo ser creado: Error-> ' + error)
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
            messages.success(request, 'El HTML del KUDE fue generado satisfactoriamente')

            # Enviar correo si es que el cliente tiene correo
            if not credit_note_header.credit_note_email_sent:
                send_credit_note_email_html(request, credit_note_header)

        else:
            transaction_log_html.success = False
            transaction_log_html.save()
            messages.error(request, 'No se pudo crear el HTML del KUDE: Error-> '
                           + sifen_response_html['error'])


def consult_sifen_credit_note_dte_batch(request, credit_note_header):
    # Se genera la Transacción para consultar el estado del lote de notas de credito
    transaction_log = SifenTransaction.objects.create(
        user=request.user,
        url=None,
        invoice_header=None,
        credit_note_header=credit_note_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate sifen Payload
    sifen_payload = generate_credit_note_batch_request_payload(credit_note_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_REQUEST_INVOICE_BATCH_URL

    # Send Sifen Payload Generar Factura
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        messages.error(request, 'El Lote de La Nota de crédito no pudo ser consultado en la SET: Error-> ' + error)
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
            messages.success(request, 'El Lote fue consultado correctamente en la SET')

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            messages.error(request, 'La Nota de Crédito no pudo ser enviada a la SET: Error-> '
                           + sifen_response['error'])


def consult_sifen_dte_batch(request, invoice_header):
    # Se genera la Transacción para consultar el estado del lote de facturas
    transaction_log = SifenTransaction.objects.create(
        user=request.user,
        url=None,
        invoice_header=invoice_header,
        payload=None,
        response=None,
        success=False
    )

    # Generate sifen Payload
    sifen_payload = generate_invoice_batch_request_payload(invoice_header, transaction_id=transaction_log.id)
    url = SIFEN_MIDDLEWARE_REQUEST_INVOICE_BATCH_URL

    # Send Sifen Payload Generar Factura
    transaction_log.payload = sifen_payload
    transaction_log.url = url
    transaction_log.save()
    sifen_response = send_payload(url, sifen_payload)

    # IF JSON ERROR
    if sifen_response == "JSON DECODE ERROR":
        error = "Ocurrió un error con el parseo del json antes de enviar el payload"
        messages.error(request, 'El Lote de La Factura no pudo ser consultado en la SET: Error-> ' + error)
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
            messages.success(request, 'El Lote fue consultado correctamente en la SET')

        # si la respuesta es un error
        else:
            transaction_log.success = False
            transaction_log.save()
            messages.error(request, 'La Factura no pudo ser enviada a la SET: Error-> '
                           + sifen_response['error'])


def split_invoice_number(string):
    parts = string.split('-')
    return parts


def zerofill(numero, min_digitos):
    numero_str = str(numero)
    while len(numero_str) < min_digitos:
        numero_str = "0" + numero_str
    return numero_str


def invoice_base64_to_pdf(invoice):
    """
    Convierte una cadena de base64 que representa un archivo PDF en un archivo
    PDF descargable.

    Args:
        base64_string (str): La cadena de base64 que representa el archivo PDF.

    Returns:
        django.core.files.File: Un objeto de archivo de Django que representa
        el archivo PDF descargable.
    """
    # Convierte la cadena de base64 en una secuencia de bytes decodificada
    decoded_bytes = base64.b64decode(invoice.invoice_pdf_base64)

    # Crea un objeto de archivo BytesIO a partir de los bytes decodificados
    file_bytes = BytesIO(decoded_bytes)

    # Crea un archivo Django a partir de los bytes del archivo
    file = ContentFile(file_bytes.getvalue())

    # Agrega una extensión pdf al archivo (opcional)
    filename = invoice.invoice_number
    file.name = filename + '.pdf'

    return file


def credit_note_base64_to_pdf(credit_note):
    """
    Convierte una cadena de base64 que representa un archivo PDF en un archivo
    PDF descargable.

    Args:
        base64_string (str): La cadena de base64 que representa el archivo PDF.

    Returns:
        django.core.files.File: Un objeto de archivo de Django que representa
        el archivo PDF descargable.
    """
    # Convierte la cadena de base64 en una secuencia de bytes decodificada
    decoded_bytes = base64.b64decode(credit_note.credit_note_pdf_base64)

    # Crea un objeto de archivo BytesIO a partir de los bytes decodificados
    file_bytes = BytesIO(decoded_bytes)

    # Crea un archivo Django a partir de los bytes del archivo
    file = ContentFile(file_bytes.getvalue())

    # Agrega una extensión pdf al archivo (opcional)
    filename = credit_note.credit_note_number
    file.name = filename + '.pdf'

    return file


def invoice_string_xml_to_xml(invoice):
    # Crea un objeto ContentFile con la cadena de texto
    xml_file = ContentFile(invoice.invoice_xml_text.encode('utf-8'))

    # Asigna una extensión .xml al archivo
    file_name = invoice.invoice_number + '.xml'
    xml_file.name = file_name

    # Guarda el archivo en el almacenamiento predeterminado (default_storage)
    path = default_storage.save(file_name, xml_file)

    # Consigue la ruta completa en el sistema de archivos para el archivo
    full_path = default_storage.path(path)

    # Lee el contenido del archivo generado
    with open(full_path, 'rb') as f:
        contenido = f.read()

    # Borra el archivo generado
    os.remove(full_path)

    response = {
        'name': file_name,
        'file': xml_file
    }

    # Retorna el contenido del archivo y el nombre del archivo generado en un tuple
    return response


def credit_note_string_xml_to_xml(credit_note):
    # Crea un objeto ContentFile con la cadena de texto
    xml_file = ContentFile(credit_note.credit_note_xml_text.encode('utf-8'))

    # Asigna una extensión .xml al archivo
    file_name = credit_note.credit_note_number + '.xml'
    xml_file.name = file_name

    # Guarda el archivo en el almacenamiento predeterminado (default_storage)
    path = default_storage.save(file_name, xml_file)

    # Consigue la ruta completa en el sistema de archivos para el archivo
    full_path = default_storage.path(path)

    # Lee el contenido del archivo generado
    with open(full_path, 'rb') as f:
        contenido = f.read()

    # Borra el archivo generado
    os.remove(full_path)

    response = {
        'name': file_name,
        'file': xml_file
    }

    # Retorna el contenido del archivo y el nombre del archivo generado en un tuple
    return response


def send_invoice_email(request, invoice_header):
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
            messages.success(request, 'La Factura fue enviada correctamente por email al cliente!')
        except Exception as e:
            print(e)
            messages.error(request, 'La Factura no pudo ser enviada por email al cliente: Error-> ' + str(e))
            pass


def send_invoice_email_html(request, invoice_header):
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
                                                                    'el CDC citado aquí abajo.\n' \
                                                                    'El CDC de tu factura es: ' + invoice_header.invoice_cdc + '\n ' \
                                                                                                                               'Saludos\n' + invoice_header.company.sifen_business_name
        mensaje_html = invoice_header.invoice_kude_html
        files = []
        # pdf_file = invoice_base64_to_pdf(invoice_header)
        xml_file = invoice_string_xml_to_xml(invoice_header)
        # files.append(pdf_file)
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
            if request is None:
                print('La Factura fue enviada correctamente por email al cliente!')
            else:
                messages.success(request, 'La Factura fue enviada correctamente por email al cliente!')
        except Exception as e:
            print(e)
            if request is None:
                print('La Factura no pudo ser enviada por email al cliente: Error-> ' + str(e))
            else:
                messages.error(request, 'La Factura no pudo ser enviada por email al cliente: Error-> ' + str(e))
            pass


def send_credit_note_email(request, credit_note_header):
    if credit_note_header.customer.customer_email:
        asunto = credit_note_header.company.sifen_business_name + \
                 ' - Nota de Crédito Electrónica - ' + credit_note_header.credit_note_number
        recipientes = credit_note_header.customer.customer_email
        prioridad = 'now'
        con_template = False
        contexto = ''
        template = ''
        mensaje = 'Hola ' + credit_note_header.customer.customer_name + ':\n ' \
                                                                        'Adjuntamos tus comprobantes legales.\n ' \
                                                                        'Puedes consultar los datos de tu Nota de crédito en https://ekuatia.set.gov.py/consultas ingresando ' \
                                                                        'el CDC citado aquí abajo, o escaneando el Código QR que aparece en el PDF.\n' \
                                                                        'El CDC de tu nota de crédito es: ' + credit_note_header.credit_note_cdc + '\n ' \
                                                                                                                                                   'Saludos\n' + credit_note_header.company.sifen_business_name
        mensaje_html = ''
        files = []
        pdf_file = credit_note_base64_to_pdf(credit_note_header)
        xml_file = credit_note_string_xml_to_xml(credit_note_header)
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
            credit_note_header.credit_note_email_sent = True
            credit_note_header.save()
            messages.success(request, 'La Nota de crédito fue enviada correctamente por email al cliente!')
        except Exception as e:
            print(e)
            messages.error(request, 'La Nota de crédito no pudo ser enviada por email al cliente: Error-> ' + str(e))
            pass


def send_credit_note_email_html(request, credit_note_header):
    if credit_note_header.customer.customer_email:
        asunto = credit_note_header.company.sifen_business_name + \
                 ' - Nota de Crédito Electrónica - ' + credit_note_header.credit_note_number
        recipientes = credit_note_header.customer.customer_email
        prioridad = 'now'
        con_template = False
        contexto = ''
        template = ''
        mensaje = 'Hola ' + credit_note_header.customer.customer_name + ':\n ' \
                                                                        'Adjuntamos tus comprobantes legales.\n ' \
                                                                        'Puedes consultar los datos de tu Nota de crédito en https://ekuatia.set.gov.py/consultas ingresando ' \
                                                                        'el CDC citado aquí abajo.\n' \
                                                                        'El CDC de tu nota de crédito es: ' + credit_note_header.credit_note_cdc + '\n ' \
                                                                                                                                                   'Saludos\n' + credit_note_header.company.sifen_business_name
        mensaje_html = credit_note_header.credit_note_kude_html
        files = []
        # pdf_file = credit_note_base64_to_pdf(credit_note_header)
        xml_file = credit_note_string_xml_to_xml(credit_note_header)
        # files.append(pdf_file)
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
            credit_note_header.credit_note_email_sent = True
            credit_note_header.save()
            if request is None:
                print('La Nota de crédito fue enviada correctamente por email al cliente!')
            else:
                messages.success(request, 'La Nota de crédito fue enviada correctamente por email al cliente!')
        except Exception as e:
            print(e)
            if request is None:
                print('La Nota de crédito no pudo ser enviada por email al cliente: Error-> ' + str(e))
            else:
                messages.error(request,
                               'La Nota de crédito no pudo ser enviada por email al cliente: Error-> ' + str(e))
            pass


class ValidateRucSetView(View):

    def get(self, request, *args, **kwargs):
        ruc_str = kwargs['ruc_str']

        response = validate_ruc_set(ruc_str)

        if response['ok']:
            return JsonResponse(response, status=200, safe=False)
        else:
            return JsonResponse(response, status=500, safe=False)


def validate_ruc_set(ruc_str):
    # busca si existe un customer con ese ruc
    customer = Customer.objects.filter(customer_tax_id_number=ruc_str).first()

    ruc_str_sin_dv = ruc_str.split("-")[0]

    # si existe el customer
    if customer:
        # si el ruc del customer no fue validado
        if customer.sifen_ruc_validated is False:
            # Se genera la transaccion para consultar el ruc
            transaction_log_ruc_validation = SifenTransaction.objects.create(
                user=User.objects.get(username='systemuser'),
                url=None,
                invoice_header=None,
                credit_note_header=None,
                payload=None,
                response=None,
                success=False
            )

            # Generate payload de consultar ruc
            sifen_payload_validate_ruc = generate_ruc_validation_sifen_payload(
                ruc_str_sin_dv, transaction_id=transaction_log_ruc_validation.id)
            url = SIFEN_MIDDLEWARE_VALIDATE_RUC_URL

            # Send Sifen Payload consultar ruc
            transaction_log_ruc_validation.payload = sifen_payload_validate_ruc
            transaction_log_ruc_validation.url = url
            transaction_log_ruc_validation.save()
            sifen_response_validate_ruc = send_payload(url, sifen_payload_validate_ruc)

            # IF JSON ERROR
            if sifen_response_validate_ruc == "JSON DECODE ERROR":
                error = "Ocurrió un error con el parseo del json antes de enviar el payload"
                print('El RUC no pudo ser consultado: Error-> ' + error)
                transaction_log_ruc_validation.response = error
                transaction_log_ruc_validation.success = False
                transaction_log_ruc_validation.save()
            # si no hay error de json
            else:
                print(sifen_response_validate_ruc)
                transaction_log_ruc_validation.response = sifen_response_validate_ruc

                cod_res = sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC']['ns2:dCodRes']

                if cod_res == '0502':  # RUC Encontrado
                    transaction_log_ruc_validation.success = True
                    transaction_log_ruc_validation.save()

                    customer.sifen_ruc_validated = True
                    customer.save()
                    print('El RUC fue consultado satisfactoriamente!')

                    data = {
                        'ok': sifen_response_validate_ruc['ok'],
                        'ruc': ruc_str,
                        'ruc_sin_dv':
                            sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC']['ns2:xContRUC'][
                                'ns2:dRUCCons'],
                        'name':
                            sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC']['ns2:xContRUC'][
                                'ns2:dRazCons'],
                        'error': ''
                    }

                    return data

                elif cod_res == '0500':  # RUC no existe
                    transaction_log_ruc_validation.success = False
                    transaction_log_ruc_validation.save()
                    print('No se pudo verificar el RUC: Error-> ' +
                          sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC'][
                              'ns2:dMsgRes'])

                    data = {
                        'ok': False,
                        'ruc': ruc_str,
                        'ruc_sin_dv': '',
                        'name': '',
                        'error': sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC'][
                            'ns2:dMsgRes']
                    }

                    return data

                # La respuesta de ruc no es exitosa
                else:
                    transaction_log_ruc_validation.success = False
                    transaction_log_ruc_validation.save()
                    print('No se pudo verificar el RUC: Error-> ' + sifen_response_validate_ruc['error'])

                    data = {
                        'ok': sifen_response_validate_ruc['ok'],
                        'ruc': ruc_str,
                        'ruc_sin_dv': '',
                        'name': '',
                        'error': sifen_response_validate_ruc['error']
                    }

                    return data
        else:
            data = {
                'ok': True,
                'ruc': ruc_str,
                'ruc_sin_dv': '',
                'name': customer.customer_name,
                'error': ''
            }

            return data

    # En caso de que no haya encontrado un customer
    else:
        # Se genera la transaccion para consultar el ruc
        transaction_log_ruc_validation = SifenTransaction.objects.create(
            user=User.objects.get(username='systemuser'),
            url=None,
            invoice_header=None,
            credit_note_header=None,
            payload=None,
            response=None,
            success=False
        )

        # Generate payload de consultar ruc
        sifen_payload_validate_ruc = generate_ruc_validation_sifen_payload(
            ruc_str_sin_dv, transaction_id=transaction_log_ruc_validation.id)
        url = SIFEN_MIDDLEWARE_VALIDATE_RUC_URL

        # Send Sifen Payload consultar ruc
        transaction_log_ruc_validation.payload = sifen_payload_validate_ruc
        transaction_log_ruc_validation.url = url
        transaction_log_ruc_validation.save()
        sifen_response_validate_ruc = send_payload(url, sifen_payload_validate_ruc)

        # IF JSON ERROR
        if sifen_response_validate_ruc == "JSON DECODE ERROR":
            error = "Ocurrió un error con el parseo del json antes de enviar el payload"
            print('El RUC no pudo ser consultado: Error-> ' + error)
            transaction_log_ruc_validation.response = error
            transaction_log_ruc_validation.success = False
            transaction_log_ruc_validation.save()
        # si no hay error de json
        else:
            print(sifen_response_validate_ruc)
            transaction_log_ruc_validation.response = sifen_response_validate_ruc
            try:
                cod_res = sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC']['ns2:dCodRes']
            except Exception as error:
                print(error)
                cod_res = ''
            if cod_res == '0502':  # RUC Encontrado
                transaction_log_ruc_validation.success = True
                transaction_log_ruc_validation.save()

                print('El RUC fue consultado satisfactoriamente!')

                data = {
                    'ok': sifen_response_validate_ruc['ok'],
                    'ruc': ruc_str,
                    'ruc_sin_dv':
                        sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC']['ns2:xContRUC'][
                            'ns2:dRUCCons'],
                    'name': sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC']['ns2:xContRUC'][
                        'ns2:dRazCons'],
                    'error': ''
                }

                return data

            elif cod_res == '0500':  # RUC no existe
                transaction_log_ruc_validation.success = False
                transaction_log_ruc_validation.save()
                print('No se pudo verificar el RUC: Error-> ' +
                      sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC']['ns2:dMsgRes'])

                data = {
                    'ok': False,
                    'ruc': ruc_str,
                    'ruc_sin_dv': '',
                    'name': '',
                    'error': sifen_response_validate_ruc['result']['setResponse']['ns2:rResEnviConsRUC']['ns2:dMsgRes']
                }

                return data

            # La respuesta de ruc no es exitosa
            else:
                transaction_log_ruc_validation.success = False
                transaction_log_ruc_validation.save()
                print('No se pudo verificar el RUC: Error-> ' + sifen_response_validate_ruc['error'])

                data = {
                    'ok': sifen_response_validate_ruc['ok'],
                    'ruc': ruc_str,
                    'ruc_sin_dv': '',
                    'name': '',
                    'error': sifen_response_validate_ruc['error']
                }

                return data


class CustomerDatatable(Datatable):
    actions = columns.DisplayColumn(_('Actions'), processor='get_actions')
    is_taxpayer = columns.DisplayColumn(_('Is taxpayer'), processor='get_is_taxpayer')
    customer_type = columns.DisplayColumn(_('Customer Type'), processor='get_customer_type')
    sifen_ruc_validated = columns.DisplayColumn(_('SIFEN RUC Validated'), processor='get_sifen_ruc_validated')
    patient = columns.DisplayColumn(_('Patient'), processor='get_patient')

    class Meta:
        model = Customer
        columns = ['actions',
                   'id',
                   'customer_name',
                   'customer_tax_id_number',
                   'customer_email',
                   'customer_address',
                   'customer_phone_number',
                   'is_taxpayer',
                   'customer_type',
                   'patient',
                   'sifen_ruc_validated'
                   ]

        search_fields = ['id',
                         'customer_name',
                         'customer_tax_id_number',
                         'customer_email',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_actions(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        detail_url = reverse('invoicing.customer_detail', args=[rid])
        update_url = reverse('invoicing.customer_update', args=[rid])
        delete_url = reverse('invoicing.customer_delete', args=[rid])

        str_div_edit = """
                                        <div class="col ">
                                            <a href="{}" class="btn btn-info btn-circle">
                                                <i class="fas fa-pencil-alt"></i>
                                            </a>
                                        </div>
                            """.format(update_url)

        str_div_delete = """
                                        <div class="col ">
                                            <a href="{}" class="btn btn-info btn-circle">
                                                <i class="fas fa-trash"></i>
                                            </a>
                                        </div>
                            """.format(delete_url)

        str_div_detail = """
                    <div class="col ">
                        <a href="{}" class="btn btn-info btn-circle">
                            <i class="fas fa-eye"></i>
                        </a>
                    </div>
        """.format(detail_url)

        str_div_container = """
               <div class="container">
                       <div class="row">
                           {}
                           {}
                           {}
                       </div>
               </div>
        """.format(str_div_detail, str_div_edit, str_div_delete)

        return str_div_container

    @staticmethod
    def get_is_taxpayer(instance, view, *args, **kwargs):
        if instance.is_taxpayer:
            result = 'Si'
        else:
            result = 'No'
        return result

    @staticmethod
    def get_customer_type(instance, view, *args, **kwargs):
        result = dict(Customer.CUSTOMER_TYPES).get(instance.customer_type)
        return result

    @staticmethod
    def get_sifen_ruc_validated(instance, view, *args, **kwargs):
        if instance.sifen_ruc_validated:
            result = 'Si'
        else:
            result = 'No'
        return result

    @staticmethod
    def get_patient(instance, view, *args, **kwargs):
        if instance.patient:
            patient_id = int(instance.patient.pk)
            patient_detail_url = reverse('patient.detail', args=[patient_id])
            return """<div>
                        <a href="{}" target="_blank"> 
                        {}
                        </a>
                    </div>""".format(patient_detail_url, instance.patient)
        else:
            return """<div>
                    <b>Sin Paciente asociado</b>
                </div>"""


class CustomerDataTableView(DatatableView):
    model = Customer
    datatable_class = CustomerDatatable
    template_name = "invoicing/customer/customer_list.html"


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'invoicing/customer/customer_create.html'

    def form_invalid(self, form):
        print("Formulario no valido")
        error = form.errors
        print(error)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('invoicing.customer_list')


class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = "invoicing/customer/customer_update.html"
    form_class = CustomerForm
    context_object_name = 'customer'

    def form_invalid(self, form):
        print("Formulario no valido")
        error = form.errors
        print(error)
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('invoicing.customer_list')


class CustomerDeleteView(DeleteView):
    template_name = "invoicing/customer/customer_delete.html"
    model = Customer
    context_object_name = 'customer'

    def post(self, request, *args, **kwargs):
        client_id = kwargs['pk']
        client = get_object_or_404(Customer, pk=client_id)
        client.delete()

        messages.success(self.request, "El cliente fue eliminado satisfactoriamente.")
        return HttpResponseRedirect(reverse('invoicing.customer_list'))


class CustomerDetailView(DetailView):
    model = Customer
    template_name = "invoicing/customer/customer_detail.html"
    context_object_name = 'customer'
