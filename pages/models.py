from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from colorfield.fields import ColorField
from hitcount.models import HitCount
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

    def get_total_links_hits(self):
        links = Link.objects.filter(page=self)
        total_hits = 0
        for link in links:
            total_hits += HitCount.objects.get_for_object(link).hits
        return total_hits


class Link(models.Model):
    page = models.ForeignKey('Page', on_delete=models.CASCADE)
    url = models.URLField(max_length=255)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PageDecorator(models.Model):
    page = models.OneToOneField(
        'Page', on_delete=models.CASCADE, related_name='decorator')
    background_color = ColorField(default='#212529')
    text_color = ColorField(default='#FFFFFF')
    card_color = ColorField(default='#A5C9CA')
    show_date = models.BooleanField(default=True)

    def __str__(self):
        return self.page.slug


class LinkDecorator(models.Model):
    link = models.OneToOneField(
        'Link', on_delete=models.CASCADE, related_name='decorator')
    background_color = ColorField(default='#29292D')
    text_color = ColorField(default='#FFFFFF')

    def __str__(self):
        return self.link.name
