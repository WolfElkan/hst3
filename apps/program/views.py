from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from .managers import CourseTrads, Courses, Enrollments, Auditions
from apps.payment.managers import Invoices

from Utils.data  import equip, find_all, Each
from Utils.security import authorized, getme, getyear

def from_myaccount(request, **kwargs):
	me = getme(request)
	if me.owner.children:
		return redirect('/register/student/{}/'.format(me.owner.children[0].id))
	else:
		return redirect('/myaccount/')

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
	reg_year = getyear()
	courses = Courses.filter(year=reg_year,tradition__e=True).order_by('tradition__order')
	cart = me.owner.enrollments_in(reg_year)
	cart_pend = cart.filter(isAudition=True)
	cart_paid = cart.filter(isAudition=False, invoice__status='P')
	cart_unpaid = cart.filter(isAudition=False, invoice__status='N')
	volunteer_total = me.owner.volunteer_total_in(reg_year)
	context = {
		'invoiceable' : bool(cart.filter(isAudition=False,invoice_id__isnull=True)),
		'reg_year': reg_year,
		'family'  : me.owner,
		'students': equip(me.owner.children, lambda student: student.hst_age_in(reg_year), attr='age'),
		'current_student' : current_student,
		'courses' : equip(courses, lambda course: course.eligible(current_student), attr='elig'),
		'cart'    : equip(cart, lambda enr: enr.course.eligible(enr.student), attr='elig'),
		'nCourses': {
			'total' : len(cart),
			'pend'  : len(cart_pend) + len(cart_unpaid),
			'paid'  : len(cart_paid),
			'unpaid': len(cart) - len(cart_pend) - len(cart_paid) - len(cart_unpaid),
		},
		'hours' : {
			'total' : me.owner.volunteer_total_in(reg_year),
			'pend'  : me.owner.hours_signed_in(reg_year),
			'paid'  : me.owner.hours_worked_in(reg_year),
			'unpaid': me.owner.volunteer_total_in(reg_year) 
					- me.owner.hours_signed_in(reg_year) 
					- me.owner.hours_worked_in(reg_year),
		},
		'tuition' : {
			'total' : me.owner.total_tuition_in(reg_year),
			'pend'  : me.owner.pend_tuition_in(reg_year),
			'paid'  : me.owner.paid_tuition_in(reg_year),
			'unpaid': me.owner.unpaid_tuition_in(reg_year),
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
	student_id = kwargs.setdefault('id',0)
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
	# Find the enrollment
	enrollment = Enrollments.fetch(course=course, student=student)
	# Find the invoice to which enrollment has been added, (if it has been added to an invoice)
	invoices = set([enrollment.invoice])
	# Delete enrollment
	enrollment.delete()
	# Check for any other enrollments that student is now ineligible for
	now_inelig = find_all(Enrollments.filter(student=student), lambda enr: not enr.eligible['now'])
	# If course comes with prepaid tickets...
	if course.prepaid:
		# ...make sure some student in family is enrolled in another course that needs them
		other = Enrollments.filter(
			student__family=student.family, 
			course__tradition__prepaid=True, 
			course__tradition__show=course.show,
			course__year=getyear()
		)
		# Otherwise, delete the prepaid tickets from the cart
		if not other:
			Ktrad = CourseTrads.fetch(id__startswith='K',id__endswith=course.show[1])
			K = Courses.fetch(year=course.year, tradition=Ktrad)
			prepaid = Enrollments.fetch(student__family=student.family, course=K)
			if prepaid:
				if prepaid.invoice:
					invoices.add(prepaid.invoice)
				prepaid.delete()
	Each(invoices).update_amount()
	return redirect('/register/student/{}/'.format(student_id))