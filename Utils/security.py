def authorized(request, level=0):
	me = getme(request)
	if me:
		return me.permission >= level

# Find User object for current logged-in user, without causing errors.
# me is always a User, never a Family, Student, or Teacher
from apps.people.managers import Users
def getme(request):
	if 'meid' in request.session:
		me = Users.fetch(id=request.session['meid'])
		if me:
			return me
		else:
			request.session.pop('meid')

from datetime import datetime
from trace import DEV

def getyear():
	if DEV:
		return 2019
	now = datetime.now()
	return now.year + (0 if now.month < 5 else 1)

from apps.program.managers import Courses
def gethist():
	years = []
	for year in range(getyear()-1,1994,-1):
		if Courses.filter(year=year):
			years.append(year)
	return years
