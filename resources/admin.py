from django.contrib import admin
from resources.models import UserProfile, Blog, Comment

admin.site.register(UserProfile)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'user__username', 'tags')
    prepopulated_fields = {'slug': ('title',)}  

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'comment', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'blog__title', 'comment')
