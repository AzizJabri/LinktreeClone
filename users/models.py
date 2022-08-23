from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from .managers import CustomUserManager
from django.template.defaultfilters import slugify
from datetime import datetime
from PIL import Image
from .custom_fields import CountryField
from .utils import image_resize
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


class Profile(models.Model):
    def change_avatar_name(instance, filename):
        return 'avatars/' + str(instance.user.uuid) + '.' + filename.split('.')[-1]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    username = models.SlugField(max_length=255, blank=False, unique=True)
    bio = models.TextField(max_length=500, blank=True)
    location = CountryField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(
        upload_to=change_avatar_name, blank=False, default='default.jpg')

    def __str__(self) -> str:
        return self.user.email

    def save(self, *args, **kwargs):
        new_width = 300
        new_height = 300
        if self.avatar:
            image_resize(self.avatar, new_width, new_height)
        # run save of parent class above to save original image to disk
        super().save(*args, **kwargs)
