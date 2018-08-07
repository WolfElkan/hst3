from django.shortcuts import render, redirect, HttpResponse
from apps.program.managers import Enrollments
from .search import search_query

from Utils.data import collect, sub
from Utils.security import restricted

from datetime import datetime
import re

from ..fields import FIELDS
from ..widgets import MODELS

def home(request):
	bad = restricted(request)
	if bad:
		return bad
	context = {}
	return render(request, 'rest/home.html', context)

def index(request, model):
	bad = restricted(request)
	if bad:
		return bad
	columns = []
	for ftp in FIELDS[model]:
		field = ftp['field']
		columns.append(field)
	query = collect(request.GET, str)
	order_by = query.get('order_by')
	if order_by:
		query.pop('order_by')
	limit  = query.get('limit')
	offset = query.get('offset')
	limit  = int(limit)  if limit  else None
	offset = int(offset) if offset else None
	if limit and offset:
		query.pop('limit')
		query.pop('offset')
		qset = MODELS[model].filter(**query)[offset:offset+limit]
	elif limit:
		query.pop('limit')
		qset = MODELS[model].filter(**query)[:limit]
	elif offset:
		query.pop('offset')
		qset = MODELS[model].filter(**query)[offset:]
	else:
		qset = MODELS[model].filter(**query)
	if order_by:
		qset = qset.order_by(order_by)
	display = []
	for thing in qset:
		dthing = ['<a href="/rest/show/{}/{}">{}</a>'.format(model, thing.id, thing.id)]
		for ftp in FIELDS[model]:
			field = ftp['field']
			value = thing.__getattribute__(field)
			template = ftp['template']
			value = value if value else template.default
			dthing.append(template.static(field,value))
		display.append(dthing)
	context = {
		'columns' : columns,
		'display' : display,
		'model'   : model,
		'Model'   : sub(model,{'coursetrad':'Course Tradition'}).title()
	}
	return render(request, 'rest/index.html', context)

def new(request, model, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	if 'foreign_model' in kwargs:
		old_model = model
		model = kwargs['foreign_model']
	else:
		old_model = None
	manager = MODELS[model]
	neutral = sub(model,{'mother':'parent','father':'parent'})
	tempset = FIELDS[neutral]
	display = []
	for ftp in tempset:
		field = ftp['field']
		template = ftp['template']
		value = template.default
		if str(model) == 'mother' and field == 'sex':
			value = 'F'
		if str(field) == str(old_model):
			value = MODELS[old_model].get(id=kwargs['id'])
		# print kwargs
		value = template.widget(field,value)
		display.append({
			'field':template.field if template.field else field, 
			'input':value
		})
	context = {
		'display' : display,
		'model'   : model,
		'neutral' : neutral,
		'Model'   : sub(neutral,{'coursetrad':'Course Tradition'}).title()
	}
	return render(request, 'rest/new.html', context)

def create(request, model, **kwargs):
	bad = restricted(request,5)
	if bad:
		return bad
	if 'foreign_model' in kwargs:
		old_model = model
		model = kwargs['foreign_model']
	else:
		old_model = None
	manager = MODELS[model]
	thing = {}
	for ftp in FIELDS[model]:
		template = ftp['template']
		field = ftp['field']
		value = request.POST[field] if field in request.POST else template.default
		thing = template.set(thing, field, request.POST, False)
	thing = manager.create(**thing)
	if old_model:
		old = MODELS[old_model].fetch(id=kwargs['id'])
		if old and hasattr(old, model):
			old.__setattr__(model, thing)
			old.save()
	return redirect('/rest/show/{}/{}/'.format(old_model,kwargs['id']) if old_model else '/rest/show/{}/{}/'.format(thing.rest_model,thing.id))

def show(request, model, id):
	return show_or_edit(request, model, id, False)

def edit(request, model, id):
	return show_or_edit(request, model, id, True)

def show_or_edit(request, model, id, isEdit):
	manager = MODELS[model]
	thing = manager.get(id=id)
	bad = restricted(request,5) if isEdit else restricted(request,4,thing,1)
	if bad:
		return bad
	method = request.GET.get('method')
	if method:
		call = thing.__getattribute__(method)
		if hasattr(call,'__call__'):
			call()
		return redirect('/rest/{}/{}/{}/'.format('edit' if isEdit else 'show', model, id))
	tempset = FIELDS[model]
	display = []
	for ftp in tempset:
		field = ftp['field']
		value = thing.__getattribute__(field)
		value = value if value else ''
		template = ftp['template']
		if isEdit:
			value = template.widget(field,value)
		else:
			value = template.static(field,value)
		if value == None:
			value = ''
		display.append({
			'field':template.field if hasattr(template,'field') and template.field else field, 
			'input':value
		})
	context = {
		'thing'   : thing,
		'display' : display,
		'model'   : model,
		'Model'   : sub(model,{'coursetrad':'Course Tradition'}).title()
	}
	return render(request, 'rest/edit.html' if isEdit else 'rest/show.html', context)

def update(request, model, id):
	bad = restricted(request,5)
	if bad:
		return bad
	manager = MODELS[model]
	thing = manager.get(id=id)
	for ftp in FIELDS[model]:
		template = ftp['template']
		field = ftp['field']
		value = request.POST[field] if field in request.POST else template.default
		thing = template.set(thing, field, request.POST, True)
	thing.save()
	# return redirect("/rest/index/coursetrad?e=True")
	return redirect("/rest/show/{}/{}".format(model, thing.id))

def delete(request, model, id):
	bad = restricted(request,5)
	if bad:
		return bad
	manager = MODELS[model]
	thing = manager.get(id=id)
	thing.delete()
	return redirect('/rest/')

def search(request, **kwargs):
	query = request.GET.get('query')
	if ' in ' in query:
		match = re.match(r'(?P<student>.*?) in (?P<course>.*)',query).groupdict()
		students = search_query(match['student'], all_tables=False, student=True)
		courses  = search_query(match['course'],  all_tables=False, course=True)
		results  = Enrollments.filter(student__in=students,course__in=courses)
	else:
		results = search_query(query)
	context = {
		'results':results,
		'query':query,
	}
	return render(request, 'rest/search_results.html', context)

