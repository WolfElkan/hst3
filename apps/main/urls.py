from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index),
	
	url(r'^register$', views.reg),
	url(r'^register/familyinfo$', views.reg_familyinfo),
	url(r'^register/parentsinfo$', views.reg_parentsinfo),
	url(r'^register/studentsinfo$', views.reg_studentsinfo),
	
	url(r'^hot$', views.hot),
	url(r'^run$', views.run),
	url(r'^test$', views.test),
	url(r'^clear$', views.clear),
	# url(r'^nuke$', views.clearthedatabaselikeanuclearbombandthisnameisverylongsoyoudontcallitbymistake),
]