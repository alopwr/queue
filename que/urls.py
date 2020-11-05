from django.urls import path

from . import views

#
# def login_as_cieplucha(request):
#     """only for testing purposes"""
#     request.session['userId'] = 1
#     request.session['userPrincipalName'] = "g@g.pl"
#     return redirect("que")


urlpatterns = [
    path("", views.queue_view_dispatcher, name="que"),
    path("next", views.next_view, name="next"),
    path("not_in_queue", views.next_view, name="next"),
    path("clear", views.clear_view, name="clear"),
    path("cancel", views.cancel_view, name="cancel"),
    path("login", views.sign_in, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("ticket/create", views.create_view, name='create'),
    # path("cieplucha", login_as_cieplucha),
]
