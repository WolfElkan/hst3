# - - - - - DEPENDENCIES - - - - -

from __future__ import unicode_literals
from django.db import models, connection
from datetime import datetime
import re
from .utilities import get

# - - - - - CLASSES - - - - -

class Validation(object):
	def __init__(self, field, regex, error):
		self.field = field
		self.regex = regex
		self.error = error
		self.types = (str,unicode,buffer)
	def __mistype(self, data):
		return not isinstance(data[self.field],self.types)
	def __valid(self, data):
		# print '*'*100
		datum = get(data, self.field)
		# print datum
		return self.__mistype(data) or re.match(self.regex, datum) != None
	def isValid(self, data, andLast=True):
		return andLast and self.__valid(data)
	def errors(self, data, messages):
		if not self.__valid(data):
			messages += [self.error]
		return messages

class Confirmation(Validation):
	def __init__(self, field, other, error):
		super(Confirmation, self).__init__()
		self.other = other
		self.types = (object)
	def __valid(self, data):
		return self.__mistype(data) or data[self.field] == data[self.other]

class FutureDate(Validation):
	def __init__(self, field, error):
		super(FutureDate, self).__init__()
		self.types = (datetime)
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
		self.types = (int,float,datetime)
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
	def __init__(self, app, table):
		self.name   = 'objects'
		self._db    = None
		self._hints = {}
		self.table_name  = app + '_' + table
		self.fields = []
		self.validations = []
	def isValid(self, data):
		valid = True
		for x in self.validations:
			# datum = data[x.field]
			valid = x.isValid(data, valid)
		return valid
	def errors(self, data):
		messages = []
		for x in self.validations:
			datum = data[x.field]
			messages = x.errors(datum, messages)
		return messages
	def create(self, new_thing):
		super(SuperManager, self).create(**new_thing)

def quickvalid(request, form, valid_bool, field, message):
	if valid_bool:
		request.session[form][field]['e'] = ""
	else:
		request.session[form][field]['e'] = message