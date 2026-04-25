from django import forms
from .models import Comment, Post


class CommentForm(forms.ModelForm):
    class Meta:
        model   = Comment
        fields  = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            })
        }


class QuickPostForm(forms.ModelForm):
    """فورم إضافة بوست سريع من الصفحة الرئيسية مثل Facebook"""
    class Meta:
        model   = Post
        fields  = ('title', 'content')
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
            'title':   'Title',
            'content': '',
        }
