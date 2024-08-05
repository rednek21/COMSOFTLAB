from django.urls import path

from .views import EmailsView

urlpatterns = [
    path('emails/', EmailsView.as_view(), name='emails'),
]
