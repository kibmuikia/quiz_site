# -*- coding: utf-8 -*-

from django import forms

class testForm( forms.Form ):
	name = forms.CharField( max_length=20,
									help_text='Enter your nickname' )
	bio = forms.CharField( max_length=140,
									help_text='Write about yourself',
									label='Bioghraphy' )