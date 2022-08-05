from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Page, Link
from django.template.defaultfilters import slugify
from .forms import PageForm, LinkForm


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


class PageView(TemplateView):
    template_name = 'pages/page.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['page'] = Page.objects.get(slug=kwargs['slug'])
            context['links'] = Link.objects.filter(
                page=context['page']).order_by('created_at')
            return context
        except Page.DoesNotExist:
            raise Http404("Page does not exist")

    def get(self, request, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))


class PageCreate(LoginRequiredMixin, TemplateView):
    template_name = 'pages/page_create.html'

    def get(self, request, **kwargs):
        form = PageForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, **kwargs):
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.user = request.user
            page.save()
            messages.success(request, 'Page created successfully')
            return redirect('page_detail', slug=page.slug)

        return render(request, self.template_name, {'form': form})


class PageUpdate(LoginRequiredMixin, TemplateView):
    template_name = 'pages/page_update.html'

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
    template_name = 'pages/page_delete.html'

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


class LinkCreate(LoginRequiredMixin, TemplateView):
    template_name = 'pages/link_create.html'

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
                messages.success(request, 'Link created successfully')
                return redirect('page_detail', slug=page.slug)
            return render(request, self.template_name, {'form': form, 'page': page})
        else:
            messages.error(
                request, 'You are not authorized to add links to this page')
            return redirect('page_detail', slug=page.slug)


class LinkUpdate(LoginRequiredMixin, TemplateView):
    template_name = 'pages/link_update.html'

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
    template_name = 'pages/link_delete.html'

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
