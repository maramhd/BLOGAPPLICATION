"""
URL configuration for blog app.
"""

from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check_view, name='health_check'),
    
    # Home & Listing
    path('', views.PostListView.as_view(), name='home'),
    
    # Post CRUD
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Search & Categories
    path('search/', views.PostSearchView.as_view(), name='post_search'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profiles
     path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    path('profile/<str:username>/', views.profile_view, name='profile'),
    
    # API/AJAX
    path('post/<slug:slug>/like/', views.toggle_like_view, name='toggle_like'),
]
