from django.shortcuts import render, redirect, HttpResponse
from .models import Family, Address, Parent, User, Student
from apps.program.managers import CourseTrads, Courses, Enrollments, Auditions
from Utils.custom_fields import Bcrypt, PhoneNumber
from datetime import datetime
from Utils.hacks import copy, copyatts, seshinit, forminit, first, getme, numero, metanumero, json, copy_items_to_attrs, year, FriendlyEncoder, namecase, Each, equip, find_all
import json as JSON
from io import StringIO
from trace import TRACE, DEV

Addresses = Address.objects
Families  = Family.objects
Parents   = Parent.objects
Students  = Student.objects
Users     = User.objects

# - - - - - SECURITY FUNCTIONS - - - - -

def authorized(request, level=0):
	if TRACE:
		print '# main.views.authorized'
	return 'meid' in request.session

# - - - - - APPLICATION VIEWS - - - - -

def index(request):
	if TRACE:
		print '@ main.views.index'
	me = getme(request)
	context = {
		'name':me.owner if me else None,
		'incomplete_registration': me and not me.owner.children
	}
	return render(request, 'main/index.html', context)


def login(request):
	if TRACE:
		print '@ main.views.login'
	forminit(request,'login',['username','password'])
	if request.method == 'GET':
		return login_get(request)
	elif request.method == 'POST':
		return login_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def login_get(request):
	if TRACE:
		print '@ main.views.login_get'
	context = copy(request.session, ['p','e'])
	return render(request, 'main/login.html', context)

def login_post(request):
	if TRACE:
		print '@ main.views.login_post'
	me = Users.fetch(username=request.POST['username'])
	persist = copy(request.POST, ['username','password'])
	if not me:
		family = Families.fetch(last=namecase(request.POST['username']))
		if DEV and family:
			new_user = copy(request.POST,['username','password'])
			new_user['owner'] = family
			new_user['permission'] = 7
			Users.create(**new_user)
			request.session['meid'] = new_user['id']
			return redirect('/')
		else:
			request.session['e'] = {'login':{'username': "You do not have an account.  Please register."}}
			request.session['p'] = {'login':persist}
			return redirect('/login')
	elif not me.password(request.POST['password']):
		request.session['e'] = {'login':{'password': "Your password is incorrect"}}
		request.session['p'] = {'login':persist}
		return redirect('/login')
	else:
		request.session['meid'] = me.id
		return redirect('/')


def logout(request):
	if TRACE:
		print '@ main.views.logout'
	request.session.clear()
	return redirect ('/')


def account(request):
	if TRACE:
		print '@ main.views.account'
	me = getme(request)
	password = unicode(me.password.html)
	context = {
		'me':me,
		'password':password,
	}
	return render(request, 'main/account.html', context)


def changepassword(request, **kwargs):
	forminit(request,'form',['current_pw','password','pw_confm'])
	if request.method == 'GET':
		return changepassword_get(request, **kwargs)
	elif request.method == 'POST':
		return changepassword_post(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def changepassword_get(request):
	context = copy(request.session,'pe')
	return render(request, 'main/changepassword.html', context)

def changepassword_post(request):
	me = getme(request)
	if not me:
		return redirect('/')
	user = copy(request.POST,['password','pw_confm'])
	valid = Users.isValid(user, partial=True)
	if not valid:
		request.session['e'] = Users.errors(user, partial=True)
	correct = me.password(request.POST['current_pw'])
	if not correct:
		request.session['e']['current_pw'] = "Your password is incorrect"
	if correct and valid:
		request.session['e'] = {}
		me.password = request.POST['password']
		me.save()
		return redirect('/myaccount')
	else:
		return redirect('/changepassword')

#   - - - - NEW FAMILY REGISTRATION - - - -

def reg(request):
	if TRACE:
		print '@ main.views.reg'
	me = getme(request)
	if not me or not me.owner:
		return redirect('/register/familyinfo')
	elif not me.owner.mother and not me.owner.father:
		return redirect('/register/parentsinfo')
	else:
		return redirect('/register/studentsinfo')


def reg_familyinfo(request):
	if TRACE:
		print '@ main.views.reg_familyinfo'
	forminit(request,'family',['last','phone','email'])
	forminit(request,'user',['username','password','pw_confm'])
	seshinit(request,'password_set',False)
	if request.method == 'GET':
		return reg_familyinfo_get(request)
	elif request.method == 'POST':
		return reg_familyinfo_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def reg_familyinfo_get(request):
	if TRACE:
		print '@ main.views.reg_familyinfo_get'
	me = getme(request)
	if me and me.owner:
		request.session['p']['family'].update(copyatts(me.owner, ['last','phone_type','email']))
		request.session['p']['family']['phone'] = str(me.owner.phone)
		request.session['p']['user']['username'] = me.username
		request.session['password_set'] = True
	context = copy(request.session, ['p','e','password_set'])
	return render(request, 'register/familyinfo.html', context)

def reg_familyinfo_post(request):
	if TRACE:
		print '@ main.views.reg_familyinfo_post'
	me = getme(request)
	if me:
		me.username = request.POST['username']
		if me.owner:
			me.owner.save()
	new_family = copy(request.POST,['last','phone','phone_type','email'])
	new_family['last'] = namecase(new_family['last'])
	new_user = copy(request.POST,['username','password','pw_confm'])
	new_user['permission'] = 2
	ouu = me and str(new_user['username']) == str(me.username)
	if Families.isValid(new_family) and Users.isValid(new_user, override_unique_username=ouu):
		new_user.pop('pw_confm')
		if not me:
			print 'not me'
			new_family = Families.create(**new_family)
			new_user['owner'] = new_family
			me = Users.create(**new_user)
		elif me and not me.owner:
			print 'me and not me.owner'
			me.username = new_user['username']
			new_family = Families.create(**new_family)
			me.owner = new_family
			me.save()
		elif me and me.owner:
			print 'me and me.owner'
			me.username = new_user['username']
			family = me.owner
			family.last  = new_family['last']
			family.phone = new_family['phone']
			family.email = new_family['email']
			family.phone_type = new_family['phone_type']
			print new_family['email']
			print family.email
			family.save()
			me.save()
		request.session['e'] = {}
		request.session['meid'] = me.id
		return redirect('/register/parentsinfo')
	else:
		request.session['p'] = {
			'family': new_family,
			'user'  : new_user,
		}
		request.session['e'] = {
			'family': Families.errors(new_family),
			'user'  : Users.errors(new_user)
		}
		return redirect('/register/familyinfo')

# if me.owner
def reg_parentsinfo(request):
	if TRACE:
		print '@ main.views.reg_parentsinfo'
	if not authorized(request):
		return redirect('/')
	forminit(request,'mom',['mom_skipped','mom_first','mom_alt_last','mom_alt_phone','mom_alt_email'])
	forminit(request,'dad',['dad_skipped','dad_first','dad_alt_last','dad_alt_phone','dad_alt_email'])
	if request.method == 'GET':
		return reg_parentsinfo_get(request)
	elif request.method == 'POST':
		return reg_parentsinfo_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def reg_parentsinfo_get(request):
	if TRACE:
		print '@ main.views.reg_parentsinfo_get'
	me = getme(request)
	if not me or not me.owner:
		return redirect('/register/familyinfo')
	if me and me.owner.mother:
		request.session['p']['mom'].update({
			'mom_first'     : me.owner.mother.first,
			'mom_alt_last'  : me.owner.mother.alt_last,
			'mom_alt_phone' : me.owner.mother.alt_phone,
			'mom_alt_email' : me.owner.mother.alt_email,
			'mom_alt_phone_type' : me.owner.mother.phone_type,
		})
	if me and me.owner.father:
		request.session['p']['dad'].update({
			'dad_first'     : me.owner.father.first,
			'dad_alt_last'  : me.owner.father.alt_last,
			'dad_alt_phone' : me.owner.father.alt_phone,
			'dad_alt_email' : me.owner.father.alt_email,
			'dad_alt_phone_type' : me.owner.father.phone_type,
		})
	context = {
		'last'  : me.owner.last,
		'phone' : me.owner.phone,
		'email' : me.owner.email,
		'p'     : request.session['p'],
		'e'     : request.session['e'],
	}
	return render(request, 'register/parentsinfo.html', context)

def reg_parentsinfo_post(request):
	if TRACE:
		print '@ main.views.reg_parentsinfo_post'
	me = getme(request)
	# Create new Parent objects
	mom = copy(request.POST, [
		'mom_skipped',
		'mom_first',
		'mom_alt_last',
		'mom_alt_phone',
		'mom_phone_type',
		'mom_alt_email'
	])
	dad = copy(request.POST, [
		'dad_skipped',
		'dad_first',
		'dad_alt_last',
		'dad_alt_phone',
		'dad_phone_type',
		'dad_alt_email'
	])
	mother = copy(mom,trunc=4)
	father = copy(dad,trunc=4)
	# Convert 'skipped' booleans from JavaScript strings, to Python bools.
	mother['skipped'] = mother['skipped'] == 'true'
	father['skipped'] = father['skipped'] == 'true'
	# May it be many years before we have to change these two lines of code.
	mother['sex'] = 'F'
	father['sex'] = 'M'
	# Assign Parents to Family 
	mother['family_id'] = me.owner.id
	father['family_id'] = me.owner.id
	# Return sarcastic condescending message if both parents were somehow skipped.
	if mother['skipped'] and father['skipped']:
		return HttpResponse('''
			Congratulations!  You figured out how to hack JavaScript and skip both parents!
			Seriously though, we do need at least one first name.  Sorry.
			''')
	# Validate new Parent objects
	mother_valid = mother['skipped'] or Parents.isValid(mother)
	father_valid = father['skipped'] or Parents.isValid(father)
	if mother_valid and father_valid:
		request.session['e'] = {}
		# Add parents to Database if they have not been skipped
		if not mother.pop('skipped'):
			if me.owner.mother:
				mother_proxy = me.owner.mother
				mother_proxy.first     = mother['first']
				mother_proxy.alt_last  = mother['alt_last']
				mother_proxy.alt_phone = mother['alt_phone']
				mother_proxy.alt_email = mother['alt_email']
				mother_proxy.save()
			else:
				family = me.owner
				family.mother = Parents.create(**mother)
				family.save()
		if not father.pop('skipped'):
			if me.owner.father:
				father_proxy = me.owner.father
				father_proxy.first     = father['first']
				father_proxy.alt_last  = father['alt_last']
				father_proxy.alt_phone = father['alt_phone']
				father_proxy.alt_email = father['alt_email']
				father_proxy.save()
			else:
				family = me.owner
				family.father = Parents.create(**father)
				family.save()
		return redirect('/register/studentsinfo')
	else:
		request.session['p'] = {
			'mom':mom,
			'dad':dad,
		}
		request.session['e'] = {
			'mom':Parents.errors(mother),
			'dad':Parents.errors(father),
		}
		return redirect('/register/parentsinfo')        

# if me.owner.mother or me.owner.father
def reg_studentsinfo(request):
	if TRACE:
		print '@ main.views.reg_studentsinfo'
	if not authorized(request):
		return redirect('/')
	elif request.method == 'GET':
		return reg_studentsinfo_get(request)
	elif request.method == 'POST':
		return reg_studentsinfo_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def reg_studentsinfo_get(request):
	if TRACE:
		print '@ main.views.reg_studentsinfo_get'
	me = getme(request)
	if not me or not me.owner or not (me.owner.mother or me.owner.father):
		return redirect('/register')
	reg_year = year()
	grades = []
	for x in range(1,13):
		grades += [{'grade':x,'grad_year':reg_year - x + 12}]
	context = {
		'reg_year': reg_year,
		'grades'  : grades,
		'family'  : me.owner,
		't_shirt_sizes': metanumero(Student.t_shirt_sizes),
		'validations'  : json(Students.validations),
		'students': JSON.dumps(list(me.owner.children), cls=FriendlyEncoder) if me.owner.children else [],
	}
	return render(request, 'register/studentsinfo.html', context)

def reg_studentsinfo_post(request):
	if TRACE:
		print '@ main.views.reg_studentsinfo_post'
	me = getme(request)
	students = JSON.loads(request.POST['students'])
	for student in students:
		current = student.pop('exists')
		if student.pop('isNew'):
			student['family'] = me.owner
			student['current'] = True
			Students.create(**student)
		else:
			student_proxy = Students.fetch(id=student['id'])
			if student_proxy:
				if current:
					for key in ['first','middle','alt_last','alt_first','sex','grad_year','height','alt_phone','alt_email','tshirt']:
						if key in student:
							student_proxy.__setattr__(key, student[key])
				else:
					student_proxy.current = False
				student_proxy.save()
	return redirect('/register/student/{}/'.format(me.owner.children[0].id))


def reg_courses(request, **kwargs):
	if request.method == 'GET':
		return reg_courses_get(request, **kwargs)
	elif request.method == 'POST':
		return reg_courses_post(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def hours_worked(family):
	return 0.0

def reg_courses_get(request, **kwargs):
	me = getme(request)
	if not me or not me.owner or not me.owner.children:
		return redirect('/register')
	current_id = kwargs['id'] if 'id' in kwargs else 0
	if 'id' in kwargs:
		current_id = kwargs['id']
		current_student = me.owner.student_set.fetch(id=current_id)
		if not current_student:
			return redirect('/')
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
	return render(request, 'register/toggle_courses.html', context)

def reg_courses_enroll(request, **kwargs):
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

def reg_courses_audition(request, **kwargs):
	student_id = kwargs['id'] if 'id' in kwargs else 0
	student = Students.fetch(id=student_id)
	course = Courses.fetch(id=request.GET['course_id'])
	if course.eligible(student)['aud']:
		Enrollments.create(course=course, student=student, isAudition=True)
	return redirect('/register/student/{}/'.format(student_id))

def reg_courses_drop(request, **kwargs):
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


def reg_courses_post(request):
	return redirect('/')