function $$(arguments) {
	return $(arguments)[0]
}

function set(selector, value, create=false) {
	value = String(value)
	var element = type(selector) == String ? $$(selector) : selector
	if (element.tagName == 'INPUT') {
		element.value = value
		return element.value
	} else if (element.tagName == 'SELECT') {
		var winner = undefined
		for (var i = 0; i < element.length; i++) {
			selected = element[i].value == value || element[i].innerText == value
			element[i].selected = selected
			if (selected) {
				winner = element[i]
			}
		}
		if (winner) {
			return winner.value
		} else if (create) {
			created = new Option(value, value, true, true)
			element.add(created)
			return value
		}
	}
}

function custom_parse(json) {
		json = json.replace(/&quot;/g, '"')
		// json = json.replace(/("regex": )(")([^"]*)(")/g, "$1/$3/")
		// json = json.replace(/"regex": "/g, '"regex": /')
		json = json.replace(/\\/g,"\\\\")
		// json = json.replace(/~/g,"~")
		// json = JSON.stringify(json)
		return JSON.parse(json)
}

function type(thing) {
	return thing.__proto__.constructor
}

function DateET() {
	if (arguments.length == 1) {
		arg = arguments[0]
		if (type(arg) == Number) {
			return new Date(arg)
		} else if (type(arg) == String) {
			ymd = arg.match(/(\d{4})-(\d{2})-(\d{2})/) 
			if (ymd) {
				return new Date(ymd[1],ymd[2]-1,ymd[3])
			}
		} else if (type(arg) == Date) {
			if (arg.getTimezoneOffset() == 240 && String(arg).substr(35,3) == 'EDT' ||
				arg.getTimezoneOffset() == 300 && String(arg).substr(35,3) == 'EST') {
				return arg
			} else {
				return new Date(Number(arg))
			}
		}
	} else {
		a = arguments
		return [
			new Date(),
			new Date(a[0]),
			new Date(a[0],a[1]),
			new Date(a[0],a[1],a[2]),
			// new Date(a[0],a[1],a[2],a[3]),
			// new Date(a[0],a[1],a[2],a[3],a[4]),
			// new Date(a[0],a[1],a[2],a[3],a[4],a[5]),
			// new Date(a[0],a[1],a[2],a[3],a[4],a[5],a[6]),
			// new Date(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7])
		][a.length]
	}
}