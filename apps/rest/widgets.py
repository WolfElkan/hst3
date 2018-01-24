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


MODELS = {
	'address'   : Addresses,
	'family'    : Families,
	'parent'    : Parents,
	'student'   : Students,
	'coursetrad': CourseTrads,
	'course'    : Courses,
	'enrollment': Enrollments,
}


def rest_link(foreign):
	if foreign:
		return '<a href="/rest/show/{}/{}/">{}</a>'.format(foreign.rest_model,foreign.id,str(foreign))
	else:
		return ''

def rest_list(qset):
	if qset:
		html = '<span>({})</span><ul>'.format(len(qset))
		for foreign in qset:
			html += '<li>{}</li>'.format(rest_link(foreign))
		html += '</ul>'
		return html
	else:
		return '(0)'


class VarChar(object):
	def __init__(self, maxlength):
		self.force = ''
		self.maxlength = maxlength
	def widget(self, field, value):
		return '<input type="text" maxlength="{}" name="{}" value="{}">'.format(self.maxlength, field, value)
	def static(self, field, value):
		return value
	def clean(self, value):
		return value

class Integer(object):
	def __init__(self, suffix=''):
		self.force = 0
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
		self.options = options
		if not options[0]:
			self.force = options[0]
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
		self.force = 0
		self.options = options
	def widget(self, field, value):
		value = value if value else 0
		html = ''
		for o in range(len(self.options)):
			html += '<input type="radio" name="{}" value="{}" {}>{}<br>'.format(field, o,' checked' if value == o else '',self.options[o])
		return html
	def static(self, field, value):
		return self.options[value]
	def clean(self, value):
		return value

class Checkbox(object):
	def __init__(self, suffix=''):
		self.force = False
		self.suffix = suffix
	def widget(self, field, value):
		return '<input type="checkbox" name="{}" {}> {}'.format(field, ' checked' if value else '',self.suffix)
	def static(self, field, value):
		return 'Yes' if value else 'No'
	def clean(self, value):
		print '*'*100
		print value
		return value == 'on'

class Date(object):
	def widget(self, field, value):
		return '<input type="date" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		if value:
			return value.strftime('%B %-d, %Y')
	def clean(self, value):
		return value

class Time(object):
	def widget(self, field, value):
		return '<input type="time" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		return value
	def clean(self, value):
		return value

class ForeignKey(object):
	def static(self, field, value):
		self.field = field
		if value:
			return rest_link(value)
		else:
			return '<a href="new/{}/">add</a>'.format(field)
	def widget(self, field, value):
		self.field = field
		html = '<select name="{}_id">'.format(field)
		if value:
			for foreign in MODELS[value.rest_model].all():
				html += '<option value="{}"{}>{}</option>'.format(foreign.id,' selected' if value == foreign else '',str(foreign))
		html += '</select>'
		return html
	def clean(self, value):
		return value

class ForeignSet(object):
	def __init__(self, **kwargs):
		self.widget_query = kwargs['widget_query'] if 'widget_query' in kwargs else None
	def static(self, field, qset):
		return rest_list(qset)
	def widget(self, field, qset):
		return rest_list(qset)
	def clean(self, qset):
		return qset

class ToggleSet(object):
	def __init__(self, **kwargs):
		self.static_set = kwargs['static_set'] if 'static_set' in kwargs else None
		self.widget_set = kwargs['widget_set'] if 'widget_set' in kwargs else None
		self.clean_func = kwargs['clean_func'] if 'clean_func' in kwargs else None
	def static(self, field, qset):
		pass
	def widget(self, field, qset):
		pass
	def clean(self, value):
		if self.clean_func:
			return self.clean_func(value)
		else:
			return value
	