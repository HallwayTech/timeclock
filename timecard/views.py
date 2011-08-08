# Create your views here.
#from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.views.generic.dates import MonthArchiveView, YearArchiveView
from timecard.models import TimeEntry

class ReportMonthView(MonthArchiveView):
    make_object_list = True
    
    def get_queryset(self):
        qs = TimeEntry.objects.filter(user = self.request.user)
        qs = qs.values('date', 'task')
        qs = qs.annotate(Sum('hours'))
        return qs

class ReportYearView(YearArchiveView):
    make_object_list = True
    
    def get_queryset(self):
        qs = TimeEntry.objects.filter(user = self.request.user)
        qs = qs.values('date_year', 'date_month')
        qs = qs.annotate(Sum('hours'))
        return qs
