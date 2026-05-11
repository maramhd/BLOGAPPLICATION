#!/usr/bin/env python
"""
Fix remaining redirect calls in views.py
"""
import re

file_path = r'c:\Users\Maram\Desktop\S2\Web application development\BlogApplication\blog\views.py'

with open(file_path, 'r') as f:
    content = f.read()

# Find all redirect calls
redirects = [
    ("redirect('login')", "redirect('blog:login')"),
    ("redirect('home')", "redirect('blog:home')"),
    ("redirect('post_detail'", "redirect('blog:post_detail'"),
    ("redirect('profile'", "redirect('blog:profile'"),
]

original_content = content
for old, new in redirects:
    content = content.replace(old, new)

if content != original_content:
    with open(file_path, 'w') as f:
        f.write(content)
    print("✓ Fixed all redirect calls")
else:
    print("✗ No changes made")
