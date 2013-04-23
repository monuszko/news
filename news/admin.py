from news.models import Entry, Comment
from django.contrib import admin

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1

class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    inlines = [CommentInline]

admin.site.register(Entry, EntryAdmin)
