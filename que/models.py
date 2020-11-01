import jsonfield
from django.db import models


class Queue(models.Model):
    name = models.CharField(max_length=150)


class AuthorizedTeamsUser(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    principal_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    token = jsonfield.JSONField(null=True, blank=True)
