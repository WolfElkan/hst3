from django.shortcuts import render, redirect
from .models import USER, FAMILY, STUDENT, PARENT
from .custom_fields import BcryptHash
from datetime import datetime
from .utilities import copy, reprint

Users    = USER.objects
Families = FAMILY.objects
Students = STUDENT.objects
Parents  = PARENT.objects

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

def nuke(request):
	Users.all().delete()
	Families.all().delete()
	Students.all().delete()
	Parents.all().delete()
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
	# print '*'*100
	# print context
	return render(request, 'register/familyinfo.html', context)

def reg_familyinfo_post(request):
	new_family = copy(request.POST,['last','phone','email'])
	new_family['joined_hst'] = datetime.now().year
	new_user = copy(request.POST,['username','password','pw_confm'])
	if Families.isValid(new_family) and Users.isValid(new_user):
		new_family = Families.create(new_family)
		new_user['owner'] = new_family
		me = Users.create(new_user)
		request.session['meid'] = me.id
		return redirect('/')
	else:
		print '~'*100
		request.session['p'] = {
			'family': new_family,
			'user'  : new_user,
		}
		request.session['e'] = {
			'family': Families.errors(new_family),
			'user'  : Users.errors(new_user)
		}
		return redirect('/register/familyinfo')

