from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from django_mysql import models as sqlmod
from datetime import datetime

class InvoiceManager(sm.SuperManager):
	def __init__(self):
		super(InvoiceManager, self).__init__('main.InvoiceManager')
		self.fields = []
		self.validations = []
Invoices = InvoiceManager()