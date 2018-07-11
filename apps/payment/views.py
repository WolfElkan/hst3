from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from HST.settings import PAYPAL_BUSINESS_EMAIL, CURRENT_HOST

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from .managers import Invoices
from .models import PayPal
PayPals = PayPal.objects

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts, cleandate
from Utils.debug import pretty, divs
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase, cleanhex
from Utils.security import getme, getyear, gethist, restricted
from Utils.seshinit import seshinit, forminit

from datetime import datetime

def invoice_create(request, ref):
	me = getme(request)
	invoice = Invoices.create(family=me.owner)
	return redirect('/{}/invoice/{}'.format(ref,invoice.id))

def invoice_show(request, ref, id):
	# me = getme(request)
	invoice = Invoices.fetch(id=id)
	bad = restricted(request,5,invoice)
	if bad:
		return bad
	context = {
		'invoice': invoice,
		'ref'    : ref, # Note: There are two 'ref' variables here.  They mean different things.
		'email'  : PAYPAL_BUSINESS_EMAIL,
		'host'   : 'https://{}'.format(CURRENT_HOST),
		'waiting': invoice.status == 'N' and request.GET.get('ref') == 'paypal',
	}
	return render(request, 'invoice.html', context)

def invoice_index(request, family_id):
	family = Families.fetch(id=family_id)
	bad = restricted(request,5,family)
	if bad:
		return bad
	invoices = Invoices.filter(family=family)
	context = {
		'hist' : collect(gethist(0), lambda year: {'year':year, 'invoices':Invoices.filter(year=year,family=family)})
	}
	return render(request, 'invoice_index.html', context)

@csrf_exempt
def paypal_ipn(request):
	paypal_url = 'https://www.paypal.com/cgi-bin/webscr'
	if request.POST.get('test_ipn'):
		paypal_url = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
	invoice = Invoices.fetch(id=request.POST.get('invoice'))
	paypal = PayPals.create(request.POST)
	if invoice.confirm(paypal):
		verified = paypal.verify(paypal_url)
		if verified:
			invoice.pay(paypal)
	return HttpResponse('')
