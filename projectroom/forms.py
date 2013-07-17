__author__ = 'christian'

from django import forms
import models

class TicketItemForm(forms.ModelForm):
    status = forms.ChoiceField(choices=models.JOB_STATUS_CHOICES)
    text = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(TicketItemForm, self).__init__(*args, **kwargs)

        self.fields['ticket'].widget = forms.HiddenInput()
        self.fields['creator'].widget = forms.HiddenInput()

    def save(self, **kwargs):
        cd = self.cleaned_data
        ticket = cd.get('ticket')
        status = int(cd.get('status'))
        text = cd.get('text')
        ti_instance = super(TicketItemForm, self).save(**kwargs)

        if status != ticket.status:
            print "Changed ", status, ticket.status, type(status), type(ticket.status)
            tsc = models.TicketStatusChange(item=ti_instance, pre_status=ticket.status, post_status=status)
            tsc.save()

        if text:
            tt = models.TicketText(item=ti_instance, text=text)
            tt.save()

        return ti_instance



    class Meta:
        fields = ('ticket', 'creator',)
        model = models.TicketItem

class TicketForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')

        self.fields['job'].widget = forms.HiddenInput()
        self.fields['request_by'].widget = forms.HiddenInput()
        self.fields['status'].widget = forms.HiddenInput()


        if not instance:
            self.fields['assigned_to'].widget = forms.HiddenInput()
            self.fields['duration_post'].widget = forms.HiddenInput()

    def clean(self):
        cd = self.cleaned_data
        request_by = cd.get('request_by')
        cd.update({'assigned_to': request_by})
        return cd

    def save(self, **kwargs):
        cd = self.cleaned_data
        text = cd.pop('text')

        ticket_instance = super(TicketForm, self).save(**kwargs)

        if text:
            ti = models.TicketItem(ticket=ticket_instance, creator=ticket_instance.request_by)
            ti.save()
            tt = models.TicketText(item=ti, text=text)
            tt.save()

        return ticket_instance


    class Meta:
        model = models.Ticket

class JobForm(forms.ModelForm):
    class Meta:
        model = models.Job