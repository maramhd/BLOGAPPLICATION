from django.views import generic, View
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Post, Like, Comment
from .forms import CommentForm, QuickPostForm


class PostList(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status=1).order_by('-created_on')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quick_post_form'] = QuickPostForm()
        # للايك: نمرر set بـ IDs للبوستات التي أعجب بها المستخدم الحالي
        if self.request.user.is_authenticated:
            liked_ids = set(
                Like.objects.filter(user=self.request.user)
                .values_list('post_id', flat=True)
            )
        else:
            liked_ids = set()
        context['liked_ids'] = liked_ids
        return context

    def post(self, request, *args, **kwargs):
        """إضافة بوست سريع من الصفحة الرئيسية"""
        if not request.user.is_authenticated:
            return redirect('login')
        form = QuickPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.status = 1  # Publish مباشرة
            # توليد slug فريد من العنوان
            base_slug = slugify(post.title)
            slug = base_slug or f"post-{Post.objects.count()+1}"
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}" if base_slug else f"post-{Post.objects.count()+1}"
                counter += 1
            post.slug = slug
            post.save()
            messages.success(request, "Post published!")
        return redirect('home')


class PostDetail(generic.DetailView):
    model         = Post
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        # آخر تعليق نشط
        last_comment = post.comments.filter(active=True).order_by('-created_on').first()
        context['last_comment']  = last_comment
        context['all_comments']  = post.comments.filter(active=True).order_by('-created_on')
        context['comment_form']  = CommentForm()
        context['total_likes']   = post.total_likes()
        context['user_liked']    = (
            post.is_liked_by(self.request.user)
            if self.request.user.is_authenticated else False
        )
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        post = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment        = form.save(commit=False)
            comment.post   = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added!")
        return redirect('post_detail', slug=post.slug)


class LikeToggleView(View):
    """Toggle Like – يستجيب بـ JSON لتحديث العداد بدون reload"""
    def post(self, request, slug):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'login required'}, status=403)
        post   = get_object_or_404(Post, slug=slug)
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f"Welcome back!")
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=profile_user, status=1).order_by('-created_on')
    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'posts_count': posts.count(),
    })
