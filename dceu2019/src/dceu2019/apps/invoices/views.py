import os

from dceu2019.apps.ticketholders.decorators import login_required
from django.http.response import FileResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.list import ListView

from . import models


class TicketList(ListView):

    model = models.TicketbutlerTicket
    template_name = "invoices/ticket_list.html"
    context_object_name = "tickets"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return ListView.dispatch(self, request, *args, **kwargs)

    def get_queryset(self):
        return ListView.get_queryset(self).filter(user=self.request.user)


class FetchInvoicePDF(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):

        invoice_id = kwargs.get("invoice_id")

        invoice = models.Invoice.objects.get(id=invoice_id, tickets__user=request.user)

        file_name = invoice.billy_id + ".pdf"
        pdf_path = os.path.join(
            os.path.dirname(__file__), "pdfs", file_name
        )
        return FileResponse(open(pdf_path, "rb"), as_attachment=True, filename=file_name)
