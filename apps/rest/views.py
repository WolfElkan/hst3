from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
from Utils.hacks import copy, getme, seshinit, forminit, first, copyatts, pretty, pdir

from .fields import FIELDS
from .widgets import MODELS

def home(request, model):
	context = {}
	return render(request, 'rest/home.html')

def index(request, model):
	columns = []
	for ftp in FIELDS[model]:
		columns.append(ftp['field'])
	query = request.GET
	# print query
	qset = MODELS[model].filter(**query)
	display = []
	for thing in qset:
		dthing = ['<a href="/rest/show/{}/{}">{}</a>'.format(model, thing.id, thing.id)]
		for ftp in FIELDS[model]:
			value = thing.__getattribute__(ftp['field'])
			value = value if value else ''
			template = ftp['template']
			dthing.append(template.static(ftp['field'],value))
		display.append(dthing)
	context = {
		'columns' : columns,
		'display' : display,
		'model'   : model,
		'Model'   : 'Course Tradition' if model == 'coursetrad' else model.title(),
	}
	return render(request, 'rest/index.html', context)

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
		value = thing.__getattribute__(ftp['field'])
		value = value if value else ''
		template = ftp['template']
		if isEdit:
			value = template.widget(ftp['field'],value)
		else:
			value = template.static(ftp['field'],value)
		if value == None:
			value = ''
		display.append({
			'field':template.field if template.field else ftp['field'], 
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
		field = template.field if template.field else ftp['field']
		# print field, field in request.POST
		if field in request.POST and request.POST[field]:
			value = request.POST[field]
			value = ftp['template'].clean(value)
			# print field, value
			thing.__setattr__(field, value)
		elif hasattr(template,'force'):
			thing.__setattr__(field, template.force)
	thing.save()
	return redirect("/rest/show/{}/{}".format(model, thing.id))