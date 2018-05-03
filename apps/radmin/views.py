from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts, equip
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase, cleanhex
from Utils.security import getme, getyear
from Utils.seshinit import seshinit, forminit

from datetime import datetime

def dashboard(request, **kwargs):
	context = {}
	return render(request, 'radmin/dashboard.html', context)

def newyear_year(request, **kwargs):
	if request.method == 'GET':
		return newyear_year_get(request, **kwargs)
	elif request.method == 'POST':
		return newyear_year_post(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def newyear_year_get(request, method=None):
	context = {
		'year': getyear(),
	}
	if 'year' in request.GET:
		year = request.GET['year']
		context.update({
			'year'   : year,
			'year2'  : year[-2:],
			'courses': equip(CourseTrads.filter(e=True).order_by('order'), lambda trad: bool(Courses.filter(year=year,tradition=trad)), attr='already'),
		})
	elif request.GET:
		for key in request.GET:
			if request.GET[key] == 'on':
				Courses.create_by_id(key)
		return redirect('/admin/newyear/year/')
	return render(request, 'radmin/newyear/year.html', context)

def newyear_year_post(request, id, method=None):
	return redirect('/admin/newyear/year/'.format(newyear_year.id))


