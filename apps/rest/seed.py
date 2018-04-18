from django.shortcuts import render, redirect, HttpResponse

from apps.people.managers import Families, Addresses, Parents, Users, Students
from apps.program.managers import CourseTrads, Courses, Enrollments, Venues

from Utils.data  import copy, copyatts, Each
from Utils.fjson import FriendlyEncoder
from Utils.seshinit import seshinit
from Utils.snippets import order_coursetrads, make
from Utils.security import getyear

from datetime import datetime
import json

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
	return render(request, 'json/seed.html', context)

def load_post(request):
	start_import = datetime.now()
	nUsers       = 0
	nFamilies    = 0
	nStudents    = 0
	nParents     = 0
	nAddresses   = 0
	nVenues      = 0
	nCourseTrads = 0
	nCourses     = 0
	nEnrollments = 0
	json_dump = request.POST['json_dump']
	request.session['json_dump'] = ''
	data = json.loads(json_dump)
	for ct in data['coursetrads']:
		if 'alias_id' not in ct:
			already = CourseTrads.fetch(id=ct['id'])
			if already:
				print 'Exists:   '+ct['title'].upper()
			else:
				print 'Importing '+ct['title'].upper()
				CourseTrads.create(**ct)
				nCourseTrads += 1
	for ct in data['coursetrads']:
		if 'alias_id' in ct:
			already = CourseTrads.fetch(id=ct['id'])
			if already:
				print 'Exists:   '+ct['title'].upper()
			else:
				print 'Importing '+ct['title'].upper()
				alias = CourseTrads.get(id=ct.pop('alias_id'))
				ct['alias'] = alias
				CourseTrads.create(**ct)
				nCourseTrads += 1
	# cts = CourseTrads.filter(e=True)
	# for year in data['years']:
	# 	for ct in cts:
	# 		ct.make(year)
	# 		nCourses += 1
	for fam in data['families']:
		print fam['last']
		family = copy(fam,['last','phone','email'])
		if 'address' in fam:
			address = copy(fam['address'])
			if 'zipcode' not in address:
				address['zipcode'] = 00000
			address = Addresses.create(**address)
			nAddresses += 1
			family['address'] = address
		family = Families.create(**family)
		family.update_name_num()
		nFamilies += 1
		if 'mother' in fam:
			mother = copy(fam['mother'])
			mother['family_id'] = family.id
			family.mother = Parents.create(**mother)
			nParents += 1
		if 'father' in fam:
			father = copy(fam['father'])
			father['family_id'] = family.id
			family.father = Parents.create(**father)
			nParents += 1
		family.save()
		for stu in fam['students']:
			print '  '+stu['first']
			student = copy(stu)
			enrollments = student.pop('enrollments') if 'enrollments' in student else []
			student['family'] = family
			newStudent = Students.create(**student)
			for enrollment in enrollments:
				rolled = type(enrollment) in [object,dict]
				course_id = enrollment['course_id'] if rolled else enrollment
				print '    '+course_id
				course = Courses.fetch(id=course_id)
				if not course:
					course = Courses.create_by_id(course_id)
					nCourses += 1
				enrollment_kwargs = {
					'student': newStudent,
					'course' : course,
					'status' : "enrolled"
				}
				if rolled:
					enrollment_kwargs['role']      = enrollment['role']
					enrollment_kwargs['role_type'] = enrollment['role_type']
				Enrollments.create(**enrollment_kwargs)
				nEnrollments += 1
				# if type(enrollment) in [str,unicode]:
				# 	Courses.get(id=enrollment).sudo_enroll(newStudent)
				# else:
				# 	course = Courses.get(id=enrollment['course_id'])
				# 	Enrollments.create(course=course, student=newStudent, role=enrollment['role'], role_type=enrollment['role_type'])
			nStudents += 1
	print "-assign name_num's"
	Each(Families.all()).update_name_num()
	print '- order_coursetrads'
	order_coursetrads()
	year = getyear()
	print '- make {}'.format(year)
	nCourses += make(year)
	import_duration = datetime.now() - start_import
	print
	print 'IMPORT COMPLETED'
	print 'Users:     ' + str(nUsers).rjust(5)
	print 'Families:  ' + str(nFamilies).rjust(5)
	print 'Students:  ' + str(nStudents).rjust(5)
	print 'Parents:   ' + str(nParents).rjust(5)
	print 'Addresses: ' + str(nAddresses).rjust(5)
	print 'Venues:    ' + str(nVenues).rjust(5)
	print 'Traditions:' + str(nCourseTrads).rjust(5)
	print 'Courses:   ' + str(nCourses).rjust(5)
	print 'Enrollments:'+ str(nEnrollments).rjust(4)
	print 'Time:    '   + str(import_duration)

	return redirect('/seed/load/')

def dump(request):
	data = {
		'venues':[],
		'coursetrads':[],
		'families':[],
	}
	years = set()
	CourseTradsAll = CourseTrads.all()
	for ct in CourseTradsAll:
		if not ct.alias_id:
			data['coursetrads'].append({
				'id'       : ct.id,
				'title'    : ct.title,
				'e'        : ct.e,
				'day'      : ct.day,
				'semester' : ct.semester,
				'start'    : str(ct.start),
				'end'      : str(ct.end),
				'nMeets'   : ct.nMeets,
				'show'     : ct.show,
				'sa'       : ct.sa,
				'min_age'  : ct.min_age,
				'max_age'  : ct.max_age,
				'min_grd'  : ct.min_grd,
				'max_grd'  : ct.max_grd,
				'eligex'   : ct.eligex,
				'tuition'  : float(ct.tuition),
				'redtuit'  : float(ct.redtuit),
				'vol_hours': ct.vol_hours,
				'the_hours': ct.the_hours,
				'auto'     : ct.auto,
				'trig'     : ct.trig,
			})
		else:
			data['coursetrads'].append({
				'id': ct.id,
				'title'    : ct.title,
				'alias_id' : ct.alias_id,
				'e'        : False,
			})
	for family in Families.all_join_alpha():
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
			if int(family.mother.alt_phone):
				family_obj['mother']['alt_phone'] = family.mother.alt_phone
			if family.mother.alt_email:
				family_obj['mother']['alt_email'] = family.mother.alt_email
		if family.father_id:
			family_obj['father'] = copyatts(family.father,['first','sex'])
			if family.father.alt_last:
				family_obj['father']['alt_last' ] = family.father.alt_last
			if int(family.father.alt_phone):
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
		for student in family.children:
				student_obj = student.__json__()
				student_obj.pop('id')
				enrollments = student.enrollments
				if enrollments:
					student_obj['enrollments'] = []
					for enrollment in enrollments:
						if enrollment.role or enrollment.role_type:
							student_obj['enrollments'].append({
								'course_id': enrollment.course_id,
								'role'     : enrollment.role,
								'role_type': enrollment.role_type,
							})
						else:
							student_obj['enrollments'].append(enrollment.course_id)
						years.update([int(enrollment.course.year)])
				family_obj['students'].append(student_obj)
		data['families'].append(family_obj)
		data['years'] = list(years)
	return HttpResponse(json.dumps(data, cls=FriendlyEncoder))

def nuke(request):
	Users.all().delete()
	Families.all().delete()
	Students.all().delete()
	Parents.all().delete()
	Addresses.all().delete()
	Venues.all().delete()
	CourseTrads.all().delete()
	Courses.all().delete()
	Enrollments.all().delete()
	print '\n\n'+' '*34+'THE RADIANCE OF A THOUSAND SUNS'+'\n\n'
	return redirect ('/seed/load')