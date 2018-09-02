from Utils.data import Each

def log(request, *items):
	items = Each(items).__str__().split('\n')
	request.session['log'].append(list(items))
