from .widgets import VarChar, Integer, Enum, Radio, Checkbox, Date, Time, ForeignKey, ForeignSet, ToggleSet, NullBoolean, Static, Method
from Utils.custom_fields import Bcrypt, PhoneNumber, ZipCode, DayOfWeek, Dollar
from Utils.data import collect, sub
from apps.program.managers import CourseTrads, Enrollments
from apps.program.eligex   import status_choices
from apps.payment.managers import Invoices
from apps.people.models    import Address, Family, Student, Parent, User

fields = {
	'address'   : [
		{'field':'owner'     , 'template': Static()},
		{'field':'line1'     , 'template': VarChar(maxlength=50)},
		{'field':'line2'     , 'template': VarChar(maxlength=50)},
		{'field':'city'      , 'template': VarChar(maxlength=25)},
		{'field':'state'     , 'template': VarChar(maxlength=2)},
		{'field':'zipcode'   , 'template': ZipCode()},
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'family'    : [
		{'field':'oid'       , 'template': Static()},
		{'field':'hid'       , 'template': Static()},
		{'field':'last'      , 'template': VarChar(maxlength=30)},
		{'field':'phone'     , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum(options=['','Home','Cell','Work'])},
		{'field':'email'     , 'template': VarChar(maxlength=254)},
		{'field':'mother'    , 'template': ForeignKey(model='parent', null=True, order_by='sex')},
		{'field':'father'    , 'template': ForeignKey(model='parent', null=True, order_by='sex')},
		{'field':'address'   , 'template': ForeignKey(model='address', null=True, order_by='zipcode')},
		{'field':'children'  , 'template': ForeignSet(model='student')},
		{'field':'accounts'  , 'template': ForeignSet(model='user',reflex='owner_id')},
		{'field':'invoices'  , 'template': ForeignSet(model='invoice')},
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'parent'    : [
		{'field':'first'     , 'template': VarChar(maxlength=20)},
		{'field':'family'    , 'template': ForeignKey(model='family',order_by=['last','name_num'])},
		{'field':'alt_last'  , 'template': VarChar(maxlength=30)},
		{'field':'sex'       , 'template': Enum(items=Parent.sex_choices)},
		{'field':'alt_phone' , 'template': PhoneNumber()},
		{'field':'phone_type', 'template': Enum(options=['','Home','Cell','Work'])},
		{'field':'alt_email' , 'template': VarChar(maxlength=254)},
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'student'   : [
		{'field':'hid'       , 'template': Static()},
		{'field':'first'     , 'template': VarChar(maxlength=20)},
		{'field':'alt_first' , 'template': VarChar(maxlength=20)},
		{'field':'family'    , 'template': ForeignKey(model='family',order_by=['last','name_num'])},
		{'field':'alt_last'  , 'template': VarChar(maxlength=30)},
		{'field':'sex'       , 'template': Enum(items=Student.sex_choices)},
		{'field':'current'   , 'template': Checkbox(suffix='Student is currently in HST')},
		{'field':'birthday'  , 'template': Date(cake=0x1f388)},
		{'field':'grad_year' , 'template': Integer()},
		{'field':'alt_phone' , 'template': PhoneNumber()},
		{'field':'alt_email' , 'template': VarChar(maxlength=254)},
		{'field':'tshirt'    , 'template': Enum(items=Student.t_shirt_sizes)},
		{'field':'needs'     , 'template': VarChar()},
		{'field':'enrollment', 'template': ForeignSet(model='enrollment')},
		# {'field':'courses_toggle_enrollments', 'template': ToggleSet(field='courses',model='enrollment')},
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'user'      : [
		{'field':'username'  , 'template': Static()},
		{'field':'password'  , 'template': Bcrypt()},
		{'field':'permission', 'template': Enum(items=User.perm_levels)},
		{'field':'owner_id'  , 'template': Static()},
		{'field':'owner'     , 'template': ForeignKey(model='family',order_by=['last','name_num'])},
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'coursetrad': [
		{'field':'id'        , 'template': VarChar(maxlength=2)},
		{'field':'oid'       , 'template': Static()},
		{'field':'order'     , 'template': Integer()},
		{'field':'r'         , 'template': Checkbox(suffix='This course is real, and not an aggregator.')},
		{'field':'m'         , 'template': Checkbox(suffix='This course will be visible on course menu.')},
		{'field':'e'         , 'template': Checkbox(suffix='This course will be visible in family enrollment shopping cart.')},
		{'field':'action'    , 'template': Enum(options=CourseTrads.model.action_choices,default='none')},
		{'field':'title'     , 'template': VarChar(maxlength=50)},
		{'field':'abbr'      , 'template': VarChar(maxlength=13)},
		{'field':'eligex'    , 'template': VarChar(default='a')},
		{'field':'default'   , 'template': Enum(options=dict(status_choices).keys())},
		{'field':'day'       , 'template': DayOfWeek()},
		{'field':'start'     , 'template': Time()},
		{'field':'end'       , 'template': Time()},
		{'field':'place'     , 'template': ForeignKey(model='venue',null=True,order_by='name')},
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
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'course'    : [
		{'field':'title'     , 'template': VarChar(maxlength=50)},
		{'field':'abbr'      , 'template': VarChar(maxlength=13)},
		{'field':'year'      , 'template': Integer()},
		{'field':'nSlots'    , 'template': Integer()},
		{'field':'last_date' , 'template': Date()},
		{'field':'early_tuit', 'template': Dollar()},
		{'field':'after_tuit', 'template': Dollar()},
		{'field':'vol_hours' , 'template': Integer()},
		{'field':'the_hours' , 'template': Integer()},
		{'field':'teacher'   , 'template': ForeignKey(model='teacher',order_by=['last','first'])},
		{'field':'tradition' , 'template': ForeignKey(model='coursetrad',order_by='order')},
		{'field':'aud_date'  , 'template': Date()},
		{'field':'repop'     , 'template': Method()},
		{'field':'enrollments','template': ForeignSet(model='enrollment')},
		# {'field':'students'  , 'template': ForeignSet(model='student')},
		# {'field':'students_toggle_enrollments','template': ToggleSet(field='students')},
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'enrollment': [
		{'field':'student'   , 'template': ForeignKey(model='student',order_by=['family__last','family__name_num','birthday'])},
		{'field':'course'    , 'template': ForeignKey(model='course',order_by=['year','tradition__order'])},
		{'field':'status'    , 'template': Enum(options=dict(status_choices).keys())},
		{'field':'tuition'   , 'template': Dollar()},
		{'field':'invoice'   , 'template': ForeignKey(model='invoice',null=True)},
		{'field':'role'      , 'template': VarChar()},
		{'field':'role_type' , 'template': Enum(options=['','Chorus','Support','Lead'])},
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'invoice': [
		{'field':'family'    , 'template': ForeignKey(model='family',order_by=['last','name_num'])},
		{'field':'amount'    , 'template': Dollar()},
		{'field':'method'    , 'template': Enum(options=['','Cash','Check','PayPal'])},
		{'field':'status'    , 'template': Enum(items=Invoices.model.status_choices)},
		{'field':'items'     , 'template': ForeignSet(model='enrollment')},
		# {'field':'update_amount','template': Method()},
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	],
	'venue': [
		{'field':'id'        , 'template': VarChar(maxlength=3)},
		{'field':'name'      , 'template': VarChar(maxlength=30)},
		{'field':'address'   , 'template': ForeignKey(model='address', null=True, order_by='zipcode')},		
		{'field':'created_at', 'template': Static()},
		{'field':'updated_at', 'template': Static()},
	]
}

class FieldIndex(object):
	def __init__(self, fields, subs):
		super(FieldIndex, self).__init__()
		self.fields = fields
		self.subs = subs
	def __getitem__(self, key):
		key = str(key)
		key = sub(key, self.subs)
		return self.fields[key]

FIELDS = FieldIndex(fields, {
	'mother':'parent',
	'father':'parent',
})		

