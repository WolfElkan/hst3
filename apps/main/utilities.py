def get(obj, key):
	key = str(key)
	if type(obj) == dict:
		for kvp in obj.items():
			if kvp[0] == key:
				return kvp[1]
	else:
		return getattr(obj, key)