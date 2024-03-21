from .views import *
from django.urls import path

urlpatterns = [
    # INVOICE
    path('list/', InvoiceDataTableView.as_view(), name='invoice_list'),
    path('details/<int:pk>', InvoiceDetailsView.as_view(), name='invoice_detail'),
    path('create/', InvoiceCreationView.as_view(), name='invoice_create'),
    path('createfromconsultationsheet/<int:consultation_entry_sheet_id>', InvoiceCreationFromConsultationSheetView.as_view(), name='invoice.create.consultationsheet'),
    path('delete/<int:pk>', InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('modify/<int:pk>', InvoiceUpdateView.as_view(), name='invoice_update'),
    path('consultafactura/<int:company_id>', InvoiceLastNumber.as_view(), name='invoice.lastnumber'),
    path('print/<int:pk>/', InvoicePrintView.as_view(), name='invoice.print'),
    path('send_invoice_to_sifen/<int:pk>/', InvoiceSendToSifenView.as_view(), name='invoice.send_to_sifen'),
    path('send_invoice_email_to_cliente/<int:pk>/', InvoiceEmailSendToClientView.as_view(), name='invoice.email_send_to_client'),
    path('consultacliente/', CustomerQuery.as_view(), name='customer.query'),
    path('createfrominsurancereport/', InvoiceCreateFromInsuranceReportView.as_view(), name='invoice.create.insurance_report'),
    path('download_invoice_pdf/<int:pk>/', InvoiceDownloadPdfview.as_view(), name='invoice.download_invoice_pdf'),
    path('generate_invoice_pdf_sifen/<int:pk>/', InvoiceGenerateSifenPdfView.as_view(), name='invoice.generate_sifen_pdf'),
    path('consult_invoice_batch_sifen/<int:pk>/', InvoiceConsultBatchToSifenView.as_view(), name='invoice.consult_invoice_batch_sifen'),

    path('show_invoice_html/<int:pk>/', InvoiceShowHtmlView.as_view(), name='invoice.show_invoice_html'),
    path('generate_invoice_html_sifen/<int:pk>/', InvoiceGenerateSifenHtmlView.as_view(), name='invoice.generate_sifen_html'),
    path('print_invoice_preview_html/<int:pk>/', PrintInvoicePreviewHtmlView.as_view(), name='invoice.print_invoice_preview_html'),

    # CCREDIT NOTE
    path('credit_note/list/', CreditNoteDataTableView.as_view(), name='credit_note_list'),
    path('credit_note/details/<int:pk>', CreditNoteDetailsView.as_view(), name='credit_note_detail'),
    path('credit_note/create/', CreditNoteCreationView.as_view(), name='credit_note_create'),
    path('credit_note/create_from_invoice/<int:invoice_header_id>/', CreditNoteCreationFromInvoiceView.as_view(), name='credit_note.create_from_invoice'),
    path('credit_note/delete/<int:pk>/', CreditNoteDeleteView.as_view(), name='credit_note_delete'),
    path('credit_note/modify/<int:pk>/', CreditNoteUpdateView.as_view(), name='credit_note_update'),
    path('credit_note/print/<int:pk>/', CreditNotePrintView.as_view(), name='credit_note.print'),

    path('send_credit_note_to_sifen/<int:pk>/', CreditNoteSendToSifenView.as_view(), name='credit_note.send_to_sifen'),
    path('generate_credit_note_pdf_sifen/<int:pk>/', CreditNoteGenerateSifenPdfView.as_view(), name='credit_note.generate_sifen_pdf'),
    path('download_credit_note_pdf/<int:pk>/', CreditNoteDownloadPdfview.as_view(), name='credit_note.download_pdf'),
    path('consult_credit_note_batch_sifen/<int:pk>/', CreditNoteConsultBatchToSifenView.as_view(), name='credit_note.consult_credit_note_batch_sifen'),
    path('send_credit_note_email_to_cliente/<int:pk>/', CreditNoteEmailSendToClientView.as_view(), name='credit_note.email_send_to_client'),
    path('get_last_credit_note_number/<int:company_id>/', CreditNoteGetLastNumberView.as_view(), name='credit_note.get_last_number'),

    path('get_invoice_data_json/<int:invoice_id>/', GetInvoiceDataJsonView.as_view(), name='invoice.get_invoice_data_json'),
    path('get_invoices_by_company_json/<int:company_id>/', GetInvoicesByCompanyJsonView.as_view(), name='invoice.get_invoices_by_company_json'),

    path('generate_credit_note_html_sifen/<int:pk>/', CreditNoteGenerateSifenHtmlView.as_view(), name='credit_note.generate_sifen_html'),
    path('show_credit_note_html/<int:pk>/', CreditNoteShowHtmlView.as_view(), name='credit_note.show_credit_note_html'),

    # RUC Validation
    path('validate_ruc_set/<str:ruc_str>/', ValidateRucSetView.as_view(), name='validate_ruc_set'),

    # CUSTOMER
    path('customer/list/', CustomerDataTableView.as_view(), name='invoicing.customer_list'),
    path('customer/create/', CustomerCreateView.as_view(), name='invoicing.customer_create'),
    path('customer/update/<int:pk>', CustomerUpdateView.as_view(), name='invoicing.customer_update'),
    path('customer/delete/<int:pk>', CustomerDeleteView.as_view(), name='invoicing.customer_delete'),
    path('customer/details/<int:pk>', CustomerDetailView.as_view(), name='invoicing.customer_detail'),


]
