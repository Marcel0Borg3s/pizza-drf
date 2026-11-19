from django.contrib import admin
from pizzas.models import Pizza


@admin.register(Pizza)
class PizzaAppAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in Pizza._meta.fields)
