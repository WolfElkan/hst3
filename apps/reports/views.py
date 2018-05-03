from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Addresses, Families, Parents, Users, Students
from apps.program.managers import Courses, CourseTrads, Enrollments

from Utils.data import sub
from Utils.security import getyear, gethist, restricted

import re

def index(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	context = {
		'courses':Courses.filter(year=getyear()).order_by('tradition__order'),
		'year':getyear()
	}
	return render(request, 'index.html', context)

def roster(request, id):
	course = Courses.fetch(id=id)
	bad = restricted(request,5,course)
	if bad:
		return bad
	context = {
		'course':course
	}
	return render(request, 'rowspan_roster.html', context)

def historical(request, **kwargs):
	history = []
	for year in gethist():
		history.append({
			'year':year,
			'courses':Courses.filter(year=year),
		})
	context = {'history':history}
	return render(request, 'historical.html', context)

def students(request, **kwargs):
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
		families = families.filter(student__enrollment__course__year=year).distinct()
	families = families.order_by('last','name_num')
	table = []
	blank = {'content':'','rowspan':1,'class':'enr'}
	ctids = {'SB':'TT','SG':'GB','SJ':'JR'}
	for family in families:
		oldest = True
		children = family.children if siblings else family.children_enrolled_in(year)
		for student in children:
			row = {
				'family' : family,
				'last'   : family.unique_last_in(year),
				'student': student,
				'age'    : student.hst_age_in(year),
				'nchild' : len(children),
				'oldest' : oldest,
			}
			oldest = False
			for enrollment in student.enrollments_in(year):
				ctid = enrollment.course.tradition.id
				row[ctid[:1]] = '<a href="/rest/show/enrollment/{}/">{}</a>'.format(enrollment.id, sub(ctid, ctids))
			table.append(row)
	context = {
		'year'  : year,
		'table' : table,
	}
	return render(request, 'students.html', context)

def mass_enroll(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	year = kwargs['year'] if 'year' in kwargs else getyear()
	courses = Courses.filter(year=kwargs['year'])
	students = []
	for x in request.POST:
		if re.match(r'^\d+$', x):
			students.append(Students.fetch(id=int(x)))
	students.sort(key=lambda student: student.last)
	context = {
		'students': students,
		'courses' : courses,
	}
	return render(request, 'mass_enroll.html', context)

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
		Enrollments.create(student=student, course=course, role=new_enrollments[x]['role'], role_type=new_enrollments[x]['role_type'])
	return redirect('/reports/students/2016/')
	