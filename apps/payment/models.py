from django.db import models

from apps.program.managers import Enrollments
from .managers import Invoices

from Utils import custom_fields as custom
from Utils import supermodel as sm

from datetime import datetime
from trace import DEV

# Create your models here.

class Invoice(models.Model):
	family = models.ForeignKey('people.Family')
	amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	method = custom.EnumField(choices=['','Cash','Check','PayPal'], default='')
	paid   = models.BooleanField(default=False)
	payment_id = models.PositiveIntegerField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	settled_at = models.DateTimeField(null=True)
	objects = Invoices
	def __getattribute__(self, field):
		if field in []:
			call = super(Enrollment, self).__getattribute__(field)
			return call()
		else:
			return super(Enrollment, self).__getattribute__(field)
		