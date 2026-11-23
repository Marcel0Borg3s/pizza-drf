from django.urls import path
from . import views


urlpatterns = [
    path('reviews/', views.ReviewListCreateView.as_view(), name='review-list-view'),
    path('reviews/<uuid:pk>/', views.ReviewRetrieveUpdateDestroyView.as_view(), name='review-detail-view'),    
]