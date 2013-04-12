from news.models import Entry
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    list_filter = ['created_at']
    date_hierarchy = 'created_at'

admin.site.register(Entry, EntryAdmin)
