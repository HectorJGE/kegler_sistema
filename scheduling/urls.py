from django.urls import path
from scheduling.views import AppointmentListView, AppointmentListForCalendarView, AppointmentCalendarView, \
    AppointmentCreateView, AppointmentUpdateView, AppointmentCancelView, AppointmentDetailView, \
    AppointmentCheckEquipmentAvailabilityView, AppointmentCheckDoctorAvailabilityView, AppointmentsOfTheDayListView, \
    AppointmentDocumentPrintView

urlpatterns = [
    # Appointment
    path('appointment/calendar/', AppointmentCalendarView.as_view(), name='appointment.calendar'),
    path('appointment/list_for_calendar/', AppointmentListForCalendarView.as_view(), name='appointment.list_for_calendar'),
    path('appointment/list/', AppointmentListView.as_view(), name='appointment.list'),
    path('appointment/appointments_of_the_day_list/', AppointmentsOfTheDayListView.as_view(), name='appointment.list_appointments_of_the_day'),
    path('appointment/detail/<int:pk>/', AppointmentDetailView.as_view(), name='appointment.detail'),
    path('appointment/create/', AppointmentCreateView.as_view(), name='appointment.create'),
    path('appointment/update/<int:pk>/', AppointmentUpdateView.as_view(), name='appointment.update'),
    # path('appointment/delete/<int:pk>/', AppointmentDeleteView.as_view(), name='appointment.delete'),
    path('appointment/cancel_appointment/<int:pk>/', AppointmentCancelView.as_view(), name='appointment.cancel_appointment'),
    path('appointment/check_equipment_availability/', AppointmentCheckEquipmentAvailabilityView.as_view(), name='appointment.check_equipment_availability'),
    path('appointment/check_docor_availability/', AppointmentCheckDoctorAvailabilityView.as_view(), name='appointment.check_doctor_availability'),

    path('appointment_document/print_view/<int:pk>/', AppointmentDocumentPrintView.as_view(), name='appointment.document_print'),

]
