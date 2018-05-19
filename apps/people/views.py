from django.shortcuts import render, redirect, HttpResponse

from .managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.radmin.managers import Policies

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase
from Utils.security import restricted, getme, getyear
from Utils.seshinit import seshinit, forminit

import re
from datetime import datetime
import json as JSON

def reg(request):
	me = getme(request)
	if not me or not me.owner:
		return redirect('/register/family')
	elif not me.owner.mother and not me.owner.father:
		return redirect('/register/parents')
	else:
		return redirect('/register/students')

def family(request):
	forminit(request,'family',['last','phone','email'])
	forminit(request,'user',['username','password','pw_confm'])
	seshinit(request,'password_set',False)
	if request.method == 'GET':
		return family_get(request)
	elif request.method == 'POST':
		return family_post(request)
	else:
		return HttpResponse("Unrecognized HTTP Verb", status=405)

def family_get(request):
	me = getme(request)
	if me and me.owner:
		request.session['p']['family'].update(copyatts(me.owner, ['last','phone_type','email']))
		request.session['p']['family']['phone'] = str(me.owner.phone)
		request.session['p']['user']['username'] = me.username
		request.session['password_set'] = True
	context = copy(request.session, ['p','e','password_set'])
	return render(request, 'family.html', context)

def family_post(request):
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
			new_family = Families.create(**new_family)
			new_user['owner'] = new_family
			me = Users.create(**new_user)
		elif me and not me.owner:
			me.username = new_user['username']
			new_family = Families.create(**new_family)
			me.owner = new_family
			me.save()
		elif me and me.owner:
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
		return redirect('/register/parents')
	else:
		request.session['p'] = {
			'family': new_family,
			'user'  : new_user,
		}
		request.session['e'] = {
			'family': Families.errors(new_family),
			'user'  : Users.errors(new_user)
		}
		return redirect('/register/family')

# if me.owner
def parents(request):
	if restricted(request):
		return redirect('/')
	forminit(request,'mom',['mom_skipped','mom_first','mom_alt_last','mom_alt_phone','mom_alt_email'])
	forminit(request,'dad',['dad_skipped','dad_first','dad_alt_last','dad_alt_phone','dad_alt_email'])
	if request.method == 'GET':
		return parents_get(request)
	elif request.method == 'POST':
		return parents_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def parents_get(request):
	me = getme(request)
	if not me or not me.owner:
		return redirect('/register/family')
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
	return render(request, 'parents.html', context)

def parents_post(request):
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
		return redirect('/register/students')
	else:
		request.session['p'] = {
			'mom':mom,
			'dad':dad,
		}
		request.session['e'] = {
			'mom':Parents.errors(mother),
			'dad':Parents.errors(father),
		}
		return redirect('/register/parents')        

# if me.owner.mother or me.owner.father
def students(request):
	if restricted(request):
		return redirect('/')
	elif request.method == 'GET':
		return students_get(request)
	elif request.method == 'POST':
		return students_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def students_get(request):
	me = getme(request)
	if not me or not me.owner or not (me.owner.mother or me.owner.father):
		return redirect('/register')
	reg_year = getyear()
	grades = []
	for x in range(1,13):
		grades += [{'grade':x,'grad_year':reg_year - x + 12}]
	context = {
		'reg_year': reg_year,
		'grades'  : grades,
		'family'  : me.owner,
		't_shirt_sizes': collect(Students.model.t_shirt_sizes, lambda obj: dict(collect(obj,lambda val, index: ['no'+str(index),val]))),
		'validations'  : JSON.dumps(Students.validations, cls=FriendlyEncoder),
		'students': JSON.dumps(list(me.owner.children), cls=FriendlyEncoder) if me.owner.children else [],
	}
	return render(request, 'students.html', context)

def students_post(request):
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
					for key in ['first','alt_last','alt_first','sex','grad_year','height','alt_phone','alt_email','tshirt','needs']:
						if key in student:
							student_proxy.__setattr__(key, student[key])
				else:
					student_proxy.current = False
				student_proxy.save()
	return redirect('/register/policy/1/')


def policy(request, **kwargs):
	if request.method == 'GET':
		return policy_get(request, **kwargs)
	elif request.method == 'POST':
		return policy_post(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb", status=405)
	
def policy_get(request, page=None):
	if not page:
		return redirect(request.path_info+'1/')
	page = int(page)
	me = getme(request)
	policy = Policies.current
	if not policy:
		return HttpResponse("We're sorry.  We are unable to register you at this time as we have not yet finalized this year's policy agreement.  Please check back soon.")
	elif page <= policy.nPages:
		context = {
			'page'   : page,
			'full'   : policy,
			'content': policy.html(page),
		}
		return render(request, 'policy.html', context)
	else:
		return redirect('/register/student/{}/'.format(me.owner.children[0].id))

def policy_post(request, page):
	page = int(page)
	if page != int(request.POST.get('page')):
		return HttpResponse('Page numbers do not match', status=409)
	year = int(request.POST.get('year'))
	me = getme(request)
	path = re.match(r'(.*)(policy/\d+/?)',request.path_info)
	if path:
		path = path.groups()[0]
	if request.POST.get('accept'):
		family = me.owner
		family.policyYear = year
		family.policyPage = page
		family.policyDate = datetime.now()
		family.save()
		return redirect('{}policy/{}/'.format(path,page+1))
	elif str(path) == '/register/':
		return redirect('/')
	else:
		return redirect(path)
