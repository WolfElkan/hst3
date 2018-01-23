from django.shortcuts import render, redirect, HttpResponse
from Utils.custom_fields import Bcrypt, PhoneNumber, ZipCode
from datetime import datetime
from Utils.hacks import copy, getme, seshinit, forminit, first, copyatts, pdir
import json
import io

from apps.main.models import Family, Address, Parent, User, Student
Addresses = Address.objects
Families  = Family.objects
Parents   = Parent.objects
Students  = Student.objects
Users     = User.objects

from apps.program.models import Venue, CourseTrad, Course, Enrollment
Venues      = Venue.objects
CourseTrads = CourseTrad.objects
Courses     = Course.objects
Enrollments = Enrollment.objects

def load(request):
	if request.method == 'GET':
		return load_get(request)
	elif request.method == 'POST':
		return load_post(request)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def load_get(request):
	seshinit(request,'json_dump')
	context = {
		'json_dump': request.session['json_dump']
	}
	return render(request, 'main/seed.html', context)

def load_post(request):
	nUsers = 0
	nFamilies = 0
	nStudents = 0
	nParents = 0
	nAddresses = 0
	nVenues = 0
	nCourseTrads = 0
	nCourses = 0
	nEnrollments = 0
	json_dump = request.POST['json_dump']
	request.session['json_dump'] = ''
	data = json.loads(json_dump)
	for ct in data['coursetrads']:
		if 'alias_id' not in ct:
			print 'Importing '+ct['title'].upper()
			CourseTrads.create(ct)
			nCourseTrads += 1
	for ct in data['coursetrads']:
		if 'alias_id' in ct:
			print 'Importing '+ct['title'].upper()
			alias = CourseTrads.get(id=ct.pop('alias_id'))
			ct['alias'] = alias
			CourseTrads.create(ct)
			nCourseTrads += 1
	for fam in data['families']:
		print 'Importing '+fam['last']
		family = copy(fam,['last','phone','email'])
		address = copy(fam['address'])
		if 'zipcode' not in address:
			address['zipcode'] = 00000
		address = Addresses.create(address)
		nAddresses += 1
		family['address'] = address
		family = Families.create(family)
		nFamilies += 1
		if 'mother' in fam:
			mother = copy(fam['mother'])
			mother['family_id'] = family.id
			family.mother = Parents.create(mother)
			nParents += 1
		if 'father' in fam:
			father = copy(fam['father'])
			father['family_id'] = family.id
			family.father = Parents.create(father)
			nParents += 1
		family.save()
		for stu in fam['students']:
			student = copy(stu)
			enrollments = student.pop('enrollments')
			print enrollments
			student['family'] = family
			Students.create(student)
			nStudents += 1
	print 'IMPORT COMPLETE'
	print 'Users:     ' + str(nUsers).rjust(4)
	print 'Families:  ' + str(nFamilies).rjust(4)
	print 'Students:  ' + str(nStudents).rjust(4)
	print 'Parents:   ' + str(nParents).rjust(4)
	print 'Addresses: ' + str(nAddresses).rjust(4)
	print 'Venues:    ' + str(nVenues).rjust(4)
	print 'Traditions:' + str(nCourseTrads).rjust(4)
	print 'Courses:   ' + str(nCourses).rjust(4)
	print 'Enrollments:'+ str(nCourseTrads).rjust(3)

	return redirect('/seed/load')

# MANUAL DATA ENTRY (REST)

MODELS = {
	'address'   : Addresses,
	'family'    : Families,
	'parent'    : Parents,
	'student'   : Students,
	'coursetrad': CourseTrads,
	'course'    : Courses,
	'enrollment': Enrollments,
}

	# WIDGET TEMPLATES

class VarChar(object):
	def __init__(self, maxlength):
		self.force = False
		self.maxlength = maxlength
	def widget(self, field, value):
		return '<input type="text" maxlength="{}" name="{}" value="{}">'.format(self.maxlength, field, value)
	def static(self, field, value):
		return value
	def clean(self, value):
		return value

class Integer(object):
	def __init__(self, suffix=''):
		self.force = False
		self.suffix = suffix
	def widget(self, field, value):
		if value:
			value = int(value)
		return '<input type="number" name="{}" value="{}"> {}'.format(field, value, self.suffix)
	def static(self, field, value):
		if value:
			return str(value) +' '+ self.suffix
	def clean(self, value):
		return value if value else 0

class Enum(object):
	def __init__(self, *options):
		self.force = True
		self.options = options
	def widget(self, field, value):
		html = '<select name="{}">'.format(field)
		for option in self.options:
			html += '<option value="{}"{}>{}</option>'.format(option,' selected' if value == option else '',option)
		html += '</select>'
		return html
	def static(self, field, value):
		return value
	def clean(self, value):
		return value

class Radio(object):
	def __init__(self, options):
		self.force = True
		self.options = options
	def widget(self, field, value):
		value = value if value else 0
		html = ''
		for o in range(len(self.options)):
			html += '<input type="radio" name="{}" value="{}" {}>{}<br>'.format(field, o,' checked' if value == o else '',self.options[o])
		return html
	def static(self, field, value):
		return value
	def clean(self, value):
		return value

class Checkbox(object):
	def __init__(self, suffix=''):
		self.force = True
		self.suffix = suffix
	def widget(self, field, value):
		return '<input type="checkbox" name="{}" {}> {}'.format(field, ' checked' if value else '',self.suffix)
	def static(self, field, value):
		return value
	def clean(self, value):
		return value == 'on'

class Date(object):
	def __init__(self):
		self.force = False
	def widget(self, field, value):
		return '<input type="date" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		if value:
			return value.strftime('%B %-d, %Y')
	def clean(self, value):
		return value

class Time(object):
	def __init__(self):
		self.force = False
	def widget(self, field, value):
		return '<input type="time" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		return value
	def clean(self, value):
		return value

class ForeignKey(object):
	def __init__(self, *manager):
		if manager:
			self.manager = manager
		self.force = False
	def widget(self, field, value):
		rel = field
		if field in ['mother','father']:
			field = 'parent'
		html = '<select name="{}_id">'.format(rel)
		for foreign in MODELS[field].all():
			html += '<option value="{}"{}>{}</option>'.format(foreign.id,' selected' if value == foreign else '',str(foreign))
		html += '</select>'
		return html
	def static(self, field, value):
		rel = field
		if value:
			if field in ['mother','father']:
				field = 'parent'
			return '<a href="/rest/show/{}/{}">{}</a>'.format(field,value.id,str(value))
		else:
			return '<a href="new/{}">add</a>'.format(rel)
	def clean(self, value):
		return value

class ForeignSet(object):
	def __init__(self, foreign):
		self.force = False
		self.foreign = foreign
	def widget(self, field, value):
		pass
	def static(self, field, value):
		things = self.foreign.filter(**value['mapping'])
		html = '<ul>'
		for thing in things:
			html += '<li>{}</li>'.format(ForeignKey().static(value['model'], thing))
		html += '</ul>'
		return html
	def clean(self, value):
		return value

FIELDS = {
	'address'   : [
		{'field':'line1'     , 'template': VarChar(50)},
		{'field':'line2'     , 'template': VarChar(50)},
		{'field':'city'      , 'template': VarChar(25)},
		{'field':'state'     , 'template': VarChar(2)},
		{'field':'zipcode'   , 'template': ZipCode()},
	],
	'family'    : [
		{'field':'last'      , 'template': VarChar(30)},
		{'field':'phone'     , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum('','Home','Cell','Work')},
		{'field':'email'     , 'template': VarChar(254)},
		{'field':'mother'    , 'template': ForeignKey()},
		{'field':'father'    , 'template': ForeignKey()},
		{'field':'address'   , 'template': ForeignKey()},
		{'field':'_children' , 'template': ForeignSet(Students)},
	],
	'parent'    : [
		{'field':'first'     , 'template': VarChar(20)},
		{'field':'family'    , 'template': ForeignKey()},
		{'field':'alt_last'  , 'template': VarChar(30)},
		{'field':'sex'       , 'template': Enum('M','F')},
		{'field':'alt_phone' , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum('','Home','Cell','Work')},
		{'field':'alt_email' , 'template': VarChar(254)},
	],
	'student'   : [
		{'field':'first'     , 'template': VarChar(20)},
		{'field':'alt_first' , 'template': VarChar(20)},
		{'field':'middle'    , 'template': VarChar(20)},
		{'field':'family'    , 'template': ForeignKey()},
		{'field':'alt_last'  , 'template': VarChar(30)},
		{'field':'sex'       , 'template': Enum('M','F')},
		{'field':'current'   , 'template': Checkbox('Student is currently in HST')},
		{'field':'birthday'  , 'template': Date()},
		{'field':'grad_year' , 'template': Integer()},
		{'field':'height'    , 'template': Integer('inches')},
		{'field':'alt_phone' , 'template': PhoneNumber()},
		{'field':'alt_email' , 'template': VarChar(254)},
		{'field':'tshirt'    , 'template': Enum('','YS','YM','YL','XS','AS','AM','AL','XL','2X','3X')},
		{'field':'_enrollments','template': ForeignSet(Enrollments)},
	],
	'coursetrad': [
		{'field':'title'     , 'template': VarChar(50)},
		{'field':'e'         , 'template': Checkbox('This is a real (and currently offered) course that may be enrolled in, not a student group for admin purposes')},
		{'field':'day'       , 'template': Enum('','Mon','Tue','Wed','Thu','Fri','Sat','Sun')},
		{'field':'start'     , 'template': Time()},
		{'field':'end'       , 'template': Time()},
		{'field':'nMeets'    , 'template': Integer()},
		{'field':'show'      , 'template': VarChar(2)},
		{'field':'vs'        , 'template': Checkbox('This class performs in the Variety Show')},
		{'field':'min_age'   , 'template': Integer()},
		{'field':'max_age'   , 'template': Integer()},
		{'field':'min_grd'   , 'template': Integer()},
		{'field':'max_grd'   , 'template': Integer()},
		{'field':'M'         , 'template': Checkbox('Boys may enroll')},
		{'field':'F'         , 'template': Checkbox('Girls may enroll')},
		{'field':'C'         , 'template': Checkbox('Only current students may enroll')},
		{'field':'I'         , 'template': Checkbox('Students must complete 1 year of Tap or Irish Soft Shoe to enroll')},
		{'field':'A'         , 'template': Radio([
			'No audition or acting class required',
			'Students must pass a skills assessment (or have already taken this class) to enroll',
			'1 year of Acting A or B required to enroll',
			'1 year of Acting A or B required to audition',
			'1 year of Acting and 1 year of Troupe required to audition',
		])},
		{'field':'tuition'   , 'template': Integer()},
		{'field':'redtuit'   , 'template': Integer()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'the_hours' , 'template': Integer()},
		{'field':'prepaid'   , 'template': Checkbox('Families must purchase 10 prepaid tickets for $100, not included in tuition')},
		{'field':'_courses'  , 'template': ForeignSet(Courses)},
	],
	'course'    : [
		{'field':'year'      , 'template': Integer()},
		{'field':'last_date' , 'template': Date()},
		{'field':'tuition'   , 'template': Integer()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'the_hours' , 'template': Integer()},
		{'field':'prepaid'   , 'template': Checkbox()},
		{'field':'teacher'   , 'template': ForeignKey()},
		{'field':'trad'      , 'template': ForeignKey(CourseTrads)},
		{'field':'aud_date'  , 'template': Date()},
		{'field':'_students' , 'template': ForeignSet(Enrollments)},
	],
	'enrollment': [
		{'field':'student'   , 'template': ForeignKey()},
		{'field':'course'    , 'template': ForeignKey()},
		{'field':'role'      , 'template': VarChar(0)},
		{'field':'role_type' , 'template': Enum('','Chorus','Support','Lead')},
	],
}

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
		if isEdit:
			value = ftp['template'].widget(ftp['field'],value)
		else:
			value = ftp['template'].static(ftp['field'],value)
		if value == None:
			value = ''
		display.append({
			'field':ftp['field'], 
			'input':value
		})
	context = {
		'thing'   : thing,
		'display' : display,
		'model'   : model,
		'Model'   : 'Course Tradition' if model == 'coursetrad' else model.title(),
	}
	return render(request, 'main/rest/edit.html' if isEdit else 'main/rest/show.html', context)

def update(request, model, id):
	manager = MODELS[model]
	thing = manager.get(id=id)
	for ftp in FIELDS[model]:
		field = ftp['field']
		if type(ftp['template']) is ForeignKey:
			field += '_id'
		# print field
		if field in request.POST and (request.POST[field] or ftp['template'].force):
			value = request.POST[field]
			value = ftp['template'].clean(value)
			thing.__setattr__(field, value)
	thing.save()
	return redirect("/rest/show/{}/{}".format(model, thing.id))

def dump(request):
	data = {
		'venues':[],
		'coursetrads':[],
		'families':[],
	}
	CourseTradsAll = CourseTrads.all()
	for ct in CourseTradsAll:
		if not ct.alias_id:
			data['coursetrads'].append({
				'id'       : ct.id,
				'title'    : ct.title,
				'enroll'   : ct.enroll,
				'day'      : ct.day,
				'start'    : str(ct.start),
				'end'      : str(ct.end),
				'nMeets'   : ct.nMeets,
				'show'     : ct.show,
				'vs'       : ct.vs,
				'min_age'  : ct.min_age,
				'max_age'  : ct.max_age,
				'min_grd'  : ct.min_grd,
				'max_grd'  : ct.max_grd,
				'tuition'  : float(ct.tuition),
				'redtuit'  : float(ct.redtuit),
				'vol_hours': ct.vol_hours,
				'the_hours': ct.the_hours,
				'prepaid'  : ct.prepaid,
				'M': ct.M, 'F': ct.F, 'C': ct.C, 'I': ct.I, 'A': ct.A,
			})
		else:
			data['coursetrads'].append({
				'id': ct.id,
				'title'    : ct.title,
				'alias_id' : ct.alias_id,
			})
	FamiliesAll = Families.all()
	for family in FamiliesAll:
		family_obj = {
			'last':family.last,
			'phone':int(family.phone),
			'phone_type':family.phone_type,
			'email':family.email,
		}
		if family.mother_id:
			family_obj['mother'] = copyatts(family.mother,['first','sex'])
			if family.mother.alt_last:
				family_obj['mother']['alt_last' ] = family.mother.alt_last
			if family.mother.alt_phone:
				family_obj['mother']['alt_phone'] = family.mother.alt_phone
			if family.mother.alt_email:
				family_obj['mother']['alt_email'] = family.mother.alt_email
		if family.father_id:
			family_obj['father'] = copyatts(family.father,['first','sex'])
			if family.father.alt_last:
				family_obj['father']['alt_last' ] = family.father.alt_last
			if family.father.alt_phone:
				family_obj['father']['alt_phone'] = family.father.alt_phone
			if family.father.alt_email:
				family_obj['father']['alt_email'] = family.father.alt_email
		if family.address_id:
			family_obj['address'] = copyatts(family.address,['line1','city','state'])
			if family.address.zipcode:
				family_obj['address']['zipcode' ] = float(family.address.zipcode) if float(family.address.zipcode) % 1 else int(family.address.zipcode)
			if family.address.line2:
				family_obj['address']['line2' ] = family.address.line2
		family_obj['students'] = []
		for student in family.children.all():
				student_obj = copyatts(student,['first','sex'])
				if student.birthday:
					student_obj['birthday']  = str(student.birthday)
				if student.alt_first:
					student_obj['alt_first'] = student.alt_first
				if student.middle:
					student_obj['middle']    = student.middle
				if student.alt_last:
					student_obj['alt_last']  = student.alt_last
				if student.grad_year:
					student_obj['grad_year'] = student.grad_year
				if student.height:
					student_obj['height']    = student.height
				if student.alt_phone:
					student_obj['alt_phone'] = student.alt_phone
				if student.alt_email:
					student_obj['alt_email'] = student.alt_email
				if student.tshirt:
					student_obj['tshirt']    = student.tshirt
				student_obj['enrollments'] = []
				family_obj['students'].append(student_obj)
		data['families'].append(family_obj)
		huge = json.dumps(data)
	print 'Rendered ' + str(len(huge)) + ' characters of JSON'
	return HttpResponse(huge)

def nuke(request):
	Users.all().delete()
	Families.all().delete()
	Students.all().delete()
	Parents.all().delete()
	Addresses.all().delete()
	Venues.all().delete()
	CourseTrads.all().delete()
	Courses.all().delete()
	print '\n\n'+' '*34+'THE RADIANCE OF A THOUSAND SUNS'+'\n\n'
	return redirect ('/seed/load')







