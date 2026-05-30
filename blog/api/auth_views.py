"""
 DRF Authentication Views - User Registration and Login
تطبيق المصادقة في API - تسجيل المستخدمين والدخول
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from ..serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserRegisterView(APIView):
    """
     تسجيل مستخدم جديد عبر API
    (User registration endpoint)
    
    POST /api/auth/register/
    {
        "username": "user123",
        "email": "user@example.com",
        "password": "securepass123",
        "password2": "securepass123"
    }
    """
    
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            password2 = data.get('password2')
            
            # التحقق من البيانات (Validate data)
            if not username or not email or not password or not password2:
                return Response(
                    {'error': 'All fields are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if password != password2:
                return Response(
                    {'error': 'Passwords do not match'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(password) < 8:
                return Response(
                    {'error': 'Password must be at least 8 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # التحقق من وجود المستخدم (Check if user exists)
            if User.objects.filter(username=username).exists():
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if User.objects.filter(email=email).exists():
                return Response(
                    {'error': 'Email already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # إنشاء المستخدم الجديد (Create new user)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # إنشاء Token للمستخدم (Create token for user)
            token, created = Token.objects.get_or_create(user=user)
            
            # إنشاء JWT tokens (Create JWT tokens)
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"New user registered via API: {username}")
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLoginView(APIView):
    """
    تسجيل الدخول عبر API
    (User login endpoint)
    
    POST /api/auth/login/
    {
        "username": "user123",
        "password": "securepass123"
    }
    """
    
    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')
            
            # التحقق من البيانات (Validate data)
            if not username or not password:
                return Response(
                    {'error': 'Username and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # المصادقة (Authenticate user)
            user = authenticate(username=username, password=password)
            
            if not user:
                logger.warning(f"Login attempt failed for username: {username}")
                return Response(
                    {'error': 'Invalid username or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # الحصول على Token (Get or create token)
            token, created = Token.objects.get_or_create(user=user)
            
            # إنشاء JWT tokens (Create JWT tokens)
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"User logged in via API: {username}")
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
def logout_view(request):
    """
   تسجيل الخروج عبر API
    (User logout endpoint - invalidate token)
    
    POST /api/auth/logout/
    """
    try:
        # حذف الـ token (Delete token)
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        
        logger.info(f"User logged out via API: {request.user.username}")
        
        return Response(
            {'message': 'Logout successful'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
