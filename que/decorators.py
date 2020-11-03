from functools import wraps

from django.http import HttpResponseForbidden

from que.models import PrincipalName


def is_teacher_required(view_func):
    @wraps(view_func)
    def _required(request, *args, **kwargs):
        try:
            PrincipalName.objects.get(name=request.session.get("userPrincipalName", ""))
            return view_func(request, *args, **kwargs)
        except PrincipalName.DoesNotExist:
            return HttpResponseForbidden()

    return _required
