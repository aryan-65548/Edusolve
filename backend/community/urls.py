from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DiscussionThreadViewSet,
    ThreadReplyViewSet,
    ReplyUpvoteViewSet,
    CommunityStatsViewSet,
)

# Create router
router = DefaultRouter()
router.register(r'threads', DiscussionThreadViewSet, basename='discussion-thread')
router.register(r'replies', ThreadReplyViewSet, basename='thread-reply')
router.register(r'upvote', ReplyUpvoteViewSet, basename='reply-upvote')
router.register(r'stats', CommunityStatsViewSet, basename='community-stats')

app_name = 'community'

urlpatterns = [
    path('', include(router.urls)),
]