from django.http.request import QueryDict
# Use IceCream?
def pretty(arr, delim='  ', indent='', level=0, printout=''):
	if type(arr) in [dict, QueryDict]:
		lens = []
		for key in arr:
			lens.append(len(key))
		maxlens = max(lens)
		for key in arr:
			print "{}{} : {}".format(key,' '*(maxlens-len(key)),arr[key])
	else:	
		for thing in arr:
			if type(thing) is list:
				printout = pretty(thing, delim, indent+'['+delim, level+1, printout)
			else:
				printout += indent + str(thing) + '\n'
		return printout if level else printout[:-1]

def pdir(thing):
	return pretty(dir(thing))

def san(string):
	return string.replace('<','&lt;').replace('>','&gt;')

from django.http.request import QueryDict

def divs(obj,emoji='&#x1F535;'):
	visible = '&#9644;' if obj == '' else obj
	if type(obj) is int:
		return '<span class="int number">{}</span>'.format(visible)
	elif type(obj) is long:
		return '<span class="long number">{}L</span>'.format(visible)
	elif type(obj) is float:
		return '<span class="float number">{}</span>'.format(visible)
	elif type(obj) is complex:
		return '<span class="complex number">{}</span>'.format(visible)

	elif type(obj) is str:
		return '<span class="str string">{}</span>'.format(san(obj))
	elif type(obj) is unicode:
		return '<span class="unicode string">{}</span>'.format(san(obj))
	elif type(obj) is buffer:
		return '<span class="buffer string">{}</span>'.format(san(obj))

	elif type(obj) is bool:
		return '<span class="bool {}">{}</span>'.format(obj,obj)

	elif type(obj) is list:
		html = '<ol start="0" class="list">'
		for item in obj:
			html += '<li>{}</li>'.format(divs(item,emoji))
		html += '</ol>'
		return html

	elif type(obj) is tuple:
		html = '<ol start="0" class="tuple">'
		for item in obj:
			html += '<li>{}</li>'.format(divs(item,emoji))
		html += '</ol>'
		return html

	elif type(obj) is dict:
		html = '<table class="dict">'
		for key in obj:
			html += '<tr class="pair"><td class="key">{}:</td><td class="value">{}</td></tr>'.format(key,divs(obj[key],emoji))
		html += '</table>'
		return html

	elif type(obj) is QueryDict:
		html = '<table class="QueryDict">'
		for key in obj:
			html += '<tr class="pair"><td class="key">{}:</td><td class="value">{}</td></tr>'.format(key,divs(obj[key],emoji))
		html += '</table>'
		return html


	# elif hasattr(obj, '__dict__') and type(obj.__dict__) is dict:
	# 	html = '<table class="nudge dict">'
	# 	for key in obj.__dict__:
	# 		if key in obj.__dict__:
	# 			html += '<tr class="pair"><td class="key">{}:</td><td class="value">{}</td></tr>'.format(key,obj.__dict__[key])
	# 	html += '</table>'
	# 	return html

	else:
		return '<div class="object"><span class="type">{}</span><span class="strobj">{}{}</span></div>'.format(type(obj),san(repr(obj)),emoji)








