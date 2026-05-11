"""
DRF ViewSets for blog app REST API.
"""

import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from ..models import Post, Comment, Like, Category
from ..serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer, LikeSerializer, CategorySerializer
)
from ..permissions import IsAuthorOrReadOnly
from ..services import PostService, CommentService, LikeService

logger = logging.getLogger(__name__)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog posts.
    
    Endpoints:
    - GET    /api/posts/          - List all published posts
    - POST   /api/posts/          - Create a new post (authenticated)
    - GET    /api/posts/<id>/     - Retrieve a single post
    - PUT    /api/posts/<id>/     - Update a post (author only)
    - DELETE /api/posts/<id>/     - Delete a post (author only)
    - POST   /api/posts/<id>/like/    - Toggle like on a post
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'author', 'status']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get posts with optimized queries."""
        if self.request.user.is_authenticated and self.request.user.is_staff:
            # Staff can see all posts including drafts
            return Post.objects.select_related('author', 'category').prefetch_related('comments', 'likes')
        else:
            # Regular users only see published posts
            return Post.objects.filter(
                status=Post.Status.PUBLISH
            ).select_related('author', 'category').prefetch_related('comments', 'likes')

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'retrieve':
            return PostDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        """Set author to current user when creating post."""
        serializer.save(author=self.request.user)
        logger.info(f"Post '{serializer.instance.title}' created via API by {self.request.user}")

    def perform_update(self, serializer):
        """Log post updates."""
        serializer.save()
        logger.info(f"Post '{serializer.instance.title}' updated via API by {self.request.user}")

    def perform_destroy(self, instance):
        """Log post deletion."""
        post_title = instance.title
        instance.delete()
        logger.info(f"Post '{post_title}' deleted via API by {self.request.user}")

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """
        Toggle like on a post.
        
        POST /api/posts/<id>/like/
        """
        post = self.get_object()
        
        try:
            liked, total_likes = LikeService.toggle_like(post, request.user)
            return Response({
                'liked': liked,
                'total_likes': total_likes,
                'message': 'Post liked' if liked else 'Post unliked'
            })
        except Exception as e:
            logger.error(f"Error toggling like: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Get comments for a post.
        
        GET /api/posts/<id>/comments/
        """
        post = self.get_object()
        comments = post.comments.filter(active=True)
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        """
        Get trending posts (most liked/commented).
        
        GET /api/posts/trending/
        """
        from django.db.models import Count
        
        posts = self.get_queryset().annotate(
            like_count=Count('likes'),
            comment_count=Count('comments', filter=Q(comments__active=True))
        ).order_by('-like_count', '-comment_count')[:10]
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """
        Get current user's posts.
        
        GET /api/posts/my_posts/
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    
    Endpoints:
    - GET    /api/comments/      - List all comments
    - POST   /api/comments/      - Create a new comment (authenticated)
    - GET    /api/comments/<id>/ - Retrieve a comment
    - PUT    /api/comments/<id>/ - Update a comment (author only)
    - DELETE /api/comments/<id>/ - Delete a comment (author only)
    """
    
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'author', 'active']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get active comments."""
        return Comment.objects.filter(active=True).select_related('author', 'post')

    def perform_create(self, serializer):
        """Set author to current user when creating comment."""
        comment = serializer.save(author=self.request.user)
        logger.info(f"Comment added to post '{comment.post.title}' via API by {self.request.user}")


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing categories (read-only).
    
    Endpoints:
    - GET /api/categories/      - List all categories
    - GET /api/categories/<id>/ - Retrieve a category
    """
    
    queryset = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status=Post.Status.PUBLISH))
    ).filter(post_count__gt=0)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def posts(self, request, slug=None):
        """
        Get posts in a category.
        
        GET /api/categories/<slug>/posts/
        """
        category = self.get_object()
        posts = Post.objects.filter(
            category=category,
            status=Post.Status.PUBLISH
        ).order_by('-created_at')
        
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing likes.
    
    Endpoints:
    - GET    /api/likes/      - List all likes
    - POST   /api/likes/      - Create a like (authenticated)
    - DELETE /api/likes/<id>/ - Delete a like (user only)
    """
    
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'user']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get all likes."""
        return Like.objects.select_related('user', 'post')

    def perform_create(self, serializer):
        """Set user to current user and ensure uniqueness."""
        try:
            serializer.save(user=self.request.user)
            logger.info(f"Like created via API by {self.request.user}")
        except Exception as e:
            logger.warning(f"Like already exists: {str(e)}")
            raise
