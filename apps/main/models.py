from __future__ import unicode_literals
from django.db import models
from . import custom_fields as custom
from . import supermodel as sm
from datetime import datetime


# - - - - - M A N A G E R S - - - - - 

class FamilyManager(sm.SuperManager):
	def __init__(self):
		super(FamilyManager, self).__init__('main_family')
		self.fields = ['last','phone','email','joined_hst']
		self.validations = [
			sm.Present('last' ,'Please enter the family surname, as used by the children.'),
			sm.Regular('last' ,r'^.{,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Present('phone','Please enter the main family phone number.'),
			sm.Regular('phone',r'^$|^[ -.()/\\~]*(\d[ -.()/\\~]*){10}$','Please enter a valid 10-digit phone number.'),
			sm.Present('email','Please enter an email address.'),
			sm.Regular('email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address.'),
		]
Families = FamilyManager()

class ParentManager(sm.SuperManager):
	def __init__(self):
		super(ParentManager, self).__init__('main_parent')
		self.fields = ['first','last','sex','alt_phone','alt_email']
		self.validations = [
			sm.Present('first','Please enter the first name for at least one parent'),
			sm.Regular('first',r'^.{,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Regular('last',r'^.{,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Regular('alt_phone',r'^$|^[ -.()/\\~]*(\d[ -.()/\\~]*){10}$','Please enter a valid 10-digit phone number.'),
			sm.Regular('alt_email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address.'),
		]
Parents = ParentManager()

class StudentManager(sm.SuperManager):
	def __init__(self):
		super(StudentManager, self).__init__('main_student')
		self.fields = ['first','middle','last','prefer','sex','birthday','grad_year','height','alt_phone','alt_email','tshirt']
		self.validations = [
			sm.Present('first','Please enter a first name.'),
			sm.Regular('first',r'^.{0,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Regular('middle',r'^.{0,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Regular('last',r'^.{0,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Regular('prefer',r'^.{0,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Present('sex','Please select a sex.'),
			sm.Present('birthday','Please enter a date of birth.'),
			sm.Regular('alt_phone',r'^$|^[^\d]*(\d[^\d]*){10}$','Please enter a valid 10-digit phone number, or leave blank to use family phone.'),
			sm.Regular('alt_email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address, or leave blank to use family email.'),
		]
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
			sm.Confirmation('pw_confm','password','Passwords do not match.')
		]
Users = UserManager()

# - - - - - M O D E L S - - - - - 

class Address(models.Model):
	line1      = models.CharField(null=False, max_length=50)
	line2      = models.CharField(null=True, max_length=50)
	city       = models.CharField(null=True, max_length=25)
	state      = models.CharField(null=True, max_length=2)
	zipcode    = models.DecimalField(null=False, max_digits=9, decimal_places=4)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	def id_(self):
		return self.id

class Parent(models.Model):
	def id_(self):
		return self.id
	first = models.CharField(max_length=20)
	def first_(self):
		return self.first
	family_id = models.PositiveIntegerField()
	def family_(self):
		# print 'hello'
		# print FamilyManager()
		return Families.get(id=self.family_id)
	last = models.CharField(null=True, max_length=30)
	def last_(self):
		return self.last if self.last else self.family_().last
	sex = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	def sex_(self):
		return self.sex
	alt_phone = custom.PhoneNumberField(null=True)
	def phone_(self):
		return custom.PhoneNumber(self.phone if self.phone else self.family_().phone_())
	alt_email = models.EmailField(null=True)
	def email_(self):
		return self.email if self.email else self.family_().email_()
	created_at = models.DateTimeField(auto_now_add=True)
	def created_at_(self):
		return self.created_at
	updated_at = models.DateTimeField(auto_now=True)
	def updated_at_(self):
		return self.updated_at
	objects = Parents
	def __str__(self):
		if self.sex == 'M':
			prefix = 'Mr. '
		elif self.sex == 'F':
			prefix = 'Mrs. '
		return prefix+self.first+' '+self.last_()

class Family(models.Model):
	last       = models.CharField(max_length=30)
	phone      = custom.PhoneNumberField()
	email      = models.EmailField()
	mother_id  = models.PositiveIntegerField(null=True)
	father_id  = models.PositiveIntegerField(null=True)
	reg_status = models.PositiveSmallIntegerField(default=0)
	joined_hst = models.DecimalField(max_digits=4, decimal_places=0)
	address    = models.OneToOneField(Address, null=True, primary_key=False, rel=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Families
	def __str__(self):
		return self.last+' Family'
	def __getattribute__(self, field):
		if field == '':
			pass
		elif field == 'phone':
			return custom.PhoneNumber(super(Family, self).__getattribute__('phone'))
		elif field == 'mother':
			return Parents.get(id=super(Family, self).__getattribute__('mother_id'))
		elif field == 'father':
			return Parents.get(id=super(Family, self).__getattribute__('father_id'))
		else:
			return super(Family, self).__getattribute__(field)
	def __setattr__(self, field, value):
		if field == 'mother' and value.__class__ == Parent:
			super(Family, self).__setattr__('mother_id', value.id)
			return self.save()
		if field == 'father' and value.__class__ == Parent:
			super(Family, self).__setattr__('father_id', value.id)
			return self.save()
		else:
			return super(Family, self).__setattr__(field, value)


class Student(models.Model):
	def id_(self):
		return self.id
	first = models.CharField(max_length=20)
	def first_(self):
		return self.first
	middle = models.CharField(max_length=20, null=True)
	def middle_(self):
		return self.middle
	last = models.CharField(max_length=30, null=True)
	def last_(self):
		return self.last if self.last else self.family_().last_()
	prefer = models.CharField(max_length=20, null=True)
	def prefer_(self):
		return self.prefer if self.prefer else self.first
	family = models.ForeignKey(Family)
	def family_(self):
		return self.family
	sex = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	def sex_(self):
		return self.sex
	current = custom.BooleanField()
	def current_(self):
		return self.current
	birthday = models.DateField()
	def birthday_(self):
		return self.birthday
	grad_year = models.DecimalField(max_digits=4, decimal_places=0, null=True)
	def grad_year_(self):
		return self.grad_year
	def grade_(self, *year):
		if not year:
			now = datetime.now()
			year = now.year + (0 if now.month < 4 else 1)
		grade = year - self.grad_year + 12
		return grade if grade <= 12 else 'A'
	height = models.FloatField(null=True)
	def height_(self):
		return self.height
	alt_phone  = custom.PhoneNumberField(null=True)
	def phone_(self):
		return self.alt_phone if self.alt_phone else self.family_().phone_()
	alt_email  = models.EmailField(null=True)
	t_shirt_sizes = [
		('YS','Youth Small'),
		('YM','Youth Medium'),
		('YL','Youth Large'),
		('XS','Adult Extra Small'),
		('AS','Adult Small'),
		('AM','Adult Medium'),
		('AL','Adult Large'),
		('XL','Adult Extra Large'),
		('2X','Adult 2XL'),
		('3X','Adult 3XL'),
	]
	tshirt = models.CharField(max_length=2, choices=t_shirt_sizes, null=True)
	def tshirt_(self):
		return self.tshirt
	created_at = models.DateTimeField(auto_now_add=True)
	def created_at_(self):
		return self.created_at
	updated_at = models.DateTimeField(auto_now=True)
	def updated_at_(self):
		return self.updated_at
	objects = Students
	def __str__(self):
		return self.prefer_()+' '+self.last_()

class User(models.Model):
	username = models.CharField(max_length=30, unique=True)
	password = custom.BcryptField()
	# def password_(self, *guess):
	# 	bcrypt = custom.Bcrypt(self.password)
	# 	if not guess:
	# 		return bcrypt
	# 	else:
	# 		return bcrypt(guess)
	# TODO: Change this to manual polymorphism.  I don't trust this.
	owner = custom.PolymorphicField('owner', UserManager, [Family,Student])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Users
	def __str__(self):
		return self.username
	def __getattribute__(self, field):
		if field == 'pw':
			return custom.Bcrypt(super(User, self).__getattribute__('password'))
		else:
			return super(User, self).__getattribute__(field)
