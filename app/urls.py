from django.contrib import admin
from django.urls import path
from clients.views import ClientListCreateView, ClientRetrieveUpdateDestroyView
from pizzas.views import PizzaCreateListView, PizzaRetrieveUpdateDestroyView
from reviews.views import ReviewCreatListView, ReviewRetrieveUpdateDestroyView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('clients/', ClientListCreateView.as_view(), name='client-list-view'),
    path('clients/<uuid:pk>/', ClientRetrieveUpdateDestroyView.as_view(), name='client-detail-view'),

    path('pizzas/', PizzaCreateListView.as_view(), name='pizza-list-view'),
    path('pizzas/<uuid:pk>/', PizzaRetrieveUpdateDestroyView.as_view(), name='pizza-detail-view'),

    path('reviews/', ReviewCreatListView.as_view(), name='review-list-view'),
    path('reviews/<int:pk>/', ReviewRetrieveUpdateDestroyView.as_view(), name='review-detail-view'),
]
