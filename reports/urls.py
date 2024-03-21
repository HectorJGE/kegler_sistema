from django.urls import path
from reports.views import CashReportListView, ReportingDoctorsReportListView, TreatingDoctorsReportListView, InsurancesAgreementsReportListView, ConsultationSheetTotalReportListView, \
    ReportDefinitionListView, ReportDefinitionCreateView, ReportDefinitionUpdateView, RunReportView, SaveReportView, InvoiceReportListView

urlpatterns = [
    # Cash Report
    path('cash_report_list/', CashReportListView.as_view(), name='reports.cash_report_list'),

    # Invoice Report
    path('invoice_report_list/', InvoiceReportListView.as_view(), name='reports.invoice_report_list'),

    # Reporting Doctors Report
    path('reporting_doctors_report_list/', ReportingDoctorsReportListView.as_view(), name='reports.reporting_doctors_report_list'),

    # Treating Doctors Report
    path('treating_doctors_report_list/', TreatingDoctorsReportListView.as_view(), name='reports.treating_doctors_report_list'),

    # Insurances Agreements Report
    path('insurances_agreements_report_list/', InsurancesAgreementsReportListView.as_view(), name='reports.insurances_agreements_report_list'),

    # Consultation Sheet Total Report
    path('consultation_sheet_total_report_list/', ConsultationSheetTotalReportListView.as_view(), name='reports.consultation_sheet_total_report_list'),

    # List Reports Definitions
    path('reports_definition_list/', ReportDefinitionListView.as_view(), name='reports.reports_definition_list'),

    # Create Report Definition
    path('report_definition/create/', ReportDefinitionCreateView.as_view(), name='reports.report_definition.create'),

    # Update Report Definition
    path('report_definition/update/<int:pk>', ReportDefinitionUpdateView.as_view(), name='reports.report_definition.update'),

    # Report Save
    path('save_report/<int:pk>/', SaveReportView.as_view(), name='reports.report_definition.save'),

    # Report Run
    path('run_report/', RunReportView.as_view(), name='reports.report_definition.run'),



]
