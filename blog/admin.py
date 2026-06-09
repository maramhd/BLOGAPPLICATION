from django.contrib import admin
from django.contrib.auth.models import User
from .models import Post, Comment, Like, Category


class BlogAdminSite(admin.AdminSite):
    site_header = "Blog Admin"
    site_title = "Blog Admin"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['post_count'] = Post.objects.count()
        extra_context['comment_count'] = Comment.objects.count()
        extra_context['like_count'] = Like.objects.count()
        extra_context['user_count'] = User.objects.count()
        return super().index(request, extra_context=extra_context)


admin_site = BlogAdminSite(name='blog_admin')


@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Post, site=admin_site)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'excerpt', 'content', 'image')
        }),
        ('Metadata', {
            'fields': ('author', 'status', 'created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment, site=admin_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'active', 'created_at')
    list_filter = ('active', 'created_at', 'post')
    search_fields = ['author__username', 'content', 'post__title']
    readonly_fields = ('created_at',)
    ordering = ['-created_at']
    actions = ['approve_comments', 'reject_comments']

    fieldsets = (
        ('Comment Details', {
            'fields': ('post', 'author', 'content')
        }),
        ('Status', {
            'fields': ('active', 'created_at')
        }),
    )

    def approve_comments(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f"{updated} comment(s) approved.")

    def reject_comments(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f"{updated} comment(s) rejected.")


@admin.register(Like, site=admin_site)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ['user__username', 'post__title']
    readonly_fields = ('created_at',)
    ordering = ['-created_at']
