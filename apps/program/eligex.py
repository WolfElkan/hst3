from .managers import Courses, Enrollments
from apps.people.managers import Students
from Utils.data import Each
from Utils.debug import kwargle
import re, random, datetime

TRACE = False

def check_eligex(course, student, **kwargs):
	# Set defaults for omitted keyword arguments
	eligex = kwargs.setdefault('eligex', None)
	year   = kwargs.setdefault('year'  , None)
	aud    = kwargs.setdefault('aud'   , False)
	cur    = kwargs.setdefault('cur'   , False)
	conj   = kwargs.setdefault('conj'  , True)
	debug  = kwargs.setdefault('debug' , TRACE)

	if kwargs.get('debug'):
		print 'check_eligex', course, student, kwargle(kwargs)

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
	if course.aud_date and datetime.datetime.now().date() > course.aud_date:
		kwargs['aud'] = False

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
			kwargs['conj'] = True
			result = check_eligex(trad, student, **kwargs)
			result = not result if x[0] else result
			if kwargs.get('debug'):
				print '{'+x[1]+'} =', result

		# OR clause
		elif x[3]:
			kwargs['eligex'] = x[3]
			kwargs['conj'] = False
			result = check_eligex(trad, student, **kwargs)
			result = not result if x[2] else result
			if kwargs.get('debug'):
				print '<{}> ='.format(x[3]), result

		# Eligex WORD
		elif x[5]:
			result = check_word(trad, student, x[5], **kwargs)
			result = not result if x[4] else result
			if kwargs.get('debug'):
				print x[5],'=', result

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
	debug  = kwargs.setdefault('debug' , TRACE)

	if kwargs.get('debug'):
		print 'check_word', trad, student, word, kwargle(kwargs)
	
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
			'status__in':["enrolled","invoiced","need_pay","aud_pass","maydefer"],
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
			# if kwargs.get('debug'):
				# print query
			return bool(Enrollments.filter(**query).exclude(student=student,course__tradition=trad,course__year=year))

		# If the word is '**', then you don't care what course it is, as long as it's this year.
		if word == '**':
			if kwargs['cur']:
				return True
			query['course__year'] = year
			# if kwargs.get('debug'):
				# print query
			return bool(Enrollments.filter(**query).exclude(student=student,course__tradition=trad,course__year=year))

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
		query_result = Enrollments.filter(**query).exclude(student=student,course__tradition=trad,course__year=year)
		# if kwargs.get('debug'):
			# print query
			# print 'Quota:',word.count('+')
		if '+' in word:
			# return True
			# print word.count('+')
			# print len(set(Each(Each(query_result).student).id))
			# return len(set(Each(Each(query_result).student).id))
			# return len(set(Each(Each(query_result).student).id)) >= word.count('+')
			# print ids
			# return False
			# return len(Students.filter(enrollment__id__in=ids).distinct())
			return len(Students.filter(enrollment__in=query_result).distinct()) >= word.count('+')
		else:
			return bool(query_result)


def calc_status(enr, cart=False):
	if TRACE:
		print 'calc_status',enr,cart
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
	if TRACE:
		print 'eligible',course,student
	superdebug = False
	if superdebug:
		print
		print '_'*100
		print student, course
	enrollment = Enrollments.fetch(course=course,student=student)
	if enrollment and enrollment.status in ["aud_pass","aud_pend"]:
		return True
	return student.family.has_accepted_policy(course.year) and check_eligex(course, student, debug=superdebug)


def audible(course, student):
	if TRACE:
		print 'audible',course,student
	return check_eligex(course, student, aud=True)


def enroll(course, student):
	pass

def drop(course, student):
	pass

def defer(enrollment):
	pass

def accept(course,student):
	pass

def reject(course,student):
	pass

status_choices = [
	("enrolled","{student} {proverb} enrolled in {course} ({year})"),                               # invoice__status='P' # Stable
	("eligible","{student} is eligible for {course}"),                                                                    # Stable
	("invoiced","{student}'s enrollment in {course} has been added to invoice #{invoice}"),         # invoice__status='N' # Stable
	("need_pay","{student} is registered for {course} pending tuition payment"),                                          # Stable
	("not_elig","{student} is not eligible for {course}"),                                                                # Unstable
	("aud_need","{student} is eligible for {article} {audskil} for {course}."),                                           # Unstable
	("aud_pend","{student} has scheduled {article} {audskil} for {course} ({year})"),                                     # Stable
	("pendpass","{student} has completed the {audskil} and is recommended for {course} {year}, pending executive approval."),  # Stable
	("pendfail","{student} has completed the {audskil} but is not recommended for {course} {year}, pending executive approval."),  # Stable
	("pend_pub","{student} has completed {article} {audskil} for {course} and is awaiting the results."),                 
	("fail_pub",""),
	("aud_pass","{student} has passed the {audskil} for {course}!"),                                                      # Stable
	("aud_fail","{student} did not pass the {audskil} for {course}."),                                                    # Invisible
	("aud_drop","{student} passed the {audskil} for {course} and may now enroll."),   # Stable
	("aud_lock","{student} has passed the {audskil} for {course} and must enroll."),                                      # Stable
	("conflict","{student} is in another class at the same time as {course}"),                                            # Unstable
	("need_cur","{student} will be eligible for {course} once {pronoun} enrolls in at least 1 other {year} class"),              # Unstable
	("needboth","{student} will be eligible to audition for {course} once {pronoun} enrolls in at least 1 other {year} class"),  # Unstable
	("nonexist","{student} was enrolled in {course} ({year}) on cancelled invoice #{invoice}"),     # invoice__status='C' # Invisible
	("nopolicy","{family} must accept HST's {year} Policy Agreement before enrolling students."),
	("clasfull","This class is full."),
	("maydefer","{course} may be deferred until Fall Parent Meeting"),
	("deferred","{course} has been deferred, but must be paid for by Fall Parent Meeting"),
]
