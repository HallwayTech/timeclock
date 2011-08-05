from models import Project, TimeEntry
from django.contrib import admin

class TimeEntryAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('project', 'date', 'user')
    list_filter = ('date','project__name')
    ordering = ('date',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

admin.site.register(Project)
admin.site.register(TimeEntry, TimeEntryAdmin)

