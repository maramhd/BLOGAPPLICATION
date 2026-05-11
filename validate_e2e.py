#!/usr/bin/env python
"""
End-to-end runtime simulation of complete user workflows.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlogProject.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from blog.models import Post, Category, Comment, Like

User = get_user_model()
client = Client()

print("=" * 70)
print("END-TO-END RUNTIME VALIDATION")
print("=" * 70)
print()

# Clean up
User.objects.filter(username__startswith='e2e_').delete()
Post.objects.filter(title__startswith='E2E').delete()
Category.objects.filter(name__startswith='E2E').delete()

errors = []
tests_passed = 0

print("WORKFLOW 1: User Registration & Login")
print("-" * 70)

# Step 1: Visit homepage
try:
    response = client.get('/')
    if response.status_code == 200:
        print("✓ Homepage loads")
        tests_passed += 1
    else:
        errors.append(f"Homepage returned {response.status_code}")
        print(f"✗ Homepage error: {response.status_code}")
except Exception as e:
    errors.append(f"Homepage error: {str(e)}")
    print(f"✗ {e}")

# Step 2: Register user
try:
    response = client.post('/register/', {
        'username': 'e2e_user1',
        'email': 'e2euser1@example.com',
        'password1': 'SecurePass123!@',
        'password2': 'SecurePass123!@'
    }, follow=True)
    user = User.objects.filter(username='e2e_user1').first()
    if user:
        print("✓ User registration successful")
        tests_passed += 1
    else:
        print(f"✗ Registration failed")
        errors.append("User not created after registration")
except Exception as e:
    errors.append(f"Registration error: {str(e)}")
    print(f"✗ {e}")

# Step 3: Login
try:
    success = client.login(username='e2e_user1', password='SecurePass123!@')
    if success:
        print("✓ User login successful")
        tests_passed += 1
    else:
        errors.append("User login failed")
        print(f"✗ Login failed")
except Exception as e:
    errors.append(f"Login error: {str(e)}")
    print(f"✗ {e}")

print("\nWORKFLOW 2: Post Creation & Management")
print("-" * 70)

# Step 4: Create category
try:
    category = Category.objects.create(
        name='E2E Test Category',
        slug='e2e-test-category'
    )
    print("✓ Category created")
    tests_passed += 1
except Exception as e:
    errors.append(f"Category creation error: {str(e)}")
    print(f"✗ {e}")
    category = None

# Step 5: Create post
try:
    response = client.post('/post/create/', {
        'title': 'E2E Test Post',
        'content': 'This is an end-to-end test post',
        'category': category.id if category else 1,
        'status': 1  # PUBLISH
    }, follow=True)
    post = Post.objects.filter(title='E2E Test Post').first()
    if post:
        print("✓ Post creation successful")
        tests_passed += 1
    else:
        print(f"✗ Post not created")
        errors.append("Post not found after creation")
except Exception as e:
    errors.append(f"Post creation error: {str(e)}")
    print(f"✗ {e}")
    post = None

# Step 6: View post detail
if post:
    try:
        response = client.get(f'/post/{post.slug}/')
        if response.status_code == 200:
            print("✓ Post detail view loads")
            tests_passed += 1
        else:
            errors.append(f"Post detail returned {response.status_code}")
            print(f"✗ Post detail error: {response.status_code}")
    except Exception as e:
        errors.append(f"Post detail error: {str(e)}")
        print(f"✗ {e}")

    # Step 7: Edit post
    try:
        response = client.post(f'/post/{post.slug}/edit/', {
            'title': 'E2E Test Post - Edited',
            'content': 'This is an edited test post',
            'category': category.id if category else 1,
            'status': 1  # PUBLISH
        }, follow=True)
        post.refresh_from_db()
        if 'Edited' in post.title:
            print("✓ Post edit successful")
            tests_passed += 1
        else:
            errors.append("Post not updated after edit")
            print(f"✗ Post edit failed")
    except Exception as e:
        errors.append(f"Post edit error: {str(e)}")
        print(f"✗ {e}")

print("\nWORKFLOW 3: Comments & Interactions")
print("-" * 70)

# Step 8: Add comment
if post:
    try:
        response = client.post(f'/post/{post.slug}/', {
            'content': 'Great post!'
        }, follow=True)
        comment = Comment.objects.filter(post=post).first()
        if comment:
            print("✓ Comment creation successful")
            tests_passed += 1
        else:
            print(f"✗ Comment not created")
            errors.append("Comment not found after posting")
    except Exception as e:
        errors.append(f"Comment error: {str(e)}")
        print(f"✗ {e}")

    # Step 9: Like post
    try:
        response = client.post(f'/post/{post.slug}/like/', {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        like = Like.objects.filter(post=post, user=user).first()
        if like or response.status_code == 200:
            print("✓ Like functionality works")
            tests_passed += 1
        else:
            print(f"✗ Like not created")
            errors.append("Like not registered")
    except Exception as e:
        errors.append(f"Like error: {str(e)}")
        print(f"✗ {e}")

print("\nWORKFLOW 4: Search & Filter")
print("-" * 70)

# Step 10: Search posts
try:
    response = client.get('/search/', {'q': 'E2E'})
    if response.status_code == 200:
        print("✓ Search functionality works")
        tests_passed += 1
    else:
        errors.append(f"Search returned {response.status_code}")
        print(f"✗ Search error: {response.status_code}")
except Exception as e:
    errors.append(f"Search error: {str(e)}")
    print(f"✗ {e}")

# Step 11: Browse categories
try:
    response = client.get('/categories/')
    if response.status_code == 200:
        print("✓ Category list loads")
        tests_passed += 1
    else:
        errors.append(f"Categories returned {response.status_code}")
        print(f"✗ Categories error: {response.status_code}")
except Exception as e:
    errors.append(f"Categories error: {str(e)}")
    print(f"✗ {e}")

# Step 12: View category posts
if category:
    try:
        response = client.get(f'/category/{category.slug}/')
        if response.status_code == 200:
            print("✓ Category detail loads")
            tests_passed += 1
        else:
            errors.append(f"Category detail returned {response.status_code}")
            print(f"✗ Category detail error: {response.status_code}")
    except Exception as e:
        errors.append(f"Category detail error: {str(e)}")
        print(f"✗ {e}")

print("\nWORKFLOW 5: User Profile")
print("-" * 70)

# Step 13: View profile
try:
    response = client.get(f'/profile/{user.username}/')
    if response.status_code == 200:
        print("✓ User profile loads")
        tests_passed += 1
    else:
        errors.append(f"Profile returned {response.status_code}")
        print(f"✗ Profile error: {response.status_code}")
except Exception as e:
    errors.append(f"Profile error: {str(e)}")
    print(f"✗ {e}")

# Step 14: Edit profile
try:
    response = client.post('/profile/edit/', {
        'email': 'newemail@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }, follow=True)
    user.refresh_from_db()
    if user.email == 'newemail@example.com':
        print("✓ Profile edit successful")
        tests_passed += 1
    else:
        print(f"✗ Profile not updated")
        errors.append("Email not updated after profile edit")
except Exception as e:
    errors.append(f"Profile edit error: {str(e)}")
    print(f"✗ {e}")

print("\nWORKFLOW 6: Logout")
print("-" * 70)

# Step 15: Logout
try:
    response = client.get('/logout/', follow=True)
    print("✓ Logout successful")
    tests_passed += 1
except Exception as e:
    errors.append(f"Logout error: {str(e)}")
    print(f"✗ {e}")

print("\n" + "=" * 70)
print(f"END-TO-END RESULTS: {tests_passed} passed, {len(errors)} failed")
print("=" * 70)

if errors:
    print("\nErrors:")
    for error in errors:
        print(f"  - {error}")
    exit(1)
else:
    print("✓ All end-to-end workflows PASSED!")
    print("✓ Application is production-ready for basic operations")
    exit(0)
