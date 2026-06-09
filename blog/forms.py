from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Comment, Post, Category


class PostForm(forms.ModelForm):
    """Complete form for creating and editing blog posts."""
    
    class Meta:
        model = Post
        fields = ['title', 'category', 'excerpt', 'content', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title...',
                'maxlength': '200'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief summary of the post (optional)',
                'maxlength': '500'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Write your post content here...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'title': 'Post Title',
            'category': 'Category',
            'excerpt': 'Summary',
            'content': 'Content',
            'image': 'Featured Image',
            'status': 'Status',
        }
    
    def clean_title(self):
        """Validate title uniqueness excluding current post."""
        title = self.cleaned_data.get('title')
        if title:
            # Check if another post with same title exists
            existing = Post.objects.filter(title__iexact=title)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError("A post with this title already exists.")
        return title

    def clean_image(self):
        """Validate image file."""
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file size must not exceed 5MB.")
        return image


class CommentForm(forms.ModelForm):
    """Form for creating comments on posts."""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...',
                'maxlength': '1000'
            })
        }
        labels = {
            'content': 'Your Comment',
        }

    def clean_content(self):
        """Validate comment content."""
        content = self.cleaned_data.get('content')
        if content and len(content.strip()) < 3:
            raise forms.ValidationError("Comment must be at least 3 characters long.")
        return content


class QuickPostForm(forms.ModelForm):
    """Quick post form for homepage (Facebook-style)."""
    
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control mb-2',
                'placeholder': "Post title..."
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': "What's on your mind?"
            }),
        }
        labels = {
            'title': 'Title',
            'content': '',
        }


class SearchForm(forms.Form):
    """Search form for blog posts."""
    
    query = forms.CharField(
        label='Search Posts',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts by title, content...'
        })
    )


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        """Check if email already exists."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        """Save user with email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(UserChangeForm):
    """Form for updating user profile."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
