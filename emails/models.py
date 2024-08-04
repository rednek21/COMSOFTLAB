from django.conf import settings
from django.db import models


class EmailConfig(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=64)
    server = models.CharField(max_length=128)
    port = models.PositiveIntegerField()

    # Реализованный Singleton для хранения единственной конфигурации
    #
    # def save(self, *args, **kwargs):
    #     self.__class__.objects.exclude(id=self.id).delete()
    #     super(EmailConfig, self).save(*args, **kwargs)


class File(models.Model):
    name = models.CharField(max_length=64)
    file_url = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class EmailMessage(models.Model):
    got_from = models.CharField(max_length=128)
    subject = models.CharField(max_length=64, null=True, blank=True)
    date_sent = models.DateTimeField()
    date_received = models.DateTimeField()
    body = models.TextField(null=True, blank=True)
    attachments = models.ManyToManyField(File)

    def __str__(self):
        return self.got_from
