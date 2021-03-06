from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.security import getyear
from django_mysql import models as sqlmod

class CourseTradManager(sm.SuperManager):
	def __init__(self):
		super(CourseTradManager, self).__init__('program_coursetrad')
		self.fields = ['year','tradition','last_date','aud_date','teacher','early_tuit','after_tuit','vol_hours','the_hours']
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
		for field in ['vol_hours','the_hours','early_tuit','after_tuit','title','abbr','nSlots']:
			if field not in data:
				data[field] = data['tradition'].__getattribute__(field)
		data['id'] = str(int(data['year'])%100).zfill(2)+data['tradition'].id
		already = self.fetch(id=data.get('id'))
		if already:
			return already
		else:
			return super(CourseManager, self).create(**data)
	def fetch(self, **kwargs):
		# print 0, kwargs
		qset = self.filter(**kwargs)
		if qset and not qset[0].tradition.alias:
			# print 1
			return qset[0]
		elif 'id' in kwargs:
			# print 2
			split = self.split_id(kwargs.pop('id'))
			if split:
				kwargs.update(split)
				return self.fetch(**kwargs)
		# elif 'tradition' in kwargs:
		# 	# print 3
		# 	year = kwargs.setdefault('year',getyear())
		# 	tradition = kwargs['tradition']
		# 	if tradition.r:
		# 		pass
		# 	else:
		# 		return self.simulate(tradition, year)
	def create_by_id(self, course_id, **kwargs):
		course = self.fetch(id=course_id)
		if course:
			return course
		if 'tradition' in kwargs and 'year' in kwargs:
			split = kwargs.copy()
			if type(split['tradition'] is str):
				split['tradition'] = CourseTrads.fetch(id=split['tradition'])
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
		# print kwargs
		already = kwargs.copy()
		if 'course' in kwargs:
			course = kwargs['course']
			kwargs.setdefault('status',course.tradition.default)
			if course.tradition.byFamily():
				student = already.pop('student')
				already['student__family'] = student.family
		already = self.fetch(**already)
		if already:
			return already
		else:
			return super(EnrollmentManager, self).create(**kwargs)
Enrollments = EnrollmentManager()

class VenueManager(sm.SuperManager):
	def __init__(self):
		super(VenueManager, self).__init__('program_venue')
Venues = VenueManager()