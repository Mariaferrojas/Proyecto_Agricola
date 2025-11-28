
## 📌 1. Introducción

La API implementa un sistema de autenticación basado en *tokens*, el cual permite que los usuarios accedan de forma segura a los recursos protegidos. Este manual explica:

- Cómo obtener el token de acceso.
- Cómo usarlo correctamente.
- Cómo hacer pruebas desde Postman y Thunder Client.
- Ejemplos de peticiones y manejo de errores.

---

## 🧩 2. Requisitos Previos

Antes de comenzar, asegúrese de tener:

- Usuario y contraseña registrados en el sistema.
- La API corriendo localmente o en un servidor.
- Una herramienta de pruebas HTTP:
  - *Postman*, o  
  - *Thunder Client* (extensión de VS Code).
- Conocimientos básicos de peticiones HTTP (GET, POST, PUT, DELETE).

---

## 🔐 3. Flujo de Autenticación

La autenticación se realiza mediante token:

1. El usuario envía credenciales a la API.
2. La API verifica credenciales.
3. Si son correctas, devuelve un token.
4. El usuario usa este token en el header de cada petición.
5. La API autoriza o rechaza la solicitud según la validez del token.

### Esquema del proceso
-Usuario → Envía credenciales → Servidor
-Servidor → Devuelve token → Usuario
-Usuario → Envía solicitudes con token → Servidor
-Servidor → Respuesta autorizada

---

## 📥 4. Obtención del Token

### *Endpoint* 
### *Body (JSON)*
```json
{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI..."
}
-Errores frecuentes

-400 Bad Request – Datos mal enviados.

-401 Unauthorized – Credenciales inválidas.

-500 Internal Server Error – Error interno. Todas las peticiones protegidas deben incluir el token en el header:

Authorization: Bearer TU_TOKEN_AQUI

###Ejemplo-GET /api/productos/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI... 6. Pruebas con Postman
###6.1. Obtener el token

-Abrir Postman.

-Crear nueva petición tipo POST.

-URL:

-http://localhost:8000/api/auth/login/ En Body → raw → JSON, enviar:

{
  "username": "admin",
  "password": "123456"
}


Clic en Send.

Copiar el token recibido 6.2. Usar el token en Postman

Crear una nueva petición.

En la pestaña Headers, agregar:

Key: Authorization
Value: Bearer TU_TOKEN


Enviar la solicitud.

⚡ 7. Pruebas con Thunder Client (VS Code)
7.1. Obtener token

Abrir la extensión Thunder Client.

Nueva Request → método POST.

URL:

http://localhost:8000/api/auth/login/


En Body → JSON, enviar las credenciales.

Clic en Send.

Copiar el token.

7.2. Usar token

Crear nueva Request.

Ir a Auth.

Elegir Bearer Token.

Pegar el token.

Enviar la solicitud.

