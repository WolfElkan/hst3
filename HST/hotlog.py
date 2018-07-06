from Utils.data import Each

def log(request, *items):
	items = Each(items).__str__()
	items = Each(items).split('\n')
	request.session['log'].append(list(items))
