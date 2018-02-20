from django.db.models.query import QuerySet
from django.http.request import QueryDict
from inspect import getargspec # Update getargspec -> signature in Python3

class Caller(object):
	def __init__(self, arr, fx):
		self.arr = arr
		self.fx = fx
	def __str__(self):
		new = []
		for x in self.arr:
			new.append(x.__getattribute__(self.fx))
		return str(new)
	def __repr__(self):
		return '<Caller: {} @{}>'.format(self.arr,self.fx)
	def __iter__(self):
		for x in self.arr:
			yield x.__getattribute__(self.fx)
	def __call__(self, *args, **kwargs):
		new = []
		for x in self.arr:
			if hasattr(x, self.fx):
				new.append(x.__getattribute__(self.fx).__call__(*args, **kwargs))
			else:
				new.append(x)
		return Each(new)
	def __getattr__(self, attr):
		new = []
		for x in self.arr:
			new.append(x.__getattribute__(attr))
		return Caller(new, None)
	def setattr(self, attr, value):
		new = []
		for x in self.arr:
			x.__setattr__(attr, value)
			if type(x) is QuerySet:
				x.save()
			new.append(x)
		return Each(new)

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

class Each(object):
	def __init__(self, arr):
		self.arr = arr
	def __getattribute__(self, attr):
		if attr == '_':
			return super(Each,self).__getattribute__('arr')
		else:
			return Caller(super(Each,self).__getattribute__('arr'), attr)
	def __iter__(self):
		for x in super(Each,self).__getattribute__('arr'):
			yield x
	def __str__(self):
		return '<'+str(super(Each,self).__getattribute__('arr'))+'>'
	def __repr__(self):
		return '<Each: {}>'.format(str(super(Each,self).__getattribute__('arr')))
	def __len__(self):
		return len(super(Each,self).__getattribute__('arr'))
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

# There might be a Python built-in method for this
def sub(val, dic):
	if val in dic:
		return dic[val]
	else:
		return val