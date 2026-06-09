# Blog Application

A full-featured blog platform built with Django and Django REST Framework, featuring JWT authentication, REST API, caching with Redis, and Docker containerization.

---

## Features

### Core Features

- User registration and authentication (Session + Token + JWT)
- Create, read, update, and delete blog posts
- Comment system with moderation
- Like/unlike posts
- Category-based post organization
- Full-text search
- User profiles

### Technical Features

- RESTful API (DRF) with full CRUD operations
- JWT Authentication (access + refresh tokens)
- Token Authentication (DRF built-in)
- Session Authentication (browsable API)
- Redis caching for performance
- Pagination, filtering, and search
- Rate limiting (throttling)
- Custom permission classes
- Health check endpoint
- Comprehensive logging

### DevOps Features

- Docker multi-stage build (optimized image size)
- Docker Compose with 3 services (API, Nginx, Redis)
- Nginx reverse proxy
- Gunicorn WSGI server
- Automated database migrations
- Health checks for all services

---

## Project Structure

```
BlogApplication/
├── BlogProject/              # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Main settings (JWT, DRF, Cache, etc.)
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── blog/                     # Main blog app
│   ├── api/                  # REST API module
│   │   ├── __init__.py
│   │   ├── auth_views.py     # Registration & Login endpoints
│   │   ├── urls.py           # API URL routing
│   │   └── viewsets.py       # DRF ViewSets (Post, Comment, Category, Like)
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py              # Django forms
│   ├── models.py             # Database models (Post, Comment, Like, Category)
│   ├── permissions.py        # Custom DRF permissions
│   ├── serializers.py        # DRF serializers
│   ├── services.py           # Business logic layer
│   ├── urls.py               # App URL routing
│   └── views.py              # Class-based and function-based views
├── templates/                # HTML templates
│   ├── base.html             # Base layout
│   ├── index.html            # Homepage with post feed
│   ├── post_detail.html      # Single post view
│   ├── post_form.html        # Create/Edit post
│   ├── post_search.html      # Search results
│   ├── profile.html          # User profile
│   ├── profile_edit.html     # Edit profile
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── category_list.html    # All categories
│   ├── category_detail.html  # Posts by category
│   ├── 404.html              # Not found page
│   ├── 500.html              # Server error page
│   ├── password_reset*.html  # Password reset flow
│   └── sidebar.html          # Sidebar partial
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User uploaded files
├── staticfiles/              # Collected static files
├── nginx/                    # Nginx configuration
│   ├── Dockerfile
│   └── nginx.conf
├── .env                      # Environment variables
├── .gitignore
├── .dockerignore
├── db.sqlite3                # SQLite database
├── Dockerfile                # API Docker image
├── docker-compose.yml        # Docker Compose services
├── docker-entrypoint.sh      # Container entrypoint script
├── manage.py                 # Django management command
├── pyproject.toml            # Project metadata
├── poetry.lock               # Poetry lock file
└── requirements.txt          # Python dependencies
```

---

## Models

### Category

| Field      | Type      | Description            |
| ---------- | --------- | ---------------------- |
| name       | CharField | Category name (unique) |
| slug       | SlugField | URL-friendly slug      |
| created_at | DateTime  | Auto-created           |

### Post

| Field      | Type         | Description                   |
| ---------- | ------------ | ----------------------------- |
| title      | CharField    | Post title (unique)           |
| slug       | SlugField    | URL-friendly slug             |
| author     | ForeignKey   | Link to User                  |
| category   | ForeignKey   | Link to Category (optional)   |
| content    | TextField    | Full post content             |
| excerpt    | TextField    | Brief summary (max 500 chars) |
| image      | ImageField   | Featured image (optional)     |
| status     | IntegerField | Draft (0) or Published (1)    |
| created_at | DateTime     | Auto-created                  |
| updated_at | DateTime     | Auto-updated                  |

### Comment

| Field      | Type         | Description     |
| ---------- | ------------ | --------------- |
| post       | ForeignKey   | Link to Post    |
| author     | ForeignKey   | Link to User    |
| content    | TextField    | Comment text    |
| active     | BooleanField | moderation flag |
| created_at | DateTime     | Auto-created    |

### Like

| Field      | Type       | Description  |
| ---------- | ---------- | ------------ |
| post       | ForeignKey | Link to Post |
| user       | ForeignKey | Link to User |
| created_at | DateTime   | Auto-created |

---

## API Endpoints

### Authentication

| Method | Endpoint                   | Description              | Auth Required |
| ------ | -------------------------- | ------------------------ | ------------- |
| POST   | `/api/auth/register/`      | Register new user        | No            |
| POST   | `/api/auth/login/`         | Login and get tokens     | No            |
| POST   | `/api/auth/token/`         | Get JWT access/refresh   | No            |
| POST   | `/api/auth/token/refresh/` | Refresh JWT access token | No            |
| POST   | `/api/auth/logout/`        | Invalidate token         | Yes           |

### Posts

| Method | Endpoint                    | Description              | Auth Required |
| ------ | --------------------------- | ------------------------ | ------------- |
| GET    | `/api/posts/`               | List published posts     | No            |
| POST   | `/api/posts/`               | Create new post          | Yes           |
| GET    | `/api/posts/<id>/`          | Retrieve single post     | No            |
| PUT    | `/api/posts/<id>/`          | Update post (author)     | Yes           |
| DELETE | `/api/posts/<id>/`          | Delete post (author)     | Yes           |
| POST   | `/api/posts/<id>/like/`     | Toggle like              | Yes           |
| GET    | `/api/posts/<id>/comments/` | Get post comments        | No            |
| GET    | `/api/posts/trending/`      | Get trending posts       | No            |
| GET    | `/api/posts/my_posts/`      | Get current user's posts | Yes           |

### Comments

| Method | Endpoint              | Description             | Auth Required |
| ------ | --------------------- | ----------------------- | ------------- |
| GET    | `/api/comments/`      | List comments           | No            |
| POST   | `/api/comments/`      | Create comment          | Yes           |
| PUT    | `/api/comments/<id>/` | Update comment (author) | Yes           |
| DELETE | `/api/comments/<id>/` | Delete comment (author) | Yes           |

### Categories

| Method | Endpoint                        | Description           | Auth Required |
| ------ | ------------------------------- | --------------------- | ------------- |
| GET    | `/api/categories/`              | List categories       | No            |
| GET    | `/api/categories/<slug>/`       | Get category detail   | No            |
| GET    | `/api/categories/<slug>/posts/` | Get posts in category | No            |

---

## Getting Started

### Prerequisites

- Python 3.12+
- pip
- Docker & Docker Compose (optional)

---

### Option 1: Run Locally (Development)

#### 1. Clone the repository

```bash
git clone https://github.com/maramhd/BLOGAPPLICATION.git
cd BlogApplication
```

#### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set up environment variables

Edit the `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### 5. Run database migrations

```bash
python manage.py migrate
```

#### 6. Create a superuser (admin account)

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

#### 7. Collect static files

```bash
python manage.py collectstatic --noinput
```

#### 8. Run the development server

```bash
python manage.py runserver
```

#### 9. Open in browser

- **Homepage:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Root:** http://127.0.0.1:8000/api/
- **Health Check:** http://127.0.0.1:8000/health/

---

### Option 2: Run with Docker (Recommended for Production)

#### 1. Clone the repository

```bash
git clone https://github.com/maramhd/BLOGAPPLICATION.git
cd BlogApplication
```

#### 2. Edit .env file

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,api,blog_api
CREATE_SUPERUSER=false
```

#### 3. Build and start containers

```bash
docker compose up -d --build
```

#### 4. Verify all services are running

```bash
docker compose ps
```

Expected output:

```
NAME         IMAGE                   STATUS          PORTS
blog_api     blogapplication-api     healthy         0.0.0.0:8000->8000/tcp
blog_nginx   blogapplication-nginx   healthy         0.0.0.0:81->80/tcp
blog_redis   redis:7-alpine          healthy         0.0.0.0:6380->6379/tcp
```

#### 5. Open in browser

- **Homepage (via Nginx):** http://localhost:81
- **Admin Panel:** http://localhost:81/admin/
- **API Root:** http://localhost:81/api/
- **API (direct):** http://localhost:8000/api/
- **Health Check:** http://localhost:81/health/

#### 6. Create a superuser inside Docker

```bash
docker compose exec api python manage.py createsuperuser
```

#### Useful Docker Commands

```bash
# View logs
docker compose logs api
docker compose logs nginx
docker compose logs -f          # Follow all logs

# Restart a specific service
docker compose restart api

# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v

# Rebuild after code changes
docker compose up -d --build

# Run Django management commands
docker compose exec api python manage.py migrate
docker compose exec api python manage.py collectstatic --noinput
docker compose exec api python manage.py createsuperuser
```

---

## Environment Variables

| Variable                | Default                          | Description                 |
| ----------------------- | -------------------------------- | --------------------------- |
| `SECRET_KEY`            | (insecure default)               | Django secret key           |
| `DEBUG`                 | `True`                           | Debug mode (True/False)     |
| `ALLOWED_HOSTS`         | `localhost,127.0.0.1,testserver` | Comma-separated hostnames   |
| `REDIS_URL`             | `redis://redis:6379/0`           | Redis connection URL        |
| `EMAIL_BACKEND`         | `console.EmailBackend`           | Email backend for dev       |
| `EMAIL_HOST`            | `smtp.gmail.com`                 | SMTP server host            |
| `EMAIL_PORT`            | `587`                            | SMTP server port            |
| `EMAIL_USE_TLS`         | `True`                           | Use TLS for email           |
| `EMAIL_HOST_USER`       | (empty)                          | SMTP username               |
| `EMAIL_HOST_PASSWORD`   | (empty)                          | SMTP password               |
| `DEFAULT_FROM_EMAIL`    | `noreply@blog.com`               | Default from email address  |
| `SECURE_SSL_REDIRECT`   | `False`                          | Redirect HTTP to HTTPS      |
| `SESSION_COOKIE_SECURE` | `False`                          | Secure session cookies      |
| `CSRF_COOKIE_SECURE`    | `False`                          | Secure CSRF cookies         |
| `CREATE_SUPERUSER`      | `false`                          | Auto-create admin in Docker |
| `ENVIRONMENT`           | `production`                     | Environment name            |

---

## Authentication

The application supports three authentication methods:

### 1. JWT Authentication (Recommended for APIs)

```bash
# Get access and refresh tokens
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "youruser", "password": "yourpass"}'

# Response:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
# }

# Use the access token in requests
curl http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer eyJ0eXAi..."

# Refresh an expired access token
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAi..."}'
```

### 2. Token Authentication

```bash
# Register and get token
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "user@example.com", "password": "pass1234", "password2": "pass1234"}'

# Use the token
curl http://localhost:8000/api/posts/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### 3. Session Authentication (Browsable API)

Open http://localhost:8000/api/ in a browser and use the login form.

---

## Technology Stack

| Layer          | Technology                         |
| -------------- | ---------------------------------- |
| **Backend**    | Django 5.2 + Django REST Framework |
| **Auth**       | JWT (SimpleJWT) + Token + Session  |
| **Database**   | SQLite (development)               |
| **Cache**      | Redis 7                            |
| **Web Server** | Nginx 1.25 (reverse proxy)         |
| **WSGI**       | Gunicorn 21.2                      |
| **Container**  | Docker + Docker Compose            |
| **Language**   | Python 3.12                        |

---

## License

This project is for educational purposes it's made By Maram Alhaddad
