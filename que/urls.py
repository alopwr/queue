from django.urls import path

from . import views

urlpatterns = [
    path("", views.QueueView.as_view(), name='que'),
    path("login", views.sign_in, name='login'),
    path("logout", views.logout, name='logout'),
    path("callback", views.callback, name='callback'),
]
