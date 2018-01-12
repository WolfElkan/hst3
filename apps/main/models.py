from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from django_mysql import models as sqlmod
from datetime import datetime


# - - - - - M A N A G E R S - - - - - 

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
	first      = models.CharField(max_length=20)
	family_id  = models.PositiveIntegerField()
	alt_last   = models.CharField(null=True, max_length=30)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	alt_phone  = custom.PhoneNumberField(null=True)
	phone_type = sqlmod.EnumField(null=True, choices=['Home','Cell','Work'])
	alt_email  = models.EmailField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Parents
	def __getattribute__(self, field):
		if field == '':
			pass
		elif field == 'last':
			if super(Parent, self).__getattribute__('alt_last'):
				return super(Parent, self).__getattribute__('alt_last') 
			else: 
				return super(Parent, self).__getattribute__('family').last
		elif field == 'phone':
			return custom.PhoneNumber(self.alt_phone if self.alt_phone else self.family.phone)
		elif field == 'email':
			return self.alt_email if self.alt_email else self.family.email
		elif field == 'family':
			family_id = super(Parent, self).__getattribute__('family_id')
			return Families.get(id=family_id)
		else:
			return super(Parent, self).__getattribute__(field)
	def __str__(self):
		if self.sex == 'M':
			prefix = 'Mr. '
		elif self.sex == 'F':
			prefix = 'Mrs. '
		return prefix+self.first+' '+self.last

class Family(models.Model):
	last       = models.CharField(max_length=30)
	phone      = custom.PhoneNumberField()
	phone_type = sqlmod.EnumField(null=True, choices=['Home','Cell','Work'])
	email      = models.EmailField()
	mother_id  = models.PositiveIntegerField(null=True)
	father_id  = models.PositiveIntegerField(null=True)
	reg_status = models.PositiveSmallIntegerField(default=0)
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
	first     = models.CharField(max_length=20)
	alt_first = models.CharField(max_length=20, null=True)
	middle    = models.CharField(max_length=20, null=True)
	alt_last  = models.CharField(max_length=30, null=True)
	family    = models.ForeignKey(Family, related_name='children')
	sex       = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	current   = models.BooleanField()
	birthday  = models.DateField()
	grad_year = models.DecimalField(max_digits=4, decimal_places=0, null=True)
	height    = models.FloatField(null=True)
	alt_phone = custom.PhoneNumberField(null=True)
	alt_email = models.EmailField(null=True)
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
	tshirt     = models.CharField(max_length=2, choices=t_shirt_sizes, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Students
	def __str__(self):
		return self.prefer+' '+self.last
	def __getattribute__(self, field):
		if field == '':
			pass
		elif field == 'prefer':
			if super(Student, self).__getattribute__('alt_first'):
				return super(Student, self).__getattribute__('alt_first') 
			else: 
				return super(Student, self).__getattribute__('first')
		elif field == 'last':
			if super(Student, self).__getattribute__('alt_last'):
				return super(Student, self).__getattribute__('alt_last') 
			else: 
				return self.family.last
		elif field == 'phone':
			return custom.PhoneNumber(self.alt_phone if self.alt_phone else self.family.phone)
		elif field == 'email':
			return self.alt_email if self.alt_email else self.family.email
		elif field == 'grade':
			now = datetime.now()
			# Switch to the following year on May 1
			year = now.year + (0 if now.month < 5 else 1)
			grade = year - self.grad_year + 12
			return grade
		elif field == 'family':
			family_id = super(Student, self).__getattribute__('family_id')
			return Families.get(id=family_id)
		elif field == 'full_name':
			return ' '.join([self.first,self.middle,self.last] if self.middle else [self.first,self.last])
		else:
			return super(Student, self).__getattribute__(field)
	def __getattr__(self, field):
		return None

class Teacher(models.Model):
	first      = models.CharField(max_length=20)
	last       = models.CharField(max_length=30)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	phone      = custom.PhoneNumberField()
	email      = models.EmailField()
	address    = models.OneToOneField(Address, null=True, primary_key=False, rel=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)		

class User(models.Model):
	username   = models.CharField(max_length=30, unique=True)
	password   = custom.BcryptField()
	owner      = custom.PolymorphicField('owner', UserManager, [Family,Student,Teacher,Parent])
	perm_levels = [
		(0,'Public') ,
		(1,'Student'),
		(2,'Parent') ,
		(3,'Captain'),
		(4,'Teacher'),
		(5,'Founder'),
		(6,'Admin')
	]
	permission = models.PositiveSmallIntegerField(default=0, choices=perm_levels)
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
