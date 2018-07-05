# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect

#from .forms import testForm

# import generic views
from django.views.generic import View, TemplateView

class indexView( TemplateView ):
	template_name = 'site-index.html'

	#def get( self, request, **kwargs ):
		#return render( request, self.template_name, {} )

class glyphiconView( TemplateView ):
	template_name = 'glyphicon_list.html'