from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from django_mysql import models as sqlmod

class CourseTradManager(sm.SuperManager):
	def __init__(self):
		super(CourseTradManager, self).__init__('program_coursetrad')
	def get(self, **kwargs):
		thing = super(CourseTradManager, self).get(**kwargs)
		return thing.alias if thing.alias else thing
CourseTrads = CourseTradManager()

class CourseManager(sm.SuperManager):
	def __init__(self):
		super(CourseManager, self).__init__('program_course')
	def create(self, **data):
		# Inherit these fields from Tradition, unless overridden.
		for field in ['tuition','vol_hours','the_hours','prepaid']:
			if field not in data:
				data[field] = data['tradition'].__getattribute__(field)
		data['id'] = str(int(data['year'])%100).zfill(2)+data['tradition'].id
		super(CourseManager, self).create(data)
	def fetch(self, **kwargs):
		things = self.filter(**kwargs)
		if things:
			alias_id = things[0].alias_id
			if alias_id:
				return self.fetch(id=alias_id)
	# TODO: Figure out inheritance
Courses = CourseManager()

class EnrollmentManager(sm.SuperManager):
	def __init__(self):
		super(EnrollmentManager, self).__init__('program_enrollment')
Enrollments = EnrollmentManager()

class AuditionManager(sm.SuperManager):
	def __init__(self):
		super(AuditionManager, self).__init__('program_audition')
Auditions = AuditionManager()