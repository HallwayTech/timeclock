from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import RedirectView
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from timecard.models import TimeEntry
import report.urls
import timecard.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # use time entry as the landing page
    url(r'^$', RedirectView.as_view(url = 'admin/timecard/timeentry/add/')),

    url(r'^report/', include(report.urls)),

    # url(r'^$', 'timeclock.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

