from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView

from que.decorators import is_teacher_required
from .auth_helper import get_sign_in_url, get_token_from_code, get_user
from .models import AuthorizedTeamsUser, QueueTicket, PastMeeting, average_meeting_time
from webpush import send_group_notification

channel_layer = get_channel_layer()


def sign_in(request):
    sign_in_url, state = get_sign_in_url(request)
    # Save the expected state so we can validate in the callback
    request.session["auth_state"] = state
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(sign_in_url)


def logout(request):
    request.session.flush()
    return redirect("que")


def callback(request):
    # Get the state saved in session
    expected_state = request.session.pop("auth_state", "")
    # Make the token request
    token = get_token_from_code(request, expected_state)
    # Get the user's profile
    user = get_user(token)
    if user["userPrincipalName"] == "gaspar.sekula.2019@zsa.pwr.edu.pl":
        user["displayName"] += " 🤓🤓"
    AuthorizedTeamsUser.objects.update_or_create(
        id=user["id"],
        defaults={
            "display_name": user["displayName"],
            "principal_name": user["userPrincipalName"],
            "title": user["jobTitle"],
            "token": token,
        },
    )
    request.session["userId"] = user["id"]
    request.session["userPrincipalName"] = user["userPrincipalName"]
    return redirect("que")


@is_teacher_required
def next_view(request):
    finished_ticket = QueueTicket.objects.first()
    if finished_ticket is not None:
        PastMeeting.objects.filter(
            finished_at__isnull=True,
            teacher__principal_name=request.session["userPrincipalName"],
            student=finished_ticket.user,
        ).update(finished_at=timezone.now())
        finished_ticket.delete()
    now_starting_meeting = QueueTicket.objects.first()
    if now_starting_meeting is not None:
        create_past_meeting(request, now_starting_meeting.user)
    async_to_sync(channel_layer.group_send)(
        "students", {"type": "queue.next", "average": average_meeting_time(),}
    )
    return redirect("que")


def create_past_meeting(request, student):
    obj, _ = PastMeeting.objects.filter(finished_at__isnull=True).get_or_create(
        teacher=AuthorizedTeamsUser.objects.get(
            principal_name=request.session["userPrincipalName"]
        ),
        student=student,
    )
    return obj


@is_teacher_required
def clear_view(request):
    QueueTicket.objects.all().delete()
    PastMeeting.objects.filter(finished_at__isnull=True).delete()
    async_to_sync(channel_layer.group_send)("students", {"type": "queue.cleared",})
    return redirect("que")


def cancel_view(request):
    ticket = QueueTicket.objects.get(
        user__principal_name=request.session.get("userPrincipalName")
    )
    principal_name = ticket.user.principal_name
    position = ticket.position_in_queue
    ticket.delete()
    async_to_sync(channel_layer.group_send)(
        "queue_listeners",
        {
            "type": "queue.ticket_deleted",
            "position": position,
            "principal_name": principal_name,
            "average": average_meeting_time(),
        },
    )
    return redirect("que")


def create_view(request):
    obj, created = QueueTicket.objects.get_or_create(user_id=request.session["userId"])
    if created:
        async_to_sync(channel_layer.group_send)(
            "teachers",
            {
                "type": "queue.ticket_appended",
                "display_name": obj.user.display_name,
                "principal_name": obj.user.principal_name,
                "average": average_meeting_time(),
            },
        )
    return redirect("que")


def queue_view_dispatcher(request):
    try:
        teams_user = AuthorizedTeamsUser.objects.get(
            id=request.session["userId"],
            principal_name=request.session["userPrincipalName"],
        )
    except:
        return AnonymQueueView.as_view()(request)
    if teams_user.is_teacher:
        return TeacherQueueView.as_view(teams_user=teams_user)(request)
    else:
        try:
            ticket = QueueTicket.objects.get(user=teams_user)
            return StudentQueueView.as_view(ticket=ticket)(request)
        except QueueTicket.DoesNotExist:
            return StudentNotInQueueView.as_view()(request)


class AnonymQueueView(TemplateView):
    template_name = "que/anonym.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["queue_length"] = max(QueueTicket.objects.count(), 0)
        context["estimated_time"] = context["queue_length"] * average_meeting_time() + 1
        return context


class TeacherQueueView(ListView):
    template_name = "que/teacher.html"
    model = QueueTicket
    context_object_name = "queue"
    teams_user = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = self.teams_user
        webpush = {"group": self.teams_user.principal_name}
        context["webpush"] = webpush
        if (
            len(context["queue"]) > 0
        ):  # creating a meeting for the 1st person in the queue
            context["startedAt"] = create_past_meeting(
                self.request, QueueTicket.objects.first().user
            ).started_at.isoformat()
        return context


class StudentNotInQueueView(TemplateView):
    template_name = "que/student_not_in_queue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["queue_length"] = max(QueueTicket.objects.count(), 0)
        context["estimated_time"] = context["queue_length"] * average_meeting_time() + 1
        return context


class StudentQueueView(DetailView):
    template_name = "que/students.html"
    context_object_name = "student_ticket"
    ticket = None

    def get_object(self, queryset=None):
        return self.ticket

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["queue_position"] = context["student_ticket"].position_in_queue
        webpush = {"group": context["student_ticket"].user.principal_name}
        context["webpush"] = webpush
        if context["queue_position"] == 0:
            try:
                payload = {
                    "head": "Twoja kolej!",
                    "body": "Za moment pan Walczyński zadzwoni na Teamsach.",
                    "icon": "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/microsoft/209/black-telephone_260e.png",
                }
                send_group_notification(
                    group_name=context["student_ticket"].user.principal_name,
                    payload=payload,
                    ttl=1000,
                )
            except:
                pass
            if QueueTicket.objects.count() == 1:
                try:
                    payload = {
                        "head": "Nowy oczekujący",
                        "body": "{} prosi o połączenie.".format(
                            context["student_ticket"].user.display_name
                        ),
                        "icon": "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/microsoft/209/black-telephone_260e.png",
                    }
                    send_group_notification(
                        group_name="maciej.walczynski@zsa.pwr.edu.pl",
                        payload=payload,
                        ttl=1000,
                    )
                except:
                    pass
        context["estimated_time"] = (
            context["student_ticket"].position_in_queue * average_meeting_time()
        )
        return context
