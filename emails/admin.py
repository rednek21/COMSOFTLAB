from django.contrib import admin
from .models import File, EmailConfig, EmailMessage


admin.site.register(File)
admin.site.register(EmailConfig)
admin.site.register(EmailMessage)
