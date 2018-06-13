from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.data import sub, Each, find_all
from Utils.security import getyear
from django_mysql import models as sqlmod
from .managers import CourseTrads, Courses, Enrollments, Venues
from .eligex import check_eligex, check_word, calc_status, eligible, audible, status_choices, TRACE
Q = models.Q
from apps.people.managers import Students, Families
from trace import DEV
from datetime import datetime
import pytz, re

class Venue(models.Model):
	id   = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=30)
	address = models.ForeignKey('people.Address', null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "venue"
	objects = Venues
	def stand(self, me):
		return False
	def __str__(self):
		return self.id
	# def __getattribute__(self, field):
	# 	if field in []:
	# 		function = super(Venue, self).__getattribute__(field)
	# 		return function()
	# 	else:
	# 		return super(Venue, self).__getattribute__(field)


class CourseTrad(models.Model):
	# General:
	id         = models.CharField(max_length=2, primary_key=True)
	oid        = models.CharField(max_length=10,default='')
	title      = models.CharField(max_length=50)
	alias      = models.ForeignKey('self', null=True)
	order      = models.FloatField(null=True)
	e          = models.BooleanField(default=True)
	m          = models.BooleanField(default=True)
	# Commitment:
	day        = custom.DayOfWeekField(default='')
	start      = models.TimeField(default="00:00:00")
	end        = models.TimeField(default="00:00:00")
	nMeets     = models.PositiveIntegerField(default=0)
	place      = models.ForeignKey(Venue, null=True)
	show       = models.CharField(max_length=2, default="")
	sa         = models.BooleanField(default=False)
	semester_choices = [
		('N','Neither'),
		('F','Fall'),
		('S','Spring'),
		('B','Both'),
	]
	semester   = models.CharField(max_length=1,default='N')
	# Prerequisites
	nSlots  = models.PositiveIntegerField(default=0)
	min_age = models.PositiveIntegerField(default=9)
	max_age = models.PositiveIntegerField(default=18)
	min_grd = models.PositiveIntegerField(default=1)
	max_grd = models.PositiveIntegerField(default=12)
	eligex  = models.TextField(default="#")
	default = models.CharField(max_length=8,choices=status_choices)
	# Cost
	early_tuit = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	after_tuit = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	vol_hours  = models.FloatField(default=0)
	the_hours  = models.FloatField(default=0)
	# Behavior
	action_choices = ['none','trig','casc','stat']
	action     = sqlmod.EnumField(choices=action_choices, default='none')
	deferrable = models.BooleanField(default=False) # Whether course may be paid for in October
	droppable  = models.BooleanField(default=True)  # Whether course may be dropped AFTER a successful audition
	# Meta
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "coursetrad"
	objects = CourseTrads

	def stand(self, me):
		if me.owner_type == 'Family':
			return bool(self.courses.filter(enrollment__student__family=me.owner))
		elif me.owner_type == 'Student':
			return bool(self.courses.filter(enrollment__student=me.owner))

	genre_codes = {
		'A':'Acting',
		'B':'Ballet', # Historical
		'C':'Choir',
		'D':'DanceIntensive', # Historical
		# 'E':'',
		'F':'Finale',
		'G':'GeneralAudition',
		'H':'HipHop',
		'I':'Irish',
		'J':'Jazz',
		'K':'PrepaidTickets', # Admin
		'L':'SignLanguage', # Historical
		'M':'Makeup', 
		# 'N':'',
		'O':'Overture', # Historical
		'P':'Tap', # Broadway (Older Beginners)
		# 'Q':'',
		'R':'Statistical',
		'S':'Troupe',
		'T':'Tap',
		# 'U':'',
		# 'V':'',
		'W':'Workshop',
		'X':'Tech',
		# 'Y':'',
		'Z':'Jazz', # Broadway (Older Beginners)
	}
	def genre(self):
		code = self.id[0]
		if code in self.genre_codes:
			return self.genre_codes[code]

	def subid(self):
		return sub(self.id, {
			'SB':'TT',
			'SG':'GB',
			'SJ':'JR',
			'P1':'BT1',
			'P2':'BT2',
			'Z1':'BJ1',
			'Z2':'BJ2',
		})

	def display_semester(self):
		sem = self.semester
		return ' ({})'.format(sem) if sem in 'FS' else ''

	def byFamily(self):
		return '+' in self.eligex

	def courses(self):
		return Courses.filter(tradition_id=self.id)

	def make(self, year):
		course = Courses.fetch(tradition=self, year=year)
		if course:
			return course
		else:
			return Courses.create(tradition=self, year=year)

	def __str__(self):
		return self.title.upper()
	def __getattribute__(self, field):
		if field in ['courses','genre','subid','display_semester']:
			function = super(CourseTrad, self).__getattribute__(field)
			return function()
		else:
			return super(CourseTrad, self).__getattribute__(field)
	
	def eligible(self, student, year):
		if not student.family.has_accepted_policy(year):
			return False
		course = Courses.fetch(tradition=self, year=year)
		if course:
			return course.eligible(student)
		else:
			return self.check_eligex(student, year)


class Course(models.Model):
	# Database Attributes
	id         = models.CharField(max_length=4, primary_key=True)
	year       = models.DecimalField(max_digits=4, decimal_places=0)
	tradition  = models.ForeignKey(CourseTrad, unique_for_year=True, db_column='trad_id')
	nSlots     = models.PositiveIntegerField(default=0)
	title      = models.CharField(max_length=50)
	last_date  = models.DateField(null=True)
	aud_date   = models.DateField(null=True)
	teacher    = models.ForeignKey('people.Teacher', null=True)
	early_tuit = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	after_tuit = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	vol_hours  = models.FloatField()
	the_hours  = models.FloatField()
	approved   = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "course"
	objects = Courses

	def stand(self, me):
		if me.owner_type == 'Family':
			return bool(self.students.filter(family=me.owner))
		elif me.owner_type == 'Student':
			return bool(self.students.filter(id=me.owner.id))

	def tuition(self, asof=datetime.now()):
		cutoff = datetime(year=self.year-1,month=7,day=2)
		return self.early_tuit if asof < cutoff else self.after_tuit

	def slots_open(self):
		if self.nSlots == 0:
			return NotImplemented
		else:
			return max(self.nSlots - len(self.students), 0)

	def enrollments(self):
		return Enrollments.filter(course_id=self.id,status='enrolled')
	def students(self):
		return Students.filter(enrollment__course=self,enrollment__status='enrolled').order_by('family__last','birthday').distinct()
	def boys(self):
		return self.students.filter(sex='M')
	def girls(self):
		return self.students.filter(sex='F')
	def families(self):
		return Families.filter(student__enrollment__course=self).distinct()

	def equipped_students(self):
		result = []
		students = self.students.reverse()
		nOlders = 0
		for s in range(len(students)):
			student = students[s]
			if s and student.family.id == students[s-1].family.id:
				nOlders += 1
			else:
				nOlders = 0
			oldest = s >= len(students)-1 or student.family.id != students[s+1].family.id
			result.append({
				'whole' :student,
				'first' :student.alt_first if student.alt_first else student.first,
				'last'  :student.alt_last if student.alt_last else student.family.last,
				'age'   :student.hst_age_in(self.year),
				'rows'  :nOlders + 1,
				'oldest':oldest
			})
		result.reverse()
		return result

	def students_toggle_enrollments(self):
		result = []
		for enrollment in self.enrollments:
			result.append({'widget':enrollment,'static':Students.get(id=enrollment.student_id)})
		return result

	def conflicts_with(self, other):
		if self.id == other.id:
			return False
		elif self.year != other.year:
			return False
		elif self.nMeets < 5 or other.nMeets < 5:
			return False
		elif self.semester == 'N' or  other.semester == 'N':
			return False
		elif self.semester == 'F' and other.semester == 'S':
			return False
		elif self.semester == 'S' and other.semester == 'F':
			return False
		elif self.day != other.day:
			return False
		elif self.end <= other.start:
			return False
		elif self.start >= other.end:
			return False
		else:
			return True

	def cart(self, student):
		enr = self.enroll(student)
		student.family.fate()
		return enr

	def enroll(self, student, **kwargs):
		enrollment = Enrollments.fetch(course=self,student=student)
		if enrollment:
			enrollment.status = sub(enrollment.status, {
				'aud_drop':'aud_pass',
				'deferred':'maydefer',
			})
			enrollment.save()
		else:
			if eligible(self, student) and self.slots_open:
				enrollment = Enrollments.create(course=self, student=student, status="need_pay")
			elif kwargs.get('passed_audition'):
				enrollment = Enrollments.create(course=self, student=student, status="aud_pass")
			elif audible(self, student) and self.slots_open:
				return Enrollments.create(course=self, student=student, status="aud_pend")
		if self.tradition.action == 'trig':
			self.trig(student)
		return enrollment

	def trig(self, student):
		for casc in Courses.filter(year=self.year,tradition__action='casc'):
			if eligible(casc, student):
				Enrollments.create(course=casc,student=student)
		for stat in Courses.filter(year=self.year,tradition__action='stat'):
			if eligible(stat, student):
				Enrollments.create(course=stat,student=student)

	def __str__(self):
		return '{} ({})'.format(self.title,self.year)

	def __len__(self):
		return len(self.students)

	def __getattribute__(self, field):
		if field in ['students_toggle_enrollments','students','enrollments','prepaid','slots_open']:
			call = super(Course, self).__getattribute__(field)
			return call()
		elif '_' not in field and field not in ['audible','clean','delete','eligible','enroll','id','objects','pk','save','title','tradition'] and hasattr(CourseTrad, field):
			return super(Course, self).__getattribute__('tradition').__getattribute__(field)
		else:
			return super(Course, self).__getattribute__(field)


class Enrollment(models.Model):
	student    = models.ForeignKey('people.Student')
	course     = models.ForeignKey(Course)
	invoice    = models.ForeignKey('payment.Invoice', null=True)
	tuition    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	role       = models.TextField(null=True)
	role_type  = sqlmod.EnumField(choices=['','Chorus','Support','Lead'])
	status_choices = status_choices
	status     = models.CharField(max_length=8,choices=status_choices)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "enrollment"
	objects = Enrollments

	def title(self):
		display = self.get_status_display()
		kwargs = self.title_kwargs()
		# if self.course.tradition.byFamily():
		# 	display = '{family} {proverb} recieving {course} {year}'
		return display.format(**kwargs)
	def title_kwargs(self):
		return {
			'student' : self.student.family if self.course.tradition.byFamily() else self.student,
			'family'  : self.student.family,
			'course'  : self.course.title,
			'year'    : self.course.year,
			'invoice' : self.invoice.id if self.invoice else 0,
			'pronoun' : 'he' if self.student.sex == 'M' else 'she',
			'proverb' : 'was' if self.course.year < getyear() else 'is',
			'audskil' : 'audition' if self.course.id[2] in 'SC' else 'skill assessment',
			'article' : 'an' if self.course.id[2] in 'SC' else 'a',		
		}

	def public_status(self):
		return sub(self.status, {"pendpass":"aud_pend","pendfail":"aud_pend","aud_fail":"fail_pub"})
	def public_title(self):
		real_status = self.status
		self.status = self.public_status
		title = self.title
		self.status = real_status
		return title

	def stand(self, me):
		if me.owner_type == 'Family':
			return self.student.family.id == me.owner.id
		elif me.owner_type == 'Student':
			return self.student.id == me.owner.id

	def price(self):
		if self.tuition:
			return self.tuition
		elif self.status == "enrolled" and self.invoice:
			return self.course.tuition(self.invoice.updated_at)
		else:
			return self.course.tuition()
		
	def pay(self):
		if self.status == "invoiced":
			self.tuition = self.course.tuition()
			self.status = "enrolled"
			self.save()
		return self.tuition

	def accept(self, user):
		if self.status in ["aud_pend","pendpass","pendfail"]:
			if user.permission >= 5:
				# self.course.accept(self.student)
				self.status = "aud_pass" if self.course.tradition.droppable else "aud_lock"
			elif user.permission >= 4:
				self.status = "pendpass"
			self.save()
			self.student.trigger(self.course.year)

	def reject(self, user):
		if self.status in ["aud_pend","pendpass","pendfail"]:
			if user.permission >= 5:
				self.status = "aud_fail"
			elif user.permission >= 4:
				self.status = "pendfail"
			self.save()
			self.student.trigger(self.course.year)

	def fate(self):
		self.status = calc_status(self)
		self.save()
		if self.status in ["not_elig","aud_need","conflict","need_cur","needboth"]:
			self.delete()

	def drop(self):
		if self.status == "aud_pass" and self.course.tradition.droppable:
			self.status = "aud_drop"
			self.save()
			self.student.family.fate()
		elif self.status in ["aud_pend","need_pay"]:
			self.delete()
			self.student.family.fate()
		elif self.status == "invoiced":
			invoice = self.invoice
			self.delete()
			invoice.update_amount()
		if self.course.tradition.action == 'trig':
			self.fate()

	def defer(self):
		if self.status == "maydefer":
			self.status = "deferred"
			self.save()

	def cancel(self):
		if self.status == "invoiced":
			self.status = "nonexist"
			self.save()

	def __str__(self):
		return '{} in {}'.format(self.student, self.course)

	def __getattribute__(self, field):
		if field in ['paid','eligible','display_student','title','public_title','public_status']:
			call = super(Enrollment, self).__getattribute__(field)
			return call()
		elif field in Students.fields:
			return self.student.__getattribute__(field)
		elif field in Courses.fields:
			return self.course.__getattribute__(field)
		else:
			return super(Enrollment, self).__getattribute__(field)


class Year(object):

	def __init__(self, year):
		self.year = year

	def season(self):
		return self.year - 1995

	def spring(self):
		return self.year

	def fall(self):
		return self.year - 1

	def dash(self):
		return "{}-{}".format(self.fall,self.spring)

	def nocent(self):
		return str(self.year)[2:]

	def nSlotsW(self):
		return sum(Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='W')).nSlots)

	def nSlotsS(self):
		return sum(Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='S')).nSlots)

	def nSlotsD(self):
		return sum([
			Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='H')).nSlots,
			Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='I')).nSlots,
			Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='J')).nSlots,
			Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='Z')).nSlots,
			Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='T')).nSlots,
			Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='P')).nSlots,
		])

	def nSlotsX(self):
		return sum(Each(Courses.filter(year=self.year,tradition__e=True,tradition__id__startswith='X')).nSlots)

	def nSlotsSDX(self):
		return sum([self.nSlotsS,self.nSlotsD,self.nSlotsX])

	def __str__(self):
		return "HST Year {}-{}".format(self.fall,self.spring)

	def __getattribute__(self, field):
		if field in ['season','spring','fall','dash','nocent','nSlotsW','nSlotsS','nSlotsD','nSlotsX','nSlotsSDX']:
			call = super(Year, self).__getattribute__(field)
			return call()
		elif len(field) == 2:
			return Courses.fetch(year=self.year,tradition__id=field.upper())
		else:
			return super(Year, self).__getattribute__(field)
