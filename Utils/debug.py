# Use IceCream?
def pretty(arr, delim='  ', indent='', level=0, printout=''):
	for thing in arr:
		if type(thing) is list:
			printout = pretty(thing, delim, indent+'['+delim, level+1, printout)
		else:
			printout += indent + str(thing) + '\n'
	return printout if level else printout[:-1]

def pdir(thing):
	return pretty(dir(thing))