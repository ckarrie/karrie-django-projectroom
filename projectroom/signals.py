from django.apps import apps
from django.core.mail import send_mail
from django.db.models import signals
from django.utils.translation import ugettext as _


def job_create_notify_admin(sender, *args, **kwargs):
    created = kwargs.pop('created', False)
    instance = kwargs.pop('instance', None)

    if created and instance:
        url = 'https://tickets.xn--karri-fsa.de' + instance.get_absolute_url()
        msg_data = {
            'url': url,
            'description': instance.description,
            'name': instance.name,
            'type': unicode(instance.job_type),
            'project': unicode(instance.project),
        }
        subject = _('New Job created: %(project)s / %(name)s / %(type)s') % msg_data
        message = _('Hello,\n\n'
                    'a new job has been created,\n\n'
                    'Link: %(url)s\n'
                    'Project: %(project)s\n'
                    'Type: %(type)s\n\n'
                    + '-' * 50 + '\n'
                    '== %(name)s ==\n\n'
                    '%(description)s'
                    + '-' * 50 + '\n'
                    '\n\n\n\nSend via https://tickets.xn--karri-fsa.de') % msg_data

        recipient_list = []
        for user in apps.get_model('auth.User').objects.filter(is_superuser=True, email__isnull=False):
            recipient_list.append(user.email)

        if recipient_list:
            print "Sending job_create_notify_admin to", recipient_list
            send_mail(subject=subject, message=message, from_email='noreply@tickets.xn--karri-fsa.de', recipient_list=recipient_list)


def ticketitem_notify_requester(sender, *args, **kwargs):
    print "Calling ticketitem_notify_requester"
    created = kwargs.pop('created', False)
    instance = kwargs.pop('instance', None)

    ticket_text = None

    if instance:
        if sender == apps.get_model('projectroom.TicketText'):
            ticket_text = instance.text
        elif sender == apps.get_model('projectroom.TicketStatusChange'):
            ticket_text = unicode(instance)

    if ticket_text:
        ticket = instance.item.ticket
        url = 'https://tickets.xn--karri-fsa.de' + ticket.get_absolute_url()
        msg_data = {
            'project': unicode(ticket.job.project),
            'job': unicode(ticket.job),
            'ticket': _('#%(id)s %(name)s') % {'id': ticket.pk, 'name': ticket.name},
            'text': ticket_text,
            'url': url
        }
        subject = _('Ticket changed: %(project)s / %(job)s / %(ticket)s') % msg_data
        message = _('Hello,\n\n'
                    'a ticket has been changed.\n\n'
                    'Link: %(url)s\n'
                    'Project: %(project)s\n'
                    'Job: %(job)s\n\n'
                    + '-' * 50 + '\n'
                    '== %(ticket)s ==\n\n'
                    '%(text)s\n'
                    + '-' * 50 +
                    '\n\n\n\nSend via https://tickets.xn--karri-fsa.de') % msg_data

        recipient_list = []

        # me
        for person in apps.get_model('projectroom.Person').objects.filter(user__email__isnull=False, id__in=[1, ]):
            recipient_list.append(person.user.email)

        # job requester
        for person in apps.get_model('projectroom.Person').objects.filter(user__email__isnull=False, id__in=[ticket.job.request_by.pk]):
            recipient_list.append(person.user.email)

        recipient_list = list(set(recipient_list))

        if recipient_list:
            print "Sending ticketitem_notify_requester to", recipient_list
            send_mail(subject=subject, message=message, from_email='noreply@tickets.xn--karri-fsa.de', recipient_list=recipient_list)


def register_signals(config):
    signals.post_save.connect(receiver=job_create_notify_admin, sender=apps.get_model('projectroom.Job'))
    signals.post_save.connect(receiver=ticketitem_notify_requester)
    print "Finsished register_signals for ", config.name
