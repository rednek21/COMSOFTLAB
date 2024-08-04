from django.urls import path
from .api import FetchEmailsView, EmailListView
from .views import EmailsView

urlpatterns = [
    path('fetch-emails/', FetchEmailsView.as_view(), name='fetch_emails'),
    path('emails-list/', EmailListView.as_view(), name='email_list'),

    path('emails/', EmailsView.as_view(), name='emails'),
]
