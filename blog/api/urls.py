"""
REST API URLs for blog app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import PostViewSet, CommentViewSet, CategoryViewSet, LikeViewSet

app_name = 'api'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'likes', LikeViewSet, basename='like')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),  # For browsable API login
]
