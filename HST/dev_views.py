from django.shortcuts import render, redirect, HttpResponse
from Utils.custom_fields import Bcrypt, PhoneNumber
from datetime import datetime
from Utils.hacks import copy, getme, seshinit, first, pretty, pdir

from apps.main.models import Family, Address, Parent, User, Student
Addresses = Address.objects
Families  = Family.objects
Parents   = Parent.objects
Students  = Student.objects
Users     = User.objects

from apps.program.models import Venue, CourseTrad, Course, Enrollment
Venues      = Venue.objects
CourseTrads = CourseTrad.objects
Courses     = Course.objects
Enrollments = Enrollment.objects

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
	# request.session.clear()
	print '\n\n'+' '*34+'THE RADIANCE OF A THOUSAND SUNS'+'\n\n'
	return redirect ('/hot')

def clear(request):
	request.session.clear()
	return redirect ('/hot')