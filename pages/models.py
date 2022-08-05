from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify

User = get_user_model()


class Page(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.slug

    def get_links_count(self):
        return Link.objects.filter(page=self).count()


class Link(models.Model):
    page = models.ForeignKey('Page', on_delete=models.CASCADE)
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
