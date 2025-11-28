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
   
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
       
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'detail': f'Error en el registro: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomTokenObtainPairView(TokenObtainPairView):
   
  
    permission_classes = [IsAuthenticated]


class CustomTokenRefreshView(TokenRefreshView):
    
    
   
    permission_classes = [IsAuthenticated]


class PasswordResetRequestAPIView(APIView):

    permission_classes = [permissions.AllowAny]

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

        email = request.data.get('email', '').strip()
        
        if not email:
            return Response(
                {'detail': 'Se requiere el email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
            
            
            reset_token = PasswordResetToken.create_for_user(user)
            
            
            return Response(
                {'detail': 'Si el email existe en nuestro sistema, recibirás un enlace de reinicio de contraseña.'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            
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
        
        token = request.data.get('token', '').strip()
        password = request.data.get('password', '').strip()
        password2 = request.data.get('password2', '').strip()
        
        
        if not token or not password or not password2:
            return Response(
                {'detail': 'Token, contraseña y confirmar contraseña son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
        if password != password2:
            return Response(
                {'detail': 'Las contraseñas no coinciden.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
        if len(password) < 8:
            return Response(
                {'detail': 'La contraseña debe tener al menos 8 caracteres.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            
            reset_token = PasswordResetToken.objects.get(token=token)
            
            
            if not reset_token.is_valid():
                return Response(
                    {'detail': 'El token ha expirado o ya ha sido utilizado.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            
            user = reset_token.user
            user.set_password(password)
            user.save()
            
            
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



class PasswordResetAPIView(PasswordResetRequestAPIView):
    
    pass
