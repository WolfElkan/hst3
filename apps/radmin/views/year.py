from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices
from ..managers import Policies

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts, equip
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase, cleanhex
from Utils.security import getme, getyear, restricted
from Utils.seshinit import seshinit, forminit

from datetime import datetime

def bib(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	if request.method == 'GET':
		return new(request, **kwargs)
	elif request.method == 'POST':
		return create(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def new(request, method=None):
	bad = restricted(request,5)
	if bad:
		return bad
	context = {
		'year': getyear(),
	}
	if 'year' in request.GET:
		year = request.GET['year']
		context.update({
			'year'   : year,
			'year2'  : year[-2:],
			'courses': equip(CourseTrads.filter(alias=None, r=True).order_by('order'), lambda trad: bool(Courses.filter(year=year,tradition=trad)), attr='already'),
		})
	elif request.GET:
		for key in request.GET:
			if request.GET[key] == 'on':
				Courses.create_by_id(key)
		return redirect('/admin/year/')
	return render(request, 'radmin/newyear/year.html', context)

def create(request, id, method=None):
	bad = restricted(request,5)
	if bad:
		return bad
	return redirect('/admin/year/'.format(year.id))