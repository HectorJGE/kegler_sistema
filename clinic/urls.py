from django.urls import path

from clinic.views import PatientListView, PatientDetailView, PatientDetailJsonView, \
    PatientUpdateView, PatientCreateView, PatientDeleteView, MedicalStudyDetailJsonView, \
    MedicalEquipmentListByStudyJsonView, DoctorListByStudyJsonView, MedicalEquipmentListAllJsonView, \
    DoctorListAllJsonView, PatientDataTableView, PatientDetailAutocompleteJsonView, \
    MedicalStudyAutocompleteDetailJsonView

urlpatterns = [
    # Patient
    path('patient/list/', PatientDataTableView.as_view(), name='patient.list'),
    path('patient/list_datatable/', PatientDataTableView.as_view(), name='patient.list_datatable'),
    path('patient/detail/<int:pk>/', PatientDetailView.as_view(), name='patient.detail'),
    path('patient/detail_json/<int:pk>/', PatientDetailJsonView.as_view(), name='patient.detail_json'),
    path('patient/detail_autocomplete_json/', PatientDetailAutocompleteJsonView.as_view(), name='patient.detail_autocomplete_json'),
    path('patient/create/', PatientCreateView.as_view(), name='patient.create'),
    path('patient/delete/<int:pk>/', PatientDeleteView.as_view(), name='patient.delete'),
    path('patient/update/<int:pk>/', PatientUpdateView.as_view(), name='patient.update'),

    # Medical Study
    path('medical_study/detail_json/<int:pk>/', MedicalStudyDetailJsonView.as_view(), name='medical_study.detail_json'),
    path('medical_study/autocomplete_detail_json/', MedicalStudyAutocompleteDetailJsonView.as_view(), name='medical_study.autocomplete_detail_json'),

    # Medical Equipment
    path('medical_equipment/get_list_by_study_json/<int:pk>/', MedicalEquipmentListByStudyJsonView.as_view(), name='medical_equipment.list_by_study_json'),
    path('medical_equipment/get_list_all_json/', MedicalEquipmentListAllJsonView.as_view(), name='medical_equipment.list_all_json'),

    # Doctor
    path('doctor/get_list_by_study_json/<int:pk>/', DoctorListByStudyJsonView.as_view(), name='doctor.list_by_study_json'),
    path('doctor/get_list_all_json/', DoctorListAllJsonView.as_view(), name='doctor.list_all_json'),
]
