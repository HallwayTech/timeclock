from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TimeEntry(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    project = models.CharField(max_length = 50)
    hours = models.IntegerField()
    
    def __unicode__(self):
        return "%s - %s - %s" % (self.project, self.date, self.user)