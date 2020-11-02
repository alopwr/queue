import jsonfield
from django.db import models


class PrincipalName(models.Model):
    name = models.EmailField()

    def __str__(self):
        return self.name


class AuthorizedTeamsUser(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    principal_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    token = jsonfield.JSONField(null=True, blank=True)

    @property
    def is_teacher(self):
        try:
            PrincipalName.objects.get(name=self.principal_name)
            return True
        except:
            return False

    def __str__(self):
        return self.principal_name


class QueueTicket(models.Model):
    user = models.ForeignKey(AuthorizedTeamsUser, on_delete=models.CASCADE)
    in_queue_since = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["in_queue_since"]

    def __str__(self):
        return self.user.display_name + " since " + str(self.in_queue_since)
