from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from django_mysql import models as sqlmod
from .managers import Addresses, Families, Parents, Students, Users
from datetime import datetime

from apps.program.managers import CourseTrads, Courses, Enrollments, Auditions

class Address(models.Model):
	line1      = models.CharField(null=False, max_length=50)
	line2      = models.CharField(null=True, max_length=50)
	city       = models.CharField(null=True, max_length=25)
	state      = models.CharField(null=True, max_length=2)
	zipcode    = custom.ZipCodeField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "address"
	objects = Addresses
	def __str__(self):
		title = self.line1 + ('\n'+self.line2 if self.line2 else '') + '\n' + self.city + ', ' + self.state + '\n' + str(self.zipcode)
		return title

class Parent(models.Model):
	first      = models.CharField(max_length=20)
	family_id  = models.PositiveIntegerField()
	alt_last   = models.CharField(null=True, max_length=30)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	alt_phone  = custom.PhoneNumberField(null=True)
	phone_type = sqlmod.EnumField(choices=['','Home','Cell','Work'], default='')
	alt_email  = models.EmailField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "parent"
	objects = Parents
	def __getattribute__(self, field):
		if field == '':
			pass
		elif field == 'last':
			if super(Parent, self).__getattribute__('alt_last'):
				return super(Parent, self).__getattribute__('alt_last')
			else: 
				return self.family.last
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
	phone_type = sqlmod.EnumField(choices=['','Home','Cell','Work'], default='')
	email      = models.EmailField()
	mother_id  = models.PositiveIntegerField(null=True)
	father_id  = models.PositiveIntegerField(null=True)
	reg_status = models.PositiveSmallIntegerField(default=0)
	address    = models.OneToOneField(Address, null=True, primary_key=False, rel=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "family"
	objects = Families
	def mother(self):
		return Parents.fetch(id=self.mother_id)
	def father(self):
		return Parents.fetch(id=self.father_id)
	def unique_last(self):
		return self.last
	def children(self):
		return Students.filter(family_id=self.id).order_by('birthday')
	def __str__(self):
		return self.last+' Family'
	def __getattribute__(self, field):
		if field in ['mother','father','unique_last','children']:
			function = super(Family, self).__getattribute__(field)
			return function()
		else:
			return super(Family, self).__getattribute__(field)
	def __setattr__(self, field, value):
		if field == 'mother' and value.__class__ == Parent:
			value.family_id = self.id
			value.save()
			super(Family, self).__setattr__('mother_id', value.id)
			return self.save()
		if field == 'father' and value.__class__ == Parent:
			value.family_id = self.id
			value.save()
			super(Family, self).__setattr__('father_id', value.id)
			return self.save()
		else:
			return super(Family, self).__setattr__(field, value)

class Student(models.Model):
	first     = models.CharField(max_length=20)
	alt_first = models.CharField(max_length=20, null=True)
	middle    = models.CharField(max_length=20, null=True)
	alt_last  = models.CharField(max_length=30, null=True)
	family    = models.ForeignKey(Family)
	sex       = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	current   = models.BooleanField(default=True)
	birthday  = models.DateField()
	grad_year = models.DecimalField(max_digits=4, decimal_places=0, null=True)
	height    = models.FloatField(null=True)
	alt_phone = custom.PhoneNumberField(null=True)
	alt_email = models.EmailField(null=True)
	rest_model = "student"
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
	# Mirror functions: student.fxn(course) calls course.fxn(student)
	def eligible(self, course):
		return course.eligible(self)
	def audible(self, course):
		return course.audible(self)
	def enroll(self, course):
		return course.enroll(self)
	def audition(self, course):
		return course.audition(self)
	def hst_age_in(self, year):
		return year - self.birthday.year - 1
	def hst_age(self):
		now = datetime.now()
		year = now.year + (0 if now.month < 5 else 1)
		return self.hst_age_in(year)
	def grade_in(self, year):
		return year - self.grad_year + 12
	def grade(self):
		now = datetime.now()
		# Switch to the following year on May 1
		year = now.year + (0 if now.month < 5 else 1)
		return self.grade_in(year)
	def enrollments(self):
		return Enrollments.filter(student_id=self.id).order_by('course__year')
	def enrollments_in(self, year):
		return Enrollments.filter(student_id=self.id, course__year=year)
	def courses(self):
		qset = []
		for enrollment in self.enrollments:
			qset.append(Courses.get(id=enrollment.course_id))
		return qset
	def courses_toggle_enrollments(self):
		qset = []
		for enrollment in self.enrollments:
			qset.append({'widget':enrollment,'static':Courses.get(id=enrollment.course_id)})
		return qset
	def prefer(self):
		return self.alt_first if self.alt_first else self.first
	def last(self):
		return self.alt_last  if self.alt_last  else self.family.last
	def phone(self):
		return self.alt_phone if self.alt_phone else self.family.phone
	def email(self):
		return self.alt_email if self.alt_email else self.family.email
	def full_name(self):
		return ' '.join([self.first,self.middle,self.last] if self.middle else [self.first,self.last])
	def mother(self):
		return self.family.mother
	def father(self):
		return self.family.father
	def __str__(self):
		return self.prefer+' '+self.last
	def __getattribute__(self, field):
		if field in ['hst_age','grade','enrollments','courses','courses_toggle_enrollments','prefer','last','phone','email','full_name','mother','father']:
			call = super(Student, self).__getattribute__(field)
			return call()
		else:
			return super(Student, self).__getattribute__(field)

class Teacher(models.Model):
	first      = models.CharField(max_length=20)
	last       = models.CharField(max_length=30)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	phone      = custom.PhoneNumberField()
	email      = models.EmailField()
	address    = models.OneToOneField(Address, null=True, primary_key=False, rel=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "teacher"

class User(models.Model):
	username   = models.CharField(max_length=30, unique=True)
	password   = custom.BcryptField()
	owner      = custom.PolymorphicField('owner', Users, [Family,Student,Teacher,Parent])
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
	rest_model = "user"
	objects = Users
	def __str__(self):
		return self.username
	def __getattribute__(self, field):
		if field == 'pw':
			return custom.Bcrypt(super(User, self).__getattribute__('password'))
		else:
			return super(User, self).__getattribute__(field)
