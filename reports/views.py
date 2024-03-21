import io
import datetime

from django.db.models.query_utils import Q
from django.http.response import HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from easy_pdf.rendering import render_to_pdf, make_response
from xlsxwriter import Workbook
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView
from django.utils.translation import gettext as _
from clinic.models import Sector
from consultation.models import ConsultationSheet, ConsultationState
from invoicing.models import PaymentMethod, InvoiceHeader
from reports.forms import ReportingDoctorsReportFiltersForm, CashReportFiltersForm, TreatingDoctorsReportFiltersForm, \
    InsurancesAgreementsReportFiltersForm, ConsultationSheetsTotalReportFiltersForm, InvoiceReportFiltersForm
from sales.models import ConsultationSheetSalePayment

import json
import uuid

from django.db.models import Sum, Q
from django.http import HttpResponseBadRequest, Http404
from django.utils.safestring import SafeString
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from reportbro import Report, ReportBroError
from timeit import default_timer as timer

from .models import ReportDefinition, ReportRequest
from .utils import json_default, get_menu_items, create_album_report_template

MAX_CACHE_SIZE = 1000 * 1024 * 1024  # keep max. 1000 MB of generated pdf files in db


# REPORTS
# Cash Report List View
class CashReportListView(LoginRequiredMixin, ListView):
    template_name = 'cash_report/cash_report_list.html'
    context_object_name = "payments"
    model = ConsultationSheetSalePayment

    def get_queryset(self):
        queryset = []
        form = CashReportFiltersForm(self.request.GET)
        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            if form.is_valid():
                start = form.cleaned_data.get('date_time_start')
                end = form.cleaned_data.get('date_time_end')
                queryset = ConsultationSheetSalePayment.objects.filter(
                    amount__gt=0,
                    payment_datetime__range=[start, end],
                )
                payment_method = form.cleaned_data.get('payment_method', None)
                study_type = form.cleaned_data.get('study_type', None)

                if payment_method:
                    queryset = queryset.filter(payment_method=payment_method)

                if study_type:
                    queryset = queryset.filter(consultation_sheet__medical_study__type=study_type)

        else:
            if self.request.GET.get('payment_method') or self.request.GET.get('study_type'):
                if form.is_valid():
                    queryset = ConsultationSheet.objects.all()
                    payment_method = form.cleaned_data.get('payment_method', None)

                    if payment_method:
                        queryset = queryset.filter(consultation_sheet__payment_method=payment_method)

                    study_type = form.cleaned_data.get('study_type', None)

                    if study_type:
                        queryset = queryset.filter(consultation_sheet__medical_study__type=study_type)

        return queryset

    def get(self, request, *args, **kwargs):
        form = CashReportFiltersForm(self.request.GET)
        if form.is_valid():
            filters = []
            start = form.cleaned_data.get('date_time_start')
            end = form.cleaned_data.get('date_time_end')
            payment_method = form.cleaned_data.get('payment_method', None)
            study_type = form.cleaned_data.get('study_type', None)

            if payment_method:
                report_filter = {
                    'name': _('Payment Method'),
                    'value': str(payment_method)
                }
                filters.append(report_filter)

            if study_type:
                report_filter = {
                    'name': _('Study Type'),
                    'value': str(study_type)
                }
                filters.append(report_filter)

            report_filter = {
                'name': _('User'),
                'value': self.request.user.username
            }
            filters.append(report_filter)

            elements = self.get_queryset()
            report_type = form.cleaned_data.get('report_type')

            if elements and report_type == str(CashReportFiltersForm.EXCEL_TYPE):
                return self.export_excel(elements)

            elif elements and report_type == str(CashReportFiltersForm.PDF_TYPE):
                return self.export_pdf(elements, start, end, filters)

            else:
                return super().get(self, request, *args, **kwargs)

        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}

        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            initial['date_time_start'] = self.request.GET.get('date_time_start')
            initial['date_time_end'] = self.request.GET.get('date_time_end')
        else:
            now = datetime.datetime.now()
            inicio = datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=1,
                minute=0,
                second=0
            )
            fin = datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=22,
                minute=59,
                second=59
            )

            inicio = timezone.make_aware(inicio)
            fin = timezone.make_aware(fin)

            initial['date_time_start'] = inicio
            initial['date_time_end'] = fin

        if self.request.GET.get('payment_method'):
            initial['payment_method'] = self.request.GET.get('payment_method')

        if self.request.GET.get('study_type'):
            initial['study_type'] = self.request.GET.get('study_type')

        if self.request.GET.get('report_type'):
            initial['report_type'] = self.request.GET.get('report_type')

        filter_form = CashReportFiltersForm(initial=initial)
        context.update({
            'filter_form': filter_form
        })
        return context

    def export_excel(self, elements):
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # r = Row and c = Column
        r = 0
        c = 1

        # Table header
        table_headers = [
            # 'ID Ficha de Estudio',
            'Fecha Hora',
            'Paciente',
            'Seguro',
            'Servicio',
            'Método de Pago',
            'Arancel de Estudio',
            'Total de Insumos',
            'Descuento',
            'Total a Pagar Paciente',
            'Monto Pagado'
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            # worksheet.write(r, 0, element.id)
            payment_date = timezone.localtime(element.payment_datetime)
            payment_date = payment_date.strftime("%d/%m/%Y %H:%M")

            worksheet.write(r, 1, payment_date)
            worksheet.write(r, 2, str(element.consultation_sheet.patient))
            worksheet.write(r, 3, str(element.consultation_sheet.patient_insurance_plan))
            worksheet.write(r, 4, str(element.consultation_sheet.medical_study))
            worksheet.write(r, 5, str(element.consultation_sheet.payment_method))
            worksheet.write(r, 6, element.consultation_sheet.medical_study_ammount)
            worksheet.write(r, 7, element.consultation_sheet.medical_supplies_ammount)
            worksheet.write(r, 8, element.consultation_sheet.discount)
            worksheet.write(r, 9, element.consultation_sheet.total_ammount_to_pay_patient_with_discount)
            worksheet.write(r, 10, element.amount)
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('cash_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response

    def export_pdf(self, elements, start, end, filters):
        list_elements = []
        total_medical_study_ammount = 0
        total_medical_supply_ammount = 0
        total_discount = 0
        total_total_ammount_to_pay_patient_with_discount = 0
        total_amount_paid = 0

        payment_methods = PaymentMethod.objects.all()
        totals_payment_method = []

        for payment_method in payment_methods:
            total_payment_method = {
                'total_name': payment_method.name,
                'total': 0
            }
            totals_payment_method.append(total_payment_method)

        for element in elements:
            # column.append(element.id)
            payment_date = timezone.localtime(element.payment_datetime)
            payment_date = payment_date.strftime("%d/%m/%Y %H:%M")

            total_medical_study_ammount += element.consultation_sheet.medical_study_ammount
            total_medical_supply_ammount += element.consultation_sheet.medical_supplies_ammount
            total_discount += element.consultation_sheet.discount
            total_total_ammount_to_pay_patient_with_discount += element.consultation_sheet.total_ammount_to_pay_patient_with_discount
            total_amount_paid += element.amount

            if element.payment_method.abbreviation == 'CS':
                service_amount = element.consultation_sheet.total_ammount_to_pay_insurance
                discount = 0
                to_pay = 0
                paid = 0
                balance = 0
            else:
                service_amount = element.consultation_sheet.total_ammount_to_pay_patient
                discount = element.consultation_sheet.discount
                to_pay = element.consultation_sheet.total_ammount_to_pay_patient_with_discount
                paid = element.amount
                # TODO: Cambiar esto por el saldo del momento luego de ocurrir el pago.
                balance = to_pay - element.amount

            for total_payment_method in totals_payment_method:
                if element.payment_method and element.payment_method.name == total_payment_method['total_name']:
                    total_payment_method['total'] += to_pay

            dictionary = {
                'document_number': element.consultation_sheet.patient.document_number,
                'patient': element.consultation_sheet.patient.name + " " + element.consultation_sheet.patient.last_name,
                'insurance': element.consultation_sheet.patient_insurance_plan.name,
                'service': element.consultation_sheet.medical_study.name,
                'payment_method': element.payment_method.abbreviation,
                'service_amount': service_amount,
                'discount': discount,
                'to_pay': to_pay,
                'paid': paid,
                'balance': balance
            }
            list_elements.append(dictionary)

        special_totals = []
        for total_payment_method in totals_payment_method:
            if total_payment_method['total'] > 0:
                special_totals.append(total_payment_method)

        file_name = _('cash_report')
        report_title = _('Cash Report')

        # NOTE: these params must match exactly with the parameters defined in the
        # report definition in ReportBro Designer, check the name and type (Number, Date, List, ...)
        # of those parameters in the Designer.
        params = dict(
            payments=list_elements,
            special_totals=special_totals,
            filters=filters,
            start=start,
            end=end,
            report_title=report_title,
            current_date=datetime.datetime.now()
        )

        report_definition = ReportDefinition.objects.get(report_type='cash_report')
        if not report_definition:
            return HttpResponseServerError('no report_definition available')

        try:
            report_inst = Report(json.loads(report_definition.report_definition), params)
            if report_inst.errors:
                # report definition should never contain any errors,
                # unless you saved an invalid report and didn't test in ReportBro Designer
                raise ReportBroError(report_inst.errors[0])

            pdf_report = report_inst.generate_pdf()
            response = HttpResponse(pdf_report, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="{filename}"'.format(filename=file_name + '.pdf')
            return response
        except ReportBroError as ex:
            return HttpResponseServerError('report error: ' + str(ex.error))
        except Exception as ex:
            return HttpResponseServerError('report exception: ' + str(ex))


# Reporting Doctors Report
class ReportingDoctorsReportListView(LoginRequiredMixin, ListView):
    template_name = 'reporting_doctors_report/reporting_doctors_report_list.html'
    context_object_name = "consultation_sheets"
    model = ConsultationSheet

    def get_queryset(self):
        queryset = []
        form = ReportingDoctorsReportFiltersForm(self.request.GET)
        reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
        delivered_state = ConsultationState.objects.get(state_code=ConsultationState.DELIVERED_STATE)
        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            if form.is_valid():
                start = form.cleaned_data.get('date_time_start')
                end = form.cleaned_data.get('date_time_end')
                queryset = ConsultationSheet.objects.filter(
                    Q(consultation_date__range=[start, end], consultation_state=reported_state) |
                    Q(consultation_date__range=[start, end], consultation_state=delivered_state)
                )

                # Reporting Doctor Filter
                reporting_doctor = form.cleaned_data.get('reporting_doctor', None)
                if reporting_doctor:
                    queryset = queryset.filter(reporting_doctor=reporting_doctor)

                # Sector Filter
                sector = form.cleaned_data.get('sector', None)
                if sector:
                    queryset = queryset.filter(medical_study__sector=sector)

        else:
            if self.request.GET.get('insurance_plan') or self.request.GET.get('sector'):
                if form.is_valid():
                    queryset = ConsultationSheet.objects.filter(
                        Q(consultation_state=reported_state) |
                        Q(consultation_state=delivered_state)
                    )

                    # Reporting Doctor Filter
                    reporting_doctor = form.cleaned_data.get('reporting_doctor', None)
                    if reporting_doctor:
                        queryset = queryset.filter(reporting_doctor=reporting_doctor)

                    # Sector Filter
                    sector = form.cleaned_data.get('sector', None)
                    if sector:
                        queryset = queryset.filter(medical_study__sector=sector)

        return queryset

    def get(self, request, *args, **kwargs):
        form = ReportingDoctorsReportFiltersForm(self.request.GET)
        if form.is_valid():
            filters = []

            start = form.cleaned_data.get('date_time_start')
            end = form.cleaned_data.get('date_time_end')
            reporting_doctor = form.cleaned_data.get('reporting_doctor', None)
            sector = form.cleaned_data.get('sector', None)

            if reporting_doctor:
                report_filter = {
                    'name': _('Reporting Doctor'),
                    'value': str(reporting_doctor)
                }
                filters.append(report_filter)

            if sector:
                report_filter = {
                    'name': _('Sector'),
                    'value': str(sector)
                }
                filters.append(report_filter)

            report_filter = {
                'name': _('User'),
                'value': self.request.user.username
            }
            filters.append(report_filter)

            elements = self.get_queryset()
            report_type = form.cleaned_data.get('report_type')

            if elements and report_type == str(ReportingDoctorsReportFiltersForm.EXCEL_TYPE):
                return self.export_excel(elements)

            elif elements and report_type == str(ReportingDoctorsReportFiltersForm.PDF_TYPE):
                return self.export_pdf(elements, start, end, filters)

            else:
                return super().get(self, request, *args, **kwargs)

        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}

        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            initial['date_time_start'] = self.request.GET.get('date_time_start')
            initial['date_time_end'] = self.request.GET.get('date_time_end')
        else:
            now = datetime.datetime.now()
            inicio = datetime.datetime(year=now.year,
                                       month=now.month,
                                       day=now.day,
                                       hour=1,
                                       minute=0,
                                       second=0)
            fin = datetime.datetime(year=now.year,
                                    month=now.month,
                                    day=now.day,
                                    hour=22,
                                    minute=59,
                                    second=59)

            inicio = timezone.make_aware(inicio)
            fin = timezone.make_aware(fin)

            initial['date_time_start'] = inicio
            initial['date_time_end'] = fin

        if self.request.GET.get('reporting_doctor'):
            initial['reporting_doctor'] = self.request.GET.get('reporting_doctor')

        if self.request.GET.get('sector'):
            initial['sector'] = self.request.GET.get('sector')

        if self.request.GET.get('report_type'):
            initial['report_type'] = self.request.GET.get('report_type')

        filter_form = ReportingDoctorsReportFiltersForm(initial=initial)
        context.update({
            'filter_form': filter_form
        })
        return context

    def export_excel(self, elements):
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # r = Row and c = Column
        r = 0
        c = 1

        # Table header
        table_headers = [
            # 'ID Ficha de Estudio',
            'Fecha Hora',
            'Paciente',
            'Seguro',
            'Doctor Informante',
            'Estudio',
            'Sector',
            'Arancel de Estudio',
            'Insumos',
            'Descuento',
            'Total Pagado Seguro',
            'Total Pagado Paciente'
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            # worksheet.write(r, 0, element.id)
            consultation_date = timezone.localtime(element.consultation_date)
            consultation_date = consultation_date.strftime("%d/%m/%Y %H:%M")

            worksheet.write(r, 1, consultation_date)
            worksheet.write(r, 2, str(element.patient))
            worksheet.write(r, 3, str(element.patient_insurance_plan))
            worksheet.write(r, 4, str(element.reporting_doctor))
            worksheet.write(r, 5, str(element.medical_study))
            worksheet.write(r, 6, str(element.medical_study.sector))
            worksheet.write(r, 7, element.medical_study_ammount)
            worksheet.write(r, 8, element.medical_supplies_ammount)
            worksheet.write(r, 9, element.discount)
            worksheet.write(r, 10, element.total_ammount_to_pay_insurance)
            worksheet.write(r, 11, element.total_ammount_to_pay_patient_with_discount)
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('reporting_doctor_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response

    def export_pdf(self, elements, start, end, filters):
        list_elements = []

        for element in elements:
            # column.append(element.id)
            consultation_date = timezone.localtime(element.consultation_date)
            consultation_date = consultation_date.strftime("%d/%m/%Y %H:%M")

            dictionary = {
                'date': consultation_date,
                'patient': element.patient.name + " " + element.patient.last_name,
                'doctor': element.reporting_doctor.name + " " + element.reporting_doctor.last_name,
                'study': element.medical_study.name,
                'sector': element.medical_study.sector.name,
                'study_amount': element.medical_study_ammount,
                'supplies_amount': element.medical_supplies_ammount,
                'discount': element.discount,
                'insurance_amount': element.total_ammount_to_pay_insurance,
                'patient_amount': element.total_ammount_to_pay_patient_with_discount
            }
            list_elements.append(dictionary)

        file_name = _('reporting_doctor_report')
        report_title = _('Reporting Doctors Report')

        # NOTE: these params must match exactly with the parameters defined in the
        # report definition in ReportBro Designer, check the name and type (Number, Date, List, ...)
        # of those parameters in the Designer.
        params = dict(
            consultation_sheets=list_elements,
            filters=filters,
            start=start,
            end=end,
            report_title=report_title,
            current_date=datetime.datetime.now()
        )

        report_definition = ReportDefinition.objects.get(report_type='reporting_doctors_report')
        if not report_definition:
            return HttpResponseServerError('no report_definition available')

        try:
            report_inst = Report(json.loads(report_definition.report_definition), params)
            if report_inst.errors:
                # report definition should never contain any errors,
                # unless you saved an invalid report and didn't test in ReportBro Designer
                raise ReportBroError(report_inst.errors[0])

            pdf_report = report_inst.generate_pdf()
            response = HttpResponse(pdf_report, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="{filename}"'.format(filename=file_name + '.pdf')
            return response
        except ReportBroError as ex:
            return HttpResponseServerError('report error: ' + str(ex.error))
        except Exception as ex:
            return HttpResponseServerError('report exception: ' + str(ex))


# Treating Doctors Report List View
class TreatingDoctorsReportListView(LoginRequiredMixin, ListView):
    template_name = 'treating_doctors_report/treating_doctors_report_list.html'
    context_object_name = "consultation_sheets"
    model = ConsultationSheet

    def get_queryset(self):
        queryset = []
        form = TreatingDoctorsReportFiltersForm(self.request.GET)
        # reported_state = ConsultationState.objects.get(state_code=ConsultationState.REPORTED_STATE)
        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            if form.is_valid():
                start = form.cleaned_data.get('date_time_start')
                end = form.cleaned_data.get('date_time_end')
                queryset = ConsultationSheet.objects.filter(
                    consultation_date__range=[start, end],
                    # consultation_state=reported_state
                )

                # Treating Doctor Filter
                treating_doctor = form.cleaned_data.get('treating_doctor', None)
                if treating_doctor:
                    queryset = queryset.filter(treating_doctor=treating_doctor)

                # Sector Filter
                sector = form.cleaned_data.get('sector', None)
                if sector:
                    queryset = queryset.filter(medical_study__sector=sector)

        else:
            if self.request.GET.get('treating_doctor') or self.request.GET.get('sector'):
                if form.is_valid():
                    queryset = ConsultationSheet.objects.all()

                    # Reporting Doctor Filter
                    treating_doctor = form.cleaned_data.get('treating_doctor', None)
                    if treating_doctor:
                        queryset = queryset.filter(treating_doctor=treating_doctor)

                    # Sector Filter
                    sector = form.cleaned_data.get('sector', None)
                    if sector:
                        queryset = queryset.filter(medical_study__sector=sector)

        return queryset

    def get(self, request, *args, **kwargs):
        form = TreatingDoctorsReportFiltersForm(self.request.GET)
        if form.is_valid():
            filters = []

            start = form.cleaned_data.get('date_time_start')
            end = form.cleaned_data.get('date_time_end')
            treating_doctor = form.cleaned_data.get('treating_doctor', None)
            sector = form.cleaned_data.get('sector', None)

            if treating_doctor:
                report_filter = {
                    'name': _('Treating Doctor'),
                    'value': str(treating_doctor)
                }
                filters.append(report_filter)

            if sector:
                report_filter = {
                    'name': _('Sector'),
                    'value': str(sector)
                }
                filters.append(report_filter)

            report_filter = {
                'name': _('User'),
                'value': self.request.user.username
            }
            filters.append(report_filter)

            elements = self.get_queryset()
            report_type = form.cleaned_data.get('report_type')

            if elements and report_type == str(TreatingDoctorsReportFiltersForm.EXCEL_TYPE):
                return self.export_excel(elements)

            elif elements and report_type == str(TreatingDoctorsReportFiltersForm.PDF_TYPE):
                return self.export_pdf(elements, start, end, filters)

            else:
                return super().get(self, request, *args, **kwargs)

        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}

        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            initial['date_time_start'] = self.request.GET.get('date_time_start')
            initial['date_time_end'] = self.request.GET.get('date_time_end')
        else:
            now = datetime.datetime.now()
            inicio = datetime.datetime(year=now.year,
                                       month=now.month,
                                       day=now.day,
                                       hour=1,
                                       minute=0,
                                       second=0)
            fin = datetime.datetime(year=now.year,
                                    month=now.month,
                                    day=now.day,
                                    hour=22,
                                    minute=59,
                                    second=59)

            inicio = timezone.make_aware(inicio)
            fin = timezone.make_aware(fin)

            initial['date_time_start'] = inicio
            initial['date_time_end'] = fin

        if self.request.GET.get('treating_doctor'):
            initial['treating_doctor'] = self.request.GET.get('treating_doctor')

        if self.request.GET.get('sector'):
            initial['sector'] = self.request.GET.get('sector')

        if self.request.GET.get('report_type'):
            initial['report_type'] = self.request.GET.get('report_type')

        filter_form = TreatingDoctorsReportFiltersForm(initial=initial)
        context.update({
            'filter_form': filter_form
        })
        return context

    def export_excel(self, elements):
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # r = Row and c = Column
        r = 0
        c = 1

        # Table header
        table_headers = [
            # 'ID Ficha de Estudio',
            'Fecha Hora',
            'Paciente',
            'Seguro',
            'Doctor Tratante',
            'Estudio',
            'Sector',
            'Arancel de Estudio',
            'Insumos',
            'Descuento',
            'Total Pagado Seguro',
            'Total Pagado Paciente'
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            # worksheet.write(r, 0, element.id)
            consultation_date = timezone.localtime(element.consultation_date)
            consultation_date = consultation_date.strftime("%d/%m/%Y %H:%M")

            worksheet.write(r, 1, consultation_date)
            worksheet.write(r, 2, str(element.patient))
            worksheet.write(r, 3, str(element.patient_insurance_plan))
            worksheet.write(r, 4, str(element.treating_doctor))
            worksheet.write(r, 5, str(element.medical_study))
            worksheet.write(r, 6, str(element.medical_study.sector))
            worksheet.write(r, 7, element.medical_study_ammount)
            worksheet.write(r, 8, element.medical_supplies_ammount)
            worksheet.write(r, 9, element.discount)
            worksheet.write(r, 10, element.total_ammount_to_pay_insurance)
            worksheet.write(r, 11, element.total_ammount_to_pay_patient_with_discount)
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('treating_doctor_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response

    def export_pdf(self, elements, start, end, filters):
        list_elements = []

        for element in elements:
            # column.append(element.id)
            consultation_date = timezone.localtime(element.consultation_date)
            consultation_date = consultation_date.strftime("%d/%m/%Y %H:%M")

            dictionary = {
                'date': consultation_date,
                'patient': element.patient.name + " " + element.patient.last_name,
                'doctor': element.treating_doctor.name + " " + element.treating_doctor.last_name,
                'study': element.medical_study.name,
                'sector': element.medical_study.sector.name,
                'study_amount': element.medical_study_ammount,
                'supplies_amount': element.medical_supplies_ammount,
                'discount': element.discount,
                'insurance_amount': element.total_ammount_to_pay_insurance,
                'patient_amount': element.total_ammount_to_pay_patient_with_discount
            }
            list_elements.append(dictionary)

        file_name = _('treating_doctor_report')
        report_title = _('Treating Doctors Report')

        # NOTE: these params must match exactly with the parameters defined in the
        # report definition in ReportBro Designer, check the name and type (Number, Date, List, ...)
        # of those parameters in the Designer.
        params = dict(
            consultation_sheets=list_elements,
            filters=filters,
            start=start,
            end=end,
            report_title=report_title,
            current_date=datetime.datetime.now()
        )

        report_definition = ReportDefinition.objects.get(report_type='treating_doctors_report')
        if not report_definition:
            return HttpResponseServerError('no report_definition available')

        try:
            report_inst = Report(json.loads(report_definition.report_definition), params)
            if report_inst.errors:
                # report definition should never contain any errors,
                # unless you saved an invalid report and didn't test in ReportBro Designer
                raise ReportBroError(report_inst.errors[0])

            pdf_report = report_inst.generate_pdf()
            response = HttpResponse(pdf_report, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="{filename}"'.format(filename=file_name + '.pdf')
            return response
        except ReportBroError as ex:
            return HttpResponseServerError('report error: ' + str(ex.error))
        except Exception as ex:
            return HttpResponseServerError('report exception: ' + str(ex))


# Insurances Agreements Report List View
class InsurancesAgreementsReportListView(LoginRequiredMixin, ListView):
    template_name = 'insurances_agreements_report/insurances_agreements_report_list.html'
    context_object_name = "consultation_sheets"
    model = ConsultationSheet

    def get_queryset(self):
        queryset = []
        form = InsurancesAgreementsReportFiltersForm(self.request.GET)
        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            if form.is_valid():
                start = form.cleaned_data.get('date_time_start')
                end = form.cleaned_data.get('date_time_end')
                queryset = ConsultationSheet.objects.filter(
                    consultation_date__range=[start, end],
                    total_ammount_to_pay_insurance__gt=0,
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

        else:
            if self.request.GET.get('insurance_plan') or self.request.GET.get('sector') or self.request.GET.get(
                    'study_type'):
                if form.is_valid():
                    queryset = ConsultationSheet.objects.all().filter(
                        total_ammount_to_pay_insurance__gt=0).order_by(
                        'medical_study__sector', 'consultation_date')

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

    def get(self, request, *args, **kwargs):
        form = InsurancesAgreementsReportFiltersForm(self.request.GET)
        if form.is_valid():
            filters = []
            start = form.cleaned_data.get('date_time_start')
            end = form.cleaned_data.get('date_time_end')
            insurance_plan = form.cleaned_data.get('insurance_plan', None)
            sector = form.cleaned_data.get('sector', None)
            study_type = form.cleaned_data.get('study_type', None)
            invoice_filter = form.cleaned_data.get('invoice_filter', None)

            if insurance_plan:
                report_filter = {
                    'name': _('Insurance Plan'),
                    'value': str(insurance_plan)
                }
                filters.append(report_filter)

            if sector:
                report_filter = {
                    'name': _('Sector'),
                    'value': str(sector)
                }
                filters.append(report_filter)

            if study_type:
                report_filter = {
                    'name': _('Study Type'),
                    'value': str(study_type)
                }
                filters.append(report_filter)

            if invoice_filter:
                report_filter = {
                    'name': _('Invoice Filter'),
                    'value': str(invoice_filter)
                }
                filters.append(report_filter)

            elements = self.get_queryset()
            report_type = form.cleaned_data.get('report_type')

            if elements and report_type == str(InsurancesAgreementsReportFiltersForm.EXCEL_TYPE):
                return self.export_excel(elements)

            elif elements and report_type == str(InsurancesAgreementsReportFiltersForm.PDF_TYPE):
                return self.export_pdf(elements, start, end, filters)

            else:
                return super().get(self, request, *args, **kwargs)

        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}

        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            initial['date_time_start'] = self.request.GET.get('date_time_start')
            initial['date_time_end'] = self.request.GET.get('date_time_end')
        else:
            now = datetime.datetime.now()
            inicio = datetime.datetime(year=now.year,
                                       month=now.month,
                                       day=now.day,
                                       hour=1,
                                       minute=0,
                                       second=0)
            fin = datetime.datetime(year=now.year,
                                    month=now.month,
                                    day=now.day,
                                    hour=22,
                                    minute=59,
                                    second=59)

            inicio = timezone.make_aware(inicio)
            fin = timezone.make_aware(fin)

            initial['date_time_start'] = inicio
            initial['date_time_end'] = fin

        if self.request.GET.get('insurance_plan'):
            initial['insurance_plan'] = self.request.GET.get('insurance_plan')

        if self.request.GET.get('sector'):
            initial['sector'] = self.request.GET.get('sector')

        if self.request.GET.get('study_type'):
            initial['study_type'] = self.request.GET.get('study_type')

        if self.request.GET.get('report_type'):
            initial['report_type'] = self.request.GET.get('report_type')

        if self.request.GET.get('invoice_filter'):
            initial['invoice_filter'] = self.request.GET.get('invoice_filter')

        filter_form = InsurancesAgreementsReportFiltersForm(initial=initial)
        context.update({
            'filter_form': filter_form
        })
        return context

    def export_excel(self, elements):
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # r = Row and c = Column
        r = 0
        c = 1

        # Table header
        table_headers = [
            # 'ID Ficha de Estudio',
            'Fecha Hora',
            'Paciente',
            'Seguro',
            'Servicio',
            'Sector',
            'Arancel de Estudio',
            'Insumos',
            'Total a Cobrar Seguro'
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            # worksheet.write(r, 0, element.id)
            consultation_date = timezone.localtime(element.consultation_date)
            consultation_date = consultation_date.strftime("%d/%m/%Y %H:%M")

            worksheet.write(r, 1, consultation_date)
            worksheet.write(r, 2, str(element.patient))
            worksheet.write(r, 3, str(element.patient_insurance_plan))
            worksheet.write(r, 4, str(element.medical_study))
            worksheet.write(r, 5, str(element.medical_study.sector))
            worksheet.write(r, 6, element.medical_study_ammount_to_pay_insurance)
            worksheet.write(r, 7, element.medical_supplies_ammount_to_pay_insurance)
            worksheet.write(r, 8, element.total_ammount_to_pay_insurance)
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('insurances_agreements_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response

    def export_pdf(self, elements, start, end, filters):
        # Line to change elements order
        # elements = elements.order_by('patient', 'consultation_date')

        totals_sectors = []

        sectors = Sector.objects.all()

        list_elements = []

        for sector in sectors:
            total_sector = {
                'total_name': sector.name,
                'total': 0
            }
            totals_sectors.append(total_sector)

        for element in elements:
            # column.append(element.id)
            consultation_date = timezone.localtime(element.consultation_date)
            consultation_date = consultation_date.strftime("%d/%m/%Y %H:%M")

            dictionary = {
                'date': consultation_date,
                'patient': element.patient.name + " " + element.patient.last_name,
                'study': element.medical_study.name,
                'sector': element.medical_study.sector.name,
                'study_amount': element.medical_study_ammount_to_pay_insurance,
                'supplies_amount': element.medical_supplies_ammount_to_pay_insurance,
                'insurance_amount': element.total_ammount_to_pay_insurance
            }
            list_elements.append(dictionary)

            for total_sector in totals_sectors:
                if element.medical_study.sector and element.medical_study.sector.name == total_sector['total_name']:
                    total_sector['total'] += element.total_ammount_to_pay_insurance

        special_totals = []
        for total_sector in totals_sectors:
            if total_sector['total'] > 0:
                special_totals.append(total_sector)

        file_name = _('insurances_agreements_report')
        report_title = _('Insurances Agreements Report')

        # NOTE: these params must match exactly with the parameters defined in the
        # report definition in ReportBro Designer, check the name and type (Number, Date, List, ...)
        # of those parameters in the Designer.
        params = dict(
            consultation_sheets=list_elements,
            special_totals=special_totals,
            filters=filters,
            start=start,
            end=end,
            report_title=report_title,
            current_date=datetime.datetime.now()
        )

        report_definition = ReportDefinition.objects.get(report_type='insurances_agreements_report')
        if not report_definition:
            return HttpResponseServerError('no report_definition available')

        try:
            report_inst = Report(json.loads(report_definition.report_definition), params)
            if report_inst.errors:
                # report definition should never contain any errors,
                # unless you saved an invalid report and didn't test in ReportBro Designer
                raise ReportBroError(report_inst.errors[0])

            pdf_report = report_inst.generate_pdf()
            response = HttpResponse(pdf_report, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="{filename}"'.format(filename=file_name + '.pdf')
            return response
        except ReportBroError as ex:
            return HttpResponseServerError('report error: ' + str(ex.error))
        except Exception as ex:
            return HttpResponseServerError('report exception: ' + str(ex))


# Consultation Sheet Total Report List View
class ConsultationSheetTotalReportListView(LoginRequiredMixin, ListView):
    template_name = 'consultation_sheet_total_report/consultation_sheet_total_report.html'
    context_object_name = "consultation_sheets"
    model = ConsultationSheet

    def get_queryset(self):
        queryset = []
        form = ConsultationSheetsTotalReportFiltersForm(self.request.GET)
        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            if form.is_valid():
                start = form.cleaned_data.get('date_time_start')
                end = form.cleaned_data.get('date_time_end')
                queryset = ConsultationSheet.objects.filter(
                    consultation_date__range=[start, end],
                )

                # Insurance Plan Filter
                insurance_plan = form.cleaned_data.get('insurance_plan', None)
                if insurance_plan:
                    queryset = queryset.filter(patient_insurance_plan=insurance_plan)

                # Medical Study
                medical_study = form.cleaned_data.get('medical_study', None)
                if medical_study:
                    queryset = queryset.filter(medical_study=medical_study)

                # Sector Filter
                sector = form.cleaned_data.get('sector', None)
                if sector:
                    queryset = queryset.filter(medical_study__sector=sector)

                # Study Type Filter
                study_type = form.cleaned_data.get('study_type', None)
                if study_type:
                    queryset = queryset.filter(medical_study__type=study_type)

                # Medical Equipment
                medical_equipment = form.cleaned_data.get('medical_equipment', None)
                if medical_study:
                    queryset = queryset.filter(medical_equipment=medical_equipment)

                # Doctor
                doctor = form.cleaned_data.get('doctor', None)
                if doctor:
                    queryset = queryset.filter(doctor=doctor)

                # Reporting Doctor
                reporting_doctor = form.cleaned_data.get('reporting_doctor', None)
                if reporting_doctor:
                    queryset = queryset.filter(reporting_doctor=reporting_doctor)

                # Treating Doctor
                treating_doctor = form.cleaned_data.get('treating_doctor', None)
                if treating_doctor:
                    queryset = queryset.filter(treating_doctor=treating_doctor)

                # Payment Method
                payment_method = form.cleaned_data.get('payment_method', None)
                if payment_method:
                    queryset = queryset.filter(payment_method=payment_method)

        else:
            if self.request.GET.get('insurance_plan') or self.request.GET.get('sector') or self.request.GET.get(
                    'study_type'):
                if form.is_valid():
                    queryset = ConsultationSheet.objects.all()

                # Insurance Plan Filter
                insurance_plan = form.cleaned_data.get('insurance_plan', None)
                if insurance_plan:
                    queryset = queryset.filter(patient_insurance_plan=insurance_plan)

                # Medical Study
                medical_study = form.cleaned_data.get('medical_study', None)
                if medical_study:
                    queryset = queryset.filter(medical_study=medical_study)

                # Sector Filter
                sector = form.cleaned_data.get('sector', None)
                if sector:
                    queryset = queryset.filter(medical_study__sector=sector)

                # Study Type Filter
                study_type = form.cleaned_data.get('study_type', None)
                if study_type:
                    queryset = queryset.filter(medical_study__type=study_type)

                # Medical Equipment
                medical_equipment = form.cleaned_data.get('medical_equipment', None)
                if medical_study:
                    queryset = queryset.filter(medical_equipment=medical_equipment)

                # Doctor
                doctor = form.cleaned_data.get('doctor', None)
                if doctor:
                    queryset = queryset.filter(doctor=doctor)

                # Reporting Doctor
                reporting_doctor = form.cleaned_data.get('reporting_doctor', None)
                if reporting_doctor:
                    queryset = queryset.filter(reporting_doctor=reporting_doctor)

                # Treating Doctor
                treating_doctor = form.cleaned_data.get('treating_doctor', None)
                if treating_doctor:
                    queryset = queryset.filter(treating_doctor=treating_doctor)

                # Payment Method
                payment_method = form.cleaned_data.get('payment_method', None)
                if payment_method:
                    queryset = queryset.filter(payment_method=payment_method)

        return queryset

    def get(self, request, *args, **kwargs):
        form = ConsultationSheetsTotalReportFiltersForm(self.request.GET)
        if form.is_valid():
            elements = self.get_queryset()
            report_type = form.cleaned_data.get('report_type')

            if elements and report_type == str(ConsultationSheetsTotalReportFiltersForm.EXCEL_TYPE):
                return self.export_excel(elements)

            else:
                return super().get(self, request, *args, **kwargs)

        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}

        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            initial['date_time_start'] = self.request.GET.get('date_time_start')
            initial['date_time_end'] = self.request.GET.get('date_time_end')
        else:
            now = datetime.datetime.now()
            inicio = datetime.datetime(year=now.year,
                                       month=now.month,
                                       day=now.day,
                                       hour=1,
                                       minute=0,
                                       second=0)
            fin = datetime.datetime(year=now.year,
                                    month=now.month,
                                    day=now.day,
                                    hour=22,
                                    minute=59,
                                    second=59)

            inicio = timezone.make_aware(inicio)
            fin = timezone.make_aware(fin)

            initial['date_time_start'] = inicio
            initial['date_time_end'] = fin

        if self.request.GET.get('insurance_plan'):
            initial['insurance_plan'] = self.request.GET.get('insurance_plan')

        if self.request.GET.get('medical_study'):
            initial['medical_study'] = self.request.GET.get('medical_study')

        if self.request.GET.get('sector'):
            initial['sector'] = self.request.GET.get('sector')

        if self.request.GET.get('study_type'):
            initial['study_type'] = self.request.GET.get('study_type')

        if self.request.GET.get('medical_equipment'):
            initial['medical_equipment'] = self.request.GET.get('medical_equipment')

        if self.request.GET.get('doctor'):
            initial['doctor'] = self.request.GET.get('doctor')

        if self.request.GET.get('reporting_doctor'):
            initial['reporting_doctor'] = self.request.GET.get('reporting_doctor')

        if self.request.GET.get('treating_doctor'):
            initial['treating_doctor'] = self.request.GET.get('treating_doctor')

        if self.request.GET.get('payment_method'):
            initial['payment_method'] = self.request.GET.get('payment_method')

        if self.request.GET.get('report_type'):
            initial['report_type'] = self.request.GET.get('report_type')

        filter_form = ConsultationSheetsTotalReportFiltersForm(initial=initial)
        context.update({
            'filter_form': filter_form
        })
        return context

    def export_excel(self, elements):
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # r = Row and c = Column
        r = 0
        c = 1

        # Table header
        table_headers = [
            # 'ID Ficha de Estudio', #0
            'Fecha Hora',  # 1
            'Paciente',  # 2
            'Seguro',  # 3
            'Estudio',  # 4
            'Empresa',  # 5
            'Sector',  # 6
            'Equipo Médico',  # 7
            'Doctor',  # 8
            'Doctor Informante',  # 9
            'Doctor Tratante',  # 10
            'Método de Pago',  # 11
            'Arancel de Estudio',  # 12
            'Total a Pagar Estudio Seguro',  # 13
            'Total a Pagar Estudio Paciente',  # 14
            'Insumos',  # 15
            'Total a Pagar Insumos Seguro',  # 16
            'Total a Pagar Insumos Paciente',  # 17
            'Total a Pagar Paciente',  # 18
            'Descuento',  # 19
            'Total a Pagar Paciente con Descuento',  # 20
            'Total a Pagar Seguro',  # 21
            'Factura a Cliente Nro.',  # 22
            'Factura a Seguro Nro.',  # 23
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            # worksheet.write(r, 0, element.id) #0
            consultation_date = timezone.localtime(element.consultation_date)
            consultation_date = consultation_date.strftime("%d/%m/%Y %H:%M")
            invoice = element.consultation_entry_sheet.invoice
            insurance_invoice = element.consultation_entry_sheet.insurance_invoice

            worksheet.write(r, 1, consultation_date)  # 1
            worksheet.write(r, 2, str(element.patient))  # 2
            worksheet.write(r, 3, str(element.patient_insurance_plan))  # 3
            worksheet.write(r, 4, str(element.medical_study))  # 4
            worksheet.write(r, 5, str(element.medical_study.type))  # 5
            worksheet.write(r, 6, str(element.medical_study.sector))  # 6
            worksheet.write(r, 7, str(element.medical_equipment if element.medical_equipment else '-'))  # 7
            worksheet.write(r, 8, str(element.doctor if element.doctor else '-'))  # 8
            worksheet.write(r, 9, str(element.reporting_doctor if element.reporting_doctor else '-'))  # 9
            worksheet.write(r, 10, str(element.treating_doctor if element.treating_doctor else '-'))  # 10
            worksheet.write(r, 11, str(element.payment_method if element.payment_method else '-'))  # 11
            worksheet.write(r, 12, element.medical_study_ammount)  # 12
            worksheet.write(r, 13, element.medical_study_ammount_to_pay_insurance)  # 13
            worksheet.write(r, 14, element.medical_study_ammount_to_pay_patient)  # 14
            worksheet.write(r, 15, element.medical_supplies_ammount)  # 15
            worksheet.write(r, 16, element.medical_supplies_ammount_to_pay_insurance)  # 16
            worksheet.write(r, 17, element.medical_supplies_ammount_to_pay_patient)  # 17
            worksheet.write(r, 18, element.total_ammount_to_pay_patient)  # 18
            worksheet.write(r, 19, element.discount)  # 19
            worksheet.write(r, 20, element.total_ammount_to_pay_patient_with_discount)  # 20
            worksheet.write(r, 21, element.total_ammount_to_pay_insurance)  # 21
            worksheet.write(r, 22, invoice.invoice_number if invoice else '-')  # 22
            worksheet.write(r, 23, insurance_invoice.invoice_number if insurance_invoice else '-')  # 23
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('consultation_sheets_total_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response


class ReportDefinitionListView(ListView, LoginRequiredMixin):
    template_name = 'report_definition_list.html'
    context_object_name = "report_definitions"
    model = ReportDefinition


class ReportDefinitionCreateView(View, LoginRequiredMixin):

    def get(self, request, *args, **kwargs):
        new_report_definition = create_album_report_template()
        return redirect(reverse('reports.report_definition.update', kwargs={'pk': new_report_definition.pk}))


class ReportDefinitionUpdateView(View, LoginRequiredMixin):

    def get(self, request, *args, **kwargs):
        """Shows a page with ReportBro Designer to edit our albums report template.

         The report template is loaded from the db (report_definition table),
         in case no report template exists a hardcoded template is generated in
         *create_album_report_template* for this Demo App. Normally you'd probably
         start with an empty report (empty string, so no report is loaded
         in the Designer) in this case.
         """
        context = dict()
        report_id = kwargs['pk']
        # context['menu_items'] = get_menu_items('report')

        # load ReportBro report definition stored in our report_definition table
        row = ReportDefinition.objects.get(pk=report_id)
        context['report_definition'] = SafeString(row.report_definition)
        context['report_definition_object'] = row
        return render(request, 'edit_report.html', context)


class SaveReportView(View, LoginRequiredMixin):

    def put(self, request, *args, **kwargs):
        """Save report_definition in our db table.

        This method is called by save button in ReportBro Designer.
        The url is called in *saveReport* callback from the Designer,
        see *saveCallback* in edit.html
        """
        report_id = kwargs['pk']
        json_data = json.loads(request.body.decode('utf-8'))

        # perform some basic checks if all necessary fields for report_definition are present
        if not isinstance(json_data, dict) or not isinstance(json_data.get('docElements'), list) or \
                not isinstance(json_data.get('styles'), list) or not isinstance(json_data.get('parameters'), list) or \
                not isinstance(json_data.get('documentProperties'), dict) or not isinstance(json_data.get('version'),
                                                                                            int):
            return HttpResponseBadRequest('invalid values')

        report_definition = json.dumps(
            dict(
                docElements=json_data.get('docElements'), styles=json_data.get('styles'),
                parameters=json_data.get('parameters'),
                documentProperties=json_data.get('documentProperties'),
                version=json_data.get('version'),
                report_type=json_data.get('report_type'),
            ),
        )

        now = datetime.datetime.now()
        report_definition_object = ReportDefinition.objects.get(pk=report_id)
        report_definition_object.report_definition = report_definition
        report_definition_object.last_modified_at = now
        report_definition_object.report_type = json_data.get('report_type')
        report_definition_object.save()

        return HttpResponse('ok')


class RunReportView(View, LoginRequiredMixin):

    @xframe_options_exempt
    def put(self, request, *args, **kwargs):
        additional_fonts = []
        # add additional fonts here if additional fonts are used in ReportBro Designer
        now = datetime.datetime.now()
        # all data needed for report preview is sent in the initial PUT request, it contains
        # the format (pdf or xlsx), the report itself (report_definition), the data (test data
        # defined within parameters in the Designer) and is_test_data flag (always True
        # when request is sent from Designer)
        json_data = json.loads(request.body.decode('utf-8'))
        if not isinstance(json_data, dict) or not isinstance(json_data.get('report'), dict) or \
                not isinstance(json_data.get('data'), dict) or not isinstance(json_data.get('isTestData'), bool):
            return HttpResponseBadRequest('invalid report values')

        output_format = json_data.get('outputFormat')
        if output_format not in ('pdf', 'xlsx'):
            return HttpResponseBadRequest('outputFormat parameter missing or invalid')

        report_definition = json_data.get('report')
        data = json_data.get('data')
        is_test_data = json_data.get('isTestData')
        try:
            report = Report(report_definition, data, is_test_data, additional_fonts=additional_fonts)
        except Exception as e:
            return HttpResponseBadRequest('failed to initialize report: ' + str(e))

        if report.errors:
            # return list of errors in case report contains errors, e.g. duplicate parameters.
            # with this information ReportBro Designer can select object containing errors,
            # highlight erroneous fields and display error messages
            return HttpResponse(json.dumps(dict(errors=report.errors)))
        try:
            # delete old reports (older than 3 minutes) to avoid table getting too big
            ReportRequest.objects.filter(created_on__lt=(now - datetime.timedelta(minutes=3))).delete()

            total_size = ReportRequest.objects.aggregate(Sum('pdf_file_size'))
            if total_size['pdf_file_size__sum'] and total_size['pdf_file_size__sum'] > MAX_CACHE_SIZE:
                # delete all reports older than 10 seconds to reduce db size for cached pdf files
                ReportRequest.objects.filter(created_on__lt=(now - datetime.timedelta(seconds=10))).delete()

            start = timer()
            report_file = report.generate_pdf()
            end = timer()
            print('pdf generated in %.3f seconds' % (end - start))

            key = str(uuid.uuid4())
            # add report request into sqlite db, this enables downloading the report by url
            # (the report is identified by the key) without any post parameters.
            # This is needed for pdf and xlsx preview.
            ReportRequest.objects.create(
                key=key, report_definition=json.dumps(report_definition, default=json_default),
                data=json.dumps(data, default=json_default), is_test_data=is_test_data,
                pdf_file=report_file, pdf_file_size=len(report_file), created_on=now)

            return HttpResponse('key:' + key)
        except ReportBroError as err:
            # in case an error occurs during report generation a ReportBroError exception is thrown
            # to stop processing. We return this error within a list so the error can be
            # processed by ReportBro Designer.
            return HttpResponse(json.dumps(dict(errors=[err.error])))

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        additional_fonts = []
        # add additional fonts here if additional fonts are used in ReportBro Designer
        now = datetime.datetime.now()
        output_format = request.GET.get('outputFormat')
        if output_format not in ('pdf', 'xlsx'):
            return HttpResponseBadRequest('outputFormat parameter missing or invalid')
        key = request.GET.get('key')

        report = None
        report_file = None
        if key and len(key) == 36:
            # the report is identified by a key which was saved
            # in a table during report preview with a PUT request
            try:
                report_request = ReportRequest.objects.get(key=key)
            except ReportRequest.DoesNotExist:
                return HttpResponseBadRequest(
                    'report not found (preview probably too old), update report preview and try again')
            if output_format == 'pdf' and report_request.pdf_file:
                report_file = report_request.pdf_file
            else:
                report_definition = json.loads(report_request.report_definition)
                data = json.loads(report_request.data)
                is_test_data = report_request.is_test_data
                report = Report(report_definition, data, is_test_data, additional_fonts=additional_fonts)
                if report.errors:
                    return HttpResponseBadRequest(reason='error generating report')
        else:
            # in case there is a GET request without a key we expect all report data to be available.
            # this is NOT used by ReportBro Designer and only added for the sake of completeness.
            json_data = json.loads(request.body.decode('utf-8'))
            if not isinstance(json_data, dict) or not isinstance(json_data.get('report'), dict) or \
                    not isinstance(json_data.get('data'), dict) or not isinstance(json_data.get('isTestData'), bool):
                return HttpResponseBadRequest('invalid report values')
            report_definition = json_data.get('report')
            data = json_data.get('data')
            is_test_data = json_data.get('isTestData')
            if not isinstance(report_definition, dict) or not isinstance(data, dict):
                return HttpResponseBadRequest('report_definition or data missing')
            report = Report(report_definition, data, is_test_data, additional_fonts=additional_fonts)
            if report.errors:
                return HttpResponseBadRequest(reason='error generating report')

        try:
            # once we have the reportbro.Report instance we can generate
            # the report (pdf or xlsx) and return it
            if output_format == 'pdf':
                if report_file is None:
                    # as it is currently implemented the pdf file is always stored in the
                    # report_request table along the other report data. Therefor report_file
                    # will always be set. The generate_pdf call here is only needed in case
                    # the code is changed to clear report_request.pdf_file column when the
                    # data in this table gets too big (currently whole table rows are deleted)
                    report_file = report.generate_pdf()
                response = HttpResponse(
                    report_file, content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="{filename}"'.format(
                    filename='report-' + str(now) + '.pdf')
            else:
                report_file = report.generate_xlsx()
                response = HttpResponse(
                    report_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'inline; filename="{filename}"'.format(
                    filename='report-' + str(now) + '.xlsx')
            return response
        except ReportBroError:
            return HttpResponseBadRequest('error generating report')

    @xframe_options_exempt
    def options(self, request, *args, **kwargs):
        response = HttpResponse('')
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, PUT, OPTIONS'
        response[
            'Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, X-HTTP-Method-Override, Content-Type, Accept, Z-Key'
        return response


class InvoiceReportListView(LoginRequiredMixin, ListView):
    template_name = 'invoicing_report/invoicing_report_list.html'
    context_object_name = "invoice"
    model = InvoiceHeader

    def get_queryset(self):
        queryset = []
        form = InvoiceReportFiltersForm(self.request.GET)
        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            if form.is_valid():
                start = form.cleaned_data.get('date_time_start')
                end = form.cleaned_data.get('date_time_end')
                queryset = InvoiceHeader.objects.filter(
                    invoice_date__range=[start, end],
                )
                payment_term = form.cleaned_data.get('payment_term', None)
                company_name = form.cleaned_data.get('company_name', None)
                customer_name = form.cleaned_data.get('client', None)
                if payment_term:
                    queryset = queryset.filter(payment_term=payment_term)

                if company_name:
                    queryset = queryset.filter(company=company_name)

                if customer_name:
                    queryset = queryset.filter(customer=customer_name)

        else:
            if self.request.GET.get('payment_method') or self.request.GET.get('company_name'):
                if form.is_valid():
                    queryset = InvoiceHeader.objects.all()
                    payment_term = form.cleaned_data.get('payment_term', None)

                    if payment_term:
                        queryset = queryset.filter(payment_term=payment_term)

                    company_name = form.cleaned_data.get('company_name', None)

                    if company_name:
                        queryset = queryset.filter(company=company_name)

                    customer_name = form.cleaned_data.get('client', None)

                    if customer_name:
                        queryset = queryset.filter(customer=customer_name)

        return queryset

    def get(self, request, *args, **kwargs):
        form = InvoiceReportFiltersForm(self.request.GET)
        if form.is_valid():
            filters = []
            start = form.cleaned_data.get('date_time_start')
            end = form.cleaned_data.get('date_time_end')
            payment_term = form.cleaned_data.get('payment_term', None)
            company_name = form.cleaned_data.get('company_name', None)
            customer_name = form.cleaned_data.get('client', None)

            if payment_term:
                report_filter = {
                    'name': _('Payment Method'),
                    'value': str(payment_term)
                }
                filters.append(report_filter)

            if company_name:
                report_filter = {
                    'name': _('Study Type'),
                    'value': str(company_name)
                }
                filters.append(report_filter)

            report_filter = {
                'name': _('User'),
                'value': self.request.user.username
            }
            filters.append(report_filter)

            elements = self.get_queryset()
            report_type = form.cleaned_data.get('report_type')

            if elements and report_type == str(InvoiceReportFiltersForm.EXCEL_TYPE):
                return self.export_excel(elements)
            elif elements and report_type == str(InvoiceReportFiltersForm.ABACO_TYPE):
                return self.export_abaco(elements)
            else:
                return super().get(self, request, *args, **kwargs)

        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}

        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            initial['date_time_start'] = self.request.GET.get('date_time_start')
            initial['date_time_end'] = self.request.GET.get('date_time_end')
        else:
            now = datetime.datetime.now()
            inicio = datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=1,
                minute=0,
                second=0
            )
            fin = datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=22,
                minute=59,
                second=59
            )

            inicio = timezone.make_aware(inicio)
            fin = timezone.make_aware(fin)

            initial['date_time_start'] = inicio
            initial['date_time_end'] = fin

        if self.request.GET.get('company_name'):
            initial['company_name'] = self.request.GET.get('company_name')

        if self.request.GET.get('client'):
            initial['client'] = self.request.GET.get('client')

        if self.request.GET.get('payment_term'):
            initial['payment_term'] = self.request.GET.get('payment_term')

        if self.request.GET.get('report_type'):
            initial['report_type'] = self.request.GET.get('report_type')

        filter_form = InvoiceReportFiltersForm(initial=initial)
        context.update({
            'filter_form': filter_form
        })
        return context

    def export_excel(self, elements):
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # r = Row and c = Column
        r = 0
        c = 0

        # Table header
        table_headers = [
            # 'Nro Factura',
            'Numero de Factura',
            'Empresa',
            'Fecha',
            'RUC',
            'Cliente',
            'Condicion de Pago',
            'Exentas',
            'IVA 5%',
            'IVA 10%',
            'Total'
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            # worksheet.write(r, 0, element.id)
            # invoice_date = timezone.localtime(element.invoice_date)
            invoice_date = element.invoice_date.strftime("%d/%m/%Y")

            worksheet.write(r, 0, str(element.invoice_number))
            worksheet.write(r, 1, str(element.company.company_name))
            worksheet.write(r, 2, str(invoice_date))
            worksheet.write(r, 3, str(element.client_tax_identification_number))
            worksheet.write(r, 4, str(element.client_name))
            worksheet.write(r, 5, str(element.payment_term))
            worksheet.write(r, 6, str(element.total_exempt))
            worksheet.write(r, 7, element.total_tax5)
            worksheet.write(r, 8, element.total_tax10)
            worksheet.write(r, 9, element.invoice_total)
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('invoice_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response

    def export_abaco(self, elements):
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        # r = Row and c = Column
        r = 0
        c = 0

        # Table header
        table_headers = [
            # 'ID Factura',
            'FECHA',
            'FACTURA',
            'TIMBRADO',
            'TIMBRADO_VENCIMIENTO',
            'RUC',
            'PERSONA',
            'GRAVADAS_10',
            'GRAVADAS_05',
            'EXENTAS',
            'TOTAL',
            'MONEDA',
            'CONDICION',
            'CUOTAS',
            'CUENTA_10',
            'CUENTA_05',
            'CUENTA_00'
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            invoice_date = element.invoice_date.strftime("%d/%m/%Y")
            stamp_end_date = element.invoice_stamp.endDate.strftime("%d/%m/%Y")
            stamp = element.invoice_stamp.number

            worksheet.write(r, 0, invoice_date)
            worksheet.write(r, 1, element.invoice_number)
            worksheet.write(r, 2, stamp)
            worksheet.write(r, 3, stamp_end_date)
            worksheet.write(r, 4, str(element.client_tax_identification_number))
            worksheet.write(r, 5, str(element.client_name))
            worksheet.write(r, 6, element.total_tax10)
            worksheet.write(r, 7, element.total_tax5)
            worksheet.write(r, 8, element.total_exempt)
            worksheet.write(r, 9, element.invoice_total)
            # calculo del total se realiza por formula en Excel.

            worksheet.write(r, 10, "GS")
            worksheet.write(r, 11, str(element.payment_term))
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('abaco_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response
