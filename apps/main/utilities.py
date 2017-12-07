def get(obj, key):
	key = str(key)
	if type(obj) == dict:
		for kvp in obj.items():
			if kvp[0] == key:
				return kvp[1]
	else:
		return getattr(obj, key)

def copy(source, keys=False):
	this = {}
	if not keys:
		keys = source.keys()
	for key in keys:
		this[key] = source[key]
	return this

def reprint(obj, lev=0):
	if type(obj) == dict:
		for key in obj.keys():
			reprint(key, lev+1)
	elif 'items' in dir(obj):
		for key in obj.items():
			reprint(key, lev+1)
	else:
		print '  '*lev + str(obj)

class BcryptHash(object):
	def __init__(self, char60):
		self.hashed = char60 if char60[0] == '$' else char60[1:]
	def __call__(self, pw):
		return bcrypt.checkpw(bytes(pw), bytes(self.hashed))
	def __str__(self):
		return self.hashed[:7]+self.hashed[55:]
		# return u'\U0001f512 ' + unicode(trunc)
	def full(self):
		return self.hashed
	def html(self):
		return '<span title='+self.hashed+'>&#x1f512;</span>'