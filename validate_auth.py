#!/usr/bin/env python
"""
Validate authentication and authorization flows.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlogProject.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from blog.models import Post, Category

User = get_user_model()
client = Client()

print("=" * 60)
print("AUTHENTICATION & AUTHORIZATION VALIDATION")
print("=" * 60)
print()

# Clean up test data
User.objects.filter(username__startswith='test_').delete()
Post.objects.filter(title__startswith='Test Post').delete()
Category.objects.filter(name__startswith='Test').delete()

errors = []
tests_passed = 0

# Test 1: Registration page loads
print("Test 1: Registration page loads...")
try:
    response = client.get('/register/')
    if response.status_code == 200:
        print(f"  ✓ Status code: {response.status_code}")
        tests_passed += 1
    else:
        errors.append(f"Registration page returned {response.status_code}")
        print(f"  ✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"Registration page error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 2: User registration
print("\nTest 2: Register new user...")
try:
    response = client.post('/register/', {
        'username': 'test_user_123',
        'email': 'test@example.com',
        'password1': 'SecurePass123!',
        'password2': 'SecurePass123!'
    }, follow=True)
    user = User.objects.filter(username='test_user_123').first()
    if user:
        print(f"  ✓ User created: {user.username}")
        tests_passed += 1
    else:
        errors.append("User registration failed")
        print(f"  ✗ Registration failed")
except Exception as e:
    errors.append(f"User registration error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 3: Login page loads
print("\nTest 3: Login page loads...")
try:
    response = client.get('/login/')
    if response.status_code == 200:
        print(f"  ✓ Status code: {response.status_code}")
        tests_passed += 1
    else:
        errors.append(f"Login page returned {response.status_code}")
        print(f"  ✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"Login page error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 4: User login
print("\nTest 4: User login...")
try:
    response = client.post('/login/', {
        'username': 'test_user_123',
        'password': 'SecurePass123!'
    }, follow=True)
    if response.wsgi_request.user.is_authenticated:
        print(f"  ✓ User authenticated: {response.wsgi_request.user}")
        tests_passed += 1
    else:
        errors.append("User login failed")
        print(f"  ✗ Login failed")
except Exception as e:
    errors.append(f"User login error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 5: Anonymous user cannot create post
print("\nTest 5: Anonymous user cannot create post...")
try:
    client.logout()
    response = client.get('/post/create/')
    if response.status_code == 302:  # Redirect to login
        print(f"  ✓ Redirected to login (status {response.status_code})")
        tests_passed += 1
    else:
        errors.append(f"Expected redirect, got {response.status_code}")
        print(f"  ✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"Anonymous create post error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 6: Authenticated user can access create post
print("\nTest 6: Authenticated user can access create post...")
try:
    client.login(username='test_user_123', password='SecurePass123!')
    response = client.get('/post/create/')
    if response.status_code == 200:
        print(f"  ✓ Status code: {response.status_code}")
        tests_passed += 1
    else:
        errors.append(f"Create post returned {response.status_code}")
        print(f"  ✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"Create post access error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 7: Create a post and test author-only editing
print("\nTest 7: Create test post...")
try:
    user = User.objects.get(username='test_user_123')
    category = Category.objects.create(name='Test', slug='test')
    post = Post.objects.create(
        title='Test Post for Auth',
        slug='test-post-auth',
        content='Test content',
        excerpt='Test excerpt',
        author=user,
        category=category,
        status=Post.Status.PUBLISH
    )
    print(f"  ✓ Post created: {post.title}")
    tests_passed += 1
except Exception as e:
    errors.append(f"Post creation error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 8: Author can edit their post
print("\nTest 8: Author can edit their post...")
try:
    response = client.get(f'/post/{post.slug}/edit/')
    if response.status_code == 200:
        print(f"  ✓ Status code: {response.status_code}")
        tests_passed += 1
    else:
        errors.append(f"Author edit returned {response.status_code}")
        print(f"  ✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"Author edit error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 9: Non-author cannot edit post
print("\nTest 9: Non-author cannot edit post...")
try:
    # Create another user
    other_user = User.objects.create_user(
        username='test_other_user',
        email='other@example.com',
        password='SecurePass123!'
    )
    client.login(username='test_other_user', password='SecurePass123!')
    response = client.get(f'/post/{post.slug}/edit/')
    if response.status_code == 403:  # Forbidden
        print(f"  ✓ Access forbidden (status {response.status_code})")
        tests_passed += 1
    else:
        errors.append(f"Expected 403, got {response.status_code}")
        print(f"  ✗ Status code: {response.status_code} (expected 403)")
except Exception as e:
    errors.append(f"Non-author edit error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 10: Author can delete their post
print("\nTest 10: Author can delete their post...")
try:
    client.login(username='test_user_123', password='SecurePass123!')
    response = client.get(f'/post/{post.slug}/delete/')
    if response.status_code == 200:
        print(f"  ✓ Status code: {response.status_code}")
        tests_passed += 1
    else:
        errors.append(f"Author delete returned {response.status_code}")
        print(f"  ✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"Author delete error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 11: User logout
print("\nTest 11: User logout...")
try:
    response = client.get('/logout/', follow=True)
    if not response.wsgi_request.user.is_authenticated:
        print(f"  ✓ User logged out successfully")
        tests_passed += 1
    else:
        errors.append("User logout failed")
        print(f"  ✗ Logout failed")
except Exception as e:
    errors.append(f"Logout error: {str(e)}")
    print(f"  ✗ Error: {e}")

# Test 12: CSRF token present in forms
print("\nTest 12: CSRF protection in forms...")
try:
    response = client.get('/login/')
    if 'csrf' in response.content.decode().lower():
        print(f"  ✓ CSRF token present")
        tests_passed += 1
    else:
        errors.append("CSRF token not found")
        print(f"  ✗ CSRF token missing")
except Exception as e:
    errors.append(f"CSRF check error: {str(e)}")
    print(f"  ✗ Error: {e}")

print()
print("=" * 60)
print(f"RESULTS: {tests_passed} passed, {len(errors)} failed")
if errors:
    print("\nErrors:")
    for error in errors:
        print(f"  - {error}")
    exit(1)
else:
    print("✓ All authentication and authorization tests PASSED!")
    exit(0)
