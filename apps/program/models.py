from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.hacks import sub
from django_mysql import models as sqlmod
from .managers import CourseTrads, Courses, Enrollments
Q = models.Q
from apps.main.managers import Students
from trace import TRACE, DEV

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
	M = models.BooleanField(default=True)  # Boys may enroll
	F = models.BooleanField(default=True)  # Girls may enroll
	C = models.BooleanField(default=False) # Only current students may enroll
	I = models.BooleanField(default=False) # 1 year IS or T* or P* required
	A_levels = [
		(0, 'needs no audition to enroll in'),
		(1, 'must pass a skills assessment (or have already taken this class) to enroll in'),
		(2, 'must take 1 year of Acting A or B required to enroll in'),
		(3, 'must take 1 year of Acting A or B required to audition for'),
		(4, 'must take 1 year of Acting and 1 year of Troupe required to audition for'),
		(5, 'must audition for')
	]
	eL = [
		lambda self, past, auds: 
			True,
		lambda self, past, auds: 
			auds.filter(course__tradition=self, success=True) or past.filter(course__tradition=self),
		lambda self, past, auds: 
			past.filter(id__startswith='A'),
		lambda self, past, auds: 
			auds.filter(course__tradition=self, success=True),
		lambda self, past, auds: 
			auds.filter(course__tradition=self, success=True),
	]
	aL = {
		0: lambda self, past: 
			True,
		1: lambda self, past: past.filter(
			id__startswith=sub(self.id[:1],{'P':'T','Z':'J'}), id__endswith=int(self.id[1:])-1),
		2: lambda self, past: 
			False,
		3: lambda self, past: 
			past.filter(id__startswith='A'),
		4: lambda self, past: 
			past.filter(id__startswith='A') and past.filter(id__startswith='S'),
	}

	A = custom.TinyIntegerField(default=0, choices=A_levels) # Audition Required
	# Cost
	tuition    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	redtuit    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	vol_hours  = models.FloatField(default=0)
	the_hours  = models.FloatField(default=0)
	prepaid    = models.BooleanField(default=False)
	rest_model = "coursetrad"
	objects = CourseTrads
	def __str__(self):
		return self.title.upper()
	def courses(self):
		return Courses.filter(tradition_id=self.id)
	def make(self, year):
		return Courses.create(tradition=self, year=year)
	def genre(self):
		code = self.id[0]
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
			# 'K':'Tickets',
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
		if code in genre_codes:
			return genre_codes[code]
	def eligible(self, student, year, check_C=True):
		if student.hst_age_in(year) < self.min_age:
			if ELG:
				print '{} is too young for {}'.format(student, self)
			return False  # Too young
		if student.hst_age_in(year) > self.max_age:
			if ELG:
				print '{} is too old for {}'.format(student, self)
			return False  # Too old
		if student.grad_year and student.grade_in(year) < self.min_grd:
			if ELG:
				print '{} is too young academically for {}'.format(student, self)
			return False  # Too young academically
		if student.grad_year and student.grade_in(year) > self.max_grd:
			if ELG:
				print '{} is too old academically for {}'.format(student, self)
			return False  # Too old academically
		if str(student.sex) == 'M' and not self.M:
			if ELG:
				print '{} is a boy and not allowed in {}'.format(student, self)
			return False  # No boys allowed
		if str(student.sex) == 'F' and not self.F:
			if ELG:
				print '{} is a girl and not allowed in {}'.format(student, self)
			return False  # No girls allowed
		if check_C and self.C and not student.enrollments_in(year):
			if ELG:
				print '{} is not a current student for {}'.format(student, self)
			return False  # Current students only
		tpi = Q(
			Q(course__tradition__id__startswith='T') | # Tap Courses
			Q(course__tradition__id__startswith='P') | # Broadway Tap Courses
			Q(course__tradition__id__startswith='I')   # Irish Dance Courses
		)
		if self.I and not student.enrollments.filter(tpi, course__year__lt=year):
			if ELG:
				print '{} has not taken Irish or Tap required for {}'.format(student, self)
			return False  # Irish or Tap required
		if self.A == 0:
			if ELG:
				print '{} is eligible for {}!'.format(student, self)
			return True
		elif self.A == 1:
			return bool(
				student.auditions_in(year).filter(course__tradition=self, success=True) or 
				student.enrollments_before(year).filter(course__tradition=self)
			)
		elif self.A == 2:
			return bool(student.enrollments_before(year).filter(id__startswith='A'))
		elif self.A in [3,4]:
			return bool(student.auditions_in(year).filter(course__tradition=self, success=True))
		elif self.A == 5:
			return True
		# return bool(self.eL[self.A](self,student.enrollments_before(year),student.auditions_in(year)))
	def audible(self, student, year):
			if ELG:
				print student, self.get_A_display(), self, year
			if self.A == 0:
				return self.eligible(student, year)
			elif self.A == 1:
				return student.enrollments_before(year).filter(
					id__startswith=sub(self.id[:1],{'P':'T','Z':'J'}), 
					id__endswith=int(self.id[1:])-1
				)
			elif self.A == 2:
				return False
			elif self.A == 3:
				return student.enrollments_before(year).filter(id__startswith='A') or (DEV and student.enrollments_before(year).filter(id__startswith='S'))
			elif self.A == 4:
				return student.enrollments_before(year).filter(id__startswith='A') and student.enrollments_before(year).filter(id__startswith='S')
			elif self.A == 5:
				return student.enrollments_in(year)
		# return bool(self.aL[self.A](self,student.enrollments_before(year)))
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
		return self.tradition.eligible(student, self.year)
	def audible(self, student):
		return self.tradition.audible(student, self.year)
	def eligcss(self, student):
		enrollment = Enrollments.fetch(course=self, student=student)
		if enrollment:
			if enrollment.isAudition:
				if ELG:
					print '{} has scheduled an audition for {}'.format(student, self)
				return "audition" # The student has scheduled an audition for this class
			elif enrollment.paid:
				if ELG:
					print '{} has successfully enrolled in {}'.format(student, self)
				return "enrolled" # The student is registered for this class and has paid
			else:
				if ELG:
					print '{} is registered for {} but needs to pay'.format(student, self)
				return "need_pay" # This class has been added to the cart, pending tuition payment
		overlapQ = Q(
			Q(course__tradition__start__gte=self.start, course__tradition__end__lte=self.end) |
			Q(course__tradition__start__lte=self.end, course__tradition__end__gte=self.start) |
			Q(course__tradition__start__gte=self.start, course__tradition__start__lte=self.end) 
		)
		conflicts = Enrollments.filter(
			overlapQ,
			student=student,
			course__year=self.year,
			course__tradition__day=self.day,
		)
		if conflicts:
			if ELG:
				print '{} is in another class at the same time as {}'.format(student, self)
			return "conflict" # The student is registered for another class at the same time as this one
		elif self.eligible(student):
			return "eligible" # The student may register for this class, but has not yet
		elif self.audible(student):
			return "need_aud" # An audition is required for this class for which student is eligible
		elif self.tradition.eligible(student, self.year, False):
			return "need_cur" # Student will be eligible once they enroll in at least 1 other class
		else:
			return "not_elig" # The student does not meet the requirements to enroll in or audition for this class
	def enroll(self, student):
		if self.eligible(student):
			return Enrollments.create(course=self, student=student)
	def sudo_enroll(self, student):
		return Enrollments.create(course=self, student=student)
	def audition(self, student):
		if self.audible(student):
			return Enrollments.create(course=self, student=student, isAudition=True)
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