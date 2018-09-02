from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers  import Addresses, Families, Parents, Users, Students
from apps.program.managers import Courses, CourseTrads, Enrollments
from apps.program.eligex   import status_choices
from apps.program.models   import Year

from Utils.data import sub, Each, equip
from Utils.security import getyear, gethist, restricted
from decimal import Decimal

import re, datetime

def index(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	context = {
		'courses':Courses.filter(year=getyear()).order_by('tradition__order'),
		'year':getyear(),
	}
	return render(request, 'reports/index.html', context)

def roster(request, id):
	course = Courses.fetch(id=id)
	bad = restricted(request,5,course)
	if bad:
		return bad
	context = {
		'course':course
	}
	return render(request, 'reports/rowspan_roster.html', context)

def historical(request, **kwargs):
	history = []
	for year in gethist():
		history.append({
			'year':year,
			'courses':Courses.filter(year=year),
		})
	context = {'history':history}
	return render(request, 'reports/historical.html', context)

def enrollment_matrix(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	year = int(kwargs['year']) if 'year' in kwargs else getyear()
	kwargs.update(request.GET)
	everyone = kwargs.setdefault('everyone',False) == [u'True']
	siblings = kwargs.setdefault('siblings',False) == [u'True']
	siblings |= everyone
	families = Families.all()
	if not everyone:
		families = families.filter(children__enrollment__course__year=year).distinct()
	families = families.order_by('last','name_num')
	table = []
	blank = {'content':'','rowspan':1,'class':'enr'}
	ctids = {'SB':'TT','SG':'GB','SJ':'JR'}
	for family in families:
		oldest = True
		children = family.children.all() if siblings else family.children_enrolled_in(year)
		for student in children:
			row = {
				'family' : family,
				'last'   : family.unique_last_in(year),
				'student': student,
				'age'    : student.hst_age_in(year),
				'nchild' : len(children),
				'oldest' : oldest,
				'XW'     : [],
			}
			oldest = False
			for enrollment in student.enrollments_in(year):
				ctid = enrollment.course.tradition.id
				row[enrollment.course.genre] = {'enr':enrollment,'ctid':sub(ctid,ctids)}
				if ctid[0] in 'XW':
					row['XW'].append(enrollment)
			table.append(row)
	context = {
		'year'  : year,
		'table' : table,
	}
	return render(request, 'reports/enrollment_matrix_edit.html', context)

def address(request, **kwargs):
	bad = restricted(request,1)
	if bad:
		return bad
	year = getyear()
	context = {
		'families':Families.filter(children__enrollment__course__year=year).order_by('last').distinct(),
		'year':year,
	}
	return render(request, 'reports/addresses.html', context)

def directory(request, **kwargs):
	bad = restricted(request,1)
	if bad:
		return bad
	year = getyear()
	families = Families.filter(children__enrollment__course__year=year).order_by('last').distinct()
	context = {
		'families':families,
		'year':year,
	}
	return render(request, 'reports/directory.html', context)

def registration(request, **kwargs):
	bad = restricted(request,1)
	if bad:
		return bad
	year = getyear()
	qset = Students.filter(enrollment__course__year=year,enrollment__course__tradition__m=True).select_related('family').distinct().order_by('family__last','family__id','birthday')
	families = []
	students = []
	nchild = 0
	for s in xrange(len(qset)):
		student = qset[s]
		prevstu = qset[s-1] if s else None
		if not (prevstu and student.family.id == prevstu.family.id):
			nchild = 0
			stu = {
				'o':student,
				'first':True,
				'age':student.hst_age_in(year),
				'current_enrollments':student.enrollment.filter(course__year=year, course__tradition__m=True),
				'famspan':0,
			}
		# 	fam['students'].append(stu)
		else:
			stu = {
				'o':student,
				'first':False,
				'age':student.hst_age_in(year),
				'current_enrollments':student.enrollment.filter(course__year=year, course__tradition__m=True),
			}
		# 	fam = {
		# 		'o':student.family,
		# 		'students':[stu],
		# 	}
			nchild += 1
		# 	families.append(fam.copy())
		students.append(stu.copy())
		students[s-nchild]['famspan'] += 1
		# stu = {}
	context = {
		'families':families,
		'students':students,
		'year':year,
		'now':datetime.datetime.now()
	}
	return render(request, 'reports/registration.html', context)


def summary(request, **kwargs):
	kwargs.setdefault('year',getyear())
	context = {
		'year':Year(int(kwargs['year'])),
		'prev':Year(int(kwargs['year'])-1),
		'date':datetime.datetime.now(),
	}
	return render(request, 'reports/summary.html', context)

def refresh_summary(request, **kwargs):
	kwargs.setdefault('year',getyear())
	for course in Courses.filter(year__in=[kwargs['year'],kwargs['year']-1],tradition__action='trig'):
		for student in Students.filter(enrollment__course=course):
			course.trig(student)
	return redirect('/reports/summary/')

def generate_summary(request, **kwargs):
	Courses.create_by_id(request.GET['course_id'])
	return redirect('/reports/summary/')

def overview(request, **kwargs):
	GET = request.GET.copy()
	year = GET.setdefault('year',getyear())
	courses = Courses.filter(year=year).order_by('tradition__order')
	nTickets = {
		'SB': [len(Courses.fetch(tradition__id='KB',year=year).students),0,0],
		'SC': [len(Courses.fetch(tradition__id='KC',year=year).students),0,0],
		'SG': [
			len(Courses.fetch(tradition__id='KG',year=year).students),
			len(Courses.fetch(tradition__id='KS',year=year).students),
			len(Courses.fetch(tradition__id='KW',year=year).students),
		],
		'SJ': [
			len(Courses.fetch(tradition__id='KJ',year=year).students),
			len(Courses.fetch(tradition__id='KT',year=year).students),
			len(Courses.fetch(tradition__id='KX',year=year).students),
		],
		'SH': [
			len(Courses.fetch(tradition__id='KH',year=year).students),
			len(Courses.fetch(tradition__id='KU',year=year).students),
			len(Courses.fetch(tradition__id='KY',year=year).students),
		],
		'SR': [
			len(Courses.fetch(tradition__id='KR',year=year).students),
			len(Courses.fetch(tradition__id='KV',year=year).students),
			len(Courses.fetch(tradition__id='KZ',year=year).students),
		],
	}
	tSlots  = 0
	tFilled = 0
	tuitionRev = 0
	for course in courses.filter(tradition__e=True, tradition__m=True):
		tSlots  += course.tradition.nSlots
		tFilled += len(course.students)
		tuitionRev += course.revenue
	context = {
		'date':datetime.datetime.now(),
		'year':Year(year),
		'ar'  :'{:02}'.format(int(year)%100),
		'real':courses.filter(tradition__e=True, tradition__m=True),
		'auto':courses.filter(tradition__e=True, tradition__m=False),
		'stat':courses.filter(tradition__e=False,tradition__m=False),
		'rf'  :Courses.fetch(tradition__id='RF',year=year),
		'tSlots':tSlots,
		'tFilled':tFilled,
		'tuitionRev':tuitionRev,
		'total':{
			'SB': nTickets['SB'][0] * 10,
			'SC': nTickets['SC'][0] * 10,
			'SG': nTickets['SG'][0] * 10 + nTickets['SG'][1] * 15 + nTickets['SG'][2] * 20,
			'SH': nTickets['SH'][0] * 10 + nTickets['SH'][1] * 15 + nTickets['SH'][2] * 20,
			'SJ': nTickets['SJ'][0] * 10 + nTickets['SJ'][1] * 15 + nTickets['SJ'][2] * 20,
			'SR': nTickets['SR'][0] * 10 + nTickets['SR'][1] * 15 + nTickets['SR'][2] * 20,
			'10': sum(Each(nTickets.values()).__getitem__(0)),
			'15': sum(Each(nTickets.values()).__getitem__(1)),
			'20': sum(Each(nTickets.values()).__getitem__(2)),
			'tt': sum(Each(nTickets.values()).__getitem__(0)) * 10
				+ sum(Each(nTickets.values()).__getitem__(1)) * 15
				+ sum(Each(nTickets.values()).__getitem__(2)) * 20,
		},
	}
	prepaidRev = context['prepaidRev'] = context['total']['tt'] * 10
	context['totalRev'] = prepaidRev + context['tuitionRev'] + context['rf'].revenue
	return render(request, 'reports/overview.html', context)

def mass_enroll(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	year = kwargs.setdefault('year',getyear())
	courses = Courses.filter(year=kwargs['year'])
	students = []
	for x in request.POST:
		if x.isdigit():
			students.append(Students.fetch(id=int(x)))
	students.sort(key=lambda student: student.last)
	context = {
		'students': students,
		'courses' : courses,
		'status_choices': dict(status_choices).keys(),
	}
	return render(request, 'reports/mass_enroll.html', context)

# From mass_enroll
def register(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	new_enrollments = {}
	course = Courses.get(id=str(request.POST['course_id']))
	for x in request.POST:
		role_match = re.match(r'^role_(\d+)$', x)
		role_type_match = re.match(r'^role_type_(\d+)$', x)
		if role_match:
			student_id = role_match.groups()[0]
			if student_id not in new_enrollments:
				new_enrollments[student_id] = {}
			new_enrollments[student_id]['role'] = request.POST[x]
		elif role_type_match:
			student_id = role_type_match.groups()[0]
			if student_id not in new_enrollments:
				new_enrollments[student_id] = {}
			new_enrollments[student_id]['role_type'] = request.POST[x]
	for x in new_enrollments:
		student = Students.fetch(id=int(x))
		Enrollments.create(student=student, course=course, role=new_enrollments[x]['role'], role_type=new_enrollments[x]['role_type'], status=request.POST['status'])
	return redirect('/reports/students/2016/')
	