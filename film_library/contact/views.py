from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django import forms
from allauth.account.views import LoginView
from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView

from .models import Contact
from .forms import ContactForm


class ContactView(CreateView):
    model = Contact
    form_class = ContactForm
    success_url = "/"


def LOGIN_VIEW():
    class LoginForm(forms.Form):
        username = forms.CharField(max_length=254)
        password = forms.CharField(widget=forms.PasswordInput)

    return LoginView.as_view(
        template_name='/movies/movie_list.html',
        form_class=LoginForm,
        success_url=reverse_lazy('/'),
        extra_context={
            'title': _('Log in'),
            'show_password_reset': True,
        },
    )
