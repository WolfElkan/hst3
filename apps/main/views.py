from django.shortcuts import render, redirect
from .models import User, Family, Student, Parent
from datetime import datetime
from .utilities import get

Users    = User.objects
Families = Family.objects
Students = Student.objects
Parents  = Parent.objects

# Create your views here.

# - - - - - HELPER FUNCTIONS - - - - -

# Function for initializing session variables.
def seshinit(request, sesh, val=''):
	if sesh not in request.session:
		request.session[sesh] = val

def forminit(request, form_name, fields):
	blank = {}
	for f in fields:
		blank[f] = {'p':"", 'e':""}
	seshinit(request, form_name, blank)

def copy(source, keys=False):
	this = {}
	if not keys:
		keys = source.keys()
	for key in keys:
		this[key] = source[key]
	return this

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

def nuke(request):
	Users.all().delete()
	Families.all().delete()
	Students.all().delete()
	Parents.all().delete()
	return redirect ('/hot')

# - - - - - APPLICATION VIEWS - - - - -

def index(request):
	context = {}
	return render(request, 'main/index.html', context)

def test(request):
	# print models.User.password
	return render(request, 'main/index.html')

#   - - - - NEW FAMILY REGISTRATION - - - -

def reg(request):
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
	context = {
		'family': request.session['family'],
		'user'  : request.session['user'],
	}
	return render(request, 'register/familyinfo.html', context)

def reg_familyinfo_post(request):
	# Creates both Family AND User in database if they are valid
	new_family = copy(request.POST,['last','phone','email'])
	new_family['joined_hst'] = datetime.now().year
	new_user = copy(request.POST,['username','password','pw_confm'])
	new_user['owner_type'] = 'F'
	# print Families.create.__func__.func_code.co_varnames
	if Families.isValid(new_family) and Users.isValid(new_user):
		new_family = Families.create(new_family)
		new_user['owner_id'] = new_family.id
		me = Users.create(new_user)
		return redirect('/')
	else:
		request.session['family'] = Families.errors(new_family)
		request.session['user'] = Users.errors(new_user)
		return redirect('/register/familyinfo')

