from django.shortcuts import render, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from leads.models import Agent
from .forms import AgentModelForm
from leads.functions import get_session

# Create your views here.


class AgentListView(LoginRequiredMixin, generic.ListView):
    template_name = 'agents/agent-list.html'
    context_object_name = 'agents'

    def get_queryset(self):
        return Agent.objects.all()


class AgentCreateView(generic.CreateView):
    template_name = 'agents/agent-create.html'
    form_class = AgentModelForm

    def form_valid(self, form):
        user = form.save()
        user.set_password(user.password)
        user.save()

        # user.save()
        Agent.objects.create(
            user=user,
            session=get_session()
        )
        # user = authenticate(username=user.username, password=user.password)
        login(self.request, user)
        return super(AgentCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('lead-list')
