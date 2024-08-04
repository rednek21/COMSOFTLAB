import base64
import email
import os
from email.header import decode_header
from email.utils import parsedate_to_datetime
import logging
from imaplib import IMAP4_SSL
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmailConfig, EmailMessage, File
from .serializers import EmailMessageSerializer

logger = logging.getLogger(__name__)


class FetchEmailsView(APIView):
    @staticmethod
    def decode_mime_string(mime_str):
        parts = mime_str.split('?')

        charset = parts[1]
        encoding = parts[2]
        encoded_text = parts[3]

        if encoding.upper() == 'B':
            decoded_bytes = base64.b64decode(encoded_text)
        else:
            raise ValueError

        decoded_str = decoded_bytes.decode(charset)
        return decoded_str

    def get(self, request):
        config = EmailConfig.objects.first()
        if not config:
            return Response({'error': 'Email configuration not found.'}, status=status.HTTP_404_NOT_FOUND)

        mail = IMAP4_SSL(config.server, config.port)
        mail.login(config.email, config.password)
        mail.select('inbox')

        typ, data = mail.search(None, 'ALL')
        msgs = data[0].split()[-10:]  # Кринж (пояснение дальше)

        # Загружать все сообщения разом - не совсем оправдано с т.з. нагрузки на сеть и времени ожидания
        # с реализаций скачивания определенного количества сообщений не разобрался.
        # Скачивать все и отсекать некоторое количество - буэээ :)
        # Ограничение на последние 10 непрочитанных сообщений, веротяно улучшит ситуацию,
        # но все упирается в потребности клиента/компании
        # Может не спасти
        # typ, data = mail.search(None, '(UNSEEN)')
        # msgs = data[0].split()

        messages = []
        for id in msgs:
            typ, msg = mail.fetch(id, '(RFC822)')
            msg = email.message_from_bytes(msg[0][1])

            got_from = msg['From'].split(' ')
            got_from_user = self.decode_mime_string(got_from[0]) if len(got_from) > 1 else got_from[0]
            got_from_email = (' ' + got_from[1][1:-1]) if len(got_from) > 1 else ''
            got_from = got_from_user + got_from_email
            subject = decode_header(msg['Subject'])[0][0].decode() if msg['Subject'] else None
            date = parsedate_to_datetime(msg['Date'])

            # Проверка на существование сообщения в БД. Защита от создания n-количества копий при перезапуске страницы
            if EmailMessage.objects.filter(subject=subject, date_sent=date).exists():
                continue

            attachments = []
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8')
                if part.get_content_disposition() == 'attachment':
                    file_name = self.decode_mime_string(part.get_filename())
                    if File.objects.filter(name=file_name).exists():
                        continue
                    else:
                        file_content = part.get_payload(decode=True)

                        folder = 'email_files'
                        folder_path = os.path.join(settings.MEDIA_ROOT, folder)
                        os.makedirs(folder_path, exist_ok=True)

                        path = default_storage.save(os.path.join(folder, file_name), ContentFile(file_content))
                        file_url = default_storage.url(path)

                        file = File(name=file_name, file_url=file_url)
                        file.save()
                        attachments.append(file)

            body = body if body else None
            email_message = EmailMessage(got_from=got_from, subject=subject,
                                         date_sent=date, date_received=date,
                                         body=body)
            email_message.save()
            email_message.attachments.set(attachments)
            messages.append(email_message)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'emails_group',
                {
                    'type': 'email_message',
                    'message': EmailMessageSerializer(email_message).data
                }
            )

        serializer = EmailMessageSerializer(messages, many=True)
        logger.info('Fetched emails successfully')
        return Response(serializer.data)


class EmailListView(APIView):
    def get(self, request):
        messages = EmailMessage.objects.all()
        serializer = EmailMessageSerializer(messages, many=True)
        logger.info('Retrieved email list successfully')
        return Response(serializer.data)
