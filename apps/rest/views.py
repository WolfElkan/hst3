from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
from Utils.hacks import copy, getme, seshinit, forminit, first, copyatts, pretty, pdir, metastr
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
	qset = MODELS[model].filter(**query)
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
		'Model'   : 'Course Tradition' if model == 'coursetrad' else model.title(),
	}
	return render(request, 'rest/index.html', context)

def new(request, model, *relation):
	manager = MODELS[model]
	tempset = FIELDS[model]
	display = []
	for ftp in tempset:
		field = ftp['field']
		template = ftp['template']
		value = template.force if hasattr(template, 'force') else ''
		value = template.widget(field,value)
		display.append({
			'field':template.field if template.field else field, 
			'input':value
		})
	context = {
		'display' : display,
		'model'   : model,
		'Model'   : 'Course Tradition' if model == 'coursetrad' else model.title(),
	}
	return render(request, 'rest/new.html', context)

def create(request, model, *relation):
	manager = MODELS[model]
	thing = {}
	for ftp in FIELDS[model]:
		# if field not in ['csrfmiddlewaretoken']:
			# thing[field] = request.POST[field]
		template = ftp['template']
		field = ftp['field']
		field = template.field if template.field else field
		print field
		value = request.POST[field] if field in request.POST else template.force
		if hasattr(template, 'clean'):
			value = template.clean(value)
			thing.__setitem__(field, value)
		# elif hasattr(template,'force'):
		# 	thing.__setitem__(field, template.force)
	print thing
	manager.create(**thing)
	return redirect('/rest/index/{}/'.format(model))

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
		'Model'   : 'Course Tradition' if model == 'coursetrad' else model.title(),
	}
	return render(request, 'rest/edit.html' if isEdit else 'rest/show.html', context)

def update(request, model, id):
	manager = MODELS[model]
	thing = manager.get(id=id)
	for ftp in FIELDS[model]:
		template = ftp['template']
		field = ftp['field']
		field = template.field if template.field else field
		# print field, field in request.POST
		if field in request.POST and request.POST[field]:
			value = request.POST[field]
			# print field, value
			value = template.clean(value)
			thing.__setattr__(field, value)
		elif hasattr(template,'force'):
			thing.__setattr__(field, template.force)
	thing.save()
	return redirect("/rest/show/{}/{}".format(model, thing.id))