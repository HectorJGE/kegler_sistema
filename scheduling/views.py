from itertools import chain
import pytz
import io

from auditlog.models import LogEntry
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DetailView
from django.views.generic.base import View
from easy_pdf.rendering import render_to_pdf, make_response
from xlsxwriter import Workbook
from base.models import Currency
from clinic.forms import PatientForm
from clinic.models import MedicalEquipment, Doctor, Patient, TreatingDoctor
from scheduling.forms import AppointmentCreateForm, AppointmentUpdateForm, CalendarFiltersForm, \
    AppointmentReportFiltersForm, AppointmentsOfTheDayReportFiltersForm, AppointmentDocumentFormSet
from scheduling.models import Appointment, AppointmentState, AppointmentStateUserLog, Schedule, AppointmentDocument
from django.http import JsonResponse
import datetime
from django.http.response import HttpResponse, HttpResponseServerError
from django.utils.translation import gettext as _

import json

from reportbro import Report, ReportBroError


from reports.models import ReportDefinition

import pytz

MAX_CACHE_SIZE = 1000 * 1024 * 1024  # keep max. 1000 MB of generated pdf files in db


# Appointment
# Appointment Calendar View
class AppointmentCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'appointments/appointment_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipments = MedicalEquipment.objects.all().exclude(sector__sector_code='ECO')
        doctors = Doctor.objects.filter(sectors__sector_code='ECO')
        # equipments_and_doctors = list(chain(equipments, doctors))

        if self.request.GET.get('event_datetime'):
            event_datetime = self.request.GET['event_datetime']
        else:
            event_datetime = None

        if self.request.GET.get('event_id'):
            event_id = self.request.GET['event_id']
        else:
            event_id = None

        context.update({
            'calendar_filters_form': CalendarFiltersForm(),
            'equipments': equipments,
            'doctors': doctors,
            'event_datetime': event_datetime,
            'event_id': event_id
        })
        return context


# Appointment List
class AppointmentListView(LoginRequiredMixin, ListView):
    template_name = 'appointments/appointment_list.html'
    context_object_name = "appointments"
    model = Appointment
    ordering = ['-appointment_date_start']

    def get_queryset(self):
        queryset = []
        form = AppointmentReportFiltersForm(self.request.GET)

        if self.request.GET.get('date_time_start') and self.request.GET.get('date_time_end'):
            if form.is_valid():
                start = form.cleaned_data.get('date_time_start')
                end = form.cleaned_data.get('date_time_end')
                queryset = Appointment.objects.filter(appointment_date_start__range=[start, end])

                insurance_plan = form.cleaned_data.get('insurance_plan', None)
                medical_study = form.cleaned_data.get('medical_study', None)
                medical_equipment = form.cleaned_data.get('medical_equipment', None)
                doctor = form.cleaned_data.get('doctor', None)
                treating_doctor = form.cleaned_data.get('treating_doctor', None)
                appointment_state = form.cleaned_data.get('appointment_state', None)
                sector = form.cleaned_data.get('sector', None)
                user = form.cleaned_data.get('user', None)

                if insurance_plan:
                    queryset = queryset.filter(insurance_plan=insurance_plan)

                if medical_study:
                    queryset = queryset.filter(medical_study=medical_study)

                if medical_equipment:
                    queryset = queryset.filter(medical_equipment=medical_equipment)

                if doctor:
                    queryset = queryset.filter(doctor=doctor)

                if treating_doctor:
                    queryset = queryset.filter(treating_doctor=treating_doctor)

                if appointment_state:
                    queryset = queryset.filter(appointment_state=appointment_state)

                if sector:
                    queryset = queryset.filter(medical_study__sector=sector)

                if user:
                    user_state_logs = AppointmentStateUserLog.objects.filter(
                        state_log_datetime__range=[start, end],
                        appointment_state_id=1,
                        user=user
                        )
                    queryset = queryset.filter(id__in=[user_state_logs.values_list('appointment_id')])

        else:
            if self.request.GET.get('insurance_plan') \
                    or self.request.GET.get('medical_study') or self.request.GET.get('medical_equipment') \
                    or self.request.GET.get('doctor') or self.request.GET.get('treating_doctor') \
                    or self.request.GET.get('appointment_state'):
                if form.is_valid():
                    queryset = Appointment.objects.all()
                    insurance_plan = form.cleaned_data.get('insurance_plan', None)
                    medical_study = form.cleaned_data.get('medical_study', None)
                    medical_equipment = form.cleaned_data.get('medical_equipment', None)
                    doctor = form.cleaned_data.get('doctor', None)
                    treating_doctor = form.cleaned_data.get('treating_doctor', None)
                    appointment_state = form.cleaned_data.get('appointment_state', None)
                    sector = form.cleaned_data.get('sector', None)
                    user = form.cleaned_data.get('user', None)

                    if insurance_plan:
                        queryset = queryset.filter(insurance_plan=insurance_plan)

                    if medical_study:
                        queryset = queryset.filter(medical_study=medical_study)

                    if medical_equipment:
                        queryset = queryset.filter(medical_equipment=medical_equipment)

                    if doctor:
                        queryset = queryset.filter(doctor=doctor)

                    if treating_doctor:
                        queryset = queryset.filter(treating_doctor=treating_doctor)

                    if appointment_state:
                        queryset = queryset.filter(appointment_state=appointment_state)

                    if sector:
                        queryset = queryset.filter(mecical_study__sector=sector)

                    if user:
                        user_state_logs = AppointmentStateUserLog.objects.filter(
                            user=user,
                            appointment_state_id=1
                        )
                        queryset = queryset.filter(id__in=user_state_logs.values_list('appointment_id'))

        return queryset

    def get(self, request, *args, **kwargs):
        form = AppointmentReportFiltersForm(self.request.GET)
        if form.is_valid():
            filters = []
            start = form.cleaned_data.get('date_time_start')
            end = form.cleaned_data.get('date_time_end')
            insurance_plan = form.cleaned_data.get('insurance_plan', None)
            medical_study = form.cleaned_data.get('medical_study', None)
            medical_equipment = form.cleaned_data.get('medical_equipment', None)
            doctor = form.cleaned_data.get('doctor', None)
            treating_doctor = form.cleaned_data.get('treating_doctor', None)
            appointment_state = form.cleaned_data.get('appointment_state', None)
            sector = form.cleaned_data.get('sector', None)
            user = form.cleaned_data.get('user', None)

            if insurance_plan:
                report_filter = {
                    'name': _('Insurance Plan'),
                    'value': str(insurance_plan)
                }
                filters.append(report_filter)

            if medical_study:
                report_filter = {
                    'name': _('Medical study'),
                    'value': str(medical_study)
                }
                filters.append(report_filter)

            if medical_equipment:
                report_filter = {
                    'name': _('Medical Equipment'),
                    'value': str(medical_equipment)
                }
                filters.append(report_filter)

            if doctor:
                report_filter = {
                    'name': _('Doctor'),
                    'value': str(doctor)
                }
                filters.append(report_filter)

            if treating_doctor:
                report_filter = {
                    'name': _('Treating Doctor'),
                    'value': str(treating_doctor)
                }
                filters.append(report_filter)

            if appointment_state:
                report_filter = {
                    'name': _('Appointment State'),
                    'value': str(appointment_state)
                }
                filters.append(report_filter)

            if sector:
                report_filter = {
                    'name': _('Sector'),
                    'value': str(sector)
                }
                filters.append(report_filter)

            if user:
                report_filter = {
                    'name': _('User'),
                    'value': str(user)
                }
                filters.append(report_filter)

            elements = self.get_queryset()
            report_type = form.cleaned_data.get('report_type')

            if elements and report_type == str(AppointmentReportFiltersForm.EXCEL_TYPE):
                return self.export_excel(elements)

            elif elements and report_type == str(AppointmentReportFiltersForm.PDF_TYPE):
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

        if self.request.GET.get('medical_study'):
            initial['medical_study'] = self.request.GET.get('medical_study')

        if self.request.GET.get('medical_equipment'):
            initial['medical_equipment'] = self.request.GET.get('medical_equipment')

        if self.request.GET.get('doctor'):
            initial['doctor'] = self.request.GET.get('doctor')

        if self.request.GET.get('treating_doctor'):
            initial['treating_doctor'] = self.request.GET.get('treating_doctor')

        if self.request.GET.get('appointment_state'):
            initial['appointment_state'] = self.request.GET.get('appointment_state')

        if self.request.GET.get('sector'):
            initial['sector'] = self.request.GET.get('sector')

        if self.request.GET.get('user'):
            initial['user'] = self.request.GET.get('user')

        filter_form = AppointmentReportFiltersForm(initial=initial)
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
            'Fecha Hora Inicio',
            'Fecha Hora Fin',
            'Paciente',
            'Contacto',
            'Seguro',
            'Estudio',
            'Equipo',
            'Doctor',
            'Doctor Tratante',
            'Estado',
            'Sector',
            'Observaciones'
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            # worksheet.write(r, 0, element.id)
            start_date = timezone.localtime(element.appointment_date_start)
            end_date = timezone.localtime(element.appointment_date_end)
            worksheet.write(r, 1, start_date.strftime("%d/%m/%Y %H:%M"))
            worksheet.write(r, 2, end_date.strftime("%d/%m/%Y %H:%M"))
            worksheet.write(r, 3, str(element.patient))
            worksheet.write(r, 4, str(element.patient.phone_number) + " \n" + str(element.patient.email))
            worksheet.write(r, 5, str(element.insurance_plan))
            worksheet.write(r, 6, str(element.medical_study))
            worksheet.write(r, 7, str(element.medical_equipment))
            worksheet.write(r, 8, str(element.doctor))
            worksheet.write(r, 9, str(element.treating_doctor))
            worksheet.write(r, 10, str(element.appointment_state))
            worksheet.write(r, 11, str(element.medical_study.sector))
            worksheet.write(r, 12, str(element.observations))
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('appointments_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response

    def export_pdf(self, elements, start, end, filters):
        final_list = []
        elements = elements.order_by('appointment_date_start')

        for element in elements:
            time_start = utc_to_local(element.appointment_date_start)
            time_end = utc_to_local(element.appointment_date_end)
            time_range = time_start.strftime("%H:%M") + "-" + time_end.strftime("%H:%M")
            if element.patient.insurance_plan:
                insurance_plan = element.patient.insurance_plan.name
            else:
                insurance_plan = None
            new_list_element = {
                'time_range': time_range,
                'patient': element.patient.name + " " + element.patient.last_name,
                'patient_phone_number': element.patient.phone_number,
                'insurance_plan': insurance_plan,
                'medical_study': element.medical_study.name,
                'observations': element.observations
            }
            final_list.append(new_list_element)

        file_name = _('appointments_list_report')
        report_title = _('Appointments List Report')

        # NOTE: these params must match exactly with the parameters defined in the
        # report definition in ReportBro Designer, check the name and type (Number, Date, List, ...)
        # of those parameters in the Designer.
        params = dict(
            appointments=final_list,
            filters=filters,
            start=start,
            end=end,
            report_title=report_title,
            current_date=datetime.datetime.now()
        )

        report_definition = ReportDefinition.objects.get(report_type='appointments_list_report')
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
            response['Content-Disposition'] = 'inline; filename="{filename}"'.format(filename=file_name+'.pdf')
            return response
        except ReportBroError as ex:
            return HttpResponseServerError('report error: ' + str(ex.error))
        except Exception as ex:
            return HttpResponseServerError('report exception: ' + str(ex))


# Appointment Detail
class AppointmentDetailView(LoginRequiredMixin, DetailView):
    template_name = 'appointments/appointment_detail.html'
    model = Appointment
    context_object_name = 'appointment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        audit_log_entries = LogEntry.objects.filter(object_id=self.object.id, content_type_id=31)
        context['audit_log_entries'] = audit_log_entries
        return context


# Appointment List For Calendar View (JSON)
class AppointmentListForCalendarView(LoginRequiredMixin, ListView):
    model = Appointment
    context_object_name = 'appointments'

    def get_queryset(self):
        start = datetime.datetime.strptime(self.request.GET['start'], "%Y-%m-%dT%H:%M:%S%z")
        end = datetime.datetime.strptime(self.request.GET['end'], "%Y-%m-%dT%H:%M:%S%z")

        queryset = Appointment.objects.filter(
            appointment_date_start__gte=start,
            appointment_date_end__lte=end,
            appointment_state__state_code__in=[AppointmentState.SCHEDULED_STATE, AppointmentState.FILED_STATE]
        )
        if self.request.GET.get('study_id'):
            queryset = queryset.filter(
                medical_study_id=self.request.GET.get('study_id')
            )

        if self.request.GET.get('equipment_id'):
            queryset = queryset.filter(
                medical_equipment_id=self.request.GET.get('equipment_id')
            )

        if self.request.GET.get('doctor_id'):
            queryset = queryset.filter(
                doctor_id=self.request.GET.get('doctor_id')
            )

        return queryset

    def get(self, request, *args, **kwargs):
        appointments_json_list = []
        appointments = self.get_queryset()
        for appointment in appointments:
            if appointment.medical_equipment:
                if appointment.medical_equipment.tag_color:
                    color = appointment.medical_equipment.tag_color
                else:
                    color = '#FF0000'
            else:
                if appointment.doctor.tag_color:
                    color = appointment.doctor.tag_color
                else:
                    color = '#FF0000'
            appointment_json = {
                'id': appointment.id,
                'title': appointment.patient.name + " " + appointment.patient.last_name + " - " +
                         str(appointment.medical_study) + " - " + str(appointment.insurance_plan) +
                         " - " + appointment.observations,
                'start': str(appointment.appointment_date_start),
                'end': str(appointment.appointment_date_end),
                'color': color
            }
            appointments_json_list.append(appointment_json)
        data = appointments_json_list
        return JsonResponse(data, status=200, safe=False)


# Appointment Create View
class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    template_name = 'appointments/appointment_create.html'
    form_class = AppointmentCreateForm

    def get_initial(self):
        scheduled_state = AppointmentState.objects.get(name='Agendado')
        currency = Currency.objects.get(name='Guarani')
        initial = {
            'appointment_state':  scheduled_state,
            'currency': currency
        }
        return initial

    def post(self, request, *args, **kwargs):
        return super(AppointmentCreateView, self).post(request)

    def get_context_data(self, **kwargs):
        context = super(AppointmentCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['documents_formset'] = AppointmentDocumentFormSet(self.request.POST, self.request.FILES)

        else:
            context['documents_formset'] = AppointmentDocumentFormSet()

        return context

    @transaction.atomic
    def form_valid(self, form):
        patient = form.cleaned_data['patient']
        # New Patient
        context = self.get_context_data()
        documents_formset = context['documents_formset']

        if patient is None or patient == '':
            patient_data = {
                'name': form.cleaned_data['patient_name'],
                'last_name': form.cleaned_data['patient_last_name'],
                'sex': form.cleaned_data['patient_sex'],
                'weight': form.cleaned_data['patient_weight'],
                'birth_date': form.cleaned_data['patient_birth_date'],
                'document_number': form.cleaned_data['patient_document_number'],

                # invoicing
                'tax_identification_number': form.cleaned_data['patient_tax_id_number'],
                'tax_identification_name': form.cleaned_data['patient_tax_id_name'],
                'phone_number': form.cleaned_data['contact_number'],
                'email': form.cleaned_data['contact_email'],
                'address': form.cleaned_data['patient_address'],
                'is_taxpayer': form.cleaned_data['patient_is_taxpayer'],

                'city': form.cleaned_data['patient_city'],
                'insurance_plan': form.cleaned_data['insurance_plan']
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

                data = {
                    'errors': form_errors,
                }
                return JsonResponse(data, status=500, safe=False)

        else:
            # Updating patient
            patient.weight = form.cleaned_data['patient_weight']
            patient.city = form.cleaned_data['patient_city']

            # invoicing
            patient.tax_identification_number = form.cleaned_data['patient_tax_id_number']
            patient.tax_identification_name = form.cleaned_data['patient_tax_id_name']
            patient.address = form.cleaned_data['patient_address']
            patient.phone_number = form.cleaned_data['contact_number']
            patient.email = form.cleaned_data['contact_email']
            patient.is_taxpayer = form.cleaned_data['patient_is_taxpayer']

            patient.insurance_plan = form.cleaned_data['insurance_plan']
            patient.save()
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

        if form.cleaned_data['estimated_cost'] == '':
            form.instance.estimated_cost = 0

        appointment = form.save()
        appointment.save()
        if documents_formset.is_valid():
            documents_formset.instance = appointment
            documents_formset.save()

        appointment_state_user_log = AppointmentStateUserLog.objects.create(
            appointment=appointment,
            appointment_state=appointment.appointment_state,
            user=self.request.user,
        )
        print(appointment_state_user_log)

        # Updating Patient fields
        patient = appointment.patient
        patient.phone_number = appointment.contact_number
        patient.email = appointment.contact_email
        patient.save()
        data = {
            'id': appointment.id,
            'title': str(appointment.patient),
            'start': str(appointment.appointment_date_start),
            'end': str(appointment.appointment_date_end)
        }

        return JsonResponse(data, status=200, safe=False)

    def form_invalid(self, form):
        errors = []
        for error in form.errors:
            errors.append(error)

        data = {
            'title': str(form.cleaned_data['patient']),
            'start': str(form.cleaned_data['appointment_date_start']),
            'end': str(form.cleaned_data['appointment_date_end']),
            'errors': errors
        }
        return JsonResponse(data, status=500, safe=False)


# Appointment Update View
class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    template_name = 'appointments/appointment_update.html'
    form_class = AppointmentUpdateForm

    def post(self, request, *args, **kwargs):
        return super(AppointmentUpdateView, self).post(request)

    def get_initial(self):
        patient = self.object.patient
        patient_name = str(self.object.patient)
        medical_study_name = str(self.object.medical_study)
        initial = {
            'patient_autocomplete': patient_name,
            'medical_study_autocomplete': medical_study_name,
            'patient_tax_id_number': patient.tax_identification_number,
            'patient_tax_id_name': patient.tax_identification_name,
            'patient_address': patient.address,
            'patient_is_taxpayer': patient.is_taxpayer
        }
        return initial

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        appointment = form.save()
        patient = appointment.patient
        # invoicing
        patient.address = form.cleaned_data['patient_address']
        patient.tax_identification_number = form.cleaned_data['patient_tax_id_number']
        patient.tax_identification_name = form.cleaned_data['patient_tax_id_name']
        patient.phone_number = appointment.contact_number
        patient.email = appointment.contact_email
        patient.is_taxpayer = form.cleaned_data['patient_is_taxpayer']

        patient.save()
        data = {
            'id': appointment.id,
            'title': str(appointment.patient),
            'start': str(appointment.appointment_date_start),
            'end': str(appointment.appointment_date_end)
        }

        documents_formset = context['documents_formset']
        if documents_formset.is_valid():
            documents_formset.instance = appointment
            documents_formset.save()

        return JsonResponse(data, status=200, safe=False)

    def form_invalid(self, form):
        data = {
            'title': str(form.cleaned_data['patient']),
            'start': str(form.cleaned_data['appointment_date_start']),
            'end': str(form.cleaned_data['appointment_date_end'])
        }
        return JsonResponse(data, status=500, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consultation_sheet = self.object.consultation_sheets.first()
        context.update({
            'consultation_sheet': consultation_sheet
        })
        if self.request.POST:
            context['documents_formset'] = AppointmentDocumentFormSet(self.request.POST, self.request.FILES, instance=self.get_object())

        else:
            context['documents_formset'] = AppointmentDocumentFormSet(instance=self.get_object())
        return context


# Appointment Cancel View
class AppointmentCancelView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        appointment_id = kwargs['pk']
        appointment = Appointment.objects.get(pk=appointment_id)
        cancel_state = AppointmentState.objects.get(state_code=AppointmentState.CANCELED_STATE)
        appointment.appointment_state = cancel_state
        appointment.save()

        appointment_state_user_log = AppointmentStateUserLog.objects.create(
            appointment=appointment,
            appointment_state=appointment.appointment_state,
            user=self.request.user,
        )
        print(appointment_state_user_log)

        data = {
            'success': True
        }
        return JsonResponse(data, status=200, safe=False)


# Check Equipment Availability View
class AppointmentCheckEquipmentAvailabilityView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        event_datetime_start = None
        event_datetime_end = None
        equipment_id = None

        if self.request.GET.get('event_datetime_start'):
            event_datetime_start = self.request.GET['event_datetime_start']

        if self.request.GET.get('event_datetime_end'):
            event_datetime_end = self.request.GET['event_datetime_end']

        if self.request.GET.get('equipment_id'):
            equipment_id = self.request.GET['equipment_id']

        try:
            start = datetime.datetime.strptime(event_datetime_start, "%d/%m/%Y %H:%M")
        except:
            start = datetime.datetime.strptime(event_datetime_start, "%d/%m/%Y %H:%M:%S")

        start = pytz.utc.localize(start)

        try:
            end = datetime.datetime.strptime(event_datetime_end, "%d/%m/%Y %H:%M")
        except:
            end = datetime.datetime.strptime(event_datetime_end, "%d/%m/%Y %H:%M:%S")

        end = pytz.utc.localize(end)
        equipment = MedicalEquipment.objects.get(pk=equipment_id)

        msg = ''

        appointments = Appointment.objects.filter(
            appointment_date_start__gte=start,
            appointment_date_end__lte=end,
            medical_equipment=equipment
        )

        if appointments:
            msg += 'ATENCION!!! Ya existen turnos con este equipo, en esta fecha, y en este rango de tiempo\n'
        data = {
            'msg': msg
        }
        return JsonResponse(data, status=200, safe=False)


# Check Doctor Availability View
class AppointmentCheckDoctorAvailabilityView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        event_datetime_start = None
        event_datetime_end = None
        doctor_id = None

        if self.request.GET.get('event_datetime_start'):
            event_datetime_start = self.request.GET['event_datetime_start']

        if self.request.GET.get('event_datetime_end'):
            event_datetime_end = self.request.GET['event_datetime_end']

        if self.request.GET.get('doctor_id'):
            doctor_id = self.request.GET['doctor_id']

        doctor = Doctor.objects.get(pk=doctor_id)
        msg = ''

        start = datetime.datetime.strptime(event_datetime_start, "%d/%m/%Y %H:%M")
        start = pytz.utc.localize(start)
        end = datetime.datetime.strptime(event_datetime_end, "%d/%m/%Y %H:%M")
        end = pytz.utc.localize(end)

        print(start.strftime("%d/%m/%Y %H:%M"))
        print(end.strftime("%d/%m/%Y %H:%M"))

        week_start_date = start - datetime.timedelta(days=start.weekday())
        week_end_date = week_start_date + datetime.timedelta(days=6)

        # Busqueda del calendario de la semana del doctor
        doctor_schedules_this_week = Schedule.objects.filter(
            schedule_date__range=[week_start_date, week_end_date],
            doctor=doctor
        )

        dentro_del_rango = False
        # Si NO encuentra el calendario de la semana
        if not doctor_schedules_this_week:
            msg += 'ATENCION!!! El doctor seleccionado, no tiene calendarizada su atención en este semana.\n ' \
                   'Puede continuar con el agendamiento del turno, pero con el riesgo de que el doctor asignado no esté disponible en el día y horario agendado.'
        else:
            # Si Encuentra el calendario de la semana, busca entre estos el del día específico
            doctor_schedules = doctor_schedules_this_week.filter(schedule_date=start.date())

            # Si encuentra el calendario del día
            if doctor_schedules:

                for doctor_schedule in doctor_schedules:
                    # Si Hay un clendario del doctor dentro del rango buscado
                    if start.time() >= doctor_schedule.start_time and end.time() <= doctor_schedule.end_time:
                        print('Dentro del rango')
                        dentro_del_rango = True

                    # Si NO hay un calendario del doctor dentro del rango buscado
                    else:
                        msg += 'ATENCION!!! El doctor seleccionado, no tiene calendarizada su atención en este rango horario.\n' \
                               'Puede continuar con el agendamiento del turno, pero con el riesgo de que el doctor asignado no esté disponible en el horario agendado.\n'
                        msg += 'Los horarios encontrados de este doctor en esta semana son:\n'
                        for schedule in doctor_schedules_this_week:
                            msg += str(schedule) + '\n'

            # Si NO encuentra el calendario del día
            else:
                msg += 'ATENCION!!! El doctor seleccionado, no tiene calendarizada su atención en este día.\n' \
                       'Puede continuar con el agendamiento del turno, pero con el riesgo de que el doctor asignado no esté disponible en el día y horario agendado.\n'
                msg += 'Los horarios encontrados de este doctor en esta semana son:\n'
                for schedule in doctor_schedules_this_week:
                    msg += str(schedule) + '\n'

        # Busca también si hay turnos de ese doctor en esa fecha y en ese rango horario
        appointments = Appointment.objects.filter(
            appointment_date_start__gte=start,
            appointment_date_end__lte=end,
            doctor=doctor
        )

        if dentro_del_rango:
            msg = ''

        if appointments:
            msg += 'ATENCION!!! Ya existen turnos con este doctor en este horario\n ' \
                   'Puede continuar con el agendamiento, pero con el riesgo de que el doctor asignado esté realizando otro estudio en ese preciso momento.\n'

        data = {
            'msg': msg
        }
        return JsonResponse(data, status=200, safe=False)


# Appointments of the day
class AppointmentsOfTheDayListView(LoginRequiredMixin, ListView):
    template_name = 'appointments/appointments_of_the_day_list.html'
    context_object_name = "appointments"
    model = Appointment
    ordering = ['-appointment_date_start']

    def get_queryset(self):
        queryset = []
        form = AppointmentsOfTheDayReportFiltersForm(self.request.GET)

        if form.is_valid():
            start = form.cleaned_data.get('date')
            # start = start + datetime.timedelta(hours=6)
            end = form.cleaned_data.get('date')
            end = end.replace(hour=0, minute=0)
            end = end + datetime.timedelta(hours=23, minutes=45)

            pending_state = AppointmentState.objects.get(state_code=AppointmentState.SCHEDULED_STATE)
            filed_state = AppointmentState.objects.get(state_code=AppointmentState.FILED_STATE)

            queryset = Appointment.objects.filter(
                appointment_date_start__range=[start, end],
                appointment_state__in=[pending_state, filed_state]
            ).order_by('appointment_date_start')

            medical_equipment = form.cleaned_data.get('medical_equipment', None)
            doctor = form.cleaned_data.get('doctor', None)

            if medical_equipment:
                queryset = queryset.filter(medical_equipment=medical_equipment)

            if doctor:
                queryset = queryset.filter(doctor=doctor)

        return queryset

    def get(self, request, *args, **kwargs):
        form = AppointmentsOfTheDayReportFiltersForm(self.request.GET)
        if form.is_valid():
            filters = []
            start = form.cleaned_data.get('date')
            # start = start + datetime.timedelta(hours=6)
            end = form.cleaned_data.get('date')
            end = end.replace(hour=0, minute=0)
            end = end + datetime.timedelta(hours=23, minutes=45)

            time_interval = form.cleaned_data.get('time_interval')

            medical_equipment = form.cleaned_data.get('medical_equipment', None)
            doctor = form.cleaned_data.get('doctor', None)

            if medical_equipment:
                report_filter = {
                    'name': _('Medical Equipment'),
                    'value': str(medical_equipment)
                }
                filters.append(report_filter)

            if doctor:
                report_filter = {
                    'name': _('Doctor'),
                    'value': str(doctor)
                }
                filters.append(report_filter)

            elements = self.get_queryset()
            report_type = form.cleaned_data.get('report_type')

            if elements and report_type == str(AppointmentsOfTheDayReportFiltersForm.EXCEL_TYPE):
                return self.export_excel(elements)

            elif elements and report_type == str(AppointmentsOfTheDayReportFiltersForm.PDF_TYPE):
                return self.export_pdf(elements, start, end, filters, time_interval)

            else:
                return super().get(self, request, *args, **kwargs)

        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}

        if self.request.GET.get('date'):
            initial['date'] = self.request.GET.get('date')
        else:
            now = datetime.datetime.now()
            inicio = datetime.datetime(year=now.year,
                                       month=now.month,
                                       day=now.day,
                                       hour=1,
                                       minute=0,
                                       second=0)

            inicio = timezone.make_aware(inicio)

            initial['date'] = inicio

        if self.request.GET.get('medical_equipment'):
            initial['medical_equipment'] = self.request.GET.get('medical_equipment')

        if self.request.GET.get('doctor'):
            initial['doctor'] = self.request.GET.get('doctor')

        if self.request.GET.get('time_interval'):
            initial['time_interval'] = self.request.GET.get('time_interval')

        filter_form = AppointmentsOfTheDayReportFiltersForm(initial=initial)
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
            'Fecha Hora Inicio',
            'Fecha Hora Fin',
            'Paciente',
            'Contacto',
            'Seguro',
            'Estudio',
            'Equipo',
            'Doctor',
            'Doctor Tratante',
            'Estado',
            'Sector',
            'Observaciones'
        ]

        for header in table_headers:
            worksheet.write(r, c, header)
            c += 1

        r += 1

        for element in elements:
            # worksheet.write(r, 0, element.id)
            start_date = timezone.localtime(element.appointment_date_start)
            end_date = timezone.localtime(element.appointment_date_end)
            worksheet.write(r, 1, start_date.strftime("%d/%m/%Y %H:%M"))
            worksheet.write(r, 2, end_date.strftime("%d/%m/%Y %H:%M"))
            worksheet.write(r, 3, str(element.patient))
            worksheet.write(r, 4, str(element.patient.phone_number) + "\n" + str(element.patient.email))
            worksheet.write(r, 5, str(element.insurance_plan))
            worksheet.write(r, 6, str(element.medical_study))
            worksheet.write(r, 7, str(element.medical_equipment))
            worksheet.write(r, 8, str(element.doctor))
            worksheet.write(r, 9, str(element.treating_doctor))
            worksheet.write(r, 10, str(element.appointment_state))
            worksheet.write(r, 11, str(element.medical_study.sector))
            worksheet.write(r, 12, str(element.observations))
            r += 1

        workbook.close()
        output.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response = HttpResponse(output.read(), content_type=content_type)
        file_name = _('appointments_report')
        response['Content-Disposition'] = "attachment; filename=" + file_name + ".xlsx"
        return response

    def export_pdf(self, elements, start, end, filters, time_interval):
        this_day = start
        list_elements = []
        list_elements_15_min = []
        list_elements_20_min = []
        list_elements_30_min = []

        # 15 min
        if time_interval == '15':
            last_date = this_day
            initial_date = last_date
            time_to_next_day = time_until_end_of_day(initial_date) - datetime.timedelta(hours=1, minutes=15)
            # time_to_next_day = datetime.timedelta(hours=17, minutes=45)
            while last_date <= initial_date + time_to_next_day:
                if last_date.hour == 6 and last_date.minute == 0:
                    time_dictionary = {
                        'range_start': last_date,
                    }
                else:
                    time_dictionary = {
                        'range_start': last_date + datetime.timedelta(seconds=1),
                    }
                last_date = last_date + datetime.timedelta(minutes=15)
                time_dictionary['range_end'] = last_date

                time_range_start = time_dictionary['range_start']
                time_range_start_str = time_range_start.strftime("%H:%M")

                time_range_end = time_dictionary['range_end']
                time_range_end_str = time_range_end.strftime("%H:%M")

                time_dictionary['time_range'] = time_range_start_str + " - " + time_range_end_str

                list_elements_15_min.append(time_dictionary)
            list_elements = list_elements_15_min

        # 20 min
        if time_interval == '20':
            last_date = this_day
            initial_date = last_date
            time_to_next_day = time_until_end_of_day(initial_date) - datetime.timedelta(hours=1, minutes=15)
            # time_to_next_day = datetime.timedelta(hours=17, minutes=45)
            while last_date <= initial_date + time_to_next_day:
                if last_date.hour == 6 and last_date.minute == 0:
                    time_dictionary = {
                        'range_start': last_date,
                    }
                else:
                    time_dictionary = {
                        'range_start': last_date + datetime.timedelta(seconds=1),
                    }
                last_date = last_date + datetime.timedelta(minutes=20)
                time_dictionary['range_end'] = last_date

                time_range_start = time_dictionary['range_start']
                time_range_start_str = time_range_start.strftime("%H:%M")

                time_range_end = time_dictionary['range_end']
                time_range_end_str = time_range_end.strftime("%H:%M")

                time_dictionary['time_range'] = time_range_start_str + " - " + time_range_end_str

                list_elements_20_min.append(time_dictionary)
            list_elements = list_elements_20_min

        # 30 min
        if time_interval == '30':
            last_date = this_day
            initial_date = last_date
            time_to_next_day = time_until_end_of_day(initial_date) - datetime.timedelta(hours=1, minutes=15)
            # time_to_next_day = datetime.timedelta(hours=17, minutes=45)
            while last_date <= initial_date + time_to_next_day:
                if last_date.hour == 6 and last_date.minute == 0:
                    time_dictionary = {
                        'range_start': last_date,
                    }
                else:
                    time_dictionary = {
                        'range_start': last_date + datetime.timedelta(seconds=1),
                    }
                last_date = last_date + datetime.timedelta(minutes=30)
                time_dictionary['range_end'] = last_date

                time_range_start = time_dictionary['range_start']
                time_range_start_str = time_range_start.strftime("%H:%M")

                time_range_end = time_dictionary['range_end']
                time_range_end_str = time_range_end.strftime("%H:%M")

                time_dictionary['time_range'] = time_range_start_str + " - " + time_range_end_str

                list_elements_30_min.append(time_dictionary)
            list_elements = list_elements_30_min

        final_list = []

        i = 0
        # Time range
        for list_element in list_elements:
            final_list.append(list_element)

            # Appointments
            for element in elements:
                appointment_date_start = element.appointment_date_start + datetime.timedelta(seconds=1)
                appointment_date_start = utc_to_local(appointment_date_start)
                appointment_date_start_str = appointment_date_start.strftime("%H:%M")
                appointment_date_end = element.appointment_date_end
                appointment_date_end = utc_to_local(appointment_date_end)
                appointment_date_end_str = appointment_date_end.strftime("%H:%M")
                appointment_time_range_str = "(" + appointment_date_start_str + " - " + appointment_date_end_str + ")"

                time_range_start = list_element['range_start']
                time_range_end = list_element['range_end']

                if element.insurance_plan:
                    insurance_plan_name = element.insurance_plan.name
                else:
                    insurance_plan_name = "Sin Seguro"

                # If appointment start time is within time range
                if time_range_start <= appointment_date_start <= time_range_end:
                    if 'patient' in list_element:

                        new_list_element = {
                            'range_start': list_elements[i]['range_start'],
                            'range_end': list_elements[i]['range_end'],
                            'time_range': list_elements[i]['time_range'],
                            'patient': appointment_time_range_str + " " + element.patient.name + " " + element.patient.last_name,
                            'patient_phone_number': element.patient.phone_number,
                            'insurance_plan': insurance_plan_name,
                            'medical_study': element.medical_study.name,
                            'observations': element.observations
                        }
                        final_list.append(new_list_element)

                    else:
                        list_elements[i]['time_range'] = list_element['time_range']
                        list_elements[i]['patient'] = appointment_time_range_str + " " + element.patient.name + " " + element.patient.last_name  # + " - " + appointment_date_start_str + " al " + appointment_date_end_str
                        list_elements[i]['patient_phone_number'] = element.patient.phone_number
                        list_elements[i]['insurance_plan'] = insurance_plan_name
                        list_elements[i]['medical_study'] = element.medical_study.name
                        list_elements[i]['observations'] = element.observations

                    if appointment_date_end > time_range_end:
                        new_list_element = {
                            'range_start': list_elements[i+1]['range_start'],
                            'range_end': list_elements[i+1]['range_end'],
                            'time_range': list_elements[i+1]['time_range'],
                            'patient': appointment_time_range_str + " " + element.patient.name + " " + element.patient.last_name,
                            'patient_phone_number': element.patient.phone_number,
                            'insurance_plan': insurance_plan_name,
                            'medical_study': element.medical_study.name,
                            'observations': element.observations
                        }
                        final_list.append(new_list_element)

                        if appointment_date_end > list_elements[i+1]['range_end']:
                            new_list_element = {
                                'range_start': list_elements[i+2]['range_start'],
                                'range_end': list_elements[i+2]['range_end'],
                                'time_range': list_elements[i+2]['time_range'],
                                'patient': appointment_time_range_str + " " + element.patient.name + " " + element.patient.last_name,
                                'patient_phone_number': element.patient.phone_number,
                                'insurance_plan': insurance_plan_name,
                                'medical_study': element.medical_study.name,
                                'observations': element.observations
                            }
                            final_list.append(new_list_element)
            i += 1

        file_name = _('appointments_of_the_day_report')
        report_title = _('Appointments of the Day Report')

        # NOTE: these params must match exactly with the parameters defined in the
        # report definition in ReportBro Designer, check the name and type (Number, Date, List, ...)
        # of those parameters in the Designer.
        params = dict(
            appointments=final_list,
            filters=filters,
            start=start,
            end=end,
            report_title=report_title,
            current_date=datetime.datetime.now()
        )

        report_definition = ReportDefinition.objects.get(report_type='appointments_of_the_day_report')
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
            response['Content-Disposition'] = 'inline; filename="{filename}"'.format(filename=file_name+'.pdf')
            return response
        except ReportBroError as ex:
            return HttpResponseServerError('report error: ' + str(ex.error))
        except Exception as ex:
            return HttpResponseServerError('report exception: ' + str(ex))


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def time_until_end_of_day(dt=None):
    # type: (datetime.datetime) -> datetime.timedelta
    """
    Get timedelta until end of day on the datetime passed, or current time.
    """
    if dt is None:
        dt = datetime.datetime.now()
    tomorrow = dt + datetime.timedelta(days=1)
    delta = tomorrow - dt
    # return datetime.datetime.combine(tomorrow, datetime.time.min) - dt
    return delta


# Appointment Document Print View
class AppointmentDocumentPrintView(LoginRequiredMixin, TemplateView):
    template_name = "appointments/appointment_document_print.html"

    def get_context_data(self, **kwargs):
        context = super(AppointmentDocumentPrintView, self).get_context_data(**kwargs)
        appointment_document = AppointmentDocument.objects.get(pk=kwargs['pk'])
        context.update(
            {
                'appointment_document': appointment_document,
            }
        )
        return context