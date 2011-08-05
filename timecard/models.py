from django.db import models
from django.contrib.auth.models import User

"""A project to which hours can be attributed
"""
class Project(models.Model):
	name = models.CharField(max_length = 50)
	start_date = models.DateField(blank = True, null = True)
	end_date = models.DateField(blank = True, null = True)

	def __unicode__(self):
		return self.name

"""A record of a block of hours for a project.
"""
class TimeEntry(models.Model):
	user = models.ForeignKey(User)
	date = models.DateField()
	project = models.ForeignKey(Project)
	hours = models.IntegerField()

	def __unicode__(self):
		return self.project

	class Meta:
		verbose_name_plural = 'Time Entries'

