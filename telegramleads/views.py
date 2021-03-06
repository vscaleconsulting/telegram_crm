from django.shortcuts import render, reverse, redirect
from django.views.generic import TemplateView
from agents.forms import AddLeadForm
from leads.functions import add_all_users, generate_message_campaign


class LandingPageView(TemplateView):
    template_name = 'home_page.html'


def add_leads(request):
    if request.user.is_staff:
        form = AddLeadForm()
        if request.method == 'POST':
            form = AddLeadForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                target_grp = data['target_group']
                source_grp = data['source_group']
                add_all_users(source_grp)
                generate_message_campaign(target_grp, source_grp)
            return redirect('/')
        return render(request, 'add-leads.html', {'form': form})
    return redirect('/login')
    
