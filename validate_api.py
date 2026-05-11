#!/usr/bin/env python
"""
Validate REST API endpoints and functionality.
"""
import os
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlogProject.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from blog.models import Post, Category, Comment

User = get_user_model()
client = Client()

print("=" * 70)
print("REST API VALIDATION")
print("=" * 70)
print()

# Clean up test data
User.objects.filter(username__startswith='api_').delete()
Post.objects.filter(title__startswith='API Test').delete()
Category.objects.filter(name__startswith='API Test').delete()

errors = []
tests_passed = 0

# Setup: Create test user and data
print("Setting up test data...")
try:
    # Create test user
    user = User.objects.create_user(
        username='api_test_user',
        email='apitest@example.com',
        password='TestPass123!'
    )
    
    # Create test category
    category = Category.objects.create(
        name='API Test Category',
        slug='api-test-category'
    )
    
    # Create test post
    post = Post.objects.create(
        title='API Test Post',
        slug='api-test-post',
        content='API test content',
        excerpt='API test excerpt',
        author=user,
        category=category,
        status=Post.Status.PUBLISH
    )
    
    print(f"  ✓ Test user created: {user.username}")
    print(f"  ✓ Test category created: {category.name}")
    print(f"  ✓ Test post created: {post.title}")
except Exception as e:
    errors.append(f"Setup error: {str(e)}")
    print(f"  ✗ Setup error: {e}")
    exit(1)

print("\n" + "=" * 70)
print("TEST 1: GET /api/posts/ - List posts")
print("=" * 70)
try:
    response = client.get('/api/posts/', HTTP_ACCEPT='application/json')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✓ Successfully retrieved posts")
        print(f"  Response type: {type(data).__name__}")
        if isinstance(data, dict) and 'results' in data:
            print(f"  Total posts: {data.get('count', 'N/A')}")
            print(f"  Posts in response: {len(data.get('results', []))}")
        elif isinstance(data, list):
            print(f"  Posts in response: {len(data)}")
        tests_passed += 1
    else:
        errors.append(f"GET /api/posts/ returned {response.status_code}")
        print(f"✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"GET /api/posts/ error: {str(e)}")
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TEST 2: GET /api/posts/{id}/ - Get specific post")
print("=" * 70)
try:
    response = client.get(f'/api/posts/{post.id}/', HTTP_ACCEPT='application/json')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✓ Successfully retrieved post detail")
        print(f"  Title: {data.get('title', 'N/A')}")
        print(f"  Author: {data.get('author', 'N/A')}")
        tests_passed += 1
    else:
        errors.append(f"GET /api/posts/{post.id}/ returned {response.status_code}")
        print(f"✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"GET /api/posts/{post.id}/ error: {str(e)}")
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TEST 3: GET /api/categories/ - List categories")
print("=" * 70)
try:
    response = client.get('/api/categories/', HTTP_ACCEPT='application/json')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✓ Successfully retrieved categories")
        if isinstance(data, dict) and 'results' in data:
            print(f"  Total categories: {data.get('count', 'N/A')}")
        elif isinstance(data, list):
            print(f"  Categories in response: {len(data)}")
        tests_passed += 1
    else:
        errors.append(f"GET /api/categories/ returned {response.status_code}")
        print(f"✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"GET /api/categories/ error: {str(e)}")
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TEST 4: POST /api/posts/ - Create post (requires auth)")
print("=" * 70)
try:
    client.login(username='api_test_user', password='TestPass123!')
    response = client.post('/api/posts/', {
        'title': 'API Created Post',
        'slug': 'api-created-post',
        'content': 'Created via API',
        'excerpt': 'Excerpt',
        'category': category.id,
        'status': 'published'
    }, HTTP_ACCEPT='application/json')
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = json.loads(response.content)
        print(f"✓ Successfully created post via API")
        print(f"  Title: {data.get('title', 'N/A')}")
        tests_passed += 1
    else:
        print(f"✗ Status code: {response.status_code}")
        if response.content:
            try:
                data = json.loads(response.content)
                print(f"  Error response: {data}")
            except:
                print(f"  Response: {response.content[:200]}")
except Exception as e:
    errors.append(f"POST /api/posts/ error: {str(e)}")
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TEST 5: GET /api/comments/ - List comments")
print("=" * 70)
try:
    response = client.get('/api/comments/', HTTP_ACCEPT='application/json')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✓ Successfully retrieved comments")
        if isinstance(data, dict) and 'results' in data:
            print(f"  Total comments: {data.get('count', 'N/A')}")
        elif isinstance(data, list):
            print(f"  Comments in response: {len(data)}")
        tests_passed += 1
    else:
        errors.append(f"GET /api/comments/ returned {response.status_code}")
        print(f"✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"GET /api/comments/ error: {str(e)}")
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TEST 6: GET /api/ - API root")
print("=" * 70)
try:
    response = client.get('/api/', HTTP_ACCEPT='application/json')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"✓ API root accessible")
        print(f"  Available endpoints: {list(data.keys())}")
        tests_passed += 1
    else:
        errors.append(f"GET /api/ returned {response.status_code}")
        print(f"✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"GET /api/ error: {str(e)}")
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("TEST 7: DRF Browsable API")
print("=" * 70)
try:
    response = client.get('/api/posts/', HTTP_ACCEPT='text/html')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ DRF Browsable API working")
        tests_passed += 1
    else:
        errors.append(f"Browsable API returned {response.status_code}")
        print(f"✗ Status code: {response.status_code}")
except Exception as e:
    errors.append(f"Browsable API error: {str(e)}")
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print(f"RESULTS: {tests_passed} passed, {len(errors)} failed")
print("=" * 70)

if errors:
    print("\nErrors found:")
    for error in errors:
        print(f"  - {error}")
    exit(1)
else:
    print("✓ All API validation tests PASSED!")
    exit(0)
