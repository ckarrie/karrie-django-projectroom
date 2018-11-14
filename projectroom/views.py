from braces.views import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.forms import modelformset_factory, inlineformset_factory
from django.utils import timezone
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

import forms
import models


class LoginRequiredView(LoginRequiredMixin):
    login_url = '/login'
    raise_exception = False

    def get_context_data(self, **kwargs):
        ctx = super(LoginRequiredView, self).get_context_data(**kwargs)
        ctx.update({'is_secure': self.request.is_secure()})
        return ctx


class DashboardView(LoginRequiredView, generic.TemplateView):
    template_name = 'projectroom/dashboard.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        my_projects = models.Project.objects.filter(Q(read_acl__user=user) | Q(write_acl__user=user)).distinct()
        my_open_jobs = models.Job.objects.filter(
            project__in=my_projects,
            ticket__status__lt=models.JOB_STATUS_LEN,
            ticket__assigned_to__user=user
        ).distinct().order_by('deadline')

        kwargs.update({
            'my_projects': my_projects,
            'latest_ticketitems': models.TicketItem.objects.filter(ticket__hidden=False, ticket__job__project__in=my_projects).order_by('-created')[:5],
            'my_open_jobs': my_open_jobs
        })
        return super(DashboardView, self).get_context_data(**kwargs)


class ProjectListView(LoginRequiredView, generic.ListView):
    model = models.Project

    def get_queryset(self):
        user = self.request.user
        qs = super(ProjectListView, self).get_queryset()
        qs = qs.filter(Q(read_acl__user=user) | Q(write_acl__user=user)).distinct()

        return qs


class JobListView(LoginRequiredView, generic.ListView):
    model = models.Job

    def get_queryset(self):
        user = self.request.user
        qs = super(JobListView, self).get_queryset()
        qs = qs.filter(
            Q(project__read_acl__user=user) | Q(project__write_acl__user=user),
            project__slug=self.kwargs.get('project__slug')
        ).distinct()

        return qs

    def get_context_data(self, **kwargs):
        ctx = super(JobListView, self).get_context_data(**kwargs)
        ctx.update({
            'project': models.Project.objects.get(slug=self.kwargs.get('project__slug'))
        })
        return ctx


class JobCreateView(LoginRequiredView, generic.CreateView):
    model = models.Job
    form_class = forms.CreateJobForm

    def get_initial(self):
        init = super(JobCreateView, self).get_initial()
        init.update({
            'deadline': timezone.now(),
            'rate': models.Rate.objects.first(),
            'account': self.get_possible_accounts().first()
        })
        return init

    def get_context_data(self, **kwargs):
        ctx = super(JobCreateView, self).get_context_data(**kwargs)
        jobfile_fs = forms.JobFileFormSet(instance=self.object)

        if self.request.POST:
            jobfile_fs = forms.JobFileFormSet(self.request.POST, self.request.FILES, instance=self.object)

        ctx.update({
            'jobfile_fs': jobfile_fs
        })

        return ctx

    def get_possible_accounts(self):
        project = models.Project.objects.get(slug=self.kwargs.get('project__slug'))
        return models.Account.objects.filter(project=project)

    def get_form_kwargs(self):
        kwargs = super(JobCreateView, self).get_form_kwargs()
        project = models.Project.objects.get(slug=self.kwargs.get('project__slug'))
        kwargs.update({
            'possible_accounts': self.get_possible_accounts()
        })
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        project = models.Project.objects.get(slug=self.kwargs.get('project__slug'))
        self.object.request_by = models.Person.objects.get(user=self.request.user)
        self.object.project = project
        context = self.get_context_data()
        jobfile_fs = context['jobfile_fs']
        with transaction.atomic():
            self.object.save()

            if jobfile_fs.is_valid():
                jobfile_fs.instance = self.object
                jobfile_fs.save()

        return HttpResponseRedirect(reverse('job', kwargs={'project__slug': project.slug, 'pk': self.object.pk}))


class JobDetailView(LoginRequiredView, generic.DetailView):
    model = models.Job

    def get_context_data(self, **kwargs):
        ctx = super(JobDetailView, self).get_context_data(**kwargs)
        tickets = self.object.get_all_tickets().filter(
            Q(assigned_to__user=self.request.user, hidden=True)
            |
            Q(job__project__write_acl__user=self.request.user)
        )
        ctx.update({
            'tickets': tickets,

        })
        return ctx


class JobUpdateView(LoginRequiredView, generic.UpdateView):
    form_class = forms.JobForm
    model = models.Job

    def get_context_data(self, **kwargs):
        ctx = super(JobUpdateView, self).get_context_data(**kwargs)
        jobfile_fs = forms.JobFileFormSet(instance=self.object)

        if self.request.POST:
            jobfile_fs = forms.JobFileFormSet(self.request.POST, self.request.FILES, instance=self.object)

        ctx.update({
            'jobfile_fs': jobfile_fs
        })

        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        jobfile_fs = context['jobfile_fs']
        with transaction.atomic():
            self.object = form.save()

            if jobfile_fs.is_valid():
                jobfile_fs.instance = self.object
                jobfile_fs.save()
        return super(JobUpdateView, self).form_valid(form)


class TicketDetailView(LoginRequiredView, generic.DetailView):
    model = models.Ticket

    def get_object(self, queryset=None):
        obj = super(TicketDetailView, self).get_object(queryset)
        person = models.Person.objects.get(user=self.request.user),
        if obj.hidden and person != obj.assigned_to:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        kwargs.update({
            'ticket_form': forms.TicketItemForm(initial={
                'ticket': self.object,
                'creator': models.Person.objects.get(user=self.request.user),
                'status': self.object.status
            })
        })
        return super(TicketDetailView, self).get_context_data(**kwargs)


class TicketCreateView(LoginRequiredView, generic.CreateView):
    model = models.Ticket
    form_class = forms.TicketForm

    def get_initial(self):
        job = models.Job.objects.get(pk=self.kwargs.get('pk'), project__slug=self.kwargs.get('project__slug'))
        return {
            'job': job,
            'request_by': models.Person.objects.get(user=self.request.user),
            'status': 1
        }


class TicketItemCreateView(LoginRequiredView, generic.CreateView):
    form_class = forms.TicketItemForm
    model = models.TicketItem

    def get_success_url(self):
        ticket = models.Ticket.objects.get(pk=self.kwargs.get('pk'))
        return ticket.get_absolute_url()

    def get_initial(self):
        ticket = models.Ticket.objects.get(pk=self.kwargs.get('pk'))
        creator = models.Person.objects.get(user=self.request.user)
        status = ticket.status
        return {
            'ticket': ticket,
            'creator': creator,
            'status': status
        }

    def form_valid(self, form):
        return super(TicketItemCreateView, self).form_valid(form)
