from django.db import models
import bcrypt
from django.contrib.contenttypes.fields import GenericForeignKey
from django_mysql import models as sqlmod
from .utilities import get as _
from . import gistfile1 as gipi

class BcryptHash(object):
	def __init__(self, char60):
		self.hashed = char60 if char60[0] == '$' else char60[1:]
	def __call__(self, pw):
		return bcrypt.checkpw(bytes(pw), bytes(self.hashed))
	def __str__(self):
		trunc = self.hashed[:5]+'~'+self.hashed[55:]
		return u'\U0001f512 ' + unicode(trunc)
	def full(self):
		return self.hashed
	def html(self):
		return '<span title="%s">&#x1f512;</span>'.format(self.hashed)

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
	def __value__(self, obj):
		char60 = getattr(obj, self.attname)
		return BcryptHash(char60)

class PolymorphicIdField(models.PositiveIntegerField):
	def __init__(self):
		super(EnumField,self).__init__(rel=True)

class PolymorphicField(models.CharField):
	def __init__(self, manager, relatables):
		super(PolymorphicField,self).__init__(max_length=30)
		self.manager = manager
		self.relatables = relatables
		type_col_name = self.attname+'_type'
		id_col_name = self.attname+'_id'
		self.model[type_col_name] = EnumField(relatables)
		self.model[id_col_name] = PolymorphicIdField()
	def pre_save(self, model_instance, add):
		value = super(PolymorphicField,self).pre_save(model_instance, add)
		return value.__str__()
	def __value__(self, obj):
		_type = getattr(obj, self.type_col_name)
		_id = getattr(obj, self.id_col_name)
		return self.relatables[_type].objects.get(id=_id)

class PolymorphicField(gipi.MultiColumnField):
	def __init__(self, attname, manager, relatables):
		self.attname = str(attname)
		self.manager = manager
		self.relatables = []
		for rel in relatables:
			self.relatables += [rel if type(rel) in [str,unicode] else rel.__name__]
		self.fields = {
			'type': sqlmod.EnumField(null=True, choices=self.relatables),
			'id'  : models.PositiveIntegerField(null=True, rel=True),
		}
		this = self
		old_create = self.manager.create
		def new_create(self, thing):
			print '*'*100
			print thing
			attr = thing.pop(this.attname)
			thing[this.attname + '_type'] = attr.__class__.__name__
			thing[this.attname + '_id'] = attr.id
			return old_create(self, thing)
		self.manager.create = new_create
	# def pre_save(self, model_instance, add):
	# 	print model_instance
	# 	value = super(PolymorphicField,self).pre_save(model_instance, add)
	# 	return value
