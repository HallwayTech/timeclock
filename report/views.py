# Create your views here.
from django.views.generic.list_detail import object_list
from timecard.models import TimeEntry

def user_timeentries(request, page):
    return TimeEntry.objects.filter(user = request.user)
#    return entries_list
#    return object_list(request, queryset = entries_list, page = page)

