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

def reprint(obj, lev=0):
	if type(obj) == dict:
		for key in obj.keys():
			reprint(key, lev+1)
	elif 'items' in dir(obj):
		for key in obj.items():
			reprint(key, lev+1)
	else:
		print '  '*lev + str(obj)

class Copy(object):
	def __init__(self, source, *keys):
		if not keys:
			keys = source.keys()
		for key in keys:
			if key in source:
				self[key] = source[key]
			else:
				self[key] = None
	def __getattr__(self, key):
		return super(Copy, self).__getitem__(key)
	# def __getitem__(self, key):
	# 	return super(Copy, self).__getitem__(key)
	def __setattr__(self, key, value):
		return super(Copy, self).__setitem__(key, value)
	# def __setitem__(self, key, value):
	# 	return super(Copy, self).__setitem__(key, value)
		