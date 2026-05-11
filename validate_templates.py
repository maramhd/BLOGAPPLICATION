#!/usr/bin/env python
"""
Validate all templates can be loaded and rendered without errors.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlogProject.settings')
django.setup()

from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.contrib.auth import get_user_model
from blog.models import Post, Category, Comment

User = get_user_model()

# Create test data
try:
    category = Category.objects.first() or Category.objects.create(
        name='Test Category',
        slug='test-category'
    )
    
    # Try to get or create a test user
    user = User.objects.first() or User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    
    post = Post.objects.filter(status=Post.Status.PUBLISH).first()
    if not post:
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            excerpt='Test excerpt',
            author=user,
            category=category,
            status=Post.Status.PUBLISH
        )
except Exception as e:
    print(f"Warning: Could not create test data: {e}")
    post = None
    user = None

# Templates to validate
templates_to_check = [
    'base.html',
    'index.html',
    'login.html',
    'register.html',
    'post_detail.html',
    'post_form.html',
    'post_confirm_delete.html',
    'post_search.html',
    'profile.html',
    'profile_edit.html',
    'category_list.html',
    'category_detail.html',
    '404.html',
    '500.html',
]

print("=" * 60)
print("TEMPLATE VALIDATION")
print("=" * 60)
print()

errors = []
for template_name in templates_to_check:
    try:
        # Try to load and render the template with context
        context = {
            'user': user,
            'post': post,
            'posts': Post.objects.filter(status=Post.Status.PUBLISH)[:5],
            'categories': Category.objects.all(),
            'is_paginated': False,
            'page_obj': None,
            'query': '',
            'object': post,
        }
        html = render_to_string(template_name, context)
        # Check for common template issues
        if not html or len(html) < 10:
            print(f"⚠ {template_name:30} - Template too small or empty")
        else:
            print(f"✓ {template_name:30} - {len(html)} bytes")
    except TemplateDoesNotExist as e:
        errors.append(f"✗ {template_name}: Template not found")
        print(f"✗ {template_name:30} - NOT FOUND")
    except TemplateSyntaxError as e:
        errors.append(f"✗ {template_name}: Syntax error on line {e.lineno}: {e.msg}")
        print(f"✗ {template_name:30} - SYNTAX ERROR: {e.msg}")
    except Exception as e:
        errors.append(f"✗ {template_name}: {str(e)}")
        print(f"✗ {template_name:30} - ERROR: {type(e).__name__}")

print()
print("=" * 60)
if errors:
    print(f"RESULT: {len(errors)} template errors found!")
    for error in errors:
        print(error)
    exit(1)
else:
    print(f"RESULT: ✓ All {len(templates_to_check)} templates PASSED!")
    exit(0)
