def get(obj, key):
	key = str(key)
	if type(obj) == dict:
		for kvp in obj.items():
			if kvp[0] == key:
				return kvp[1]
	else:
		return getattr(obj, key)

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

# Return the current HST registration year (This year until May 1, next year thereafter)
def year():
	now = datetime.now()
	return now.year + (0 if now.month < 5 else 1)

# Find User object for current logged-in user, without causing errors.
# me is always a User, never a Family, Student, or Teacher
import apps
def getme(request):
	if 'meid' not in request.session:
		return None
	else:
		return first(apps.main.models.User.objects.filter(id=request.session['meid']))
