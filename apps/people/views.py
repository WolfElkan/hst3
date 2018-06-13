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

def reg(request, ref, step, id=None):
	me = getme(request)
	if step == 'family':
		return family(request, ref)
	elif step == 'parents':
		return parents(request, ref)
	elif step == 'students':
		return students(request, ref, id)
	elif step == 'policy':
		return policy(request, ref, id)
	elif step == 'redirect':
		if not me or not me.owner:
			return redirect('/register/family/')
		elif not me.owner.mother and not me.owner.father:
			return redirect('/register/parents/')
		else:
			return redirect('/register/students/')



def family(request, ref):
	forminit(request,'family',['last','phone','email'])
	forminit(request,'user',['username','password','pw_confm'])
	seshinit(request,'password_set',False)
	if request.method == 'GET':
		return family_get(request, ref)
	elif request.method == 'POST':
		return family_post(request, ref)
	else:
		return HttpResponse("Unrecognized HTTP Verb", status=405)

def family_get(request, ref):
	me = getme(request)
	if me and me.owner:
		request.session['p']['family'].update(copyatts(me.owner, ['last','phone_type','email']))
		request.session['p']['family']['phone'] = str(me.owner.phone)
		request.session['p']['user']['username'] = me.username
		request.session['password_set'] = True
	context = copy(request.session, ['p','e','password_set'])
	return render(request, 'family.html', context)

def family_post(request, ref):
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
def parents(request, ref):
	if restricted(request):
		return redirect('/')
	forminit(request,'mom',['mom_skipped','mom_first','mom_alt_last','mom_alt_phone','mom_alt_email'])
	forminit(request,'dad',['dad_skipped','dad_first','dad_alt_last','dad_alt_phone','dad_alt_email'])
	if request.method == 'GET':
		return parents_get(request, ref)
	elif request.method == 'POST':
		return parents_post(request, ref)
	else:
		print "Unrecognized HTTP Verb"
		return index(request, ref)

def parents_get(request, ref):
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

def parents_post(request, ref):
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

student_fields = ['first','alt_last','alt_first','sex','birthday','grad_year','tshirt','alt_phone','alt_email','needs']

# if me.owner.mother or me.owner.father
def students(request, ref, id):
	if restricted(request):
		return redirect('/')
	elif request.method == 'GET':
		if id == 'new':
			return students_new(request, ref)
		else:
			return students_edit(request, ref, id)
	elif request.method == 'POST':
		if id == 'new':
			return students_create(request, ref)
		else:
			return students_update(request, ref, id)
	else:
		print "Unrecognized HTTP Verb"
		return index(request, ref)

def students_edit(request, ref, id):
	me = getme(request)
	if not me or not me.owner or not (me.owner.mother or me.owner.father):
		return redirect('/register/redirect/')
	student = Students.fetch(id=id)
	if not student:
		return redirect('/{}/students/new/'.format(ref))
	forminit(request,'student',student_fields,obj=student)
	context = {
		'new':False,
		'reg_year': getyear(),
		'family'  : me.owner,
		't_shirt_sizes': collect(Students.model.t_shirt_sizes, lambda obj: dict(collect(obj,lambda val, index: ['no'+str(index),val]))),
		'students': me.owner.children,
		'ref':ref,
		'current_student':student,
		'e':request.session['e'],
		'p':request.session['p'],
	}
	return render(request, 'students2.html', context)

def students_update(request, ref, id):
	student = Students.fetch(id=id)
	data = copy(request.POST, student_fields)
	if not Students.isValid(data):
		request.session['e'] = Students.errors(data)
		request.session['p'] = data.copy()
		return redirect('/{}/students/{}/'.format(ref,student.id))
	else:
		request.session['e'] = {}
		for field in student_fields:
			student.__setattr__(field,data[field])
		student.save()
		return redirect('/{}/students/{}/'.format(ref,request.POST['next']))

new_student = {'prefer':'New Student','id':'new'}

def students_new(request, ref):
	me = getme(request)
	if not me or not me.owner or not (me.owner.mother or me.owner.father):
		return redirect('/register/redirect/')
	students = list(me.owner.children)
	students.append(new_student)
	context = {
		'new':True,
		'reg_year': getyear(),
		'family'  : me.owner,
		't_shirt_sizes': collect(Students.model.t_shirt_sizes, lambda obj: dict(collect(obj,lambda val, index: ['no'+str(index),val]))),
		'students': students,
		'ref':ref,
		'current_student':new_student,
		'e':request.session['e'],
		'p':request.session['p'],
	}
	return render(request, 'students2.html', context)

def students_create(request, ref):
	me = getme(request)
	data = copy(request.POST, student_fields)
	if not Students.isValid(data):
		if request.POST['next'] == 'new':
			request.session['e'] = Students.errors(data)
			request.session['p'] = data.copy()
			return redirect('/{}/students/new/'.format(ref))
		else:
			request.session['e'] = {}
			return redirect('/{}/students/{}/'.format(ref,request.POST['next']))
	else:
		data['family'] = me.owner
		new_student = Students.create(**data)
		request.session['e'] = {}
		if request.POST['next'] == 'new':
			return redirect('/{}/students/{}/'.format(ref,new_student.id))
		else:
			return redirect('/{}/students/{}/'.format(ref,request.POST['next']))
	

def policy(request, ref, page):
	if request.method == 'GET':
		return policy_get(request, ref, page)
	elif request.method == 'POST':
		return policy_post(request, ref, page)
	else:
		return HttpResponse("Unrecognized HTTP Verb", status=405)
	
def policy_get(request, ref, page=None):
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
		return redirect('/register/classes/{}/'.format(me.owner.children[0].id))

def policy_post(request, ref, page):
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
