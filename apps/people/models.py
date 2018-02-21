from django.db import models

from .managers import Addresses, Families, Parents, Students, Users
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices

from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.data import collect, copyatts, Each
from Utils.misc import namecase, safe_delete
from Utils.security import getyear

from django_mysql import models as sqlmod
from datetime import datetime
from trace import DEV
Q = models.Q


class Address(models.Model):
	line1      = models.CharField(null=False, max_length=50)
	line2      = models.CharField(default='', max_length=50)
	city       = models.CharField(default='', max_length=25)
	state      = models.CharField(default='', max_length=2)
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
	alt_last   = models.CharField(default='', max_length=30)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	alt_phone  = custom.PhoneNumberField(null=True)
	phone_type = sqlmod.EnumField(choices=['','Home','Cell','Work'], default='')
	alt_email  = models.EmailField(default='')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	hid = NotImplemented
	rest_model = "parent"
	objects = Parents

	def last(self):
		return self.alt_last  if self.alt_last  else self.family.last 
	def phone(self):
		return self.alt_phone if self.alt_phone > 0 else self.family.phone
	def email(self):
		return self.alt_email if self.alt_email else self.family.email
	def family(self):
		return Families.get(id=self.family_id)

	def __getattribute__(self, field):
		if field in ['last','phone','email','family']:
			call = super(Parent, self).__getattribute__(field)
			return call()
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
	address    = models.OneToOneField(Address, null=True, primary_key=False, rel=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	hid = NotImplemented
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

	paid_query = Q(invoice__status='P')
	pend_query = Q( Q(isAudition=False,invoice__status='N') | Q(isAudition=True,happened=False) )
	def enrollments_in(self, year):
		qset = Enrollments.filter(student__family=self, course__year=year).order_by('created_at')
		qset = qset.exclude(isAudition=True,success=False)
		qset = qset.exclude(exists=False)
		return qset
	def paid_enrollments_in(self, year):
		return self.enrollments_in(year).filter(self.paid_query)
	def pend_enrollments_in(self, year):
		return self.enrollments_in(year).filter(self.pend_query)
	def unpaid_enrollments_in(self, year):
		return self.enrollments_in(year).exclude(self.paid_query).exclude(self.pend_query)

	def total_tuition_in(self, year):
		return sum(Each(self.enrollments_in(year)).tuition)
	def paid_tuition_in(self, year):
		return sum(Each(Invoices.filter(family=self,status='P')).amount)
		# return sum(collect(self.enrollments_in(year), lambda enr: 0 if enr.isAudition else enr.course.tuition))
	def pend_tuition_in(self, year):
		return sum(Each(self.pend_enrollments_in(year)).tuition)
		# return sum(Each(Invoices.filter(family=self,status='N')).amount) + sum(Each(Each(Enrollments.filter(student__family=self, course__year=year, isAudition=True, happened=False)).course).tuition)
	def unpaid_tuition_in(self, year):
		return self.total_tuition_in(year) - self.pend_tuition_in(year) - self.paid_tuition_in(year)

	def volunteer_total_in(self, year):
		return max([0.0]+list(collect(self.enrollments_in(year), lambda enr: enr.course.vol_hours)))
	def hours_worked_in(self, year):
		return 0.0
	def hours_signed_in(self, year):
		return 0.0

	def delete(self):
		# Manual cascading for Parents and Users
		safe_delete(self.mother)
		safe_delete(self.father)
		safe_delete(self.address)
		Users.filter(owner=self).delete()
		return super(Family, self).delete()

	def __str__(self):
		return self.last+' Family'
	def __getattribute__(self, field):
		if field in ['mother','father','unique_last','children','enrollments','hours_worked']:
			call = super(Family, self).__getattribute__(field)
			return call()
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
	alt_first = models.CharField(max_length=20, default='')
	middle    = models.CharField(max_length=20, default='')
	alt_last  = models.CharField(max_length=30, default='')
	family    = models.ForeignKey(Family)
	sex       = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	current   = models.BooleanField(default=True)
	birthday  = models.DateField()
	grad_year = models.DecimalField(max_digits=4, decimal_places=0, null=True)
	height    = models.FloatField(null=True)
	alt_phone = custom.PhoneNumberField(null=True)
	alt_email = models.EmailField(default='')
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
	hid = NotImplemented
	objects = Students
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

	# Courtesy functions: student.fxn(course) calls course.fxn(student)
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
		return self.hst_age_in(getyear())
	def grade_in(self, year):
		return year - self.grad_year + 12
	def grade(self):
		return self.grade_in(getyear())

	def enrollments(self):
		return Enrollments.filter(student=self).order_by('course__year')
	def enrollments_in(self, year):
		return self.enrollments.filter(course__year=year)
	def enrollments_before(self, year):
		return self.enrollments.filter(course__year__lt=year)

	def auditions(self):
		return Enrollments.filter(student=self, isAudition=True)
	def auditions_in(self, year):
		return Enrollments.filter(student=self, isAudition=True, course__year=year)
	def courses(self): # TODO: Use a DB join statement instead # As if I know how to do that
		qset = []
		for enrollment in self.enrollments:
			if not enrollment.isAudition or enrollment.success or not enrollment.happened:
				qset.append(Courses.get(id=enrollment.course_id))
		return qset
	def courses_in(self, year): 
		qset = []
		for enrollment in self.enrollments_in(year):
			if not enrollment.isAudition or enrollment.success or not enrollment.happened:
				qset.append(Courses.get(id=enrollment.course_id))
		return qset
	def courses_toggle_enrollments(self):
		qset = []
		for enrollment in self.enrollments:
			qset.append({'widget':enrollment,'static':Courses.get(id=enrollment.course_id)})
		return qset

	def __str__(self):
		return self.prefer+' '+self.last
	def __json__(self):
		obj = copyatts(self,['first','sex','id','alt_first','middle','alt_last','grad_year','height','alt_email','tshirt','current'], False)
		if self.birthday:
			obj['birthday']  = str(self.birthday)
		if int(self.alt_phone):
			obj['alt_phone'] = self.alt_phone
		return obj 
	def __getattribute__(self, field):
		if field in ['hst_age','grade','enrollments','courses','courses_toggle_enrollments','auditions','prefer','last','phone','email','full_name','mother','father']:
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
	hid = NotImplemented
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
		(6,'Admin'),
		(7,'Demo')
	]
	permission = models.PositiveSmallIntegerField(default=0, choices=perm_levels)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "user"
	objects = Users
	def __str__(self):
		return self.username
	# def __getattribute__(self, field):
	# 	if field == 'pw':
	# 		return custom.Bcrypt(super(User, self).__getattribute__('password'))
	# 	else:
	# 		return super(User, self).__getattribute__(field)
