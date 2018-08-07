from .widgets import VarChar, Integer, Enum, Radio, Checkbox, Date, Time, ForeignKey, ForeignSet, ToggleSet, NullBoolean, Static, Method
from Utils.custom_fields import Bcrypt, PhoneNumber, ZipCode, DayOfWeek, Dollar
from Utils.data import collect
from apps.program.managers import CourseTrads, Enrollments
from apps.program.eligex   import status_choices
from apps.payment.managers import Invoices
from apps.people.models    import Address, Family, Student, Parent, User

FIELDS = {
	'address'   : [
		{'field':'owner'     , 'template': Static()},
		{'field':'line1'     , 'template': VarChar(maxlength=50)},
		{'field':'line2'     , 'template': VarChar(maxlength=50)},
		{'field':'city'      , 'template': VarChar(maxlength=25)},
		{'field':'state'     , 'template': VarChar(maxlength=2)},
		{'field':'zipcode'   , 'template': ZipCode()},
	],
	'family'    : [
		{'field':'oid'       , 'template': Static()},
		{'field':'hid'       , 'template': Static()},
		{'field':'last'      , 'template': VarChar(maxlength=30)},
		{'field':'phone'     , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum(options=['','Home','Cell','Work'])},
		{'field':'email'     , 'template': VarChar(maxlength=254)},
		{'field':'mother'    , 'template': ForeignKey(model='parent', null=True)},
		{'field':'father'    , 'template': ForeignKey(model='parent', null=True)},
		{'field':'address'   , 'template': ForeignKey(model='address', null=True)},
		{'field':'children'  , 'template': ForeignSet(model='student')},
		{'field':'accounts'  , 'template': ForeignSet(model='user',reflex='owner_id')},
		{'field':'invoices'  , 'template': ForeignSet(model='invoice')},
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
		{'field':'enrollments','template': ForeignSet(model='enrollment')}
		# {'field':'courses_toggle_enrollments', 'template': ToggleSet(field='courses',model='enrollment')},
	],
	'user'      : [
		{'field':'username'  , 'template': Static()},
		{'field':'password'  , 'template': Bcrypt()},
		{'field':'permission', 'template': Enum(items=User.perm_levels)},
		{'field':'owner_id'  , 'template': Static()},
		{'field':'owner'     , 'template': ForeignKey(model='family')}
	],
	'coursetrad': [
		{'field':'id'        , 'template': VarChar(maxlength=2)},
		{'field':'oid'       , 'template': Static()},
		{'field':'m'         , 'template': Checkbox(suffix='This course will be visible on course menu.')},
		{'field':'e'         , 'template': Checkbox(suffix='This course will be visible in family enrollment shopping cart.')},
		{'field':'action'    , 'template': Enum(options=CourseTrads.model.action_choices,default='none')},
		{'field':'title'     , 'template': VarChar(maxlength=50)},
		{'field':'eligex'    , 'template': VarChar(default='a')},
		{'field':'default'   , 'template': Enum(options=dict(status_choices).keys())},
		{'field':'day'       , 'template': DayOfWeek()},
		{'field':'start'     , 'template': Time()},
		{'field':'end'       , 'template': Time()},
		{'field':'place'     , 'template': ForeignKey(model='venue',null=True)},
		{'field':'min_age'   , 'template': Integer(default= 9)},
		{'field':'max_age'   , 'template': Integer(default=18)},
		{'field':'nSlots'    , 'template': Integer()},
		{'field':'show'      , 'template': VarChar(maxlength=2,default='SC')},
		{'field':'early_tuit', 'template': Dollar()},
		{'field':'after_tuit', 'template': Dollar()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'semester'  , 'template': Enum(items=CourseTrads.model.semester_choices,default='B')},
		{'field':'nMeets'    , 'template': Integer(default=20)},
		{'field':'sa'        , 'template': Checkbox(suffix='This class performs in the Variety Show',default=False)},
		{'field':'min_grd'   , 'template': Integer(default= 1)},
		{'field':'max_grd'   , 'template': Integer(default=12)},
		{'field':'the_hours' , 'template': Integer()},
		# {'field':'courses'   , 'template': ForeignSet(model='course')},
	],
	'course'    : [
		{'field':'title'     , 'template': VarChar(maxlength=50)},
		{'field':'year'      , 'template': Integer()},
		{'field':'nSlots'    , 'template': Integer()},
		{'field':'last_date' , 'template': Date()},
		{'field':'early_tuit', 'template': Dollar()},
		{'field':'after_tuit', 'template': Dollar()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'the_hours' , 'template': Integer()},
		{'field':'teacher'   , 'template': ForeignKey(model='teacher')},
		{'field':'tradition' , 'template': ForeignKey(model='coursetrad')},
		{'field':'aud_date'  , 'template': Date()},
		{'field':'enrollments','template': ForeignSet(model='enrollment')}
		# {'field':'students'  , 'template': ForeignSet(model='student')}
		# {'field':'students_toggle_enrollments','template': ToggleSet(field='students')},
	],
	'enrollment': [
		{'field':'student'   , 'template': ForeignKey(model='student')},
		{'field':'course'    , 'template': ForeignKey(model='course')},
		{'field':'status'    , 'template': Enum(options=dict(status_choices).keys())},
		{'field':'tuition'   , 'template': Dollar()},
		{'field':'invoice'   , 'template': ForeignKey(model='invoice',null=True)},
		{'field':'role'      , 'template': VarChar()},
		{'field':'role_type' , 'template': Enum(options=['','Chorus','Support','Lead'])},
	],
	'invoice': [
		{'field':'family'    , 'template': ForeignKey(model='family')},
		{'field':'amount'    , 'template': Dollar()},
		{'field':'method'    , 'template': Enum(options=['','Cash','Check','PayPal'])},
		{'field':'status'    , 'template': Enum(items=Invoices.model.status_choices)},
		{'field':'items'     , 'template': ForeignSet(model='enrollment')},
		{'field':'update_amount','template': Method()},
	],
	'venue': [
		{'field':'id'        , 'template': VarChar(maxlength=3)},
		{'field':'name'      , 'template': VarChar(maxlength=30)},
		{'field':'address'   , 'template': ForeignKey(model='address', null=True)},		
	]
}