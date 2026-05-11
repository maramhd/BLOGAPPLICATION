# Django Blog Application - Production Ready

A professional, scalable Django blog application built with modern engineering standards, featuring REST API, caching, logging, and comprehensive admin interface.

## Features

### Core Features ✅

- **Authentication System**: Register, login, logout, session management
- **User Profiles**: Create and manage user profiles with posts
- **Blog Posts**: Create, read, update, delete posts with images
- **Categories**: Organize posts by categories
- **Comments**: Discuss posts with comment system
- **Likes System**: Like/unlike posts (AJAX-powered)
- **Search**: Full-text search across posts
- **Pagination**: Paginated post listings

### API Features ✅

- **REST API**: Complete CRUD endpoints for all models
- **Filtering & Search**: Advanced filtering and full-text search
- **Pagination**: Configurable page-based pagination
- **Permissions**: Custom authorization (author-only editing)
- **Throttling**: Rate limiting for API endpoints

### Technical Features ✅

- **Logging System**: Comprehensive logging to file and console
- **Caching**: Infrastructure for caching (ready for Redis)
- **Sessions**: Track user visits and preferences
- **Database Optimization**: Indexes and query optimization
- **Security**: CSRF protection, HTTPS ready, secure cookies
- **Error Handling**: Custom error pages and exception handling

## Project Structure

```
BlogApplication/
├── blog/                          # Main Django app
│   ├── api/                       # REST API
│   │   ├── __init__.py
│   │   ├── viewsets.py           # DRF ViewSets
│   │   └── urls.py               # API URL routing
│   ├── migrations/                # Database migrations
│   ├── templates/blog/            # App templates (future)
│   ├── static/blog/               # App static files (future)
│   ├── admin.py                   # Admin customization
│   ├── apps.py                    # App configuration
│   ├── forms.py                   # Form classes
│   ├── models.py                  # Database models
│   ├── permissions.py             # Custom permissions
│   ├── serializers.py             # DRF serializers
│   ├── services.py                # Business logic
│   ├── urls.py                    # URL routing
│   └── views.py                   # View classes
├── BlogProject/                   # Project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                # Django settings (MODIFIED)
│   ├── urls.py                    # Root URL routing (MODIFIED)
│   └── wsgi.py
├── templates/                     # Global templates
│   ├── base.html                  # Base template
│   ├── index.html                 # Homepage
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── post_detail.html           # Post detail view
│   ├── post_form.html             # Create/edit post (NEW)
│   ├── post_confirm_delete.html   # Delete confirmation (NEW)
│   ├── post_search.html           # Search results (NEW)
│   ├── profile.html               # User profile (UPDATED)
│   ├── profile_edit.html          # Edit profile (NEW)
│   ├── category_list.html         # Categories (NEW)
│   ├── category_detail.html       # Posts by category (NEW)
│   ├── 404.html                   # Not found error (NEW)
│   ├── 500.html                   # Server error (NEW)
│   └── sidebar.html               # Sidebar component
├── static/                        # Static files
├── media/                         # User uploads
├── logs/                          # Log files
├── db.sqlite3                     # SQLite database
├── manage.py                      # Django management
├── requirements.txt               # Python dependencies (NEW)
├── .env                          # Environment variables (NEW)
└── README.md                      # This file
```

## Database Models

### Category

```python
- name: CharField (unique, indexed)
- slug: SlugField (unique)
- created_at: DateTimeField (auto_now_add)
```

### Post

```python
- title: CharField (unique, indexed)
- slug: SlugField (unique, indexed)
- author: ForeignKey(User)
- category: ForeignKey(Category, null=True)
- content: TextField
- excerpt: TextField (up to 500 chars)
- image: ImageField (optional)
- status: IntegerField (Draft=0, Published=1)
- created_at: DateTimeField (auto_now_add)
- updated_at: DateTimeField (auto_now)
```

### Comment

```python
- post: ForeignKey(Post)
- author: ForeignKey(User)
- content: TextField
- active: BooleanField (default=True)
- created_at: DateTimeField (auto_now_add)
```

### Like

```python
- post: ForeignKey(Post)
- user: ForeignKey(User)
- created_at: DateTimeField (auto_now_add)
- unique_together: (post, user)
```

## Installation & Setup

### Prerequisites

- Python 3.10+
- pip or pipenv
- Virtual environment (recommended)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd BlogApplication

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy .env file and update settings
cp .env .env.local
# Edit .env.local with your settings
```

### Step 3: Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 4: Collect Static Files

```bash
python manage.py collectstatic
```

### Step 5: Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Usage

### Admin Interface

- URL: `http://localhost:8000/admin/`
- Create and manage posts, comments, and categories
- Approve/reject comments
- View detailed statistics

### Main Website

- **Homepage**: Browse all published posts
- **Create Post**: Write new blog posts (when logged in)
- **Edit Post**: Modify your own posts
- **Delete Post**: Remove your posts
- **Search**: Find posts by keywords
- **Categories**: Browse posts by category
- **Profile**: View user profiles and posts
- **Like**: AJAX-powered like/unlike posts
- **Comment**: Add comments to posts

### REST API Endpoints

#### Posts

- `GET /api/posts/` - List all published posts
- `POST /api/posts/` - Create new post (authenticated)
- `GET /api/posts/<id>/` - Retrieve single post
- `PUT /api/posts/<id>/` - Update post (author only)
- `DELETE /api/posts/<id>/` - Delete post (author only)
- `POST /api/posts/<id>/like/` - Toggle like
- `GET /api/posts/trending/` - Get trending posts
- `GET /api/posts/my_posts/` - Get user's posts

#### Comments

- `GET /api/comments/` - List all comments
- `POST /api/comments/` - Create comment (authenticated)
- `GET /api/comments/<id>/` - Retrieve comment
- `PUT /api/comments/<id>/` - Update comment (author only)
- `DELETE /api/comments/<id>/` - Delete comment (author only)

#### Categories

- `GET /api/categories/` - List all categories
- `GET /api/categories/<slug>/` - Retrieve category
- `GET /api/categories/<slug>/posts/` - Get category posts

#### Likes

- `GET /api/likes/` - List all likes
- `POST /api/likes/` - Create like (authenticated)
- `DELETE /api/likes/<id>/` - Delete like

### API Query Parameters

#### Filtering

```
/api/posts/?status=1&category=2&author=3
```

#### Search

```
/api/posts/?search=django
```

#### Ordering

```
/api/posts/?ordering=-created_at
```

#### Pagination

```
/api/posts/?page=2
```

## Configuration

### Settings (.env)

```ini
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
```

### Logging

Logs are written to:

- `logs/blog.log` - Application logs
- `logs/security.log` - Security-related logs
- Console (during development)

### Caching

Default: In-memory cache (LocMemCache)
Production: Redis cache (recommended)

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
    }
}
```

## Authentication

### Session Authentication

- Used by web interface
- Django's built-in session framework
- Session data stored in database

### Permissions

- Anonymous users: Read-only access
- Authenticated users: Create posts and comments
- Authors: Edit/delete their own posts
- Staff: Full admin access

## Services Layer

### PostService

- `get_published_posts()` - Get all published posts
- `get_post_by_slug()` - Get single post with caching
- `search_posts(query)` - Full-text search
- `get_posts_by_category(slug)` - Get category posts
- `create_post()` - Create new post
- `update_post()` - Update existing post
- `delete_post()` - Delete post

### CommentService

- `add_comment()` - Add new comment
- `get_post_comments()` - Get post comments

### LikeService

- `toggle_like()` - Like/unlike post
- `is_liked_by()` - Check like status

## Security Features

- ✅ CSRF Protection
- ✅ SQL Injection Prevention (ORM)
- ✅ XSS Protection
- ✅ Secure session cookies
- ✅ Password hashing (bcrypt)
- ✅ User authentication required for sensitive actions
- ✅ Authorization checks (author-only editing)
- ✅ Rate limiting on API endpoints

## Performance Optimizations

- Database indexes on frequently queried fields
- Query optimization (select_related, prefetch_related)
- Caching layer (posts, user data)
- Pagination for large datasets
- Efficient serializers
- Compressed responses

## Testing

### Run Tests

```bash
python manage.py test blog
```

### Test Files

- `blog/tests/test_models.py` - Model tests
- `blog/tests/test_views.py` - View tests
- `blog/tests/test_api.py` - API endpoint tests

## Deployment

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set secure `SECRET_KEY`
- [ ] Configure static file serving (CDN or whitenoise)
- [ ] Set up database (PostgreSQL recommended)
- [ ] Configure email backend
- [ ] Set up Redis for caching
- [ ] Configure logging
- [ ] Set up SSL/TLS (HTTPS)
- [ ] Configure CORS if needed
- [ ] Set up monitoring and alerting
- [ ] Create database backups

### Using Gunicorn

```bash
gunicorn BlogProject.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Docker

```bash
docker build -t blog-app .
docker run -p 8000:8000 blog-app
```

## Troubleshooting

### Migrations Issues

```bash
# Reset migrations (development only)
python manage.py migrate blog 0001
python manage.py migrate

# Make new migrations
python manage.py makemigrations
```

### Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Database Issues

```bash
# Check database
python manage.py dbshell

# Run migrations again
python manage.py migrate --run-syncdb
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:

- Create an issue on GitHub
- Check existing issues
- Read documentation

## Changelog

### Version 1.0.0

- Initial production release
- REST API implementation
- Category system
- Search functionality
- Comment system
- Like system
- Logging system
- Professional admin interface

## Future Enhancements

- [ ] Email notifications for comments
- [ ] User following system
- [ ] Post recommendations
- [ ] Full-text search with Elasticsearch
- [ ] CDN integration
- [ ] Analytics dashboard
- [ ] Social media sharing
- [ ] Tags system
- [ ] Post scheduling
- [ ] Multi-language support
