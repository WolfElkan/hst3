from django.shortcuts import render, redirect, HttpResponse
from apps.people.models import Family, Address, Parent, User, Student
from .managers import CourseTrads, Courses, Enrollments, Auditions
from Utils.custom_fields import Bcrypt, PhoneNumber
from datetime import datetime
from Utils.hacks import copy, copyatts, seshinit, forminit, getme, json, copy_items_to_attrs, year, FriendlyEncoder, namecase, Each, equip, find_all, pretty
import json as JSON
from io import StringIO
from trace import TRACE, DEV
import re

Addresses = Address.objects
Families  = Family.objects
Parents   = Parent.objects
Students  = Student.objects
Users     = User.objects

def hours_worked(family):
	return 0.0

def courses(request, **kwargs):
	me = getme(request)
	if not me or not me.owner or not me.owner.children:
		return redirect('/register')
	current_id = kwargs['id'] if 'id' in kwargs else 0
	if 'id' in kwargs:
		current_id = kwargs['id']
		current_student = me.owner.student_set.fetch(id=current_id)
		if not current_student:
			return redirect('/')
	else:
		current_student = me.owner.children[0]
	reg_year = year()
	courses = Courses.filter(year=reg_year,tradition__e=True).order_by('tradition__order')
	cart = me.owner.enrollments_in(reg_year)
	volunteer_total = me.owner.volunteer_total_in(reg_year)
	context = {
		'reg_year': reg_year,
		'family'  : me.owner,
		'students': equip(me.owner.children, lambda student: student.hst_age_in(reg_year), attr='age'),
		'current_student' : current_student,
		'courses' : equip(courses, lambda course: course.eligible(current_student), attr='elig'),
		'cart'    : equip(cart, lambda enr: enr.course.eligible(enr.student), attr='elig'),
		'nCourses': {
			'total' : len(cart),
			'paid'  : len(cart.filter(paid=True)),
			'unpaid': len(cart.filter(paid=False)),
		},
		'hours' : {
			'total' : volunteer_total,
			'paid'  : hours_worked(me.owner),
			'unpaid': volunteer_total - hours_worked(me.owner),
		},
		'tuition' : {
			'total' : me.owner.total_tuition_in(reg_year),
			'paid'  : me.owner.paid_tuition_in(reg_year),
			'unpaid': me.owner.total_tuition_in(reg_year) - me.owner.paid_tuition_in(reg_year),
		},
	}
	return render(request, 'courses.html', context)

def courses_enroll(request, **kwargs):
	student_id = kwargs['id'] if 'id' in kwargs else 0
	student = Students.fetch(id=student_id)
	course = Courses.fetch(id=request.GET['course_id'])
	if course.eligible(student)['now']:
		if course.prepaid:
			Ktrad = CourseTrads.fetch(id__startswith='K',id__endswith=course.show[1])
			Kid = course.id[0:2]+Ktrad.id
			K = Courses.create_by_id(Kid)
			prepaid = Enrollments.fetch(student__family=student.family, course=K)
			if not prepaid:
				Enrollments.create(student=student, course=K)
		Enrollments.create(course=course, student=student)
	return redirect('/register/student/{}/'.format(student_id))

def courses_audition(request, **kwargs):
	student_id = kwargs['id'] if 'id' in kwargs else 0
	student = Students.fetch(id=student_id)
	course = Courses.fetch(id=request.GET['course_id'])
	if course.eligible(student)['aud']:
		Enrollments.create(course=course, student=student, isAudition=True)
	return redirect('/register/student/{}/'.format(student_id))

def courses_drop(request, **kwargs):
	# Safely get student id
	student_id = kwargs['id'] if 'id' in kwargs else 0
	# Safely fetch student
	student = Students.fetch(id=student_id)
	# Safely fetch course
	course = Courses.fetch(id=request.GET['course_id'])
	# Find the enrollment and delete it
	Enrollments.filter(course=course, student=student).delete()
	# Check for any other enrollments that student is now ineligible for
	now_inelig = find_all(Enrollments.filter(student=student), lambda enr: not enr.eligible())
	# If course comes with prepaid tickets...
	if course.prepaid:
		# ...make sure some student in family is enrolled in another course that needs them
		other = Enrollments.filter(
			student__family=student.family, 
			course__tradition__prepaid=True, 
			course__tradition__show=course.show,
			course__year=year()
		)
		# Otherwise, delete the prepaid tickets from the cart
		if not other:
			Ktrad = CourseTrads.fetch(id__startswith='K',id__endswith=course.show[1])
			K = Courses.fetch(year=course.year, tradition=Ktrad)
			prepaid = Enrollments.fetch(student__family=student.family, course=K)
			if prepaid:
				prepaid.delete()
	return redirect('/register/student/{}/'.format(student_id))


def courses_post(request):
	return redirect('/')