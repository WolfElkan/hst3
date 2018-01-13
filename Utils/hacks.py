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