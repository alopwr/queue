import jsonfield
from django.conf import settings
from django.db import models


class AuthorizedTeamsUser(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    principal_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    token = jsonfield.JSONField(null=True, blank=True)

    @property
    def is_teacher(self):
        return self.principal_name in settings.TEACHERS_PRINCIPAL_NAMES


class QueueTicket(models.Model):
    user = models.ForeignKey(AuthorizedTeamsUser, on_delete=models.CASCADE)
    in_queue_since = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['in_queue_since']
