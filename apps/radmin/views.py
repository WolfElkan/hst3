from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices
from .managers import Policies

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts, equip
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase, cleanhex
from Utils.security import getme, getyear, restricted
from Utils.seshinit import seshinit, forminit

from datetime import datetime

def dashboard(request, **kwargs):
	bad = restricted(request,4)
	if bad:
		return bad
	context = {}
	return render(request, 'radmin/dashboard.html', context)

def newyear_year(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	if request.method == 'GET':
		return newyear_year_get(request, **kwargs)
	elif request.method == 'POST':
		return newyear_year_post(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def newyear_year_get(request, method=None):
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
			'courses': equip(CourseTrads.filter(e=True).order_by('order'), lambda trad: bool(Courses.filter(year=year,tradition=trad)), attr='already'),
		})
	elif request.GET:
		for key in request.GET:
			if request.GET[key] == 'on':
				Courses.create_by_id(key)
		return redirect('/admin/newyear/year/')
	return render(request, 'radmin/newyear/year.html', context)

def newyear_year_post(request, id, method=None):
	bad = restricted(request,5)
	if bad:
		return bad
	return redirect('/admin/newyear/year/'.format(newyear_year.id))

def policy_index(request):
	context = {
		'policies':Policies.all()
	}
	return render(request, 'radmin/policy/index.html', context)

def policy_edit(request, **kwargs):
	if request.method == 'GET':
		return policy_edit_get(request, **kwargs)
	elif request.method == 'POST':
		return policy_edit_post(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb", status=405)

def policy_edit_get(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	year = int(kwargs.get('year') or getyear())
	policy = Policies.fetch(year=year)
	if not policy:
		policy = Policies.fetch(year=year-1)
	context = {
		'current':policy.markdown,
		'year':year,
	}
	return render(request, 'radmin/policy/edit.html', context)

def policy_edit_post(request, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	policy = Policies.fetch(year=request.POST.get('year'))
	if policy:
		policy.markdown = request.POST.get('markdown')
		policy.save()
	else:
		policy = Policies.create(**copy(request.POST,['year','markdown']))
	return redirect('/admin/policy/show/{}'.format(policy.year))

def policy_show(request, **kwargs):
	bad = restricted(request,1)
	if bad:
		return bad
	policy = Policies.fetch(year=kwargs.get('year'))
	context = {
		'policy':policy
	}
	return render(request, 'radmin/policy/show.html', context)




