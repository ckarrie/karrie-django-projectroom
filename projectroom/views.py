from braces.views import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

import forms
import models


class LoginRequiredView(LoginRequiredMixin):
    login_url = '/login'
    raise_exception = False


class DashboardView(LoginRequiredView, generic.TemplateView):
    template_name = 'projectroom/dashboard.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        my_projects = models.Project.objects.filter(Q(read_acl__user=user) | Q(write_acl__user=user)).distinct()
        kwargs.update({
            'my_projects': my_projects,
            'latest_ticketitems': models.TicketItem.objects.filter(ticket__hidden=False, ticket__job__project__in=my_projects).order_by('-created')[:25]
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
        obj = form.save(commit=False)
        project = models.Project.objects.get(slug=self.kwargs.get('project__slug'))
        obj.request_by = models.Person.objects.get(company=project.client_company, user=self.request.user)
        obj.project = project
        obj.save()
        return HttpResponseRedirect(reverse('job', kwargs={'project__slug': project.slug, 'pk': obj.pk}))


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
