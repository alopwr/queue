from django.contrib import admin

# Register your models here.
from .models import AuthorizedTeamsUser, QueueTicket, PrincipalName, PastMeeting

admin.site.register(AuthorizedTeamsUser)
admin.site.register(QueueTicket)
admin.site.register(PrincipalName)
admin.site.register(PastMeeting)
