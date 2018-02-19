from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments, Auditions
from .managers import Invoices

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase
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
