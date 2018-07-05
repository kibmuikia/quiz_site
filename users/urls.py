# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

#from django.views.generic import TemplateView

urlpatterns = [

	# home/index page for app[ users ]
	url( r'^$', views.indexView.as_view(), name="users_index_link" ),

	# view [ login ]
	url( r'^login/$', views.loginView.as_view(), name='users_login_link' ),
	# (?P<site_msg>[^\/]*)/

	# view [ Register ]
	url( r'^register/$', views.registerView.as_view(), name='users_register_link' ),

	# view-function [ Logout ]
	url( r'^logout/$', views.logoutFunctionView, name='users_logout_link' ),

	# view [ profile details ]
	url( r'^profile_details/$', views.profileView.as_view(), name='profile_details_link' ),

	# testing django-bootstrap4
  	url( r'^testpage/$', views.testView.as_view(), name='test_link' ),

  	# pdfView
	url( r'^pdf/$', views.pdfView.as_view(), name='pdf_link' ),

]