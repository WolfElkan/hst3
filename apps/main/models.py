from __future__ import unicode_literals
from django.db import models
from . import custom_fields as custom
from . import supermodel as sm


# - - - - - M A N A G E R S - - - - - 

class FamilyManager(sm.SuperManager):
	def __init__(self):
		super(FamilyManager, self).__init__('main','family')
		self.fields = ['last','phone','email','joined_hst']
		self.validations = [
			sm.Present('last' ,'Please enter the family surname, as used by the children.'),
			sm.Regular('last' ,r'^.{,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Present('phone','Please enter the main family phone number.'),
			sm.Regular('phone',r'^$|^[ -.()/\\~]*(\d[ -.()/\\~]*){10}$','Please enter a valid 10-digit phone number.'),
			sm.Present('email','Please enter an email address.'),
			sm.Regular('email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address.'),
		]

class ParentManager(sm.SuperManager):
	def __init__(self):
		super(ParentManager, self).__init__('main','parent')
		self.fields = ['first','last','sex','alt_phone','alt_email']
		self.validations = [
			sm.Present('first','Please enter the first name for at least one parent'),
			sm.Regular('first',r'^$|^.{,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Regular('last',r'^$|^.{,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Regular('alt_phone',r'^$|^[ -.()/\\~]*(\d[ -.()/\\~]*){10}$','Please enter a valid 10-digit phone number.'),
			sm.Regular('alt_email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address.'),
		]

class UserManager(sm.SuperManager):
	def __init__(self):
		super(UserManager, self).__init__('main','user')
		self.fields = ['username','password','owner_type','owner_id']
		self.validations = [
			sm.Present('username','Please enter a username.'),
			sm.Unique(self,'username','This username is taken. Please select another.'),
			sm.Present('password','Please enter a password'),
			sm.Regular('password', r'^$|^.{8,}$','Password is too short. It should be at least 8 characters.'),
			sm.Present('pw_confm','Please confirm your password'),
			sm.Confirmation('pw_confm','password','Passwords do not match.')
		]

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
		FamilyManager.get(id=self.family_id)
	last = models.CharField(null=True, max_length=30)
	def last_(self):
		return self.last if self.last else self.family_().last_()
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
	objects = ParentManager()
	def __str__(self):
		if self.sex == 'M':
			prefix = 'Mr. '
		elif self.sex == 'F':
			prefix == 'Mrs. '
		return prefix+self.first+' '+self.last

class Family(models.Model):
	def id_(self):
		return self.id
	last = models.CharField(max_length=30)
	def last_(self):
		return self.last
	phone = custom.PhoneNumberField()
	def phone_(self):
		return custom.PhoneNumber(self.phone)
	email = models.EmailField()
	def email_(self):
		return self.email     
	mother_id = models.PositiveIntegerField(null=True)
	def mother_(self):
		return self.mother    
	father_id = models.PositiveIntegerField(null=True)
	def father_(self):
		return self.father    
	reg_status = models.PositiveSmallIntegerField(default=0)
	def reg_status_(self):
		return self.reg_status
	joined_hst = models.DecimalField(max_digits=4, decimal_places=0)
	def joined_hst_(self):
		return self.joined_hst
	address = models.OneToOneField(Address, null=True, primary_key=False, rel=True, related_name='floop')
	def address_(self):
		return self.address   
	created_at = models.DateTimeField(auto_now_add=True)
	def created_at_(self):
		return self.created_at
	updated_at = models.DateTimeField(auto_now=True)
	def updated_at_(self):
		return self.updated_at
	objects = FamilyManager()
	def __str__(self):
		return self.last_()+' Family'

class Student(models.Model):
	def id_(self):
		return self.id
	first = models.CharField(max_length=20)
	def first_(self):
		return self.first
	middle     = models.CharField(max_length=20, null=True)
	def middle_(self):
		return self.middle
	last = models.CharField(max_length=30, null=True)
	def last_(self):
		return self.last if self.last else family_().last_()
	prefer = models.CharField(max_length=20, null=True)
	def prefer_(self):
		return self.prefer if self.prefer else self.first
	sex = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	def sex_(self):
		return self.sex
	family = models.ForeignKey(Family)
	def family_(self):
		return self.family
	birthday = models.DateField()
	def birthday_(self):
		return self.birthday
	height = models.FloatField()
	def height_(self):
		return self.height
	alt_phone  = custom.PhoneNumberField(null=True)
	def phone(self):
		return self.alt_phone if self.alt_phone else family_().phone_()
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
	tshirt     = models.CharField(max_length=2, choices=t_shirt_sizes)
	def tshirt_(self):
		return self.tshirt
	created_at = models.DateTimeField(auto_now_add=True)
	def created_at_(self):
		return self.created_at
	updated_at = models.DateTimeField(auto_now=True)
	def updated_at_(self):
		return self.updated_at
	objects = sm.SuperManager('main','student')
	def __str__(self):
		return self._prefer()+' '+self._last()

class User(models.Model):
	def id_(self):
		return self.id
	username = models.CharField(max_length=30, unique=True)
	def username_(self):
		return self.username
	password = custom.BcryptField()
	def password_(self):
		return custom.Bcrypt(self.password)
	# TODO: Change this to manual polymorphism.  I don't trust this.
	owner = custom.PolymorphicField('owner', UserManager, [Family,Student])
	def owner_(self):
		return self.owner
	created_at = models.DateTimeField(auto_now_add=True)
	def created_at_(self):
		return self.created_at
	updated_at = models.DateTimeField(auto_now=True)
	def updated_at_(self):
		return self.updated_at
	objects    = UserManager()
	def __str__(self):
		return self.username