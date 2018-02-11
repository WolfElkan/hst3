from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.hacks import sub, Each
from django_mysql import models as sqlmod
from .managers import CourseTrads, Courses, Enrollments
Q = models.Q
from apps.main.managers import Students
from trace import TRACE, DEV
import re

ELG = False

class Venue(models.Model):
	id   = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=30)
	address = models.ForeignKey('main.Address', null=True)
	rest_model = "venue"
	# def __getattribute__(self, field):
	# 	if field in []:
	# 		function = super(Venue, self).__getattribute__(field)
	# 		return function()
	# 	else:
	# 		return super(Venue, self).__getattribute__(field)

class CourseTrad(models.Model):
	# General:
	id         = models.CharField(max_length=2, primary_key=True)
	title      = models.CharField(max_length=50)
	alias      = models.ForeignKey('self', null=True)
	order      = models.FloatField(null=True)
	e          = models.BooleanField(default=True)
	# Commitment:
	day        = custom.DayOfWeekField(default='')
	start      = models.TimeField(default="00:00:00")
	end        = models.TimeField(default="00:00:00")
	nMeets     = models.PositiveIntegerField(default=0)
	place      = models.ForeignKey(Venue, null=True)
	show       = models.CharField(max_length=2, default="")
	vs         = models.BooleanField(default=False)
	# Prerequisites
	min_age = models.PositiveIntegerField(default=9)
	max_age = models.PositiveIntegerField(default=18)
	min_grd = models.PositiveIntegerField(default=1)
	max_grd = models.PositiveIntegerField(default=12)
	prereqs = models.TextField(default="{ a g }")
	# Cost
	tuition    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	redtuit    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	vol_hours  = models.FloatField(default=0)
	the_hours  = models.FloatField(default=0)
	prepaid    = models.BooleanField(default=False)
	rest_model = "coursetrad"
	genre_codes = {
		'A':'Acting',
		# 'B':'Ballet',
		'C':'Choir',
		# 'D':'Dance Intensive',
		# 'E':'',
		'F':'Finale',
		'G':'General Audition',
		'H':'Jazz/Hip-Hop',
		'I':'Irish',
		'J':'Jazz',
		# 'K':'Prepaid Tickets',
		# 'L':'Sign Language',
		# 'M':'',
		# 'N':'',
		'O':'Overture',
		'P':'Tap',
		# 'Q':'',
		# 'R':'',
		'S':'Troupe',
		'T':'Tap',
		# 'U':'',
		# 'V':'',
		'W':'Workshop',
		'X':'Tech',
		# 'Y':'',
		'Z':'Jazz',
	}
	objects = CourseTrads
	def __str__(self):
		return self.title.upper()
	def courses(self):
		return Courses.filter(tradition_id=self.id)
	def make(self, year):
		return Courses.create(tradition=self, year=year)
	def genre(self):
		code = self.id[0]
		if code in self.genre_codes:
			return self.genre_codes[code]
	def check_eligex(self, student, year, **kwargs):
		if re.match(r'<[^>]*<|{[^}]*{',self.prereqs):
			print 'Nested clauses of the same type are not currently supported.  Call Wolf if you need this changed.'
		eligex = kwargs.pop('eligex') if 'eligex' in kwargs else self.prereqs
		conj   = kwargs.pop('conj')   if 'conj'   in kwargs else True
		kwargs['aud'] = kwargs['aud'] if 'aud' in kwargs else False
		kwargs['cur'] = kwargs['cur'] if 'cur' in kwargs else False
		matches = re.findall(r'(!?){([^}]*)}|(!?)<([^>]*)>|(!?)([^<>{} ]*)', eligex)
		for x in matches:
			if x[1]:
				kwargs['eligex'] = x[1]
				kwargs['conj'] = True
				result = self.check_eligex(student, year, **kwargs)
				result = not result if x[0] else result
			elif x[3]:
				kwargs['eligex'] = x[3]
				result = self.check_eligex(student, year, **kwargs)
				result = not result if x[2] else result
			elif x[5]:
				result = self.check_word(student, year, x[5], **kwargs)
				result = not result if x[4] else result
			else:
				result = conj
			if result != conj:
				return result
		return conj
	def check_word(self, student, year, word, **kwargs):
		if '#' in word:
			return True
		elif 'm' in word:
			return student.sex == 'M'
		elif 'f' in word:
			return student.sex == 'F'
		elif 'a' in word:
			# print word, student.hst_age_in(year)
			result = student.hst_age_in(year) >= self.min_age - word.count('y') and student.hst_age_in(year) <= self.max_age + word.count('o')
			# print result
			return result
		elif 'g' in word:
			if not student.grad_year:
				return True
			return student.grade_in(year)   >= self.min_grd - word.count('y') and student.grade_in(year)   <= self.max_grd + word.count('o')
		else:
			query = {
				'student':student,
				'isAudition':False,
			}
			if '*' not in word:
				query['course__tradition__id'] = word[0:2]
			elif word[0] is not '*':
				query['course__tradition__id__startswith'] = word[0]
			elif word[1] is not '*':
				query['course__tradition__id__endswith'] = word[1]
			if 'c' in word:
				if kwargs['cur']:
					return True
				query['course__year'] = year
			if 'p' in word:
				query['course__year__lt'] = year
			if '@' in word:
				if kwargs['aud']:
					return True
				query['isAudition'] = True
				query['success'] = True
			if '$' in word:
				query['paid'] = True
			return bool(Enrollments.filter(**query))
	# def eligible(self, student, year):
	# 	self.check_eligex(student, year)
	# 	return {
	# 		# Whether student is eligible under current actual circumstances
	# 		'now' : self.check_eligex(student, year), 
	# 		# Whether student is eligible ignoring all audition requirements
	# 		'aud' : self.check_eligex(student, year, aud=True), 
	# 		# Whether student is eligible ignoring audition and current enrollment requirements
	# 		'cur' : self.check_eligex(student, year, aud=True, cur=True), 
	# 		'reason': '{} is eligible for {} in {}'.format(student, self.title, year),
	# 		'css': '',
	# 	}
	def enroll(self, student, year):
		course = Courses.fetch(tradition=self, year=year)
		if course and course.eligible(student):
			return course.enroll(student)
	def audition(self, student, year):
		course = Courses.fetch(tradition=self, year=year)
		if course and course.audible(student):
			return course.audition(student)
	def __getattribute__(self, field):
		if field in ['courses','genre']:
			function = super(CourseTrad, self).__getattribute__(field)
			return function()
		else:
			return super(CourseTrad, self).__getattribute__(field)

class Course(models.Model):
	id         = models.CharField(max_length=4, primary_key=True)
	year       = models.DecimalField(max_digits=4, decimal_places=0)
	tradition  = models.ForeignKey(CourseTrad, unique_for_year=True, db_column='trad_id')
	last_date  = models.DateField(null=True)
	aud_date   = models.DateField(null=True)
	teacher    = models.ForeignKey('main.Teacher', null=True)
	tuition    = models.DecimalField(max_digits=6, decimal_places=2)
	vol_hours  = models.FloatField()
	the_hours  = models.FloatField()
	prepaid    = models.BooleanField()
	rest_model = "course"
	objects = Courses
	def enrollments(self):
		return Enrollments.filter(course_id=self.id)
	def students(self):
		qset = []
		for enrollment in self.enrollments:
			qset.append(Students.get(id=enrollment.student_id))
		return qset
	def students_toggle_enrollments(self):
		qset = []
		for enrollment in self.enrollments:
			qset.append({'widget':enrollment,'static':Students.get(id=enrollment.student_id)})
		return qset
	def __str__(self):
		return self.title+' ('+str(self.year)+')'
	def eligible(self, student):
		elig = {
			'now':False,
			'aud':False,
		}
		enrollment = Enrollments.fetch(course=self, student=student)
		if enrollment:
			if enrollment.isAudition:
				elig['reason'] = '{} has scheduled an audition for {}'.format(student, self)
				elig['css'] = "audition"
			elif enrollment.paid:
				elig['reason'] = '{} has successfully enrolled in {}'.format(student, self)
				elig['css'] = "enrolled"
			else:
				elig['reason'] = '{} is registered for {} pending tuition payment'
				elig['css'] = "need_pay"

		# Check if not eligible under any circumstances
		elif not self.tradition.check_eligex(student, self.year, aud=True, cur=True):
			
			# not_elig
			elig['reason'] = '{} is not eligible for {}'
			elig['css'] = "not_elig"

		# Check for conflicts
		elif any(Each(student.courses_in(self.year)).conflicts_with(self)):

			# conflict
			elig['reason'] = '{} is in another class at the same time as {}'
			elig['css'] = "conflict"
		
		# Check if eligible now
		elif self.tradition.check_eligex(student, self.year):

			# eligible
			elig['reason'] = '{} is eligible to register for {}'
			elig['css'] = "eligible"
			elig['now'] = True

		# Check if eligible with audition
		elif self.tradition.check_eligex(student, self.year, aud=True):

			# need_aud
			elig['reason'] = '{} is eligible to audition for {}'
			elig['css'] = "need_aud"
			elig['aud'] = True

		# Check if eligible with current enrollment
		elif self.tradition.check_eligex(student, self.year, cur=True):

			# need_cur
			elig['reason'] = '{} will be eligible for {} once {} enrolls in at least 1 other class'
			elig['css'] = "need_cur" 

		elif self.tradition.check_eligex(student, self.year, cur=True):

			# need_cur (Same css, only reason is different)
			elig['reason'] = '{} will be eligible to audition for {} once {} enrolls in at least 1 other class'
			elig['css'] = "need_cur" 

		elig['reason'] = elig['reason'].format(student, self.title, 'he' if student.sex == 'M' else 'she')
		return elig
	def enroll(self, student):
		if self.eligible(student):
			return Enrollments.create(course=self, student=student)
	def sudo_enroll(self, student):
		return Enrollments.create(course=self, student=student)
	def audition(self, student):
		if self.audible(student):
			return Enrollments.create(course=self, student=student, isAudition=True)
	def conflicts_with(self, other):
		if self.year != other.year:
			return False
		elif self.day != other.day:
			return False
		elif self.end < other.start:
			return False
		elif self.start > other.end:
			return False
		else:
			return True
	def __getattribute__(self, field):
		if field in ['students_toggle_enrollments','students','enrollments']:
			call = super(Course, self).__getattribute__(field)
			return call()
		elif '_' not in field and field not in ['audible','clean','delete','eligible','enroll','id','objects','pk','save','tradition'] and hasattr(CourseTrad, field):
			return super(Course, self).__getattribute__('tradition').__getattribute__(field)
		else:
			return super(Course, self).__getattribute__(field)

class Enrollment(models.Model):
	student    = models.ForeignKey('main.Student')
	course     = models.ForeignKey(Course)
	isAudition = models.BooleanField(default=False)
	role       = models.TextField(null=True)
	role_type  = sqlmod.EnumField(choices=['','Chorus','Support','Lead'])
	paid       = models.BooleanField(default=False)
	auto       = models.BooleanField(default=False)
	ret_status = models.BooleanField(default=False)
	happened   = models.BooleanField(default=False)
	success    = models.NullBooleanField()	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "enrollment"
	objects = Enrollments
	def __str__(self):
		return str(self.student) + (' as '+self.role if self.role else '') + ' in ' + str(self.course)
	# def __getattribute__(self, field):
	# 	if field in []:
	# 		function = super(Enrollment, self).__getattribute__(field)
	# 		return function()
	# 	else:
	# 		return super(Enrollment, self).__getattribute__(field)