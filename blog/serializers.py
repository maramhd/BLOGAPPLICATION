"""
DRF Serializers for blog app REST API.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Like, Category


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'post_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_post_count(self, obj):
        """Return count of published posts in category."""
        from django.db.models import Count, Q
        return obj.posts.filter(status=Post.Status.PUBLISH).count()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_id', 'content', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """Create comment with authenticated user as author."""
        validated_data.pop('author_id', None)
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model."""
    
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class PostListSerializer(serializers.ModelSerializer):
    """Simplified serializer for post listings."""
    
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'category',
            'excerpt', 'image', 'status', 'created_at', 'updated_at',
            'comment_count', 'like_count', 'user_liked'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        """Return count of active comments."""
        return obj.comments.filter(active=True).count()

    def get_like_count(self, obj):
        """Return total likes."""
        return obj.total_likes()

    def get_user_liked(self, obj):
        """Check if requesting user liked the post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False


class PostDetailSerializer(serializers.ModelSerializer):
    """Full serializer for post detail view."""
    
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'category',
            'content', 'excerpt', 'image', 'status',
            'created_at', 'updated_at', 'comments', 'likes',
            'comment_count', 'like_count', 'user_liked', 'is_author'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        """Return count of active comments."""
        return obj.comments.filter(active=True).count()

    def get_like_count(self, obj):
        """Return total likes."""
        return obj.total_likes()

    def get_user_liked(self, obj):
        """Check if requesting user liked the post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by(request.user)
        return False

    def get_is_author(self, obj):
        """Check if requesting user is the author."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating posts."""
    
    author = UserSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
        source='category'
    )

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'category_id', 'excerpt', 'content',
            'image', 'status', 'author', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create post with authenticated user as author."""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def validate_title(self, value):
        """Validate title uniqueness."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            if Post.objects.filter(title__iexact=value).exists():
                raise serializers.ValidationError("A post with this title already exists.")
        return value

    def validate_image(self, value):
        """Validate image file size."""
        if value and value.size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError("Image file size must not exceed 5MB.")
        return value
