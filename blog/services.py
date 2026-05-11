"""
Business logic and utility functions for blog app.
"""

import logging
from typing import Optional, List
from django.core.cache import cache
from django.db.models import Count, Q
from .models import Post, Comment, Like, Category

logger = logging.getLogger(__name__)


class PostService:
    """Service class for Post-related operations."""

    @staticmethod
    def get_published_posts(cached=True):
        """Get all published posts with optional caching."""
        cache_key = 'published_posts'
        
        if cached:
            posts = cache.get(cache_key)
            if posts is not None:
                return posts
        
        posts = Post.objects.filter(
            status=Post.Status.PUBLISH
        ).select_related('author', 'category').prefetch_related('comments', 'likes')
        
        if cached:
            cache.set(cache_key, posts, 3600)
        
        return posts

    @staticmethod
    def get_post_by_slug(slug: str):
        """Get a single published post by slug."""
        cache_key = f'post_{slug}'
        post = cache.get(cache_key)
        
        if post is None:
            post = Post.objects.filter(
                slug=slug,
                status=Post.Status.PUBLISH
            ).select_related('author', 'category').prefetch_related('comments', 'likes').first()
            
            if post:
                cache.set(cache_key, post, 3600)
        
        return post

    @staticmethod
    def search_posts(query: str):
        """Search posts by title, excerpt, or content."""
        logger.info(f"Searching posts for query: {query}")
        
        return Post.objects.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query),
            status=Post.Status.PUBLISH
        ).select_related('author', 'category')

    @staticmethod
    def get_posts_by_category(category_slug: str):
        """Get all published posts for a specific category."""
        cache_key = f'posts_category_{category_slug}'
        posts = cache.get(cache_key)
        
        if posts is None:
            posts = Post.objects.filter(
                category__slug=category_slug,
                status=Post.Status.PUBLISH
            ).select_related('author', 'category')
            
            cache.set(cache_key, posts, 3600)
        
        return posts

    @staticmethod
    def get_user_posts(user):
        """Get all posts by a specific user."""
        return Post.objects.filter(
            author=user,
            status=Post.Status.PUBLISH
        ).select_related('author', 'category')

    @staticmethod
    def create_post(title: str, content: str, author, excerpt: str = '', 
                   image=None, category: Optional[Category] = None) -> Post:
        """Create a new post."""
        try:
            post = Post.objects.create(
                title=title,
                content=content,
                author=author,
                excerpt=excerpt or content[:500],
                image=image,
                category=category,
                status=Post.Status.PUBLISH
            )
            logger.info(f"Post '{title}' created by {author}")
            
            # Clear cache
            cache.delete('published_posts')
            
            return post
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            raise

    @staticmethod
    def update_post(post: Post, **kwargs) -> Post:
        """Update an existing post."""
        allowed_fields = ['title', 'content', 'excerpt', 'image', 'category', 'status']
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(post, field, value)
        
        post.save()
        logger.info(f"Post '{post.title}' updated")
        
        # Clear caches
        cache.delete('published_posts')
        cache.delete(f'post_{post.slug}')
        
        return post

    @staticmethod
    def delete_post(post: Post) -> bool:
        """Delete a post."""
        try:
            post_title = post.title
            post.delete()
            logger.info(f"Post '{post_title}' deleted")
            
            # Clear caches
            cache.delete('published_posts')
            cache.delete(f'post_{post.slug}')
            
            return True
        except Exception as e:
            logger.error(f"Error deleting post: {str(e)}")
            return False


class CommentService:
    """Service class for Comment-related operations."""

    @staticmethod
    def add_comment(post: Post, author, content: str) -> Comment:
        """Add a comment to a post."""
        try:
            comment = Comment.objects.create(
                post=post,
                author=author,
                content=content,
                active=True
            )
            logger.info(f"Comment added to post '{post.title}' by {author}")
            
            # Clear post cache
            cache.delete(f'post_{post.slug}')
            
            return comment
        except Exception as e:
            logger.error(f"Error adding comment: {str(e)}")
            raise

    @staticmethod
    def get_post_comments(post: Post, active_only: bool = True):
        """Get comments for a post."""
        query = post.comments
        
        if active_only:
            query = query.filter(active=True)
        
        return query.select_related('author').order_by('-created_at')


class LikeService:
    """Service class for Like-related operations."""

    @staticmethod
    def toggle_like(post: Post, user) -> tuple:
        """Toggle like status for a post. Returns (liked, total_likes)."""
        try:
            like, created = Like.objects.get_or_create(
                post=post,
                user=user
            )
            
            if not created:
                like.delete()
                liked = False
            else:
                liked = True
            
            logger.info(f"Post '{post.title}' {'liked' if liked else 'unliked'} by {user}")
            
            # Clear post cache
            cache.delete(f'post_{post.slug}')
            
            total_likes = post.total_likes()
            return liked, total_likes
        except Exception as e:
            logger.error(f"Error toggling like: {str(e)}")
            raise

    @staticmethod
    def is_liked_by(post: Post, user) -> bool:
        """Check if a user has liked a post."""
        if not user.is_authenticated:
            return False
        return post.is_liked_by(user)
