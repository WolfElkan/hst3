from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.security import getyear
from dateparser import parse
from Utils.data import Each
from django_mysql import models as sqlmod
from datetime import datetime
from trace import DEV

class PolicyManager(sm.SuperManager):
	def __init__(self):
		super(PolicyManager, self).__init__('radmin_policy')
Policies = PolicyManager()
