# - - - - - DEPENDENCIES - - - - -

from __future__ import unicode_literals
from django.db import models, connection
from datetime import datetime
import re
from .utilities import get, copy

# - - - - - CLASSES - - - - -

class Validation(object):
	def __init__(self, field, error):
		# print '*'*50, 'Validation.__init__'
		self.field = field
		self.error = error
		self.types = [object]
	def __mistype(self, data):
		return type(data[self.field]) not in self.types
	def isValid(self, data, andLast=True):
		return andLast and self.__valid(data)
	def errors(self, data, messages):
		if not self.__valid(data):
			if self.field not in messages:
				messages[self.field] = self.error
			else:
				messages[self.field] += ' ' + self.error
		return messages

class Regular(Validation):
	def __init__(self, field, regex, error):
		super(Regular, self).__init__(field, error)
		self.regex = regex
		self.types = [str,unicode,buffer]
	def __mistype(self, data):
		return type(data[self.field]) not in self.types
	def __valid(self, data):
		datum = get(data, self.field)
		return self.__mistype(data) or re.match(self.regex, datum)
	def isValid(self, data, andLast=True):
		return andLast and self.__valid(data)
	def errors(self, data, messages):
		if not self.__valid(data):
			if self.field not in messages:
				messages[self.field] = self.error
			else:
				messages[self.field] += ' ' + self.error
		return messages

class Present(Regular):
	def __init__(self, field, error):
		super(Present, self).__init__(field, r'.+', error)
	def __mistype(self, data):
		return type(data[self.field]) not in self.types
	def __valid(self, data):
		datum = get(data, self.field)
		return self.__mistype(data) or re.match(self.regex, datum)
	def isValid(self, data, andLast=True):
		return andLast and self.__valid(data)
	def errors(self, data, messages):
		if not self.__valid(data):
			if self.field not in messages:
				messages[self.field] = self.error
			else:
				messages[self.field] += ' ' + self.error
		return messages

class Unique(Validation):
	def __init__(self, manager, field, error):
		self.manager = manager
		self.field = field
		self.error = error
		self.types = [str,unicode,buffer]
	def __mistype(self, data):
		return type(data[self.field]) not in self.types
	def __valid(self, data):
		return not self.manager.filter(**{self.field:data[self.field]})
	def isValid(self, data, andLast=True):
		return andLast and self.__valid(data)
	def isValid(self, data, andLast=True):
		return andLast and self.__valid(data)
	# 	return messages
	def errors(self, data, messages):
		if not self.__valid(data):
			if self.field not in messages:
				messages[self.field] = self.error
			else:
				messages[self.field] += ' ' + self.error
		return messages

class Confirmation(Validation):
	def __init__(self, field, other, error):
		self.field = field
		self.other = other
		self.error = error
		self.types = [object]
	def __mistype(self, data):
		return type(data[self.field]) not in self.types
	def __valid(self, data):
		return self.__mistype(data) or data[self.field] == data[self.other]
	def isValid(self, data, andLast=True):
		return andLast and self.__valid(data)
	def errors(self, data, messages):
		if not self.__valid(data):
			if self.field not in messages:
				messages[self.field] = self.error
			else:
				messages[self.field] += ' ' + self.error
		return messages

class FutureDate(Validation):
	def __init__(self, field, error):
		super(FutureDate, self).__init__()
		self.types = [datetime]
	def __valid(self, data):
		datum = data[self.field]
		return self.__mistype(data) or datum > datetime.date(datetime.now())

class PastDate(FutureDate):
	def __valid(self, data):
		datum = data[self.field]
		return self.__mistype(data) or datum < datetime.date(datetime.now())

class Comparison(Validation):
	def __init__(self, field, after, error):
		super(Comparison, self).__init__()
		self.after = after
		self.types = [int,float,datetime]
	def __mistype(self, data):
		return False
	def __valid(self, data):
		datum = data[self.field]
		latum = data[self.after]
		datum_bad = not isinstance(datum,self.types)
		latum_bad = not isinstance(latum,self.types)
		different = type(datum) != type(latum)
		mistype = datum_bad or latum_bad or different
		return mistype or datum < latum

class Manual(Validation):
	def __init__(self, field, valid, error):
		super(Confirmation, self).__init__()
		self.valid = valid
	def __valid(self, data):
		return self.valid

class Field(object):
	def __init__(self, fields_array, name, data_type, *validations):
		kwargs = ""
		chars = re.search(r'(?<=[Cc]har)\d*',data_type)
		if chars:
			kwargs = "max_length={}".format(chars.group())
			data_type = "Char"
		column = "{}=models.{}Field({})".format(name, data_type, kwargs)
		exec(column)
		fields_array += [self]

class SuperManager(models.Manager):
	def __init__(self, app_name, ic):
		# print '*'*50, 'SuperManager.__init__'
		self.name = 'objects'
		self._db = None
		self._hints = {}
		if type(ic) in [str,unicode]:
			self.ic = None
			self.class_name = ic
		else:
			self.ic = ic
			self.class_name = ic.__name__
		self.table_name = app_name + '_' + self.class_name.lower()
		self.fields = []
		self.validations = []
	def isValid(self, data):
		# print '*'*50, 'SuperManager.isValid'
		valid = True
		for x in self.validations:
			valid = x.isValid(data, valid)
		return valid
	def errors(self, data):
		# print '*'*50, 'SuperManager.isValid'
		messages = {}
		for x in self.validations:
			messages = x.errors(data, messages)
		return messages
	def create(self, data):
		new_thing = copy(data,self.fields)
		return super(SuperManager, self).create(**new_thing)
	def get(self, **kwery):
		got_thing = super(SuperManager, self).get(**kwery)
		if self.ic:
			return self.ic(got_thing)
		else:
			return got_thing
