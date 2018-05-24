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
	'EP',
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
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices, PayPals
from apps.radmin.managers  import Policies

from Utils.data  import sub
import re, datetime

fake_families = [
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

def transfer():
	nFamilies = nParents = nStudents = 0
	start = datetime.datetime.now()
	orphans = []
	for family in OldFamilies.all():
		fam = Families.create(
			oid        = family.id,
			created_at = family.creationdate,
			updated_at = family.moddate,
			last       = family.family,
			hid        = family.accessid,
			phone      = family.home,
		)
		nFamilies += 1
		print family.family
		if family.mfirst:
			mom = Parents.create(
				family_id = fam.id,
				first     = family.mnick if family.mnick else family.mfirst,
				alt_last  = '' if family.mlast == fam.last else family.mlast,
				sex       = 'F',
				alt_phone = family.mcell,
			)
			fam.mother_id = mom.id
			nParents += 1
		if family.ffirst:
			dad = Parents.create(
				family_id = fam.id,
				first     = family.fnick if family.fnick else family.ffirst,
				alt_last  = '' if family.flast == fam.last else family.flast,
				sex       = 'M',
				alt_phone = family.fcell,
			)
			fam.father_id = dad.id
			nParents += 1
		if mom or dad:
			fam.save()
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
				first      = student.first,
				alt_last   = '' if (not family) or family.last  == student.last  else student.last,
				alt_email  = '' if (not family) or family.email == student.email else student.email,
				sex        = student.sex,
				birthday   = student.dob if student.dob else '2020-12-31',
				grad_year  = est_grad(student),
				tshirt     = sub(student.tshirt,{'AXL':'XL'}),
				needs      = student.needsdescribe
			)
			nStudents += 1
			print stu
		else:
			# print 'NO FAMILY FOUND FOR STUDENT', student.id
			orphans.append(student.id)
	print
	print 'TRANSFER COMPLETE'
	# print 'Users:     ' + str(nUsers).rjust(6)
	print 'Families:  ' + str(nFamilies).rjust(6)
	print 'Parents:   ' + str(nParents).rjust(6)
	print 'Students:  ' + str(nStudents).rjust(6)
	print 'Orphans:   ' + str(len(orphans)).rjust(6)
	# print 'Addresses: ' + str(nAddresses).rjust(6)
	# print 'Venues:    ' + str(nVenues).rjust(6)
	# print 'Traditions:' + str(nCourseTrads).rjust(6)
	# print 'Courses:   ' + str(nCourses).rjust(6)
	# print 'Enrollments:'+ str(nEnrollments).rjust(5)
	print 'Time:     '  + str(datetime.datetime.now() - start)
































