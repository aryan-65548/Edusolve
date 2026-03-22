from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PracticeQuestionViewSet, StudentAnswerViewSet

router = DefaultRouter()
router.register(r'questions', PracticeQuestionViewSet, basename='practice-question')
router.register(r'answers', StudentAnswerViewSet, basename='student-answer')

urlpatterns = [
    path('', include(router.urls)),
]