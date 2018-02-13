from trace import TRACE, DEV

def get(obj, key):
	key = str(key)
	if type(obj) == dict:
		for kvp in obj.items():
			if kvp[0] == key:
				return kvp[1]
	else:
		return getattr(obj, key)

def metastr(query):
	clean = {}
	for key in query:
		clean[key] = str(query[key])
	return clean

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

def copy_items_to_attrs(this, source, *keys):
	if not keys:
		keys = source.keys()
	for key in keys:
		this.__setattr__(key, source[key])
	return this

# Function for initializing session variables.
def seshinit(request, sesh, val=''):
	if sesh not in request.session:
		request.session[sesh] = val

# Initialize form error/persist structure in session
def forminit(request, form_name, fields):
	for pe in 'pe':
		seshinit(request, pe, {})
		if form_name not in request.session[pe]:
			request.session[pe][form_name] = {}
			for f in fields:
				if f not in request.session[pe][form_name]:
					request.session[pe][form_name][f] = ''

# Select the first element in a query, without causing errors
def first(arr):
	if len(arr) == 0:
		return None
	else:
		return arr[0]

# Convert a list to a dict object, so it can be parsed correctly on front end
def numero(obj):
	result = {}
	for x in range(len(obj)):
		result['no'+str(x)] = obj[x]
	return result

# Just like numero, but meta
def metanumero(obj):
	result = []
	for x in obj:
		result += [numero(x)]
	return result

import json
class FriendlyEncoder(json.JSONEncoder):
	def default(self, obj):
		if TRACE:
			print '@ rest.seed.default'
		if hasattr(obj,'__json__'):
			return obj.__json__()
		else:
			return str(obj)

def json(obj):
	result = []
	for x in obj:
		result += [x.__dict__]
	result = str(result)
	result = result.replace('\'','"')
	result = result.replace('&quot','"')
	result = result.replace('u"','"')
	result = result.replace('<type ','')
	result = result.replace('>','')
	return result

def pretty(arr, delim='  ', indent='', level=0, printout=''):
	for thing in arr:
		if type(thing) is list:
			printout = pretty(thing, delim, indent+'['+delim, level+1, printout)
		else:
			printout += indent + str(thing) + '\n'
	return printout if level else printout[:-1]

def pdir(thing):
	return pretty(dir(thing))

def sub(val, dic):
	if val in dic:
		return dic[val]
	else:
		return val

# Return the current HST registration year (This year until May 1, next year thereafter)
from datetime import datetime
def year():
	if DEV:
		return 2018
	now = datetime.now()
	return now.year + (0 if now.month < 5 else 1)

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
			new.append(x.__getattribute__(self.fx).__call__(*args, **kwargs))
		return Each(new)
	def __getattr__(self, attr):
		new = []
		for x in self.arr:
			new.append(x.__getattribute__(attr))
		return new

class Each(object):
	def __init__(self, arr):
		self.arr = list(arr)
	def __str__(self):
		return '<'+str(super(Each,self).__getattribute__('arr'))+'>'
	def __repr__(self):
		return '<Each: {}>'.format(str(super(Each,self).__getattribute__('arr')))
	def __getattribute__(self, attr):
		if attr == '_':
			return super(Each,self).__getattribute__('arr')
		else:
			return Caller(super(Each,self).__getattribute__('arr'), attr)
	def __iter__(self):
		for x in super(Each,self).__getattribute__('arr'):
			yield x
	def __len__(self):
		return len(super(Each,self).__getattribute__('arr'))

def collect(arr, lam):
	new = []
	for x in arr:
		new.append(lam(x))
	return new

def find_all(arr, lam):
	new = []
	for x in arr:
		if lam(x):
			new.append(x)
	return new

def equip(arr, lam, **kwargs):
	for x in arr:
		if 'item' in kwargs:
			x.__setitem__(kwargs['item'],lam(x))
		if 'attr' in kwargs:
			x.__setattr__(kwargs['attr'],lam(x))
	return list(arr)

import re
def namecase(name):
	if re.match(r'^[A-Z][a-z]+[A-Z][a-z]*$',name):
		return name
	regex = r'(m[a]?c|d[ei])(.+)'
	match = re.match(regex,name,flags=re.I)
	if match:
		group = match.groups()
		return ''.join(Each(group).title())
	else:
		return name.title()

def safe_delete(thing):
	if thing and hasattr(thing,'delete'):
		thing.delete()


def authorized(request, level=0):
	if TRACE:
		print '# main.views.authorized'
	return 'meid' in request.session

# Find User object for current logged-in user, without causing errors.
# me is always a User, never a Family, Student, or Teacher
import apps
def getme(request):
	if TRACE:
		print '# hacks.getme'
	if 'meid' in request.session:
		me = apps.people.managers.Users.fetch(id=request.session['meid'])
		if me:
			return me
		else:
			request.session.pop('meid')
