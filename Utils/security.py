from trace import DEV
# def authorized(request, level=0):
# 	me = getme(request)
# 	if me:
# 		return me.permission >= level

from django.shortcuts import render

# def verify_standing(me, standing):
# 	if not standing:
# 		return False
# 	person = me.owner
# 	if person.rest_model == 'family':
# 		family = standing_family(standing)
# 		return family and person.id == family.id
# 	elif person.rest_model == 'student':
# 		student = standing_student(standing)
# 		return student and person.id == student.id
# 	elif standing.rest_model == 'course':
# 		return False
# 	else:
# 		return False

# def standing_family(standing):
# 	if standing.rest_model == 'user' and standing.owner.rest_model == 'family':
# 		return standing.owner
# 	elif standing.rest_model == 'family':
# 		return standing
# 	elif standing.rest_model in ['student','parent','invoice','paypal']:
# 		return standing.family
# 	elif standing.rest_model == 'enrollment':
# 		return standing.student.family

# def standing_student(standing):
# 	if standing.rest_model == 'user' and standing.owner.rest_model == 'student':
# 		return standing.owner
# 	elif standing.rest_model == 'student':
# 		return standing
# 	elif standing.rest_model == 'enrollment':
# 		return standing.student

def restricted(request, level=0, standing=None):
	me = getme(request)
	if standing and standing.stand(me):
		return False
	if not me or me.permission < level:
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
	if DEV:
		return 2019
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
