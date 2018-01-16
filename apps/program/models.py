from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from django_mysql import models as sqlmod

# - - - - - M A N A G E R S - - - - - 

# - - - - - M O D E L S - - - - - 

class Venue(models.Model):
	code = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=30)
	address = models.ForeignKey('main.Address', null=True)

class CourseTrad(models.Model):
	# General:
	id         = models.CharField(max_length=2, primary_key=True)
	title      = models.CharField(max_length=50)
	alias      = models.ForeignKey('self', null=True)
	enroll     = models.BooleanField(default=True)
	# Commitment:
	day        = custom.DayOfWeekField()
	start      = models.TimeField()
	end        = models.TimeField()
	nMeets     = models.PositiveIntegerField(default=20)
	place      = models.ForeignKey(Venue, null=True)
	show       = models.CharField(max_length=2)
	vs         = models.BooleanField(default=False)
	# Prerequisites
	min_age = models.PositiveIntegerField(default=9)
	max_age = models.PositiveIntegerField(default=18)
	M = models.BooleanField(default=True)  # Boys may enroll
	F = models.BooleanField(default=True)  # Girls may enroll
	C = models.BooleanField(default=False) # Only current students may enroll
	I = models.BooleanField(default=False) # 1 year IS or T* or P* required
	A = custom.TinyIntegerField(default=0) # Audition Required
	# Cost
	tuition    = models.DecimalField(max_digits=6, decimal_places=2)
	redtuit    = models.DecimalField(max_digits=6, decimal_places=2)
	vol_hours  = models.FloatField()
	the_hours  = models.FloatField()
	prepaid    = models.BooleanField()

class Course(models.Model):
	code       = models.CharField(max_length=4, primary_key=True)
	year       = models.DecimalField(max_digits=4, decimal_places=0)
	tradition  = models.ForeignKey(CourseTrad)
	last       = models.DateField()
	teacher    = models.ForeignKey('main.Teacher', null=True)
	tuition    = models.DecimalField(max_digits=6, decimal_places=2)
	vol_hours  = models.FloatField()
	the_hours  = models.FloatField()
	prepaid    = models.BooleanField()
