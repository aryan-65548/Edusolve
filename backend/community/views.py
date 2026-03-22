from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import DiscussionThread, ThreadReply
from .serializers import (
    DiscussionThreadSerializer,
    DiscussionThreadDetailSerializer,
    CreateThreadSerializer,
    ThreadReplySerializer,
    CreateReplySerializer,
)


class DiscussionThreadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DiscussionThread
    
    Community forum where students discuss topics
    Just like Hitesh teaches - full CRUD with ViewSet!
    
    Endpoints:
    - GET    /api/community/threads/              - List all threads
    - POST   /api/community/threads/              - Create new thread
    - GET    /api/community/threads/{id}/         - Get thread with replies
    - PUT    /api/community/threads/{id}/         - Update thread
    - DELETE /api/community/threads/{id}/         - Delete thread
    - POST   /api/community/threads/{id}/increment-views/ - Track views
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'views_count', 'updated_at']
    ordering = ['-is_pinned', '-updated_at']  # Pinned first, then newest
    
    def get_queryset(self):
        """
        Return all threads with filtering options
        """
        queryset = DiscussionThread.objects.all()
        
        # Filter by subject
        subject = self.request.query_params.get('subject', None)
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # Filter by pinned status
        pinned = self.request.query_params.get('pinned', None)
        if pinned is not None:
            is_pinned = pinned.lower() == 'true'
            queryset = queryset.filter(is_pinned=is_pinned)
        
        # Filter by locked status
        locked = self.request.query_params.get('locked', None)
        if locked is not None:
            is_locked = locked.lower() == 'true'
            queryset = queryset.filter(is_locked=is_locked)
        
        # Filter by author (my threads)
        my_threads = self.request.query_params.get('my_threads', None)
        if my_threads == 'true':
            queryset = queryset.filter(author=self.request.user)
        
        return queryset
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == 'retrieve':
            return DiscussionThreadDetailSerializer
        elif self.action == 'create':
            return CreateThreadSerializer
        return DiscussionThreadSerializer
    
    def perform_create(self, serializer):
        """
        Automatically set the author to current user
        Award points for creating thread
        """
        thread = serializer.save(author=self.request.user)
        
        # Award points for creating a thread
        self.request.user.add_points(5)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get thread details and increment view count
        """
        instance = self.get_object()
        
        # Increment view count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Only author can update their own threads
        """
        thread = self.get_object()
        
        if thread.author != request.user:
            return Response({
                'error': 'You can only edit your own threads'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Only author can delete their own threads
        """
        thread = self.get_object()
        
        if thread.author != request.user:
            return Response({
                'error': 'You can only delete your own threads'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)


class ThreadReplyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ThreadReply
    
    Students can reply to discussion threads
    
    Endpoints:
    - GET    /api/community/replies/               - List replies
    - POST   /api/community/replies/               - Create reply
    - GET    /api/community/replies/{id}/          - Get specific reply
    - PUT    /api/community/replies/{id}/          - Update reply
    - DELETE /api/community/replies/{id}/          - Delete reply
    - POST   /api/community/replies/{id}/upvote/   - Upvote reply
    - POST   /api/community/replies/{id}/downvote/ - Remove upvote
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return all replies, optionally filtered by thread
        """
        queryset = ThreadReply.objects.filter(is_hidden=False)
        
        # Filter by thread
        thread_id = self.request.query_params.get('thread', None)
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        
        # Filter by author (my replies)
        my_replies = self.request.query_params.get('my_replies', None)
        if my_replies == 'true':
            queryset = queryset.filter(author=self.request.user)
        
        # Filter solutions only
        solutions_only = self.request.query_params.get('solutions', None)
        if solutions_only == 'true':
            queryset = queryset.filter(is_solution=True)
        
        return queryset.order_by('created_at')
    
    def get_serializer_class(self):
        """
        Use different serializers
        """
        if self.action == 'create':
            return CreateReplySerializer
        return ThreadReplySerializer
    
    def perform_create(self, serializer):
        """
        Set author and award points
        """
        reply = serializer.save(author=self.request.user)
        
        # Award points for replying
        self.request.user.add_points(3)
    
    def update(self, request, *args, **kwargs):
        """
        Only author can update their own replies
        """
        reply = self.get_object()
        
        if reply.author != request.user:
            return Response({
                'error': 'You can only edit your own replies'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Only author can delete their own replies
        """
        reply = self.get_object()
        
        if reply.author != request.user:
            return Response({
                'error': 'You can only delete your own replies'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        Create a reply
        Check if thread is locked
        """
        thread_id = request.data.get('thread')
        thread = get_object_or_404(DiscussionThread, id=thread_id)
        
        # Check if thread is locked
        if thread.is_locked:
            return Response({
                'error': 'This thread is locked. No new replies allowed.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)


class ReplyUpvoteViewSet(viewsets.ViewSet):
    """
    ViewSet for upvoting replies
    
    Separate from ThreadReplyViewSet for clarity
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        """
        Upvote a reply
        
        POST /api/community/upvote/{reply_id}/upvote/
        """
        reply = get_object_or_404(ThreadReply, pk=pk)
        
        # Check if already upvoted
        if request.user in reply.upvotes.all():
            return Response({
                'message': 'You have already upvoted this reply',
                'upvote_count': reply.upvote_count
            }, status=status.HTTP_200_OK)
        
        # Add upvote
        reply.upvotes.add(request.user)
        
        # Award points to reply author
        reply.author.add_points(2)
        
        return Response({
            'message': 'Reply upvoted successfully',
            'upvote_count': reply.upvote_count
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def remove_upvote(self, request, pk=None):
        """
        Remove upvote from a reply
        
        POST /api/community/upvote/{reply_id}/remove_upvote/
        """
        reply = get_object_or_404(ThreadReply, pk=pk)
        
        # Check if upvoted
        if request.user not in reply.upvotes.all():
            return Response({
                'message': 'You have not upvoted this reply',
                'upvote_count': reply.upvote_count
            }, status=status.HTTP_200_OK)
        
        # Remove upvote
        reply.upvotes.remove(request.user)
        
        return Response({
            'message': 'Upvote removed successfully',
            'upvote_count': reply.upvote_count
        }, status=status.HTTP_200_OK)


class CommunityStatsViewSet(viewsets.ViewSet):
    """
    ViewSet for community statistics
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """
        Get overall community statistics
        
        GET /api/community/stats/
        """
        total_threads = DiscussionThread.objects.count()
        total_replies = ThreadReply.objects.filter(is_hidden=False).count()
        
        # Student's stats
        user_threads = DiscussionThread.objects.filter(author=request.user).count()
        user_replies = ThreadReply.objects.filter(author=request.user).count()
        user_solutions = ThreadReply.objects.filter(
            author=request.user,
            is_solution=True
        ).count()
        
        # Subject breakdown
        subject_stats = {}
        for subject, label in DiscussionThread.SUBJECT_CHOICES:
            subject_stats[subject] = DiscussionThread.objects.filter(
                subject=subject
            ).count()
        
        stats = {
            'community': {
                'total_threads': total_threads,
                'total_replies': total_replies,
            },
            'my_activity': {
                'threads_created': user_threads,
                'replies_posted': user_replies,
                'solutions_provided': user_solutions,
            },
            'by_subject': subject_stats,
        }
        
        return Response(stats)