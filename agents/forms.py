from django import forms
from leads.models import Agent
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


User = get_user_model()

class AgentModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class AddLeadForm(forms.Form):
    target_group = forms.CharField(max_length=255, required=True)
    source_group = forms.CharField(max_length=255, required=True)
  