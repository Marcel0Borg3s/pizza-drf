from django.contrib import admin
from clients.models import Client

@admin.register(Client)
class ClientAppAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in Client._meta.fields)
