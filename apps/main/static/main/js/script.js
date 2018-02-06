function $$(arguments) {
	return $(arguments)[0]
}

function set(selector, value) {
	var element = $$(selector)
	if (element.tagName == 'INPUT') {
		element.value = value
	} else if (element.tagName == 'SELECT')
	for (var i = 0; i < element.length; i++) {
		element[i].selected = element[i].value == value || element[i].innerText == value
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