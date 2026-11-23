from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include('clients.urls')),
    path('api/v1/', include('pizzas.urls')),
    path('api/v1/', include('reviews.urls')),
]
