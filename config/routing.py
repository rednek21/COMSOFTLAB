from django.urls import path

from emails import consumers

websocket_urlpatterns = [
    path('ws/emails/', consumers.EmailConsumer.as_asgi()),
]
