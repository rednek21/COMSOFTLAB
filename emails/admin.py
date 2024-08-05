from django.contrib import admin

from .models import EmailConfig, EmailMessage, File

admin.site.register(File)
admin.site.register(EmailConfig)
admin.site.register(EmailMessage)
