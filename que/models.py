from django.db import models


class Queue(models.Model):
    name = models.CharField(max_length=150)


class Person(models.Model):
    name = models.CharField(max_length=150)
    in_queue_from = models.DateTimeField(auto_now_add=True)
