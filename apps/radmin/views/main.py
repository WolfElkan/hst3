from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments
from apps.payment.managers import Invoices
from ..managers import Policies

from Utils.custom_fields import Bcrypt, PhoneNumber
from Utils.data  import collect, copy, copyatts, equip, Each
from Utils.fjson import FriendlyEncoder, json
from Utils.misc  import namecase, cleanhex
from Utils.security import getme, getyear, restricted
from Utils.seshinit import seshinit, forminit

from datetime import datetime

def dashboard(request, **kwargs):
	bad = restricted(request,4)
	if bad:
		return bad
	context = {'year':getyear()}
	return render(request, 'radmin/dashboard.html', context)

K = {
	'SB':{'10':'KB', '15':'KD','20':'KE'},
	'SC':{'10':'KC', '15':'KM','20':'KN'},
	'SG':{'10':'KG','15':'KS','20':'KW'},
	'SH':{'10':'KH','15':'KT','20':'KX'},
	'SJ':{'10':'KJ','15':'KU','20':'KY'},
	'SR':{'10':'KR','15':'KV','20':'KZ'},
}

def deferred(request, **kwargs):
	families = Families.filter(
		children__enrollment__course__year=getyear(),
		children__enrollment__course__tradition__id__startswith='K',
		children__enrollment__status='deferred'
	).distinct().order_by('last','name_num').prefetch_related('children__enrollment')
	agg = []
	for family in families:
		row = {}
		for show in K:
			tix = 0
			for qty in K[show]:
				tix += sum(Each(family.children).enrollment.filter(status='deferred',course__tradition__id=K[show][qty]).count()) * int(qty)
			row[show] = tix
		row['amount'] = sum(row.values()) * 10.00
		row['o'] = family
		agg.append(row)
	context = {
		'families':agg
	}
	for show_id in K:
		total = 0
		context[show_id] = {}
		for status in ['enrolled','invoiced','deferred']:
			new = get_stat(show_id, status)
			total += new['total']
			context[show_id][status] = new
		new = get_stat(show_id,['need_pay','maydefer'])
		context[show_id]['in_cart'] = get_stat(show_id,['need_pay','maydefer'])
		context[show_id]['total'] = total + new['total']
	return render(request, 'radmin/deferred.html', context)

def get_stat(show_id, status):
	if type(status) is not list:
		status = [status]
	x  = len(Enrollments.filter(course__year=getyear(),course__tradition=K[show_id]['10'],status__in=status))
	xv = len(Enrollments.filter(course__year=getyear(),course__tradition=K[show_id]['15'],status__in=status))
	xx = len(Enrollments.filter(course__year=getyear(),course__tradition=K[show_id]['20'],status__in=status))
	return {
		'10':x,
		'15':xv,
		'20':xx,
		'total': (x * 10) + (xv * 15) + (xx * 20)
	}

def rescind(request, **kwargs):
	for enrollment in Enrollments.filter(status__in=['deferred','maydefer']):
		enrollment.status = 'need_pay'
		enrollment.save()
	return redirect('/admin/deferred/')


def sudochangepassword(request, **kwargs):
	both = getme(request, both=True)
	if 'them_id' in kwargs:
		them = Users.fetch(id=kwargs['them_id'])
	else:
		them = both['sudo']
	me = both['login']
	if not me:
		return redirect('/')
	bad = restricted(request,6,them,allow_sudo=True)
	if bad:
		return bad 
	user = copy(request.POST,['password','pw_confm'])
	valid = Users.isValid(user, partial=True)
	if not valid:
		request.session['e'] = Users.errors(user, partial=True)
	correct = me.password(request.POST['current_pw'])
	if not correct:
		request.session['e']['current_pw'] = "Your password is incorrect"
	if correct and valid:
		if not them:
			return HttpResponse('User not found.', status=404)
		request.session['e'] = {}
		them.password = str(request.POST['password'])
		them.save()
	return redirect(request.META['HTTP_REFERER'])

def sudo(request):
	sudo_id = request.GET.get('sudo')
	if sudo_id:
		request.session['sudo'] = int(sudo_id)
		return redirect('/sudo/')
	else:
		context = {
			'users':Users.all(),
			'current_sudo':Users.fetch(id=request.session.get('sudo')),
			'current_me':Users.fetch(id=request.session.get('meid')),
			'me':getme(request),
		}
		return render(request, 'radmin/sudo.html', context)

def sudo_exit(request):
	request.session.pop('sudo')
	return redirect('/sudo/')

def sudo_invoice(request, **kwargs):
	invoice = Invoices.fetch(id=kwargs.get('id'))
	bad = restricted(request,5,standing=invoice)
	if bad:
		return bad
	action = request.GET.get('action')
	method = request.GET.get('method')
	if invoice and action == 'pay' and method in Each(Invoices.model.method_choices).lower():
		invoice.status = 'P'
		invoice.method = method
		for item in invoice.items:
			item.pay()
		invoice.save()
	print Each(Invoices.model.method_choices).lower()
	return redirect('/{ref}/invoice/{id}/'.format(**kwargs))


