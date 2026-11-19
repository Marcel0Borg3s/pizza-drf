from django.contrib import admin
from reviews.models import Review


@admin.register(Review)
class ReviewAppAdmin(admin.ModelAdmin):
    list_display = tuple(field.name for field in Review._meta.fields)
