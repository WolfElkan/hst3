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
from trace import DEV

# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
# ]
from django.conf.urls import include

from . import dev_views   as dev
import apps.main.views    as main
import apps.old.views     as old
import apps.payment.views as payment
import apps.people.views  as people
import apps.program.views as program
import apps.rest.views    as rest
import apps.reports.views as reports
import apps.rest.seed     as seed
import apps.radmin.views.main   as radmin
import apps.radmin.views.policy as policy
import apps.radmin.views.year   as year

urlpatterns = [

	url(r'^.*[^/]$', main.slash),

	url(r'^$', main.index),

	url(r'^login(?P<path>.*)/$', main.login),
	url(r'^logout/$', main.logout),
	url(r'^myaccount/$', main.account),
	url(r'^myaccount/changepassword/$', main.changepassword),
	
	url(r'^register/$', people.reg),
	url(r'^register/family/$', people.family),
	url(r'^register/family/changepassword/$', main.changepassword),
	url(r'^myaccount/parents/$', people.parents),
	url(r'^register/parents/$', people.parents),
	url(r'^myaccount/students/$', people.students),
	url(r'^register/students/$', people.students),
	url(r'^register/policy/(?P<page>\d+)/$', people.policy),
	url(r'^myaccount/policy/(?P<page>\d+)/$', people.policy),
	url(r'^myaccount/policy/$', people.policy),

	url(r'^myaccount/courses/$', program.from_myaccount),
	url(r'^register/student/(?P<id>\d+)/$', program.courses),
	url(r'^register/student/(?P<id>\d+)/enroll/$', program.courses_enroll),
	url(r'^register/student/(?P<id>\d+)/audition/$', program.courses_audition),
	url(r'^register/student/(?P<id>\d+)/drop/$', program.courses_drop),

	url(r'^register/process/$',payment.invoice_create),
	url(r'^register/invoice/(?P<id>\d{6})/$',payment.invoice_show),
	url(r'^ipn/$', payment.paypal_ipn),

	url(r'^family/(?P<family_id>\d+)/invoices/$',payment.invoice_index),
	
	url(r'^hot/$', dev.hot),
	url(r'^run/$', dev.run),
	url(r'^clear/$', dev.clear),
	url(r'^nuke/$', seed.nuke),

	url(r'^rest/$', rest.home),
	url(r'^rest/edit/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/$', rest.edit),
	url(r'^rest/show/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/$', rest.show),
	url(r'^rest/update/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/$', rest.update),
	url(r'^rest/index/(?P<model>[a-zA-Z]+)/$', rest.index),
	url(r'^rest/new/(?P<model>[a-zA-Z]+)/$', rest.new),
	url(r'^rest/new/(?P<model>[a-zA-Z]+)/create/$', rest.create),
	url(r'^rest/create/(?P<model>[a-zA-Z]+)/$', rest.create),

	url(r'^reports/$', reports.index),
	url(r'^reports/historical/$', reports.historical),
	url(r'^reports/roster/(?P<id>\d\d\w\w)/$', reports.roster),
	url(r'^reports/students/$', reports.enrollment_matrix),
	url(r'^reports/students/(?P<year>\d{4})/$', reports.enrollment_matrix),

	url(r'^reports/students/mass_enroll/$', reports.mass_enroll),
	url(r'^reports/students/(?P<year>\d{4})/mass_enroll/$', reports.mass_enroll),

	url(r'^reports/students/mass_enroll/register/$', reports.register),
	url(r'^reports/students/(?P<year>\d{4})/mass_enroll/register/$', reports.register),

	url(r'^admin/dashboard/$', radmin.dashboard),

	url(r'^admin/auditions/$', program.audition_menu),
	url(r'^admin/auditions/(?P<id>\d\d\w\w)/$', program.audition_results),
	url(r'^admin/auditions/(?P<id>\d\d\w\w)/process/$', program.audition_process),

	url(r'^admin/policy/edit/$', policy.mod),
	url(r'^admin/policy/edit/(?P<year>\d{4})/$', policy.mod),
	url(r'^admin/policy/show/(?P<year>\d{4})/$', policy.show),
	url(r'^admin/policy/index/$', policy.index),

	url(r'^admin/year/$', year.bib),

	url(r'^rest/(show|edit)/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/add/(?P<foreign_model>[a-zA-Z]+)/$', rest.new),
	url(r'^rest/(show|edit)/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/add/(?P<foreign_model>[a-zA-Z]+)/create/$', rest.create),
	url(r'^rest/delete/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/$', rest.delete),
	url(r'^seed/load/$', seed.load),
	url(r'^seed/dump/$', seed.dump),
	url(r'^seed/nuke/$', seed.nuke),
	url(r'^seed/old/$', old.old),

]

# DEV = False
if not DEV:
	urlpatterns.append(url(r'.*', main.dciv))