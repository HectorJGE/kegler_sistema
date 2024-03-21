from django.urls import path, include
from django.contrib.auth import views as auth_views

# Base
import stock
from base import views
from base.views import DashboardView, DataTablesTranslationsJsonView

# Clinic
import clinic
from clinic import urls

# Scheduling
import scheduling
from scheduling import urls

# Consultation
import consultation
from consultation import urls

# Stock
import stock
from stock import urls

# Invoicing
import invoicing
from invoicing import urls

# Reports
import reports.urls


urlpatterns = [
    # Base URLs
    path('login/', views.Login.as_view(), name='login'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Datatables translation
    path('datatables_translation', DataTablesTranslationsJsonView.as_view(), name='datatables_translation'),

    # Clinic URLs
    path('clinic/', include(clinic.urls)),

    # Scheduling URLs
    path('scheduling/', include(scheduling.urls)),

    # Consultation URLs
    path('consultation/', include(consultation.urls)),

    # Stock URLs
    path('stock/', include(stock.urls)),

    # Invoicing URLs
    path('invoicing/', include(invoicing.urls)),

    # Reports URLs
    path('reports/', include(reports.urls)),

]
