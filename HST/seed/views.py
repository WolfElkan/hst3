from django.shortcuts import render, redirect, HttpResponse
from Utils.custom_fields import Bcrypt, PhoneNumber
from datetime import datetime
from Utils.hacks import copy, getme, seshinit, forminit, first, copyatts
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

class VarChar(object):
	def __init__(self, maxlength):
		self.force = False
		self.maxlength = maxlength
	def widget(self, field, value):
		return '<input type="text" maxlength="{}" name="{}" value="{}">'.format(self.maxlength, field, value)

class Numeric(object):
	def __init__(self, suffix=''):
		self.force = True
		self.suffix = suffix
	def widget(self, field, value):
		return '<input type="number" name="{}" value="{}"> {}'.format(field, value, self.suffix)

class Enum(object):
	def __init__(self, *options):
		self.force = True
		self.options = options
	def widget(self, field, value):
		html = '<select name={}>'.format(field)
		for option in self.options:
			html += '<option value="{}"{}>{}</option>'.format(option,' selected' if value == option else '',option)
		html += '</select>'
		return html

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

class Checkbox(object):
	def __init__(self, suffix=''):
		self.force = True
		self.suffix = suffix
	def widget(self, field, value):
		return '<input type="checkbox" name="{}" {}> {}'.format(field, ' checked' if value else '',self.suffix)

class Date(object):
	def __init__(self):
		self.force = False
	def widget(self, field, value):
		return '<input type="date" name="{}" value="{}">'.format(field, value)

class Time(object):
	def __init__(self):
		self.force = False
	def widget(self, field, value):
		return '<input type="time" name="{}" value="{}">'.format(field, value)

class ForeignKey(object):
	def __init__(self):
		self.force = False
	def widget(self, field, value):
		if field in ['mother','father']:
			field = 'parent'
		return '<a href="/seed/manual/{}/{}">{}</a>'.format(field,value.id,str(value))

FIELDS = {
	'address'   : [
		{'field':'line1'     , 'template': VarChar(50)},
		{'field':'line2'     , 'template': VarChar(50)},
		{'field':'city'      , 'template': VarChar(25)},
		{'field':'state'     , 'template': VarChar(2)},
		{'field':'zipcode'   , 'template': Numeric()},
	],
	'family'    : [
		{'field':'last'      , 'template': VarChar(30)},
		{'field':'phone'     , 'template': Numeric()},
		{'field':'phone_type', 'template': Enum('','Home','Cell','Work')},
		{'field':'email'     , 'template': VarChar(254)},
		{'field':'mother'    , 'template': ForeignKey()},
		{'field':'father'    , 'template': ForeignKey()},
		{'field':'address'   , 'template': ForeignKey()},
	],
	'parent'    : [
		{'field':'first'     , 'template': VarChar(20)},
		{'field':'family'    , 'template': ForeignKey()},
		{'field':'alt_last'  , 'template': VarChar(30)},
		{'field':'sex'       , 'template': Enum('M','F')},
		{'field':'alt_phone' , 'template': Numeric()},
		{'field':'phone_type', 'template': Enum('','Home','Cell','Work')},
		{'field':'alt_email' , 'template': VarChar(254)},
	],
	'student'   : [
		{'field':'first'     , 'template': VarChar(20)},
		{'field':'alt_first' , 'template': VarChar(20)},
		{'field':'middle'    , 'template': VarChar(20)},
		{'field':'alt_last'  , 'template': VarChar(30)},
		{'field':'sex'       , 'template': Enum('M','F')},
		{'field':'current'   , 'template': Checkbox('Student is currently in HST')},
		{'field':'birthday'  , 'template': Date()},
		{'field':'grad_year' , 'template': Numeric()},
		{'field':'height'    , 'template': Numeric('inches')},
		{'field':'alt_phone' , 'template': Numeric()},
		{'field':'alt_email' , 'template': VarChar(254)},
		{'field':'tshirt'    , 'template': VarChar(2)},
		{'field':'family'    , 'template': ForeignKey()},
	],
	'coursetrad': [
		{'field':'title'     , 'template': VarChar(50)},
		{'field':'enroll'    , 'template': Checkbox()},
		{'field':'day'       , 'template': Enum('','Mon','Tue','Wed','Thu','Fri','Sat','Sun')},
		{'field':'start'     , 'template': Time()},
		{'field':'end'       , 'template': Time()},
		{'field':'nMeets'    , 'template': Numeric()},
		{'field':'show'      , 'template': VarChar(2)},
		{'field':'vs'        , 'template': Checkbox()},
		{'field':'min_age'   , 'template': Numeric()},
		{'field':'max_age'   , 'template': Numeric()},
		{'field':'min_grd'   , 'template': Numeric()},
		{'field':'max_grd'   , 'template': Numeric()},
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
		{'field':'tuition'   , 'template': Numeric()},
		{'field':'redtuit'   , 'template': Numeric()},
		{'field':'vol_hours' , 'template': Numeric()},
		{'field':'the_hours' , 'template': Numeric()},
		{'field':'prepaid'   , 'template': Checkbox()},
	],
	'course'    : [
		{'field':'year'      , 'template': Numeric()},
		{'field':'last_date' , 'template': Date()},
		{'field':'tuition'   , 'template': Numeric()},
		{'field':'vol_hours' , 'template': Numeric()},
		{'field':'the_hours' , 'template': Numeric()},
		{'field':'prepaid'   , 'template': Checkbox()},
		{'field':'teacher'   , 'template': ForeignKey()},
		{'field':'trad'      , 'template': VarChar(2)},
		{'field':'aud_date'  , 'template': Date()},
	],
	'enrollment': [
		{'field':'role'      , 'template': VarChar(0)},
		{'field':'role_type' , 'template': Enum('','Chorus','Support','Lead')},
		{'field':'course'    , 'template': ForeignKey()},
		{'field':'student'   , 'template': ForeignKey()},
	],
}

MODELS = {
	'address'   : Addresses,
	'family'    : Families,
	'parent'    : Parents,
	'student'   : Students,
	'coursetrad': CourseTrads,
	'course'    : Courses,
	'enrollment': Enrollments,
}

def manual(request, *args, **kwargs):
	if request.method == 'GET':
		return manual_get(request, *args, **kwargs)
	elif request.method == 'POST':
		return manual_post(request, *args, **kwargs)
	else:
		return HttpResponse("Unrecognized HTTP Verb")

def manual_get(request, model, id):
	manager = MODELS[model]
	thing = manager.get(id=id)
	print thing
	tempset = FIELDS[model]
	display = []
	for ftp in tempset:
		value = thing.__getattribute__(ftp['field'])
		value = value if value else ''
		display.append({
			'field':ftp['field'], 
			'input':ftp['template'].widget(ftp['field'],value)
		})
	context = {
		'thing'   : thing,
		'display' : display,
		'model'   : 'Course Tradition' if model == 'coursetrad' else model.title(),
	}
	return render(request, 'main/manual.html', context)


def manual_post(request, model, id):
	manager = MODELS[model]
	thing = manager.get(id=id)
	for ftp in FIELDS[model]:
		field = ftp['field']
		if field in request.POST and (request.POST[field] or ftp['template'].force):
			print field, request.POST[field]
			# TODO: Actually make the changes
	return HttpResponse(str(thing))

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







