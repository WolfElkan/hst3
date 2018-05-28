from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from django_mysql import models as sqlmod

class CourseTradManager(sm.SuperManager):
	def __init__(self):
		super(CourseTradManager, self).__init__('program_coursetrad')
		self.fields = ['year','tradition','last_date','aud_date','teacher','tuition','vol_hours','the_hours','trig','auto']
	def get(self, **kwargs):
		thing = super(CourseTradManager, self).get(**kwargs)
		return thing.alias if thing.alias else thing
	def fetch(self, **kwargs):
		qset = self.filter(**kwargs)
		if qset:
			q = qset[0]
			return q.alias if q.alias else q
CourseTrads = CourseTradManager()

class CourseManager(sm.SuperManager):
	def __init__(self):
		super(CourseManager, self).__init__('program_course')
	def create(self, **data):
		# Inherit these fields from Tradition, unless overridden.
		for field in ['tuition','vol_hours','the_hours','title']:
			if field not in data:
				data[field] = data['tradition'].__getattribute__(field)
		data['id'] = str(int(data['year'])%100).zfill(2)+data['tradition'].id
		return super(CourseManager, self).create(**data)
	def fetch(self, **kwargs):
		qset = self.filter(**kwargs)
		if qset and not qset[0].tradition.alias:
			return qset[0]
		elif 'id' in kwargs:
			split = self.split_id(kwargs.pop('id'))
			if split:
				kwargs.update(split)
				return self.fetch(**kwargs)
	def create_by_id(self, course_id):
		course = self.fetch(id=course_id)
		if course:
			return course
		else:
			split = self.split_id(course_id)
			if split:
				return split['tradition'].make(split['year'])
	def split_id(self, course_id):
		course_id = str(course_id)
		year = course_id[:2]
		if year.isdigit():
			year = int(year)
			year += 2000 if year < 95 else 1900
			trad_id = course_id[2:]
			tradition = CourseTrads.fetch(id=trad_id)
			# print year, tradition
			if tradition:
				return {
					'year':year,
					'tradition':tradition
				}
Courses = CourseManager()

class EnrollmentManager(sm.SuperManager):
	def __init__(self):
		super(EnrollmentManager, self).__init__('program_enrollment')
	def create(self, **kwargs):
		already = kwargs.copy()
		if 'course' in kwargs and '+' in kwargs['course'].eligex:
			student = already.pop('student')
			already['student__family'] = student.family
		already = self.fetch(**already)
		if already:
			return already
		else:
			return super(EnrollmentManager, self).create(**kwargs)
	def filter(self, **kwargs):
		phantom = 'phantom' in kwargs and kwargs.pop('phantom')
		qset = super(EnrollmentManager, self).filter(**kwargs)
		if not phantom:
			qset = qset.exclude(status='nonexist')
		return qset
	def simulate(self, **kwargs):
		thing = self.fetch(**kwargs)
		thing = thing if thing else self.model(**kwargs)
		return thing.set_status()
Enrollments = EnrollmentManager()

from .models import Venue
Venues = Venue.objects