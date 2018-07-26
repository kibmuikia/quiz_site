# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from import_export import resources
from .models import ProfileModel

class profilemodelResource( resources.ModelResource ):
	class Meta:
		model = ProfileModel