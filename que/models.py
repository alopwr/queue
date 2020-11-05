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
        except PrincipalName.DoesNotExist:
            return False

    def __str__(self):
        return self.principal_name


class QueueTicket(models.Model):
    user = models.ForeignKey(AuthorizedTeamsUser, on_delete=models.CASCADE, unique=True)
    in_queue_since = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["in_queue_since"]

    def __str__(self):
        return self.user.display_name + " since " + str(self.in_queue_since)

    @property
    def position_in_queue(self):
        position = 0
        for ticket in QueueTicket.objects.order_by():
            if ticket == self:
                return position
            position += 1


class PastMeeting(models.Model):
    teacher = models.ForeignKey(
        AuthorizedTeamsUser, on_delete=models.CASCADE, related_name="teacher"
    )
    student = models.ForeignKey(
        AuthorizedTeamsUser, on_delete=models.CASCADE, related_name="student"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    @property
    def duration(self):
        if not self.finished_at:
            return None
        return self.finished_at - self.started_at


def average_meeting_time():
    if not PastMeeting.objects.exists():
        return 6
    if len(PastMeeting.objects.all()) == 0:
        return 3
    durations = []
    for pm in PastMeeting.objects.all():
        if pm.duration:
            durations.append(pm.duration.seconds)
    average_duration = sum(durations) / len(durations) / 60
    return min(max(average_duration, 2), 6)
