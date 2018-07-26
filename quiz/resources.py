# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from import_export import resources
from .models import Quiz, Category, Progress, Sitting, Question

class sittingResource( resources.ModelResource ):
	class Meta:
		model = Sitting


class progressResource( resources.ModelResource ):
	class Meta:
		model = Progress


class quizResource( resources.ModelResource ):
	class Meta:
		model = Quiz


class questionResource( resources.ModelResource ):
	class Meta:
		model = Question