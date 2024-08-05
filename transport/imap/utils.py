import os
from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_to_datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from emails.models import EmailMessage, File
from emails.serializers import EmailMessageSerializer


def process_email_message(msg, imap_client):
    got_from = msg['From'].split(' ')
    got_from_user = imap_client.decode_mime_string(got_from[0]) if len(got_from) > 1 else got_from[0]
    got_from_email = (' ' + got_from[1][1:-1]) if len(got_from) > 1 else ''
    got_from = got_from_user + got_from_email
    subject = decode_header(msg['Subject'])[0][0].decode() if msg['Subject'] else None
    date = parsedate_to_datetime(msg['Date'])

    if EmailMessage.objects.filter(subject=subject, date_sent=date).exists():
        return None, None

    body = None
    attachments = []
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode('utf-8')
        if part.get_content_disposition() == 'attachment':
            file_name = imap_client.decode_mime_string(part.get_filename())
            unique_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            unique_file_name = f"{unique_id}_{file_name}"

            file_content = part.get_payload(decode=True)
            folder = 'email_files'
            folder_path = os.path.join(settings.MEDIA_ROOT, folder)
            os.makedirs(folder_path, exist_ok=True)

            path = default_storage.save(os.path.join(folder, unique_file_name), ContentFile(file_content))
            file_url = default_storage.url(path)

            file = File(name=unique_file_name, file_url=file_url)
            file.save()
            attachments.append(file)

    body = body if body else None
    email_message = EmailMessage(got_from=got_from, subject=subject,
                                 date_sent=date, date_received=date,
                                 body=body)
    email_message.save()
    email_message.attachments.set(attachments)
    return email_message, attachments


def send_email_notification(email_message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'emails_group',
        {
            'type': 'email_message',
            'message': EmailMessageSerializer(email_message).data
        }
    )
