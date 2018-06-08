# Function for initializing session variables.
def seshinit(request, sesh, val=''):
	if sesh not in request.session:
		request.session[sesh] = val

# Initialize form error/persist structure in session
def forminit(request, form_name, fields, obj=None, data=None):
	seshinit(request,'p',{})
	seshinit(request,'e',{})
	if form_name not in request.session['p']:
		request.session['p'][form_name] = {}
		for f in fields:
			if f not in request.session['p'][form_name]:
				request.session['p'][form_name][f] = obj.__getattribute__(f) if obj and hasattr(obj,f) else data[f] if data and f in data else ''
	if form_name not in request.session['e']:
		request.session['e'][form_name] = {}
		for f in fields:
			if f not in request.session['e'][form_name]:
				request.session['e'][form_name][f] = ''