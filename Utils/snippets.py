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

from apps.program.managers import CourseTrads

def make(year):
	qset = CourseTrads.filter(e=True).exclude(id__startswith='W')
	for q in qset:
		c = q.make(year)
		print c

orders = [
	{'id':"AA",'order': 10},
	{'id':"AB",'order': 20},
	{'id':"AC",'order': 30},
	{'id':"A0",'order': 30},
	{'id':"A1",'order': 31},
	{'id':"A2",'order': 32},
	{'id':"A3",'order': 33},
	{'id':"A4",'order': 34},
	{'id':"A5",'order': 35},
	{'id':"A6",'order': 36},
	{'id':"A7",'order': 37},
	{'id':"A8",'order': 38},
	{'id':"A9",'order': 39},
	{'id':"C1",'order': 41},
	{'id':"C2",'order': 42},
	{'id':"O1",'order': 51},
	{'id':"O2",'order': 52},
	{'id':"J1",'order': 61},
	{'id':"J2",'order': 62},
	{'id':"J3",'order': 63},
	{'id':"J4",'order': 64},
	{'id':"Z1",'order': 65},
	{'id':"Z2",'order': 66},
	{'id':"T1",'order': 71},
	{'id':"T2",'order': 72},
	{'id':"T3",'order': 73},
	{'id':"T4",'order': 74},
	{'id':"P1",'order': 75},
	{'id':"P2",'order': 76},
	{'id':"IS",'order': 85},
	{'id':"IH",'order': 86},
	{'id':"HB",'order': 95},
	{'id':"HJ",'order': 96},
	{'id':"FN",'order': 99},
	{'id':"F0",'order':100},
	{'id':"F1",'order':101},
	{'id':"F2",'order':102},
	{'id':"F3",'order':103},
	{'id':"F4",'order':104},
	{'id':"F5",'order':105},
	{'id':"F6",'order':106},
	{'id':"F7",'order':107},
	{'id':"F8",'order':108},
	{'id':"F9",'order':109},
	{'id':"FX",'order':110},
	{'id':"FY",'order':111},
	{'id':"FZ",'order':112},
	{'id':"GA",'order':121},
	{'id':"SG",'order':122},
	{'id':"SJ",'order':123},
	{'id':"SB",'order':131},
	{'id':"SH",'order':132},
	{'id':"SR",'order':133},
	{'id':"XA",'order':141},
	{'id':"XM",'order':142},
	{'id':"XX",'order':143},
	{'id':"WX",'order':151},
	{'id':"WP",'order':152},
	{'id':"WN",'order':153},
	{'id':"WW",'order':154},
]
def order_coursetrads():
	for o in orders:
		q = CourseTrads.fetch(id=o['id'])
		if q:
			q.order = o['order']
			q.save()