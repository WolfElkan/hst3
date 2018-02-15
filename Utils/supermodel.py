from __future__ import unicode_literals
from django.db import models, connection
from datetime import datetime
import re
from .data import find

class Validation(object):
	def __init__(self, field, error):
		self.field = field
		self.error = error
		self.types = [object]
	def __missing(self, data):
		return self.field not in data
	def __mistype(self, data):
		return type(data[self.field]) not in self.types
	def isValid(self, data, **kwargs):
		andLast = kwargs['andLast'] if 'andLast' in kwargs else True
		return andLast and self.__valid(data)
	def errors(self, data, messages):
		if not self.__valid(data):
			if self.field not in messages:
				messages[self.field] = self.error
			else:
				messages[self.field] += ' ' + self.error
		return messages
	def __json__(self):
		return {
			'field':self.field,
			'regex':self.regex,
			'error':self.error,
		}

class Regular(Validation):
	def __init__(self, field, regex, error):
		super(Regular, self).__init__(field, error)
		self.regex = regex
		self.types = [str,unicode,buffer]
	def __mistype(self, data):
		return type(data[self.field]) not in self.types
	def __valid(self, data):
		datum = find(data, self.field)
		return self.__mistype(data) or re.match(self.regex, datum)
	def isValid(self, data, **kwargs):
		andLast = kwargs['andLast'] if 'andLast' in kwargs else True
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
		datum = find(data, self.field)
		return self.__mistype(data) or re.match(self.regex, datum)
	def isValid(self, data, **kwargs):
		andLast = kwargs['andLast'] if 'andLast' in kwargs else True
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
	def isValid(self, data, **kwargs):
		andLast = kwargs['andLast'] if 'andLast' in kwargs else True
		return andLast and self.__valid(data)
	def isValid(self, data, **kwargs):
		andLast = kwargs['andLast'] if 'andLast' in kwargs else True
		return andLast and self.__valid(data)
	# 	return messages
	def errors(self, data, messages):
		if not self.__valid(data):
			if self.field not in messages:
				messages[self.field] = self.error
			else:
				messages[self.field] += ' ' + self.error
		return messages

class Confirm(Validation):
	def __init__(self, field, other, error):
		self.field = field
		self.other = other
		self.error = error
		self.types = [str,unicode,buffer]
	def __mistype(self, data):
		return type(data[self.field]) not in self.types
	def __valid(self, data):
		return self.__mistype(data) or data[self.field] == data[self.other]
	def isValid(self, data, **kwargs):
		andLast = kwargs['andLast'] if 'andLast' in kwargs else True
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
	def __init__(self, field, lam, error):
		self.lam = lam
	def __valid(self, data):
		return self.lam(data)

class SuperManager(models.Manager):
	def __init__(self, table_name):
		self.name = 'objects'
		self._db = None
		self._hints = {}
		self.table_name = table_name
		self.fields = []
		self.validations = []
	def isValid(self, data, **kwargs):
		partial = 'partial' in kwargs and kwargs['partial']
		valid = True
		for x in self.validations:
			if not partial or x.field in data:
				valid = x.isValid(data, andLast=valid)
		return valid
	def errors(self, data, **kwargs):
		partial = 'partial' in kwargs and kwargs['partial']
		messages = {}
		for x in self.validations:
			if not partial or x.field in data:
				messages = x.errors(data, messages)
		return messages
	def fetch(self, **kwargs):
		qset = self.filter(**kwargs)
		if qset:
			return qset[0]
