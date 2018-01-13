from django.shortcuts import render, redirect, HttpResponse
from .models import Course, CourseTrad, Venue

# Create your views here.

def SeedCourseTraditions(request):
	CourseTrad.objects.create(
		code="AA",
		title="Acting A",
		# day="Fri" ,
		start="10:00",
		end = "12:00",
		# venue=rbc ,
		max_age=11 ,
		show="SC",
		tuition=280.00,
		redtuit=300.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		vs=True
	)
	CourseTrad.objects.create(
		code="AB",
		title="Acting B",
		# day="Fri" ,
		start="10:00",
		end = "12:00",
		# venue=rbc ,
		min_age=12,
		vs=True,
		show="SC",
		tuition=280.00,
		redtuit=300.00 ,
		vol_hours=17,
		the_hours= 2,
		prepaid=True
	)
	CourseTrad.objects.create(
		code="C2",
		title="CHOIR A Cappella",
		# day="Fri" ,
		start="10:45",
		end = "12:00",
		# venue=rbc ,
		min_age=14,
		show="SC",
		tuition=75.00,
		redtuit=75.00,
		vol_hours= 0,
		the_hours= 0,
		prepaid=True,
		# preq="cur"
	)
	CourseTrad.objects.create(
		code="C1",
		title="CHOIR Broadway",
		# day="Fri" ,
		start="10:45",
		end = "12:00",
		# venue=rbc ,
		min_age=10,
		show="SC",
		nMeets=10,
		tuition=150.00,
		redtuit=170.00,
		vol_hours= 2,
		the_hours= 2,
		prepaid=True,
		# preq="girl",
	)
	CourseTrad.objects.create(
		code="IS",
		title="Irish Dance Soft Shoe",
		# day="Wed" ,
		start="10:00",
		end = "11:00",
		show="SC",
		# venue=adi ,
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2
	)
	CourseTrad.objects.create(
		code="IH",
		title="Irish Dance Hard Shoe",
		# day="Wed" ,
		start="11:00",
		end = "12:00",
		# venue=adi ,
		min_age=11,
		show="SC",
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="iort"
	)
	CourseTrad.objects.create(
		code="HB",
		title="Boys Jazz & Hip-Hop",
		# day="Tue",
		start="11:30",
		end = "12:30",
		# venue=adi ,
		show="SC",
		max_age=12,
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="boy"
	)
	CourseTrad.objects.create(
		code="HJ",
		title="Jazz & Hip-Hop",
		# day="Wed" ,
		start="11:00",
		end = "12:00",
		# venue=adi ,
		min_age=13,
		show="SC",
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2
	)
	CourseTrad.objects.create(
		code="Z1",
		title="Broadway Jazz 1",
		# day="Wed" ,
		start="11:00",
		end = "12:00",
		# venue=adi ,
		min_age=13,
		show="SC",
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2
	)
	CourseTrad.objects.create(
		code="Z2",
		title="Broadway Jazz 2",
		# day="Wed" ,
		start="12:15",
		end = "13:30",
		# venue=adi ,
		min_age=13,
		show="SC",
		tuition=300.00,
		redtuit=320.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="J1",
		title="Jazz 1",
		# day="Tue".,
		start="14:00",
		end = "15:00",
		# venue=adi ,
		max_age=12,
		show="SC",
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2
	)
	CourseTrad.objects.create(
		code="J2",
		title="Jazz 2",
		# day="Tue".,
		start="12:45",
		end = "13:45",
		# venue=adi ,
		min_age=11,
		show="SC",
		max_age=12 ,
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="J3",
		title="Jazz 3",
		# day="Wed" ,
		start="12:15",
		end = "13:30",
		# venue=adi ,
		min_age=14,
		show="SC",
		tuition=300.00,
		redtuit=320.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="J4",
		title="Jazz 4",
		# day="Wed" ,
		start="13:45",
		end = "15:00",
		# venue=adi ,
		min_age=16,
		show="SC",
		tuition=300.00,
		redtuit=320.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="P1",
		title="Broadway Tap 1",
		# day="Wed" ,
		start="10:00",
		end = "11:00",
		# venue=adi ,
		min_age=13,
		show="SC",
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="P2",
		title="Broadway Tap 2",
		# day="Wed" ,
		start="13:45",
		end = "15:00",
		# venue=adi ,
		min_age=13,
		show="SC",
		tuition=300.00,
		redtuit=320.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="T1",
		title="Tap 1",
		# day="Tue".,
		start="12:45",
		end = "13:45",
		# venue=adi ,
		max_age=12,
		show="SC",
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="T2",
		title="Tap 2",
		# day="Tue".,
		start="14:00",
		end = "15:00",
		# venue=adi ,
		min_age=11,
		show="SC",
		max_age=12,
		tuition=250.00,
		redtuit=270.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="T3",
		title="Tap 3",
		# day="Wed" ,
		start="13:45",
		end = "15:00",
		# venue=adi ,
		min_age=14,
		show="SC",
		tuition=300.00,
		redtuit=320.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="T4",
		title="Tap 4",
		# day="Wed" ,
		start="12:15",
		end = "13:30",
		# venue=adi ,
		min_age=16,
		show="SC",
		tuition=300.00,
		redtuit=320.00 ,
		prepaid=True,
		vol_hours=17,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="XA",
		title="Tech Apps",
		# day="Fri" ,
		start="10:00",
		end = "12:00",
		# venue=rbc ,
		min_age=12,
		show="no",
		tuition=150.00,
		redtuit=160.00,
		prepaid=False,
		vol_hours= 2,
		the_hours= 2,
		# preq="mast"
	)
	CourseTrad.objects.create(
		code="XX",
		title="Tech Crew",
		# day="Fri" ,
		start="12:15",
		end = "16:15",
		# venue=rbc ,
		min_age=12,
		show="as",
		tuition=150.00,
		redtuit=160.00,
		prepaid=False,
		vol_hours= 2,
		the_hours= 2,
		# preq="WX"
	)
	CourseTrad.objects.create(
		code="GB",
		title="Gaithersburg Troupe",
		# day="Fri" ,
		start="13:00",
		end = "16:00",
		# venue=rbc,
		min_age=10,
		max_age=13,
		show="GB",
		tuition=450.00,
		redtuit=450.00,
		prepaid=True,
		vol_hours=22,
		the_hours=22,
		# preq="Aud1"
	)
	CourseTrad.objects.create(
		code="JR",
		title="Junior Troupe",
		# day="Fri" ,
		start="13:00",
		end = "16:00",
		# venue=rbc,
		min_age=10,
		max_age=13,
		show="JR",
		tuition=450.00,
		redtuit=450.00,
		prepaid=True,
		vol_hours=22,
		the_hours=22,
		# preq="Aud1"
	)
	CourseTrad.objects.create(
		code="TT",
		title="Travel Troupe",
		# day="Fri" ,
		start="13:00",
		end = "16:00",
		# venue=rbc,
		min_age=14,
		show="TT",
		tuition=425.00,
		redtuit=425.00,
		prepaid=True,
		vol_hours=22,
		the_hours=22,
		# preq="Act"
	)
	CourseTrad.objects.create(
		code="SH",
		title="Shakespeare Troupe",
		# day="Fri" ,
		start="12:30",
		end = "16:00",
		# venue=rbc,
		min_age=14,
		show="SH",
		tuition=475.00,
		redtuit=475.00,
		prepaid=True,
		vol_hours=22,
		the_hours=22,
		# preq="Aud2"
	)
	CourseTrad.objects.create(
		code="SR",
		title="Senior Troupe",
		# day="Fri" ,
		start="12:30",
		end = "16:00",
		# venue=rbc,
		min_age=14,
		show="SR",
		tuition=475.00,
		redtuit=475.00,
		prepaid=True,
		vol_hours=22,
		the_hours=22,
		# preq="Aud2"
	)
	return HttpResponse('27 courses added')

def ClearCourseTraditions(request):
	Course.objects.all().delete()
	return HttpResponse('courses cleared')

def both(request):
	Course.objects.all().delete()
	return SeedCourseTraditions(request)