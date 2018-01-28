from apps.main.managers import Addresses, Families, Parents, Users, Students
from apps.main.models import Teacher
from apps.program.managers import Courses, CourseTrads, Enrollments, Auditions

MODELS = {
	'address'   : Addresses,
	'family'    : Families,
	'parent'    : Parents,
	'student'   : Students,
	'teacher'   : Teacher.objects,
	'user'      : Users,
	'coursetrad': CourseTrads,
	'tradition' : CourseTrads,
	'course'    : Courses,
	'enrollment': Enrollments,
	'audition'  : Auditions,
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
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None		
		self.maxlength = kwargs['maxlength'] if 'maxlength' in kwargs else None		
		self.force = ''
	def widget(self, field, value):
		return '<input type="text" maxlength="{}" name="{}" value="{}">'.format(self.maxlength, field, value)
	def static(self, field, value):
		return value
	def clean(self, value):
		return str(value)

class Integer(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.suffix = kwargs['suffix'] if 'suffix' in kwargs else ''
		self.force = 0
	def widget(self, field, value):
		if value:
			value = int(value)
		return '<input type="number" name="{}" value="{}"> {}'.format(field, value, self.suffix)
	def static(self, field, value):
		return '<div>{} {}</div>'.format(value, self.suffix) if value else '<div>0</div>'
	def clean(self, value):
		return value if value else 0

class Enum(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.options = kwargs['options'] if 'options' in kwargs else []
		self.force = self.options[0]
	def widget(self, field, value):
		html = '<select name="{}">'.format(field)
		for option in self.options:
			html += '<option value="{}"{}>{}</option>'.format(option,' selected' if value == option else '',option)
		html += '</select>'
		return html
	def static(self, field, value):
		return value
	def clean(self, value):
		return str(value)
		
class Radio(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.options = kwargs['options'] if 'options' in kwargs else []
		self.force = 0
	def widget(self, field, value):
		value = value if value else 0
		html = ''
		for o in range(len(self.options)):
			html += '<input type="radio" name="{}" value="{}" {}>{}<br>'.format(field, o,' checked' if value == o else '',self.options[o])
		return html
	def static(self, field, value):
		value = value if value else 0
		return self.options[value]
	def clean(self, value):
		return value

class Checkbox(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.suffix = kwargs['suffix'] if 'suffix' in kwargs else ''
		self.force = False
	def widget(self, field, value):
		return '<input type="checkbox" name="{}" {}> {}'.format(field, ' checked' if value else '',self.suffix)
	def static(self, field, value):
		return 'Yes' if value else 'No'
	def clean(self, value):
		return str(value) == 'on'

class Date(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.force = None
	def widget(self, field, value):
		return '<input type="date" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		if value:
			return value.strftime('%B %-d, %Y')
	def clean(self, value):
		return str(value) if value else '0000-00-00'

class Time(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.force = None
	def widget(self, field, value):
		return '<input type="time" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		if value:
			return value.strftime('<div>%-I:%M %p</div>')
	def clean(self, value):
		return str(value) if value else '00:00'

class Price(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.force = 0.00
	def widget(self, field, value):
		if value:
			value = float(value)
		else:
			value = 0
		return '<input type="number" step="0.01" name="{}" value="{:.2f}">'.format(field, value)
	def static(self, field, value):
		if value:
			value = float(value)
			return '<div>${:.2f}</div>'.format(value)
		else:
			return '<div>$0.00</div>'
	def clean(self, value):
		return str(value) if value else 0.00

class ForeignKey(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.force = None
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
			model = value.rest_model
		else:
			model = field if field not in ['mother','father'] else 'parent'
		for foreign in MODELS[model].all():
			html += '<option value="{}"{}>{}</option>'.format(foreign.id,' selected' if value == foreign else '',str(foreign))
		html += '</select>'
		return html
	# def clean(self, value):
	# 	return str(value)

class ForeignSet(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.force = None
	def static(self, field, qset):
		return rest_list(qset)
	def widget(self, field, qset):
		return rest_list(qset)
	# def clean(self, qset):
	# 	return qset

class ToggleSet(object):
	def __init__(self, **kwargs):
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.force = None
	def static(self, field, qset):
		if qset:
			display = []
			for foreign in qset:
				display.append(foreign['static'])
			return rest_list(display)
	def widget(self, field, qset):
		if qset:
			display = []
			for foreign in qset:
				display.append(foreign['widget'])
			return rest_list(display)
	# def clean(self, value):
	# 	return None
	