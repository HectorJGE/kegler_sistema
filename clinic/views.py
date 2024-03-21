from datatableview import Datatable, columns
from datatableview.views import DatatableView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Value
from django.db.models.functions import Concat
from django.db.models.query_utils import Q
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from clinic.forms import PatientForm
from clinic.models import Patient, MedicalStudy, MedicalEquipment, MedicalEquipmentType, Doctor, DoctorMedicalStudy, InsurancePlanMedicalStudyFee, InsurancePlan, MedicalStudyInsuranceAgreement, Sector
from scheduling.models import Appointment, AppointmentState
from django.utils.translation import ugettext_lazy as _
import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

# Create your views here.
# Patient
# Patient List
class PatientListView(LoginRequiredMixin, ListView):
    template_name = 'patient/patient_list.html'
    context_object_name = "patients"
    model = Patient


class PatientDatatable(Datatable):
    actions = columns.DisplayColumn(_('Actions'), processor='get_actions')
    birth_date = columns.DisplayColumn(_('Birth date'), processor='get_birth_date')
    insurance_plan = columns.DisplayColumn(_('Insurance'), source='insurance_plan')
    sex = columns.DisplayColumn(_('Sex'), processor='get_sex')
    city = columns.DisplayColumn(_('City'), processor='get_city')

    class Meta:
        model = Patient
        columns = ['actions', 'id', 'name', 'last_name', 'document_number', 'tax_identification_name',
                   'tax_identification_number', 'email', 'sex', 'weight', 'phone_number', 'email', 'birth_date',
                   'city', 'address', 'insurance_plan']
        search_fields = ['id',
                         'name', 'last_name', 'document_number',
                         'insurance_plan__name',
                         ]
        structure_template = "datatableview/bootstrap_structure.html"
        ordering = ['-id']

    @staticmethod
    def get_actions(instance, view, *args, **kwargs):
        rid = int(instance.pk)
        detail_url = reverse('patient.detail', args=[rid])
        update_url = reverse('patient.update', args=[rid])
        delete_url = reverse('patient.delete', args=[rid])
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
    def get_birth_date(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        return datetime.datetime.strftime(instance.birth_date, '%d/%m/%Y')

    @staticmethod
    def get_sex(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        return instance.get_sex_display()

    @staticmethod
    def get_city(instance, view, *args, **kwargs):  # pylint: disable=unused-argument
        return instance.get_city_display()


class PatientDataTableView(PermissionRequiredMixin, DatatableView):
    model = Patient
    datatable_class = PatientDatatable
    template_name = 'patient/patient_list_datatable.html'
    permission_required = 'clinic.view_patient'
    permission_denied_message = 'No tienes los permisos requeridos'

    def get_login_url(self):
        return reverse('dashboard')

    def handle_no_permission(self):
        try:
            return super(PatientDataTableView, self).handle_no_permission()
        except PermissionDenied as e:
            messages.error(self.request, e)
            return redirect(self.get_login_url())


# Patient Detail
class PatientDetailView(LoginRequiredMixin, DetailView):
    template_name = 'patient/patient_detail.html'
    model = Patient
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super(PatientDetailView, self).get_context_data(**kwargs)
        filed_state = AppointmentState.objects.get(state_code=AppointmentState.FILED_STATE)
        context['appointments'] = Appointment.objects\
            .filter(patient=self.object)\
            .exclude(appointment_state=filed_state)\
            .order_by('-appointment_date_start')
        return context


# Patient Detail Json
class PatientDetailJsonView(LoginRequiredMixin, DetailView):
    model = Patient

    def get(self, request, *args, **kwargs):
        patient_id = kwargs['pk']
        patient = Patient.objects.get(pk=patient_id)
        data = patient.tojson()
        return JsonResponse(data, status=200, safe=False)


# Patient Update
class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patient/patient_update_form.html'

    def get_success_url(self):
        return reverse('patient.detail', kwargs={'pk': self.object.pk})


# Patient Create
class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patient/patient_create_form.html'

    def get_success_url(self):
        return reverse('patient.detail', kwargs={'pk': self.object.pk})


# Patient Delete
class PatientDeleteView(LoginRequiredMixin, DeleteView):
    model = Patient
    template_name = "patient/patient_delete_confirm.html"

    def get_success_url(self):
        return reverse('patient.list')


# Medical Study Detail (JSON))
class MedicalStudyDetailJsonView(LoginRequiredMixin, DetailView):
    model = MedicalStudy

    def get(self, request, *args, **kwargs):
        medical_study_id = kwargs['pk']
        medical_study = MedicalStudy.objects.get(pk=medical_study_id)
        insurance_plan_id = request.GET.get('insurance_plan_id')
        insurance_plan = None
        if insurance_plan_id == '' or insurance_plan_id is None:
            insurance_plan_medical_study_fee = None
        else:
            insurance_plan = InsurancePlan.objects.get(pk=insurance_plan_id)
            insurance_plan_medical_study_fee = InsurancePlanMedicalStudyFee.objects.filter(medical_study=medical_study, insurance_plan=insurance_plan).first()

        if insurance_plan_medical_study_fee:
            medical_study_insurance_agreement = MedicalStudyInsuranceAgreement.objects.filter(insurance_plan=insurance_plan, medical_study=medical_study).first()
            agreement_id = None
            insurance_coverage_percent = 0
            insurance_coverage_amount = 0
            study_cover_type = 0
            if medical_study_insurance_agreement:
                agreement_id = medical_study_insurance_agreement.id
                study_cover_type = medical_study_insurance_agreement.cover_type
                insurance_coverage_percent = medical_study_insurance_agreement.coverage_percentage
                insurance_coverage_amount = medical_study_insurance_agreement.coverage_amount
            data = {
                'id': medical_study.id,
                'price': insurance_plan_medical_study_fee.price,
                'duration_in_minutes': insurance_plan_medical_study_fee.medical_study.duration_in_minutes,
                'sector_code': medical_study.sector.sector_code,
                'insurance_agreement_id': agreement_id,
                'study_cover_type': study_cover_type,
                'insurance_coverage_percent': insurance_coverage_percent,
                'insurance_coverage_amount': insurance_coverage_amount,
            }
            return JsonResponse(data, status=200, safe=False)
        else:
            data = {
                'id': medical_study.id,
                'price': 0.0,
                'duration_in_minutes': medical_study.duration_in_minutes,
                'sector_code': medical_study.sector.sector_code,
                'insurance_agreement_id': None,
                'study_cover_type': 0,
                'insurance_coverage_percent': 0,
                'insurance_coverage_amount': 0,

            }
            return JsonResponse(data, status=200, safe=False)


# Medical Study Autocomplete Detail (JSON))
class MedicalStudyAutocompleteDetailJsonView(LoginRequiredMixin, DetailView):
    model = MedicalStudy

    def get(self, request, *args, **kwargs):
        medical_study_name = request.GET.get('term')
        medical_studys = MedicalStudy.objects.filter(name__icontains=medical_study_name)
        studies_list = []
        for medical_study in medical_studys:
            data = {
                'label': medical_study.name,
                'value': medical_study.id
            }
            studies_list.append(data)
        return JsonResponse(studies_list, status=200, safe=False)


# Medical Equipment List By Study View (JSON)
class MedicalEquipmentListByStudyJsonView(LoginRequiredMixin, ListView):
    model = MedicalEquipment

    def get_queryset(self):
        medical_study_id = self.kwargs['pk']
        medical_study = MedicalStudy.objects.get(pk=medical_study_id)
        queryset = MedicalEquipment.objects.filter(sector=medical_study.sector)
        return queryset

    def get(self, request, *args, **kwargs):
        equipment_list_json = []
        equipments = self.get_queryset()
        for equipment in equipments:
            equipment_json = {
                'id': equipment.id,
                'name': equipment.name
            }
            equipment_list_json.append(equipment_json)
        data = equipment_list_json
        return JsonResponse(data, status=200, safe=False)


# Doctor List By Study View (JSON)
class DoctorListByStudyJsonView(LoginRequiredMixin, ListView):
    model = Doctor

    def get_queryset(self):
        medical_study_id = self.kwargs['pk']
        medical_study = MedicalStudy.objects.get(pk=medical_study_id)

        queryset = Doctor.objects.filter(sectors__in=[medical_study.sector])

        return queryset

    def get(self, request, *args, **kwargs):
        doctor_list_json = []
        doctors = self.get_queryset()
        for doctor in doctors:
            doctor_json = {
                'id': doctor.id,
                'name': str(doctor)
            }
            doctor_list_json.append(doctor_json)
        data = doctor_list_json
        return JsonResponse(data, status=200, safe=False)


# Doctor List All View (JSON)
class DoctorListAllJsonView(LoginRequiredMixin, ListView):
    model = Doctor

    def get_queryset(self):

        queryset = Doctor.objects.filter(sectors__sector_code='ECO')

        return queryset

    def get(self, request, *args, **kwargs):
        doctor_list_json = []
        doctors = self.get_queryset()
        for doctor in doctors:
            doctor_json = {
                'id': doctor.id,
                'name': str(doctor)
            }
            doctor_list_json.append(doctor_json)
        data = doctor_list_json
        return JsonResponse(data, status=200, safe=False)


# Medical Equipment List All View (JSON)
class MedicalEquipmentListAllJsonView(LoginRequiredMixin, ListView):
    model = MedicalEquipment

    def get_queryset(self):
        queryset = MedicalEquipment.objects.all().exclude(sector__sector_code='ECO')
        return queryset

    def get(self, request, *args, **kwargs):
        equipment_list_json = []
        equipments = self.get_queryset()
        for equipment in equipments:
            equipment_json = {
                'id': equipment.id,
                'name': equipment.name
            }
            equipment_list_json.append(equipment_json)
        data = equipment_list_json
        return JsonResponse(data, status=200, safe=False)


class PatientDetailAutocompleteJsonView(LoginRequiredMixin, DetailView):
    model = Patient

    @staticmethod
    def get(request, *args, **kwargs):
        q = request.GET.get('term')
        qs_partial = Patient.objects.annotate(search_fullname=Concat('name', Value(' '), 'last_name'))
        queryset = qs_partial.filter(search_fullname__icontains=q)

        qs = Patient.objects.all()
        for term in q.split():
            qs = qs.filter(Q(name__icontains=term) | Q(last_name__icontains=term) |
                           Q(document_number__icontains=term) | Q(tax_identification_number__icontains=term)
                           )

        data = []
        for patient in qs:
            json_data = patient.tojson()
            json_data['label'] = str(patient)
            json_data['value'] = patient.id
            json_data['ruc'] = patient.tax_identification_number
            data.append(
                json_data
            )
        return JsonResponse(data, status=200, safe=False)
