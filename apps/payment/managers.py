from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.security import getyear, cleandate
from Utils.data import Each
from django_mysql import models as sqlmod
from datetime import datetime
from trace import DEV
import json

from apps.program.managers import Enrollments

class PayPalManager(sm.SuperManager):
	def __init__(self):
		super(PayPalManager, self).__init__('payment.paypal')
	def create(self, post):
		return super(PayPalManager, self).create(
			message   = json.dumps(post),
			txn_id    = post['txn_id'],
			payment_date = cleandate(post['payment_date']),
		)
PayPals = PayPalManager()

class InvoiceManager(sm.SuperManager):
	def __init__(self):
		super(InvoiceManager, self).__init__('payment.InvoiceManager')
		self.fields = []
		self.validations = []
	def create(self, **kwargs):
		kwargs.setdefault('year', getyear())
		year0000 = (int(kwargs['year']) % 100) * 10000
		qset = self.filter(id__gte=year0000,id__lte=year0000+9999)
		kwargs.setdefault('id',max([year0000]+list(Each(qset).id)) + 1)
		# kwargs.setdefault('amount', kwargs['family'].total_tuition_in(kwargs['year']))
		this = super(InvoiceManager, self).create(**kwargs)
		qset = Enrollments.filter(
			student__family=kwargs['family'],
			course__year=kwargs['year'],
			status__in=['aud_pass','aud_lock','need_pay'])
		for q in qset:
			q.invoice = this
			q.status = 'invoiced'
			q.save()
		amount = this.update_amount()
		this.update_amount()
		return this
Invoices = InvoiceManager()