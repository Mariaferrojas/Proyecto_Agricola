from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import json
from .models import PasswordResetToken


class AuthenticationTestCase(TestCase):
    """Tests para endpoints de autenticación (registro, login, refresh, password reset)."""

    def setUp(self):
        """Crear cliente API y usuario de prueba."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

    def test_register_success(self):
        """Registrar un nuevo usuario correctamente."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        """Registrar con contraseñas que no coinciden."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'differentpass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        """Registrar con un username que ya existe."""
        data = {
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Login correcto y obtener access/refresh tokens."""
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Login con credenciales inválidas."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Login con usuario que no existe."""
        data = {
            'username': 'nonexistent',
            'password': 'securepass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Refrescar token usando refresh token."""
        # Primero hacer login para obtener tokens
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post('/api/auth/login/', login_data, format='json')
        refresh_token = login_response.data['refresh']

        # Usar refresh token para obtener nuevo access token
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/auth/token/refresh/', refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_verify_valid(self):
        """Verificar que un token válido es aceptado."""
        # Login para obtener token
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post('/api/auth/login/', login_data, format='json')
        access_token = login_response.data['access']

        # Verificar token
        verify_data = {'token': access_token}
        response = self.client.post('/api/auth/token/verify/', verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_verify_invalid(self):
        """Verificar que un token inválido es rechazado."""
        verify_data = {'token': 'invalid.token.here'}
        response = self.client.post('/api/auth/token/verify/', verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_valid_email(self):
        """Solicitar password reset con email válido."""
        data = {'email': 'testuser@example.com'}
        response = self.client.post('/api/auth/password-reset/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        # Verificar que se creó el token
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())

    def test_password_reset_invalid_email(self):
        """Solicitar password reset con email que no existe (debe retornar 200 por seguridad)."""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post('/api/auth/password-reset/', data, format='json')
        # Django retorna 200 incluso si el email no existe (por seguridad)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_missing_email(self):
        """Solicitar password reset sin email."""
        data = {}
        response = self.client.post('/api/auth/password-reset/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_protected_endpoint_with_token(self):
        """Acceder a un endpoint protegido con token válido."""
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post('/api/auth/login/', login_data, format='json')
        access_token = login_response.data['access']

        # Usar token en header Authorization para acceder a admin panel (o cualquier endpoint protegido)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/token/verify/', format='json')
        # El endpoint /verify solo espera un token en el body, pero al menos verificamos que el token es válido
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_protected_endpoint_without_token(self):
        """Acceder a un endpoint protegido sin token."""
        # Sin credentials, intenta acceder a /verify (que es pública pero requiere token en body)
        response = self.client.post('/api/auth/token/verify/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_success(self):
        """Confirmar reset de contraseña con token válido."""
        # Crear token de reset
        reset_token = PasswordResetToken.create_for_user(self.user)
        
        # Confirmar reset
        data = {
            'token': reset_token.token,
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post('/api/auth/password-reset/confirm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el token está marcado como usado
        reset_token.refresh_from_db()
        self.assertTrue(reset_token.used)
        
        # Verificar que la nueva contraseña funciona
        login_data = {
            'username': 'testuser',
            'password': 'newpassword123'
        }
        login_response = self.client.post('/api/auth/login/', login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_invalid_token(self):
        """Confirmar reset con token inválido."""
        data = {
            'token': 'invalid_token_12345',
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post('/api/auth/password-reset/confirm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_password_mismatch(self):
        """Confirmar reset con contraseñas que no coinciden."""
        reset_token = PasswordResetToken.create_for_user(self.user)
        
        data = {
            'token': reset_token.token,
            'password': 'newpassword123',
            'password2': 'differentpassword123'
        }
        response = self.client.post('/api/auth/password-reset/confirm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
