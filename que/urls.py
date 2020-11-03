from django.urls import path

from . import views

urlpatterns = [
    path("", views.queue_view_dispatcher, name="que"),
    path("next", views.next_view, name="next"),
    path("clear", views.clear_view, name="clear"),
    path("cancel", views.cancel_view, name="cancel"),
    path("login", views.sign_in, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
]
