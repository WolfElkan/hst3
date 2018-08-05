from django.shortcuts import render, redirect, HttpResponse

from Utils.security import restricted
from Utils.data import sub

from ..fields import FIELDS
from ..widgets import MODELS

def records(request, model, old_id, new_id):
	bad = restricted(request,5)
	if bad:
		return bad
	manager = MODELS[model]
	old = manager.get(id=old_id)
	new = manager.get(id=new_id)
	tempset = FIELDS[model]
	display = []
	for ftp in tempset:

		field = ftp['field']
		template = ftp['template']

		old_value = old.__getattribute__(field)
		old_value = old_value if old_value else ''
		old_value = template.static(field,old_value)
		if old_value == None:
			old_value = ''

		new_value = new.__getattribute__(field)
		new_value = new_value if new_value else ''
		new_value = template.static(field,new_value)
		if new_value == None:
			new_value = ''

		display.append({
			'field':template.field if template.field else field, 
			'old':old_value,
			'new':new_value,
			'merge':template.merge(old,new) if hasattr(template,'merge') else ''
		})
	context = {
		'old'     : old,
		'new'     : new,
		'display' : display,
		'model'   : model,
		'Model'   : sub(model,{'coursetrad':'Course Tradition'}).title()
	}
	return render(request, 'rest/merge.html', context)

def swap(request, model, old_id, new_id):
	bad = restricted(request,5)
	if bad:
		return bad
	field = request.GET.get('field')
	manager = MODELS[model]
	old = manager.get(id=old_id)
	new = manager.get(id=new_id)

	right = old.__getattribute__(field)
	left  = new.__getattribute__(field)
	old.__setattr__(field, left)
	new.__setattr__(field, right)
	old.save()
	new.save()
	return redirect('/rest/merge/{}/{}/{}/'.format(model,old_id,new_id))

def copy(request, model, old_id, new_id):
	bad = restricted(request,5)
	if bad:
		return bad
	field = request.GET.get('field')
	manager = MODELS[model]
	old = manager.get(id=old_id)
	new = manager.get(id=new_id)

	new.__setattr__(field, old.__getattribute__(field))
	new.save()
	return redirect('/rest/merge/{}/{}/{}/'.format(model,old_id,new_id))
	
def transfer(request, model, old_id, new_id):
	bad = restricted(request,5)
	if bad:
		return bad
	field = request.GET.get('field')
	blank = request.GET.get('blank')
	manager = MODELS[model]
	old = manager.get(id=old_id)
	new = manager.get(id=new_id)

	mid = old.__getattribute__(field)
	old.__setattr__(field, blank)
	old.save()
	if hasattr(mid,'rest_model') and mid.rest_model == 'parent' and old.rest_model == 'family':
		mid.family_id = new.id
		mid.save()
	new.__setattr__(field, mid)
	new.save()
	return redirect('/rest/merge/{}/{}/{}/'.format(model,old_id,new_id))

def delete(request, model, old_id, new_id):
	bad = restricted(request,6)
	if bad:
		return bad
	else:
		manager = MODELS[model]
		old = manager.get(id=old_id)
		old.delete()
		return redirect('/rest/show/{}/{}/'.format(model,new_id))
