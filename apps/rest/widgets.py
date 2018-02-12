from apps.main.managers import Addresses, Families, Parents, Users, Students
from apps.main.models import Teacher
from apps.program.managers import Courses, CourseTrads, Enrollments, Auditions
from trace import TRACE

MODELS = {
	'address'   : Addresses,
	'family'    : Families,
	'parent'    : Parents,
	'mother'    : Parents,
	'father'    : Parents,
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
	if TRACE:
		print '# rest.widgets.rest_link'
	if foreign:
		return '<a href="/rest/show/{}/{}/">{}</a>'.format(foreign.rest_model,foreign.id,str(foreign))
	else:
		return ''

def rest_list(qset):
	if TRACE:
		print '# rest.widgets.rest_list'
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
		if TRACE:
			print '* rest.widgets.VarChar'
		self.field = kwargs['field'] if 'field' in kwargs else None		
		self.default = kwargs['default'] if 'default' in kwargs else ''
		self.maxlength = kwargs['maxlength'] if 'maxlength' in kwargs else None		
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.VarChar:widget'
		return '<input type="text" maxlength="{}" name="{}" value="{}">'.format(self.maxlength, field, value)
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.VarChar:static'
		return value
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.VarChar:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		if isAttr:
			thing.__setattr__(field, str(value))
		else:
			thing.__setitem__(field, str(value))
		return thing

class Integer(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.Integer'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.suffix = kwargs['suffix'] if 'suffix' in kwargs else ''
		self.default = kwargs['default'] if 'default' in kwargs else 0
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.Integer:widget'
		if value:
			value = int(value)
		return '<input type="number" name="{}" value="{}"> {}'.format(field, value, self.suffix)
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.Integer:static'
		return '<div>{} {}</div>'.format(value, self.suffix) if value else '<div>0</div>'
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.Integer:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		if isAttr:
			thing.__setattr__(field, value if value else 0)
		else:
			thing.__setitem__(field, value if value else 0)
		return thing

class Enum(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.Enum'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.options = kwargs['options'] if 'options' in kwargs else []
		self.default = kwargs['default'] if 'default' in kwargs else self.options[0]
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.Enum:widget'
		html = '<select name="{}">'.format(field)
		for option in self.options:
			html += '<option value="{}"{}>{}</option>'.format(option,' selected' if value == option else '',option)
		html += '</select>'
		return html
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.Enum:static'
		return value
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.Enum:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		if isAttr:
			thing.__setattr__(field, str(value))
		else:
			thing.__setitem__(field, str(value))
		return thing
		
class Radio(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.Radio'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.options = kwargs['options'] if 'options' in kwargs else []
		self.default = kwargs['default'] if 'default' in kwargs else 0
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.Radio:widget'
		value = value if value else 0
		html = ''
		for o in range(len(self.options)):
			html += '<input type="radio" name="{}" value="{}" {}>{}<br>'.format(field, o,' checked' if value == o else '',self.options[o])
		return html
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.Radio:static'
		value = value if value else 0
		return self.options[value]
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.Radio:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		if isAttr:
			thing.__setattr__(field, value)
		else:
			thing.__setitem__(field, value)
		return thing

class Checkbox(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.Checkbox'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.suffix = kwargs['suffix'] if 'suffix' in kwargs else ''
		self.default = kwargs['default'] if 'default' in kwargs else False
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.Checkbox:widget'
		return '<input type="checkbox" name="{}" {}> {}'.format(field, ' checked' if value else '',self.suffix)
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.Checkbox:static'
		return 'Yes' if value else 'No'
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.Checkbox:set'
		if field in post:
			value = str(post[field]) == 'on'
		else:
			value = self.default
		if isAttr:
			thing.__setattr__(field, value)
		else:
			thing.__setitem__(field, value)
		return thing

class NullBoolean(Enum):
	def __init__(self):
		super(NullBoolean, self).__init__(options=['-','No','Yes'])
		

class Date(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.Date'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.default = kwargs['default'] if 'default' in kwargs else None
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.Date:widget'
		return '<input type="date" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.Date:static'
		if value:
			return value.strftime('%B %-d, %Y')
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.Date:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		if isAttr:
			thing.__setattr__(field, str(value) if value else '0000-00-00')
		else:
			thing.__setitem__(field, str(value) if value else '0000-00-00')
		return thing

class Time(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.Time'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.default = kwargs['default'] if 'default' in kwargs else None
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.Time:widget'
		return '<input type="time" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.Time:static'
		if value:
			return value.strftime('<div>%-I:%M %p</div>')
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.Time:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		if isAttr:
			thing.__setattr__(field, str(value) if value else '00:00')
		else:
			thing.__setitem__(field, str(value) if value else '00:00')
		return thing

class Dollar(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.Dollar'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.default = kwargs['default'] if 'default' in kwargs else 0.00
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.Dollar:widget'
		if value:
			value = float(value)
		else:
			value = 0
		return '<input type="number" step="0.01" name="{}" value="{:.2f}">'.format(field, value)
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.Dollar:static'
		if value:
			value = float(value)
			return '<div>${:.2f}</div>'.format(value)
		else:
			return '<div>$0.00</div>'
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.Dollar:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		if isAttr:
			thing.__setattr__(field, str(value) if value else 0.00)
		else:
			thing.__setitem__(field, str(value) if value else 0.00)
		return thing

class ForeignKey(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.ForeignKey'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.model = kwargs['model'] if 'model' in kwargs else None
		self.null  = kwargs['null']  if 'null'  in kwargs else False
		self.default = kwargs['default'] if 'default' in kwargs else None
	def widget(self, field, value):
		if TRACE:
			print '# rest.widgets.ForeignKey:widget'
		self.field = field
		html = '<select name="{}_id">'.format(field)
		if not self.model:
			self.model = field
		if self.null:
			html += '<option value="0"{}>- select -</option>'.format(' selected' if not value else '')
		for foreign in MODELS[self.model].all():
			html += '<option value="{}"{}>{}</option>'.format(foreign.id,' selected' if value == foreign else '',foreign)
		html += '</select>'
		return html
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.ForeignKey:static'
		self.field = field
		if value:
			return rest_link(value)
		else:
			return '<a href="add/{}/">add</a>'.format(field)
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.ForeignKey:set'
		field += '_id'
		if field in post:
			value = post[field]
		else:
			value = self.default
		if str(value) == '0':
			return thing
		if isAttr:
			thing.__setattr__(field, str(value))
		else:
			thing.__setitem__(field, str(value))
		return thing

class ForeignSet(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.ForeignSet'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.model = kwargs['model'] if 'model' in kwargs else None
		self.default = kwargs['default'] if 'default' in kwargs else None
	def widget(self, field, qset):
		if TRACE:
			print '# rest.widgets.ForeignSet:widget'
		html = rest_list(qset)
		html += '<a class="plus" href="add/{}/">+</a>'.format(self.model)
		return html
	def static(self, field, qset):
		if TRACE:
			print '# rest.widgets.ForeignSet:static'
		return rest_list(qset)
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.ForeignSet:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		return thing

class ToggleSet(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.ToggleSet'
		self.field = kwargs['field'] if 'field' in kwargs else None
		self.model = kwargs['model'] if 'model' in kwargs else None
		self.default = kwargs['default'] if 'default' in kwargs else None
	def widget(self, field, qset):
		if TRACE:
			print '# rest.widgets.ToggleSet:widget'
		html = ''
		if qset:
			display = []
			for foreign in qset:
				display.append(foreign['widget'])
			html += rest_list(display)
		html += '<a class="plus" href="add/{}/">+</a>'.format(self.model)
		return html
	def static(self, field, qset):
		if TRACE:
			print '# rest.widgets.ToggleSet:static'
		if qset:
			display = []
			for foreign in qset:
				display.append(foreign['static'])
			return rest_list(display)
	def set(self, thing, field, post, isAttr):
		if TRACE:
			print '# rest.widgets.ToggleSet:set'
		if field in post:
			value = post[field]
		else:
			value = self.default
		return thing
	