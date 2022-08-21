from django.contrib import admin
from .models import Page, Link, PageDecorator, LinkDecorator

# Register your models here.
admin.site.register(Page)
admin.site.register(Link)
admin.site.register(PageDecorator)
admin.site.register(LinkDecorator)
