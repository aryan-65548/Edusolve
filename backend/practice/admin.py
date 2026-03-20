from django.contrib import admin
from .models import PracticeQuestion, StudentAnswer


@admin.register(PracticeQuestion)
class PracticeQuestionAdmin(admin.ModelAdmin):
    """Admin interface for PracticeQuestion"""
    
    list_display = [
        'question_preview', 
        'difficulty', 
        'related_session', 
        'times_attempted',
        'accuracy_display',
        'created_at'
    ]
    
    list_filter = [
        'difficulty', 
        'related_session__subject',  # Filter by subject
        'created_at'
    ]
    
    search_fields = [
        'question_text', 
        'topic',
        'related_session__title'
    ]
    
    readonly_fields = [
        'created_at',
        'times_attempted',
        'times_correct',
        'accuracy_rate'
    ]
    
    ordering = ['-created_at']
    
    # Custom display methods
    def question_preview(self, obj):
        """Show first 50 characters of question"""
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    
    question_preview.short_description = 'Question'
    
    def accuracy_display(self, obj):
        """Display accuracy as percentage"""
        return f"{obj.accuracy_rate}%"
    
    accuracy_display.short_description = 'Accuracy'
    accuracy_display.admin_order_field = 'times_correct'  # Allow sorting


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    """Admin interface for StudentAnswer"""
    
    list_display = [
        'student', 
        'question_preview', 
        'selected_answer',
        'is_correct', 
        'time_taken_seconds',
        'attempted_at'
    ]
    
    list_filter = [
        'is_correct', 
        'attempted_at',
        'question__difficulty'
    ]
    
    search_fields = [
        'student__username',
        'question__question_text'
    ]
    
    readonly_fields = ['attempted_at']
    
    ordering = ['-attempted_at']
    
    def question_preview(self, obj):
        """Show question preview"""
        return obj.question.question_text[:40] + '...'
    
    question_preview.short_description = 'Question'