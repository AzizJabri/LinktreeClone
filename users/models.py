from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from .managers import CustomUserManager

# create custom user model


class User(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email
