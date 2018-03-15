from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.security import getyear
from Utils.data import Each
from django_mysql import models as sqlmod
from datetime import datetime

from apps.program.managers import Enrollments

class InvoiceManager(sm.SuperManager):
	def __init__(self):
		super(InvoiceManager, self).__init__('main.InvoiceManager')
		self.fields = []
		self.validations = [
			sm.Present('id','Please enter the 6-digit Invoice ID (Probably {:02d}xxxx)'.format(getyear()%100)),
			sm.Regular('id',r'^$|^\d{6}$','This is not a valid Invoice ID. It should be a 6-digit number.'),
			sm.Present('code','Please enter the 32-character Invoice Code.'),
			sm.Regular('code',r'^$|([0-9a-fA-F]-?){32}','This is not a valid UUID. It should be 32 hexidecimal digits')
		]
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
		this.update_amount()
		return this
Invoices = InvoiceManager()