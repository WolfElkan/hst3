from django.shortcuts import render, redirect, HttpResponse
from .models import User, Family, Student, Parent, Address
from .custom_fields import Bcrypt, PhoneNumber
from datetime import datetime
from .utilities import copy, reprint
import json as JSON
from io import StringIO

Addresses = Address.objects
Families  = Family.objects
Parents   = Parent.objects
Students  = Student.objects
Users     = User.objects

# Create your views here.

# - - - - - HELPER FUNCTIONS - - - - -

# Function for initializing session variables.
def seshinit(request, sesh, val=''):
	if sesh not in request.session:
		request.session[sesh] = val

# Initialize form error/persist structure in session
def forminit(request, form_name, fields):
	for pe in 'pe':
		seshinit(request, pe, {})
		if form_name not in request.session[pe]:
			request.session[pe][form_name] = {}
			for f in fields:
				if f not in request.session[pe][form_name]:
					request.session[pe][form_name][f] = ''

# Select the first element in a query, without causing errors
def first(arr):
	if len(arr) == 0:
		return None
	else:
		return arr[0]

# Find User object for current logged-in user, without causing errors.
# me is always a User, never a Family, Student, or Faculty
def getme(request):
	if 'meid' not in request.session:
		return None
	else:
		return first(Users.filter(id=request.session['meid']))

# def setpath(obj,keypath,value):
#   if type(keypath) in [list,tuple] and len(keypath) > 1:
#       if '__getitem__' in dir(obj):
#           setpath(obj.__getitem__(keypath[0]),keypath[1:],value)
#       else:
#           setpath(obj.__getattribute__(keypath[0]),keypath[1:],value)
#   else:
#       obj.__setitem__(keypath[0], value)
#   return obj

# Does my having written this function belie a fundamental misunderstanding of Python?
def add(obj,tree):
	methods = dir(obj)
	for branch in tree:
		if type(tree[branch]) is not dict:
			if '__setitem__' in methods:
				obj.__setitem__(branch, tree[branch])
			elif '__setattr__' in methods:
				obj.__setattr__(branch, tree[branch])
		else:
			if '__getitem__' in methods:
				level = obj.__getitem__(branch)
			if '__getattr__' in methods:
				level = obj.__getattr__(branch)
			else:
				level = obj.__getattribute__(branch)
			add(level, tree[branch])
	return obj

# Convert a list to a dict object, so it can be parsed correctly on front end
def numero(obj):
	result = {}
	for x in range(len(obj)):
		result['no'+str(x)] = obj[x]
	return result

# Just like numero, but meta
def metanumero(obj):
	result = []
	for x in obj:
		result += [numero(x)]
	return result

def json(obj):
	result = []
	for x in obj:
		result += [x.__dict__]
	result = str(result)
	result = result.replace('\'','"')
	result = result.replace('&quot','"')
	result = result.replace('u"','"')
	result = result.replace('<type ','')
	result = result.replace('>','')
	return result

# - - - - - DEVELOPER VIEWS - - - - -

def hot(request):
	me = getme(request)
	seshinit(request,'command')
	context = {
		'command': request.session['command']
	}
	return render(request, 'main/hot.html', context)

def run(request):
	me = getme(request)
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

# - - - - - SECURITY FUNCTIONS - - - - -

def authorized(request):
	return 'meid' in request.session

# - - - - - APPLICATION VIEWS - - - - -

def index(request):
	me = getme(request)
	context = {
		'name':me.owner if me else None
	}
	return render(request, 'main/index.html', context)

def login(request):
	forminit(request,'login',['username','password'])
	if request.method == 'GET':
		return login_get(request)
	elif request.method == 'POST':
		return login_post(request)
	else:
		print "Unrecognized HTTP Verb"
		return index(request)

def login_get(request):
	context = copy(request.session, ['p','e'])
	return render(request, 'main/login.html', context)

def login_post(request):
	me = first(Users.filter(username=request.POST['username']))
	persist = copy(request.POST, ['username','password'])
	if not me:
		request.session['e'] = {'login':{'username': "You do not have an account.  Please register."}}
		request.session['p'] = {'login':persist}
		return redirect('/login')
	elif not me.pw(request.POST['password']):
		request.session['e'] = {'login':{'password': "Your password is incorrect"}}
		request.session['p'] = {'login':persist}
		return redirect('/login')
	else:
		request.session['meid'] = me.id
		return redirect('/')

def logout(request):
	request.session.clear()
	return redirect ('/')

#   - - - - NEW FAMILY REGISTRATION - - - -

def reg(request):
	me = getme(request)
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
	new_user = copy(request.POST,['username','password','pw_confm'])
	new_family['joined_hst'] = datetime.now().year
	new_family['reg_status'] = 1
	if Families.isValid(new_family) and Users.isValid(new_user):
		new_user.pop('pw_confm')
		new_family = Families.create(new_family)
		new_user['owner'] = new_family
		print new_user
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
	if not authorized(request):
		return redirect('/')
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
	me = getme(request)
	context = {
		'last'  : me.owner.last,
		'phone' : me.owner.phone,
		'email' : me.owner.email,
		'p'     : request.session['p'],
		'e'     : request.session['e'],
	}
	return render(request, 'register/parentsinfo.html', context)

def reg_parentsinfo_post(request):
	me = getme(request)
	# Create new Parent objects
	mom = copy(request.POST, ['mom_skipped','mom_first','mom_last','mom_alt_phone','mom_alt_email'])
	dad = copy(request.POST, ['dad_skipped','dad_first','dad_last','dad_alt_phone','dad_alt_email'])
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
			mother = Parents.create(mother)
			me.owner.mother = mother
		if not father.pop('skipped'):
			father = Parents.create(father)
			me.owner.father = father
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
	me = getme(request)
	# Every year on April 1, registration switches to the following year.
	now = datetime.now()
	next_year = 0 if now.month < 4 else 1
	reg_year = now.year + next_year
	grades = []
	for x in range(1,13):
		grades += [{'grade':x,'grad_year':reg_year - x + 12}]
	context = {
		'reg_year': reg_year,
		'grades'  : grades,
		'family'  : me.owner,
		't_shirt_sizes': metanumero(Student.t_shirt_sizes),
		'validations'  : json(Students.validations),
	}
	return render(request, 'register/studentsinfo.html', context)

def reg_studentsinfo_post(request):
	me = getme(request)
	students = JSON.loads(request.POST['students'])
	# print students
	for student in students:
		if student.pop('exists'):
			if student.pop('isNew'):
				student['family'] = me.owner
				student['current'] = True
				Students.create(student)
			else:
				pass
	return redirect('/register/studentsinfo')


