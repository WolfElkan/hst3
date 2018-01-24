from django.db import models
import bcrypt, re
from django.contrib.contenttypes.fields import GenericForeignKey
from django_mysql import models as sqlmod
from .hacks import get as _
from . import gistfile1 as poly
from datetime import datetime

class Bcrypt(object):
	def __init__(self, char60):
		self.field = None
		self.char60 = char60
		self.full = char60 if char60[0] == '$' else char60[1:]
	def __call__(self, pw):
		return bcrypt.checkpw(bytes(pw), bytes(self.full))
	def __str__(self):
		return self.full[:7]+self.full[55:]
	def widget(self):
		pass
	def static(self):
		return '<span title='+self.full+'>&#x1f512;</span>'

class BcryptField(models.Field):
	def __init__(self):
		super(BcryptField,self).__init__()
	def db_type(self, connection):
		if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
			return 'CHAR(60)'
		else:
			return 'CHAR(60)' # TODO: Figure out equivalent field in other db softwares
	def pre_save(self, model_instance, add):
		plaintext = getattr(model_instance, self.attname)
		if type(plaintext) == Bcrypt:
			plaintext = plaintext.char60
		hashed = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt())
		if len(hashed) == 59:
			hashed = '+' + hashed
		return hashed


short_days = ['','Mon','Tue','Wed','Thu','Fri','Sat','Sun']
long_days = ['N/A','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

class DayOfWeek(object):
	def __init__(self, *value):
		self.field = None
		if value:
			if type(value) is tuple:
				value = value[0]
			if type(value) is DayOfWeek:
				self.value = int(value.value)
			elif type(value) in [int,float]:
				self.value = int(value)
			elif type(value) is datetime:
				self.value = value.isoweekday()
			elif type(value) in [str,unicode]:
				value = value.title()
				if value in short_days:
					self.value = short_days.index(value)
				elif value in long_days:
					self.value = long_days.index(value)
		else:
			self.value = 0
	def __str__(self):
		return long_days[self.value]
	def __int__(self):
		return self.value
	def __json__(self):
		return short_days[self.value]
	def widget(self, field, value):
		self.__init__(value)
		html = '<select name="{}">'.format(field)
		for x in range(len(short_days)):
			html += '<option value="{}"{}>{}</option>'.format(x,' selected' if self.value == x else '', short_days[x])
		html += '</select>'
		return html
	def static(self, field, value):
		self.__init__(value)
		return str(self)
	def clean(self, value):
		self.__init__(value)
		# print self.value
		return short_days[self.value]
		
class DayOfWeekField(sqlmod.EnumField):
	def __init__(self, **kwargs):
		kwargs['choices'] = short_days
		super(DayOfWeekField, self).__init__(**kwargs)
	def from_db_value(self, value, col, wrapper, options):
		return DayOfWeek(value)


class PhoneNumber(object):
	def __init__(self, *value):
		self.field = None
		self.force = False
		if value:
			if type(value) is tuple:
				value = value[0]
			if type(value) is PhoneNumber:
				self.value = value.value
			elif type(value) is int:
				self.value = value 
			else:
				self.value = self.sanitize(value)
			self.cod  = str(self.value / 10**7).zfill(3)
			self.mid  = str(self.value % 10**7 / 10**4).zfill(3)
			self.last = str(self.value % 10**4).zfill(4)
	def sanitize(self, *value):
		value = value if value else self.value
		value = str(value)
		value = re.findall(r'\d',value)
		if len(value) == 0:
			return 0
		value = ''.join(value)
		value = int(value)
		value %= 10**10
		return value
	def __int__(self):
		return self.value
	def __str__(self):
		return '('+self.cod+') '+self.mid+'-'+self.last if self.value else ''
	def __get__(self):
		return int(self.value)
	def widget(self, field, value):
		self.__init__(value)
		if value:
			value = int(value)
		return '<input type="number" name="{}" value="{}">'.format(field, value)
	def static(self, field, value):
		self.__init__(value)
		if value:
			return str(self)
	def clean(self, value):
		self.__init__(value)
		return self.value

class PhoneNumberField(models.DecimalField):
	def __init__(self, **kwargs):
		kwargs['max_digits'] = 10
		kwargs['decimal_places'] = 0
		super(PhoneNumberField, self).__init__(**kwargs)
	def pre_save(self, model_instance, add):
		num = getattr(model_instance, self.attname)
		return PhoneNumber(num).sanitize()
	def from_db_value(self, value, col, wrapper, options):
		return PhoneNumber(value)


class ZipCode(object):
	def __init__(self, *value):
		self.field = None
		if value:
			if type(value) is tuple:
				self.value = value[0]
			elif type(value) is ZipCode:
				self.value = value.value
			elif type(value) is str:
				self.value = float(value.replace('-','.'))
			else:
				self.value = value
			self.value = float(self.value)
		else:
			self.value = 00000.0000
	def __str__(self):
		result = str(int(self.value)).zfill(5)
		if self.value % 1:
			result += '-' + str(self.value)[-4:]
		return result
	def __float__(self):
		return self.value
	def __int__(self):
		return int(self.value)
	def static(self, field, value):
		self.__init__(value)
		return str(self)
	def widget(self, field, value):
		self.__init__(value)
		return '<input type="number" name="{}" value="{}" step="0.0001"> (If adding an extra 4 digits, use a decimal point in place of a dash)'.format(field, self.value)
	def clean(self, value):
		self.__init__(value)
		return self.value

class ZipCodeField(models.DecimalField):
	def __init__(self, **kwargs):
		kwargs['max_digits'] = 9
		kwargs['decimal_places'] = 4
		super(ZipCodeField, self).__init__(**kwargs)
	def from_db_value(self, value, col, wrapper, options):
		return ZipCode(value)


class PolymorphicField(poly.MultiColumnField):
	def __init__(self, attname, manager, relatables):
		self.attname = str(attname)
		self.manager = manager
		self.relatables = relatables
		self.relatable_names = []
		for rel in relatables:
			self.relatable_names += [rel.__name__.title()]
		self.fields = {
			'type': sqlmod.EnumField(null=True, choices=self.relatable_names),
			'id'  : models.PositiveIntegerField(null=True, rel=True),
		}
		this = self
		old_create = self.manager.create
		def new_create(self, thing):
			attr = thing.pop(this.attname)
			thing[this.attname + '_type'] = attr.__class__.__name__.title()
			thing[this.attname + '_id'] = attr.id
			return old_create(self, thing)
		self.manager.create = new_create
	def __get__(self, thing, model):
		_type = _(thing , self.attname + '_type').title()
		_id = _(thing , self.attname + '_id')
		model_index = self.relatable_names.index(_type)
		model = self.relatables[model_index]
		return model.objects.get(id=_id)
	
# https://djangosnippets.org/snippets/2513/
class TinyIntegerField(models.SmallIntegerField):
    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
            return "tinyint"
        else:
            return super(TinyIntegerField, self).db_type(connection)

class PositiveTinyIntegerField(models.PositiveSmallIntegerField):
    def db_type(self, connection):
        if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
            return "tinyint unsigned"
        else:
            return super(PositiveTinyIntegerField, self).db_type(connection)