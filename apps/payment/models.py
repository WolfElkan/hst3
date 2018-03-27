from django.db import models

from apps.program.managers import Enrollments, Courses
from apps.program.models import Enrollment
from apps.people.managers import Students
from .managers import Invoices, Discounts, PayPals

from Utils import custom_fields as custfd
from Utils import supermodel as sm
from Utils.data import Each, collect

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

	txn_type_choices = [
		"",
		"adjustment",
		"cart",
		"express_checkout",
		"masspay",
		"merch_pmt",
		"mp_cancel",
		"new_case",
		"payout",
		"pro_hosted",
		"recurring_payment",
		"recurring_payment_expired",
		"recurring_payment_failed",
		"recurring_payment_profile_cancel",
		"recurring_payment_profile_created",
		"recurring_payment_skipped",
		"recurring_payment_suspended",
		"recurring_payment_suspended_due_to_max_failed_payment",
		"send_money",
		"subscr_cancel",
		"subscr_eot",
		"subscr_failed",
		"subscr_modify",
		"subscr_payment",
		"subscr_signup",
		"virtual_terminal",
		"web_accept",
	]
	payment_status_choices = [
		"Canceled_Reversal",
		"Completed",
		"Declined",
		"Expired",
		"Failed",
		"In-Progress",
		"Partially_Refunded",
		"Pending",
		"Processed",
		"Refunded",
		"Reversed",
		"Voided"
	]
	fraud_choices = [
		( 0, "Trustworthy"),
		( 1, "AVS No Match"),
		( 2, "AVS Partial Match"),
		( 3, "AVS Unavailable/Unsupported"),
		( 4, "Card Security Code (CSC) Mismatch"),
		( 5, "Maximum Transaction Amount"),
		( 6, "Unconfirmed Address"),
		( 7, "Country Monitor"),
		( 8, "Large Order Number"),
		( 9, "Billing/Shipping Address Mismatch"),
		(10, "Risky ZIP Code"),
		(11, "Suspected Freight Forwarder Check"),
		(12, "Total Purchase Price Minimum"),
		(13, "IP Address Velocity"),
		(14, "Risky Email Address Domain Check"),
		(15, "Risky Bank Identification Number (BIN) Check"),
		(16, "Risky IP Address Range"),
		(17, "PayPal Fraud Model"),
	]
	pending_reason_choices = [
		("AD", "address"             , "The payment is pending because your customer did not include a confirmed shipping address and your Payment Receiving Preferences is set to allow you to manually accept or deny each of these payments. To change your preference, go to the Preferences section of your Profile."),
		("AU", "authorization"       , "You set the payment action to Authorization and have not yet captured funds."),
		("DD", "delayed_disbursement", "The transaction has been approved and is currently awaiting funding from the bank. This typically takes less than 48 hrs."),
		("EC", "echeck"              , "The payment is pending because it was made by an eCheck that has not yet cleared."),
		("IN", "intl"                , "The payment is pending because you hold a non-U.S. account and do not have a withdrawal mechanism. You must manually accept or deny this payment from your Account Overview."),
		("MC", "multi_currency"      , "You do not have a balance in the currency sent, and you do not have your profiles's Payment Receiving Preferences option set to automatically convert and accept this payment. As a result, you must manually accept or deny this payment."),
		("OR", "order"               , "You set the payment action to Order and have not yet captured funds."),
		("PR", "paymentreview"       , "The payment is pending while it is reviewed by PayPal for risk."),
		("RR", "regulatory_review"   , "The payment is pending because PayPal is reviewing it for compliance with government regulations. PayPal will complete this review within 72 hours. When the review is complete, you will receive a second IPN message whose payment_status/reason code variables indicate the result."),
		("UL", "unilateral"          , "The payment is pending because it was made to an email address that is not yet registered or confirmed."),
		("UP", "upgrade"             , "The payment is pending because it was made via credit card and you must upgrade your account to Business or Premier status before you can receive the funds. upgrade can also mean that you have reached the monthly limit for transactions on your account."),
		("VF", "verify"              , "The payment is pending because you are not yet verified. You must verify your account before you can accept this payment."),
		("OT", "other"               , "The payment is pending for a reason other than those listed above. For more information, contact PayPal Customer Service."),
	]
	# Transaction and notification-related variables
	business               = models.CharField(max_length=127, default="") 
	charset                = models.CharField(max_length= 15, default="")
	custom                 = models.CharField(max_length=255, default="")
	ipn_track_id           = models.CharField(max_length= 15, default="", primary_key=True)
	notify_version         = models.CharField(max_length= 10, default="")
	parent_txn_id          = models.CharField(max_length= 20, default="")
	receipt_id             = models.TextField(max_length= 20, default="")
	receiver_email         = models.EmailField(               default="")
	receiver_id            = models.CharField(max_length= 13, default="")
	resend                 = models.BooleanField(default=False)
	residence_country      = models.CharField(max_length=  2, default="")
	test_ipn               = models.BooleanField(default=False)
	# Buyer information variables
	address_country        = models.CharField(max_length= 64, default="")
	address_city           = models.CharField(max_length= 40, default="")
	address_country_code   = models.CharField(max_length=  2, default="")
	address_name           = models.CharField(max_length=128, default="")
	address_state          = models.CharField(max_length= 40, default="")
	address_status         = custfd.EnumField(choices=['confirmed','unconfirmed'])
	address_street         = models.CharField(max_length=200, default="")
	address_zip            = models.TextField(max_length= 20, default="")
	contact_phone          = models.TextField(max_length= 20, default="")
	first_name             = models.CharField(max_length= 64, default="")
	last_name              = models.CharField(max_length= 64, default="")
	payer_business_name    = models.CharField(max_length=127, default="")
	payer_email            = models.CharField(max_length=127, default="")
	payer_id               = models.CharField(max_length= 13, default="")
	# Payment information variables
	auth_amount            = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	auth_exp               = custfd.PayPalDateTimeField()
	auth_id                = models.CharField(max_length= 19, default="")
	auth_status            = NotImplemented
	discount               = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	echeck_time_processed  = custfd.PayPalDateTimeField()
	exchange_rate          = models.FloatField()
	fraud                  = models.PositiveIntegerField(choices=fraud_choices,  default=0)
	invoice                = models.CharField(max_length=127, default="")
	item_nameS             = models.TextField()
	item_numberS           = models.TextField()
	mc_currency            = models.CharField(max_length= 3)
	mc_fee                 = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	mc_gross               = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	mc_gross_S             = models.TextField()
	mc_handling            = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	mc_shipping            = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	mc_shippingS           = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	memo                   = models.CharField(max_length=255, default="")
	num_cart_items         = models.PositiveIntegerField()
	optionS_json           = models.TextField()
	payer_status           = custfd.EnumField(choices=['verified','unverified'])
	payment_date           = custfd.PayPalDateTimeField()
	payment_fee            = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	payment_fee_S          = models.TextField()
	payment_gross          = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	payment_gross_S        = models.TextField()
	payment_status         = custfd.EnumField(choices=payment_status_choices)
	payment_type           = custfd.EnumField(choices=['echeck','instant'])
	pending_reason         = models.CharField(max_length=  2, default="  ")
	

	insurance_amount       = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	# item_name              = models.CharField(max_length=30)
	# item_number            = models.PositiveIntegerField(default=0)
	protection_eligibility = models.CharField(max_length=15)
	quantity               = models.PositiveIntegerField(default=1)
	shipping_discount      = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	shipping_method        = models.CharField(max_length=20)
	transaction_subject    = models.CharField(max_length=15)
	txn_type               = custfd.EnumField(choices=txn_type_choices)
	verify_sign            = models.CharField(max_length=60)

