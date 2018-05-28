from django.shortcuts import redirect

from .migrate import transfer

def old(request):
	transfer()
	return redirect('/seed/load/')