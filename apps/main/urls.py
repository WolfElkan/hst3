from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index),
	url(r'^hot$', views.hot),
	url(r'^run$', views.run),
	url(r'^test$', views.test),
	url(r'^register$', views.reg),
	url(r'^register/familyinfo$', views.reg_familyinfo),
	# url(r'^nuke$', views.nuke),
]