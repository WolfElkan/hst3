from django.db import models

from apps.program.managers import Enrollments, Courses
from apps.program.models import Enrollment
from apps.people.managers import Students
from .managers import Invoices, PayPals

from Utils import custom_fields as custfd
from Utils import supermodel as sm
from Utils.data import Each, collect

from datetime import datetime
from decimal import Decimal
from trace import DEV
import uuid
import json

class PayPal(models.Model):
	message    = models.TextField(editable=False)
	csrf_safe  = models.BooleanField(default=False)
	verified   = models.BooleanField(default=False)
	txn_id     = models.CharField(max_length= 20)
	created_at = models.DateTimeField(auto_now_add=True)
	payment_date = models.DateTimeField(null=True)
	objects = PayPals
	def __getitem__(self, field):
		dic = self.data()
		if field in dic:
			return dic[field]
	def data(self):
		return json.loads(self.message)

class Invoice(models.Model):
	family = models.ForeignKey('people.Family')
	amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	method = custfd.EnumField(choices=['','Cash','Check','PayPal'], default='')
	status_choices = {
		('N','Not Paid'),
		('P','Paid'),
		('C','Cancelled'),
	}
	status = models.CharField(max_length=1,default='N',choices=status_choices)
	year   = models.DecimalField(max_digits=4, decimal_places=0)
	csrf   = models.UUIDField(default=uuid.uuid4, editable=False)
	paypal = models.OneToOneField(PayPal, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Invoices
	def __str__(self):
		return "Invoice #{}".format(self.id)
	def items(self):
		return Enrollments.filter(invoice=self, phantom=True)
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
	def pay(self, paypal):
		if self.status == 'N':
			for item in self.items:
				if item.status == "invoiced":
					item.status = "enrolled"
					item.save()
			self.status = 'P'
			self.paypal = paypal
			self.save()
	def __getattribute__(self, field):
		if field in ['items','get_status_display']:
			call = super(Invoice, self).__getattribute__(field)
			return call()
		else:
			return super(Invoice, self).__getattribute__(field)
