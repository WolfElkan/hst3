from django.db import models

from .managers import Addresses, Families, Parents, Students, Users, NameClashes, Teachers
from apps.program.managers import CourseTrads, Courses, Enrollments, Venues
from apps.payment.managers import Invoices
from apps.radmin.managers  import Policies

from apps.program.eligex import calc_status, eligible

from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.data import collect, copyatts, Each, find_all
from Utils.misc import namecase, safe_delete
from Utils.security import getyear
from Utils.debug import pretty

from django_mysql import models as sqlmod
from datetime import datetime
#from trace import DEV
import trace
Q = models.Q

sex_choices = [('M','Male'),('F','Female')]

class Address(models.Model):
	line1      = models.CharField(null=False, max_length=50)
	line2      = models.CharField(default='', max_length=50)
	city       = models.CharField(default='', max_length=25)
	state      = models.CharField(default='', max_length= 2)
	zipcode    = custom.ZipCodeField()
	# lattitude  = models.DecimalField(null=True, max_digits=10, decimal_places=6)
	# longitude  = models.DecimalField(null=True, max_digits=10, decimal_places=6)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "address"
	objects = Addresses
	def stand(self, me):
		if me.owner_type == 'Family':
			family = me.owner
		elif me.owner_type == 'Student':
			family = me.owner.family
		else:
			family = None
		return family and family.address.id == self.id
	def owner(self):
		return Families.fetch(address=self) or Venues.fetch(address=self) or Teacher.objects.fetch(address=self)
	def __getattribute__(self, field):
		if field in ['owner']:
			call = super(Address, self).__getattribute__(field)
			return call()
		else:
			return super(Address, self).__getattribute__(field)	
	def __str__(self):
		title = self.line1 + ('\n'+self.line2 if self.line2 else '') + '\n' + self.city + ', ' + self.state + '\n' + str(self.zipcode)
		return title


class Parent(models.Model):
	hid        = models.CharField(max_length=7, null=True)
	first      = models.CharField(max_length=20)
	family_id  = models.PositiveIntegerField()
	alt_last   = models.CharField(default='', max_length=30)
	sex_choices= sex_choices
	sex        = models.CharField(max_length=1, choices=sex_choices)
	alt_phone  = custom.PhoneNumberField(null=True)
	phone_type = sqlmod.EnumField(choices=['','Home','Cell','Work'], default='')
	alt_email  = models.EmailField(default='')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
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

	def stand(self, me):
		if me.owner_type == 'Family':
			family = me.owner
		elif me.owner_type == 'Student':
			family = me.owner.family
		else:
			family = None
		return self.family.id == family.id
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


# Current and Alumni families are both kept in this table.
class Family(models.Model):
	hid        = models.CharField(max_length=10, null=True)
	oid        = models.PositiveIntegerField(default=0)
	last       = models.CharField(max_length=30)
	name_num   = models.PositiveIntegerField(default=0)
	phone      = custom.PhoneNumberField()
	phone_type = sqlmod.EnumField(choices=['','Home','Cell','Work'], default='')
	email      = models.EmailField()
	mother     = models.ForeignKey(Parent, null=True, related_name='mother')
	father     = models.ForeignKey(Parent, null=True, related_name='father')
	address    = models.OneToOneField(Address, null=True, primary_key=False, rel=True)
	policyYear = models.DecimalField(max_digits=4, decimal_places=0, null=True)
	policyPage = models.PositiveIntegerField(default=0)
	policyDate = models.DateTimeField(null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "family"
	objects = Families

	def stand(self, me):
		if me.owner_type == 'Family':
			family = me.owner
		elif me.owner_type == 'Student':
			family = me.owner.family
		else:
			family = None
		return self.id == family.id

	def has_accepted_policy(self, year=getyear()):
		policy = Policies.fetch(year=year)
		return not policy or self.policyYear == year and self.policyPage == policy.nPages

	def unique_last(self):
		return '{} #{}'.format(self.last,self.name_num) if self.name_num else self.last
	def unique_last_in(self, year):
		clashes = Families.filter(last=self.last,student__enrollment__course__year=year).exclude(id=self.id)
		if clashes:
			return self.unique_last
		else:
			return self.last

	def children(self):
		return Students.filter(family_id=self.id).order_by('birthday')
	def children_enrolled_in(self,year):
		return self.children.filter(enrollment__course__year=year).distinct()

	def all_enrollments_in(self, year):
		return Enrollments.filter(student__family=self, course__year=year)
	def all_enrollments(self):
		return self.all_enrollments_in(getyear())
	def enrollments_in(self, year):
		qset = self.all_enrollments_in(year)
		qset = qset.exclude(status__in=['nonexist','aud_fail','aud_drop'])
		qset = qset.order_by('created_at')
		return qset
	def enrollments(self):
		return self.enrollments_in(getyear())
	def live_enrollments_in(self, year):
		qset = self.all_enrollments_in(year)
		qset = qset.filter(status__in=['enrolled','invoiced','need_pay','aud_pend','pendpass','pendfail','pend_pub','fail_pub','aud_pass','aud_drop','aud_lock','maydefer','deferred'])
		qset = qset.order_by('created_at')
		return qset
	def live_enrollments(self):
		return self.live_enrollments_in(getyear())


	def total_tuition_in(self, year):
		return sum(Each(Each(self.enrollments_in(year)).course).tuition)
	def paid_tuition_in(self, year):
		return sum(Each(Invoices.filter(family=self,status='P')).amount)
		# return sum(collect(self.enrollments_in(year), lambda enr: 0 if enr.isAudition else enr.course.tuition()))
	def pend_tuition_in(self, year):
		return sum(Each(Each(self.pend_enrollments_in(year)).course).tuition)
		# return sum(Each(Invoices.filter(family=self,status='N')).amount) + sum(Each(Each(Enrollments.filter(student__family=self, course__year=year, isAudition=True, happened=False)).course).tuition)
	def unpaid_tuition_in(self, year):
		return self.total_tuition_in(year) - self.pend_tuition_in(year) - self.paid_tuition_in(year)

	def volunteer_total_in(self, year):
		return max([0.0]+list(collect(self.enrollments_in(year), lambda enr: enr.course.vol_hours)))
	def hours_worked_in(self, year):
		return 0.0
	def hours_signed_in(self, year):
		return 0.0

	def fate(self, year=None):
		if not year:
			year = getyear()
		Each(self.children).fate(year)
	def delete(self):
		# Manual cascading for Parents and Users
		safe_delete(self.mother)
		safe_delete(self.father)
		safe_delete(self.address)
		Users.filter(owner=self).delete()
		return super(Family, self).delete()
	def clear_name_num(self):
		self.name_num = 0
		self.save()
	def update_name_num(self, fix_all=False):
		clashes = Families.filter(last=self.last).exclude(id=self.id)
		older = clashes.filter(created_at__lt=self.created_at)
		if fix_all:
			Each(older).update_name_num()
		if older:
			self.name_num = max(Each(older).name_num) + 1
		else:
			self.name_num = int(bool(clashes))
		self.save()
		if fix_all:
			newer = clashes.filter(created_at__lt=self.created_at)
			Each(newer).update_name_num()
		return self.name_num
	def __str__(self):
		# return ('{} Family #{}' if self.name_num else '{} Family').format(self.last,self.name_num)
		return '{} Family'.format(self.last)
	def __getattribute__(self, field):
		if field in ['unique_last','children','enrollments','hours_worked']:
			call = super(Family, self).__getattribute__(field)
			return call()
		else:
			return super(Family, self).__getattribute__(field)


# Current students, alumni, and prospective students are all kept in this table.
class Student(models.Model):
	hid       = models.CharField(max_length=10, null=True)
	oid       = models.PositiveIntegerField(default=0)
	first     = models.CharField(max_length=20)
	alt_first = models.CharField(max_length=20, default='')
	alt_last  = models.CharField(max_length=30, default='')
	family    = models.ForeignKey(Family)
	sex_choices = sex_choices
	sex       = models.CharField(max_length=1, choices=sex_choices)
	current   = models.BooleanField(default=True)
	birthday  = models.DateField()
	grad_year = models.DecimalField(max_digits=4, decimal_places=0, null=True)
	alt_phone = custom.PhoneNumberField(null=True)
	alt_email = models.EmailField(default='')
	needs     = models.TextField(default='')
	rest_model = "student"
	t_shirt_sizes = [
		('YM','Youth Medium'),
		('YL','Youth Large'),
		('AS','Adult Small'),
		('AM','Adult Medium'),
		('AL','Adult Large'),
		('XL','Adult XL'),
	]
	tshirt     = models.CharField(max_length=2, choices=t_shirt_sizes, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Students
	def stand(self, me):
		if me.owner_type == 'Family':
			return me.owner.id == self.family.id
		elif me.owner_type == 'Student':
			return me.owner.family.id == self.family.id
	def prefer(self):
		return self.alt_first if self.alt_first else self.first
	def last(self):
		return self.alt_last  if self.alt_last  else self.family.last
	def phone(self):
		return self.alt_phone if self.alt_phone else self.family.phone
	def email(self):
		return self.alt_email if self.alt_email else self.family.email
	def full_name(self):
		return ' '.join([self.first,self.last])
	def mother(self):
		return self.family.mother
	def father(self):
		return self.family.father

	def infolock(self):
		return getyear() != 2019 and self.family.policyDate > self.created_at

	# Courtesy functions: student.fxn(course) calls course.fxn(student)
	# def eligible(self, course):
	# 	return course.eligible(self)
	# def audible(self, course):
	# 	return course.audible(self)
	# def enroll(self, course):
	# 	return course.enroll(self)
	# def audition(self, course):
	# 	return course.audition(self)

	def hst_age_in(self, year):
		return year - self.birthday.year - 1
	def hst_age(self):
		return self.hst_age_in(getyear())
	def grade_in(self, year):
		if self.grad_year:
			return year - self.grad_year + 12
	def grade(self):
		return self.grade_in(getyear())

	def enrollments(self):
		return Enrollments.filter(student=self).order_by('course__year').exclude(status__in=['nonexist','aud_fail','aud_drop'])
	def enrollments_in(self, year):
		return self.enrollments.filter(course__year=year)
	def enrollments_before(self, year):
		return self.enrollments.filter(course__year__lt=year)
	def trigger(self, year):
		for course in Courses.filter(year=year,tradition__action='auto'):
			course.enroll(self)

	def auditions(self):
		return Enrollments.filter(student=self, status__startswith="aud")
	def auditions_in(self, year):
		return Enrollments.filter(student=self, status__startswith="aud", course__year=year)
	def courses(self): 
		return Courses.filter(enrollment__in=self.enrollments)
	def courses_in(self, year):
		return self.courses.filter(year=year)
	def courses_toggle_enrollments(self):
		qset = []
		for enrollment in self.enrollments:
			qset.append({'widget':enrollment,'static':Courses.get(id=enrollment.course_id)})
		return qset
	def course_menu(self, year=getyear()):
		courses = Courses.filter(year=year,tradition__e=True,tradition__m=True)
		courses = courses.order_by('tradition__order')
		for course in courses:
			enrollment = Enrollments.fetch(student=self,course=course)
			if not enrollment or enrollment.status == 'nonexist':
				enrollment = Enrollments.model(student=self,course=course)
				enrollment.status = calc_status(enrollment)
			yield enrollment
	def fate(self, year=None):
		if not year:
			year = getyear()
		for enrollment in self.enrollments_in(year):
			if not eligible(enrollment.course, self):
				enrollment.delete()
		while True:
			drops = self.enrollments_in(year)
			for drop in drops:
				if eligible(drop.course, self):
					drops = drops.exclude(id=drop.id)
				else:
					drop.delete()
			if not drops:
				break

		# for auto_trad in CourseTrads.filter(action='auto'):
		# 	# print auto_trad
		# 	auto_course = Courses.fetch(year=year,tradition=auto_trad)
		# 	if auto_course:
		# 		enrollment = Enrollments.fetch(student=self,course=auto_course)
		# 		if enrollment:
		# 			enrollment.fate()
		# 		elif eligible(auto_course, self):
		# 			Enrollments.create(student=self,course=auto_course)
	def __str__(self):
		return self.prefer+' '+self.last
	def __json__(self):
		obj = copyatts(self,['first','sex','id','alt_first','alt_last','grad_year','alt_email','tshirt','current'], False)
		if self.birthday:
			obj['birthday']  = str(self.birthday)
		if int(self.alt_phone):
			obj['alt_phone'] = self.alt_phone
		return obj 
	def __getattribute__(self, field):
		auto_methods = [
			'hst_age',
			'grade',
			'enrollments',
			'courses',
			'courses_toggle_enrollments',
			'auditions',
			'prefer',
			'last',
			'phone',
			'email',
			'full_name',
			'mother',
			'father'
		]
		if field in auto_methods:
			call = super(Student, self).__getattribute__(field)
			return call()
		else:
			return super(Student, self).__getattribute__(field)

		
class Teacher(models.Model):
	hid = NotImplemented
	first      = models.CharField(max_length=20)
	last       = models.CharField(max_length=30)
	sex        = models.CharField(max_length=1, choices=[('M','Male'),('F','Female')])
	phone      = custom.PhoneNumberField()
	email      = models.EmailField()
	address    = models.OneToOneField(Address, null=True, primary_key=False, rel=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = Teachers
	rest_model = "teacher"
	def stand(self, me):
		if me.owner_type == 'Family':
			return False
		elif me.owner_type == 'Student':
			return bool(Enrollments.filter(student_id=me.owner.id,course__teacher=self))
	def courses(self):
		pass
	def __getattribute__(self, field):
		if field in ['courses']:
			call = super(Teacher, self).__getattribute__(field)
			return call()
		else:
			return super(Teacher, self).__getattribute__(field)


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
		(5,'Board'),
		(6,'Admin'),
		(7,'Developer')
	]
	default_val = 7 * int(False)
	permission = models.PositiveSmallIntegerField(default=default_val, choices=perm_levels)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "user"
	objects = Users
	def stand(self, me):
		return self.id == me.id
	def __str__(self):
		return self.username
	def __getattribute__(self, field):
		if field in ['get_permission_display']:
			call = super(User, self).__getattribute__(field)
			return call()
		else:
			return super(User, self).__getattribute__(field)
