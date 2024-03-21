from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *


# Register your models here.
# ####################################  PAYMENT TERM
# class PaymentTermResource(resources.ModelResource):
#
#     class Meta:
#         model = PaymentTerm
#
#
# class PaymentTermAdmin(ImportExportModelAdmin):
#     resource_class = PaymentTermResource
#     search_fields = ['id', 'name']
#     list_filter = ['created_at', 'updated_at']
#
#     list_display = (
#         'id',
#         'name',
#         'created_at',
#         'updated_at'
#     )


# admin.site.register(PaymentTerm, PaymentTermAdmin)


# Invoice Detail Inline
class InvoiceDetailsInlineAdmin(admin.TabularInline):
    model = InvoiceDetails


# ####################################### INVOICE HEADER
class InvoiceHeaderResource(resources.ModelResource):

    class Meta:
        model = InvoiceHeader


class InvoiceHeaderAdmin(ImportExportModelAdmin):
    resource_class = InvoiceHeaderResource
    search_fields = ['id', 'invoice_number', 'client_name', 'client_tax_identification_number', 'payment_term__name']
    list_filter = ['payment_term', 'invoice_date', 'currency', 'created_at', 'updated_at']

    list_display = (
        'id',
        'invoice_number',
        'client_name',
        'client_tax_identification_number',
        'invoice_date',
        'payment_term',
        'invoice_total',
        'currency',
        'invoice_total_letters',
        'created_at',
        'updated_at'
    )

    inlines = [
        InvoiceDetailsInlineAdmin
    ]


admin.site.register(InvoiceHeader, InvoiceHeaderAdmin)


# ######################################### INVOICE DETAILS
class InvoiceDetailsResource(resources.ModelResource):

    class Meta:
        model = InvoiceDetails


class InvoiceDetailsAdmin(ImportExportModelAdmin):
    resource_class = InvoiceDetailsResource
    search_fields = ['id', 'name', 'description', 'invoice_header__invoice_number']
    list_filter = ['currency', 'created_at', 'updated_at']

    list_display = (
        'id',
        'invoice_header',
        'quantity',
        'description',
        'unit_price',
        'currency',
        'total_price',
        'created_at',
        'updated_at'
    )


# admin.site.register(InvoiceDetails, InvoiceDetailsAdmin)


# ######################################### PAYMENT METHOD
class PaymentMethodResource(resources.ModelResource):

    class Meta:
        model = PaymentMethod


class PaymentMethodAdmin(ImportExportModelAdmin):
    resource_class = PaymentMethodResource
    search_fields = ['id', 'name']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'id',
        'name',
        'created_at',
        'updated_at'
    )


admin.site.register(PaymentMethod, PaymentMethodAdmin)

# ######################################### STAMP
class InvoiceStampAdminResource(resources.ModelResource):

    class Meta:
        model = InvoiceStamp


class InvoiceStampAdmin(ImportExportModelAdmin):
    resource_class = InvoiceStampAdminResource
    search_fields = ['id', 'number']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'startDate',
        'endDate',
        'number',
        'company_name',
        'electronic_stamp'
    )


admin.site.register(InvoiceStamp, InvoiceStampAdmin)


# ######################################### CREDIT NOTE STAMP
class CreditNoteStampAdminResource(resources.ModelResource):

    class Meta:
        model = CreditNoteStamp


class CreditNoteStampAdmin(ImportExportModelAdmin):
    resource_class = CreditNoteStampAdminResource
    search_fields = ['id', 'number']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'startDate',
        'endDate',
        'number',
        'company_name',
        'electronic_stamp'
    )


admin.site.register(CreditNoteStamp, CreditNoteStampAdmin)


# Rango de Facturas
class InvoiceRangeAdminResource(resources.ModelResource):

    class Meta:
        model = InvoiceRange


class InvoiceRangeAdmin(ImportExportModelAdmin):
    resource_class = InvoiceRangeAdminResource
    search_fields = ['id', 'sucursal_number', 'boca_number', 'start_number', 'end_number']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'id',
        'sucursal_number',
        'boca_number',
        'start_number',
        'end_number',
    )


admin.site.register(InvoiceRange, InvoiceRangeAdmin)


# Rango de Notas de Credito
class CreditNoteRangeAdminResource(resources.ModelResource):

    class Meta:
        model = CreditNoteRange


class CreditNoteRangeAdmin(ImportExportModelAdmin):
    resource_class = CreditNoteRangeAdminResource
    search_fields = ['id', 'sucursal_number', 'boca_number', 'start_number', 'end_number']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'id',
        'sucursal_number',
        'boca_number',
        'start_number',
        'end_number',
    )


admin.site.register(CreditNoteRange, CreditNoteRangeAdmin)


# Tabla de relacion rango-timbrado
class CreditNoteStampRangeResource(resources.ModelResource):

    class Meta:
        model = CreditNoteStampRange


class CreditNoteStampRangeAdmin(ImportExportModelAdmin):
    resource_class = CreditNoteStampRangeResource
    search_fields = ['stamp', 'range_credit_note']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'stamp', 'range_credit_note', 'user'
    )


admin.site.register(CreditNoteStampRange, CreditNoteStampRangeAdmin)


# Tabla de relacion rango-timbrado
class StampRangeResource(resources.ModelResource):

    class Meta:
        model = StampRange


class StampRangeAdmin(ImportExportModelAdmin):
    resource_class = StampRangeResource
    search_fields = ['stamp', 'range_invoice']
    list_filter = ['created_at', 'updated_at']

    list_display = (
        'stamp', 'range_invoice', 'user'
    )


admin.site.register(StampRange, StampRangeAdmin)


# Compañīas para Facturar
class CompanyResource(resources.ModelResource):

    class Meta:
        model = IssuingCompanyName


class CompanyAdmin(ImportExportModelAdmin):
    resource_class = CompanyResource
    search_fields = ['id', 'company_name', 'company_tax_id']
    list_filter = ['created_at', 'updated_at']
    list_display = ('company_name', 'company_tax_id')


admin.site.register(IssuingCompanyName, CompanyAdmin)


# Clientes
class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer


class CustomerAdmin(ImportExportModelAdmin):
    resource_class = CustomerResource
    search_fields = ['id', 'customer_name', 'customer_tax_id_number']
    list_filter = ['created_at', 'updated_at']
    list_display = (
        'id',
        'customer_name',
        'customer_tax_id_number',
        'customer_email',
        'customer_address',
        'customer_phone_number',
        'patient',
        'sifen_ruc_validated',
        'is_taxpayer',
        'customer_type'
    )


admin.site.register(Customer, CustomerAdmin)


class SifenTransactionResource(resources.ModelResource):
    class Meta:
        model = SifenTransaction


class SifenTransactionAdmin(ImportExportModelAdmin):
    resource_class = SifenTransactionResource
    search_fields = ['id']
    list_filter = ['created_at', 'updated_at', 'success']
    list_display = (
        'id',
        'invoice_header',
        'credit_note_header',
        'url',
        'transaction_datetime',
        'user',
        'success'
    )


admin.site.register(SifenTransaction, SifenTransactionAdmin)


# Credit Note Detail Inline
class CreditNoteDetailInlineAdmin(admin.TabularInline):
    model = CreditNoteDetail


# ####################################### CREDIT NOTE HEADER
class CreditNoteHeaderResource(resources.ModelResource):

    class Meta:
        model = CreditNoteHeader


class CreditNoteHeaderAdmin(ImportExportModelAdmin):
    resource_class = CreditNoteHeaderResource
    search_fields = ['id', 'credit_note_number', 'client_name', 'client_tax_identification_number']
    list_filter = ['credit_note_date', 'currency', 'created_at', 'updated_at']

    list_display = (
        'id',
        'invoice_header',
        'credit_note_number',
        'client_name',
        'client_tax_identification_number',
        'credit_note_date',
        'credit_note_total',
        'currency',
        'credit_note_total_letters',
        'created_at',
        'updated_at'
    )

    inlines = [
        CreditNoteDetailInlineAdmin
    ]


admin.site.register(CreditNoteHeader, CreditNoteHeaderAdmin)


# ######################################### CREDIT NOTE DETAILS
class CreditNoteDetailResource(resources.ModelResource):

    class Meta:
        model = CreditNoteDetail


class CreditNoteDetailAdmin(ImportExportModelAdmin):
    resource_class = CreditNoteDetailResource
    search_fields = ['id', 'name', 'description', 'credit_note_header__credit_note_number']
    list_filter = ['currency', 'created_at', 'updated_at']

    list_display = (
        'id',
        'credit_note_header',
        'quantity',
        'description',
        'unit_price',
        'currency',
        'total_price',
        'created_at',
        'updated_at'
    )


# admin.site.register(CreditNoteDetail, CreditNoteDetailAdmin)
