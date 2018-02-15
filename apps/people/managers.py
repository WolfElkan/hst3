from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils.misc import namecase
from Utils import supermodel as sm
from django_mysql import models as sqlmod
from datetime import datetime


class AddressManager(sm.SuperManager):
	def __init__(self):
		super(AddressManager, self).__init__('address_family')
Addresses = AddressManager()

class FamilyManager(sm.SuperManager):
	def __init__(self):
		super(FamilyManager, self).__init__('main_family')
		self.fields = ['last','phone','email','phone_type']
		self.validations = [
			sm.Present('last' ,'Please enter the family surname, as used by the children.'),
			sm.Regular('last' ,r'^.{,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Present('phone','Please enter the main family phone number.'),
			sm.Regular('phone',r'^$|^[ -.()/\\~]*(\d[ -.()/\\~]*){10}$','Please enter a valid 10-digit phone number.'),
			sm.Present('email','Please enter an email address.'),
			sm.Regular('email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address.'),
		]
	def create(self, **kwargs):
		if 'last' in kwargs:
			kwargs['last'] = namecase(kwargs['last'])
		return super(FamilyManager, self).create(**kwargs)
Families = FamilyManager()

class ParentManager(sm.SuperManager):
	def __init__(self):
		super(ParentManager, self).__init__('main_parent')
		self.fields = ['first','alt_last','sex','alt_phone','alt_email','phone_type']
		self.validations = [
			sm.Present('first','Please enter a first name or skip this parent'),
			sm.Regular('first',r'^.{,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Regular('alt_last',r'^.{,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Regular('alt_phone',r'^$|^[ -.()/\\~]*(\d[ -.()/\\~]*){10}$','Please enter a valid 10-digit phone number.'),
			sm.Regular('alt_email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address.'),
		]
Parents = ParentManager()

class StudentManager(sm.SuperManager):
	def __init__(self):
		super(StudentManager, self).__init__('main_student')
		self.fields = ['first','middle','alt_last','alt_first','sex','birthday','grad_year','height','alt_phone','alt_email','tshirt']
		self.validations = [
			sm.Present('first','Please enter a first name.'),
			sm.Regular('first',r'^.{0,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Regular('middle',r'^.{0,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Regular('alt_last',r'^.{0,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Regular('alt_first',r'^.{0,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Present('sex','Please select a sex.'),
			sm.Present('birthday','Please enter a date of birth.'),
			# sm.Regular('birthday',r'^$|^\d{4}-\d{2}-\d{2}$','Please enter the date as YYYY-MM-DD'),
			sm.Regular('alt_phone',r'^$|^[^\d]*(\d[^\d]*){10}$','Please enter a valid 10-digit phone number, or leave blank to use family phone.'),
			sm.Regular('alt_email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address, or leave blank to use family email.'),
		]
	def create(self, **kwargs):
		if 'alt_last' in kwargs:
			kwargs['alt_last'] = namecase(kwargs['alt_last'])
		return super(StudentManager, self).create(**kwargs)
Students = StudentManager()

class UserManager(sm.SuperManager):
	def __init__(self):
		super(UserManager, self).__init__('main_user')
		self.fields = ['username','password','owner_type','owner_id']
		self.validations = [
			sm.Present('username','Please enter a username.'),
			sm.Unique(self,'username','This username is taken. Please select another.'),
			sm.Present('password','Please enter a password'),
			sm.Regular('password', r'^$|^.{8,}$','Password is too short. It should be at least 8 characters.'),
			sm.Regular('password', r'^$|^[^$].*$','Password may not begin with a dollar sign ($).'),
			sm.Present('pw_confm','Please confirm your password'),
			sm.Confirm('pw_confm','password','Passwords do not match.')
		]
	def isValid(self, data, **kwargs):
		if 'override_unique_username' in kwargs and kwargs['override_unique_username']:
			del self.validations[1]
		return super(UserManager, self).isValid(data, **kwargs)
	def filter(self, **kwargs):
		if 'owner' in kwargs:
			owner = kwargs.pop('owner')
			kwargs['owner_id'] = owner.id
			kwargs['owner_type'] = owner.__class__.__name__.title()
		return super(UserManager, self).filter(**kwargs)
Users = UserManager()