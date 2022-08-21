from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from .managers import CustomUserManager
from django.template.defaultfilters import slugify
from datetime import datetime
from PIL import Image
from .custom_fields import CountryField
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
        super(Profile, self).save(*args, **kwargs)
        if not self.username:
            self.username = slugify(
                self.user.first_name + ' ' + self.user.last_name + ' ' + str(self.id))
            self.save()

        img = Image.open(self.avatar.path)
        if img.width > img.height:
            x = (img.width / 2) - (img.height / 2)
            box = (x, 0, x + img.height, img.height)
            cropped_image = img.crop(box)
            if cropped_image.height > 500 or cropped_image.width > 500:
                new_image = cropped_image.resize((500, 500))
                new_image.save(self.avatar.path)
        elif img.width < img.height:
            x = (img.height / 2) - (img.width / 2)
            box = (0, x, img.width, x + img.width)
            cropped_image = img.crop(box)
            if cropped_image.height > 500 or cropped_image.width > 500:
                new_image = cropped_image.resize((500, 500))
                new_image.save(self.avatar.path)
        else:
            image = img.resize((500, 500))
            image.save(self.avatar.path)
