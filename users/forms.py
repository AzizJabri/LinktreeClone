from .custom_fields import COUNTRIES
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm
import unicodedata
from .models import Profile

UserModel = get_user_model()


def _unicode_ci_compare(s1, s2):
    """
    Perform case-insensitive comparison of two identifiers, using the
    recommended algorithm from Unicode Technical Report 36, section
    2.11.2(B)(2).
    """
    return (
        unicodedata.normalize("NFKC", s1).casefold()
        == unicodedata.normalize("NFKC", s2).casefold()
    )


class RegisterForm(UserCreationForm):
    # fields we want to include and customize in our form
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           }))
    first_name = forms.CharField(max_length=100, min_length=4,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                               'class': 'form-control',
                                                               }))
    last_name = forms.CharField(max_length=100, min_length=4,
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name',
                                                              'class': 'form-control',
                                                              }))
    password1 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))
    password2 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password1',
                                                                  }))

    class Meta:
        model = UserModel
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']


class LoginForm(forms.Form):
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           'id': 'email',
                                                           }))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 }))

    class Meta:
        fields = ['email', 'password']


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", "class": "form-control"}),
        validators=[]
    )
    error_messages = {
        "user_notfound": _("User with this email address does not exist."),
    }

    def clean_email(self):
        email = self.cleaned_data["email"]
        self.users_cache = UserModel.objects.filter(email=email)
        if not self.users_cache:
            raise ValidationError(
                self.error_messages["user_notfound"],
                code="user_notfound",
            )
        return email

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(
            subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(
                html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
            and _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=True,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        email_field_name = UserModel.get_email_field_name()
        for user in self.get_users(email):
            user_email = getattr(user, email_field_name)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", 'class': 'form-control', 'id': 'password1'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", 'class': 'form-control', 'id': 'password2'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """

    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": _(
            "Your old password was entered incorrectly. Please enter it again."
        ),
    }
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password",
                   "autofocus": True, 'class': 'form-control', 'id': 'old_password', }
        ),
    )

    field_order = ["old_password", "new_password1", "new_password2"]

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages["password_incorrect"],
                code="password_incorrect",
            )
        return old_password


class ProfileForm(forms.ModelForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'id': 'username'}),
        max_length=30,
        min_length=5,
        required=True,
    )
    location = forms.ChoiceField(
        label=_("Location"),
        widget=forms.Select(
            attrs={'class': 'form-control', 'id': 'location'}),
        choices=COUNTRIES,
        required=True,
    )
    avatar = forms.ImageField(label=_('Company Logo'), required=False, error_messages={'invalid': _(
        "Image files only")}, widget=forms.FileInput(attrs={'class': 'form-control', 'id': 'avatar'}))

    class Meta:
        model = Profile
        fields = ['username', 'bio', 'location', 'birth_date', 'avatar']
        widgets = {
            'bio': forms.TextInput(attrs={'class': 'form-control', 'id': 'bio'}),
            'birth_date': forms.TextInput(attrs={'class': 'form-control', 'id': 'birth_date', 'type': 'date'}),
        }
