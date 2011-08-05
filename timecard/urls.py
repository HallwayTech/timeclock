from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import RedirectView
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from models import TimeEntry

urlpatterns = patterns('',
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
)

