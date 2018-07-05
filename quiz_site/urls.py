"""quiz_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
#from django.urls import path

from django.conf.urls import url, include
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  url( r'^admin/', admin.site.urls ),

  # site index page
  url( r'^$', views.indexView.as_view(), name='site_index_link' ),

  # view list of glyphicons
  url( r'^glyphicon/$', views.glyphiconView.as_view(), name='glyphicon_link' ),

  # application[ users ]
  url( r'^users/', include( 'users.urls' ) ),

  # application[ quiz ]
  url( r'^quiz/', include( 'quiz.urls' ) ),

  # application[ qa ]
  url(r'^qa/', include('qa.urls') ),

]

if settings.DEBUG is True:
  urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )