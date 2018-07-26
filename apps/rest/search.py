from django.db.models import Q

from apps.people.managers  import Families, Addresses, Parents, Users, Students, Teachers
from apps.program.managers import CourseTrads, Courses, Venues, Enrollments
from apps.payment.managers import Invoices, PayPals

def search_word(word, all_tables=True, **kwargs):
	results = set([])
	if all_tables or kwargs.get('family'):
		results |= set(Families.filter(Q(
			Q(hid=word)|
			Q(last__icontains=word)|
			Q(phone__icontains=word)|
			Q(phone_type=word)|
			Q(email__icontains=word))))
	if all_tables or kwargs.get('parent'):
		results |= set(Parents.filter(Q(
			Q(hid=word)|
			Q(first__icontains=word)|
			Q(alt_last__icontains=word)|
			Q(alt_phone__icontains=word)|
			Q(phone_type=word)|
			Q(alt_email__icontains=word))))
	if all_tables or kwargs.get('student'):
		results |= set(Students.filter(Q(
			Q(hid=word)|
			Q(first__icontains=word)|
			Q(alt_first__icontains=word)|
			Q(family__last__icontains=word)|
			Q(alt_last__icontains=word)|
			Q(alt_phone__icontains=word)|
			Q(alt_email__icontains=word)|
			Q(needs__icontains=word))))
	if all_tables or kwargs.get('coursetrad'):
		results |= set(CourseTrads.filter(Q(
			Q(id=word)|
			Q(oid=word)|
			Q(title__icontains=word)|
			Q(alias_id=word)|
			Q(eligex__icontains=word)|
			Q(default=word)|
			Q(action=word))))
	if all_tables or kwargs.get('course'):
		results |= set(Courses.filter(Q(
			Q(id=word)|
			Q(tradition__id=word)|
			Q(tradition__oid=word)|
			Q(title__icontains=word)|
			Q(tradition__title__icontains=word)|
			Q(tradition__alias_id=word)|
			Q(tradition__eligex__icontains=word)|
			Q(tradition__default=word)|
			Q(tradition__action__icontains=word))))
	if all_tables or kwargs.get('address'):
		results |= set(Addresses.filter(Q(
			Q(line1__icontains=word)|
			Q(line2__icontains=word)|
			Q(city__icontains=word)|
			Q(state__icontains=word)|
			Q(zipcode__icontains=word))))
	if all_tables or kwargs.get('venue'):
		results |= set(Venues.filter(name__icontains=word))
	if all_tables or kwargs.get('enrollment'):
		results |= set(Enrollments.filter(role__icontains=word))
	if all_tables or kwargs.get('user'):
		results |= set(Users.filter(username__icontains=word))
	if all_tables or kwargs.get('teacher'):
		results |= set(Teachers.filter(Q(
			Q(first__icontains=word)|
			Q(last__icontains=word)|
			Q(phone__icontains=word)|
			Q(email__icontains=word))))
	return results

def search_number(number, all_tables=True, **kwargs):
	results = set([])
	if all_tables or kwargs.get('family'):
		results |= set(Families.filter(Q(
			Q(id=word)|
			Q(oid=word)|
			Q(name_num=word))))
	if all_tables or kwargs.get('parent'):
		results |= set(Parents.filter(id=word))
	if all_tables or kwargs.get('student'):
		results |= set(Students.filter(Q(
			Q(id=word)|
			Q(oid=word)|
			Q(grad_year=word))))
	if all_tables or kwargs.get('invoice'):
		results |= set(Invoices.filter(Q(
			Q(id=word)|
			Q(amount=word))))
	if all_tables or kwargs.get('course'):
		results |= set(Courses.filter(year=word))
	if all_tables or kwargs.get('address'):
		results |= set(Addresses.filter(id=word))
	return results

def search_query(query, **kwargs):
	results = set([])
	for word in query.split(' '):
		if word.title() == 'Family':
			results &= set(Families.all())
		elif results:
			results &= search_number(word, **kwargs) if word.isdigit() else search_word(word, **kwargs)
		else:
			results = search_word(word, **kwargs)
	return results

def fetch(query):
	result = list(search_query(query))
	if result:
		return result[0]