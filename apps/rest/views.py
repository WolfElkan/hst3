from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
from Utils.hacks import copy, getme, seshinit, forminit, first, copyatts, pretty, pdir, metastr, sub
import re
from .fields import FIELDS
from .widgets import MODELS

def home(request):
	context = {}
	return render(request, 'rest/home.html', context)

def index(request, model):
	columns = []
	for ftp in FIELDS[model]:
		field = ftp['field']
		columns.append(field)
	query = metastr(request.GET)
	qset = MODELS[model].filter(**query).order_by('-id')
	display = []
	for thing in qset:
		dthing = ['<a href="/rest/show/{}/{}">{}</a>'.format(model, thing.id, thing.id)]
		for ftp in FIELDS[model]:
			field = ftp['field']
			value = thing.__getattribute__(field)
			template = ftp['template']
			value = value if value else (template.force if hasattr(template, 'force') else '')
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
		value = template.force
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
		value = request.POST[field] if field in request.POST else template.force
		thing = template.set(thing, field, request.POST, False)
	thing = manager.create(**thing)
	print kwargs
	if old_model:
		old = MODELS[old_model].fetch(id=kwargs['id'])
		print old
		if old and hasattr(old, model):
			old.__setattr__(model, thing)
			old.save()
	return redirect('/rest/show/{}/{}/'.format(old_model,kwargs['id']) if old_model else '/rest/index/{}/'.format(model))

def show(request, model, id):
	return show_or_edit(request, model, id, False)

def edit(request, model, id):
	return show_or_edit(request, model, id, True)

def show_or_edit(request, model, id, isEdit):
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
	manager = MODELS[model]
	thing = manager.get(id=id)
	for ftp in FIELDS[model]:
		template = ftp['template']
		field = ftp['field']
		value = request.POST[field] if field in request.POST else template.force
		thing = template.set(thing, field, request.POST, True)
	thing.save()
	return redirect("/rest/show/{}/{}".format(model, thing.id))

def delete(request, model, id):
	manager = MODELS[model]
	thing = manager.get(id=id)
	thing.delete()
	return redirect('/reports/students/2017/')