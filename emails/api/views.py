import logging

from rest_framework import status, viewsets
from rest_framework.response import Response

from emails.models import EmailConfig, EmailMessage
from emails.serializers import EmailMessageSerializer
from transport.imap.imap_client import IMAPClient
from transport.imap.utils import process_email_message, send_email_notification

logger = logging.getLogger(__name__)


class FetchEmailsView(viewsets.ViewSet):
    def list(self, request):
        config = EmailConfig.objects.first()
        if not config:
            return Response({'error': 'Email configuration not found.'}, status=status.HTTP_404_NOT_FOUND)

        imap_client = IMAPClient(config.server, config.port, config.email, config.password)
        imap_client.login()
        imap_client.select('inbox')

        last_email = EmailMessage.objects.all().first()
        since_date = last_email.date_sent if last_email else None
        email_ids = imap_client.search_emails(since_date)

        messages = []
        for email_id in email_ids:
            msg = imap_client.fetch_email(email_id)
            email_message, attachments = process_email_message(msg, imap_client)
            if email_message:
                send_email_notification(email_message)
                messages.append(email_message)

        serializer = EmailMessageSerializer(messages, many=True)
        return Response({
            "total": len(messages),
            "data": serializer.data
        })


class EmailListView(viewsets.ReadOnlyModelViewSet):
    queryset = EmailMessage.objects.all()
    serializer_class = EmailMessageSerializer
