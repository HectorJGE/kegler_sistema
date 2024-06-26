from django.db import models
from django.utils.translation import ugettext_lazy as _


# store report requests for testing, used by ReportBro Designer
# for preview of pdf and xlsx
class ReportRequest(models.Model):
    key = models.CharField(max_length=36)
    report_definition = models.TextField()
    data = models.TextField()
    is_test_data = models.BooleanField()
    pdf_file = models.BinaryField(null=True)
    pdf_file_size = models.IntegerField(null=True)
    created_on = models.DateTimeField()

    class Meta:
        verbose_name = _("Report Request")
        verbose_name_plural = _("Reports Requests")


# report definition for our album report which is used for printing
# the pdf with the album list. When the report is saved
# in ReportBro Designer it will be stored in this table.
class ReportDefinition(models.Model):
    report_definition = models.TextField()
    report_type = models.CharField(max_length=30)
    remark = models.TextField(null=True)
    last_modified_at = models.DateTimeField()

    class Meta:
        verbose_name = _("Report Definition")
        verbose_name_plural = _("Reports Definitions")

    def __str__(self):
        desc = self.report_type
        if self.remark:
            desc += ', ' + self.remark
        desc += ' (' + str(self.last_modified_at) + ')'
        return desc