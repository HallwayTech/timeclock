from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import RedirectView
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from timecard.models import TimeEntry

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# use time entry as the landing page
	url(r'^$', RedirectView.as_view(url = 'admin/timecard/timeentry/add/')),

	# report by year
	url(r'^report/(?P<year>\d{4})/$',
		YearArchiveView.as_view(
			date_field = 'date',
			queryset = TimeEntry.objects.all())),

	# report by year, month
	url(r'^report/(?P<year>\d{4})/(?P<month>\d{2})/$',
		MonthArchiveView.as_view(
			date_field = 'date',
			month_format = '%m',
			queryset = TimeEntry.objects.all())),

	# url(r'^$', 'timeclock.views.home', name='home'),
	# url(r'^timeclock/', include('timeclock.foo.urls')),

	# Uncomment the admin/doc line below to enable admin documentation:
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
)

