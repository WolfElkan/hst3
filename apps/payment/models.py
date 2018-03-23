from django.db import models

from apps.program.managers import Enrollments, Courses
from apps.program.models import Enrollment
from apps.people.managers import Students
from .managers import Invoices, Discounts, PayPals

from Utils import custom_fields as custfd
from Utils import supermodel as sm
from Utils.data import Each

from datetime import datetime
from decimal import Decimal
from trace import DEV
import uuid
import json

# Create your models here.

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
	year = models.DecimalField(max_digits=4, decimal_places=0)
	code = models.UUIDField(default=uuid.uuid4, editable=False)
	priv = models.UUIDField(default=uuid.uuid4, editable=False)
	                                             # Check:        PayPal:
	memo = models.TextField(default='')          # Memo line     custom
	payment_id = models.CharField(max_length=20) # Check Number  txn_id
	check_date = models.DateField(null=True)     # Check Date    NULL
	depos_date = models.DateTimeField(null=True) # deposited     payment_date
	clear_date = models.DateTimeField(null=True) # cleared       IPN recieved
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
	def pay(self, ipn):
		if self.status == 'N':
			for item in self.items:
				if item.status == "invoiced":
					item.status = "enrolled"
					item.save()
			self.status = 'P'
			self.save()
	def __getattribute__(self, field):
		if field in ['items','get_status_display']:
			call = super(Invoice, self).__getattribute__(field)
			return call()
		else:
			return super(Invoice, self).__getattribute__(field)

# https://developer.paypal.com/docs/classic/ipn/integration-guide/IPNandPDTVariables/
class PayPal(models.Model):
	message                = models.TextField(editable=False)
	txn_id                 = models.CharField(max_length= 20)
	created_at             = models.DateTimeField(auto_now_add=True)
	objects = PayPals
	def __getitem__(self, field):
		dic = self.data()
		if field in dic:
			return dic[field]
	def data(self):
		return json.loads(self.message)

	# txn_type_choices = [
	# 	"",
	# 	"adjustment",
	# 	"cart",
	# 	"express_checkout",
	# 	"masspay",
	# 	"merch_pmt",
	# 	"mp_cancel",
	# 	"new_case",
	# 	"payout",
	# 	"pro_hosted",
	# 	"recurring_payment",
	# 	"recurring_payment_expired",
	# 	"recurring_payment_failed",
	# 	"recurring_payment_profile_cancel",
	# 	"recurring_payment_profile_created",
	# 	"recurring_payment_skipped",
	# 	"recurring_payment_suspended",
	# 	"recurring_payment_suspended_due_to_max_failed_payment",
	# 	"send_money",
	# 	"subscr_cancel",
	# 	"subscr_eot",
	# 	"subscr_failed",
	# 	"subscr_modify",
	# 	"subscr_payment",
	# 	"subscr_signup",
	# 	"virtual_terminal",
	# 	"web_accept",
	# ]
	# payment_status_choices = [
	# 	"Canceled_Reversal",
	# 	"Completed",
	# 	"Declined",
	# 	"Expired",
	# 	"Failed",
	# 	"In-Progress",
	# 	"Partially_Refunded",
	# 	"Pending",
	# 	"Processed",
	# 	"Refunded",
	# 	"Reversed",
	# 	"Voided"
	# ]
	# fraud_choices = [
	# 	( 0, "Trustworthy")
	# 	( 1, "AVS No Match")
	# 	( 2, "AVS Partial Match")
	# 	( 3, "AVS Unavailable/Unsupported")
	# 	( 4, "Card Security Code (CSC) Mismatch")
	# 	( 5, "Maximum Transaction Amount")
	# 	( 6, "Unconfirmed Address")
	# 	( 7, "Country Monitor")
	# 	( 8, "Large Order Number")
	# 	( 9, "Billing/Shipping Address Mismatch")
	# 	(10, "Risky ZIP Code")
	# 	(11, "Suspected Freight Forwarder Check")
	# 	(12, "Total Purchase Price Minimum")
	# 	(13, "IP Address Velocity")
	# 	(14, "Risky Email Address Domain Check")
	# 	(15, "Risky Bank Identification Number (BIN) Check")
	# 	(16, "Risky IP Address Range")
	# 	(17, "PayPal Fraud Model")
	# ]
	# business               = models.CharField(max_length=127, null=True) 
	# charset                = models.CharField(max_length= 15, null=True)
	# custom                 = models.CharField(max_length=255, null=True)
	# ipn_track_id           = models.CharField(max_length= 15, null=True)
	# notify_version         = models.CharField(max_length= 10, null=True)
	# parent_txn_id          = models.CharField(max_length= 20, null=True)
	# receipt_id             = models.TextField(max_length= 20, null=True)
	# receiver_email         = models.EmailField(               null=True)
	# receiver_id            = models.CharField(max_length= 13, null=True)
	# resend                 = models.BooleanField(default=False)
	# residence_country      = models.CharField(max_length=  2, null=True)
	# test_ipn               = models.BooleanField(default=False)
	
	# address_country        = models.CharField(max_length= 64, null=True)
	# address_city           = models.CharField(max_length= 40, null=True)
	# address_country_code   = models.CharField(max_length=  2, null=True)
	# address_name           = models.CharField(max_length=128, null=True)
	# address_state          = models.CharField(max_length= 40, null=True)
	# address_status         = custfd.EnumField(choices=['confirmed','unconfirmed'])
	# address_street         = models.CharField(max_length=200, null=True)
	# address_zip            = models.TextField(max_length= 20, null=True)
	# contact_phone          = models.TextField(max_length= 20, null=True)
	# first_name             = models.CharField(max_length= 64, null=True)
	# last_name              = models.CharField(max_length= 64, null=True)
	# payer_business_name    = models.CharField(max_length=127, null=True)
	# payer_email            = models.CharField(max_length=127, null=True)
	# payer_id               = models.CharField(max_length= 13, null=True)
	# auth_amount            = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# auth_exp               = custfd.PayPalDateTimeField()
	# auth_id                = models.CharField(max_length= 19, null=True)
	# discount               = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# echeck_time_processed  = custfd.PayPalDateTimeField()
	# exchange_rate          = models.FloatField()
	# fraud                  = models.PositiveIntegerField(choices=fraud_choices,  default=0)
	# invoice                = models.CharField(max_length=127, null=True)

	# # insurance_amount       = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# # item_name              = models.CharField(max_length=30)
	# # item_number            = models.PositiveIntegerField(default=0)
	# # mc_currency            = models.CharField(max_length= 3)
	# # mc_fee                 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# # mc_gross               = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# # payer_status           = models.CharField(max_length=15)
	# # payment_date           = models.DateTimeField(null=True)
	# # payment_fee            = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# # payment_gross          = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# # payment_status         = custfd.EnumField(choices=payment_status_choices)
	# # payment_type           = custfd.EnumField(choices=['echeck','instant'])
	# # protection_eligibility = models.CharField(max_length=15)
	# # quantity               = models.PositiveIntegerField(default=1)
	# # shipping_discount      = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# # shipping_method        = models.CharField(max_length=20)
	# # transaction_subject    = models.CharField(max_length=15)
	# # txn_type               = custfd.EnumField(choices=txn_type_choices)
	# # verify_sign            = models.CharField(max_length=60)

