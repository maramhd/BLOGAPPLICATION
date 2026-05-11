from django.contrib import admin
from .models import Post, Comment, Like, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for blog categories."""
    
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for blog posts with enhanced features."""
    
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
        """Automatically set author when creating a post."""
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for comments with moderation features."""
    
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
        """Action to approve selected comments."""
        updated = queryset.update(active=True)
        self.message_user(request, f"{updated} comment(s) approved.")

    def reject_comments(self, request, queryset):
        """Action to reject selected comments."""
        updated = queryset.update(active=False)
        self.message_user(request, f"{updated} comment(s) rejected.")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin interface for likes."""
    
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ['user__username', 'post__title']
    readonly_fields = ('created_at',)
    ordering = ['-created_at']
