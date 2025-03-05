from django.contrib import admin
from .models import Discussion, Review




@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'created_on', 'is_active']
    list_filter = ['is_active', 'created_on', 'updated_on']
    search_fields = ['user', 'review', 'body']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'created_on', 'status']
    list_filter = ['status', 'created_on', 'updated_on', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_on'
    ordering = ['status', 'created_on']
    show_facets = admin.ShowFacets.ALWAYS