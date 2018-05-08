from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.security import getyear
from dateparser import parse
from Utils.data import Each
from django_mysql import models as sqlmod
from datetime import datetime
from trace import DEV

class PolicyManager(sm.SuperManager):
	def __init__(self):
		super(PolicyManager, self).__init__('radmin_policy')
	def create(self, **kwargs):
		new = super(PolicyManager, self).create(**kwargs)
		new.countpages()
		return new
	def fetch(self, **kwargs):
		already = self.filter(**kwargs)[0]
		if already:
			return already
		elif not self.filter(year=kwargs.get('year')):
			return self.create(year=kwargs['year'],markdown='# HST Policy Agreement')
Policies = PolicyManager()
