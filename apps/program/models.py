from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from django_mysql import models as sqlmod
from .managers import CourseTrads, Courses, Enrollments, Auditions

class Venue(models.Model):
	id   = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=30)
	address = models.ForeignKey('main.Address', null=True)

class CourseTrad(models.Model):
	# General:
	id         = models.CharField(max_length=2, primary_key=True)
	title      = models.CharField(max_length=50)
	alias      = models.ForeignKey('self', null=True)
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
	A = custom.TinyIntegerField(default=0) # Audition Required
	# Cost
	tuition    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	redtuit    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	vol_hours  = models.FloatField(default=0)
	the_hours  = models.FloatField(default=0)
	prepaid    = models.BooleanField(default=False)
	objects = CourseTrads
	def _courses(self):
		return {'mapping':{'trad_id':self.id},'model':'course'}
	def __str__(self):
		return self.title.upper()
	def make(self, year):
		return Courses.create(tradition=self, year=year)
	def genre(self):
		code = self.id[0]
		genre_codes = {
			'A':'Acting',
			'C':'Choir',
			'F':'Finale Group',
			'G':'General Audition',
			'H':'Hip-Hop',
			'I':'Irish',
			'J':'Jazz',
			'P':'Tap',
			'S':'Troupe',
			'T':'Tap',
			'W':'Workshop',
			'X':'Tech',
			'Z':'Jazz',
		}
		if code in genre_codes:
			return genre_codes[code]
	def eligible(self, student, year):
		return True
	def audible(self, student, year):
		return True
	def take(self, student, year):
		course = Courses.fetch(tradition=self, year=year)
		if course:
			return course.take(student)
	def saud(self, student, year):
		course = Courses.fetch(tradition=self, year=year)
		if course:
			return course.saud(student)

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
	objects = Courses
	def _students(self):
		return {'mapping':{'course_id':self.id},'model':'student'}
	def __str__(self):
		return self.tradition.title+' ('+str(self.year)+')'
	def eligible(self, student):
		return self.tradition.eligible(student, self.year)
	def audible(self, student):
		return self.tradition.audible(student, self.year)
	def take(self, student):
		if self.eligible(student):
			Enrollments.create({'course': self, 'student': student})
	def saud(self, student):
		if self.audible(student):
			Auditions.create({'course': self, 'student': student})

class Enrollment(models.Model):
	student    = models.ForeignKey('main.Student')
	course     = models.ForeignKey(Course)
	role       = models.TextField(null=True)
	role_type  = sqlmod.EnumField(choices=['','Chorus','Support','Lead'])
	created_at = models.DateTimeField(auto_now_add=True)
	objects = Enrollments
	def __str__(self):
		return str(self.student) + (' as '+self.role if self.role else '') + ' in ' + str(self.course)

class Audition(models.Model):
	student    = models.ForeignKey('main.Student')
	course     = models.ForeignKey(Course)
	auto       = models.BooleanField(default=False)
	date       = models.DateField(null=True)
	happened   = models.BooleanField(default=False)
	success    = models.NullBooleanField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)		
	objects = Auditions
