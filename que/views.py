from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import DetailView

from que.decorators import is_teacher_required
from .auth_helper import get_sign_in_url, get_token_from_code, get_user
from .models import AuthorizedTeamsUser, QueueTicket


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
    first = QueueTicket.objects.first()
    if first is not None:
        first.delete()
    return redirect("que")


@is_teacher_required
def clear_view(request):
    QueueTicket.objects.all().delete()
    return redirect("que")


class QueueView(DetailView):
    def get_template_names(self):
        if self.request.session.get("userPrincipalName", None) is None:
            return ["que/anonym.html"]
        elif (
            self.request.session["userPrincipalName"]
            in settings.TEACHERS_PRINCIPAL_NAMES
        ):
            return ["que/teacher.html"]
        else:
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
        elif context["object"].is_teacher:
            context["queue"] = QueueTicket.objects.all()
        else:
            pass
        return context
