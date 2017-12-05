from django.db import models
import bcrypt

class BcryptHash(object):
	def __init__(self, char60):
		self.hashed = char60 if char60[0] == '$' else char60[1:]
	def __call__(self, pw):
		return bcrypt.checkpw(bytes(pw), bytes(self.hashed))
	def __str__(self):
		return self.hashed[:6]+'...'+self.hashed[55:]
	def full(self):
		return self.hashed

class BcryptField(models.Field):
	description = "A string password encrypted with bcrypt"
	def db_type(self, connection):
		if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
			return 'char(60)'
		else:
			return 'char(60)' # TODO: Figure out equivalent field in other db softwares
	def pre_save(self, model_instance, add):
		plaintext = getattr(model_instance, self.attname)
		hashed = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt())
		if len(hashed) == 59:
			hashed = '+' + hashed
		return hashed
	def __value__(self, obj):
		char60 = getattr(obj, self.attname)
		return BcryptHash(char60)

class PolymorphicField(models.Field):
	def __init__(self, contentable_models):
		self.models = contentable_models
		self.type_col_name = self.attname+'_type'
		self.id_col_name = self.attname+'_id'
	def db_type(self, connection):
		# somehow make two db Integer columns:
		#   self.type_col_name
		#   self.id_col_name
		pass
	def pre_save(self, model_instance, add):
		pass
	def __value__(self, obj):
		_type = getattr(obj, self.type_col_name)
		_id = getattr(obj, self.id_col_name)
		return self.models[_type].objects.get(id=_id)

