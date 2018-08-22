from django.shortcuts import render, redirect, HttpResponse

from Utils.security import restricted
from Utils.data import sub as substitute
from Utils.data import collect

from ..fields import FIELDS
from ..widgets import MODELS

from ..search import search_query

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
		'Model'   : substitute(model,{'coursetrad':'Course Tradition'}).title()
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

def move_all(request, model, old_id, new_id):
	field = request.GET.get('field')
	manager = MODELS[model]
	reflex = request.GET.get('reflex')
	field = request.GET.get('field')
	old = manager.get(id=old_id)
	if reflex[-3:] == '_id':
		for sub in old.__getattribute__(field):
			sub.__setattr__(reflex,new_id)
			sub.save()
	else:
		new = manager.get(id=new_id)
		for sub in old.__getattribute__(field):
			sub.__setattr__(reflex,new)
			sub.save()
	return redirect('/rest/merge/{}/{}/{}/'.format(model,old_id,new_id))

def sub_merge(request, model, old_id, new_id):
	return sub(request, model, old_id, new_id, 'rest/sub_merge.html')

def sub_move(request, model, old_id, new_id):
	return sub(request, model, old_id, new_id, 'rest/sub_move.html')

def sub(request, model, old_id, new_id, template):
	field = request.GET.get('field')
	reflex = request.GET.get('reflex')
	manager = MODELS[model]
	old = manager.get(id=old_id)
	new = manager.get(id=new_id)
	old_subs = old.__getattribute__(field)
	new_subs = new.__getattribute__(field)
	context = {
		'old':old,
		'new':new,
		'old_subs':old_subs,
		'new_subs':new_subs,
		'field':field,
		'reflex':reflex,
	}
	return render(request, template, context)
	# return redirect('/rest/merge/{}/{}/{}/'.format(model,old_id,new_id))

def sub_transfer(request, model, old_id, new_id):
	fargs = collect(request.GET,str)
	manager = MODELS[fargs['model']]
	thing = manager.get(id=fargs['sub_id'])
	dest = fargs['dest']
	if fargs['reflex'][-3:] != '_id':
		dest_manager = MODELS[model]
		dest = dest_manager.get(id=fargs['dest'])
	thing.__setattr__(fargs['reflex'],dest)
	thing.save()
	return redirect('/rest/merge/{}/{}/{}/sub_move/?field={field}&reflex={reflex}'.format(model,old_id,new_id,**fargs))

def sub_delete(request, model, old_id, new_id):
	fargs = collect(request.GET,str)
	manager = MODELS[fargs['model']]
	thing = manager.get(id=fargs['sub_id'])
	thing.delete()
	return redirect('/rest/merge/{}/{}/{}/sub_move/?field={field}&reflex={reflex}'.format(model,old_id,new_id,**fargs))

def new_merge(request):
	if 'query' in request.GET:
		return merge_search(request)
	elif 'model' not in request.GET:
		return render(request, 'rest/merge_search.html')
	fargs = collect(request.GET,str)
	return redirect('/rest/merge/{model}/{old_id}/{new_id}/'.format(**fargs))

def merge_search(request):
	model = request.GET.get('model')
	kwargs = {model:True}
	context = {
		'model'   : model,
		'Model'   : substitute(model,{'coursetrad':'Course Tradition'}).title(),
		'results' : search_query(request.GET['query'], all_tables=False, **kwargs),
	}
	return render(request, 'rest/merge_results.html', context)

def sub_exit(request, model, old_id, new_id):
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
