from django.shortcuts import render, redirect, HttpResponse
from apps.main.managers import Addresses, Families, Parents, Users, Students
from apps.main.models import Teacher
Teachers = Teacher.objects
from apps.program.managers import Courses, CourseTrads, Enrollments, Auditions
from Utils.hacks import year as getyear


# Create your views here.

def make(request, year):
	cts = CourseTrads.filter(e=True)
	for ct in cts:
		ct.make(year)
	return HttpResponse('ok')


def students(request, **kwargs):
	year = kwargs['year'] if 'year' in kwargs else getyear()
	families = Families.all()
	table = []
	blank = {'content':'','rowspan':1,'class':'enr'}
	for family in families:
		oldest = True
		for student in family.children:
			row = {}
			row['family'] = family.last
			row['rowspan'] = len(family.children)
			row['oldest'] = oldest
			row['name'] = student.prefer
			row['id']     = student.id
			row['age']    = student.hst_age
			oldest = False
			for enrollment in student.enrollments_in(year):
				ctid = enrollment.course.tradition.id
				row[ctid[:1]] = '<a href="/rest/show/enrollment/{}">{}</a>'.format(enrollment.id, ctid)
			# if oldest:
			# 	row.append({
			# 		'content': family.last,
			# 		'rowspan': len(family.children),
			# 		'class'  : ''
			# 	})
			# 	oldest = False
			# row.append({
			# 	'content': student.id,
			# 	'rowspan': 1,
			# 	'class'  : 'right'
			# })
			# row.append({
			# 	'content': student.prefer,
			# 	'rowspan': 1,
			# 	'class'  : ''
			# })
			# row.append({
			# 	'content': student.hst_age,
			# 	'rowspan': 1,
			# 	'class'  : 'right'
			# })
			# for x in xrange(6):
			# 	row.append(blank)
			# for enrollment in student.enrollments_in(year):
			# 	ctid = enrollment.course.tradition.id
			# 	col = genredir[ctid[:1]]

			table.append(row)
			# row = []
	context = {
		'year'  : year,
		'table' : table,
	}
	return render(request, 'students.html', context)