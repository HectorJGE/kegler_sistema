import ast

import datetime

from auditlog.models import LogEntry
from django.template import loader
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView
from easy_pdf.rendering import render_to_pdf, make_response

from base.models import Currency, UserPrintTagConfiguration
from clinic.forms import PatientForm
from clinic.models import Doctor, Patient, TreatingDoctor
from consultation.forms import ConsultationSheetCreateForm, ConsultationSheetUpdateForm, \
    ConsultationSheetDocumentFormSet, MedicalSupplyUsedCreateFormSet, MedicalSupplyUsedUpdateFormSet, \
    ConsultationEntrySheetCreateForm, ConsultationEntrySheetUpdateForm, ConsultationSheetSalePaymentFormSet, \
    TechnicianConsultationCreateForm, TechnicianConsultationUpdateForm, DoctorConsultationCreateForm, \
    DoctorConsultationUpdateForm, DoctorConsultationReportCreateForm, ConsultationReportUpdateForm, \
    DoctorMultipleConsultationCreateForm, ConsultationAssignFilesForm, ConsultationFileFormSet
from consultation.models import ConsultationSheet, ConsultationState, ConsultationStateUserLog, ConsultationEntrySheet, \
    Consultation, ConsultationReport, DoctorReportTemplate, ConsultationFile, ConsultationSheetDocument, \
    ConsultationSheetDocumentType
from invoicing.models import PaymentMethod
from sales.models import ConsultationEntrySheetSaleHeader, ConsultationSheetSaleDetail, ConsultationSheetSalePayment
from scheduling.models import Appointment, AppointmentState, AppointmentStateUserLog, AppointmentDocumentType
from sistema import settings
from stock.models import Deposit, StockMovement, ProductDepositQuantity
from django.utils.translation import ugettext_lazy as _
from datatableview import Datatable, columns
from datatableview.views import DatatableView


# Create your views here.
# ############################################ CONSULTATION SHEET
# Consultation Sheet List View
class ConsultationSheetListView(LoginRequiredMixin, ListView):
    template_name = 'consultation_sheet/consultation_sheet_list.html'
    context_object_name = "consultation_sheets"
    model = ConsultationSheet
    ordering = ['-consultation_date']


class ConsultationSheetDatatable(Datatable):
    actions = columns.DisplayColumn(_('Actions'), processor='get_actions')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')
    patient_insurance_plan = columns.DisplayColumn(_('Insurance'), source='patient_insurance_plan')

    class Meta:
        model = ConsultationSheet
        columns = ['actions', 'id', 'consultation_date', 'patient', 'patient_insurance_plan', 'medical_study',
                   'doctor', 'medical_equipment', 'total_ammount_to_pay_insurance', 'total_ammount_to_pay_patient',
                   'payment_method', 'treating_doctor', 'reporting_doctor', 'appointment', 'consultation_entry_sheet',
                   'internal_results_delivery_date', 'patient_results_delivery_date', 'consultation_state']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'patient__insurance_plan__name',
                         'medical_study__name',
                         'medical_equipment__name',
                         'doctor__name', 'doctor__last_name',
                         'payment_method__name',
                         'treating_doctor__name', 'treating_doctor__last_name',
                         'reporting_doctor__name', 'reporting_doctor__last_name',
                         'consultation_state__name'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_actions(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        detail_url = reverse('consultation_sheet.detail', args=[rid])
        update_url = reverse('consultation_sheet.update', args=[rid])
        delete_url = reverse('consultation_sheet.delete', args=[rid])
        return """
        <div class="container">
            <div class="row">
                <div class="col " style="width: 80px; ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                        <i class="fas fa-eye"></i>
                    </a>
                </div>
                <div class="col " style="width: 80px; ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                        <i class="fas fa-pencil-alt"></i>
                    </a>
                </div> 
            </div>
        </div>
        """.format(detail_url, update_url)

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M:%S')


class ConsultationSheetListDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationSheet
    datatable_class = ConsultationSheetDatatable
    template_name = 'consultation_sheet/consultation_sheet_list_datatable.html'
    permission_required = 'consultation.view_consultationsheet'
    permission_denied_message = 'No tienes los permisos requeridos'

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetListDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


class ConsultationEntrySheetDatatable(Datatable):
    actions = columns.DisplayColumn(_('Actions'), processor='get_actions')
    consultation_entry_sheet_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_entry_sheet_date')
    studies = columns.DisplayColumn(_('Studies'), processor='get_studies')
    invoice = columns.DisplayColumn(_('Invoice'), processor='get_invoice')
    insurance_invoice = columns.DisplayColumn(_('Insurance Invoice'), processor='get_insurance_invoice')
    patient = columns.DisplayColumn(_('Patient'), processor='get_patient')

    class Meta:
        model = ConsultationEntrySheet
        columns = ['actions', 'id', 'consultation_entry_sheet_date', 'patient', 'studies', 'invoice',
                   'insurance_invoice', 'total_amount', 'total_amount_to_pay_insurance',
                   'total_amount_to_pay_patient', 'total_amount_paid_by_patient', 'patient_balance']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'patient__insurance_plan__name',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_actions(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        detail_url = reverse('consultation_entry_sheet.detail', args=[rid])
        update_url = reverse('consultation_entry_sheet.update', args=[rid])
        delete_url = reverse('consultation_entry_sheet.delete', args=[rid])
        str_div_detail = ''
        str_div_update = ''

        str_div_detail = """
            <div class="col ">
                <a href="{}" class="btn btn-info btn-circle"> 
                    <i class="fas fa-eye"></i>
                </a>
            </div>""".format(detail_url)
        if instance.invoice is None and instance.insurance_invoice is None:
            str_div_update = """
                    <div class="col ">
                        <a href="{}" class="btn btn-info btn-circle"> 
                            <i class="fas fa-pencil-alt"></i>
                        </a>
                    </div>""".format(update_url)

        return """
        <div class="container">
            <div class="row">
                {}
                {} 
            </div>
        </div>
        """.format(str_div_detail, str_div_update)

    @staticmethod
    def get_invoice(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        create_invoice_url = reverse('invoice.create.consultationsheet', args=[rid])
        if instance.invoice is not None:
            detail_url = reverse('invoice_detail', args=[instance.invoice.pk])
            invoice_number = instance.invoice.invoice_number

            return """<div>
                                <a href="{}" target="_blank"> 
                                   {}
                                </a>
                            </div>""".format(detail_url, invoice_number)
        else:
            if instance.total_amount_to_pay_patient > 0:
                return """<div>
                                <a href="{}" class="btn btn-info btn-circle"> 
                                    <i class="fas fa-file-invoice"></i>
                                </a>
                          </div>""".format(create_invoice_url)
            else:
                return "---"

    @staticmethod
    def get_patient(instance, view, *args, **kwargs):
        patient_detail_url = reverse('patient.detail', args=[instance.patient.id])
        if instance.patient is not None:
            return """<div>
                                    <a href="{}" target="_blank"> 
                                       {}
                                    </a>
                                </div>""".format(patient_detail_url, instance.patient)
        else:
            return "---"

    @staticmethod
    def get_insurance_invoice(instance, view, *args, **kwargs):
        if instance.insurance_invoice is not None:
            detail_url = reverse('invoice_detail', args=[instance.insurance_invoice.pk])
            invoice_number = instance.insurance_invoice.invoice_number

            return """<div><a href="{}" target="_blank">{}</a></div>""".format(detail_url, invoice_number)
        else:
            return """---"""

    @staticmethod
    def get_consultation_entry_sheet_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_entry_sheet_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M:%S')

    @staticmethod
    def get_studies(instance, view, *args, **kwargs):
        rid = int(instance.pk)

        str_to_return = """
        <ol>
        """
        for study in instance.consultation_sheets.all():
            str_to_add = """<li>""" + study.medical_study.name + """</li>"""
            str_to_return += str_to_add

        str_to_return += """
        </ol>
        """
        return str_to_return


class ConsultationEntrySheetListDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationEntrySheet
    datatable_class = ConsultationEntrySheetDatatable
    template_name = 'consultation_entry_sheet/consultation_entry_sheet_list_datatable.html'
    permission_required = 'consultation.view_consultationentrysheet'
    permission_denied_message = 'No tienes los permisos requeridos'

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(ConsultationEntrySheetListDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# Consultation Sheet List Unnasigned View
class ConsultationSheetListUnassignedView(LoginRequiredMixin, ListView):
    template_name = 'consultation_sheet/consultation_sheet_list_unassigned.html'
    context_object_name = "consultation_sheets"
    model = ConsultationSheet
    ordering = ['consultation_date']

    def get_queryset(self):
        filed_state = ConsultationState.objects.get(state_code=ConsultationState.FILED_STATE)
        performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
        queryset = ConsultationSheet.objects.filter(
            consultation_state__in=[filed_state, performed_state],
            reporting_doctor=None
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ConsultationSheetListUnassignedView, self).get_context_data(**kwargs)
        context['doctors'] = Doctor.objects.all()
        return context


# Consultation Sheet List UnDelivered View
class ConsultationSheetListUndeliveredView(LoginRequiredMixin, ListView):
    template_name = 'consultation_sheet/consultation_sheet_list_undelivered.html'
    context_object_name = "consultation_sheets"
    model = ConsultationSheet
    ordering = ['consultation_date']

    def get_queryset(self):
        reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
        queryset = ConsultationSheet.objects.filter(
            consultation_state=reported_state
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ConsultationSheetListUndeliveredView, self).get_context_data(**kwargs)
        return context


# Consultation Sheet Detail View
class ConsultationSheetDetailView(LoginRequiredMixin, DetailView):
    template_name = 'consultation_sheet/consultation_sheet_detail.html'
    model = ConsultationSheet
    context_object_name = 'consultation_sheet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        audit_log_entries = LogEntry.objects.filter(object_id=self.object.id, content_type_id=36)
        context['audit_log_entries'] = audit_log_entries
        return context


# Consultation Sheet Update View
class ConsultationSheetUpdateView(PermissionRequiredMixin, UpdateView):
    model = ConsultationSheet
    form_class = ConsultationSheetUpdateForm
    template_name = 'consultation_sheet/consultation_sheet_update_form.html'
    context_object_name = 'consultation_sheet'
    permission_required = 'consultation.change_consultationsheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetUpdateView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect('consultation_entry_sheet.list')

    def get_success_url(self):
        return reverse('consultation_entry_sheet.update', kwargs={'pk': self.object.consultation_entry_sheet.id})

    def get_initial(self):
        currency = Currency.objects.get(name='Guarani')
        patient_name = str(self.object.patient)
        patient_id = self.object.patient.id
        initial = {
            'patient': patient_id,
            'patient_autocomplete': patient_name,
            'currency': currency.id
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super(ConsultationSheetUpdateView, self).get_context_data(**kwargs)
        currency = Currency.objects.get(name='Guarani')
        if self.request.POST:
            context['documents_formset'] = ConsultationSheetDocumentFormSet(self.request.POST, self.request.FILES, instance=self.get_object())
            context['medical_supplies_formset'] = MedicalSupplyUsedUpdateFormSet(self.request.POST, self.request.FILES, instance=self.get_object())
            context['payments_formset'] = ConsultationSheetSalePaymentFormSet(self.request.POST, self.request.FILES, instance=self.get_object())
            for form_medical_supply in context['medical_supplies_formset']:
                form_medical_supply.initial = {'currency': currency}

            for payment in context['payments_formset']:
                payment.initial = {'currency': currency}

        else:
            context['documents_formset'] = ConsultationSheetDocumentFormSet(instance=self.get_object())
            context['medical_supplies_formset'] = MedicalSupplyUsedUpdateFormSet(instance=self.get_object(), initial=[{'currency': currency}])
            context['payments_formset'] = ConsultationSheetSalePaymentFormSet(instance=self.get_object(), initial=[{'currency': currency}])

        return context

    def get_consultation_entry_sheet(self):
        consultation_entry_sheet = ConsultationEntrySheet.objects.filter(pk=self.kwargs.get('consultation_entry_sheet_id')).first()
        return consultation_entry_sheet

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        documents_formset = context['documents_formset']
        medical_supplies_formset = context['medical_supplies_formset']
        payments_formset = context['payments_formset']
        if documents_formset.is_valid() and medical_supplies_formset.is_valid() and payments_formset.is_valid():
            consultation_sheet = form.save()
            consultation_sheet.save()

            documents_formset.instance = consultation_sheet
            documents_formset.save()

            medical_supplies_formset.instance = consultation_sheet
            medical_supplies_formset.save()

            payments_formset.instance = consultation_sheet
            payments_formset.save()

            for new_object in medical_supplies_formset.new_objects:
                default_deposit = Deposit.objects.filter(default_deposit=True).first()
                if default_deposit:
                    stock_movement = StockMovement.objects.create(
                        deposit=default_deposit,
                        quantity=new_object.quantity,
                        product=new_object.medical_supply,
                        type=StockMovement.OUT_MOVEMENT_TYPE,
                        user=self.request.user,
                        description='Movement from consultation sheet creation'
                    )
                    product_deposit = ProductDepositQuantity.objects.filter(deposit=default_deposit, product=new_object.medical_supply).first()
                    if product_deposit:
                        if product_deposit.quantity < 0.0:
                            messages.warning(self.request, 'Atención! el stock de ' + str(new_object.medical_supply) + ' se encuentra ahora en valor negativo.')
                    print(str(stock_movement))
                else:
                    messages.warning(self.request, 'Atención! No se creó ningún movimiento en el stock debido a que no existe un depósito por defecto')

            consultation_entry_sheet = self.get_consultation_entry_sheet()

            messages.success(self.request, 'La Ficha de Estudio fue actualizada satisfactoriamente')
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(self.request, 'Datos de formulario inválidos! '
                                         'Por Favor vuelva a revisar todos los datos. '
                                         'Si los datos son correctos, y el problema persiste, '
                                         'póngase en contacto con un administrador del sistema.')
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        context = self.get_context_data()
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        documents_formset = context['documents_formset']
        medical_supplys_formset = context['medical_supplies_formset']
        return self.render_to_response(self.get_context_data(form=form))


# Consultation Sheet Create View
class ConsultationSheetCreateView(LoginRequiredMixin, CreateView):
    model = ConsultationSheet
    form_class = ConsultationSheetCreateForm
    template_name = 'consultation_sheet/consultation_sheet_create_form.html'

    def get_initial(self):
        currency = Currency.objects.get(name='Guarani')
        filed_state = ConsultationState.objects.get(state_code=ConsultationState.FILED_STATE)
        consultation_entry_sheet = self.get_consultation_entry_sheet()
        patient_name = str(consultation_entry_sheet.patient)

        if consultation_entry_sheet:
            initial = {
                'consultation_date': consultation_entry_sheet.consultation_entry_sheet_date,
                'patient': consultation_entry_sheet.patient.id,
                'patient_autocomplete': patient_name,

                'patient_name': consultation_entry_sheet.patient.name,
                'patient_last_name': consultation_entry_sheet.patient.last_name,
                'patient_sex': consultation_entry_sheet.patient.sex,
                'patient_document_number': consultation_entry_sheet.patient.document_number,

                'patient_weight': consultation_entry_sheet.patient.weight,
                'patient_birth_date': consultation_entry_sheet.patient.birth_date,
                'patient_city': consultation_entry_sheet.patient.city,
                'patient_address': consultation_entry_sheet.patient.address,

                'contact_number': consultation_entry_sheet.patient.phone_number,
                'contact_email': consultation_entry_sheet.patient.email,

                'patient_insurance_plan': consultation_entry_sheet.patient.insurance_plan,

                'consultation_state': filed_state.id,
                'currency': currency,

            }
        else:
            initial = {
                'currency': currency,
                'consultation_state': filed_state.id
            }
        return initial

    def get_consultation_entry_sheet(self):
        consultation_entry_sheet = ConsultationEntrySheet.objects.filter(pk=self.kwargs.get('consultation_entry_sheet_id')).first()
        return consultation_entry_sheet

    def get_context_data(self, **kwargs):
        context = super(ConsultationSheetCreateView, self).get_context_data(**kwargs)
        currency = Currency.objects.get(name='Guarani')
        consultation_entry_sheet = self.get_consultation_entry_sheet()
        context.update(
            {
                'consultation_entry_sheet': consultation_entry_sheet
            }
        )
        if self.request.POST:
            context['documents_formset'] = ConsultationSheetDocumentFormSet(self.request.POST, self.request.FILES)
            context['medical_supplys_formset'] = MedicalSupplyUsedCreateFormSet(self.request.POST, self.request.FILES)

        else:
            context['documents_formset'] = ConsultationSheetDocumentFormSet()
            context['medical_supplys_formset'] = MedicalSupplyUsedCreateFormSet(initial=[{'currency': currency}])

        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        documents_formset = context['documents_formset']
        medical_supplys_formset = context['medical_supplys_formset']
        if documents_formset.is_valid() and medical_supplys_formset.is_valid():

            patient = form.cleaned_data['patient']
            if patient is None or patient == '':
                new_patient = Patient.objects.create(
                    name=form.cleaned_data['patient_name'],
                    last_name=form.cleaned_data['patient_last_name'],
                    sex=form.cleaned_data['patient_sex'],
                    weight=form.cleaned_data['patient_weight'],
                    birth_date=form.cleaned_data['patient_birth_date'],
                    city=form.cleaned_data['patient_city'],
                    address=form.cleaned_data['patient_address'],
                    document_number=form.cleaned_data['patient_document_number'],
                    phone_number=form.cleaned_data['contact_number'],
                    email=form.cleaned_data['contact_email'],
                    insurance_plan=form.cleaned_data['patient_insurance_plan'],
                )
                print('new patien created')
                print(new_patient)
                form.instance.patient = new_patient

            treating_doctor = form.cleaned_data['treating_doctor']
            new_treating_doctor_check_box = form.cleaned_data['new_treating_doctor']
            last_treating_doctor_id = TreatingDoctor.objects.last().id
            # New Treating Doctor
            if treating_doctor is None or treating_doctor == '':
                if new_treating_doctor_check_box:
                    new_treating_doctor = TreatingDoctor.objects.create(
                        name=form.cleaned_data['treating_doctor_name'],
                        last_name=form.cleaned_data['treating_doctor_last_name'],
                        sex=form.cleaned_data['treating_doctor_sex'],
                        document_number=last_treating_doctor_id + 1,
                    )
                    form.instance.treating_doctor = new_treating_doctor

            consultation_sheet = form.save()

            # Consultation Entry Sheet
            consultation_entry_sheet = self.get_consultation_entry_sheet()
            if consultation_entry_sheet:
                consultation_sheet.consultation_entry_sheet = consultation_entry_sheet
            consultation_sheet.save()

            # setting consultation state filed
            consultation_state_user_log = ConsultationStateUserLog.objects.create(
                consultation_sheet=consultation_sheet,
                consultation_state=consultation_sheet.consultation_state,
                user=self.request.user,
            )
            print(consultation_state_user_log)

            if consultation_sheet.reporting_doctor:
                # Performed state
                performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
                consultation_sheet.consultation_state = performed_state
                consultation_sheet.save()

                consultation_state_user_log = ConsultationStateUserLog.objects.create(
                    consultation_sheet=consultation_sheet,
                    consultation_state=consultation_sheet.consultation_state,
                    user=self.request.user,
                )
                print(consultation_state_user_log)

                # Assigned State
                assigned_state = ConsultationState.objects.get(state_code=ConsultationState.ASSIGNED_STATE)
                consultation_sheet.consultation_state = assigned_state
                consultation_sheet.save()

                consultation_state_user_log = ConsultationStateUserLog.objects.create(
                    consultation_sheet=consultation_sheet,
                    consultation_state=consultation_sheet.consultation_state,
                    user=self.request.user,
                )
                print(consultation_state_user_log)

                # Reported State
                reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
                consultation_sheet.consultation_state = reported_state
                consultation_sheet.save()

                consultation_state_user_log = ConsultationStateUserLog.objects.create(
                    consultation_sheet=consultation_sheet,
                    consultation_state=consultation_sheet.consultation_state,
                    user=self.request.user,
                )
                print(consultation_state_user_log)

            patient = consultation_sheet.patient
            patient.phone_number = consultation_sheet.contact_number
            patient.email = consultation_sheet.contact_email
            patient.save()

            documents_formset.instance = consultation_sheet
            documents_formset.save()

            medical_supplys_formset.instance = consultation_sheet
            medical_supplies_used = medical_supplys_formset.save()
            for medical_supply_used in medical_supplies_used:
                default_deposit = Deposit.objects.get(default_deposit=True)
                stock_movement = StockMovement.objects.create(
                    deposit=default_deposit,
                    quantity=medical_supply_used.quantity,
                    product=medical_supply_used.medical_supply,
                    type=StockMovement.OUT_MOVEMENT_TYPE,
                    user=self.request.user,
                    description='Movement from consultation sheet creation'
                )
                product_deposit = ProductDepositQuantity.objects.filter(deposit=default_deposit, product=medical_supply_used.medical_supply).first()
                if product_deposit:
                    if product_deposit.quantity < 0.0:
                        messages.warning(self.request, 'Atención! el stock de ' + str(medical_supply_used.medical_supply) + ' se encuentra ahora en valor negativo.')
                print(str(stock_movement))

            if consultation_entry_sheet:
                sale_header = consultation_entry_sheet.sale_header.all().first()
                if sale_header is None:
                    # creating new sale header
                    new_sale = ConsultationEntrySheetSaleHeader.objects.create(
                        client_name=consultation_entry_sheet.patient.name + ' ' + consultation_entry_sheet.patient.last_name,
                        client_tax_identification_number=consultation_entry_sheet.patient.tax_identification_number,
                        sale_date=consultation_entry_sheet.consultation_entry_sheet_date,
                        sale_total=consultation_entry_sheet.total_amount_to_pay_patient,
                        currency=consultation_entry_sheet.currency,
                        consultation_entry_sheet=consultation_entry_sheet
                    )
                    print(new_sale)
                    sale_header = new_sale

                sale_detail = ConsultationSheetSaleDetail.objects.create(
                    sale_header=sale_header,
                    quantity=1,
                    unit_price=consultation_sheet.total_ammount_to_pay_patient_with_discount,
                    total_price=consultation_sheet.total_ammount_to_pay_patient_with_discount,
                    currency=consultation_sheet.currency
                )
                # Patient Payment
                if consultation_sheet.amount_paid > 0:
                    sale_payment = ConsultationSheetSalePayment.objects.create(
                        sale=sale_detail.sale_header,
                        amount=consultation_sheet.amount_paid,
                        currency=consultation_sheet.currency,
                        payment_method=consultation_sheet.payment_method,
                        consultation_sheet=consultation_sheet,
                        observations="Pago del Paciente al momento de la creación de la ficha"
                    )
                    print(sale_payment)

                # Insurance Payment
                if consultation_sheet.total_ammount_to_pay_insurance > 0:
                    payment_method_insurance = PaymentMethod.objects.get(abbreviation='CS')
                    sale_payment = ConsultationSheetSalePayment.objects.create(
                        sale=sale_detail.sale_header,
                        amount=consultation_sheet.total_ammount_to_pay_insurance,
                        currency=consultation_sheet.currency,
                        payment_method=payment_method_insurance,
                        consultation_sheet=consultation_sheet,
                        observations="Pago del Seguro al momento de la creación de la ficha"
                    )
                    print(sale_payment)
                messages.success(self.request, 'La ficha de estudio fue creada satisfactoriamente.')
                return HttpResponseRedirect(reverse('consultation_entry_sheet.update', kwargs={'pk': consultation_entry_sheet.id}))
            else:
                return HttpResponseRedirect(reverse('consultation_sheet.detail', kwargs={'pk': consultation_sheet.id}))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        context = self.get_context_data()
        documents_formset = context['documents_formset']
        medical_supplys_formset = context['medical_supplys_formset']
        return self.render_to_response(self.get_context_data(form=form))


# Consultation Sheet Create From Appointment View
class ConsultationSheetCreateFromAppointmentView(LoginRequiredMixin, CreateView):
    model = ConsultationSheet
    form_class = ConsultationSheetCreateForm
    template_name = 'consultation_sheet/consultation_sheet_create_form.html'

    def get_appointment(self):
        appointment = get_object_or_404(Appointment, pk=self.kwargs['appointment_id'])
        return appointment

    def get_consultation_entry_sheet(self):
        consultation_entry_sheet = ConsultationEntrySheet.objects.filter(pk=self.kwargs['consultation_entry_sheet_id']).first()
        return consultation_entry_sheet

    def get_initial(self):
        appointment = self.get_appointment()
        filed_state = ConsultationState.objects.get(state_code=ConsultationState.FILED_STATE)
        patient_name = str(appointment.patient)

        initial = {
            'consultation_date': appointment.appointment_date_start,
            'patient': appointment.patient.id,
            'patient_autocomplete': patient_name,

            'patient_name': appointment.patient.name,
            'patient_last_name': appointment.patient.last_name,
            'patient_sex': appointment.patient.sex,
            'patient_document_number': appointment.patient.document_number,

            'patient_weight': appointment.patient.weight,
            'patient_birth_date': appointment.patient.birth_date,
            'patient_city': appointment.patient.city,
            'patient_address': appointment.patient.address,

            'contact_number': appointment.contact_number,
            'contact_email': appointment.contact_email,
            'doctor': appointment.doctor,
            'patient_insurance_plan': appointment.insurance_plan,
            'medical_study': appointment.medical_study,
            'medical_equipment': appointment.medical_equipment,
            'medical_study_ammount': appointment.estimated_cost,
            'total_amount': appointment.estimated_cost,
            'currency': appointment.currency,
            'consultation_state': filed_state.id,
            'reporting_doctor': appointment.doctor,
            'treating_doctor': appointment.treating_doctor
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super(ConsultationSheetCreateFromAppointmentView, self).get_context_data(**kwargs)
        appointment = self.get_appointment()
        consultation_entry_sheet = self.get_consultation_entry_sheet()
        currency = Currency.objects.get(name='Guarani')
        context.update(
            {
                'appointment': appointment,
                'consultation_entry_sheet': consultation_entry_sheet
            }
        )
        if self.request.POST:
            context['documents_formset'] = ConsultationSheetDocumentFormSet(self.request.POST, self.request.FILES)
            context['medical_supplys_formset'] = MedicalSupplyUsedCreateFormSet(self.request.POST, self.request.FILES)

        else:
            if appointment.appointment_documents.count() > 0:
                context['documents_from_appointment'] = appointment.appointment_documents.all()
            else:
                context['documents_from_appointment'] = None
            context['documents_formset'] = ConsultationSheetDocumentFormSet()
            context['medical_supplys_formset'] = MedicalSupplyUsedCreateFormSet(initial=[{'currency': currency}])

        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        documents_formset = context['documents_formset']
        medical_supplys_formset = context['medical_supplys_formset']
        appointment = self.get_appointment()

        if documents_formset.is_valid() and medical_supplys_formset.is_valid():

            patient = form.cleaned_data['patient']
            if patient is None or patient == '':
                new_patient = Patient.objects.create(
                    name=form.cleaned_data['patient_name'],
                    last_name=form.cleaned_data['patient_last_name'],
                    sex=form.cleaned_data['patient_sex'],
                    weight=form.cleaned_data['patient_weight'],
                    birth_date=form.cleaned_data['patient_birth_date'],
                    city=form.cleaned_data['patient_city'],
                    address=form.cleaned_data['patient_address'],
                    document_number=form.cleaned_data['patient_document_number'],
                    phone_number=form.cleaned_data['contact_number'],
                    email=form.cleaned_data['contact_email'],
                    insurance_plan=form.cleaned_data['patient_insurance_plan'],
                )
                print('new patien created')
                print(new_patient)
                form.instance.patient = new_patient
            else:
                # Updating patient
                patient.weight = form.cleaned_data['patient_weight']
                patient.address = form.cleaned_data['patient_address']
                patient.city = form.cleaned_data['patient_city']
                patient.phone_number = form.cleaned_data['contact_number']
                patient.email = form.cleaned_data['contact_email']
                patient.insurance_plan = form.cleaned_data['patient_insurance_plan']
                form.instance.patient = patient

            treating_doctor = form.cleaned_data['treating_doctor']
            new_treating_doctor_check_box = form.cleaned_data['new_treating_doctor']
            last_treating_doctor_id = TreatingDoctor.objects.last().id
            # New Treating Doctor
            if treating_doctor is None or treating_doctor == '':
                if new_treating_doctor_check_box:
                    new_treating_doctor = TreatingDoctor.objects.create(
                        name=form.cleaned_data['treating_doctor_name'],
                        last_name=form.cleaned_data['treating_doctor_last_name'],
                        sex=form.cleaned_data['treating_doctor_sex'],
                        document_number=last_treating_doctor_id + 1,
                    )
                    form.instance.treating_doctor = new_treating_doctor

            consultation_sheet = form.save()

            # Appointment Filed State
            appointments_filed_state = AppointmentState.objects.get(state_code=AppointmentState.FILED_STATE)
            appointment.appointment_state = appointments_filed_state
            appointment.save()

            appointment_state_user_log = AppointmentStateUserLog.objects.filter(appointment=appointment, appointment_state=appointment.appointment_state)
            if not appointment_state_user_log:
                appointment_state_user_log = AppointmentStateUserLog.objects.create(
                    appointment=appointment,
                    appointment_state=appointment.appointment_state,
                    user=self.request.user,
                )
                print(appointment_state_user_log)

            consultation_sheet.appointment = appointment

            # Consultation Entry Sheet
            consultation_entry_sheet = self.get_consultation_entry_sheet()
            if consultation_entry_sheet:
                consultation_sheet.consultation_entry_sheet = consultation_entry_sheet

            consultation_sheet.save()

            # Consultation Filed State
            consultation_state_user_log = ConsultationStateUserLog.objects.filter(consultation_sheet=consultation_sheet, consultation_state=consultation_sheet.consultation_state)
            if not consultation_state_user_log:
                consultation_state_user_log = ConsultationStateUserLog.objects.create(
                    consultation_sheet=consultation_sheet,
                    consultation_state=consultation_sheet.consultation_state,
                    user=self.request.user,
                )
                print(consultation_state_user_log)

            if consultation_sheet.reporting_doctor:
                # Performed state
                performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
                consultation_sheet.consultation_state = performed_state
                consultation_sheet.save()

                consultation_state_user_log = ConsultationStateUserLog.objects.create(
                    consultation_sheet=consultation_sheet,
                    consultation_state=consultation_sheet.consultation_state,
                    user=self.request.user,
                )
                print(consultation_state_user_log)

                # Assigned State
                assigned_state = ConsultationState.objects.get(state_code=ConsultationState.ASSIGNED_STATE)
                consultation_sheet.consultation_state = assigned_state
                consultation_sheet.save()

                consultation_state_user_log = ConsultationStateUserLog.objects.create(
                    consultation_sheet=consultation_sheet,
                    consultation_state=consultation_sheet.consultation_state,
                    user=self.request.user,
                )
                print(consultation_state_user_log)

                # Reported State
                reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
                consultation_sheet.consultation_state = reported_state
                consultation_sheet.save()

                consultation_state_user_log = ConsultationStateUserLog.objects.create(
                    consultation_sheet=consultation_sheet,
                    consultation_state=consultation_sheet.consultation_state,
                    user=self.request.user,
                )
                print(consultation_state_user_log)

            # Filed State
            # appointment = consultation_sheet.appointment
            # appointment_state_filed = AppointmentState.objects.get(state_code=AppointmentState.FILED_STATE)
            # appointment.appointment_state = appointment_state_filed
            # appointment.save()
            #
            # consultation_state_user_log = ConsultationStateUserLog.objects.create(
            #     consultation_sheet=consultation_sheet,
            #     consultation_state=consultation_sheet.consultation_state,
            #     user=self.request.user,
            # )
            # print(consultation_state_user_log)

            patient = appointment.patient
            patient.phone_number = appointment.contact_number
            patient.email = appointment.contact_email
            patient.save()

            documents_formset.instance = consultation_sheet
            documents_formset.save()

            # Appointment documents
            if appointment.appointment_documents.count() > 0:
                for appointment_document in appointment.appointment_documents.all():
                    new_consultation_sheet_document = ConsultationSheetDocument.objects.create(
                        consultation_sheet=consultation_sheet,
                        document_type=ConsultationSheetDocumentType.objects.get(name=appointment_document.document_type.name),
                        file=appointment_document.file
                    )
                    print(new_consultation_sheet_document)

            medical_supplys_formset.instance = consultation_sheet
            medical_supplies_used = medical_supplys_formset.save()
            for medical_supply_used in medical_supplies_used:
                default_deposit = Deposit.objects.get(default_deposit=True)
                stock_movement = StockMovement.objects.create(
                    deposit=default_deposit,
                    quantity=medical_supply_used.quantity,
                    product=medical_supply_used.medical_supply,
                    type=StockMovement.OUT_MOVEMENT_TYPE,
                    user=self.request.user,
                    description='Movement from consultation sheet creation'
                )
                product_deposit = ProductDepositQuantity.objects.filter(deposit=default_deposit, product=medical_supply_used.medical_supply).first()
                if product_deposit:
                    if product_deposit.quantity < 0.0:
                        messages.warning(self.request, 'Atención! el stock de ' + str(medical_supply_used.medical_supply) + ' se encuentra ahora en valor negativo.')
                print(str(stock_movement))

            if consultation_entry_sheet:
                sale_header = consultation_entry_sheet.sale_header.all().first()
                if sale_header is None:
                    # creating new sale header
                    new_sale = ConsultationEntrySheetSaleHeader.objects.create(
                        client_name=consultation_entry_sheet.patient.name + ' ' + consultation_entry_sheet.patient.last_name,
                        client_tax_identification_number=consultation_entry_sheet.patient.tax_identification_number,
                        sale_date=consultation_entry_sheet.consultation_entry_sheet_date,
                        sale_total=consultation_entry_sheet.total_amount_to_pay_patient,
                        currency=consultation_entry_sheet.currency,
                        consultation_entry_sheet=consultation_entry_sheet
                    )
                    print(new_sale)
                    sale_header = new_sale

                sale_detail = ConsultationSheetSaleDetail.objects.create(
                    sale_header=sale_header,
                    quantity=1,
                    unit_price=consultation_sheet.total_ammount_to_pay_patient_with_discount,
                    total_price=consultation_sheet.total_ammount_to_pay_patient_with_discount,
                    currency=consultation_sheet.currency
                )
                # Patient Payment
                if consultation_sheet.amount_paid > 0:
                    sale_payment = ConsultationSheetSalePayment.objects.create(
                        sale=sale_detail.sale_header,
                        amount=consultation_sheet.amount_paid,
                        currency=consultation_sheet.currency,
                        payment_method=consultation_sheet.payment_method,
                        consultation_sheet=consultation_sheet,
                        observations="Pago del Paciente al momento de la creación de la ficha"
                    )
                    print(sale_payment)

                # Insurance Payment
                if consultation_sheet.total_ammount_to_pay_insurance > 0:
                    payment_method_insurance = PaymentMethod.objects.get(abbreviation='CS')
                    sale_payment = ConsultationSheetSalePayment.objects.create(
                        sale=sale_detail.sale_header,
                        amount=consultation_sheet.total_ammount_to_pay_insurance,
                        currency=consultation_sheet.currency,
                        payment_method=payment_method_insurance,
                        consultation_sheet=consultation_sheet,
                        observations="Pago del Seguro al momento de la creación de la ficha"
                    )
                    print(sale_payment)
                messages.success(self.request, 'La ficha de estudio fue creada satisfactoriamente.')
                return HttpResponseRedirect(reverse('consultation_entry_sheet.update', kwargs={'pk': consultation_entry_sheet.id}))
            else:
                return HttpResponseRedirect(reverse('consultation_sheet.detail', kwargs={'pk': consultation_sheet.id}))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        context = self.get_context_data()
        messages.error(self.request, form.errors)
        documents_formset = context['documents_formset']
        medical_supplys_formset = context['medical_supplys_formset']
        return self.render_to_response(self.get_context_data(form=form))


# Consultation Sheet Delete View
class ConsultationSheetDeleteView(PermissionRequiredMixin, DeleteView):
    model = ConsultationSheet
    template_name = "consultation_sheet/consultation_sheet_delete_confirm.html"
    context_object_name = 'consultation_sheet'
    permission_required = 'consultation.delete_consultationsheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetDeleteView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect('consultation_entry_sheet.list')

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        consultation_sheet_id = kwargs['pk']
        consultation_sheet = get_object_or_404(ConsultationSheet, pk=consultation_sheet_id)
        appointment = consultation_sheet.appointment
        if appointment:
            appointments_scheduled_state = AppointmentState.objects.get(state_code=AppointmentState.SCHEDULED_STATE)
            appointment_states = AppointmentStateUserLog.objects.filter(appointment=consultation_sheet.appointment)
            for appointment_state in appointment_states:
                appointment_state.delete()
            new_appointment_state = AppointmentStateUserLog.objects.create(
                appointment=consultation_sheet.appointment,
                appointment_state=appointments_scheduled_state,
                user=self.request.user
            )
            print(new_appointment_state)
            appointment.appointment_state = appointments_scheduled_state
            appointment.save()

        consultation_entry_sheet = consultation_sheet.consultation_entry_sheet
        consultation_sheet.delete()

        messages.success(self.request, 'La Ficha de estudio fue borrada satisfactoriamente.')

        return HttpResponseRedirect(reverse('consultation_entry_sheet.update', kwargs={'pk': consultation_entry_sheet.id}))


# Consultation Sheet Assign Reporting Doctor View
class ConsultationSheetAssignReportingDoctorView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        consultation_sheet_id = kwargs['consultation_sheet_id']
        doctor_id = kwargs['doctor_id']
        consultation_sheet = ConsultationSheet.objects.get(pk=consultation_sheet_id)
        doctor = Doctor.objects.get(pk=doctor_id)

        # Performed state
        performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
        consultation_sheet.consultation_state = performed_state
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        # Assigned State
        assigned_state = ConsultationState.objects.get(state_code=ConsultationState.ASSIGNED_STATE)
        consultation_sheet.consultation_state = assigned_state
        consultation_sheet.reporting_doctor = doctor
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        # Reported State
        reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
        consultation_sheet.consultation_state = reported_state
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        data = {
            'success': True
        }
        return JsonResponse(data, status=200, safe=False)


# Consultation Sheet Mark As Delivered View
class ConsultationSheetMarkAsDeliveredView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        consultation_sheet_id = kwargs['consultation_sheet_id']
        received_by = request.GET.get('received_by')
        consultation_sheet = ConsultationSheet.objects.get(pk=consultation_sheet_id)

        # Prepared state
        prepared_state = ConsultationState.objects.get(state_code=ConsultationState.PREPARED_STATE)
        consultation_sheet.consultation_state = prepared_state
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        # Delivered State
        delivered_state = ConsultationState.objects.get(state_code=ConsultationState.DELIVERED_STATE)
        consultation_sheet.consultation_state = delivered_state
        consultation_sheet.received_by = received_by
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        data = {
            'success': True
        }
        return JsonResponse(data, status=200, safe=False)


# Consultation Sheet Print View
class ConsultationSheetPrintView(LoginRequiredMixin, TemplateView):
    template_name = "consultation_sheet/consultation_sheet_print.html"

    def get_context_data(self, **kwargs):
        context = super(ConsultationSheetPrintView, self).get_context_data(**kwargs)
        consultation_sheet = ConsultationSheet.objects.get(pk=kwargs['pk'])
        context.update(
            {
                'consultation_entry_sheet': None,
                'consultation_sheet': consultation_sheet,
                'studies_sheets': None
            }
        )
        return context


# Consultation Sheet Print Tag View
class ConsultationSheetPrintTagView(LoginRequiredMixin, TemplateView):
    template_name = "consultation_sheet/consultation_sheet_print_tag.html"

    def get_context_data(self, **kwargs):
        context = super(ConsultationSheetPrintTagView, self).get_context_data(**kwargs)
        consultation_sheet = ConsultationSheet.objects.get(pk=kwargs['pk'])
        user_print_tag_configuration = UserPrintTagConfiguration.objects.get(user=self.request.user)
        context.update(
            {
                'consultation_sheet': consultation_sheet,
                'user_print_tag_configuration': user_print_tag_configuration,
            }
        )
        return context


# ############################################ CONSULTATION ENTRY SHEET
# Consultation Entry Sheet List View
class ConsultationEntrySheetListView(LoginRequiredMixin, ListView):
    template_name = 'consultation_entry_sheet/consultation_entry_sheet_list.html'
    context_object_name = "consultation_entry_sheets"
    model = ConsultationEntrySheet
    ordering = ['-consultation_entry_sheet_date']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConsultationEntrySheetListView, self).get_context_data(**kwargs)
        return context


# Consultation Entry Sheet Create View
class ConsultationEntrySheetCreateView(LoginRequiredMixin, CreateView):
    model = ConsultationEntrySheet
    form_class = ConsultationEntrySheetCreateForm
    template_name = 'consultation_entry_sheet/consultation_entry_sheet_create_form.html'

    def get_initial(self):
        currency = Currency.objects.get(name='Guarani')
        initial = {
            'currency': currency.id
        }

        if self.request.GET.get('consultation_sheet_ids'):
            consultation_sheet_ids = self.request.GET.getlist('consultation_sheet_ids')
            consultation_sheets = ConsultationSheet.objects.filter(pk__in=consultation_sheet_ids)
            initial = {
                'consultation_entry_sheet_date': consultation_sheets[0].consultation_date,
                'patient': consultation_sheets[0].patient,
            }

        return initial

    def form_invalid(self, form):
        messages.error(self.request, 'Error de validación del formulario')
        return self.render_to_response(self.get_context_data(form=form))

    @transaction.atomic
    def form_valid(self, form):
        patient = form.cleaned_data['patient']
        # New Patient
        if patient is None or patient == '':
            patient_data = {
                'name': form.cleaned_data['patient_name'],
                'last_name': form.cleaned_data['patient_last_name'],
                'sex': form.cleaned_data['patient_sex'],
                'weight': form.cleaned_data['patient_weight'],
                'birth_date': form.cleaned_data['patient_birth_date'],
                'city': form.cleaned_data['patient_city'],
                'address': form.cleaned_data['patient_address'],
                'document_number': form.cleaned_data['patient_document_number'],
                'tax_identification_number': form.cleaned_data['patient_tax_identification_number'],
                'tax_identification_name': form.cleaned_data['patient_tax_identification_name'],
                'phone_number': form.cleaned_data['patient_phone_number'],
                'email': form.cleaned_data['patient_email'],
                'insurance_plan': form.cleaned_data['patient_insurance_plan']
            }
            patient_form = PatientForm(
                data=patient_data
            )
            if patient_form.is_valid():
                patient = patient_form.save()
                form.instance.patient = patient
            else:
                form_errors = []
                for error in patient_form.errors:
                    form_errors.append(patient_form.errors[error][0])

                messages.error(self.request, patient_form.errors)
                return self.render_to_response(self.get_context_data(form=form))
        else:
            # Updating patient
            patient.weight = form.cleaned_data['patient_weight']
            patient.address = form.cleaned_data['patient_address']
            patient.city = form.cleaned_data['patient_city']
            patient.tax_identification_number = form.cleaned_data['patient_tax_identification_number']
            patient.tax_identification_name = form.cleaned_data['patient_tax_identification_name']
            patient.phone_number = form.cleaned_data['patient_phone_number']
            patient.email = form.cleaned_data['patient_email']
            patient.insurance_plan = form.cleaned_data['patient_insurance_plan']
            form.instance.patient = patient

        consultation_entry_sheet = form.save()

        sale_header = consultation_entry_sheet.sale_header.all().first() if hasattr(consultation_entry_sheet, 'sale_header') else None
        if sale_header is None:
            sale = ConsultationEntrySheetSaleHeader.objects.create(
                consultation_entry_sheet=consultation_entry_sheet,
                client_name=consultation_entry_sheet.patient.name + ' ' + consultation_entry_sheet.patient.last_name,
                client_tax_identification_number=consultation_entry_sheet.patient.tax_identification_number,
                sale_date=consultation_entry_sheet.consultation_entry_sheet_date,
                sale_total=0,
                currency=consultation_entry_sheet.currency
            )
            print(sale)
            sale_header = sale

        if form.data.get('consultation_sheets'):
            consultation_sheet_ids = form.data.getlist('consultation_sheets')
            consultation_sheets = ConsultationSheet.objects.filter(pk__in=consultation_sheet_ids)

            for consultation_sheet in consultation_sheets:
                consultation_sheet.consultation_entry_sheet = consultation_entry_sheet
                consultation_sheet.save()

        messages.success(self.request, 'Ficha de Entrada Creada Exitosamente!')
        return HttpResponseRedirect(reverse('consultation_entry_sheet.update', kwargs={'pk': consultation_entry_sheet.id}))

    def get_context_data(self, **kwargs):
        context = super(ConsultationEntrySheetCreateView, self).get_context_data(**kwargs)
        if self.request.GET.get('consultation_sheet_ids'):
            consultation_sheet_ids = self.request.GET.getlist('consultation_sheet_ids')
            consultation_sheets = ConsultationSheet.objects.filter(pk__in=consultation_sheet_ids)

            if consultation_sheets:
                patient = consultation_sheets.first().patient
                consultation_date = consultation_sheets.first().consultation_date
                day_start = datetime.datetime(
                    year=consultation_date.year,
                    month=consultation_date.month,
                    day=consultation_date.day,
                    hour=0,
                    minute=0,
                    second=0
                )
                day_end = datetime.datetime(
                    year=consultation_date.year,
                    month=consultation_date.month,
                    day=consultation_date.day,
                    hour=22,
                    minute=59,
                    second=59
                )
                day_start = timezone.make_aware(day_start)
                day_end = timezone.make_aware(day_end)
            else:
                patient = None
                day_start = None
                day_end = None

            patient_consultation_sheets_of_the_day = []
            patient_appointments_of_the_day = []

            if patient:
                patient_consultation_sheets_of_the_day = ConsultationSheet.objects.filter(
                    patient=patient, consultation_date__range=[day_start, day_end],
                    consultation_entry_sheet=None
                ).exclude(pk__in=consultation_sheet_ids)

                patient_appointments_of_the_day = Appointment.objects.filter(
                    patient=patient, appointment_date_start__range=[day_start, day_end],
                    consultation_sheets=None
                )

            context.update(
                {
                    'consultation_sheets': consultation_sheets,
                    'patient_consultation_sheets_of_the_day': patient_consultation_sheets_of_the_day,
                    'patient_appointments_of_the_day': patient_appointments_of_the_day,
                }
            )
        return context


# Consultation Entry Sheet Update View
class ConsultationEntrySheetUpdateView(LoginRequiredMixin, UpdateView):
    model = ConsultationEntrySheet
    form_class = ConsultationEntrySheetUpdateForm
    template_name = 'consultation_entry_sheet/consultation_entry_sheet_update_form.html'
    context_object_name = 'consultation_entry_sheet'

    def get_initial(self):
        patient = self.object.patient
        consultation_sheets = self.object.consultation_sheets.all()
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

        self.object.total_amount = total_amount
        self.object.total_amount_to_pay_insurance = total_amount_to_pay_insurance
        self.object.total_amount_to_pay_patient = total_amount_to_pay_patient
        self.object.total_amount_paid_by_patient = total_amount_paid_by_patient
        self.object.patient_balance = patient_balance
        self.object.save()

        initial = {
            # Static info
            'patient_name': patient.name,
            'patient_autocomplete': str(patient),
            'patient_last_name': patient.last_name,
            'patient_sex': patient.sex,
            'patient_birth_date': patient.birth_date,
            'patient_document_number': patient.document_number,

            # Changing info
            'patient_weight': patient.weight,
            'patient_city': patient.city,
            # invoicing
            'patient_tax_identification_number': patient.tax_identification_number,
            'patient_tax_identification_name': patient.tax_identification_name,
            'patient_phone_number': patient.phone_number,
            'patient_email': patient.email,
            'patient_address': patient.address,
            'patient_is_taxpayer': patient.is_taxpayer,

            'patient_insurance_plan': patient.insurance_plan,

        }
        return initial

    def form_invalid(self, form):
        context = self.get_context_data()
        return self.render_to_response(self.get_context_data(form=form))

    @transaction.atomic
    def form_valid(self, form):
        patient = form.cleaned_data['patient']
        # New Patient
        if patient is None or patient == '':
            new_patient = Patient.objects.create(
                name=form.cleaned_data['patient_name'],
                last_name=form.cleaned_data['patient_last_name'],
                sex=form.cleaned_data['patient_sex'],
                weight=form.cleaned_data['patient_weight'],
                birth_date=form.cleaned_data['patient_birth_date'],
                city=form.cleaned_data['patient_city'],
                document_number=form.cleaned_data['patient_document_number'],
                # invoicing
                address=form.cleaned_data['patient_address'],
                tax_identification_number=form.cleaned_data['patient_tax_identification_number'],
                tax_identification_name=form.cleaned_data['patient_tax_identification_name'],
                phone_number=form.cleaned_data['patient_phone_number'],
                email=form.cleaned_data['patient_email'],
                is_taxpayer=form.cleaned_data['patient_is_taxpayer'],

                insurance_plan=form.cleaned_data['patient_insurance_plan'],
            )
            form.instance.patient = new_patient
        else:
            # Updating patient
            patient.weight = form.cleaned_data['patient_weight']
            patient.city = form.cleaned_data['patient_city']
            # invoicing
            patient.tax_identification_number = form.cleaned_data['patient_tax_identification_number']
            patient.tax_identification_name = form.cleaned_data['patient_tax_identification_name']
            patient.phone_number = form.cleaned_data['patient_phone_number']
            patient.email = form.cleaned_data['patient_email']
            patient.address = form.cleaned_data['patient_address']
            patient.is_taxpayer = form.cleaned_data['patient_is_taxpayer']

            patient.insurance_plan = form.cleaned_data['patient_insurance_plan']
            form.instance.patient = patient
            patient.save()

        consultation_entry_sheet = form.save()
        if form.data.get('consultation_sheets'):
            originals_consultation_sheets = self.object.consultation_sheets.all()
            consultation_sheet_ids = form.data.getlist('consultation_sheets')
            consultation_sheets_from_form = ConsultationSheet.objects.filter(pk__in=consultation_sheet_ids)

            for consultation_sheet in consultation_sheets_from_form:
                consultation_sheet.consultation_entry_sheet = consultation_entry_sheet
                consultation_sheet.save()

            set1 = set(originals_consultation_sheets)
            set2 = set(consultation_sheets_from_form)

            missing_consultation_sheets = list(sorted(set1 - set2))

            for missing_consultation_sheet in missing_consultation_sheets:
                missing_consultation_sheet.consultation_entry_sheet = None
                missing_consultation_sheet.save()

        messages.success(self.request, 'Ficha de Entrada Actualizada Exitosamente!')
        return HttpResponseRedirect(reverse('consultation_entry_sheet.update', kwargs={'pk': consultation_entry_sheet.id}))

    def get_context_data(self, **kwargs):
        context = super(ConsultationEntrySheetUpdateView, self).get_context_data(**kwargs)
        consultation_sheets = self.object.consultation_sheets.all()
        patient = self.object.patient
        consultation_date = utc_to_local(self.object.consultation_entry_sheet_date)

        day_start = None
        day_end = None

        if consultation_date:
            day_start = datetime.datetime(
                year=consultation_date.year,
                month=consultation_date.month,
                day=consultation_date.day,
                hour=1,
                minute=0,
                second=0
            )
            day_end = datetime.datetime(
                year=consultation_date.year,
                month=consultation_date.month,
                day=consultation_date.day,
                hour=22,
                minute=59,
                second=59
            )

            day_start = timezone.make_aware(day_start)
            day_end = timezone.make_aware(day_end)

        patient_consultation_sheets_of_the_day = []
        patient_appointments_of_the_day = []

        if patient and consultation_date:
            scheduled_state = AppointmentState.objects.get(state_code=AppointmentState.SCHEDULED_STATE)

            patient_consultation_sheets_of_the_day = ConsultationSheet.objects.filter(
                patient=patient, consultation_date__range=[day_start, day_end],
                consultation_entry_sheet=None
            ).exclude(pk__in=list(consultation_sheets.values_list('id', flat=True)))

            patient_appointments_of_the_day = Appointment.objects.filter(
                patient=patient, appointment_date_start__range=[day_start, day_end],
                appointment_state=scheduled_state
            )

        context.update(
            {
                'consultation_sheets': consultation_sheets,
                'patient_consultation_sheets_of_the_day': patient_consultation_sheets_of_the_day,
                'patient_appointments_of_the_day': patient_appointments_of_the_day,
            }
        )
        return context


# Consultation Entry Sheet Detail View
class ConsultationEntrySheetDetailView(LoginRequiredMixin, DetailView):
    model = ConsultationEntrySheet
    template_name = 'consultation_entry_sheet/consultation_entry_sheet_detail.html'
    context_object_name = 'consultation_entry_sheet'

    def get_context_data(self, **kwargs):
        context = super(ConsultationEntrySheetDetailView, self).get_context_data(**kwargs)
        return context


# Consultation Entry Sheet Print View
class ConsultationEntrySheetPrintView(LoginRequiredMixin, TemplateView):
    template_name = "consultation_entry_sheet/consultation_entry_sheet_print.html"

    def get_context_data(self, **kwargs):
        context = super(ConsultationEntrySheetPrintView, self).get_context_data(**kwargs)
        consultation_entry_sheet = ConsultationEntrySheet.objects.get(pk=kwargs['pk'])

        context.update(
            {
                'consultation_entry_sheet': consultation_entry_sheet,
            }

        )

        if consultation_entry_sheet.consultation_sheets.all():
            studies_selected = self.request.GET.getlist('studies_selected')
            if studies_selected:
                studies_sheets = ConsultationSheet.objects.filter(id__in=studies_selected)
            else:
                studies_sheets = consultation_entry_sheet.consultation_sheets.all().order_by('patient_results_delivery_date')

            context.update(
                {
                    'consultation_sheet': consultation_entry_sheet.consultation_sheets.all()[0],
                    'studies_sheets': studies_sheets,
                }

            )
        return context


class CreateConsultationEntrySheetFromAppointment(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        appointment = get_object_or_404(Appointment, pk=self.kwargs['appointment_id'])
        consultation_entry_sheet = ConsultationEntrySheet.objects.create(
            patient=appointment.patient,
            consultation_entry_sheet_date=timezone.now(),
            total_amount=0,
            total_amount_to_pay_insurance=0,
            total_amount_to_pay_patient=0,
            total_amount_paid_by_patient=0,
            patient_balance=0,
            currency=appointment.currency,
        )
        sale_header = ConsultationEntrySheetSaleHeader.objects.create(
            client_name=consultation_entry_sheet.patient.name + ' ' + consultation_entry_sheet.patient.last_name,
            client_tax_identification_number=consultation_entry_sheet.patient.tax_identification_number,
            sale_date=consultation_entry_sheet.consultation_entry_sheet_date,
            sale_total=0,
            consultation_entry_sheet=consultation_entry_sheet,
            currency=consultation_entry_sheet.currency
        )
        print(sale_header)
        return HttpResponseRedirect(reverse('consultation_entry_sheet.update', kwargs={'pk': consultation_entry_sheet.id}))


# Consultation Entry Sheet Delete View
class ConsultationEntrySheetDeleteView(PermissionRequiredMixin, DeleteView):
    model = ConsultationEntrySheet
    template_name = "consultation_entry_sheet/consultation_entry_sheet_delete_confirm.html"
    context_object_name = 'consultation_entry_sheet'
    permission_required = 'consultation.delete_consultationentrysheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def handle_no_permission(self):
        try:
            return super(ConsultationEntrySheetDeleteView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect('consultation_entry_sheet.list')

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        consultation_entry_sheet_id = kwargs['pk']
        consultation_entry_sheet = get_object_or_404(ConsultationEntrySheet, pk=consultation_entry_sheet_id)
        for consultation_sheet in consultation_entry_sheet.consultation_sheets.all():
            appointment = consultation_sheet.appointment
            if appointment:
                appointments_scheduled_state = AppointmentState.objects.get(state_code=AppointmentState.SCHEDULED_STATE)
                appointment_states = AppointmentStateUserLog.objects.filter(appointment=consultation_sheet.appointment)
                for appointment_state in appointment_states:
                    appointment_state.delete()
                new_appointment_state = AppointmentStateUserLog.objects.create(
                    appointment=consultation_sheet.appointment,
                    appointment_state=appointments_scheduled_state,
                    user=self.request.user
                )
                appointment.appointment_state = appointments_scheduled_state
                appointment.save()
                print(new_appointment_state)
            consultation_sheet.delete()

        consultation_entry_sheet.delete()

        messages.success(self.request, 'La Ficha de Entrada fue borrada satisfactoriamente.')
        return HttpResponseRedirect(reverse('consultation_entry_sheet.list'))


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


class ConsultationSheetUnassignedDatatable(Datatable):
    reporting_doctor = columns.DisplayColumn(_('Reporting Doctor'), processor='get_reporting_doctor_action')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')
    patient_insurance_plan = columns.DisplayColumn(_('Insurance'), source='patient_insurance_plan')

    class Meta:
        model = ConsultationSheet
        columns = ['reporting_doctor', 'id', 'consultation_date', 'patient', 'patient_insurance_plan', 'medical_study',
                   'medical_equipment', 'consultation_state']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'patient__insurance_plan__name',
                         'medical_study__name',
                         'medical_equipment__name',
                         'reporting_doctor__name', 'reporting_doctor__last_name',
                         'consultation_state__name'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_reporting_doctor_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        id = str(rid)
        doctors = Doctor.objects.all()
        str_doctors = ""
        for doctor in doctors:
            str_doctors += "<option value=" + str(doctor.id)+ ">" + doctor.name + " " + doctor.last_name + "</option>"
        str_return = """
                <td>
                  <div id="div_id_reporting_doctor_select_""" + id + """" class="form-group">
                    <select class="select form-control reporting-doctor-select"
                            id="id_reporting_doctor_select_""" + id + """"
                            name="reporting_doctor"
                            data-consultation-sheet-id='""" + id + """'
                    >
                      <option value="">------</option>
                      """ + str_doctors + """
                    </select>
                  </div>
                </td>
                """

        return str_return

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M:%S')


class ConsultationSheetListUnassignedDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationSheet
    datatable_class = ConsultationSheetUnassignedDatatable
    template_name = 'consultation_sheet/consultation_sheet_list_unassigned_datatable.html'
    permission_required = 'consultation.view_consultationsheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_login_url(self):
        return reverse('dashboard')

    def get_queryset(self):
        filed_state = ConsultationState.objects.get(state_code=ConsultationState.FILED_STATE)
        performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
        queryset = ConsultationSheet.objects.filter(
            # consultation_state__in=[performed_state],
            consultation_state__in=[filed_state],
            reporting_doctor=None
        )
        return queryset

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetListUnassignedDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


class ConsultationSheetAssignedDatatable(Datatable):
    reporting_doctor = columns.DisplayColumn(_('Reporting Doctor'), processor='get_reporting_doctor_action')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')
    patient_insurance_plan = columns.DisplayColumn(_('Insurance'), source='patient_insurance_plan')

    class Meta:
        model = ConsultationSheet
        columns = ['reporting_doctor', 'id', 'consultation_date', 'patient', 'patient_insurance_plan', 'medical_study',
                   'medical_equipment', 'consultation_state']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'patient__insurance_plan__name',
                         'medical_study__name',
                         'medical_equipment__name',
                         'reporting_doctor__name', 'reporting_doctor__last_name',
                         'consultation_state__name'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_reporting_doctor_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        id = str(rid)
        doctors = Doctor.objects.all()
        str_doctors = ""
        for doctor in doctors:
            if doctor.id == instance.reporting_doctor.id:
                str_doctors += "<option selected value=" + str(doctor.id) + ">" + doctor.name + " " + doctor.last_name + "</option>"
            else:
                str_doctors += "<option value=" + str(doctor.id) + ">" + doctor.name + " " + doctor.last_name + "</option>"
        str_return = """
                <td>
                  <div id="div_id_reporting_doctor_select_""" + id + """" class="form-group">
                    <select class="select form-control reporting-doctor-select"
                            id="id_reporting_doctor_select_""" + id + """"
                            name="reporting_doctor"
                            data-consultation-sheet-id='""" + id + """'
                    >
                      <option value="">------</option>
                      """ + str_doctors + """
                    </select>
                  </div>
                </td>
                """

        return str_return

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M:%S')


class ConsultationSheetListAssignedDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationSheet
    datatable_class = ConsultationSheetAssignedDatatable
    template_name = 'consultation_sheet/consultation_sheet_list_assigned_datatable.html'
    permission_required = 'consultation.view_consultationsheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_login_url(self):
        return reverse('dashboard')

    def get_queryset(self):
        assigned_state = ConsultationState.objects.get(state_code=ConsultationState.ASSIGNED_STATE)
        queryset = ConsultationSheet.objects.filter(
            consultation_state__in=[assigned_state]
        )
        return queryset

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetListAssignedDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# ############################### Consultation Sheet UnDelivered Datatable
class ConsultationSheetUnDeliveredDatatable(Datatable):
    action = columns.DisplayColumn(_('Received By'), processor='get_action')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')
    patient_insurance_plan = columns.DisplayColumn(_('Insurance'), source='patient_insurance_plan')
    internal_results_delivery_date = columns.DisplayColumn(_('Internal Results Delivery Date'), processor='get_internal_results_delivery_date')
    patient_results_delivery_date = columns.DisplayColumn(_('Patient Results Delivery Date'), processor='get_patient_results_delivery_date')

    class Meta:
        model = ConsultationSheet
        columns = ['action', 'id', 'consultation_date', 'patient', 'patient_insurance_plan', 'medical_study',
                   'reporting_doctor', 'internal_results_delivery_date', 'patient_results_delivery_date', 'consultation_state']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'patient__insurance_plan__name',
                         'medical_study__name',
                         'medical_equipment__name',
                         'reporting_doctor__name', 'reporting_doctor__last_name',
                         'consultation_state__name'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']


    @staticmethod
    def get_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        id = str(rid)
        str_return = """
              <td>
                <div style="padding-top: 20px" id="div_id_received_by_""" + id + """" class="form-group">
                  <input style="text-transform: uppercase; width: 132px;" class="textinput textInput form-control to-upper-case" id="id_received_by_""" + id + """" type="text" placeholder="Nombre y CI">
                </div>
              </td>
              <td>
                <div style="padding-top: 20px" class="form-group">
                  <input class="btn btn-sm btn-success shadow-sm mark-as-delivered-button" data-consultation-sheet-id='""" + id + """' type="button" value="Marcar Como entregado">
                </div>
              </td>
        """
        return str_return

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')

    @staticmethod
    def get_internal_results_delivery_date(instance, view, *args, **kwargs):
        if instance.internal_results_delivery_date:
            date_to_return = utc_to_local(instance.internal_results_delivery_date)
            return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')
        else:
            return None

    @staticmethod
    def get_patient_results_delivery_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        if instance.patient_results_delivery_date:
            date_to_return = utc_to_local(instance.patient_results_delivery_date)
            return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')
        else:
            return None


# ############################### Consultation Sheet UnDelivered Datatable View
class ConsultationSheetListUnDeliveredDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationSheet
    datatable_class = ConsultationSheetUnDeliveredDatatable
    template_name = 'consultation_sheet/consultation_sheet_list_undelivered_datatable.html'
    permission_required = 'consultation.view_consultationsheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_login_url(self):
        return reverse('dashboard')

    def get_queryset(self):
        # finished_state = ConsultationState.objects.get(state_code=ConsultationState.FINISHED_STATE)
        reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
        queryset = ConsultationSheet.objects.filter(
            # Q(consultation_state=finished_state) | Q(consultation_state=reported_state)
            consultation_state=reported_state
        )
        return queryset

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetListUnDeliveredDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# ############################### Consultation Sheet Delivered Datatable
class ConsultationSheetDeliveredDatatable(Datatable):

    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')
    patient_insurance_plan = columns.DisplayColumn(_('Insurance'), source='patient_insurance_plan')

    patient_results_delivery_date = columns.DisplayColumn(_('Patient Results Delivery Date'), processor='get_patient_results_delivery_date')

    class Meta:
        model = ConsultationSheet
        columns = ['id', 'consultation_date', 'patient', 'patient_insurance_plan', 'medical_study',
                   'reporting_doctor', 'patient_results_delivery_date', 'received_by', 'consultation_state']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'patient__insurance_plan__name',
                         'medical_study__name',
                         'medical_equipment__name',
                         'reporting_doctor__name', 'reporting_doctor__last_name',
                         'consultation_state__name'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')

    @staticmethod
    def get_internal_results_delivery_date(instance, view, *args, **kwargs):
        if instance.internal_results_delivery_date:
            date_to_return = utc_to_local(instance.internal_results_delivery_date)
            return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')
        else:
            return None

    @staticmethod
    def get_patient_results_delivery_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        if instance.patient_results_delivery_date:
            date_to_return = utc_to_local(instance.patient_results_delivery_date)
            return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')
        else:
            return None


# ############################### Consultation Sheet Delivered Datatable View
class ConsultationSheetListDeliveredDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationSheet
    datatable_class = ConsultationSheetDeliveredDatatable
    template_name = 'consultation_sheet/consultation_sheet_list_delivered_datatable.html'
    permission_required = 'consultation.view_consultationsheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_login_url(self):
        return reverse('dashboard')

    def get_queryset(self):
        delivered_state = ConsultationState.objects.get(state_code=ConsultationState.DELIVERED_STATE)
        queryset = ConsultationSheet.objects.filter(
            consultation_state=delivered_state
        )
        return queryset

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetListDeliveredDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# ############################### Consultation Sheet UnRealized Datatable
class ConsultationSheetUnRealizedTechnicianDatatable(Datatable):
    action = columns.DisplayColumn(_('Action'), processor='get_action')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')
    patient_insurance_plan = columns.DisplayColumn(_('Insurance'), source='patient_insurance_plan')

    class Meta:
        model = ConsultationSheet
        columns = ['action', 'id', 'consultation_date', 'patient', 'medical_equipment', 'medical_study',
                   'patient_insurance_plan', 'consultation_state']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'patient__insurance_plan__name',
                         'medical_study__name',
                         'medical_equipment__name',
                         'consultation_state__name'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']


    @staticmethod
    def get_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        initiate_study_url = reverse('consultation.technician_consultation_create', args=[rid])
        return """
        <div class="container">
            <div class="row">
                <div class="col">
                    <a href="{}" class="btn btn-sm btn-success shadow-sm"> 
                        Iniciar Estudio
                    </a>
                </div>
                
            </div>
        </div>
        """.format(initiate_study_url)

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')


# ############################### Consultation Sheet UnRealized Datatable View
class ConsultationSheetListUnRealizedTechnicianDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationSheet
    datatable_class = ConsultationSheetUnRealizedTechnicianDatatable
    template_name = 'consultation_sheet/consultation_sheet_list_unrealized_technicians.html'
    permission_required = 'consultation.view_consultationsheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_login_url(self):
        return reverse('dashboard')

    def get_queryset(self):
        filed_state = ConsultationState.objects.get(state_code=ConsultationState.FILED_STATE)
        queryset = ConsultationSheet.objects.filter(
            Q(consultation_state=filed_state) & ~Q(medical_study__sector__sector_code='ECO')
        )
        return queryset

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetListUnRealizedTechnicianDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# ############################### Consultation Sheet UnRealized Datatable for Doctors
class ConsultationSheetUnRealizedDoctorsDatatable(Datatable):
    action = columns.DisplayColumn(_('Select / Action'), processor='get_action')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')

    class Meta:
        model = ConsultationSheet
        columns = ['action', 'id', 'consultation_date', 'patient', 'doctor', 'medical_study',
                   'consultation_state']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'doctor__name', 'doctor__last_name',
                         'medical_study__name',
                         'medical_equipment__name',
                         'consultation_state__name'
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']


    @staticmethod
    def get_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)

        initiate_study_url = reverse('consultation.doctor_consultation_create', args=[rid])
        return """
        <div class="container">
            <div class="row">
                <div class="col">
                    <input type="checkbox" name="consultation_sheets_ids" value="{}">
                    <input type="hidden" name="patients_ids" value="{}"> 
                    &nbsp;
                    <a href="{}" class="btn btn-sm btn-success shadow-sm"> 
                        Iniciar e informar este Estudio
                    </a>
                </div>
                
            </div>
        </div>
        """.format(rid, instance.patient.id, initiate_study_url)

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')


# ############################### Consultation Sheet UnRealized Doctor Datatable View
class ConsultationSheetListUnRealizedDoctorDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationSheet
    datatable_class = ConsultationSheetUnRealizedDoctorsDatatable
    template_name = 'consultation_sheet/consultation_sheet_list_unrealized_doctors.html'
    permission_required = 'consultation.view_consultationsheet'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_login_url(self):
        return reverse('dashboard')

    def get_queryset(self):
        filed_state = ConsultationState.objects.get(state_code=ConsultationState.FILED_STATE)
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Copiadores').exists():
            queryset = ConsultationSheet.objects.filter(
                consultation_state=filed_state, medical_study__sector__sector_code='ECO'
            )
        else:
            try:
                doctor = self.request.user.doctor
            except Exception as e:
                doctor = None
            if doctor:
                queryset = ConsultationSheet.objects.filter(
                    consultation_state=filed_state, medical_study__sector__sector_code='ECO', reporting_doctor=self.request.user.doctor
                )
            else:
                queryset = ConsultationSheet.objects.none()
        return queryset

    def handle_no_permission(self):
        try:
            return super(ConsultationSheetListUnRealizedDoctorDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# Technician Consultation Create View
class TechnicianConsultationCreateView(PermissionRequiredMixin, CreateView):
    model = Consultation
    form_class = TechnicianConsultationCreateForm
    template_name = 'consultation/technician_consultation_form.html'
    permission_required = 'consultation.add_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        consultation_sheet = self.get_consultation_sheet()
        patient = consultation_sheet.patient
        initial = {
            'technician': consultation_sheet.technician,
            'patient': consultation_sheet.patient.id,
            'patient_autocomplete': str(patient),
            'doctor': consultation_sheet.doctor,
            'medical_study': consultation_sheet.medical_study,
            'medical_equipment': consultation_sheet.medical_equipment,
            'treating_doctor': consultation_sheet.treating_doctor,
            'consultation_sheet': consultation_sheet.id,
        }
        return initial

    def get_consultation_sheet(self):
        consultation_sheet = ConsultationSheet.objects.filter(pk=self.kwargs['consultation_sheet_id']).first()
        return consultation_sheet

    def get_context_data(self, **kwargs):
        context = super(TechnicianConsultationCreateView, self).get_context_data(**kwargs)
        consultation_sheet = self.get_consultation_sheet()
        context.update(
            {
                'patient': consultation_sheet.patient,
                'consultation_sheet': consultation_sheet,
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        consultation = form.save()
        consultation_sheet = consultation.consultation_sheet
        print("Consultation created:")
        print(consultation)

        # Performed state
        performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
        consultation_sheet.consultation_state = performed_state
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        messages.success(self.request, 'El Estudio se creó satisfactoriamente')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('consultation_sheet.list_unrealized_technicians')


# Doctor Consultation Create View
class DoctorConsultationCreateView(PermissionRequiredMixin, CreateView):
    model = Consultation
    form_class = DoctorConsultationCreateForm
    template_name = 'consultation/doctor_consultation_form.html'
    permission_required = 'consultation.add_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        consultation_sheet = self.get_consultation_sheet()
        initial = {
            'technician': consultation_sheet.technician,
            'patient': consultation_sheet.patient.id,
            'patient_autocomplete': str(consultation_sheet.patient),
            'doctor': consultation_sheet.doctor,
            'medical_study': consultation_sheet.medical_study,
            'medical_equipment': consultation_sheet.medical_equipment,
            'treating_doctor': consultation_sheet.treating_doctor,
            'consultation_sheet': consultation_sheet.id
        }
        return initial

    def get_consultation_sheet(self):
        consultation_sheet = ConsultationSheet.objects.filter(pk=self.kwargs['consultation_sheet_id']).first()
        return consultation_sheet

    def get_context_data(self, **kwargs):
        context = super(DoctorConsultationCreateView, self).get_context_data(**kwargs)
        consultation_sheet = self.get_consultation_sheet()
        context.update(
            {
                'patient': consultation_sheet.patient,
                'consultation_sheet': consultation_sheet,
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        consultation = form.save()
        consultation_sheet = consultation.consultation_sheet
        print("Consultation created:")
        print(consultation)

        # Performed state
        performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
        consultation_sheet.consultation_state = performed_state
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        # Assigned state
        assigned_state = ConsultationState.objects.get(state_code=ConsultationState.ASSIGNED_STATE)
        consultation_sheet.consultation_state = assigned_state
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        # Create Consultation Report
        consultation_report = ConsultationReport.objects.create(
            patient=consultation.patient,
            doctor=consultation.doctor,
            report_date=consultation.consultation_date,
            report_title=form.cleaned_data['report_title'],
            add_digital_signature=form.cleaned_data['add_digital_signature'],
            report=consultation.notes
        )
        print("consultation Report Created:")
        print(consultation_report)
        consultation.consultation_report = consultation_report
        consultation.save()
        # Reported state
        reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
        consultation_sheet.consultation_state = reported_state
        consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        messages.success(self.request, 'El Estudio se creó satisfactoriamente')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('consultation_sheet.list_unrealized_doctors')


# Doctor Multiple Consultation Create View
class DoctorMultipleConsultationCreateView(PermissionRequiredMixin, FormView):
    form_class = DoctorMultipleConsultationCreateForm
    template_name = 'consultation/doctor_multiple_consultation_form.html'
    permission_required = 'consultation.add_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        consultation_sheet_ids = self.request.GET.getlist('consultation_sheets_ids')
        initial = {}
        if consultation_sheet_ids:
            consultation_sheets = ConsultationSheet.objects.filter(id__in=consultation_sheet_ids)
            consultation_sheet = consultation_sheets.first()
            initial = {
                'consultation_date': timezone.now(),
                'patient': consultation_sheet.patient,
                'doctor': consultation_sheet.doctor,
            }
        return initial

    def get_context_data(self, **kwargs):
        context = super(DoctorMultipleConsultationCreateView, self).get_context_data(**kwargs)
        consultation_sheet_ids = self.request.GET.getlist('consultation_sheets_ids')
        studies = ConsultationSheet.objects.filter(id__in=consultation_sheet_ids)
        patient = studies.first().patient
        context.update(
            {
                'studies': studies,
                'patient': patient
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        consultation_sheets_ids = self.request.POST.getlist('consultation_sheets')
        notes = self.request.POST.getlist('notes')
        consultations = []

        consultation_sheets = ConsultationSheet.objects.filter(id__in=consultation_sheets_ids)
        i = 0
        for consultation_sheet in consultation_sheets:
            if notes[i] == '':
                notes[i] = 'No se Escribió ninguna nota sobre este estudio.'
            consultation = Consultation.objects.create(
                consultation_sheet=consultation_sheet,
                patient=form.cleaned_data['patient'],
                doctor=form.cleaned_data['doctor'],
                treating_doctor=consultation_sheet.treating_doctor,
                consultation_date=form.cleaned_data['consultation_date'],
                medical_study=consultation_sheet.medical_study,
                technician=consultation_sheet.technician,
                medical_equipment=consultation_sheet.medical_equipment,
                notes=notes[i],
                consultation_report=None
            )
            i += 1

            print("Consultation created:")
            print(consultation)
            consultations.append(consultation)

            # Performed state
            performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
            consultation_sheet.consultation_state = performed_state
            consultation_sheet.save()

            consultation_state_user_log = ConsultationStateUserLog.objects.create(
                consultation_sheet=consultation_sheet,
                consultation_state=consultation_sheet.consultation_state,
                user=self.request.user,
            )
            print(consultation_state_user_log)

            # Assigned state
            assigned_state = ConsultationState.objects.get(state_code=ConsultationState.ASSIGNED_STATE)
            consultation_sheet.consultation_state = assigned_state
            consultation_sheet.save()

            consultation_state_user_log = ConsultationStateUserLog.objects.create(
                consultation_sheet=consultation_sheet,
                consultation_state=consultation_sheet.consultation_state,
                user=self.request.user,
            )
            print(consultation_state_user_log)

        # Create Consultation Report
        consultation_report = ConsultationReport.objects.create(
            report_title=form.cleaned_data['report_title'],
            patient=form.cleaned_data['patient'],
            doctor=form.cleaned_data['doctor'],
            report_date=form.cleaned_data['consultation_date'],
            add_digital_signature=form.cleaned_data['add_digital_signature'],
            report=form.cleaned_data['report']
        )
        print("consultation Report Created:")
        print(consultation_report)

        for consultation in consultations:
            consultation.consultation_report = consultation_report
            consultation.save()
            consultation_sheet = consultation.consultation_sheet

            # Reported state
            reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
            consultation_sheet.consultation_state = reported_state
            consultation_sheet.save()

            consultation_state_user_log = ConsultationStateUserLog.objects.create(
                consultation_sheet=consultation_sheet,
                consultation_state=consultation_sheet.consultation_state,
                user=self.request.user,
            )
            print(consultation_state_user_log)

        messages.success(self.request, 'Los Estudios y reporte se crearon satisfactoriamente')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('consultation_sheet.list_unrealized_doctors')


# ############################### Technician Consultation Sheet List Datatable
class TechnicianConsultationListDatatable(Datatable):
    action = columns.DisplayColumn(_('Action'), processor='get_action')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')

    class Meta:
        model = Consultation
        columns = ['action', 'id', 'consultation_date', 'patient', 'medical_equipment', 'medical_study',
                   'technician'
                   ]
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'technician__name', 'technician__last_name',
                         'medical_study__name',
                         'medical_equipment__name',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        update_study_url = reverse('consultation.technician_consultation_update', args=[rid])
        detail_url = reverse('consultation.detail', args=[rid])
        return """
        <div class="container">
            <div class="row">
                <div class="col ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                        <i class="fas fa-eye"></i>
                    </a>
                </div>
                <div class="col ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                         <i class="fas fa-pencil-alt"></i>
                    </a>
                </div>
                
            </div>
        </div>
        """.format(detail_url, update_study_url)

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')


# ############################### Technician Consultation Sheet List Datatable View
class TechniciansConsultationListDataTableView(PermissionRequiredMixin, DatatableView):
    model = Consultation
    datatable_class = TechnicianConsultationListDatatable
    template_name = 'consultation/technicians_consultations_list.html'
    permission_required = 'consultation.view_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Consultation.objects.all()
        else:
            queryset = Consultation.objects.filter(
                ~Q(technician=None)
            )

        return queryset

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(TechniciansConsultationListDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# Technician Consultation Update View
class TechnicianConsultationUpdateView(PermissionRequiredMixin, UpdateView):
    model = Consultation
    form_class = TechnicianConsultationUpdateForm
    template_name = 'consultation/technician_consultation_form.html'
    context_object_name = 'consultation'
    permission_required = 'consultation.change_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        consultation_sheet = self.object.consultation_sheet
        patient = consultation_sheet.patient
        initial = {
            'technician': consultation_sheet.technician,
            'patient': consultation_sheet.patient.id,
            'patient_autocomplete': str(patient),
            'doctor': consultation_sheet.doctor,
            'medical_study': consultation_sheet.medical_study,
            'medical_equipment': consultation_sheet.medical_equipment,
            'treating_doctor': consultation_sheet.treating_doctor,
            'consultation_sheet': consultation_sheet.id,
        }
        return initial

    def get_consultation_sheet(self):
        consultation_sheet = self.object.consultation_sheet
        return consultation_sheet

    def get_context_data(self, **kwargs):
        context = super(TechnicianConsultationUpdateView, self).get_context_data(**kwargs)
        consultation_sheet = self.get_consultation_sheet()
        context.update(
            {
                'patient': consultation_sheet.patient,
                'consultation_sheet': consultation_sheet,
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        consultation = form.save()
        print("Consultation updated:")
        print(consultation)

        messages.success(self.request, 'El Estudio se actualizó satisfactoriamente')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('consultation.list_technicians')

    def handle_no_permission(self):
        try:
            return super(TechnicianConsultationUpdateView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect('consultation.list_technicians')


# Consultation Deatil View
class ConsultationDetailView(PermissionRequiredMixin, DetailView):
    model = Consultation
    template_name = 'consultation/consultation_detail.html'
    context_object_name = 'consultation'
    permission_required = 'consultation.view_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_consultation_sheet(self):
        consultation_sheet = self.object.consultation_sheet
        return consultation_sheet

    def get_context_data(self, **kwargs):
        context = super(ConsultationDetailView, self).get_context_data(**kwargs)
        consultation_sheet = self.get_consultation_sheet()
        context.update(
            {
                'patient': consultation_sheet.patient,
                'consultation_sheet': consultation_sheet,
            }
        )
        return context

    def handle_no_permission(self):
        try:
            return super(ConsultationDetailView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect('consultation.list_technicians')


# ############################### Doctor Consultation Sheet List Datatable
class DoctorsConsultationListDatatable(Datatable):
    action = columns.DisplayColumn(_('Action'), processor='get_action')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')

    class Meta:
        model = Consultation
        columns = ['action', 'id', 'consultation_date', 'patient', 'medical_study', 'medical_equipment',
                   'technician', 'doctor'
                   ]
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'doctor__name', 'doctor__last_name',
                         'technician__name', 'technician__last_name',
                         'medical_study__name',
                         'medical_equipment__name',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']


    @staticmethod
    def get_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        update_study_url = reverse('consultation.doctor_consultation_update', args=[rid])
        detail_url = reverse('consultation.detail', args=[rid])
        return """
        <div class="container">
            <div class="row">
                <div class="col ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                        <i class="fas fa-eye"></i>
                    </a>
                </div>
                <div class="col ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                         <i class="fas fa-pencil-alt"></i>
                    </a>
                </div>
                
            </div>
        </div>
        """.format(detail_url, update_study_url)


    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')


# ############################### Doctor Consultation List Datatable View
class DoctorsConsultationListDataTableView(PermissionRequiredMixin, DatatableView):
    model = Consultation
    datatable_class = DoctorsConsultationListDatatable
    template_name = 'consultation/doctors_consultations_list.html'
    permission_required = 'consultation.view_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Copiadores').exists():
            queryset = Consultation.objects.all()
        else:
            try:
                doctor = self.request.user.doctor
            except Exception as e:
                doctor = None
            if doctor:
                queryset = Consultation.objects.filter(
                    doctor=self.request.user.doctor
                )
            else:
                queryset = Consultation.objects.none()
        return queryset

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(DoctorsConsultationListDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# Doctor Consultation Update View
class DoctorConsultationUpdateView(PermissionRequiredMixin, UpdateView):
    model = Consultation
    form_class = DoctorConsultationUpdateForm
    template_name = 'consultation/doctor_consultation_form.html'
    context_object_name = 'consultation'
    permission_required = 'consultation.change_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        consultation_sheet = self.get_consultation_sheet()
        initial = {
            'technician': consultation_sheet.technician,
            'patient': consultation_sheet.patient.id,
            'patient_autocomplete': str(consultation_sheet.patient),
            'doctor': consultation_sheet.doctor,
            'medical_study': consultation_sheet.medical_study,
            'medical_equipment': consultation_sheet.medical_equipment,
            'treating_doctor': consultation_sheet.treating_doctor,
            'consultation_sheet': consultation_sheet.id
        }
        return initial

    def get_consultation_sheet(self):
        consultation_sheet = self.object.consultation_sheet
        return consultation_sheet

    def get_context_data(self, **kwargs):
        context = super(DoctorConsultationUpdateView, self).get_context_data(**kwargs)
        consultation_sheet = self.get_consultation_sheet()
        context.update(
            {
                'patient': consultation_sheet.patient,
                'consultation_sheet': consultation_sheet,
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        consultation = form.save()
        print("Consultation updated:")
        print(consultation)

        messages.success(self.request, 'El Estudio se actualizó satisfactoriamente')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('consultation.list_doctors')

    def handle_no_permission(self):
        try:
            return super(DoctorConsultationUpdateView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect('consultation.list_doctors')


# ############################### Doctor Consultation Sheet List Datatable
class DoctorsConsultationsToInformListDatatable(Datatable):
    action = columns.DisplayColumn(_('Action'), processor='get_action')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')

    class Meta:
        model = Consultation
        columns = ['action', 'id', 'consultation_date', 'patient', 'medical_study', 'medical_equipment',
                   'technician', 'doctor'
                   ]
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'doctor__name', 'doctor__last_name',
                         'technician__name', 'technician__last_name',
                         'medical_study__name',
                         'medical_equipment__name',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']


    @staticmethod
    def get_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        create_report_url = reverse('consultation_report.create', args=[rid])
        return """
        <div class="container">
            <div class="row">
                <div class="col">
                    <input type="checkbox" name="consultation_ids" value="{}">
                    <input type="hidden" name="patients_ids" value="{}"> 
                    &nbsp;
                    <a href="{}" class="btn btn-sm btn-success shadow-sm"> 
                        Informar Este Estudio
                    </a>
                </div>
                
            </div>
        </div>
        """.format(rid, instance.patient, create_report_url)

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')


# ############################### Doctors Consultation Sheet List Datatable View
class DoctorsConsultationsToInformListDataTableView(PermissionRequiredMixin, DatatableView):
    model = Consultation
    datatable_class = DoctorsConsultationsToInformListDatatable
    template_name = 'consultation/doctors_consultations_to_inform_list.html'
    permission_required = 'consultation.view_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_queryset(self):
        assigned_state = ConsultationState.objects.get(state_code=ConsultationState.ASSIGNED_STATE)
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Copiadores').exists():
            queryset = Consultation.objects.filter(
                consultation_sheet__consultation_state=assigned_state
            )
        else:
            try:
                doctor = self.request.user.doctor
            except Exception as e:
                doctor = None
            if doctor:
                queryset = Consultation.objects.filter(
                    consultation_sheet__consultation_state=assigned_state,
                    consultation_sheet__reporting_doctor=self.request.user.doctor
                )
            else:
                queryset = Consultation.objects.none()
        return queryset

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(DoctorsConsultationsToInformListDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# Doctor Consultation Report Create View
class DoctorConsultationReportCreateView(PermissionRequiredMixin, CreateView):
    model = ConsultationReport
    form_class = DoctorConsultationReportCreateForm
    template_name = 'consultation_report/consultation_report_form.html'
    permission_required = 'consultation.add_consultationreport'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        consultation = self.get_consultation()
        if consultation.doctor:
            doctor = consultation.doctor
        else:
            doctor = consultation.consultation_sheet.reporting_doctor
        initial = {
            'report_date': consultation.consultation_date,
            'patient': consultation.patient.id,
            'patient_autocomplete': str(consultation.patient),
            'doctor': doctor,
        }
        return initial

    def get_consultation(self):
        consultation = Consultation.objects.filter(pk=self.kwargs['consultation_id']).first()
        return consultation

    def get_context_data(self, **kwargs):
        context = super(DoctorConsultationReportCreateView, self).get_context_data(**kwargs)
        consultation = self.get_consultation()
        studies = [consultation]
        context.update(
            {
                'consultation': consultation,
                'patient': consultation.patient,
                'studies': studies
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        consultation_report = form.save()
        audio_file = self.request.FILES.get('sound_file')
        consultation_report.audio_report = audio_file
        consultation_report.save()
        consultation_id = self.request.POST['consultations']
        consultation = Consultation.objects.get(pk=consultation_id)
        consultation_sheet = consultation.consultation_sheet
        consultation.consultation_report = consultation_report
        consultation.save()

        print("Consultation Report created:")
        print(consultation_report)

        if consultation_report.report != '':
            # Reported state
            reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
            consultation_sheet.consultation_state = reported_state
            consultation_sheet.save()
        else:
            # Recorded state
            recorded_state = ConsultationState.objects.get(state_code=ConsultationState.RECORDED_STATE)
            consultation_sheet.consultation_state = recorded_state
            consultation_sheet.save()

        consultation_state_user_log = ConsultationStateUserLog.objects.create(
            consultation_sheet=consultation_sheet,
            consultation_state=consultation_sheet.consultation_state,
            user=self.request.user,
        )
        print(consultation_state_user_log)

        return JsonResponse({
            'success': True,
            'success_url': self.get_success_url(),
            'message': 'El Reporte de Estudio se creó satisfactoriamente'
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'message': 'Datos de formulario inválidos! '
                       'Por Favor vuelva a revisar todos los datos. '
                       'Si los datos son correctos, y el problema persiste, '
                       'póngase en contacto con un administrador del sistema.'
        })

    def get_success_url(self):
        return reverse('consultation.doctors_list_to_inform')


# ############################### Consultation Reports List Datatable
class ConsultationReportsListDatatable(Datatable):
    action = columns.DisplayColumn(_('Action'), processor='get_action')
    report_date = columns.DisplayColumn(_('Date Time'), processor='get_report_date')
    studies = columns.DisplayColumn(_('Studies'), processor='get_studies')

    class Meta:
        model = ConsultationReport
        columns = ['action', 'id', 'report_date', 'report_title', 'patient', 'doctor', 'studies'
                   ]
        search_fields = ['id', 'report_title',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'doctor__name', 'doctor__last_name',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        update_study_url = reverse('consultation_report.update', args=[rid])
        create_pdf_url = reverse('consultation_report.create_pdf_view', args=[rid])
        detail_url = reverse('consultation_report.detail', args=[rid])
        return """
        <div class="container">
            <div class="row">
                <div class="col ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                        <i class="fas fa-eye"></i>
                    </a>
                </div>
                <div class="col ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                         <i class="fas fa-pencil-alt"></i>
                    </a>
                </div>
                <div class="col">
                    <a href="{}" class="btn btn-info btn-circle"> 
                        <i class="fas fa-file-download"></i>
                    </a>
                </div>
                
                
            </div>
        </div>
        """.format(detail_url, update_study_url, create_pdf_url)

    @staticmethod
    def get_report_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.report_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')

    @staticmethod
    def get_studies(instance, view, *args, **kwargs):
        rid = int(instance.pk)

        str_to_return = """
        <ol>
        """
        for study in instance.consults.all():
            str_to_add = """<li>""" + study.medical_study.name + """</li>"""
            str_to_return += str_to_add

        str_to_return += """
        </ol>
        """
        return str_to_return


# ############################### Consultation Report List Datatable View
class ConsultationsReportListDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationReport
    datatable_class = ConsultationReportsListDatatable
    template_name = 'consultation_report/doctors_consultations_reports_list.html'
    permission_required = 'consultation.view_consultationreport'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_queryset(self):
        reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Copiadores').exists():
            queryset = ConsultationReport.objects.filter(consults__consultation_sheet__consultation_state=reported_state)
        else:
            try:
                doctor = self.request.user.doctor
            except Exception as e:
                doctor = None
            if doctor:
                queryset = ConsultationReport.objects.filter(
                    doctor=self.request.user.doctor,
                    consults__consultation_sheet__consultation_state=reported_state
                )
            else:
                queryset = ConsultationReport.objects.none()
        return queryset

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(ConsultationsReportListDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# ############################### Consultation Report Finished List Datatable View
class ConsultationsReportFinishedListDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationReport
    datatable_class = ConsultationReportsListDatatable
    template_name = 'consultation_report/doctors_consultations_reports_list_finished.html'
    permission_required = 'consultation.view_consultationreport'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_queryset(self):
        finished_state = ConsultationState.objects.get(state_code=ConsultationState.FINISHED_STATE)
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Copiadores').exists():
            queryset = ConsultationReport.objects.filter(consults__consultation_sheet__consultation_state=finished_state)
        else:
            try:
                doctor = self.request.user.doctor
            except Exception as e:
                doctor = None
            if doctor:
                queryset = ConsultationReport.objects.filter(
                    doctor=self.request.user.doctor,
                    consults__consultation_sheet__consultation_state=finished_state,
                )
            else:
                queryset = ConsultationReport.objects.none()
        return queryset

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(ConsultationsReportListDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# ############################### Consultation Report recorded List to be copied Datatable View
class ConsultationsReportRecordedListDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationReport
    datatable_class = ConsultationReportsListDatatable
    template_name = 'consultation_report/doctors_consultations_reports_list.html'
    permission_required = 'consultation.view_consultationreport'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_queryset(self):
        recorded_state = ConsultationState.objects.get(state_code=ConsultationState.RECORDED_STATE)
        if self.request.user.is_superuser or self.request.user.groups.filter(name='Copiadores').exists():
            queryset = ConsultationReport.objects.filter(consults__consultation_sheet__consultation_state=recorded_state)
        else:
            try:
                doctor = self.request.user.doctor
            except Exception as e:
                doctor = None
            if doctor:
                queryset = ConsultationReport.objects.filter(
                    doctor=self.request.user.doctor,
                    consults__consultation_sheet__consultation_state=recorded_state
                )
            else:
                queryset = ConsultationReport.objects.none()
        return queryset

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(ConsultationsReportRecordedListDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())



# ############################### Consultation Reports List By Patient Datatable
class ConsultationReportsListByPatientDatatable(Datatable):
    action = columns.DisplayColumn(_('Action'), processor='get_action')
    report_date = columns.DisplayColumn(_('Date Time'), processor='get_report_date')
    studies = columns.DisplayColumn(_('Studies'), processor='get_studies')

    class Meta:
        model = ConsultationReport
        columns = ['action', 'id', 'report_date', 'report_title', 'patient', 'doctor', 'studies'
                   ]
        search_fields = ['id', 'report_title',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'doctor__name', 'doctor__last_name',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_action(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        update_study_url = reverse('consultation_report.update', args=[rid])
        detail_url = reverse('consultation_report.detail', args=[rid])
        create_pdf_url = reverse('consultation_report.create_pdf_view', args=[rid])
        return """
        <div class="container">
            <div class="row">
                <div class="col ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                        <i class="fas fa-eye"></i>
                    </a>
                </div>
                <div class="col ">
                    <a href="{}" class="btn btn-info btn-circle"> 
                         <i class="fas fa-pencil-alt"></i>
                    </a>
                </div>
                <div class="col">
                    <a href="{}" class="btn btn-info btn-circle"> 
                        <i class="fas fa-file-download"></i>
                    </a>
                </div>
                
                
            </div>
        </div>
        """.format(detail_url, update_study_url, create_pdf_url)

    @staticmethod
    def get_report_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.report_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M')

    @staticmethod
    def get_studies(instance, view, *args, **kwargs):
        rid = int(instance.pk)

        str_to_return = """
        <ol>
        """
        for study in instance.consults.all():
            str_to_add = """<li>""" + study.medical_study.name + """</li>"""
            str_to_return += str_to_add

        str_to_return += """
        </ol>
        """
        return str_to_return


# ############################### Consultation Report List Datatable View
class ConsultationsReportListByPatientDataTableView(PermissionRequiredMixin, DatatableView):
    model = ConsultationReport
    datatable_class = ConsultationReportsListByPatientDatatable
    template_name = 'consultation_report/doctors_consultations_reports_list.html'
    permission_required = 'consultation.view_consultationreport'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_patient(self, *args, **kwargs):
        patient_id = self.kwargs['patient_id']
        patient = Patient.objects.get(pk=patient_id)
        return patient

    def get_queryset(self):
        patient = self.get_patient()
        queryset = ConsultationReport.objects.filter(patient=patient)
        return queryset

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(ConsultationsReportListByPatientDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# ########################## Consultation Report Update View
class ConsultationReportUpdateView(PermissionRequiredMixin, UpdateView):
    model = ConsultationReport
    form_class = ConsultationReportUpdateForm
    template_name = 'consultation_report/consultation_report_form.html'
    context_object_name = 'consultation_report'
    permission_required = 'consultation.change_consultationreport'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        patient = self.object.patient
        initial = {
            'patient': patient.id,
            'patient_autocomplete': str(patient)
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super(ConsultationReportUpdateView, self).get_context_data(**kwargs)
        report_consultations = Consultation.objects.filter(
            consultation_report=self.object
        )
        context.update(
            {
                'patient': self.object.patient,
                'studies': report_consultations
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        consultation_report = form.save()
        print("Consultation Report updated:")
        print(consultation_report)

        for consultation in consultation_report.consults.all():
            consultation_sheet = consultation.consultation_sheet
            if consultation_sheet.consultation_state.state_code == ConsultationState.RECORDED_STATE and consultation_report.report != '':
                # Reported state
                reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
                consultation_sheet.consultation_state = reported_state
                consultation_sheet.save()

                consultation_state_user_log = ConsultationStateUserLog.objects.create(
                    consultation_sheet=consultation_sheet,
                    consultation_state=consultation_sheet.consultation_state,
                    user=self.request.user,
                )
                print(consultation_state_user_log)

        if consultation_report.finished:
            for consultation in consultation_report.consults.all():
                consultation_sheet = consultation.consultation_sheet
                if consultation_sheet.consultation_state.state_code == ConsultationState.REPORTED_STATE and consultation_report.report != '':
                    # Reported state
                    finished_state = ConsultationState.objects.get(state_code=ConsultationState.FINISHED_STATE)
                    consultation_sheet.consultation_state = finished_state
                    consultation_sheet.save()

                    consultation_state_user_log = ConsultationStateUserLog.objects.create(
                        consultation_sheet=consultation_sheet,
                        consultation_state=consultation_sheet.consultation_state,
                        user=self.request.user,
                    )
                    print(consultation_state_user_log)


        messages.success(self.request, 'El Informe de Estudio se actualizó satisfactoriamente')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('consultation_report.list')

    def handle_no_permission(self):
        try:
            return super(ConsultationReportUpdateView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect('consultation_report.list')


# ########################## Consultation Report Detail View
class ConsultationReportDetailView(PermissionRequiredMixin, DetailView):
    model = ConsultationReport
    template_name = 'consultation_report/consultation_report_detail.html'
    context_object_name = 'consultation_report'
    permission_required = 'consultation.change_consultationreport'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_context_data(self, **kwargs):
        context = super(ConsultationReportDetailView, self).get_context_data(**kwargs)
        report_consultations = Consultation.objects.filter(
            consultation_report=self.object
        )
        context.update(
            {
                'patient': self.object.patient,
                'studies': report_consultations
            }
        )
        return context

    def handle_no_permission(self):
        try:
            return super(ConsultationReportDetailView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect('consultation_report.list')


# Consultation Report Doctor Multiple Consultation Create View
class DoctorMultipleConsultationCreateReportView(PermissionRequiredMixin, FormView):
    form_class = DoctorMultipleConsultationCreateForm
    template_name = 'consultation_report/doctor_multiple_consultation_report_form.html'
    permission_required = 'consultation.add_consultationreport'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        consultation_ids = self.request.GET.getlist('consultation_ids')
        initial = {}
        if consultation_ids:
            consultations = Consultation.objects.filter(id__in=consultation_ids)
            consultation = consultations.first()
            initial = {
                'consultation_date': consultation.consultation_date,
                'patient': consultation.patient,
                'doctor': consultation.doctor,
            }
        return initial

    def get_context_data(self, **kwargs):
        context = super(DoctorMultipleConsultationCreateReportView, self).get_context_data(**kwargs)
        consultation_ids = self.request.GET.getlist('consultation_ids')
        studies = Consultation.objects.filter(id__in=consultation_ids)
        patient = studies.first().patient
        context.update(
            {
                'studies': studies,
                'patient': patient
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        consultation_ids = self.request.POST.getlist('consultations')
        consultations = Consultation.objects.filter(id__in=consultation_ids)

        # Create Consultation Report
        consultation_report = ConsultationReport.objects.create(
            patient=form.cleaned_data['patient'],
            doctor=form.cleaned_data['doctor'],
            report_date=form.cleaned_data['consultation_date'],
            report_title=form.cleaned_data['report_title'],
            report=form.cleaned_data['report']
        )
        print("consultation Report Created:")
        print(consultation_report)

        for consultation in consultations:
            consultation.consultation_report = consultation_report
            consultation.save()
            consultation_sheet = consultation.consultation_sheet

            # Reported state
            reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
            consultation_sheet.consultation_state = reported_state
            consultation_sheet.save()

            consultation_state_user_log = ConsultationStateUserLog.objects.create(
                consultation_sheet=consultation_sheet,
                consultation_state=consultation_sheet.consultation_state,
                user=self.request.user,
            )
            print(consultation_state_user_log)

        messages.success(self.request, 'El reporte de multiples estudios se creó satisfactoriamente')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('consultation_sheet.list_unrealized_doctors')


# Doctor Report Template Detail View (JSON)
class DoctorReportTemplateDetailJsonView(LoginRequiredMixin, DetailView):
    model = DoctorReportTemplate

    def get(self, request, *args, **kwargs):
        template_id = kwargs['pk']
        template = DoctorReportTemplate.objects.get(pk=template_id)
        data = {
            'id': template.id,
            'doctor': str(template.doctor),
            'medical_study': str(template.medical_study),
            'template_text': str(template.template_text),
        }
        return JsonResponse(data, status=200, safe=False)


class ConsultationReportCreatePdfView(LoginRequiredMixin, View):
    """permite descargar el informe del estudio"""

    @staticmethod
    def get(request, *args, **kwargs):
        consultation_report = get_object_or_404(ConsultationReport, pk=kwargs['pk'])
        if hasattr(settings, 'LOGO_URL'):
            logo_url = settings.LOGO_URL
        else:
            logo_url = ''
        if hasattr(settings, 'STATIC_ROOT'):
            static_url = settings.STATIC_ROOT
        else:
            static_url = ''

        template = loader.get_template('pdf/consultation_report_pdf.html')
        context = {
            'consultation_report': consultation_report,
            'url': static_url,
            'logo': logo_url,
            'request': request
        }
        pdf = render_to_pdf(
            'pdf/consultation_report_pdf.html',
            context
        )
        # return HttpResponse(template.render(context, request))
        return make_response(pdf, 'informe_' + consultation_report.report_title.replace(' ', '_') + '.pdf', content_type='application/pdf')


class ConsultationSheetUpdateDocumentsView(LoginRequiredMixin, TemplateView):
    template_name = "consultation_sheet_documents/consultation_sheet_documents_update_form.html"

    def get_consultation_sheet(self):
        consultation_sheet_id = self.kwargs['pk']
        consultation_sheet = ConsultationSheet.objects.get(pk=consultation_sheet_id)
        return consultation_sheet

    def get_context_data(self, **kwargs):
        consultation_sheet = self.get_consultation_sheet()
        context = {
            'consultation_sheet': consultation_sheet
        }
        if self.request.POST:
            context['documents_formset'] = ConsultationSheetDocumentFormSet(self.request.POST, self.request.FILES, instance=consultation_sheet)

        else:
            context['documents_formset'] = ConsultationSheetDocumentFormSet(instance=consultation_sheet)

        return context

    def get_consultation_entry_sheet(self):
        consultation_entry_sheet = ConsultationEntrySheet.objects.filter(pk=self.kwargs.get('consultation_entry_sheet_id')).first()
        return consultation_entry_sheet

    def get_success_url(self):
        return reverse('consultation_entry_sheet.update', kwargs={'pk': self.get_consultation_sheet().consultation_entry_sheet.id})

    def post(self, request, pk):
        context = self.get_context_data()
        documents_formset = context['documents_formset']
        consultation_sheet = self.get_consultation_sheet()
        if documents_formset.is_valid():

            documents_formset.instance = consultation_sheet
            documents_formset.save()

            messages.success(self.request, 'La Ficha de Estudio fue actualizada satisfactoriamente')
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(self.request, 'Datos de formulario inválidos! '
                                         'Por Favor vuelva a revisar todos los datos. '
                                         'Si los datos son correctos, y el problema persiste, '
                                         'póngase en contacto con un administrador del sistema.')
            return self.render_to_response(self.get_context_data())


class ConsultationDatatable(Datatable):
    actions = columns.DisplayColumn(_('Actions'), processor='get_actions')
    consultation_date = columns.DisplayColumn(_('Date Time'), processor='get_consultation_date')
    patient_insurance_plan = columns.DisplayColumn(_('Insurance'), processor='get_patient_insurance_plan')

    class Meta:
        model = Consultation
        columns = ['actions', 'id', 'consultation_date', 'patient', 'patient_insurance_plan', 'medical_study',
                   'doctor', 'medical_equipment', 'treating_doctor']
        search_fields = ['id',
                         'patient__name', 'patient__last_name', 'patient__document_number',
                         'patient__insurance_plan__name',
                         'medical_study__name',
                         'medical_equipment__name',
                         'doctor__name', 'doctor__last_name',
                         'treating_doctor__name', 'treating_doctor__last_name',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_actions(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        assign_file_url = reverse('consultation.assign_files', args=[rid])

        return """
        <div class="container">
            <div class="row">
                <div class="col " style="width: 80px; ">
                    <a href="{}" class="btn btn-sm btn-success shadow-sm"> 
                    Asignar Archivo
                    </a>
                </div> 
            </div>
        </div>
        """.format(assign_file_url)

    @staticmethod
    def get_consultation_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        date_to_return = utc_to_local(instance.consultation_date)
        return datetime.datetime.strftime(date_to_return, '%d/%m/%Y %H:%M:%S')

    @staticmethod
    def get_patient_insurance_plan(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        insurance_plan = instance.patient.insurance_plan
        if insurance_plan:
            insurance_plan = insurance_plan.name
        return insurance_plan


class ConsultationListWithoutFilesDataTableView(PermissionRequiredMixin, DatatableView):
    model = Consultation
    datatable_class = ConsultationDatatable
    template_name = 'consultation/consultation_list_without_file_datatable.html'
    permission_required = 'consultation.view_consultationsheet'
    permission_denied_message = 'No tienes los permisos requeridos'

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(ConsultationListWithoutFilesDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())

    def get_queryset(self):
        performed_state = ConsultationState.objects.get(state_code=ConsultationState.PERFORMED_STATE)
        queryset = Consultation.objects.filter(consultation_sheet__consultation_state=performed_state)
        return queryset


# Consultation Assign Files View
class ConsultationAssignFilesView(PermissionRequiredMixin, FormView):
    form_class = ConsultationAssignFilesForm
    template_name = 'consultation/consultation_assign_file_form.html'
    permission_required = 'consultation.change_consultation'
    permission_denied_message = _("Your User or User Group, don't have the necessary permissions to access this view")

    def get_initial(self):
        consultation_id = self.kwargs['consultation_id']
        consultation = Consultation.objects.get(pk=consultation_id)
        consultation_files = ConsultationFile.objects.filter(consultation=consultation)

        initial = {
            'consultation': consultation.id,
            'consultation_files': consultation_files
        }
        return initial

    def get_context_data(self, **kwargs):
        context = super(ConsultationAssignFilesView, self).get_context_data(**kwargs)
        consultation_id = self.kwargs['consultation_id']
        consultation = Consultation.objects.get(pk=consultation_id)

        if self.request.POST:
            consultation_files_formset = ConsultationFileFormSet(self.request.POST, self.request.FILES)
        else:
            consultation_files_formset = ConsultationFileFormSet(instance=consultation)

        context.update(
            {
                'consultation': consultation,
                'consultation_files_formset': consultation_files_formset
            }
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        consultation_id = self.kwargs['consultation_id']
        consultation = Consultation.objects.get(pk=consultation_id)
        consultation_files_formset = context['consultation_files_formset']
        doctor = form.cleaned_data['doctor']

        if consultation_files_formset.is_valid():
            consultation_files_formset.instance = consultation
            consultation_files_formset.save()

            assigned_state = ConsultationState.objects.get(state_code=ConsultationState.ASSIGNED_STATE)
            consultation.consultation_sheet.consultation_state = assigned_state
            consultation.doctor = doctor
            consultation.consultation_sheet.doctor = doctor
            consultation.consultation_sheet.save()
            consultation.save()

            messages.success(self.request, 'Los archivos fueron agregados a los estudios satisfactoriamente')
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(self.request, 'Datos de formulario inválidos! '
                                         'Por Favor vuelva a revisar todos los datos. '
                                         'Si los datos son correctos, y el problema persiste, '
                                         'póngase en contacto con un administrador del sistema.')
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, 'Datos de formulario inválidos! '
                                     'Por Favor vuelva a revisar todos los datos. '
                                     'Si los datos son correctos, y el problema persiste, '
                                     'póngase en contacto con un administrador del sistema.')
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse('consultation.list_without_files')


# Consultation Sheet Document Print View
class ConsultationSheetDocumentPrintView(LoginRequiredMixin, TemplateView):
    template_name = "consultation_sheet/consultation_sheet_document_print.html"

    def get_context_data(self, **kwargs):
        context = super(ConsultationSheetDocumentPrintView, self).get_context_data(**kwargs)
        consultation_sheet_document = ConsultationSheetDocument.objects.get(pk=kwargs['pk'])
        context.update(
            {
                'consultation_sheet_document': consultation_sheet_document,
            }
        )
        return context