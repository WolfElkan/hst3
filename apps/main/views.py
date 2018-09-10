from django.shortcuts import render, redirect, HttpResponse


from apps.people.managers   import Families, Addresses, Parents, Users, Students
from apps.program.managers  import CourseTrads, Courses, Enrollments
from apps.radmin.managers   import Policies
from apps.radmin.views.main import sudochangepassword

from Utils.data  import collect, copy, copyatts, Each, equip, find, find_all, sub
from Utils.debug import pretty, pdir, divs
from Utils.fjson import FriendlyEncoder
from Utils.misc  import namecase, safe_delete
from Utils.security import getme, getyear
from Utils.seshinit import seshinit, forminit

#from trace import DEV

import re

def index(request):
	if 'course' in request.GET:
		course = request.GET['course']
		if course:
			return redirect('/reports/roster/{}'.format(course))
		else:
			return redirect('/')
	me = getme(request)
	context = {
		'year':getyear(),
		'me':me,
		'name':me.owner if me else None,
		'incomplete_registration': me and me.owner and not me.owner.children,
		'sudo':Users.fetch(id=request.session.get('sudo')),
		'courses':Courses.filter(year=getyear(),tradition__m=True).order_by('tradition__order')
	}
	return render(request, 'main/index.html', context)

def slash(request):
	if request.POST:
		raise Warning('Slash Redirect does not support POST data.  Make sure form action ends with "/"')
	return redirect(request.path_info+'/')

def login(request, **kwargs):
	# Do not put any user authorization here!
	forminit(request,'login',['username','password'])
	if request.method == 'GET':
		return login_get(request, **kwargs)
	elif request.method == 'POST':
		return login_post(request, **kwargs)
	else:
		print "Unrecognized HTTP Verb"
		return index(request, **kwargs)

def login_get(request, **kwargs):
	context = copy(request.session, ['p','e'])
	return render(request, 'main/login.html', context)

def login_post(request, path):
	if not path:
		path = '/'
	me = Users.fetch(username=request.POST['username'])
	persist = copy(request.POST, ['username','password'])
	if not me:
		me = Families.fetch(email=request.POST['username'])
		if me:
			me = me.accounts
			if me:
				me = me[0]
	if not me:
		request.session['e'] = {'login':{'username': "You do not have an account.  Please register."}}
		request.session['p'] = {'login':persist}
		return redirect('/login{}'.format(path))
	elif not me.password(request.POST['password']):
		request.session['e'] = {'login':{'password': "Your password is incorrect"}}
		request.session['p'] = {'login':persist}
		return redirect('/login{}'.format(path))
	else:
		request.session['meid'] = me.id
		return redirect(path)


def logout(request):
	request.session.clear()
	return redirect ('/')


def account(request):
	me = getme(request)
	if not me:
		return redirect('/')
	password = unicode(me.password.html)
	context = {
		'me':me,
		'password':password,
		'year':getyear(),
		'policy':Policies.current,
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

def changepassword_get(request, **kwargs):
	context = copy(request.session,'pe')
	if 'them_id' in kwargs:
		context.update({'me':{
			'login': getme(request, both=True)['login'],
			'sudo' : Users.fetch(id=kwargs['them_id']),
		}})
	else:
		context.update({'me':getme(request, both=True)})
	return render(request, 'main/changepassword.html', context)

def changepassword_post(request, **kwargs):
	print "*"*100
	ref = kwargs.setdefault('ref',None)
	both = getme(request, both=True)
	me = both['login']
	if not me:
		return redirect('/')
	if 'them_id' in kwargs or both['sudo']:
		return sudochangepassword(request, **kwargs)
	user = copy(request.POST,['password','pw_confm'])
	valid = Users.isValid(user, partial=True)
	if not valid:
		request.session['e'] = {}
		request.session['e'] = Users.errors(user, partial=True)
	correct = me.password(request.POST['current_pw'])
	if not correct:
		request.session['e']['current_pw'] = "Your password is incorrect"
	if correct and valid:
		request.session['e'] = {}
		me.password = request.POST['password']
		me.save()
		return redirect('/{}/'.format(ref))
	return redirect(request.META['HTTP_REFERER'])


def dciv(request):
	return render(request, 'main/404.html', status=404)
