course_mappings = [None,None,
	'AA',
	None,
	'AB',
	'SB',
	None,
	'C1',
	'J2',
	'HB',
	'Z1',
	'P1',
	'DI',
	'SG',
	'I1',
	'IH',
	'I2',
	'I3',
	'J1',
	'J2',
	'J3',
	'J4',
	'SJ',
	'O1',
	'O2',
	'SH',
	'LN',
	'SR',
	'T1',
	None,
	'T2',
	'T3',
	'T4',
	None,
	None,
	'XX',
	'C2',
	'WX',
	'CB',
	'JH',
	'XM',
	'IA',
	'IB',
	'IC',
	'JB',
	'IM',
	'WX',
	'ZZ',
	'WN',
	'AT',
	'Z2',
	None,
	'IS',
	'P2',
	None,
	'WW',
	'XA',
	'WP',
	'HM']

from .models import Alumnifamily
AlumniFamilies = Alumnifamily.objects

from .models import Courses as OldCourse
OldCourses = OldCourse.objects

# from .models import ErrorTable as Error
# Errors = Error.objects

from .models import Family as OldFamily
OldFamilies = OldFamily.objects

# from .models import Helptext as HelpText
# HelpTexts = HelpText.objects

from .models import Invoice as OldInvoice
OldInvoices = OldInvoice.objects

# from .models import Mailout
# Mailouts = Mailout.objects

from .models import Paypal as OldPayPal
OldPayPals = OldPayPal.objects

from .models import Registration
Registrations = Registration.objects

from .models import Showcase
Showcases = Showcase.objects

from .models import Student as OldStudent
OldStudents = OldStudent.objects

from apps.people.managers  import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments, Venues
from apps.payment.managers import Invoices, PayPals
from apps.radmin.managers  import Policies

from Utils.data import sub
from Utils.misc import namecase
from Utils.snippets import order_coursetrads, make
import re, datetime

test_families = [
3,37,276,277,280,300,305,308,309,310,311,312,313,314,315,
316,317,318,319,320,348,350,380,387,402,406,407,408,409,433,436]

def parse_grade(varchar):
	match = re.match(r'(\d\d?)(.{2})?',varchar)
	if match:
		return int(match.groups()[0])
	elif re.match(r'fresh',varchar,re.I):
		return 9
	elif re.match(r'soph',varchar,re.I):
		return 10
	elif re.match(r'junior',varchar,re.I):
		return 11
	elif re.match(r'senior',varchar,re.I):
		return 12
	elif re.match(r'c|alum|grad',varchar,re.I):
		return 13
	elif re.match(r'K',varchar,re.I):
		return 0

def est_grad(student):
	grade = parse_grade(student.grade)
	if grade:
		return student.moddate.year - grade + 13

def permission(family):
	admin = family.role == 'admin'
	board = family.board == 'TRUE'
	director = family.director == 'TRUE'
	if family.id in [210,372,55]:
		return 7
	elif director and admin:
		return 6
	elif board:
		return 5
	elif director:
		return 4
	elif admin:
		return 3
	elif family.id in [280,434]:
		return 1
	elif family.id in test_families:
		return 0
	else:
		return 2

def lookup_venue(varchar):
	if len(varchar) == 3:
		return varchar
	elif re.match(r'Redland',varchar):
		return 'RBC'
	elif re.match(r'Mullan',varchar):
		return 'MUL'
	else:
		return ''

def parse_venue(varchar):
	venue_id = lookup_venue(varchar)
	qset = Venues.filter(id=venue_id)
	if qset:
		return qset[0]

def parse_show(varchar):
	return {
		'As Assigned':'?',
		'Coffee House':'SB',
		'GB':'SG',
		'In class':'OP',
		'JR':'SJ',
		'none':'',
		'SH':'SH',
		'Showcase':'SC',
		'SR':'SR'
	}[varchar]

def parse_semester(old):
	if old.id in [47,51]:
		return 'N'
	elif re.match(r'fall',old.name,re.I) or re.match(r'.*?(Sep|Oct|Nov|Dec)',old.notes):
		return 'F'
	elif re.match(r'spring',old.name,re.I) or re.match(r'.*?(Jan|Feb|Mar|Apr)',old.notes):
		return 'S'
	else:
		return 'B'

def create_family(family):
	n = {
		'families':0,
		'parents' :0,
		'students':0,
		'users'   :0,
		'trads'   :0,
		'courses' :0,
		'enroll'  :0,
	}

	fam = Families.create(
		oid        = family.id,
		created_at = family.creationdate,
		updated_at = family.moddate,
		last       = family.family,
		hid        = family.accessid if hasattr(family,'accessid') else None,
		phone      = family.home,
	)
	n['families'] += 1
	print family.family
	if '@' in family.email and not Users.filter(username=family.email):
		user = Users.create(
			username   = family.email[0:30],
			password   = '$1$' + family.password,
			owner      = fam,
			permission = permission(family),
		)
		n['users'] += 1

	mom = None
	if family.mfirst:
		mom = Parents.create(
			family_id = fam.id,
			first     = family.mnick if family.mnick else family.mfirst,
			alt_last  = '' if family.mlast == fam.last else family.mlast,
			sex       = 'F',
			alt_phone = family.mcell,
		)
		fam.mother_id = mom.id
		n['parents'] += 1

	dad = None
	if family.ffirst:
		dad = Parents.create(
			family_id = fam.id,
			first     = family.fnick if family.fnick else family.ffirst,
			alt_last  = '' if family.flast == fam.last else family.flast,
			sex       = 'M',
			alt_phone = family.fcell,
		)
		fam.father_id = dad.id
		n['parents'] += 1

	if mom or dad:
		fam.save()

	return n


year = 2017

def transfer():
	n = {
		'families':0,
		'parents' :0,
		'students':0,
		'users'   :0,
		'trads'   :0,
		'courses' :0,
		'enroll'  :0,
	}
	start = datetime.datetime.now()
	orphans = []
	for family in OldFamilies.all().exclude(id__in=test_families):
		cf = create_family(family)
		for x in cf:
			n[x] += cf[x]
	for family in AlumniFamilies.filter(id=76):
		cf = create_family(family)
		for x in cf:
			n[x] += cf[x]

	print '*'*100

	for student in OldStudents.all():
		family = Families.fetch(hid=student.familyid)
		if family:
			stu = Students.create(
				oid        = student.id,
				hid        = student.studentid,
				created_at = student.creationdate,
				updated_at = student.moddate,
				family     = family,
				first      = namecase(student.first),
				alt_last   = '' if (not family) or family.last  == student.last  else student.last,
				alt_email  = '' if (not family) or family.email == student.email else student.email,
				sex        = student.sex,
				birthday   = student.dob if student.dob else '2020-12-31',
				grad_year  = est_grad(student),
				tshirt     = sub(student.tshirt,{'AXL':'XL'}),
				needs      = student.needsdescribe
			)
			n['students'] += 1
			print stu

		else:
			# print 'NO FAMILY FOUND FOR STUDENT', student.id
			orphans.append(student.id)

	print '*'*100

	for x in xrange(59):
		if course_mappings[x]:
			old = OldCourses.filter(id=x)[0]
			new = CourseTrads.fetch(id=course_mappings[x])
			if new:
				new.oid = old.courseid
				new.place = parse_venue(old.location)
				new.tuition = old.cost
				new.save()
			else:
				new = CourseTrads.create(
					id         = course_mappings[x],
					oid        = old.courseid,
					title      = old.name.title(),
					# e          = False,
					day        = old.day,
					start      = old.start,
					end        = old.end,
					place      = parse_venue(old.location),
					show       = parse_show(old.show),
					sa         = bool(old.show2),
					semester   = parse_semester(old),
					min_age    = old.minage,
					max_age    = old.maxage,
					tuition    = old.cost,
					vol_hours  = old.volhours,
					the_hours  = 2*bool(old.volhours),
					created_at = old.creationdate,
					updated_at = old.moddate
				)
				print new
				n['trads'] += 1

	print '*'*100

	n['courses'] += make(year)

	for reg in Registrations.all():
		student = Students.fetch(hid=reg.studentid)
		course  = Courses.fetch(year=year,tradition__oid=reg.courseid)
		print student, course
		if student and course:
			Enrollments.create(student=student, course=course)
			n['enroll'] += 1

	print
	print 'TRANSFER COMPLETE'
	print 'Users:     ' + str(n['users']).rjust(6)
	print 'Families:  ' + str(n['families']).rjust(6)
	print 'Parents:   ' + str(n['parents']).rjust(6)
	print 'Students:  ' + str(n['students']).rjust(6)
	print 'Orphans:   ' + str(len(orphans)).rjust(6)
	# print 'Addresses: ' + str(nAddresses).rjust(6)
	# print 'Venues:    ' + str(nVenues).rjust(6)
	print 'Traditions:' + str(n['trads']).rjust(6)
	print 'Courses:   ' + str(n['courses']).rjust(6)
	print 'Enrollments:'+ str(n['enroll']).rjust(5)
	print 'Time:     '  + str(datetime.datetime.now() - start)
































