import re
from .data import Each
def namecase(name):
	if re.match(r'^[A-Z][a-z]+[A-Z][a-z]*$',name):
		return name
	regex = r'(m[a]?c|di)(.+)'
	match = re.match(regex,name,flags=re.I)
	if match:
		group = match.groups()
		return ''.join(Each(group).title())
	else:
		return name.title()

def cleanhex(string):
	return ''.join(re.findall(r'[0-9a-fA-F]',str(string))).lower()

def safe_delete(thing):
	if thing and hasattr(thing,'delete'):
		thing.delete()