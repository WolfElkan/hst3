from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices

from Utils.custom_fields import Bcrypt, PhoneNumber, DayOfWeek
from Utils.data  import collect, copy, copyatts, Each, equip, find, find_all, sub
from Utils.debug import pretty, pdir
from Utils.fjson import FriendlyEncoder
from Utils.misc  import namecase, safe_delete
from Utils.security import authorized, getme, getyear
from Utils.seshinit import seshinit, forminit
from Utils.snippets import order_coursetrads

from datetime import datetime
import re

def check_en(student, course):
	print '{} is {}eligible for {}'.format(student,'' if student.eligible(course) else 'not ',course)

def check_aud(student, course):
	print '{} may {}audition for {}'.format(student,'' if student.audible(course) else 'not ',course)

def hot(request):
	me = getme(request)
	seshinit(request,'command')
	context = {
		'command': request.session['command'],
		# 'session': pretty(request.session.dict)
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
	Courses.all().delete()
	# request.session.clear()
	print '\n\n'+' '*34+'THE RADIANCE OF A THOUSAND SUNS'+'\n\n'
	return redirect ('/hot')

def clear(request):
	request.session.clear()
	return redirect ('/hot')