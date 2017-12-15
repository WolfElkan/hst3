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