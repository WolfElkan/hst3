from trace import TRACE

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

def copyatts(source, keys):
	this = {}
	for key in keys:
		if hasattr(source, key):
			this[key] = source.__getattribute__(key)
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
	now = datetime.now()
	return now.year + (0 if now.month < 5 else 1)

class Funky(object):
	def __init__(self, callback):
		self.callback = callback
	def __call__(self, *args, **kwargs):
		return self.callback(*args, **kwargs)
		
# class PunchingBag(object):
# 	def __init__(self, *args, **kwargs):
# 		super(PunchingBag, self).__init__()
# 	def __getattribute__(self, other):
# 		return Funky(other)
# 	def __setattr__(self, other, value):
# 		print 'PUNCH: {} = {}'.format(other, value)

class Each(object):
	def __init__(self, arr):
		self.arr = list(arr)
	def __getattribute__(self, attr):
		new = []
		for x in super(Each,self).__getattribute__('arr'):
			new.append(x.__getattribute__(attr))
		return new
		

def safe_delete(thing):
	if thing and hasattr(thing,'delete'):
		thing.delete()

# Find User object for current logged-in user, without causing errors.
# me is always a User, never a Family, Student, or Teacher
import apps
def getme(request):
	if TRACE:
		print '# hacks.getme'
	if 'meid' in request.session:
		me = apps.main.managers.Users.fetch(id=request.session['meid'])
		if me:
			return me
		else:
			request.session.pop('meid')
