def route(request, **kwargs):
	if request.method == 'GET':
		return route_get(request, **kwargs)
	elif request.method == 'POST':
		return route_post(request, **kwargs)
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

from apps.program.managers import CourseTrads, Courses

def make(year):
	count = 0
	for tradition in CourseTrads.filter(e=True):
		if not Courses.fetch(year=year,tradition=tradition):
			count += 1
			print tradition.make(year)
	return count

orders = [
	{'id':'AA','order': 10.0},
	{'id':'AB','order': 20.0},
	{'id':'A0','order': 30.0},
	{'id':'AC','order': 30.0},
	{'id':'A1','order': 31.0},
	{'id':'A2','order': 32.0},
	{'id':'A3','order': 33.0},
	{'id':'A4','order': 34.0},
	{'id':'A5','order': 35.0},
	{'id':'A6','order': 36.0},
	{'id':'A7','order': 37.0},
	{'id':'A8','order': 38.0},
	{'id':'A9','order': 39.0},
	{'id':'C1','order': 41.0},
	{'id':'C2','order': 42.0},
	{'id':'C0','order': 43.0},
	{'id':'O1','order': 51.0},
	{'id':'O2','order': 52.0},
	{'id':'J1','order': 61.0},
	{'id':'J2','order': 62.0},
	{'id':'J3','order': 63.0},
	{'id':'J4','order': 64.0},
	{'id':'Z1','order': 65.0},
	{'id':'Z2','order': 66.0},
	{'id':'HA','order': 67.0},
	{'id':'HB','order': 68.0},
	{'id':'T1','order': 71.0},
	{'id':'T2','order': 72.0},
	{'id':'T3','order': 73.0},
	{'id':'T4','order': 74.0},
	{'id':'P1','order': 75.0},
	{'id':'P2','order': 76.0},
	{'id':'IS','order': 85.0},
	{'id':'IH','order': 86.0},
	{'id':'HJ','order': 96.0},
	{'id':'FN','order': 99.0},
	{'id':'F0','order':100.0},
	{'id':'F1','order':101.0},
	{'id':'F2','order':102.0},
	{'id':'F3','order':103.0},
	{'id':'F4','order':104.0},
	{'id':'F5','order':105.0},
	{'id':'F6','order':106.0},
	{'id':'F7','order':107.0},
	{'id':'F8','order':108.0},
	{'id':'F9','order':109.0},
	{'id':'FX','order':110.0},
	{'id':'FY','order':111.0},
	{'id':'FZ','order':112.0},
	{'id':'SG','order':122.0},
	{'id':'SJ','order':123.0},
	{'id':'SB','order':131.0},
	{'id':'SH','order':132.0},
	{'id':'SR','order':133.0},
	{'id':'XA','order':141.0},
	{'id':'XX','order':143.0},
	{'id':'WX','order':151.0},
	{'id':'WP','order':152.0},
	{'id':'WN','order':153.0},
	{'id':'WW','order':154.0},
	{'id':'MU','order':161.0},
	{'id':'MW','order':162.0},
	{'id':'VP','order':180.0},
]

def order_coursetrads():
	for o in orders:
		q = CourseTrads.fetch(id=o['id'])
		if q:
			q.order = o['order']
			q.save()