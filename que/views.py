from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import DetailView

from que.decorators import is_teacher_required
from .auth_helper import get_sign_in_url, get_token_from_code, get_user
from .models import AuthorizedTeamsUser, QueueTicket, PrincipalName, PastMeeting


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
        finished_meeting = PastMeeting.objects.update(
            teacher=AuthorizedTeamsUser.objects.get(
                principal_name=request.session["userPrincipalName"]
            ),
            student=finished_ticket.user,
            finished_at=timezone.now(),
        )
        finished_ticket.delete()
    now_starting_meeting = QueueTicket.objects.first()
    if now_starting_meeting is not None:
        create_past_meeting(request, now_starting_meeting.user)
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
    return redirect("que")


def cancel_view(request):
    student = AuthorizedTeamsUser.objects.get(
        principal_name=request.session.get("userPrincipalName")
    )
    student_ticket = QueueTicket.objects.get(user=student)
    student_ticket.delete()
    return redirect("que")


class QueueView(DetailView):
    def get_template_names(self):
        if self.request.session.get("userPrincipalName", None) is None:
            return ["que/anonym.html"]
        try:
            PrincipalName.objects.get(name=self.request.session["userPrincipalName"])
            return ["que/teacher.html"]
        except:
            return ["que/students.html"]

    def get_object(self, queryset=None):
        try:
            return AuthorizedTeamsUser.objects.get(
                id=self.request.session["userId"],
                principal_name=self.request.session["userPrincipalName"],
            )
        except:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context["object"] is None:
            context["queue_length"] = max(QueueTicket.objects.count() - 1, 0)
            context["estimated_time"] = context["queue_length"] * 5
        elif context["object"].is_teacher:
            context["queue"] = QueueTicket.objects.all()
            # creating a meeting for the 1st person in the queue
            if len(context["queue"]) > 0:
                create_past_meeting(self.request, QueueTicket.objects.first().user)
        else:  # user is a student
            student = AuthorizedTeamsUser.objects.get(
                principal_name=self.request.session.get("userPrincipalName")
            )
            try:
                student_ticket = QueueTicket.objects.get(user=student)
            except:
                student_ticket = QueueTicket.objects.create(user=student)
            context["queue_position"] = student_ticket.position_in_queue
            context["estimated_time"] = student_ticket.position_in_queue * 5
        return context
