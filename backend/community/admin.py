from django.contrib import admin
from .models import DiscussionThread, ThreadReply


@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    """Admin interface for DiscussionThread"""
    
    list_display = [
        'title', 
        'author', 
        'subject', 
        'views_count',
        'reply_count_display',
        'is_pinned',
        'is_locked',
        'created_at'
    ]
    
    list_filter = [
        'subject', 
        'is_pinned', 
        'is_locked',
        'created_at'
    ]
    
    search_fields = [
        'title', 
        'content', 
        'author__username'
    ]
    
    readonly_fields = [
        'views_count', 
        'created_at', 
        'updated_at'
    ]
    
    ordering = ['-is_pinned', '-created_at']
    
    # Enable/disable pinned and locked status easily
    list_editable = ['is_pinned', 'is_locked']
    
    date_hierarchy = 'created_at'
    
    def reply_count_display(self, obj):
        """Display number of replies"""
        return obj.reply_count
    
    reply_count_display.short_description = 'Replies'


@admin.register(ThreadReply)
class ThreadReplyAdmin(admin.ModelAdmin):
    """Admin interface for ThreadReply"""
    
    list_display = [
        'thread', 
        'author', 
        'content_preview',
        'is_solution',
        'upvote_count_display',
        'is_hidden',
        'created_at'
    ]
    
    list_filter = [
        'is_solution', 
        'is_hidden', 
        'created_at'
    ]
    
    search_fields = [
        'content', 
        'author__username', 
        'thread__title'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    ordering = ['-created_at']
    
    # Quick edit solution and hidden status
    list_editable = ['is_solution', 'is_hidden']
    
    def content_preview(self, obj):
        """Show first 50 characters"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = 'Content'
    
    def upvote_count_display(self, obj):
        """Display number of upvotes"""
        return obj.upvote_count
    
    upvote_count_display.short_description = 'Upvotes'