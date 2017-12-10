from django.shortcuts import render, redirect, HttpResponse
from .models import USER, FAMILY, STUDENT, PARENT, ADDRESS
from .custom_fields import Bcrypt, PhoneNumber
from datetime import datetime
from .utilities import copy, reprint

Users     = USER.objects
Families  = FAMILY.objects
Students  = STUDENT.objects
Parents   = PARENT.objects
Addresses = ADDRESS.objects

# Create your views here.

# - - - - - HELPER FUNCTIONS - - - - -

# Function for initializing session variables.
def seshinit(request, sesh, val=''):
	if sesh not in request.session:
		request.session[sesh] = val

def forminit(request, form_name, fields):
	for pe in 'pe':
		seshinit(request, pe, {})
		if form_name not in request.session[pe]:
			request.session[pe][form_name] = {}
			for f in fields:
				if f not in request.session[pe][form_name]:
					request.session[pe][form_name][f] = ''

# - - - - - DEVELOPER VIEWS - - - - -

def hot(request):
	seshinit(request,'command')
	context = {
		# Models
		'command': request.session['command']
	}
	return render(request, 'main/hot.html', context)

def run(request):
	command = request.POST['command']
	request.session['command'] = command
	exec(command)
	return redirect ('/hot')

def clearthedatabaselikeanuclearbombandthisnameisverylongsoyoudontcallitbymistake(request):
	Users.all().delete()
	Families.all().delete()
	Students.all().delete()
	Parents.all().delete()
	Addresses.all().delete()
	request.session.clear()
	print '\n\n'+' '*34+'THE RADIANCE OF A THOUSAND SUNS'+'\n\n'
	return redirect ('/hot')

def clear(request):
	request.session.clear()
	return redirect ('/hot')

# - - - - - APPLICATION VIEWS - - - - -

def index(request):
	context = {}
	return render(request, 'main/index.html', context)

def test(request):
	return render(request, 'main/index.html')

#   - - - - NEW FAMILY REGISTRATION - - - -

def reg(request):
	# TODO: Detect if family has partially registered, redirect to appropriate step.
	return redirect('/register/familyinfo')

def reg_familyinfo(request):
	forminit(request,'family',['last','phone','email'])
	forminit(request,'user',['username','password','pw_confm'])
	if request.method == 'GET':
		return reg_familyinfo_get(request)
	elif request.method == 'POST':
		return reg_familyinfo_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def reg_familyinfo_get(request):
	context = copy(request.session, ['p','e'])
	return render(request, 'register/familyinfo.html', context)

def reg_familyinfo_post(request):
	new_family = copy(request.POST,['last','phone','email'])
	new_family['joined_hst'] = datetime.now().year
	new_family['reg_status'] = 1
	new_user = copy(request.POST,['username','password','pw_confm'])
	if Families.isValid(new_family) and Users.isValid(new_user):
		new_family = Families.create(new_family)
		new_user['owner'] = new_family
		me = Users.create(new_user)
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


def reg_parentsinfo(request):
	forminit(request,'mom',['mom_skipped','mom_first','mom_last','mom_alt_phone','mom_alt_email'])
	forminit(request,'dad',['dad_skipped','dad_first','dad_last','dad_alt_phone','dad_alt_email'])
	if request.method == 'GET':
		return reg_parentsinfo_get(request)
	elif request.method == 'POST':
		return reg_parentsinfo_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def reg_parentsinfo_get(request):
	me = Users.get(id=request.session['meid'])
	context = {
		'last'  : me.owner.last,
		'phone' : me.owner.phone,
		'email' : me.owner.email,
		'p'     : request.session['p'],
		'e'     : request.session['e'],
	}
	return render(request, 'register/parentsinfo.html', context)

def reg_parentsinfo_post(request):
	me = Users.get(id=request.session['meid'])
	# Create new Parent objects
	mom = copy(request.POST, ['mom_skipped','mom_first','mom_last','mom_alt_phone','mom_alt_email'])
	dad = copy(request.POST, ['dad_skipped','dad_first','dad_last','dad_alt_phone','dad_alt_email'])
	mother = copy(mom,trunc=4)
	father = copy(dad,trunc=4)
	# Convert 'skipped' booleans from JavaScript-friendly strings, to Python bools
	mother['skipped'] = mother['skipped'] == 'true'
	father['skipped'] = father['skipped'] == 'true'
	# May it be many years before we have to change these two lines of code.
	mother['sex'] = 'F'
	father['sex'] = 'M'
	# Return sarcastic condescending message if both parents were somehow skipped.
	if mother['skipped'] and father['skipped']:
		return HttpResponse('''
			Congratulations!  You figured out how to hack JavaScript and skip both parents!
			Seriously though, we do need at least one first name.  Sorry.
			''')
	# Validate new Parent objects
	mother_valid = not mother['skipped'] and Parents.isValid(mother)
	father_valid = not father['skipped'] and Parents.isValid(father)
	if mother_valid and father_valid:
		# Add parents to Database if they have not been skipped
		if not mother.pop('skipped'):
			mother = Parents.create(mother)
			me.owner.mother = mother
		if not father.pop('skipped'):
			father = Parents.create(father)
			me.owner.father = father
		me.owner.save()
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


def reg_studentsinfo(request):
	if request.method == 'GET':
		return reg_studentsinfo_get(request)
	elif request.method == 'POST':
		return reg_studentsinfo_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def reg_studentsinfo_get(request):
	context = {}
	return render(request, 'register/studentsinfo.html', context)

def reg_studentsinfo_post(request):
	return redirect('register')