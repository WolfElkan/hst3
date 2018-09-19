from django.db.models.query import QuerySet
from inspect import getargspec # Update getargspec -> signature in Python3

def allify(obj):
	if hasattr(obj,'all'):
		return obj.all()
	else:
		return obj

def collect(thing, lam):
	if type(thing) in [list, tuple, QuerySet]:
		new = []
		nargs = len(getargspec(lam).args)
		if nargs == 1:
			for x in thing:
				new.append(lam(x))
		elif nargs == 2:
			for t in range(len(thing)):
				new.append(lam(thing[t],t))
	elif hasattr(thing, '__dict__'):
		new = {}
		for key in thing:
			new[key] = lam(thing[key])
	else:
		new = thing.copy()
	return new

# https://stackoverflow.com/questions/3420122/filter-dict-to-contain-only-certain-keys
def copy(source, keys=False, trunc=0):
	this = {}
	if not keys:
		keys = source.keys()
	for key in keys:
		trunckey = key[trunc:]
		if key in source:
			this[trunckey] = source[key]
		else:
			this[trunckey] = None
	return this

# Keep
def copyatts(source, keys, ifnull=True):
	this = {}
	for key in keys:
		if hasattr(source, key):
			val = source.__getattribute__(key)
			if val or type(val) is bool or ifnull:
				this[key] = val
		else:
			this[key] = None
	return this

import re
from datetime import datetime

#               Thu Mar 22 2018 20:06:56 GMT-0400 (EDT)
def cleandate(string):
	months = [0,'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	pattern = r'[a-z]{3} [a-z]{3} [0-9]{2} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}'
	dic = re.match(pattern, string, flags=re.I)
	tz = re.search(r'GMT([+-][0-9]{4})',string).group(1)
	naive = datetime.strptime(dic.group(0),'%a %b %d %Y %H:%M:%S')
	zone = datetime.now()
	return datetime.replace(naive,tzinfo=tz)

class Each(object):
	def __init__(self, content):
		self._content = allify(content._content if type(content) is Each else content)
	def __iter__(self):
		for item in self._content:
			yield item
	def __len__(self):
		return len(self._content)
	def __repr__(self):
		return 'Each({})'.format(self._content)
	def __str__(self):
		return 'Each({})'.format(self._content)
	def __setattr__(self, attr, value):
		if attr == '_content':
			super(Each, self).__setattr__(attr, value)
		else:
			for item in self._content:
				item.__setattr__(attr, value)
	def __getattribute__(self, attr):
		if attr == '_content':
			return super(Each, self).__getattribute__(attr)
		else:
			new_content = []
			for item in self._content:
				result = item.__getattribute__(attr)
				new_content.append(result)
			return Each(new_content)
	def __call__(self, *args, **kwargs):
		new_content = []
		for item in self._content:
			if callable(item):
				new_content.append(item(*args, **kwargs))
			else:
				new_content.append(item)
		return Each(new_content)

# class Each(object):
# 	def __init__(self, arr):
# 		print arr
# 		self.arr = arr
# 	def __getattribute__(self, attr):
# 		if attr == '_':
# 			return super(Each,self).__getattribute__('arr')
# 		else:
# 			return Caller(super(Each,self).__getattribute__('arr'), attr)
# 	def __iter__(self):
# 		for x in super(Each,self).__getattribute__('arr'):
# 			yield x
# 	def __str__(self):
# 		return '<'+str(super(Each,self).__getattribute__('arr'))+'>'
# 	def __repr__(self):
# 		return '<Each: {}>'.format(str(super(Each,self).__getattribute__('arr')))
# 	def __len__(self):
# 		return len(super(Each,self).__getattribute__('arr'))
	# def __setattr__(self, attr, value):
	# 	for x in super(Each,self).__getattribute__('arr'):
	# 		x.__setattr__(attr, value)
	# 		print type(x)
	# 		if type(x) is QuerySet:
	# 			x.save()
	# 	return self

def equip(arr, lam, **kwargs):
	for x in arr:
		if 'item' in kwargs:
			x.__setitem__(kwargs['item'],lam(x))
		if 'attr' in kwargs:
			x.__setattr__(kwargs['attr'],lam(x))
	return list(arr)

def find(obj, key):
	key = str(key)
	return obj.get(key) if hasattr(obj, 'get') else getattr(obj, key)

def find_all(arr, lam):
	new = []
	for x in arr:
		if lam(x):
			new.append(x)
	return new

def serial(manager, column, **query):
	qset = manager.filter(**query)
	arr = Each(qset).__getattribute__(column)
	return max(arr) + 1 if arr else 1

# There might be a Python built-in method for this
def sub(val, dic):
	if val in dic:
		return dic[val]
	else:
		return val