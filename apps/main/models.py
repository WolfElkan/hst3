from __future__ import unicode_literals
from django.db import models
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
from . import custom_fields as custom
from . import supermodel as sm

# Create your models here.

class FamilyManager(sm.SuperManager):
	def __init__(self):
		super(FamilyManager, self).__init__('main','family')
		self.fields = ['last','phone','email','joined_hst']
		self.validations = [
			sm.Validation('last', r'.+'      , 'Please enter the family surname, as used by the children.'),
			sm.Validation('last', r'^.{,30}$', 'Name is too long.  Max is 30 characters.'),
			sm.Validation('phone',r'.+'      , 'Please enter the main family phone number.'),
			sm.Validation('phone',r'.+'      , 'Please enter a valid 10-digit phone number.'),
			sm.Validation('email',r'.+'      , 'Please enter an email address.'),
			sm.Validation('email',r''        , 'Please enter a valid email address.'),
		]

class Family(models.Model):
	last       = models.CharField(max_length=30)
	phone      = models.DecimalField(max_digits=11, decimal_places=0)
	email      = models.EmailField()
	joined_hst = models.DecimalField(max_digits=4, decimal_places=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects    = FamilyManager()
	def __str__(self):
		return self.last+' Family'

class Student(models.Model):
	first      = models.CharField(max_length=20)
	middle     = models.CharField(max_length=20)
	last       = models.CharField(max_length=30)
	prefer     = models.CharField(max_length=20)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	family     = models.ForeignKey(Family, related_name='children')
	birthday   = models.DateField()
	height     = models.FloatField()
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
	def _prefer(self):
		return self.first if self.prefer == '' else self.prefer
	def _last(self):
		return self.last
	def __str__(self):
		return self._prefer()+' '+self._last()

class UserManager(sm.SuperManager):
	def __init__(self):
		super(UserManager, self).__init__('main','user')
		self.fields = ['username','password','owner_type','owner_id']
		self.validations = []
	def isValid(self, data):
		return True

class User(models.Model):
	username   = models.CharField(max_length=30)
	password   = custom.BcryptField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	# owner    = custom.PolymorphicField([Family,Student,'Faculty','Admin'])
	owner_types = [('F','Family'),('S','Student'),('T','Faculty'),('A','Admin')]
	owner_type_models = [Family,Student,None,None]
	owner_type = models.CharField(max_length=1, choices=owner_types)
	owner_id   = models.PositiveIntegerField(null=True)
	def owner(self):
		for x in xrange(len(self.owner_types)):
			if self.owner_type == self.owner_types[x][0]:
				owner_type_model = self.owner_type_models[x]
		return owner_type_model.objects.get(id=self.owner_id)
	objects = UserManager()

class Parent(models.Model):
	first      = models.CharField(max_length=20)
	last       = models.CharField(max_length=30)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	def __str__(self):
		if self.sex == 'M':
			prefix = 'Mr. '
		elif self.sex == 'F':
			prefix == 'Mrs. '
		return prefix+self.first+' '+self._last()

