from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
from Utils.hacks import copy, getme, seshinit, forminit, copyatts, pretty, pdir, sub, collect
import re
from .fields import FIELDS
from .widgets import MODELS
from trace import TRACE

def home(request):
	if TRACE:
		print '@ rest.views.home'
	context = {}
	return render(request, 'rest/home.html', context)

def index(request, model):
	if TRACE:
		print '@ rest.views.index'
	columns = []
	for ftp in FIELDS[model]:
		field = ftp['field']
		columns.append(field)
	query = collect(request.GET, str)
	qset = MODELS[model].filter(**query)
	# qset.order_by('-updated_at')
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
	if TRACE:
		print '@ rest.views.new'
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
	if TRACE:
		print '@ rest.views.create'
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
	if TRACE:
		print '@ rest.views.show'
	return show_or_edit(request, model, id, False)

def edit(request, model, id):
	if TRACE:
		print '@ rest.views.edit'
	return show_or_edit(request, model, id, True)

def show_or_edit(request, model, id, isEdit):
	if TRACE:
		print '@ rest.views.show_or_edit'
	manager = MODELS[model]
	thing = manager.get(id=id)
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
			'field':template.field if template.field else field, 
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
	if TRACE:
		print '@ rest.views.update'
	manager = MODELS[model]
	thing = manager.get(id=id)
	for ftp in FIELDS[model]:
		template = ftp['template']
		field = ftp['field']
		value = request.POST[field] if field in request.POST else template.default
		thing = template.set(thing, field, request.POST, True)
	thing.save()
	return redirect("/rest/index/coursetrad?e=True")
	return redirect("/rest/show/{}/{}".format(model, thing.id))

def delete(request, model, id):
	if TRACE:
		print '@ rest.views.delete'
	manager = MODELS[model]
	thing = manager.get(id=id)
	thing.delete()
	return redirect('/reports/students/2017/')