from django.urls import path
from . import views


urlpatterns = [
    path('pizzas/', views.PizzaCreateListView.as_view(), name='pizza-list-view'),
    path('pizzas/<uuid:pk>/', views.PizzaRetrieveUpdateDestroyView.as_view(), name='pizza-detail-view'),    
]