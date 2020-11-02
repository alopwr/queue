from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden


def is_teacher_required(view_func):
    @wraps(view_func)
    def _required(request, *args, **kwargs):
        if (
            request.session.get("userPrincipalName", "")
            in settings.TEACHERS_PRINCIPAL_NAMES
        ):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    return _required
