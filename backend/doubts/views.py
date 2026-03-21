from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import DoubtSession, ChatMessage
from .serializers import (
    DoubtSessionSerializer,
    DoubtSessionDetailSerializer,
    CreateDoubtSessionSerializer,
    ChatMessageSerializer,
    ChatMessageDetailSerializer,
)


class DoubtSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DoubtSession
    
    Provides CRUD operations for doubt sessions
    Just like Hitesh teaches - ViewSet gives us everything automatically!
    
    Endpoints:
    - GET    /api/doubts/              - List all sessions
    - POST   /api/doubts/              - Create new session
    - GET    /api/doubts/{id}/         - Get specific session
    - PUT    /api/doubts/{id}/         - Update session
    - PATCH  /api/doubts/{id}/         - Partial update
    - DELETE /api/doubts/{id}/         - Delete session
    - POST   /api/doubts/{id}/resolve/ - Mark as resolved
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return sessions for current user only
        Students can only see their own doubt sessions
        """
        return DoubtSession.objects.filter(student=self.request.user)
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        - Detail view: Include all messages
        - List view: Just basic info
        - Create: Minimal fields
        """
        if self.action == 'retrieve':
            return DoubtSessionDetailSerializer
        elif self.action == 'create':
            return CreateDoubtSessionSerializer
        return DoubtSessionSerializer
    
    def perform_create(self, serializer):
        """
        Automatically set the student to current user when creating
        """
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Custom action to mark session as resolved
        
        POST /api/doubts/{id}/resolve/
        
        Hitesh teaches custom actions with @action decorator!
        """
        session = self.get_object()
        session.mark_resolved()
        
        serializer = self.get_serializer(session)
        return Response({
            'message': 'Session marked as resolved!',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Get all messages for a specific doubt session
        
        GET /api/doubts/{id}/messages/
        """
        session = self.get_object()
        messages = session.messages.all()
        serializer = ChatMessageDetailSerializer(messages, many=True)
        
        return Response({
            'count': messages.count(),
            'messages': serializer.data
        })


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ChatMessage
    
    Handles sending and receiving messages in doubt sessions
    
    Endpoints:
    - GET  /api/messages/           - List messages (filtered by session)
    - POST /api/messages/           - Send a message
    - GET  /api/messages/{id}/      - Get specific message
    """
    
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter messages by session if provided
        Only show messages from user's own sessions
        """
        queryset = ChatMessage.objects.filter(
            session__student=self.request.user
        )
        
        # Filter by session if provided in query params
        session_id = self.request.query_params.get('session', None)
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        return queryset.order_by('timestamp')
    
    def create(self, request, *args, **kwargs):
        """
        Send a new message
        
        POST /api/messages/
        {
            "session": 1,
            "content": "I don't understand quadratic equations",
            "sender_type": "student",
            "image": (optional file)
        }
        
        For now, this just saves the student's message.
        YOUR TEAMMATE will add AI logic here to generate a response.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate that session belongs to current user
        session_id = request.data.get('session')
        session = get_object_or_404(
            DoubtSession,
            id=session_id,
            student=request.user
        )
        
        # Save student's message
        student_message = serializer.save()
        
        # ============================================
        # TODO: AI INTEGRATION POINT
        # ============================================
        # Your teammate will add AI logic here:
        # 
        # ai_response_content = generate_ai_response(
        #     session=session,
        #     student_message=student_message.content
        # )
        # 
        # ai_message = ChatMessage.objects.create(
        #     session=session,
        #     sender_type='ai',
        #     content=ai_response_content,
        #     ai_model='claude-3-sonnet'
        # )
        # ============================================
        
        # For now, just return the student's message
        return Response({
            'message': 'Message sent successfully!',
            'data': ChatMessageSerializer(student_message).data,
            'note': 'AI response will be added by your teammate'
        }, status=status.HTTP_201_CREATED)


class StudentDoubtStatsView(viewsets.ViewSet):
    """
    View for getting student's doubt statistics
    
    GET /api/doubts/stats/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """
        Get statistics for current student
        """
        student = request.user
        sessions = DoubtSession.objects.filter(student=student)
        
        stats = {
            'total_sessions': sessions.count(),
            'active_sessions': sessions.filter(status='active').count(),
            'resolved_sessions': sessions.filter(status='resolved').count(),
            'archived_sessions': sessions.filter(status='archived').count(),
            'total_messages': ChatMessage.objects.filter(
                session__student=student
            ).count(),
            'subjects': {
                'mathematics': sessions.filter(subject='mathematics').count(),
                'physics': sessions.filter(subject='physics').count(),
                'chemistry': sessions.filter(subject='chemistry').count(),
                'biology': sessions.filter(subject='biology').count(),
            }
        }
        
        return Response(stats)