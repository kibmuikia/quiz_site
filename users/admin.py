# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# import models
from .models import ProfileModel

# Register your models here.
admin.site.register( ProfileModel )

admin.site.site_header = 'Kibuthi The Developer'
admin.site.index_title = 'Computer Architecture Learning Administration'
admin.site.site_title = 'Kib-Quiz Control Panel'
