import re
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, request
from django.views import generic
from .models import Lead, MessageCampaign, Agent
from .functions import mark_contacted, get_leads_to_msg, get_otp, assign_new_session


def leads_list(request):
    leads = MessageCampaign.objects.filter(agent__user_id=request.user.id)
    context = {
        'leads': leads,
        'campaign_contacted': MessageCampaign.objects.filter(
            agent__user_id=request.user.id, contacted=True),
        'campaign_not_contacted': MessageCampaign.objects.filter(
            agent__user_id=request.user.id, contacted=False)
    }
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('otp') is not None:
            context['otp'] = get_otp(request.user)
        elif request.POST.get('swap') is not None:
            assign_new_session(request.user)
    
    context['agent'] = Agent.objects.get(user=request.user)
        # print(request.POST.get('otp-button'))
        # if request.POST.get('otp-button'):
            
    
    return render(request, 'leads/lead-list-fancy.html', context)


class LeadsListView(generic.View):
    template_name = 'leads/lead-list.html'
    context_object_name = 'campaigns'

    def get_queryset(self):
        request_user_id = self.request.user.id
        print("This is THe id", request_user_id)
        return MessageCampaign.objects.filter(agent__user_id=request_user_id)

    def get_context_data(self, **kwargs):
        request_user_id = self.request.user.id
        context = super(LeadsListView, self).get_context_data(**kwargs)
        
        # status_form = context['status_form']
        # print(status_form)
        
        context['agent'] = Agent.objects.get(user=self.request.user)
        context['campaign_contacted'] = MessageCampaign.objects.filter(
            agent__user_id=request_user_id, contacted=True)
        context['campaign_not_contacted'] = MessageCampaign.objects.filter(
            agent__user_id=request_user_id, contacted=False)
        # if self.request.method == 'POST':
            # print('Y')
            
        # else:
        context['otp'] = ''
        #     print('N')
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['otp'] = 'OTP: ' + get_otp(request.user.id)
        return super(LeadsListView, self).post(request, *args, **kwargs)


def update_db(request, msg_id):
    mark_contacted(msg_id)
    return redirect(reverse('lead-list'))


def repopulate(request):
    get_leads_to_msg(request.user.id)
    return redirect(reverse('lead-list'))



