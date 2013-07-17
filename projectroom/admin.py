from django.contrib.gis import admin
from django.utils.translation import ugettext as _
import models

__author__ = 'christian'

admin.site.register(models.Company)
admin.site.register(models.Person)
admin.site.register(models.Project)
admin.site.register(models.Account)
admin.site.register(models.AccountEntry)
admin.site.register(models.Rate)
admin.site.register(models.Job)
admin.site.register(models.JobType)
admin.site.register(models.Ticket)
admin.site.register(models.TicketItem)
admin.site.register(models.TicketText)
admin.site.register(models.TicketStatusChange)
admin.site.register(models.TicketAccountEntry)
