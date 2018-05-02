var trace = false

var fields = ['first','alt_last','alt_first','sex','birthday','grad_year','tshirt','alt_phone','alt_email']

function zeropad(num, places) {
// if (trace && student_bank[0]) {console.log(student_bank[0].first)}
// if (trace) {console.log('zeropad',arguments)}
	num = Math.floor(num)
	var pad = ''
	for (var i = 0; i < places-String(num).length; i++) {
		pad += '0'
	}
	return pad + String(num)
}

function phone_format(num) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('phone_format',num)}
	var cod  = zeropad(num / 10**7, 3)
	var mid  = zeropad(num % 10**7 / 10**4, 3)
	var last = zeropad(num % 10**4, 4)
	return `(${cod}) ${mid}-${last}`
}

function date_format(date) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('date_format',date)}
	months = ['Jan','Feb','March','April','May','June','July','Aug','Sep','Oct','Nov','Dec']
	return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`
}

function Student(arg) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('Student',arg)}
	var isNew = type(arg) == Number
	this.id  = isNew ? arg : arg.id
	this.pre = isNew ? 'n' : 'd'
	this.sid = this.pre + this.id
	this.exists = arg.current || isNew
	this.isNew = isNew
	this.update = function() {
	if (trace && student_bank[0]) {console.log(student_bank[0].first)}
	if (trace) {console.log('Student.update')}
		if (this.isNew || form_type == 2) {
			for (var i = 0; i < fields.length; i++) {
				var field = fields[i]
				this[field] = $$('#'+field).value
			}
		} else {
			for (var i = 0; i < fields.length; i++) {
				var field = fields[i]
				this[field] = arg[field] ? arg[field] : ''
			}
		}
		if (this.birthday && type(this.birthday) == String) {
			this.birthday = {
				'year' : Number(this.birthday.substr(0,4)),
				'month': Number(this.birthday.substr(5,2)),
				'date' : Number(this.birthday.substr(8,2)),
			}
			if (this.birthday.year < reg_year % 100) {
				this.birthday.year += Math.floor(reg_year / 100) * 100
			} else if (this.birthday.year < 100) {
				this.birthday.year += Math.floor(reg_year / 100) * 100 - 100
			}
			this.birthday.js = new Date(this.birthday.year, this.birthday.month-1, this.birthday.date)
			this.birthday.db = `${zeropad(this.birthday.year,4)}-${zeropad(this.birthday.month,2)}-${zeropad(this.birthday.date,2)}`
		}
		this.grade = this.grad_year ? reg_year - this.grad_year + 12 : ''
		if (this.grade > 12) {
			this.grade = ''
		}
		this.hst_age = reg_year - this.birthday.year - 1

	}
	this.update()
	this.cur_age = function() {
	if (trace && student_bank[0]) {console.log(student_bank[0].first)}
	if (trace) {console.log('Student.cur_age')}
		var now = new Date()
		var c_month = now.getMonth() + 1
		var c_date  = now.getDate()
		var had_birthday = c_month * 31 + c_date >= this.birthday.month * 31 + this.birthday.date
		var age_this_year = now.getFullYear() - this.birthday.year
		var age = age_this_year + (had_birthday ? 0 : -1)
		if (age != this.hst_age) {
			$('.footnote').show()
		}
		return age
	}
	this.isValid = function(validations) {
		return true
	// if (trace && student_bank[0]) {console.log(student_bank[0].first)}
	// if (trace) {console.log('Student.isValid',validations)}
	// 	console.log(this)
	// 	for (var i = 0; i < validations.length; i++) {
	// 		var regex = new RegExp(validations[i].regex)
	// 		var field = validations[i].field
	// 		if (!String(this[field]).match(regex)) {
	// 			return false
	// 		}
	// 	}
	// 	return true
	}
	this.show_errors = function(validations) {
	if (trace && student_bank[0]) {console.log(student_bank[0].first)}
	if (trace) {console.log('Student.show_errors',validations)}
		var error_tds = $('.error')
		for (var i = 0; i < error_tds.length; i++) {
			error_tds[i].innerText = ''
		}
		for (var i = 0; i < validations.length; i++) {
			var regex = new RegExp(validations[i].regex)
			var field = validations[i].field
			if (!String(this[field]).match(regex)) {
				$$('#'+field+'_error').innerText = validations[i].error
			}
		}
	}
	this.populate_form = function() {
	if (trace && student_bank[0]) {console.log(student_bank[0].first)}
	if (trace) {console.log('Student.populate_form')}
		for (var i = 0; i < fields.length; i++) {
			var field = fields[i]
			set('#'+field, this[field])
		}				
		$$('#birthday').value = this.birthday.db
		$$('#birthday_static').innerText = date_format(this.birthday.js)
		if (this.isNew) {
			$('#birthday').show()
			$('#birthday_static').hide()
		} else {
			$('#birthday_static').show()
			$('#birthday').hide()
		}
	}
	this.tr = function() {
	if (trace && student_bank[0]) {console.log(student_bank[0].first)}
	if (trace) {console.log('Student.tr')}
		return `<tr id="${this.sid}"><td>${this.alt_first ? this.alt_first : this.first} ${this.alt_last ? this.alt_last : family_last}</td><td>${this.birthday ? this.hst_age : ''}${this.hst_age == this.cur_age() ? '' : '*'}</td><td>${this.sex}</td><td>${this.grade}</td><td>${this.tshirt}</td><td>${this.alt_phone ? phone_format(this.alt_phone) : ''}</td><td>${this.alt_email ? this.alt_email : ''}</td><td><button class="edit">Edit</button><button class="delete">Delete</button></td></tr>`
	} 
	this.json = function() {
	if (trace && student_bank[0]) {console.log(student_bank[0].first)}
	if (trace) {console.log('Student.json')}
		var columns = ['first','alt_last','alt_first','sex','grad_year','alt_phone','alt_email','tshirt','isNew','exists']
		json_obj = {}
		for (var i = 0; i < columns.length; i++) {
			var col = columns[i]
			if (this[col] || this[col] === false) {
				json_obj[col] = this[col]
			}
			if (!this.isNew) {
				json_obj.id = this.id
			}
		}
		json_obj.birthday = this.birthday.db
		return json_obj
	}
}

function clear_form() {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('clear_form')}
	for (var i = 0; i < fields.length; i++) {
		var field = fields[i]
		$$('#'+field).value = ''
		$$('#'+field+'_error').innerText = ''
	}
	update_alt_first_placeholder()
}

function update_alt_first_placeholder() {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('update_alt_first_placeholder')}
	$$('#alt_first').placeholder = $$('#first').value
}

function form_display(type) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('form_display',type)}
	form_type = type
	if (type) {
		$('#student_form_div').css('display','inline-block')
		if (type == 1) {
			$$('#student_form_type').innerText = 'New Student:'
		} else if (type == 2) {
			$$('#student_form_type').innerText = 'Edit Student:'
		}
	} else {
		$('#student_form_div').css('display','none')
	}
}

function find_student(sid) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('find_student',sid)}
	for (var i = 0; i < student_bank.length; i++) {
		var student = student_bank[i]
		if (student.sid == sid) {
			student.index = i
			return student
		}
	}
}

function save_student(student) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('save_student',student)}
	student.update()
	if (form_type == 1) {
		student_bank.push(student)
		$('#student_list').append(student.tr())
	} else if (form_type == 2) {
		console.log(student.first)
		$$('#'+student.sid).outerHTML = student.tr()
		x = find_student(student.sid).index
		student_bank[x] = student
	}
	dynamic(student.sid)
	form_display(0)
	clear_form()
}

function edit_student(sid) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('edit_student',sid)}
	current_sid = sid
	var student = find_student(sid)
	// console.log(student)
	student.populate_form()
	form_display(2)
}

function delete_student(sid) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('delete_student',sid)}
	find_student(sid).exists = false
	if (sid == current_sid) {
		form_display(0)
	}
	$('#'+sid).hide()
}

// Add functionality to dynamically created Edit and Delete buttons
function dynamic(sid) {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('dynamic',sid)}
	trid = $('#'+sid)
	trid.find('.edit').click(function() {
		edit_student(sid)
	})
	trid.find('.delete').click(function() {
		delete_student(sid)
	})
}

function new_current_sid_increment() {
if (trace && student_bank[0]) {console.log(student_bank[0].first)}
if (trace) {console.log('new_current_sid_increment')}
	var max = 0
	for (var i = 0; i < student_bank.length; i++) {
		student = student_bank[i]
		if (student.isNew && student.id > max) {
			max = student.id
		}
	}
	max += 1
	return max
}

// Which student is currently being created or edited
var current_sid = ''

// 0 = Form Hidden, 1 = New Student, 2 = Edit Student
var form_type = 0

// Array to hold the students until page is submitted
var student_bank = []

$(document).ready(function() {

	$('#add_student').click(function() {
		clear_form()
		if (form_type == 0) {
			current_sid = new_current_sid_increment()
			console.log(current_sid)
			form_display(1)
		}
	})

	$('#save_student').click(function() {
		if (form_type == 1) {
			var student = new Student(current_sid)
		} else if (form_type == 2) {
			var student = find_student(current_sid)
		}
		if (student.isValid(validations)) {
			student.sid = current_sid
			save_student(student)
			$('#submit').show()
		} else {
			student.show_errors(validations)
		}
	})

	$('#cancel').click(function() {
		form_display(0)
		clear_form()
	})

	$('#first').focusout(function() {
		update_alt_first_placeholder()
	})

	$('#submit').click(function() {
		students_json = []
		for (var i = 0; i < student_bank.length; i++) {
			student = student_bank[i]
			if (student.exists || !student.isNew) {}
			students_json.push(student_bank[i].json())
		}
		$$('#data').value = JSON.stringify(students_json)
		$('#submission').submit()
	})

	// console.log(students_from_db)
	for (var i = 0; i < students_from_db.length; i++) {
		student = new Student(students_from_db[i])
		if (student.exists) {
			student_bank.push(student)
			$('#student_list').append(student.tr())
			dynamic(student.sid)
			$('#submit').css('display','block')
		}
	}

})