from apps.people.managers import Addresses, Families, Parents, Users, Students
from apps.people.models import Teacher
Teachers = Teacher.objects
from apps.program.managers import Courses, CourseTrads, Enrollments, Venues
from apps.payment.managers import Invoices
#from trace import TRACE
TRACE = False

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
	'venue'     : Venues,
}


def rest_link(foreign):
	if foreign:
		extra = ' (#{})'.format(foreign.id) if foreign.rest_model in ['family','student','parent'] else ''
		return '<a href="/rest/show/{}/{}/">{}{}</a>'.format(foreign.rest_model,foreign.id,str(foreign),extra)
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
		self.field = kwargs.setdefault('field', None)
		self.default = kwargs.setdefault('default', '')
		self.maxlength = kwargs.setdefault('maxlength', None)
	def widget(self, field, value, **kwargs):
		return '<input type="text" maxlength="{}" name="{}" value="{}">'.format(self.maxlength, field, value)
	def static(self, field, value):
		self.field = field
		return value
	def merge(self, old, new):
		if self.field == 'id':
			return ''
		else:
			return '''
		<form action="copy/">
			<input type="hidden" name="field" value="{field}">
			<button>Copy&rarr;</button>
		</form>
		<form action="transfer/">
			<input type="hidden" name="field" value="{field}">
			<input type="hidden" name="blank" value="">
			<button>Transfer&rarr;</button>
		</form>
		'''.format(field=self.field)
	def set(self, thing, field, post, isAttr):
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
		self.field = kwargs.setdefault('field', None)
		self.suffix = kwargs.setdefault('suffix', '')
		self.default = kwargs.setdefault('default', 0)
	def widget(self, field, value, **kwargs):
		if value:
			value = int(value)
		return '<input type="number" name="{}" value="{}"> {}'.format(field, value, self.suffix)
	def static(self, field, value):
		self.field = field
		return '<div>{} {}</div>'.format(value, self.suffix) if value else '<div>0</div>'
	def merge(self, old, new):
		return '''
		<form action="copy/">
			<input type="hidden" name="field" value="{field}">
			<button>Copy&rarr;</button>
		</form>
		<form action="transfer/">
			<input type="hidden" name="field" value="{field}">
			<input type="hidden" name="blank" value="{default}">
			<button>Transfer&rarr;</button>
		</form>
		'''.format(field=self.field,default=self.default)
	def set(self, thing, field, post, isAttr):
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
		self.field = kwargs.setdefault('field', None)
		self.items = kwargs.setdefault('items', [])
		if hasattr(self.items, 'items'):
			self.items = self.items.items()
		self.options = kwargs.setdefault('options', [])
		self.default = kwargs.setdefault('default', self.items[0][0] if self.items else self.options[0])
	def widget(self, field, value, **kwargs):
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
		self.field = field
		if self.items:
			return dict(self.items).get(value)
		else:
			return value
	def merge(self, old, new):
		return '''
		<form action="copy/">
			<input type="hidden" name="field" value="{field}">
			<button>Copy&rarr;</button>
		</form>
		<form action="swap/">
			<input type="hidden" name="field" value="{field}">
			<button>&larr;Swap&rarr;</button>
		</form>
		'''.format(field=self.field,default=self.default)
	def set(self, thing, field, post, isAttr):
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
		self.field = kwargs.setdefault('field', None)
		self.options = kwargs.setdefault('options', [])
		self.default = kwargs.setdefault('default', 0)
	def widget(self, field, value, **kwargs):
		value = value if value else 0
		html = ''
		for o in range(len(self.options)):
			html += '<input type="radio" name="{}" value="{}" {}>{}<br>'.format(field, o,' checked' if value == o else '',self.options[o])
		return html
	def static(self, field, value):
		self.field = field
		value = value if value else 0
		return self.options[value]
	def set(self, thing, field, post, isAttr):
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
		self.field = kwargs.setdefault('field', None)
		self.suffix = kwargs.setdefault('suffix', '')
		self.default = kwargs.setdefault('default', False)
	def widget(self, field, value, **kwargs):
		return '<input type="checkbox" name="{}" {}> {}'.format(field, ' checked' if value else '',self.suffix)
	def static(self, field, value):
		self.field = field
		return 'Yes' if value else 'No'
	def merge(self, old, new):
		return '''
		<form action="copy/">
			<input type="hidden" name="field" value="{field}">
			<button>Copy&rarr;</button>
		</form>
		<form action="swap/">
			<input type="hidden" name="field" value="{field}">
			<button>&larr;Swap&rarr;</button>
		</form>
		'''.format(field=self.field,default=self.default)
	def set(self, thing, field, post, isAttr):
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
	def merge(self, old, new):
		return '''
		<form action="copy/">
			<input type="hidden" name="field" value="{field}">
			<button>Copy&rarr;</button>
		</form>
		<form action="transfer/">
			<input type="hidden" name="field" value="{field}">
			<input type="hidden" name="blank" value="-">
			<button>Transfer&rarr;</button>
		</form>
		'''.format(field=self.field)
		

class Date(object):
	def __init__(self, **kwargs):
		self.field = kwargs.setdefault('field', None)
		self.default = kwargs.setdefault('default', None)
	def widget(self, field, value, **kwargs):
		return '<input type="date" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		self.field = field
		if value:
			return value.strftime('%B %-d, %Y')
	def merge(self, old, new):
		return '''
		<form action="copy/">
			<input type="hidden" name="field" value="{field}">
			<button>Copy&rarr;</button>
		</form>
		<form action="transfer/">
			<input type="hidden" name="field" value="{field}">
			<input type="hidden" name="blank" value="2020-12-31">
			<button>Transfer&rarr;</button>
		</form>
		<form action="swap/">
			<input type="hidden" name="field" value="{field}">
			<button>&larr;Swap&rarr;</button>
		</form>
		'''.format(field=self.field)
	def set(self, thing, field, post, isAttr):
		# return thing
		if field in post:
			value = post[field]
		if value:
			if isAttr:
				thing.__setattr__(field, str(value))
			else:
				thing.__setitem__(field, str(value))
		return thing

class Time(object):
	def __init__(self, **kwargs):
		self.field = kwargs.setdefault('field', None)
		self.default = kwargs.setdefault('default', None)
	def widget(self, field, value, **kwargs):
		return '<input type="time" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		self.field = field
		if value:
			return value.strftime('<div>%-I:%M %p</div>')
	def merge(self, old, new):
		return '''
		<form action="copy/">
			<input type="hidden" name="field" value="{field}">
			<button>Copy&rarr;</button>
		</form>
		<form action="transfer/">
			<input type="hidden" name="field" value="{field}">
			<input type="hidden" name="blank" value="00:00:00">
			<button>Transfer&rarr;</button>
		</form>
		<form action="swap/">
			<input type="hidden" name="field" value="{field}">
			<button>&larr;Swap&rarr;</button>
		</form>
		'''.format(field=self.field)
	def set(self, thing, field, post, isAttr):
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
		self.field   = kwargs.setdefault('field'  , None)
		self.model   = kwargs.setdefault('model'  , None)
		self.null    = kwargs.setdefault('null'   , False)
		self.default = kwargs.setdefault('default', None)
		self.xstatic = kwargs.setdefault('static' , False)
	def widget(self, field, value, **kwargs):
		if self.xstatic:
			return self.static(field, value, **kwargs)
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
		self.field = field
		if value:
			return rest_link(value)
		elif self.xstatic:
			return '-'
		else:
			return '<a href="add/{}/">add</a>'.format(field)
	def merge(self, old, new):
		html = '' if self.field in ['mother','father'] else '''
			<form action="copy/">
				<input type="hidden" name="field" value="{field}">
				<button>Copy&rarr;</button>
			</form>'''
		html += '''
			<form action="transfer/">
				<input type="hidden" name="field" value="{field}">
				<button>Transfer&rarr;</button>
			</form>
		'''
		fargs = {
			'field':self.field,
			'default':self.default,
		}
		old_sub = old.__getattribute__(self.field)
		if old_sub:
			fargs['old_id'] = old_sub.id
		new_sub = new.__getattribute__(self.field)
		if new_sub:
			fargs['new_id'] = new_sub.id
		if old_sub and new_sub:
			fargs['model'] = old_sub.rest_model
			# JavaScript within HTML within Python.  What is this world coming to?
			html += '''<button onclick="window.location='/rest/merge/{model}/{old_id}/{new_id}/'">Sub Merge</button>'''
		html += ''
		return html.format(**fargs)
	def set(self, thing, field, post, isAttr):
		field += '_id'
		if field in post:
			value = post[field]
		else:
			value = self.default
		# if value == 'None':
		# 	value = None
		if str(value) in ['0','None']:
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
		self.field = field
		return value
	def merge(self, old, new):
		return ''
	def set(self, thing, field, post, isAttr):
		return thing

class ForeignSet(object):
	def __init__(self, **kwargs):
		self.field = kwargs.setdefault('field', None)
		self.model = kwargs.setdefault('model', None)
		self.default = kwargs.setdefault('default', None)
		self.reflex = kwargs.setdefault('reflex', None)
	def widget(self, field, qset, **kwargs):
		html = rest_list(qset)
		html += '<a class="plus" href="add/{}/">+</a>'.format(self.model)
		return html
	def static(self, field, qset):
		self.field = field
		return rest_list(qset)
	def merge(self, old, new):
		if self.field == 'accounts':
			return ''
		reflex = self.reflex if self.reflex else old.rest_model
		html ='''
		<form action="move_all/">
			<input type="hidden" name="field" value="{field}">
			<input type="hidden" name="reflex" value="{reflex}">
			<button>Move All&rarr;</button>
		</form>
		<form action="sub_move/">
			<input type="hidden" name="field" value="{field}">
			<input type="hidden" name="reflex" value="{reflex}">
			<button>Sub Move</button>
		</form>
		<form action="sub_merge/">
			<input type="hidden" name="field" value="{field}">
			<input type="hidden" name="reflex" value="{reflex}">
			<button>Sub Merge</button>
		</form>
		'''
		return html.format(field=self.field,reflex=reflex)
	def set(self, thing, field, post, isAttr):
		if field in post:
			value = post[field]
		else:
			value = self.default
		return thing

class ToggleSet(object):
	def __init__(self, **kwargs):
		self.field = kwargs.setdefault('field', None)
		self.model = kwargs.setdefault('model', None)
		self.default = kwargs.setdefault('default', None)
	def widget(self, field, qset, **kwargs):
		html = ''
		if qset:
			display = []
			for foreign in qset:
				display.append(foreign['widget'])
			html += rest_list(display)
		html += '<a class="plus" href="add/{}/">+</a>'.format(self.model)
		return html
	def static(self, field, qset):
		if qset:
			display = []
			for foreign in qset:
				display.append(foreign['static'])
			return rest_list(display)
	def set(self, thing, field, post, isAttr):
		if field in post:
			value = post[field]
		else:
			value = self.default
		return thing

# class YearAndCourse(object):
# 	def __init__(self, **kwargs):
# 		self.field = kwargs.setdefault('field', None)
# 		self.model = 'course'
		

# class Method(object):
# 	def __init__(self, **kwargs):
# 		self.params = kwargs.setdefault('params', [])
# 	def widget(self, **kwargs):
# 		return self.static()
# 	def static(self, field, **kwargs):
# 		return '<a class="button" href="method/{}/">{}</a>'.format(field, field)
# 	def set(self, thing, field, post, isAttr):
# 		return thing

# 		