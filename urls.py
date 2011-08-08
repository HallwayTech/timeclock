from django.conf.urls.defaults import patterns, include
from django.views.generic.base import RedirectView
import timecard.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # use time entry as the landing page
    (r'^$', RedirectView.as_view(url = 'admin/timecard/timeentry/add/')),

    (r'^timecard/', include(timecard.urls)),

    # url(r'^$', 'timeclock.views.home', name='home'),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

