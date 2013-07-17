# django imports
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

# django-apps

from mptt.models import TreeForeignKey, MPTTModel, TreeManager

# python imports
import datetime

#


JOB_STATUS_CHOICES = (
    (1, 'Requested by Customer'),
    (2, 'Seen by Worker'),
    (3, 'Started by Worker'),
    (4, 'Cancelled by Worker'),
    (5, 'Cancelled by Customer'),
    (6, 'Waiting for Approval by Customer'),
    (7, 'Approved by Customer'),
    (8, 'Worker waiting to get Payed'),
    (9, 'Closed and finished by Worker')
)

JOB_STATUS_LEN = len(JOB_STATUS_CHOICES)

CURRENCY_CHOICES = (
    ('EUR', 'Euro'),
    ('CHF', 'Swiss Francs'),
)


class JobType(models.Model):
    """
    i.e.: programming
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def __unicode__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def __unicode__(self):
        return self.name

class Person(models.Model):
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)

    def __unicode__(self):
        return self.user.get_full_name()

class Project(models.Model):
    client_company = models.ForeignKey(Company)
    read_acl = models.ManyToManyField(Person, null=True, blank=True, related_name='project_readacl')
    write_acl = models.ManyToManyField(Person, null=True, blank=True, related_name='project_writeacl')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('client_company__name',)

class Account(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    balance = models.DecimalField("Kontostand", decimal_places=2, max_digits=8, blank=True)
    currency = models.CharField(_('Currency'), max_length=3, choices=CURRENCY_CHOICES)

    def __unicode__(self):
        return self.name

    def calculate_balance(self):
        ai = self.accountentry_set.all().aggregate(values_sum = models.Sum('value'))
        values_sum = ai.get('values_sum')
        return values_sum

class AccountEntry(models.Model):
    account = models.ForeignKey(Account)
    value = models.DecimalField("Wert", decimal_places=2, max_digits=8)


class Rate(models.Model):
    """
    Rate per Client = Tarif
    """
    hourly_rate = models.DecimalField("Stundensatz", decimal_places=2, max_digits=8)
    initial_rate = models.DecimalField("Einmaliger Satz", decimal_places=2, max_digits=8)
    currency = models.CharField(_('Currency'), max_length=3, choices=CURRENCY_CHOICES)
    rate_of_taxation = models.DecimalField("Steuersatz", decimal_places=2, max_digits=8)

    def __unicode__(self):
        return _('%(hr)s %(c)s/h') % {
            'hr': self.hourly_rate,
            'c': self.get_currency_display()
        }

class JobManager(TreeManager):
    def open(self):
        return self.filter(ticket__status__lt=JOB_STATUS_LEN)


class Job(MPTTModel):
    project = models.ForeignKey(Project)
    job_type = models.ForeignKey(JobType)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    rate = models.ForeignKey(Rate)
    request_by = models.ForeignKey(Person)
    account = models.ForeignKey(Account)

    objects = JobManager()

    def get_path(self):
        return self.get_ancestors(include_self=True)

    def get_all_tickets(self):
        ticket_ids = []
        subjobs = self.get_descendants(include_self=True)
        for job in subjobs:
            ticket_ids.extend(job.ticket_set.values_list('pk', flat=True))
        return Ticket.objects.filter(pk__in=ticket_ids)

    @models.permalink
    def get_absolute_url(self):
        return ('job', [], {'pk': self.pk, 'project__slug': self.project.slug})

    @models.permalink
    def get_edit_url(self):
        return ('job_edit', [], {'pk': self.pk, 'project__slug': self.project.slug})

    def __unicode__(self):
        return self.name

class TicketManager(models.Manager):
    def active(self):
        return self.filter(status__lt = JOB_STATUS_LEN)

class Ticket(models.Model):
    job = models.ForeignKey(Job)
    name = models.CharField(max_length=255)

    request_by = models.ForeignKey(Person, related_name='requested_tickets')
    status = models.IntegerField(choices=JOB_STATUS_CHOICES)
    assigned_to = models.ForeignKey(Person, related_name='assigned_tickets', null=True, blank=True)
    duration_pre = models.IntegerField(null=True, blank=True)
    duration_post = models.IntegerField(null=True, blank=True)

    objects = TicketManager()

    def update_status(self):
        tsc = TicketStatusChange.objects.filter(item__ticket=self).latest('item__created')
        self.status = tsc.post_status

    def progress(self):
        return float(self.status) / float(JOB_STATUS_LEN) * 100.0

    def get_costs(self):
        return self.job.rate.hourly_rate * self.duration_pre

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('ticket', [], {'pk': self.pk, 'project__slug': self.job.project.slug, 'job__pk': self.job.pk})

class TicketItem(models.Model):
    ticket = models.ForeignKey(Ticket)
    creator = models.ForeignKey(Person)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return _("%s: %s %s") % (self.ticket.name, self.creator, self.created)

class TicketText(models.Model):
    item = models.ForeignKey(TicketItem)
    text = models.TextField()

class TicketStatusChange(models.Model):
    item = models.ForeignKey(TicketItem)
    pre_status = models.IntegerField(choices=JOB_STATUS_CHOICES)
    post_status = models.IntegerField(choices=JOB_STATUS_CHOICES)

    def save(self, *args, **kwargs):
        super(TicketStatusChange, self).save(*args, **kwargs)
        self.item.ticket.update_status()
        self.item.ticket.save()

    def __unicode__(self):
        return _("%s: %s > %s") % (self.item.ticket.name, self.pre_status, self.post_status)

class TicketAccountEntry(models.Model):
    item = models.ForeignKey(TicketItem)
    accountentry = models.ForeignKey(AccountEntry)
