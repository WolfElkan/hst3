from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.data import sub, Each, find_all
from Utils.security import getyear
from django_mysql import models as sqlmod
from .managers import CourseTrads, Courses, Enrollments
Q = models.Q
from apps.people.managers import Students, Families
from trace import TRACE, DEV
from datetime import datetime
import re

class Venue(models.Model):
	id   = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=30)
	address = models.ForeignKey('people.Address', null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
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
	sa         = models.BooleanField(default=False)
	semester_choices = [
		('N','Neither'),
		('F','Fall'),
		('S','Spring'),
		('B','Both'),
	]
	semester   = models.CharField(max_length=1,default='N')
	# Prerequisites
	min_age = models.PositiveIntegerField(default=9)
	max_age = models.PositiveIntegerField(default=18)
	min_grd = models.PositiveIntegerField(default=1)
	max_grd = models.PositiveIntegerField(default=12)
	eligex  = models.TextField(default="#")
	# Cost
	tuition    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	redtuit    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	vol_hours  = models.FloatField(default=0)
	the_hours  = models.FloatField(default=0)
	auto       = models.BooleanField(default=False) # Whether course is automatically added to eligible carts
	trig       = models.BooleanField(default=False) # Whether course triggers an addition of all eligible auto courses
	droppable  = models.BooleanField(default=True) # Whether course may be dropped AFTER a successful audition
	rest_model = "coursetrad"
	genre_codes = {
		'A':'Acting',
		'B':'Ballet', # Historical
		'C':'Choir',
		'D':'Dance Intensive', # Historical
		# 'E':'',
		'F':'Finale',
		'G':'General Audition',
		'H':'Jazz/Hip-Hop',
		'I':'Irish',
		'J':'Jazz',
		'K':'Prepaid Tickets', # Admin
		'L':'Sign Language', # Historical
		# 'M':'', # Merchandise? Makeup kits? Meeting?
		# 'N':'',
		'O':'Overture', # Historical
		'P':'Tap', # Broadway (Older Beginners)
		# 'Q':'',
		# 'R':'',
		'S':'Troupe',
		'T':'Tap',
		# 'U':'',
		# 'V':'',
		'W':'Workshop',
		'X':'Tech',
		# 'Y':'',
		'Z':'Jazz', # Broadway (Older Beginners)
	}
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = CourseTrads
	def __str__(self):
		return self.title.upper()
	def display_semester(self):
		sem = self.semester
		return ' ({})'.format(sem) if sem in 'FS' else ''
	def courses(self):
		return Courses.filter(tradition_id=self.id)
	def make(self, year):
		course = Courses.fetch(tradition=self, year=year)
		if course:
			return course
		else:
			return Courses.create(tradition=self, year=year)
	def genre(self):
		code = self.id[0]
		if code in self.genre_codes:
			return self.genre_codes[code]
	def check_eligex(self, student, year, **kwargs):
		if re.match(r'<[^>]*<|{[^}]*{',self.eligex):
			raise Exception('Nested clauses of the same type are not currently supported.  \nCall Wolf if you need this changed: (267) 380-0597')
		kwargs.setdefault('eligex',self.eligex)
		kwargs.setdefault('conj',True)
		kwargs.setdefault('aud', False)
		kwargs.setdefault('cur', False)
		kwargs.setdefault('debug',False)
		eligex  = kwargs.pop('eligex')
		conj    = kwargs.pop('conj')
		matches = re.findall(r'(!?){([^}]*)}|(!?)<([^>]*)>|(!?)([^<>{} ]*)', eligex)
		for x in matches:
			if x[1]:
				# AND
				kwargs['eligex'] = x[1]
				result = self.check_eligex(student, year, **kwargs)
				result = not result if x[0] else result
				if kwargs['debug']:
					print '{',x[1],'}', result
					print
			elif x[3]:
				# OR
				kwargs['eligex'] = x[3]
				kwargs['conj'] = False
				result = self.check_eligex(student, year, **kwargs)
				result = not result if x[2] else result
				if kwargs['debug']:
					print '<{}>'.format(x[3]), result
					print
			elif x[5]:
				# WORD
				result = self.check_word(student, year, x[5], **kwargs)
				result = not result if x[4] else result
				if kwargs['debug']:
					print x[5], result
					print
			else:
				result = conj
			if result != conj:
				return result
		return conj
	def check_word(self, student, year, word, **kwargs):
		if '#' in word:
			return True
		elif '~' in word:
			return False
		elif 'm' in word:
			return student.sex == 'M'
		elif 'f' in word:
			return student.sex == 'F'
		elif word == '%':
			return DEV
		elif 'a' in word:
			return student.hst_age_in(year) >= self.min_age - word.count('y') and student.hst_age_in(year) <= self.max_age + word.count('o')
		elif 'g' in word:
			if not student.grad_year:
				return True
			return student.grade_in(year)   >= self.min_grd - word.count('y') and student.grade_in(year)   <= self.max_grd + word.count('o')
		else:
			query = {
				'student':student,
				'status__in':["enrolled","invoiced","need_pay","aud_pass"],
			}
			if word == '@':
				if kwargs['aud']:
					return True
				query.update({
					'status':"aud_pass",
					'course__tradition': self,
					'course__year': year,
				})
				if kwargs['debug']:
					print query
				return bool(Enrollments.filter(**query))
			if word == 'c':
				if kwargs['cur']:
					return True
				query['course__year'] = year
				if kwargs['debug']:
					print query
				return bool(Enrollments.filter(**query).exclude(course__tradition__id__startswith='K'))
			if '*' not in word:
				query['course__tradition__id'] = word[0:2]
			elif word[0] != '*':
				query['course__tradition__id__startswith'] = word[0]
			elif word[1] != '*':
				query['course__tradition__id__endswith'] = word[1]
			if 'c' in word and not kwargs['cur']:
				query['course__year'] = year
			if 'p' in word:
				query['course__year__lt'] = year
			if '$' in word:
				query.pop('status__in')
				query['status'] = "enrolled"
			if '+' in word:
				query.pop('student')
				query['student__family'] = student.family
			if kwargs['debug']:
				print datetime.now()
				print query
			return bool(Enrollments.filter(**query).exclude(course__tradition__id__startswith='K'))
	def eligible(self, student, year):
		course = Courses.fetch(tradition=self, year=year)
		if course:
			return course.eligible(student)
		else:
			return self.check_eligex(student, year)
	def enroll(self, student, year):
		course = Courses.fetch(tradition=self, year=year)
		if course and course.eligible(student):
			return course.enroll(student)
	def audition(self, student, year):
		course = Courses.fetch(tradition=self, year=year)
		if course and course.audible(student):
			return course.audition(student)
		else:
			return self.check_eligex(student, year, aud=True)
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
	title      = models.CharField(max_length=50)
	last_date  = models.DateField(null=True)
	aud_date   = models.DateField(null=True)
	teacher    = models.ForeignKey('people.Teacher', null=True)
	tuition    = models.DecimalField(max_digits=6, decimal_places=2)
	vol_hours  = models.FloatField()
	the_hours  = models.FloatField()
	approved   = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "course"
	objects = Courses
	def enrollments(self):
		return Enrollments.filter(course_id=self.id)
	def students(self):
		return Students.filter(enrollment__course=self).order_by('family__last','birthday')
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
	def boys(self):
		return self.students.filter(sex='M')
	def girls(self):
		return self.students.filter(sex='F')
	def __str__(self):
		return self.title+' ('+str(self.year)+')'
	def eligible(self, student):
		return self.check_eligex(student)
	def audible(self, student):
		return self.check_eligex(student, aud=True)
	def check_eligex(self, student, **kwargs):
		# If this course's audition date has already passed, don't check for audition eligibility
		if self.aud_date and datetime.now().date() > self.aud_date:
			kwargs['aud'] = False
		return self.tradition.check_eligex(student, self.year, **kwargs)
	def enroll(self, student, **kwargs):
		enrollment = Enrollments.fetch(course=self,student=student)
		if enrollment:
			enrollment.status = sub(enrollment.status, {
				'aud_drop':'aud_pass',
			})
			enrollment.save()
		else:
			passed_audition = kwargs.setdefault('passed_audition',False)
			if passed_audition or self.eligible(student):
				enrollment = Enrollments.create(course=self, student=student)
				enrollment.save()
				if self.tradition.trig:
					student.fate()
		return enrollment
	def accept(self, student):
		return self.enroll(student, passed_audition=True)
	def audition(self, student):
		if self.audible(student):
			return Enrollments.create(course=self, student=student, status="aud_pend")
	def cart(self, student):
		enrollment = self.enroll(student)
		if not enrollment:
			enrollment = Enrollments.create(course=self, student=student, status="aud_pend")
		student.fate()
		return enrollment
	def conflicts_with(self, other):
		if self.id == other.id:
			return False
		elif self.year != other.year:
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
	def prepaid(self):
		return self.trig
	def __getattribute__(self, field):
		if field in ['students_toggle_enrollments','students','enrollments','prepaid']:
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
	role       = models.TextField(null=True)
	role_type  = sqlmod.EnumField(choices=['','Chorus','Support','Lead'])
	status_choices = [
 		("eligible","{student} is eligible for {course}"),                                                                    # Stable
		("not_elig","{student} is not eligible for {course}"),                                                                # Unstable
		("aud_need","{student} is eligible for {article} {audskil} for {course}."),                                           # Unstable
		("aud_pend","{student} has scheduled {article} {audskil} for {course} ({year})"),                                     # Stable
		("pendpass","{student} has completed the {audskil} and is recommended for {course} {year}, pending executive approval."),  # Stable
		("pendfail","{student} has completed the {audskil} but is not recommended for {course} {year}, pending executive approval."),  # Stable
		("pend_pub","{student} has completed {article} {audskil} for {course} and is awaiting the results."),                 
		("fail_pub",""),
		("aud_pass","{student} has passed the {audskil} for {course}!"),                                                      # Stable
		("aud_fail","{student} did not pass the {audskil} for {course}."),                                                    # Invisible
		("aud_drop","{student} passed the {audskil} for {course} and then dropped it, but {pronoun} may still re-enroll."),   # Stable
		("aud_lock","{student} has passed the {audskil} for {course} and must enroll."),                                      # Stable
		("enrolled","{student} {proverb} enrolled in {course} ({year})"),                               # invoice__status='P' # Stable
		("invoiced","{student}'s enrollment in {course} has been added to invoice #{invoice}"),         # invoice__status='N' # Stable
		("need_pay","{student} is registered for {course} pending tuition payment"),                                          # Stable
		("conflict","{student} is in another class at the same time as {course}"),                                            # Unstable
		("need_cur","{student} will be eligible for {course} once {pronoun} enrolls in at least 1 other class"),              # Unstable
		("needboth","{student} will be eligible to audition for {course} once {pronoun} enrolls in at least 1 other class"),  # Unstable
		("nonexist","{student} was enrolled in {course} ({year}) on cancelled invoice #{invoice}"),     # invoice__status='C' # Invisible
	]
	status     = models.CharField(max_length=8,choices=status_choices,default='need_pay')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "enrollment"
	objects = Enrollments
	def __init__(self, *args, **kwargs):
		if hasattr(self, '_state'):
			self.set_status()
		return super(Enrollment, self).__init__(*args, **kwargs)
	def title(self):
		display = self.get_status_display()
		if self.is_prepaid_tickets():
			display = '{family} {proverb} recieving {course} {year}'
		return display.format(
			student = self.student,
			family  = self.student.family,
			course  = self.course.title,
			year    = self.course.year,
			invoice = self.invoice.id if self.invoice else 0,
			pronoun = 'he' if self.student.sex == 'M' else 'she',
			proverb = 'was' if self.course.year < getyear() else 'is',
			audskil = 'audition' if self.course.id[2] in 'SC' else 'skill assessment',
			article = 'an' if self.course.id[2] in 'SC' else 'a',
		)
	def public_status(self):
		return sub(self.status, {"pendpass":"aud_pend","pendfail":"aud_pend","aud_fail":"fail_pub"})
	def public_title(self):
		real_status = self.status
		self.status = self.public_status
		title = self.title
		self.status = real_status
		return title
	def calc_status(self):
		if self.status in ["aud_pass","aud_fail","aud_drop","nonexist"]:
			return self.status
		if not self.course.check_eligex(self.student, aud=True, cur=True):
			return "not_elig"
		elif any(Each(self.student.courses_in(self.course.year)).conflicts_with(self.course)):
			return "conflict"
		elif self.course.check_eligex(self.student):
			return self.status if self.id else "eligible"
		elif self.course.check_eligex(self.student, aud=True):
			return self.status if self.id else "aud_need"
		elif self.course.check_eligex(self.student, cur=True):
			return "need_cur"
		# elif self.course.check_eligex(self.student, aud=True, cur=True):
		else:
			return "needboth"
	def set_status(self):
		if not self.id:
			self.status = self.calc_status()
		return self
	def inspect(self):
		print
		print 'id         :',self.id
		print 'student    :',self.student
		print 'course     :',self.course
		print 'invoice    :',self.invoice
		print 'role       :',self.role
		print 'role_type  :',self.role_type
		print 'status     :',self.status
		print 'created_at :',self.created_at
		print 'updated_at :',self.updated_at
	def is_prepaid_tickets(self):
		return self.course.tradition.id[0] == 'K'
	def display_student(self):
		return '' if self.is_prepaid_tickets() else self.student.prefer
	def paid(self):
		return self.invoice.status == 'P' if self.invoice else False
	def accept(self, user):
		if self.status in ["aud_pend","pendpass","pendfail"]:
			if user.permission >= 5:
				self.course.accept(self.student)
				self.status = "aud_pass" if self.course.tradition.droppable else "aud_lock"
			elif user.permission >= 4:
				self.status = "pendpass"
			self.save()
			self.student.fate()
	def reject(self, user):
		if self.status in ["aud_pend","pendpass","pendfail"]:
			if user.permission >= 5:
				self.status = "aud_fail"
			elif user.permission >= 4:
				self.status = "pendfail"
			self.save()
			self.student.fate()
	def fate(self):
		self.status = self.calc_status()
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
	def cancel(self):
		if self.status == "invoiced":
			self.status = "nonexist"
			self.save()
	def tuition(self):
		return self.course.tuition
	def __getattribute__(self, field):
		if field in ['paid','eligible','display_student','tuition','title','public_title','public_status']:
			call = super(Enrollment, self).__getattribute__(field)
			return call()
		elif field in Students.fields:
			return self.student.__getattribute__(field)
		elif field in Courses.fields:
			return self.course.__getattribute__(field)
		else:
			return super(Enrollment, self).__getattribute__(field)