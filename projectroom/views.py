from django.core.urlresolvers import reverse
from django.views import generic
from django.db.models import Q

from braces.views import LoginRequiredMixin

import models, forms

class LoginRequiredView(LoginRequiredMixin):
    login_url = '/login'
    raise_exception = False

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
        qs = qs.filter(Q(project__read_acl__user=user) | Q(project__write_acl__user=user)).distinct()
        #project__slug = self.kwargs.get('project__slug'))

        return qs

class JobDetailView(LoginRequiredView, generic.DetailView):
    model = models.Job

class JobUpdateView(LoginRequiredView, generic.UpdateView):
    form_class = forms.JobForm
    model = models.Job


class TicketDetailView(LoginRequiredView, generic.DetailView):
    model = models.Ticket

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

