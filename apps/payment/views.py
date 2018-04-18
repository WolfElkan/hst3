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
from Utils.security import authorized, getme, getyear, gethist
from Utils.seshinit import seshinit, forminit

# from urllib import urlencode
# from urllib2 import urlopen

from datetime import datetime

def invoice_create(request):
	me = getme(request)
	invoice = Invoices.create(family=me.owner)
	return redirect('/register/invoice/{}'.format(invoice.id))

def invoice_show(request, id):
	# me = getme(request)
	invoice = Invoices.fetch(id=id)
	context = {
		'invoice': invoice,
		'email'  : PAYPAL_BUSINESS_EMAIL,
		# 'host'   : "http://{REMOTE_ADDR}:{SERVER_PORT}".format(**request.META),
		'host'   : 'https://{}'.format(CURRENT_HOST)
	}
	return render(request, 'invoice.html', context)

def invoice_index(request, family_id):
	family = Families.fetch(id=family_id)
	invoices = Invoices.filter(family=family)
	context = {
		'hist' : collect(gethist(0), lambda year: {'year':year, 'invoices':Invoices.filter(year=year,family=family)})
	}
	return render(request, 'invoice_index.html', context)

def paypal_pay(request, id):
	invoice = Invoices.fetch(id=id)
	paypal_data = {
		'business'      : PAYPAL_BUSINESS_EMAIL,
		'cmd'           : '_xclick',
		'item_name'     : 'HST Tuition Invoice #{}'.format(invoice.id),
		'amount'        : invoice.amount,
		'currency_code' : 'USD',
		'invoice'       : invoice.id,
		'notify_url'    : '{}/register/invoice/{}/success?uuid={}'.format(request.environ['HTTP_HOST'],invoice.id,invoice.code),
		'cancel_return' : '{}/register/invoice/{}/cancel?uuid={}'.format(request.environ['HTTP_HOST'],invoice.id,invoice.code),
		'return'        : '{}/register/invoice/{}/success?uuid={}'.format(request.environ['HTTP_HOST'],invoice.id,invoice.code),
	}
	post_data = paypal_data.items()
	result = urlopen("https://www.paypal.com/cgi-bin/webscr",urlencode(post_data))
	yo = result.read()
	return HttpResponse(yo)

@csrf_exempt
def paypal_ipn(request, csrf):

	print '*'*100

	paypal_url = 'https://www.paypal.com/cgi-bin/webscr'
	if request.POST.get('test_ipn'):
		paypal_url = 'https://www.sandbox.paypal.com/cgi-bin/webscr'

	invoice = Invoices.fetch(id=request.POST.get('invoice'))
	csrf_safe = bool(invoice) and cleanhex(csrf) == cleanhex(invoice.csrf)

	paypal = PayPals.create(request.POST, csrf_safe)

	verified = paypal.verify(paypal_url)
	
	if csrf_safe and verified and request.POST.get('payment_status') == 'Completed':
		invoice.pay(paypal)
	return HttpResponse('')
