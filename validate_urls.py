#!/usr/bin/env python
"""
Validate all URL reversals to ensure no broken routes.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlogProject.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

test_urls = [
    ('blog:home', {}),
    ('blog:post_create', {}),
    ('blog:post_detail', {'slug': 'test-post'}),
    ('blog:post_edit', {'slug': 'test-post'}),
    ('blog:post_delete', {'slug': 'test-post'}),
    ('blog:post_search', {}),
    ('blog:category_list', {}),
    ('blog:category_detail', {'slug': 'test-category'}),
    ('blog:register', {}),
    ('blog:login', {}),
    ('blog:logout', {}),
    ('blog:profile', {'username': 'testuser'}),
    ('blog:profile_edit', {}),
    ('blog:toggle_like', {'slug': 'test-post'}),
]

print("=" * 60)
print("URL REVERSAL VALIDATION")
print("=" * 60)
print()

errors = []
for name, kwargs in test_urls:
    try:
        url = reverse(name, kwargs=kwargs)
        print(f"✓ {name:30} → {url}")
    except NoReverseMatch as e:
        errors.append(f"✗ {name}: {str(e)}")
        print(f"✗ {name}: {str(e)}")

print()
print("=" * 60)
if errors:
    print(f"RESULT: {len(errors)} URL reversal errors found!")
    for error in errors:
        print(error)
    exit(1)
else:
    print(f"RESULT: ✓ All {len(test_urls)} URL reversals PASSED!")
    exit(0)
