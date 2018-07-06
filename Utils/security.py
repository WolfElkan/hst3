from django.shortcuts import render, redirect

def restricted(request, level=0, standing=None, standing_level=0):
	me = getme(request)
	if not me:
		return redirect('/login{}'.format(request.path))
	if me.permission < (standing_level if standing and standing.stand(me) else level):
		me.perm_levels.append((8,'Eight'))
		context = {
			'me':me,
			'need':dict(me.perm_levels)[level]
		}
		return render(request, 'main/403.html', context, status=403)


from datetime import datetime

def cleandate(date):
	print date
	return datetime.now()

# Find User object for current logged-in user, without causing errors.
# me is always a User, never a Family, Student, or Teacher

from apps.program.managers import Courses

def gethist(ago=1):
	years = []
	for year in range(getyear()-ago,1994,-1):
		if Courses.filter(year=year):
			years.append(year)
	return years
def getyear():
	# if DEV:
	# 	return 2017
	now = datetime.now()
	return now.year + (0 if now.month < 5 else 1)

from apps.people.managers import Users
def getme(request):
	if 'meid' in request.session:
		me = Users.fetch(id=request.session['meid'])
		if me:
			return me
		else:
			request.session.pop('meid')
