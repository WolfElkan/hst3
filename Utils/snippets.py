def route(request):
	if request.method == 'GET':
		return route_get(request)
	elif request.method == 'POST':
		return route_post(request)
	else:
		return HttpResponse("Unrecognized HTTP Verb")
def route_get(request):
	seshinit(request,'variable')
	context = {
		'variable': request.session['variable'],
	}
	return render(request, 'route.html', context)
def route_post(request):
	return redirect('/route')