from django.urls import path
from consultation.views import ConsultationSheetListView, ConsultationSheetCreateView, ConsultationSheetUpdateView, \
    ConsultationSheetDetailView, ConsultationSheetDeleteView, \
    ConsultationSheetCreateFromAppointmentView, ConsultationSheetListUnassignedView, \
    ConsultationSheetAssignReportingDoctorView, ConsultationSheetMarkAsDeliveredView, \
    ConsultationSheetListUndeliveredView, ConsultationEntrySheetListView, ConsultationEntrySheetCreateView, \
    ConsultationEntrySheetDetailView, \
    ConsultationEntrySheetUpdateView, ConsultationEntrySheetPrintView, ConsultationSheetPrintView, \
    ConsultationSheetPrintTagView, CreateConsultationEntrySheetFromAppointment, \
    ConsultationEntrySheetDeleteView, ConsultationSheetListDataTableView, ConsultationEntrySheetListDataTableView, \
    ConsultationSheetListUnassignedDataTableView, \
    ConsultationSheetListUnDeliveredDataTableView, ConsultationSheetListUnRealizedTechnicianDataTableView, \
    TechnicianConsultationCreateView, TechniciansConsultationListDataTableView, TechnicianConsultationUpdateView, \
    ConsultationSheetListUnRealizedDoctorDataTableView, DoctorsConsultationListDataTableView, \
    DoctorConsultationUpdateView, DoctorConsultationCreateView, DoctorsConsultationsToInformListDataTableView, \
    DoctorConsultationReportCreateView, ConsultationsReportListDataTableView, ConsultationReportUpdateView, \
    DoctorMultipleConsultationCreateView, DoctorMultipleConsultationCreateReportView, \
    DoctorReportTemplateDetailJsonView, ConsultationReportCreatePdfView, ConsultationSheetListAssignedDataTableView, \
    ConsultationSheetUpdateDocumentsView, ConsultationsReportListByPatientDataTableView, ConsultationReportDetailView, \
    ConsultationDetailView, ConsultationListWithoutFilesDataTableView, ConsultationAssignFilesView, \
    ConsultationsReportRecordedListDataTableView, ConsultationSheetListDeliveredDataTableView, \
    ConsultationsReportFinishedListDataTableView, ConsultationSheetDocumentPrintView

urlpatterns = [
    # #################################  CONSULTATION SHEET
    path('consultation_sheet/list/', ConsultationSheetListDataTableView.as_view(), name='consultation_sheet.list'),
    path('consultation_sheet/list_datatable/', ConsultationSheetListDataTableView.as_view(), name='consultation_sheet.list_datatable'),
    path('consultation_sheet/list_unassigned_datatable/', ConsultationSheetListUnassignedDataTableView.as_view(), name='consultation_sheet.list_unassigned'),
    path('consultation_sheet/list_assigned_datatable/', ConsultationSheetListAssignedDataTableView.as_view(), name='consultation_sheet.list_assigned'),
    path('consultation_sheet/list_undelivered_datatable/', ConsultationSheetListUnDeliveredDataTableView.as_view(), name='consultation_sheet.list_undelivered'),
    path('consultation_sheet/list_delivered_datatable/', ConsultationSheetListDeliveredDataTableView.as_view(), name='consultation_sheet.list_delivered'),
    path('consultation_sheet/list_unrealized_technician/', ConsultationSheetListUnRealizedTechnicianDataTableView.as_view(), name='consultation_sheet.list_unrealized_technicians'),
    path('consultation_sheet/list_unrealized_doctors/', ConsultationSheetListUnRealizedDoctorDataTableView.as_view(), name='consultation_sheet.list_unrealized_doctors'),

    path('consultation_sheet/detail/<int:pk>/', ConsultationSheetDetailView.as_view(), name='consultation_sheet.detail'),

    path('consultation_sheet/create/', ConsultationSheetCreateView.as_view(), name='consultation_sheet.create'),
    path('consultation_sheet/create_from_consultation_entry_sheet/<int:consultation_entry_sheet_id>/', ConsultationSheetCreateView.as_view(), name='consultation_sheet.create_from_consultation_entry_sheet'),
    path('consultation_sheet/create_from_appointment/<int:appointment_id>/<int:consultation_entry_sheet_id>/', ConsultationSheetCreateFromAppointmentView.as_view(), name='consultation_sheet.create_from_appointment'),
    path('consultation_sheet/update/<int:pk>/', ConsultationSheetUpdateView.as_view(), name='consultation_sheet.update'),
    path('consultation_sheet/update_documents/<int:pk>/', ConsultationSheetUpdateDocumentsView.as_view(), name='consultation_sheet.update_documents'),
    path('consultation_sheet/delete/<int:pk>/', ConsultationSheetDeleteView.as_view(), name='consultation_sheet.delete'),

    path('consultation_sheet/assign_reporting_doctor/<int:consultation_sheet_id>/<int:doctor_id>', ConsultationSheetAssignReportingDoctorView.as_view(), name='consultation_sheet.assign_reporting_doctor'),
    path('consultation_sheet/mark_as_delivered/<int:consultation_sheet_id>/', ConsultationSheetMarkAsDeliveredView.as_view(), name='consultation_sheet.mark_as_delivered'),
    path('consultation_sheet/print_view/<int:pk>/', ConsultationSheetPrintView.as_view(), name='consultation_sheet.print'),
    path('consultation_sheet/print_tag/<int:pk>/', ConsultationSheetPrintTagView.as_view(), name='consultation_sheet.print_tag'),
    path('consultation_sheet/print_document/<int:pk>/', ConsultationSheetDocumentPrintView.as_view(), name='consultation_sheet.document_print'),

    # #################################  CONSULTATION ENTRY SHEET
    path('consultation_entry_sheet/list/', ConsultationEntrySheetListDataTableView.as_view(), name='consultation_entry_sheet.list'),
    path('consultation_entry_sheet/list_datatable/', ConsultationEntrySheetListDataTableView.as_view(), name='consultation_entry_sheet.list_datatable'),
    path('consultation_entry_sheet/detail/<int:pk>/', ConsultationEntrySheetDetailView.as_view(), name='consultation_entry_sheet.detail'),
    path('consultation_entry_sheet/create/', ConsultationEntrySheetCreateView.as_view(), name='consultation_entry_sheet.create'),
    path('consultation_entry_sheet/update/<int:pk>/', ConsultationEntrySheetUpdateView.as_view(), name='consultation_entry_sheet.update'),
    path('consultation_entry_sheet/print_view/<int:pk>/', ConsultationEntrySheetPrintView.as_view(), name='consultation_entry_sheet.print'),
    path('consultation_entry_sheet/delete/<int:pk>/', ConsultationEntrySheetDeleteView.as_view(), name='consultation_entry_sheet.delete'),

    path('consultation_entry_sheet/create_from_appointment/<int:appointment_id>/', CreateConsultationEntrySheetFromAppointment.as_view(), name='consultation_entry_sheet.create_from_appointment'),


    # #################################  CONSULTATION
    path('consultation/technician_create/<int:consultation_sheet_id>', TechnicianConsultationCreateView.as_view(), name='consultation.technician_consultation_create'),
    path('consultation/doctor_create/<int:consultation_sheet_id>', DoctorConsultationCreateView.as_view(), name='consultation.doctor_consultation_create'),
    path('consultation/doctor_create_multiple/', DoctorMultipleConsultationCreateView.as_view(), name='consultation.doctor_multiple_consultation_create'),
    path('consultation/list_technician/', TechniciansConsultationListDataTableView.as_view(), name='consultation.list_technicians'),
    path('consultation/list_doctors/', DoctorsConsultationListDataTableView.as_view(), name='consultation.list_doctors'),
    path('consultation/technician_update/<int:pk>', TechnicianConsultationUpdateView.as_view(), name='consultation.technician_consultation_update'),
    path('consultation/detail/<int:pk>', ConsultationDetailView.as_view(), name='consultation.detail'),
    path('consultation/doctor_update/<int:pk>', DoctorConsultationUpdateView.as_view(), name='consultation.doctor_consultation_update'),
    path('consultation/doctors_list_to_inform/', DoctorsConsultationsToInformListDataTableView.as_view(), name='consultation.doctors_list_to_inform'),
    path('consultation/list_without_files/', ConsultationListWithoutFilesDataTableView.as_view(), name='consultation.list_without_files'),
    path('consultation/assign_files/<int:consultation_id>', ConsultationAssignFilesView.as_view(), name='consultation.assign_files'),

    # #################################  CONSULTATION REPORT
    path('consultation_report/create/<int:consultation_id>', DoctorConsultationReportCreateView.as_view(), name='consultation_report.create'),
    path('consultation_report/list/', ConsultationsReportListDataTableView.as_view(), name='consultation_report.list'),
    path('consultation_report/list_finished/', ConsultationsReportFinishedListDataTableView.as_view(), name='consultation_report.list_finished'),
    path('consultation_report/recorded_list/', ConsultationsReportRecordedListDataTableView.as_view(), name='consultation_report.recorded_list'),
    path('consultation_report/list_by_patient/<int:patient_id>', ConsultationsReportListByPatientDataTableView.as_view(), name='consultation_report.list_by_patient'),
    path('consultation_report/update/<int:pk>', ConsultationReportUpdateView.as_view(), name='consultation_report.update'),
    path('consultation_report/detail/<int:pk>', ConsultationReportDetailView.as_view(), name='consultation_report.detail'),
    path('consultation_report/doctor_create_multiple/', DoctorMultipleConsultationCreateReportView.as_view(), name='consultation_report.doctor_multiple_consultation_create_report'),
    path('consultation_report/create_pdf/<int:pk>', ConsultationReportCreatePdfView.as_view(), name='consultation_report.create_pdf_view'),


    # #################################  DOCTOR REPORT TEMPLATE
    path('get_doctor_report_template_json/<int:pk>', DoctorReportTemplateDetailJsonView.as_view(), name='consultation.get_doctor_report_template_detail_json'),

]
