from apps.people.managers import Addresses, Families, Parents, Users, Students
from apps.people.models import Teacher
Teachers = Teacher.objects
from apps.program.managers import Courses, CourseTrads, Enrollments
from apps.payment.managers import Invoices
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
	'audition'  : Enrollments,
	'invoice'   : Invoices,
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
		self.field = kwargs.setdefault('field', None		)
		self.default = kwargs.setdefault('default', '')
		self.maxlength = kwargs.setdefault('maxlength', None		)
	def widget(self, field, value, **kwargs):
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
		self.field = kwargs.setdefault('field', None)
		self.suffix = kwargs.setdefault('suffix', '')
		self.default = kwargs.setdefault('default', 0)
	def widget(self, field, value, **kwargs):
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
		self.field = kwargs.setdefault('field', None)
		self.items = kwargs.setdefault('items', [])
		if hasattr(self.items, 'items'):
			self.items = self.items.items()
		self.options = kwargs.setdefault('options', [])
		self.default = kwargs.setdefault('default', self.items[0][0] if self.items else self.options[0])
	def widget(self, field, value, **kwargs):
		if TRACE:
			print '# rest.widgets.Enum:widget'
		html = '<select name="{}">'.format(field)
		if self.items:
			for db, full in self.items:
				html += '<option value="{}"{}>{}</option>'.format(db,' selected' if value == db else '',full)
		elif self.options:
			for option in self.options:
				html += '<option value="{}"{}>{}</option>'.format(option,' selected' if value == option else '',option)
		html += '</select>'
		return html
	def static(self, field, value):
		if TRACE:
			print '# rest.widgets.Enum:static'
		if self.items:
			return dict(self.items).get(value)
		else:
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
		self.field = kwargs.setdefault('field', None)
		self.options = kwargs.setdefault('options', [])
		self.default = kwargs.setdefault('default', 0)
	def widget(self, field, value, **kwargs):
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
		self.field = kwargs.setdefault('field', None)
		self.suffix = kwargs.setdefault('suffix', '')
		self.default = kwargs.setdefault('default', False)
	def widget(self, field, value, **kwargs):
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
		self.field = kwargs.setdefault('field', None)
		self.default = kwargs.setdefault('default', None)
	def widget(self, field, value, **kwargs):
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
		self.field = kwargs.setdefault('field', None)
		self.default = kwargs.setdefault('default', None)
	def widget(self, field, value, **kwargs):
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

class ForeignKey(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.ForeignKey'
		self.field = kwargs.setdefault('field', None)
		self.model = kwargs.setdefault('model', None)
		self.null  = kwargs.setdefault('null', False)
		self.default = kwargs.setdefault('default', None)
	def widget(self, field, value, **kwargs):
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

class Static(object):
	def __init__(self, **kwargs):
		self.default = kwargs.setdefault('default',None)
		self.field = kwargs.setdefault('field',None)
		super(Static, self).__init__()
	def widget(self, field, value, **kwargs):
		return value
	def static(self, field, value):
		return value
	def set(self, thing, field, post, isAttr):
		return thing

class ForeignSet(object):
	def __init__(self, **kwargs):
		if TRACE:
			print '* rest.widgets.ForeignSet'
		self.field = kwargs.setdefault('field', None)
		self.model = kwargs.setdefault('model', None)
		self.default = kwargs.setdefault('default', None)
	def widget(self, field, qset, **kwargs):
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
		self.field = kwargs.setdefault('field', None)
		self.model = kwargs.setdefault('model', None)
		self.default = kwargs.setdefault('default', None)
	def widget(self, field, qset, **kwargs):
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
	