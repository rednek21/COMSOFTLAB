from celery import shared_task

from .api.views import FetchEmailsView


@shared_task
def fetch_emails_task():
    fetch_view = FetchEmailsView()
    fetch_view.list(None)
