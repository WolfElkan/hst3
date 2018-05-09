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

def dashboard(request, **kwargs):
	bad = restricted(request,4)
	if bad:
		return bad
	context = {}
	return render(request, 'radmin/dashboard.html', context)