from django.db.models.query import QuerySet
from django.http import request
from django.shortcuts import redirect, render, reverse
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic.edit import UpdateView
from .models import Lead, Category
from agents.mixins import OrganizerandLoginRequiredMixin
from .forms import LeadFormModel, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib import messages

# Create your views here.


class SignupView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


class LandingPageView(TemplateView):
    template_name = 'landing.html'


def landing(request):
    return render(request, 'landing.html')


class LeadListView(LoginRequiredMixin, ListView):
    template_name = 'leads/home_page.html'
    context_object_name = 'leads'

    def get_queryset(self):
        user = self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization, agent__isnull=False)
            queryset = queryset.filter(agent__user=user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile,
                                           agent__isnull=True)

            context.update({
                'unassigned_leads': queryset,
            })

        return context


def home(request):
    lead = Lead.objects.all()
    context = {'leads': lead}
    return render(request, 'leads/home_page.html', context=context)


class LeadDetailView(LoginRequiredMixin, DetailView):
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'

    def get_queryset(self):
        user = self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.userprofile)
            queryset = queryset.filter(agent__user=user)

        return queryset


def lead_details(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        'lead': lead
    }

    return render(request, 'leads/lead_detail.html', context=context)


class LeadCreateView(OrganizerandLoginRequiredMixin, CreateView):
    template_name = 'leads/create_lead.html'
    form_class = LeadFormModel

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile

        lead.save()
        send_mail(
            subject="Creted a new lead",
            message="new lead created",
            from_email='test@test.com',
            recipient_list=['test2@test.com']
        )
        messages.success(self.request, "You have successfully created a lead")
        return super(LeadCreateView, self).form_valid(form)


def create(request):
    form = LeadFormModel()

    if request.method == "POST":
        form = LeadFormModel(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/leads')

    context = {
        'form': form
    }

    return render(request, 'leads/create_lead.html', context=context)


class LeadUpdateView(OrganizerandLoginRequiredMixin, UpdateView):
    template_name = 'leads/lead_update.html'
    form_class = LeadFormModel

    def get_queryset(self):
        user = self.request.user

        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")


def update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadFormModel(instance=lead)

    if request.method == "POST":
        form = LeadFormModel(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect(f'/leads/{pk}')

    context = {
        'lead': lead,
        'form': form
    }

    return render(request, 'leads/lead_update.html', context=context)


class LeadDeleteView(OrganizerandLoginRequiredMixin, DeleteView):
    template_name = 'leads/lead_delete.html'

    def get_queryset(self):
        user = self.request.user

        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")


def delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect('/leads')


class AssignAgentView(OrganizerandLoginRequiredMixin, generic.FormView):
    template_name = 'leads/assign-agent.html'
    
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'request': self.request,
        })
        return kwargs

    def get_success_url(self):
        return reverse('leads:lead-list')

    def form_valid(self, form):
        agent = form.cleaned_data['agent']
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()

        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/category_list.html'
    context_object_name = 'category_list'

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile, )
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization)

        context.update({
            'unassigned_lead_count': queryset.filter(category__isnull=True).count()
        })

        return context

    def get_queryset(self):
        user = self.request.user

        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile)
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization)

        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'leads/category-detail.html'
    context_object_name = 'category'

    def get_queryset(self):
        user = self.request.user

        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile)
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization)

        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/lead-category-update.html'
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization)
            queryset = queryset.filter(agent__user=user)

        return queryset

    def get_success_url(self):
        return reverse('leads:lead-details', kwargs={"pk": self.get_object().id})

# def create(request):
#     form = LeadForm()

#     if request.method == "POST":
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             agent = Agent.objects.first()

#             Lead.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 age=age,
#                 agent=agent,
#             )
#             return redirect('/leads')

#     context = {
#         'form': form
#     }

#     return render(request, 'leads/create_lead.html', context=context)


# def create(request):
#     form = LeadForm()

#     if request.method == "POST":
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             agent = Agent.objects.first()

#             Lead.objects.create(
#                 first_name=first_name,
#                 last_name=last_name,
#                 age=age,
#                 agent=agent,
#             )
#             return redirect('/leads')

#     context = {
#         'form': form
#     }

#     return render(request, 'leads/create_lead.html', context=context)
