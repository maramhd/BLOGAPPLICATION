# 📚 REST API Documentation - Blog Application

## 🔐 Authentication

The API supports three authentication methods:

### 1️⃣ Token Authentication (Simple)

```bash
Authorization: Token YOUR_TOKEN_HERE
```

### 2️⃣ JWT Authentication (Recommended)

```bash
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

### 3️⃣ Session Authentication (Development)

```bash
Cookie: sessionid=YOUR_SESSION_ID
```

---

## 🚀 Getting Your Authentication Token

### Get JWT Access Token

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

Response:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refresh JWT Token

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### Get API Token (REST Framework Token)

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

Response:

```json
{
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "user@example.com"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Login successful"
}
```

---

## 👤 User Management

### Register New User

```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepass123",
  "password2": "securepass123"
}
```

Response: `201 Created`

```json
{
  "user": {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Registration successful"
}
```

### Login User

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepass123"
}
```

---

## 📝 Posts API

### List All Posts

```bash
GET /api/posts/
Authorization: Bearer YOUR_JWT_TOKEN

# Query Parameters:
# - ?page=1           # Pagination
# - ?search=django    # Search in title/content
# - ?ordering=-created_at  # Sort by date
# - ?category=1       # Filter by category
```

Response: `200 OK`

```json
{
  "count": 15,
  "next": "http://localhost:8000/api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Getting Started with Django",
      "slug": "getting-started-django",
      "excerpt": "A beginner's guide...",
      "author": {
        "id": 1,
        "username": "admin"
      },
      "category": {
        "id": 1,
        "name": "Django",
        "slug": "django"
      },
      "status": 1,
      "created_at": "2024-05-11T10:30:00Z",
      "updated_at": "2024-05-11T10:30:00Z",
      "comment_count": 5,
      "like_count": 12
    }
  ]
}
```

### Create Post (Authenticated Only)

```bash
POST /api/posts/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "title": "My New Post",
  "content": "Post content here...",
  "excerpt": "Brief summary",
  "category": 1,
  "status": 1
}
```

Response: `201 Created`

### Get Single Post

```bash
GET /api/posts/1/
Authorization: Bearer YOUR_JWT_TOKEN
```

Response:

```json
{
  "id": 1,
  "title": "Getting Started with Django",
  "slug": "getting-started-django",
  "content": "Full content...",
  "excerpt": "Brief summary",
  "author": {...},
  "category": {...},
  "comments": [
    {
      "id": 1,
      "author": "user1",
      "content": "Great post!",
      "created_at": "2024-05-11T11:00:00Z"
    }
  ],
  "likes": [
    {
      "id": 1,
      "user": "user1",
      "created_at": "2024-05-11T11:05:00Z"
    }
  ],
  "like_count": 12,
  "comment_count": 5
}
```

### Update Post (Author Only)

```bash
PUT /api/posts/1/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content...",
  "excerpt": "Updated summary",
  "status": 1
}
```

### Delete Post (Author Only)

```bash
DELETE /api/posts/1/
Authorization: Bearer YOUR_JWT_TOKEN
```

Response: `204 No Content`

### Get Trending Posts

```bash
GET /api/posts/trending/
```

Returns posts sorted by most likes.

### Get My Posts (Authenticated Users)

```bash
GET /api/posts/my_posts/
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 💬 Comments API

### List Comments

```bash
GET /api/comments/
Authorization: Bearer YOUR_JWT_TOKEN

# Query Parameters:
# - ?post=1   # Filter by post
```

### Create Comment (Authenticated Only)

```bash
POST /api/comments/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "post": 1,
  "content": "Great post!"
}
```

### Update Comment (Author Only)

```bash
PUT /api/comments/1/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "content": "Updated comment"
}
```

### Delete Comment (Author Only)

```bash
DELETE /api/comments/1/
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 👍 Likes API

### List Likes

```bash
GET /api/likes/
Authorization: Bearer YOUR_JWT_TOKEN
```

### Like a Post

```bash
POST /api/likes/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "post": 1
}
```

### Unlike a Post

```bash
DELETE /api/likes/1/
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 📂 Categories API

### List Categories

```bash
GET /api/categories/
```

Response:

```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Django",
      "slug": "django",
      "post_count": 12
    },
    {
      "id": 2,
      "name": "Python",
      "slug": "python",
      "post_count": 8
    }
  ]
}
```

### Get Category Details

```bash
GET /api/categories/1/
```

---

## 🧪 Testing with cURL

### Example: Register and Create Post

#### Step 1: Register

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'
```

Save the `access` token from response.

#### Step 2: Create Post

```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "My First Post",
    "content": "This is my first post content",
    "excerpt": "My first post",
    "category": 1,
    "status": 1
  }'
```

#### Step 3: List Posts

```bash
curl -X GET http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 Status Codes

| Code | Meaning                                |
| ---- | -------------------------------------- |
| 200  | OK - Successful GET/PUT request        |
| 201  | Created - Successful POST request      |
| 204  | No Content - Successful DELETE request |
| 400  | Bad Request - Invalid data             |
| 401  | Unauthorized - Missing/invalid token   |
| 403  | Forbidden - Permission denied          |
| 404  | Not Found - Resource not found         |
| 500  | Server Error - Internal error          |

---

## 🔒 Permissions

- **Anonymous Users**: Can view posts and categories (read-only)
- **Authenticated Users**: Can create comments, like posts, create posts
- **Authors**: Can edit/delete their own posts and comments
- **Staff**: Can access admin panel and manage all content

---

## 🚀 Rate Limiting

- **Anonymous Users**: 100 requests/hour
- **Authenticated Users**: 1000 requests/hour

---

## 💡 Best Practices

1. **Use JWT for Production**: More secure than tokens
2. **Always Use HTTPS**: In production environment
3. **Store Tokens Securely**: Never commit tokens to version control
4. **Refresh Tokens**: Regularly refresh JWT tokens
5. **CORS Settings**: Configure properly for cross-origin requests

---

## 🐛 Common Errors

### "Invalid token"

- Token has expired
- Token is malformed
- Token is revoked

### "Permission denied"

- User is not authenticated
- User doesn't have permission to modify resource

### "Not found"

- Resource doesn't exist
- Incorrect URL path

---

## 📝 Example: JavaScript Fetch

```javascript
// Register
async function register() {
  const response = await fetch("/api/auth/register/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: "newuser",
      email: "user@example.com",
      password: "pass123",
      password2: "pass123",
    }),
  });
  const data = await response.json();
  localStorage.setItem("access_token", data.access);
  return data;
}

// Get Posts
async function getPosts() {
  const token = localStorage.getItem("access_token");
  const response = await fetch("/api/posts/", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await response.json();
}

// Create Post
async function createPost(title, content) {
  const token = localStorage.getItem("access_token");
  const response = await fetch("/api/posts/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ title, content, status: 1 }),
  });
  return await response.json();
}
```

---

## 📚 Additional Resources

- [DRF Documentation](https://www.django-rest-framework.org/)
- [JWT Documentation](https://github.com/jpadilla/pyjwt)
- [API Endpoint Reference](#)

---

**Last Updated**: May 11, 2024  
**Status**: ✅ Complete
