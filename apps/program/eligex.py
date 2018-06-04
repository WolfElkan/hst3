from .managers import Courses, Enrollments
from Utils.data import Each
import re


def check_eligex(course, student, **kwargs):

	# Set defaults for omitted keyword arguments
	eligex = kwargs.setdefault('eligex', None)
	year   = kwargs.setdefault('year'  , None)
	aud    = kwargs.setdefault('aud'   , False)
	cur    = kwargs.setdefault('cur'   , False)
	conj   = kwargs.setdefault('conj'  , True)
	debug  = kwargs.setdefault('debug' , False)

	# Check for Course or CourseTrad
	if course.rest_model == 'course':
		trad = course.tradition
		kwargs['year'] = year = course.year
	elif course.rest_model == 'coursetrad':
		trad = course
		course = Courses.fetch(year=year, tradition=trad)
	else:
		raise Exception('course argument must be Course or CourseTrad object')

	# Set default eligex.  This will be overridden in recursion.
	if eligex is None:
		eligex = trad.eligex

	# If this course's audition date has already passed, don't check for audition eligibility
	if course and course.aud_date and datetime.now().date() > course.aud_date:
		aud = False

	# Checks to make sure Eligex is valid
	if re.match(r'<[^>]*<|{[^}]*{',trad.eligex):
		raise Exception('Nested clauses of the same type are not currently supported.')

	# Find Eligex words and clauses
	matches = re.findall(r'(!?){([^}]*)}|(!?)<([^>]*)>|(!?)([^<>{} ]*)', eligex)

	# Iterate Eligex words and clauses
	for x in matches:

		# AND clause
		if x[1]:
			kwargs['eligex'] = x[1]
			result = check_eligex(trad, student, **kwargs)
			result = not result if x[0] else result
			if kwargs.get('debug'):
				print '{',x[1],'}\n', result

		# OR clause
		elif x[3]:
			kwargs['eligex'] = x[3]
			kwargs['conj'] = False
			result = check_eligex(trad, student, **kwargs)
			result = not result if x[2] else result
			if kwargs.get('debug'):
				print '<{}>\n'.format(x[3]), result

		# Eligex WORD
		elif x[5]:
			result = check_word(trad, student, x[5], **kwargs)
			result = not result if x[4] else result
			if kwargs.get('debug'):
				print x[5],'\n', result

		else:
			result = kwargs['conj']

		if result != kwargs['conj']:
			return result

	return kwargs['conj']


def check_word(trad, student, word, **kwargs):
	
	# Set defaults for omitted keyword arguments
	year   = kwargs.setdefault('year'  , None)
	aud    = kwargs.setdefault('aud'   , False)
	cur    = kwargs.setdefault('cur'   , False)
	debug  = kwargs.setdefault('debug' , False)

	# Boolean literals
	if '#' in word:
		return True
	elif '~' in word:
		return False

	# Sex literals
	elif 'm' in word:
		return student.sex == 'M'
	elif 'f' in word:
		return student.sex == 'F'

	# Development literal
	elif word == '%':
		return DEV

	# Check age
	elif 'a' in word:
		old_enough   = student.hst_age_in(year) >= trad.min_age - word.count('y')
		young_enough = student.hst_age_in(year) <= trad.max_age + word.count('o')
		return old_enough and young_enough

	# Check grade
	elif 'g' in word:
		if not student.grad_year:
			return True
		old_enough   = student.grade_in(year) >= trad.min_grd - word.count('y') 
		young_enough = student.grade_in(year) <= trad.max_grd + word.count('o')
		return old_enough and young_enough
	
	# If you get this far, you're going to query the database
	else:
		query = {
			'student':student,
			'status__in':["enrolled","invoiced","need_pay","aud_pass"],
		}

		# Check for auditions
		if word == '@':
			if aud:
				return True
			else:
				query.update({
					'status':"aud_pass",
					'course__tradition': trad,
					'course__year': year,
				})
			if kwargs.get('debug'):
				print query
			return bool(Enrollments.filter(**query))

		# If the word is '**', then you don't care what course it is, as long as it's this year.
		if word == '**':
			if kwargs['cur']:
				return True
			query['course__year'] = year
			if kwargs.get('debug'):
				print query
			return bool(Enrollments.filter(**query))

		# Support * for representing any character
		if '*' not in word:
			query['course__tradition__id'] = word[0:2]
		elif word[0] != '*':
			query['course__tradition__id__startswith'] = word[0]
		elif word[1] != '*':
			query['course__tradition__id__endswith'] = word[1]


		if not kwargs['cur'] and '/' not in word:
			query['course__year'] = year
		if '/' in word:
			query['course__year__lt'] = year
		if '$' in word:
			query.pop('status__in')
			query['status'] = "enrolled"
		if '+' in word:
			query.pop('student')
			query['student__family'] = student.family
		if kwargs.get('debug'):
			print query
		return bool(Enrollments.filter(**query))


def calc_status(enr, cart=False):
	# print enr.course.id, enr.status
	if cart:
		if check_eligex(enr.course, enr.student):
			return "need_pay"
		elif check_eligex(enr.course, enr.student, aud=True):
			return "aud_pend"
	if enr.status in ["aud_pass","aud_fail","aud_drop","nonexist","aud_pend"]:
		return enr.status
	if not check_eligex(enr.course, enr.student, aud=True, cur=True):
		return "not_elig"
	elif not enr.student.family.has_accepted_policy(enr.course.year):
		return "nopolicy"
	elif enr.course.nSlots and len(enr.course.students) >= enr.course.nSlots:
		return "clasfull"
	elif any(Each(enr.student.courses_in(enr.course.year)).conflicts_with(enr.course)):
		return "conflict"
	elif check_eligex(enr.course, enr.student):
		return enr.status if enr.id else "eligible"
	elif check_eligex(enr.course, enr.student, aud=True):
		return enr.status if enr.id else "aud_need"
	elif check_eligex(enr.course, enr.student, cur=True):
		return "need_cur"
	# elif check_eligex(enr.course, enr.student, aud=True, cur=True):
	else:
		return "needboth"


def eligible(course, student):
	return student.family.has_accepted_policy(course.year) and check_eligex(course, student)


def audible(course, student):
	return check_eligex(course, student, aud=True)