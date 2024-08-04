from django.views.generic import TemplateView


class EmailsView(TemplateView):
    template_name = 'emails/email_list.html'
