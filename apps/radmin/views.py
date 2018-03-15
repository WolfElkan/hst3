from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts, equip
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase, cleanhex
from Utils.security import authorized, getme, getyear
from Utils.seshinit import seshinit, forminit

from datetime import datetime

# Create your views here.

def dashboard(request, **kwargs):
	context = {}
	return render(request, 'radmin/dashboard.html', context)

def invoice(request, **kwargs):
	if 'invoice_code' not in request.session:
		return redirect('/')
	invoice = Invoices.fetch(id=kwargs['id'])
	if cleanhex(invoice.code) != cleanhex(request.session['invoice_code']):
		return redirect('/')
	if request.method == 'GET':
		return invoice_get(request, **kwargs)
	elif request.method == 'POST':
		return invoice_post(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def invoice_get(request, id, method=None):
	invoice = Invoices.fetch(id=id)
	context = {
		'invoice':Invoices.fetch(id=id),
		'method' :method,
	}
	if invoice.status == 'N':
		return render(request, 'radmin/unpaid_invoice.html', context)
	else:
		return render(request, 'radmin/static_invoice.html', context)

def invoice_post(request, id, method=None):
	invoice = Invoices.fetch(id=id)
	invoice.payment_id = request.POST['payment_id']
	invoice.check_date = request.POST['check_date']
	invoice.memo       = request.POST['memo']
	invoice.method = method
	invoice.status = 'P'
	invoice.save()
	return redirect('/admin/invoice/{}/'.format(invoice.id))

def invoice_deposit(request, id):
	invoice = Invoices.fetch(id=id)
	invoice.depos_date = datetime.now()
	invoice.save()
	return redirect('/admin/invoice/{}/'.format(invoice.id))

def invoice_clear(request, id):
	invoice = Invoices.fetch(id=id)
	if invoice.depos_date:
		invoice.clear_date = datetime.now()
		invoice.save()
		for enrollment in invoice.items:
			enrollment.status = "enrolled"
			enrollment.save()
	return redirect('/admin/invoice/{}/'.format(invoice.id))

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


