from apps.people.managers import Students
# from apps.program.managers import Enrollments
from Utils.data import find_all
from eligex import check_eligex
from datetime import date

class StudentList(object):
	def __init__(self, tradition, year, **kwargs):
		self.tradition = tradition
		self.year = year
		self.id = str(int(self.year)%100).zfill(2)+self.tradition.id
		self.rest_model = 'course'
		self.aud_date = None
		self.all_students = kwargs.setdefault('all_students',Students.all())
		# Inherit these fields from Tradition, unless overridden.
		for field in ['vol_hours','the_hours','early_tuit','after_tuit','title','abbr','nSlots']:
			if field in kwargs:
				self.__setattr__(field, kwargs[field])
			else:
				self.__setattr__(field, self.tradition.__getattribute__(field))
		self.students = find_all(self.all_students, lambda student: check_eligex(course=self.tradition, student=student, year=self.year))
		# self.students = Students.all()
	def __str__(self):
		return '{} [{}]'.format(self.title,self.year)