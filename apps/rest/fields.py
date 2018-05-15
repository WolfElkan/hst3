from .widgets import VarChar, Integer, Enum, Radio, Checkbox, Date, Time, ForeignKey, ForeignSet, ToggleSet, NullBoolean, Static
from Utils.custom_fields import Bcrypt, PhoneNumber, ZipCode, DayOfWeek, Dollar
from Utils.data import collect
from apps.program.managers import CourseTrads, Enrollments
from apps.payment.managers import Invoices
from apps.people.models import Address, Family, Student, Parent, User

FIELDS = {
	'address'   : [
		{'field':'line1'     , 'template': VarChar(maxlength=50)},
		{'field':'line2'     , 'template': VarChar(maxlength=50)},
		{'field':'city'      , 'template': VarChar(maxlength=25)},
		{'field':'state'     , 'template': VarChar(maxlength=2)},
		{'field':'zipcode'   , 'template': ZipCode()},
	],
	'family'    : [
		{'field':'hid'       , 'template': Static()},
		{'field':'last'      , 'template': VarChar(maxlength=30)},
		{'field':'phone'     , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum(options=['','Home','Cell','Work'])},
		{'field':'email'     , 'template': VarChar(maxlength=254)},
		{'field':'mother'    , 'template': ForeignKey(model='parent', null=True)},
		{'field':'father'    , 'template': ForeignKey(model='parent', null=True)},
		{'field':'address'   , 'template': ForeignKey(model='address', null=True)},
		{'field':'children'  , 'template': ForeignSet(model='student')},
	],
	'parent'    : [
		{'field':'first'     , 'template': VarChar(maxlength=20)},
		{'field':'family'    , 'template': ForeignKey(model='family')},
		{'field':'alt_last'  , 'template': VarChar(maxlength=30)},
		{'field':'sex'       , 'template': Enum(items=Parent.sex_choices)},
		{'field':'alt_phone' , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum(options=['','Home','Cell','Work'])},
		{'field':'alt_email' , 'template': VarChar(maxlength=254)},
	],
	'student'   : [
		{'field':'hid'       , 'template': Static()},
		{'field':'first'     , 'template': VarChar(maxlength=20)},
		{'field':'alt_first' , 'template': VarChar(maxlength=20)},
		{'field':'family'    , 'template': ForeignKey(model='family')},
		{'field':'alt_last'  , 'template': VarChar(maxlength=30)},
		{'field':'sex'       , 'template': Enum(items=Student.sex_choices)},
		{'field':'current'   , 'template': Checkbox(suffix='Student is currently in HST')},
		{'field':'birthday'  , 'template': Date()},
		{'field':'grad_year' , 'template': Integer()},
		{'field':'alt_phone' , 'template': PhoneNumber()},
		{'field':'alt_email' , 'template': VarChar(maxlength=254)},
		{'field':'tshirt'    , 'template': Enum(items=Student.t_shirt_sizes)},
		{'field':'needs'     , 'template': VarChar()},
		{'field':'courses_toggle_enrollments', 'template': ToggleSet(field='courses',model='enrollment')},
	],
	'user'      : [
		{'field':'username'  , 'template': Static()},
		{'field':'permission', 'template': Enum(items=User.perm_levels)},
	],
	'coursetrad': [
		{'field':'id'        , 'template': VarChar(maxlength=2)},
		{'field':'title'     , 'template': VarChar(maxlength=50)},
		{'field':'eligex'    , 'template': VarChar(default='~')},
		{'field':'e'         , 'template': Checkbox(suffix='This is a real (and currently offered) course that may be enrolled in, not a student group for admin purposes')},
		{'field':'day'       , 'template': DayOfWeek()},
		{'field':'start'     , 'template': Time()},
		{'field':'end'       , 'template': Time()},
		{'field':'nMeets'    , 'template': Integer()},
		{'field':'semester'  , 'template': Enum(items=CourseTrads.model.semester_choices)},
		{'field':'show'      , 'template': VarChar(maxlength=2,default='SC')},
		{'field':'sa'        , 'template': Checkbox(suffix='This class performs in the Variety Show')},
		{'field':'min_age'   , 'template': Integer(default= 9)},
		{'field':'max_age'   , 'template': Integer(default=18)},
		{'field':'min_grd'   , 'template': Integer(default= 1)},
		{'field':'max_grd'   , 'template': Integer(default=12)},
		{'field':'tuition'   , 'template': Dollar()},
		# {'field':'redtuit'   , 'template': Dollar()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'the_hours' , 'template': Integer()},
		{'field':'auto'      , 'template': Checkbox(suffix='Courses in this tradition are automatically added to eligible carts.')},
		{'field':'trig'      , 'template': Checkbox(suffix='Families must purchase 10 prepaid tickets for $100, not included in tuition')},
		# {'field':'courses'   , 'template': ForeignSet(model='course')},
	],
	'course'    : [
		{'field':'year'      , 'template': Integer()},
		{'field':'last_date' , 'template': Date()},
		{'field':'tuition'   , 'template': Dollar()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'the_hours' , 'template': Integer()},
		{'field':'prepaid'   , 'template': Checkbox()},
		{'field':'teacher'   , 'template': ForeignKey(model='teacher')},
		{'field':'tradition' , 'template': ForeignKey(model='coursetrad')},
		{'field':'aud_date'  , 'template': Date()},
		{'field':'students_toggle_enrollments','template': ToggleSet(field='students')},
	],
	'enrollment': [
		{'field':'student'   , 'template': ForeignKey(model='student')},
		{'field':'course'    , 'template': ForeignKey(model='course')},
		{'field':'role'      , 'template': VarChar()},
		{'field':'role_type' , 'template': Enum(options=['','Chorus','Support','Lead'])},
		{'field':'status'    , 'template': Enum(options=['']+collect(Enrollments.model.status_choices, lambda choice: choice[0]))},
	],
	'invoice': [
		{'field':'family'    , 'template': ForeignKey(model='family')},
		{'field':'amount'    , 'template': Dollar()},
		{'field':'method'    , 'template': Enum(options=['','Cash','Check','PayPal'])},
		{'field':'status'    , 'template': Enum(items=Invoices.model.status_choices)},
		{'field':'items'     , 'template': ForeignSet(model='enrollment')},
	],
}