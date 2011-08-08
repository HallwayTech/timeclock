from django.conf.urls.defaults import patterns
from views import ReportMonthView, ReportYearView

urlpatterns = patterns('',
    # report by year
    (r'^report/(?P<year>\d{4})/$',
        ReportYearView.as_view(date_field = 'date')),

    # report by year, month
    (r'^report/(?P<year>\d{4})/(?P<month>\d{2})/$',
        ReportMonthView.as_view(date_field = 'date', month_format = '%m')),

	# url(r'^$', 'timeclock.views.home', name='home'),
	# url(r'^timeclock/', include('timeclock.foo.urls')),
)

