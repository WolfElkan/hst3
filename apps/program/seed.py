from django.shortcuts import render, redirect, HttpResponse
from .models import Course, CourseTrad, Venue
from Utils import custom_fields as custom

def CourseTraditions(request):
	# Get Venues
	# rbc = Venue.objects.get(id=rbc)
	# adi = Venue.objects.get(id=adi)
	# mul = Venue.objects.get(id=mul)
	# fsf = Venue.objects.get(id=fsf)
	# Make Showcase Non-Dance CourseTrad objects
	CourseTrad.objects.create(id="AA", enroll=True , day="Fri", start="10:00", end="12:00", nMeets=21, show="SC", vs=True , min_age= 9, max_age=11, M=1,F=1,C=0,I=0,A=0, tuition=280.00, redtuit=300.00, vol_hours=17,the_hours=2, prepaid=True , title="Acting A") # place=rbc, 
	CourseTrad.objects.create(id="AB", enroll=True , day="Fri", start="10:00", end="12:00", nMeets=21, show="SC", vs=True , min_age=12, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition=280.00, redtuit=300.00, vol_hours=17,the_hours=2, prepaid=True , title="Acting B") # place=rbc, 
	CourseTrad.objects.create(id="C2", enroll=True , day="Fri", start="10:45", end="12:00", nMeets= 5, show="SC", vs=False, min_age=14, max_age=18, M=1,F=1,C=1,I=0,A=0, tuition= 75.00, redtuit= 75.00, vol_hours= 0,the_hours=0, prepaid=True , title="A Cappella Choir") # place=rbc, 
	CourseTrad.objects.create(id="C1", enroll=True , day="Fri", start="10:45", end="12:00", nMeets=10, show="SC", vs=False, min_age=10, max_age=18, M=0,F=1,C=0,I=0,A=0, tuition=150.00, redtuit=170.00, vol_hours= 2,the_hours=2, prepaid=True , title="Broadway Choir") # place=rbc, 
	# Make Dance CourseTrad objects
	CourseTrad.objects.create(id="IS", enroll=True , day="Wed", start="10:00", end="11:00", nMeets=20, show="SC", vs=False, min_age= 9, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Irish Dance Soft Shoe") # place=adi, 
	CourseTrad.objects.create(id="IH", enroll=True , day="Wed", start="11:00", end="12:00", nMeets=20, show="SC", vs=False, min_age=11, max_age=18, M=1,F=1,C=0,I=1,A=0, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Irish Dance Hard Shoe") # place=adi, 
	CourseTrad.objects.create(id="HB", enroll=True , day="Tue", start="11:30", end="12:30", nMeets=20, show="SC", vs=False, min_age= 9, max_age=12, M=1,F=0,C=0,I=0,A=0, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Boys Jazz & Hip-Hop") # place=adi, 
	CourseTrad.objects.create(id="HJ", enroll=True , day="Wed", start="11:00", end="12:00", nMeets=20, show="SC", vs=False, min_age=13, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Jazz & Hip-Hop") # place=adi, 
	CourseTrad.objects.create(id="Z1", enroll=True , day="Wed", start="11:00", end="12:00", nMeets=20, show="SC", vs=False, min_age=13, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Broadway Jazz 1") # place=adi, 
	CourseTrad.objects.create(id="Z2", enroll=True , day="Wed", start="12:15", end="13:30", nMeets=20, show="SC", vs=False, min_age=13, max_age=18, M=1,F=1,C=0,I=0,A=1, tuition=300.00, redtuit=320.00, vol_hours=17,the_hours=2, prepaid=True , title="Broadway Jazz 2") # place=adi, 
	CourseTrad.objects.create(id="J1", enroll=True , day="Tue", start="14:00", end="15:00", nMeets=20, show="SC", vs=False, min_age= 9, max_age=12, M=1,F=1,C=0,I=0,A=0, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Jazz 1") # place=adi, 
	CourseTrad.objects.create(id="J2", enroll=True , day="Tue", start="12:45", end="13:45", nMeets=20, show="SC", vs=False, min_age=11, max_age=12, M=1,F=1,C=0,I=0,A=1, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Jazz 2") # place=adi, 
	CourseTrad.objects.create(id="J3", enroll=True , day="Wed", start="12:15", end="13:30", nMeets=20, show="SC", vs=False, min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=1, tuition=300.00, redtuit=320.00, vol_hours=17,the_hours=2, prepaid=True , title="Jazz 3") # place=adi, 
	CourseTrad.objects.create(id="J4", enroll=True , day="Wed", start="13:45", end="15:00", nMeets=20, show="SC", vs=False, min_age=16, max_age=18, M=1,F=1,C=0,I=0,A=1, tuition=300.00, redtuit=320.00, vol_hours=17,the_hours=2, prepaid=True , title="Jazz 4") # place=adi, 
	CourseTrad.objects.create(id="P1", enroll=True , day="Wed", start="10:00", end="11:00", nMeets=20, show="SC", vs=False, min_age=13, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Broadway Tap 1") # place=adi, 
	CourseTrad.objects.create(id="P2", enroll=True , day="Wed", start="13:45", end="15:00", nMeets=20, show="SC", vs=False, min_age=13, max_age=18, M=1,F=1,C=0,I=0,A=1, tuition=300.00, redtuit=320.00, vol_hours=17,the_hours=2, prepaid=True , title="Broadway Tap 2") # place=adi, 
	CourseTrad.objects.create(id="T1", enroll=True , day="Tue", start="12:45", end="13:45", nMeets=20, show="SC", vs=False, min_age= 9, max_age=12, M=1,F=1,C=0,I=0,A=0, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Tap 1") # place=adi, 
	CourseTrad.objects.create(id="T2", enroll=True , day="Tue", start="14:00", end="15:00", nMeets=20, show="SC", vs=False, min_age=11, max_age=12, M=1,F=1,C=0,I=0,A=1, tuition=250.00, redtuit=270.00, vol_hours=17,the_hours=2, prepaid=True , title="Tap 2") # place=adi, 
	CourseTrad.objects.create(id="T3", enroll=True , day="Wed", start="13:45", end="15:00", nMeets=20, show="SC", vs=False, min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=1, tuition=300.00, redtuit=320.00, vol_hours=17,the_hours=2, prepaid=True , title="Tap 3") # place=adi, 
	CourseTrad.objects.create(id="T4", enroll=True , day="Wed", start="12:15", end="13:30", nMeets=20, show="SC", vs=False, min_age=16, max_age=18, M=1,F=1,C=0,I=0,A=1, tuition=300.00, redtuit=320.00, vol_hours=17,the_hours=2, prepaid=True , title="Tap 4") # place=adi, 
	# Make Tech CourseTrad objects
	CourseTrad.objects.create(id="XA", enroll=True , day="Fri", start="10:00", end="12:00", nMeets=10, show="no", vs=False, min_age=12, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition=150.00, redtuit=160.00, vol_hours= 2,the_hours=2, prepaid=False, title="Tech Apps") # place=rbc, 
	CourseTrad.objects.create(id="XX", enroll=True , day="Fri", start="12:15", end="16:15", nMeets=11, show="no", vs=False, min_age=12, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition=150.00, redtuit=160.00, vol_hours= 2,the_hours=2, prepaid=False, title="Tech Team") # place=rbc, 
	CourseTrad.objects.create(id="WX", enroll=True , day="Sat", start="10:00", end="14:30", nMeets= 1, show="no", vs=False, min_age=12, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition= 50.00, redtuit= 50.00, vol_hours= 2,the_hours=2, prepaid=False, title="Tech Crew Workshop") # place=mul, 
	CourseTrad.objects.create(id="XM", enroll=True , day="Fri", start="10:00", end="12:00", nMeets=10, show="no", vs=False, min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition=150.00, redtuit=160.00, vol_hours= 2,the_hours=2, prepaid=False, title="Makeup Team") # place=rbc, 
	CourseTrad.objects.create(id="WW", enroll=True , day="Mon", start="13:00", end="17:00", nMeets= 1, show="no", vs=False, min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition= 50.00, redtuit= 50.00, vol_hours= 2,the_hours=2, prepaid=False, title="Wig Workshop") # place=mul, 
	CourseTrad.objects.create(id="WN", enroll=True , day="Sat", start="14:00", end="17:00", nMeets= 2, show="no", vs=False, min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition= 50.00, redtuit= 50.00, vol_hours= 2,the_hours=2, prepaid=False, title="Painting Workshop") # place=mul, 
	CourseTrad.objects.create(id="WP", enroll=True , day="Sat", start="13:00", end="17:00", nMeets= 1, show="no", vs=False, min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=0, tuition= 30.00, redtuit= 30.00, vol_hours= 2,the_hours=2, prepaid=False, title="Prop Workshop") # place=mul, 
	# Make Troupes CourseTrad objects
	CourseTrad.objects.create(id="SG", enroll=True , day="Fri", start="13:00", end="16:00", nMeets=24, show="GB", vs=False, min_age=10, max_age=13, M=1,F=1,C=0,I=0,A=4, tuition=450.00, redtuit=450.00, vol_hours=22,the_hours=2, prepaid=True , title="Gaithersburg Troupe") # place=rbc, 
	CourseTrad.objects.create(id="SJ", enroll=True , day="Fri", start="13:00", end="16:00", nMeets=24, show="JR", vs=False, min_age=10, max_age=13, M=1,F=1,C=0,I=0,A=4, tuition=450.00, redtuit=450.00, vol_hours=22,the_hours=2, prepaid=True , title="Junior Troupe") # place=rbc, 
	CourseTrad.objects.create(id="SB", enroll=True , day="Fri", start="13:00", end="16:00", nMeets=22, show="TT", vs=True , min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=2, tuition=425.00, redtuit=425.00, vol_hours=22,the_hours=2, prepaid=True , title="Travel Troupe") # place=rbc, 
	CourseTrad.objects.create(id="SH", enroll=True , day="Fri", start="12:30", end="16:00", nMeets=24, show="SH", vs=False, min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=3, tuition=475.00, redtuit=475.00, vol_hours=22,the_hours=2, prepaid=True , title="Shakespeare Troupe") # place=rbc, 
	CourseTrad.objects.create(id="SR", enroll=True , day="Fri", start="12:30", end="16:00", nMeets=25, show="SR", vs=False, min_age=14, max_age=18, M=1,F=1,C=0,I=0,A=3, tuition=475.00, redtuit=475.00, vol_hours=22,the_hours=2, prepaid=True , title="Senior Troupe") # place=rbc, 
	CourseTrad.objects.create(id="GA", enroll=True , day="Fri", start="10:30", end="12:00", nMeets= 1, show="no", vs=False, min_age=10, max_age=13, M=1,F=1,C=0,I=0,A=3, tuition=  0.00, redtuit=  0.00, vol_hours=22,the_hours=2, prepaid=False, title="JR/GB General Audition") # place=rbc, 
	# Make Showcase Acting Skits CourseTrad objects
	CourseTrad.objects.create(id="A0", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #0") # place=fsf, 
	CourseTrad.objects.create(id="A1", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #1") # place=fsf, 
	CourseTrad.objects.create(id="A2", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #2") # place=fsf, 
	CourseTrad.objects.create(id="A3", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #3") # place=fsf, 
	CourseTrad.objects.create(id="A4", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #4") # place=fsf, 
	CourseTrad.objects.create(id="A5", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #5") # place=fsf, 
	CourseTrad.objects.create(id="A6", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #6") # place=fsf, 
	CourseTrad.objects.create(id="A7", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #7") # place=fsf, 
	CourseTrad.objects.create(id="A8", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #8") # place=fsf, 
	CourseTrad.objects.create(id="A9", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Acting Scene #9") # place=fsf, 
	# Make Showcase Finale Groups CourseTrad objects
	CourseTrad.objects.create(id="FN", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale") # place=fsf, 
	CourseTrad.objects.create(id="F0", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #0 (Seniors)") # place=fsf, 
	CourseTrad.objects.create(id="F1", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #1") # place=fsf, 
	CourseTrad.objects.create(id="F2", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #2") # place=fsf, 
	CourseTrad.objects.create(id="F3", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #3") # place=fsf, 
	CourseTrad.objects.create(id="F4", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #4") # place=fsf, 
	CourseTrad.objects.create(id="F5", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #5") # place=fsf, 
	CourseTrad.objects.create(id="F6", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #6") # place=fsf, 
	CourseTrad.objects.create(id="F7", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #7") # place=fsf, 
	CourseTrad.objects.create(id="F8", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #8") # place=fsf, 
	CourseTrad.objects.create(id="F9", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #9") # place=fsf, 
	CourseTrad.objects.create(id="FX", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #10") # place=fsf, 
	CourseTrad.objects.create(id="FY", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #11") # place=fsf, 
	CourseTrad.objects.create(id="FZ", enroll=False, day=""   , start="00:00", end="00:00", nMeets= 0, show="SC", vs=False, min_age= 0, max_age=99, M=1,F=1,C=0,I=0,A=0, tuition=  0.00,redtuit=  0.00, vol_hours= 0, the_hours=0, prepaid=False, title="Showcase Finale Group #12") # place=fsf, 
	# Get CourseTrad objects to Redirect
	SB = CourseTrad.objects.get(id="SB")
	SG = CourseTrad.objects.get(id="SG")
	SJ = CourseTrad.objects.get(id="SJ")
	# Make Redirects CourseTrad objects
	CourseTrad.objects.create(id="GB", enroll=False, alias=SG, title="Gaithersburg Troupe Alias")
	CourseTrad.objects.create(id="JR", enroll=False, alias=SJ, title="Junior Troupe Alias")
	CourseTrad.objects.create(id="TT", enroll=False, alias=SB, title="Travel Troupe Alias")
	CourseTrad.objects.create(id="AI", enroll=False, alias=SB, title="Travel Troupe Alias (as Acting Intensive)")
	CourseTrad.objects.create(id="CH", enroll=False, alias=SB, title="Travel Troupe Alias (as Coffee House)")
	return HttpResponse('62 courses added')

def ClearCourseTraditions(request):
	Course.objects.all().delete()
	return HttpResponse('courses cleared')

def both(request):
	Course.objects.all().delete()
	return SeedCourseTraditions(request)