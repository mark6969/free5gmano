from django.db import models
from django.contrib.auth.models import User as us
from django.contrib.auth.models import AbstractUser


class User(us):
    role = models.CharField(max_length=20, default='user')
