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

# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
# ]
from django.conf.urls import include

from . import dev_views   as dev
import apps.main.views    as main
import apps.payment.views as payment
import apps.people.views  as people
import apps.program.views as program
import apps.radmin.views  as radmin
import apps.rest.views    as rest
import apps.reports.views as reports
import apps.rest.seed     as seed

urlpatterns = [

	url(r'^$', main.index),

	url(r'^login/?$', main.login),
	url(r'^logout/?$', main.logout),
	url(r'^myaccount/?$', main.account),
	url(r'^myaccount/changepassword/?$', main.changepassword),
	
	url(r'^register/?$', people.reg),
	url(r'^register/familyinfo/?$', people.familyinfo),
	url(r'^register/familyinfo/changepassword/?$', main.changepassword),
	url(r'^myaccount/parents/?$', people.parentsinfo),
	url(r'^register/parentsinfo/?$', people.parentsinfo),
	url(r'^myaccount/students/?$', people.studentsinfo),
	url(r'^register/studentsinfo/?$', people.studentsinfo),

	url(r'^myaccount/courses/?$', program.from_myaccount),
	url(r'^register/student/(?P<id>\d+)/?$', program.courses),
	url(r'^register/student/(?P<id>\d+)/enroll/?$', program.courses_enroll),
	url(r'^register/student/(?P<id>\d+)/audition/?$', program.courses_audition),
	url(r'^register/student/(?P<id>\d+)/drop/?$', program.courses_drop),

	url(r'^register/process/?$',payment.invoice_create),
	url(r'^register/invoice/(?P<id>\d+)/?$',payment.invoice_show),
	url(r'^register/invoice/(?P<id>\d+)/paypal/?$',payment.paypal_pay),
	url(r'^ipn/(?P<csrf>([0-9a-fA-F]-?){32})/?$', payment.paypal_ipn),

	url(r'^family/(?P<family_id>\d+)/invoices/?$',payment.invoice_index),
	
	url(r'^hot/?$', dev.hot),
	url(r'^run/?$', dev.run),
	url(r'^clear/?$', dev.clear),
	url(r'^nuke/?$', dev.clearthedatabaselikeanuclearbombandthisnameisverylongsoyoudontcallitbymistake),

	url(r'^rest/?$', rest.home),
	url(r'^rest/edit/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/?$', rest.edit),
	url(r'^rest/show/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/?$', rest.show),
	url(r'^rest/update/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/?$', rest.update),
	url(r'^rest/index/(?P<model>[a-zA-Z]+)/?$', rest.index),
	url(r'^rest/new/(?P<model>[a-zA-Z]+)/?$', rest.new),
	url(r'^rest/new/(?P<model>[a-zA-Z]+)/create/?$', rest.create),
	url(r'^rest/create/(?P<model>[a-zA-Z]+)/?$', rest.create),

	url(r'^reports/?$', reports.index),
	url(r'^reports/historical/?$', reports.historical),
	url(r'^reports/roster/(?P<id>\d\d\w\w)/?$', reports.roster),
	url(r'^reports/students/?$', reports.students),
	url(r'^reports/students/(?P<year>\d{4})/?$', reports.students),

	url(r'^reports/students/mass_enroll/?$', reports.mass_enroll),
	url(r'^reports/students/(?P<year>\d{4})/mass_enroll/?$', reports.mass_enroll),

	url(r'^reports/students/mass_enroll/register/?$', reports.register),
	url(r'^reports/students/(?P<year>\d{4})/mass_enroll/register/?$', reports.register),

	url(r'^admin/dashboard/?$', radmin.dashboard),

	url(r'^admin/auditions/?$', program.audition_menu),
	url(r'^admin/auditions/(?P<id>\d\d\w\w)/?$', program.audition_results),
	url(r'^admin/auditions/(?P<id>\d\d\w\w)/process/?$', program.audition_process),

	url(r'^admin/newyear/year/?$', radmin.newyear_year),

	url(r'^rest/(show|edit)/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/add/(?P<foreign_model>[a-zA-Z]+)/?$', rest.new),
	url(r'^rest/(show|edit)/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/add/(?P<foreign_model>[a-zA-Z]+)/create/?$', rest.create),
	url(r'^rest/delete/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/?$', rest.delete),
	url(r'^seed/load/?$', seed.load),
	url(r'^seed/dump/?$', seed.dump),
	url(r'^seed/nuke/?$', seed.nuke),

]