from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers  import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices, PayPals
from apps.radmin.managers  import Policies

from Utils.custom_fields import Bcrypt, PhoneNumber, DayOfWeek
from Utils.data  import collect, copy, copyatts, Each, equip, find, find_all, sub, cleandate
from Utils.debug import pretty, pdir, divs
from Utils.fjson import FriendlyEncoder
from Utils.misc  import namecase, cleanhex, safe_delete
from Utils.security import getme, getyear, gethist, restricted
from Utils.seshinit import seshinit, forminit
from Utils.snippets import order_coursetrads, make

import datetime
import re

def lookup_student(obj):
	first = namecase(obj['first'])
	last = namecase(obj['last'])
	student = Students.fetch(first=first,family__last=last)
	if not student:
		student = Students.fetch(alt_first=first,family__last=last)
	return student

def reset(user):
	Enrollments.filter(student__family=user.owner,course__year=getyear()).delete()

def add_hids(**kwargs):
	for family in Families.filter(**kwargs):
		match = re.match(r'^([a-z])[^a-z]*([a-z])[^a-z]*([a-z])',family.last,flags=re.I)
		las = ''.join(match.groups()).upper()
		if not family.hid:
			# print las
			clash3 = Families.filter(hid__startswith=las)
			num = 1
			for x in clash3:
				clashnum = int(x.hid[3:5])
				if clashnum >= num:
					num = clashnum + 1
			fhid = '{}{:0>2}'.format(las,num)
			if not Families.filter(hid=hid):
				family.hid = fhid
				family.save()
		print family.hid, family
		if family.father and not family.father.hid:
			family.father.hid = '{}{:0>2}'.format(las,'FA')
		if family.mother and not family.mother.hid:
			family.mother.hid = '{}{:0>2}'.format(las,'MO')
		for student in family.children:
			if student.hid:
				continue
			num = student.birthday.year
			while True: # First time I've ever needed to use a do-while loop, and it's Python. Sigh.
				num %= 100
				shid = '{}{:0>2}'.format(family.hid,num)
				num += 1
				if not Students.filter(hid=shid):
					break
			student.hid = shid
			student.save()
			print student.hid, student

def hot(request):
	bad = restricted(request,7)
	if bad:
		return bad
	me = getme(request)
	seshinit(request,'command')
	context = {
		'command': request.session['command'],
		'session': divs(request.session.__dict__['_session_cache']),
		'request': divs(request.__dict__.copy()),
		'get': divs(request.GET.__dict__.copy()),
		'post': divs(request.POST.__dict__.copy()),
	}
	return render(request, 'main/hot.html', context)

def run(request):
	bad = restricted(request,7)
	if bad:
		return bad
	me = getme(request)
	command = request.POST['command']
	request.session['command'] = command
	exec(command)
	return redirect ('/hot')

def clear(request):
	bad = restricted(request,7)
	if bad:
		return bad
	request.session.clear()
	return redirect ('/')