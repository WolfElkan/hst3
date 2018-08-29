from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils.data import serial
from Utils.misc import namecase
from Utils.security import getyear, gethist
from Utils import supermodel as sm
from django_mysql import models as sqlmod
from datetime import datetime


class AddressManager(sm.SuperManager):
	def __init__(self):
		super(AddressManager, self).__init__('people.address')
Addresses = AddressManager()


class FamilyManager(sm.SuperManager):
	def __init__(self):
		super(FamilyManager, self).__init__('people.family')
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
			las = kwargs['last'][:3].upper()
			# kwargs['hid'] = las + str(serial(self, 'hid', hid__startswith=las))
		return super(FamilyManager, self).create(**kwargs)
	def all_join_alpha(self):
		result = []
		ids = []
		for year in gethist(0)[::-1]:
			for family in self.filter(children__enrollment__course__year=year).order_by('last'):
				if family.id not in ids:
					ids.append(family.id)
					result.append(family)
		for family in Families.all().exclude(id__in=ids):
			result.append(family)
		return result
Families = FamilyManager()


class ParentManager(sm.SuperManager):
	def __init__(self):
		super(ParentManager, self).__init__('people.parent')
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
		super(StudentManager, self).__init__('people.student')
		self.fields = ['first','alt_last','alt_first','sex','birthday','grad_year','height','alt_phone','alt_email','tshirt']
		self.validations = [
			sm.Present('first','Please enter a first name.'),
			sm.Regular('first',r'^.{0,20}$','This name is too long.  The maximum is 20 characters.'),
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
	def current(self, year=getyear()):
		return self.filter(enrollment__course__year=year)
Students = StudentManager()


class NameClashManager(sm.SuperManager):
	def __init__(self):
		super(NameClashManager, self).__init__('people.nameclash')
	def filter(self, **kwargs):
		if 'family' in kwargs:
			family = kwargs.pop('family')
			kwargs['last'] = family.last
		return super(NameClashManager, self).filter(**kwargs)
	def blanks(self, family):
		return self.model.blanks(self.model(), family)
	def calc(self, family, year=None):
		if hasattr(family,'last'):
			last = family.last
		else:
			last = family
		clashes = Families.filter(last=last)
		if year:
			clashes = clashes.filter(children__enrollment__course__year=year).distinct()
		if len(clashes) <= 1:
			return 0
		else:
			for tup in self.model.style_choices:
				num = tup[0]
				style = tup[1]
				unique = set([])
				good = True
				for family in clashes:
					blanks = self.blanks(family)
					styled = style.format(**blanks)
					if styled in unique:
						good = False
						break
					else:
						unique.add(styled)
				if good:
					return num
	def fate(self, family, year):
		num = self.calc(family,year)
		if num:
			return self.create(last=family.last,year=year,style=num)
	def universal(self, family):
		num = self.calc(family)
		return self.model.style_choices[num][1].format(**self.blanks(family))
NameClashes = NameClashManager()
		

class UserManager(sm.SuperManager):
	def __init__(self):
		super(UserManager, self).__init__('people.user')
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

class TeacherManager(sm.SuperManager):
	def __init__(self):
		super(TeacherManager, self).__init__('people_teacher')
Teachers = TeacherManager()