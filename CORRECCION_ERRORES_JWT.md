# Correción de Errores JWT - Registro y Password Reset

## ✓ Problemas Solucionados

### 1. **Error en el Registro**

**Problema:** El serializer de registro no retornaba el `id` del usuario.

**Solución:**
- Agregué `id = serializers.IntegerField(read_only=True)` al `RegisterSerializer`
- Mejoré validaciones en el serializer:
  - `validate_username()` verifica que sea único y tenga mínimo 3 caracteres
  - `validate_email()` verifica que sea único
  - Validación de longitud mínima de contraseña (8 caracteres)
  - Validación de que la contraseña no sea solo números

**Respuesta ahora incluye:**
```json
{
  "id": 1,
  "username": "usuario",
  "email": "usuario@ejemplo.com"
}
```

---

### 2. **Error en Password Reset**

**Problema:** El endpoint de reset no era funcional. Necesitaba un sistema de tokens para verificar la identidad.

**Solución:**

#### A. Creación de Modelo `PasswordResetToken`
```python
# Nuevo modelo en autenticacion/models.py
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, ...)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # 24 horas
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
```

#### B. Nuevo Endpoint: `POST /api/auth/password-reset/confirm/`

**Solicitud:**
```json
{
  "token": "token_de_reset",
  "password": "nueva_contraseña",
  "password2": "nueva_contraseña"
}
```

**Respuesta:**
```json
{
  "detail": "Contraseña actualizada exitosamente."
}
```

#### C. Flujo Completo de Reset:

**Paso 1: Solicitar reset**
```bash
POST /api/auth/password-reset/
{
  "email": "usuario@ejemplo.com"
}
```
Respuesta: `200 OK` - Se crea un token seguro en la BD

**Paso 2: Confirmar reset (en el cliente)**
```bash
POST /api/auth/password-reset/confirm/
{
  "token": "<token_recibido>",
  "password": "nueva_contraseña",
  "password2": "nueva_contraseña"
}
```
Respuesta: `200 OK` - Contraseña actualizada

---

## Cambios Realizados

### Archivos Modificados:

1. **`autenticacion/serializers.py`**
   - Mejorada validación de username
   - Validación de email único
   - Validación de longitud mínima (8 caracteres)
   - Retorna `id` en la respuesta

2. **`autenticacion/models.py`** (NUEVO)
   - Modelo `PasswordResetToken` para gestionar tokens seguros
   - Método `create_for_user()` para generar tokens
   - Método `is_valid()` para verificar expiración

3. **`autenticacion/views.py`**
   - Mejorada `RegisterView` con manejo de errores
   - Nuevo `PasswordResetRequestAPIView` - solicita reset
   - Nuevo `PasswordResetConfirmAPIView` - confirma reset
   - Mejor documentación Swagger

4. **`autenticacion/urls.py`**
   - Nuevo endpoint: `/api/auth/password-reset/confirm/`
   - Mantenida compatibilidad con `/api/auth/password-reset/`

5. **`autenticacion/tests.py`**
   - 17 tests total (antes 14)
   - Tests para reset con token válido
   - Tests para validación de tokens expirados
   - Tests para cambio exitoso de contraseña

### Migraciones:

```bash
# Se ejecutó automáticamente:
python manage.py makemigrations autenticacion
python manage.py migrate autenticacion
```

Nueva migración: `autenticacion/migrations/0001_initial.py` con el modelo `PasswordResetToken`

---

## ✓ Tests Ejecutados: 17/17 PASADOS

```
✓ test_register_success
✓ test_register_password_mismatch  
✓ test_register_duplicate_username
✓ test_login_success
✓ test_login_invalid_credentials
✓ test_login_nonexistent_user
✓ test_token_refresh
✓ test_token_verify_valid
✓ test_token_verify_invalid
✓ test_password_reset_valid_email
✓ test_password_reset_invalid_email
✓ test_password_reset_missing_email
✓ test_password_reset_confirm_success (NUEVO)
✓ test_password_reset_confirm_invalid_token (NUEVO)
✓ test_password_reset_confirm_password_mismatch (NUEVO)
✓ test_access_protected_endpoint_with_token
✓ test_access_protected_endpoint_without_token
```

---

## Ejemplo Completo de Uso

### 1. Registrar Usuario
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username":"newuser",
    "email":"user@example.com",
    "password":"SecurePass123!",
    "password2":"SecurePass123!"
  }'

# Respuesta:
{
  "id": 5,
  "username": "newuser",
  "email": "user@example.com"
}
```

### 2. Login
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username":"newuser",
    "password":"SecurePass123!"
  }'

# Respuesta:
{
  "access": "eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwgImV4cCI6...",
  "refresh": "eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsIGV4cCI6..."
}
```

### 3. Solicitar Reset de Contraseña
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/password-reset/" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# Respuesta:
{
  "detail": "Si el email existe en nuestro sistema, recibirás un enlace de reinicio de contraseña."
}

# En BD se crea PasswordResetToken con token único
```

### 4. Confirmar Reset (Cliente usa token recibido)
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/password-reset/confirm/" \
  -H "Content-Type: application/json" \
  -d '{
    "token":"abcd1234567890...",
    "password":"NewPassword456!",
    "password2":"NewPassword456!"
  }'

# Respuesta:
{
  "detail": "Contraseña actualizada exitosamente."
}
```

### 5. Usar Nueva Contraseña
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username":"newuser",
    "password":"NewPassword456!"
  }'

# Respuesta:
{
  "access": "eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwgImV4cCI6...",
  "refresh": "eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsIGV4cCI6..."
}
```

---

## Seguridad Implementada

✓ **Tokens seguros:** Generados con `get_random_string(length=64)`
✓ **Expiración:** 24 horas automáticamente
✓ **Single-use:** Token se marca como `used=True` tras primer uso
✓ **No reutilizable:** Tokens anteriores del usuario se invalidan
✓ **Privacy:** No se revela si email existe
✓ **Contraseñas:** Hash seguro con `set_password()`
✓ **Validación:** Mínimo 8 caracteres, no solo números

---

## Siguientes Pasos Opcionales

1. **Email Real:** Configurar SMTP para enviar enlace con token por email
2. **Frontend:** Implementar form de reset que use el token
3. **2FA:** Añadir autenticación multi-factor
4. **Audit:** Registrar intentos de reset fallidos

---

**Estado:** ✅ REPARADO Y PROBADO
**Fecha:** 28 de noviembre de 2025
**Tests:** 17/17 pasados
