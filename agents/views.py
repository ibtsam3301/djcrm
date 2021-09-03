from django.db import models
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import OrganizerandLoginRequiredMixin
from leads.models import Agent
from django.shortcuts import reverse
from .forms import AgentModelForm, User
from django.core.mail import send_mail
import random


class AgentListView(OrganizerandLoginRequiredMixin, generic.ListView):
    template_name = 'agents/agent-list.html'

    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)


class AgentCreateView(OrganizerandLoginRequiredMixin, generic.CreateView):
    template_name = 'agents/agent-create.html'
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse('agents:agent-list')

    def form_valid(self, form):
        user = form.save()
        user.is_agent = True
        user.is_organizer = False
        user.set_password(f"{random.randint(0, 100000)}")
        user.save()
        Agent.objects.create(
            user=user,
            organization=self.request.user.userprofile
        )
        send_mail(
            subject="You have been added as an agent",
            message="Login to your account and start working as an agent on DJCRM",
            from_email='admin@djcrm.com',
            recipient_list=[user.email]

        )

        # agent.organization = self.request.user.userprofile
        # agent.save()
        return super(AgentCreateView, self).form_valid(form)


class AgentDetailView(OrganizerandLoginRequiredMixin, generic.DetailView):
    template_name = 'agents/agent-detail.html'
    context_object_name = 'agent'

    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)


class AgentUpdateView(OrganizerandLoginRequiredMixin, generic.UpdateView):
    template_name = 'agents/agent-update.html'
    form_class = AgentModelForm

    def get_queryset(self):
        user = self.request.user
        return Agent.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        return reverse('agents:agent-list')


class AgentDeleteView(OrganizerandLoginRequiredMixin, generic.DeleteView):
    template_name = 'agents/agent-delete.html'
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse('agents:agent-list')

    def get_queryset(self):
        organization = self.request.user.userprofile
        return Agent.objects.filter(organization=organization)
