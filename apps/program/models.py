from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from django_mysql import models as sqlmod

# from apps.main import models as main

# - - - - - M A N A G E R S - - - - - 

# - - - - - M O D E L S - - - - - 

class Venue(models.Model):
	name    = models.CharField(max_length=30)
	# address = models.ForeignKey(main.Address)

class CourseTrad(models.Model):
	# General:
	code       = models.CharField(max_length=2, primary_key=True)
	title      = models.CharField(max_length=50)
	alias      = models.ForeignKey('self', null=True)
	enroll     = models.BooleanField(default=True)
	# Commitment:
	# day        = custom.DayOfWeekField()
	start      = models.TimeField()
	end        = models.TimeField()
	nMeets     = models.PositiveIntegerField(default=20)
	place      = models.ForeignKey(Venue, null=True)
	show       = models.CharField(max_length=2)
	vs         = models.BooleanField(default=False)
	# Prerequisites
	min_age    = models.PositiveIntegerField(default=9)
	max_age    = models.PositiveIntegerField(default=18)
	# preq       = sqlmod.EnumField(choices=['Age','Boy','Girl','Curr','IorT','Mast','Act','AudM','AudH'], default='Age')
	# Cost
	tuition    = models.DecimalField(max_digits=6, decimal_places=2)
	redtuit    = models.DecimalField(max_digits=6, decimal_places=2)
	vol_hours  = models.FloatField()
	the_hours  = models.FloatField()
	prepaid    = models.BooleanField()

class Course(models.Model):
	year       = models.DecimalField(max_digits=4, decimal_places=0)
	tradition  = models.ForeignKey(CourseTrad)
	last       = models.DateField()
	# teacher    = models.ForeignKey(main.Teacher)
	tuition    = models.DecimalField(max_digits=6, decimal_places=2)
	vol_hours  = models.FloatField()
	the_hours  = models.FloatField()
	prepaid    = models.BooleanField()
