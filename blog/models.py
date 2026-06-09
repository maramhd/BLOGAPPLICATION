from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    #Django ORM لا يعتبر الكلاس جدولاً في قاعدة البيانات إلا إذا ورث من models.Model.
    """
     فئات المنشورات - تنظيم المحتوى
    (Blog post category for organizing content)
    """
    
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ إنشاء slug تلقائياً من الاسم (Auto-generate slug from name)"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    """
     نموذج المنشورات - المحتوى الرئيسي للمدونة
    (Blog post model with full publication features)
    """
    
    class Status(models.IntegerChoices):
        DRAFT = 0, "Draft"
        PUBLISH = 1, "Published"

    title = models.CharField(max_length=200, unique=True, db_index=True)
    
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    #ربط المنشور بمستخدم واحد.
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    content = models.TextField()
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief summary of the post"
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def total_likes(self):
        """Return total number of likes on this post."""
        return self.likes.count()

    def is_liked_by(self, user):
        """Check if a specific user has liked this post."""
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()
    
    def total_comments(self):
        """Return count of approved comments."""
        return self.comments.filter(active=True).count()



class Comment(models.Model):
    """
     التعليقات - تفاعل القراء مع المنشورات
    (User comments on blog posts)
    """
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    active = models.BooleanField(default=True, help_text="Show this comment on the site")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'active', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Like(models.Model):
    """
     الإعجابات - تفاعل المستخدمين مع المنشورات
    (User likes on blog posts)
    """
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        indexes = [
            models.Index(fields=['user', 'post']),
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"
