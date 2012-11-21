import random, logging
from django import forms
from models import *
from django.forms import ModelForm, Form, ValidationError
from django.contrib.auth.forms import AuthenticationForm

class SignUpForm(ModelForm):
  email = forms.EmailField(max_length=30, 
    error_messages={'required': 'required', 'invalid': 'invalid email',
    'unique': 'email is already being used',})
  password = forms.CharField(widget=forms.PasswordInput, label="Your Password",
    error_messages={'required': 'required'})
  name = forms.CharField(max_length=50, label="Publicly visible name",
    error_messages={'required': 'required'})
  def save(self, force_insert=False, force_update=False, commit=True):
    u = super(SignUpForm, self).save(commit=False)
    email = self.cleaned_data['email']
    password = self.cleaned_data['password']
    u.user = User.objects.create_user(email, email, password)
    if commit:
      u.save()
    return u
  class Meta:
    model = UserProfile
    fields = ('email', 'password', 'name',)
  
class LogInForm(AuthenticationForm):
  username = forms.EmailField(max_length=30, label='Email',
    error_messages={'required': 'required', 'invalid': 'invalid email',})
  password = forms.CharField(widget=forms.PasswordInput, label="Password",
    error_messages={'required': 'required'})
  def clean(self):
    try:
      return super(LogInForm, self).clean()
    except ValidationError, err:
      if "username" in str(err) and "password" in str(err):
        raise ValidationError(("Incorrect email/password combination"))
      raise
      
class NoteForm(ModelForm):
  message = CharField(widget=forms.Textarea, 
    error_messages={'required': 'required'})
  def save(self, force_insert=False, force_update=False, commit=True):
    m = super(NoteForm, self).save(commit=False)
    m.author = author
    if commit:
      m.save()
    return m
  class Meta:
    model = Note
    fields = ('message',)
