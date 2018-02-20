from __future__ import unicode_literals
from django.db import models
from Utils import custom_fields as custom
from Utils import supermodel as sm
from Utils.data import sub, Each, find_all
from django_mysql import models as sqlmod
from .managers import CourseTrads, Courses, Enrollments
Q = models.Q
from apps.people.managers import Students
from trace import TRACE, DEV
from datetime import datetime
import re

class Venue(models.Model):
	id   = models.CharField(max_length=3, primary_key=True)
	name = models.CharField(max_length=30)
	address = models.ForeignKey('people.Address', null=True)
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
	eligex  = models.TextField(default="a")
	# Cost
	tuition    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	redtuit    = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	vol_hours  = models.FloatField(default=0)
	the_hours  = models.FloatField(default=0)
	prepaid    = models.BooleanField(default=False)
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
		# 'M':'', # Merchandise? Makeup kits?
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
				'isAudition':False,
			}
			if word == '@':
				if kwargs['aud']:
					return True
				query.update({
					'isAudition': True,
					'success': True,
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
			if '@' in word:
				query['isAudition'] = True
				if '?' not in word:
					query['success'] = True
			if '$' in word:
				query['paid'] = True
			if kwargs['debug']:
				print query
			return bool(Enrollments.filter(**query).exclude(course__tradition__id__startswith='K'))
	def eligible(self, student, year):
		course = Courses.fetch(tradition=self, year=year)
		if course:
			return course.eligible(student)
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
	teacher    = models.ForeignKey('people.Teacher', null=True)
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
			'invoice_id':0,
		}
		enrollment = Enrollments.fetch(course=self, student=student)
		if enrollment:
			if enrollment.isAudition and not enrollment.happened:
				elig['reason'] = '{} has scheduled an audition for {}'.format(student, self)
				elig['aud'] = True
				elig['css'] = "audition"
			elif enrollment.isAudition and not enrollment.success:
				elig['reason'] = ''
				elig['css'] = "not_elig"
			elif enrollment.paid:
				elig['reason'] = '{} has successfully enrolled in {}'.format(student, self)
				elig['now'] = True
				elig['css'] = "enrolled"
			elif enrollment.invoice:
				elig['reason'] = "{}'s enrollment in {} has been added to invoice #{}".format(student, self, enrollment.invoice.id)
				elig['now'] = True
				elig['css'] = "invoiced"
				elig['invoice_id'] = enrollment.invoice.id
			else:
				elig['reason'] = '{} is registered for {} pending tuition payment'
				elig['now'] = True
				elig['css'] = "need_pay"
		# Fast fail: Student is not eligible under any circumstances
		elif not self.tradition.check_eligex(student, self.year, aud=True, cur=True):
			elig['reason'] = '{} is not eligible for {}' 
			elig['css'] = "not_elig"
		# Check for conflicts
		elif any(Each(student.courses_in(self.year)).conflicts_with(self)):
			elig['reason'] = '{} is in another class at the same time as {}'
			elig['css'] = "conflict"
		# Check if eligible now
		elif self.tradition.check_eligex(student, self.year):
			elig['reason'] = '{} is eligible for {}'
			elig['css'] = "eligible"
			elig['now'] = True
		# Check if eligible with audition
		elif self.tradition.check_eligex(student, self.year, aud=True):
			elig['reason'] = '{} is eligible to audition for {}'
			elig['css'] = "need_aud"
			elig['aud'] = True
		# Check if eligible with current enrollment
		elif self.tradition.check_eligex(student, self.year, cur=True):
			elig['reason'] = '{} will be eligible for {} once {} enrolls in at least 1 other class'
			elig['css'] = "need_cur"
		# Check if eligible with audition AND current enrollment
		elif self.tradition.check_eligex(student, self.year, aud=True, cur=True):
			elig['reason'] = '{} will be eligible to audition for {} once {} enrolls in at least 1 other class'
			elig['css'] = "need_cur" 
		# Format reason with student's name and course
		elig['reason'] = elig['reason'].format(student, self.title, 'he' if student.sex == 'M' else 'she')
		return elig
	def check_eligex(self, student, **kwargs):
		# If this course's audition date has already passed, don't check for audition eligibility
		if self.aud_date and datetime.now().date() > self.aud_date:
			kwargs['aud'] = False
		return self.tradition.check_eligex(student, self.year, **kwargs)
	def enroll(self, student):
		# Check if student is eligible now, do nothing and return None otherwise. (Shouldn't happen)
		if self.eligible(student)['now']:
			# Check if course requires purchase of prepaid tickets 
			if self.prepaid:
				# If so, find the tradition corresponding to this course's show's prepaid tickets
				Ktrad = CourseTrads.fetch(id__startswith='K',id__endswith=self.show[1])
				# Stringly calculate the id for this course's prepaid tix this year
				Kid = self.id[0:2]+Ktrad.id
				# Create (or find if it already exists) this ticket course
				K = Courses.create_by_id(Kid)
				# Check for enrollments by this family in this ticket course
				prepaid = Enrollments.fetch(student__family=student.family, course=K)
				# If you find none...
				if not prepaid:
					# ...make one
					Enrollments.create(student=student, course=K)
			# But either way, create and return the enrollment
			return Enrollments.create(course=self, student=student)
	def sudo_enroll(self, student):
		# Admin method for creating an enrollment without checking eligibility or prepaid tickets
		return Enrollments.create(course=self, student=student)
	def audition(self, student):
		if self.audible(student):
			return Enrollments.create(course=self, student=student, isAudition=True)
	def conflicts_with(self, other):
		if self.year != other.year:
			return False
		elif self.day != other.day:
			return False
		elif self.end <= other.start:
			return False
		elif self.start >= other.end:
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
	student    = models.ForeignKey('people.Student')
	course     = models.ForeignKey(Course)
	invoice    = models.ForeignKey('payment.Invoice', null=True)
	role       = models.TextField(null=True)
	role_type  = sqlmod.EnumField(choices=['','Chorus','Support','Lead'])
	isAudition = models.BooleanField(default=False)
	ret_status = models.BooleanField(default=True)
	happened   = models.BooleanField(default=False)
	exists     = models.BooleanField(default=True)
	success    = models.NullBooleanField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	rest_model = "enrollment"
	objects = Enrollments
	def __str__(self):
		if self.course.tradition.id[0] == 'K':
			return '{} recieves {}, {}'.format(self.student.family,self.course.title,self.course.year)
		else:
			return '{}{}{} {} {} in {}'.format(
				self.student,
				' as ' if self.role else '',
				self.role if self.role else '',
				'will audition for' if self.isAudition else 'in',
				self.course.title,
				self.course.year
			)
	# Delete the enrollment and all that goes with it
	def delete(self):
		# Begin collecting the invoices which will need to be updated
		invoices = set()
		# Find the invoice to which enrollment has been added, (if it has been added to an invoice)
		if self.invoice:
			invoices.add(self.invoice)
		# Now delete the enrollment itself, and save the deletion info to return it
		if self.invoice and self.invoice.status == 'P':
			self.exists = False
			self.save()
			deletion_info = [0L, {u'program.Enrollment':0L}]
		else:
			deletion_info = list(super(Enrollment, self).delete())
		# If course comes with prepaid tickets...
		if self.course.prepaid:
			# ...make sure some student in family is enrolled in another course that needs them
			other = Enrollments.filter(
				student__family=self.student.family, 
				course__tradition__prepaid=True, 
				course__tradition__show=self.course.show,
				course__year=self.course.year
			).exclude(course__tradition__id__startswith='K')
			# If you don't find any, then you're going to need to delete the prepaid tickets from the cart
			if not other:
				# Find the CourseTrad for the prepaid tickets for this show
				Ktrad = CourseTrads.fetch(id__startswith='K',id__endswith=self.course.show[1])
				# Find the course that corresponds to this year
				K = Courses.fetch(year=self.course.year, tradition=Ktrad)
				# Check if there are already
				prepaid = Enrollments.fetch(student__family=self.student.family, course=K)
				# If there are...
				if prepaid:
					# If they're already on an invoice...
					if prepaid.invoice:
						# ...add that invoice to the ones to be updated
						invoices.add(prepaid.invoice)
					# ...delete the prepaid tickets
					prepaid.delete()
		# Recursively cascade to delete any other enrollments for which the student is ineligible
		all_enrls = self.student.enrollments_in(self.course.year)
		bad_enrls = find_all(all_enrls, lambda enr: not enr.eligible)
		for x in bad_enrls:
			print x
			x.delete()
		deletions = Each(bad_enrls).delete()
		for x in deletions:
			deletion_info[0] += x[0]
			for key in x[1]:
				if key in deletion_info:
					deletion_info[1][key] += x[1][key]
		# Update any invoices that need to be updated (This won't apply to invoices that have already been paid)
		Each(invoices).update_amount()
		# And finally, return the deletion info
		return tuple(deletion_info)
	# Don't bother with all that other stuff.  Just delete the enrollment already!
	def sudo_delete(self):
		return super(Enrollment, self).delete()
	# Courtesy method
	def eligible(self, **kwargs):
		course  = kwargs.setdefault('course',  self.course)
		student = kwargs.setdefault('student', self.student)
		return course.check_eligex(student, aud=self.isAudition)
	# Update attributes after a successful audition
	def accept(self):
		if self.isAudition:
			self.happened = True
			self.success = True
			self.isAudition = False
			self.save()
	# Update attributes after an unsuccessful audition
	def reject(self):
		if self.isAudition:
			self.happened = True
			self.success = False
			self.save()
	def paid(self):
		return self.invoice.status == 'P' if self.invoice else False
	def display_student(self):
		return self.student.prefer if self.course.tradition.id[0] != 'K' else ''
	def tuition(self):
		return self.course.tuition
	def __getattribute__(self, field):
		if field in ['paid','eligible','display_student','tuition']:
			call = super(Enrollment, self).__getattribute__(field)
			return call()
		elif field in Students.fields:
			return self.student.__getattribute__(field)
		elif field in Courses.fields:
			return self.course.__getattribute__(field)
		else:
			return super(Enrollment, self).__getattribute__(field)