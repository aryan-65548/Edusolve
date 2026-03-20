from rest_framework import serializers
from .models import DiscussionThread, ThreadReply
from accounts.serializers import StudentSerializer


class ThreadReplySerializer(serializers.ModelSerializer):
    """
    Serializer for ThreadReply model
    """
    author_detail = StudentSerializer(source='author', read_only=True)
    upvote_count = serializers.ReadOnlyField()
    is_upvoted_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = ThreadReply
        fields = [
            'id',
            'thread',
            'author',
            'author_detail',
            'content',
            'image',
            'is_solution',
            'is_hidden',
            'upvote_count',
            'is_upvoted_by_user',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'author',
            'upvote_count',
            'created_at',
            'updated_at'
        ]
    
    def get_is_upvoted_by_user(self, obj):
        """
        Check if current user has upvoted this reply
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.upvotes.filter(id=request.user.id).exists()
        return False


class DiscussionThreadSerializer(serializers.ModelSerializer):
    """
    Serializer for DiscussionThread model
    """
    author_detail = StudentSerializer(source='author', read_only=True)
    reply_count = serializers.ReadOnlyField()
    
    class Meta:
        model = DiscussionThread
        fields = [
            'id',
            'author',
            'author_detail',
            'subject',
            'title',
            'content',
            'views_count',
            'reply_count',
            'is_pinned',
            'is_locked',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'author',
            'views_count',
            'reply_count',
            'created_at',
            'updated_at'
        ]


class DiscussionThreadDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer with all replies
    """
    author_detail = StudentSerializer(source='author', read_only=True)
    replies = ThreadReplySerializer(many=True, read_only=True)
    reply_count = serializers.ReadOnlyField()
    
    class Meta:
        model = DiscussionThread
        fields = [
            'id',
            'author',
            'author_detail',
            'subject',
            'title',
            'content',
            'views_count',
            'reply_count',
            'is_pinned',
            'is_locked',
            'created_at',
            'updated_at',
            'replies',
        ]
        read_only_fields = [
            'id',
            'author',
            'views_count',
            'created_at',
            'updated_at'
        ]


class CreateThreadSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new thread
    """
    
    class Meta:
        model = DiscussionThread
        fields = ['subject', 'title', 'content']


class CreateReplySerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new reply
    """
    
    class Meta:
        model = ThreadReply
        fields = ['thread', 'content', 'image']