from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
