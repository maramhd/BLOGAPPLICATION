# 🔐 Social Authentication Setup Guide

## Django Blog Application - Google & Facebook Login Integration

This guide explains how to set up Google and Facebook OAuth login for your Django Blog Application using `django-allauth`.

---

## 📋 Prerequisites

1. Django Blog Application is running
2. `django-allauth` is installed in your virtual environment
3. Admin site configured and running

---

## 🔧 PART 1: Django Configuration (Already Done ✅)

The following configurations are already in place:

### ✅ settings.py - INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ...
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    # ...
]
```

### ✅ settings.py - AUTHENTICATION_BACKENDS

```python
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
```

### ✅ settings.py - SITE_ID

```python
SITE_ID = 1
```

### ✅ urls.py - Allauth URLs

```python
path('accounts/', include('allauth.urls')),
```

---

## 🚀 PART 2: Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"**
3. Enter project name: `Blog Application`
4. Click **"Create"**

### Step 2: Enable Google+ API

1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for **"Google+ API"**
3. Click on it and select **"Enable"**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. If prompted, click **"Configure Consent Screen"** first
4. On the consent screen:
   - Choose **"External"** for User Type
   - Fill in:
     - **App name**: Blog Application
     - **User support email**: your-email@gmail.com
     - **Developer contact**: your-email@gmail.com
5. Click **"Save and Continue"**
6. On Scopes page, click **"Save and Continue"**
7. Click **"Create Credentials"** → **"OAuth client ID"**
8. Select **"Web application"**
9. Under **Authorized redirect URIs**, add:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   http://yourdomain.com/accounts/google/login/callback/  (for production)
   ```
10. Click **"Create"**
11. Copy your **Client ID** and **Client Secret**

### Step 4: Add Google Credentials to Blog Application

1. Open Django Admin: `http://localhost:8000/admin/`
2. Go to **Sites** and ensure:
   - Domain name: `localhost:8000` (for development)
   - Display name: `Blog Application`
3. Go to **Social applications** (under Socialaccount)
4. Click **"Add Social Application"**
5. Fill in:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: (paste your Google Client ID here)
   - **Secret key**: (paste your Google Client Secret here)
   - **Sites**: Select your site
6. Click **"Save"**

### Google OAuth Configuration Summary

```python
# These will be stored in Django admin:
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'YOUR-GOOGLE-CLIENT-ID'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'YOUR-GOOGLE-CLIENT-SECRET'

# ✅ Redirect URI for Google:
# http://localhost:8000/accounts/google/login/callback/
```

---

## 🚀 PART 3: Facebook OAuth Setup

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **"My Apps"** → **"Create App"**
3. Select **"Consumer"** as the app type
4. Fill in:
   - **App Name**: Blog Application
   - **App Email**: your-email@example.com
   - **App Purpose**: Select appropriate category
5. Click **"Create App"**

### Step 2: Add Facebook Login Product

1. In your app dashboard, click **"+ Add Product"**
2. Find **"Facebook Login"** and click **"Set Up"**
3. Select **"Web"** as platform
4. Configure Facebook Login:
   - **Valid OAuth Redirect URIs**:
     ```
     http://127.0.0.1:8000/accounts/facebook/login/callback/
     http://localhost:8000/accounts/facebook/login/callback/
     http://yourdomain.com/accounts/facebook/login/callback/  (production)
     ```
   - Click **"Save Changes"**

### Step 3: Get Facebook Credentials

1. Go to **Settings** → **Basic**
2. Copy:
   - **App ID**
   - **App Secret**

### Step 4: Add Facebook Credentials to Blog Application

1. Open Django Admin: `http://localhost:8000/admin/`
2. Go to **Social applications**
3. Click **"Add Social Application"**
4. Fill in:
   - **Provider**: Facebook
   - **Name**: Facebook OAuth
   - **Client id**: (paste your Facebook App ID here)
   - **Secret key**: (paste your Facebook App Secret here)
   - **Sites**: Select your site
5. Click **"Save"**

### Facebook OAuth Configuration Summary

```python
# These will be stored in Django admin:
SOCIAL_AUTH_FACEBOOK_KEY = 'YOUR-FACEBOOK-APP-ID'
SOCIAL_AUTH_FACEBOOK_SECRET = 'YOUR-FACEBOOK-APP-SECRET'

# ✅ Redirect URI for Facebook:
# http://localhost:8000/accounts/facebook/login/callback/
```

---

## 🎨 PART 4: Update Login Template

Add social login buttons to your login page:

```html
{% extends "base.html" %} {% block content %}
<div class="container mt-5">
  <div class="row justify-content-center">
    <div class="col-md-5">
      <div class="card">
        <div class="card-body">
          <h2 class="card-title mb-4 text-center">Login</h2>

          <!-- Your existing login form here -->
          <form method="post">
            {% csrf_token %}
            <!-- ... -->
          </form>

          <hr class="my-4" />

          <!-- ✅ Social Login Buttons -->
          <h5 class="text-center mb-3">Or login with</h5>

          <a
            href="{% provider_login_url 'google' %}"
            class="btn btn-outline-danger w-100 mb-2"
          >
            <i class="fab fa-google me-2"></i> Google
          </a>

          <a
            href="{% provider_login_url 'facebook' %}"
            class="btn btn-outline-primary w-100"
          >
            <i class="fab fa-facebook me-2"></i> Facebook
          </a>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

Don't forget to load the allauth template tag at the top:

```django
{% load socialaccount %}
```

---

## 🧪 Testing

### Test Google Login

1. Go to your blog homepage
2. Click **"Login"** or navigate to `/accounts/login/`
3. Click **"Login with Google"**
4. You should be redirected to Google's login page
5. After login, you should be redirected back to your blog

### Test Facebook Login

1. Same process but click **"Login with Facebook"**
2. You should be redirected to Facebook's login page
3. After login, you should be redirected back to your blog

---

## 🔧 Troubleshooting

### ❌ "Invalid OAuth Redirect URI"

- **Solution**: Make sure the redirect URI in your OAuth provider exactly matches:
  ```
  http://127.0.0.1:8000/accounts/google/login/callback/
  ```
- Check for trailing slashes and exact domain match

### ❌ "Site matching query does not exist"

- **Solution**: Go to Django admin → Sites → ensure Domain is set to `localhost:8000`

### ❌ "SocialApp matching query does not exist"

- **Solution**: In Django admin → Social applications, make sure the provider is added with correct credentials

### ❌ "Credentials not found" error

- **Solution**: Make sure you've saved the social app in Django admin with both Client ID and Secret

---

## 📝 .env File (Optional - For Production)

```bash
# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-client-id-here
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here

# Facebook OAuth
FACEBOOK_APP_ID=your-app-id-here
FACEBOOK_APP_SECRET=your-app-secret-here

# Email Configuration (for password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

---

## ✅ Production Checklist

- [ ] Update `ALLOWED_HOSTS` in settings.py with your domain
- [ ] Set `DEBUG = False` in production
- [ ] Update redirect URIs in Google and Facebook apps to your production domain
- [ ] Configure SMTP email for production
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Add social app providers with production credentials

---

## 📚 Resources

- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login)

---

**Status**: ✅ Setup complete! Your blog now supports Google and Facebook login.
