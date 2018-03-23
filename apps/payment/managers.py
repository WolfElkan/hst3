from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.security import getyear
from Utils.data import Each
from django_mysql import models as sqlmod
from datetime import datetime
from trace import DEV

from apps.program.managers import Enrollments

class DiscountManager(sm.SuperManager):
	def __init__(self):
		super(DiscountManager, self).__init__('payment.DiscountManager')
	# def create(self, **kwargs):
	# 	return super(DiscountManager, self).create(**kwargs)
Discounts = DiscountManager()


class InvoiceManager(sm.SuperManager):
	def __init__(self):
		super(InvoiceManager, self).__init__('payment.InvoiceManager')
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
		amount = this.update_amount()
		divide = 2
		# if DEV:
		# 	Discounts.create(
		# 		amount=amount.__mul__((10 ** divide) - 1).shift(-divide), 
		# 		course='total divided by 1{} for testing'.format('0'*divide),
		# 		invoice=this
		# 	)
		this.update_amount()
		return this
Invoices = InvoiceManager()

class PayPalManager(sm.SuperManager):
	def __init__(self):
		super(PayPalManager, self).__init__('payment.paypal')
		self.fields = [u'last_name',u'txn_id',u'shipping_method',u'shipping_discount',u'receiver_email',u'payment_status',u'payment_gross',u'residence_country',u'invoice',u'address_state',u'payer_status',u'txn_type',u'address_country',u'payment_date',u'first_name',u'item_name',u'address_street',u'charset',u'custom',u'notify_version',u'address_name',u'item_number',u'receiver_id',u'transaction_subject',u'business',u'payer_id',u'discount',u'verify_sign',u'address_zip',u'payment_fee',u'address_country_code',u'address_city',u'address_status',u'receipt_id',u'insurance_amount',u'mc_fee',u'mc_currency',u'payer_email',u'payment_type',u'mc_gross',u'ipn_track_id',u'quantity']
PayPals = PayPalManager()