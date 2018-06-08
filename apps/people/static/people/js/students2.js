function go(next) {
	$('#next').val(next)
	$('#birthday').val(get_birthday())
	$('#student_info').submit()
}

function isDateSupported() {
	var i = document.createElement("input");
	i.setAttribute("type", "date");
	return i.type !== "text";
}

function determine_birthday_input() {
	if (infolock) {
		$('.static_birthday').show()
		$('.native_birthday').hide()
		$('.manual_birthday').hide()
		return '.frozen_birthday'
	} else {
		$('.static_birthday').hide()
		if (isDateSupported()) {
			$('.native_birthday').show()
			$('.manual_birthday').hide()
			return '.native_birthday'
		} else {
			$('.manual_birthday').show()
			$('.native_birthday').hide()
			return '.manual_birthday'
		}
	}
}

function feb(year) {
	leap = (year % 4 == 0) && (year % 100 != 0) || (year % 400 == 0)
	return leap ? 29 : 28
}

function validate_date(element) {
	year  = $$('#manual_year')
	month = $$('#manual_month')
	date  = $$('#manual_date')
	if (element) {
		element[0].hidden = true
	}
	y = Number(year.value)
	m = Number(month.value)
	d = Number(date.value)
	nDays = [31,feb(y),31,30,31,30,31,31,30,31,30,31][m-1]
	for (var i = 28; i <= 31; i++) {
		date[i].hidden = i > nDays
	}
	if (y && m && d) {
		if (d > nDays) {
			d = set(date,nDays)
		}
		return new Date(y,m-1,d)
	}
}

function get_birthday() {
	birthday_input = determine_birthday_input()
	if (birthday_input == '.manual_birthday') {
		return validate_date().toISOString().substr(0,10)
	} else {
		return $$(birthday_input).value
	}
}