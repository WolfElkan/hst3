from datetime import datetime
from Utils.data import cleandate

def getyear(now=None):
	if now:
		now = cleandate(now)
	else:
		now = datetime.now()
	return now.year + (0 if now.month < 5 else 1)

from django.shortcuts import render, redirect

def restricted(request, level=0, standing=None, standing_level=0, allow_sudo=False):
	if allow_sudo:
		me = Users.fetch(id=request.session.get('meid'))
	else:
		me = getme(request)
	if not me:
		return redirect('/login{}'.format(request.path))
	if me.permission < (standing_level if standing and standing.stand(me) else level):
		me.perm_levels.append((8,"So-high-it-doesn't-exist"))
		context = {
			'me':me,
			'need':dict(me.perm_levels)[level]
		}
		return render(request, 'main/403.html', context, status=403)



# def cleandate(date):
# 	print date
# 	return datetime.now()

# from apps.program.managers import Courses

def gethist(ago=1):
	return range(getyear()-ago,1994,-1)

# Find User object for current logged-in user, without causing errors.
# me is always a User, never a Family, Student, or Teacher
from apps.people.managers import Users
def getme(request, both=False):
	if 'meid' in request.session:
		me = Users.fetch(id=request.session['meid'])
		if me:
			if me.permission >= 6 and 'sudo' in request.session:
				sudo = Users.fetch(id=request.session['sudo'])
				if sudo and sudo.permission < me.permission:
					return {'login':me,'sudo':sudo} if both else sudo
				else:
					request.session.pop('sudo')
					return {'login':me,'sudo':None} if both else me
			return {'login':me,'sudo':None} if both else me
		else:
			request.session.pop('meid')
			return {'login':None,'sudo':None} if both else None

