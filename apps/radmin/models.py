from django.db import models

from apps.program.managers import Enrollments, Courses
from apps.program.models import Enrollment
from apps.people.managers import Students
from .managers import Policies

from Utils import custom_fields as custfd
from Utils import supermodel as sm
from Utils.data import Each, collect

from datetime import datetime
from trace import DEV, OPEN
import markdown2, re

class Policy(models.Model):
	year       = models.DecimalField(max_digits=4, decimal_places=0, primary_key=True)
	markdown   = models.TextField(default='# HST Policy Agreement')
	nPages     = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects    = Policies
	ff = r'(\n|^)\s*# '
	def html(self,page=0):
		if page:
			md = '# '+(re.split(self.ff)[page])
		else:
			md = self.markdown
		return markdown2.markdown(md)
	def countpages(self):
		self.nPages = len(re.findall(self.ff,self.markdown))
		super(Policy, self).save()
	def save(self, **kwargs):
		self.countpages()
		super(Policy, self).save(**kwargs)
	def __str__(self):
		return '{} Policy'.format(self.year)
	def __getattribute__(self, field):
		if field in ['html']:
			call = super(Policy, self).__getattribute__(field)
			return call()
		else:
			return super(Policy, self).__getattribute__(field)
