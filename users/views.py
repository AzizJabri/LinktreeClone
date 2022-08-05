from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import *
from django.views.generic import TemplateView
from django.views import View
from django.conf import settings
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginView(TemplateView):

    template_name = 'users/login.html'

    def user_exists(self, email):
        return User.objects.filter(email=email).exists()

    def post(self, request, **kwargs):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if not self.user_exists(email):
                messages.error(request, 'User with this email does not exist')
            else:
                user = authenticate(email=email, password=password)
                if user is not None and user.is_active:
                    login(request, user)
                    messages.success(request, 'Logged in successfully !')
                    return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
                else:
                    messages.error(request, 'Invalid email or password')
                    return render(request, self.template_name, {'form': form})
        return render(request, self.template_name, {'form': form})

    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        form = LoginForm()
        return render(request, self.template_name, {'form': form})


class LogoutView(TemplateView):

    template_name = 'pages/index.html'

    def get(self, request, **kwargs):

        logout(request)
        return redirect(settings.LOGIN_URL)


class RegisterView(View):

    template_name = 'users/register.html'

    def get(self, request, **kwargs):
        form = RegisterForm()
        if request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.template_name, {'form': form})

    def post(self, request, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f'Registered successfully ! You are now logged in as {user.email}')
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.template_name, {'form': form})
