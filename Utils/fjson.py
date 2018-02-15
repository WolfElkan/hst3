import json
class FriendlyEncoder(json.JSONEncoder):
	def default(self, obj):
		if hasattr(obj,'__json__'):
			return obj.__json__()
		else:
			return str(obj)