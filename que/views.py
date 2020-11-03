from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView

from que.decorators import is_teacher_required
from .auth_helper import get_sign_in_url, get_token_from_code, get_user
from .models import AuthorizedTeamsUser, QueueTicket, PastMeeting


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
    return redirect("logout")


def average_meeting_time():
    if len(PastMeeting.objects.all()) == 0:
        return 3
    durations = []
    for pm in PastMeeting.objects.all():
        if pm.duration:
            durations.append(pm.duration.seconds)
    average_duration = sum(durations) / len(durations) / 60
    print(average_duration)
    return min(max(average_duration, 2), 6)


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
        return StudentQueueView.as_view(teams_user=teams_user)(request)


class AnonymQueueView(TemplateView):
    template_name = "que/anonym.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["queue_length"] = max(QueueTicket.objects.count(), 0)
        context["estimated_time"] = context["queue_length"] * average_meeting_time()
        return context


class TeacherQueueView(ListView):
    template_name = "que/teacher.html"
    model = QueueTicket
    context_object_name = "queue"
    teams_user = None

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.teams_user
        if len(context["queue"]) > 0:  # creating a meeting for the 1st person in the queue
            context["startedAt"] = create_past_meeting(
                self.request, QueueTicket.objects.first().user
            ).started_at.isoformat()
        return context


class StudentQueueView(DetailView):
    template_name = "que/students.html"
    context_object_name = "student_ticket"
    teams_user = None

    def get_object(self, queryset=None):
        obj, _ = QueueTicket.objects.get_or_create(user=self.teams_user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["queue_position"] = context['student_ticket'].position_in_queue
        context["estimated_time"] = (
                context['student_ticket'].position_in_queue * average_meeting_time()
        )
        return context
