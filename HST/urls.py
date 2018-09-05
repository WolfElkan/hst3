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
#from trace import DEV

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
import apps.reports.views as reports

import apps.rest.views.main     as rest
import apps.rest.views.seed     as seed
import apps.rest.views.merge    as merge

import apps.radmin.views.main   as radmin
import apps.radmin.views.policy as policy
import apps.radmin.views.year   as year

urlpatterns = [

	# url(r'^reports/(?P<template>.+\.html)$', reports.general),
	url(r'^.*[^/]$', main.slash),

	url(r'^$', main.index),
	url(r'^login(?P<path>.*)/$', main.login),
	url(r'^logout/$', main.logout),
	url(r'^myaccount/$', main.account),
	
	url(r'^(?P<ref>register|myaccount)/changepassword/$',main.changepassword),
	url(r'^rest/edit/user/(?P<them_id>\d+)/sudochangepassword/$',main.changepassword),
	
	url(r'^(?P<ref>register|myaccount)/(?P<step>redirect|family|parents|students|policy)/(?P<id>[^/]*)/$',people.reg),
	url(r'^(?P<ref>register|myaccount)/(?P<step>redirect|family|parents|students|policy)/$',people.reg),

	url(r'^(?P<ref>register|myaccount)/classes/(?P<id>[^/]*)/$',program.courses),
	url(r'^(?P<ref>register|myaccount)/classes/$',program.oldest_student),
	url(r'^(?P<ref>register|myaccount)/classes/(?P<id>\d+)/enroll/$', program.courses_enroll),
	# url(r'^(?P<ref>register|myaccount)/classes/(?P<id>\d+)/audition/$', program.courses_audition),
	url(r'^(?P<ref>register|myaccount)/classes/(?P<id>\d+)/drop/$', program.courses_drop),
	url(r'^(?P<ref>register|myaccount)/classes/(?P<id>\d+)/cancel/$', program.courses_cancel),

	url(r'^(?P<ref>register|myaccount)/process/$',payment.invoice_create),
	url(r'^(?P<ref>register|myaccount|rest)/invoice/(?P<id>\d{6})/$',payment.invoice_show),
	url(r'^(?P<ref>register|myaccount|rest)/invoice/(?P<id>\d{6})/sudo/$',radmin.sudo_invoice),

	url(r'^ipn/$', payment.paypal_ipn),

	url(r'^family/(?P<family_id>\d+)/invoices/$',payment.invoice_index),
	
	url(r'^hot/$', dev.hot),
	url(r'^run/$', dev.run),
	url(r'^clear/$', dev.clear),
	# url(r'^nuke/$', seed.nuke),

	url(r'^rest/$', rest.home),
	url(r'^rest/search/$', rest.search),
	url(r'^rest/edit/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w|\w{3})/$', rest.edit),
	url(r'^rest/show/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w|\w{3})/$', rest.show),
	url(r'^rest/update/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/$', rest.update),
	url(r'^rest/index/(?P<model>[a-zA-Z]+)/$', rest.index),
	url(r'^rest/new/(?P<model>[a-zA-Z]+)/$', rest.new),
	url(r'^rest/new/(?P<model>[a-zA-Z]+)/create/$', rest.create),
	url(r'^rest/create/(?P<model>[a-zA-Z]+)/$', rest.create),

	url(r'^rest/admin/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w|\w{3})/$', rest.admin),

	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/$', merge.records),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/swap/$', merge.swap),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/copy/$', merge.copy),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/transfer/$', merge.transfer),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/delete/$', merge.delete),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/move_all/$', merge.move_all),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/sub_move/$', merge.sub_move),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/sub_move/transfer/$', merge.sub_transfer),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/sub_move/delete/$', merge.sub_delete),
	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/sub_merge/$', merge.sub_merge),

	url(r'^rest/merge/$', merge.new_merge),

	url(r'^rest/merge/(?P<model>[a-zA-Z]+)/(?P<old_id>\d+|(\d\d)?\w\w|\w{3})/(?P<new_id>\d+|(\d\d)?\w\w|\w{3})/sub_m(ove|erge)/exit/$', merge.sub_exit),

	url(r'^reports/$', reports.index),
	url(r'^reports/historical/$', reports.historical),
	url(r'^reports/roster/(?P<id>\d\d\w\w)/$', reports.roster),
	url(r'^reports/students/$', reports.enrollment_matrix),
	url(r'^reports/students/(?P<year>\d{4})/$', reports.enrollment_matrix),

	url(r'^reports/students/mass_enroll/$', reports.mass_enroll),
	url(r'^reports/students/(?P<year>\d{4})/mass_enroll/$', reports.mass_enroll),

	url(r'^reports/addresse?s?/$', reports.address),
	url(r'^reports/directory/$', reports.directory),
	url(r'^reports/registration/$', reports.registration),

	url(r'^reports/students/mass_enroll/register/$', reports.register),
	url(r'^reports/students/(?P<year>\d{4})/mass_enroll/register/$', reports.register),

	url(r'^reports/summary/(?P<year>\d{4})/$', reports.summary),
	url(r'^reports/summary/$', reports.summary),
	url(r'^reports/summary/(?P<year>\d{4})/refresh/$', reports.refresh_summary),
	url(r'^reports/summary/refresh/$', reports.refresh_summary),
	url(r'^reports/summary/generate/$', reports.generate_summary),
	url(r'^reports/summary/\d{4}/generate/$', reports.generate_summary),

	url(r'^reports/overview/$', reports.overview),

	url(r'^admin/dashboard/$', radmin.dashboard),

	url(r'^admin/auditions/$', program.audition_menu),
	url(r'^admin/auditions/(?P<id>\d\d\w\w)/$', program.audition_results),
	url(r'^admin/auditions/(?P<id>\d\d\w\w)/process/$', program.audition_process),

	url(r'^admin/deferred/$', radmin.deferred),
	url(r'^admin/deferred/rescind/$', radmin.rescind),

	url(r'^admin/policy/edit/$', policy.mod),
	url(r'^admin/policy/edit/(?P<year>\d{4})/$', policy.mod),
	url(r'^admin/policy/show/(?P<year>\d{4})/$', policy.show),
	url(r'^admin/policy/index/$', policy.index),

	url(r'^admin/year/$', year.bib),

	url(r'^sudo/$', radmin.sudo),
	url(r'^sudo/exit/$', radmin.sudo_exit),	

	url(r'^rest/(show|edit)/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/add/(?P<foreign_model>[a-zA-Z]+)/$', rest.new),
	url(r'^rest/(show|edit)/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/add/(?P<foreign_model>[a-zA-Z]+)/create/$', rest.create),
	url(r'^rest/delete/(?P<model>[a-zA-Z]+)/(?P<id>\d+|(\d\d)?\w\w)/$', rest.delete),
	url(r'^seed/load/$', seed.load),
	url(r'^seed/dump/$', seed.dump),
	# url(r'^seed/nuke/$', seed.nuke),
	url(r'^seed/old/$', old.old),

#	url(r'.*', main.dciv),
]
