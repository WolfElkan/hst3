from django.db import models

from apps.program.managers import Enrollments, Courses
from apps.program.models import Enrollment
from apps.people.managers import Students
from .managers import Policies

from Utils import custom_fields as custfd
from Utils import supermodel as sm
from Utils.data import Each, collect

import datetime
#from trace import DEV, OPEN
import markdown2, re

class Policy(models.Model):
	year       = models.DecimalField(max_digits=4, decimal_places=0, primary_key=True)
	markdown   = models.TextField(default='# HST Policy Agreement')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = 'policy'
	emoji      = emoji = "&#x1f4c3;"
	objects    = Policies
	ff = r'^\s*# |\n\s*# '
	def md(self, page=0):
		if page and page <= self.nPages:
			return '# '+(re.split(self.ff,self.markdown)[page])
		elif not page:
			return self.markdown
	def html(self,page=0):
		return markdown2.markdown(self.md(page))
	def nPages(self):
		return len(re.findall(self.ff,self.markdown))
	def clean(self):
		epsilon = datetime.timedelta(0,5)
		return self.updated_at - self.created_at < epsilon
	def __str__(self):
		return '{} Policy'.format(self.year)
	def __getattribute__(self, field):
		if field in ['nPages']:
			call = super(Policy, self).__getattribute__(field)
			return call()
		else:
			return super(Policy, self).__getattribute__(field)
