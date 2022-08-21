
from multiprocessing import context
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Page, Link, PageDecorator, LinkDecorator
from django.template.defaultfilters import slugify
from .forms import PageForm, LinkForm
from django.urls import reverse
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
import requests
import json


class IndexView(TemplateView):
    template_name = 'pages/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name)


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'pages/dashboard.html'

    def get(self, request, **kwargs):
        pages = Page.objects.filter(user=request.user).order_by('-created_at')
        return render(request, self.template_name, {'pages': pages})


class PageView(TemplateView, HitCountMixin):
    template_name = 'pages/page.html'
    count_hit = True

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        return requests.get(
            f'https://geolocation-db.com/json/{ip}&position=true').json()

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page'] = Page.objects.get(slug=kwargs['slug'])
            context['links'] = Link.objects.filter(
                page=context['page']).order_by('created_at')
            context['page_decorator'] = PageDecorator.objects.get_or_create(
                page=context['page'])[0]
            return context
        except Page.DoesNotExist:
            raise Http404("Page does not exist")

    def get(self, request, **kwargs):
        hit_count = HitCount.objects.get_for_object(
            self.get_context_data(**kwargs)["page"])
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
        return render(request, self.template_name, self.get_context_data(**kwargs))


class PageCreate(LoginRequiredMixin, TemplateView):
    template_name = 'pages/page_templates/page_create.html'

    def get(self, request, **kwargs):
        form = PageForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, **kwargs):
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.user = request.user
            page.save()
            page_decorator = PageDecorator(page=page)
            page_decorator.save()
            messages.success(request, 'Page created successfully')
            return redirect('page_customize', slug=page.slug)

        return render(request, self.template_name, {'form': form})


class PageUpdate(LoginRequiredMixin, TemplateView):
    template_name = 'pages/page_templates/page_update.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page'] = Page.objects.get(slug=kwargs['slug'])
            return context
        except Page.DoesNotExist:
            raise Http404("Page does not exist")

    def get(self, request, **kwargs):
        page = self.get_context_data(**kwargs)['page']
        if page.user == request.user:
            form = PageForm(instance=Page.objects.get(slug=kwargs['slug']))
            return render(request, self.template_name, {'form': form, 'page': page})
        else:
            messages.error(request, 'You are not authorized to edit this page')
            return redirect('page_detail', slug=page.slug)

    def post(self, request, **kwargs):
        page = self.get_context_data(**kwargs)['page']
        if page.user == request.user:
            form = PageForm(request.POST, instance=page)
            if form.is_valid():
                form.save()
                messages.success(request, 'Page updated successfully')
                return redirect('page_detail', slug=page.slug)
            return render(request, self.template_name, {'form': form, 'page': page})
        else:
            messages.error(request, 'You are not authorized to edit this page')
            return redirect('page_detail', slug=page.slug)


class PageDelete(LoginRequiredMixin, TemplateView):
    template_name = 'pages/page_templates/page_delete.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page'] = Page.objects.get(slug=kwargs['slug'])
            return context
        except Page.DoesNotExist:
            raise Http404("Page does not exist")

    def get(self, request, **kwargs):
        page = self.get_context_data(**kwargs)['page']
        if page.user == request.user:
            return render(request, self.template_name, {'page': page})
        else:
            messages.error(
                request, 'You are not authorized to delete this page')
            return redirect('page_detail', slug=page.slug)

    def post(self, request, **kwargs):
        page = self.get_context_data(**kwargs)['page']
        if page.user == request.user:
            page.delete()
            messages.success(request, 'Page deleted successfully')
            return redirect('index')
        else:
            messages.error(request, 'You are not allowed to delete this page')
            return redirect('page_detail', slug=page.slug)


class PageCustomize(LoginRequiredMixin, TemplateView):
    template_name = 'pages/page_templates/page_customize.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page'] = Page.objects.get(slug=kwargs['slug'])
            return context
        except Page.DoesNotExist:
            raise Http404("Page does not exist")

    def get(self, request, **kwargs):
        page = self.get_context_data(**kwargs)['page']
        if page.user == request.user:
            return render(request, self.template_name, self.get_context_data(**kwargs))
        else:
            messages.error(request, 'You are not authorized to edit this page')
            return redirect('page_detail', slug=page.slug)

    def post(self, request, **kwargs):
        page = self.get_context_data(**kwargs)['page']
        print(request.POST)
        if page.user == request.user:
            page_decorator = page.decorator
            page_decorator.background_color = request.POST['background_color']
            page_decorator.card_color = request.POST['card_color']
            page_decorator.text_color = request.POST['text_color']
            page_decorator.show_date = request.POST.get('show_date', False)
            page_decorator.save()
            messages.success(request, 'Page updated successfully')
            return redirect('page_detail', slug=page.slug)
        else:
            messages.error(request, 'You are not authorized to edit this page')
            return redirect('page_detail', slug=page.slug)


class LinkCreate(LoginRequiredMixin, TemplateView):
    template_name = 'pages/link_templates/link_create.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page'] = Page.objects.get(slug=kwargs['slug'])
            return context
        except Page.DoesNotExist:
            raise Http404("Page does not exist")

    def get(self, request, **kwargs):
        page = self.get_context_data(**kwargs)['page']
        if page.user == request.user:
            form = LinkForm()
            return render(request, self.template_name, {'form': form, 'page': page})
        else:
            messages.error(
                request, 'You are not authorized to add links to this page')
            return redirect('page_detail', slug=page.slug)

    def post(self, request, **kwargs):
        page = self.get_context_data(**kwargs)['page']
        if page.user == request.user:
            form = LinkForm(request.POST)
            if form.is_valid():
                link = form.save(commit=False)
                link.page = page
                link.save()
                link_decorator = LinkDecorator(link=link)
                link_decorator.save()
                messages.success(request, 'Link created successfully')
                return redirect('link_customize', slug=page.slug, id=link.pk)
            return render(request, self.template_name, {'form': form, 'page': page})
        else:
            messages.error(
                request, 'You are not authorized to add links to this page')
            return redirect('page_detail', slug=page.slug)


class LinkUpdate(LoginRequiredMixin, TemplateView):
    template_name = 'pages/link_templates/link_update.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['link'] = Link.objects.get(id=kwargs['id'])
            return context
        except Link.DoesNotExist:
            raise Http404("Link does not exist")

    def get(self, request, **kwargs):
        link = self.get_context_data(**kwargs)['link']
        if link.page.user == request.user:
            form = LinkForm(instance=link)
            return render(request, self.template_name, {'form': form, 'link': link})
        else:
            messages.error(
                request, 'You are not authorized to edit this link')
            return redirect('page_detail', slug=link.page.slug)

    def post(self, request, **kwargs):
        link = self.get_context_data(**kwargs)['link']
        if link.page.user == request.user:
            form = LinkForm(request.POST, instance=link)
            if form.is_valid():
                form.save()
                messages.success(request, 'Link updated successfully')
                return redirect('page_detail', slug=link.page.slug)
            return render(request, self.template_name, {'form': form, 'link': link})
        else:
            messages.error(
                request, 'You are not authorized to edit this link')
            return redirect('page_detail', slug=link.page.slug)


class LinkDelete(LoginRequiredMixin, TemplateView):
    template_name = 'pages/link_templates/link_delete.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['link'] = Link.objects.get(id=kwargs['id'])
            return context
        except Link.DoesNotExist:
            raise Http404("Link does not exist")

    def get(self, request, **kwargs):
        link = self.get_context_data(**kwargs)['link']
        if link.page.user == request.user:
            return render(request, self.template_name, {'link': link})
        else:
            messages.error(
                request, 'You are not authorized to delete this link')
            return redirect('page_detail', slug=link.page.slug)

    def post(self, request, **kwargs):
        link = self.get_context_data(**kwargs)['link']
        if link.page.user == request.user:
            link.delete()
            messages.success(request, 'Link deleted successfully')
            return redirect('page_detail', slug=link.page.slug)
        else:
            messages.error(
                request, 'You are not authorized to delete this link')
            return redirect('page_detail', slug=link.page.slug)


def not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


class LinkView(TemplateView, HitCountMixin):
    count_hit = True

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['link'] = Link.objects.get(id=kwargs['id'])
            return context
        except Link.DoesNotExist:
            raise Http404("Link does not exist")

    def get(self, request, **kwargs):
        link = self.get_context_data(**kwargs)['link']
        hit_count = HitCount.objects.get_for_object(link)
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
        return redirect(link.url)


class LinkCustomize(LoginRequiredMixin, TemplateView):
    template_name = 'pages/link_templates/link_customize.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page'] = Page.objects.get(slug=kwargs['slug'])
            context['link'] = Link.objects.get(id=kwargs['id'])
            return context
        except Link.DoesNotExist:
            raise Http404("Link does not exist")

    def get(self, request, **kwargs):
        link = self.get_context_data(**kwargs)['link']
        if link.page.user == request.user:
            return render(request, self.template_name, self.get_context_data(**kwargs))
        else:
            messages.error(
                request, 'You are not authorized to edit this link')
            return redirect('page_detail', slug=link.page.slug)

    def post(self, request, **kwargs):
        link = self.get_context_data(**kwargs)['link']
        if link.page.user == request.user:
            link_decorator = link.decorator
            link_decorator.background_color = request.POST['background_color']
            link_decorator.text_color = request.POST['text_color']
            link_decorator.save()
            messages.success(request, 'Page updated successfully')
        else:
            messages.error(
                request, 'You are not authorized to edit this link')
        return redirect('page_detail', slug=link.page.slug)
