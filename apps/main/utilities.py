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
		this[trunckey] = source[key]
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