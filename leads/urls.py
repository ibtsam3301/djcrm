from django.urls import path
from .views import *

app_name = 'leads'

urlpatterns = [
    path('', LeadListView.as_view(), name='lead-list'),
    path('create/', LeadCreateView.as_view(), name='lead-create'),
    path('<int:pk>/', LeadDetailView.as_view(), name='lead-details'),
    path('<int:pk>/update', LeadUpdateView.as_view(), name='lead-update'),
    path('<int:pk>/delete', LeadDeleteView.as_view(), name='lead-delete'),
    path('<int:pk>/assign-agent', AssignAgentView.as_view(), name='assign-agent'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(),
         name='category-detail'),
    path('<int:pk>/categories/', LeadCategoryUpdateView.as_view(),
         name='category-update'),
    path('categories', CategoryListView.as_view(), name='category-list')

]
