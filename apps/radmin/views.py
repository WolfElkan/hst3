from django.shortcuts import render

# Create your views here.

def dashboard(request, **kwargs):
	context = {}
	return render(request, 'dashboard.html', context)
