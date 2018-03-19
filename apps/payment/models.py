from django.db import models

from apps.program.managers import Enrollments, Courses
from apps.program.models import Enrollment
from apps.people.managers import Students
from .managers import Invoices, Discounts

from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.data import Each

from datetime import datetime
from decimal import Decimal
from trace import DEV
import uuid

# Create your models here.

class Invoice(models.Model):
	family = models.ForeignKey('people.Family')
	amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	method = custom.EnumField(choices=['','Cash','Check','PayPal'], default='')
	status_choices = {
		('N','Not Paid'),
		('P','Paid'),
		('C','Cancelled'),
	}
	status = models.CharField(max_length=1,default='N',choices=status_choices)
	year = models.DecimalField(max_digits=4, decimal_places=0)
	code = models.UUIDField(default=uuid.uuid4, editable=False)
	memo = models.TextField(default='')
	payment_id = models.PositiveIntegerField(null=True) # Check number or PayPal Transaction ID
	created_at = models.DateTimeField(auto_now_add=True)
	check_date = models.DateField(null=True)
	depos_date = models.DateTimeField(null=True)
	clear_date = models.DateField(null=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Invoices
	def items(self):
		return list(Enrollments.filter(invoice=self, phantom=True)) + list(Discounts.filter(invoice=self))
	def calc_amount(self):
		amount = Decimal(0)
		for q in self.items:
			if type(q) is Enrollment:
				amount += q.course.tuition
			elif type(q) is Discount:
				amount -= q.amount
		return amount
		# return sum(Each(self.items).course.tuition)
	def update_amount(self):
		if self.status == 'N':
			self.amount = self.calc_amount()
			self.save()
			return self.amount
	def cancel(self):
		if self.status == 'N':
			for item in self.items:
				item.status = "nonexist"
				item.save()
			self.status = 'C'
			self.save()
	def __getattribute__(self, field):
		if field in ['items','get_status_display']:
			call = super(Invoice, self).__getattribute__(field)
			return call()
		else:
			return super(Invoice, self).__getattribute__(field)

class Discount(models.Model):
	objects    = Discounts
	amount     = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	title      = models.CharField(max_length=50)
	invoice    = models.ForeignKey(Invoice)
	display_student = 'Discount:'
	def tuition(self):
		return '({})'.format(self.amount)
	def __getattribute__(self, field):
		if field in ['tuition']:
			call = super(Discount, self).__getattribute__(field)
			return call()
		else:
			return super(Discount, self).__getattribute__(field)
				