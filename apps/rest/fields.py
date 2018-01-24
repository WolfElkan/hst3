from .widgets import VarChar, Integer, Enum, Radio, Checkbox, Date, Time, Price, ForeignKey, ForeignSet, ToggleSet
from Utils.custom_fields import Bcrypt, PhoneNumber, ZipCode, DayOfWeek

FIELDS = {
	'address'   : [
		{'field':'line1'     , 'template': VarChar(maxlength=50)},
		{'field':'line2'     , 'template': VarChar(maxlength=50)},
		{'field':'city'      , 'template': VarChar(maxlength=25)},
		{'field':'state'     , 'template': VarChar(maxlength=2)},
		{'field':'zipcode'   , 'template': ZipCode()},
	],
	'family'    : [
		{'field':'last'      , 'template': VarChar(maxlength=30)},
		{'field':'phone'     , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum(options=['','Home','Cell','Work'])},
		{'field':'email'     , 'template': VarChar(maxlength=254)},
		{'field':'mother'    , 'template': ForeignKey()},
		{'field':'father'    , 'template': ForeignKey()},
		{'field':'address'   , 'template': ForeignKey()},
		{'field':'children'  , 'template': ForeignSet()},
	],
	'parent'    : [
		{'field':'first'     , 'template': VarChar(maxlength=20)},
		{'field':'family'    , 'template': ForeignKey()},
		{'field':'alt_last'  , 'template': VarChar(maxlength=30)},
		{'field':'sex'       , 'template': Enum(options=['M','F'])},
		{'field':'alt_phone' , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum(options=['','Home','Cell','Work'])},
		{'field':'alt_email' , 'template': VarChar(maxlength=254)},
	],
	'student'   : [
		{'field':'first'     , 'template': VarChar(maxlength=20)},
		{'field':'middle'    , 'template': VarChar(maxlength=20)},
		{'field':'alt_first' , 'template': VarChar(maxlength=20)},
		{'field':'family'    , 'template': ForeignKey()},
		{'field':'alt_last'  , 'template': VarChar(maxlength=30)},
		{'field':'sex'       , 'template': Enum(options=['M','F'])},
		{'field':'current'   , 'template': Checkbox(suffix='Student is currently in HST')},
		{'field':'birthday'  , 'template': Date()},
		{'field':'grad_year' , 'template': Integer()},
		{'field':'height'    , 'template': Integer(suffix='inches')},
		{'field':'alt_phone' , 'template': PhoneNumber()},
		{'field':'alt_email' , 'template': VarChar(maxlength=254)},
		{'field':'tshirt'    , 'template': Enum(options=['','YS','YM','YL','XS','AS','AM','AL','XL','2X','3X'])},
		{'field':'courses_toggle_enrollments', 'template': ToggleSet(field='courses')},
	],
	'coursetrad': [
		{'field':'title'     , 'template': VarChar(maxlength=50)},
		{'field':'e'         , 'template': Checkbox(suffix='This is a real (and currently offered) course that may be enrolled in, not a student group for admin purposes')},
		{'field':'day'       , 'template': DayOfWeek()},
		{'field':'start'     , 'template': Time()},
		{'field':'end'       , 'template': Time()},
		{'field':'nMeets'    , 'template': Integer()},
		{'field':'show'      , 'template': VarChar(maxlength=2)},
		{'field':'vs'        , 'template': Checkbox(suffix='This class performs in the Variety Show')},
		{'field':'min_age'   , 'template': Integer()},
		{'field':'max_age'   , 'template': Integer()},
		{'field':'min_grd'   , 'template': Integer()},
		{'field':'max_grd'   , 'template': Integer()},
		{'field':'M'         , 'template': Checkbox(suffix='Boys may enroll')},
		{'field':'F'         , 'template': Checkbox(suffix='Girls may enroll')},
		{'field':'C'         , 'template': Checkbox(suffix='Only current students may enroll')},
		{'field':'I'         , 'template': Checkbox(suffix='Students must complete 1 year of Tap or Irish Soft Shoe to enroll')},
		{'field':'A'         , 'template': Radio(options=[
			'No audition or acting class required',
			'Students must pass a skills assessment (or have already taken this class) to enroll',
			'1 year of Acting A or B required to enroll',
			'1 year of Acting A or B required to audition',
			'1 year of Acting and 1 year of Troupe required to audition',
		])},
		{'field':'tuition'   , 'template': Price()},
		{'field':'redtuit'   , 'template': Price()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'the_hours' , 'template': Integer()},
		{'field':'prepaid'   , 'template': Checkbox(suffix='Families must purchase 10 prepaid tickets for $100, not included in tuition')},
		{'field':'courses'   , 'template': ForeignSet()},
	],
	'course'    : [
		{'field':'year'      , 'template': Integer()},
		{'field':'last_date' , 'template': Date()},
		{'field':'tuition'   , 'template': Price()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'the_hours' , 'template': Integer()},
		{'field':'prepaid'   , 'template': Checkbox()},
		{'field':'teacher'   , 'template': ForeignKey()},
		{'field':'tradition' , 'template': ForeignKey()},
		{'field':'aud_date'  , 'template': Date()},
		{'field':'students_toggle_enrollments','template': ToggleSet(field='students')},
	],
	'enrollment': [
		{'field':'student'   , 'template': ForeignKey()},
		{'field':'course'    , 'template': ForeignKey()},
		{'field':'role'      , 'template': VarChar(maxlength=0)},
		{'field':'role_type' , 'template': Enum(options=['','Chorus','Support','Lead'])},
	],
}