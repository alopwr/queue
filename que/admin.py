from django.contrib import admin

# Register your models here.
from .models import AuthorizedTeamsUser, QueueTicket, PrincipalName, PastMeeting

admin.site.register(AuthorizedTeamsUser)
admin.site.register(QueueTicket)
admin.site.register(PrincipalName)


class PastMeetingAdmin(admin.ModelAdmin):
    readonly_fields = ("started_at",)


admin.site.register(PastMeeting, PastMeetingAdmin)
