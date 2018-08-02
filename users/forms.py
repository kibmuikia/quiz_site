# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from .models import ProfileModel

# form for model[ User ] : registration
class UserForm( forms.ModelForm ):
	class Meta:
		model = User
		fields = [ 'first_name', 'last_name', 'email', 'username', 'password' ]
		widgets = { 'password':forms.PasswordInput() }

# form - model[ ProfileModel ]
class ProfileForm( forms.ModelForm ):
	class Meta:
		model = ProfileModel
		fields = [ 'pic', 'bio' ]

# form - 'login'
class loginForm( forms.Form ):
	username = forms.CharField( max_length=150 )
	password = forms.CharField( widget=forms.PasswordInput() )

class testForm( forms.Form ):
	name = forms.CharField( max_length=20,
									help_text='Enter your nickname' )
	bio = forms.CharField( max_length=140,
									help_text='Write about yourself',
									label='Bioghraphy' )