from models import TimeEntry
from django.contrib import admin

class TimeEntryAdmin(admin.ModelAdmin):
    exclude = ('user', 'date_year', 'date_month')
    list_display = ('task', 'date', 'user')
    list_filter = ('date','task')
    ordering = ('date',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

admin.site.register(TimeEntry, TimeEntryAdmin)
