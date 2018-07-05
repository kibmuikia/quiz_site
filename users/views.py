# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect, reverse
from django.http import FileResponse, Http404

# import generic views
from django.views.generic import View, TemplateView
from django.views import generic

# import authenticate and login functionalities
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.decorators import login_required

# import from forms.py
from .forms import UserForm, ProfileForm, loginForm, testForm

from django.contrib.auth.models import User
# import from models.py
from .models import ProfileModel

from django.forms.models import inlineformset_factory

# Create your views here.

# view to display a pdf
# coded by Kibuthi
class pdfView( View ):
    def get( self, request, *args, **kwargs ):
        try:
            return FileResponse( open( 'media/study/book-1.pdf', 'rb' ),
                                        content_type='application/pdf' )

            # end try
        except FileNotFoundError:
            raise HttpResponse( 'Page ni M.I.A' )
# end : pdfView

# view[ index page ]
class indexView( View ):
	template_name = 'site_users_index.html'

	def get( self, request, *args, **kwargs ):
			# get url-query-string data
		site_msg = request.GET.get( 'site_message','' )
		just_logged_out = request.GET.get( 'just_logged_out','' )
		just_logged_in = request.GET.get( 'just_logged_in','' )

		args = {
			'site_message':site_msg,
			'just_logged_out':just_logged_out,
			'just_logged_in':just_logged_in
			}

		return render( request, self.template_name, args )

	def post( self, request, **kwargs ):
		pass

# view[ register page ]
class registerView( View ):
	template_name = 'users-register.html'
	form_user = UserForm
	form_profile = ProfileForm

	def get( self, request, **kwargs ):
		uform = self.form_user( None )
		AccountInlineFormSet = inlineformset_factory( User, ProfileModel, fields=('account_type','pic','bio') )
		pform = AccountInlineFormSet( None )
		#pform = self.form_profile( None )

		args = {
		'uform':uform,
		'pform':pform
		}

		return render( request, self.template_name, args )

	def post( self, request, **kwargs ):
		uform = self.form_user( request.POST )
		AccountInlineFormSet = inlineformset_factory( User, ProfileModel, fields=('account_type','pic','bio') )
		pform = AccountInlineFormSet( request.POST, request.FILES )
		#pform = self.form_profile( request.POST, request.FILES )

		# all( [ uform.is_valid(), pform.is_valid() ] )
		if uform.is_valid():
			created_user = uform.save( commit=False )

			pform = AccountInlineFormSet( request.POST, request.FILES, instance=created_user )
			#pform = self.form_profile( request.POST, request.FILES, instance=created_user )

			if pform.is_valid():

				username = uform.cleaned_data['username']
				password = uform.cleaned_data['password']
				#image = pform.request.FILES['pic']
				#image.name = username

				created_user.set_password( password )

				created_user.save()
				# not working
				pform.save()

				created_user = authenticate( username=username, password=password )
				if created_user is not None:
					if created_user.is_active:
						msg = '[ '+ username +' ] is registered and authenticated'
						args = {
						'site_message':msg
						}
						return render( request, 'site_users_index.html', args )

		args = {
		'uform':uform,
		'pform':pform
		}

		return render( request, self.template_name, args )

# view[ login page ]
class loginView( View ):
	template_name = 'users-login.html'
	form_login = loginForm

	def get( self, request, *args, **kwargs ):
		if request.session.has_key('loggedin_user') or request.user.is_authenticated:
				# Deny Access because user is already logged in
			args = { 'message':'Already Logged-in' }
			msg = 'Access to Login-form Denied, you are already logged in!'

			return redirect( '/users/?site_message=%s' % msg )

			#return render( request, 'site_users_index.html', args )

		else:
				# Allow access since no user is logged in
			lform = self.form_login( None )
			site_msg = request.GET.get('site_message','')

			args = {
			'loginform':lform,
			'site_message':site_msg
			}

			return render( request, self.template_name, args )

	def post( self, request, *args, **kwargs ):
		lform = self.form_login( request.POST )

		if lform.is_valid():
			username = lform.cleaned_data['username']
			password = lform.cleaned_data['password']

			created_user = authenticate( username=username, password=password )
			if created_user is not None:
				if created_user.is_active:
					login( request, created_user )

					# create session
					request.session['loggedin_user'] = username
					#to check for session :> if request.session.has_key('loggedin_user'):

					args = {
					'just_logged_in':username,
					'status':'Authenticated, Active, Logged-in and Session created.'
					}

					return redirect( '/users/?site_message=%s&just_logged_in=%s'
											%( args['status'], username ) )
					#return render( request, 'site_users_index.html', args )

					#text = username + ' - is authenticated, active, action[login] performed and session created.'
					#return HttpResponse(text)

		args = {
		'loginform':lform
		}
		return render( request, self.template_name, args )

# logout function
def logoutFunctionView( request ):
	if request.user.is_authenticated and request.session.has_key('loggedin_user'):
		out_user = request.user
		logout( request )
		try:
			del request.session['loggedin_user']

		except:
			pass

		args = {
		'just_logged_out':out_user
		}
		#return render( request, 'site_users_index.html', args )
		msg = '['+out_user.username+'] logged out and session destroyed'

		#return redirect( '/users/?just_logged_out=%s&site_message=%s' %(  args['just_logged_out'], msg ) )
		return redirect( '/?just_logged_out=%s&site_message=%s' %( args['just_logged_out'], msg ) )

	else:
		#args = {
		#'message':'log-out FAILED ![ not authenticated OR no session["loggedin_user"] present ]'
		#}
		#return render( request, 'site_users_index.html', args )

		#msg = 'log-out FAILED ![ not authenticated OR no session["loggedin_user"] present ]'
		msg = 'log-out FAILED !'
		return redirect( '/users/?site_message=%s' % msg )

# view profile details
class profileView( TemplateView ):
	template_name = 'details_user.html'

	def get( self, request, *args, **kwargs ):

		# check if session['logged_in'] & is_authenticated, is active
		if request.session.has_key('loggedin_user') and request.user.is_authenticated:
			args = {}
			return render( request, self.template_name, args )
		else:
			msg = 'Access to Profile page Denied, Please Login'

			response = redirect( 'users_login_link' )
				# redirect returns a HttpResponseRedirect object
			response['Location'] += '?site_message=' + msg

			args = {}
			#return HttpResponseRedirect( reverse('users_login_link', kwargs={ 'site_msg':msg }) )
			return redirect( '/users/login/?site_message=%s' % msg )

class testView( View ):
	template_name = 'djangobootstrap4_test.html'
	form_test = testForm

	def get( self, request, *args, **kwargs ):

		args = { 'testform': self.form_test }

		return render( request, self.form_test, args )
		# end: get()