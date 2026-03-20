from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Student
from .serializers import (
    StudentRegistrationSerializer,
    StudentProfileSerializer,
    StudentSerializer,
    ChangePasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration
    
    POST /api/auth/register/
    {
        "username": "student1",
        "email": "student@example.com",
        "password": "securepass123",
        "password2": "securepass123",
        "first_name": "John",
        "last_name": "Doe",
        "grade": 9
    }
    """
    queryset = Student.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = StudentRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': StudentSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful!'
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login
    
    POST /api/auth/login/
    {
        "username": "student1",
        "password": "securepass123"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': StudentSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Login successful!'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API endpoint for user logout
    
    POST /api/auth/logout/
    {
        "refresh": "refresh_token_here"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'message': 'Logout successful!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token or token already blacklisted'
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile
    
    GET /api/auth/profile/ - Get current user profile
    PUT/PATCH /api/auth/profile/ - Update current user profile
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    API endpoint for changing password
    
    POST /api/auth/change-password/
    {
        "old_password": "oldpass123",
        "new_password": "newpass456",
        "new_password2": "newpass456"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.data.get('old_password')):
                return Response({
                    'error': 'Old password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            return Response({
                'message': 'Password changed successfully!'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentListView(generics.ListAPIView):
    """
    API endpoint for listing all students (for leaderboard, etc.)
    
    GET /api/students/
    """
    queryset = Student.objects.all().order_by('-points')
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Enable filtering, searching, ordering
    filterset_fields = ['grade']
    search_fields = ['username', 'first_name', 'last_name']
    ordering_fields = ['points', 'created_at']