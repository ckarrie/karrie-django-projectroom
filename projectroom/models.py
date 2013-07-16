from django.db import models
from django.contrib.auth.models import User

JOB_STATUS_CHOICES = (
    (0, 'Requested by Customer'),
    (1, 'Seen by Worker'),
    (2, 'Started by Worker'),
    (3, 'Cancelled by Worker'),
    (4, 'Cancelled by Customer'),
    (5, 'Waiting for Approval by Customer'),
    (6, 'Approved by Customer'),
    (7, '')
)

class Project(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

class Module(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

class JobType(models.Model):
    """
    i.e.: programming
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField()

class Company(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

class Person(models.Model):
    user = models.ForeignKey(User)
    company = models.ForeignKey(Company)



class JobRequest(models.Model):
    project = models.ForeignKey(Project)
    module = models.ForeignKey(Module)
    job_type = models.ForeignKey(JobType)
    request_by = models.ForeignKey(Person)
    description = models.TextField()
    deadline = models.DateTimeField()

class Job(models.Model):
    request = models.ForeignKey(JobRequest)
    status = models.IntegerField(choices=JOB_STATUS_CHOICES)
    assigned_to = models.ForeignKey(Person)
    duration_pre = models.TimeField()
    duration_post = models.TimeField(null=True, blank=True)