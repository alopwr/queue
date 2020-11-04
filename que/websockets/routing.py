from django.urls import re_path

from . import consumers

urls = [
    re_path(r'ws/teacher/$', consumers.TeacherConsumer.as_asgi()),
    re_path(r'ws/students/$', consumers.StudentConsumer.as_asgi()),
]
