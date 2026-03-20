from django.db import models
from django.conf import settings


class DiscussionThread(models.Model):
    """
    Community discussion threads where students discuss topics
    
    Like a forum or Reddit post - students can discuss and help each other
    """
    
    SUBJECT_CHOICES = [
        ('mathematics', 'Mathematics'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('general', 'General Discussion'),
    ]
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='threads',
        help_text="Student who created this thread"
    )
    
    subject = models.CharField(
        max_length=20, 
        choices=SUBJECT_CHOICES
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Thread title/question"
    )
    
    content = models.TextField(
        help_text="Detailed description or question"
    )
    
    # Engagement metrics
    views_count = models.IntegerField(
        default=0,
        help_text="Number of times this thread was viewed"
    )
    
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pinned threads appear at top"
    )
    
    is_locked = models.BooleanField(
        default=False,
        help_text="Locked threads don't allow new replies"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        verbose_name = "Discussion Thread"
        verbose_name_plural = "Discussion Threads"
        indexes = [
            models.Index(fields=['subject', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def reply_count(self):
        """Get total number of replies"""
        return self.replies.count()


class ThreadReply(models.Model):
    """
    Replies to discussion threads
    
    Students can reply to threads and upvote helpful replies
    """
    
    thread = models.ForeignKey(
        DiscussionThread,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text="The thread this reply belongs to"
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='thread_replies'
    )
    
    content = models.TextField(
        help_text="Reply content"
    )
    
    # Optional image
    image = models.ImageField(
        upload_to='community_images/',
        null=True,
        blank=True
    )
    
    # Engagement - ManyToManyField (Hitesh covers this!)
    # Multiple students can upvote one reply
    # One student can upvote multiple replies
    upvotes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='upvoted_replies',
        blank=True,
        help_text="Students who upvoted this reply"
    )
    
    # Moderation
    is_solution = models.BooleanField(
        default=False,
        help_text="Mark if this reply solves the thread question"
    )
    
    is_hidden = models.BooleanField(
        default=False,
        help_text="Hidden replies (for moderation)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Thread Reply"
        verbose_name_plural = "Thread Replies"
    
    def __str__(self):
        return f"Reply by {self.author.username} on {self.thread.title}"
    
    @property
    def upvote_count(self):
        """Get total upvotes"""
        return self.upvotes.count()
    
    def save(self, *args, **kwargs):
        """Award points when reply is marked as solution"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Award points for helpful reply
        if not is_new and self.is_solution:
            self.author.add_points(20)