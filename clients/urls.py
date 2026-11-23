from django.urls import path
from . import views


urlpatterns = [
    path('clients/', views.ClientListCreateView.as_view(), name='client-list-view'),
    path('clients/<uuid:pk>/', views.ClientRetrieveUpdateDestroyView.as_view(), name='client-detail-view'),    
]