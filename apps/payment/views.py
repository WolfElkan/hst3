from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from .managers import Invoices

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase, cleanhex
from Utils.security import authorized, getme, getyear
from Utils.seshinit import seshinit, forminit

# Create your views here.

def invoice_create(request):
	me = getme(request)
	invoice = Invoices.create(family=me.owner)
	return redirect('/register/invoice/{}'.format(invoice.id))

def invoice_show(request, id):
	me = getme(request)
	invoice = Invoices.fetch(id=id)
	context = {
		'family' : me.owner,
		'invoice': invoice,
	}
	return render(request, 'invoice.html', context)

def find_invoice(request, **kwargs):
	forminit(request,'invoice',['id','code'])
	if request.method == 'GET':
		return find_invoice_get(request, **kwargs)
	elif request.method == 'POST':
		return find_invoice_post(request, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def find_invoice_get(request):
	context = copy(request.session,'pe')
	return render(request, 'find_invoice.html', context)

def find_invoice_post(request):
	query = {
		'id'  : request.POST['invoice_id'],
		'code': request.POST['invoice_code'],
	}
	if Invoices.isValid(query):
		invoice = Invoices.fetch(id=query['id'])
	else:
		request.session['e'] = {'invoice':Invoices.errors(query)}
		request.session['p'] = {'invoice':query.copy()}
		return redirect('/admin/invoice/find/')
	if not invoice:
		request.session['e'] = {'invoice':{'id':'Invoice not found.'}}
		request.session['p'] = {'invoice':query.copy()}
		return redirect('/admin/invoice/find/')
	elif cleanhex(invoice.code) != cleanhex(query['code']):
		request.session['e'] = {'invoice':{'code':'Invoice code incorrect.'}}
		request.session['p'] = {'invoice':query.copy()}
		return redirect('/admin/invoice/find/')
	else:
		request.session['invoice_code'] = cleanhex(query['code'])
		return redirect('/admin/invoice/{}/'.format(invoice.id))

