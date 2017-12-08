from django.db import models
import bcrypt, re
from django.contrib.contenttypes.fields import GenericForeignKey
from django_mysql import models as sqlmod
from .utilities import get as _
from . import gistfile1 as gipi

class Bcrypt(object):
	def __init__(self, char60):
		self.full = char60 if char60[0] == '$' else char60[1:]
		self.html = '<span title='+self.full+'>&#x1f512;</span>'
	def __call__(self, pw):
		return bcrypt.checkpw(bytes(pw), bytes(self.full))
	def __str__(self):
		return self.full[:7]+self.full[55:]

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
		hashed = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt())
		if len(hashed) == 59:
			hashed = '+' + hashed
		return hashed

class PhoneNumber(object):
	def __init__(self, *num):
		self.num = num if type(num) is int else self.sanitize(num)
		self.cod  = self.num / 10**7
		self.mid  = self.num % 10**7 / 10**4
		self.last = self.num % 10**4
	def sanitize(self, *num):
		num = str(num)
		num = re.findall(r'\d',num)
		num = ''.join(num)
		num = int(num)
		num %= 10**10
		return num
	def __str__(self):
		return '('+str(self.cod)+') '+str(self.mid)+'-'+str(self.last)

class PhoneNumberField(models.DecimalField):
	def __init__(self):
		super(PhoneNumberField, self).__init__(max_digits=10, decimal_places=0)
	def pre_save(self, model_instance, add):
		num = getattr(model_instance, self.attname)
		# return PhoneNumber(num).sanitize()
		num = re.findall(r'\d',num)
		num = ''.join(num)
		return int(num)

class PolymorphicField(gipi.MultiColumnField):
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
	