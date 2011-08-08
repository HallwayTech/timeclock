from django.db import models
from django.contrib.auth.models import User

"""A record of a block of hours for a task.
"""
class TimeEntry(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    date_year = models.IntegerField()
    date_month = models.IntegerField()
    task = models.CharField(max_length = 50)
    hours = models.IntegerField()

    def __unicode__(self):
        return "%s (%s)" % (self.task, self.hours)

    def save(self):
        self.date_year = self.date.year
        self.date_month = self.date.month
        super(TimeEntry, self).save()

    class Meta:
        verbose_name_plural = 'Time Entries'
