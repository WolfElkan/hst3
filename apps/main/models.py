from __future__ import unicode_literals
from django.db import models
from . import custom_fields as custom
from . import supermodel as sm


# - - - - - A D D R E S S - - - - -

def Address(sql):
	return sql
AddressManager = sm.SuperManager('main','address')
class ADDRESS(models.Model):
	line1      = models.CharField(null=False, max_length=50)
	line2      = models.CharField(null=True, max_length=50)
	city       = models.CharField(null=True, max_length=25)
	state      = models.CharField(null=True, max_length=2)
	zipcode    = models.DecimalField(null=False, max_digits=9, decimal_places=4)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects    = AddressManager

# - - - - - P A R E N T - - - - -

class Parent(object):
	def __init__(self, sql):
		super(Parent, self).__init__()
		self.first      = sql.first
		self.last       = sql.last if sql.last else sql.family.last
		self.sex        = sql.sex
		self.phone      = custom.PhoneNumber(sql.alt_phone if sql.alt_phone else sql.family.phone)
		self.email      = sql.alt_email if sql.alt_email else sql.family.email
		self.created_at = sql.created_at
		self.updated_at = sql.updated_at
	def __str__(self):
		if self.sex == 'M':
			prefix = 'Mr. '
		elif self.sex == 'F':
			prefix == 'Mrs. '
		return prefix+self.first+' '+self.last

class ParentManager(sm.SuperManager):
	def __init__(self):
		super(ParentManager, self).__init__('main',Parent)
		self.fields = ['first','last','sex','alt_phone','alt_email']
		self.validations = [
			sm.Present('first','Please enter the first name for at least one parent'),
			sm.Regular('first',r'^$|^.{,20}$','This name is too long.  The maximum is 20 characters.'),
			sm.Regular('last',r'^$|^.{,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Regular('alt_phone',r'^$|^[ -.()/\\~]*(\d[ -.()/\\~]*){10}$','Please enter a valid 10-digit phone number.'),
			sm.Regular('alt_email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address.'),
		]

class PARENT(models.Model):
	first      = models.CharField(max_length=20)
	last       = models.CharField(null=True, max_length=30)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	alt_phone  = custom.PhoneNumberField(null=True)
	alt_email  = models.EmailField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects    = ParentManager()

# - - - - - F - - - - -

class Family(object):
	def __init__(self, sql):
		self.last       = sql.last
		self.phone      = custom.PhoneNumber(sql.phone)
		self.email      = sql.email
		self.mother     = sql.mother
		self.father     = sql.father
		self.reg_status = sql.reg_status
		self.joined_hst = sql.joined_hst
		self.address    = Address(sql.address)
		self.created_at = sql.created_at
		self.updated_at = sql.updated_at
	def __str__(self):
		return self.last+' Family'

class FamilyManager(sm.SuperManager):
	def __init__(self):
		super(FamilyManager, self).__init__('main',Family)
		self.fields = ['last','phone','email','joined_hst']
		self.validations = [
			sm.Present('last' ,'Please enter the family surname, as used by the children.'),
			sm.Regular('last' ,r'^.{,30}$','This name is too long.  The maximum is 30 characters.'),
			sm.Present('phone','Please enter the main family phone number.'),
			sm.Regular('phone',r'^$|^[ -.()/\\~]*(\d[ -.()/\\~]*){10}$','Please enter a valid 10-digit phone number.'),
			sm.Present('email','Please enter an email address.'),
			sm.Regular('email',r'^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)','Please enter a valid email address.'),
		]

class FAMILY(models.Model):
	last       = models.CharField(max_length=30)
	phone      = custom.PhoneNumberField()
	email      = models.EmailField()
	mother     = models.OneToOneField(PARENT, null=True, related_name='family', rel=True)
	father     = models.OneToOneField(PARENT, null=True, related_name='father', rel=True)
	reg_status = models.PositiveSmallIntegerField(default=0)
	joined_hst = models.DecimalField(max_digits=4, decimal_places=0)
	address    = models.OneToOneField(ADDRESS, null=True, primary_key=False, rel=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects    = FamilyManager()

# - - - - - S - - - - -



class STUDENT(models.Model):
	first      = models.CharField(max_length=20)
	middle     = models.CharField(max_length=20, null=True)
	last       = models.CharField(max_length=30, null=True)
	prefer     = models.CharField(max_length=20, null=True)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	family     = models.ForeignKey(FAMILY, related_name='children')
	birthday   = models.DateField()
	height     = models.FloatField()
	alt_phone  = custom.PhoneNumberField(null=True)
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
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects    = sm.SuperManager('main','student')
	def _prefer(self):
		return self.first if self.prefer == '' else self.prefer
	def _last(self):
		return self.last
	def __str__(self):
		return self._prefer()+' '+self._last()

# - - - - - U - - - - -

class User(object):
	def __init__(self, sql):
		self.username   = sql.username
		self.password   = custom.Bcrypt(sql.password)
		self.owner      = sql.owner
		self.created_at = sql.created_at
		self.updated_at = sql.updated_at
	def __str__(self):
		return self.username

class UserManager(sm.SuperManager):
	def __init__(self):
		super(UserManager, self).__init__('main',User)
		self.fields = ['username','password','owner_type','owner_id']
		self.validations = [
			sm.Present('username','Please enter a username.'),
			sm.Unique(self,'username','This username is taken. Please select another.'),
			sm.Present('password','Please enter a password'),
			sm.Regular('password', r'^$|^.{8,}$','Password is too short. It should be at least 8 characters.'),
			sm.Present('pw_confm','Please confirm your password'),
			sm.Confirmation('pw_confm','password','Passwords do not match.')
		]

class USER(models.Model):
	username   = models.CharField(max_length=30, unique=True)
	password   = custom.BcryptField()
	owner      = custom.PolymorphicField('owner', UserManager, [FAMILY,STUDENT])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects    = UserManager()