from django.db import models
import bcrypt, re
from django.contrib.contenttypes.fields import GenericForeignKey
from django_mysql import models as sqlmod
from .hacks import get as _
from . import gistfile1 as poly

class Bcrypt(object):
	def __init__(self, char60):
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
long_days = [None,'Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']

class DayOfWeek(object):
	# TODO: Passing a datetime object into DayOfWeek returns that datetime's day of the week.
	def __init__(self, short):
		self.num = short_days.index(short)
	def __str__(self):
		return long_days[self.num]
	def __int__(self):
		return self.num
		
class DayOfWeekField(sqlmod.EnumField):
	def __init__(self, **kwargs):
		kwargs['choices'] = short_days
		# kwargs['max_length'] = 3
		super(DayOfWeekField, self).__init__(**kwargs)
	# def to_python(self, value):
	# 	return DayOfWeek(value)


class PhoneNumber(object):
	def __init__(self, *num):
		self.force = False
		if num:
			if type(num) is tuple:
				num = num[0]
			if type(num) is PhoneNumber:
				self.num = num.num
			elif type(num) is int:
				self.num = num 
			else:
				self.num = self.sanitize(num)
			self.cod  = str(self.num / 10**7).zfill(3)
			self.mid  = str(self.num % 10**7 / 10**4).zfill(3)
			self.last = str(self.num % 10**4).zfill(4)
	def sanitize(self, *num):
		num = num if num else self.num
		num = str(num)
		num = re.findall(r'\d',num)
		if len(num) == 0:
			return 0
		num = ''.join(num)
		num = int(num)
		num %= 10**10
		return num
	def __int__(self):
		return self.num
	def __str__(self):
		return '('+self.cod+') '+self.mid+'-'+self.last
	def __get__(self):
		return int(self.num)
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
		return self.num


class PhoneNumberField(models.DecimalField):
	def __init__(self, **kwargs):
		kwargs['max_digits'] = 10
		kwargs['decimal_places'] = 0
		super(PhoneNumberField, self).__init__(**kwargs)
	def pre_save(self, model_instance, add):
		num = getattr(model_instance, self.attname)
		return PhoneNumber(num).sanitize()

class ZipCode(object):
	def __init__(self, *value):
		if value:
			if type(value) is tuple and len(value) == 1:
				self.value = value[0]
			else:
				self.value = value
	def __str__(self):
		result = str(int(self.value)).zfill(5)
		if not self.value._isinteger():
			result += '-' + str(self.value)[-4:]
		return result
	def static(self, field, value):
		self.__init__(value)
		return str(self)
	def widget(self, field, value):
		if value:
			value = float(value)
		return '<input type="number" name="{}" value="{}" step="0.0001">'.format(field, value)
	def clean(self, value):
		return value if value else 0

class ZipCodeField(models.DecimalField):
	def __init__(self, **kwargs):
		kwargs['max_digits'] = 9
		kwargs['decimal_places'] = 4
		super(ZipCodeField, self).__init__(**kwargs)
	def to_python(self, value):
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