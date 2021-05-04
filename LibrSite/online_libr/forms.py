from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, UsernameField)
from django.contrib.auth import get_user_model, models as auth_models
from django.forms.utils import ErrorList

from . import models as olm

from random import choice

class DivErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return '<div class="alert alert-danger">%s</div>' % ''.join(['<div class="error">%s</div>' % e for e in self])


class BootstrapFormMixin(forms.BaseForm):
    def as_bootstrap(self):
        """Return this form rendered as bootstrap 4 stacked form."""
        self.error_class = DivErrorList
        return self._html_output(
            normal_row='<div class="form-group"%(html_class_attr)s>%(label)s %(field)s%(help_text)s%(errors)s </div>',
            error_row='<div class="alert alert-danger">%s</div>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=False,
        )


class MyAuthForm(BootstrapFormMixin, AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Enter username'}))
    password = forms.CharField(
        label= ("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control',
                                          'placeholder': 'Enter password'}),
    )


class MyRegisterForm(forms.Form, BootstrapFormMixin):
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Enter username'}))
    password1 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control',
                                          'placeholder': 'Enter password'}),
    )
    password2 = forms.CharField(
        label=("Repeat password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control',
                                          'placeholder': 'Repeat password'}),
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(choices=olm.SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}))

    def clean_username(self):
        try:
            rep_user = get_user_model().objects.get_by_natural_key(self.cleaned_data.get('username'))
            if rep_user:
                raise forms.ValidationError('Username already in use')
        except get_user_model().DoesNotExist:
            pass
        return self.cleaned_data.get('username')

    def clean_password2(self):
        pwd1 = self.cleaned_data.get('password1')
        pwd2 = self.cleaned_data.get('password2')
        if not pwd1 or not pwd2:
            raise forms.ValidationError('Password is empty')
        if pwd1 != pwd2:
            raise forms.ValidationError('Passwords do not match')
        return pwd2


class ReviewForm(forms.ModelForm, BootstrapFormMixin):

    class Meta:
        model = olm.Review
        fields = ['comment', 'rating']
        widgets = {'comment': forms.Textarea(attrs={'class': 'textarea', 'cols': False, 'rows': False})}


class ReadStatusForm(forms.ModelForm):
    class Meta:
        model = olm.ReadStatus
        fields = ['status']


class SearchForm(forms.Form, BootstrapFormMixin):
    query = forms.CharField(label='Search', strip=False,
                            widget=forms.TextInput(attrs={'class': 'form-control mb-2 mr-2 '}))


class UpdateProfileForm(forms.ModelForm, BootstrapFormMixin):
    sex = forms.ChoiceField(choices=olm.SEX_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}))

    class Meta:
        model = auth_models.User
        fields = ['username', 'first_name', 'last_name', 'email', 'sex', 'birth_date']
        widgets = {'username': forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control'}),
                   'email': forms.EmailInput(attrs={'class': 'form-control'})}

    """def save(self, commit=True):  # if i want to use in UpdateView
        # libuser = olm.LibUser.objects.get(pk=self.instance.libuser.pk)
        self.instance.libuser.sex = self.cleaned_data['sex']
        self.instance.libuser.birth_date = self.cleaned_data['birth_date']
        self.instance.libuser.save(commit)  # if commit=False?
        super(UpdateProfileForm, self).save(commit)"""


chosen_book = choice(olm.Book.objects.all())
