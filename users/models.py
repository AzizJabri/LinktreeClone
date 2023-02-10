from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from .managers import CustomUserManager
from django.template.defaultfilters import slugify
from datetime import datetime
from PIL import Image
from .custom_fields import CountryField
from .utils import resize_image
# create custom user model
import cloudinary


class LongerImageField(models.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2048)
        super(LongerImageField, self).__init__(*args, **kwargs)


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
        return 'avatars/' + str(instance.user.uuid) + "/" + "img" + '.' + filename.split('.')[-1]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    username = models.SlugField(max_length=255, blank=False, unique=True)
    bio = models.TextField(max_length=500, blank=True)
    location = CountryField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = LongerImageField(
        upload_to=change_avatar_name, blank=False, default='default_ibxmy4.jpg')

    def __str__(self) -> str:
        return self.user.email

    def get_avatar_url(self):
        return self.transform_avatar_url(self.avatar.url)

    def transform_avatar_url(self, url):
        transformations = 'w_300,c_fill,ar_1:1'
        parts = url.split('upload/')
        transformed_url = parts[0] + 'upload/' + \
            transformations + '/' + parts[1]
        return transformed_url


"""

https://res.cloudinary.com/dpvdcwtff/image/upload/v1/media/https://res.cloudinary.com/dpvdcwtff/image/upload/w_300%2Cc_fill%2Car_1:1/v1/media/avatars/ebc28c49-d215-41b1-bb2a-16c982c0d0aa/img_lyyuld

"""
