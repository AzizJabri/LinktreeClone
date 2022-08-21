from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("password_change/", PasswordChangeView.as_view(
        template_name="users/password_change.html"), name="password_change"),
    path("password_change/done/", PasswordChangeDoneView.as_view(
        template_name="users/password_change_done.html"), name="password_change_done"),
    path("password_reset/", PasswordResetView.as_view(
         html_email_template_name="users/password_reset_email.html", template_name="users/password_reset.html"), name="password_reset"),
    path("password_reset/done/", PasswordResetDoneView.as_view(
        template_name="users/password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(post_reset_login=True,
                                                                     template_name="users/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", PasswordResetCompleteView.as_view(
        template_name="users/password_reset_complete.html"), name="password_reset_complete"),

]
