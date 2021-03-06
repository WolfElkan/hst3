from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers  import Addresses, Families, Parents, Users, Students
from apps.program.managers import Courses, CourseTrads, Enrollments
from apps.program.eligex   import status_choices
from apps.program.models   import Year

from Utils.data import sub, Each, equip, cleandate
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
	bad = restricted(request,1)
	if bad:
		return bad
	context = {
		'course':course
	}
	return render(request, 'reports/rowspan_roster.html', context)

def historical(request, **kwargs):
	bad = restricted(request,1)
	if bad:
		return bad
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
	# families = Families.filter(children__enrollment__course__year=year).order_by('last').distinct()
	families = layered_students_and_families(year)['families']
	context = {
		'families':families,
		'year':year,
	}
	return render(request, 'reports/directory.html', context)

def layered_queryset(year):
	qset = Students.select_related('family').filter(
		enrollment__course__year=year,
		enrollment__course__tradition__m=True,
		enrollment__status__in=['enrolled','invoiced','need_pay','aud_pass','aud_pend']).distinct()
	return qset.order_by('family__last','family__id','birthday')
	

def layered_students_and_families(year, qset=None, enrollments=False):
	if not qset:
		qset = layered_queryset(year)
	families = []
	students = []
	nchild = 0
	for s in xrange(len(qset)):
		student = qset[s]
		prevstu = qset[s-1] if s else None
		if not (prevstu and student.family.id == prevstu.family.id):
			if prevstu:
				families.append(family.copy())
			nchild = 0
			stu = {
				'o':student,
				'first':True,
				'age':student.hst_age_in(year),
				'famspan':0,
				'serial':s,
			}
			if enrollments:
				stu.update({'current_enrollments':student.enrollment.filter(course__year=year, course__tradition__m=True),})
			family = {
				'o':student.family,
				'children':[stu]
			}
		else:
			stu = {
				'o':student,
				'first':False,
				'age':student.hst_age_in(year),
				'serial':s,
			}
			if enrollments:
				stu.update({'current_enrollments':student.enrollment.filter(course__year=year, course__tradition__m=True),})
			family['children'].append(stu)
			nchild += 1
		students.append(stu.copy())
		students[s-nchild]['famspan'] += 1
	return {
		'students':students,
		'families':families,
	}


def registration(request, **kwargs):
	bad = restricted(request,1)
	if bad:
		return bad
	year = int(request.GET.copy().setdefault('year',getyear()))
	context = {
		'year':year,
		'now':datetime.datetime.now(),
		'sc':Courses.fetch(year=year, tradition=CourseTrads.fetch(id='SC')),
	}
	context.update(layered_students_and_families(year, enrollments=True))
	return render(request, 'reports/registration.html', context)


def summary(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	kwargs.setdefault('year',getyear())
	context = {
		'year':Year(int(kwargs['year'])),
		'prev':Year(int(kwargs['year'])-1),
		'date':datetime.datetime.now(),
	}
	return render(request, 'reports/summary.html', context)

def refresh_summary(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	kwargs.setdefault('year',getyear())
	for course in Courses.filter(year__in=[kwargs['year'],kwargs['year']-1],tradition__action='trig'):
		for student in Students.filter(enrollment__course=course):
			course.trig(student)
	return redirect('/reports/summary/')

def generate_summary(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	Courses.create_by_id(request.GET['course_id'])
	return redirect('/reports/summary/')

def overview(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	GET = request.GET.copy()
	year = GET.setdefault('year',getyear())
	if 'repop' in GET:
		all_students=Students.all()
		course = Courses.fetch(id=GET['repop'])
		if course:
			course.repop(all_students=all_students)
			return redirect('/reports/overview/?year='+year)
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
		'stat':Courses.filter(tradition__r=False, year=year).order_by('tradition__order'),
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
		'latest_enrollment':Enrollments.all().order_by('-updated_at')[0]
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
	
def signin(request):
	day = request.GET.get('day')
	if not day:
		context = {
			'today':datetime.datetime.today(),
		}
		return render(request, 'reports/signin_home.html', context)
	else:
		start = cleandate(request.GET.get('start'))
		qset = Enrollments.filter(
			course__tradition__m=True,
			course__tradition__day=day,course__year=getyear(start),
		).order_by(
			'student__family__last',
			'student__family__name_num',
			'student__birthday',
			'course__tradition__start',
		).distinct()
		weeks = request.GET.get('weeks')

		starts = list(set(Each(qset).course.tradition.start))
		starts.sort()
		context = {
			'qset':starts,
		}
		return render(request, 'reports/signin.html', context)
		# day_specs = {
		# 	'sun':None,
		# 	'mon':None,
		# 	'tue':{'start':datetime.date(2018,10, 9)},
		# 	'wed':{'start':datetime.date(2018,10,10)},
		# 	'thu':None,
		# 	'fri':{'start':datetime.date(2018, 9,28)},
		# 	'sat':None,
		# }[day]
		# print day_specs






