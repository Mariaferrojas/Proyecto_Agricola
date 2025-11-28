from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import json
from .models import PasswordResetToken


class AuthenticationTestCase(TestCase):
   
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

    def test_register_success(self):
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
        data = {
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        data = {
            'username': 'nonexistent',
            'password': 'securepass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post('/api/auth/login/', login_data, format='json')
        refresh_token = login_response.data['refresh']

        
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/auth/token/refresh/', refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_verify_valid(self):
       
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post('/api/auth/login/', login_data, format='json')
        access_token = login_response.data['access']

       
        verify_data = {'token': access_token}
        response = self.client.post('/api/auth/token/verify/', verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_verify_invalid(self):
       
        verify_data = {'token': 'invalid.token.here'}
        response = self.client.post('/api/auth/token/verify/', verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_valid_email(self):
        
        data = {'email': 'testuser@example.com'}
        response = self.client.post('/api/auth/password-reset/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
       
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())

    def test_password_reset_invalid_email(self):
        
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post('/api/auth/password-reset/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_missing_email(self):
        data = {}
        response = self.client.post('/api/auth/password-reset/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_protected_endpoint_with_token(self):

        
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post('/api/auth/login/', login_data, format='json')
        access_token = login_response.data['access']

        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/token/verify/', format='json')
       

    def test_access_protected_endpoint_without_token(self):
       
        response = self.client.post('/api/auth/token/verify/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_success(self):
      
        reset_token = PasswordResetToken.create_for_user(self.user)
        
        
        data = {
            'token': reset_token.token,
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post('/api/auth/password-reset/confirm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
       
        reset_token.refresh_from_db()
        self.assertTrue(reset_token.used)
        
      
        login_data = {
            'username': 'testuser',
            'password': 'newpassword123'
        }
        login_response = self.client.post('/api/auth/login/', login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_invalid_token(self):
       
        data = {
            'token': 'invalid_token_12345',
            'password': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post('/api/auth/password-reset/confirm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_password_mismatch(self):
       
        reset_token = PasswordResetToken.create_for_user(self.user)
        
        data = {
            'token': reset_token.token,
            'password': 'newpassword123',
            'password2': 'differentpassword123'
        }
        response = self.client.post('/api/auth/password-reset/confirm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
