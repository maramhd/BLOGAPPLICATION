"""
Views for blog application with CRUD operations, authentication, and business logic.
"""

import logging
from typing import Optional
from django.views import generic, View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.views.decorators.http import require_POST

from .models import Post, Like, Comment, Category
from .forms import (
    PostForm, CommentForm, QuickPostForm, SearchForm,
    UserRegistrationForm, UserProfileForm
)
from .services import PostService, CommentService, LikeService
from .permissions import IsAuthorOrReadOnly

logger = logging.getLogger(__name__)


# ============================================================================
# POST VIEWS
# ============================================================================

class PostListView(generic.ListView):
    """Display paginated list of published blog posts."""
    
    model = Post
    template_name = 'index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        """Get published posts ordered by creation date."""
        return Post.objects.filter(
            status=Post.Status.PUBLISH
        ).select_related('author', 'category').annotate(
            comment_count=Count('comments', filter=Q(comments__active=True))
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        """Add quick post form and liked posts to context."""
        context = super().get_context_data(**kwargs)
        context['quick_post_form'] = QuickPostForm()
        context['search_form'] = SearchForm()
        
        # Get liked post IDs for current user
        if self.request.user.is_authenticated:
            liked_ids = set(
                Like.objects.filter(user=self.request.user)
                .values_list('post_id', flat=True)
            )
        else:
            liked_ids = set()
        context['liked_ids'] = liked_ids
        
        # Session tracking
        self.track_visit()
        
        return context

    def track_visit(self):
        """Track user visits using sessions."""
        session = self.request.session
        
        # Track visit count
        session['visit_count'] = session.get('visit_count', 0) + 1
        session['last_visit'] = str(__import__('django.utils.timezone', fromlist=['now']).now())
        session.modified = True

    def post(self, request, *args, **kwargs):
        """Handle quick post creation from homepage."""
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post.")
            return redirect('blog:login')
        
        form = QuickPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.status = Post.Status.PUBLISH
            post.excerpt = post.content[:500]  # Auto-generate excerpt
            post.save()
            
            messages.success(request, "Post published successfully!")
            logger.info(f"Post '{post.title}' created by {request.user}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return redirect('blog:home')


class PostDetailView(generic.DetailView):
    """Display individual post with comments and likes."""
    
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'

    def get_queryset(self):
        """Only show published posts."""
        return Post.objects.filter(
            status=Post.Status.PUBLISH
        ).select_related('author', 'category').prefetch_related('comments', 'likes')

    def get_context_data(self, **kwargs):
        """Add comments, likes, and forms to context."""
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Comments
        comments = post.comments.filter(active=True).select_related('author')
        context['all_comments'] = comments
        context['comment_form'] = CommentForm()
        
        # Likes
        context['total_likes'] = post.total_likes()
        context['user_liked'] = (
            post.is_liked_by(self.request.user)
            if self.request.user.is_authenticated else False
        )
        
        # Check if user is author
        context['is_author'] = post.author == self.request.user
        
        return context

    def post(self, request, *args, **kwargs):
        """Handle comment submission."""
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('blog:login')
        
        post = self.get_object()
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = CommentService.add_comment(
                post=post,
                author=request.user,
                content=form.cleaned_data['content']
            )
            messages.success(request, "Comment added successfully!")
            logger.info(f"Comment added to post '{post.title}' by {request.user}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return redirect('blog:post_detail', slug=post.slug)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Create a new blog post."""
    
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = reverse_lazy('blog:home')
    login_url = 'blog:login'

    def form_valid(self, form):
        """Set author to current user."""
        form.instance.author = self.request.user
        form.instance.status = Post.Status.PUBLISH
        
        response = super().form_valid(form)
        messages.success(self.request, f"Post '{form.instance.title}' created successfully!")
        logger.info(f"Post '{form.instance.title}' created by {self.request.user}")
        
        return response

    def get_context_data(self, **kwargs):
        """Add title to context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create New Post'
        context['submit_text'] = 'Publish Post'
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit an existing blog post."""
    
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    slug_field = 'slug'
    login_url = 'blog:login'

    def test_func(self):
        """Only author can edit post."""
        post = self.get_object()
        return post.author == self.request.user

    def form_valid(self, form):
        """Handle successful form submission."""
        response = super().form_valid(form)
        messages.success(self.request, "Post updated successfully!")
        logger.info(f"Post '{form.instance.title}' updated by {self.request.user}")
        return response

    def get_context_data(self, **kwargs):
        """Add title and submit text to context."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Post'
        context['submit_text'] = 'Update Post'
        return context

    def get_success_url(self):
        """Redirect to post detail after successful update."""
        return reverse('blog:post_detail', kwargs={'slug': self.object.slug})

    def handle_no_permission(self):
        """Redirect unauthorized users."""
        messages.error(self.request, "You can only edit your own posts.")
        return redirect('blog:home')


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a blog post."""
    
    model = Post
    template_name = 'post_confirm_delete.html'
    success_url = reverse_lazy('blog:home')
    slug_field = 'slug'
    login_url = 'blog:login'

    def test_func(self):
        """Only author can delete post."""
        post = self.get_object()
        return post.author == self.request.user

    def delete(self, request, *args, **kwargs):
        """Log deletion and show message."""
        post = self.get_object()
        messages.success(request, f"Post '{post.title}' deleted successfully.")
        logger.info(f"Post '{post.title}' deleted by {request.user}")
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirect unauthorized users."""
        messages.error(self.request, "You can only delete your own posts.")
        return redirect('blog:home')


# ============================================================================
# SEARCH & CATEGORY VIEWS
# ============================================================================

class PostSearchView(generic.ListView):
    """Search blog posts by title and content."""
    
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        """Search posts based on query parameter."""
        query = self.request.GET.get('q', '')
        if query:
            logger.info(f"Search performed for: {query}")
            return PostService.search_posts(query)
        return Post.objects.none()

    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['search_form'] = SearchForm()
        return context


class CategoryListView(generic.ListView):
    """Display all categories."""
    
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        """Get categories with post count."""
        return Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status=Post.Status.PUBLISH))
        ).filter(post_count__gt=0)


class CategoryDetailView(generic.ListView):
    """Display posts from specific category."""
    
    model = Post
    template_name = 'category_detail.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        """Get published posts from category."""
        slug = self.kwargs.get('slug')
        return Post.objects.filter(
            category__slug=slug,
            status=Post.Status.PUBLISH
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        """Add category to context."""
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context['category'] = get_object_or_404(Category, slug=slug)
        return context


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

@require_POST
@login_required
def toggle_like_view(request, slug: str):
    """Toggle like on a post (AJAX endpoint)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=403)
    
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISH)
    
    try:
        liked, total_likes = LikeService.toggle_like(post, request.user)
        logger.info(f"Post {slug} {'liked' if liked else 'unliked'} by {request.user}")
        
        return JsonResponse({
            'liked': liked,
            'total_likes': total_likes,
            'status': 'success'
        })
    except Exception as e:
        logger.error(f"Error toggling like: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('blog:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account has been created.")
            logger.info(f"New user registered: {user.username}")
            return redirect('blog:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('blog:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            logger.info(f"User {user.username} logged in")
            return redirect(request.GET.get('next', 'blog:home'))
        else:
            messages.error(request, "Invalid username or password.")
            logger.warning(f"Failed login attempt for username: {username}")
    
    return render(request, 'login.html')


def logout_view(request):
    """User logout."""
    username = request.user.username if request.user.is_authenticated else None
    logout(request)
    messages.info(request, "You have been logged out.")
    if username:
        logger.info(f"User {username} logged out")
    return redirect('blog:home')


# ============================================================================
# PROFILE VIEWS
# ============================================================================

def profile_view(request, username: str):
    """Display user profile with their posts."""
    profile_user = get_object_or_404(User, username=username)
    
    # Get user's published posts
    posts = Post.objects.filter(
        author=profile_user,
        status=Post.Status.PUBLISH
    ).select_related('author', 'category').annotate(
        comment_count=Count('comments', filter=Q(comments__active=True))
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Check if viewing own profile
    is_own_profile = request.user.is_authenticated and request.user == profile_user
    
    context = {
        'profile_user': profile_user,
        'page_obj': page_obj,
        'posts_count': posts.count(),
        'is_own_profile': is_own_profile,
        'followers_count': 0,  # Can be extended
        'following_count': 0,  # Can be extended
    }
    
    return render(request, 'profile.html', context)



@login_required
def profile_edit_view(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            logger.info(f"User {request.user.username} updated profile")
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'profile_edit.html', {'form': form})


# ============================================================================
# ERROR HANDLING VIEWS
# ============================================================================

def page_not_found_view(request, exception=None):
    """Handle 404 errors."""
    return render(request, '404.html', status=404)


def server_error_view(request):
    """Handle 500 errors."""
    logger.error("Server error occurred")
    return render(request, '500.html', status=500)


def health_check_view(request):
    """
    Health check endpoint for container orchestration and monitoring.
    Checks database connectivity and basic system health.
    """
    from django.db import connection
    from django.core.cache import cache
    
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check cache connectivity
        cache.set('health_check', True, 10)
        cache_ok = cache.get('health_check')
        
        if cache_ok:
            return JsonResponse({
                'status': 'healthy',
                'database': 'connected',
                'cache': 'connected'
            }, status=200)
        else:
            return JsonResponse({
                'status': 'degraded',
                'database': 'connected',
                'cache': 'error'
            }, status=200)
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
