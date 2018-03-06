from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from .managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices

from Utils.data  import equip, find_all, Each, collect
from Utils.security import authorized, getme, getyear

def from_myaccount(request, **kwargs):
	me = getme(request)
	if me.owner.children:
		return redirect('/register/student/{}/'.format(me.owner.children[0].id))
	else:
		return redirect('/register/studentsinfo/')

def courses(request, **kwargs):
	me = getme(request)
	if not me or not me.owner or not me.owner.children:
		return redirect('/register')
	current_id = kwargs.setdefault('id',0)
	if 'id' in kwargs:
		current_id = kwargs['id']
		current_student = me.owner.student_set.fetch(id=current_id)
		if not current_student:
			return redirect('/')
	else:
		current_student = me.owner.children[0]
	reg_year = getyear()
	courses = Courses.filter(year=reg_year,tradition__e=True).order_by('tradition__order')
	cart = me.owner.enrollments_in(reg_year)
	cart_pend = cart.filter(status__in=['aud_pend','invoiced','lockedin'])
	cart_paid = cart.filter(status='enrolled')
	# cart_unpaid = cart.difference(cart_pend,cart_paid) # Use this line instead of next in Django 1.11+
	cart_unpaid = cart.exclude(status__in=['aud_pend','invoiced','lockedin','enrolled'])
	volunteer_total = me.owner.volunteer_total_in(reg_year)
	context = {
		'invoiceable' : bool(cart_unpaid), # TODO: This is simple enough now to be calculated in the HTML page
		'reg_year': reg_year,
		'family'  : me.owner,
		'students': equip(me.owner.children, lambda student: student.hst_age_in(reg_year), attr='age'),
		'current_student' : current_student,
		'menu'    : current_student.course_menu(year=reg_year),
		'cart'    : cart,
		'nCourses': {
			'total' : len(cart),
			'pend'  : len(cart_pend),
			'paid'  : len(cart_paid),
			'unpaid': len(cart_unpaid),
		},
		'tuition' : {
			'total' : sum(collect(cart, lambda enr: enr.course.tuition)),
			'pend'  : sum(collect(cart_pend, lambda enr: enr.course.tuition)),
			'paid'  : sum(collect(cart_paid, lambda enr: enr.course.tuition)),
			'unpaid': sum(collect(cart_unpaid, lambda enr: enr.course.tuition)),
		},
		'hours' : {
			'total' : me.owner.volunteer_total_in(reg_year),
			'pend'  : me.owner.hours_signed_in(reg_year),
			'paid'  : me.owner.hours_worked_in(reg_year),
			'unpaid': me.owner.volunteer_total_in(reg_year) 
					- me.owner.hours_signed_in(reg_year) 
					- me.owner.hours_worked_in(reg_year),
		},
	}
	return render(request, 'courses.html', context)


def courses_enroll(request, **kwargs):
	student_id = kwargs.setdefault('id',0)
	student = Students.fetch(id=student_id)
	course = Courses.fetch(id=request.GET['course_id'])
	course.cart(student)
	return redirect('/register/student/{}/'.format(student_id))

def courses_audition(request, **kwargs):
	student_id = kwargs.setdefault('id',0)
	student = Students.fetch(id=student_id)
	course = Courses.fetch(id=request.GET['course_id'])
	if course.audible(student):
		Enrollments.create(course=course, student=student, status="aud_pend")
	return redirect('/register/student/{}/'.format(student_id))

def courses_drop(request, **kwargs):
	student_id = kwargs.setdefault('id',0)
	enrollment = Enrollments.fetch(id=request.GET['enr_id'])
	if enrollment:
		enrollment.drop()
	return redirect('/register/student/{}/'.format(student_id))

def audition_menu(request, **kwargs):
	context = {
		'courses' : Courses.filter(enrollment__status__in=["aud_pend","pendpass","pendfail"]).distinct()
	}
	return render(request, 'audition_menu.html', context)

def audition_results(request, **kwargs):
	course = Courses.fetch(id=kwargs['id'])
	context = {
		'course' : course,
		'me' : getme(request),
	}
	return render(request, 'audition_results.html', context)

def audition_process(request, **kwargs):
	me = getme(request)
	course = Courses.fetch(id=kwargs['id'])
	for key in request.POST:
		if key.isdigit():
			student = Students.fetch(id=int(key))
			enrollment = student.enrollments.filter(course=course)[0]
			print student
			if request.POST[key] == u'accept':
				enrollment.accept(me)
			if request.POST[key] == u'reject':
				enrollment.reject(me)
	return redirect('/admin/auditions/')
