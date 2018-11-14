# django imports
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _

# django-apps

from mptt.models import TreeForeignKey, MPTTModel, TreeManager

# python imports
import os

JOB_STATUS_CHOICES = (
    (1, _('Requested by Customer')),
    (2, _('Seen by Worker')),
    (3, _('Started by Worker')),
    (4, _('Cancelled by Worker')),
    (5, _('Cancelled by Customer')),
    (6, _('Waiting for Approval by Customer')),
    (7, _('Approved by Customer')),
    (8, _('Worker waiting to get Payed')),
    (9, _('Closed and finished by Worker'))
)

JOB_STATUS_LEN = len(JOB_STATUS_CHOICES)

CURRENCY_CHOICES = (
    ('EUR', _('Euro')),
    ('CHF', _('Swiss Francs')),
)


class JobType(models.Model):
    """
    i.e.: programming
    """
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Person(models.Model):
    user = models.OneToOneField(User)
    company = models.ForeignKey(Company)

    def __unicode__(self):
        return self.user.get_full_name() or self.user.get_username()


class Project(models.Model):
    client_company = models.ForeignKey(Company)
    read_acl = models.ManyToManyField(Person, blank=True, related_name='project_readacl')
    write_acl = models.ManyToManyField(Person, blank=True, related_name='project_writeacl')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    active = models.BooleanField(default=True)

    def get_read_users(self):
        return User.objects.filter(person__project_readacl=self)

    def get_write_users(self):
        return User.objects.filter(person__project_writeacl=self)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('client_company__name',)


class Account(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    balance = models.DecimalField("Kontostand", decimal_places=2, max_digits=8, blank=True, null=True)
    currency = models.CharField(_('Currency'), max_length=3, choices=CURRENCY_CHOICES)

    def __unicode__(self):
        return self.name

    def calculate_balance(self):
        ai = self.accountentry_set.all().aggregate(values_sum=models.Sum('value'))
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
    job_type = models.ForeignKey(JobType, verbose_name=_('Job type'))
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_('Parent Job'))
    name = models.CharField(max_length=255, verbose_name=_('Job name'))
    description = models.TextField(verbose_name=_('Description'))
    deadline = models.DateTimeField(verbose_name=_('Deadline'))
    rate = models.ForeignKey(Rate, verbose_name=_('Rate'))
    request_by = models.ForeignKey(Person, verbose_name=_('Requested by'))
    request_at = models.DateTimeField(verbose_name=_('Requested at'), auto_now_add=True)
    account = models.ForeignKey(Account, verbose_name=_('Account'))

    objects = JobManager()

    def get_path(self):
        return self.get_ancestors(include_self=True)

    def get_all_tickets(self):
        ticket_ids = []
        subjobs = self.get_descendants(include_self=True)
        for job in subjobs:
            ticket_ids.extend(job.ticket_set.all().values_list('pk', flat=True))
        return Ticket.objects.filter(pk__in=ticket_ids)

    def get_all_active_tickets(self):
        ticket_ids = []
        subjobs = self.get_descendants(include_self=True)
        for job in subjobs:
            ticket_ids.extend(job.ticket_set.active().values_list('pk', flat=True))
        return Ticket.objects.filter(pk__in=ticket_ids)

    def is_old_deadline(self):
        return self.deadline < timezone.now()

    def get_aggregated_duration_pre(self):
        return self.get_all_tickets().aggregate(sum_duration_pre=models.Sum('duration_pre')).get('sum_duration_pre') or 0

    @models.permalink
    def get_absolute_url(self):
        return ('job', [], {'pk': self.pk, 'project__slug': self.project.slug})

    @models.permalink
    def get_edit_url(self):
        return ('job_edit', [], {'pk': self.pk, 'project__slug': self.project.slug})

    def __unicode__(self):
        return self.name


class JobFile(models.Model):
    job = models.ForeignKey(Job)
    filefield = models.FileField(upload_to='jobfile', verbose_name=_('File'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))

    def is_image(self):
        if self.filefield:
            fn, ext = os.path.splitext(self.filefield.path)
            ext = ext.lower()
            if ext in ['.jpg', '.png']:
                return True
        return False

    def get_basename(self):
        if self.filefield:
            return os.path.basename(self.filefield.path)


class TicketManager(models.Manager):
    def active(self):
        return self.filter(status__lt=JOB_STATUS_LEN, hidden=False)


class Ticket(models.Model):
    job = models.ForeignKey(Job)
    name = models.CharField(max_length=255, verbose_name=_('Ticket name'))
    request_by = models.ForeignKey(Person, related_name='requested_tickets', verbose_name=_('Requested by'))
    status = models.IntegerField(choices=JOB_STATUS_CHOICES, verbose_name=_('Ticket status'))
    assigned_to = models.ForeignKey(Person, related_name='assigned_tickets', null=True, blank=True, verbose_name=_('Assigned to'))
    duration_pre = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True, verbose_name=_('valued effort'))
    duration_post = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True, verbose_name=_('actual effort'))

    hidden = models.BooleanField(default=False)

    objects = TicketManager()

    def update_status(self):
        tsc = TicketStatusChange.objects.filter(item__ticket=self).latest('item__created')
        self.status = tsc.post_status

    def progress(self):
        return float(self.status) / float(JOB_STATUS_LEN) * 100.0

    def progress_int(self):
        return int(self.progress())

    def get_costs(self):
        return self.job.rate.hourly_rate * self.duration_pre

    def get_read_users(self):
        if self.hidden:
            return [self.assigned_to.user]
        else:
            return self.job.project.get_read_users()

    def is_closed(self):
        return self.status == 9

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
        return _("%(ticket_name)s: %(creator)s %(created)s") % {'ticket_name': self.ticket.name, 'creator': self.creator, 'created': self.created}


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
        return _("%(ticket_name)s: %(pre)s > %(post)s") % {'ticket_name': self.item.ticket.name, 'pre': self.pre_status, 'post': self.post_status}


class TicketAccountEntry(models.Model):
    item = models.ForeignKey(TicketItem)
    accountentry = models.ForeignKey(AccountEntry)
