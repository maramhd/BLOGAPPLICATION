from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    class Status(models.IntegerChoices):
        DRAFT   = 0, "Draft"
        PUBLISH = 1, "Publish"

    title      = models.CharField(max_length=200, unique=True)
    slug       = models.SlugField(max_length=200, unique=True)
    author     = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )
    content    = models.TextField()
    status     = models.IntegerField(
        choices=Status.choices, default=Status.DRAFT
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.count()

    def is_liked_by(self, user):
        return self.likes.filter(user=user).exists()


class Comment(models.Model):
    post       = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author     = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    content    = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active     = models.BooleanField(default=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"


class Like(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='likes'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes'
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"
