# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from jchart import Chart
from .models import Quiz, Category, Progress, Sitting, Question
from django.views.generic import DetailView, ListView, TemplateView, FormView, View

# sample chart
class lineChart( Chart ):
	chart_type = 'line'
	responsive = True
	
	def get_datasets( self, **kwargs ):
		data = [{
			'label' : "My Dataset",
			'data' : [69,30,45,60,55]
		}]
		return data

# trial progress chart
class progressChart( Chart ):
	chart_type = 'line'
	responsive = True

	def get_dataset( self, request, **kwargs ):
		userSittingData = Sitting.objects.filter( user=26 )
		#examData = userProgressData.show_exams()
		quizAll = []
		scoreAll = []
		for sitting in userSittingData:
			quizAll.append(sitting.quiz)
			scoreAll.append(sitting.current_score)
		#data = [{'x': sitting.quiz, 'y': sitting.current_score} for sitting in userSittingData]
		data = [{'x': quizAll, 'y': scoreAll}]
		#data = [{
		#	'label' : "Progress Data",
		#	'data' : function(){
		#		for sitting in userSittingData:
		#			sitting.current_score
		#	}
		#}]

		#return [DataSet(data=data)]
		return data