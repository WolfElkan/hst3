from django.db.models import Q

from apps.people.managers  import Families, Addresses, Parents, Users, Students, Teachers
from apps.program.managers import CourseTrads, Courses, Venues, Enrollments
from apps.payment.managers import Invoices, PayPals

def search_word(word, all_tables=True, **kwargs):
	results = set([])
	if all_tables or kwargs.get('family'):
		results |= set(Families.filter(Q(
			Q(hid=word)|
			Q(last__contains=word)|
			Q(phone__contains=word)|
			Q(phone_type=word)|
			Q(email__contains=word))))
	if all_tables or kwargs.get('parent'):
		results |= set(Parents.filter(Q(
			Q(hid=word)|
			Q(first__contains=word)|
			Q(alt_last__contains=word)|
			Q(alt_phone__contains=word)|
			Q(phone_type=word)|
			Q(alt_email__contains=word))))
	if all_tables or kwargs.get('student'):
		results |= set(Students.filter(Q(
			Q(hid=word)|
			Q(first__contains=word)|
			Q(alt_first__contains=word)|
			Q(family__last__contains=word)|
			Q(alt_last__contains=word)|
			Q(alt_phone__contains=word)|
			Q(alt_email__contains=word)|
			Q(needs__contains=word))))
	if all_tables or kwargs.get('coursetrad'):
		results |= set(CourseTrads.filter(Q(
			Q(id=word)|
			Q(oid=word)|
			Q(title__contains=word)|
			Q(alias_id=word)|
			Q(eligex__contains=word)|
			Q(default=word)|
			Q(action=word))))
	if all_tables or kwargs.get('course'):
		results |= set(Courses.filter(Q(
			Q(id=word)|
			Q(tradition__id=word)|
			Q(tradition__oid=word)|
			Q(title__contains=word)|
			Q(tradition__title__contains=word)|
			Q(tradition__alias_id=word)|
			Q(tradition__eligex__contains=word)|
			Q(tradition__default=word)|
			Q(tradition__action__contains=word))))
	if all_tables or kwargs.get('address'):
		results |= set(Addresses.filter(Q(
			Q(line1__contains=word)|
			Q(line2__contains=word)|
			Q(city__contains=word)|
			Q(state__contains=word)|
			Q(zipcode__contains=word))))
	if all_tables or kwargs.get('venue'):
		results |= set(Venues.filter(name__contains=word))
	if all_tables or kwargs.get('enrollment'):
		results |= set(Enrollments.filter(role__contains=word))
	if all_tables or kwargs.get('user'):
		results |= set(Users.filter(username__contains=word))
	if all_tables or kwargs.get('teacher'):
		results |= set(Teachers.filter(Q(
			Q(first__contains=word)|
			Q(last__contains=word)|
			Q(phone__contains=word)|
			Q(email__contains=word))))
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
	if all_tables or kwargs.get('user'):
		results |= set(Users.filter(username__contains=word))
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