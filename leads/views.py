from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, request
from django.views import generic
from .models import Lead, MessageCampaign
from .functions import mark_contacted, get_leads_to_msg


def leads_list(request):
    leads = MessageCampaign.objects.filter(agent__user_id=request.user.id)
    return render(request, 'leads/lead-list.html', {'leads': leads})


class LeadsListView(generic.ListView):
    template_name = 'leads/lead-list.html'
    context_object_name = 'campaigns'
    
    def get_queryset(self):
        request_user_id = self.request.user.id
        print("This is THe id", request_user_id)
        return MessageCampaign.objects.filter(agent__user_id=request_user_id)
    
    def get_context_data(self, **kwargs):
        request_user_id = self.request.user.id
        context = super(LeadsListView, self).get_context_data(**kwargs)
        context['campaign_contacted'] = MessageCampaign.objects.filter(agent__user_id=request_user_id, contacted=True)
        context['campaign_not_contacted'] = MessageCampaign.objects.filter(agent__user_id=request_user_id, contacted=False)
        return context

        

def update_db(request, msg_id):
    mark_contacted(msg_id)
    return redirect(reverse('lead-list'))


def repopulate(request):
    get_leads_to_msg(request.user.id)
    return redirect(reverse('lead-list'))