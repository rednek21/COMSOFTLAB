from rest_framework import routers

from .views import EmailListView, FetchEmailsView

router = routers.SimpleRouter()
router.register(r'fetch-emails', FetchEmailsView, basename='fetch-emails')
router.register(r'emails-list', EmailListView, basename='emails-list')
