from django.db import models
import requests

from apps.program.managers import Enrollments, Courses
from apps.program.models import Enrollment
from apps.people.managers import Students
from .managers import Invoices, PayPals

from Utils import custom_fields as custfd
from Utils import supermodel as sm
from Utils.data import Each, collect

from datetime import datetime
from decimal import Decimal
#from trace import DEV
import uuid
import json

class PayPal(models.Model):
	message    = models.TextField(editable=False)
	verified   = models.NullBooleanField()
	txn_id     = models.CharField(max_length= 20)
	created_at = models.DateTimeField(auto_now_add=True)
	payment_date = models.DateTimeField(null=True)
	objects = PayPals
	def invoice(self):
		return Invoices.fetch(id=self.get('invoice'))
	def __getitem__(self, field):
		return self.data().get(field)
	def data(self):
		return json.loads(self.message)
	def verify(self, url):
		query = 'cmd=_notify-validate'
		data = self.data()
		for key in data:
			query += '&{}={}'.format(key, data[key])
		response = requests.post(url, data=query)
		self.verified = response.text == 'VERIFIED'
		self.save()
		return self.verified
	def stand(self, me):
		return self.invoice.family.id == me.owner.id
	def __getattribute__(self, field):
		if field in ['invoice','family']:
			call = super(PayPal, self).__getattribute__(field)
			return call()
		else:
			return super(PayPal, self).__getattribute__(field)


class Invoice(models.Model):
	family = models.ForeignKey('people.Family')
	amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	method = custfd.EnumField(choices=['','Cash','Check','PayPal'], default='')
	status_choices = [
		('N','Not Paid'),
		('P','Paid'),
		('C','Cancelled'),
	]
	status = models.CharField(max_length=1,default='N',choices=status_choices)
	year   = models.DecimalField(max_digits=4, decimal_places=0)
	paypal = models.OneToOneField(PayPal, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Invoices
	def __str__(self):
		return "Invoice #{}".format(self.id)
	def stand(self, me):
		return self.family.id == me.owner.id
	def items(self):
		return Enrollments.filter(invoice=self)
	def calc_amount(self):
		amount = Decimal(0)
		for q in self.items:
			if type(q) is Enrollment:
				amount += q.course.tuition()
			elif type(q) is Discount:
				amount -= q.amount
		return amount
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
	def confirm(self, paypal):
		return self.status == 'N' and paypal['amount'] == self.amount and paypal['invoice'] == self.id
	def pay(self, paypal):
		if self.confirm(paypal):
			for item in self.items:
				item.pay()
			self.status = 'P'
			self.method = 'PayPal'
			self.paypal =  paypal
			self.save()
			return True
	def __getattribute__(self, field):
		if field in ['items','get_status_display']:
			call = super(Invoice, self).__getattribute__(field)
			return call()
		else:
			return super(Invoice, self).__getattribute__(field)
