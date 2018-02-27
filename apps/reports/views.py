from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Addresses, Families, Parents, Users, Students
from apps.program.managers import Courses, CourseTrads, Enrollments

from Utils.data import sub
from Utils.security import getyear

import re

def make(request, year):
	cts = CourseTrads.filter(e=True)
	for ct in cts:
		ct.make(year)
	return HttpResponse('ok')


def students(request, **kwargs):
	year = int(kwargs['year']) if 'year' in kwargs else getyear()
	families = Families.all().order_by('last')
	table = []
	blank = {'content':'','rowspan':1,'class':'enr'}
	ctids = {'SB':'TT','SG':'GB','SJ':'JR'}
	for family in families:
		oldest = True
		for student in family.children:
			row = {
				'family' : family,
				'student': student,
				'age'    : student.hst_age_in(year),
				'nchild' : len(family.children),
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
	