#!/usr/bin/env python
"""
Script de prueba para los endpoints de autenticación JWT.
Uso: python test_auth_endpoints.py
"""

import os
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# URL base de la API
BASE_URL = 'http://127.0.0.1:8000/api/auth'

def print_section(title):
    """Imprimir una sección del test."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_response(response, title="Respuesta"):
    """Imprimir respuesta HTTP formateada."""
    print(f"{title}:")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response Body: {response.text}")
    print()

def test_registration():
    """Prueba 1: Registrar un nuevo usuario."""
    print_section("PRUEBA 1: REGISTRO DE USUARIO")
    
    # Limpiar si el usuario ya existe
    User.objects.filter(username='testuser123').delete()
    
    data = {
        'username': 'testuser123',
        'email': 'testuser123@example.com',
        'password': 'SecurePassword123!',
        'password2': 'SecurePassword123!'
    }
    
    print(f"POST {BASE_URL}/register/")
    print(f"Payload: {json.dumps(data, indent=2)}\n")
    
    response = requests.post(f'{BASE_URL}/register/', json=data)
    print_response(response, "Respuesta de Registro")
    
    if response.status_code == 201:
        print("✓ ÉXITO: Usuario registrado correctamente")
        return True
    else:
        print("✗ ERROR: No se pudo registrar el usuario")
        return False

def test_registration_password_mismatch():
    """Prueba 1b: Registrar con contraseñas diferentes."""
    print_section("PRUEBA 1B: REGISTRO CON CONTRASEÑAS DIFERENTES")
    
    User.objects.filter(username='badpass').delete()
    
    data = {
        'username': 'badpass',
        'email': 'badpass@example.com',
        'password': 'SecurePassword123!',
        'password2': 'DifferentPassword123!'
    }
    
    print(f"POST {BASE_URL}/register/")
    print(f"Payload: {json.dumps(data, indent=2)}\n")
    
    response = requests.post(f'{BASE_URL}/register/', json=data)
    print_response(response, "Respuesta de Registro")
    
    if response.status_code == 400:
        print("✓ ÉXITO: Sistema rechazó contraseñas no coincidentes")
        return True
    else:
        print("✗ ERROR: Debería haber rechazado las contraseñas")
        return False

def test_login():
    """Prueba 2: Login y obtener tokens JWT."""
    print_section("PRUEBA 2: LOGIN Y OBTENER TOKENS JWT")
    
    data = {
        'username': 'testuser123',
        'password': 'SecurePassword123!'
    }
    
    print(f"POST {BASE_URL}/login/")
    print(f"Payload: {json.dumps(data, indent=2)}\n")
    
    response = requests.post(f'{BASE_URL}/login/', json=data)
    print_response(response, "Respuesta de Login")
    
    if response.status_code == 200 and 'access' in response.json():
        print("✓ ÉXITO: Tokens obtenidos correctamente")
        return response.json()
    else:
        print("✗ ERROR: No se obtuvieron los tokens")
        return None

def test_login_invalid():
    """Prueba 2b: Login con credenciales inválidas."""
    print_section("PRUEBA 2B: LOGIN CON CREDENCIALES INVÁLIDAS")
    
    data = {
        'username': 'testuser123',
        'password': 'WrongPassword123!'
    }
    
    print(f"POST {BASE_URL}/login/")
    print(f"Payload: {json.dumps(data, indent=2)}\n")
    
    response = requests.post(f'{BASE_URL}/login/', json=data)
    print_response(response, "Respuesta de Login")
    
    if response.status_code == 401:
        print("✓ ÉXITO: Sistema rechazó credenciales inválidas")
        return True
    else:
        print("✗ ERROR: Debería haber rechazado las credenciales")
        return False

def test_token_verify(access_token):
    """Prueba 3: Verificar token JWT."""
    print_section("PRUEBA 3: VERIFICAR TOKEN JWT")
    
    data = {'token': access_token}
    
    print(f"POST {BASE_URL}/token/verify/")
    print(f"Payload: {{'token': '<token_aqui>'}}\n")
    
    response = requests.post(f'{BASE_URL}/token/verify/', json=data)
    print_response(response, "Respuesta de Verificación")
    
    if response.status_code == 200:
        print("✓ ÉXITO: Token verificado correctamente")
        return True
    else:
        print("✗ ERROR: Token inválido")
        return False

def test_token_refresh(refresh_token):
    """Prueba 4: Refrescar token JWT."""
    print_section("PRUEBA 4: REFRESCAR TOKEN JWT")
    
    data = {'refresh': refresh_token}
    
    print(f"POST {BASE_URL}/token/refresh/")
    print(f"Payload: {{'refresh': '<refresh_token_aqui>'}}\n")
    
    response = requests.post(f'{BASE_URL}/token/refresh/', json=data)
    print_response(response, "Respuesta de Refresh")
    
    if response.status_code == 200 and 'access' in response.json():
        print("✓ ÉXITO: Nuevo access token obtenido")
        return response.json()['access']
    else:
        print("✗ ERROR: No se pudo refrescar el token")
        return None

def test_password_reset():
    """Prueba 5: Solicitar reinicio de contraseña."""
    print_section("PRUEBA 5: SOLICITAR REINICIO DE CONTRASEÑA")
    
    data = {'email': 'testuser123@example.com'}
    
    print(f"POST {BASE_URL}/password-reset/")
    print(f"Payload: {json.dumps(data, indent=2)}\n")
    
    response = requests.post(f'{BASE_URL}/password-reset/', json=data)
    print_response(response, "Respuesta de Password Reset")
    
    if response.status_code == 200:
        print("✓ ÉXITO: Solicitud de reinicio procesada")
        return True
    else:
        print("✗ ERROR: No se procesó la solicitud")
        return False

def test_password_reset_missing_email():
    """Prueba 5b: Password reset sin email."""
    print_section("PRUEBA 5B: PASSWORD RESET SIN EMAIL")
    
    data = {}
    
    print(f"POST {BASE_URL}/password-reset/")
    print(f"Payload: {json.dumps(data, indent=2)}\n")
    
    response = requests.post(f'{BASE_URL}/password-reset/', json=data)
    print_response(response, "Respuesta de Password Reset")
    
    if response.status_code == 400:
        print("✓ ÉXITO: Sistema rechazó solicitud sin email")
        return True
    else:
        print("✗ ERROR: Debería haber rechazado la solicitud")
        return False

def main():
    """Ejecutar todas las pruebas."""
    print("\n" + "="*60)
    print("  PRUEBAS DE AUTENTICACIÓN JWT - PROYECTO AGRÍCOLA")
    print("="*60)
    print(f"\nURL Base: {BASE_URL}")
    print(f"Servidor: http://127.0.0.1:8000\n")
    
    results = []
    
    # Ejecutar pruebas
    results.append(("Registro exitoso", test_registration()))
    results.append(("Registro con contraseñas diferentes", test_registration_password_mismatch()))
    results.append(("Login exitoso", test_login() is not None))
    results.append(("Login con credenciales inválidas", test_login_invalid()))
    
    # Login para obtener tokens
    tokens = test_login()
    if tokens:
        results.append(("Verificar token JWT", test_token_verify(tokens['access'])))
        results.append(("Refrescar token JWT", test_token_refresh(tokens['refresh']) is not None))
    
    results.append(("Password reset", test_password_reset()))
    results.append(("Password reset sin email", test_password_reset_missing_email()))
    
    # Resumen
    print_section("RESUMEN DE RESULTADOS")
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for test_name, result in results:
        status_str = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{status_str}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} pruebas pasadas")
    
    if failed == 0:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print(f"\n⚠️  {failed} pruebas fallaron")

if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: No se puede conectar al servidor.")
        print("Asegúrate de que el servidor está levantado:")
        print("  python manage.py runserver")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
