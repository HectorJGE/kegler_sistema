from django.contrib.auth.models import User
from django.db import models
from softdelete.models import SoftDeleteObject
from django.utils.translation import ugettext_lazy as _
from auditlog.registry import auditlog
from base.models import Person, Currency, TimeStampModel

# Create your models here.
# Company Name
from clinic.models import Patient


class Customer(SoftDeleteObject, TimeStampModel):
    INDIVIDUAL = 0
    LEGAL_ENTITY = 1

    CUSTOMER_TYPES = (
        (INDIVIDUAL, _("Individual")),
        (LEGAL_ENTITY, _("Legal Entity"))
    )
    customer_name = models.CharField(verbose_name=_('Customer Name'),
                                     max_length=40, null=False, blank=False)
    customer_tax_id_number = models.CharField(verbose_name=_('Customer Tax Identification Number'),
                                              max_length=40, null=False, blank=False, unique=True)
    patient = models.ForeignKey(to=Patient, on_delete=models.PROTECT,
                                null=True, blank=True)

    customer_email = models.EmailField(verbose_name=_('Customer Email'),
                                       null=True, blank=False)
    customer_address = models.CharField(verbose_name=_('Customer Address'),
                                        max_length=250, null=True, blank=False)
    customer_phone_number = models.CharField(verbose_name=_('Customer Phone Number'),
                                             max_length=20, null=True, blank=False)
    sifen_ruc_validated = models.BooleanField(
        verbose_name=_('Sifen RUC Validated'), default=False, null=True, blank=True
    )
    is_taxpayer = models.BooleanField(
        verbose_name=_('Is Taxpayer'), default=True, null=True, blank=False
    )
    customer_type = models.IntegerField(
        verbose_name=_('Customer Type'),
        null=True, blank=False,
        choices=CUSTOMER_TYPES,
        default=0
    )

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        if self.customer_tax_id_number:
            return self.customer_name + " (" + self.customer_tax_id_number + ")"
        else:
            return self.customer_name


class IssuingCompanyName(SoftDeleteObject, TimeStampModel):
    company_name = models.CharField(verbose_name=_('Company Name'),
                                    max_length=40, null=False, blank=False, unique=True)
    company_tax_id = models.CharField(verbose_name=_('Client Tax Identification Number'),
                                      max_length=50, null=False, blank=False, unique=True)

    # SIFEN CLIENT PARAMS
    sifen_logo = models.CharField(verbose_name=_('SIFEN LOGO'), blank=False, null=True, max_length=200)
    sifen_password = models.CharField(verbose_name=_('SIFEN PASSWORD'), blank=False, null=True, max_length=100)
    sifen_id_csc = models.CharField(verbose_name=_('SIFEN ID CSC'), blank=False, null=True, max_length=100)
    sifen_csc = models.CharField(verbose_name=_('SIFEN CSC'), blank=False, null=True, max_length=200)

    # SIFEN PARAMS
    sifen_digital_signature_date = models.CharField(verbose_name=_('SIFEN DIGITAL SIGNATURE DATE'),
                                                    blank=False, null=True, max_length=100)
    sifen_ruc = models.CharField(verbose_name=_('SIFEN RUC'), blank=False, null=True, max_length=100)
    sifen_business_name = models.CharField(verbose_name=_('SIFEN BUSINESS NAME'), blank=False,
                                           null=True, max_length=200)
    sifen_fantasy_name = models.CharField(verbose_name=_('SIFEN FANTASY NAME'), blank=False,
                                          null=True, max_length=200)

    # SIFEN PARAMS - ECONOMIC ACTIVITY
    sifen_economic_activity_code = models.CharField(verbose_name=_('SIFEN ECONOMIC ACTIVITY CODE'), blank=False,
                                                    null=True, max_length=10)
    sifen_economic_activity_description = models.CharField(verbose_name=_('SIFEN ECONOMIC ACTIVITY DESCRIPTION'),
                                                           blank=False, null=True, max_length=200)
    sifen_stamp_number = models.CharField(verbose_name=_('SIFEN STAMP NUMBER'), blank=False, null=True, max_length=200)
    sifen_stamp_date = models.CharField(verbose_name=_('SIFEN STAMP DATE'), blank=False, null=True, max_length=100)

    # PARAMS - ESTABLISHMENT
    sifen_establishment_code = models.CharField(verbose_name=_('SIFEN ESTABLISHMENT CODE'),
                                                blank=False, null=True, max_length=4)
    sifen_establishment_direction = models.CharField(verbose_name=_('SIFEN ESTABLISHMENT DIRECTION'),
                                                     blank=False, null=True, max_length=200)
    sifen_establishment_house_number = models.CharField(verbose_name=_('SIFEN ESTABLISHMENT HOUSE NUMBER'),
                                                        blank=False, null=True, max_length=200)
    sifen_establishment_street_name_1 = models.CharField(verbose_name=_('SIFEN ESTABLISHMENT STREET NAME 1'),
                                                         blank=False, null=True, max_length=200)
    sifen_establishment_street_name_2 = models.CharField(verbose_name=_('SIFEN ESTABLISHMENT STREET NAME 2'),
                                                         blank=False, null=True, max_length=200)
    sifen_establishment_department_code = models.CharField(verbose_name=_('SIFEN ESTABLISHMENT DEPARTMENT CODE'),
                                                           blank=False, null=True, max_length=3)
    sifen_establishment_department_description = models.CharField(
        verbose_name=_('SIFEN ESTABLISHMENT DEPARTMENT DESCRIPTION'), blank=False, null=True, max_length=200)
    sifen_establishment_district_code = models.CharField(
        verbose_name=_('SIFEN ESTABLISHMENT DISTRICT CODE'), blank=False, null=True, max_length=3)
    sifen_establishment_district_description = models.CharField(
        verbose_name=_('SIFEN ESTABLISHMENT DISTRICT DESCRIPTION'), blank=False, null=True, max_length=200)
    sifen_establishment_city_code = models.CharField(
        verbose_name=_('SIFEN ESTABLISHMENT CITY CODE'), blank=False, null=True, max_length=3)
    sifen_establishment_city_description = models.CharField(
        verbose_name=_('SIFEN ESTABLISHMENT CITY DESCRIPTION'), blank=False, null=True, max_length=50)
    sifen_establishment_phone = models.CharField(
        verbose_name=_('SIFEN ESTABLISHMENT PHONE'), blank=False, null=True, max_length=12)
    sifen_establishment_email = models.CharField(
        verbose_name=_('SIFEN ESTABLISHMENT EMAIL'), blank=False, null=True, max_length=100)
    sifen_establishment_denomination = models.CharField(
        verbose_name=_('SIFEN ESTABLISHMENT DENOMINATION'), blank=False, null=True, max_length=200)

    # SIFEN - EMAIL SENDER
    sifen_email_host = models.CharField(verbose_name=_('SIFEN EMAIL HOST'), blank=False, null=True, max_length=100)
    sifen_email_port = models.CharField(verbose_name=_('SIFEN EMAIL PORT'), blank=False, null=True, max_length=5)
    sifen_email_host_user = models.CharField(verbose_name=_('SIFEN EMAIL HOST USER'),
                                             blank=False, null=True, max_length=100)
    sifen_email_host_password = models.CharField(verbose_name=_('SIFEN EMAIL HOST PASSWORD'),
                                                 blank=False, null=True, max_length=100)
    sifen_email_use_tls = models.BooleanField(verbose_name=_('SIFEN EMAIL USE TLS'), null=False, default=True)
    sifen_email_default_from = models.CharField(verbose_name=_('SIFEN EMAIL DEFAULT FROM'),
                                                blank=False, null=True, max_length=200)

    class Meta:
        verbose_name = _('Issuing Company')
        verbose_name_plural = _('Issuing Companys')

    def __str__(self):
        return self.company_name


# Invoice Stamp
class InvoiceStamp(SoftDeleteObject, TimeStampModel):
    startDate = models.DateField(verbose_name=_('Start Date'))
    endDate = models.DateField(verbose_name=_('End Date'))
    number = models.CharField(max_length=30, verbose_name=_('Number'))
    company_name = models.ForeignKey(to=IssuingCompanyName, on_delete=models.PROTECT,
                                     null=True, blank=True,
                                     verbose_name=_('Company Name'),
                                     related_name='company')
    electronic_stamp = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Invoice Stamp')
        verbose_name_plural = _('Invoice Stamps')

    def as_json(self):
        return dict(
            label=self.number,
            numero=self.number,
            id=self.id
        )

    def __str__(self):
        return self.number + " - " + str(self.company_name)


auditlog.register(InvoiceStamp)


# Credit Note Stamp
class CreditNoteStamp(SoftDeleteObject, TimeStampModel):
    startDate = models.DateField(verbose_name=_('Start Date'))
    endDate = models.DateField(verbose_name=_('End Date'))
    number = models.CharField(max_length=30, verbose_name=_('Number'))
    company_name = models.ForeignKey(to=IssuingCompanyName, on_delete=models.PROTECT,
                                     null=True, blank=True,
                                     verbose_name=_('Company Name'),
                                     related_name='credit_note_stamps')
    electronic_stamp = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Credit Note Stamp')
        verbose_name_plural = _('Credit Note Stamps')

    def as_json(self):
        return dict(
            label=self.number,
            numero=self.number,
            id=self.id
        )

    def __str__(self):
        return self.number + " - " + str(self.company_name)


auditlog.register(InvoiceStamp)


class InvoiceRange(SoftDeleteObject, TimeStampModel):
    sucursal_number = models.CharField(max_length=30, verbose_name=_('Branch Office Number'))
    boca_number = models.CharField(max_length=30, verbose_name=_('Collection Point Number'))
    start_number = models.CharField(max_length=30, verbose_name=_('Start Number'))
    end_number = models.CharField(max_length=30, verbose_name=_('End Number'))

    def as_json(self):
        return dict(
            label="{} - {}".format(self.sucursal_number, self.boca_number),
            nro_sucursal=self.sucursal_number,
            nro_boca=self.boca_number,
            nro_desde=self.start_number,
            nro_hasta=self.end_number,
            id=self.id
        )

    class Meta:
        verbose_name = _('Invoice Range')
        verbose_name_plural = _('Invoice Ranges')

    def __str__(self):
        return self.sucursal_number + '-' + self.boca_number + ' - (' + self.start_number + '-' + self.end_number + ')'


auditlog.register(InvoiceRange)


# CREDIT NOTE RANGE
class CreditNoteRange(SoftDeleteObject, TimeStampModel):
    sucursal_number = models.CharField(max_length=30, verbose_name=_('Branch Office Number'))
    boca_number = models.CharField(max_length=30, verbose_name=_('Collection Point Number'))
    start_number = models.CharField(max_length=30, verbose_name=_('Start Number'))
    end_number = models.CharField(max_length=30, verbose_name=_('End Number'))

    def as_json(self):
        return dict(
            label="{} - {}".format(self.sucursal_number, self.boca_number),
            nro_sucursal=self.sucursal_number,
            nro_boca=self.boca_number,
            nro_desde=self.start_number,
            nro_hasta=self.end_number,
            id=self.id
        )

    class Meta:
        verbose_name = _('Credit Note Range')
        verbose_name_plural = _('Credit Note Ranges')

    def __str__(self):
        return self.sucursal_number + '-' + self.boca_number + ' - (' + self.start_number + '-' + self.end_number + ')'


auditlog.register(CreditNoteRange)


# INVOICE HEADER
class InvoiceHeader(SoftDeleteObject, TimeStampModel):
    CONDITIONS = (
        ('CONTADO', 'CONTADO'),
        ('CREDITO', 'CREDITO'),
    )
    customer = models.ForeignKey(to=Customer, null=True, blank=True, default=None,
                                 verbose_name=_('Customer'), on_delete=models.PROTECT,
                                 related_name='invoice_headers')
    invoice_number = models.CharField(verbose_name=_('Invoice Number'),
                                      max_length=25, null=False, blank=False)
    client_name = models.CharField(verbose_name=_('Client Name'), max_length=150, null=False, blank=False)
    client_tax_identification_number = models.CharField(verbose_name=_('Client Tax Identification Number'),
                                                        max_length=50, null=True, blank=False)
    client_email = models.CharField(verbose_name=_('Client Email'),
                                    max_length=200, null=True, blank=False)
    client_address = models.CharField(verbose_name=_('Client Address'),
                                      max_length=250, null=True, blank=False)
    client_phone_number = models.CharField(verbose_name=_('Client Phone Number'),
                                           max_length=15, null=True, blank=False)
    invoice_date = models.DateField(verbose_name=_('Invoice Date'), null=False, blank=False)
    payment_term = models.CharField(max_length=15, choices=CONDITIONS, verbose_name=_('Condicion de pago'), null=False,
                                    blank=False)
    company = models.ForeignKey(to=IssuingCompanyName, on_delete=models.PROTECT,
                                null=True, blank=False,
                                verbose_name=_('Company Name'),
                                related_name='invoice_headers'
                                )
    invoice_stamp = models.ForeignKey(to=InvoiceStamp, on_delete=models.PROTECT,
                                      null=False, blank=False,
                                      verbose_name=_('Invoice Stamp'),
                                      related_name='invoice_headers'
                                      )
    subtotal = models.FloatField(verbose_name=_('Subtotal'), blank=False, default=0)
    invoice_total = models.FloatField(verbose_name=_('Invoice Total'), blank=False, default=0)
    total_tax10 = models.FloatField(verbose_name=_('TOTAL TAX 10%'), blank=False, null=True, default=0)
    total_tax5 = models.FloatField(verbose_name=_('TOTAL TAX 5%'), blank=False, null=True, default=0)
    total_exempt = models.FloatField(verbose_name=_('TOTAL EXEMPTS'), blank=False, null=True, default=0)
    total_tax = models.FloatField(verbose_name=_('TOTAL TAXES'), blank=False, null=True, default=0)
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='invoice_headers'
    )
    invoice_total_letters = models.CharField(verbose_name=_('Invoice Total Letters'), max_length=250, blank=False)
    # SIFEN FIELDS
    invoice_cdc = models.CharField(verbose_name=_('Invoice CDC'), max_length=250, blank=True, null=True)
    invoice_xml_text = models.TextField(verbose_name=_('Invoice XML'), blank=True, null=True)
    invoice_pdf_base64 = models.TextField(verbose_name=_('Invoice PDF base64'), blank=True, null=True)
    invoice_kude_html = models.TextField(verbose_name=_('Invoice KUDE HTML'), blank=True, null=True)
    invoice_email_sent = models.BooleanField(verbose_name=_('Invoice Sent'), default=False, null=True)
    invoice_batch_id = models.CharField(verbose_name=_('Invoice Batch ID'), max_length=250, blank=True, null=True)
    invoice_batch_sended = models.BooleanField(verbose_name=_('Invoice Batch sended'), default=False, blank=True,
                                               null=True)

    class Meta:
        verbose_name = _('Invoice Header')
        verbose_name_plural = _('Invoice Headers')

    def __str__(self):
        return str(self.invoice_stamp) + " - " + self.invoice_number + ' - ' + self.client_name


auditlog.register(InvoiceHeader)


#  INVOICE DETAILS
class InvoiceDetails(SoftDeleteObject, TimeStampModel):
    invoice_header = models.ForeignKey(
        to=InvoiceHeader, on_delete=models.CASCADE,
        verbose_name=_('Invoice Header'),
        null=False, blank=False,
        related_name='invoice_details'
    )
    quantity = models.IntegerField(verbose_name=_('Quantity'), blank=False, default=0)
    description = models.CharField(verbose_name=_('Description'), max_length=250, null=False, blank=False)
    unit_price = models.FloatField(verbose_name=_('Unit price'), null=False, blank=False, default=0)
    tax_10 = models.FloatField(verbose_name=_('TAX 10%'), blank=False, null=True, default=0)
    tax_5 = models.FloatField(verbose_name=_('TAX 5%'), blank=False, null=True, default=0)
    exempt = models.FloatField(verbose_name=_('EXEMPTS'), blank=False, null=True, default=0)

    class Meta:
        verbose_name = _('Invoice Detail')
        verbose_name_plural = _('Invoice Details')

    def __str__(self):
        return str(self.invoice_header) + ' - (' + str(self.quantity) + ')' + self.description


auditlog.register(InvoiceDetails)


# CREDIT NOTE HEADER
class CreditNoteHeader(SoftDeleteObject, TimeStampModel):
    invoice_header = models.ForeignKey(
        to=InvoiceHeader, on_delete=models.CASCADE,
        verbose_name=_('Invoice Header'),
        null=False, blank=False,
        related_name='credit_notes'
    )
    customer = models.ForeignKey(to=Customer, null=True, blank=True, default=None,
                                 verbose_name=_('Customer'), on_delete=models.PROTECT,
                                 related_name='credit_notes')
    credit_note_number = models.CharField(verbose_name=_('Credit Note Number'),
                                          max_length=25, null=False, blank=False)
    client_name = models.CharField(verbose_name=_('Client Name'), max_length=150, null=False, blank=False)
    client_address = models.CharField(verbose_name=_('Client Address'), max_length=250, null=True, blank=False)
    client_tax_identification_number = models.CharField(verbose_name=_('Client Tax Identification Number'),
                                                        max_length=50, null=True, blank=False)
    client_email = models.EmailField(verbose_name=_('Client Email'), null=True, blank=False)
    client_phone_number = models.CharField(verbose_name=_('Client Phone Number'),
                                           max_length=15, null=True, blank=False)

    credit_note_date = models.DateField(verbose_name=_('Credit note Date'), blank=False)
    company = models.ForeignKey(to=IssuingCompanyName, on_delete=models.PROTECT,
                                null=True, blank=False,
                                verbose_name=_('Company Name'),
                                related_name='credit_notes'
                                )
    credit_note_stamp = models.ForeignKey(to=CreditNoteStamp, on_delete=models.PROTECT,
                                          null=False, blank=False,
                                          verbose_name=_('Credit Note Stamp'))
    subtotal = models.FloatField(verbose_name=_('Subtotal'), blank=False, default=0)
    credit_note_total = models.FloatField(verbose_name=_('Credit Note Total'), blank=False, default=0)
    total_tax10 = models.FloatField(verbose_name=_('TOTAL TAX 10%'), blank=False, null=True, default=0)
    total_tax5 = models.FloatField(verbose_name=_('TOTAL TAX 5%'), blank=False, null=True, default=0)
    total_exempt = models.FloatField(verbose_name=_('TOTAL EXEMPTS'), blank=False, null=True, default=0)
    total_tax = models.FloatField(verbose_name=_('TOTAL TAXES'), blank=False, null=True, default=0)
    currency = models.ForeignKey(
        to=Currency, on_delete=models.PROTECT,
        verbose_name=_('Currency'),
        null=False, blank=False,
        related_name='credit_notes'
    )
    credit_note_total_letters = models.CharField(
        verbose_name=_('Credit Note Total Letters'), blank=False, max_length=250)
    # SIFEN FIELDS
    credit_note_cdc = models.CharField(verbose_name=_('Credit Note CDC'), max_length=250, blank=True, null=True)
    credit_note_xml_text = models.TextField(verbose_name=_('Credit Note XML'), blank=True, null=True)
    credit_note_pdf_base64 = models.TextField(verbose_name=_('Credit Note PDF base64'), blank=True, null=True)
    credit_note_kude_html = models.TextField(verbose_name=_('Credit Note KUDE HTML'), blank=True, null=True)
    credit_note_email_sent = models.BooleanField(verbose_name=_('Credit Note Sent'), default=False, null=True)
    credit_note_batch_id = models.CharField(verbose_name=_('Credit Note Batch ID'), max_length=250, blank=True,
                                            null=True)
    credit_note_batch_sended = models.BooleanField(verbose_name=_('Credit Note Batch sended'), default=False,
                                                   blank=True, null=True)

    class Meta:
        verbose_name = _('Credit Note Header')
        verbose_name_plural = _('Credit Note Headers')

    def __str__(self):
        return self.credit_note_stamp.number + ' - ' + self.credit_note_number + ' - ' + self.client_name


auditlog.register(CreditNoteHeader)


#  CREDIT NOTE DETAIL
class CreditNoteDetail(SoftDeleteObject, TimeStampModel):
    credit_note_header = models.ForeignKey(
        to=CreditNoteHeader, on_delete=models.CASCADE,
        verbose_name=_('Credit Note Header'),
        null=False, blank=False,
        related_name='credit_note_details'
    )
    quantity = models.IntegerField(verbose_name=_('Quantity'), blank=False, default=0)
    description = models.CharField(verbose_name=_('Description'), max_length=250, null=False, blank=False)
    unit_price = models.FloatField(verbose_name=_('Unit price'), null=False, blank=False, default=0)
    tax_10 = models.FloatField(verbose_name=_('TAX 10%'), blank=False, null=True, default=0)
    tax_5 = models.FloatField(verbose_name=_('TAX 5%'), blank=False, null=True, default=0)
    exempt = models.FloatField(verbose_name=_('EXEMPTS'), blank=False, null=True, default=0)

    class Meta:
        verbose_name = _('Credit Note Detail')
        verbose_name_plural = _('Credit Note Details')

    def __str__(self):
        return str(self.credit_note_header) + ' - (' + str(self.quantity) + ')' + self.description


auditlog.register(CreditNoteDetail)


class PaymentMethod(SoftDeleteObject, TimeStampModel):
    name = models.CharField(max_length=100, verbose_name=_('Name'), null=False, blank=False)
    abbreviation = models.CharField(max_length=2, verbose_name=_('Abbreviation'), null=True, blank=True)

    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Method')

    def __str__(self):
        return self.name


auditlog.register(PaymentMethod)


class StampRange(SoftDeleteObject, TimeStampModel):
    stamp = models.ForeignKey(InvoiceStamp, on_delete=models.PROTECT, verbose_name=_('Stamp'))
    range_invoice = models.ForeignKey(InvoiceRange, on_delete=models.PROTECT, verbose_name=_('Invoice Range'))
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('User'))

    class Meta:
        verbose_name = _('Stamp Range')
        verbose_name_plural = _('Stamp Ranges')

    def __str__(self):
        return self.user.username + ' - ' + self.stamp.company_name.company_name + ' - ' + self.range_invoice.start_number + ' - ' + self.range_invoice.end_number


auditlog.register(StampRange)


# ######################################## CREDIT NOTE STAMP RANGE
class CreditNoteStampRange(SoftDeleteObject, TimeStampModel):
    stamp = models.ForeignKey(CreditNoteStamp, on_delete=models.PROTECT, verbose_name=_('Credit Note Stamp'))
    range_credit_note = models.ForeignKey(CreditNoteRange, on_delete=models.PROTECT, verbose_name=_('CreditNote Range'))
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('User'))

    class Meta:
        verbose_name = _('Credit Note Stamp Range')
        verbose_name_plural = _('Credit Note Stamp Ranges')

    def __str__(self):
        return self.user.username + ' - ' + self.stamp.company_name.company_name + ' - ' + self.range_credit_note.start_number + ' - ' + self.range_credit_note.end_number


auditlog.register(CreditNoteStampRange)


class SifenTransaction(SoftDeleteObject, TimeStampModel):
    transaction_datetime = models.DateTimeField(
        verbose_name=_('Transaction Date Time'), auto_now=True, blank=False, null=False
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('User'))
    invoice_header = models.ForeignKey(
        to=InvoiceHeader, on_delete=models.CASCADE,
        verbose_name=_('Invoice Header'),
        null=True, blank=True,
        related_name='sifen_transactions'
    )
    credit_note_header = models.ForeignKey(
        to=CreditNoteHeader, on_delete=models.CASCADE,
        verbose_name=_('Credit Note Header'),
        null=True, blank=True,
        related_name='sifen_transactions'
    )
    url = models.URLField(verbose_name=_('URL'), blank=True, null=True)
    payload = models.JSONField(verbose_name=_('Payload'), blank=True, null=True)
    response = models.JSONField(verbose_name=_('Response'), blank=True, null=True)
    success = models.BooleanField(verbose_name=_('Success'), default=False)

    class Meta:
        verbose_name = _('Sifen Transaction')
        verbose_name_plural = _('Sifen Transactions')

    def __str__(self):
        return str(self.user) + ' - ' + self.transaction_datetime.strftime("%d/%m/%Y %H:%M")
