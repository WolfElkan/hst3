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

def index(request):
	if not Policies.fetch(year=getyear()):
		Policies.create(year=getyear())
	context = {
		'policies':Policies.all()
	}
	return render(request, 'radmin/policy/index.html', context)

def mod(request, **kwargs):
	if request.method == 'GET':
		return edit(request, **kwargs)
	elif request.method == 'POST':
		return update(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb", status=405)

def edit(request, **kwargs):
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

def update(request, **kwargs):
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

def show(request, **kwargs):
	bad = restricted(request,1)
	if bad:
		return bad
	policy = Policies.fetch(year=kwargs.get('year'))
	context = {
		'policy':policy
	}
	return render(request, 'radmin/policy/show.html', context)




