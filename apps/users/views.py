"""
Autenticación personalizada

Sistema de autenticación con dos métodos:
1. Google OAuth (para admins)
2. Credenciales phone/password (para clientes)
"""
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from apps.users.models import Role
import os

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """Login con username (phone1) y password"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginView(APIView):
    """
    Login con credenciales (para clientes)
    
    POST /api/auth/login/
    {
        "username": "3123456789",  // phone1
        "password": "31234567891990"  // phone1 + birth_year
    }
    """
    permission_classes = []
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que sea cliente
        if not user.has_role(Role.CLIENTE):
            return Response({
                'error': 'Este método de autenticación es solo para clientes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'roles': user.get_roles()
            }
        })


class GoogleLoginSerializer(serializers.Serializer):
    """Login con Google token"""
    id_token = serializers.CharField()


class GoogleLoginView(APIView):
    """
    Login con Google (para admins)
    
    POST /api/auth/google/
    {
        "id_token": "eyJhbGciOi..."  // Token de Google
    }
    
    Solo permite emails configurados en ADMIN_EMAILS del .env
    """
    permission_classes = []
    
    def post(self, request):
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        serializer = GoogleLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['id_token']
        
        try:
            # Verificar el token con Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                settings.GOOGLE_OAUTH_CLIENT_ID
            )
            
            # Extraer información
            email = idinfo['email']
            google_id = idinfo['sub']
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            
            # Verificar que el email esté en la lista de admins permitidos
            allowed_admin_emails = os.getenv('ADMIN_EMAILS', '').split(',')
            allowed_admin_emails = [e.strip() for e in allowed_admin_emails if e.strip()]
            
            if email not in allowed_admin_emails:
                return Response({
                    'error': 'Este email no está autorizado como administrador'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Buscar o crear el usuario
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'name': name,
                    'google_id': google_id,
                    'profile_picture': picture
                }
            )
            
            # Actualizar datos si ya existía
            if not created:
                user.name = name
                user.google_id = google_id
                user.profile_picture = picture
                user.save()
            
            # Asignar rol admin si no lo tiene
            admin_role, _ = Role.objects.get_or_create(name=Role.ADMIN)
            if not user.has_role(Role.ADMIN):
                from apps.users.models import UserRole
                UserRole.objects.create(user=user, role=admin_role)
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'picture': user.profile_picture,
                    'roles': user.get_roles()
                }
            })
            
        except ValueError as e:
            print(f"Error verificando token de Google: {e}")
            print("client id", os.getenv('GOOGLE_OAUTH_CLIENT_ID'))
            return Response({
                'error': 'Token de Google inválido'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Logout (blacklist del refresh token)
    
    POST /api/auth/logout/
    {
        "refresh": "eyJhbGciOi..."
    }
    """
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout exitoso'})
        except Exception:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
