from django.urls import path

from . import views

app_name = 'invoices'


urlpatterns = [
    path('tickets/', views.TicketList.as_view(), name='ticket_list'),
    path('tickets/<int:invoice_id>/', views.FetchInvoicePDF.as_view(), name='ticket_invoice'),
]
