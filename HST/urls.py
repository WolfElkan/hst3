"""HST URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]
from django.conf.urls import include
import apps.main.views as main
import apps.program.views as program
import apps.program.seed as program_seed

urlpatterns = [
	url(r'^$', main.index),

	url(r'^login$', main.login),
	url(r'^logout$', main.logout),
	
	url(r'^register$', main.reg),
	url(r'^register/familyinfo$', main.reg_familyinfo),
	url(r'^register/parentsinfo$', main.reg_parentsinfo),
	url(r'^register/studentsinfo$', main.reg_studentsinfo),
	
	url(r'^hot$', main.hot),
	url(r'^run$', main.run),
	url(r'^clear$', main.clear),
	url(r'^nuke$', main.clearthedatabaselikeanuclearbombandthisnameisverylongsoyoudontcallitbymistake),

	url(r'^seed$', program_seed.CourseTraditions),
]
