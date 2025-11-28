from django.contrib.auth.models import User
from django.conf import settings
from django.utils.timezone import now
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated

from drf_yasg import openapi

from .serializers import RegisterSerializer
from .models import PasswordResetToken


class RegisterView(generics.CreateAPIView):
    """
    API endpoint para registrar un nuevo usuario.
    
    **POST** - Registrar un nuevo usuario
    - Requiere: username, email, password, password2
    - Retorna: usuario creado con id, username, email
    - Status: 201 si es exitoso, 400 si hay error de validación
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Override para añadir manejo de errores mejorado."""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'detail': f'Error en el registro: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint para login y obtener JWT tokens.
    
    **POST** - Obtener access y refresh tokens
    - Requiere: username, password
    - Retorna: { "access": "<token>", "refresh": "<token>" }
    - Status: 200 si es exitoso, 401 si las credenciales son inválidas
    """
    permission_classes = [permissions.AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    """
    API endpoint para refrescar el access token.
    
    **POST** - Obtener nuevo access token usando refresh token
    - Requiere: refresh token en body { "refresh": "<token>" }
    - Retorna: { "access": "<nuevo_token>" }
    - Status: 200 si es exitoso, 401 si el token es inválido
    """
    permission_classes = [IsAuthenticated]


class PasswordResetRequestAPIView(APIView):
    """
    API endpoint para solicitar reinicio de contraseña.
    
    **POST** - Solicitar enlace de reinicio por email
    - Requiere: email del usuario en body { "email": "user@example.com" }
    - Retorna: { "detail": "Si el email existe, recibirás un enlace de reinicio..." }
    - Status: 200 si es exitoso o si el email no existe (por seguridad), 400 si falta email
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email del usuario'),
            },
            required=['email'],
        ),
        responses={
            200: openapi.Response(
                description='Email de reinicio enviado',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(description='Email requerido o inválido'),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Solicita un enlace de reinicio de contraseña para el email proporcionado.
        """
        email = request.data.get('email', '').strip()
        
        if not email:
            return Response(
                {'detail': 'Se requiere el email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            
            # Crear token de reset
            reset_token = PasswordResetToken.create_for_user(user)
            
            # Aquí enviarías un email con el token
            # Por ahora solo retornamos un mensaje seguro
            return Response(
                {'detail': 'Si el email existe en nuestro sistema, recibirás un enlace de reinicio de contraseña.'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            # Retornamos el mismo mensaje por razones de seguridad (no revelar si el usuario existe)
            return Response(
                {'detail': 'Si el email existe en nuestro sistema, recibirás un enlace de reinicio de contraseña.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'detail': f'Error al procesar la solicitud: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordResetConfirmAPIView(APIView):
    """
    API endpoint para confirmar el reinicio de contraseña.
    
    **POST** - Cambiar contraseña usando token de reset
    - Requiere: token, nueva_contraseña, confirmar_contraseña
    - Retorna: { "detail": "Contraseña actualizada exitosamente" }
    - Status: 200 si es exitoso, 400 si hay error
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de reset'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Nueva contraseña'),
                'password2': openapi.Schema(type=openapi.TYPE_STRING, description='Confirmar contraseña'),
            },
            required=['token', 'password', 'password2'],
        ),
        responses={
            200: openapi.Response(description='Contraseña actualizada'),
            400: openapi.Response(description='Token inválido o expirado'),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Confirma el reset de contraseña usando el token.
        """
        token = request.data.get('token', '').strip()
        password = request.data.get('password', '').strip()
        password2 = request.data.get('password2', '').strip()
        
        # Validar que todos los campos estén presentes
        if not token or not password or not password2:
            return Response(
                {'detail': 'Token, contraseña y confirmar contraseña son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que las contraseñas coincidan
        if password != password2:
            return Response(
                {'detail': 'Las contraseñas no coinciden.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar longitud mínima
        if len(password) < 8:
            return Response(
                {'detail': 'La contraseña debe tener al menos 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Buscar el token
            reset_token = PasswordResetToken.objects.get(token=token)
            
            # Validar que el token sea válido
            if not reset_token.is_valid():
                return Response(
                    {'detail': 'El token ha expirado o ya ha sido utilizado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Actualizar contraseña del usuario
            user = reset_token.user
            user.set_password(password)
            user.save()
            
            # Marcar token como usado
            reset_token.used = True
            reset_token.used_at = now()
            reset_token.save()
            
            return Response(
                {'detail': 'Contraseña actualizada exitosamente.'},
                status=status.HTTP_200_OK
            )
            
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'detail': 'Token inválido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'detail': f'Error al actualizar la contraseña: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Mantener el endpoint antiguo para compatibilidad
class PasswordResetAPIView(PasswordResetRequestAPIView):
    """Alias para compatibilidad con versiones anteriores."""
    pass
